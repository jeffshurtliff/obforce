# -*- coding: utf-8 -*-
"""
:Module:            tests.unit.test_models
:Synopsis:          Tests deterministic identities, coverage, ownership, and fingerprint inputs
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     22 Oct 2026
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from obforce import constants as const
from obforce.config import Layout, Options
from obforce.errors import ConflictError, ExitCode, ModelError
from obforce.models import (
    Availability,
    CollectionCoverage,
    Component,
    ComponentKey,
    Coverage,
    CoverageStatus,
    FieldValue,
    NoteState,
    Relationship,
    Selection,
    SourceBinding,
    canonical_json,
    component_fingerprint,
    creation_fingerprint,
    fingerprint,
    graph_fingerprint,
    property_owner,
    render_fingerprint,
    require_same_source,
    validate_identities,
)

BINDING = SourceBinding('demo-org', 'local')
KEY = ComponentKey('demo-org', 'ApexClass', None, 'DemoService')
COMPLETE = CollectionCoverage(CoverageStatus.COMPLETE, 'synthetic', pagination='exhausted', limit_reached=False)
UNAVAILABLE = CollectionCoverage(CoverageStatus.UNAVAILABLE, 'by_design', requested=False)
NOTE_ID = '00000000-0000-4000-8000-000000000001'
OTHER_ID = '00000000-0000-4000-8000-000000000002'
DIGEST = 'a' * 64


def note(*, key: ComponentKey = KEY, path: str = 'Apex/DemoService.md', identity: str = NOTE_ID) -> NoteState:
    """Construct a private-state-shaped synthetic record without touching a vault."""
    baseline = {'obforce_id': FieldValue(Availability.VALUE, identity), 'obforce_schema': FieldValue(Availability.VALUE, 1)}
    return NoteState(identity, BINDING, key, path, DIGEST, DIGEST, DIGEST, baseline, DIGEST)


def test_structured_canonical_keys_keep_case_namespace_unicode_and_segment_boundaries() -> None:
    """Avoid delimiter collisions and accidental case/Unicode normalization of identities."""
    assert KEY.token == '["demo-org","ApexClass",null,"DemoService"]'
    keys = [
        KEY,
        replace(KEY, full_name='demoservice'),
        replace(KEY, namespace='pkg'),
        replace(KEY, full_name='Café'),
        replace(KEY, full_name='Cafe\u0301'),
        replace(KEY, namespace='x:y', full_name='z'),
        replace(KEY, namespace='x', full_name='y:z'),
    ]
    assert len({key.token for key in keys}) == len(keys)
    assert replace(KEY, namespace='') == KEY
    with pytest.raises(ModelError):
        replace(KEY, metadata_type='OtherType')


@pytest.mark.parametrize(
    'value',
    [
        {1: 'bad'},
        {True: 'bad'},
        {'bad': Path('/fictional')},
        {'bad': float('nan')},
        {'bad': float('inf')},
        {'bad': 1.0},
        {'bad': {'set'}},
    ],
)
def test_canonical_json_rejects_unsupported_and_lossy_values(value: object) -> None:
    """Require explicit normalized primitives rather than implicit object/string coercion."""
    with pytest.raises(ModelError):
        canonical_json(value)


def test_json_mapping_order_and_array_order_are_explicit() -> None:
    """Sort dictionaries, preserve intentional list order and literal Unicode."""
    assert canonical_json({'é': False, 'a': [None, '']}) == '{"a":[null,""],"é":false}'
    assert fingerprint({'b': 1, 'a': 2}) == fingerprint({'a': 2, 'b': 1})
    assert fingerprint([1, 2]) != fingerprint([2, 1])


def test_absent_unavailable_null_false_empty_and_zero_remain_distinct() -> None:
    """Prevent unknown facts and false assessments from becoming equivalent baselines."""
    fields = [
        None,
        FieldValue(Availability.UNAVAILABLE),
        FieldValue(Availability.NULL),
        FieldValue(Availability.VALUE, False),
        FieldValue(Availability.VALUE, ''),
        FieldValue(Availability.VALUE, ()),
        FieldValue(Availability.VALUE, 0),
    ]
    components = [Component(BINDING, KEY, {} if value is None else {'status': value}) for value in fields]
    assert len({component.source_hash for component in components}) == len(fields)
    assert FieldValue(Availability.VALUE, False) != FieldValue(Availability.VALUE, 0)
    assert FieldValue(Availability.VALUE, True) != FieldValue(Availability.VALUE, 1)
    for arguments in [
        (Availability.VALUE, None),
        (Availability.NULL, False),
        (Availability.UNAVAILABLE, ''),
        ('value', False),
        (Availability.VALUE, ['mutable']),
        (Availability.VALUE, (False,)),
    ]:
        with pytest.raises(ModelError):
            FieldValue(*arguments)


def test_source_hash_ordering_and_timestamp_independence_and_immutability() -> None:
    """Exclude collection time while retaining actual Salesforce audit changes."""
    attrs = {'status': FieldValue(Availability.VALUE, 'Active'), 'last_modified_at': FieldValue(Availability.UNAVAILABLE)}
    first = Component(BINDING, KEY, attrs, provenance=('xml', 'project'), collected_at='2026-10-18T00:00:00Z')
    second = Component(
        BINDING, KEY, dict(reversed(list(attrs.items()))), provenance=('project', 'xml'), collected_at='2026-10-19T00:00:00Z'
    )
    assert first.canonical() == second.canonical()
    assert first.source_hash == second.source_hash
    attrs['status'] = FieldValue(Availability.VALUE, 'Inactive')
    assert first.attributes['status'].value == 'Active'
    with pytest.raises(TypeError):
        first.attributes['status'] = attrs['status']
    with pytest.raises(FrozenInstanceError):
        first.key = replace(KEY, full_name='Changed')
    changed = replace(first, attributes={'last_modified_at': FieldValue(Availability.VALUE, '2026-01-01T00:00:00Z')})
    assert changed.source_hash != first.source_hash
    other = Component(BINDING, replace(KEY, full_name='OtherService'))
    assert component_fingerprint([first, other]) == component_fingerprint([other, second])


def test_invalid_component_facts_are_not_dumped_into_records() -> None:
    """Refuse raw API fields, wrong binding, and local claims of Salesforce IDs."""
    for changes in (
        {'attributes': {'Body': FieldValue(Availability.VALUE, 'fictional')}},
        {'attributes': {'status': False}},
        {'binding': SourceBinding('other-workspace', 'local')},
        {'record_id': 'fictional-id'},
    ):
        with pytest.raises(ModelError):
            replace(Component(BINDING, KEY), **changes)


def test_duplicate_component_and_salesforce_mappings_block_even_identical_records() -> None:
    """Never resolve ambiguous identity by last-write-wins or silent deduplication."""
    component = Component(BINDING, KEY)
    with pytest.raises(ConflictError):
        component_fingerprint([component, component])
    live = SourceBinding('demo-org', 'live', 'fictional-verified-org')
    first = Component(live, KEY, record_id='fictional-record')
    second = replace(first, key=replace(KEY, full_name='OtherService'))
    with pytest.raises(ConflictError):
        validate_identities([first, second])


def test_source_binding_refuses_switches_but_is_independent_of_alias_and_machine_path() -> None:
    """Bind verified live identity, never an alias or checkout path."""
    require_same_source(BINDING, SourceBinding('demo-org', 'local'))
    live = SourceBinding('demo-org', 'live', 'fictional-verified-org')
    require_same_source(live, SourceBinding('demo-org', 'live', 'fictional-verified-org'))
    for changed in [live, SourceBinding('other', 'local')]:
        with pytest.raises(ConflictError):
            require_same_source(BINDING, changed)
    with pytest.raises(ConflictError):
        require_same_source(live, replace(live, org_id='different-verified-org'))
    with pytest.raises(ConflictError):
        validate_identities([Component(BINDING, KEY), Component(live, replace(KEY, full_name='OtherService'))])
    with pytest.raises(ModelError):
        SourceBinding('demo-org', 'live')
    with pytest.raises(ModelError):
        SourceBinding('demo-org', 'local', 'fictional-org')


def test_scope_filters_order_namespace_and_binding_change_scope() -> None:
    """Keep scope comparable without equating it to successful collection."""
    assert Selection(full_names=('B', 'A')).scope_hash(BINDING) == Selection(full_names=('A', 'B')).scope_hash(BINDING)
    assert Selection().scope_hash(BINDING) != Selection(True).scope_hash(BINDING)
    assert Selection().scope_hash(BINDING) != Selection().scope_hash(SourceBinding('another', 'local'))
    with pytest.raises(ModelError):
        Selection(full_names=('A', 'A'))


def test_coverage_tracks_independent_dimensions_and_request_intent() -> None:
    """Offline design exclusions can succeed while explicit incomplete requests cannot."""
    coverage = Coverage(BINDING, Selection(), COMPLETE, UNAVAILABLE, UNAVAILABLE)
    assert coverage.outcome == ExitCode.SUCCESS
    assert coverage.audit.status == CoverageStatus.UNAVAILABLE
    partial = replace(COMPLETE, status=CoverageStatus.PARTIAL, pagination='incomplete', limit_reached=True)
    changed = replace(coverage, inventory=partial)
    assert changed.outcome == ExitCode.INCOMPLETE
    assert changed.scope_hash == coverage.scope_hash
    assert fingerprint(changed.canonical()) != fingerprint(coverage.canonical())
    assert replace(coverage, relationships=replace(UNAVAILABLE, requested=True)).outcome == ExitCode.INCOMPLETE
    assert replace(coverage, relationships=replace(UNAVAILABLE, status=CoverageStatus.NOT_COLLECTED, requested=True)).outcome == 4
    for changes in (
        {'pagination': 'unknown'},
        {'pagination': 'incomplete'},
        {'limit_reached': True},
        {'limit_reached': None},
        {'requested': 1},
        {'status': 'complete'},
        {'limit_reached': 0},
    ):
        with pytest.raises(ModelError):
            replace(COMPLETE, **changes)


def test_relationship_hash_includes_direction_staleness_coverage_unresolved_and_target_moves() -> None:
    """Changing an incoming edge or target location invalidates an unchanged component."""
    other = replace(KEY, full_name='OtherService')
    outgoing = Relationship(KEY, other, 'references', 'platform_reported', COMPLETE)
    incoming = Relationship(other, KEY, 'references', 'platform_reported', COMPLETE)
    paths = {KEY: 'Apex/DemoService.md', other: 'Apex/OtherService.md'}
    initial = graph_fingerprint([outgoing, incoming], paths)
    assert initial == graph_fingerprint([incoming, outgoing], dict(reversed(list(paths.items()))))
    assert initial != graph_fingerprint([outgoing], paths)
    assert initial != graph_fingerprint([outgoing, replace(incoming, stale=True)], paths)
    assert initial != graph_fingerprint([outgoing, replace(incoming, coverage=UNAVAILABLE)], paths)
    assert initial != graph_fingerprint([outgoing, incoming], {**paths, other: 'Moved/OtherService.md'})
    unresolved = replace(outgoing, target=None, unresolved_target='UnsupportedType:Example')
    assert graph_fingerprint([unresolved], {}) != graph_fingerprint([], {})
    with pytest.raises(ModelError):
        replace(outgoing, target=None)
    with pytest.raises(ModelError):
        replace(outgoing, unresolved_target='ambiguous')
    with pytest.raises(ModelError):
        graph_fingerprint([outgoing, outgoing], paths)


def test_render_inputs_invalidate_without_rendering_or_reading_templates(monkeypatch: pytest.MonkeyPatch) -> None:
    """Track generated templates, graph, schema/version, layout, privacy, and new-note template."""
    inputs = {
        'source_hash': DIGEST,
        'graph_hash': DIGEST,
        'generated_template_hash': DIGEST,
        'layout': Layout(),
        'options': Options(),
    }
    initial = render_fingerprint(**inputs)
    for changed in (
        {'source_hash': 'b' * 64},
        {'graph_hash': 'b' * 64},
        {'generated_template_hash': 'b' * 64},
        {'layout': Layout(apex_classes='Other')},
        {'options': Options(include_audit_names=False)},
    ):
        assert render_fingerprint(**(inputs | changed)) != initial
    assert creation_fingerprint(initial, 'b' * 64) != creation_fingerprint(initial, 'c' * 64)
    assert render_fingerprint(**inputs) == initial
    for name in ['RENDERER_VERSION', 'NOTE_SCHEMA_VERSION', 'MARKER_VERSION']:
        with monkeypatch.context() as context:
            context.setattr(const, name, getattr(const, name) + 1)
            assert render_fingerprint(**inputs) != initial
    with pytest.raises(ModelError):
        render_fingerprint(**(inputs | {'source_hash': 'invalid'}))


def test_exact_ownership_and_marker_contract() -> None:
    """Reserve only named ownership fields and refuse unknown sf_* extensions."""
    for name in const.OWNED_PROPERTIES:
        assert property_owner(name) == 'obforce'
    for name in ['type', 'tags', 'aliases', 'business_owner', 'technical_debt', 'technical_debt_status', 'obforce_custom']:
        assert property_owner(name) == 'user'
    with pytest.raises(ModelError):
        property_owner('sf_body')
    assert const.GENERATED_START == '<!-- obforce:generated:start -->'
    assert const.GENERATED_END == '<!-- obforce:generated:end -->'
    assert const.NOTE_SCHEMA_VERSION == const.MARKER_VERSION == 1


def test_note_state_copies_baselines_validates_schema_and_preserves_mapping_on_move() -> None:
    """An ID and source key survive note moves; paths independently invalidate links."""
    original = note()
    moved = replace(original, path='Moved/DemoService.md')
    assert moved.obforce_id == original.obforce_id
    assert moved.key == original.key
    assert moved.source_hash == original.source_hash
    assert fingerprint(moved.canonical()) != fingerprint(original.canonical())
    with pytest.raises(TypeError):
        original.generated_properties['sf_status'] = FieldValue(Availability.VALUE, 'x')
    for changes in (
        {'schema_version': 2},
        {'schema_version': True},
        {'path': '../escape.md'},
        {'obforce_id': 'bad'},
        {'source_hash': 'bad'},
        {'generated_properties': {}},
        {'generated_properties': dict(original.generated_properties) | {'tags': FieldValue(Availability.VALUE, ())}},
        {'generated_properties': dict(original.generated_properties) | {'obforce_schema': FieldValue(Availability.VALUE, True)}},
    ):
        with pytest.raises(ModelError):
            replace(original, **changes)


@pytest.mark.parametrize(
    'other',
    [
        note(path='Moved.md'),
        note(identity=OTHER_ID),
        note(key=replace(KEY, full_name='OtherService'), path='apex/demoservice.MD', identity=OTHER_ID),
    ],
)
def test_note_ids_keys_and_portable_paths_cannot_collide(other: NoteState) -> None:
    """Independently detect copied IDs, duplicated component mappings, and case collisions."""
    with pytest.raises(ConflictError):
        validate_identities([], [note(), other])


def test_unicode_paths_collide_without_collapsing_component_identity() -> None:
    """Preserve exact component names while refusing unsafe portable note-path collisions."""
    first = note(path='Apex/Café.md')
    second = note(key=replace(KEY, full_name='Other'), path='Apex/Cafe\u0301.md', identity=OTHER_ID)
    with pytest.raises(ConflictError):
        validate_identities([], [first, second])


def test_mixed_workspace_inventory_cannot_bind_one_vault() -> None:
    """Reject a batch spanning multiple configured workspace identities."""
    other = Component(SourceBinding('other', 'local'), replace(KEY, workspace_id='other'))
    with pytest.raises(ConflictError):
        validate_identities([Component(BINDING, KEY), other])
    with pytest.raises(ModelError):
        Coverage(BINDING, Selection(), replace(COMPLETE, requested=False), UNAVAILABLE, UNAVAILABLE)


@pytest.mark.parametrize('value', ['\ud800', {'\ud800': 1}])
def test_invalid_unicode_is_a_typed_model_error(value: object) -> None:
    """Never emit unencodable hashes or expose raw encoder failures."""
    with pytest.raises(ModelError):
        canonical_json(value)


@pytest.mark.parametrize(
    'factory',
    [
        lambda: Component(BINDING, KEY, attributes=[]),
        lambda: Component(BINDING, KEY, provenance='xml'),
        lambda: Selection(full_names='DemoService'),
        lambda: replace(note(), generated_properties=[]),
        lambda: Coverage(BINDING, Selection(), 'complete', UNAVAILABLE, UNAVAILABLE),
        lambda: Relationship(KEY, KEY, 'references', 'synthetic', 'complete'),
    ],
)
def test_malformed_record_shapes_raise_typed_errors(factory) -> None:
    """Do not accidentally coerce scalar collections or raw API-shaped objects."""
    with pytest.raises(ModelError):
        factory()
