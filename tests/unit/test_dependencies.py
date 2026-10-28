# -*- coding: utf-8 -*-
"""
:Module:            tests.unit.test_dependencies
:Synopsis:          Verifies directed graph preservation and reciprocal invalidation offline
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     28 Oct 2026
"""

from dataclasses import replace

import pytest

from obforce import constants as const
from obforce.errors import ConfigError, ConflictError, ModelError
from obforce.graph.dependencies import DependencyGraph, Edge, Endpoint, Evidence, component_index, refresh_graph, resolve_endpoint
from obforce.models import (
    CollectionCoverage,
    Component,
    ComponentKey,
    CoverageStatus,
    Selection,
    SourceBinding,
    component_fingerprint,
)

BINDING = SourceBinding('demo', 'live', '00D000000000001EAA')
SELECTION = Selection()
COMPLETE = CollectionCoverage(CoverageStatus.COMPLETE, 'synthetic-reported', pagination='exhausted', limit_reached=False)
PARTIAL = CollectionCoverage(CoverageStatus.PARTIAL, 'synthetic-reported', warnings=('synthetic_truncation',))
UNAVAILABLE = CollectionCoverage(CoverageStatus.UNAVAILABLE, 'synthetic-reported', warnings=('query_unavailable',))
A = Component(BINDING, ComponentKey('demo', 'ApexClass', None, 'FictionalService'), record_id='01p000000000001AAA')
B = Component(BINDING, ComponentKey('demo', 'ApexClass', None, 'FictionalHelper'), record_id='01p000000000002AAA')
C = Component(BINDING, ComponentKey('demo', 'ApexClass', None, 'FictionalOther'), record_id='01p000000000003AAA')
INDEX = component_index((A, B, C), BINDING, SELECTION)
PATHS = {A.key: 'Classes/Service.md', B.key: 'Classes/Helper.md', C.key: 'Classes/Other.md'}


def endpoint(component):
    """Resolve an exact fictional inventory descriptor."""
    return resolve_endpoint('ApexClass', component.key.namespace, component.key.full_name, component.record_id, INDEX)


def edge(source=A, target=B, coverage=COMPLETE, method='synthetic-platform'):
    """Build directed synthetic evidence without reading code or querying a service."""
    return Edge(endpoint(source), endpoint(target), (Evidence(method, coverage),))


def graph(edges=(), coverage=COMPLETE, **kwargs):
    """Construct a synthetic bound snapshot, never a platform completeness assertion."""
    return DependencyGraph(kwargs.get('binding', BINDING), kwargs.get('selection', SELECTION), coverage, tuple(edges))


def test_outgoing_incoming_and_both_endpoint_invalidation():
    """A -> B changes both incident views, leaving all component source hashes unchanged."""
    source_hash = component_fingerprint((A, B, C))
    before, after = graph(), graph((edge(),))
    assert after.references(A.key) == after.referenced_by(B.key) == after.edges
    assert after.references(B.key) == after.referenced_by(A.key) == ()
    assert before.note_fingerprint(A.key, PATHS) != after.note_fingerprint(A.key, PATHS)
    assert before.note_fingerprint(B.key, PATHS) != after.note_fingerprint(B.key, PATHS)
    assert before.note_fingerprint(C.key, PATHS) == after.note_fingerprint(C.key, PATHS)
    assert component_fingerprint((A, B, C)) == source_hash
    removed = refresh_graph(graph(), after)
    assert removed.edges == ()
    assert removed.note_fingerprint(B.key, PATHS) == before.note_fingerprint(B.key, PATHS)


def test_batch_graph_paths_validate_once_and_preserve_incident_hashes(monkeypatch):
    from obforce.graph import dependencies

    snapshot = graph((edge(), edge(B, C), edge(C, A)))
    expected = {key: snapshot.note_fingerprint(key, PATHS) for key in PATHS}
    source = dict(PATHS)
    prepared = dependencies._FingerprintPaths(source, BINDING.workspace_id)
    calls = []
    original = dependencies._checked_locations

    def checked(paths, workspace):
        calls.append(dict(paths))
        return original(paths, workspace)

    monkeypatch.setattr(dependencies, '_checked_locations', checked)
    assert {key: snapshot.note_fingerprint(key, prepared) for key in PATHS} == expected
    assert len(calls) == 1
    source[B.key] = 'Moved/Helper.md'
    assert snapshot.note_fingerprint(A.key, prepared) == expected[A.key]
    assert snapshot.note_fingerprint(A.key, dependencies._FingerprintPaths(source, BINDING.workspace_id)) != expected[A.key]
    assert len(calls) == 2
    with pytest.raises(TypeError):
        prepared.source[A.key] = 'Changed.md'


def test_batch_graph_paths_keep_unrelated_invalid_locations_and_workspace_guards():
    from obforce.graph.dependencies import _FingerprintPaths

    snapshot = graph((edge(),))
    invalid = dict(PATHS)
    invalid[C.key] = PATHS[A.key].swapcase()
    prepared = _FingerprintPaths(invalid, BINDING.workspace_id)
    for mapping in (invalid, prepared, prepared):
        with pytest.raises(ConflictError, match='Duplicate portable'):
            snapshot.note_fingerprint(A.key, mapping)
    with pytest.raises(ConflictError, match='another workspace'):
        snapshot.note_fingerprint(replace(A.key, workspace_id='other'), prepared)
    # A snapshot made for another workspace cannot reuse its checked result.
    source = {replace(A.key, workspace_id='other'): PATHS[A.key]}
    with pytest.raises(ConflictError, match='another workspace'):
        snapshot.note_fingerprint(A.key, _FingerprintPaths(source, 'other'))


def test_duplicate_reordered_self_and_cycle_evidence():
    """Deduplication and cycles never depend on traversal order or recurse through paths."""
    rows = (edge(), edge(B, A), edge(A, A), edge(method='synthetic-other'), edge())
    first, second = graph(rows), graph(reversed(rows))
    assert len(first.edges) == 3
    assert len(first.references(A.key)) == 2 and len(first.referenced_by(A.key)) == 2
    assert sum(len(item.evidence) for item in first.edges) == 4
    assert first == second
    for key in PATHS:
        assert first.note_fingerprint(key, PATHS) == second.note_fingerprint(key, dict(reversed(tuple(PATHS.items()))))


def test_moving_target_or_source_path_invalidates_neighbors_only():
    """Note moves affect incident graph hashes without mutating facts or resolving unknown paths."""
    snapshot = graph((edge(),))
    moved = {**PATHS, B.key: 'Moved/Helper.md'}
    for key in (A.key, B.key):
        assert snapshot.note_fingerprint(key, PATHS) != snapshot.note_fingerprint(key, moved)
    assert snapshot.note_fingerprint(C.key, PATHS) == snapshot.note_fingerprint(C.key, moved)
    assert snapshot.note_fingerprint(A.key, PATHS) == snapshot.note_fingerprint(A.key, {**PATHS, C.key: 'Moved/Other.md'})
    assert A.source_hash == replace(A).source_hash


@pytest.mark.parametrize('coverage', [PARTIAL, UNAVAILABLE, CollectionCoverage(CoverageStatus.NOT_COLLECTED, 'not-collected')])
def test_incomplete_empty_refresh_retains_stale_prior(coverage):
    """Failed/unavailable/truncated/uncollected refreshes cannot establish authoritative emptiness."""
    prior = graph((edge(), edge(B, A)))
    current = refresh_graph(graph(coverage=coverage), prior)
    assert len(current.edges) == 2 and all(item.stale for item in current.edges)
    assert all(item.evidence[0].coverage == COMPLETE for item in current.edges)
    assert all(item.evidence[0].method == 'synthetic-platform' for item in current.edges)
    assert current.coverage == coverage
    assert current.note_fingerprint(A.key, PATHS) != prior.note_fingerprint(A.key, PATHS)
    assert refresh_graph(graph(coverage=coverage), current) == current


def test_reaffirmation_and_contradictory_coverage_are_retained():
    """An exact current observation reaffirms old evidence; changed evidence coexists stale."""
    prior = graph((edge(), edge(B, A)))
    reaffirmed = refresh_graph(graph((edge(),), PARTIAL), prior)
    assert not reaffirmed.references(A.key)[0].stale
    assert reaffirmed.references(B.key)[0].stale
    contradicted = refresh_graph(graph((edge(coverage=PARTIAL),), PARTIAL), graph((edge(),)))
    assert len(contradicted.edges) == 1 and len(contradicted.edges[0].evidence) == 2
    assert {item.stale for item in contradicted.edges[0].evidence} == {True, False}
    assert refresh_graph(graph(), contradicted).edges == ()  # Complete synthetic empty snapshot only.


@pytest.mark.parametrize(
    'binding,selection',
    [
        (SourceBinding('other', 'live', BINDING.org_id), SELECTION),
        (SourceBinding('demo', 'live', '00D000000000002EAA'), SELECTION),
        (SourceBinding('demo', 'local'), SELECTION),
        (BINDING, Selection(True)),
        (BINDING, Selection(full_names=('FictionalService',))),
    ],
)
def test_previous_scope_or_binding_is_never_adopted(binding, selection):
    """Even a complete replacement cannot silently rebind or change prior scope."""
    with pytest.raises(ConflictError):
        refresh_graph(graph(binding=binding, selection=selection), graph((edge(),)))


def test_namespaces_case_and_all_descriptors_must_match():
    """Resolve identical names separately by namespace, never by name or ID alone."""
    namespaced = replace(A, key=replace(A.key, namespace='demoPkg'), record_id='01p000000000004AAA')
    index = component_index((A, namespaced), BINDING, Selection(True))
    assert resolve_endpoint('ApexClass', 'demoPkg', A.key.full_name, namespaced.record_id, index).key == namespaced.key
    for namespace, name, record_id, resolution in [
        ('demopkg', A.key.full_name, namespaced.record_id, 'identity_mismatch'),
        (None, A.key.full_name.lower(), A.record_id, 'identity_mismatch'),
        (None, A.key.full_name, None, 'unresolved'),
        (None, A.key.full_name, C.record_id, 'external'),
    ]:
        result = resolve_endpoint('ApexClass', namespace, name, record_id, index)
        assert result.key is None and result.resolution == resolution
    with pytest.raises(ConflictError):
        component_index((namespaced,), BINDING, SELECTION)


def test_unsupported_external_and_unresolved_referencing_endpoints():
    """Incoming unsupported sources remain labeled and directed rather than invented Apex keys."""
    unsupported = resolve_endpoint('Flow', None, 'FictionalFlow', 'fictional-flow-id', INDEX)
    unknown = resolve_endpoint(None, None, None, None, INDEX)
    external = resolve_endpoint('ApexClass', 'externalPkg', 'ExternalService', '01p000000000004AAA', INDEX)
    rows = [Edge(item, endpoint(B), (Evidence('synthetic-platform', PARTIAL),)) for item in (unsupported, unknown, external)]
    snapshot = graph(rows, PARTIAL)
    assert len(snapshot.referenced_by(B.key)) == 3 and snapshot.references(A.key) == ()
    assert {item.source.resolution for item in snapshot.edges} == {'unsupported', 'unresolved', 'external'}
    assert snapshot.note_fingerprint(B.key, PATHS) != graph(coverage=PARTIAL).note_fingerprint(B.key, PATHS)
    assert 'FictionalFlow' not in repr(snapshot) and 'ExternalService' not in repr(rows)


@pytest.mark.parametrize('path', ['../escape.md', '.obsidian/config.md', '/absolute.md', 'CON.md'])
def test_unsafe_paths_are_refused(path):
    """Explicit locations use the frozen portable path validator without filesystem access."""
    with pytest.raises(ConfigError):
        graph((edge(),)).note_fingerprint(A.key, {A.key: path})


def test_portable_path_and_workspace_collision():
    """Supplied paths confer no adoption and cannot create ambiguous managed links."""
    with pytest.raises(ConflictError):
        graph().note_fingerprint(A.key, {A.key: 'Classes/A.md', B.key: 'classes/a.MD'})
    with pytest.raises(ConflictError):
        graph().note_fingerprint(replace(A.key, workspace_id='other'), {})
    with pytest.raises(ConflictError):
        graph().note_fingerprint(A.key, {replace(A.key, workspace_id='other'): 'Other.md'})


@pytest.mark.parametrize('value', ['', ' bad ', '\x00private', 10, ['private'], 'x' * 513])
def test_endpoint_validation_redacts_invalid_values(value):
    """Malformed descriptors never become raw API data in exceptions."""
    with pytest.raises(ModelError) as error:
        Endpoint('ApexClass', None, value, None)
    assert 'private' not in str(error.value)


def test_graph_bounds_and_incompatible_endpoint_keys(monkeypatch):
    """Private snapshots and malformed component maps still receive typed refusals."""
    monkeypatch.setattr(const, 'MAX_GRAPH_EDGES', 1)
    with pytest.raises(ModelError):
        graph((edge(), edge(B, A)))
    with pytest.raises(ConflictError):
        graph((edge(),), binding=SourceBinding('other', 'live', BINDING.org_id))
    with pytest.raises(ConflictError):
        component_index((A, A), BINDING, SELECTION)
    with pytest.raises(ModelError):
        component_index((replace(A, record_id=None),), BINDING, SELECTION)


def test_observation_bound_refuses_without_discarding_previous(monkeypatch):
    """A bounded merge fails safely instead of pruning stale evidence to fit memory."""
    prior = graph((edge(),))
    current = graph((edge(B, A, PARTIAL),), PARTIAL)
    monkeypatch.setattr(const, 'MAX_GRAPH_OBSERVATIONS', 1)
    with pytest.raises(ModelError):
        refresh_graph(current, prior)
    assert prior.edges == (edge(),)
