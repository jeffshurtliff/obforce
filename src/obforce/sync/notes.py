# -*- coding: utf-8 -*-
"""
:Module:            obforce.sync.notes
:Synopsis:          Parses supplied managed-note bytes and constructs preservation patches
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     20 Oct 2026
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date, datetime
from types import MappingProxyType
from uuid import UUID

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError
from ruamel.yaml.events import CollectionEndEvent, CollectionStartEvent, NodeEvent, ScalarEvent
from ruamel.yaml.nodes import MappingNode, ScalarNode, SequenceNode
from ruamel.yaml.tokens import AliasToken, AnchorToken, DirectiveToken, ScalarToken, TagToken

from obforce import constants as const
from obforce.errors import ConfigError, ConflictError, ModelError
from obforce.models import Availability, CoverageStatus, FieldValue, NoteState
from obforce.renderer.notes import _GENERATED_HEADINGS, GeneratedCandidate, _frontmatter, _section_check


@dataclass(frozen=True, repr=False)
class ParsedNote:
    """Hold a private immutable view; this establishes no filesystem ownership.

    Properties use immutable primitive values; absent keys remain absent. Offsets
    refer to exact supplied bytes, except private YAML spans which index Unicode.
    Instances are observations, never permission to publish or bypass baselines.
    """

    raw: bytes
    properties: Mapping[str, object]
    generated_properties: Mapping[str, FieldValue]
    region_start: int
    region_end: int
    front_start: int
    front_end: int
    ending: bytes
    _front: str = field(repr=False)
    _spans: Mapping[str, tuple[int, int, int]] = field(repr=False)
    _comments: tuple[tuple[int, int], ...] = field(repr=False)

    @property
    def region(self) -> bytes:
        """Return exact marker-interior bytes, without newline normalization."""
        return self.raw[self.region_start : self.region_end]

    @property
    def region_hash(self) -> str:
        """Hash exact observed marker-interior bytes, including line endings."""
        return hashlib.sha256(self.region).hexdigest()


@dataclass(frozen=True, repr=False)
class NotePatch:
    """Return candidate bytes and the exact baselines a later caller would save.

    No state file is loaded or written. This record is not a transaction, change
    planner, move reconciliation or publication authorization.
    """

    content: bytes
    generated_properties: Mapping[str, FieldValue]
    generated_region: bytes
    generated_region_hash: str
    source_hash: str
    graph_hash: str
    render_hash: str
    changed: bool


def _yaml() -> YAML:
    """Use fresh safe-derived pure round-trip instances without added constructors."""
    parser = YAML(typ='rt', pure=True)
    parser.allow_duplicate_keys = False
    parser.preserve_quotes = True
    parser.max_depth = const.MAX_YAML_DEPTH + 1  # Library counts leaf scalars as a level.
    return parser


def _ending(data: bytes) -> bytes:
    """Refuse mixed endings within a generator-controlled envelope."""
    crlf = data.count(b'\r\n')
    if crlf and data.count(b'\n') != crlf:
        raise ConflictError('Managed envelope has mixed line endings')
    return b'\r\n' if crlf else b'\n'


def _preflight(text: str) -> tuple[tuple[int, int], ...]:
    """Bound scanner tokens and parser events before composition or construction."""
    comments = set()
    for count, token in enumerate(_yaml().scan(text), 1):
        if count > const.MAX_YAML_TOKENS:
            raise ConflictError('Frontmatter exceeds token bound')
        if isinstance(token, (AliasToken, AnchorToken, DirectiveToken, TagToken)):
            raise ConflictError('Unsupported YAML reference or tag')
        pending = list(getattr(token, 'comment', None) or [])
        while pending:
            item = pending.pop()
            if isinstance(item, list):
                pending.extend(item)
            elif type(item) is str:
                # ruamel stores block-scalar header comments without source marks.
                if not isinstance(token, ScalarToken) or token.style not in ('|', '>'):
                    raise ConflictError('Unsupported comment representation')
                line_end = text.find('\n', token.start_mark.index, token.end_mark.index)
                comment_start = text.find('#', token.start_mark.index, line_end)
                if line_end < 0 or comment_start < 0:
                    raise ConflictError('Unsupported comment boundary')
                comments.add((comment_start, line_end + 1))
            elif item is not None:
                comments.add((item.start_mark.index, item.end_mark.index))
    depth = nodes = 0
    for event in _yaml().parse(text):
        if isinstance(event, NodeEvent):
            nodes += 1
            if nodes > const.MAX_YAML_NODES:
                raise ConflictError('Frontmatter exceeds node bound')
        if isinstance(event, ScalarEvent) and len(event.value.encode('utf-8')) > const.MAX_YAML_SCALAR_BYTES:
            raise ConflictError('Frontmatter exceeds scalar bound')
        if isinstance(event, CollectionStartEvent):
            depth += 1
            if depth > const.MAX_YAML_DEPTH:
                raise ConflictError('Frontmatter exceeds depth bound')
        elif isinstance(event, CollectionEndEvent):
            depth -= 1
    return tuple(sorted(comments))


def _scalar(node: ScalarNode, value: object, *, owned: bool) -> object:
    """Normalize only supported YAML scalar types, never arbitrary objects."""
    if not isinstance(node, ScalarNode) or len(node.value.encode('utf-8')) > const.MAX_YAML_SCALAR_BYTES:
        raise ConflictError('Unsupported or excessive YAML scalar')
    kind = node.tag.removeprefix('tag:yaml.org,2002:')
    if kind == 'str' and isinstance(value, str):
        return str(value)
    if kind == 'null' and value is None:
        return None
    if kind == 'bool' and type(value) is bool:
        return value
    if kind == 'int' and isinstance(value, int) and not isinstance(value, bool) and value.bit_length() <= 64:
        return int(value)
    if not owned and kind == 'float' and isinstance(value, float) and math.isfinite(value):
        return float(value)
    if not owned and kind == 'timestamp' and isinstance(value, (date, datetime)):
        return datetime.fromisoformat(value.isoformat()) if isinstance(value, datetime) else date.fromisoformat(value.isoformat())
    raise ConflictError('Unsupported YAML scalar type')


def _value(node: object, value: object, *, owned: bool) -> object:
    """Accept flat scalars or bounded lists of strings, including their empty forms."""
    if isinstance(node, ScalarNode):
        return _scalar(node, value, owned=owned)
    if isinstance(node, SequenceNode) and len(node.value) <= const.MAX_YAML_LIST_ITEMS:
        if not isinstance(value, list) or any(
            not isinstance(n, ScalarNode) or n.tag != 'tag:yaml.org,2002:str' for n in node.value
        ):
            raise ConflictError('YAML lists require strings')
        return tuple(_scalar(n, v, owned=owned) for n, v in zip(node.value, value, strict=True))
    raise ConflictError('Unsupported YAML structure')


def _fields(properties: Mapping[str, object]) -> Mapping[str, FieldValue]:
    """Preserve exact owned values and absent/null/false/empty distinctions."""
    return MappingProxyType(
        {
            key: FieldValue(Availability.NULL if value is None else Availability.VALUE, value)
            for key, value in properties.items()
            if key in const.OWNED_PROPERTIES
        }
    )


def _identity(properties: Mapping[str, object]) -> None:
    """Require an existing canonical UUID and the exact integer note schema."""
    identity = properties.get('obforce_id')
    try:
        valid = type(identity) is str and str(UUID(identity)) == identity
    except (ValueError, TypeError, AttributeError):
        valid = False
    if (
        not valid
        or type(properties.get('obforce_schema')) is not int
        or properties['obforce_schema'] != const.NOTE_SCHEMA_VERSION
    ):
        raise ConflictError('Managed identity or schema is invalid')


def parse_note(raw: bytes) -> ParsedNote:
    """Parse bounded caller-supplied bytes without discovery, adoption or I/O.

    :param raw: One UTF-8 managed note with an explicit supported envelope.
    :returns: Immutable observations, exact region and private round-trip spans.
    :raises ModelError: For a non-bytes caller input.
    :raises ConflictError: For malformed, unsafe, unsupported or excessive content.
    """
    if type(raw) is not bytes:
        raise ModelError('Managed-note input must be immutable bytes')
    if len(raw) > const.MAX_NOTE_BYTES:
        raise ConflictError('Managed note exceeds byte bound')
    try:
        raw.decode('utf-8')
    except UnicodeError:
        raise ConflictError('Managed note requires UTF-8') from None
    if b'\x00' in raw or b'\r' in raw.replace(b'\r\n', b''):
        raise ConflictError('Managed note contains unsupported controls')
    lines = raw.splitlines(keepends=True)
    if not lines or lines[0] not in (b'---\n', b'---\r\n'):
        raise ConflictError('Managed frontmatter boundary is invalid')
    closing = next((i for i in range(1, len(lines)) if lines[i] in (b'---\n', b'---\r\n')), None)
    if closing is None:
        raise ConflictError('Managed frontmatter boundary is invalid')
    front_start = len(lines[0])
    front_end = sum(map(len, lines[:closing]))
    envelope_end = front_end + len(lines[closing])
    if front_end - front_start > const.MAX_FRONTMATTER_BYTES:
        raise ConflictError('Frontmatter exceeds byte bound')
    _ending(raw[:envelope_end])
    front = raw[front_start:front_end].decode('utf-8')
    if any(c in front for c in ('\x85', '\u2028', '\u2029', '\ufeff')):
        raise ConflictError('Unsupported frontmatter character')
    markers = []
    offset = envelope_end
    for line in lines[closing + 1 :]:
        if b'obforce:' in line:
            if line not in tuple(m.encode() + e for m in (const.GENERATED_START, const.GENERATED_END) for e in (b'\n', b'\r\n')):
                raise ConflictError('Generated marker is malformed')
            markers.append((line, offset))
        offset += len(line)
    if (
        len(markers) != 2
        or not markers[0][0].startswith(const.GENERATED_START.encode())
        or not markers[1][0].startswith(const.GENERATED_END.encode())
        or b'obforce:' in raw[:envelope_end]
    ):
        raise ConflictError('Expected exactly one ordered generated marker pair')
    region_start = markers[0][1] + len(markers[0][0])
    region_end = markers[1][1]
    ending = _ending(raw[markers[0][1] : region_end + len(markers[1][0])])
    # Each envelope can have a different uniform convention; user prose is opaque.
    try:
        comments = _preflight(front)
        root = _yaml().compose(front)
        if not isinstance(root, MappingNode) or root.flow_style or len(root.value) > const.MAX_NOTE_PROPERTIES:
            raise ConflictError('Frontmatter requires a bounded block mapping')
        data = _yaml().load(front)
        properties, spans = {}, {}
        for key, node in root.value:
            if (
                not isinstance(key, ScalarNode)
                or key.tag != 'tag:yaml.org,2002:str'
                or key.start_mark.column != 0
                or key.end_mark.line != key.start_mark.line
                or key.value == '<<'
                or not key.value
                or len(key.value.encode()) > const.MAX_YAML_SCALAR_BYTES
            ):
                raise ConflictError('Unsupported YAML property key')
            name = key.value
            if name.startswith('sf_') and name not in const.OWNED_PROPERTIES:
                raise ConflictError('Unknown reserved Salesforce property')
            properties[name] = _value(node, data[name], owned=name in const.OWNED_PROPERTIES)
            spans[name] = (key.start_mark.index, node.start_mark.index, node.end_mark.index)
        _identity(properties)
    except (
        YAMLError,
        ValueError,
        TypeError,
        KeyError,
        RecursionError,
        OverflowError,
        AttributeError,
        IndexError,
        NotImplementedError,
    ):
        raise ConflictError('Invalid or unsupported managed frontmatter') from None
    return ParsedNote(
        raw,
        MappingProxyType(properties),
        _fields(properties),
        region_start,
        region_end,
        front_start,
        front_end,
        ending,
        front,
        MappingProxyType(spans),
        comments,
    )


def _candidate(candidate: GeneratedCandidate, state: NoteState) -> Mapping[str, FieldValue]:
    """Check the accepted generated-candidate shape without creation-template use."""
    if not isinstance(candidate, GeneratedCandidate):
        raise ModelError('Expected a generated candidate')
    try:
        if type(candidate.region) is not str or len(candidate.region) > const.MAX_RENDER_SECTION_BYTES:
            raise ModelError('Invalid generated region bound')
        _section_check(candidate.region, _GENERATED_HEADINGS)
        _frontmatter(candidate.properties)
        region = candidate.region.encode('utf-8')
        if (
            not region.endswith(b'\n')
            or b'\r' in region
            or b'\x00' in region
            or b'obforce:' in region
            or len(region) > const.MAX_RENDER_SECTION_BYTES
            or candidate.properties.keys() - const.OWNED_PROPERTIES
            or not {
                'obforce_id',
                'obforce_schema',
                'sf_type',
                'sf_full_name',
                'sf_namespace',
                'sf_source_mode',
                'sf_dependency_coverage',
                'sf_lifecycle',
            }
            <= candidate.properties.keys()
            or candidate.properties.get('sf_lifecycle') != 'active'
            or candidate.properties.get('sf_dependency_coverage') not in {status.value for status in CoverageStatus}
        ):
            raise ModelError('Invalid generated candidate')
        values = {}
        for key, value in candidate.properties.items():
            if value is not None and type(value) not in (str, bool, int, tuple):
                raise ModelError('Invalid generated property')
            if type(value) is int and value.bit_length() > 64:
                raise ModelError('Invalid generated integer')
            if type(value) is tuple and (len(value) > const.MAX_YAML_LIST_ITEMS or any(type(v) is not str for v in value)):
                raise ModelError('Invalid generated list')
            encoded = json.dumps(value, ensure_ascii=False)
            if len(encoded.encode()) > const.MAX_YAML_SCALAR_BYTES or 'obforce:' in encoded:
                raise ModelError('Invalid generated property bound')
            values[key] = value
        _identity(values)
        for digest in (candidate.source_hash, candidate.graph_hash, candidate.render_hash):
            if type(digest) is not str or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
                raise ModelError('Invalid generated fingerprint')
    except (ConfigError, UnicodeError, AttributeError, TypeError, ValueError):
        raise ModelError('Invalid generated candidate') from None
    if (
        values['obforce_id'] != state.obforce_id
        or values.get('sf_type') != state.key.metadata_type
        or values.get('sf_full_name') != state.key.full_name
        or values.get('sf_namespace') != state.key.namespace
        or values.get('sf_source_mode') != state.binding.mode
    ):
        raise ConflictError('Candidate identity does not match supplied state')
    return _fields(values)


def _retained_comments(note: ParsedNote, start: int, end: int, ending: str) -> str:
    """Keep comment text when an owned lexical span is replaced or removed."""
    result = []
    for left, right in note._comments:
        if start <= left < end:
            if right > end:
                raise ConflictError('Unsupported comment boundary')
            comment = note._front[left:right].rstrip(' \t')
            result.append(comment if comment.endswith('\n') else comment + ending)
    return ''.join(result)


def _patch_front(note: ParsedNote, incoming: Mapping[str, FieldValue]) -> bytes:
    """Splice owned source spans; never dump or recreate human YAML entries."""
    if note.generated_properties == incoming:
        return note.raw[note.front_start : note.front_end]
    text = note._front
    ending = _ending(note.raw[: note.front_end]).decode('ascii')
    edits = []
    for key, old in note.generated_properties.items():
        if key in incoming and old == incoming[key]:
            continue
        key_start, start, end = note._spans[key]
        if key not in incoming:
            edits.append((key_start, end, _retained_comments(note, key_start, end, ending)))
        else:
            value = incoming[key].value
            rendered = json.dumps(value, ensure_ascii=False, separators=(',', ':'))
            comments = _retained_comments(note, start, end, ending)
            terminal = ending if text[start:end].endswith('\n') or comments else ''
            # An implicit null can begin immediately after ':'.
            prefix = ' ' if start and not text[start - 1].isspace() else ''
            if start and text[start - 1] == '\n':
                prefix = '  '  # Indentless block sequence replaced by a scalar/flow list.
            edits.append((start, end, prefix + rendered + terminal + comments))
    for start, end, replacement in sorted(edits, reverse=True):
        text = text[:start] + replacement + text[end:]
    for key in sorted(incoming.keys() - note.generated_properties.keys()):
        text += json.dumps(key) + ': ' + json.dumps(incoming[key].value, ensure_ascii=False, separators=(',', ':')) + ending
    encoded = text.encode('utf-8')
    if len(encoded) > const.MAX_FRONTMATTER_BYTES:
        raise ConflictError('Patched frontmatter exceeds byte bound')
    return encoded


def patch_note(raw: bytes, state: NoteState, baseline_region: bytes, candidate: GeneratedCandidate) -> NotePatch:
    """Compare both saved baselines before constructing an in-memory candidate.

    :param raw: Current caller-supplied managed-note bytes.
    :param state: Already validated in-memory NoteState, never a state filename.
    :param baseline_region: Exact saved marker-interior bytes, independently of hashes.
    :param candidate: Accepted Thread 07 generated candidate; never a whole new note.
    :returns: Candidate bytes and exact output baselines; a no-op retains original bytes.
    :raises ConflictError: For edited/ambiguous managed content or excessive output.
    :raises ModelError: For invalid caller contracts.
    """
    if not isinstance(state, NoteState) or type(baseline_region) is not bytes:
        raise ModelError('Expected in-memory state and immutable baseline bytes')
    if len(baseline_region) > const.MAX_NOTE_BYTES:
        raise ModelError('Baseline exceeds byte bound')
    note = parse_note(raw)
    if (
        note.properties['obforce_id'] != state.obforce_id
        or note.generated_properties != state.generated_properties
        or hashlib.sha256(baseline_region).hexdigest() != state.generated_region_hash
        or note.region != baseline_region
    ):
        raise ConflictError('Managed content differs from saved baseline')
    if (
        note.properties.get('sf_type') != state.key.metadata_type
        or note.properties.get('sf_full_name') != state.key.full_name
        or note.properties.get('sf_namespace') != state.key.namespace
        or note.properties.get('sf_source_mode') != state.binding.mode
    ):
        raise ConflictError('Managed source identity does not match supplied state')
    incoming = _candidate(candidate, state)
    region = candidate.region.encode('utf-8').replace(b'\n', note.ending)
    front = _patch_front(note, incoming)
    content = raw[: note.front_start] + front + raw[note.front_end : note.region_start] + region + raw[note.region_end :]
    if content == raw:
        content = raw
    else:
        checked = parse_note(content)
        before = {k: v for k, v in note.properties.items() if k not in const.OWNED_PROPERTIES}
        after = {k: v for k, v in checked.properties.items() if k not in const.OWNED_PROPERTIES}
        if before != after or checked.generated_properties != incoming or checked.region != region:
            raise ConflictError('Candidate cannot preserve supported note structure')
    return NotePatch(
        content,
        incoming,
        region,
        hashlib.sha256(region).hexdigest(),
        candidate.source_hash,
        candidate.graph_hash,
        candidate.render_hash,
        content is not raw,
    )
