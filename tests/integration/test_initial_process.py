# -*- coding: utf-8 -*-
"""
:Module:            tests.integration.test_initial_process
:Synopsis:          Exercises public setup death, journal recovery and competing initial writers
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     25 Oct 2026
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest
from click.testing import CliRunner

from obforce.cli import main

_SETUP = (Path(__file__).resolve().parents[2] / 'dev/probe_engine.py').read_text().rsplit("if __name__ == '__main__':", 1)[0]
_GUARD = """
def deny(event, args):
    if event.startswith('socket.') or event in {'subprocess.Popen', 'os.system', 'os.posix_spawn', 'os.spawn'}:
        raise RuntimeError('Runtime network/process access forbidden')
sys.addaudithook(deny)
"""


@pytest.mark.parametrize(
    'boundary',
    ['config_ready', 'config_created', 'setup_ready', 'directory_created', 'publication_ready', 'ready', 'published', 'commit'],
)
def test_public_initial_death_keeps_validated_or_manual_evidence(tmp_path, boundary):
    root = tmp_path.resolve()
    script = (
        _SETUP
        + _GUARD
        + """
import os
from obforce.sync import engine
root = Path(sys.argv[1])
source = project(root)
config = root / 'Config.toml'
boundary = sys.argv[2]
def die_setup(name):
    if name == boundary:
        os._exit(97)
def die_transaction(name, index=-1):
    if name == boundary and (name != 'published' or index == 0):
        os._exit(97)
engine._checkpoint = die_setup
transactions._checkpoint = die_transaction
result = invoke('init', '--config', config, '--source', source.name, '--vault', 'New Parent/Vault', '--workspace-id', 'demo')
assert result.exit_code == 0, result.output
result = invoke('build', '--config', config)
raise AssertionError('Death boundary not reached: ' + result.output)
"""
    )
    result = subprocess.run(
        [sys.executable, '-I', '-c', script, str(root), boundary],
        cwd=root,
        env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'),
        capture_output=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 97, result.stderr.decode()
    vault, config = root / 'New Parent/Vault', root / 'Config.toml'
    source = root / 'Fictional Project'
    assert (source / 'package/classes/Alpha.cls').read_text() == '// Fictional source\n'
    if boundary.startswith('config_'):
        assert config.exists() == (boundary == 'config_created')
        assert not vault.exists()
    elif boundary in {'ready', 'published', 'commit'}:
        journal = vault / '.obforce/journal.json'
        before = journal.read_bytes(), journal.stat().st_mtime_ns
        result = CliRunner().invoke(main, ['recover', '--config', str(config)])
        assert result.exit_code == 0, result.output
        assert (journal.read_bytes(), journal.stat().st_mtime_ns) == before
        operation = '--cleanup' if boundary == 'commit' else '--rollback'
        result = CliRunner().invoke(main, ['recover', '--config', str(config), operation])
        assert result.exit_code == 0, result.output
        assert not journal.exists()
        if boundary != 'commit':
            assert not list(vault.rglob('*.md')) and not (vault / '.obforce/state.json').exists()
    else:
        assert not list(root.rglob('*.md')) and not list(root.rglob('state.json'))
        # Only the process that observed setup stamps can clean those directories.
        # No persisted ownership is fabricated after its death.
        assert not (vault / '.obforce/journal.json').exists()
    assert not (root / '.obforce').exists()


def test_public_competing_writers_and_recovery_refuse_held_guard(tmp_path):
    root = tmp_path.resolve()
    marker = root / 'ready.marker'
    script = (
        _SETUP
        + _GUARD
        + """
import os, time
root = Path(sys.argv[1])
source = project(root)
config = root / 'Config.toml'
assert invoke('init', '--config', config, '--source', source.name, '--vault', 'Vault', '--workspace-id', 'demo').exit_code == 0
def hold(name, index=-1):
    if name == 'ready':
        (root / 'ready.marker').write_text('ready')
        while True:
            time.sleep(0.05)
transactions._checkpoint = hold
result = invoke('build', '--config', config)
raise AssertionError('Guard boundary not reached: ' + result.output)
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
        while not marker.exists() and time.monotonic() < deadline and process.poll() is None:
            time.sleep(0.02)
        assert marker.exists(), process.communicate(timeout=1)[1].decode() if process.poll() is not None else 'Ready timeout'
        journal = root / 'Vault/.obforce/journal.json'
        before = journal.read_bytes()
        for args in (['build'], ['recover', '--rollback']):
            result = CliRunner().invoke(main, args + ['--config', str(root / 'Config.toml')])
            assert result.exit_code == 3, result.output
            assert journal.read_bytes() == before
        assert not list((root / 'Vault').rglob('*.md'))
    finally:
        process.kill()
        process.communicate(timeout=10)
    result = CliRunner().invoke(main, ['recover', '--rollback', '--config', str(root / 'Config.toml')])
    assert result.exit_code == 0, result.output


@pytest.mark.parametrize('boundary', ['ready', 'published', 'commit', 'replace_after', 'cleanup_before'])
@pytest.mark.parametrize('human_edit', [False, True])
def test_public_sync_process_death_retains_complete_or_manual_evidence(tmp_path, boundary, human_edit):
    root = tmp_path.resolve()
    script = (
        _SETUP
        + _GUARD
        + """
import os
root = Path(sys.argv[1])
source = project(root)
config = root / 'Config.toml'
assert invoke('init', '--config', config, '--source', source.name, '--vault', 'Vault', '--workspace-id', 'demo').exit_code == 0
assert invoke('build', '--config', config).exit_code == 0
metadata = source / 'package/classes/Alpha.cls-meta.xml'
metadata.write_text(metadata.read_text().replace('67.0', '68.0'))
def die(name, index=-1):
    if name == sys.argv[2] and (name not in {'published', 'replace_after'} or index == 0):
        os._exit(97)
transactions._checkpoint = die
result = invoke('sync', '--config', config)
raise AssertionError('Sync death boundary not reached: ' + result.output)
"""
    )
    result = subprocess.run(
        [sys.executable, '-I', '-c', script, str(root), boundary],
        cwd=root,
        env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'),
        capture_output=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 97, result.stderr.decode()
    vault, config = root / 'Vault', root / 'Config.toml'
    note = next(vault.rglob('*.md'))
    if human_edit:
        note.write_bytes(note.read_bytes() + b'\nIntervening edit after worker death\n')
    snapshot = {
        p.relative_to(root): (p.stat().st_mtime_ns, p.read_bytes() if p.is_file() else None) for p in (root, *root.rglob('*'))
    }
    refused = CliRunner().invoke(main, ['sync', '--config', str(config)])
    assert refused.exit_code == 3, refused.output
    preview = CliRunner().invoke(main, ['recover', '--config', str(config)])
    operation = '--cleanup' if boundary in ('commit', 'cleanup_before') else '--rollback'
    recovered = CliRunner().invoke(main, ['recover', '--config', str(config), operation])
    if human_edit or boundary == 'replace_after':
        assert preview.exit_code == recovered.exit_code == 3
        assert {
            p.relative_to(root): (p.stat().st_mtime_ns, p.read_bytes() if p.is_file() else None) for p in (root, *root.rglob('*'))
        } == snapshot
    else:
        assert preview.exit_code == recovered.exit_code == 0, (preview.output, recovered.output)
        assert CliRunner().invoke(main, ['sync', '--config', str(config)]).exit_code == 0
        from obforce.sync.state import parse_state

        assert parse_state((vault / '.obforce/state.json').read_bytes()).evidence is not None


def test_competing_public_sync_and_recovery_preserve_existing_state(tmp_path):
    root = tmp_path.resolve()
    script = (
        _SETUP
        + _GUARD
        + """
import time
root = Path(sys.argv[1])
source = project(root)
config = root / 'Config.toml'
assert invoke('init', '--config', config, '--source', source.name, '--vault', 'Vault', '--workspace-id', 'demo').exit_code == 0
assert invoke('build', '--config', config).exit_code == 0
metadata = source / 'package/classes/Alpha.cls-meta.xml'
metadata.write_text(metadata.read_text().replace('67.0', '68.0'))
def hold(name, index=-1):
    if name == 'ready':
        (root / 'ready.marker').write_text('ready')
        while True:
            time.sleep(0.05)
transactions._checkpoint = hold
result = invoke('sync', '--config', config)
raise AssertionError('Sync lock boundary not reached: ' + result.output)
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
        state_path = root / 'Vault/.obforce/state.json'
        saved = state_path.read_bytes(), state_path.stat().st_mtime_ns
        for command in (['sync'], ['sync', '--dry-run'], ['recover', '--rollback']):
            result = CliRunner().invoke(main, command + ['--config', str(root / 'Config.toml')])
            assert result.exit_code == 3, result.output
            assert (state_path.read_bytes(), state_path.stat().st_mtime_ns) == saved
    finally:
        process.kill()
        process.communicate(timeout=10)
    recovered = CliRunner().invoke(main, ['recover', '--rollback', '--config', str(root / 'Config.toml')])
    assert recovered.exit_code == 0, recovered.output
