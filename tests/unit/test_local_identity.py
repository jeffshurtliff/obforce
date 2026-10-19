# -*- coding: utf-8 -*-
"""
:Module:            tests.unit.test_local_identity
:Synopsis:          Verifies narrow Windows path and descriptor identity compatibility
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     19 Oct 2026
"""

from __future__ import annotations

import stat
from types import SimpleNamespace

import pytest

from obforce.sources import local


def metadata(**changes):
    """Supply deterministic synthetic file metadata without native platform claims."""
    values = dict(st_dev=1, st_ino=2, st_mode=stat.S_IFREG | 0o600, st_size=3, st_mtime_ns=4, st_ctime_ns=5)
    return SimpleNamespace(**(values | changes))


@pytest.mark.parametrize('platform', ['nt', 'posix'])
def test_exact_descriptor_identity(platform, monkeypatch):
    """An exact original fingerprint remains valid on either platform."""
    monkeypatch.setitem(vars(local), 'os', SimpleNamespace(name=platform))
    assert local._matches_descriptor(metadata(), metadata())


@pytest.mark.parametrize('platform,expected', [('nt', True), ('posix', False)])
def test_birthtime_bridge_is_windows_only(platform, expected, monkeypatch):
    """Only Windows permits exact creation time to explain the ctime mismatch."""
    monkeypatch.setitem(vars(local), 'os', SimpleNamespace(name=platform))
    assert local._matches_descriptor(metadata(), metadata(st_ctime_ns=9, st_birthtime_ns=5)) is expected


@pytest.mark.parametrize('birthtime', [None, True, 5.0, '5', 4, 6])
def test_birthtime_bridge_requires_exact_integer(birthtime, monkeypatch):
    """Missing, coerced, rounded, or different birthtime never explains a mismatch."""
    monkeypatch.setitem(vars(local), 'os', SimpleNamespace(name='nt'))
    assert not local._matches_descriptor(metadata(), metadata(st_ctime_ns=9, st_birthtime_ns=birthtime))


@pytest.mark.parametrize(
    'field,value',
    [
        ('st_dev', 2),
        ('st_ino', 3),
        ('st_mode', stat.S_IFDIR | 0o600),
        ('st_mode', stat.S_IFREG | 0o400),
        ('st_size', 4),
        ('st_mtime_ns', 5),
    ],
)
def test_birthtime_bridge_preserves_other_identity_fields(field, value, monkeypatch):
    """Matching birthtime cannot hide replacement, mode, size, or mtime changes."""
    monkeypatch.setitem(vars(local), 'os', SimpleNamespace(name='nt'))
    assert not local._matches_descriptor(metadata(), metadata(**{field: value}, st_ctime_ns=9, st_birthtime_ns=5))
