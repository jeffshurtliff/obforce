# -*- coding: utf-8 -*-
"""
:Module:            tests.unit.test_dashboards
:Synopsis:          Verifies literal Bases syntax, exact ownership and recoverable asset batches
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     26 Oct 2026
"""

from __future__ import annotations

import ast
import base64
import json
import runpy
import socket
import subprocess
from dataclasses import replace
from pathlib import Path

import pytest
from ruamel.yaml import YAML

from obforce import constants as const
from obforce.config import Layout
from obforce.errors import ConflictError, ModelError
from obforce.renderer.dashboards import dashboard_path, render_dashboard, validate_dashboard_content
from obforce.sync import transactions
from obforce.sync.state import SavedDashboard, parse_state, serialize_state

_HELPERS = runpy.run_path(str(Path(__file__).resolve().parents[2] / 'dev/probe_dashboard.py'))
invoke, snapshot, setup, document, seed_prior = (
    _HELPERS[n] for n in ('invoke', 'snapshot', 'setup', 'document', 'seed_prior_asset')
)


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError('Runtime network/process access forbidden')

    monkeypatch.setattr(socket, 'socket', deny)
    monkeypatch.setattr(subprocess, 'Popen', deny)


@pytest.fixture
def vault(tmp_path):
    source, config, vault = setup(tmp_path.resolve())
    result = invoke('build', '--config', config)
    assert result.exit_code == 0, result.output
    return tmp_path.resolve(), source, config, vault


def evaluate(expression, note):
    """Interpret only the documented expression subset for synthetic data, never eval/Python code.

    This independently checks packaged predicates/formulas, not Obsidian rendering.
    """

    def visit(node):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            return {'note': note, 'null': None, 'true': True, 'false': False}[node.id]
        if isinstance(node, ast.Attribute):
            return visit(node.value).get(node.attr)
        if isinstance(node, ast.Compare):
            a, b = visit(node.left), visit(node.comparators[0])
            equal = type(a) is type(b) and a == b
            return equal if isinstance(node.ops[0], ast.Eq) else not equal
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == 'choose':
                return visit(node.args[1] if visit(node.args[0]) else node.args[2])
            if isinstance(node.func, ast.Attribute) and node.func.attr == 'isType':
                return type(visit(node.func.value)) is {'string': str, 'boolean': bool}[visit(node.args[0])]
        raise AssertionError('Unexpected Bases test expression')

    return visit(ast.parse(expression.replace('if(', 'choose('), mode='eval').body)


def test_packaged_schema_filters_columns_and_no_external_dependency():
    raw = render_dashboard()
    base = YAML(typ='safe').load(raw)
    assert set(base) == {'filters', 'formulas', 'properties', 'views'}
    assert set(base['filters']) == {'and'} and len(base['filters']['and']) == 5
    assert base['filters']['and'][0] == 'file.ext == "md"'
    filters = base['filters']['and'][1:]
    good = {'obforce_id': '00000000-0000-4000-8000-000000000001', 'obforce_schema': 1, 'sf_type': 'ApexClass'}
    for update in ({}, {'type': 'human', 'tags': []}):
        assert all(evaluate(f, good | update) for f in filters)
    for update in (
        {'obforce_id': None},
        {'obforce_id': ''},
        {'obforce_id': 42},
        {'obforce_schema': True},
        {'obforce_schema': 2},
        {'sf_type': 'Flow'},
    ):
        assert not all(evaluate(f, good | update) for f in filters)
    assert not all(evaluate(f, {'type': 'salesforce_component', 'tags': ['salesforce']}) for f in filters)
    assert 'file.asLink(note.sf_full_name)' == base['formulas']['class_link']
    (view,) = base['views']
    assert view['type'] == 'table' and view['name'] == 'Apex Classes'
    columns = view['order']
    assert set(columns) == set(base['properties']) and columns[0] == 'formula.class_link'
    assert {
        'formula.class_link',
        'note.sf_namespace',
        'note.sf_status',
        'note.sf_api_version',
        'note.sf_created',
        'note.sf_last_modified',
        'note.technical_debt',
        'note.tech_debt_severity',
        'note.tech_debt_status',
        'note.last_reviewed',
    } <= set(columns)
    assert b'file.mtime' not in raw and b'file.ctime' not in raw and b'hasTag' not in raw
    assert b'Dataview' not in raw and b'inFolder' not in raw and b'http' not in raw


@pytest.mark.parametrize('suffix', [b'\r\n', b'\x00\n', b'\xff\n', b'# obforce:dashboard:duplicate\n'])
def test_saved_content_rejects_controls_encoding_and_duplicate_indicators(suffix):
    with pytest.raises((ModelError, UnicodeError)):
        validate_dashboard_content(render_dashboard() + suffix)


def test_asset_and_path_bounds(monkeypatch):
    assert dashboard_path(Layout(dashboards='Team Space/Bases')) == 'Team Space/Bases/Apex Classes.base'
    monkeypatch.setattr(const, 'MAX_DASHBOARD_BYTES', 8)
    with pytest.raises(ModelError):
        render_dashboard()
    with pytest.raises(ConflictError):
        SavedDashboard('Dashboards/Apex Classes.base', b'x' * 9)


@pytest.mark.parametrize(
    'field,value',
    [
        ('dashboard_schema', True),
        ('dashboard_schema', 2),
        ('dashboard_schema', '1'),
        ('path', '../Apex Classes.base'),
        ('path', '.obsidian/Apex Classes.base'),
        ('path', 'Dashboards/Other.base'),
        ('content_hash', 'a' * 64),
        ('content', ''),
        ('content', '!!!!'),
        ('content', base64.b64encode(b'bad').decode()),
    ],
)
def test_exact_state_extension_refuses_tampering_and_creates_nothing(vault, field, value):
    root, _, _, output = vault
    data = document(output).canonical()
    data['dashboard'][field] = value
    before = snapshot(root)
    with pytest.raises(ConflictError):
        parse_state(json.dumps(data).encode())
    assert snapshot(root) == before


def test_state_extension_legacy_shapes_and_unknown_keys(vault):
    root, _, _, output = vault
    saved = document(output)
    assert parse_state(serialize_state(saved)) == saved
    old = replace(saved, dashboard=None)
    assert 'dashboard' not in old.canonical() and parse_state(serialize_state(old)) == old
    for value in (None, {}, dict(saved.dashboard.canonical(), future=True)):
        with pytest.raises(ConflictError):
            parse_state(json.dumps(old.canonical() | {'dashboard': value}).encode())
    before = snapshot(root)
    with pytest.raises(ConflictError):
        replace(saved, evidence=None)
    assert snapshot(root) == before


@pytest.mark.parametrize(
    'change',
    [
        'edit',
        'strip-marker',
        'missing',
        'move',
        'duplicate',
        'config',
        'case-parent',
        'unowned-identical',
        'unowned-different',
        'file-parent',
        'note-edit',
        'oversized-base',
    ],
)
def test_any_asset_ownership_conflict_blocks_entire_source_update(vault, change):
    root, source, config, output = vault
    saved = document(output)
    asset = output / saved.dashboard.path
    metadata = source / 'package/classes/Alpha.cls-meta.xml'
    metadata.write_text(metadata.read_text().replace('67.0', '68.0'), encoding='utf-8')
    if change == 'edit':
        asset.write_bytes(asset.read_bytes() + b'# Human edit\n')
    elif change == 'strip-marker':
        asset.write_bytes(asset.read_bytes().split(b'\n', 1)[1])
    elif change == 'missing':
        asset.unlink()
    elif change == 'move':
        asset.rename(output / 'Moved.base')
    elif change == 'duplicate':
        (output / 'Copy.base').write_bytes(asset.read_bytes())
    elif change == 'config':
        config.write_text(config.read_text() + '\n[layout]\ndashboards = "Other"\n', encoding='utf-8')
    elif change == 'case-parent':
        asset.parent.rename(output / 'DASHBOARDS')
    elif change.startswith('unowned'):
        (output / '.obforce/state.json').write_bytes(serialize_state(replace(saved, dashboard=None)))
        if change == 'unowned-different':
            asset.write_text('views: []\n', encoding='utf-8')
    elif change == 'file-parent':
        asset.unlink()
        asset.parent.rmdir()
        (output / '.obforce/state.json').write_bytes(serialize_state(replace(saved, dashboard=None)))
        asset.parent.write_text('Human file\n', encoding='utf-8')
    elif change == 'note-edit':
        seed_prior(output)  # A pending dashboard update must also be blocked.
        note = output / saved.notes[0].note.path
        note.write_bytes(note.read_bytes().replace(b'"sf_status": "Active"', b'"sf_status": "Human edit"'))
    else:
        (output / 'Human.base').write_bytes(b'x' * (const.MAX_DASHBOARD_BYTES + 1))
    before = snapshot(root)
    for flags in (['--dry-run'], []):
        result = invoke('sync', '--config', config, *flags)
        assert result.exit_code == 3, (change, result.output, result.exception)
        assert snapshot(root) == before


def test_first_asset_from_thread13_and_combined_human_content_preservation(vault):
    root, source, config, output = vault
    saved = document(output)
    asset = output / saved.dashboard.path
    asset.unlink()
    asset.parent.rmdir()
    old = replace(saved, dashboard=None)
    (output / '.obforce/state.json').write_bytes(serialize_state(old))
    note = output / saved.notes[0].note.path
    note.write_bytes(
        note.read_bytes().replace(
            b'"technical_debt": false', b'technical_debt: false # human\ntechnical_debt_other: "kept"\naliases: ["A"]'
        )
        + b'\nHuman\n  - indentation\n'
    )
    moved = output / 'Human Location/Alpha.md'
    moved.parent.mkdir()
    note.rename(moved)
    (output / 'Human.base').write_text('views: []\n', encoding='utf-8')
    (output / '.obsidian').mkdir()
    (output / '.obsidian/settings.json').write_bytes(b'private fictional settings')
    before = snapshot(root)
    assert invoke('sync', '--config', config, '--dry-run').exit_code == 0
    assert snapshot(root) == before
    note_before = moved.read_bytes()
    result = invoke('sync', '--config', config)
    assert result.exit_code == 0, result.output
    assert asset.read_bytes() == render_dashboard() and moved.read_bytes() == note_before
    assert document(output).notes[0].note.obforce_id == old.notes[0].note.obforce_id
    assert document(output).notes[0].note.path == 'Human Location/Alpha.md'
    protected = snapshot(source)
    before = snapshot(root)
    assert invoke('sync', '--config', config).exit_code == 0 and snapshot(root) == before
    assert snapshot(source) == protected


@pytest.mark.parametrize(
    'phase,index',
    [
        ('ready', -1),
        ('published', 0),
        ('published', 1),
        ('commit', -1),
        ('cleanup_before', 0),
        ('cleanup', 1),
        ('cleanup_final', -1),
    ],
)
@pytest.mark.parametrize('new_asset', [False, True])
def test_asset_recovery_restores_prior_state_or_cleans_committed(vault, monkeypatch, phase, index, new_asset):
    root, _, config, output = vault
    saved = document(output)
    asset = output / saved.dashboard.path
    if new_asset:
        asset.unlink()
        (output / '.obforce/state.json').write_bytes(serialize_state(replace(saved, dashboard=None)))
        prior = None
    else:
        prior = seed_prior(output)
    prior_state = (output / '.obforce/state.json').read_bytes()

    def fail(name, number=-1):
        if (name, number) == (phase, index):
            raise OSError('Synthetic interruption')

    monkeypatch.setattr(transactions, '_checkpoint', fail)
    result = invoke('sync', '--config', config)
    assert result.exit_code == 3 and 'recovery_required: true' in result.output, result.output
    monkeypatch.setattr(transactions, '_checkpoint', lambda *args: None)
    before = snapshot(root)
    assert invoke('recover', '--config', config).exit_code == 0
    assert snapshot(root) == before
    committed = phase in {'commit', 'cleanup_before', 'cleanup', 'cleanup_final'}
    result = invoke('recover', '--config', config, '--cleanup' if committed else '--rollback')
    assert result.exit_code == 0, result.output
    if committed:
        assert asset.read_bytes() == render_dashboard() and document(output).dashboard is not None
    else:
        assert (asset.read_bytes() if asset.exists() else None) == prior
        assert (output / '.obforce/state.json').read_bytes() == prior_state
    assert invoke('sync', '--config', config).exit_code == 0


@pytest.mark.parametrize('phase', ['published', 'commit'])
@pytest.mark.parametrize('changed', ['dashboard', 'unchanged-dashboard', 'state', 'note'])
def test_intervening_edits_refuse_recovery_without_mutation(vault, monkeypatch, phase, changed):
    root, source, config, output = vault
    if changed == 'unchanged-dashboard':
        metadata = source / 'package/classes/Alpha.cls-meta.xml'
        metadata.write_text(metadata.read_text().replace('67.0', '68.0'), encoding='utf-8')
    else:
        seed_prior(output)

    def fail(name, index=-1):
        if name == phase and (name != 'published' or index == 0):
            raise OSError('Synthetic failure')

    monkeypatch.setattr(transactions, '_checkpoint', fail)
    assert invoke('sync', '--config', config).exit_code == 3
    monkeypatch.setattr(transactions, '_checkpoint', lambda *args: None)
    saved = document(output)
    path = output / (
        saved.dashboard.path
        if 'dashboard' in changed
        else '.obforce/state.json'
        if changed == 'state'
        else saved.notes[0].note.path
    )
    path.write_bytes(path.read_bytes() + b'\nHuman intervention\n')
    before = snapshot(root)
    for flags in ([], ['--rollback'], ['--cleanup']):
        assert invoke('recover', '--config', config, *flags).exit_code == 3
        assert snapshot(root) == before


@pytest.mark.parametrize(
    'change', ['remove', 'move', 'state-only', 'unowned-before', 'before-bytes', 'after-bytes', 'extra-target']
)
def test_recovery_semantics_refuse_asset_state_mismatch(vault, monkeypatch, change):
    root, _, config, output = vault
    seed_prior(output)

    def fail(name, index=-1):
        if name == 'ready':
            raise OSError('Synthetic interruption')

    monkeypatch.setattr(transactions, '_checkpoint', fail)
    assert invoke('sync', '--config', config).exit_code == 3
    journal = json.loads((output / '.obforce/journal.json').read_bytes())
    content = []
    for index, entry in enumerate(journal['entries']):
        content.append(
            {
                label: (output / f'.obforce/transaction/{index:04d}.{label}').read_bytes()
                for label in ('before', 'after')
                if entry[label] is not None
            }
        )
    after = parse_state(content[-1]['after'])
    if change in {'remove', 'move', 'state-only'}:
        after = replace(
            after,
            dashboard=None
            if change == 'remove'
            else replace(after.dashboard, path='Other/Apex Classes.base')
            if change == 'move'
            else replace(after.dashboard, content=after.dashboard.content + b'# Not published\n'),
        )
        content[-1]['after'] = serialize_state(after)
    elif change == 'unowned-before':
        content[-1]['before'] = serialize_state(replace(parse_state(content[-1]['before']), dashboard=None))
    elif change in {'before-bytes', 'after-bytes'}:
        content[0]['before' if change == 'before-bytes' else 'after'] += b'# forged\n'
    else:
        journal['entries'].insert(1, dict(journal['entries'][0], path='Other/Apex Classes.base'))
        content.insert(1, dict(content[0]))
    before = snapshot(root)
    with pytest.raises(ConflictError):
        transactions._semantics(journal, content, output, transactions._Reader())
    assert snapshot(root) == before


@pytest.mark.parametrize('change', ['asset', 'bytes', 'omit', 'intent'])
def test_independent_writer_revalidation_refuses_forged_dashboard_candidate(vault, change):
    from obforce.config import load_config
    from obforce.sync.engine import _excluded
    from obforce.sync.transactions import TransactionInputs, publish_plan

    root, _, config, output = vault
    saved = document(output)
    seed_prior(output)
    inputs = TransactionInputs(
        output,
        output / '.obforce/state.json',
        saved.evidence.components,
        saved.coverage,
        saved.evidence.graph,
        _excluded(load_config(config)),
        persist_evidence=True,
        include_dashboard=True,
    )
    plan = inputs.plan()
    assert not plan.blocked and plan.dashboard.content_changed
    if change == 'asset':
        plan = replace(plan, dashboard=replace(plan.dashboard, content_changed=False))
    elif change == 'bytes':
        plan = replace(plan, state_bytes=plan.state_bytes + b' ')
    elif change == 'omit':
        plan = replace(plan, dashboard=None)
    else:
        inputs = replace(inputs, include_dashboard=False)
    before = snapshot(root)
    assert publish_plan(plan, inputs).outcome == 3
    assert snapshot(root) == before
