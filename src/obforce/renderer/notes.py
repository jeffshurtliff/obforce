# -*- coding: utf-8 -*-
"""
:Module:            obforce.renderer.notes
:Synopsis:          Serializes deterministic Apex candidates without reading or writing notes
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     28 Oct 2026
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from functools import cached_property
from types import MappingProxyType
from uuid import UUID

from obforce import constants as const
from obforce.config import Layout, Options, relative_path
from obforce.errors import ConfigError, ConflictError, ModelError
from obforce.graph.dependencies import DependencyGraph, Endpoint, _FingerprintPaths
from obforce.models import (
    Availability,
    Component,
    ComponentKey,
    Coverage,
    FieldValue,
    creation_fingerprint,
    fingerprint,
    property_owner,
    render_fingerprint,
    require_same_source,
    validate_identities,
)
from obforce.renderer.templates import TemplateAsset, load_template

_DEFAULT_LAYOUT = Layout()
_DEFAULT_OPTIONS = Options()

_HUMAN_HEADINGS = ('## Business Context', '## Known Issues / Technical Debt', '## Additional Information')
_GENERATED_HEADINGS = ('## Salesforce Metadata', '## Coverage', '## References', '## Referenced By')


def _bounded(value: object) -> None:
    """Bound normalized primitive input before hashing, escaping or template evaluation."""
    pending = [value]
    count, size = 0, 0
    while pending:
        item = pending.pop()
        count += 1
        if count > const.MAX_RENDER_INPUT_NODES:
            raise ModelError('Rendering input exceeds node bound')
        if type(item) is str:
            if len(item) > const.MAX_RENDER_TEXT_CHARS:
                raise ModelError('Rendering input exceeds text bound')
            try:
                size += len(item.encode('utf-8'))
            except UnicodeError as error:
                raise ModelError('Rendering requires valid Unicode') from error
            if 'obforce:' in item or any(unicodedata.category(c) in {'Cc', 'Cs', 'Cf', 'Zl', 'Zp'} for c in item):
                raise ModelError('Rendering input contains controls or reserved markers')
        elif item is None or type(item) is bool:
            size += 5
        elif type(item) is int and item.bit_length() <= 64:
            size += 20
        elif type(item) is dict:
            if len(item) > const.MAX_RENDER_COMPONENTS or any(type(k) is not str for k in item):
                raise ModelError('Invalid bounded input mapping')
            pending.extend(item.keys())
            pending.extend(item.values())
        elif type(item) in (tuple, list) and len(item) <= const.MAX_RENDER_INPUT_NODES:
            pending.extend(item)
        else:
            raise ModelError('Unsupported rendering input')
        if size > const.MAX_RENDER_INPUT_BYTES:
            raise ModelError('Rendering input exceeds aggregate byte bound')


def markdown(value: str) -> str:
    """Escape data within fixed inline prefixes or validated wikilink labels.

    Ordinary inline punctuation stays readable; only intraword underscores,
    nondomain periods and whole ISO timestamp colons are literal. Delimiter
    underscores and syntax-capable punctuation retain numeric escaping. Never
    use this for raw block boundaries, link targets, HTML attributes or markers.
    """
    _bounded(value)
    timestamp = re.fullmatch(r'"?\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})"?', value)
    result = []
    for index, char in enumerate(value):
        intraword = char == '_' and 0 < index < len(value) - 1 and value[index - 1].isalnum() and value[index + 1].isalnum()
        period = char == '.' and (index == len(value) - 1 or not value[index + 1].isalpha())
        ordinary = char in ' /-"\',;()' or period or (char == ':' and timestamp is not None)
        result.append(char if char.isalnum() or ordinary or intraword else f'&#{ord(char)};')
    return ''.join(result)


def _path(path: str) -> str:
    """Validate portable Markdown locations and unambiguous literal wikilink targets."""
    relative_path(path)
    if (
        len(path) > const.MAX_RENDER_PATH_CHARS
        or len(path.split('/')) > const.MAX_RENDER_PATH_DEPTH
        or not path.endswith('.md')
        or any(c in path for c in '#[]^%&;`!{}')
        or any(unicodedata.category(c) in {'Cf', 'Zl', 'Zp'} for c in path)
        or any(len(part.encode('utf-8')) > 240 for part in path.split('/'))
    ):
        raise ModelError('Invalid or ambiguous managed Markdown path')
    return path


@dataclass(frozen=True)
class _BatchPaths(Mapping[ComponentKey, str]):
    """Hold an immutable batch snapshot with validation at existing call sites.

    Construct afresh for each planning pass. Lazy views retain error precedence;
    standalone renderer calls with ordinary mappings still validate every call.
    """

    source: Mapping[ComponentKey, str]
    workspace_id: str

    def __post_init__(self) -> None:
        object.__setattr__(self, 'source', MappingProxyType(dict(self.source)))

    def __getitem__(self, key: ComponentKey) -> str:
        return self.source[key]

    def __iter__(self) -> Iterator[ComponentKey]:
        return iter(self.source)

    def __len__(self) -> int:
        return len(self.source)

    @cached_property
    def checked(self) -> Mapping[ComponentKey, str]:
        return MappingProxyType(_paths(self.source))

    @cached_property
    def workspaces(self) -> frozenset[str]:
        return frozenset(key.workspace_id for key in self.checked)

    @cached_property
    def graph_paths(self) -> _FingerprintPaths:
        return _FingerprintPaths(self.checked, self.workspace_id)


def _paths(paths: Mapping[ComponentKey, str]) -> Mapping[ComponentKey, str]:
    """Refuse portable collisions in supplied mappings, including parent/file ambiguity."""
    if type(paths) is _BatchPaths:
        return paths.checked
    if not isinstance(paths, Mapping) or len(paths) > const.MAX_RENDER_COMPONENTS:
        raise ModelError('Invalid or excessive managed-note mapping')
    checked, portable, prefixes = {}, set(), set()
    spellings: dict[str, str] = {}
    for key, path in paths.items():
        if not isinstance(key, ComponentKey):
            raise ModelError('Managed-note mapping requires supported component keys')
        _bounded([key.canonical(), path])
        location = unicodedata.normalize('NFC', _path(path)).casefold()
        for n in range(1, len(path.split('/')) + 1):
            spelling = '/'.join(path.split('/')[:n])
            token = unicodedata.normalize('NFC', spelling).casefold()
            if token in spellings and spellings[token] != spelling:
                raise ConflictError('Ambiguous namespace or path spelling')
            spellings[token] = spelling
        parents = {'/'.join(location.split('/')[:n]) for n in range(1, len(location.split('/')))}
        if location in portable or location in prefixes or parents & portable:
            raise ConflictError('Ambiguous portable managed-note paths')
        portable.add(location)
        prefixes.update(parents)
        checked[key] = path
    _bounded([[key.canonical(), path] for key, path in checked.items()])
    return checked


def note_paths(components: Sequence[Component], layout: Layout = _DEFAULT_LAYOUT) -> dict[ComponentKey, str]:
    """Propose deterministic new paths; proposals do not discover or establish ownership.

    :raises ConflictError: For duplicate identities or portable namespace/path collisions.
    :raises ModelError: For unsafe identity-derived filenames or excessive inputs.
    """
    if not isinstance(components, (list, tuple)) or len(components) > const.MAX_RENDER_COMPONENTS:
        raise ModelError('Expected a bounded component sequence')
    if any(not isinstance(component, Component) for component in components):
        raise ModelError('Expected normalized components')
    _bounded([component.canonical() for component in components])
    validate_identities(components)
    result = {}
    for component in components:
        key = component.key
        for part in (key.full_name, key.namespace):
            if part is not None and ('/' in part or relative_path(part) != part):
                raise ModelError('Component name cannot form a portable path segment')
        namespace = '' if key.namespace is None else key.namespace + '/'
        result[key] = f'{layout.apex_classes}/{namespace}{key.full_name}.md'
    return _paths(result)


def _scalar(value: object) -> str:
    """Serialize supported flat property values in the JSON-compatible YAML subset."""
    _bounded(value)
    if (
        value is not None
        and type(value) not in (str, bool, int)
        and not (type(value) in (list, tuple) and all(type(v) is str for v in value))
    ):
        raise ModelError('Properties require flat scalars or lists of strings')
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def _frontmatter(properties: Mapping[str, object]) -> str:
    """Serialize exact engine-owned keys and explicit creation-only user defaults."""
    if len(properties) > 128:
        raise ModelError('Too many creation properties')
    lines = []
    for key in sorted(properties):
        if type(key) is not str or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,127}', key):
            raise ModelError('Unsupported flat property name')
        property_owner(key)
        lines.append(f'{json.dumps(key)}: {_scalar(properties[key])}')
    return '---\n' + '\n'.join(lines) + '\n---\n'


def _section_check(text: str, headings: tuple[str, ...]) -> None:
    """Validate candidate-only structure; this is never an existing-note parser."""
    if (
        not text.endswith('\n')
        or 'obforce:' in text
        or '\r' in text
        or '\x00' in text
        or any(text.splitlines().count(heading) != 1 for heading in headings)
        or any(line.strip() in {'---', '...'} or line.lstrip().startswith(('sf_', 'obforce_')) for line in text.splitlines())
    ):
        raise ConfigError('Rendered candidate has invalid required structure')


def _field_text(value: FieldValue | None) -> str:
    """Explain absent, unavailable, observed null and available false distinctly."""
    if value is None:
        return 'absent (not supplied)'
    if value.availability != Availability.VALUE:
        return 'observed null' if value.availability == Availability.NULL else 'unavailable (not collected or accessible)'
    return markdown(_scalar(value.value))


def _properties(component: Component, coverage: Coverage, identity: str, options: Options) -> dict[str, object]:
    """Build reserved properties without including raw identifiers or unknown audit values."""
    try:
        if type(identity) is not str or str(UUID(identity)) != identity:
            raise ValueError
    except (ValueError, TypeError, AttributeError) as error:
        raise ModelError('Caller must supply a canonical persistent note UUID') from error
    properties = {
        'obforce_id': identity,
        'obforce_schema': const.NOTE_SCHEMA_VERSION,
        'sf_type': 'ApexClass',
        'sf_full_name': component.key.full_name,
        'sf_namespace': component.key.namespace,
        'sf_source_mode': component.binding.mode,
        'sf_dependency_coverage': coverage.relationships.status.value,
        'sf_lifecycle': 'active',
    }
    for name, value in component.attributes.items():
        if not options.include_audit_names and name in {'created_by', 'last_modified_by'}:
            continue
        if value.availability == Availability.VALUE:
            properties[f'sf_{name}'] = value.value
        elif value.availability == Availability.NULL and name in {'api_version', 'status'}:
            properties[f'sf_{name}'] = None
    for attribute, property_name in (('created_at', 'sf_created'), ('last_modified_at', 'sf_last_modified')):
        value = component.attributes.get(attribute)
        if value is not None and value.availability == Availability.VALUE and type(value.value) is str:
            try:
                timestamp = datetime.fromisoformat(value.value)
                if timestamp.tzinfo is not None:
                    properties[property_name] = timestamp.astimezone(UTC).date().isoformat()
            except (ValueError, OverflowError):
                # Retain the original normalized value; an unsupported value is
                # never guessed into an authoritative date-only projection.
                continue
    return properties


def _endpoint(endpoint: Endpoint, paths: Mapping[ComponentKey, str]) -> str:
    """Link only exact supported mapped keys; IDs never enter the display projection."""
    label = '/'.join(part for part in (endpoint.namespace, endpoint.name) if part is not None) or 'Unnamed endpoint'
    label = markdown(label)
    if endpoint.key is not None and endpoint.key in paths:
        return f'[[{paths[endpoint.key]}|{label}]]'
    status = 'unmapped' if endpoint.key is not None else endpoint.resolution
    return f'{label} (type: {markdown(endpoint.metadata_type or "unknown")}; {status}; no managed link)'


def _relations(graph: DependencyGraph, key: ComponentKey, paths: Mapping[ComponentKey, str], incoming: bool) -> str:
    """Render reciprocal directions with each distinct provenance/coverage/stale observation."""
    title = 'Referenced By' if incoming else 'References'
    edges = graph.referenced_by(key) if incoming else graph.references(key)
    lines = [f'## {title}', '']
    for edge in edges:
        endpoint = edge.source if incoming else edge.target
        observations = '; '.join(
            f'{markdown(item.method)}: {item.coverage.status.value}, {"stale" if item.stale else "current"}'
            f', requested: {str(item.coverage.requested).lower()}, pagination: {item.coverage.pagination}'
            f', limit reached: {_scalar(item.coverage.limit_reached)}'
            f', API version: {markdown(item.coverage.api_version or "unknown")}'
            f', collection method: {markdown(item.coverage.method)}'
            f', warnings: {"; ".join(markdown(warning) for warning in item.coverage.warnings) or "none"}'
            for item in edge.evidence
        )
        lines.append(f'- {_endpoint(endpoint, paths)} — {observations}')
    if not edges:
        lines.append('No reported references in this snapshot; absence is not proof of no dependencies.')
    return '\n'.join(lines)


@dataclass(frozen=True, repr=False)
class GeneratedCandidate:
    """Hold validated generated bytes/baselines, without publication permission or state I/O."""

    region: str
    properties: Mapping[str, object] = field(repr=False)
    source_hash: str
    graph_hash: str
    render_hash: str

    def __post_init__(self) -> None:
        object.__setattr__(self, 'properties', MappingProxyType(dict(self.properties)))

    @property
    def region_hash(self) -> str:
        """Hash the exact bytes strictly between future engine-controlled markers."""
        return hashlib.sha256(self.region.encode('utf-8')).hexdigest()


@dataclass(frozen=True, repr=False)
class NewNoteCandidate:
    """Hold complete new-note bytes only; never apply this to an existing note."""

    path: str
    text: str
    generated: GeneratedCandidate
    creation_hash: str


def render_generated(
    component: Component,
    coverage: Coverage,
    graph: DependencyGraph,
    *,
    identity: str,
    managed_paths: Mapping[ComponentKey, str],
    layout: Layout = _DEFAULT_LAYOUT,
    options: Options = _DEFAULT_OPTIONS,
    template: TemplateAsset | None = None,
) -> GeneratedCandidate:
    """Render one supported candidate using explicit normalized facts and managed paths.

    No source acquisition, note discovery, existing-note parsing or writes occur.
    Hash equality grants no permission to replace an edited generated baseline.

    :raises ModelError: For excessive, unsafe or unsupported normalized input.
    :raises ConflictError: For source/scope/path ambiguity.
    :raises ConfigError: For invalid templates or candidate structure.
    """
    if not isinstance(component, Component) or not isinstance(coverage, Coverage) or not isinstance(graph, DependencyGraph):
        raise ModelError('Rendering requires normalized source, coverage and graph records')
    if not isinstance(layout, Layout) or not isinstance(options, Options):
        raise ModelError('Rendering requires normalized layout and privacy options')
    require_same_source(component.binding, coverage.binding)
    require_same_source(component.binding, graph.binding)
    if coverage.selection != graph.selection or coverage.relationships != graph.coverage:
        raise ConflictError('Graph and source coverage scope disagree')
    if (
        options.include_namespaced != coverage.selection.include_namespaced
        or (component.key.namespace is not None and not options.include_namespaced)
        or (coverage.selection.full_names and component.key.full_name not in coverage.selection.full_names)
    ):
        raise ConflictError('Rendering identity or options are outside selected scope')
    if component.binding.mode == 'local' and (graph.edges or coverage.relationships.status.value != 'not_collected'):
        raise ConflictError('Offline relationships must remain not collected')
    paths = _paths(managed_paths)
    workspaces = managed_paths.workspaces if type(managed_paths) is _BatchPaths else (key.workspace_id for key in paths)
    if any(workspace != component.binding.workspace_id for workspace in workspaces):
        raise ConflictError('Managed paths belong to another workspace')
    incident = tuple(edge for edge in graph.edges if component.key in (edge.source.key, edge.target.key))
    if len(incident) > const.MAX_RENDER_EDGES:
        raise ModelError('Incident graph exceeds rendering edge bound')
    _bounded([component.canonical(), coverage.canonical(), [edge.canonical() for edge in incident]])
    properties = _properties(component, coverage, identity, options)
    # Validate even properties that will only be returned for a generated-only candidate.
    _frontmatter(properties)
    facts = [
        '## Salesforce Metadata',
        '',
        f'- ApexClass: {markdown(component.key.full_name)}',
        f'- Namespace: {markdown(component.key.namespace) if component.key.namespace else "none"}',
        f'- Source: {component.binding.mode}',
    ]
    if component.provenance:
        facts.append('- Source provenance: ' + '; '.join(markdown(item) for item in component.provenance))
    for name in sorted(const.COMPONENT_ATTRIBUTES):
        label = markdown(name)
        if name in {'created_by', 'last_modified_by'} and not options.include_audit_names:
            facts.append(f'- {label}: omitted by privacy option')
        else:
            facts.append(f'- {label}: {_field_text(component.attributes.get(name))}')
    facets = ['## Coverage', '']
    for name in ('inventory', 'audit', 'relationships'):
        record = getattr(coverage, name)
        facets.append(
            f'- {name}: {record.status.value}; requested: {str(record.requested).lower()}; '
            f'method: {markdown(record.method)}; pagination: {record.pagination}; '
            f'limit reached: {_scalar(record.limit_reached)}; API version: {markdown(record.api_version or "unknown")}'
        )
        for warning in record.warnings:
            facets.append(f'{const.MARKDOWN_LIST_INDENT}- Warning: {markdown(warning)}')
    facets.extend(
        [
            '',
            'Inventory describes only the selected accessible scope. Offline audit values remain unavailable.',
            'Offline relationships are not collected. Requested platform relationships remain partial/unavailable:',
            'the fixed collector cannot establish exhaustion, including clean empty results.',
            'Platform-reported references are not runtime proof or comprehensive impact analysis.',
        ]
    )
    context = {
        'metadata': '\n'.join(facts),
        'coverage': '\n'.join(facets),
        'references': _relations(graph, component.key, paths, False),
        'referenced_by': _relations(graph, component.key, paths, True),
    }
    asset = template if template is not None else load_template('apex_generated.md.j2')
    if not isinstance(asset, TemplateAsset) or asset.name != 'apex_generated.md.j2':
        raise ConfigError('Expected the known generated-section template')
    region = asset.render(context)
    _section_check(region, _GENERATED_HEADINGS)
    graph_paths = managed_paths.graph_paths if type(managed_paths) is _BatchPaths else paths
    graph_hash = graph.note_fingerprint(component.key, graph_paths)
    context_graph_hash = fingerprint({'graph': graph_hash, 'coverage': coverage.canonical()})
    render_hash = render_fingerprint(
        source_hash=component.source_hash,
        graph_hash=context_graph_hash,
        generated_template_hash=asset.content_hash,
        layout=layout,
        options=options,
    )
    return GeneratedCandidate(region, properties, component.source_hash, graph_hash, render_hash)


def render_new_note(
    component: Component,
    coverage: Coverage,
    graph: DependencyGraph,
    *,
    identity: str,
    managed_paths: Mapping[ComponentKey, str],
    layout: Layout = _DEFAULT_LAYOUT,
    options: Options = _DEFAULT_OPTIONS,
    generated_template: TemplateAsset | None = None,
    creation_template: TemplateAsset | None = None,
    user_properties: Mapping[str, object] | None = None,
) -> NewNoteCandidate:
    """Construct and validate a whole NEW note, never rerender an existing note.

    :param identity: Persistent canonical UUID supplied by the caller, never regenerated.
    :param user_properties: Explicit flat creation defaults; owned by the user thereafter.
    :returns: Candidate with exact engine envelope and separate generated/creation hashes.
    """
    generated = render_generated(
        component,
        coverage,
        graph,
        identity=identity,
        managed_paths=managed_paths,
        layout=layout,
        options=options,
        template=generated_template,
    )
    if component.key not in managed_paths:
        raise ModelError('A new-note candidate requires an explicit validated path')
    properties = {
        'type': 'salesforce_component',
        'tags': ('salesforce',),
        'technical_debt': False,
        'tech_debt_severity': '',
        'tech_debt_status': '',
        'last_reviewed': None,
    }
    if user_properties is not None:
        if not isinstance(user_properties, Mapping) or len(user_properties) > 128:
            raise ModelError('Invalid creation properties')
        for key, value in user_properties.items():
            if property_owner(key) != 'user':
                raise ConflictError('Creation defaults cannot redefine reserved properties')
            if key == 'technical_debt' and type(value) is not bool:
                raise ModelError('New-note technical_debt requires a Boolean')
            _scalar(value)
            properties[key] = value
    properties.update(generated.properties)
    envelope = _frontmatter(properties)
    asset = creation_template if creation_template is not None else load_template('apex_created.md.j2')
    if not isinstance(asset, TemplateAsset) or asset.name != 'apex_created.md.j2':
        raise ConfigError('Expected the known creation template')
    human = asset.render({})
    _section_check(human, _HUMAN_HEADINGS)
    text = envelope + '\n' + const.GENERATED_START + '\n' + generated.region + const.GENERATED_END + '\n\n' + human
    if len(text.encode('utf-8')) > const.MAX_NOTE_BYTES:
        raise ModelError('Complete note exceeds output byte bound')
    # Exact construction plus equality validates the entire new envelope, with no
    # permissive YAML parsing, duplicate keys, template-supplied markers or repair.
    if text.count(const.GENERATED_START) != 1 or text.count(const.GENERATED_END) != 1 or not text.startswith(envelope):
        raise ConfigError('Invalid complete new-note envelope')
    return NewNoteCandidate(
        _path(managed_paths[component.key]), text, generated, creation_fingerprint(generated.render_hash, asset.content_hash)
    )
