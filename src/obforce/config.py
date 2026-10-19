# -*- coding: utf-8 -*-
"""
:Module:            obforce.config
:Synopsis:          Loads explicit strict TOML configuration without filesystem writes
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     19 Oct 2026
"""

import re
import tomllib
import unicodedata
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Literal

from obforce import constants as const
from obforce.errors import ConfigError, OperationalError


def _text(value: object, label: str) -> str:
    """Require nonempty trimmed text without control characters."""
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or any(unicodedata.category(char) in {'Cc', 'Cs'} for char in value)
    ):
        raise ConfigError(f'{label} must be nonempty text without surrounding whitespace or controls')
    return value


def relative_path(value: object) -> str:
    """Validate a portable vault-relative path without consulting the filesystem.

    :param value: Slash-separated path, also used for future note-state records.
    :returns: Unchanged validated path.
    :raises ConfigError: For traversal, absolute, reserved, or nonportable names.
    """
    path = _text(value, 'Relative path')
    if '\\' in path or PurePosixPath(path).is_absolute() or PureWindowsPath(path).drive:
        raise ConfigError('Expected a portable vault-relative path')
    for part in path.split('/'):
        if part.casefold() in {'.obsidian', '.obforce', '.git'}:
            raise ConfigError('Reserved vault control directory')
        if part in ('', '.', '..') or part.endswith(('.', ' ')) or any(char in '<>:"|?*' for char in part):
            raise ConfigError('Invalid relative path segment')
        stem = part.split('.')[0].upper()
        if stem in {'CON', 'PRN', 'AUX', 'NUL'} or re.fullmatch(r'(COM|LPT)[1-9¹²³]', stem):
            raise ConfigError('Reserved relative path segment')
    return path


def _resolve(value: object, base: Path) -> Path:
    """Resolve an explicit native path from the config directory without creating it."""
    raw = _text(value, 'Path')
    if raw.startswith('~') or '$' in raw or '%' in raw:
        raise ConfigError('Path expansion is unsupported; use a literal path')
    path = Path(raw)
    if not path.is_absolute() and (PureWindowsPath(raw).drive or '\\' in raw):
        raise ConfigError('Path is not native to this platform')
    try:
        return (base / path).resolve()
    except (OSError, RuntimeError, ValueError) as error:
        raise ConfigError('Path cannot be resolved') from error


def _table(value: object, allowed: set[str], required: set[str], label: str) -> dict[str, Any]:
    """Reject unknown/missing keys and scalar replacements for known TOML tables."""
    if not isinstance(value, dict) or value.keys() - allowed or required - value.keys():
        raise ConfigError(f'Invalid keys or table structure in {label}')
    return value


def _boolean(value: object, label: str) -> bool:
    """Require a TOML boolean rather than a truthy scalar."""
    if type(value) is not bool:
        raise ConfigError(f'{label} must be a boolean')
    return value


@dataclass(frozen=True)
class SourceSelection:
    """Describe one explicit source selector without authentication or acquisition."""

    mode: Literal['local', 'live']
    project: Path | None = None
    org: str | None = None

    def __post_init__(self) -> None:
        """Refuse absent, contradictory, and mode-incompatible selectors."""
        if self.mode == 'local' and isinstance(self.project, Path) and self.project.is_absolute() and self.org is None:
            return
        if self.mode == 'live' and self.project is None and self.org is not None:
            _text(self.org, 'Live org selector')
            if self.org.startswith('-'):
                raise ConfigError('Live org selector cannot begin with a hyphen')
            return
        raise ConfigError('Source requires exactly one mode-compatible explicit selector')


@dataclass(frozen=True)
class Layout:
    """Hold portable vault-relative generated directories for future renderers."""

    apex_classes: str = const.DEFAULT_APEX_DIRECTORY
    dashboards: str = const.DEFAULT_DASHBOARD_DIRECTORY

    def __post_init__(self) -> None:
        """Validate both directories, without creating or probing a vault."""
        relative_path(self.apex_classes)
        relative_path(self.dashboards)


@dataclass(frozen=True)
class Options:
    """Hold explicit namespace scope and audit-label privacy choices."""

    include_namespaced: bool = False
    include_audit_names: bool = True

    def __post_init__(self) -> None:
        """Keep false distinct from missing and reject non-booleans."""
        _boolean(self.include_namespaced, 'include_namespaced')
        _boolean(self.include_audit_names, 'include_audit_names')


@dataclass(frozen=True)
class Config:
    """Hold validated config paths and selection; this record grants no live access."""

    path: Path
    workspace_id: str
    vault: Path
    source: SourceSelection
    layout: Layout
    options: Options
    template_directory: Path | None = None


def select_source(config: Config | None = None, *, project: Path | None = None, org: str | None = None) -> SourceSelection:
    """Apply supported explicit selectors before config, refusing source-mode switches.

    Paths supplied by a future CLI are resolved by its caller. A live org override
    remains subject to verified org-binding checks after acquisition.

    :param config: Previously validated config, or none during future initialization.
    :param project: Absolute offline path; cannot override an existing config.
    :param org: Explicit live target override; cannot switch local mode to live.
    :returns: Exactly one source selection, never a machine default.
    :raises ConfigError: If selectors conflict or no source is selected.
    """
    if project is not None and org is not None:
        raise ConfigError('Source selectors are mutually exclusive')
    if config is None:
        return SourceSelection('local' if project is not None else 'live', project, org)
    if project is not None or (org is not None and config.source.mode != 'live'):
        raise ConfigError('Configured source cannot be switched by invocation')
    return SourceSelection('live', org=org) if org is not None else config.source


def load_config(path: Path) -> Config:
    """Read one explicit TOML file and validate version-one keys, types, and paths.

    No discovery, fallback, environment expansion, directory creation, or source
    inspection occurs. Destination existence and publication safety are later gates.

    :param path: Explicit config file; relative file names use the caller's cwd.
    :returns: Immutable normalized configuration.
    :raises ConfigError: For missing/invalid/oversized config or invalid paths.
    :raises OperationalError: For read permission and other filesystem failures.
    """
    try:
        config_path = path.resolve()
        with config_path.open('rb') as stream:
            raw = stream.read(const.MAX_CONFIG_BYTES + 1)
    except FileNotFoundError as error:
        raise ConfigError('Explicit configuration file does not exist') from error
    except (OSError, RuntimeError, ValueError) as error:
        raise OperationalError('Cannot read explicit configuration file') from error
    if len(raw) > const.MAX_CONFIG_BYTES:
        raise ConfigError('Configuration exceeds size limit')
    try:
        data = tomllib.loads(raw.decode('utf-8'))
    except (UnicodeError, tomllib.TOMLDecodeError, RecursionError) as error:
        raise ConfigError('Configuration is not valid UTF-8 TOML') from error
    root = _table(
        data,
        {'schema_version', 'workspace_id', 'vault', 'source', 'layout', 'options', 'templates'},
        {'schema_version', 'workspace_id', 'vault', 'source'},
        'config',
    )
    if type(root['schema_version']) is not int or root['schema_version'] != const.CONFIG_SCHEMA_VERSION:
        raise ConfigError('Unsupported configuration schema_version')
    workspace = _text(root['workspace_id'], 'workspace_id')
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', workspace):
        raise ConfigError('workspace_id must contain 1–128 ASCII letters, digits, underscores, or hyphens')
    base = config_path.parent
    source = _table(root['source'], {'mode', 'project', 'org'}, {'mode'}, 'source')
    selection = SourceSelection(
        source['mode'], _resolve(source['project'], base) if 'project' in source else None, source.get('org')
    )
    layout = _table(root.get('layout', {}), {'apex_classes', 'dashboards'}, set(), 'layout')
    options = _table(root.get('options', {}), {'include_namespaced', 'include_audit_names'}, set(), 'options')
    templates = _table(root['templates'], {'directory'}, {'directory'}, 'templates') if 'templates' in root else None
    result = Config(
        config_path,
        workspace,
        _resolve(root['vault'], base),
        selection,
        Layout(**layout),
        Options(**options),
        _resolve(templates['directory'], base) if templates is not None else None,
    )
    protected = [config_path, selection.project, result.template_directory]
    for other in protected:
        if other is not None and (other.is_relative_to(result.vault) or result.vault.is_relative_to(other)):
            raise ConfigError('Vault must not overlap config, source, or template roots')
    return result
