# -*- coding: utf-8 -*-
"""
:Module:            tests.unit.test_note_preservation
:Synopsis:          Verifies bounded in-memory patches using fictional hand-edited notes
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     26 Oct 2026
"""

from __future__ import annotations

import hashlib
import json
import socket
import subprocess
from dataclasses import replace
from pathlib import Path

import pytest

from obforce import constants as const
from obforce.config import Options
from obforce.errors import ConflictError, ExitCode, ModelError, exit_code
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
from obforce.renderer.notes import note_paths, render_generated, render_new_note
from obforce.renderer.templates import TemplateAsset
from obforce.sync.notes import parse_note, patch_note

IDENTITY = '00000000-0000-4000-8000-000000000001'
FIXTURE = Path(__file__).parents[1] / 'fixtures/vaults/hand_edited_v2.md'


@pytest.fixture
def example(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError('Runtime network/process forbidden')

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


def generated(example, **kwargs):
    a, coverage, graph = example
    return render_generated(a, coverage, graph, identity=IDENTITY, managed_paths=note_paths([a]), **kwargs)


def state_for(raw, example):
    a, _, _ = example
    candidate = generated(example)
    note = parse_note(raw)
    return NoteState(
        IDENTITY,
        a.binding,
        a.key,
        'Custom Code/Apex Classes/DemoService.md',
        candidate.source_hash,
        candidate.graph_hash,
        candidate.render_hash,
        note.generated_properties,
        note.region_hash,
    )


def updated(example, **kwargs):
    a, coverage, graph = example
    return generated((replace(a, attributes={**a.attributes, **kwargs}), coverage, graph))


def test_audit_update_preserves_exact_body_user_yaml_and_inputs(example, tmp_path, monkeypatch):
    raw = FIXTURE.read_bytes()
    note = parse_note(raw)
    state = state_for(raw, example)
    snapshot = state.canonical()
    incoming = updated(example, last_modified_at=FieldValue(Availability.VALUE, '2026-10-20T12:00:00Z'))
    monkeypatch.chdir(tmp_path)
    result = patch_note(raw, state, note.region, incoming)
    after = parse_note(result.content)
    assert result.content == (FIXTURE.parent / 'expected_updated.md').read_bytes()
    assert result.changed
    assert result.content[after.front_end : after.region_start] == raw[note.front_end : note.region_start]
    assert result.content[after.region_end :] == raw[note.region_end :]
    assert result.content[: note.front_end] == raw[: note.front_end]
    assert after.properties['sf_last_modified_at'] == '2026-10-20T12:00:00Z'
    for key, value in note.properties.items():
        if key not in const.OWNED_PROPERTIES:
            assert after.properties[key] == value
    assert b"sf_api_version: '68.0' # owned audit presentation" in result.content
    assert b'technical_debt: false' in result.content
    assert b'technical_debt_assessed: false' in result.content
    assert state.canonical() == snapshot and raw == FIXTURE.read_bytes()
    assert incoming.region.encode() == result.generated_region
    assert result.generated_region_hash == after.region_hash
    assert (result.source_hash, result.graph_hash, result.render_hash) == (
        incoming.source_hash,
        incoming.graph_hash,
        incoming.render_hash,
    )
    assert not list(tmp_path.iterdir())
    with pytest.raises(TypeError):
        after.properties['tags'] = ()
    with pytest.raises(TypeError):
        result.generated_properties['sf_status'] = None
    assert 'Human' not in repr(note) and 'DemoService' not in repr(result)


@pytest.mark.parametrize('ending', [b'\n', b'\r\n'])
@pytest.mark.parametrize('debt', [b'technical_debt: true\n', b'technical_debt: false\n'])
def test_noop_original_bytes_and_debt_distinctions(example, ending, debt):
    raw = FIXTURE.read_bytes().replace(b'technical_debt: false\n', debt).replace(b'\n', ending)
    note = parse_note(raw)
    state = state_for(raw, example)
    first = patch_note(raw, state, note.region, generated(example))
    assert first.content is raw and not first.changed
    assert first.generated_region_hash == hashlib.sha256(note.region).hexdigest()
    assert first.generated_region == note.region
    change = updated(example, api_version=FieldValue(Availability.VALUE, '69.0'))
    result = patch_note(raw, state, note.region, change)
    after = parse_note(result.content)
    assert result.content[after.front_end : after.region_start] == raw[note.front_end : note.region_start]
    assert result.content[after.region_end :] == raw[note.region_end :]
    assert after.properties.get('technical_debt', 'absent') == note.properties.get('technical_debt', 'absent')
    assert after.region == change.region.encode().replace(b'\n', ending)
    # The next saved baseline is the adapted exact bytes, never the LF renderer hash.
    next_state = replace(
        state, generated_properties=result.generated_properties, generated_region_hash=result.generated_region_hash
    )
    assert patch_note(result.content, next_state, result.generated_region, change).content is result.content


def test_mixed_human_endings_and_independent_uniform_envelopes(example):
    raw = FIXTURE.read_bytes().replace(b'Human whitespace: retained\n', b'Human whitespace:   \r\n')
    note = parse_note(raw)
    # Frontmatter CRLF and body/markers LF are individually uniform and supported.
    raw = raw[: note.front_end + 4].replace(b'\n', b'\r\n') + raw[note.front_end + 4 :]
    note = parse_note(raw)
    state = state_for(raw, example)
    result = patch_note(raw, state, note.region, updated(example, status=FieldValue(Availability.VALUE, 'Changed')))
    after = parse_note(result.content)
    assert result.content[after.front_end : after.region_start] == raw[note.front_end : note.region_start]
    assert result.content[after.region_end :] == raw[note.region_end :]
    assert b'Human whitespace:   \r\n' in result.content


@pytest.mark.parametrize('value', [None, False, '', (), 0, 'Active'])
def test_strict_owned_value_baselines(example, value):
    raw = FIXTURE.read_bytes()
    raw = raw.replace(b'sf_status: Active', b'sf_status: ' + json.dumps(value).encode())
    note = parse_note(raw)
    assert note.generated_properties['sf_status'] == FieldValue(Availability.NULL if value is None else Availability.VALUE, value)
    state = state_for(raw, example)
    # Changing the saved value's type is a conflict, even false vs integer zero.
    wrong = FieldValue(Availability.VALUE, False if type(value) is int else 0)
    state = replace(state, generated_properties={**state.generated_properties, 'sf_status': wrong})
    with pytest.raises(ConflictError):
        patch_note(raw, state, note.region, generated(example))


@pytest.mark.parametrize(
    'old,new',
    [
        (b'sf_status: Active', b'sf_status: Changed'),
        (b'sf_status: Active', b'sf_status: null'),
        (b'sf_status: Active\n', b''),
        (b'sf_status: Active', b'sf_status: false'),
        (b'## Salesforce Metadata', b'## Edited Salesforce Metadata'),
        (b'obforce_schema: 1', b'obforce_schema: 2'),
        (b'obforce_schema: 1', b'obforce_schema: true'),
        (b'obforce_schema: 1', b'obforce_schema: "1"'),
        (IDENTITY.encode(), b'00000000-0000-4000-8000-000000000002'),
    ],
)
def test_edits_conflict_even_unchanged_metadata_and_hashes(example, old, new):
    raw = FIXTURE.read_bytes()
    note = parse_note(raw)
    state = state_for(raw, example)
    with pytest.raises(ConflictError) as caught:
        patch_note(raw.replace(old, new), state, note.region, generated(example))
    assert caught.value.exit_code == 3
    assert 'DemoService' not in str(caught.value) and IDENTITY not in str(caught.value)


def test_hash_match_does_not_authorize_edited_body(example):
    raw = FIXTURE.read_bytes()
    note = parse_note(raw)
    edited = note.region.replace(b'## Salesforce Metadata', b'## Human edit')
    altered = raw[: note.region_start] + edited + raw[note.region_end :]
    state = replace(state_for(raw, example), generated_region_hash=hashlib.sha256(edited).hexdigest())
    with pytest.raises(ConflictError):
        patch_note(altered, state, note.region, generated(example))


@pytest.mark.parametrize('availability', [Availability.NULL, Availability.UNAVAILABLE])
def test_missing_audits_remove_keys_and_retain_comments(example, availability):
    raw = FIXTURE.read_bytes().replace(
        b'sf_status: Active', b'sf_created_by: "Fictional Person" # keep this comment\nsf_status: Active'
    )
    note = parse_note(raw)
    state = state_for(raw, example)
    incoming = updated(example, created_by=FieldValue(availability))
    result = patch_note(raw, state, note.region, incoming)
    assert 'sf_created_by' not in parse_note(result.content).properties
    assert b'# keep this comment' in result.content
    assert b'Fictional Person' not in result.content


def test_privacy_omission_effective(example):
    a, coverage, graph = example
    with_name = (
        replace(a, attributes={**a.attributes, 'created_by': FieldValue(Availability.VALUE, 'Fictional Person')}),
        coverage,
        graph,
    )
    new = render_new_note(*with_name, identity=IDENTITY, managed_paths=note_paths([a]))
    raw = new.text.encode()
    note = parse_note(raw)
    result = patch_note(
        raw, state_for(raw, with_name), note.region, generated(with_name, options=Options(include_audit_names=False))
    )
    assert b'Fictional Person' not in result.content
    assert 'sf_created_by' not in parse_note(result.content).properties


@pytest.mark.parametrize('ending', [b'\n', b'\r\n'])
@pytest.mark.parametrize(
    'value',
    [
        '| # block comment\n  Active\n',
        '>- # folded comment\n  Active\n',
        '\n- Active # indentless\n- Second\n',
        "'Changed' # suffix",
        'null # suffix',
        'false # suffix',
        '|-\n  Active\n',
        '>\n  Active\n',
        '["Active", "Second"] # suffix',
        '\n  - Active # item\n  - Second\n# retain before next key\n',
    ],
)
def test_owned_span_replacement_and_comment_preservation(example, value, ending):
    raw = FIXTURE.read_bytes().replace(b'sf_status: Active\n', ('sf_status: ' + value + '\n').encode())
    raw = raw.replace(b'\n', ending)
    note = parse_note(raw)
    result = patch_note(raw, state_for(raw, example), note.region, generated(example))
    after = parse_note(result.content)
    assert after.properties['sf_status'] == 'Active'
    for comment in (
        b'# suffix',
        b'# item',
        b'# retain before next key',
        b'# block comment',
        b'# folded comment',
        b'# indentless',
    ):
        if comment in raw:
            assert comment in result.content
    assert result.content[after.region_end :] == raw[note.region_end :]


@pytest.mark.parametrize(
    'value',
    [
        "'Person' # suffix",
        '|-\n  Person\n',
        '["Person", "Other"] # suffix',
        '\n  - Person # item\n  - Other\n# retain before next key\n',
        '# property comment\n  - Person # item\n',
    ],
)
def test_owned_span_removal_retains_comments(example, value):
    raw = FIXTURE.read_bytes().replace(b'sf_status: Active', ('sf_created_by: ' + value + '\nsf_status: Active').encode())
    note = parse_note(raw)
    result = patch_note(raw, state_for(raw, example), note.region, generated(example))
    assert 'sf_created_by' not in parse_note(result.content).properties
    for comment in (b'# suffix', b'# item', b'# property comment', b'# retain before next key'):
        if comment in raw:
            assert comment in result.content


@pytest.mark.parametrize(
    'yaml',
    [
        'custom: 1\ncustom: 2\n',
        'sf_new_unknown: null\n',
        'custom: !!python/object/apply:os.system ["private-value"]\n',
        'custom: !anything private-value\n',
        'custom: !!str private-value\n',
        'custom: &anchor private-value\n',
        'custom: *unknown\n',
        'custom: &recursive [*recursive]\n',
        '<<: {custom: private-value}\n',
        'custom: {nested: private-value}\n',
        'custom: [[private-value]]\n',
        'custom: [1, false]\n',
        '? [complex, key]\n: private-value\n',
        '? custom\n: private-value\n',
        'false: private-value\n',
        'custom: .nan\n',
        'custom: .inf\n',
        'custom: !!binary cHJpdmF0ZQ==\n',
        'custom: !!set {one: null}\n',
        'custom: "unterminated\n',
        '%YAML 1.1\n',
        '...\ncustom: private-value\n',
        'custom: 18446744073709551616\n',
    ],
)
def test_unsafe_unsupported_frontmatter_redacted(yaml):
    raw = FIXTURE.read_bytes().replace(b'obforce_schema: 1\n', b'obforce_schema: 1\n' + yaml.encode())
    with pytest.raises(ConflictError) as caught:
        parse_note(raw)
    assert caught.value.exit_code == 3
    assert 'private-value' not in str(caught.value)
    assert 'private-value' not in repr(caught.value)
    assert caught.value.__cause__ is None


@pytest.mark.parametrize(
    'mutate',
    [
        lambda r: b'\xef\xbb\xbf' + r,
        lambda r: b'preamble\n' + r,
        lambda r: r.replace(b'---\n', b'--- \n', 1),
        lambda r: r.replace(b'---\n', b'', 1),
        lambda r: r.replace(b'\n---\n', b'\n---suffix\n', 1),
        lambda r: r.replace(b'obforce_id:', b'user_id:'),
        lambda r: r.replace(b'sf_status: Active', b'sf_status: 1.5'),
        lambda r: r.replace(b'obforce_schema: 1', b'obforce_schema: null'),
        lambda r: r.replace(b'sf_status: Active', b'sf_status: Active\r\ncustom: yes'),
        lambda r: r.replace(b'## Salesforce Metadata\n', b'## Salesforce Metadata\r\n'),
        lambda r: r.replace(const.GENERATED_START.encode(), const.GENERATED_END.encode()),
        lambda r: r.replace(const.GENERATED_END.encode(), const.GENERATED_START.encode()),
        lambda r: r.replace(const.GENERATED_START.encode(), b''),
        lambda r: r.replace(const.GENERATED_END.encode(), b''),
        lambda r: r.replace(const.GENERATED_START.encode(), b'text ' + const.GENERATED_START.encode()),
        lambda r: r.replace(const.GENERATED_START.encode(), const.GENERATED_START.encode() + b' suffix'),
        lambda r: r.replace(const.GENERATED_START.encode(), b'  ' + const.GENERATED_START.encode()),
        lambda r: r.replace(
            const.GENERATED_START.encode(), const.GENERATED_START.encode() + b'\n' + const.GENERATED_START.encode()
        ),
        lambda r: r + b'\n<!-- obforce:generated:end -->\n',
        lambda r: r.replace(b'## Salesforce Metadata', b'<!-- obforce:generated:broken -->'),
        lambda r: r + b'\x00',
        lambda r: r + b'\xff',
        lambda r: r + b'\r',
    ],
)
def test_malformed_envelopes(mutate):
    with pytest.raises(ConflictError):
        parse_note(mutate(FIXTURE.read_bytes()))


@pytest.mark.parametrize(
    'limit',
    [
        'MAX_NOTE_BYTES',
        'MAX_FRONTMATTER_BYTES',
        'MAX_NOTE_PROPERTIES',
        'MAX_YAML_TOKENS',
        'MAX_YAML_NODES',
        'MAX_YAML_DEPTH',
        'MAX_YAML_SCALAR_BYTES',
        'MAX_YAML_LIST_ITEMS',
    ],
)
def test_finite_parsing_bounds(monkeypatch, limit):
    monkeypatch.setattr(const, limit, 1)
    with pytest.raises(ConflictError):
        parse_note(FIXTURE.read_bytes())


def test_output_bounds(example, monkeypatch):
    raw = FIXTURE.read_bytes()
    note = parse_note(raw)
    state = state_for(raw, example)
    incoming = updated(example, created_at=FieldValue(Availability.VALUE, 'A' * 200))
    monkeypatch.setattr(const, 'MAX_NOTE_BYTES', len(raw))
    with pytest.raises(ConflictError):
        patch_note(raw, state, note.region, incoming)
    monkeypatch.setattr(const, 'MAX_NOTE_BYTES', 1_048_576)
    monkeypatch.setattr(const, 'MAX_FRONTMATTER_BYTES', note.front_end - note.front_start)
    with pytest.raises(ConflictError):
        patch_note(raw, state, note.region, incoming)


def test_creation_template_changes_cannot_rewrite_existing_note(example):
    a, coverage, graph = example
    template = TemplateAsset(
        'apex_created.md.j2', '## Business Context\n\nChanged.\n\n## Known Issues / Technical Debt\n\n## Additional Information\n'
    )
    first = render_new_note(a, coverage, graph, identity=IDENTITY, managed_paths=note_paths([a]))
    changed = render_new_note(a, coverage, graph, identity=IDENTITY, managed_paths=note_paths([a]), creation_template=template)
    assert first.creation_hash != changed.creation_hash
    raw = FIXTURE.read_bytes()
    assert patch_note(raw, state_for(raw, example), parse_note(raw).region, changed.generated).content is raw
    with pytest.raises(ModelError):
        patch_note(raw, state_for(raw, example), parse_note(raw).region, changed)


def test_caller_contract_errors_and_identity_refusal(example):
    raw = FIXTURE.read_bytes()
    note = parse_note(raw)
    state = state_for(raw, example)
    with pytest.raises(ModelError):
        parse_note(bytearray(raw))
    with pytest.raises(ModelError):
        patch_note(raw, 'state.json', note.region, generated(example))
    with pytest.raises(ModelError):
        patch_note(raw, state, 'baseline', generated(example))
    with pytest.raises(ConflictError):
        patch_note(raw, replace(state, key=replace(state.key, full_name='Other')), note.region, generated(example))
    candidate = generated(example)
    with pytest.raises(ConflictError):
        patch_note(
            raw,
            state,
            note.region,
            replace(candidate, properties={**candidate.properties, 'obforce_id': '00000000-0000-4000-8000-000000000002'}),
        )
    assert exit_code([ExitCode.INVALID, ExitCode.CONFLICT, ExitCode.OPERATIONAL, ExitCode.INCOMPLETE]) == ExitCode.CONFLICT


@pytest.mark.parametrize('ending', [b'\n', b'\r\n'])
def test_unicode_before_owned_spans_and_block_header_removal(example, ending):
    raw = (
        FIXTURE.read_bytes()
        .replace(b'sf_api_version:', 'custom_early: "日本語 🪨" # early comment\nsf_api_version:'.encode())
        .replace(b'sf_status: Active', b'sf_created_by: | # retain header\n  Fictional Person\nsf_status: Active')
    )
    raw = raw.replace(b'\n', ending)
    note = parse_note(raw)
    result = patch_note(
        raw, state_for(raw, example), note.region, updated(example, api_version=FieldValue(Availability.VALUE, '69.0'))
    )
    after = parse_note(result.content)
    assert after.properties['sf_api_version'] == '69.0'
    assert after.properties['custom_early'] == '日本語 🪨'
    assert b'# early comment' in result.content and b'# retain header' in result.content
    assert b'Fictional Person' not in result.content
    assert result.content[after.front_end : after.region_start] == raw[note.front_end : note.region_start]
    assert result.content[after.region_end :] == raw[note.region_end :]


def test_hash_changes_with_equal_output_do_not_rewrite(example):
    raw = FIXTURE.read_bytes()
    note = parse_note(raw)
    candidate = replace(generated(example), source_hash='a' * 64, graph_hash='b' * 64, render_hash='c' * 64)
    result = patch_note(raw, state_for(raw, example), note.region, candidate)
    assert result.content is raw and not result.changed
    assert result.render_hash == 'c' * 64


@pytest.mark.parametrize(
    'change',
    [
        {'region': 'No required sections\n'},
        {'region': 'x' * (const.MAX_RENDER_SECTION_BYTES + 1)},
        {'render_hash': 'private-sentinel'},
        {'properties': {'obforce_id': IDENTITY, 'obforce_schema': 1}},
    ],
)
def test_invalid_candidates_refuse_redacted(example, change):
    raw = FIXTURE.read_bytes()
    with pytest.raises(ModelError) as caught:
        patch_note(raw, state_for(raw, example), parse_note(raw).region, replace(generated(example), **change))
    assert caught.value.exit_code == 2
    assert 'private-sentinel' not in str(caught.value)


@pytest.mark.parametrize(
    'unsafe', ['custom: &a [*a]\n', 'custom: !unsafe private-sentinel\n', 'custom: ' + '[' * 2000 + 'x' + ']' * 2000 + '\n']
)
def test_unsafe_inputs_rejected_before_yaml_construction(monkeypatch, unsafe):
    from ruamel.yaml import YAML

    def deny(*args, **kwargs):
        raise AssertionError('Unsafe YAML reached construction')

    monkeypatch.setattr(YAML, 'load', deny)
    raw = FIXTURE.read_bytes().replace(b'obforce_schema: 1\n', b'obforce_schema: 1\n' + unsafe.encode())
    with pytest.raises(ConflictError):
        parse_note(raw)


@pytest.mark.parametrize(
    'yaml',
    [
        '"null": null\n"false": false\n',
        'custom_date: 2026-10-20\ncustom_datetime: 2026-10-20T10:15:00Z\n',
        'custom_literal: |2- # block header\n  Exact human text\n  # literal, not a comment\n',
        'custom_fold: >+\n  Human words\n  continued\n\n',
        'custom_list:\n- \'one\' # list item\n- "two"\n',
        'custom_flow: ["one", # flow comment\n  "two"]\n',
    ],
)
def test_supported_user_forms_unchanged_verbatim(example, yaml):
    raw = FIXTURE.read_bytes().replace(b'obforce_schema: 1\n', b'obforce_schema: 1\n' + yaml.encode())
    note = parse_note(raw)
    result = patch_note(
        raw, state_for(raw, example), note.region, updated(example, status=FieldValue(Availability.VALUE, 'Changed'))
    )
    assert yaml.encode() in result.content
    after = parse_note(result.content)
    assert result.content[after.region_end :] == raw[note.region_end :]


def test_unavailable_baseline_is_not_observed_null(example):
    raw = FIXTURE.read_bytes().replace(b'sf_status: Active', b'sf_status: null')
    note = parse_note(raw)
    state = state_for(raw, example)
    state = replace(state, generated_properties={**state.generated_properties, 'sf_status': FieldValue(Availability.UNAVAILABLE)})
    with pytest.raises(ConflictError):
        patch_note(raw, state, note.region, generated(example))
