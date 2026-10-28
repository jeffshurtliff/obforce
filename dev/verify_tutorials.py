# -*- coding: utf-8 -*-
"""
:Module:            dev.verify_tutorials
:Synopsis:          Verifies fictional documentation journeys in independent artifact installs
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     28 Oct 2026
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
from pathlib import Path

RECOVERY_PROBE = r"""
import sys
import shutil
from pathlib import Path
from click.testing import CliRunner
from obforce.cli import main
from obforce.sync import transactions

for event in ('socket.connect', 'subprocess.Popen', 'os.system', 'os.posix_spawn'):
    try:
        sys.audit(event)
    except RuntimeError:
        pass
    else:
        raise AssertionError('Runtime guard missing')
seed = Path(sys.argv[1])
cases = [seed.parent / ('Recovery ' + phase) for phase in ('published', 'commit', 'edited')]
for case in cases:
    shutil.copytree(seed, case)
def invoke(*args):
    return CliRunner().invoke(main, [str(x) for x in args])
def snapshot():
    return {str(p.relative_to(root)): (p.stat().st_mtime_ns, p.read_bytes() if p.is_file() else None)
            for p in (root, *root.rglob('*'))}
for phase, root in zip(('published', 'commit', 'edited'), cases, strict=True):
    config = root / 'Config with spaces.toml'
    vault = root / 'Knowledge'
    meta = root / 'Fictional Project/core/main/default/classes/DemoService.cls-meta.xml'
    boundary_to_fail = 'commit' if phase == 'commit' else 'published'
    old = meta.read_bytes()
    meta.write_bytes(old.replace(b'68.0', b'69.0') if b'68.0' in old else old.replace(b'69.0', b'68.0'))
    before_notes = {str(p.relative_to(vault)): p.read_bytes() for p in vault.rglob('*.md')}
    before_state = (vault / '.obforce/state.json').read_bytes()
    checkpoint = transactions._checkpoint
    def fail(boundary, index=-1):
        if boundary == boundary_to_fail and (boundary != 'published' or index == 0):
            raise OSError('Fictional tutorial interruption')
    transactions._checkpoint = fail
    try:
        result = invoke('sync', '--config', config)
        assert result.exit_code == 3 and 'recovery_required: true' in result.output, result.output
    finally:
        transactions._checkpoint = checkpoint
    before = snapshot()
    result = invoke('recover', '--config', config)
    assert result.exit_code == 0 and snapshot() == before, result.output
    operation = '--cleanup' if phase == 'commit' else '--rollback'
    wrong = '--rollback' if phase == 'commit' else '--cleanup'
    assert invoke('recover', '--config', config, wrong).exit_code == 3 and snapshot() == before
    assert invoke('sync', '--config', config, '--dry-run').exit_code == 3 and snapshot() == before
    if phase == 'edited':
        note = next(vault.rglob('*.md'))
        saved = note.read_bytes()
        note.write_bytes(saved + b'\nIntervening fictional edit\n')
        edited = snapshot()
        assert invoke('recover', '--config', config, operation).exit_code == 3
        assert snapshot() == edited
        continue  # Keep this independent fixture's changed note and journal intact.
    result = invoke('recover', '--config', config, operation)
    assert result.exit_code == 0, result.output
    if phase == 'published':
        assert {str(p.relative_to(vault)): p.read_bytes() for p in vault.rglob('*.md')} == before_notes
        assert (vault / '.obforce/state.json').read_bytes() == before_state
        assert invoke('sync', '--config', config).exit_code == 0
    before = snapshot()
    assert invoke('recover', '--config', config).exit_code == 0 and snapshot() == before
    assert invoke('sync', '--config', config).exit_code == 0 and snapshot() == before
    assert b'Human context: reviewed' in (vault / 'Reviewed/DemoService.md').read_bytes()
print('Synthetic precommit rollback, committed cleanup and intervening-edit refusal passed')
"""


def _snapshot(root: Path) -> dict:
    """Observe bytes and modification times without altering fixture content."""
    return {
        path.relative_to(root).as_posix(): (path.stat().st_mtime_ns, path.read_bytes() if path.is_file() else None)
        for path in (root, *root.rglob('*'))
    }


def _run(command: list[str], cwd: Path, environment: dict[str, str], expected: int = 0) -> str:
    """Run an explicitly authorized synthetic child with a finite deadline."""
    result = subprocess.run(command, cwd=cwd, env=environment, capture_output=True, text=True, timeout=180, check=False)
    if result.returncode != expected or len((result.stdout + result.stderr).encode()) > 16_384:
        raise AssertionError(f'Tutorial child outcome {result.returncode}, expected {expected}: {result.stdout}{result.stderr}')
    return result.stdout


def _commands(document: Path) -> list[list[str]]:
    """Read literal shell examples without evaluating shell substitutions."""
    return [
        shlex.split(line)
        for block in re.findall(r'```sh\n(.*?)```', document.read_text(encoding='utf-8'), re.S)
        for line in block.splitlines()
        if line and not line.startswith('#')
    ]


def verify(command: list[str], python: Path, root: Path, work: Path, environment: dict[str, str]) -> None:
    """Execute user-guide examples with the supplied installed entry point.

    :param command: Actual independent console or module command prefix.
    :param python: Interpreter belonging to that independent installation.
    :param root: New fixture root outside checkout and invocation cwd.
    :param work: Existing empty invocation directory.
    :param environment: Active runtime audit guards and no external tools on PATH.
    """
    repository = Path(__file__).resolve().parents[1]
    workspace = root / 'Fictional Workspace'
    root.mkdir()
    config = workspace / 'Config with spaces.toml'
    vault = workspace / 'Knowledge'
    before_cwd = _snapshot(work)
    sample = repository / 'examples/sample_sfdx'
    before_sample = _snapshot(sample)
    substitutions = {
        '/absolute/path/Fictional Workspace': str(workspace),
        '/absolute/path/obforce-checkout': str(repository),
        '../Fictional Workspace/Config with spaces.toml': os.path.relpath(config, work),
    }

    def translate(arg: str) -> str:
        for placeholder, actual in substitutions.items():
            if arg == placeholder or arg.startswith(placeholder + '/'):
                return actual + arg[len(placeholder) :]
        return arg

    original_ids = None
    for args in _commands(repository / 'docs/QUICKSTART.md'):
        args = [translate(arg) for arg in args]
        source_before = _snapshot(workspace / 'Fictional Project') if workspace.exists() else None
        state_before = _snapshot(workspace) if workspace.exists() else None
        if args[0] == 'python' and args[1] == '-c':
            _run([str(python), *args[1:]], work, environment)
            continue
        prefix = 1 if args[0] == 'obforce' else 3
        selected = args[prefix:]
        _run([*command, *selected], work, environment)
        assert _snapshot(workspace / 'Fictional Project') == source_before
        if '--dry-run' in args or selected[0] == 'recover':
            assert _snapshot(workspace) == state_before
        if (vault / '.obforce/state.json').exists():
            state = json.loads((vault / '.obforce/state.json').read_bytes())
            ids = sorted(record['note']['obforce_id'] for record in state['notes'])
            if original_ids is None:
                original_ids = ids
            assert ids == original_ids
    assert (vault / 'Reviewed/DemoService.md').is_file()
    assert b'Human context: reviewed' in (vault / 'Reviewed/DemoService.md').read_bytes()
    assert b'68.0' in (vault / 'Reviewed/DemoService.md').read_bytes()
    before = _snapshot(workspace)
    _run([*command, 'build', '--config', str(config)], work, environment, 3)
    for selected in (str(config), os.path.relpath(config, work)):
        for args in (['sync', '--dry-run'], ['sync'], ['recover'], ['recover', '--dry-run']):
            _run([*command, *args, '--config', selected], work, environment)
            assert _snapshot(workspace) == before
    # Execute the guide's literal setup and sync commands; append its exact TOML.
    commands = _commands(repository / 'docs/CUSTOMIZATION.md')
    for args in commands:
        args = [translate(arg) for arg in args]
        if args[:2] == ['python', '-c']:
            _run([str(python), *args[1:]], work, environment)
            config.write_bytes(config.read_bytes() + b'\n[templates]\ndirectory = "./Templates"\n')
        else:
            before = _snapshot(workspace)
            _run([*command, *args[1:]], work, environment)
            if '--dry-run' in args:
                assert _snapshot(workspace) == before
    assert b'Fictional team context.' not in (vault / 'Reviewed/DemoService.md').read_bytes()
    before = _snapshot(workspace)
    _run([*command, 'sync', '--config', str(config)], work, environment)
    assert _snapshot(workspace) == before
    # New-note-only creation text is demonstrated in a separate empty destination.
    second = workspace / 'Second Config.toml'
    _run(
        [
            *command,
            'init',
            '--config',
            str(second),
            '--source',
            './Fictional Project',
            '--vault',
            './Second Knowledge',
            '--workspace-id',
            'fictional',
        ],
        work,
        environment,
    )
    second.write_bytes(second.read_bytes() + b'\n[templates]\ndirectory = "./Templates"\n')
    _run([*command, 'build', '--config', str(second), '--dry-run'], work, environment)
    assert not (workspace / 'Second Knowledge').exists()
    _run([*command, 'build', '--config', str(second)], work, environment)
    assert b'Fictional team context.' in next((workspace / 'Second Knowledge').rglob('*.md')).read_bytes()
    asset = vault / 'Dashboards/Apex Classes.base'
    saved = asset.read_bytes()
    asset.write_bytes(saved + b'\n# Fictional UI edit\n')
    before = _snapshot(workspace)
    _run([*command, 'sync', '--config', str(config)], work, environment, 3)
    assert _snapshot(workspace) == before
    asset.write_bytes(saved)  # Explicit test fixture restoration only.
    protected = _snapshot(workspace / 'Fictional Project')
    _run([str(python), '-c', RECOVERY_PROBE, str(workspace)], work, environment)
    assert _snapshot(workspace / 'Fictional Project') == protected
    assert _snapshot(sample) == before_sample and _snapshot(work) == before_cwd
    print('Fictional sample tutorials, UUID move, customization, previews/no-op and recovery passed')


def main() -> None:
    """Run the complete fresh-artifact checker including installed tutorials."""
    from check_artifacts import main as check

    check()


if __name__ == '__main__':
    main()
