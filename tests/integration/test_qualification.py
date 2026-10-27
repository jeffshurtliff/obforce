# -*- coding: utf-8 -*-
"""
:Module:            tests.integration.test_qualification
:Synopsis:          Qualifies native refusal boundaries and finite synthetic scale offline
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     27 Oct 2026
"""

from __future__ import annotations

import os
import runpy
import socket
import stat
import subprocess
import sys
from pathlib import Path

import pytest

from obforce import constants as const
from obforce.errors import ConfigError, ConflictError, ModelError, OperationalError
from obforce.models import Selection, SourceBinding
from obforce.parsers.apex import parse_apex_metadata
from obforce.renderer.templates import TemplateAsset
from obforce.sources.local import collect_local
from obforce.sources.sf_cli import Limits
from obforce.sync.notes import parse_note
from obforce.sync.state import parse_state

DEV = Path(__file__).resolve().parents[2] / 'dev'
PROBE = runpy.run_path(str(DEV / 'probe_qualification.py'))
SCALE = runpy.run_path(str(DEV / 'qualify_scale.py'))


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    """Deny actual runtime network/process calls; no real Salesforce executable is used."""

    def deny(*args, **kwargs):
        raise AssertionError('Qualification runtime network/process forbidden')

    monkeypatch.setattr(socket, 'socket', deny)
    monkeypatch.setattr(socket, 'getaddrinfo', deny)
    monkeypatch.setattr(subprocess, 'Popen', deny)


def test_thousand_class_publication_refuses_without_setup(tmp_path):
    """Use real default bounds and public build; do not substitute a raised/reduced ceiling."""
    PROBE['publication_refusal'](tmp_path.resolve(), 1000)


def test_installed_qualification_probe(tmp_path, monkeypatch):
    """Share the wheel/sdist probe with the test suite and enforce no cwd artifacts."""
    monkeypatch.chdir(tmp_path)
    active = [True]

    def deny(event, args):
        if active[0] and (event.startswith('socket.') or event in {'subprocess.Popen', 'os.system', 'os.posix_spawn'}):
            raise RuntimeError('Qualification runtime network/process forbidden')

    sys.addaudithook(deny)
    try:
        PROBE['main']()
        assert list(tmp_path.iterdir()) == []
    finally:
        active[0] = False


def test_explicit_topology_and_batched_mocked_acquisition(tmp_path):
    """Verify independently queried synthetic org identity, edge direction and call budgets."""
    inventory, calls = SCALE['mocked_inventory'](401, tmp_path.resolve())
    assert calls == {'identity': 1, 'inventory': 4, 'audit_dates': 3}
    graph, coverage = SCALE['synthetic_graph'](inventory, 4010, 15)
    repeated, _ = SCALE['synthetic_graph'](inventory, 4010, 15)
    assert graph == repeated and len(graph.edges) == 4010
    assert all(edge.source.key != edge.target.key for edge in graph.edges)
    assert all(len(graph.references(c.key)) == len(graph.referenced_by(c.key)) == 10 for c in inventory.components)
    assert coverage.relationships.status == 'partial'
    measured = SCALE['mocked_relationship_budget'](inventory, tmp_path.resolve())
    assert measured['calls'] == 101 and measured['edges'] == 0
    assert any('budget' in warning for warning in measured['warnings'])


@pytest.mark.parametrize('location', ['source', 'config', 'vault'])
@pytest.mark.parametrize('kind', ['hardlink', 'symlink', 'fifo'])
def test_native_unsafe_files_block_public_build(tmp_path, location, kind):
    """Native filesystem objects refuse before publication, retaining existing information."""
    root = tmp_path.resolve()
    source, config, vault = PROBE['setup'](root, 1)
    if location == 'source':
        target = source / 'package/classes/Class0000.cls-meta.xml'
    elif location == 'config':
        target = config
    else:
        vault.mkdir(parents=True)
        target = vault / 'Unowned.md'
        target.write_bytes(b'Human content')
    outside = root / 'Unrelated.bin'
    original = target.read_bytes()
    outside.write_bytes(original)
    target.unlink()
    if kind == 'hardlink':
        target.hardlink_to(outside)
        assert target.stat().st_nlink == 2
    elif kind == 'symlink':
        try:
            target.symlink_to(outside)
        except OSError as error:
            if os.name == 'nt' and error.winerror == 1314:
                pytest.skip('Native Windows symlink privilege unavailable; refusal remains unqualified')
            raise
        assert target.is_symlink()
    else:
        if not hasattr(os, 'mkfifo'):
            pytest.skip('Native FIFO unavailable on this platform')
        os.mkfifo(target)
        assert stat.S_ISFIFO(target.lstat().st_mode)
    before = target.lstat(), outside.read_bytes(), outside.stat().st_mtime_ns
    for flags in (['--dry-run'], []):
        result = PROBE['invoke']('build', '--config', config, *flags)
        assert result.exit_code == (2 if location == 'source' else 3), (result.output, result.exception)
        assert (target.lstat(), outside.read_bytes(), outside.stat().st_mtime_ns) == before
        assert str(outside) not in result.output and original.decode() not in result.output
        assert not (vault / '.obforce').exists()


@pytest.mark.parametrize('location', ['source', 'config', 'vault'])
def test_native_posix_permission_denial_is_redacted_and_write_free(tmp_path, location):
    """Observe actual permission denial separately from injected I/O and Windows ACLs."""
    if os.name != 'posix':
        pytest.skip('POSIX mode denial is unavailable; this is not native Windows ACL qualification')
    source, config, vault = PROBE['setup'](tmp_path.resolve(), 1)
    target = source / 'package/classes/Class0000.cls-meta.xml' if location == 'source' else config
    if location == 'vault':
        vault.mkdir(parents=True)
        target = vault
    mode = stat.S_IMODE(target.stat().st_mode)
    target.chmod(0)
    try:
        try:
            list(target.iterdir()) if target.is_dir() else target.read_bytes()
        except PermissionError:
            pass
        else:
            pytest.skip('Current identity bypasses POSIX mode denial; no permission qualification')
        for flags in (['--dry-run'], []):
            result = PROBE['invoke']('build', '--config', config, *flags)
            assert result.exit_code == 1, (result.output, result.exception)
            assert str(target) not in result.output
    finally:
        target.chmod(mode)
    assert not (vault / '.obforce').exists()


def test_native_windows_junction_refuses_without_following(tmp_path):
    """Create a real junction only on an available Windows host; never shell out."""
    if os.name != 'nt':
        pytest.skip('Native Windows junction/reparse execution unavailable on this host')
    import _winapi

    source = SCALE['project'](tmp_path.resolve(), 1)
    outside = tmp_path / 'Unrelated Directory'
    outside.mkdir()
    (outside / 'Human.txt').write_bytes(b'Human data')
    junction = source / 'package/Junction'
    _winapi.CreateJunction(str(outside), str(junction))
    assert junction.is_junction()
    try:
        with pytest.raises(ConfigError, match='unsafe link'):
            collect_local(source, SourceBinding('native', 'local'), Selection())
        assert (outside / 'Human.txt').read_bytes() == b'Human data'
    finally:
        junction.rmdir()


@pytest.mark.parametrize(
    'payload',
    [
        b'x' * (const.MAX_APEX_XML_BYTES + 1),
        b'<!DOCTYPE ApexClass [<!ENTITY x "private-sentinel">]><ApexClass>&x;</ApexClass>',
        b'<ApexClass xmlns="http://soap.sforce.com/2006/04/metadata">' + b'<x>' * 17 + b'</x>' * 17 + b'</ApexClass>',
    ],
    ids=['xml-byte-limit', 'xml-forbidden-entity', 'xml-depth-limit'],
)
def test_actual_xml_limits_and_redaction(payload):
    with pytest.raises(ModelError) as error:
        parse_apex_metadata(payload)
    assert 'private-sentinel' not in str(error.value)


@pytest.mark.parametrize(
    'parser,payload,error_type',
    [
        (parse_state, b' ' * (const.MAX_STATE_BYTES + 1), ConflictError),
        (parse_state, b'{"private-sentinel":' + b'[' * 17 + b'0' + b']' * 17 + b'}', ConflictError),
        (parse_note, b'x' * (const.MAX_NOTE_BYTES + 1), ConflictError),
    ],
    ids=['state-byte-limit', 'state-depth-limit', 'note-byte-limit'],
)
def test_actual_state_and_note_limits(parser, payload, error_type):
    with pytest.raises(error_type) as error:
        parser(payload)
    assert 'private-sentinel' not in str(error.value)


def test_actual_template_and_time_output_ceilings():
    """Finite gates refuse actual over-ceiling input without changing shared constants."""
    with pytest.raises(ConfigError):
        TemplateAsset('apex_created.md.j2', 'x' * (const.MAX_TEMPLATE_BYTES + 1))
    for values in (
        {'timeout': 61},
        {'timeout': float('inf')},
        {'stdout': const.MAX_SF_STDOUT_BYTES + 1},
        {'stderr': const.MAX_SF_STDERR_BYTES + 1},
    ):
        with pytest.raises(ConfigError):
            Limits(**values)


@pytest.mark.parametrize('command', ['init', 'build', 'sync', 'recover'])
def test_click_path_readability_defers_to_redacted_guarded_errors(tmp_path, monkeypatch, command):
    """Inject access denial on every host, separate from native permission evidence."""
    from obforce.sync import engine

    private = tmp_path / 'private-path-sentinel.toml'
    private.write_bytes(b'private-value-sentinel')
    monkeypatch.setattr(os, 'access', lambda *args, **kwargs: False)

    def denied(*args, **kwargs):
        raise OperationalError('Explicit guarded read failed')

    monkeypatch.setattr(engine, 'initialize' if command == 'init' else command, denied)
    extra = ['--source', 'Synthetic', '--vault', 'Absent', '--workspace-id', 'synthetic'] if command == 'init' else []
    result = PROBE['invoke'](command, '--config', private, *extra)
    assert result.exit_code == 1 and 'Explicit guarded read failed' in result.output
    assert 'private-path-sentinel' not in result.output and 'private-value-sentinel' not in result.output
