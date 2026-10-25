# -*- coding: utf-8 -*-
"""
:Module:            obforce.sync.engine
:Synopsis:          Orchestrates explicit initialization, initial build and local recovery
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     25 Oct 2026
"""

from __future__ import annotations

import json
import os
import stat
import tomllib
import unicodedata
from dataclasses import replace
from pathlib import Path

from obforce import constants as const
from obforce.config import Config, _resolve, parse_config, relative_path, select_source
from obforce.errors import ConfigError, ConflictError, ExitCode, ModelError, OperationalError
from obforce.graph.dependencies import DependencyGraph
from obforce.models import Coverage, Selection, SourceBinding, require_same_source
from obforce.renderer.templates import load_template
from obforce.sources import live, local, relationships
from obforce.sync.evidence import InventoryScope
from obforce.sync.planner import plan_changes
from obforce.sync.reporting import report_plan
from obforce.sync.state import _absolute, _Reader, parse_state, reconcile_vault
from obforce.sync.transactions import (
    TransactionInputs,
    TransactionResult,
    TransactionStatus,
    _contents,
    _control,
    _Guard,
    _listing,
    _lstat,
    _mkdir,
    _write_new,
    publish_plan,
    recover_transaction,
)


def _checkpoint(boundary: str) -> None:
    """Provide a synthetic setup fault boundary without production side effects."""


def _application() -> Path:
    """Derive the application boundary from installed code, never cwd or home."""
    package = Path(__file__).absolute().parents[1]
    return package.parent.parent if package.parent.name == 'src' else package


def _token(path: Path) -> str:
    return unicodedata.normalize('NFC', str(path)).casefold()


def _disjoint(left: Path, right: Path) -> None:
    a, b = _token(left), _token(right)
    if a == b or a.startswith(b + os.sep) or b.startswith(a + os.sep):
        raise ConflictError('Output overlaps a protected root')


def _path(raw: str, base: Path, reader: _Reader) -> Path:
    """Validate lexical ancestors before resolving config-relative root paths."""
    resolved = _resolve(raw, base)
    lexical = base / raw
    current = Path(lexical.anchor)
    for part in lexical.parts[1:]:
        current = current.parent if part == '..' else current / part
        info = reader.observe(current, missing=True)
        _spelling(current, reader)
        if current != resolved and info is not None and not stat.S_ISDIR(info.st_mode):
            raise ConflictError('Explicit path has a file parent')
    _absolute(resolved)
    if len(str(resolved)) > const.MAX_TRANSACTION_ABSOLUTE_CHARS:
        raise ConfigError('Explicit path exceeds setup bound')
    _observe_path(resolved, reader)
    return resolved


def _observe_path(path: Path, reader: _Reader) -> None:
    """Check safe ancestors and portable sibling aliases with bounded enumeration."""
    for item in (*reversed(path.parents), path):
        info = reader.observe(item, missing=True)
        if item != path and info is not None and not stat.S_ISDIR(info.st_mode):
            raise ConflictError('Explicit path has a file parent')
        # Existing roots such as /private/tmp may have platform-specific spelling;
        # only newly created path segments must satisfy portable output spelling.
        if info is None:
            relative_path(item.name)
        _spelling(item, reader)


def _spelling(path: Path, reader: _Reader) -> None:
    """Compare exact caller spelling before a native resolver can canonicalize it."""
    parent_info = reader.observe(path.parent, missing=True)
    if path == path.parent or parent_info is None:
        return
    names = []
    with os.scandir(path.parent) as entries:
        for entry in entries:
            if len(names) >= const.MAX_VAULT_ENTRIES:
                raise ConflictError('Setup ancestor exceeds entry bound')
            names.append(entry.name)
    for name in names:
        if _token(Path(name)) == _token(Path(path.name)) and name != path.name:
            raise ConflictError('Explicit path has a case or Unicode alias')


def _excluded(config: Config) -> tuple[Path, ...]:
    return tuple(p for p in (config.path, config.source.project, config.template_directory, _application()) if p is not None)


def _config(path: Path) -> tuple[Config, _Guard]:
    reader = _Reader()
    filename = _path(str(path), Path.cwd(), reader)
    info = reader.observe(filename, missing=True)
    if info is None:
        raise ConfigError('Explicit configuration file does not exist')
    if stat.S_ISREG(info.st_mode) and info.st_size > const.MAX_CONFIG_BYTES:
        raise ConfigError('Configuration exceeds size limit')
    raw = reader.read(filename, const.MAX_CONFIG_BYTES)
    config = parse_config(raw, filename)
    data = tomllib.loads(raw.decode('utf-8'))
    for value in (data['vault'], data['source'].get('project'), data.get('templates', {}).get('directory')):
        if value is not None:
            _path(value, filename.parent, reader)
    for root in _excluded(config):
        _disjoint(config.vault, root)
    reader.finish()
    return config, _Guard(reader.preconditions(), reader.file_stamps)


def initialize(
    path: Path, *, source: str | None, org: str | None, vault: str, workspace_id: str, preview: bool = False
) -> TransactionResult:
    """Validate explicit choices and exclusively create one new configuration.

    Root arguments are config-relative. The config parent must already exist;
    neither previews nor initialization acquire a source or create a vault.
    """
    SourceBinding(workspace_id, 'local')
    reader = _Reader()
    filename = _path(str(path), Path.cwd(), reader)
    reader.parents(filename)
    if reader.observe(filename, missing=True) is not None:
        raise ConflictError('Configuration destination already exists')
    if source is not None and org is not None:
        raise ConfigError('Source selectors are mutually exclusive')
    project = _path(source, filename.parent, reader) if source is not None else None
    selection = select_source(project=project, org=org)
    destination = _path(vault, filename.parent, reader)

    # JSON quoted strings are valid TOML basic strings; no interpolation of keys.
    def quote(value: str) -> str:
        return json.dumps(value, ensure_ascii=False)

    raw = (
        f'schema_version = 1\nworkspace_id = {quote(workspace_id)}\nvault = {quote(vault)}\n\n'
        f'[source]\nmode = {quote(selection.mode)}\n'
        + (f'project = {quote(source)}\n' if project is not None else f'org = {quote(org)}\n')
    ).encode('utf-8')
    config = parse_config(raw, filename)
    for root in _excluded(config):
        _disjoint(destination, root)
    _disjoint(filename, _application())
    reader.finish()
    guard = _Guard(reader.preconditions(), reader.file_stamps)
    guard.check()
    if preview:
        return TransactionResult(TransactionStatus.PREVIEW, ExitCode.SUCCESS, files=1)
    _checkpoint('config_ready')
    guard.change(lambda: _write_new(filename, raw), (filename,), data={filename: raw})
    _checkpoint('config_created')
    return TransactionResult(TransactionStatus.COMMITTED, ExitCode.SUCCESS, files=1)


def _empty(vault: Path, guard: _Guard) -> bool:
    """Refuse every existing entry, including history, control and user content."""
    guard.check()
    info = _lstat(vault)
    if info is not None:
        if not stat.S_ISDIR(info[2]) or _listing(vault):
            raise ConflictError('Initial build requires an absent or completely empty destination')
    guard.check()
    return info is not None


def _setup(vault: Path, guard: _Guard, created: list[Path]) -> None:
    for path in (*reversed(vault.parents), vault):
        if _lstat(path) is None:
            if len(created) >= const.MAX_SETUP_DIRECTORIES:
                raise ModelError('Initial setup exceeds directory bound')
            _mkdir(path, guard)
            created.append(path)
            _checkpoint('directory_created')


def _cleanup_setup(created: list[Path], guard: _Guard) -> None:
    """Remove only fully observed still-empty locally created setup directories."""
    for path in reversed(created):
        guard.check()
        if _listing(path):
            raise ConflictError('Setup contains retained output; explicit recovery or manual resolution required')
        guard.change(path.rmdir, (path,))


def _acquire(
    config: Config, org: str | None, executable: Path | None, directory: Path | None, state_binding: SourceBinding | None = None
):
    """Reuse accepted acquisition with explicit selection and independently checked org identity."""
    selection = Selection(include_namespaced=config.options.include_namespaced)
    source = select_source(config, org=org)
    if source.mode == 'local':
        if executable is not None or directory is not None:
            raise ConfigError('Offline build does not accept live process options')
        inventory = local.collect_local(source.project, SourceBinding(config.workspace_id, 'local'), selection)
        coverage = inventory.coverage
        graph = DependencyGraph(coverage.binding, coverage.selection, coverage.relationships)
    else:
        if executable is None or directory is None or not executable.is_absolute() or not directory.is_absolute():
            raise ConfigError('Live build requires explicit absolute executable and neutral directory')
        neutral = _Reader()
        _observe_path(directory, neutral)
        info = neutral.observe(directory)
        if not stat.S_ISDIR(info.st_mode):
            raise ConfigError('Live process directory must already exist')
        for root in (config.vault, *_excluded(config)):
            _disjoint(directory, root)
        neutral.finish()
        inventory = live.collect_live(
            executable,
            directory=directory,
            target=source.org,
            workspace_id=config.workspace_id,
            selection=selection,
            include_audit_names=config.options.include_audit_names,
            state_binding=state_binding,
        )
        collected = relationships.collect_relationships(executable, directory=directory, target=source.org, inventory=inventory)
        graph = collected.graph
        coverage = replace(inventory.coverage, relationships=graph.coverage)
    return inventory, coverage, graph


def _scope(coverage: Coverage, identifier: str | None) -> InventoryScope | None:
    if identifier is None:
        return None
    if coverage.binding.mode != 'live':
        raise ConfigError('Offline operations do not accept live scope declarations')
    try:
        return InventoryScope(identifier, coverage.inventory.method, coverage.inventory.api_version)
    except ConflictError:
        raise ConfigError('Invalid live inventory scope declaration') from None


def build(
    path: Path,
    *,
    preview: bool = False,
    org: str | None = None,
    executable: Path | None = None,
    directory: Path | None = None,
    inventory_scope_id: str | None = None,
) -> tuple[TransactionResult, str]:
    """Acquire explicit source facts and publish a first managed build only.

    No existing vault is adopted, resumed or refreshed. Missing destinations are
    planned read-only, then created under guards before independently replanning.
    """
    config, guard = _config(path)
    existed = _empty(config.vault, guard)
    if inventory_scope_id is not None and config.source.mode != 'live':
        raise ConfigError('Offline operations do not accept live scope declarations')
    if inventory_scope_id is not None:
        try:
            InventoryScope(inventory_scope_id, const.LIVE_APEX_METHOD, None)
        except ConflictError:
            raise ConfigError('Invalid live inventory scope declaration') from None
    inventory, coverage, graph = _acquire(config, org, executable, directory)
    scope = _scope(coverage, inventory_scope_id)
    generated = load_template('apex_generated.md.j2', config.template_directory)
    creation = load_template('apex_created.md.j2', config.template_directory)
    inputs = TransactionInputs(
        config.vault,
        config.vault / '.obforce/state.json',
        inventory.components,
        coverage,
        graph,
        _excluded(config),
        verified_org_id=coverage.binding.org_id,
        initial=True,
        persist_evidence=True,
        inventory_scope=scope,
        layout=config.layout,
        options=config.options,
        generated_template=generated,
        creation_template=creation,
    )
    guard.check()
    plan = plan_changes(**{name: getattr(inputs, name) for name in inputs.__dataclass_fields__}, allow_absent=not existed)
    if plan.blocked:
        return TransactionResult(TransactionStatus.BLOCKED, plan.outcome), f'Plan refused: {plan.diagnostic.value}\n'
    # Missing-destination previews enforce writer bounds without writer setup.
    entries, _ = _contents(config.vault, plan)
    parents = {parent for a in plan.actions for parent in Path(a.path).parents if str(parent) != '.'}
    if len(parents) > const.MAX_TRANSACTION_DIRECTORIES:
        raise ModelError('Initial plan exceeds directory bound')
    missing = [p for p in (*reversed(config.vault.parents), config.vault) if _lstat(p) is None]
    if len(missing) > const.MAX_SETUP_DIRECTORIES:
        raise ModelError('Initial setup exceeds directory bound')
    summary = (
        'Coverage: '
        + '; '.join(
            f'{name}={facet.status.value} (requested={str(facet.requested).lower()}, warnings={len(facet.warnings)})'
            for name in ('inventory', 'audit', 'relationships')
            for facet in (getattr(coverage, name),)
        )
        + '\n'
    )
    guard.check()
    if preview:
        _empty(config.vault, guard)
        return TransactionResult(TransactionStatus.PREVIEW, plan.outcome, files=len(entries)), summary
    created: list[Path] = []
    try:
        _checkpoint('setup_ready')
        _setup(config.vault, guard, created)
        _empty(config.vault, guard)
        fresh = inputs.plan()
        if fresh.blocked:
            failure = {ExitCode.INVALID: ModelError, ExitCode.CONFLICT: ConflictError}.get(fresh.outcome, OperationalError)
            raise failure('Initial candidate could not be revalidated after setup')
        if (fresh.actions, fresh.state_bytes, fresh.outcome) != (plan.actions, plan.state_bytes, plan.outcome):
            raise ConflictError('Initial candidate differs after guarded setup')
        guard.check()
        _checkpoint('publication_ready')
        _empty(config.vault, guard)
        result = publish_plan(fresh, inputs)
        # Publication intentionally changes the vault; setup guards must never
        # be refreshed from a failed/ambiguous publication to authorize cleanup.
        return _public_result(result), summary
    except (OperationalError, OSError):
        _cleanup_setup(created, guard)
        raise


def sync(
    path: Path,
    *,
    preview: bool = False,
    org: str | None = None,
    executable: Path | None = None,
    directory: Path | None = None,
    inventory_scope_id: str | None = None,
    attest_comparable_inventory: bool = False,
) -> tuple[TransactionResult, str]:
    """Refresh an explicitly selected existing managed vault through complete guarded plans."""
    config, config_guard = _config(path)
    source = select_source(config, org=org)
    if type(attest_comparable_inventory) is not bool:
        raise ConfigError('Invalid inventory attestation')
    if source.mode == 'local' and (inventory_scope_id is not None or attest_comparable_inventory):
        raise ConfigError('Offline operations do not accept live scope options')
    if attest_comparable_inventory and inventory_scope_id is None:
        raise ConfigError('Inventory attestation requires an explicit scope declaration')
    state_path = config.vault / '.obforce/state.json'
    reader = _Reader()
    reader.parents(state_path)
    if reader.observe(state_path, missing=True) is None:
        raise ConflictError('Existing managed state is required for refresh')
    saved = parse_state(reader.read(state_path, const.MAX_STATE_BYTES))
    if saved.evidence is None:
        raise ConflictError('Legacy state lacks required refresh evidence; no automatic migration')
    expected = SourceBinding(config.workspace_id, source.mode, saved.binding.org_id if source.mode == 'live' else None)
    require_same_source(saved.binding, expected)
    selection = Selection(include_namespaced=config.options.include_namespaced)
    if saved.selection != selection:
        raise ConflictError('Selected inventory scope changed')
    declared = saved.evidence.inventory_scope
    if inventory_scope_id is not None:
        # Validate syntax separately; a valid but different declaration is an ownership conflict.
        _scope(saved.coverage, inventory_scope_id)
        if declared is None or inventory_scope_id != declared.scope_id:
            raise ConflictError('Inventory scope declaration changed')
    _control(config.vault, pending=False)
    reconcile_vault(config.vault, state_path, saved.binding, selection, excluded_roots=_excluded(config))
    reader.finish()
    state_guard = _Guard(reader.preconditions(), reader.file_stamps)
    config_guard.check()
    inventory, coverage, graph = _acquire(config, org, executable, directory, saved.binding)
    if declared is not None and (
        declared.method != coverage.inventory.method or declared.api_version != coverage.inventory.api_version
    ):
        raise ConflictError('Inventory scope reference changed')
    state_guard.check()
    config_guard.check()
    inputs = TransactionInputs(
        config.vault,
        state_path,
        inventory.components,
        coverage,
        graph,
        _excluded(config),
        verified_org_id=coverage.binding.org_id,
        comparable_live_inventory=attest_comparable_inventory,
        persist_evidence=True,
        inventory_scope=declared,
        layout=config.layout,
        options=config.options,
        generated_template=load_template('apex_generated.md.j2', config.template_directory),
    )
    # Creation assets are irrelevant unless there are actually new components.
    if set(c.key for c in inventory.components) - {n.note.key for n in saved.notes}:
        inputs = replace(inputs, creation_template=load_template('apex_created.md.j2', config.template_directory))
    plan = inputs.plan()
    summary = report_plan(plan).text
    if coverage.binding.mode == 'live' and set(c.key for c in saved.evidence.components) - set(
        c.key for c in inventory.components
    ):
        summary += (
            'Missing evaluation: comparable inventory attested; completeness gates apply.\n'
            if attest_comparable_inventory
            else 'Missing evaluation: unavailable; prior lifecycle preserved.\n'
        )
    if plan.blocked:
        return TransactionResult(TransactionStatus.BLOCKED, plan.outcome), summary
    state_guard.check()
    config_guard.check()
    return _public_result(publish_plan(plan, inputs, preview=preview)), summary


def recover(path: Path, *, operation: str | None = None) -> TransactionResult:
    """Use only explicit config and local validated evidence, without acquisition."""
    config, guard = _config(path)
    guard.check()
    return _public_result(
        recover_transaction(
            config.vault,
            config.vault / '.obforce/state.json',
            excluded_roots=_excluded(config),
            preview=operation is None,
            operation=operation,
        )
    )


def _public_result(result: TransactionResult) -> TransactionResult:
    """Expose recovery-required refusal as conflict while retaining internal evidence."""
    if result.status == TransactionStatus.RECOVERY_REQUIRED:
        return replace(result, outcome=ExitCode.CONFLICT)
    return result
