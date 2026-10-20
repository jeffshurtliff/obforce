# -*- coding: utf-8 -*-
"""
:Module:            tests.unit.test_planner
:Synopsis:          Verifies complete synthetic read-only plans and bounded private reporting
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     20 Oct 2026
"""

from __future__ import annotations

import hashlib
import json
import os
import socket
import stat
import subprocess
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from obforce import constants as const
from obforce.config import Options
from obforce.errors import ExitCode, ModelError
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
from obforce.renderer.templates import TemplateAsset, load_template
from obforce.sync import planner as module
from obforce.sync import state as state_module
from obforce.sync.notes import parse_note
from obforce.sync.planner import ActionKind, ChangeAction, plan_changes
from obforce.sync.reporting import report_plan
from obforce.sync.state import serialize_state


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError('Runtime network/process access forbidden')

    monkeypatch.setattr(socket, 'socket', deny)
    monkeypatch.setattr(subprocess, 'Popen', deny)


def tree(root):
    """Snapshot bytes, mtimes and complete tree, excluding atime read side effects."""
    return {
        p.relative_to(root).as_posix(): (p.lstat().st_mtime_ns, p.read_bytes() if p.is_file() and not p.is_symlink() else None)
        for p in (root, *root.rglob('*'))
    }


def source(*, live=False, names=('Alpha', 'Beta', 'Gamma')):
    binding = SourceBinding('fictional', 'live', '00D000000000001EAA') if live else SourceBinding('fictional', 'local')
    inventory = CollectionCoverage(
        CoverageStatus.COMPLETE,
        const.LIVE_APEX_METHOD if live else 'synthetic-local',
        pagination='exhausted',
        limit_reached=False,
    )
    audit = CollectionCoverage(CoverageStatus.UNAVAILABLE, 'offline-or-omitted-audit', requested=False)
    relationships = CollectionCoverage(
        CoverageStatus.PARTIAL if live else CoverageStatus.NOT_COLLECTED, 'synthetic-reported', requested=live
    )
    coverage = Coverage(binding, Selection(), inventory, audit, relationships)
    components = tuple(
        Component(
            binding, ComponentKey('fictional', 'ApexClass', None, name), {'status': FieldValue(Availability.VALUE, 'Active')}
        )
        for name in names
    )
    return components, coverage, DependencyGraph(binding, coverage.selection, relationships)


def edge(a, b, coverage):
    return Edge(
        Endpoint('ApexClass', None, a.key.full_name, '01p000000000001AAA', a.key, 'resolved'),
        Endpoint('ApexClass', None, b.key.full_name, '01p000000000002AAA', b.key, 'resolved'),
        (Evidence('synthetic-reference', coverage),),
    )


def plan(vault, components, coverage, graph, **kwargs):
    options = dict(excluded_roots=(), verified_org_id=coverage.binding.org_id)
    options.update(kwargs)
    return plan_changes(vault, vault / '.obforce/state.json', components, coverage, graph, **options)


def seed_baseline(vault, candidate, *, ending=b'\n', human=False):
    """Explicit synthetic fixture setup only; never application publication code."""
    assert not candidate.blocked, report_plan(candidate).text
    saved = []
    for action in candidate.actions:
        raw = action.content.replace(b'\n', ending)
        if human:
            raw = raw.replace(b'"type": "salesforce_component"', b'type: "team_record" # custom type')
            raw = raw.replace(b'"technical_debt": null', b'technical_debt: false # retained assessment')
            raw += b'Private human narrative with Unicode caf\xc3\xa9' + ending
        path = vault / action.path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        parsed = parse_note(raw)
        saved.append(
            replace(
                action.saved,
                note=replace(action.saved.note, generated_region_hash=parsed.region_hash),
                generated_region=parsed.region,
            )
        )
    document = replace(candidate.state, notes=tuple(saved))
    state_path = vault / '.obforce/state.json'
    state_path.parent.mkdir(exist_ok=True)
    state_path.write_bytes(serialize_state(document))
    return document


@pytest.fixture
def initial(tmp_path):
    vault = (tmp_path / 'synthetic-vault').resolve()
    vault.mkdir()
    return vault, *source()


@pytest.mark.parametrize('ending', [b'\n', b'\r\n'])
def test_stable_create_repeat_and_next_baseline_noop(initial, ending):
    vault, components, coverage, graph = initial
    (vault / 'Ordinary.md').write_bytes(b'Unowned narrative\n')
    before, inputs = tree(vault), tuple(c.canonical() for c in components)
    first = plan(vault, components, coverage, graph, initial=True)
    assert not first.blocked and first.outcome == 0
    assert first.state_changed and all(a.kind == ActionKind.CREATE for a in first.actions)
    repeated = plan(vault, tuple(reversed(components)), coverage, graph, initial=True)
    assert first == repeated and first.state_bytes == repeated.state_bytes
    assert len({a.identity for a in first.actions}) == 3
    assert all(a.creation_hash and a.saved.note.render_hash != a.creation_hash for a in first.actions)
    assert tree(vault) == before and tuple(c.canonical() for c in components) == inputs
    assert b'Ordinary' not in first.state_bytes
    assert any(o.path == vault / '.obforce/state.json' and o.stamp is None for o in first.preconditions)
    assert all(a.content and b'Private' not in repr(a).encode() for a in first.actions)
    seed_baseline(vault, first, ending=ending, human=True)
    before = tree(vault)
    next_plan = plan(vault, components, coverage, graph, previous_graph=graph)
    assert not next_plan.blocked and not next_plan.state_changed
    assert all(a.kind == ActionKind.NO_OP and not a.content_changed and not a.state_changed for a in next_plan.actions)
    assert next_plan.state_bytes == (vault / '.obforce/state.json').read_bytes()
    assert all(a.content == (vault / a.path).read_bytes() for a in next_plan.actions)
    assert all(
        a.saved.note.generated_region_hash == hashlib.sha256(a.saved.generated_region).hexdigest() for a in next_plan.actions
    )
    assert any(
        o.content_hash == hashlib.sha256((vault / a.path).read_bytes()).hexdigest()
        for a in next_plan.actions
        for o in next_plan.preconditions
        if o.path == vault / a.path
    )
    assert tree(vault) == before


def assert_blocked(candidate, code=3):
    assert candidate.blocked and candidate.outcome == code
    assert candidate.state is candidate.state_bytes is candidate.graph is None
    assert not candidate.preconditions and not candidate.state_changed
    assert all(a.content is a.saved is None for a in candidate.actions)
    if code == 3:
        assert candidate.actions == (ChangeAction(ActionKind.CONFLICT),)
    else:
        assert candidate.actions == ()


@pytest.mark.parametrize(
    'edit',
    [
        'body',
        'property',
        'id',
        'schema',
        'line_endings',
        'duplicate_id',
        'vanished',
        'missing_state',
        'empty_state',
        'unknown_state',
        'bad_hash',
        'baseline',
    ],
)
def test_ownership_conflict_blocks_entire_batch_and_writes_nothing(initial, edit):
    vault, components, coverage, graph = initial
    first = plan(vault, components, coverage, graph, initial=True)
    seed_baseline(vault, first)
    target = vault / first.actions[0].path
    raw = target.read_bytes()
    state_path = vault / '.obforce/state.json'
    if edit == 'body':
        target.write_bytes(raw.replace(b'## Salesforce Metadata', b'## private-sentinel'))
    elif edit == 'property':
        target.write_bytes(raw.replace(b'"sf_status": "Active"', b'"sf_status": "private-sentinel"'))
    elif edit == 'id':
        target.write_bytes(raw.replace(first.actions[0].identity.encode(), b'00000000-0000-4000-8000-000000000001'))
    elif edit == 'schema':
        target.write_bytes(raw.replace(b'"obforce_schema": 1', b'"obforce_schema": 999'))
    elif edit == 'line_endings':
        target.write_bytes(raw.replace(b'\n', b'\r\n'))
    elif edit == 'duplicate_id':
        (vault / 'Copy.md').write_bytes(raw)
    elif edit == 'vanished':
        target.unlink()
    elif edit == 'missing_state':
        state_path.unlink()
    elif edit == 'empty_state':
        state_path.write_bytes(b'')
    elif edit == 'unknown_state':
        state_path.write_bytes(b'{"state_schema":999}')
    else:
        data = json.loads(state_path.read_bytes())
        if edit == 'bad_hash':
            data['notes'][0]['note']['generated_region_hash'] = 'a' * 64
        else:
            data['notes'][0]['note']['generated_properties']['sf_status']['value'] = 'private-sentinel'
        state_path.write_text(json.dumps(data))
    before = tree(vault)
    result = plan(vault, components, coverage, graph, previous_graph=graph)
    assert_blocked(result)
    report = report_plan(result, details=True)
    assert 'private-sentinel' not in report.text and components[0].key.full_name not in report.text
    assert str(vault) not in report.text and 'private-sentinel' not in repr(result)
    assert tree(vault) == before


@pytest.mark.parametrize('live', [False, True])
def test_collection_order_time_user_edits_and_creation_template_do_not_churn(tmp_path, live):
    vault = tmp_path.resolve()
    components, coverage, graph = source(live=live)
    first = plan(vault, components, coverage, graph, initial=True)
    seed_baseline(vault, first, human=True)
    target = vault / first.actions[0].path
    raw = target.read_bytes()
    raw = raw.replace(b'"tags": ["salesforce"]', b'tags: [team, second] # human tags')
    raw = raw.replace(b'"technical_debt": null', b'technical_debt: false')
    raw = raw.replace(b'---\n', b'---\n', 1)
    # Insert every supported kind of user-owned flat property without changing baselines.
    index = raw.index(b'---\n', 4)
    raw = (
        raw[:index]
        + (
            b'aliases: [demo]\nbusiness_owner: team\ntechnical_debt_status: reviewed\n'
            b'technical_debt_severity: 0\ntechnical_debt_review_date: "2026-10-20"\n'
        )
        + raw[index:]
    )
    target.write_bytes(raw + b'Additional human prose\n')
    before = tree(vault)
    asset = load_template('apex_created.md.j2')
    creation = TemplateAsset(asset.name, asset.text + '\nCreation template private-sentinel\n')
    changed_time = tuple(replace(c, collected_at='ignored-private-timestamp') for c in reversed(components))
    result = plan(vault, changed_time, coverage, graph, previous_graph=graph, creation_template=creation)
    assert not result.blocked and not result.state_changed
    assert all(a.kind == ActionKind.NO_OP for a in result.actions)
    assert tree(vault) == before


def test_existing_notes_patched_only_and_generated_template_changes(initial):
    vault, components, coverage, graph = initial
    first = plan(vault, components, coverage, graph, initial=True)
    seed_baseline(vault, first, ending=b'\r\n', human=True)
    asset = load_template('apex_generated.md.j2')
    template = TemplateAsset(asset.name, asset.text + '\nGenerated change\n')
    before = tree(vault)
    result = plan(vault, components, coverage, graph, previous_graph=graph, generated_template=template)
    assert not result.blocked and result.state_changed
    assert all(a.kind == ActionKind.UPDATE for a in result.actions)
    for action in result.actions:
        original, updated = parse_note((vault / action.path).read_bytes()), parse_note(action.content)
        assert action.content[updated.region_end :] == original.raw[original.region_end :]
        assert updated.properties['type'] == 'team_record' and updated.properties['technical_debt'] is False
        assert b'# custom type' in action.content and b'Private human' in action.content
        assert updated.region.endswith(b'\r\n')
        assert action.saved.note.source_hash == next(a.saved.note.source_hash for a in first.actions if a.key == action.key)
        assert action.saved.note.render_hash != next(a.saved.note.render_hash for a in first.actions if a.key == action.key)
    assert tree(vault) == before


@pytest.mark.parametrize('moved_index', [0, 1])
def test_graph_only_changes_and_both_move_directions_invalidate_neighbors(tmp_path, moved_index):
    vault = tmp_path.resolve()
    components, coverage, graph = source(live=True)
    first = plan(vault, components, coverage, graph, initial=True)
    seed_baseline(vault, first)
    a, b, c = components
    with_edge = replace(graph, edges=(edge(a, b, graph.coverage),))
    before = tree(vault)
    graph_plan = plan(vault, components, coverage, with_edge, previous_graph=graph)
    assert not graph_plan.blocked
    assert [item.kind for item in graph_plan.actions] == [ActionKind.UPDATE, ActionKind.UPDATE, ActionKind.NO_OP]
    assert all(
        item.saved.note.source_hash == original.saved.note.source_hash
        for item, original in zip(graph_plan.actions, first.actions, strict=True)
    )
    assert tree(vault) == before
    seed_baseline(vault, graph_plan)
    moved = graph_plan.actions[moved_index]
    (vault / moved.path).rename(vault / 'Moved.md')
    before = tree(vault)
    result = plan(vault, components, coverage, with_edge, previous_graph=with_edge)
    assert not result.blocked and result.state_changed
    assert result.actions[moved_index].kind == ActionKind.MOVE
    assert result.actions[moved_index].path == 'Moved.md' and result.actions[moved_index].prior_path == moved.path
    assert result.actions[1 - moved_index].kind == ActionKind.UPDATE
    assert result.actions[2].kind == ActionKind.NO_OP
    assert b'[[Moved.md|' in result.actions[1 - moved_index].content
    assert tree(vault) == before


def test_stale_edges_retained_and_repeat_stable(tmp_path):
    vault = tmp_path.resolve()
    components, coverage, graph = source(live=True)
    original = replace(graph, edges=(edge(components[0], components[1], graph.coverage),))
    first = plan(vault, components, coverage, original, initial=True)
    seed_baseline(vault, first)
    before = tree(vault)
    result = plan(vault, components, coverage, graph, previous_graph=original)
    assert not result.blocked and len(result.graph.edges) == 1 and result.graph.edges[0].stale
    assert result.graph.edges[0].evidence[0].coverage == graph.coverage
    assert tree(vault) == before
    seed_baseline(vault, result)
    again = plan(vault, components, coverage, graph, previous_graph=result.graph)
    assert not again.blocked and not again.state_changed
    assert all(a.kind == ActionKind.NO_OP for a in again.actions)


@pytest.mark.parametrize(
    'mode', ['complete', 'partial', 'unavailable', 'offline', 'not_comparable', 'other_method', 'api_changed']
)
def test_absence_requires_positive_supported_comparable_live_evidence(tmp_path, mode):
    vault = tmp_path.resolve()
    components, coverage, graph = source(live=mode != 'offline')
    first = plan(vault, components, coverage, graph, initial=True)
    seed_baseline(vault, first)
    current = components[1:]
    if mode in ('partial', 'unavailable'):
        coverage = replace(
            coverage,
            inventory=replace(coverage.inventory, status=CoverageStatus(mode), pagination='incomplete', limit_reached=None),
        )
    elif mode == 'other_method':
        coverage = replace(coverage, inventory=replace(coverage.inventory, method='unverified-method'))
    elif mode == 'api_changed':
        coverage = replace(coverage, inventory=replace(coverage.inventory, api_version='68.0'))
    before = tree(vault)
    result = plan(
        vault,
        current,
        coverage,
        graph,
        previous_graph=graph,
        retained_components=components[:1],
        comparable_live_inventory=mode != 'not_comparable',
    )
    assert not result.blocked
    lifecycle = result.actions[0].saved.note.generated_properties['sf_lifecycle'].value
    assert lifecycle == ('missing' if mode == 'complete' else 'active')
    assert (result.actions[0].kind == ActionKind.MISSING) == (mode == 'complete')
    assert all(a.kind != ActionKind.CREATE for a in result.actions)
    assert tree(vault) == before
    if mode == 'complete':
        seed_baseline(vault, result)
        again = plan(
            vault,
            current,
            coverage,
            graph,
            previous_graph=result.graph,
            retained_components=components[:1],
            comparable_live_inventory=True,
        )
        assert all(a.kind == ActionKind.NO_OP for a in again.actions)
        returned = plan(vault, components, coverage, graph, previous_graph=result.graph)
        assert returned.actions[0].kind == ActionKind.UPDATE
        assert returned.actions[0].saved.note.generated_properties['sf_lifecycle'].value == 'active'


@pytest.mark.parametrize(
    'mismatch',
    [
        'workspace',
        'mode',
        'org',
        'selection',
        'verification',
        'graph',
        'prior_graph',
        'no_prior_graph',
        'no_retained',
        'bad_retained',
        'extra_retained',
        'options',
    ],
)
def test_exact_bindings_scopes_and_retained_facts_refuse(tmp_path, mismatch):
    vault = tmp_path.resolve()
    components, coverage, graph = source(live=True)
    first = plan(vault, components, coverage, graph, initial=True)
    seed_baseline(vault, first)
    previous, kwargs = graph, {}
    if mismatch in ('workspace', 'mode', 'org'):
        binding = SourceBinding(
            'other' if mismatch == 'workspace' else 'fictional',
            'local' if mismatch == 'mode' else 'live',
            None if mismatch == 'mode' else '00D000000000002EAA' if mismatch == 'org' else coverage.binding.org_id,
        )
        components = tuple(replace(c, binding=binding, key=replace(c.key, workspace_id=binding.workspace_id)) for c in components)
        coverage = replace(coverage, binding=binding)
        graph = replace(graph, binding=binding)
    elif mismatch == 'selection':
        selection = Selection(full_names=('Alpha',))
        components = components[:1]
        coverage, graph = replace(coverage, selection=selection), replace(graph, selection=selection)
        previous = graph
    elif mismatch == 'verification':
        kwargs['verified_org_id'] = None
    elif mismatch == 'graph':
        graph = replace(graph, coverage=replace(graph.coverage, method='different'))
    elif mismatch == 'prior_graph':
        previous = replace(graph, edges=(edge(components[0], components[1], graph.coverage),))
    elif mismatch == 'no_prior_graph':
        previous = None
    elif mismatch == 'no_retained':
        components = components[1:]
    elif mismatch == 'bad_retained':
        kwargs['retained_components'] = (replace(components[0], attributes={}),)
        components = components[1:]
    elif mismatch == 'extra_retained':
        kwargs['retained_components'] = (components[0],)
    else:
        kwargs['options'] = Options(include_namespaced=True)
    before = tree(vault)
    result = plan(vault, components, coverage, graph, previous_graph=previous, **kwargs)
    assert_blocked(result)
    assert tree(vault) == before


@pytest.mark.parametrize(
    'path',
    [
        'Custom Code/Apex Classes/Alpha.md',
        'custom code',
        'Custom Code/Apex Classes',
        'Custom Code/Apex Classes/alpha.md',
        'Custom Code/Apex Classes/Alpha.md/Child.txt',
    ],
)
def test_proposed_paths_checked_against_unowned_files_and_parents(initial, path):
    vault, components, coverage, graph = initial
    target = vault / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b'Ordinary unowned human file\n')
    before = tree(vault)
    result = plan(vault, components, coverage, graph, initial=True)
    assert_blocked(result)
    assert tree(vault) == before


@pytest.mark.parametrize('names', [('Alpha', 'alpha'), ('Caf\u00e9', 'Cafe\u0301'), ('CON',), ('../Escape',), ('A#name',)])
def test_duplicate_portable_paths_unicode_reserved_and_traversal(tmp_path, names):
    components, coverage, graph = source(names=names)
    before = tree(tmp_path)
    result = plan(tmp_path.resolve(), components, coverage, graph, initial=True)
    assert result.blocked and result.outcome in (2, 3)
    assert tree(tmp_path) == before


def test_duplicate_components_and_duplicate_state_mappings(initial):
    vault, components, coverage, graph = initial
    before = tree(vault)
    assert_blocked(plan(vault, (*components, components[0]), coverage, graph, initial=True))
    assert tree(vault) == before
    first = plan(vault, components, coverage, graph, initial=True)
    seed_baseline(vault, first)
    path = vault / '.obforce/state.json'
    data = json.loads(path.read_bytes())
    data['notes'].append(data['notes'][0])
    path.write_text(json.dumps(data))
    before = tree(vault)
    assert_blocked(plan(vault, components, coverage, graph, previous_graph=graph))
    assert tree(vault) == before


@pytest.mark.parametrize('kind', ['symlink', 'hardlink', 'fifo', 'reparse'])
def test_unsafe_entries_refuse_without_artifacts(initial, kind, monkeypatch, tmp_path):
    vault, components, coverage, graph = initial
    outside = tmp_path / 'outside'
    outside.write_bytes(b'private-sentinel')
    path = vault / 'Unsafe.txt'
    if kind == 'symlink':
        try:
            path.symlink_to(outside)
        except OSError as error:
            if os.name == 'nt' and getattr(error, 'winerror', None) == 1314:
                pytest.skip('Native symlink privilege unavailable')
            raise
    elif kind == 'hardlink':
        os.link(outside, path)
    elif kind == 'fifo':
        if not hasattr(os, 'mkfifo'):
            pytest.skip('Native FIFO unavailable')
        os.mkfifo(path)
    else:
        path.write_bytes(b'private-sentinel')
        original = Path.lstat

        def reparse(self, *args, **kwargs):
            info = original(self, *args, **kwargs)
            if self == path:
                return SimpleNamespace(st_mode=info.st_mode, st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT)
            return info

        monkeypatch.setattr(Path, 'lstat', reparse)
    before = sorted(p.relative_to(vault).as_posix() for p in vault.rglob('*'))
    assert_blocked(plan(vault, components, coverage, graph, initial=True))
    assert sorted(p.relative_to(vault).as_posix() for p in vault.rglob('*')) == before
    assert outside.read_bytes() == b'private-sentinel'


def test_existing_and_new_paths_collide_without_adoption(initial):
    vault, components, coverage, graph = initial
    first = plan(vault, components[:1], coverage, graph, initial=True)
    seed_baseline(vault, first)
    (vault / first.actions[0].path).rename(vault / 'Custom Code/Apex Classes/Beta.md')
    before = tree(vault)
    assert_blocked(plan(vault, components, coverage, graph, previous_graph=graph))
    assert tree(vault) == before


@pytest.mark.parametrize('failure', ['late_note', 'late_state', 'late_parent', 'unreadable', 'partial_scan'])
def test_read_races_and_operational_failures_block_and_redact(initial, failure, monkeypatch):
    vault, components, coverage, graph = initial
    first = plan(vault, components, coverage, graph, initial=True)
    seed_baseline(vault, first)
    target = vault / first.actions[0].path
    before = tree(vault)
    original_scandir = state_module.os.scandir
    if failure in ('unreadable', 'partial_scan'):
        original = state_module.os.scandir

        def broken(path):
            if path == vault:
                raise PermissionError('private-sentinel') if failure == 'unreadable' else OSError('private-sentinel')
            return original(path)

        monkeypatch.setattr(state_module.os, 'scandir', broken)
    else:
        original = module.render_generated

        def race(*args, **kwargs):
            generated = original(*args, **kwargs)
            path = (
                target if failure == 'late_note' else vault / '.obforce/state.json' if failure == 'late_state' else target.parent
            )
            info = path.stat()
            os.utime(path, ns=(info.st_atime_ns, info.st_mtime_ns + 10_000_000))
            return generated

        monkeypatch.setattr(module, 'render_generated', race)
    result = plan(vault, components, coverage, graph, previous_graph=graph)
    monkeypatch.setattr(state_module.os, 'scandir', original_scandir)
    assert_blocked(result, 1 if failure in ('unreadable', 'partial_scan') else 3)
    assert 'private-sentinel' not in report_plan(result).text
    # The injected race itself changes mtime; the planner leaves bytes/tree untouched.
    after = tree(vault)
    assert before.keys() == after.keys() and all(before[k][1] == after[k][1] for k in before)


@pytest.mark.parametrize(
    'limit',
    [
        'MAX_PLAN_COMPONENTS',
        'MAX_PLAN_ACTIONS',
        'MAX_PLAN_INPUT_BYTES',
        'MAX_PLAN_OUTPUT_BYTES',
        'MAX_PLAN_PRECONDITIONS',
        'MAX_STATE_BYTES',
        'MAX_VAULT_READ_BYTES',
        'MAX_GRAPH_EDGES',
        'MAX_GRAPH_OBSERVATIONS',
    ],
)
def test_finite_bounds_refuse_without_writes(initial, limit, monkeypatch):
    vault, components, coverage, graph = initial
    kwargs = {'initial': True}
    if limit == 'MAX_VAULT_READ_BYTES':
        (vault / 'Ordinary.md').write_bytes(b'Ordinary narrative')
    if limit in ('MAX_GRAPH_EDGES', 'MAX_GRAPH_OBSERVATIONS'):
        components, coverage, graph = source(live=True)
        graph = replace(graph, edges=(edge(components[0], components[1], graph.coverage),))
    before = tree(vault)
    monkeypatch.setattr(const, limit, 0)
    result = plan(vault, components, coverage, graph, **kwargs)
    assert result.blocked and result.state is None and result.state_bytes is None and not result.preconditions
    assert tree(vault) == before


@pytest.mark.parametrize('field', ['api_version', 'status'])
@pytest.mark.parametrize(
    'value',
    [
        None,
        FieldValue(Availability.UNAVAILABLE),
        FieldValue(Availability.NULL),
        FieldValue(Availability.VALUE, False),
        FieldValue(Availability.VALUE, 0),
        FieldValue(Availability.VALUE, ''),
        FieldValue(Availability.VALUE, ()),
    ],
)
def test_absent_null_false_zero_empty_unavailable_remain_distinct(initial, field, value):
    vault, components, coverage, graph = initial
    component = replace(components[0], attributes={} if value is None else {field: value})
    first = plan(vault, (component,), coverage, graph, initial=True)
    assert not first.blocked
    assert first.actions[0].saved.note.source_hash == component.source_hash
    parsed = parse_note(first.actions[0].content)
    if value is None or value.availability == Availability.UNAVAILABLE:
        assert 'sf_' + field not in parsed.properties
    else:
        assert type(parsed.properties['sf_' + field]) is type(value.value)
        assert parsed.properties['sf_' + field] == value.value


def test_audit_omission_coverage_invalidation_and_safe_report(initial):
    vault, components, coverage, graph = initial
    component = replace(
        components[0], attributes={**components[0].attributes, 'created_by': FieldValue(Availability.VALUE, 'private-sentinel')}
    )
    first = plan(vault, (component,), coverage, graph, initial=True, options=Options(include_audit_names=False))
    assert not first.blocked and b'private-sentinel' not in first.actions[0].content
    seed_baseline(vault, first)
    changed = replace(
        coverage,
        inventory=replace(
            coverage.inventory, status=CoverageStatus.PARTIAL, pagination='incomplete', warnings=('private-sentinel',)
        ),
    )
    before = tree(vault)
    result = plan(vault, (component,), changed, graph, previous_graph=graph, options=Options(include_audit_names=False))
    assert not result.blocked and result.outcome == 4 and result.actions[0].kind == ActionKind.UPDATE
    report = report_plan(result, details=True)
    assert 'private-sentinel' not in report.text and 'Alpha' not in report.text and str(vault) not in report.text
    assert (
        'inventory: partial' in report.text
        and 'audit: unavailable' in report.text
        and 'relationships: not_collected' in report.text
    )
    assert result.actions[0].saved.note.source_hash == first.actions[0].saved.note.source_hash
    assert tree(vault) == before


@pytest.mark.parametrize(
    'codes,expected',
    [
        ((ExitCode.SUCCESS,), 0),
        ((ExitCode.INCOMPLETE,), 4),
        ((ExitCode.INCOMPLETE, ExitCode.OPERATIONAL), 1),
        ((ExitCode.OPERATIONAL, ExitCode.INVALID), 2),
        ((ExitCode.INVALID, ExitCode.CONFLICT), 3),
    ],
)
def test_report_counts_details_and_outcome_precedence(initial, codes, expected):
    vault, components, coverage, graph = initial
    candidate = plan(vault, components, coverage, graph, initial=True)
    report = report_plan(candidate, outcomes=codes)
    assert report.outcome == expected and f'outcome: {expected}' in report.text
    assert dict(candidate.counts)[ActionKind.CREATE] == 3 and sum(dict(candidate.counts).values()) == 3
    assert 'id:' not in report.text and 'id:' in report_plan(candidate, details=True).text
    assert report.text == report_plan(candidate, outcomes=tuple(reversed(codes))).text


def test_reporting_bounds_and_invalid_inputs_are_typed(initial, monkeypatch):
    vault, components, coverage, graph = initial
    candidate = plan(vault, components, coverage, graph, initial=True)
    before = tree(vault)
    monkeypatch.setattr(const, 'MAX_REPORT_ACTIONS', 1)
    with pytest.raises(ModelError):
        report_plan(candidate, details=True)
    monkeypatch.setattr(const, 'MAX_REPORT_BYTES', 1)
    with pytest.raises(ModelError):
        report_plan(candidate)
    for bad in (None, object(), 'private-sentinel'):
        with pytest.raises(ModelError) as caught:
            report_plan(bad)
        assert 'private-sentinel' not in str(caught.value)
    assert tree(vault) == before


def test_missing_initial_intent_noncanonical_state_and_no_source_discovery(initial, monkeypatch):
    vault, components, coverage, graph = initial
    assert_blocked(plan(vault, components, coverage, graph))
    first = plan(vault, components, coverage, graph, initial=True)
    seed_baseline(vault, first)
    state_path = vault / '.obforce/state.json'
    raw = json.dumps(json.loads(state_path.read_bytes()), indent=2).encode()
    state_path.write_bytes(raw)

    def deny(*args, **kwargs):
        raise AssertionError('Implicit discovery forbidden')

    monkeypatch.setattr(Path, 'cwd', deny)
    monkeypatch.setattr(Path, 'home', deny)
    before = tree(vault)
    candidate = plan(vault, components, coverage, graph, previous_graph=graph)
    assert not candidate.state_changed and candidate.state_bytes == raw
    assert tree(vault) == before


@pytest.mark.parametrize('changed', [None, 'path', 'parent', 'descriptor', 'birthtime'])
def test_windows_cross_api_bridge_keeps_same_api_change_guards(initial, monkeypatch, changed):
    vault, components, coverage, graph = initial
    first = plan(vault, components, coverage, graph, initial=True)
    seed_baseline(vault, first)
    target = vault / first.actions[0].path
    original_lstat, original_fstat = Path.lstat, os.fstat
    cross_api = state_module._cross_api_stamp
    monkeypatch.setattr(state_module, '_cross_api_stamp', lambda info: cross_api(info, windows=True))
    fields = ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
    calls, descriptor_calls = {}, [0]

    def by_path(path, *args, **kwargs):
        info = original_lstat(path, *args, **kwargs)
        values = {name: getattr(info, name) for name in fields}
        values.update(st_ctime_ns=10, st_birthtime_ns=10)
        calls[path] = calls.get(path, 0) + 1
        selected = target.parent if changed == 'parent' else target
        if changed in {'path', 'parent'} and path == selected and calls[path] > 1:
            values['st_ctime_ns'] += 1
        return SimpleNamespace(**values)

    def by_descriptor(fd):
        info = original_fstat(fd)
        values = {name: getattr(info, name) for name in fields}
        values.update(st_ctime_ns=20, st_birthtime_ns=10)
        descriptor_calls[0] += 1
        if descriptor_calls[0] == 2:
            if changed == 'descriptor':
                values['st_ctime_ns'] += 1
            elif changed == 'birthtime':
                values['st_birthtime_ns'] += 1
        return SimpleNamespace(**values)

    before = tree(vault)
    monkeypatch.setattr(Path, 'lstat', by_path)
    monkeypatch.setattr(os, 'fstat', by_descriptor)
    result = plan(vault, components, coverage, graph, previous_graph=graph)
    if changed is None:
        assert not result.blocked and not result.state_changed
        assert all(a.kind == ActionKind.NO_OP for a in result.actions)
    else:
        assert_blocked(result)
    monkeypatch.setattr(Path, 'lstat', original_lstat)
    monkeypatch.setattr(os, 'fstat', original_fstat)
    assert tree(vault) == before


@pytest.mark.parametrize('change', ['renderer', 'layout', 'options', 'coverage'])
def test_all_generated_fingerprint_inputs_invalidate_without_whole_note_replacement(initial, change, monkeypatch):
    vault, components, coverage, graph = initial
    first = plan(vault, components, coverage, graph, initial=True)
    seed_baseline(vault, first, human=True)
    kwargs = {}
    if change == 'renderer':
        monkeypatch.setattr(const, 'RENDERER_VERSION', const.RENDERER_VERSION + 1)
    elif change == 'layout':
        from obforce.config import Layout

        kwargs['layout'] = Layout(apex_classes='Other Classes')
    elif change == 'options':
        kwargs['options'] = Options(include_audit_names=False)
    else:
        coverage = replace(coverage, audit=replace(coverage.audit, method='changed-coverage'))
    before = tree(vault)
    result = plan(vault, components, coverage, graph, previous_graph=graph, **kwargs)
    assert not result.blocked and result.state_changed
    assert all(a.kind == ActionKind.UPDATE and a.state_changed for a in result.actions)
    for old, new in zip(first.actions, result.actions, strict=True):
        assert new.path == old.path and new.identity == old.identity
        assert new.saved.note.source_hash == old.saved.note.source_hash
        assert new.saved.note.render_hash != old.saved.note.render_hash
        assert b'Private human narrative' in new.content
    assert tree(vault) == before


@pytest.mark.parametrize(
    'invalid',
    [
        'components_list',
        'retained_list',
        'coverage',
        'graph',
        'comparable',
        'layout',
        'options',
        'initial',
        'relative_vault',
        'state_path',
        'excluded',
        'overlap',
    ],
)
def test_redacted_invalid_caller_contracts_and_overlap(initial, invalid):
    vault, components, coverage, graph = initial
    kwargs = dict(excluded_roots=(), initial=True)
    path = vault / '.obforce/state.json'
    if invalid == 'components_list':
        components = list(components)
    elif invalid == 'retained_list':
        kwargs['retained_components'] = []
    elif invalid == 'coverage':
        coverage = 'private-sentinel'
    elif invalid == 'graph':
        graph = 'private-sentinel'
    elif invalid == 'comparable':
        kwargs['comparable_live_inventory'] = 1
    elif invalid == 'layout':
        kwargs['layout'] = None
    elif invalid == 'options':
        kwargs['options'] = None
    elif invalid == 'initial':
        kwargs['initial'] = 1
    elif invalid == 'relative_vault':
        vault = Path('private-sentinel')
    elif invalid == 'state_path':
        path = vault / 'elsewhere.json'
    elif invalid == 'excluded':
        kwargs['excluded_roots'] = []
    else:
        kwargs['excluded_roots'] = (vault,)
    before = tree(initial[0])
    result = plan_changes(vault, path, components, coverage, graph, **kwargs)
    assert_blocked(result, 3 if invalid == 'overlap' else 2)
    assert 'private-sentinel' not in report_plan(result).text
    assert tree(initial[0]) == before


def test_new_uuid_policy_independent_of_layout_time_and_scope(initial):
    vault, components, coverage, graph = initial
    from obforce.config import Layout

    first = plan(vault, components[:1], coverage, graph, initial=True)
    second = plan(
        vault,
        (replace(components[0], collected_at='incidental'),),
        coverage,
        graph,
        initial=True,
        layout=Layout(apex_classes='Other'),
    )
    assert first.actions[0].identity == second.actions[0].identity == '7637447b-f5e1-54db-830d-d3ff73769182'
    assert first.actions[0].path != second.actions[0].path


def test_exact_hash_collision_never_bypasses_baseline_comparison(initial, monkeypatch):
    vault, components, coverage, graph = initial
    first = plan(vault, components, coverage, graph, initial=True)
    seed_baseline(vault, first)
    path = vault / first.actions[0].path
    path.write_bytes(path.read_bytes().replace(b'## Salesforce Metadata', b'## private-sentinel'))
    # The reconciliation compares exact saved bytes independently of every digest.
    monkeypatch.setattr(
        module,
        'render_generated',
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError('Rendering must not run after edited baseline')),
    )
    before = tree(vault)
    assert_blocked(plan(vault, components, coverage, graph, previous_graph=graph))
    assert tree(vault) == before


def test_empty_scope_requires_explicit_initial_and_remains_offline(initial):
    vault, components, coverage, graph = initial
    before = tree(vault)
    candidate = plan(vault, (), coverage, graph, initial=True)
    assert not candidate.blocked and candidate.actions == () and candidate.state.notes == ()
    assert candidate.state_changed and candidate.outcome == 0
    assert tree(vault) == before


def test_late_new_target_is_preserved_and_blocks_complete_plan(initial, monkeypatch):
    vault, components, coverage, graph = initial
    original = module.render_new_note
    target = vault / 'Custom Code/Apex Classes/Alpha.md'

    def race(*args, **kwargs):
        candidate = original(*args, **kwargs)
        if not target.exists():
            target.parent.mkdir(parents=True)
            target.write_bytes(b'Intervening unowned human file\n')
        return candidate

    monkeypatch.setattr(module, 'render_new_note', race)
    result = plan(vault, components, coverage, graph, initial=True)
    assert_blocked(result)
    assert target.read_bytes() == b'Intervening unowned human file\n'
    assert not (vault / '.obforce').exists()
    assert list(target.parent.iterdir()) == [target]


def test_safe_details_reject_fabricated_identity(initial):
    vault, components, coverage, graph = initial
    candidate = plan(vault, components, coverage, graph, initial=True)
    forged = replace(candidate, actions=(replace(candidate.actions[0], identity='private-sentinel\n'),))
    with pytest.raises(ModelError) as caught:
        report_plan(forged, details=True)
    assert 'private-sentinel' not in str(caught.value)


@pytest.mark.parametrize('phase', ['success', 'conflict', 'invalid', 'operational'])
def test_all_explicit_inputs_and_disjoint_source_tree_remain_immutable(tmp_path, phase, monkeypatch):
    vault = (tmp_path / 'vault').resolve()
    source_root = (tmp_path / 'source').resolve()
    vault.mkdir()
    source_root.mkdir()
    (source_root / 'Fictional.cls').write_bytes(b'// Synthetic source must stay untouched\n')
    components, coverage, graph = source()
    inputs = (tuple(c.canonical() for c in components), coverage.canonical(), graph)
    if phase == 'conflict':
        (vault / 'Managed.md').write_bytes(b'Untracked damaged obforce private-sentinel\n')
    elif phase == 'invalid':
        monkeypatch.setattr(const, 'MAX_PLAN_COMPONENTS', 0)
    elif phase == 'operational':

        def deny(*args, **kwargs):
            raise PermissionError('private-sentinel')

    before = tree(tmp_path)
    original_scandir = state_module.os.scandir
    if phase == 'operational':
        monkeypatch.setattr(state_module.os, 'scandir', deny)
    result = plan(vault, components, coverage, graph, initial=True, excluded_roots=(source_root,))
    monkeypatch.setattr(state_module.os, 'scandir', original_scandir)
    if phase == 'success':
        assert not result.blocked
    else:
        assert_blocked(result, {'conflict': 3, 'invalid': 2, 'operational': 1}[phase])
    assert tree(tmp_path) == before
    assert (tuple(c.canonical() for c in components), coverage.canonical(), graph) == inputs


@pytest.mark.parametrize('field,value', [('outcome', 'private-sentinel'), ('actions', None), ('blocked', 'private-sentinel')])
def test_report_malformed_result_refuses_with_redacted_typed_error(initial, field, value):
    vault, components, coverage, graph = initial
    candidate = plan(vault, components, coverage, graph, initial=True)
    with pytest.raises(ModelError) as caught:
        report_plan(replace(candidate, **{field: value}))
    assert 'private-sentinel' not in str(caught.value)


def test_busy_system_temp_ancestor_blocks_but_separate_runner_temp_stays_clean(tmp_path, monkeypatch):
    """Keep full parent checks while isolating fixtures from unrelated temp churn."""
    system_temp = tmp_path / 'shared-system-temp'
    runner_temp = tmp_path / 'dedicated-runner-temp'
    system_temp.mkdir()
    runner_temp.mkdir()
    shared_vault, isolated_vault = system_temp / 'vault', runner_temp / 'vault'
    shared_vault.mkdir()
    isolated_vault.mkdir()
    components, coverage, graph = source()
    inputs = (tuple(item.canonical() for item in components), coverage.canonical(), graph)
    original = module.render_new_note
    count = 0

    def unrelated_sibling(*args, **kwargs):
        nonlocal count
        candidate = original(*args, **kwargs)
        count += 1
        (system_temp / f'unrelated-{count}').mkdir()
        # Make the simulated concurrent directory change explicit on every host.
        stamp = system_temp.stat()
        os.utime(system_temp, ns=(stamp.st_atime_ns, stamp.st_mtime_ns + 10_000_000))
        return candidate

    monkeypatch.setattr(module, 'render_new_note', unrelated_sibling)
    shared_before, isolated_before = tree(shared_vault), tree(isolated_vault)
    assert_blocked(plan(shared_vault, components, coverage, graph, initial=True))
    isolated = plan(isolated_vault, components, coverage, graph, initial=True)
    assert not isolated.blocked, report_plan(isolated).text
    assert all(action.kind == ActionKind.CREATE for action in isolated.actions)
    assert tree(shared_vault) == shared_before and tree(isolated_vault) == isolated_before
    assert (tuple(item.canonical() for item in components), coverage.canonical(), graph) == inputs
