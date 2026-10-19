# -*- coding: utf-8 -*-
"""
:Module:            obforce.sources.local
:Synopsis:          Inventories declared local DX packages without changing source files
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     19 Oct 2026
"""

from __future__ import annotations

import json
import os
import re
import stat
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from obforce import constants as const
from obforce.config import relative_path
from obforce.errors import ConfigError, ConflictError, ModelError, OperationalError
from obforce.models import (
    CollectionCoverage,
    Component,
    ComponentKey,
    Coverage,
    CoverageStatus,
    Selection,
    SourceBinding,
    component_fingerprint,
    validate_identities,
)
from obforce.parsers.apex import parse_apex_metadata


@dataclass(frozen=True)
class LocalInventory:
    """Return normalized components and independent coverage of available local scope."""

    components: tuple[Component, ...]
    coverage: Coverage

    @property
    def inventory_hash(self) -> str:
        """Use the unchanged Thread 02 canonical inventory fingerprint."""
        return component_fingerprint(self.components)


def _identity(info: os.stat_result) -> tuple[int, ...]:
    """Compare read preconditions without treating atime as a semantic source fact."""
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def _matches_descriptor(expected: os.stat_result, opened: os.stat_result) -> bool:
    """Match a descriptor to its path, allowing only the Windows ctime semantic split.

    Windows CPython can report creation time as path ctime but change time as
    descriptor ctime. An exact descriptor birthtime may bridge only that field;
    device, inode, mode, size, and mtime still match without rounding. Callers
    must also compare raw descriptor metadata before/after the read.

    :param expected: Previously inspected no-follow pathname metadata.
    :param opened: Full metadata from the opened file descriptor.
    :returns: Whether identity and every comparable change indicator agree.
    """
    path_identity = _identity(expected)
    descriptor_identity = _identity(opened)
    if descriptor_identity == path_identity:
        return True
    birthtime = getattr(opened, 'st_birthtime_ns', None)
    return os.name == 'nt' and type(birthtime) is int and (*descriptor_identity[:-1], birthtime) == path_identity


class _Reader:
    """Check contained regular inputs and retain read-only concurrency preconditions."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.observed: dict[Path, tuple[int, ...]] = {}

    def inspect(self, path: Path) -> os.stat_result:
        """Refuse links, junctions, special files, escapes, and observed replacements."""
        try:
            info = path.lstat()
        except FileNotFoundError as error:
            if path in self.observed:
                raise OperationalError('Observed local input disappeared during acquisition') from error
            raise
        reparse = getattr(info, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0)
        if (
            stat.S_ISLNK(info.st_mode)
            or path.is_junction()
            or reparse
            or not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode))
        ):
            raise ConfigError('Local project contains an unsafe link or special file')
        if stat.S_ISREG(info.st_mode) and info.st_nlink != 1:
            raise ConfigError('Local project contains a multiply linked file')
        if not path.resolve(strict=True).is_relative_to(self.root):
            raise ConfigError('Local project path escapes its root')
        identity = _identity(info)
        if self.observed.setdefault(path, identity) != identity:
            raise OperationalError('Local project changed during acquisition; retry from a stable source')
        return info

    def read(self, path: Path, limit: int) -> bytes:
        """Read at most limit plus one bytes, checking descriptor and pathname identity."""
        before = self.inspect(path)
        if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
            raise ModelError('Expected a bounded regular source file')
        flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_BINARY', 0)
        descriptor = os.open(path, flags)
        with os.fdopen(descriptor, 'rb') as stream:
            opened = os.fstat(stream.fileno())
            if not _matches_descriptor(before, opened):
                raise OperationalError('Local source file changed before reading')
            data = stream.read(limit + 1)
            after = os.fstat(stream.fileno())
            if _identity(after) != _identity(opened) or not _matches_descriptor(before, after):
                raise OperationalError('Local source file changed while reading')
        self.inspect(path)
        if len(data) > limit:
            raise ModelError('Source file exceeds its byte limit')
        return data

    def verify(self) -> None:
        """Refuse a result after any observed input or directory changed."""
        for path in tuple(self.observed):
            self.inspect(path)


def _object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Reject duplicate JSON keys even in ignored project settings."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ConfigError('Duplicate DX project JSON key')
        result[key] = value
    return result


def _project(reader: _Reader) -> tuple[tuple[Path, ...], str | None]:
    """Validate the acquisition subset without executing unrelated DX settings."""
    try:
        document = json.loads(
            reader.read(reader.root / 'sfdx-project.json', const.MAX_PROJECT_BYTES),
            object_pairs_hook=_object,
            parse_constant=_invalid_constant,
        )
    except (UnicodeError, ValueError, RecursionError) as error:
        raise ConfigError('Malformed DX project JSON') from error
    if not isinstance(document, dict):
        raise ConfigError('DX project must be a JSON object')
    packages = document.get('packageDirectories')
    if not isinstance(packages, list) or not 1 <= len(packages) <= const.MAX_LOCAL_PACKAGES:
        raise ConfigError('DX project requires a bounded nonempty package directory list')
    namespace = document.get('namespace', '')
    if not isinstance(namespace, str) or (namespace and not re.fullmatch(r'[A-Za-z][A-Za-z0-9]{0,14}', namespace)):
        raise ConfigError('Invalid DX project namespace')
    roots: list[Path] = []
    for package in packages:
        if not isinstance(package, dict) or 'path' not in package:
            raise ConfigError('Each DX package requires a relative path')
        path = reader.root / relative_path(package['path'])
        if len(path.relative_to(reader.root).parts) > const.MAX_LOCAL_DEPTH:
            raise ConfigError('DX package path exceeds nesting limit')
        # Check every ancestor before resolving/opening a package child.
        for parent in reversed((path, *path.parents)):
            if parent.is_relative_to(reader.root) and not stat.S_ISDIR(reader.inspect(parent).st_mode):
                raise ConfigError('DX package path is not a directory')
        portable = unicodedata.normalize('NFC', path.relative_to(reader.root).as_posix()).casefold()
        prior = [unicodedata.normalize('NFC', other.relative_to(reader.root).as_posix()).casefold() for other in roots]
        if any(path.is_relative_to(other) or other.is_relative_to(path) for other in roots) or any(
            portable == other or portable.startswith(other + '/') or other.startswith(portable + '/') for other in prior
        ):
            raise ConflictError('Duplicate or overlapping DX package directories')
        roots.append(path)
    return tuple(sorted(roots)), namespace or None


def _invalid_constant(value: str) -> object:
    """Refuse JavaScript nonfinite constants, which are not valid JSON."""
    raise ConfigError('DX project contains a non-JSON numeric constant')


def _scan(reader: _Reader, roots: tuple[Path, ...]) -> tuple[list[Path], set[str]]:
    """Bound directory traversal, refusing unsafe inputs even for unsupported types."""
    files: list[Path] = []
    warnings: set[str] = set()
    pending = list(roots)
    entries = 0
    while pending:
        directory = pending.pop()
        reader.inspect(directory)
        children: list[Path] = []
        with os.scandir(directory) as iterator:
            for entry in iterator:
                entries += 1
                if entries > const.MAX_LOCAL_ENTRIES:
                    raise ModelError('Local project exceeds entry limit')
                children.append(Path(entry.path))
        names: set[str] = set()
        for path in sorted(children):
            info = reader.inspect(path)
            portable = unicodedata.normalize('NFC', path.name).casefold()
            if portable in names:
                raise ConflictError('Local project contains equivalent portable paths')
            names.add(portable)
            if path.name in {'.git', '.obsidian', '.obforce'} and stat.S_ISDIR(info.st_mode):
                warnings.add('control_directories_excluded')
                continue
            relative_path(path.name)
            if len(path.relative_to(reader.root).parts) > const.MAX_LOCAL_DEPTH:
                raise ModelError('Local project exceeds nesting limit')
            if stat.S_ISDIR(info.st_mode):
                pending.append(path)
            elif path.parent.name == 'classes' and path.name.endswith(('.cls', '.cls-meta.xml')):
                files.append(path)
            else:
                warnings.add('unsupported_files_excluded')
        if not children and directory in roots:
            warnings.add('empty_package')
    return sorted(files), warnings


def collect_local(project: Path, binding: SourceBinding, selection: Selection) -> LocalInventory:
    """Inventory declared DX Apex pairs without network, source writes, or body reads.

    Missing pairs produce partial inventory. Invalid/unsafe/unreadable inputs
    refuse the entire result. Complete always means the available selected local
    scope, never org inventory or evidence for absence/deletion.

    :param project: Explicit absolute project directory, never discovered.
    :param binding: Existing logical local workspace binding, independent of paths.
    :param selection: Existing Apex namespace/name selection.
    :returns: Deterministically ordered components and independent coverage.
    :raises ConfigError: For invalid manifest, paths, namespace, or source mode.
    :raises ModelError: For invalid metadata, filenames, or exceeded input bounds.
    :raises ConflictError: For duplicate identities or ambiguous package/portable paths.
    :raises OperationalError: For read failures or detected concurrent changes.
    """
    if not isinstance(binding, SourceBinding) or binding.mode != 'local' or not isinstance(selection, Selection):
        raise ConfigError('Offline acquisition requires local binding and normalized selection')
    if not isinstance(project, Path) or not project.is_absolute() or '..' in project.parts:
        raise ConfigError('Offline acquisition requires an explicit absolute project path')
    try:
        if project.is_symlink() or project.is_junction():
            raise ConfigError('Project root cannot be a link or junction')
        root = project.resolve(strict=True)
        reader = _Reader(root)
        if not stat.S_ISDIR(reader.inspect(root).st_mode):
            raise ConfigError('Project root must be a directory')
        roots, namespace = _project(reader)
        files, warnings = _scan(reader, roots)
        warnings.add('local_scope_only')
        if namespace and not selection.include_namespaced:
            warnings.add('namespaced_components_excluded')
        components: list[Component] = []
        partial = False
        total_xml = 0
        candidates: dict[tuple[Path, str], dict[str, Path]] = {}
        for path in files:
            kind = 'xml' if path.name.endswith('.cls-meta.xml') else 'body'
            name = path.name.removesuffix('.cls-meta.xml' if kind == 'xml' else '.cls')
            if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,39}', name):
                raise ModelError('Invalid Apex class filename')
            info = reader.inspect(path)
            limit = const.MAX_APEX_XML_BYTES if kind == 'xml' else const.MAX_APEX_SOURCE_BYTES
            if info.st_size > limit:
                raise ModelError('Apex file exceeds byte limit')
            candidates.setdefault((path.parent, name), {})[kind] = path
        # Validate duplicate identities and all metadata before selection filters.
        keys: set[str] = set()
        for (_, name), pair in sorted(candidates.items()):
            key = ComponentKey(binding.workspace_id, 'ApexClass', namespace, name)
            if key.token in keys:
                raise ConflictError('Duplicate canonical component mapping in local packages')
            keys.add(key.token)
            if 'xml' in pair:
                data = reader.read(pair['xml'], const.MAX_APEX_XML_BYTES)
                total_xml += len(data)
                if total_xml > const.MAX_LOCAL_XML_TOTAL_BYTES:
                    raise ModelError('Local project exceeds total XML byte limit')
                metadata = parse_apex_metadata(data)
                warnings.update(metadata.warnings)
            if pair.keys() != {'body', 'xml'}:
                partial = True
                warnings.add('missing_apex_pair')
                continue
            if (namespace and not selection.include_namespaced) or (selection.full_names and name not in selection.full_names):
                continue
            components.append(Component(binding, key, metadata.attributes, provenance=(const.LOCAL_APEX_METHOD,)))
        validate_identities(components)
        reader.verify()
    except FileNotFoundError as error:
        raise ConfigError('Required local project input is missing') from error
    except (OSError, RuntimeError) as error:
        raise OperationalError('Cannot safely read local project inputs') from error
    components.sort(key=lambda component: component.key.token)
    coverage = Coverage(
        binding,
        selection,
        CollectionCoverage(
            CoverageStatus.PARTIAL if partial else CoverageStatus.COMPLETE,
            const.LOCAL_APEX_METHOD,
            pagination='not_applicable',
            limit_reached=False,
            warnings=tuple(warnings),
        ),
        CollectionCoverage(
            CoverageStatus.UNAVAILABLE,
            'offline-audit-unavailable',
            requested=False,
            pagination='not_applicable',
            warnings=('salesforce_audit_unavailable',),
        ),
        CollectionCoverage(
            CoverageStatus.NOT_COLLECTED,
            'offline-relationships-uncollected',
            requested=False,
            pagination='not_applicable',
            warnings=('source_text_not_dependency_evidence',),
        ),
    )
    return LocalInventory(tuple(components), coverage)
