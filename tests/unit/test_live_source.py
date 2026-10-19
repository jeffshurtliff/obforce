# -*- coding: utf-8 -*-
"""
:Module:            tests.unit.test_live_source
:Synopsis:          Verifies live Apex identity, bounded coverage and audit privacy offline
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     19 Oct 2026
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from obforce import constants as const
from obforce.errors import ConfigError, ConflictError, CoverageError, ModelError, OperationalError
from obforce.models import Availability, Selection, SourceBinding, component_fingerprint
from obforce.sources import live, sf_cli

FIXTURE = Path(__file__).parents[1] / 'fixtures/live/session.json'
PRIVATE = 'private-token private@example.invalid https://auth.invalid/secret'


def responses():
    """Load a fresh entirely fictional CLI session."""
    return json.loads(FIXTURE.read_bytes())


def reply(records, **signals):
    """Build an ordinary synthetic CLI success envelope."""
    return {'status': 0, 'result': {'records': records, 'totalSize': len(records), 'done': True, **signals}}


@pytest.fixture
def harness(tmp_path, monkeypatch):
    """Mock resolution and binary process collection; never invoke any installed sf."""
    pending, calls = [], []
    executable, directory = tmp_path / 'fictional-sf', tmp_path / 'work'
    directory.mkdir()
    monkeypatch.setattr(sf_cli, 'resolve_executable', lambda path: path)

    def collect(argv, cwd, limits):
        calls.append((argv, cwd, limits))
        assert pending, 'Unexpected process call'
        envelope = pending.pop(0)
        if isinstance(envelope, Exception):
            raise envelope
        return (1 if envelope.get('status', 0) else 0, json.dumps(envelope).encode(), False)

    monkeypatch.setattr(sf_cli, '_collect', collect)

    def run(items, **kwargs):
        pending.extend(copy.deepcopy(items))
        target = kwargs.pop('target', 'fictional org')
        result = live.collect_live(executable, directory=directory, target=target, workspace_id='demo', **kwargs)
        assert not pending
        return result

    return run, calls, pending


def test_realistic_normalization_and_controls(harness):
    """Observe identity first, scoped audits, explicit argv, limits and independent coverage."""
    run, calls, _ = harness
    result = run(responses())
    assert result.coverage.binding == SourceBinding('demo', 'live', '00D000000000001EAA')
    assert result.coverage.outcome == 0
    assert result.coverage.inventory.pagination == 'exhausted'
    assert result.coverage.relationships.status == 'not_collected'
    assert result.coverage.relationships.requested is False
    assert result.coverage.inventory.api_version is None
    component = next(c for c in result.components if c.key.full_name == 'FictionalService')
    assert component.attributes['api_version'].value == '67.0'
    assert component.attributes['created_at'].value == '2025-04-10T12:30:00.000000Z'
    assert component.attributes['created_by'].value == 'Fictional Creator'
    assert component.provenance == tuple(sorted((const.LIVE_APEX_METHOD, const.LIVE_AUDIT_METHOD)))
    assert len(result.inventory_hash) == 64
    queries = [call[0][7] for call in calls]
    assert queries[0] == 'SELECT Id FROM Organization LIMIT 2'
    assert queries[-1].endswith("Id > '01p000000000002AAA' ORDER BY Id LIMIT 200")
    assert 'CreatedBy.Name, LastModifiedBy.Name' in queries[3]
    assert ' IN (' in queries[2] and ' IN (' in queries[3]
    for argv, cwd, limits in calls:
        assert argv[1:6] == ['data', 'query', '--json', '--target-org', 'fictional org']
        assert '--use-tooling-api' in argv if argv[7] != queries[0] else '--use-tooling-api' not in argv
        assert 0 < limits.timeout <= 60 and limits.stdout == 262_144
        assert cwd.name == 'work'
    text = ' '.join(queries)
    for forbidden in ('Body', 'Username', 'Email', 'FROM User', 'CreatedById', 'LastModifiedById', 'OFFSET'):
        assert forbidden not in text
    assert 'Fictional' not in repr(result) and '00D' not in repr(result)


def test_multiple_pages_with_terminal_probe(harness):
    """A full or short page never removes the explicit terminal query requirement."""
    run, calls, _ = harness
    items = responses()
    first, second = items[1]['result']['records']
    result = run([items[0], reply([first]), reply([]), reply([second]), reply([]), reply([])], include_audit_names=False)
    assert len(result.components) == 2
    assert [e.returned for e in result.evidence if e.phase == 'inventory'] == [1, 1, 0]
    assert result.coverage.inventory.status == 'complete'
    assert result.coverage.audit.status == 'unavailable'  # Both requested date queries omitted all fields.
    assert "Id > '01p000000000001AAA'" in calls[3][0][7]


@pytest.mark.parametrize('field', ['configured_binding', 'state_binding'])
@pytest.mark.parametrize(
    'expected',
    [SourceBinding('demo', 'live', '00D000000000002EAA'), SourceBinding('other', 'live', 'x'), SourceBinding('demo', 'local')],
)
def test_binding_conflict_before_inventory(harness, field, expected):
    """Configured or state identity cannot adopt a different target/workspace/mode."""
    run, calls, _ = harness
    with pytest.raises(ConflictError):
        run([responses()[0]], **{field: expected})
    assert len(calls) <= 1


def test_alias_change_same_verified_binding(harness):
    """Stable source identity consists of verified org/workspace, never alias text."""
    run, _, _ = harness
    binding = SourceBinding('demo', 'live', '00D000000000001EAA')
    baseline = run(responses(), configured_binding=binding, state_binding=binding)
    result = run(responses(), target='different fictional alias', configured_binding=binding, state_binding=binding)
    assert result.coverage.binding == binding and result.inventory_hash == baseline.inventory_hash


@pytest.mark.parametrize('signals', [{'done': False}, {'totalSize': 2}, {'nextRecordsUrl': '/private/next'}, {'truncated': True}])
def test_identity_requires_consistent_complete_evidence(harness, signals):
    """A single identity value cannot override contradictory exhaustion signals."""
    run, calls, _ = harness
    identity = responses()[0]
    identity['result'].update(signals)
    with pytest.raises(CoverageError):
        run([identity])
    assert len(calls) == 1


@pytest.mark.parametrize('records', [[], [{'Id': '00D000000000001EAA'}, {'Id': '00D000000000002EAA'}]])
def test_identity_cardinality(harness, records):
    """Missing or ambiguous actual org identity blocks acquisition."""
    run, _, _ = harness
    with pytest.raises(CoverageError):
        run([reply(records)])


@pytest.mark.parametrize(
    'signals,code',
    [
        ({'done': False}, 'done_not_true'),
        ({'totalSize': 9}, 'count_mismatch'),
        ({'nextRecordsUrl': PRIVATE}, 'continuation_present'),
        ({'hasMore': True}, 'unexpected_result_fields'),
    ],
)
def test_contradictory_empty_page_is_partial(harness, signals, code):
    """No process success, empty array or done flag alone proves exhaustion."""
    run, _, _ = harness
    result = run([responses()[0], reply([], **signals)])
    assert result.coverage.inventory.status == 'partial'
    assert result.coverage.outcome == 4
    assert code in result.coverage.inventory.warnings
    assert result.evidence[-1].reported_total == signals.get('totalSize', 0)
    assert PRIVATE not in repr(result) and PRIVATE not in str(result.coverage.canonical())


@pytest.mark.parametrize('phase', [0, 1])
def test_warning_or_stderr_cannot_prove_coverage(harness, monkeypatch, phase):
    """Retain warning presence without publishing private diagnostic text."""
    run, _, _ = harness
    if phase == 0:
        item = reply([])
        item['warnings'] = [PRIVATE]
        result = run([responses()[0], item])
        assert 'cli_warning_present' in result.coverage.inventory.warnings
    else:
        original = sf_cli._collect
        count = 0

        def stderr(*args):
            nonlocal count
            code, raw, _ = original(*args)
            count += 1
            return code, raw, count == 2

        monkeypatch.setattr(sf_cli, '_collect', stderr)
        result = run([responses()[0], reply([])])
        assert 'stderr_present' in result.coverage.inventory.warnings
    assert result.coverage.outcome == 4
    assert PRIVATE not in str(result.coverage.canonical())


def test_empty_inventory_complete_only_with_all_signals(harness):
    """Empty accessible selected scope includes identity and consistent bounded query evidence."""
    run, calls, _ = harness
    result = run([responses()[0], reply([])])
    assert result.components == () and result.coverage.outcome == 0
    assert len(calls) == 2 and result.coverage.audit.status == 'complete'


@pytest.mark.parametrize('include', [False, True])
def test_namespaces_and_internal_filters(harness, include):
    """Namespace selection is explicit; name filters never enter query syntax or audit scope."""
    run, calls, _ = harness
    items = responses()
    row = items[1]['result']['records'][0]
    row['NamespacePrefix'] = 'fictional'
    selection = Selection(include_namespaced=include, full_names=('FictionalService',))
    if include:
        result = run([items[0], reply([row]), reply([]), reply([])], selection=selection, include_audit_names=False)
        assert len(result.components) == 1
        assert 'NamespacePrefix = null' not in calls[1][0][7]
    else:
        result = run([items[0], reply([row])], selection=selection, include_audit_names=False)
        assert result.components == () and result.coverage.inventory.status == 'partial'
        assert 'namespace_scope_contradiction' in result.coverage.inventory.warnings
    assert 'FictionalService' not in calls[1][0][7]


def test_filtered_names_never_enrich_unselected_ids(harness):
    """Only selected components appear in scoped date/name projections."""
    run, calls, _ = harness
    items = responses()
    items[2]['result']['records'] = items[2]['result']['records'][:1]
    items[2]['result']['totalSize'] = 1
    items[3]['result']['records'] = items[3]['result']['records'][:1]
    items[3]['result']['totalSize'] = 1
    result = run(items, selection=Selection(full_names=('FictionalService',)))
    assert len(result.components) == 1
    assert '01p000000000002AAA' not in calls[2][0][7] + calls[3][0][7]


def test_audit_omission_absent_null_and_unavailable(harness):
    """Privacy omission stays absent; null is observed; missing requested dates are unavailable."""
    run, calls, _ = harness
    items = responses()
    dates = items[2]['result']['records'][0]
    dates['CreatedDate'] = None
    del dates['LastModifiedDate']
    result = run([*items[:3], items[4]], include_audit_names=False)
    component = next(c for c in result.components if c.key.full_name == 'FictionalService')
    assert component.attributes['created_at'].availability is Availability.NULL
    assert component.attributes['last_modified_at'].availability is Availability.UNAVAILABLE
    assert 'created_by' not in component.attributes and 'last_modified_by' not in component.attributes
    assert not any('.Name' in call[0][7] for call in calls)
    assert result.coverage.inventory.status == 'complete' and result.coverage.audit.status == 'partial'


@pytest.mark.parametrize('phase', [2, 3])
def test_optional_permission_or_field_failure(harness, phase):
    """Redacted optional query failure does not erase required inventory or invent audit values."""
    run, _, _ = harness
    items = responses()
    items[phase] = {'status': 1, 'name': 'INVALID_FIELD', 'message': PRIVATE}
    result = run(items)
    assert result.coverage.inventory.status == 'complete'
    assert result.coverage.audit.status == 'partial' and result.coverage.outcome == 4
    assert PRIVATE not in str(result.coverage.canonical())
    assert any('query_unavailable' in w for w in result.coverage.audit.warnings)


@pytest.mark.parametrize('phase', [0, 1, 4])
def test_required_permission_loss_fails_operationally(harness, phase):
    """Required identity/inventory errors preserve operational failure including later permission loss."""
    run, _, _ = harness
    items = responses()[: phase + 1]
    items[phase] = {'status': 1, 'name': 'INSUFFICIENT_ACCESS', 'message': PRIVATE}
    with pytest.raises(OperationalError) as error:
        run(items)
    assert type(error.value) is OperationalError and error.value.exit_code == 1
    assert PRIVATE not in str(error.value)


@pytest.mark.parametrize(
    'field,value',
    [
        ('Id', 'bad'),
        ('Id', '01p000000000001ZZZ'),
        ('Name', '../bad'),
        ('NamespacePrefix', 'bad_name'),
        ('ApiVersion', True),
        ('ApiVersion', '67.5'),
        ('ApiVersion', -1),
        ('ApiVersion', 'private'),
        ('Status', 'Inactive'),
    ],
)
def test_invalid_inventory_values(harness, field, value):
    """Invalid IDs, versions, statuses or identity text cannot reach normalized records."""
    run, _, _ = harness
    items = responses()[:2]
    items[1]['result']['records'][0][field] = value
    with pytest.raises(ModelError):
        run(items)


@pytest.mark.parametrize('date', ['2026-02-30T12:00:00Z', '2026-01-01', '2026-01-01T12:00:00', PRIVATE, 1])
def test_invalid_audit_date(harness, date):
    """Optional query success cannot legitimize malformed observed audit values."""
    run, _, _ = harness
    items = responses()[:3]
    items[2]['result']['records'][0]['CreatedDate'] = date
    with pytest.raises(ModelError) as error:
        run(items)
    assert PRIVATE not in str(error.value)


@pytest.mark.parametrize('kind', ['record_id', 'key', 'cross_page', 'audit'])
def test_duplicate_records_are_conflicts(harness, kind):
    """Reject identical and conflicting duplicates before silent merging or hashing."""
    run, _, _ = harness
    items = responses()
    if kind == 'record_id':
        items[1]['result']['records'][1]['Id'] = items[1]['result']['records'][0]['Id']
        items = items[:2]
    elif kind == 'key':
        items[1]['result']['records'][1]['Name'] = items[1]['result']['records'][0]['Name']
        items = items[:2]
    elif kind == 'cross_page':
        items[4] = items[1]
    else:
        items[2]['result']['records'][1]['Id'] = items[2]['result']['records'][0]['Id']
        items = items[:3]
    with pytest.raises(ConflictError):
        run(items)


def test_deterministic_hashes_and_observed_audit_change(harness):
    """Response field/audit ordering and equivalent UTC times do not change semantic hashes."""
    run, _, _ = harness
    first = run(responses())
    items = responses()
    items[2]['result']['records'].reverse()
    items[3]['result']['records'].reverse()
    for record in items[2]['result']['records']:
        record['CreatedDate'] = '2025-04-10T14:30:00+02:00'
    second = run(items)
    assert first.inventory_hash == second.inventory_hash
    assert first.inventory_hash == component_fingerprint(reversed(first.components))
    items[2]['result']['records'][0]['CreatedDate'] = '2025-04-11T14:30:00+02:00'
    assert run(items).inventory_hash != first.inventory_hash


@pytest.mark.parametrize('budget', ['pages', 'queries', 'records', 'time'])
def test_finite_collection_budget_is_incomplete(harness, monkeypatch, budget):
    """Record/page/process/time bounds never become success without terminal evidence."""
    run, _, _ = harness
    items = responses()
    if budget == 'pages':
        monkeypatch.setattr(const, 'MAX_LIVE_PAGES', 1)
        items = items[:4]
    elif budget == 'queries':
        monkeypatch.setattr(const, 'MAX_LIVE_QUERIES', 2)
        items = items[:2]
    elif budget == 'records':
        monkeypatch.setattr(const, 'MAX_LIVE_RECORDS', 1)
        items = items[:2]
    else:
        ticks = iter([0, 0, 0, 301, 301, 301])
        monkeypatch.setattr(live.time, 'monotonic', lambda: next(ticks))
        items = items[:2]
    result = run(items)
    assert result.coverage.inventory.status == 'partial'
    assert result.coverage.inventory.limit_reached is True and result.coverage.outcome == 4


@pytest.mark.parametrize('target', ['', '-bad', ' demo', 'demo\nsecret'])
def test_invalid_target_stops_before_process(harness, tmp_path, target):
    """Accepted process target validation cannot fall back to default-org selection."""
    _, calls, _ = harness
    with pytest.raises(ConfigError):
        live.collect_live(tmp_path / 'sf', directory=tmp_path, target=target, workspace_id='demo')
    assert calls == []


def test_windows_still_refused(tmp_path, monkeypatch):
    """An adapter invocation provides no Windows transport workaround or qualification."""
    monkeypatch.setattr(sf_cli.os, 'name', 'nt')
    with pytest.raises(ConfigError, match='unavailable on this platform'):
        live.collect_live(tmp_path / 'sf.exe', directory=tmp_path, target='demo', workspace_id='demo')


@pytest.mark.parametrize('field', ['Id', 'Name', 'NamespacePrefix', 'ApiVersion', 'Status'])
def test_required_field_absence_fails_closed(harness, field):
    """Do not invent inventory identities or required facts when a field is absent."""
    run, _, _ = harness
    items = responses()[:2]
    del items[1]['result']['records'][0][field]
    with pytest.raises(ModelError):
        run(items)


@pytest.mark.parametrize('field', ['Body', 'Email', 'Username', 'technical_debt'])
def test_unrequested_fields_not_accepted(harness, field):
    """Unexpected raw private fields cannot become normalized facts or debt assessments."""
    run, _, _ = harness
    items = responses()[:2]
    items[1]['result']['records'][0][field] = PRIVATE
    with pytest.raises(ModelError) as error:
        run(items)
    assert PRIVATE not in str(error.value)


@pytest.mark.parametrize('value', [None, {}, {'Name': None}])
def test_audit_relationship_availability(harness, value):
    """Null relationships/names are observed null; missing nested names stay unavailable."""
    run, _, _ = harness
    items = responses()
    items[3]['result']['records'][0]['CreatedBy'] = value
    result = run(items)
    component = next(c for c in result.components if c.key.full_name == 'FictionalService')
    expected = Availability.UNAVAILABLE if value == {} else Availability.NULL
    assert component.attributes['created_by'].availability is expected


@pytest.mark.parametrize('value', [PRIVATE + '\n', {'Name': PRIVATE, 'Email': PRIVATE}, 'not-a-relationship'])
def test_invalid_audit_relationship_refused_privately(harness, value):
    """Structured audit fields accept only bounded display-name values."""
    run, _, _ = harness
    items = responses()[:4]
    items[3]['result']['records'][0]['CreatedBy'] = value
    with pytest.raises(ModelError) as error:
        run(items)
    assert PRIVATE not in str(error.value)


@pytest.mark.parametrize('phase', [2, 3])
def test_partial_optional_envelope_preserves_independent_evidence(harness, phase):
    """Optional contradictory completion signals remain visible without clearing inventory."""
    run, _, _ = harness
    items = responses()
    items[phase]['result'].update(done=False, totalSize=10, nextRecordsUrl=PRIVATE)
    result = run(items)
    assert result.coverage.inventory.status == 'complete'
    assert result.coverage.audit.status == 'partial'
    evidence = result.evidence[phase]
    assert evidence.done is False and evidence.reported_total == 10 and evidence.continuation
    assert PRIVATE not in repr(evidence)


@pytest.mark.parametrize('phase', [2, 3])
def test_unselected_optional_identity_is_conflict(harness, phase):
    """An unrelated Apex record cannot be silently attached to a selected component."""
    run, _, _ = harness
    items = responses()[: phase + 1]
    items[phase]['result']['records'][0]['Id'] = '01p000000000003AAA'
    with pytest.raises(ConflictError):
        run(items)


def test_15_character_ids_canonicalize_without_hash_drift(harness):
    """Supplementary IDs share a canonical representation before binding and duplicate checks."""
    run, _, _ = harness
    baseline = run(responses())
    items = responses()
    for envelope in items:
        for record in envelope['result']['records']:
            record['Id'] = record['Id'][:15]
    assert run(items).inventory_hash == baseline.inventory_hash


@pytest.mark.parametrize('date', ['2026-01-01T00:00:00+00:99', '2026-01-01T00:00:00+2499'])
def test_invalid_offset_not_silently_normalized(harness, date):
    """Datetime's permissive offset-minute normalization must not invent valid audit times."""
    run, _, _ = harness
    items = responses()[:3]
    items[2]['result']['records'][0]['CreatedDate'] = date
    with pytest.raises(ModelError):
        run(items)


def test_malformed_optional_envelope_unavailable_not_success(harness):
    """A malformed optional JSON envelope cannot falsely complete requested audit coverage."""
    run, _, _ = harness
    items = responses()
    items[2] = {'status': 0, 'result': {'records': [], 'done': True}}
    result = run(items)
    assert result.coverage.inventory.status == 'complete'
    assert result.coverage.audit.status == 'partial' and result.coverage.outcome == 4


@pytest.mark.parametrize('failure', [ConfigError('safe'), ConflictError('safe'), ModelError('safe')])
def test_optional_phase_does_not_swallow_higher_precedence(harness, failure):
    """Existing config/model/conflict semantics outrank optional incomplete coverage."""
    run, _, _ = harness
    with pytest.raises(type(failure)):
        run([*responses()[:2], failure])


def test_no_name_match_still_exhausts_inventory_without_audits(harness):
    """A local name filter does not stop selected-scope enumeration at a nonmatching page."""
    run, calls, _ = harness
    result = run([*responses()[:2], reply([])], selection=Selection(full_names=("not-selected' OR Id != null",)))
    assert result.components == () and result.coverage.outcome == 0
    assert len(calls) == 3 and not any('not-selected' in call[0][7] for call in calls)


@pytest.mark.parametrize('value', ["01p000000000001' OR Id != null", '01p000000000001;SELECT', '01p000000000001\n', PRIVATE])
def test_response_id_cannot_inject_next_queries(harness, value):
    """Only validated IDs may enter scoped audit predicates or the next-page cursor."""
    run, calls, _ = harness
    items = responses()[:2]
    items[1]['result']['records'][0]['Id'] = value
    with pytest.raises(ModelError):
        run(items)
    assert len(calls) == 2 and value not in calls[-1][0][7]


@pytest.mark.parametrize(
    'field,value', [('selection', 'bad'), ('include_audit_names', 1), ('configured_binding', {}), ('state_binding', {})]
)
def test_invalid_invocation_before_process(harness, field, value):
    """Invalid internal selection/privacy/binding inputs never launch a process."""
    run, calls, _ = harness
    with pytest.raises(ConfigError):
        run([], **{field: value})
    assert calls == []


def test_same_name_different_namespace_is_distinct(harness):
    """Namespace inclusion preserves the existing structured key without a filename-based merge."""
    run, _, _ = harness
    items = responses()
    items[1]['result']['records'][1].update(Name='FictionalService', NamespacePrefix='fictional')
    result = run(items, selection=Selection(include_namespaced=True))
    assert len(result.components) == 2 and result.coverage.outcome == 0
    assert {c.key.namespace for c in result.components} == {None, 'fictional'}


def test_terminal_probe_at_record_ceiling_is_permitted(harness, monkeypatch):
    """Reaching the record ceiling does not block the bounded empty exhaustion probe."""
    run, _, _ = harness
    monkeypatch.setattr(const, 'MAX_LIVE_RECORDS', 2)
    assert run(responses()).coverage.outcome == 0


def test_mocked_collection_creates_no_work_artifacts(harness):
    """The internal read-only adapter leaves existing work files, bytes and mtimes untouched."""
    run, calls, _ = harness
    result = run(responses())
    directory = calls[0][1]
    assert list(directory.iterdir()) == []
    marker = directory / 'user-note.md'
    marker.write_text('Fictional user prose')
    before = marker.read_bytes(), marker.stat().st_mtime_ns
    again = run(responses())
    assert (marker.read_bytes(), marker.stat().st_mtime_ns) == before
    assert list(directory.iterdir()) == [marker]
    assert again.inventory_hash == result.inventory_hash


@pytest.mark.parametrize('id_value', ['00D000000000001ZZZ', '01p000000000001AAA', None, PRIVATE])
def test_invalid_org_identity_not_bound(harness, id_value):
    """A well-formed success envelope cannot verify an invalid/wrong-object org ID."""
    run, calls, _ = harness
    with pytest.raises(ModelError) as error:
        run([reply([{'Id': id_value}])])
    assert len(calls) == 1 and PRIVATE not in str(error.value)
