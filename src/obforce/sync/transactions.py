# -*- coding: utf-8 -*-
"""
:Module:            obforce.sync.transactions
:Synopsis:          Provides bounded internal publication and conservative recovery primitives
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     21 Oct 2026
"""

from __future__ import annotations

import errno
import hashlib
import json
import os
import stat
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from uuid import UUID, uuid4

from obforce import constants as const
from obforce.config import Layout, Options
from obforce.errors import ConflictError, ExitCode, ModelError, OperationalError, exit_code
from obforce.graph.dependencies import DependencyGraph
from obforce.models import Component, Coverage, canonical_json
from obforce.renderer.notes import GeneratedCandidate, _path
from obforce.renderer.templates import TemplateAsset
from obforce.sync.notes import parse_note, patch_note
from obforce.sync.planner import ChangePlan, plan_changes
from obforce.sync.state import (
    ReadObservation,
    _absolute,
    _cross_api_stamp,
    _pairs,
    _portable,
    _Reader,
    _safe,
    _stamp,
    parse_state,
)

_PHASES = frozenset({'preparing', 'ready', 'publishing', 'committed', 'rolling_back', 'rolled_back', 'cleaning'})
_ROOT_KEYS = frozenset(
    {
        'journal_schema',
        'transaction_id',
        'lock_token',
        'vault_identity',
        'control_identity',
        'phase',
        'entries',
        'directories',
        'guards',
        'work_stamp',
        'file_guards',
    }
)
_ENTRY_KEYS = frozenset({'path', 'before', 'after', 'original', 'published', 'restored', 'transfer', 'intent'})
_BLOB_KEYS = frozenset({'size', 'hash', 'stamp', 'removed'})
_CONTROL_NAMES = frozenset({'state.json', 'writer.lock', 'journal.json', 'transaction'})


class TransactionStatus(StrEnum):
    """Expose fixed redacted outcomes independently of private on-disk evidence."""

    PREVIEW = 'preview'
    NO_OP = 'no_op'
    COMMITTED = 'committed'
    ROLLED_BACK = 'rolled_back'
    CLEANED = 'cleaned'
    BLOCKED = 'blocked'
    RECOVERY_REQUIRED = 'recovery_required'


@dataclass(frozen=True)
class TransactionResult:
    """Return a small safe report without printing private evidence or exception text."""

    status: TransactionStatus
    outcome: ExitCode
    recovery_required: bool = False
    files: int = 0

    def __post_init__(self) -> None:
        if (
            not isinstance(self.status, TransactionStatus)
            or not isinstance(self.outcome, ExitCode)
            or type(self.recovery_required) is not bool
            or type(self.files) is not int
            or not 0 <= self.files <= const.MAX_TRANSACTION_FILES
        ):
            raise ModelError('Invalid bounded transaction result')

    @property
    def text(self) -> str:
        """Format only fixed categories and bounded counts."""
        result = (
            f'Transaction: {self.status.value}; outcome: {int(self.outcome)}; '
            f'files: {self.files}; recovery_required: {str(self.recovery_required).lower()}\n'
        )
        if len(result.encode()) > const.MAX_TRANSACTION_REPORT_BYTES:
            raise ModelError('Transaction report exceeds bound')
        return result


@dataclass(frozen=True, repr=False)
class TransactionInputs:
    """Retain explicit transient planner inputs; never acquire sources or discover paths.

    The independently regenerated candidate and the supplied plan must agree.
    Prior graph evidence remains in memory; nothing extends the accepted state wire.
    """

    vault: Path
    state_path: Path
    components: tuple[Component, ...]
    coverage: Coverage
    graph: DependencyGraph
    excluded_roots: tuple[Path, ...]
    retained_components: tuple[Component, ...] = ()
    previous_graph: DependencyGraph | None = None
    verified_org_id: str | None = None
    comparable_live_inventory: bool = False
    initial: bool = False
    layout: Layout = field(default_factory=Layout)
    options: Options = field(default_factory=Options)
    generated_template: TemplateAsset | None = None
    creation_template: TemplateAsset | None = None

    def plan(self) -> ChangePlan:
        """Re-evaluate explicit accepted read-only planning inputs."""
        return plan_changes(**{name: getattr(self, name) for name in self.__dataclass_fields__})


def _checkpoint(boundary: str, index: int = -1) -> None:
    """Provide an internal synthetic fault boundary, with no runtime callback input."""


def _hash(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _identity(stamp: tuple[int, ...] | list[int]) -> tuple[int, ...]:
    return tuple(stamp[:3])


def _lstat(path: Path) -> tuple[int, ...] | None:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None
    _safe(info)
    return _stamp(info)


def _listing(path: Path) -> dict[str, tuple[int, ...]]:
    result = {}
    with os.scandir(path) as entries:
        for entry in entries:
            if len(result) >= const.MAX_VAULT_ENTRIES:
                raise ConflictError('Directory entry bound exceeded')
            result[entry.name] = _lstat(path / entry.name)
    if any(value is None for value in result.values()):
        raise ConflictError('Directory entry vanished')
    return result


def _sync_directory(path: Path) -> None:
    """Request POSIX directory durability; Windows has no portable equivalent here."""
    if os.name != 'nt':
        flags = os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0) | getattr(os, 'O_NOFOLLOW', 0)
        descriptor = os.open(path, flags)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)


class _Guard:
    """Recheck full observations and accept only exact named directory-entry deltas."""

    def __init__(self, observations: tuple[ReadObservation, ...], file_stamps: dict[Path, tuple[int, ...]] | None = None) -> None:
        self.stamps = {item.path: item.stamp for item in observations}
        self.hashes = {item.path: item.content_hash for item in observations if item.content_hash is not None}
        self.owner: _Lock | None = None
        self.file_stamps = dict(file_stamps or {})

    def check(self) -> None:
        reader = _Reader()
        reader.snapshots.update(self.stamps)
        reader.file_stamps.update(self.file_stamps)
        for path, digest in self.hashes.items():
            if self.owner is not None and path == self.owner.path:
                raw = self.owner.read()
                stamp = _stamp(self.owner._observation)
                if path in reader.file_stamps and reader.file_stamps[path] != stamp:
                    raise ConflictError('Historical lock descriptor changed')
                reader.file_stamps[path] = stamp
            else:
                raw = reader.read(path, max(const.MAX_STATE_BYTES, const.MAX_JOURNAL_BYTES))
            if os.name == 'nt' and reader.file_stamps[path][-1] <= 0:
                raise ConflictError('Required descriptor change time is unavailable')
            if _hash(raw) != digest:
                raise ConflictError('Observed bytes changed')
        reader.finish()
        self.file_stamps.update(reader.file_stamps)

    def observe(self, path: Path, raw: bytes | None = None) -> None:
        stamp = _lstat(path)
        if path in self.stamps and stamp != self.stamps[path]:
            raise ConflictError('Observed identity changed')
        self.stamps[path] = stamp
        if raw is not None:
            self.hashes[path] = _hash(raw)

    def change(self, operation: Callable[[], None], paths: tuple[Path, ...], *, data: dict[Path, bytes] | None = None) -> None:
        self.check()
        parents = {path.parent for path in paths}
        before = {parent: _listing(parent) for parent in parents}
        prior = {parent: _lstat(parent) for parent in parents}
        operation()
        _checkpoint('mutation')
        changed = set(paths) | parents
        updates = {path: _lstat(path) for path in changed}
        for parent in parents:
            after = _listing(parent)
            allowed = {path.name for path in paths if path.parent == parent}
            allowed.update(path.name for path in parents if path.parent == parent)
            left, right = before[parent], after
            if _identity(prior[parent]) != _identity(updates[parent]) or (
                {name: stamp for name, stamp in left.items() if name not in allowed}
                != {name: stamp for name, stamp in right.items() if name not in allowed}
            ):
                raise ConflictError('Unexpected transaction parent change')
            delta = sum(stat.S_ISDIR(s[2]) for s in right.values()) - sum(stat.S_ISDIR(s[2]) for s in left.values())
            link_delta = updates[parent][3] - prior[parent][3]
            entry_model = prior[parent][3] == 2 + len(left) and updates[parent][3] == 2 + len(right)
            if (os.name == 'nt' and link_delta != 0) or (os.name != 'nt' and link_delta != delta and not entry_model):
                raise ConflictError('Unexpected parent link count')
        for path, expected in self.stamps.items():
            if path not in changed and _lstat(path) != expected:
                raise ConflictError('Unrelated observation changed')
        self.stamps.update(updates)
        for path in paths:
            self.hashes.pop(path, None)
            self.file_stamps.pop(path, None)
        if data:
            self.hashes.update((path, _hash(raw)) for path, raw in data.items())
        self.check()
        for parent in parents:
            _sync_directory(parent)


def _write_new(path: Path, raw: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_BINARY', 0)
    descriptor = os.open(path, flags, 0o600)
    with os.fdopen(descriptor, 'wb') as stream:
        _checkpoint('file_open')
        stream.write(raw)
        stream.flush()
        _checkpoint('file_flush')
        os.fsync(stream.fileno())
        _checkpoint('file_sync')


class _Lock:
    """Hold a persistent validated inode with a nonblocking process-lifetime kernel lock."""

    def __init__(self, control: Path, guard: _Guard) -> None:
        self.path, self.guard, self.descriptor = control / 'writer.lock', guard, None
        self.token = None
        self._observation = None
        self._raw = None

    def __enter__(self) -> _Lock:
        guard, path = self.guard, self.path
        if guard.owner is not None:
            raise ConflictError('Writer guard already has an owning descriptor')
        if _lstat(path) is None:
            raw = ('obforce-lock-v1 ' + str(uuid4()) + '\n').encode('ascii')
            guard.change(lambda: _write_new(path, raw), (path,), data={path: raw})
        guard.observe(path)
        guard.check()
        flags = os.O_RDWR | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NONBLOCK', 0)
        descriptor = os.open(path, flags)
        try:
            info = os.fstat(descriptor)
            _safe(info)
            if _cross_api_stamp(path.lstat()) != _cross_api_stamp(info):
                raise ConflictError('Lock descriptor mismatch')
            if os.name == 'nt':
                import msvcrt

                try:
                    msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
                except OSError as error:
                    if error.errno in {errno.EACCES, errno.EAGAIN, errno.EDEADLK}:
                        raise ConflictError('Another writer holds the guard') from None
                    raise
            else:
                import fcntl

                try:
                    fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except OSError as error:
                    if error.errno in {errno.EACCES, errno.EAGAIN}:
                        raise ConflictError('Another writer holds the guard') from None
                    raise
            raw = os.read(descriptor, 128)
            if len(raw) != 53 or not raw.startswith(b'obforce-lock-v1 ') or raw[-1:] != b'\n':
                raise ConflictError('Invalid persistent lock')
            token = raw[16:-1].decode('ascii')
            after = os.fstat(descriptor)
            _safe(after)
            if str(UUID(token)) != token or _stamp(info) != _stamp(after) or _cross_api_stamp(info) != _cross_api_stamp(after):
                raise ConflictError('Lock ownership changed')
            self.descriptor, self.token = descriptor, token
            self._observation, self._raw = info, raw
            guard.owner = self
            guard.observe(path, raw)
            guard.check()
            _checkpoint('lock')
        except BaseException:
            if guard.owner is self:
                guard.owner = None
            self.descriptor = None
            os.close(descriptor)
            raise
        return self

    def read(self) -> bytes:
        """Validate lock bytes through the continuously held owning descriptor.

        Windows denies another handle access to our locked byte. This is not a
        read exemption: exact bytes, full same-API stamps and cross-API birthtime
        identity must still agree before and after every bounded descriptor read.
        """
        if self.descriptor is None or self.guard.owner is not self or self._observation is None:
            raise ConflictError('Writer guard descriptor is not owned')
        path_before = self.path.lstat()
        before = os.fstat(self.descriptor)
        _safe(path_before)
        _safe(before)
        if (
            _stamp(path_before) != self.guard.stamps[self.path]
            or _stamp(before) != _stamp(self._observation)
            or _cross_api_stamp(before) != _cross_api_stamp(self._observation)
            or _cross_api_stamp(path_before) != _cross_api_stamp(before)
        ):
            raise ConflictError('Writer guard observation changed')
        os.lseek(self.descriptor, 0, os.SEEK_SET)
        raw = os.read(self.descriptor, 128)
        after, path_after = os.fstat(self.descriptor), self.path.lstat()
        _safe(after)
        _safe(path_after)
        if (
            raw != self._raw
            or _stamp(before) != _stamp(after)
            or _cross_api_stamp(before) != _cross_api_stamp(after)
            or _stamp(path_before) != _stamp(path_after)
            or _cross_api_stamp(path_after) != _cross_api_stamp(after)
        ):
            raise ConflictError('Writer guard bytes or identity changed')
        return raw

    def __exit__(self, *args: object) -> None:
        if self.guard.owner is self:
            self.guard.owner = None
        descriptor, self.descriptor = self.descriptor, None
        os.close(descriptor)


def _roots(vault: Path, state_path: Path, excluded_roots: tuple[Path, ...]) -> _Reader:
    _absolute(vault)
    _absolute(state_path)
    if state_path != vault / '.obforce/state.json' or len(str(vault)) > const.MAX_TRANSACTION_ABSOLUTE_CHARS:
        raise ModelError('Invalid explicit transaction paths')
    if type(excluded_roots) is not tuple or len(excluded_roots) > 128:
        raise ModelError('Invalid explicit excluded roots')
    reader = _Reader()
    reader.parents(vault)
    info = reader.observe(vault)
    if not stat.S_ISDIR(info.st_mode):
        raise ConflictError('Vault is not an existing directory')
    for root in excluded_roots:
        _absolute(root)
        left, right = str(root).casefold(), str(vault).casefold()
        import unicodedata

        left, right = unicodedata.normalize('NFC', left), unicodedata.normalize('NFC', right)
        if left == right or left.startswith(right + os.sep) or right.startswith(left + os.sep):
            raise ConflictError('Transaction paths overlap an excluded root')
        for parent in (*reversed(root.parents), root):
            if reader.observe(parent, missing=True) is None:
                break
    reader.finish()
    return reader


def _control(vault: Path, *, pending: bool) -> None:
    path = vault / '.obforce'
    stamp = _lstat(path)
    if stamp is None:
        return
    if not stat.S_ISDIR(stamp[2]):
        raise ConflictError('Invalid control directory')
    names = _listing(path).keys()
    allowed = _CONTROL_NAMES if pending else {'state.json', 'writer.lock'}
    if names - allowed:
        raise ConflictError('Recovery evidence or unknown control entry exists')
    if not pending and any(name in names for name in ('journal.json', 'transaction')):
        raise ConflictError('Incomplete transaction blocks ordinary writes')


def _validated(plan: ChangePlan, inputs: TransactionInputs) -> ChangePlan:
    if not isinstance(inputs, TransactionInputs) or not isinstance(plan, ChangePlan):
        raise ModelError('Expected explicit plan and transaction inputs')
    _roots(inputs.vault, inputs.state_path, inputs.excluded_roots)
    if plan.blocked or plan.diagnostic is not None:
        raise ConflictError('Blocked candidate is not publication authority')
    fresh = inputs.plan()
    if fresh.blocked:
        error = {ExitCode.CONFLICT: ConflictError, ExitCode.INVALID: ModelError}.get(fresh.outcome, OperationalError)
        raise error('Cannot independently validate candidate')
    if fresh != plan:
        raise ConflictError('Candidate or complete observations do not match')
    if len(plan.preconditions) > const.MAX_TRANSACTION_GUARDS:
        raise ModelError('Transaction exceeds finite file or observation bound')
    return fresh


def _blob(raw: bytes | None, stamp: tuple[int, ...] | None = None) -> dict | None:
    return None if raw is None else {'size': len(raw), 'hash': _hash(raw), 'stamp': stamp, 'removed': False}


def _guards(guard: _Guard, vault: Path) -> list[dict]:
    items = []
    for path, stamp in sorted(guard.stamps.items()):
        if path.is_relative_to(vault) and not path.is_relative_to(vault / '.obforce'):
            items.append({'path': path.relative_to(vault).as_posix(), 'stamp': stamp, 'hash': guard.hashes.get(path)})
    if len(items) > const.MAX_TRANSACTION_GUARDS:
        raise ModelError('Journal observation bound exceeded')
    return items


def _save(journal: dict, vault: Path, guard: _Guard, *, first: bool = False) -> None:
    for record in journal['directories']:
        if record['stamp'] is not None and not record['removed']:
            current = guard.stamps.get(vault / record['path'])
            if current is None or _identity(current) != _identity(record['stamp']):
                raise ConflictError('Created directory identity changed')
            record['stamp'] = current
    journal['guards'] = _guards(guard, vault)
    if any(vault / relative not in guard.file_stamps for relative in _expected_files(journal)):
        raise ConflictError('Missing historical descriptor observation')
    journal['file_guards'] = [
        {'path': relative, 'stamp': guard.file_stamps[vault / relative]} for relative in sorted(_expected_files(journal))
    ]
    work = vault / '.obforce/transaction'
    journal['work_stamp'] = _lstat(work)
    raw = (canonical_json(journal) + '\n').encode('utf-8')
    if len(raw) > const.MAX_JOURNAL_BYTES:
        raise ModelError('Journal exceeds finite byte bound')
    _decode_journal(raw)
    target, temporary = vault / '.obforce/journal.json', vault / '.obforce/journal.next'
    if first:
        guard.change(lambda: _write_new(target, raw), (target,), data={target: raw})
    else:
        guard.observe(temporary)
        if guard.stamps[temporary] is not None:
            raise ConflictError('Unowned journal temporary exists')
        guard.change(lambda: _write_new(temporary, raw), (temporary,), data={temporary: raw})
        _checkpoint('journal_next')
        guard.change(lambda: os.replace(temporary, target), (temporary, target), data={target: raw})
    _checkpoint('journal')


def _contents(vault: Path, plan: ChangePlan) -> tuple[list[dict], list[tuple[bytes | None, bytes]]]:
    entries, contents, total = [], [], 0
    changed = [(a.path, a.content) for a in plan.actions if a.content_changed]
    if plan.state_changed:
        changed.append(('.obforce/state.json', plan.state_bytes))
    for relative, after in changed:
        reader = _Reader()
        target = vault / relative
        before_stamp = _lstat(target)
        before = reader.read(target, const.MAX_STATE_BYTES) if before_stamp is not None else None
        reader.finish()
        if type(after) is not bytes:
            raise ModelError('Invalid complete candidate bytes')
        entries.append(
            {
                'path': relative,
                'before': _blob(before),
                'after': _blob(after),
                'original': before_stamp,
                'published': None,
                'restored': None,
                'transfer': None,
                'intent': None,
            }
        )
        if before_stamp is not None and before_stamp[0] != _lstat(vault)[0]:
            raise ConflictError('Target is not on the vault filesystem')
        contents.append((before, after))
        total += len(after) + (len(before) if before is not None else 0)
    if len(entries) > const.MAX_TRANSACTION_FILES or total > const.MAX_TRANSACTION_BYTES:
        raise ModelError('Transaction exceeds aggregate bound')
    return entries, contents


def _mkdir(path: Path, guard: _Guard) -> None:
    if _lstat(path) is not None:
        raise ConflictError('New directory target is occupied')
    guard.change(lambda: path.mkdir(mode=0o700), (path,))


def _stage(journal: dict, contents: list[tuple[bytes | None, bytes]], vault: Path, guard: _Guard) -> None:
    work = vault / '.obforce/transaction'
    _mkdir(work, guard)
    _save(journal, vault, guard)
    _checkpoint('staging')
    for index, (before, after) in enumerate(contents):
        for label, raw in (('before', before), ('after', after)):
            if raw is None:
                continue
            path = work / f'{index:04d}.{label}'
            guard.change(lambda p=path, r=raw: _write_new(p, r), (path,), data={path: raw})
            journal['entries'][index][label]['stamp'] = guard.stamps[path]
            _save(journal, vault, guard)
            _checkpoint(label, index)
    for entry in journal['entries']:
        path = vault / entry['path']
        missing = []
        parent = path.parent
        while _lstat(parent) is None:
            missing.append(parent)
            parent = parent.parent
        for parent in reversed(missing):
            if len(journal['directories']) >= const.MAX_TRANSACTION_DIRECTORIES:
                raise ModelError('Created parent bound exceeded')
            record = {'path': parent.relative_to(vault).as_posix(), 'stamp': None, 'removed': False}
            journal['directories'].append(record)
            _save(journal, vault, guard)
            _mkdir(parent, guard)
            record['stamp'] = guard.stamps[parent]
            _save(journal, vault, guard)
            _checkpoint('directory')
        if _lstat(path.parent)[0] != journal['vault_identity'][0]:
            raise ConflictError('Staging and destination are not on the same filesystem')
    journal['phase'] = 'ready'
    _save(journal, vault, guard)
    _checkpoint('ready')


def _publish(journal: dict, vault: Path, guard: _Guard) -> None:
    journal['phase'] = 'publishing'
    _save(journal, vault, guard)
    for index, entry in enumerate(journal['entries']):
        target = vault / entry['path']
        staged = vault / f'.obforce/transaction/{index:04d}.transfer'
        raw = _read_blob(vault / f'.obforce/transaction/{index:04d}.after', entry['after'], _Reader())
        guard.change(lambda p=staged, r=raw: _write_new(p, r), (staged,), data={staged: raw})
        entry['transfer'] = guard.stamps[staged]
        _save(journal, vault, guard)
        _checkpoint('transfer', index)
        entry['intent'] = 'publish'
        _save(journal, vault, guard)
        _checkpoint('replace_before', index)
        guard.check()
        expected = tuple(entry['original']) if entry['original'] is not None else None
        if _lstat(target) != expected:
            raise ConflictError('Publication target changed')
        guard.change(lambda s=staged, t=target: os.replace(s, t), (staged, target), data={target: raw})
        _checkpoint('replace_after', index)
        entry['published'] = guard.stamps[target]
        entry['transfer'] = None
        entry['intent'] = None
        _save(journal, vault, guard)
        _checkpoint('published', index)
    guard.check()
    journal['phase'] = 'committed'
    _checkpoint('commit_before')
    _save(journal, vault, guard)
    _checkpoint('commit')


def _failure(error: BaseException, *, evidence: bool, coverage: ExitCode = ExitCode.SUCCESS) -> TransactionResult:
    code = (
        ExitCode(error.exit_code)
        if isinstance(error, OperationalError)
        else (ExitCode.OPERATIONAL if isinstance(error, OSError) else ExitCode.INVALID)
    )
    return TransactionResult(
        TransactionStatus.RECOVERY_REQUIRED if evidence else TransactionStatus.BLOCKED, exit_code((code, coverage)), evidence
    )


def publish_plan(plan: ChangePlan, inputs: TransactionInputs, *, preview: bool = False) -> TransactionResult:
    """Validate a complete explicit plan and publish matching note/state candidates.

    :param preview: Read-only independent validation; never creates any artifact.
    :returns: Redacted result; any retained evidence blocks ordinary subsequent writes.
    """
    evidence = False
    committed = False
    coverage = ExitCode.SUCCESS
    try:
        if type(preview) is not bool:
            raise ModelError('Invalid preview flag')
        plan = _validated(plan, inputs)
        vault, control = inputs.vault, inputs.vault / '.obforce'
        coverage = plan.outcome
        _control(vault, pending=False)
        entries, contents = _contents(vault, plan)
        guard = _Guard(plan.preconditions)
        guard.check()
        if preview or not entries:
            return TransactionResult(
                TransactionStatus.PREVIEW if preview else TransactionStatus.NO_OP, coverage, files=len(entries)
            )
        if _lstat(control) is None:
            _mkdir(control, guard)
        if _lstat(control)[0] != _lstat(vault)[0]:
            raise ConflictError('Control is not on the vault filesystem')
        with _Lock(control, guard) as lock:
            _control(vault, pending=False)
            guard.check()
            journal = {
                'journal_schema': const.TRANSACTION_SCHEMA_VERSION,
                'transaction_id': str(uuid4()),
                'lock_token': lock.token,
                'vault_identity': _identity(guard.stamps[vault]),
                'control_identity': _identity(guard.stamps[control]),
                'phase': 'preparing',
                'entries': entries,
                'directories': [],
                'guards': [],
                'work_stamp': None,
                'file_guards': [],
            }
            evidence = True
            _save(journal, vault, guard, first=True)
            _checkpoint('preparing')
            _stage(journal, contents, vault, guard)
            _publish(journal, vault, guard)
            committed = True
            _cleanup(journal, vault, guard)
            evidence = False
        return TransactionResult(TransactionStatus.COMMITTED, coverage, files=len(entries))
    except (OperationalError, OSError, UnicodeError, TypeError, ValueError, AttributeError, RecursionError) as error:
        if evidence:
            try:
                evidence = any(
                    _lstat(inputs.vault / '.obforce' / name) is not None
                    for name in ('journal.json', 'journal.next', 'transaction')
                )
            except (OSError, OperationalError):
                evidence = True
        result = _failure(error, evidence=evidence, coverage=coverage)
        if committed and not evidence:
            return TransactionResult(TransactionStatus.COMMITTED, result.outcome, files=len(entries))
        return result


def _keys(value: object, keys: frozenset[str] | set[str]) -> dict:
    if type(value) is not dict or value.keys() != keys:
        raise ConflictError('Invalid journal object')
    return value


def _uuid(value: object) -> None:
    if type(value) is not str or len(value) != 36 or str(UUID(value)) != value:
        raise ConflictError('Invalid journal identity')


def _digest(value: object) -> None:
    if type(value) is not str or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
        raise ConflictError('Invalid journal digest')


def _wire_stamp(value: object, *, directory: bool = False, optional: bool = False) -> tuple[int, ...] | None:
    if value is None and optional:
        return None
    if type(value) is not list or len(value) != 7 or any(type(v) is not int or v.bit_length() > 128 for v in value):
        raise ConflictError('Invalid journal observation')
    if any(v < 0 for v in value[:5]) or not (stat.S_ISDIR(value[2]) if directory else stat.S_ISREG(value[2])):
        raise ConflictError('Invalid journal file type')
    if not directory and value[3] != 1:
        raise ConflictError('Invalid journal link count')
    return tuple(value)


def _relative(value: object, *, state: bool = False, root: bool = False) -> str:
    if root and value == '.':
        return value
    if root and type(value) is str and value.split('/')[-1] in const.CONTROL_DIRECTORIES:
        prefix = '/'.join(value.split('/')[:-1])
        if prefix:
            _relative(prefix)
        return value
    if type(value) is not str:
        raise ConflictError('Invalid journal path')
    if state and value == '.obforce/state.json':
        return value
    _portable(value)
    if any(part.casefold() in const.CONTROL_DIRECTORIES for part in value.split('/')):
        raise ConflictError('Journal target enters a control area')
    return value


def _decode_journal(raw: bytes) -> dict:
    if type(raw) is not bytes or not raw or len(raw) > const.MAX_JOURNAL_BYTES:
        raise ConflictError('Journal exceeds byte bound')
    text = raw.decode('utf-8')
    depth, quoted, escaped = 0, False, False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in '[{':
            depth += 1
            if depth > const.MAX_JOURNAL_DEPTH:
                raise ConflictError('Journal exceeds nesting bound')
        elif char in ']}':
            depth -= 1
    document = json.loads(text, object_pairs_hook=_pairs)
    nodes, pending = 0, [document]
    while pending:
        value = pending.pop()
        nodes += 1
        if nodes > const.MAX_JOURNAL_NODES:
            raise ConflictError('Journal exceeds node bound')
        if type(value) is dict:
            pending.extend(value.keys())
            pending.extend(value.values())
        elif type(value) is list:
            pending.extend(value)
        elif value is not None and type(value) not in (str, int, bool):
            raise ConflictError('Invalid journal primitive')
    _keys(document, _ROOT_KEYS)
    if type(document['journal_schema']) is not int or document['journal_schema'] != const.TRANSACTION_SCHEMA_VERSION:
        raise ConflictError('Unknown journal version')
    _uuid(document['transaction_id'])
    _uuid(document['lock_token'])
    if document['phase'] not in _PHASES:
        raise ConflictError('Unknown transaction phase')
    for name in ('vault_identity', 'control_identity'):
        identity = document[name]
        if (
            type(identity) is not list
            or len(identity) != 3
            or any(type(v) is not int or v < 0 or v.bit_length() > 128 for v in identity)
            or not stat.S_ISDIR(identity[2])
        ):
            raise ConflictError('Invalid directory identity')
    _wire_stamp(document['work_stamp'], directory=True, optional=True)
    entries, directories, observations = document['entries'], document['directories'], document['guards']
    if (
        type(entries) is not list
        or not 1 <= len(entries) <= const.MAX_TRANSACTION_FILES
        or type(directories) is not list
        or len(directories) > const.MAX_TRANSACTION_DIRECTORIES
        or type(observations) is not list
        or len(observations) > const.MAX_TRANSACTION_GUARDS
    ):
        raise ConflictError('Journal exceeds collection bounds')
    paths, total = set(), 0
    for index, entry in enumerate(entries):
        _keys(entry, _ENTRY_KEYS)
        path = _relative(entry['path'], state=True)
        if path == '.obforce/state.json':
            if index != len(entries) - 1:
                raise ConflictError('State must be published last')
        else:
            _path(path)
        token = path if path == '.obforce/state.json' else _portable(path)
        if token in paths:
            raise ConflictError('Ambiguous journal targets')
        paths.add(token)
        _wire_stamp(entry['original'], optional=True)
        _wire_stamp(entry['published'], optional=True)
        _wire_stamp(entry['restored'], optional=True)
        _wire_stamp(entry['transfer'], optional=True)
        if entry['intent'] not in (None, 'publish', 'rollback', 'remove_before', 'remove_after'):
            raise ConflictError('Unknown journal operation')
        for name in ('before', 'after'):
            blob = entry[name]
            if blob is None:
                if name != 'before' or entry['original'] is not None:
                    raise ConflictError('Missing journal content evidence')
                continue
            _keys(blob, _BLOB_KEYS)
            _digest(blob['hash'])
            limit = const.MAX_STATE_BYTES if path == '.obforce/state.json' else const.MAX_NOTE_BYTES
            if type(blob['size']) is not int or not 0 < blob['size'] <= limit or type(blob['removed']) is not bool:
                raise ConflictError('Invalid journal blob bound')
            stamp = _wire_stamp(blob['stamp'], optional=True)
            if stamp is not None and stamp[4] != blob['size']:
                raise ConflictError('Contradictory journal blob size')
            total += blob['size']
        if entry['before'] is not None and entry['original'] is None:
            raise ConflictError('Missing original observation')
    committed = document['phase'] in {'committed', 'cleaning'}
    for entry in entries:
        if committed and (
            entry['published'] is None
            or entry['restored'] is not None
            or entry['transfer'] is not None
            or entry['intent'] in {'publish', 'rollback'}
        ):
            raise ConflictError('Commit evidence is incomplete')
        if document['phase'] in {'preparing', 'ready'} and (entry['published'] is not None or entry['restored'] is not None):
            raise ConflictError('Publication contradicts journal phase')
        if document['phase'] == 'rolled_back' and entry['published'] is not None:
            raise ConflictError('Rollback evidence is incomplete')
    if entries[-1]['path'] != '.obforce/state.json' or total > const.MAX_TRANSACTION_BYTES:
        raise ConflictError('Complete matching state or byte bound missing')
    seen = set()
    for record in directories:
        _keys(record, {'path', 'stamp', 'removed'})
        path = _relative(record['path'])
        token = _portable(path)
        if token in paths or token in seen or not any(e['path'].startswith(path + '/') for e in entries):
            raise ConflictError('Unrelated or ambiguous created directory')
        seen.add(token)
        _wire_stamp(record['stamp'], directory=True, optional=True)
        if type(record['removed']) is not bool:
            raise ConflictError('Invalid directory removal evidence')
    seen = set()
    for observation in observations:
        _keys(observation, {'path', 'stamp', 'hash'})
        path = _relative(observation['path'], root=True)
        if path in seen:
            raise ConflictError('Duplicate journal observation')
        seen.add(path)
        stamp = observation['stamp']
        if stamp is not None:
            _wire_stamp(stamp, directory=type(stamp) is list and len(stamp) == 7 and stat.S_ISDIR(stamp[2]))
        if observation['hash'] is not None:
            _digest(observation['hash'])
            if stamp is None or not stat.S_ISREG(stamp[2]):
                raise ConflictError('Invalid digest observation')
    if '.' not in seen:
        raise ConflictError('Missing vault observation')
    expected = _expected_files(document)
    files = document['file_guards']
    if type(files) is not list or len(files) > const.MAX_TRANSACTION_GUARDS or len(files) != len(expected):
        raise ConflictError('Invalid descriptor observation collection')
    seen = set()
    for observation in files:
        _keys(observation, {'path', 'stamp'})
        path = observation['path']
        if type(path) is not str or path not in expected or path in seen:
            raise ConflictError('Unrelated or ambiguous descriptor observation')
        seen.add(path)
        stamp = _wire_stamp(observation['stamp'])
        prior = expected[path]
        if prior is not None and stamp[:-1] != tuple(prior[:-1]):
            raise ConflictError('Contradictory descriptor observation')
    return document


def _expected_files(journal: dict) -> dict[str, tuple[int, ...] | list[int] | None]:
    """Derive exact regular-file membership; journals cannot choose arbitrary paths."""
    files = {item['path']: item['stamp'] for item in journal['guards'] if item['hash'] is not None}
    files['.obforce/writer.lock'] = None
    for index, entry in enumerate(journal['entries']):
        stamp = entry['restored'] or entry['published'] or entry['original']
        if stamp is not None:
            files[entry['path']] = stamp
        else:
            files.pop(entry['path'], None)
        for label in ('before', 'after'):
            blob = entry[label]
            if blob is not None and blob['stamp'] is not None and not blob['removed']:
                files[f'.obforce/transaction/{index:04d}.{label}'] = blob['stamp']
        if entry['transfer'] is not None:
            files[f'.obforce/transaction/{index:04d}.transfer'] = entry['transfer']
    return files


def _read_blob(path: Path, blob: dict, reader: _Reader) -> bytes:
    if blob['stamp'] is None or blob['removed']:
        raise ConflictError('Incomplete blob ownership evidence')
    if _lstat(path) != tuple(blob['stamp']):
        raise ConflictError('Blob identity or content observation changed')
    raw = reader.read(path, const.MAX_STATE_BYTES)
    if len(raw) != blob['size'] or _hash(raw) != blob['hash']:
        raise ConflictError('Blob digest mismatch')
    return raw


def _matches(raw: bytes, blob: dict) -> None:
    if len(raw) != blob['size'] or _hash(raw) != blob['hash']:
        raise ConflictError('Recorded target content changed')


def _semantics(journal: dict, content: list[dict[str, bytes]], vault: Path, reader: _Reader) -> None:
    """Validate state/note agreement and rederive preservation patches without source acquisition."""
    state_entry, state_content = journal['entries'][-1], content[-1]
    after_raw = state_content.get('after')
    before_raw = state_content.get('before')
    # During cleanup a removed blob may be unavailable. Published/rolled-back
    # target bytes still provide the matching surviving state. No repair is inferred.
    if before_raw is not None:
        parse_state(before_raw)
    if after_raw is None:
        if journal['phase'] not in {'committed', 'cleaning', 'rolled_back'}:
            raise ConflictError('Candidate state evidence is unavailable')
        return
    after = parse_state(after_raw)
    before = parse_state(before_raw) if before_raw is not None else None
    if before is not None and (before.binding != after.binding or before.selection != after.selection):
        raise ConflictError('Recovery state bindings differ')
    old = {s.note.obforce_id: s for s in before.notes} if before else {}
    new = {s.note.obforce_id: s for s in after.notes}
    if old.keys() - new.keys():
        raise ConflictError('Journal attempts automatic note removal')
    targets = set()
    for entry, blobs in zip(journal['entries'][:-1], content[:-1], strict=True):
        raw = blobs.get('after')
        if raw is None:
            if journal['phase'] not in {'committed', 'cleaning', 'rolled_back'}:
                raise ConflictError('Candidate note evidence unavailable')
            continue
        parsed = parse_note(raw)
        identity = parsed.properties['obforce_id']
        saved = new.get(identity)
        if (
            saved is None
            or saved.note.path != entry['path']
            or parsed.generated_properties != saved.note.generated_properties
            or parsed.region != saved.generated_region
            or identity in targets
        ):
            raise ConflictError('Candidate note and state disagree')
        targets.add(identity)
        original = blobs.get('before')
        if entry['before'] is not None:
            if original is None:
                if journal['phase'] in {'committed', 'cleaning', 'rolled_back'}:
                    continue
                raise ConflictError('Before-image unavailable')
            prior = old.get(identity)
            if prior is None:
                raise ConflictError('Before-image has no accepted saved baseline')
            incoming = GeneratedCandidate(
                parsed.region.replace(b'\r\n', b'\n').decode('utf-8'),
                {k: v.value for k, v in saved.note.generated_properties.items()},
                saved.note.source_hash,
                saved.note.graph_hash,
                saved.note.render_hash,
            )
            patched = patch_note(original, prior.note, prior.generated_region, incoming)
            if patched.content != raw:
                raise ConflictError('Journal bytes are not a preservation patch')
        elif identity in old:
            raise ConflictError('Journal creates an already tracked identity')
    if state_entry['before'] is None and any(entry['before'] is not None for entry in journal['entries'][:-1]):
        raise ConflictError('Initial state cannot adopt existing managed notes')
    if before is not None or state_entry['before'] is None:
        for identity, saved in new.items():
            if identity in targets:
                continue
            prior = old.get(identity)
            if prior is None:
                raise ConflictError('Candidate state contains an uncreated identity')
            if (
                saved.note.key != prior.note.key
                or saved.note.binding != prior.note.binding
                or saved.generated_region != prior.generated_region
                or saved.note.generated_properties != prior.note.generated_properties
            ):
                raise ConflictError('Unpublished note baseline changed')
            parsed = parse_note(reader.read(vault / saved.note.path, const.MAX_NOTE_BYTES))
            if parsed.generated_properties != saved.note.generated_properties or parsed.region != saved.generated_region:
                raise ConflictError('Unchanged recovery note does not match accepted state')


def _load_recovery(vault: Path, state_path: Path, excluded_roots: tuple[Path, ...]) -> tuple[dict | None, _Guard]:
    reader = _roots(vault, state_path, excluded_roots)
    _control(vault, pending=True)
    control = vault / '.obforce'
    if reader.observe(control, missing=True) is None:
        return None, _Guard(reader.preconditions())
    reader.observe(control / 'writer.lock', missing=True)
    path = control / 'journal.json'
    if reader.observe(path, missing=True) is None:
        if _lstat(control / 'transaction') is not None:
            raise ConflictError('Unjournaled recovery material')
        return None, _Guard(reader.preconditions())
    raw = reader.read(path, const.MAX_JOURNAL_BYTES)
    try:
        journal = _decode_journal(raw)
    except ConflictError:
        raise
    except (OperationalError, UnicodeError, TypeError, ValueError, AttributeError, KeyError, IndexError, RecursionError):
        raise ConflictError('Invalid journal evidence') from None
    reader.file_stamps.update((vault / item['path'], tuple(item['stamp'])) for item in journal['file_guards'])
    if _identity(_lstat(vault)) != tuple(journal['vault_identity']) or _identity(_lstat(control)) != tuple(
        journal['control_identity']
    ):
        raise ConflictError('Recovery root identity changed')
    lock = reader.read(control / 'writer.lock', 128)
    if lock != ('obforce-lock-v1 ' + journal['lock_token'] + '\n').encode('ascii'):
        raise ConflictError('Journal does not match persistent guard')
    for observation in journal['guards']:
        target = vault / observation['path']
        expected = tuple(observation['stamp']) if observation['stamp'] is not None else None
        if _lstat(target) != expected:
            raise ConflictError('Journal observation changed')
        reader.observe(target, missing=expected is None)
        if observation['hash'] is not None:
            if _hash(reader.read(target, const.MAX_STATE_BYTES)) != observation['hash']:
                raise ConflictError('Journal observed bytes changed')
    work = control / 'transaction'
    expected = tuple(journal['work_stamp']) if journal['work_stamp'] is not None else None
    if _lstat(work) != expected:
        raise ConflictError('Unrecorded staging directory change')
    reader.observe(work, missing=expected is None)
    allowed, contents = set(), []
    for index, entry in enumerate(journal['entries']):
        target = vault / entry['path']
        stamp = reader.observe(target, missing=True)
        actual = _stamp(stamp) if stamp is not None else None
        prior = tuple(entry['original']) if entry['original'] is not None else None
        published = tuple(entry['published']) if entry['published'] is not None else None
        restored = tuple(entry['restored']) if entry['restored'] is not None else None
        blobs = {}
        if actual is not None:
            current = reader.read(target, const.MAX_STATE_BYTES)
            if published is not None and actual == published and entry['restored'] is None:
                _matches(current, entry['after'])
                blobs['after'] = current
            elif actual == prior or (restored is not None and actual == restored):
                if entry['before'] is None:
                    raise ConflictError('Unowned recovery target exists')
                _matches(current, entry['before'])
                blobs['before'] = current
            else:
                raise ConflictError('Intervening edit or unrecorded replacement')
        elif prior is not None and restored is None:
            raise ConflictError('Original recovery target disappeared')
        elif published is not None and entry['intent'] != 'rollback' and journal['phase'] not in {'rolled_back', 'cleaning'}:
            raise ConflictError('Published target disappeared')
        for label in ('before', 'after'):
            blob = entry[label]
            path = work / f'{index:04d}.{label}'
            if blob is None:
                continue
            allowed.add(path.name)
            observed = reader.observe(path, missing=True)
            if observed is not None:
                blobs[label] = _read_blob(path, blob, reader)
            elif not blob['removed'] and blob['stamp'] is not None:
                raise ConflictError('Tracked before-image or stage disappeared')
        if entry['intent'] in {'publish', 'rollback'}:
            # A completed operation not fully journaled is deliberately ambiguous.
            expected_target = prior if entry['intent'] == 'publish' else published
            if actual != expected_target:
                raise ConflictError('Unrecorded publication or rollback')
        transfer = work / f'{index:04d}.transfer'
        allowed.add(transfer.name)
        transferred = reader.observe(transfer, missing=True)
        if transferred is not None:
            if entry['transfer'] is None or _stamp(transferred) != tuple(entry['transfer']):
                raise ConflictError('Unrecorded transfer file')
            transfer_bytes = reader.read(transfer, const.MAX_STATE_BYTES)
            _matches(transfer_bytes, entry['before'] if entry['intent'] == 'rollback' else entry['after'])
        elif entry['transfer'] is not None:
            raise ConflictError('Unrecorded transfer replacement')
        contents.append(blobs)
    if expected is not None and _listing(work).keys() - allowed:
        raise ConflictError('Unowned staging entry')
    for record in journal['directories']:
        target = vault / record['path']
        if record['stamp'] is None:
            if _lstat(target) is not None:
                raise ConflictError('Unrecorded directory creation')
        elif not record['removed'] and _lstat(target) != tuple(record['stamp']):
            raise ConflictError('Created directory changed')
        elif record['removed'] and _lstat(target) is not None:
            raise ConflictError('Removed directory reappeared')
    _semantics(journal, contents, vault, reader)
    reader.finish()
    guard = _Guard(reader.preconditions(), reader.file_stamps)
    guard.check()
    return journal, guard


def _remove_blob(journal: dict, vault: Path, guard: _Guard, index: int, label: str) -> None:
    entry = journal['entries'][index]
    blob = entry[label]
    if blob is None or blob['removed']:
        return
    target = vault / f'.obforce/transaction/{index:04d}.{label}'
    if blob['stamp'] is None:
        if _lstat(target) is not None:
            raise ConflictError('Unrecorded blob cannot be cleaned')
        blob['removed'] = True
        _save(journal, vault, guard)
        return
    _read_blob(target, blob, _Reader())
    entry['intent'] = 'remove_' + label
    _save(journal, vault, guard)
    _checkpoint('cleanup_before', index)
    guard.change(target.unlink, (target,))
    blob['removed'] = True
    entry['intent'] = None
    _save(journal, vault, guard)
    _checkpoint('cleanup', index)


def _cleanup(journal: dict, vault: Path, guard: _Guard) -> None:
    """Delete only recorded unchanged blobs and exact empty transaction-owned directories."""
    rollback = journal['phase'] == 'rolled_back'
    journal['phase'] = 'rolled_back' if rollback else 'cleaning'
    _save(journal, vault, guard)
    for index, entry in enumerate(journal['entries']):
        transfer = vault / f'.obforce/transaction/{index:04d}.transfer'
        if entry['transfer'] is not None:
            if _lstat(transfer) != tuple(entry['transfer']):
                raise ConflictError('Changed transfer cannot be cleaned')
            guard.change(transfer.unlink, (transfer,))
            entry['transfer'] = None
            _save(journal, vault, guard)
        for label in ('before', 'after'):
            _remove_blob(journal, vault, guard, index, label)
    if rollback:
        for record in reversed(journal['directories']):
            path = vault / record['path']
            if record['removed'] or record['stamp'] is None:
                continue
            if _lstat(path) != tuple(record['stamp']) or _listing(path):
                raise ConflictError('Created directory is changed or nonempty')
            guard.change(path.rmdir, (path,))
            record['removed'] = True
            _save(journal, vault, guard)
            _checkpoint('directory_cleanup')
    work = vault / '.obforce/transaction'
    if _lstat(work) is not None:
        if _lstat(work) != tuple(journal['work_stamp']) or _listing(work):
            raise ConflictError('Staging directory is changed or nonempty')
        guard.change(work.rmdir, (work,))
        _save(journal, vault, guard)
    _checkpoint('cleanup_final')
    target = vault / '.obforce/journal.json'
    guard.change(target.unlink, (target,))
    _checkpoint('cleaned')


def _rollback(journal: dict, vault: Path, guard: _Guard) -> None:
    journal['phase'] = 'rolling_back'
    _save(journal, vault, guard)
    indices = [*reversed(range(len(journal['entries']) - 1)), len(journal['entries']) - 1]
    for index in indices:
        entry = journal['entries'][index]
        target = vault / entry['path']
        if entry['published'] is None or entry['restored'] is not None:
            continue
        if _lstat(target) != tuple(entry['published']):
            raise ConflictError('Rollback refuses intervening changes')
        guard.check()
        entry['intent'] = 'rollback'
        _save(journal, vault, guard)
        _checkpoint('rollback_before', index)
        if entry['before'] is None:
            guard.change(target.unlink, (target,))
        else:
            before = vault / f'.obforce/transaction/{index:04d}.before'
            raw = _read_blob(before, entry['before'], _Reader())
            transfer = vault / f'.obforce/transaction/{index:04d}.transfer'
            if entry['transfer'] is None:
                guard.change(lambda p=transfer, r=raw: _write_new(p, r), (transfer,), data={transfer: raw})
                entry['transfer'] = guard.stamps[transfer]
                _save(journal, vault, guard)
            guard.change(lambda b=transfer, t=target: os.replace(b, t), (transfer, target), data={target: raw})
            entry['transfer'] = None
        _checkpoint('rollback_after', index)
        entry['restored'] = guard.stamps[target]
        entry['published'] = None
        entry['intent'] = None
        _save(journal, vault, guard)
        _checkpoint('rollback', index)
    journal['phase'] = 'rolled_back'
    _save(journal, vault, guard)
    _checkpoint('rolled_back')


def recover_transaction(
    vault: Path, state_path: Path, *, excluded_roots: tuple[Path, ...], preview: bool = True
) -> TransactionResult:
    """Preview validated local recovery or rollback/clean under the same writer guard.

    No acquisition, auth, source facts, templates or saved graph is needed. Unknown
    or ambiguous evidence is retained for manual resolution without guessing.
    """
    evidence = False
    try:
        if type(preview) is not bool:
            raise ModelError('Invalid recovery preview flag')
        evidence = True
        journal, guard = _load_recovery(vault, state_path, excluded_roots)
        if journal is None:
            return TransactionResult(TransactionStatus.NO_OP, ExitCode.SUCCESS)
        files = len(journal['entries'])
        if preview:
            return TransactionResult(TransactionStatus.PREVIEW, ExitCode.SUCCESS, True, files)
        with _Lock(vault / '.obforce', guard) as lock:
            if lock.token != journal['lock_token']:
                raise ConflictError('Recovery guard identity differs')
            # Full evidence was read immediately before lock acquisition and is
            # rechecked again under it; there is no stale-lock deletion or retry.
            guard.check()
            committed = journal['phase'] in {'committed', 'cleaning'}
            if not committed and journal['phase'] != 'rolled_back':
                _rollback(journal, vault, guard)
            _cleanup(journal, vault, guard)
        evidence = False
        return TransactionResult(
            TransactionStatus.CLEANED if committed else TransactionStatus.ROLLED_BACK, ExitCode.SUCCESS, files=files
        )
    except (OperationalError, OSError, UnicodeError, TypeError, ValueError, AttributeError, RecursionError) as error:
        return _failure(error, evidence=evidence)
