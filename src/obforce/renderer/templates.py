# -*- coding: utf-8 -*-
"""
:Module:            obforce.renderer.templates
:Synopsis:          Loads known installed templates and enforces finite Jinja interpolation
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     20 Oct 2026
"""

from __future__ import annotations

import hashlib
import os
import stat
import unicodedata
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

from jinja2 import StrictUndefined, TemplateError, nodes
from jinja2.sandbox import ImmutableSandboxedEnvironment

from obforce import constants as const
from obforce.errors import ConfigError, OperationalError


class _Sandbox(ImmutableSandboxedEnvironment):
    """Deny all Python attribute and callable access in addition to the AST gate."""

    def is_safe_attribute(self, obj: object, attr: str, value: object) -> bool:
        return False

    def is_safe_callable(self, obj: object) -> bool:
        return False


def _section(value: str) -> str:
    """Accept only already serialized engine sections, never arbitrary objects."""
    if type(value) is not str:
        raise ConfigError('Template context must contain only serialized sections')
    return value


def _environment() -> _Sandbox:
    """Create a fresh loader-free environment with no default capabilities."""
    environment = _Sandbox(undefined=StrictUndefined, autoescape=False, keep_trailing_newline=True)
    environment.globals.clear()
    environment.filters.clear()
    environment.filters['section'] = _section
    environment.tests.clear()
    return environment


def _check_stat(info: os.stat_result, *, directory: bool) -> None:
    """Refuse links/reparse points, special files and multiply linked files."""
    if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
        raise ConfigError('Unsafe template path')
    if not (stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode) and info.st_nlink == 1):
        raise ConfigError('Unsafe template file or root')


def _identity(info: os.stat_result) -> tuple[int, ...]:
    """Compare portable pathname/descriptor evidence without mixing Windows ctime meanings."""
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns)


def _override(root: Path, name: str) -> bytes | None:
    """Read only one known file under an explicit root, without recursive discovery."""
    if not isinstance(root, Path) or not root.is_absolute() or '..' in root.parts:
        raise ConfigError('Template override root must be explicit and absolute')
    try:
        parents = (*reversed(root.parents), root)
        before = []
        missing = False
        for parent in parents:
            try:
                info = parent.lstat()
            except FileNotFoundError:
                missing = True
                break
            _check_stat(info, directory=True)
            before.append((parent, _identity(info)))
        if missing:
            return None
        path = root / name
        try:
            info = path.lstat()
        except FileNotFoundError:
            return None
        _check_stat(info, directory=False)
        if info.st_size > const.MAX_TEMPLATE_BYTES:
            raise ConfigError('Template exceeds byte bound')
        flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
        descriptor_number = os.open(path, flags)
        with os.fdopen(descriptor_number, 'rb') as stream:
            descriptor = os.fstat(stream.fileno())
            _check_stat(descriptor, directory=False)
            if _identity(info) != _identity(descriptor):
                raise ConfigError('Template changed during read')
            raw = stream.read(const.MAX_TEMPLATE_BYTES + 1)
            if _identity(descriptor) != _identity(os.fstat(stream.fileno())):
                raise ConfigError('Template changed during read')
        if _identity(info) != _identity(path.lstat()) or any(_identity(p.lstat()) != stamp for p, stamp in before):
            raise ConfigError('Template path changed during read')
        return raw
    except OSError as error:
        raise OperationalError('Cannot read explicit template override') from error


@dataclass(frozen=True, repr=False)
class TemplateAsset:
    """Hold bounded validated template text; loading never executes a template."""

    name: str
    text: str

    def __post_init__(self) -> None:
        """Validate known names, UTF-8, finite interpolation syntax and required slots."""
        if self.name not in const.TEMPLATE_SLOTS or type(self.text) is not str:
            raise ConfigError('Unknown template or invalid content')
        try:
            if len(self.text) > const.MAX_TEMPLATE_BYTES or len(self.text.encode('utf-8')) > const.MAX_TEMPLATE_BYTES:
                raise ConfigError('Template exceeds byte bound')
            if (
                any((unicodedata.category(char) in {'Cc', 'Cs', 'Cf', 'Zl', 'Zp'} and char != '\n') for char in self.text)
                or 'obforce:' in self.text
            ):
                raise ConfigError('Template contains reserved or invalid structure')
            if any(
                line.strip() in {'---', '...'} or line.lstrip().startswith(('obforce_', 'sf_')) for line in self.text.splitlines()
            ):
                raise ConfigError('Templates cannot supply frontmatter or reserved properties')
            tree = _environment().parse(self.text)
            items = list(tree.find_all(nodes.Node))
            if len(items) > const.MAX_TEMPLATE_NODES:
                raise ConfigError('Template exceeds syntax bound')
            if any(type(item) not in {nodes.Output, nodes.TemplateData, nodes.Name, nodes.Filter} for item in items):
                raise ConfigError('Template syntax is outside the finite interpolation contract')
            names = []
            for output in tree.body:
                if type(output) is not nodes.Output:
                    raise ConfigError('Template statements are unsupported')
                for item in output.nodes:
                    if type(item) is nodes.TemplateData:
                        continue
                    if (
                        type(item) is not nodes.Filter
                        or item.name != 'section'
                        or type(item.node) is not nodes.Name
                        or item.args
                        or item.kwargs
                        or item.dyn_args is not None
                        or item.dyn_kwargs is not None
                    ):
                        raise ConfigError('Templates require explicit section interpolation')
                    names.append(item.node.name)
            if sorted(names) != sorted(const.TEMPLATE_SLOTS[self.name]):
                raise ConfigError('Template must retain each required section exactly once')
        except (UnicodeError, TemplateError, RecursionError) as error:
            raise ConfigError('Invalid bounded Jinja template') from error

    @property
    def content_hash(self) -> str:
        """Hash exact template bytes without path, mtime or checkout identity."""
        return hashlib.sha256(self.text.encode('utf-8')).hexdigest()

    def render(self, context: dict[str, str]) -> str:
        """Render primitive sections under strict finite limits, returning only text.

        :raises ConfigError: For invalid context, template failure or output overflow.
        """
        if type(context) is not dict or set(context) != set(const.TEMPLATE_SLOTS[self.name]):
            raise ConfigError('Invalid template context keys')
        if any(type(value) is not str for value in context.values()):
            raise ConfigError('Invalid template context values')
        try:
            if sum(len(value.encode('utf-8')) for value in context.values()) > const.MAX_RENDER_SECTION_BYTES:
                raise ConfigError('Template context exceeds byte bound')
            result = _environment().from_string(self.text).render(context).rstrip('\n') + '\n'
            if len(result.encode('utf-8')) > const.MAX_RENDER_SECTION_BYTES:
                raise ConfigError('Rendered section exceeds byte bound')
            return result
        except (TemplateError, UnicodeError, RecursionError, ValueError, TypeError) as error:
            raise ConfigError('Bounded template rendering failed') from error


def load_template(name: str, directory: Path | None = None) -> TemplateAsset:
    """Load exactly a known override or installed default, never a metadata filename.

    :param directory: Explicit absolute local root; missing known files fall back.
    :raises ConfigError: For unknown names or invalid existing override content.
    :raises OperationalError: For read failures; these never fall back.
    """
    if name not in const.TEMPLATE_SLOTS:
        raise ConfigError('Unknown template name')
    raw = None if directory is None else _override(directory, name)
    if raw is None:
        try:
            with files('obforce').joinpath('resources', 'templates', name).open('rb') as stream:
                raw = stream.read(const.MAX_TEMPLATE_BYTES + 1)
        except OSError as error:
            raise OperationalError('Cannot read installed template resource') from error
    try:
        return TemplateAsset(name, raw.decode('utf-8'))
    except UnicodeError as error:
        raise ConfigError('Template must be valid UTF-8') from error
