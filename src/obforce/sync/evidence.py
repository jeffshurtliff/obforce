# -*- coding: utf-8 -*-
"""
:Module:            obforce.sync.evidence
:Synopsis:          Validates bounded private normalized refresh evidence
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     28 Oct 2026
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from obforce import constants as const
from obforce.errors import ConflictError
from obforce.graph.dependencies import DependencyGraph, Edge, Endpoint, Evidence, _FingerprintPaths
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
    canonical_json,
    require_same_source,
    validate_identities,
)
from obforce.renderer.notes import _bounded
from obforce.sources.live import _id

if TYPE_CHECKING:
    from obforce.sync.state import SavedNote


def _object(value: object, keys: set[str]) -> dict:
    if type(value) is not dict or value.keys() != keys:
        raise ConflictError('Invalid private evidence structure')
    return value


def _key(value: object) -> ComponentKey:
    if type(value) is not list or len(value) != 4 or value[2] == '':
        raise ConflictError('Invalid evidence key')
    return ComponentKey(*value)


def _facet(value: object) -> CollectionCoverage:
    data = dict(_object(value, {'status', 'method', 'requested', 'pagination', 'limit_reached', 'api_version', 'warnings'}))
    if type(data['warnings']) is not list:
        raise ConflictError('Invalid evidence coverage')
    data['status'], data['warnings'] = CoverageStatus(data['status']), tuple(data['warnings'])
    return CollectionCoverage(**data)


@dataclass(frozen=True, repr=False)
class InventoryScope:
    """Bind a declared access scope without claiming automatic permission verification."""

    scope_id: str
    method: str
    api_version: str | None

    def __post_init__(self) -> None:
        if type(self.scope_id) is not str or re.fullmatch(r'[A-Za-z0-9_-]{1,128}', self.scope_id) is None:
            raise ConflictError('Invalid inventory scope declaration')
        if self.method != const.LIVE_APEX_METHOD or (
            self.api_version is not None and (type(self.api_version) is not str or not 1 <= len(self.api_version) <= 512)
        ):
            raise ConflictError('Invalid inventory scope method or version')

    def canonical(self) -> dict:
        """Return stable scope metadata, never a durable attestation flag."""
        return {'scope_id': self.scope_id, 'method': self.method, 'api_version': self.api_version}


@dataclass(frozen=True, repr=False)
class RefreshEvidence:
    """Retain exact semantic facts and graph used by one accepted state generation."""

    components: tuple[Component, ...]
    graph: DependencyGraph
    inventory_scope: InventoryScope | None = None

    def __post_init__(self) -> None:
        if type(self.components) is not tuple or len(self.components) > const.MAX_PLAN_COMPONENTS:
            raise ConflictError('Invalid retained component collection')
        if not isinstance(self.graph, DependencyGraph) or (
            self.inventory_scope is not None and not isinstance(self.inventory_scope, InventoryScope)
        ):
            raise ConflictError('Invalid refresh evidence records')
        validate_identities(self.components)
        for component in self.components:
            if not isinstance(component, Component):
                raise ConflictError('Invalid retained component')
            _bounded(component.canonical())
            if component.record_id is not None and _id(component.record_id, '01p') != component.record_id:
                raise ConflictError('Noncanonical retained record identity')
        object.__setattr__(self, 'components', tuple(sorted(self.components, key=lambda c: c.key.token)))
        if len(canonical_json(self.canonical()).encode('utf-8')) > const.MAX_EVIDENCE_BYTES:
            raise ConflictError('Private evidence exceeds size bound')

    def canonical(self) -> dict:
        """Serialize only normalized semantic evidence, without incidental timestamps."""
        return {
            'evidence_schema': const.EVIDENCE_SCHEMA_VERSION,
            'components': [c.canonical() for c in self.components],
            'graph': {'coverage': self.graph.coverage.canonical(), 'edges': [e.canonical() for e in self.graph.edges]},
            'inventory_scope': None if self.inventory_scope is None else self.inventory_scope.canonical(),
        }

    def validate(self, coverage: Coverage, notes: tuple[SavedNote, ...], *, paths: bool = True) -> None:
        """Require exact source/graph association with saved ownership baselines."""
        require_same_source(coverage.binding, self.graph.binding)
        if self.graph.selection != coverage.selection or self.graph.coverage != coverage.relationships:
            raise ConflictError('Saved graph scope or coverage differs')
        if coverage.binding.mode == 'local' and (self.graph.edges or self.inventory_scope is not None):
            raise ConflictError('Offline evidence cannot assert live observations')
        if (
            coverage.binding.mode == 'live'
            and self.graph.coverage.requested
            and self.graph.coverage.status not in {CoverageStatus.PARTIAL, CoverageStatus.UNAVAILABLE}
        ):
            raise ConflictError('Platform graph cannot prove exhaustion')
        if self.inventory_scope is not None and (
            self.inventory_scope.method != coverage.inventory.method
            or self.inventory_scope.api_version != coverage.inventory.api_version
        ):
            raise ConflictError('Inventory scope reference changed')
        saved = {s.note.key: s.note for s in notes}
        if {c.key for c in self.components} != saved.keys():
            raise ConflictError('Retained facts do not match tracked notes')
        locations = {key: note.path for key, note in saved.items()}
        # Fresh for each independent evidence-validation pass, never retained
        # from rendering, planning, publication or an earlier state read.
        graph_paths = _FingerprintPaths(locations, coverage.binding.workspace_id)
        for component in self.components:
            require_same_source(coverage.binding, component.binding)
            key = component.key
            if (key.namespace is not None and not coverage.selection.include_namespaced) or (
                coverage.selection.full_names and key.full_name not in coverage.selection.full_names
            ):
                raise ConflictError('Retained component lies outside selected scope')
            if component.source_hash != saved[key].source_hash:
                raise ConflictError('Retained facts differ from saved fingerprint')
            if paths and self.graph.note_fingerprint(key, graph_paths) != saved[key].graph_hash:
                raise ConflictError('Retained graph differs from saved fingerprint')


def parse_evidence(value: object, binding: SourceBinding, selection: Selection) -> RefreshEvidence:
    """Deserialize bounded JSON primitives without deduplicating contradictory wire data."""
    data = _object(value, {'evidence_schema', 'components', 'graph', 'inventory_scope'})
    if type(data['evidence_schema']) is not int or data['evidence_schema'] != const.EVIDENCE_SCHEMA_VERSION:
        raise ConflictError('Unsupported private evidence version')
    if type(data['components']) is not list or len(data['components']) > const.MAX_PLAN_COMPONENTS:
        raise ConflictError('Invalid evidence components')
    if len(canonical_json(data).encode('utf-8')) > const.MAX_EVIDENCE_BYTES:
        raise ConflictError('Private evidence exceeds size bound')
    components = []
    for raw in data['components']:
        row = _object(raw, {'model_schema', 'binding', 'key', 'record_id', 'attributes', 'provenance'})
        if type(row['attributes']) is not dict or type(row['provenance']) is not list:
            raise ConflictError('Invalid retained facts')
        fields = {}
        for name, field in row['attributes'].items():
            field = _object(field, {'availability', 'value'})
            payload = tuple(field['value']) if type(field['value']) is list else field['value']
            fields[name] = FieldValue(Availability(field['availability']), payload)
        component = Component(binding, _key(row['key']), fields, row['record_id'], tuple(row['provenance']))
        if canonical_json(component.canonical()) != canonical_json(row):
            raise ConflictError('Noncanonical component evidence')
        components.append(component)
    raw_graph = _object(data['graph'], {'coverage', 'edges'})
    if type(raw_graph['edges']) is not list or len(raw_graph['edges']) > const.MAX_GRAPH_EDGES:
        raise ConflictError('Invalid evidence graph')
    edges, tokens, observations = [], set(), 0
    for raw in raw_graph['edges']:
        row = _object(raw, {'source', 'target', 'evidence'})
        endpoints = []
        for side in ('source', 'target'):
            end = _object(row[side], {'type', 'namespace', 'name', 'record_id', 'key', 'resolution'})
            endpoints.append(
                Endpoint(
                    end['type'],
                    end['namespace'],
                    end['name'],
                    end['record_id'],
                    None if end['key'] is None else _key(end['key']),
                    end['resolution'],
                )
            )
        if type(row['evidence']) is not list:
            raise ConflictError('Invalid relationship observations')
        observations += len(row['evidence'])
        if observations > const.MAX_GRAPH_OBSERVATIONS:
            raise ConflictError('Relationship observations exceed bound')
        evidence = []
        for item in row['evidence']:
            item = _object(item, {'method', 'coverage', 'stale'})
            evidence.append(Evidence(item['method'], _facet(item['coverage']), item['stale']))
        edge = Edge(*endpoints, tuple(evidence))
        if edge.token in tokens or canonical_json(edge.canonical()) != canonical_json(row):
            raise ConflictError('Duplicate or noncanonical graph evidence')
        tokens.add(edge.token)
        edges.append(edge)
    scope = data['inventory_scope']
    if scope is not None:
        scope = InventoryScope(**_object(scope, {'scope_id', 'method', 'api_version'}))
    result = RefreshEvidence(
        tuple(components), DependencyGraph(binding, selection, _facet(raw_graph['coverage']), tuple(edges)), scope
    )
    if canonical_json(result.canonical()) != canonical_json(data):
        raise ConflictError('Noncanonical private evidence')
    return result
