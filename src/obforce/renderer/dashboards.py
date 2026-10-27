# -*- coding: utf-8 -*-
"""
:Module:            obforce.renderer.dashboards
:Synopsis:          Loads one bounded literal native Apex dashboard without publication
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     26 Oct 2026
"""

from __future__ import annotations

from importlib.resources import files

from obforce import constants as const
from obforce.config import Layout
from obforce.errors import ModelError, OperationalError
from obforce.renderer.notes import _path


def validate_dashboard_path(path: str) -> str:
    """Require the known filename with the accepted portable link-safe path policy."""
    if type(path) is not str or path.split('/')[-1] != const.DASHBOARD_FILENAME:
        raise ModelError('Invalid managed dashboard path')
    # The longer suffix also receives the original path/segment byte limits.
    _path(path + '.md')
    return path


def dashboard_path(layout: Layout) -> str:
    """Return the explicit configured destination, independent of note locations."""
    if not isinstance(layout, Layout):
        raise ModelError('Expected normalized dashboard layout')
    return validate_dashboard_path(f'{layout.dashboards}/{const.DASHBOARD_FILENAME}')


def validate_dashboard_content(raw: bytes) -> None:
    """Bound exact saved UTF-8/LF content; do not execute or normalize it."""
    if (
        type(raw) is not bytes
        or not len(const.DASHBOARD_MARKER) < len(raw) <= const.MAX_DASHBOARD_BYTES
        or not raw.startswith(const.DASHBOARD_MARKER)
        or raw.lower().count(b'obforce:dashboard') != 1
        or b'\r' in raw
        or not raw.endswith(b'\n')
    ):
        raise ModelError('Invalid managed dashboard content')
    text = raw.decode('utf-8')
    if any(ord(c) < 32 and c != '\n' for c in text) or '\ufeff' in text:
        raise ModelError('Invalid dashboard encoding or controls')


def render_dashboard() -> bytes:
    """Read one installed literal asset with no overrides, metadata or side effects."""
    try:
        asset = files('obforce').joinpath('resources', 'bases', 'apex_classes.base')
        with asset.open('rb') as stream:
            raw = stream.read(const.MAX_DASHBOARD_BYTES + 1)
        validate_dashboard_content(raw)
        return raw
    except (OSError, UnicodeError):
        raise OperationalError('Cannot load packaged Apex dashboard') from None
