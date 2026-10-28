# -*- coding: utf-8 -*-
"""
:Module:            tests.unit.test_note_renderer
:Synopsis:          Verifies deterministic candidate contracts with synthetic metadata only
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     28 Oct 2026
"""

from __future__ import annotations

import json
import socket
import subprocess
from dataclasses import replace
from pathlib import Path

import pytest

from obforce import constants as const
from obforce.config import Options
from obforce.errors import ConfigError, ConflictError, ModelError
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
from obforce.renderer.notes import markdown, note_paths, render_generated, render_new_note
from obforce.renderer.templates import TemplateAsset, load_template

IDENTITY = '00000000-0000-4000-8000-000000000001'


@pytest.fixture
def example(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError('Runtime network/process access forbidden')

    monkeypatch.setattr(socket, 'socket', deny)
    monkeypatch.setattr(subprocess, 'Popen', deny)
    binding = SourceBinding('fictional', 'local')
    a = Component(
        binding,
        ComponentKey('fictional', 'ApexClass', None, 'DemoService'),
        {'api_version': FieldValue(Availability.VALUE, '68.0'), 'status': FieldValue(Availability.VALUE, 'Active')},
    )
    complete = CollectionCoverage(CoverageStatus.COMPLETE, 'synthetic-local', pagination='exhausted', limit_reached=False)
    audit = CollectionCoverage(CoverageStatus.UNAVAILABLE, 'offline-audit', requested=False)
    relations = CollectionCoverage(CoverageStatus.NOT_COLLECTED, 'offline-relationships', requested=False)
    coverage = Coverage(binding, Selection(), complete, audit, relations)
    graph = DependencyGraph(binding, coverage.selection, relations)
    return a, coverage, graph


def render(example, **kwargs):
    a, coverage, graph = example
    return render_new_note(a, coverage, graph, identity=IDENTITY, managed_paths=note_paths([a]), **kwargs)


def properties(text):
    raw = text.split('---\n', 2)[1]
    return {json.loads(key): json.loads(value) for key, value in (line.split(': ', 1) for line in raw.splitlines())}


def test_batch_paths_preserve_bytes_hashes_and_snapshot_caller_mutation(example):
    from obforce.renderer.notes import _BatchPaths

    component, coverage, graph = example
    paths = note_paths([component])
    batch = _BatchPaths(paths, component.binding.workspace_id)
    before = render_new_note(component, coverage, graph, identity=IDENTITY, managed_paths=paths)
    assert render_new_note(component, coverage, graph, identity=IDENTITY, managed_paths=batch) == before
    paths[component.key] = 'Moved/DemoService.md'
    assert render_new_note(component, coverage, graph, identity=IDENTITY, managed_paths=batch) == before
    moved = render_new_note(component, coverage, graph, identity=IDENTITY, managed_paths=paths)
    assert moved.path != before.path and moved.generated.graph_hash != before.generated.graph_hash
    with pytest.raises(TypeError):
        batch.source[component.key] = 'Changed.md'
    with pytest.raises(AttributeError):
        batch.source = paths


@pytest.mark.parametrize('defect', ['case', 'namespace', 'parent', 'reserved', 'workspace', 'key', 'component'])
def test_batch_paths_preserve_validation_and_combined_error_precedence(example, defect):
    from obforce.renderer.notes import _BatchPaths

    component, coverage, graph = example
    other = replace(component.key, full_name='Other')
    paths = {component.key: 'Classes/A.md', other: 'Classes/B.md'}
    if defect == 'case':
        paths[other] = 'classes/a.MD'
    elif defect == 'namespace':
        paths = {component.key: 'Classes/ns/A.md', other: 'Classes/NS/B.md'}
    elif defect == 'parent':
        paths[other] = 'Classes/A.md/B.md'
    elif defect == 'reserved':
        paths[other] = 'Classes/CON.md'
    elif defect == 'workspace':
        paths[replace(other, workspace_id='other')] = paths.pop(other)
    elif defect == 'key':
        paths['invalid-key'] = paths.pop(other)
    else:
        # Component/scope errors must still precede a simultaneous bad path map.
        component = replace(component, binding=SourceBinding('fictional', 'live', '00D000000000001EAA'))
        paths[other] = 'classes/a.MD'
    batch = _BatchPaths(paths, coverage.binding.workspace_id)
    outcomes = []
    for mapping in (paths, batch, batch):
        with pytest.raises((ModelError, ConflictError, ConfigError)) as error:
            render_generated(component, coverage, graph, identity=IDENTITY, managed_paths=mapping)
        outcomes.append((type(error.value), str(error.value)))
    assert outcomes[0] == outcomes[1] == outcomes[2]


def test_evidence_graph_validation_is_fresh_after_each_independent_pass(example, monkeypatch):
    from obforce.graph import dependencies
    from obforce.models import NoteState
    from obforce.sync.evidence import RefreshEvidence
    from obforce.sync.notes import parse_note
    from obforce.sync.state import SavedNote

    component, coverage, graph = example
    candidate = render(example)
    parsed = parse_note(candidate.text.encode())
    generated = candidate.generated
    note = NoteState(
        IDENTITY,
        component.binding,
        component.key,
        candidate.path,
        generated.source_hash,
        generated.graph_hash,
        generated.render_hash,
        parsed.generated_properties,
        parsed.region_hash,
    )
    saved = SavedNote(note, parsed.region)
    retained = RefreshEvidence((component,), graph)
    calls = []
    original = dependencies._checked_locations

    def checked(paths, workspace):
        calls.append(dict(paths))
        return original(paths, workspace)

    monkeypatch.setattr(dependencies, '_checked_locations', checked)
    retained.validate(coverage, (saved,))
    retained.validate(coverage, (saved,))
    assert len(calls) == 2
    moved = replace(saved, note=replace(note, path='Moved/DemoService.md'))
    with pytest.raises(ConflictError, match='Retained graph differs'):
        retained.validate(coverage, (moved,))
    assert len(calls) == 3 and calls[-1][component.key] == moved.note.path


def test_deterministic_snapshot_no_artifacts(example, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    first = render(example)
    assert first == render(example)
    assert first.path == 'Custom Code/Apex Classes/DemoService.md'
    snapshot = Path(__file__).parents[1] / 'fixtures/rendered/DemoService.md'
    assert first.text == snapshot.read_text()
    assert not list(tmp_path.iterdir())
    assert first.text.count(const.GENERATED_START) == first.text.count(const.GENERATED_END) == 1
    assert properties(first.text)['technical_debt'] is False
    assert first.text.split(const.GENERATED_START + '\n')[1].split(const.GENERATED_END)[0] == first.generated.region


@pytest.mark.parametrize('override', [False, True])
def test_nested_coverage_lists_use_four_spaces(example, tmp_path, monkeypatch, override):
    """Keep each facet's multiple warnings one four-space level below its bullet."""
    component, coverage, graph = example
    facets = ('inventory', 'audit', 'relationships')
    coverage = replace(
        coverage, **{name: replace(getattr(coverage, name), warnings=(f'{name}-one', '<unsafe>')) for name in facets}
    )
    graph = replace(graph, coverage=coverage.relationships)
    inputs = component.canonical(), coverage.canonical(), graph
    template = None
    if override:
        template = TemplateAsset(
            'apex_generated.md.j2',
            '{{ coverage | section }}\n\n{{ metadata | section }}\n\n'
            '{{ referenced_by | section }}\n\n{{ references | section }}\n',
        )
    monkeypatch.chdir(tmp_path)
    result = render((component, coverage, graph), generated_template=template)
    section = result.generated.region.split('## Coverage\n\n')[1].split('\n\n')[0]
    lines = section.splitlines()
    assert len(lines) == 9
    for index, name in enumerate(facets):
        assert lines[index * 3].startswith(f'- {name}: ')
        assert lines[index * 3 + 1] == '    - Warning: &#60;unsafe&#62;'
        assert lines[index * 3 + 2] == f'    - Warning: {name}-one'
    assert (component.canonical(), coverage.canonical(), graph) == inputs
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize('ending', [b'\n', b'\r\n'])
def test_indentation_upgrade_preserves_v2_baseline_and_human_content(example, monkeypatch, ending):
    """Patch only a validated old region; retain human spacing and refuse edits."""
    from obforce.models import NoteState
    from obforce.sync.notes import parse_note, patch_note
    from obforce.sync.state import SavedNote, StateDocument, parse_state, serialize_state

    component, coverage, graph = example
    coverage = replace(coverage, inventory=replace(coverage.inventory, warnings=('local_scope_only',)))
    current_example = component, coverage, graph
    current = render(current_example)
    with monkeypatch.context() as context:
        context.setattr(const, 'RENDERER_VERSION', 2)
        old_hash = render(current_example).generated.render_hash
    assert current.generated.render_hash != old_hash
    raw = current.text.replace('    - Warning:', '  - Warning:').replace(
        '"technical_debt": false', '"technical_debt": false # Human review\n"technical_debt_status": "reviewed"'
    )
    raw += '\n- Human list\n  - Keep two spaces\n    - Keep four spaces\n'
    raw = raw.encode().replace(b'\n', ending)
    note = parse_note(raw)
    state = NoteState(
        IDENTITY,
        component.binding,
        component.key,
        current.path,
        current.generated.source_hash,
        current.generated.graph_hash,
        old_hash,
        note.generated_properties,
        note.region_hash,
    )
    document = StateDocument(component.binding, coverage.selection, coverage, (SavedNote(state, note.region),))
    wire = serialize_state(document)
    assert serialize_state(parse_state(wire)) == wire
    result = patch_note(raw, state, note.region, current.generated)
    parsed = parse_note(result.content)
    assert result.changed and b'    - Warning: local_scope_only' in parsed.region
    assert result.content[: parsed.region_start] == raw[: note.region_start]
    assert result.content[parsed.region_end :] == raw[note.region_end :]
    assert parsed.properties['technical_debt'] is False and parsed.properties['technical_debt_status'] == 'reviewed'
    assert serialize_state(document) == wire
    edited = raw.replace(b'  - Warning: local_scope_only', b'  - Warning: human-edited')
    with pytest.raises(ConflictError):
        patch_note(edited, state, note.region, current.generated)


@pytest.mark.parametrize(
    'fields,expected',
    [
        ({}, 'absent (not supplied)'),
        ({'created_at': FieldValue(Availability.NULL)}, 'observed null'),
        ({'created_at': FieldValue(Availability.UNAVAILABLE)}, 'unavailable (not collected or accessible)'),
        ({'created_at': FieldValue(Availability.VALUE, False)}, 'false'),
    ],
)
def test_audit_absence_null_unavailable_false_distinct(example, fields, expected):
    a, cov, graph = example
    a = replace(a, attributes=fields)
    result = render((a, cov, graph))
    assert expected in result.generated.region
    if fields.get('created_at', FieldValue(Availability.UNAVAILABLE)).availability != Availability.VALUE:
        assert 'sf_created_at' not in properties(result.text)
    else:
        assert properties(result.text)['sf_created_at'] is False


def test_audit_names_omitted_even_if_available(example):
    a, cov, graph = example
    a = replace(a, attributes={'created_by': FieldValue(Availability.VALUE, 'Fictional Person')})
    result = render((a, cov, graph), options=Options(include_audit_names=False))
    assert 'Fictional Person' not in result.text and 'sf_created_by' not in properties(result.text)
    assert 'omitted by privacy option' in result.text


@pytest.mark.parametrize('value', [None, False, '', 0, ['[[DemoService]]'], ('a', 'b')])
def test_user_defaults_remain_flat_and_explicit(example, value):
    result = render(example, user_properties={'business_flag': value, 'aliases': ['Demo'], 'tags': ['custom']})
    assert properties(result.text)['business_flag'] == (list(value) if isinstance(value, tuple) else value)
    assert properties(result.text)['tags'] == ['custom']
    assert 'business_flag' not in result.generated.properties


@pytest.mark.parametrize('key', ['obforce_id', 'obforce_schema', 'sf_type', 'sf_unknown'])
def test_reserved_defaults_refused(example, key):
    with pytest.raises((ConflictError, ModelError)):
        render(example, user_properties={key: 'injection'})


@pytest.mark.parametrize('value', [{'nested': 'x'}, [False], 1.25, object(), float('nan')])
def test_unsafe_property_structures_refused(example, value):
    with pytest.raises(ModelError):
        render(example, user_properties={'business': value})


@pytest.mark.parametrize('identity', ['00000000-0000-4000-8000-00000000000A', 'bad', None, False])
def test_no_identity_generation(example, identity):
    a, cov, graph = example
    with pytest.raises(ModelError, match='UUID'):
        render_generated(a, cov, graph, identity=identity, managed_paths={})


@pytest.mark.parametrize('payload', ['<!-- obforce:generated:start -->', 'x\n---\nsf_type: fake', '\x00', '\u202e', '\ud800'])
def test_marker_and_control_injection_refused(example, payload):
    a, cov, graph = example
    a = replace(a, attributes={'status': FieldValue(Availability.VALUE, payload)})
    with pytest.raises(ModelError):
        render((a, cov, graph))


def test_yaml_markdown_and_link_injection_serialized(example):
    payload = '" : [x] !tag &anchor #hashtag [[evil]] <img> `code` **bold**'
    result = render(example, user_properties={'business': payload, 'aliases': ['[[User Link]]']})
    assert properties(result.text)['business'] == payload
    assert properties(result.text)['aliases'] == ['[[User Link]]']
    escaped = markdown(payload)
    assert '[[evil]]' not in escaped and '<img>' not in escaped and '**bold**' not in escaped
    assert '&#' in escaped


@pytest.mark.parametrize('name', ['../A', 'CON', 'LPT1', 'A/B', 'A\\B', 'A#x', 'A|x', 'A[x]', 'A.', 'A ', '.obsidian', 'A%20B'])
def test_unsafe_identity_paths_refused(example, name):
    a, _, _ = example
    key = replace(a.key, full_name=name) if name.strip() == name else None
    if key is None:
        with pytest.raises(ModelError):
            replace(a.key, full_name=name)
    else:
        with pytest.raises((ModelError, ConfigError)):
            note_paths([replace(a, key=key)])


@pytest.mark.parametrize('left,right', [('Demo', 'demo'), ('Café', 'Cafe\u0301')])
def test_case_unicode_component_collisions(example, left, right):
    a, _, _ = example
    with pytest.raises(ConflictError):
        note_paths([replace(a, key=replace(a.key, full_name=left)), replace(a, key=replace(a.key, full_name=right))])


def test_namespaced_paths_and_directory_spelling_collision(example):
    a, _, _ = example
    b = replace(a, key=replace(a.key, namespace='pkg'))
    assert note_paths([a, b])[b.key] == 'Custom Code/Apex Classes/pkg/DemoService.md'
    c = replace(a, key=replace(a.key, namespace='PKG', full_name='Different'))
    with pytest.raises(ConflictError):
        note_paths([b, c])


def live_graph(example):
    a, cov, _ = example
    binding = SourceBinding('fictional', 'live', '00D000000000001EAA')
    a = replace(a, binding=binding, record_id='01p000000000001AAA')
    b = replace(a, key=replace(a.key, namespace='pkg', full_name='Helper'), record_id='01p000000000002AAA')
    status = CollectionCoverage(CoverageStatus.PARTIAL, 'platform-mcd-equality-v1')
    cov = replace(cov, binding=binding, selection=Selection(include_namespaced=True), relationships=status)

    def endpoint(c):
        return Endpoint('ApexClass', c.key.namespace, c.key.full_name, c.record_id, c.key, 'resolved')

    evidence = Evidence('platform-probe', status)
    edge = Edge(endpoint(a), endpoint(b), (evidence,))
    graph = DependencyGraph(binding, cov.selection, status, (edge,))
    return a, b, cov, graph, edge


def test_reciprocal_stale_cycle_namespace_and_privacy(example):
    a, b, cov, graph, edge = live_graph(example)
    unsupported = Endpoint('Flow', None, 'FictionalFlow', 'private-record', resolution='unsupported')
    unresolved = Endpoint(None, None, 'Unknown [[link]]', None)
    external = Endpoint('ApexClass', None, 'Outside', 'external-record', resolution='external')
    graph = replace(
        graph,
        edges=(
            edge,
            Edge(edge.target, edge.source, (replace(edge.evidence[0], stale=True),)),
            Edge(unsupported, edge.source, edge.evidence),
            Edge(edge.source, unresolved, edge.evidence),
            Edge(edge.source, external, edge.evidence),
            Edge(edge.source, edge.source, edge.evidence),
        ),
    )
    paths = note_paths([a, b])
    result = render_new_note(a, cov, graph, identity=IDENTITY, managed_paths=paths, options=Options(include_namespaced=True))
    assert '[[Custom Code/Apex Classes/pkg/Helper.md|pkg/Helper]]' in result.text
    assert 'unsupported' in result.text and 'unresolved' in result.text and 'external' in result.text and 'stale' in result.text
    for private in (a.record_id, b.record_id, a.binding.org_id, 'private-record', 'external-record'):
        assert private not in result.text
    assert 'Unknown [[link]]' not in result.text
    assert (
        render_new_note(
            a,
            cov,
            replace(graph, edges=tuple(reversed(graph.edges))),
            identity=IDENTITY,
            managed_paths=dict(reversed(list(paths.items()))),
            options=Options(include_namespaced=True),
        )
        == result
    )
    incoming = render_new_note(b, cov, graph, identity=IDENTITY, managed_paths=paths, options=Options(include_namespaced=True))
    assert '[[Custom Code/Apex Classes/DemoService.md|DemoService]]' in incoming.text.split('## Referenced By')[1]


def test_unmapped_resolved_endpoint_is_text(example):
    a, b, cov, graph, _ = live_graph(example)
    candidate = render_generated(a, cov, graph, identity=IDENTITY, managed_paths={}, options=Options(include_namespaced=True))
    assert 'unmapped' in candidate.region and '[[' not in candidate.region


def test_incoming_move_coverage_and_templates_invalidate_without_source_churn(example):
    a, b, cov, graph, edge = live_graph(example)
    options = Options(include_namespaced=True)
    paths = note_paths([a, b])

    def candidate(g=graph, c=cov, p=paths, **kwargs):
        return render_new_note(b, c, g, identity=IDENTITY, managed_paths=p, options=options, **kwargs)

    before = candidate()
    changed = candidate(g=replace(graph, edges=()))
    moved = candidate(p={**paths, a.key: 'Moved/Service.md'})
    audit = candidate(c=replace(cov, audit=replace(cov.audit, method='different-audit')))
    for result in (changed, moved, audit):
        assert result.generated.source_hash == before.generated.source_hash == b.source_hash
        assert result.generated.render_hash != before.generated.render_hash
    creation = TemplateAsset('apex_created.md.j2', load_template('apex_created.md.j2').text + '\nNew context.\n')
    created = candidate(creation_template=creation)
    assert created.generated == before.generated and created.creation_hash != before.creation_hash
    generated = TemplateAsset('apex_generated.md.j2', load_template('apex_generated.md.j2').text + '\nNew presentation.\n')
    assert candidate(generated_template=generated).generated.render_hash != before.generated.render_hash
    assert before == candidate(g=replace(graph, edges=(edge, edge)))


@pytest.mark.parametrize(
    'text',
    [
        '## Business Context\n',
        '---\n## Business Context\n',
        '## Business Context\n## Known Issues / Technical Debt\n## Additional Information\n## Business Context\n',
    ],
)
def test_creation_required_structure(example, text):
    with pytest.raises(ConfigError):
        render(example, creation_template=TemplateAsset('apex_created.md.j2', text))


def test_scope_and_path_conflicts(example):
    a, cov, graph = example
    with pytest.raises(ConflictError):
        render((a, replace(cov, selection=Selection(include_namespaced=True)), graph))
    with pytest.raises(ConflictError):
        render((a, replace(cov, binding=SourceBinding('other', 'local')), graph))
    with pytest.raises(ConflictError):
        render_generated(
            a, cov, graph, identity=IDENTITY, managed_paths={a.key: 'A.md', replace(a.key, full_name='B'): 'A.md/B.md'}
        )
    with pytest.raises(ModelError):
        render_new_note(a, cov, graph, identity=IDENTITY, managed_paths={})


@pytest.mark.parametrize(
    'constant,value',
    [
        ('MAX_RENDER_TEXT_CHARS', 3),
        ('MAX_RENDER_INPUT_BYTES', 10),
        ('MAX_RENDER_INPUT_NODES', 3),
        ('MAX_RENDER_SECTION_BYTES', 10),
        ('MAX_NOTE_BYTES', 10),
    ],
)
def test_finite_rendering_refuses_before_acceptance(example, monkeypatch, constant, value):
    monkeypatch.setattr(const, constant, value)
    with pytest.raises((ModelError, ConfigError)):
        render(example)


def test_incident_edge_bound_and_source_immutability(example, monkeypatch):
    a, b, cov, graph, _ = live_graph(example)
    before = (a.source_hash, b.source_hash)
    monkeypatch.setattr(const, 'MAX_RENDER_EDGES', 0)
    with pytest.raises(ModelError, match='edge bound'):
        render_generated(
            a, cov, graph, identity=IDENTITY, managed_paths=note_paths([a, b]), options=Options(include_namespaced=True)
        )
    assert before == (a.source_hash, b.source_hash)


def test_yaml_parsed_independently_and_unicode_preserved(example):
    # Bandit's existing locked PyYAML dependency supplies a development-only oracle;
    # production serialization has no YAML parser dependency.
    from yaml import safe_load

    value = 'Unicode \U0001f642 Café "quoted" : &anchor !tag'
    result = render(example, user_properties={'null': value, 'false': ['[[Demo]]'], 'technical_debt': False})
    raw = result.text.split('---\n', 2)[1]
    parsed = safe_load(raw)
    assert parsed == properties(result.text)
    assert parsed['null'] == value and parsed['false'] == ['[[Demo]]']
    assert parsed['technical_debt'] is False


def test_generated_template_cannot_duplicate_required_headings(example):
    asset = load_template('apex_generated.md.j2')
    with pytest.raises(ConfigError, match='structure'):
        render(example, generated_template=TemplateAsset(asset.name, asset.text + '\n## Coverage\n'))


def test_offline_graph_cannot_claim_collection(example):
    a, coverage, graph = example
    relationships = CollectionCoverage(CoverageStatus.PARTIAL, 'synthetic')
    with pytest.raises(ConflictError, match='Offline'):
        render((a, replace(coverage, relationships=relationships), replace(graph, coverage=relationships)))


@pytest.mark.parametrize('text', ['api_version', 'created_at', 'local-apex-xml-v1', '"67.0"', '"Active"', 'Demo_Service'])
def test_ordinary_inline_metadata_remains_readable_without_entities(text):
    """Keep ordinary labels, provenance and JSON string quotes readable in source."""
    assert markdown(text) == text


def test_complete_metadata_uses_plain_labels_and_straight_quotes(example):
    a, coverage, graph = example
    a = replace(a, provenance=('local-apex-xml-v1',))
    text = render((a, coverage, graph)).generated.region
    assert '- Source provenance: local-apex-xml-v1\n' in text
    assert '- api_version: "68.0"\n' in text
    assert '- status: "Active"\n' in text
    assert '&#95;' not in text and '&#34;' not in text and '&#45;' not in text and '&#46;' not in text
    assert '\u201c' not in text and '\u201d' not in text


@pytest.mark.parametrize(
    'payload',
    [
        '_emphasis_',
        '__strong__',
        '*bold*',
        '[[link]]',
        '![[embed]]',
        '[text](https://example.invalid)',
        '<img src=x>',
        '&lt;script&gt;',
        '%%hidden%%',
        '==highlight==',
        '$math$',
        '^block',
        '#tag',
        '`code`',
        '\\*escaped*',
        '---',
        '1. list',
        'https://example.invalid',
        '<!-- generated -->',
    ],
)
def test_hostile_inline_syntax_keeps_conservative_escaping(payload):
    """Allow only the reviewed punctuation changes; active syntax remains encoded."""
    text = markdown(payload)
    for token in ('[[', '![[', '](', '<', '&lt;', '%%', '==', '$', '^', '#tag', '`', '\\', '*', '__'):
        assert token not in text
    assert text == payload if payload in {'---', '1. list'} else '&#' in text


def test_renderer_upgrade_preserves_legacy_state_and_human_regions(example, monkeypatch):
    """Accept an exact v1 baseline and patch only generated bytes using current output."""
    from obforce.models import NoteState
    from obforce.sync.notes import parse_note, patch_note
    from obforce.sync.state import SavedNote, StateDocument, parse_state, serialize_state

    legacy = (Path(__file__).parents[1] / 'fixtures/rendered/DemoService-v1.md').read_bytes()
    raw = legacy.replace(
        b'"technical_debt": false',
        b'"technical_debt": false # Human review\n"technical_debt_status": "reviewed"\n"aliases": ["Human Alias"]',
    )
    note = parse_note(raw)
    a, coverage, _ = example
    with monkeypatch.context() as context:
        context.setattr(const, 'RENDERER_VERSION', 1)
        old_hash = render(example).generated.render_hash
    current = render(example).generated
    assert const.RENDERER_VERSION > 1 and old_hash != current.render_hash
    state = NoteState(
        IDENTITY,
        a.binding,
        a.key,
        'Custom Code/Apex Classes/DemoService.md',
        current.source_hash,
        current.graph_hash,
        old_hash,
        note.generated_properties,
        note.region_hash,
    )
    wire = serialize_state(StateDocument(a.binding, coverage.selection, coverage, (SavedNote(state, note.region),)))
    assert serialize_state(parse_state(wire)) == wire
    snapshot = state.canonical()
    patch = patch_note(raw, state, note.region, current)
    result = parse_note(patch.content)
    assert patch.changed and result.region == current.region.encode()
    assert patch.content[: result.region_start] == raw[: note.region_start]
    assert patch.content[result.region_end :] == raw[note.region_end :]
    assert result.properties['technical_debt'] is False
    assert result.properties['technical_debt_status'] == 'reviewed' and result.properties['aliases'] == ('Human Alias',)
    assert state.canonical() == snapshot and b'&#95;' in note.region and b'&#95;' not in result.region
    edited = raw.replace(b'api&#95;version', b'human-edited-label')
    with pytest.raises(ConflictError):
        patch_note(edited, state, note.region, current)


@pytest.mark.parametrize(
    'text', ['"2026-10-22T12:34:56.000000Z"', "O'Brien", '(Fictional Reviewer)', 'Team, Inc.', 'alpha; beta']
)
def test_ordinary_audit_dates_and_names_remain_readable(text):
    assert markdown(text) == text


@pytest.mark.parametrize(
    'text',
    [
        'www.example.invalid',
        'example.com',
        '<https://example.invalid>',
        'https://127.0.0.1',
        'person@example.invalid',
        'mailto:someone',
        'tel:123',
    ],
)
def test_automatic_link_syntax_is_not_introduced(text):
    assert markdown(text) != text and '&#' in markdown(text)
