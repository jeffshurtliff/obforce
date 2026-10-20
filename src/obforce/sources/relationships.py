# -*- coding: utf-8 -*-
"""
:Module:            obforce.sources.relationships
:Synopsis:          Collects bounded best-effort platform relationships without exhaustion claims
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     19 Oct 2026
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

from obforce import constants as const
from obforce.errors import ConfigError, ConflictError, CoverageError, ModelError, OperationalError
from obforce.graph.dependencies import DependencyGraph, Edge, Endpoint, Evidence, component_index, refresh_graph, resolve_endpoint
from obforce.models import CollectionCoverage, Component, Coverage, CoverageStatus, SourceBinding, require_same_source
from obforce.sources import live

_SUFFIXES = ('Id', 'Name', 'Namespace', 'Type')
_PREFIXES = ('MetadataComponent', 'RefMetadataComponent')
_FIELDS = tuple(prefix + suffix for prefix in _PREFIXES for suffix in _SUFFIXES)
_PROJECTION = ', '.join(_FIELDS)


@dataclass(frozen=True)
class RelationshipCollection:
    """Return private graph evidence and independent source coverage without publication."""

    graph: DependencyGraph = field(repr=False)
    coverage: Coverage = field(repr=False)
    evidence: tuple[live.PageEvidence, ...] = ()


def _endpoint(record: dict[str, Any], prefix: str, index: dict[str, Component]) -> Endpoint:
    """Validate the fixed endpoint projection; resolve no name-only or cross-namespace guesses."""
    metadata_type, namespace, name, record_id = (record[prefix + suffix] for suffix in ('Type', 'Namespace', 'Name', 'Id'))
    # Validate all nullable descriptor types before any identity normalization.
    Endpoint(metadata_type, None if namespace == '' else namespace, name, record_id)
    namespace = None if namespace == '' else namespace
    if metadata_type == 'ApexClass' and record_id is not None:
        record_id = live._id(record_id, '01p')
    return resolve_endpoint(metadata_type, namespace, name, record_id, index)


def _edge(record: dict[str, Any], index: dict[str, Component], evidence: Evidence) -> Edge:
    """Refuse extra business/source fields instead of silently retaining raw records."""
    if not set(_FIELDS) <= record.keys() or record.keys() - {*_FIELDS, 'attributes'}:
        raise ModelError('Unsupported or missing relationship fields.')
    return Edge(_endpoint(record, _PREFIXES[0], index), _endpoint(record, _PREFIXES[1], index), (evidence,))


def collect_relationships(
    executable: Path,
    *,
    directory: Path,
    target: str,
    inventory: live.LiveInventory,
    previous: DependencyGraph | None = None,
) -> RelationshipCollection:
    """Probe selected live Apex IDs in both directions through the accepted CLI boundary.

    This internal entry point grants no live authorization. It rechecks actual org
    identity against the supplied inventory, never loads state, and never follows
    an endpoint. MCD's unsupported exhaustion operations mean even clean empty
    probes remain partial. Offline acquisition never calls this adapter.

    :param executable: Explicit absolute trusted executable, never discovered.
    :param directory: Explicit existing neutral CLI working directory.
    :param target: Explicit selector; org identity must match inventory.
    :param inventory: Previously normalized live facts and independent coverage.
    :param previous: Validated in-memory matching-source/scope evidence, if any.
    :returns: Graph with safe count/continuation/warning observations and coverage.
    :raises ConflictError: For incompatible source/scope or unselected probe results.
    :raises ModelError: For malformed reported metadata or noncanonical inventory IDs.
    :raises OperationalError: If required identity verification fails operationally.
    :raises CoverageError: If actual org identity cannot be established.
    """
    if not isinstance(inventory, live.LiveInventory) or not isinstance(inventory.coverage, Coverage):
        raise ConfigError('Expected normalized live inventory for relationship collection.')
    source = inventory.coverage
    if source.binding.mode != 'live':
        raise ConflictError('Platform relationships require an existing live source binding.')
    if live._id(source.binding.org_id, '00D') != source.binding.org_id:
        raise ModelError('Relationship source requires canonical verified org identity.')
    index = component_index(inventory.components, source.binding, source.selection)
    if any(live._id(record_id, '01p') != record_id for record_id in index):
        raise ModelError('Relationship inventory requires canonical Salesforce IDs.')
    # Refuse incompatible prior evidence before any process call, then recheck actual identity.
    initial = CollectionCoverage(CoverageStatus.UNAVAILABLE, const.RELATIONSHIP_METHOD)
    refresh_graph(DependencyGraph(source.binding, source.selection, initial), previous)
    session = live._Session(
        executable,
        directory,
        target,
        max_queries=const.MAX_RELATIONSHIP_QUERIES,
        timeout=const.RELATIONSHIP_TIMEOUT_SECONDS,
        stdout=const.MAX_RELATIONSHIP_STDOUT_BYTES,
    )
    identity, problems = session.query(live._IDENTITY_QUERY, 'identity')
    if problems or len(identity) != 1:
        raise CoverageError('Actual relationship org identity could not be established.')
    if identity[0].keys() - {'Id', 'attributes'}:
        raise ModelError('Unsupported relationship org identity fields.')
    actual = SourceBinding(source.binding.workspace_id, 'live', live._id(identity[0].get('Id'), '00D'))
    require_same_source(source.binding, actual)
    edges: list[Edge] = []
    warnings = {'exhaustion_unverifiable', 'supported_type_coverage_unverified'}
    if source.inventory.status is not CoverageStatus.COMPLETE:
        warnings.add('inventory_not_exhausted')
    limited, usable, returned, stop = False, 0, 0, False
    for record_id in sorted(index):
        for prefix in _PREFIXES:
            phase = 'relationships_outgoing' if prefix == _PREFIXES[0] else 'relationships_incoming'
            # Only fixed fields and checksum-validated alphanumeric 18-character Apex IDs.
            query = (
                f'SELECT {_PROJECTION} FROM MetadataComponentDependency '  # nosec B608
                f"WHERE {prefix}Id = '{record_id}' AND {prefix}Type = 'ApexClass'"
            )
            try:
                records, problems = session.query(query, phase)
            except CoverageError:
                warnings.add('collection_budget_exhausted')
                limited, stop = True, True
                break
            except OperationalError as error:
                if type(error) is not OperationalError:
                    raise
                # Boundary redaction prevents distinguishing permission/type/auth/timeout failures.
                warnings.add(phase + ':query_unavailable')
                continue
            probe_warnings = set(problems) | {'exhaustion_unverifiable'}
            if len(records) >= const.MAX_RELATIONSHIP_PAGE_RECORDS:
                probe_warnings.add('documented_query_cap_reached')
                limited = True
            warnings.update(phase + ':' + problem for problem in probe_warnings if problem != 'exhaustion_unverifiable')
            returned += len(records)
            if returned > const.MAX_RELATIONSHIP_RECORDS:
                warnings.add('record_budget_exhausted')
                limited, stop = True, True
                break
            coverage = CollectionCoverage(
                CoverageStatus.PARTIAL,
                const.RELATIONSHIP_METHOD,
                pagination='incomplete',
                limit_reached=True if len(records) >= const.MAX_RELATIONSHIP_PAGE_RECORDS else None,
                warnings=tuple(sorted(probe_warnings)),
            )
            observation = Evidence(const.RELATIONSHIP_METHOD + (':outgoing' if prefix == _PREFIXES[0] else ':incoming'), coverage)
            for record in records:
                edge = _edge(record, index, observation)
                anchor = edge.source if prefix == _PREFIXES[0] else edge.target
                if anchor.record_id != record_id or anchor.metadata_type != 'ApexClass':
                    raise ConflictError('Relationship query returned an endpoint outside its selected ID/type filter.')
                if anchor.key is None:
                    warnings.add('anchor_identity_contradiction')
                if 'identity_mismatch' in (edge.source.resolution, edge.target.resolution):
                    warnings.add('endpoint_identity_contradiction')
                edges.append(edge)
            # A clean empty probe is usable evidence of a reply, never proof of exhaustion.
            usable += 1
        if stop:
            break
    if not index:
        warnings.add('no_selected_endpoints')
    coverage = CollectionCoverage(
        CoverageStatus.PARTIAL if usable else CoverageStatus.UNAVAILABLE,
        const.RELATIONSHIP_METHOD,
        pagination='incomplete' if usable else 'unknown',
        limit_reached=True if limited else None,
        warnings=tuple(sorted(warnings)),
    )
    graph = refresh_graph(DependencyGraph(actual, source.selection, coverage, tuple(edges)), previous)
    return RelationshipCollection(graph, replace(source, relationships=coverage), tuple(session.evidence))
