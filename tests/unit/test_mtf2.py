# -*- coding: utf-8 -*-
"""
:Module:            tests.unit.test_mtf2
:Synopsis:          Verifies requested dashboard presentation and guarded date projections
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     26 Oct 2026
"""

from __future__ import annotations

import json
import socket
import subprocess
from dataclasses import replace
from pathlib import Path

import pytest
from ruamel.yaml import YAML

from obforce import constants as const
from obforce.errors import ConflictError, ModelError
from obforce.graph.dependencies import DependencyGraph
from obforce.models import (
    Availability,
    CollectionCoverage,
    Component,
    ComponentKey,
    Coverage,
    CoverageStatus,
    FieldValue,
    NoteState,
    Selection,
    SourceBinding,
)
from obforce.renderer.dashboards import render_dashboard
from obforce.renderer.notes import note_paths, render_generated, render_new_note
from obforce.sync.notes import parse_note, patch_note
from obforce.sync.state import SavedNote, StateDocument, parse_state, serialize_state

IDENTITY = '00000000-0000-4000-8000-000000000001'


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError('Runtime network/process denied')

    monkeypatch.setattr(socket, 'socket', deny)
    monkeypatch.setattr(subprocess, 'Popen', deny)


@pytest.fixture
def inputs():
    binding = SourceBinding('fictional', 'local')
    inventory = CollectionCoverage(CoverageStatus.COMPLETE, 'synthetic-local', pagination='exhausted', limit_reached=False)
    audit = CollectionCoverage(CoverageStatus.UNAVAILABLE, 'offline-audit', requested=False)
    relations = CollectionCoverage(CoverageStatus.NOT_COLLECTED, 'offline-relationships', requested=False)
    coverage = Coverage(binding, Selection(), inventory, audit, relations)
    graph = DependencyGraph(binding, coverage.selection, relations)
    component = Component(
        binding,
        ComponentKey('fictional', 'ApexClass', None, 'DemoService'),
        {'api_version': FieldValue(Availability.VALUE, '67.0'), 'status': FieldValue(Availability.VALUE, 'Active')},
    )
    return component, coverage, graph


def render(inputs, attributes=None, **kwargs):
    component, coverage, graph = inputs
    if attributes is not None:
        component = replace(component, attributes=attributes)
    return render_new_note(component, coverage, graph, identity=IDENTITY, managed_paths=note_paths([component]), **kwargs)


def test_requested_presentation_has_one_class_link_and_exact_column_names():
    base = YAML(typ='safe').load(render_dashboard())
    columns = base['views'][0]['order']
    assert base['formulas']['class_link'] == 'file.asLink(note.sf_full_name)'
    assert columns[0] == 'formula.class_link' and 'note.sf_full_name' not in columns
    assert 'note.sf_lifecycle' not in columns
    assert 'formula.debt_assessment' not in columns and 'note.technical_debt' in columns
    labels = {key: value['displayName'] for key, value in base['properties'].items()}
    assert labels['formula.class_link'] == 'Class'
    for key, label in {
        'sf_status': 'Metadata Status',
        'sf_api_version': 'API Version',
        'sf_created': 'Created',
        'sf_last_modified': 'Last Modified',
        'technical_debt': 'Technical Debt',
        'tech_debt_severity': 'Debt Severity',
        'tech_debt_status': 'Debt Status',
        'last_reviewed': 'Last Reviewed',
    }.items():
        assert labels['note.' + key] == label


def test_new_human_fields_are_blank_creation_defaults_and_not_owned(inputs):
    candidate = render(inputs)
    parsed = parse_note(candidate.text.encode())
    assert parsed.properties['tech_debt_severity'] == parsed.properties['tech_debt_status'] == ''
    assert parsed.properties['last_reviewed'] is None
    assert parsed.properties['technical_debt'] is False
    assert 'sf_created' not in parsed.properties and 'sf_last_modified' not in parsed.properties
    assert parsed.properties['sf_lifecycle'] == 'active'
    assert not {'tech_debt_severity', 'tech_debt_status', 'last_reviewed'} & candidate.generated.properties.keys()
    assert parsed.properties['sf_api_version'] == '67.0'  # YAML quotes are serialization, not value characters.
    assert json.loads('"67.0"') == parsed.properties['sf_api_version']


@pytest.mark.parametrize('value', [None, '', 0, 1, 'false', [], ['reviewing']])
def test_new_note_debt_override_requires_a_real_boolean(inputs, value):
    with pytest.raises(ModelError, match='Boolean'):
        render(inputs, user_properties={'technical_debt': value})


@pytest.mark.parametrize('value', [True, False])
def test_new_note_debt_boolean_override_remains_user_owned(inputs, value):
    candidate = render(inputs, user_properties={'technical_debt': value})
    assert parse_note(candidate.text.encode()).properties['technical_debt'] is value
    assert 'technical_debt' not in candidate.generated.properties


@pytest.mark.parametrize(
    'value,expected',
    [
        ('2026-10-26T12:34:56.123456Z', '2026-10-26'),
        ('2024-02-29T23:30:00-02:00', '2024-03-01'),
        ('2026-01-01T00:30:00+02:00', '2025-12-31'),
        ('2026-02-30T12:00:00Z', None),
        ('2026-10-26', None),
        ('unavailable', None),
        (False, None),
    ],
)
def test_date_projections_come_only_from_valid_known_timestamps(inputs, value, expected):
    attributes = {name: FieldValue(Availability.VALUE, value) for name in ('created_at', 'last_modified_at')}
    candidate = render(inputs, attributes)
    props = parse_note(candidate.text.encode()).properties
    assert props['sf_created_at'] == props['sf_last_modified_at'] == value
    for name in ('sf_created', 'sf_last_modified'):
        assert props.get(name) == expected
        assert (name in props) == (expected is not None)


@pytest.mark.parametrize('availability', [Availability.NULL, Availability.UNAVAILABLE])
def test_unavailable_audit_dates_are_not_filled_or_inferred(inputs, availability):
    candidate = render(inputs, {name: FieldValue(availability) for name in ('created_at', 'last_modified_at')})
    assert not {'sf_created', 'sf_last_modified', 'sf_created_at', 'sf_last_modified_at'} & candidate.generated.properties.keys()


@pytest.mark.parametrize('debt', [False, True])
def test_saved_baseline_roundtrip_and_generated_patch_preserve_all_human_fields(inputs, monkeypatch, debt):
    component, coverage, graph = inputs
    raw = (Path(__file__).parents[1] / 'fixtures/rendered/DemoService.md').read_bytes()
    human_debt = f'technical_debt: {json.dumps(debt)} # human decision'.encode()
    raw = raw.replace(b'"tech_debt_severity": ""\n', b'').replace(b'"tech_debt_status": ""\n', b'')
    raw = raw.replace(b'"last_reviewed": null\n', b'')
    raw = raw.replace(
        b'"technical_debt": false',
        human_debt + b'\ntech_debt_severity: Medium # human\n'
        b'tech_debt_status: "Investigating"\nlast_reviewed: 2026-10-25\n'
        b'technical_debt_custom: "retain"\naliases: ["Human alias"]',
    )
    raw += b'\nHuman content\n- One\n  - Two\n'
    parsed = parse_note(raw)
    # This fixture has 68.0; establish its existing source/graph baseline explicitly.
    old_component = replace(
        component,
        attributes={'api_version': FieldValue(Availability.VALUE, '68.0'), 'status': FieldValue(Availability.VALUE, 'Active')},
    )
    with monkeypatch.context() as context:
        context.setattr(const, 'RENDERER_VERSION', 3)
        old = render_generated(old_component, coverage, graph, identity=IDENTITY, managed_paths=note_paths([component]))
    saved = NoteState(
        IDENTITY,
        component.binding,
        component.key,
        'Custom Code/Apex Classes/DemoService.md',
        old.source_hash,
        old.graph_hash,
        old.render_hash,
        parsed.generated_properties,
        parsed.region_hash,
    )
    state = StateDocument(component.binding, coverage.selection, coverage, (SavedNote(saved, parsed.region),))
    wire = serialize_state(state)
    assert serialize_state(parse_state(wire)) == wire
    updated = replace(
        component,
        attributes={
            **component.attributes,
            'created_at': FieldValue(Availability.VALUE, '2026-10-20T12:00:00Z'),
            'last_modified_at': FieldValue(Availability.VALUE, '2026-10-26T13:00:00Z'),
        },
    )
    incoming = render_generated(updated, coverage, graph, identity=IDENTITY, managed_paths=note_paths([updated]))
    result = patch_note(raw, saved, parsed.region, incoming)
    after = parse_note(result.content)
    assert after.properties['sf_created'] == '2026-10-20' and after.properties['sf_last_modified'] == '2026-10-26'
    for key, value in parsed.properties.items():
        if key not in const.OWNED_PROPERTIES:
            assert after.properties[key] == value
    assert human_debt in result.content
    assert b'tech_debt_severity: Medium # human' in result.content
    assert result.content[after.region_end :] == raw[parsed.region_end :]
    assert serialize_state(state) == wire and old.render_hash != incoming.render_hash
    next_state = replace(
        saved,
        source_hash=incoming.source_hash,
        graph_hash=incoming.graph_hash,
        render_hash=incoming.render_hash,
        generated_properties=result.generated_properties,
        generated_region_hash=result.generated_region_hash,
    )
    assert patch_note(result.content, next_state, result.generated_region, incoming).content == result.content
    edited = result.content.replace(b'"sf_created": "2026-10-20"', b'"sf_created": "2026-10-21"')
    with pytest.raises(ConflictError):
        patch_note(edited, next_state, result.generated_region, incoming)
