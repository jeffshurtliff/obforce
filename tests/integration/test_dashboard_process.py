# -*- coding: utf-8 -*-
"""
:Module:            tests.integration.test_dashboard_process
:Synopsis:          Exercises guarded dashboard process death and concurrent writer refusal
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     26 Oct 2026
"""

from __future__ import annotations

import os
import runpy
import subprocess
import sys
import time
from pathlib import Path

import pytest
from click.testing import CliRunner

from obforce.cli import main
from obforce.renderer.dashboards import render_dashboard
from obforce.sync.state import parse_state

_PROBE = Path(__file__).resolve().parents[2] / 'dev/probe_dashboard.py'
_SETUP = _PROBE.read_text().rsplit("if __name__ == '__main__':", 1)[0]
_GUARD = """
def deny(event, args):
    if event.startswith('socket.') or event in {'subprocess.Popen', 'os.system', 'os.posix_spawn', 'os.spawn'}:
        raise RuntimeError('Application runtime network/process access forbidden')
sys.addaudithook(deny)
"""
_PREPARE = """
root = Path(sys.argv[1])
source, config, vault = setup(root)
assert invoke('build', '--config', config).exit_code == 0
prior = seed_prior_asset(vault)
(root / 'prior-state.fixture').write_bytes((vault / '.obforce/state.json').read_bytes())
"""


def test_shared_installed_dashboard_probe(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    active = [True]

    def guard(event, args):
        if active[0] and (event.startswith('socket.') or event in {'subprocess.Popen', 'os.system', 'os.posix_spawn'}):
            raise RuntimeError('Application runtime network/process access forbidden')

    sys.addaudithook(guard)
    try:
        runpy.run_path(str(_PROBE), run_name='__main__')
        assert list(tmp_path.iterdir()) == []
    finally:
        active[0] = False


@pytest.mark.parametrize('phase', ['ready', 'published', 'replace_after', 'commit', 'cleanup_before'])
@pytest.mark.parametrize('human_edit', [False, True])
def test_dashboard_process_death_recovery_keeps_exact_or_manual_evidence(tmp_path, phase, human_edit):
    root = tmp_path.resolve()
    script = (
        _SETUP
        + _GUARD
        + _PREPARE
        + """
import os
def die(name, index=-1):
    if name == sys.argv[2] and (name not in {'published', 'replace_after'} or index == 0):
        os._exit(97)
transactions._checkpoint = die
result = invoke('sync', '--config', config)
raise AssertionError('Requested dashboard death boundary not reached: ' + result.output)
"""
    )
    result = subprocess.run(
        [sys.executable, '-I', '-c', script, str(root), phase],
        cwd=root,
        env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'),
        capture_output=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 97, result.stderr.decode()
    vault, config = root / 'Vault with spaces', root / 'Config with spaces.toml'
    asset = vault / 'Dashboards/Apex Classes.base'
    if human_edit:
        # At ready, edit the existing before-image target; after publication edit the new one.
        asset.write_bytes(asset.read_bytes() + b'# Human dashboard edit after death\n')
    snapshot = {p: (p.stat().st_mtime_ns, p.read_bytes() if p.is_file() else None) for p in (root, *root.rglob('*'))}
    preview = CliRunner().invoke(main, ['recover', '--config', str(config)])
    assert {p: (p.stat().st_mtime_ns, p.read_bytes() if p.is_file() else None) for p in (root, *root.rglob('*'))} == snapshot
    committed = phase in {'commit', 'cleanup_before'}
    result = CliRunner().invoke(main, ['recover', '--config', str(config), '--cleanup' if committed else '--rollback'])
    if human_edit or phase == 'replace_after':
        assert preview.exit_code == result.exit_code == 3, (preview.output, result.output)
        assert {p: (p.stat().st_mtime_ns, p.read_bytes() if p.is_file() else None) for p in (root, *root.rglob('*'))} == snapshot
    else:
        assert preview.exit_code == result.exit_code == 0, (preview.output, result.output)
        if committed:
            assert asset.read_bytes() == render_dashboard()
        else:
            assert asset.read_bytes() == render_dashboard() + b'# Synthetic prior asset revision\n'
            assert (vault / '.obforce/state.json').read_bytes() == (root / 'prior-state.fixture').read_bytes()
        assert parse_state((vault / '.obforce/state.json').read_bytes()).dashboard.content == asset.read_bytes()


def test_competing_asset_sync_and_recovery_cannot_publish_a_subset(tmp_path):
    root = tmp_path.resolve()
    script = (
        _SETUP
        + _GUARD
        + _PREPARE
        + """
import time
def hold(name, index=-1):
    if name == 'ready':
        (root / 'ready.marker').write_text('ready')
        while True:
            time.sleep(0.05)
transactions._checkpoint = hold
result = invoke('sync', '--config', config)
raise AssertionError('Dashboard lock boundary not reached: ' + result.output)
"""
    )
    process = subprocess.Popen(
        [sys.executable, '-I', '-c', script, str(root)],
        cwd=root,
        env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        deadline = time.monotonic() + 20
        while not (root / 'ready.marker').exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.02)
        assert (root / 'ready.marker').exists(), (
            process.communicate(timeout=1)[1].decode() if process.poll() is not None else 'Ready timeout'
        )
        vault, config = root / 'Vault with spaces', root / 'Config with spaces.toml'
        saved = {
            p: (p.read_bytes(), p.stat().st_mtime_ns)
            for p in (vault / '.obforce/state.json', vault / 'Dashboards/Apex Classes.base')
        }
        for command in (['sync'], ['sync', '--dry-run'], ['recover', '--rollback']):
            result = CliRunner().invoke(main, command + ['--config', str(config)])
            assert result.exit_code == 3, result.output
            assert {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in saved} == saved
    finally:
        process.kill()
        process.communicate(timeout=10)
    result = CliRunner().invoke(main, ['recover', '--rollback', '--config', str(root / 'Config with spaces.toml')])
    assert result.exit_code == 0, result.output


@pytest.mark.parametrize('entrypoint', ['console', 'module'])
@pytest.mark.parametrize('relative', [False, True])
def test_plain_redirected_entrypoints_explicit_space_paths_and_bounded_outcomes(tmp_path, entrypoint, relative):
    import sysconfig

    helpers = runpy.run_path(str(_PROBE))
    workspace = tmp_path.resolve() / 'Fictional Workspace'
    workspace.mkdir()
    source, config, vault = helpers['setup'](workspace)
    work, guard = tmp_path.resolve() / 'work', tmp_path.resolve() / 'guard'
    work.mkdir()
    guard.mkdir()
    (guard / 'sitecustomize.py').write_text('import sys\n' + _GUARD, encoding='utf-8', newline='\n')
    script = Path(sysconfig.get_path('scripts')) / 'obforce'
    assert script.is_file()
    command = (
        [sys.executable, '-m', 'obforce']
        if entrypoint == 'module'
        else [sys.executable, str(script)]
        if os.name == 'nt'
        else [str(script)]
    )
    env = dict(os.environ, PATH='', PYTHONPATH=str(guard), PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1', NO_COLOR='1')
    selected = '../Fictional Workspace/Config with spaces.toml' if relative else str(config)

    def run(args, code):
        result = subprocess.run(command + args, cwd=work, env=env, capture_output=True, text=True, timeout=30, check=False)
        assert result.returncode == code, (result.stdout, result.stderr)
        assert len((result.stdout + result.stderr).encode()) < 4096 and '\x1b' not in result.stdout + result.stderr
        assert str(workspace) not in result.stdout and 'Alpha' not in result.stdout
        assert list(work.iterdir()) == []
        return result

    for feature in ('init', 'build', 'sync', 'recover'):
        run([feature, '--help'], 0)
    run(['sync'], 2)
    run(['sync', '--config', selected, '--sf-directory', 'not an absolute neutral path'], 3)  # No existing state.
    before = helpers['snapshot'](workspace)
    run(['build', '--config', selected, '--dry-run'], 0)
    assert helpers['snapshot'](workspace) == before
    run(['build', '--config', selected], 0)
    run(['build', '--config', selected], 3)
    before = helpers['snapshot'](workspace)
    for args in (['sync', '--dry-run'], ['sync'], ['recover'], ['recover', '--cleanup']):
        run(args + ['--config', selected], 0)
        assert helpers['snapshot'](workspace) == before
    run(['sync', '--config', selected, '--attest-comparable-inventory'], 2)
    run(['recover', '--config', selected, '--rollback', '--cleanup'], 2)
    (source / 'package/classes/Unpaired.cls').write_text('// Fictional missing XML', encoding='utf-8')
    run(['sync', '--config', selected], 4)
    asset = vault / 'Dashboards/Apex Classes.base'
    asset.write_bytes(asset.read_bytes() + b'# Human edited dashboard\n')
    before = helpers['snapshot'](workspace)
    run(['sync', '--config', selected], 3)
    assert helpers['snapshot'](workspace) == before
