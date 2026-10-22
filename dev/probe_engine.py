# -*- coding: utf-8 -*-
"""
:Module:            dev.probe_engine
:Synopsis:          Probes installed initial lifecycle and recovery with active runtime guards
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     21 Oct 2026
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from click.testing import CliRunner

from obforce.cli import main as cli
from obforce.sync import transactions
from obforce.sync.state import parse_state


def project(root: Path) -> Path:
    """Create one entirely fictional offline project outside the current directory."""
    source = root / 'Fictional Project'
    source.mkdir()
    (source / 'sfdx-project.json').write_text('{"packageDirectories":[{"path":"package"}]}', encoding='utf-8')
    classes = source / 'package/classes'
    classes.mkdir(parents=True)
    (classes / 'Alpha.cls').write_text('// Fictional source\n', encoding='utf-8')
    (classes / 'Alpha.cls-meta.xml').write_text(
        '<ApexClass xmlns="http://soap.sforce.com/2006/04/metadata">'
        '<apiVersion>67.0</apiVersion><status>Active</status></ApexClass>',
        encoding='utf-8',
    )
    return source


def snapshot(root: Path) -> dict:
    """Retain exact bytes and mtimes for source/cwd/refusal assertions."""
    return {
        p.relative_to(root).as_posix(): (p.stat().st_mtime_ns, p.read_bytes() if p.is_file() else None)
        for p in (root, *root.rglob('*'))
    }


def invoke(*args: object):
    """Run the installed public command in-process without subprocess privilege."""
    return CliRunner().invoke(cli, [str(a) for a in args])


def main() -> None:
    """Exercise preview/publication/rollback/cleanup without runtime network/process access."""
    for event in ('socket.connect', 'subprocess.Popen'):
        try:
            sys.audit(event)
        except RuntimeError:
            pass
        else:
            raise AssertionError('Runtime guard is missing')
    cwd = Path.cwd()
    cwd_before = snapshot(cwd)
    with tempfile.TemporaryDirectory(prefix='obforce-initial-synthetic-') as temporary:
        root = Path(temporary).resolve()
        source = project(root)
        source_before = snapshot(source)
        for phase in ('ready', 'published', 'commit'):
            config = root / f'{phase}.toml'
            vault = root / f'{phase} Parent/Vault'
            args = ('init', '--config', config, '--source', source.name, '--vault', str(vault), '--workspace-id', 'demo')
            before = snapshot(root)
            assert invoke(*args, '--dry-run').exit_code == 0
            assert snapshot(root) == before
            result = invoke(*args)
            assert result.exit_code == 0, result.output
            config_before = (config.read_bytes(), config.stat().st_mtime_ns)
            before = snapshot(root)
            result = invoke('build', '--config', config, '--dry-run')
            assert result.exit_code == 0, result.output
            assert snapshot(root) == before and not vault.exists()
            original = transactions._checkpoint

            def fail(boundary, index=-1, selected=phase):
                if boundary == selected and (boundary != 'published' or index == 0):
                    raise OSError('Fictional interruption')

            transactions._checkpoint = fail
            try:
                result = invoke('build', '--config', config)
                assert result.exit_code == 3 and 'recovery_required: true' in result.output, result.output
            finally:
                transactions._checkpoint = original
            before = snapshot(root)
            assert invoke('recover', '--config', config).exit_code == 0
            assert snapshot(root) == before
            correct = '--cleanup' if phase == 'commit' else '--rollback'
            wrong = '--rollback' if phase == 'commit' else '--cleanup'
            assert invoke('recover', '--config', config, wrong).exit_code == 3
            assert snapshot(root) == before
            result = invoke('recover', '--config', config, correct)
            assert result.exit_code == 0, result.output
            if phase == 'commit':
                state = parse_state((vault / '.obforce/state.json').read_bytes())
                assert len(state.notes) == 1
            else:
                assert not list(vault.rglob('*.md')) and not (vault / '.obforce/state.json').exists()
            before = snapshot(root)
            assert invoke('build', '--config', config).exit_code == 3
            assert snapshot(root) == before
            assert (config.read_bytes(), config.stat().st_mtime_ns) == config_before
        assert snapshot(source) == source_before
    assert snapshot(cwd) == cwd_before


if __name__ == '__main__':
    main()
