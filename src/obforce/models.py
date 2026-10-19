# -*- coding: utf-8 -*-
"""
:Module:            obforce.models
:Synopsis:          Defines deterministic versioned internal source and note contracts
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     19 Oct 2026
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any
from uuid import UUID

from obforce import constants as const
from obforce.config import Layout, Options, relative_path
from obforce.errors import ConfigError, ConflictError, ExitCode, ModelError


def canonical_json(value: object) -> str:
    """Serialize primitive JSON data without lossy key coercion or nonfinite numbers.

    Arrays retain order. Record constructors explicitly sort unordered collections;
    this serializer never guesses whether an arbitrary array is a set.

    :param value: Null, strings, booleans, integers, string-keyed dicts, and lists/tuples.
    :returns: Compact Unicode-preserving JSON with sorted object keys.
    :raises ModelError: For unsupported values or keys.
    """

    def check(item: object) -> None:
        if type(item) is str:
            try:
                item.encode('utf-8')
            except UnicodeError as error:
                raise ModelError('Canonical text must be valid Unicode') from error
            return
        if item is None or type(item) in (bool, int):
            return
        if type(item) is dict and all(type(key) is str for key in item):
            for key in item:
                check(key)
            for child in item.values():
                check(child)
            return
        if type(item) in (list, tuple):
            for child in item:
                check(child)
            return
        raise ModelError('Canonical data must contain only supported JSON primitives')

    check(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def fingerprint(value: object) -> str:
    """Hash canonical UTF-8 JSON with SHA-256, independent of dictionary order.

    :param value: Explicit semantic payload; callers must omit incidental data.
    :returns: Lowercase hexadecimal digest.
    """
    return hashlib.sha256(canonical_json(value).encode('utf-8')).hexdigest()


def _text(value: object) -> None:
    """Validate identity/provenance text without normalizing case or Unicode."""
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or any(unicodedata.category(char) in {'Cc', 'Cs'} for char in value)
    ):
        raise ModelError('Expected nonempty text without controls or surrounding whitespace')


def _hash(value: object) -> None:
    """Require a SHA-256 digest from untrusted internal inputs."""
    if not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{64}', value):
        raise ModelError('Expected a lowercase SHA-256 digest')


def _path(value: object) -> str:
    """Translate shared portable-path diagnostics into model validation errors."""
    try:
        return relative_path(value)
    except ConfigError as error:
        raise ModelError('Invalid vault-relative record path') from error


def _sorted_text(values: Iterable[str]) -> tuple[str, ...]:
    """Normalize an unordered text collection and reject duplicates."""
    if isinstance(values, (str, bytes)):
        raise ModelError('Expected a collection of text entries, not one string')
    items = tuple(values)
    for item in items:
        _text(item)
    if len(set(items)) != len(items):
        raise ModelError('Duplicate collection entry')
    return tuple(sorted(items))


@dataclass(frozen=True)
class SourceBinding:
    """Bind a workspace to local mode or a separately verified live org identity.

    Constructing this record does not verify an org. Live acquisition must supply
    the verified ID; a configured alias is never passed here as identity.
    """

    workspace_id: str
    mode: str
    org_id: str | None = None

    def __post_init__(self) -> None:
        """Require mode-compatible identity without storing host paths or aliases."""
        if not isinstance(self.workspace_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', self.workspace_id):
            raise ModelError('Invalid workspace identity')
        if self.mode == 'local' and self.org_id is None:
            return
        if self.mode == 'live' and self.org_id is not None:
            _text(self.org_id)
            return
        raise ModelError('Binding requires local mode or a verified live org ID')

    def canonical(self) -> dict[str, Any]:
        """Return the structured binding, independent of source location/alias."""
        return {'workspace_id': self.workspace_id, 'mode': self.mode, 'org_id': self.org_id}


def require_same_source(previous: SourceBinding, current: SourceBinding) -> None:
    """Refuse implicit workspace, source-mode, or verified-org rebinding.

    :raises ConflictError: If either binding changes; no rebinding is implemented.
    """
    if previous != current:
        raise ConflictError('Source binding changed; automatic rebinding is unsupported')


@dataclass(frozen=True)
class ComponentKey:
    """Identify one component independently of filenames, aliases, or record ordering."""

    workspace_id: str
    metadata_type: str
    namespace: str | None
    full_name: str

    def __post_init__(self) -> None:
        """Preserve identity case/Unicode and normalize empty namespace to absent."""
        SourceBinding(self.workspace_id, 'local')
        if self.metadata_type != 'ApexClass':
            raise ModelError('Only ApexClass is supported in model version 1')
        _text(self.full_name)
        if self.namespace == '':
            object.__setattr__(self, 'namespace', None)
        elif self.namespace is not None:
            _text(self.namespace)

    def canonical(self) -> tuple[str | None, ...]:
        """Return a structured key whose segments cannot collide through delimiters."""
        return (self.workspace_id, self.metadata_type, self.namespace, self.full_name)

    @property
    def token(self) -> str:
        """Return the complete canonical key, not a lossy concatenated shorthand."""
        return canonical_json(self.canonical())


class Availability(StrEnum):
    """Distinguish available values, explicitly observed null, and unavailable facts."""

    VALUE = 'value'
    NULL = 'null'
    UNAVAILABLE = 'unavailable'


@dataclass(frozen=True, eq=False)
class FieldValue:
    """Represent a normalized fact; an omitted mapping entry separately means absent."""

    availability: Availability
    value: str | bool | int | tuple[str, ...] | None = None

    def __post_init__(self) -> None:
        """Reject ambiguous nulls, mutable values, and unrecognized availability."""
        if not isinstance(self.availability, Availability):
            raise ModelError('Unknown field availability')
        if self.availability != Availability.VALUE:
            if self.value is not None:
                raise ModelError('Null/unavailable fields cannot carry a value')
        elif self.value is None or type(self.value) not in (str, bool, int, tuple):
            raise ModelError('Available fields require a supported non-null value')
        elif isinstance(self.value, tuple) and not all(type(item) is str for item in self.value):
            raise ModelError('Field lists may contain only strings')

    def canonical(self) -> dict[str, Any]:
        """Retain availability even when its payload is null."""
        return {'availability': self.availability.value, 'value': self.value}

    def __eq__(self, other: object) -> bool:
        """Keep known false and integer zero distinct even in baseline comparisons."""
        if not isinstance(other, FieldValue):
            return NotImplemented
        return self.availability == other.availability and type(self.value) is type(other.value) and self.value == other.value


@dataclass(frozen=True)
class Component:
    """Hold allowlisted source facts, provenance, and a timestamp-independent hash."""

    binding: SourceBinding
    key: ComponentKey
    attributes: Mapping[str, FieldValue] = field(default_factory=dict)
    record_id: str | None = None
    provenance: tuple[str, ...] = ()
    collected_at: str | None = field(default=None, compare=False)

    def __post_init__(self) -> None:
        """Copy mutable mappings and refuse inconsistent/unsupported normalized facts."""
        if not isinstance(self.binding, SourceBinding) or not isinstance(self.key, ComponentKey):
            raise ModelError('Expected normalized component identity records')
        if not isinstance(self.attributes, Mapping):
            raise ModelError('Expected a component attribute mapping')
        if self.key.workspace_id != self.binding.workspace_id:
            raise ModelError('Component workspace does not match source binding')
        if self.record_id is not None:
            _text(self.record_id)
            if self.binding.mode != 'live':
                raise ModelError('Local components cannot assert Salesforce record IDs')
        if self.attributes.keys() - const.COMPONENT_ATTRIBUTES or not all(
            isinstance(v, FieldValue) for v in self.attributes.values()
        ):
            raise ModelError('Unsupported component attribute or field value')
        object.__setattr__(self, 'attributes', MappingProxyType(dict(self.attributes)))
        object.__setattr__(self, 'provenance', _sorted_text(self.provenance))

    def canonical(self) -> dict[str, Any]:
        """Return semantic source content, excluding collection timestamps."""
        return {
            'model_schema': const.MODEL_SCHEMA_VERSION,
            'binding': self.binding.canonical(),
            'key': self.key.canonical(),
            'record_id': self.record_id,
            'attributes': {key: value.canonical() for key, value in self.attributes.items()},
            'provenance': self.provenance,
        }

    @property
    def source_hash(self) -> str:
        """Hash only normalized semantic source inputs."""
        return fingerprint(self.canonical())


@dataclass(frozen=True)
class Selection:
    """Describe requested inventory scope independently of collection success."""

    include_namespaced: bool = False
    full_names: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Normalize optional internal name filters and require a boolean scope."""
        if type(self.include_namespaced) is not bool:
            raise ModelError('Namespace selection must be boolean')
        object.__setattr__(self, 'full_names', _sorted_text(self.full_names))

    def canonical(self) -> dict[str, Any]:
        """Describe the sole supported type and its explicit filters."""
        return {'types': ['ApexClass'], 'include_namespaced': self.include_namespaced, 'full_names': self.full_names}

    def scope_hash(self, binding: SourceBinding) -> str:
        """Bind selection to workspace/mode/org without including collection outcomes."""
        return fingerprint(
            {'model_schema': const.MODEL_SCHEMA_VERSION, 'binding': binding.canonical(), 'selection': self.canonical()}
        )


class CoverageStatus(StrEnum):
    """Represent explicit completeness independently for each collection dimension."""

    COMPLETE = 'complete'
    PARTIAL = 'partial'
    UNAVAILABLE = 'unavailable'
    NOT_COLLECTED = 'not_collected'


@dataclass(frozen=True)
class CollectionCoverage:
    """Record one collection's status, request intent, method, and limit evidence.

    Complete means the selected scope, never whole-org or runtime dependency proof.
    Pagination values are not applicable, exhausted, incomplete, or unknown.
    """

    status: CoverageStatus
    method: str
    requested: bool = True
    pagination: str = 'unknown'
    limit_reached: bool | None = None
    api_version: str | None = None
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Reject claims of completeness that contradict pagination/limit evidence."""
        if not isinstance(self.status, CoverageStatus) or type(self.requested) is not bool:
            raise ModelError('Invalid coverage status or request flag')
        _text(self.method)
        if self.pagination not in {'not_applicable', 'exhausted', 'incomplete', 'unknown'}:
            raise ModelError('Invalid pagination outcome')
        if self.limit_reached is not None and type(self.limit_reached) is not bool:
            raise ModelError('Invalid limit outcome')
        if self.status == CoverageStatus.COMPLETE and (
            self.pagination not in {'not_applicable', 'exhausted'} or self.limit_reached is not False
        ):
            raise ModelError('Complete coverage requires affirmative pagination and limit evidence')
        if self.api_version is not None:
            _text(self.api_version)
        object.__setattr__(self, 'warnings', _sorted_text(self.warnings))

    def canonical(self) -> dict[str, Any]:
        """Include all coverage facts, without conflating empty results with success."""
        return {
            'status': self.status.value,
            'method': self.method,
            'requested': self.requested,
            'pagination': self.pagination,
            'limit_reached': self.limit_reached,
            'api_version': self.api_version,
            'warnings': self.warnings,
        }


@dataclass(frozen=True)
class Coverage:
    """Keep inventory, audit, and relationship evidence independent for a bound scope."""

    binding: SourceBinding
    selection: Selection
    inventory: CollectionCoverage
    audit: CollectionCoverage
    relationships: CollectionCoverage

    def __post_init__(self) -> None:
        """Inventory is always part of the requested source operation."""
        if not isinstance(self.binding, SourceBinding) or not isinstance(self.selection, Selection):
            raise ModelError('Expected normalized coverage binding and selection')
        if not all(isinstance(value, CollectionCoverage) for value in (self.inventory, self.audit, self.relationships)):
            raise ModelError('Expected independent normalized collection coverage')
        if not self.inventory.requested:
            raise ModelError('Inventory coverage must be requested')

    def canonical(self) -> dict[str, Any]:
        """Return independently collected evidence plus its comparable scope."""
        return {
            'model_schema': const.MODEL_SCHEMA_VERSION,
            'binding': self.binding.canonical(),
            'selection': self.selection.canonical(),
            'inventory': self.inventory.canonical(),
            'audit': self.audit.canonical(),
            'relationships': self.relationships.canonical(),
        }

    @property
    def scope_hash(self) -> str:
        """Return the comparable selected scope, not a completeness claim."""
        return self.selection.scope_hash(self.binding)

    @property
    def outcome(self) -> ExitCode:
        """Report requested incompleteness, allowing explicit offline design exclusions."""
        facets = (self.inventory, self.audit, self.relationships)
        return (
            ExitCode.INCOMPLETE if any(f.requested and f.status != CoverageStatus.COMPLETE for f in facets) else ExitCode.SUCCESS
        )


@dataclass(frozen=True)
class Relationship:
    """Record directed reported references, coverage, and unresolved endpoint evidence."""

    source: ComponentKey
    target: ComponentKey | None
    kind: str
    evidence_method: str
    coverage: CollectionCoverage
    unresolved_target: str | None = None
    stale: bool = False

    def __post_init__(self) -> None:
        """Require one resolved or unresolved target without inventing a managed note."""
        if not isinstance(self.source, ComponentKey) or (self.target is not None and not isinstance(self.target, ComponentKey)):
            raise ModelError('Expected normalized relationship endpoint keys')
        if not isinstance(self.coverage, CollectionCoverage):
            raise ModelError('Expected normalized relationship coverage')
        _text(self.kind)
        _text(self.evidence_method)
        if (self.target is None) == (self.unresolved_target is None):
            raise ModelError('Relationship requires exactly one resolved or unresolved target')
        if self.target is not None and self.target.workspace_id != self.source.workspace_id:
            raise ModelError('Relationship endpoints must belong to one workspace')
        if self.unresolved_target is not None:
            _text(self.unresolved_target)
        if type(self.stale) is not bool:
            raise ModelError('Relationship stale flag must be boolean')

    def canonical(self) -> dict[str, Any]:
        """Preserve direction, unresolved labels, provenance, coverage, and staleness."""
        return {
            'source': self.source.canonical(),
            'target': self.target.canonical() if self.target is not None else None,
            'kind': self.kind,
            'evidence_method': self.evidence_method,
            'coverage': self.coverage.canonical(),
            'unresolved_target': self.unresolved_target,
            'stale': self.stale,
        }


def graph_fingerprint(relationships: Iterable[Relationship], paths: Mapping[ComponentKey, str]) -> str:
    """Hash supplied incoming/outgoing edges and relevant resolved note locations.

    :param relationships: Incident edges supplied by the later graph layer.
    :param paths: Relevant endpoint locations; moving either endpoint invalidates links.
    :returns: Order-independent hash including coverage/stale/unresolved evidence.
    :raises ModelError: If an endpoint path is unsafe or an exact edge is duplicated.
    """
    edges = sorted(canonical_json(edge.canonical()) for edge in relationships)
    if len(set(edges)) != len(edges):
        raise ModelError('Duplicate relationship evidence')
    locations = sorted((key.token, _path(path)) for key, path in paths.items())
    return fingerprint({'model_schema': const.MODEL_SCHEMA_VERSION, 'edges': edges, 'paths': locations})


def render_fingerprint(
    *,
    source_hash: str,
    graph_hash: str,
    generated_template_hash: str,
    layout: Layout,
    options: Options,
) -> str:
    """Hash semantic render inputs without rendering, reading templates, or publishing.

    :returns: Fingerprint including schema/marker/renderer versions and layout/privacy.
    :raises ModelError: For malformed input digests.
    """
    for digest in (source_hash, graph_hash, generated_template_hash):
        _hash(digest)
    return fingerprint(
        {
            'model_schema': const.MODEL_SCHEMA_VERSION,
            'note_schema': const.NOTE_SCHEMA_VERSION,
            'marker_version': const.MARKER_VERSION,
            'renderer_version': const.RENDERER_VERSION,
            'source': source_hash,
            'graph': graph_hash,
            'generated_template': generated_template_hash,
            'layout': {'apex_classes': layout.apex_classes, 'dashboards': layout.dashboards},
            'options': {'include_namespaced': options.include_namespaced, 'include_audit_names': options.include_audit_names},
        }
    )


def creation_fingerprint(render_hash: str, creation_template_hash: str) -> str:
    """Fingerprint a new-note candidate separately from its reusable generated render hash.

    :param render_hash: Generated-only fingerprint also saved for future refreshes.
    :param creation_template_hash: Content hash of the creation-only template.
    :returns: Candidate fingerprint; never substitute this for NoteState.render_hash.
    """
    _hash(render_hash)
    _hash(creation_template_hash)
    return fingerprint({'render': render_hash, 'creation_template': creation_template_hash})


def property_owner(name: str) -> str:
    """Classify exact owned names, refusing unsupported reserved Salesforce fields.

    :raises ModelError: If a reserved sf_* name is not in version one's exact allowlist.
    """
    _text(name)
    if name in const.OWNED_PROPERTIES:
        return 'obforce'
    if name.startswith('sf_'):
        raise ModelError('Unknown reserved Salesforce property')
    return 'user'


@dataclass(frozen=True)
class NoteState:
    """Represent private note mapping/baselines without loading or publishing state.

    Full document schema, duplicate JSON keys, discovery, and reconciliation are
    later-thread responsibilities. Absent baseline keys differ from explicit null.
    """

    obforce_id: str
    binding: SourceBinding
    key: ComponentKey
    path: str
    source_hash: str
    graph_hash: str
    render_hash: str
    generated_properties: Mapping[str, FieldValue]
    generated_region_hash: str
    schema_version: int = const.STATE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        """Validate identity, path, digests, and exact generated-property baselines."""
        if not isinstance(self.binding, SourceBinding) or not isinstance(self.key, ComponentKey):
            raise ModelError('Expected normalized note-state identity records')
        if not isinstance(self.generated_properties, Mapping):
            raise ModelError('Expected an owned-property baseline mapping')
        try:
            valid_id = str(UUID(self.obforce_id)) == self.obforce_id
        except (ValueError, TypeError, AttributeError):
            valid_id = False
        if not valid_id or type(self.schema_version) is not int or self.schema_version != const.STATE_SCHEMA_VERSION:
            raise ModelError('Invalid note-state identity or schema')
        if self.key.workspace_id != self.binding.workspace_id:
            raise ModelError('Note-state workspace does not match source binding')
        _path(self.path)
        for digest in (self.source_hash, self.graph_hash, self.render_hash, self.generated_region_hash):
            _hash(digest)
        baseline = dict(self.generated_properties)
        if baseline.keys() - const.OWNED_PROPERTIES or not all(isinstance(v, FieldValue) for v in baseline.values()):
            raise ModelError('Invalid generated-property baseline')
        if baseline.get('obforce_id') != FieldValue(Availability.VALUE, self.obforce_id) or baseline.get(
            'obforce_schema'
        ) != FieldValue(Availability.VALUE, const.NOTE_SCHEMA_VERSION):
            raise ModelError('Baseline must retain exact note identity and supported schema')
        object.__setattr__(self, 'generated_properties', MappingProxyType(baseline))

    def canonical(self) -> dict[str, Any]:
        """Return the private normalized state record without adding volatile timestamps."""
        return {
            'state_schema': self.schema_version,
            'obforce_id': self.obforce_id,
            'binding': self.binding.canonical(),
            'key': self.key.canonical(),
            'path': self.path,
            'source_hash': self.source_hash,
            'graph_hash': self.graph_hash,
            'render_hash': self.render_hash,
            'generated_properties': {key: value.canonical() for key, value in self.generated_properties.items()},
            'generated_region_hash': self.generated_region_hash,
        }


def validate_identities(components: Iterable[Component], notes: Iterable[NoteState] = ()) -> None:
    """Refuse duplicate canonical keys, Salesforce mappings, note IDs, or portable paths.

    This validates supplied records only; it does not discover notes or reconcile
    edited state. Canonical component keys preserve Unicode/case while note paths
    use NFC plus casefold for conservative portable collision detection.

    :raises ConflictError: If any supplied identity or mapping is duplicated.
    """
    keys: set[str] = set()
    record_ids: set[tuple[str, str]] = set()
    binding: SourceBinding | None = None
    for component in components:
        binding = component.binding if binding is None else binding
        require_same_source(binding, component.binding)
        if component.key.token in keys:
            raise ConflictError('Duplicate canonical component mapping')
        keys.add(component.key.token)
        if component.record_id is not None:
            record_key = (canonical_json(component.binding.canonical()), component.record_id)
            if record_key in record_ids:
                raise ConflictError('Duplicate Salesforce record mapping')
            record_ids.add(record_key)
    note_ids: set[str] = set()
    note_keys: set[str] = set()
    paths: set[str] = set()
    for note in notes:
        binding = note.binding if binding is None else binding
        require_same_source(binding, note.binding)
        path_key = unicodedata.normalize('NFC', note.path).casefold()
        if note.obforce_id in note_ids or note.key.token in note_keys or path_key in paths:
            raise ConflictError('Duplicate note identity, source mapping, or portable path')
        note_ids.add(note.obforce_id)
        note_keys.add(note.key.token)
        paths.add(path_key)


def component_fingerprint(components: Iterable[Component]) -> str:
    """Hash a deterministic inventory, refusing identity collisions before ordering."""
    records = tuple(components)
    validate_identities(records)
    return fingerprint(sorted((component.canonical() for component in records), key=lambda item: canonical_json(item['key'])))
