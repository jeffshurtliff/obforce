# -*- coding: utf-8 -*-
"""
:Module:            tests.integration.test_sync_lifecycle
:Synopsis:          Exercises independent synthetic refresh, evidence and preservation lifecycles
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     26 Oct 2026
"""

from __future__ import annotations

import json
import socket
import subprocess
from dataclasses import replace
from types import SimpleNamespace

import pytest
from click.testing import CliRunner

from obforce import constants as const
from obforce.cli import main
from obforce.errors import ConflictError, OperationalError
from obforce.graph.dependencies import DependencyGraph, Edge, Endpoint, Evidence
from obforce.models import (
    Availability,
    CollectionCoverage,
    Component,
    ComponentKey,
    Coverage,
    CoverageStatus,
    FieldValue,
    Selection,
    SourceBinding,
)
from obforce.sources import live, relationships
from obforce.sync import transactions
from obforce.sync.state import parse_state, serialize_state


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError('Runtime network/process access forbidden')

    monkeypatch.setattr(socket, 'socket', deny)
    monkeypatch.setattr(subprocess, 'Popen', deny)


def invoke(*args):
    return CliRunner().invoke(main, [str(a) for a in args])


def tree(root):
    return {
        p.relative_to(root).as_posix(): (p.stat().st_mtime_ns, p.read_bytes() if p.is_file() else None)
        for p in (root, *root.rglob('*'))
    }


def xml(version='67.0'):
    return (
        '<ApexClass xmlns="http://soap.sforce.com/2006/04/metadata">'
        f'<apiVersion>{version}</apiVersion><status>Active</status></ApexClass>'
    )


@pytest.fixture
def local_vault(tmp_path):
    root = tmp_path.resolve()
    source = root / 'Fictional Project'
    classes = source / 'package/classes'
    classes.mkdir(parents=True)
    (source / 'sfdx-project.json').write_text('{"packageDirectories":[{"path":"package"}]}')
    for name in ('Alpha', 'Beta'):
        (classes / f'{name}.cls').write_text('// Fictional source, not read')
        (classes / f'{name}.cls-meta.xml').write_text(xml())
    config = root / 'Config with spaces.toml'
    result = invoke('init', '--config', config, '--source', source.name, '--vault', 'Vault', '--workspace-id', 'demo')
    assert result.exit_code == 0, result.output
    assert invoke('build', '--config', config).exit_code == 0
    return root, source, config, root / 'Vault'


def state(vault):
    return parse_state((vault / '.obforce/state.json').read_bytes())


def test_independent_multi_run_offline_moves_debt_new_absent_templates_noop(local_vault):
    root, source, config, vault = local_vault
    saved = state(vault)
    assert saved.canonical()['state_schema'] == 2 and all(n.note.schema_version == 1 for n in saved.notes)
    alpha = vault / saved.notes[0].note.path
    alpha.write_bytes(
        alpha.read_bytes().replace(
            b'"technical_debt": null', b'technical_debt: false # human\naliases: ["Team Alpha"]\ntechnical_debt_status: reviewed'
        )
        + b'\nHuman context\n- one\n  - two\n'
    )
    moved = vault / 'Team Notes/Alpha.md'
    moved.parent.mkdir()
    alpha.rename(moved)
    classes = source / 'package/classes'
    (classes / 'Alpha.cls-meta.xml').write_text(xml('68.0'))
    (classes / 'Beta.cls-meta.xml').unlink()  # Partial offline input cannot retire Beta.
    (classes / 'Gamma.cls').write_text('// Fictional')
    (classes / 'Gamma.cls-meta.xml').write_text(xml())
    (vault / '.obsidian').mkdir()
    (vault / '.obsidian/settings.json').write_text('{"fictional":true}')
    source_before = tree(source)
    before = tree(root)
    result = invoke('sync', '--config', config, '--dry-run')
    assert result.exit_code == 4, (result.output, result.exception)
    assert tree(root) == before
    result = invoke('sync', '--config', config)
    assert result.exit_code == 4, (result.output, result.exception)
    current = state(vault)
    assert len(current.notes) == len(current.evidence.components) == 3
    assert current.notes[0].note.obforce_id == saved.notes[0].note.obforce_id
    assert current.notes[0].note.path == 'Team Notes/Alpha.md'
    assert all(n.note.generated_properties['sf_lifecycle'].value == 'active' for n in current.notes)
    assert b'technical_debt: false # human' in moved.read_bytes()
    assert b'aliases: ["Team Alpha"]' in moved.read_bytes() and b'\n  - two\n' in moved.read_bytes()
    assert b'- api_version: "68.0"' in moved.read_bytes()
    before = tree(root)
    assert invoke('sync', '--config', config).exit_code == 4
    assert tree(root) == before and tree(source) == source_before
    assert invoke('build', '--config', config).exit_code == 3
    templates = root / 'Templates'
    templates.mkdir()
    (templates / 'apex_created.md.j2').write_text('Invalid creation asset is irrelevant to existing notes')
    config.write_text(config.read_text() + '\n[templates]\ndirectory="./Templates"\n')
    before = tree(root)
    assert invoke('sync', '--config', config).exit_code == 4
    assert tree(root) == before
    (templates / 'apex_generated.md.j2').write_text(
        '{{ metadata | section }}\n{{ coverage | section }}\n'
        '{{ references | section }}\n{{ referenced_by | section }}\nExtra generated text\n',
        encoding='utf-8',
        newline='\n',
    )
    assert b'\r' not in (templates / 'apex_generated.md.j2').read_bytes()
    result = invoke('sync', '--config', config)
    assert result.exit_code == 4, (result.output, result.exception)
    assert b'Extra generated text' in moved.read_bytes() and b'Human context' in moved.read_bytes()
    before = tree(root)
    assert invoke('sync', '--config', config).exit_code == 4 and tree(root) == before


@pytest.mark.parametrize('preview', [False, True])
def test_crlf_generated_override_refuses_without_writes(local_vault, preview):
    """Refuse Windows-style template bytes before publishing any pending change."""
    root, source, config, vault = local_vault
    note = vault / state(vault).notes[0].note.path
    note.write_bytes(note.read_bytes() + b'\nHuman context remains unchanged.\n')
    (source / 'package/classes/Alpha.cls-meta.xml').write_text(xml('68.0'))
    templates = root / 'Templates'
    templates.mkdir()
    config.write_text(config.read_text() + '\n[templates]\ndirectory="./Templates"\n', encoding='utf-8', newline='\n')
    template = templates / 'apex_generated.md.j2'
    template.write_text(
        '{{ metadata | section }}\n{{ coverage | section }}\n'
        '{{ references | section }}\n{{ referenced_by | section }}\nExtra generated text\n',
        encoding='utf-8',
        newline='\r\n',
    )
    assert b'\r\n' in template.read_bytes()
    before = tree(root)
    result = invoke('sync', '--config', config, *(['--dry-run'] if preview else []))
    assert result.exit_code == 2, (result.output, result.exception)
    assert 'Template contains reserved or invalid structure' in result.output
    assert tree(root) == before


@pytest.mark.parametrize(
    'damage',
    [
        'generated',
        'property',
        'duplicate',
        'missing_state',
        'legacy',
        'bad_source_hash',
        'extra_fact',
        'unknown',
        'missing_evidence',
        'duplicate_fact',
        'wrong_graph',
    ],
)
def test_conflict_refuses_whole_batch_without_human_or_source_change(local_vault, damage):
    root, source, config, vault = local_vault
    path = vault / '.obforce/state.json'
    document = json.loads(path.read_bytes())
    note = vault / state(vault).notes[0].note.path
    if damage == 'generated':
        note.write_bytes(note.read_bytes().replace(b'- ApexClass:', b'- Human edited ApexClass:'))
    elif damage == 'property':
        note.write_bytes(note.read_bytes().replace(b'"sf_status": "Active"', b'"sf_status": "Human"'))
    elif damage == 'duplicate':
        (vault / 'Duplicate.md').write_bytes(note.read_bytes())
    elif damage == 'missing_state':
        path.unlink()
    else:
        if damage == 'legacy':
            document.pop('evidence')
            document['state_schema'] = 1
        elif damage == 'bad_source_hash':
            document['evidence']['components'][0]['attributes']['status']['value'] = 'Deleted'
        elif damage in ('extra_fact', 'duplicate_fact'):
            extra = json.loads(json.dumps(document['evidence']['components'][0]))
            if damage == 'extra_fact':
                extra['key'][3] = 'Untracked'
            document['evidence']['components'].append(extra)
        elif damage == 'unknown':
            document['evidence']['evidence_schema'] = 99
        elif damage == 'missing_evidence':
            document.pop('evidence')
        elif damage == 'wrong_graph':
            document['evidence']['graph']['coverage']['method'] = 'changed'
        path.write_text(json.dumps(document))
    (source / 'package/classes/Beta.cls-meta.xml').write_text(xml('68.0'))
    before = tree(root)
    for flags in ([], ['--dry-run']):
        result = invoke('sync', '--config', config, *flags)
        assert result.exit_code == 3, (damage, result.output, result.exception)
        assert tree(root) == before


@pytest.mark.parametrize('limit,expected', [('MAX_EVIDENCE_BYTES', 3), ('MAX_STATE_NODES', 3), ('MAX_TRANSACTION_FILES', 2)])
def test_refresh_bounds_preserve_whole_tree(local_vault, monkeypatch, limit, expected):
    root, source, config, _ = local_vault
    (source / 'package/classes/Alpha.cls-meta.xml').write_text(xml('68.0'))
    monkeypatch.setattr(const, limit, 1)
    before = tree(root)
    result = invoke('sync', '--config', config)
    assert result.exit_code == expected, (result.output, result.exception)
    assert tree(root) == before


@pytest.fixture
def live_vault(tmp_path, monkeypatch):
    root = tmp_path.resolve()
    neutral = root / 'Neutral'
    neutral.mkdir()
    config = root / 'Live.toml'
    assert invoke('init', '--config', config, '--org', 'fictional', '--vault', 'Vault', '--workspace-id', 'demo').exit_code == 0
    binding = SourceBinding('demo', 'live', '00D000000000001EAA')
    inv = CollectionCoverage(CoverageStatus.COMPLETE, const.LIVE_APEX_METHOD, pagination='exhausted', limit_reached=False)
    rel = CollectionCoverage(CoverageStatus.PARTIAL, const.RELATIONSHIP_METHOD, requested=True)
    audit = CollectionCoverage(CoverageStatus.UNAVAILABLE, 'omitted', requested=False)
    coverage = Coverage(binding, Selection(), inv, audit, rel)
    components = tuple(
        Component(
            binding,
            ComponentKey('demo', 'ApexClass', None, name),
            {'status': FieldValue(Availability.VALUE, 'Active')},
            record_id=f'01p00000000000{number}AAA',
        )
        for number, name in enumerate(('Alpha', 'Beta'), 1)
    )
    edge = Edge(
        *(Endpoint('ApexClass', None, c.key.full_name, c.record_id, c.key, 'resolved') for c in components),
        (Evidence('fictional', rel),),
    )
    current = {'components': components, 'coverage': coverage, 'edges': (edge,), 'calls': 0}

    def collect(executable, **kwargs):
        current['calls'] += 1
        if kwargs.get('state_binding') is not None:
            assert kwargs['state_binding'] == binding  # Independent adapter re-verifies this binding in production.
        return SimpleNamespace(components=current['components'], coverage=current['coverage'])

    def graph(executable, **kwargs):
        cov = current['coverage']
        return SimpleNamespace(graph=DependencyGraph(cov.binding, cov.selection, cov.relationships, current['edges']))

    monkeypatch.setattr(live, 'collect_live', collect)
    monkeypatch.setattr(relationships, 'collect_relationships', graph)
    flags = ['--config', config, '--sf-executable', root / 'fictional-sf', '--sf-directory', neutral]
    assert invoke('build', *flags, '--inventory-scope-id', 'fictional-reader-v1').exit_code == 4
    return root, config, root / 'Vault', flags, current


def test_live_missing_stale_incoming_move_reactivate_and_stability(live_vault):
    root, _, vault, flags, current = live_vault
    saved = state(vault)
    moved = vault / 'Moved Beta.md'
    (vault / saved.notes[1].note.path).rename(moved)
    current['edges'] = ()
    current['components'] = current['components'][1:]
    before = tree(root)
    assert invoke('sync', *flags, '--dry-run').exit_code == 4 and tree(root) == before
    assert invoke('sync', *flags).exit_code == 4
    now = state(vault)
    assert now.notes[0].note.generated_properties['sf_lifecycle'].value == 'active'
    assert now.evidence.graph.edges[0].stale
    assert b'Moved Beta' in (vault / now.notes[0].note.path).read_bytes()
    before = tree(root)
    assert invoke('sync', *flags).exit_code == 4 and tree(root) == before
    attestation = ['--inventory-scope-id', 'fictional-reader-v1', '--attest-comparable-inventory']
    assert invoke('sync', *flags, *attestation).exit_code == 4
    assert state(vault).notes[0].note.generated_properties['sf_lifecycle'].value == 'missing'
    current['components'] = saved.evidence.components
    assert invoke('sync', *flags).exit_code == 4
    assert all(s.note.generated_properties['sf_lifecycle'].value == 'active' for s in state(vault).notes)
    # A positively complete attested empty scan marks all missing without deleting notes.
    current['components'] = ()
    assert invoke('sync', *flags, *attestation).exit_code == 4
    assert all(s.note.generated_properties['sf_lifecycle'].value == 'missing' for s in state(vault).notes)
    before = tree(root)
    assert invoke('sync', *flags, *attestation).exit_code == 4 and tree(root) == before


@pytest.mark.parametrize('kind', ['partial', 'failed', 'org', 'filter', 'method', 'scope', 'no_scope', 'version'])
def test_live_incomplete_or_changed_scope_never_infers_absence(live_vault, monkeypatch, kind):
    root, config, vault, flags, current = live_vault
    current['components'], current['edges'] = (), ()
    extra = ['--inventory-scope-id', 'fictional-reader-v1', '--attest-comparable-inventory']
    expected = 3
    if kind == 'partial':
        current['coverage'] = replace(
            current['coverage'],
            inventory=replace(current['coverage'].inventory, status=CoverageStatus.PARTIAL, pagination='incomplete'),
        )
        expected = 4
    elif kind == 'failed':

        def fail(*args, **kwargs):
            raise OperationalError('Fictional required acquisition failure')

        monkeypatch.setattr(live, 'collect_live', fail)
        expected = 1
    elif kind == 'org':
        current['coverage'] = replace(current['coverage'], binding=SourceBinding('demo', 'live', '00D000000000002EAA'))
    elif kind == 'filter':
        config.write_text(config.read_text() + '\n[options]\ninclude_namespaced=true\n')
    elif kind in ('method', 'version'):
        change = {'method': 'different'} if kind == 'method' else {'api_version': '99.0'}
        current['coverage'] = replace(current['coverage'], inventory=replace(current['coverage'].inventory, **change))
    elif kind == 'scope':
        extra[1] = 'different'
    else:
        extra = ['--attest-comparable-inventory']
        expected = 2
    before = tree(root)
    result = invoke('sync', *flags, *extra)
    assert result.exit_code == expected, (kind, result.output, result.exception)
    if kind != 'partial':
        assert tree(root) == before
    assert all(n.note.generated_properties['sf_lifecycle'].value == 'active' for n in state(vault).notes)


@pytest.mark.parametrize('boundary', ['ready', 'published', 'published_state', 'commit', 'cleanup_before'])
@pytest.mark.parametrize('human_edit', [False, True])
def test_refresh_interruption_recovery_preserves_evidence_and_intervening_edits(local_vault, monkeypatch, boundary, human_edit):
    root, source, config, vault = local_vault
    previous = (vault / '.obforce/state.json').read_bytes()
    (source / 'package/classes/Alpha.cls-meta.xml').write_text(xml('68.0'))
    before_notes = {n.note.path: (vault / n.note.path).read_bytes() for n in state(vault).notes}

    def fail(name, index=-1):
        reached = (
            (name == 'published' and index == 1)
            if boundary == 'published_state'
            else (name == boundary and (name != 'published' or index == 0))
        )
        if reached:
            raise OSError('Synthetic interruption')

    monkeypatch.setattr(transactions, '_checkpoint', fail)
    result = invoke('sync', '--config', config)
    assert result.exit_code == 3 and 'recovery_required: true' in result.output, (result.output, result.exception)
    monkeypatch.setattr(transactions, '_checkpoint', lambda *args: None)
    before = tree(root)
    assert invoke('sync', '--config', config).exit_code == 3 and tree(root) == before
    operation = '--cleanup' if boundary in ('commit', 'cleanup_before') else '--rollback'
    if human_edit:
        note = vault / next(iter(before_notes))
        note.write_bytes(note.read_bytes() + b'\nIntervening human edit\n')
        before = tree(root)
        result = invoke('recover', '--config', config, operation)
        assert result.exit_code == 3 and tree(root) == before
    else:
        result = invoke('recover', '--config', config, operation)
        assert result.exit_code == 0, (result.output, result.exception)
        recovered = state(vault)
        assert recovered.evidence is not None
        if operation == '--rollback':
            assert (vault / '.obforce/state.json').read_bytes() == previous
            assert all((vault / p).read_bytes() == raw for p, raw in before_notes.items())
        assert invoke('sync', '--config', config).exit_code == 0


def test_evidence_roundtrip_and_no_new_history(local_vault):
    root, _, config, vault = local_vault
    saved = state(vault)
    assert serialize_state(parse_state(serialize_state(saved))) == serialize_state(saved)
    assert saved.evidence.canonical()['inventory_scope'] is None
    assert 'collected_at' not in json.dumps(saved.evidence.canonical())
    before = tree(root)
    assert invoke('sync', '--config', config).exit_code == 0
    assert tree(root) == before
    with pytest.raises(ConflictError):
        parse_state(serialize_state(saved).replace(b'"evidence_schema":1', b'"evidence_schema":true'))


@pytest.mark.parametrize(
    'damage',
    [
        'duplicate_edge',
        'duplicate_observation',
        'bad_resolution',
        'foreign_key',
        'changed_path_hash',
        'scope_type',
        'scope_method',
        'extra_graph_key',
        'component_binding',
        'noncanonical_id',
        'empty_namespace',
        'model_schema',
    ],
)
def test_private_live_evidence_rejects_tampering_before_acquisition(live_vault, damage):
    root, _, vault, flags, current = live_vault
    filename = vault / '.obforce/state.json'
    data = json.loads(filename.read_bytes())
    evidence = data['evidence']
    if damage == 'duplicate_edge':
        evidence['graph']['edges'] *= 2
    elif damage == 'duplicate_observation':
        evidence['graph']['edges'][0]['evidence'] *= 2
    elif damage == 'bad_resolution':
        evidence['graph']['edges'][0]['source']['resolution'] = 'external'
    elif damage == 'foreign_key':
        evidence['graph']['edges'][0]['source']['key'][0] = 'foreign'
    elif damage == 'changed_path_hash':
        data['notes'][0]['note']['graph_hash'] = '0' * 64
    elif damage == 'scope_type':
        evidence['inventory_scope']['scope_id'] = True
    elif damage == 'scope_method':
        evidence['inventory_scope']['method'] = 'unproven'
    elif damage == 'extra_graph_key':
        evidence['graph']['raw_response'] = 'forbidden'
    elif damage == 'component_binding':
        evidence['components'][0]['binding']['workspace_id'] = 'foreign'
    elif damage == 'noncanonical_id':
        evidence['components'][0]['record_id'] = evidence['components'][0]['record_id'][:15]
    elif damage == 'empty_namespace':
        evidence['components'][0]['key'][2] = ''
    else:
        evidence['components'][0]['model_schema'] = True
    filename.write_text(json.dumps(data))
    before, calls = tree(root), current['calls']
    result = invoke('sync', *flags)
    assert result.exit_code == 3, (damage, result.output, result.exception)
    assert current['calls'] == calls and tree(root) == before


def test_null_live_scope_cannot_be_initialized_by_sync(live_vault):
    root, _, vault, flags, current = live_vault
    filename = vault / '.obforce/state.json'
    data = json.loads(filename.read_bytes())
    data['evidence']['inventory_scope'] = None  # Equivalent to a build with no optional declaration.
    filename.write_text(json.dumps(data, indent=2))
    current['components'], current['edges'] = (), ()
    before = tree(root)
    result = invoke('sync', *flags, '--inventory-scope-id', 'fictional-reader-v1', '--attest-comparable-inventory')
    assert result.exit_code == 3 and tree(root) == before
    assert invoke('sync', *flags).exit_code == 4
    assert all(n.note.generated_properties['sf_lifecycle'].value == 'active' for n in state(vault).notes)
    assert state(vault).evidence.inventory_scope is None


def test_formatted_valid_state_is_byte_stable_on_noop(local_vault):
    root, _, config, vault = local_vault
    filename = vault / '.obforce/state.json'
    filename.write_text(json.dumps(json.loads(filename.read_bytes()), indent=2))
    before = tree(root)
    assert invoke('sync', '--config', config).exit_code == 0
    assert tree(root) == before
