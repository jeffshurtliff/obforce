# -*- coding: utf-8 -*-
"""
:Module:            tests.unit.test_relationship_source
:Synopsis:          Verifies bounded relationship probes and honest coverage with synthetic CLI replies
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     19 Oct 2026
"""

from __future__ import annotations

import copy
import json
import socket
import subprocess
from dataclasses import replace
from pathlib import Path

import pytest

from obforce import constants as const
from obforce.errors import ConfigError, ConflictError, CoverageError, ModelError, OperationalError
from obforce.graph.dependencies import DependencyGraph, component_index
from obforce.models import CollectionCoverage, Component, ComponentKey, Coverage, CoverageStatus, Selection, SourceBinding
from obforce.sources import live, relationships, sf_cli

PRIVATE = 'private-token private@example.invalid https://auth.invalid/secret'
BINDING = SourceBinding('demo', 'live', '00D000000000001EAA')
COMPLETE = CollectionCoverage(CoverageStatus.COMPLETE, 'synthetic-inventory', pagination='exhausted', limit_reached=False)
NOT_COLLECTED = CollectionCoverage(CoverageStatus.NOT_COLLECTED, 'not-collected', requested=False)
A = Component(BINDING, ComponentKey('demo', 'ApexClass', None, 'FictionalService'), record_id='01p000000000001AAA')
B = Component(BINDING, ComponentKey('demo', 'ApexClass', None, 'FictionalHelper'), record_id='01p000000000002AAA')
INVENTORY = live.LiveInventory((A, B), Coverage(BINDING, Selection(), COMPLETE, COMPLETE, NOT_COLLECTED))


def row(**changes):
    """Load a small entirely fictional directed endpoint fixture."""
    record = json.loads((Path(__file__).parents[1] / 'fixtures/relationships/edge.json').read_bytes())
    record.update(changes)
    return record


def reply(records=(), **signals):
    """Encode synthetic CLI success with explicit independent envelope signals."""
    return {'status': 0, 'result': {'records': list(records), 'totalSize': len(records), 'done': True, **signals}}


def identity(org_id=BINDING.org_id):
    """Supply the required minimal identity evidence before every relationship session."""
    return reply([{'Id': org_id}])


@pytest.fixture
def harness(tmp_path, monkeypatch):
    """Mock the binary collector while forbidding sockets and real process creation."""
    pending, calls = [], []
    executable, directory = tmp_path / 'fictional-sf', tmp_path / 'neutral'
    directory.mkdir()

    def denied(*args, **kwargs):
        raise AssertionError('Real network/process execution forbidden')

    monkeypatch.setattr(socket, 'socket', denied)
    monkeypatch.setattr(subprocess, 'Popen', denied)
    monkeypatch.setattr(sf_cli, 'resolve_executable', lambda path: path)

    def collect(argv, cwd, limits):
        calls.append((argv, cwd, limits))
        assert pending, 'Unexpected process request'
        item = pending.pop(0)
        if isinstance(item, Exception):
            raise item
        stderr = item.pop('_stderr', False)
        return (1 if item.get('status', 0) else 0, json.dumps(item).encode(), stderr)

    monkeypatch.setattr(sf_cli, '_collect', collect)

    def run(items, **kwargs):
        pending.extend(copy.deepcopy(items))
        result = relationships.collect_relationships(
            executable,
            directory=directory,
            target=kwargs.pop('target', 'fictional org'),
            inventory=kwargs.pop('inventory', INVENTORY),
            **kwargs,
        )
        assert not pending
        return result

    return run, calls, pending


def session(records=()):
    """Probe A outgoing/incoming and B outgoing/incoming without unsupported pagination."""
    return [identity(), reply(records), reply(), reply(), reply(records)]


def test_fixed_safe_probes_and_reciprocal_views(harness):
    """A -> B updates one graph in both directions and never alters inventory/audit/source hashes."""
    run, calls, _ = harness
    before = INVENTORY.inventory_hash
    result = run(session([row(), row()]))
    graph = result.graph
    assert len(graph.edges) == 1 and len(graph.edges[0].evidence) == 2
    assert graph.references(A.key) == graph.referenced_by(B.key) == graph.edges
    assert result.coverage.inventory is COMPLETE and result.coverage.audit is COMPLETE
    assert result.coverage.relationships.status == 'partial' and result.coverage.outcome == 4
    assert result.coverage.relationships.api_version is None
    assert INVENTORY.inventory_hash == before and INVENTORY.coverage.relationships == NOT_COLLECTED
    assert len(calls) == 5
    assert calls[0][0][7] == 'SELECT Id FROM Organization LIMIT 2'
    for argv, cwd, limits in calls[1:]:
        assert argv[1:6] == ['data', 'query', '--json', '--target-org', 'fictional org']
        assert argv[-1] == '--use-tooling-api' and cwd.name == 'neutral'
        assert limits.stdout == const.MAX_RELATIONSHIP_STDOUT_BYTES and 0 < limits.timeout <= 60
        query = argv[7]
        assert query.startswith('SELECT ' + relationships._PROJECTION + ' FROM MetadataComponentDependency WHERE ')
        assert "Id = '01p" in query and query.endswith("Type = 'ApexClass'")
        for forbidden in ('Body', 'SymbolTable', 'FullName', 'COUNT(', 'ORDER BY', 'OFFSET', ' LIMIT ', ' > ', ' IN ', ' LIKE '):
            assert forbidden not in query
    assert 'FictionalService' not in repr(result) and '00D' not in repr(result)


def test_empty_success_cannot_claim_exhaustion_or_erase_prior(harness):
    """Even four clean empty replies lack an independent MCD exhaustion contract."""
    run, _, _ = harness
    previous = run(session([row()])).graph
    result = run(session(), previous=previous)
    assert result.coverage.outcome == 4 and result.graph.edges[0].stale
    assert 'exhaustion_unverifiable' in result.coverage.relationships.warnings
    assert result.graph.edges[0].evidence[0].method.startswith(const.RELATIONSHIP_METHOD)


@pytest.mark.parametrize(
    'signals,code',
    [
        ({'done': False}, 'done_not_true'),
        ({'totalSize': 8}, 'count_mismatch'),
        ({'nextRecordsUrl': PRIVATE}, 'continuation_present'),
        ({'hasMore': True}, 'unexpected_result_fields'),
    ],
)
def test_contradictory_pagination_signals_remain_private(harness, signals, code):
    """Counts/continuations cannot be cleared by later clean replies or followed as endpoints."""
    run, calls, _ = harness
    items = session()
    items[1] = reply(**signals)
    result = run(items)
    assert result.coverage.relationships.status == 'partial'
    assert 'relationships_outgoing:' + code in result.coverage.relationships.warnings
    assert code in result.evidence[1].problems and len(calls) == 5
    assert PRIVATE not in str(result.coverage.canonical()) + repr(result) + repr(result.evidence)


def test_all_contradictions_warning_stderr_and_prior_evidence_retained(harness):
    """A single contradictory reply preserves each safe signal and both fresh/stale evidence."""
    run, _, _ = harness
    previous = run(session([row()])).graph
    items = session([row()])
    items[1]['result'].update(done=False, totalSize=5, nextRecordsUrl=PRIVATE, unknown=True)
    items[1].update(warnings=[PRIVATE], _stderr=True)
    result = run(items, previous=previous)
    assert len(result.evidence[1].problems) == 6
    assert any(item.stale for item in result.graph.edges[0].evidence)
    assert PRIVATE not in str(result.graph.edges[0].canonical())
    assert result.coverage.inventory is COMPLETE


@pytest.mark.parametrize(
    'failure',
    [
        OperationalError('CLI request failed.'),
        {'status': 1, 'name': 'INSUFFICIENT_ACCESS', 'message': PRIVATE},
        {'status': 1, 'name': 'INVALID_TYPE', 'message': PRIVATE},
        {'status': 0, 'result': {'records': [], 'totalSize': -1, 'done': True}},
    ],
)
def test_optional_permission_capability_and_malformed_envelope_failures(harness, failure):
    """Redacted transport failure is unavailable; no guessed permission/type workaround is sent."""
    run, calls, _ = harness
    previous = run(session([row()])).graph
    result = run([identity(), failure, failure, failure, failure], previous=previous)
    assert result.coverage.relationships.status == 'unavailable' and result.coverage.outcome == 4
    assert all(edge.stale for edge in result.graph.edges)
    assert any('query_unavailable' in warning for warning in result.coverage.relationships.warnings)
    assert PRIVATE not in repr(result) + str(result.coverage.canonical())
    assert len(calls) == 10


@pytest.mark.parametrize(
    'failure',
    [ConfigError('Invalid configured input.'), ModelError('Invalid observed input.'), ConflictError('Conflicting identity.')],
)
def test_higher_precedence_errors_are_not_swallowed(harness, failure):
    """Only exact optional operational errors degrade to coverage outcomes."""
    run, _, _ = harness
    with pytest.raises(type(failure)):
        run([identity(), failure])


@pytest.mark.parametrize(
    'change',
    [
        {'MetadataComponentId': '01p000000000003AAA'},
        {'MetadataComponentType': 'Flow'},
    ],
)
def test_unselected_anchor_is_conflict(harness, change):
    """An equality query response cannot silently broaden selected source/target IDs."""
    run, _, _ = harness
    with pytest.raises(ConflictError):
        run([identity(), reply([row(**change)])])


def test_descriptor_contradictions_and_unsupported_targets_are_retained(harness):
    """Mismatching name/namespace facts stay unresolved while supported neighbors retain evidence."""
    run, _, _ = harness
    rows = [
        row(RefMetadataComponentName='ContradictoryName'),
        row(RefMetadataComponentNamespace='pkg'),
        row(RefMetadataComponentType='CustomField', RefMetadataComponentId='Account.FictionalField__c'),
        row(RefMetadataComponentName=None, RefMetadataComponentId=None),
    ]
    result = run([identity(), reply(rows), reply(), reply(), reply()])
    assert len(result.graph.references(A.key)) == 4 and result.graph.referenced_by(B.key) == ()
    assert {e.target.resolution for e in result.graph.edges} == {'identity_mismatch', 'unsupported', 'unresolved'}
    assert 'endpoint_identity_contradiction' in result.coverage.relationships.warnings


def test_unsupported_referencing_endpoint_in_incoming_view(harness):
    """A Flow -> A observation remains incoming, labeled and unsupported without a new note type."""
    run, _, _ = harness
    record = row(
        MetadataComponentId='fictional-flow',
        MetadataComponentType='Flow',
        MetadataComponentName='FictionalFlow',
        RefMetadataComponentId=A.record_id,
        RefMetadataComponentName=A.key.full_name,
    )
    result = run([identity(), reply(), reply([record]), reply(), reply()])
    assert result.graph.referenced_by(A.key)[0].source.resolution == 'unsupported'
    assert result.graph.references(A.key) == ()


@pytest.mark.parametrize(
    'field,value',
    [
        ('RefMetadataComponentId', 'bad-private-id'),
        ('RefMetadataComponentNamespace', 4),
        ('RefMetadataComponentName', PRIVATE + '\x00'),
        ('MetadataComponentType', ['ApexClass']),
        ('RefMetadataComponentName', 'x' * 513),
        ('Body', PRIVATE),
    ],
)
def test_invalid_projected_fields_fail_safely(harness, field, value):
    """Malformed fields or an unexpected body cannot be normalized into graph data."""
    run, _, _ = harness
    with pytest.raises(ModelError) as error:
        run([identity(), reply([row(**{field: value})])])
    assert PRIVATE not in str(error.value)


def test_missing_nullable_field_is_not_silently_known_null(harness):
    """The eight projected keys must be present, even for unresolved nullable endpoints."""
    run, _, _ = harness
    record = row()
    record.pop('RefMetadataComponentNamespace')
    with pytest.raises(ModelError):
        run([identity(), reply([record])])


@pytest.mark.parametrize('signals', [{'done': False}, {'totalSize': 2}, {'nextRecordsUrl': PRIVATE}])
def test_identity_ambiguity_blocks_all_relationships(harness, signals):
    """Identity verification cannot rely on a returned org ID alone."""
    run, calls, _ = harness
    item = identity()
    item['result'].update(signals)
    with pytest.raises(CoverageError):
        run([item])
    assert len(calls) == 1


def test_different_actual_org_blocks_collection(harness):
    """Retargeted aliases cannot rebind the graph/inventory source."""
    run, calls, _ = harness
    with pytest.raises(ConflictError):
        run([identity('00D000000000002EAA')])
    assert len(calls) == 1


@pytest.mark.parametrize(
    'binding,selection',
    [
        (SourceBinding('other', 'live', BINDING.org_id), Selection()),
        (SourceBinding('demo', 'live', '00D000000000002EAA'), Selection()),
        (SourceBinding('demo', 'local'), Selection()),
        (BINDING, Selection(True)),
    ],
)
def test_previous_binding_scope_mismatch_refused_before_process(harness, binding, selection):
    """No incompatible prior edge can be adopted even during optional failure."""
    run, calls, _ = harness
    previous = DependencyGraph(binding, selection, NOT_COLLECTED)
    with pytest.raises(ConflictError):
        run([], previous=previous)
    assert calls == []


def test_finite_query_budget_and_stale_preservation(harness, monkeypatch):
    """Stop before another process call, retaining selected fresh and prior stale observations."""
    run, calls, _ = harness
    previous = run(session([row()])).graph
    monkeypatch.setattr(const, 'MAX_RELATIONSHIP_QUERIES', 2)
    result = run([identity(), reply()], previous=previous)
    assert len(calls) == 7 and result.graph.edges[0].stale
    assert result.coverage.relationships.limit_reached is True
    assert 'collection_budget_exhausted' in result.coverage.relationships.warnings


def test_finite_record_budget_before_dedup(harness, monkeypatch):
    """Duplicate rows count against bounds and cannot become an exhaustion shortcut."""
    run, _, _ = harness
    monkeypatch.setattr(const, 'MAX_RELATIONSHIP_RECORDS', 1)
    result = run([identity(), reply([row(), row()])])
    assert result.graph.edges == () and result.coverage.relationships.limit_reached is True
    assert 'record_budget_exhausted' in result.coverage.relationships.warnings


def test_documented_cap_is_not_exhaustion(harness):
    """An exact cap response stays partial even when counts and done claim consistency."""
    run, _, _ = harness
    result = run([identity(), reply([row()] * 2000), reply(), reply(), reply()])
    assert result.coverage.relationships.limit_reached is True
    assert 'relationships_outgoing:documented_query_cap_reached' in result.coverage.relationships.warnings
    assert len(result.graph.edges) == 1


def test_wall_deadline_prevents_further_query(harness, monkeypatch):
    """The whole-session deadline includes identity and optional query work."""
    run, calls, _ = harness
    ticks = iter([0, 0, 301])
    monkeypatch.setattr(live.time, 'monotonic', lambda: next(ticks))
    result = run([identity()])
    assert len(calls) == 1 and result.coverage.relationships.status == 'unavailable'
    assert result.coverage.relationships.limit_reached is True


def test_empty_or_incomplete_inventory_is_independent(harness):
    """No selected endpoints is unavailable, while inventory/audit records remain unchanged."""
    run, calls, _ = harness
    empty = replace(INVENTORY, components=())
    result = run([identity()], inventory=empty)
    assert len(calls) == 1 and result.coverage.relationships.status == 'unavailable'
    assert result.coverage.inventory is COMPLETE
    partial = replace(INVENTORY, coverage=replace(INVENTORY.coverage, inventory=replace(COMPLETE, status=CoverageStatus.PARTIAL)))
    result = run(session(), inventory=partial)
    assert 'inventory_not_exhausted' in result.coverage.relationships.warnings
    assert result.coverage.audit is COMPLETE


def test_alias_and_order_do_not_change_graph_hashes(harness):
    """Private incidental URLs/order/target aliases never enter semantic graph hashes."""
    run, _, _ = harness
    baseline = run(session([row()]))
    record = row(attributes={'url': PRIVATE, 'type': 'MetadataComponentDependency'})
    reordered = replace(INVENTORY, components=tuple(reversed(INVENTORY.components)))
    result = run(session([record, record]), target='different alias', inventory=reordered)
    paths = {A.key: 'A.md', B.key: 'B.md'}
    assert baseline.graph.note_fingerprint(A.key, paths) == result.graph.note_fingerprint(A.key, paths)
    assert PRIVATE not in str(result.graph.edges[0].canonical())


def test_namespaced_endpoint_identity_and_filtering(harness):
    """Managed resolution requires exact namespace even when names match across packages."""
    run, _, _ = harness
    namespaced = replace(B, key=replace(B.key, namespace='demoPkg'))
    inventory = replace(INVENTORY, components=(A, namespaced), coverage=replace(INVENTORY.coverage, selection=Selection(True)))
    record = row(RefMetadataComponentNamespace='demoPkg')
    result = run(session([record]), inventory=inventory)
    assert result.graph.referenced_by(namespaced.key) == result.graph.references(A.key)
    assert component_index(inventory.components, BINDING, Selection(True))[B.record_id].key == namespaced.key


def test_returned_id_and_empty_namespace_normalization(harness):
    """Equivalent 15/18-character reported IDs and null/empty namespaces deduplicate."""
    run, _, _ = harness
    normal = row()
    alternate = row(
        MetadataComponentId=A.record_id[:15],
        RefMetadataComponentId=B.record_id[:15],
        MetadataComponentNamespace='',
        RefMetadataComponentNamespace='',
    )
    result = run(session([normal, alternate]))
    assert len(result.graph.edges) == 1
    assert result.graph.references(A.key) == result.graph.referenced_by(B.key)


@pytest.mark.parametrize('record_id', ["01p000000000001AAA' OR Id != null", '01p000000000001', PRIVATE])
def test_untrusted_inventory_id_never_enters_soql(harness, record_id):
    """A malformed or noncanonical supplied ID refuses before identity or relationship calls."""
    run, calls, _ = harness
    invalid = replace(INVENTORY, components=(replace(A, record_id=record_id), B))
    with pytest.raises(ModelError) as error:
        run([], inventory=invalid)
    assert calls == [] and PRIVATE not in str(error.value)


def test_required_identity_failure_keeps_operational_precedence(harness):
    """Required org verification never degrades to optional unavailable relationship coverage."""
    run, calls, _ = harness
    with pytest.raises(OperationalError) as error:
        run([OperationalError('Salesforce CLI request failed.')])
    assert type(error.value) is OperationalError and error.value.exit_code == 1
    assert len(calls) == 1


@pytest.mark.parametrize('target', ['', '--default', None])
def test_no_implicit_or_option_like_target(harness, target):
    """Explicit target controls remain enforced by the accepted CLI boundary."""
    run, calls, _ = harness
    with pytest.raises(ConfigError):
        run([], target=target)
    assert calls == []


def test_collection_creates_no_working_directory_files(harness):
    """Mocked runtime collection emits no config/state/lock/log/cache/note artifacts."""
    run, calls, _ = harness
    result = run(session([row()]))
    directory = calls[0][1]
    assert list(directory.iterdir()) == []
    assert result.graph.edges
