# -*- coding: utf-8 -*-
"""
:Module:            obforce.sync.planner
:Synopsis:          Plans complete bounded read-only changes without publication
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     21 Oct 2026
"""

from __future__ import annotations

import stat
import unicodedata
from dataclasses import dataclass, replace
from enum import StrEnum
from pathlib import Path
from uuid import UUID, uuid5

from obforce import constants as const
from obforce.config import Layout, Options
from obforce.errors import ConflictError, ExitCode, ModelError, OperationalError, exit_code
from obforce.graph.dependencies import DependencyGraph, refresh_graph
from obforce.models import (
    Component,
    ComponentKey,
    Coverage,
    CoverageStatus,
    NoteState,
    canonical_json,
    require_same_source,
    validate_identities,
)
from obforce.renderer.notes import _bounded, _paths, note_paths, render_generated, render_new_note
from obforce.renderer.templates import TemplateAsset
from obforce.sync.notes import parse_note, patch_note
from obforce.sync.state import (
    ReadObservation,
    Reconciliation,
    SavedNote,
    StateDocument,
    _portable,
    _Reader,
    reconcile_vault,
    serialize_state,
)

_DEFAULT_LAYOUT = Layout()
_DEFAULT_OPTIONS = Options()


class ActionKind(StrEnum):
    """Describe one primary effect per component; moves never request a rename."""

    CREATE = 'create'
    UPDATE = 'update'
    NO_OP = 'no_op'
    MOVE = 'move'
    MISSING = 'missing'
    CONFLICT = 'conflict'


class Diagnostic(StrEnum):
    """Expose only fixed redacted failure categories, never upstream exception text."""

    CONFLICT = 'ownership_or_scope_conflict'
    INVALID = 'invalid_planner_input'
    READ = 'read_failed'


@dataclass(frozen=True, repr=False)
class ChangeAction:
    """Retain a private in-memory candidate and independent content/state effects."""

    kind: ActionKind
    key: ComponentKey | None = None
    identity: str | None = None
    path: str | None = None
    prior_path: str | None = None
    content_changed: bool = False
    state_changed: bool = False
    content: bytes | None = None
    saved: SavedNote | None = None
    creation_hash: str | None = None


@dataclass(frozen=True, repr=False)
class ChangePlan:
    """Return a complete candidate or a blocked result with no applyable subset.

    Candidate content/state/preconditions are private and must never be logged.
    A candidate does not provide a writer, a guard or an atomic filesystem snapshot.
    """

    actions: tuple[ChangeAction, ...]
    outcome: ExitCode
    blocked: bool
    coverage: Coverage | None = None
    diagnostic: Diagnostic | None = None
    state: StateDocument | None = None
    state_bytes: bytes | None = None
    state_changed: bool = False
    graph: DependencyGraph | None = None
    preconditions: tuple[ReadObservation, ...] = ()

    @property
    def counts(self) -> tuple[tuple[ActionKind, int], ...]:
        """Count primary actions in fixed display order, including zero counts."""
        return tuple((kind, sum(action.kind == kind for action in self.actions)) for kind in ActionKind)


def _blocked(error: OperationalError, coverage: Coverage | None) -> ChangePlan:
    code = ExitCode(error.exit_code)
    diagnostic = {ExitCode.CONFLICT: Diagnostic.CONFLICT, ExitCode.INVALID: Diagnostic.INVALID}.get(code, Diagnostic.READ)
    actions = (ChangeAction(ActionKind.CONFLICT),) if code == ExitCode.CONFLICT else ()
    outcome = exit_code((code, coverage.outcome if coverage is not None else ExitCode.SUCCESS))
    return ChangePlan(actions, outcome, True, coverage, diagnostic)


def _inputs(
    components: tuple[Component, ...],
    retained: tuple[Component, ...],
    coverage: Coverage,
    graph: DependencyGraph,
    previous: DependencyGraph | None,
    verified_org_id: str | None,
) -> None:
    """Validate finite explicit normalized data before any vault read."""
    if (
        type(components) is not tuple
        or type(retained) is not tuple
        or len(components) + len(retained) > const.MAX_PLAN_COMPONENTS
        or not all(isinstance(item, Component) for item in (*components, *retained))
        or not isinstance(coverage, Coverage)
        or not isinstance(graph, DependencyGraph)
        or (previous is not None and not isinstance(previous, DependencyGraph))
    ):
        raise ModelError('Expected bounded normalized planning inputs')
    binding, selection = coverage.binding, coverage.selection
    if (binding.mode == 'live' and verified_org_id != binding.org_id) or (
        binding.mode == 'local' and verified_org_id is not None
    ):
        raise ConflictError('Independent source verification does not match')
    validate_identities((*components, *retained))
    total = 0
    for component in (*components, *retained):
        require_same_source(binding, component.binding)
        if (component.key.namespace is not None and not selection.include_namespaced) or (
            selection.full_names and component.key.full_name not in selection.full_names
        ):
            raise ConflictError('Component lies outside selected scope')
        data = component.canonical()
        _bounded(data)
        total += len(canonical_json(data).encode('utf-8'))
        if total > const.MAX_PLAN_INPUT_BYTES:
            raise ModelError('Planning input exceeds aggregate bound')
    for item in (coverage.canonical(),):
        _bounded(item)
        total += len(canonical_json(item).encode('utf-8'))
    for snapshot in (graph, previous):
        if snapshot is None:
            continue
        require_same_source(binding, snapshot.binding)
        if snapshot.selection != selection or len(snapshot.edges) > const.MAX_GRAPH_EDGES:
            raise ConflictError('Graph scope does not match')
        if sum(len(edge.evidence) for edge in snapshot.edges) > const.MAX_GRAPH_OBSERVATIONS:
            raise ModelError('Graph exceeds evidence bound')
        header = {
            'binding': snapshot.binding.canonical(),
            'selection': snapshot.selection.canonical(),
            'coverage': snapshot.coverage.canonical(),
        }
        _bounded(header)
        total += len(canonical_json(header).encode('utf-8'))
        for edge in snapshot.edges:
            data = edge.canonical()
            _bounded(data)
            total += len(canonical_json(data).encode('utf-8'))
            if total > const.MAX_PLAN_INPUT_BYTES:
                raise ModelError('Planning input exceeds aggregate bound')
    if graph.coverage != coverage.relationships:
        raise ConflictError('Independent graph coverage does not match')
    if binding.mode == 'local' and (graph.edges or (previous is not None and previous.edges)):
        raise ConflictError('Offline graph must remain uncollected')
    if (
        binding.mode == 'live'
        and coverage.relationships.requested
        and coverage.relationships.status not in {CoverageStatus.PARTIAL, CoverageStatus.UNAVAILABLE}
    ):
        raise ConflictError('Platform relationships cannot prove exhaustion')
    if total > const.MAX_PLAN_INPUT_BYTES:
        raise ModelError('Planning input exceeds aggregate bound')


def _reader(result: Reconciliation) -> _Reader:
    reader = _Reader()
    reader.snapshots.update((item.path, item.stamp) for item in result.preconditions)
    reader.digests.update((item.path, item.content_hash) for item in result.preconditions if item.content_hash is not None)
    return reader


def _targets(
    vault: Path, paths: dict[ComponentKey, str], existing: dict[ComponentKey, SavedNote], reader: _Reader, result: Reconciliation
) -> None:
    """Validate proposed and observed portable occupancy together, without creating parents."""
    locations = {}
    for path, stamp in reader.snapshots.items():
        if path == vault or not path.is_relative_to(vault):
            continue
        relative = path.relative_to(vault).as_posix()
        if any(part.casefold() in const.CONTROL_DIRECTORIES for part in path.relative_to(vault).parts):
            continue
        token = _portable(relative)
        if stamp is not None:
            locations[token] = (relative, stamp)
    for key, relative in paths.items():
        parts = relative.split('/')
        for index in range(1, len(parts) + 1):
            spelling = '/'.join(parts[:index])
            entry = locations.get(_portable(spelling))
            leaf = index == len(parts)
            if entry is not None:
                observed, stamp = entry
                if observed != spelling or (not leaf and not stat.S_ISDIR(stamp[2])):
                    raise ConflictError('Proposed path has an ambiguous or occupied parent')
                if leaf and (key not in existing or existing[key].note.path != spelling):
                    raise ConflictError('Proposed target is occupied by unowned content')
            info = reader.observe(vault / spelling, missing=True)
            if info is not None and leaf and key not in existing:
                raise ConflictError('New target appeared during planning')
            if info is not None and not leaf and not stat.S_ISDIR(info.st_mode):
                raise ConflictError('Proposed parent is not a directory')
    for change in result.path_changes:
        if unicodedata.normalize('NFC', change.old_path).casefold() != unicodedata.normalize('NFC', change.new_path).casefold():
            for index in range(1, len(change.old_path.split('/')) + 1):
                reader.observe(vault / '/'.join(change.old_path.split('/')[:index]), missing=True)
    if len(reader.snapshots) > const.MAX_PLAN_PRECONDITIONS:
        raise ModelError('Planning observation limit exceeded')


def _prior(
    result: Reconciliation,
    retained: tuple[Component, ...],
    current: dict[ComponentKey, Component],
    previous_graph: DependencyGraph | None,
) -> dict[ComponentKey, SavedNote]:
    existing = {saved.note.key: saved for saved in result.state.notes} if result.state is not None else {}
    if {component.key for component in retained} != existing.keys() - current.keys():
        raise ConflictError('Absent tracked components require exact retained source facts')
    for component in retained:
        if component.source_hash != existing[component.key].note.source_hash:
            raise ConflictError('Retained facts differ from saved source fingerprint')
    if existing:
        if previous_graph is None or previous_graph.coverage != result.state.coverage.relationships:
            raise ConflictError('Existing notes require their saved graph evidence')
        old_paths = dict(result.paths)
        old_paths.update((change.key, change.old_path) for change in result.path_changes)
        for saved in existing.values():
            if previous_graph.note_fingerprint(saved.note.key, old_paths) != saved.note.graph_hash:
                raise ConflictError('Prior graph differs from saved fingerprint')
    return existing


def _complete_absence(coverage: Coverage, result: Reconciliation, comparable: bool) -> bool:
    inventory = coverage.inventory
    return bool(
        comparable
        and coverage.binding.mode == 'live'
        and result.state is not None
        and inventory.status == CoverageStatus.COMPLETE
        and inventory.pagination == 'exhausted'
        and inventory.limit_reached is False
        and not inventory.warnings
        and inventory.method == const.LIVE_APEX_METHOD
        and result.state.coverage.inventory.method == inventory.method
        and result.state.coverage.inventory.api_version == inventory.api_version
    )


def _actions(
    components: dict[ComponentKey, Component],
    observed: set[ComponentKey],
    coverage: Coverage,
    graph: DependencyGraph,
    existing: dict[ComponentKey, SavedNote],
    paths: dict[ComponentKey, str],
    result: Reconciliation,
    *,
    layout: Layout,
    options: Options,
    generated_template: TemplateAsset | None,
    creation_template: TemplateAsset | None,
    comparable: bool,
) -> tuple[ChangeAction, ...]:
    actions, total = [], 0
    moved = {change.key: change.old_path for change in result.path_changes}
    absence = _complete_absence(coverage, result, comparable)
    for key in sorted(components, key=lambda item: item.token):
        component, prior = components[key], existing.get(key)
        identity = (
            prior.note.obforce_id
            if prior is not None
            else str(
                uuid5(
                    UUID(const.PLANNER_UUID_NAMESPACE),
                    canonical_json({'binding': component.binding.canonical(), 'key': key.canonical()}),
                )
            )
        )
        creation_hash = None
        if prior is None:
            new = render_new_note(
                component,
                coverage,
                graph,
                identity=identity,
                managed_paths=paths,
                layout=layout,
                options=options,
                generated_template=generated_template,
                creation_template=creation_template,
            )
            content, generated, creation_hash = new.text.encode('utf-8'), new.generated, new.creation_hash
            parsed = parse_note(content)
            note = NoteState(
                identity,
                component.binding,
                key,
                paths[key],
                generated.source_hash,
                generated.graph_hash,
                generated.render_hash,
                parsed.generated_properties,
                parsed.region_hash,
            )
            saved = SavedNote(note, parsed.region)
            kind, content_changed, state_changed = ActionKind.CREATE, True, True
        else:
            generated = render_generated(
                component,
                coverage,
                graph,
                identity=identity,
                managed_paths=paths,
                layout=layout,
                options=options,
                template=generated_template,
            )
            lifecycle = (
                'active' if key in observed else ('missing' if absence else prior.note.generated_properties['sf_lifecycle'].value)
            )
            generated = replace(generated, properties={**generated.properties, 'sf_lifecycle': lifecycle})
            patch = patch_note(result.observations[identity].raw, prior.note, prior.generated_region, generated)
            note = replace(
                prior.note,
                source_hash=patch.source_hash,
                graph_hash=patch.graph_hash,
                render_hash=patch.render_hash,
                generated_properties=patch.generated_properties,
                generated_region_hash=patch.generated_region_hash,
            )
            saved = SavedNote(note, patch.generated_region)
            content, content_changed = patch.content, patch.changed
            state_changed = saved != prior or key in moved
            became_missing = lifecycle == 'missing' and prior.note.generated_properties['sf_lifecycle'].value != 'missing'
            kind = (
                ActionKind.MOVE
                if key in moved
                else ActionKind.MISSING
                if became_missing
                else ActionKind.UPDATE
                if content_changed or state_changed
                else ActionKind.NO_OP
            )
        total += len(content)
        if total > const.MAX_PLAN_OUTPUT_BYTES or len(actions) >= const.MAX_PLAN_ACTIONS:
            raise ModelError('Plan output exceeds finite bound')
        actions.append(
            ChangeAction(
                kind, key, identity, paths[key], moved.get(key), content_changed, state_changed, content, saved, creation_hash
            )
        )
    validate_identities((), (action.saved.note for action in actions))
    return tuple(actions)


def plan_changes(
    vault: Path,
    state_path: Path,
    components: tuple[Component, ...],
    coverage: Coverage,
    graph: DependencyGraph,
    *,
    excluded_roots: tuple[Path, ...],
    retained_components: tuple[Component, ...] = (),
    previous_graph: DependencyGraph | None = None,
    verified_org_id: str | None = None,
    comparable_live_inventory: bool = False,
    initial: bool = False,
    allow_absent: bool = False,
    layout: Layout = _DEFAULT_LAYOUT,
    options: Options = _DEFAULT_OPTIONS,
    generated_template: TemplateAsset | None = None,
    creation_template: TemplateAsset | None = None,
) -> ChangePlan:
    """Preflight a complete deterministic candidate without filesystem publication.

    :param components: Explicit current normalized inventory, independent of coverage.
    :param retained_components: Exactly absent tracked keys, matching saved source hashes.
    :param previous_graph: Saved evidence matching prior per-note graph hashes and paths.
    :param verified_org_id: Independently verified current org ID; never discovered here.
    :param comparable_live_inventory: Caller attests unchanged accessible inventory scope.
    :returns: Complete private candidates/preconditions, or a redacted typed blocked result.
    """
    safe_coverage = coverage if isinstance(coverage, Coverage) else None
    try:
        _inputs(components, retained_components, coverage, graph, previous_graph, verified_org_id)
        if type(comparable_live_inventory) is not bool or not isinstance(layout, Layout) or not isinstance(options, Options):
            raise ModelError('Invalid planner options')
        if options.include_namespaced != coverage.selection.include_namespaced:
            raise ConflictError('Options disagree with selected scope')
        # Validate independent offline dimensions even for an empty initial inventory.
        StateDocument(coverage.binding, coverage.selection, coverage)
        result = reconcile_vault(
            vault,
            state_path,
            coverage.binding,
            coverage.selection,
            excluded_roots=excluded_roots,
            initial=initial,
            allow_absent=allow_absent,
        )
        current = {component.key: component for component in components}
        existing = _prior(result, retained_components, current, previous_graph)
        all_components = {**current, **{component.key: component for component in retained_components}}
        fresh_paths = note_paths(tuple(component for key, component in current.items() if key not in existing), layout)
        paths = _paths({**dict(result.paths), **fresh_paths})
        reader = _reader(result)
        _targets(vault, paths, existing, reader, result)
        refreshed = refresh_graph(graph, previous_graph)
        actions = _actions(
            all_components,
            set(current),
            coverage,
            refreshed,
            existing,
            paths,
            result,
            layout=layout,
            options=options,
            generated_template=generated_template,
            creation_template=creation_template,
            comparable=comparable_live_inventory,
        )
        candidate = StateDocument(coverage.binding, coverage.selection, coverage, tuple(action.saved for action in actions))
        wire = serialize_state(candidate)
        changed = result.state is None or bool(result.path_changes) or candidate.canonical() != result.state.canonical()
        if not changed:
            wire = result.state_bytes
        if sum(len(action.content) for action in actions) + len(wire) > const.MAX_PLAN_OUTPUT_BYTES:
            raise ModelError('Aggregate plan output exceeds bound')
        reader.finish()
        return ChangePlan(
            actions,
            coverage.outcome,
            False,
            coverage,
            state=candidate,
            state_bytes=wire,
            state_changed=changed,
            graph=refreshed,
            preconditions=reader.preconditions(),
        )
    except OperationalError as error:
        return _blocked(error, safe_coverage)
    except OSError:
        return _blocked(OperationalError('Cannot complete read-only planning'), safe_coverage)
    except (UnicodeError, TypeError, ValueError, AttributeError, RecursionError):
        return _blocked(ModelError('Invalid planning data'), safe_coverage)
