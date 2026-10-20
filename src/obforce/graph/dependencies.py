# -*- coding: utf-8 -*-
"""
:Module:            obforce.graph.dependencies
:Synopsis:          Normalizes private directed evidence and reciprocal graph invalidation
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     19 Oct 2026
"""

from __future__ import annotations

import unicodedata
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field, replace
from typing import Any

from obforce import constants as const
from obforce.config import relative_path
from obforce.errors import ConflictError, ModelError
from obforce.models import (
    CollectionCoverage,
    Component,
    ComponentKey,
    CoverageStatus,
    Relationship,
    Selection,
    SourceBinding,
    canonical_json,
    fingerprint,
    graph_fingerprint,
    require_same_source,
    validate_identities,
)


def _label(value: object, limit: int) -> None:
    """Validate bounded private descriptor text without echoing input."""
    if value is not None and (
        not isinstance(value, str)
        or not 0 < len(value) <= limit
        or value != value.strip()
        or any(unicodedata.category(char) in {'Cc', 'Cs'} for char in value)
    ):
        raise ModelError('Invalid relationship endpoint descriptor.')


@dataclass(frozen=True, repr=False)
class Endpoint:
    """Keep reported type/namespace/name/ID even when no supported identity resolves.

    All descriptors and canonical payloads are private metadata. Resolution grants
    neither note ownership nor permission to create a note or emit a link.
    """

    metadata_type: str | None
    namespace: str | None
    name: str | None
    record_id: str | None
    key: ComponentKey | None = None
    resolution: str = 'unresolved'

    def __post_init__(self) -> None:
        """Require explicit resolution and consistent supported identity descriptors."""
        for value in (self.metadata_type, self.namespace, self.name, self.record_id):
            _label(value, const.MAX_RELATIONSHIP_LABEL_CHARS)
        if self.resolution not in {'resolved', 'unresolved', 'unsupported', 'external', 'identity_mismatch'}:
            raise ModelError('Invalid relationship resolution.')
        if (self.key is not None) != (self.resolution == 'resolved'):
            raise ModelError('Relationship resolution requires a matching supported key.')
        if self.key is not None and (
            not isinstance(self.key, ComponentKey)
            or self.metadata_type != 'ApexClass'
            or self.key.namespace != self.namespace
            or self.key.full_name != self.name
            or self.record_id is None
        ):
            raise ModelError('Relationship key contradicts reported descriptors.')

    def __repr__(self) -> str:
        """Expose only the safe resolution category, never endpoint metadata."""
        return f'Endpoint(resolution={self.resolution!r})'

    def canonical(self) -> dict[str, Any]:
        """Return private semantic evidence; never log or render this payload directly."""
        return {
            'type': self.metadata_type,
            'namespace': self.namespace,
            'name': self.name,
            'record_id': self.record_id,
            'key': None if self.key is None else self.key.canonical(),
            'resolution': self.resolution,
        }


def resolve_endpoint(
    metadata_type: str | None,
    namespace: str | None,
    name: str | None,
    record_id: str | None,
    components: Mapping[str, Component],
) -> Endpoint:
    """Resolve only an exact supported ID/type/namespace/name inventory match.

    :param components: Already validated canonical live record-ID mapping.
    :returns: Private descriptor with an explicit unresolved/external/type label.
    """
    candidate = Endpoint(metadata_type, namespace, name, record_id)
    status, key = 'unresolved', None
    if metadata_type is not None and metadata_type != 'ApexClass':
        status = 'unsupported'
    elif metadata_type == 'ApexClass' and record_id is not None and name is not None:
        component = components.get(record_id)
        if component is None:
            status = 'external'
        elif (component.key.namespace, component.key.full_name) == (namespace, name):
            status, key = 'resolved', component.key
        else:
            status = 'identity_mismatch'
    return replace(candidate, resolution=status, key=key)


@dataclass(frozen=True)
class Evidence:
    """Retain method/coverage contradictions and freshness without raw diagnostics."""

    method: str
    coverage: CollectionCoverage
    stale: bool = False

    def __post_init__(self) -> None:
        """Reject malformed evidence without coercing unavailable coverage."""
        _label(self.method, const.MAX_RELATIONSHIP_LABEL_CHARS)
        if self.method is None or not isinstance(self.coverage, CollectionCoverage) or type(self.stale) is not bool:
            raise ModelError('Invalid relationship evidence.')

    def canonical(self) -> dict[str, Any]:
        """Preserve original coverage even when later marked stale."""
        return {'method': self.method, 'coverage': self.coverage.canonical(), 'stale': self.stale}


@dataclass(frozen=True)
class Edge:
    """Represent referencing source -> referenced target, including unsupported sources."""

    source: Endpoint = field(repr=False)
    target: Endpoint = field(repr=False)
    evidence: tuple[Evidence, ...]

    def __post_init__(self) -> None:
        """Normalize repeated/reordered observations without losing contradictions."""
        if not isinstance(self.source, Endpoint) or not isinstance(self.target, Endpoint):
            raise ModelError('Invalid directed graph endpoints.')
        if not self.evidence or not all(isinstance(item, Evidence) for item in self.evidence):
            raise ModelError('An edge requires reported evidence.')
        unique = {canonical_json(item.canonical()): item for item in self.evidence}
        object.__setattr__(self, 'evidence', tuple(unique[token] for token in sorted(unique)))

    @property
    def stale(self) -> bool:
        """Distinguish entirely stale edges from edges with a current observation."""
        return all(item.stale for item in self.evidence)

    @property
    def token(self) -> str:
        """Identify this directed endpoint pair independently of observation order."""
        return canonical_json([self.source.canonical(), self.target.canonical()])

    def canonical(self) -> dict[str, Any]:
        """Return private directed facts plus all distinct provenance/coverage evidence."""
        return {
            'source': self.source.canonical(),
            'target': self.target.canonical(),
            'evidence': [item.canonical() for item in self.evidence],
        }


@dataclass(frozen=True)
class DependencyGraph:
    """Hold a bound in-memory snapshot; no state loading, path discovery or publication."""

    binding: SourceBinding = field(repr=False)
    selection: Selection = field(repr=False)
    coverage: CollectionCoverage
    edges: tuple[Edge, ...] = field(default=(), repr=False)

    def __post_init__(self) -> None:
        """Validate binding/scope and normalize duplicate directed pairs deterministically."""
        if not isinstance(self.binding, SourceBinding) or not isinstance(self.selection, Selection):
            raise ModelError('Invalid graph binding or selection.')
        if not isinstance(self.coverage, CollectionCoverage):
            raise ModelError('Invalid graph coverage.')
        groups: dict[str, Edge] = {}
        observations = 0
        for edge in self.edges:
            if not isinstance(edge, Edge):
                raise ModelError('Invalid graph edge.')
            observations += len(edge.evidence)
            if observations > const.MAX_GRAPH_OBSERVATIONS:
                raise ModelError('Graph evidence exceeds the in-memory observation bound.')
            for endpoint in (edge.source, edge.target):
                if endpoint.key is not None:
                    if endpoint.key.workspace_id != self.binding.workspace_id:
                        raise ConflictError('Graph endpoint belongs to another workspace.')
                    if (endpoint.key.namespace is not None and not self.selection.include_namespaced) or (
                        self.selection.full_names and endpoint.key.full_name not in self.selection.full_names
                    ):
                        raise ConflictError('Resolved graph endpoint is outside selected scope.')
            if edge.token in groups:
                edge = replace(edge, evidence=(*groups[edge.token].evidence, *edge.evidence))
            groups[edge.token] = edge
            if len(groups) > const.MAX_GRAPH_EDGES:
                raise ModelError('Graph evidence exceeds the in-memory edge bound.')
        object.__setattr__(self, 'edges', tuple(groups[token] for token in sorted(groups)))

    def references(self, key: ComponentKey) -> tuple[Edge, ...]:
        """Derive outgoing References from the same directed evidence as incoming views."""
        return tuple(edge for edge in self.edges if edge.source.key == key)

    def referenced_by(self, key: ComponentKey) -> tuple[Edge, ...]:
        """Derive incoming Referenced By, retaining unsupported referencing endpoints."""
        return tuple(edge for edge in self.edges if edge.target.key == key)

    def note_fingerprint(self, key: ComponentKey, paths: Mapping[ComponentKey, str]) -> str:
        """Hash incident edges, coverage and explicit managed-note locations.

        :param key: Supported identity whose candidate may need invalidation.
        :param paths: Supplied managed-note locations; no filesystem inspection/adoption.
        :returns: Deterministic graph hash, separate from component source hashes.
        :raises ConflictError: For incompatible identities or portable path collisions.
        """
        if not isinstance(key, ComponentKey) or key.workspace_id != self.binding.workspace_id:
            raise ConflictError('Graph fingerprint identity belongs to another workspace.')
        checked: dict[ComponentKey, str] = {}
        portable: set[str] = set()
        for endpoint, path in paths.items():
            if not isinstance(endpoint, ComponentKey) or endpoint.workspace_id != self.binding.workspace_id:
                raise ConflictError('Managed graph location belongs to another workspace.')
            normalized = relative_path(path)
            location = unicodedata.normalize('NFC', normalized).casefold()
            if location in portable:
                raise ConflictError('Duplicate portable managed graph location.')
            portable.add(location)
            checked[endpoint] = normalized
        incident = tuple(edge for edge in self.edges if key in (edge.source.key, edge.target.key))
        relevant = {key} | {
            endpoint.key for edge in incident for endpoint in (edge.source, edge.target) if endpoint.key is not None
        }
        locations = {endpoint: path for endpoint, path in checked.items() if endpoint in relevant}
        # Keep the frozen Relationship and graph_fingerprint contracts unchanged.
        projected = []
        for edge in incident:
            if edge.source.key is not None:
                for item in edge.evidence:
                    projected.append(
                        Relationship(
                            edge.source.key,
                            edge.target.key,
                            'platform_reference',
                            item.method,
                            item.coverage,
                            None if edge.target.key is not None else canonical_json(edge.target.canonical()),
                            item.stale,
                        )
                    )
        # Endpoint descriptor contradictions may project to identical legacy records.
        unique = {canonical_json(item.canonical()): item for item in projected}
        return fingerprint(
            {
                'model_schema': const.MODEL_SCHEMA_VERSION,
                'scope': self.selection.scope_hash(self.binding),
                'coverage': self.coverage.canonical(),
                'legacy_graph': graph_fingerprint(unique.values(), locations),
                'reported_edges': [edge.canonical() for edge in incident],
            }
        )


def refresh_graph(current: DependencyGraph, previous: DependencyGraph | None = None) -> DependencyGraph:
    """Preserve matching-scope prior evidence stale unless a complete refresh replaces it.

    Fresh exact observations reaffirm matching prior evidence. Distinct prior
    coverage/descriptor/method evidence is retained stale, never silently erased.
    Complete synthetic snapshots can replace edges; the platform adapter cannot
    establish such completeness under its fixed transport contract.
    """
    if previous is None:
        return current
    if not isinstance(previous, DependencyGraph):
        raise ModelError('Expected a validated prior graph snapshot.')
    require_same_source(previous.binding, current.binding)
    if previous.selection != current.selection:
        raise ConflictError('Prior relationship scope does not match the requested scope.')
    if current.coverage.status is CoverageStatus.COMPLETE:
        return current
    fresh = {edge.token: edge for edge in current.edges}
    retained = list(current.edges)
    for edge in previous.edges:
        reaffirmed = {canonical_json(replace(item, stale=False).canonical()) for item in fresh.get(edge.token, edge).evidence}
        if edge.token not in fresh:
            reaffirmed = set()
        evidence = tuple(
            replace(item, stale=True)
            for item in edge.evidence
            if canonical_json(replace(item, stale=False).canonical()) not in reaffirmed
        )
        if evidence:
            retained.append(replace(edge, evidence=evidence))
    return replace(current, edges=tuple(retained))


def component_index(components: Iterable[Component], binding: SourceBinding, selection: Selection) -> dict[str, Component]:
    """Validate a supplied selected live inventory before using its ID mappings."""
    items = tuple(components)
    if len(items) > const.MAX_LIVE_RECORDS:
        raise ModelError('Relationship inventory exceeds the supported component bound.')
    validate_identities(items)
    result = {}
    for component in items:
        require_same_source(binding, component.binding)
        if component.record_id is None:
            raise ModelError('Live relationship resolution requires canonical record IDs.')
        if (component.key.namespace is not None and not selection.include_namespaced) or (
            selection.full_names and component.key.full_name not in selection.full_names
        ):
            raise ConflictError('Relationship inventory lies outside selected scope.')
        result[component.record_id] = component
    return result
