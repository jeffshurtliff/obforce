# -*- coding: utf-8 -*-
"""
:Module:            dev.probe_dashboard
:Synopsis:          Probes protected installed dashboard journeys under active runtime denial
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     26 Oct 2026
"""

from __future__ import annotations

import json
import sys
import tempfile
from dataclasses import replace
from importlib.resources import files
from pathlib import Path

from click.testing import CliRunner
from ruamel.yaml import YAML

from obforce.cli import main as cli
from obforce.renderer.dashboards import render_dashboard
from obforce.sync import transactions
from obforce.sync.notes import parse_note
from obforce.sync.state import parse_state, serialize_state


def invoke(*args: object):
    """Invoke only installed command code; runtime child processes remain denied."""
    return CliRunner().invoke(cli, [str(a) for a in args])


def snapshot(root: Path) -> dict:
    """Capture exact synthetic bytes/mtimes and directory membership."""
    return {
        p.relative_to(root).as_posix(): (p.stat().st_mtime_ns, p.read_bytes() if p.is_file() else None)
        for p in (root, *root.rglob('*'))
    }


def setup(root: Path):
    """Prepare a fictional project and config outside checkout and working directory."""
    source = root / 'Fictional Project'
    classes = source / 'package/classes'
    classes.mkdir(parents=True)
    (source / 'sfdx-project.json').write_text('{"packageDirectories":[{"path":"package"}]}', encoding='utf-8')
    (classes / 'Alpha.cls').write_text('// Fictional source\n', encoding='utf-8')
    (classes / 'Alpha.cls-meta.xml').write_text(
        '<ApexClass xmlns="http://soap.sforce.com/2006/04/metadata">'
        '<apiVersion>67.0</apiVersion><status>Active</status></ApexClass>',
        encoding='utf-8',
    )
    config, vault = root / 'Config with spaces.toml', root / 'Vault with spaces'
    assert (
        invoke('init', '--config', config, '--source', source.name, '--vault', vault.name, '--workspace-id', 'demo').exit_code
        == 0
    )
    return source, config, vault


def document(vault: Path):
    """Read only a selected synthetic state record."""
    return parse_state((vault / '.obforce/state.json').read_bytes())


def seed_prior_asset(vault: Path) -> bytes:
    """Prepare a synthetic previously accepted presentation revision, never runtime adoption."""
    saved = document(vault)
    prior = replace(saved.dashboard, content=saved.dashboard.content + b'# Synthetic prior asset revision\n')
    (vault / prior.path).write_bytes(prior.content)
    (vault / '.obforce/state.json').write_bytes(serialize_state(replace(saved, dashboard=prior)))
    return prior.content


def main() -> None:
    """Verify resources, existing-vault addition, preservation, conflicts and recovery."""
    for event in ('socket.connect', 'subprocess.Popen'):
        try:
            sys.audit(event)
        except RuntimeError:
            pass
        else:
            raise AssertionError('Runtime guard missing')
    cwd = Path.cwd()
    cwd_before = snapshot(cwd)
    assert files('obforce').joinpath('resources/bases/apex_classes.base').read_bytes() == render_dashboard()
    base = YAML(typ='safe').load(render_dashboard())
    assert base['formulas']['class_link'] == 'file.asLink(note.sf_full_name)'
    assert base['properties']['note.technical_debt']['displayName'] == 'Technical Debt'
    assert 'formula.debt_assessment' not in base['views'][0]['order']
    assert len(base['views']) == 1 and set(base['formulas']) == {'class_link'}
    with tempfile.TemporaryDirectory(prefix='obforce-dashboard-') as temporary:
        root = Path(temporary).resolve()
        source, config, vault = setup(root)
        before = snapshot(root)
        assert invoke('build', '--config', config, '--dry-run').exit_code == 0
        assert snapshot(root) == before and not vault.exists()
        assert invoke('build', '--config', config).exit_code == 0
        saved = document(vault)
        asset = vault / saved.dashboard.path
        assert asset.read_bytes() == saved.dashboard.content == render_dashboard()
        note = vault / saved.notes[0].note.path
        properties = parse_note(note.read_bytes()).properties
        assert properties['technical_debt'] is False and properties['sf_api_version'] == '67.0'
        assert properties['tech_debt_severity'] == properties['tech_debt_status'] == ''
        assert properties['last_reviewed'] is None
        assert 'sf_created' not in properties and 'sf_last_modified' not in properties
        human = b'technical_debt: false # human\naliases: ["Team"]\ntags: ["human"]\ntechnical_debt_custom: null'
        note.write_bytes(
            note.read_bytes().replace(b'"technical_debt": false', human).replace(b'"tags": ["salesforce"]\n', b'')
            + b'\nHuman prose\n- one\n  - two\n'
        )
        for flags in (['--dry-run'], []):
            before = snapshot(root)
            result = invoke('sync', '--config', config, *flags)
            assert result.exit_code == 0, result.output
            assert snapshot(root) == before
        # A valid Thread 13 document remains valid; only an absent new asset is created.
        asset.unlink()
        old_state = serialize_state(replace(saved, dashboard=None))
        (vault / '.obforce/state.json').write_bytes(old_state)
        before, note_bytes = snapshot(root), note.read_bytes()
        assert invoke('sync', '--config', config, '--dry-run').exit_code == 0
        assert snapshot(root) == before
        assert invoke('sync', '--config', config).exit_code == 0
        assert note.read_bytes() == note_bytes and document(vault).notes == saved.notes
        assert asset.read_bytes() == render_dashboard()
        # Human dashboard edits block the whole batch, including changed source facts.
        asset.write_bytes(asset.read_bytes() + b'# Human dashboard edit\n')
        metadata = source / 'package/classes/Alpha.cls-meta.xml'
        metadata.write_text(metadata.read_text().replace('67.0', '68.0'), encoding='utf-8')
        before = snapshot(root)
        for flags in (['--dry-run'], []):
            result = invoke('sync', '--config', config, *flags)
            assert result.exit_code == 3, result.output
            assert snapshot(root) == before
        asset.write_bytes(render_dashboard())  # Explicit synthetic fixture restoration.
        assert invoke('sync', '--config', config).exit_code == 0
        assert human in note.read_bytes() and b'68.0' in note.read_bytes()
        for phase in ('published', 'commit'):
            prior = seed_prior_asset(vault)
            prior_state = (vault / '.obforce/state.json').read_bytes()
            checkpoint = transactions._checkpoint

            def fail(boundary, index=-1, selected=phase):
                if boundary == selected and (boundary != 'published' or index == 0):
                    raise OSError('Synthetic asset interruption')

            transactions._checkpoint = fail
            try:
                result = invoke('sync', '--config', config)
                assert result.exit_code == 3 and 'recovery_required: true' in result.output, result.output
            finally:
                transactions._checkpoint = checkpoint
            journal = json.loads((vault / '.obforce/journal.json').read_bytes())
            assert [entry['path'] for entry in journal['entries']] == [saved.dashboard.path, '.obforce/state.json']
            before = snapshot(root)
            assert invoke('recover', '--config', config).exit_code == 0
            assert snapshot(root) == before
            assert invoke('recover', '--config', config, '--cleanup' if phase == 'commit' else '--rollback').exit_code == 0
            if phase == 'published':
                assert asset.read_bytes() == prior and (vault / '.obforce/state.json').read_bytes() == prior_state
            else:
                assert asset.read_bytes() == render_dashboard()
            assert invoke('sync', '--config', config).exit_code == 0
        before = snapshot(root)
        assert invoke('sync', '--config', config).exit_code == 0 and snapshot(root) == before
    assert snapshot(cwd) == cwd_before


if __name__ == '__main__':
    main()
