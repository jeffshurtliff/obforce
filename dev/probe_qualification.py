# -*- coding: utf-8 -*-
"""
:Module:            dev.probe_qualification
:Synopsis:          Qualifies installed publication limits and a separate bounded offline lifecycle
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     27 Oct 2026
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from obforce import constants as const
from obforce.cli import main as cli
from obforce.sync import planner
from obforce.sync.state import parse_state

XML = (
    '<ApexClass xmlns="http://soap.sforce.com/2006/04/metadata">'
    '<apiVersion>67.0</apiVersion><status>Active</status></ApexClass>\n'
)


def snapshot(root: Path) -> dict:
    """Compare synthetic bytes, mtimes and complete tree membership, excluding atimes."""
    return {
        path.relative_to(root).as_posix(): (path.stat().st_mtime_ns, path.read_bytes() if path.is_file() else None)
        for path in (root, *root.rglob('*'))
    }


def invoke(*args):
    """Exercise public command code under the caller's active runtime audit guard."""
    result = CliRunner().invoke(cli, [str(arg) for arg in args], color=False)
    assert len(result.output.encode()) <= const.MAX_REPORT_BYTES
    assert '\x1b[' not in result.output
    return result


def setup(root: Path, count: int):
    """Create only fictional pairs and an explicit config, outside checkout and cwd."""
    source, vault = root / 'Project with spaces', root / 'Absent Parent/Vault with spaces'
    classes = source / 'package/classes'
    classes.mkdir(parents=True)
    (source / 'sfdx-project.json').write_text('{"packageDirectories":[{"path":"package"}]}', encoding='utf-8')
    for index in range(count):
        (classes / f'Class{index:04d}.cls').write_text('// Synthetic private-body sentinel; never read\n', encoding='utf-8')
        (classes / f'Class{index:04d}.cls-meta.xml').write_text(XML, encoding='utf-8', newline='\n')
    config = root / 'Config with spaces.toml'
    result = invoke(
        'init',
        '--config',
        config,
        '--source',
        source.name,
        '--vault',
        'Absent Parent/Vault with spaces',
        '--workspace-id',
        'qualification',
    )
    assert result.exit_code == 0, result.output
    return source, config, vault


def publication_refusal(root: Path, count: int) -> None:
    """Refuse one indivisible over-bound first build before even creating output parents."""
    source, config, vault = setup(root, count)
    before = snapshot(root)
    assert count + 2 > const.MAX_TRANSACTION_FILES  # One dashboard and complete state are changed files too.
    for flags in (['--dry-run'], []):
        failures = []
        original = planner._blocked

        def diagnostic(error, coverage, failures=failures, original=original):
            failures.append((type(error).__name__, str(error)))
            return original(error, coverage)

        with patch.object(planner, '_blocked', diagnostic):
            result = invoke('build', '--config', config, *flags)
        assert result.exit_code == 2, (result.output, result.exception, failures)
        assert 'Transaction exceeds aggregate bound' in result.output, result.output
        assert 'sentinel' not in result.output and str(source) not in result.output
        assert snapshot(root) == before and not vault.parent.exists()


def lifecycle(root: Path) -> None:
    """Qualify a separate 12-note lifecycle, with no publication splitting or adoption."""
    source, config, vault = setup(root, 12)
    before = snapshot(root)
    assert invoke('build', '--config', config, '--dry-run').exit_code == 0
    assert snapshot(root) == before
    result = invoke('build', '--config', config)
    assert result.exit_code == 0, result.output
    saved = parse_state((vault / '.obforce/state.json').read_bytes())
    assert len(saved.notes) == len(saved.evidence.components) == 12 and saved.dashboard is not None
    first = vault / saved.notes[0].note.path
    human = b'aliases: ["Human alias"]\ntechnical_debt_custom: "human"\n'
    first.write_bytes(first.read_bytes().replace(b'---\n', b'---\n' + human, 1) + b'\nHuman prose\n- one\n  - two\n')
    moved = vault / 'Team Notes/Class0000.md'
    moved.parent.mkdir()
    first.rename(moved)
    (vault / '.obsidian').mkdir()
    (vault / '.obsidian/settings.json').write_bytes(b'{"human":true}\n')
    (vault / 'Ordinary.md').write_bytes(b'Ordinary human knowledge\n')
    xml = source / 'package/classes/Class0000.cls-meta.xml'
    xml.write_bytes(xml.read_bytes().replace(b'67.0', b'68.0'))
    protected = snapshot(source), config.read_bytes(), snapshot(vault / '.obsidian')
    before = snapshot(root)
    assert invoke('sync', '--config', config, '--dry-run').exit_code == 0
    assert snapshot(root) == before
    result = invoke('sync', '--config', config)
    assert result.exit_code == 0, result.output
    current = parse_state((vault / '.obforce/state.json').read_bytes())
    assert [n.note.obforce_id for n in current.notes] == [n.note.obforce_id for n in saved.notes]
    assert current.notes[0].note.path == 'Team Notes/Class0000.md'
    assert human in moved.read_bytes() and b'Human prose\n- one\n  - two\n' in moved.read_bytes()
    assert (snapshot(source), config.read_bytes(), snapshot(vault / '.obsidian')) == protected
    before = snapshot(root)
    for command in (['sync'], ['sync', '--dry-run'], ['recover'], ['recover', '--dry-run'], ['build']):
        result = invoke(*command, '--config', config)
        assert result.exit_code == (3 if command == ['build'] else 0), result.output
        assert snapshot(root) == before
    # One edited generated asset blocks a pending note update, preserving the complete batch.
    asset = vault / current.dashboard.path
    asset.write_bytes(asset.read_bytes() + b'# Human edit\n')
    xml.write_bytes(xml.read_bytes().replace(b'68.0', b'69.0'))
    before = snapshot(root)
    for flags in (['--dry-run'], []):
        result = invoke('sync', '--config', config, *flags)
        assert result.exit_code == 3, result.output
        assert snapshot(root) == before


def main() -> None:
    """Run installed finite-bound/lifecycle qualification with application runtime denial."""
    for event in ('socket.connect', 'subprocess.Popen'):
        try:
            sys.audit(event)
        except RuntimeError:
            pass
        else:
            raise AssertionError('Active runtime network/process guard required')
    cwd = snapshot(Path.cwd())
    with tempfile.TemporaryDirectory(prefix='obforce-qualification-') as temporary:
        root = Path(temporary).resolve()
        # Actual transaction gate, just beyond the ceiling. The 1000-note case is
        # run separately by the qualification suite; neither uses raised limits.
        publication_refusal(root / 'Over Bound', 127)
        lifecycle(root / 'Within Bound')
    assert snapshot(Path.cwd()) == cwd


if __name__ == '__main__':
    main()
