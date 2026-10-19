# -*- coding: utf-8 -*-
"""
:Module:            tests.integration.test_local_source
:Synopsis:          Verifies offline DX acquisition and input preservation with fictional projects
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     19 Oct 2026
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
from pathlib import Path

import pytest

from obforce import constants as const
from obforce.errors import ConfigError, ConflictError, ExitCode, ModelError, OperationalError
from obforce.models import Availability, Selection, SourceBinding, component_fingerprint
from obforce.sources import local
from obforce.sources.local import collect_local

BINDING = SourceBinding('fictional-workspace', 'local')
XML = f'<ApexClass xmlns="{const.SALESFORCE_METADATA_NAMESPACE}"><apiVersion>67.0</apiVersion><status>Active</status></ApexClass>'


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    """Make socket/process use an immediate failure in every source test."""

    def deny(*args, **kwargs):
        raise AssertionError('Runtime network/process access forbidden')

    monkeypatch.setattr(socket, 'socket', deny)
    monkeypatch.setattr(socket, 'getaddrinfo', deny)
    monkeypatch.setattr(subprocess, 'Popen', deny)
    monkeypatch.setenv('PATH', '')


def manifest(root, paths=('one', 'two'), **extra):
    """Create a fictional project manifest and declared empty package directories."""
    root.mkdir(parents=True, exist_ok=True)
    for path in paths:
        (root / path).mkdir(parents=True, exist_ok=True)
    value = {'packageDirectories': [{'path': path} for path in paths], **extra}
    (root / 'sfdx-project.json').write_text(json.dumps(value), encoding='utf-8')
    return root


def pair(root, package='one', name='DemoService'):
    """Create one synthetic source/metadata pair."""
    directory = root / package / 'main/default/classes'
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f'{name}.cls').write_text(f'public class {name} {{}}', encoding='utf-8')
    (directory / f'{name}.cls-meta.xml').write_text(XML, encoding='utf-8')
    return directory


def snapshot(root):
    """Record every input's bytes and modification time, including directories."""
    return {
        str(path.relative_to(root)): (path.read_bytes() if path.is_file() else None, path.stat().st_mtime_ns)
        for path in [root, *root.rglob('*')]
    }


def test_determinism_relocation_and_no_writes(tmp_path):
    """Package order, body text, timestamps, and host paths cannot alter semantic hashes."""
    root = manifest(tmp_path / 'project')
    directory = pair(root, name='ZebraService')
    pair(root, 'two', 'AlphaService')
    before = snapshot(root)
    result = collect_local(root, BINDING, Selection())
    assert snapshot(root) == before
    assert [component.key.full_name for component in result.components] == ['AlphaService', 'ZebraService']
    assert result.inventory_hash == component_fingerprint(reversed(result.components))
    assert result.coverage.inventory.status == 'complete'
    assert result.coverage.audit.status == 'unavailable' and not result.coverage.audit.requested
    assert result.coverage.relationships.status == 'not_collected' and not result.coverage.relationships.requested
    assert result.coverage.outcome == ExitCode.SUCCESS
    assert 'local_scope_only' in result.coverage.inventory.warnings
    for component in result.components:
        assert component.record_id is None and component.collected_at is None
        assert component.provenance == (const.LOCAL_APEX_METHOD,)
        assert all(
            component.attributes[key].availability == Availability.UNAVAILABLE
            for key in ('created_at', 'created_by', 'last_modified_at', 'last_modified_by')
        )
    moved = tmp_path / 'moved'
    shutil.copytree(root, moved)
    manifest(moved, ('two', 'one'), unrelated={'url': 'https://invalid.example/not-fetched'})
    (moved / 'one/main/default/classes/ZebraService.cls').write_bytes(b'arbitrary source text without parsing')
    os.utime(moved / 'one/main/default/classes/ZebraService.cls', (1, 1))
    assert collect_local(moved, BINDING, Selection()).inventory_hash == result.inventory_hash
    (directory / 'ZebraService.cls-meta.xml').write_text(XML.replace('67.0', '66.0'), encoding='utf-8')
    assert collect_local(root, BINDING, Selection()).inventory_hash != result.inventory_hash


@pytest.mark.parametrize('missing', ['body', 'xml'])
def test_missing_pair_is_partial(tmp_path, missing):
    root = manifest(tmp_path / 'project')
    directory = pair(root)
    (directory / ('DemoService.cls' if missing == 'body' else 'DemoService.cls-meta.xml')).unlink()
    result = collect_local(root, BINDING, Selection())
    assert not result.components
    assert result.coverage.inventory.status == 'partial'
    assert result.coverage.outcome == ExitCode.INCOMPLETE
    assert 'missing_apex_pair' in result.coverage.inventory.warnings
    assert not result.coverage.audit.requested and not result.coverage.relationships.requested


def test_namespaces_filters_and_unavailable_metadata(tmp_path):
    root = manifest(tmp_path / 'project', namespace='Demo')
    directory = pair(root)
    excluded = collect_local(root, BINDING, Selection())
    assert not excluded.components
    assert 'namespaced_components_excluded' in excluded.coverage.inventory.warnings
    included = collect_local(root, BINDING, Selection(True))
    assert included.components[0].key.namespace == 'Demo'
    assert included.coverage.scope_hash != excluded.coverage.scope_hash
    assert not collect_local(root, BINDING, Selection(True, ('Other',))).components
    (directory / 'DemoService.cls-meta.xml').write_text(XML.replace('<apiVersion>67.0</apiVersion>', ''), encoding='utf-8')
    missing = collect_local(root, BINDING, Selection(True))
    assert missing.components[0].attributes['api_version'].availability == Availability.UNAVAILABLE
    assert missing.coverage.inventory.status == 'complete'
    assert 'metadata_fields_unavailable' in missing.coverage.inventory.warnings


def test_empty_and_unsupported_packages(tmp_path):
    root = manifest(tmp_path / 'project')
    result = collect_local(root, BINDING, Selection())
    assert result.components == () and result.coverage.inventory.status == 'complete'
    assert 'empty_package' in result.coverage.inventory.warnings
    (root / 'two/Demo.trigger').write_text('unsupported', encoding='utf-8')
    (root / 'two/Outside.cls').write_text('not a supported classes directory', encoding='utf-8')
    result = collect_local(root, BINDING, Selection())
    assert not result.components and 'unsupported_files_excluded' in result.coverage.inventory.warnings


@pytest.mark.parametrize(
    'data',
    [
        '',
        '[]',
        '{}',
        '{"packageDirectories":[]}',
        '{"packageDirectories":true}',
        '{"packageDirectories":[{}]}',
        '{"packageDirectories":["one"]}',
        '{"packageDirectories":[{"path":"one","path":"two"}]}',
        '{"packageDirectories":[{"path":"one"}],"x":NaN}',
        '{"packageDirectories":[{"path":"one"}],"namespace":null}',
        '{"packageDirectories":[{"path":"one"}],"namespace":"bad_namespace"}',
        '{"packageDirectories":[{"path":"one"}],"namespace":true}',
        '{"packageDirectories":[{"path":"one"}],"namespace":"toolongnamespacex"}',
    ],
)
def test_bad_manifests(tmp_path, data):
    root = manifest(tmp_path / 'project')
    (root / 'sfdx-project.json').write_text(data, encoding='utf-8')
    with pytest.raises(ConfigError):
        collect_local(root, BINDING, Selection())


@pytest.mark.parametrize(
    'path',
    [
        '../escape',
        '/absolute',
        'C:/drive',
        'one/../two',
        'one//two',
        '.',
        'one\\two',
        'one/',
        'CON',
        'one/.git',
        'bad:name',
        'trailing.',
    ],
)
def test_bad_package_paths(tmp_path, path):
    root = manifest(tmp_path / 'project')
    (root / 'sfdx-project.json').write_text(json.dumps({'packageDirectories': [{'path': path}]}), encoding='utf-8')
    with pytest.raises(ConfigError):
        collect_local(root, BINDING, Selection())


@pytest.mark.parametrize('paths', [('one', 'one'), ('one', 'one/nested'), ('one', 'ONE/nested')])
def test_overlapping_package_paths(tmp_path, paths):
    root = manifest(tmp_path / 'project', paths)
    with pytest.raises(ConflictError):
        collect_local(root, BINDING, Selection())


def test_duplicate_identities_before_filtering(tmp_path):
    root = manifest(tmp_path / 'project', namespace='Demo')
    pair(root)
    pair(root, 'two')
    with pytest.raises(ConflictError):
        collect_local(root, BINDING, Selection())


@pytest.mark.parametrize('location', ['package', 'ancestor', 'xml', 'body', 'unsupported', 'manifest', 'root'])
def test_links_refused(tmp_path, location):
    root = manifest(tmp_path / 'project')
    directory = pair(root)
    target = tmp_path / 'outside'
    target.mkdir()
    if location == 'root':
        link = tmp_path / 'project-link'
        destination = root
    elif location in {'package', 'ancestor'}:
        link = root / ('two' if location == 'package' else 'one/main')
        shutil.rmtree(link)
        destination = target
    else:
        link = {
            'xml': directory / 'DemoService.cls-meta.xml',
            'body': directory / 'DemoService.cls',
            'unsupported': directory / 'Other.file',
            'manifest': root / 'sfdx-project.json',
        }[location]
        link.unlink(missing_ok=True)
        destination = target / 'payload'
        destination.write_text(XML, encoding='utf-8')
    try:
        link.symlink_to(destination, target_is_directory=destination.is_dir())
    except OSError:
        pytest.skip('Native symlink creation unavailable; link refusal not qualified on this host')
    with pytest.raises(ConfigError):
        collect_local(link if location == 'root' else root, BINDING, Selection())


def test_special_file_refused(tmp_path):
    if not hasattr(os, 'mkfifo'):
        pytest.skip('Native FIFO creation unavailable on this host')
    root = manifest(tmp_path / 'project')
    os.mkfifo(root / 'one/pipe')
    with pytest.raises(ConfigError):
        collect_local(root, BINDING, Selection())


@pytest.mark.parametrize(
    'limit,value',
    [
        ('MAX_PROJECT_BYTES', 1),
        ('MAX_LOCAL_ENTRIES', 1),
        ('MAX_LOCAL_DEPTH', 2),
        ('MAX_LOCAL_PACKAGES', 1),
        ('MAX_APEX_XML_BYTES', 1),
        ('MAX_APEX_SOURCE_BYTES', 1),
        ('MAX_LOCAL_XML_TOTAL_BYTES', 1),
    ],
)
def test_limits_refuse_without_truncation(tmp_path, monkeypatch, limit, value):
    root = manifest(tmp_path / 'project')
    pair(root)
    monkeypatch.setattr(const, limit, value)
    with pytest.raises(ConfigError):
        collect_local(root, BINDING, Selection())


def test_missing_paths_and_invalid_selection(tmp_path):
    root = manifest(tmp_path / 'project')
    with pytest.raises(ConfigError):
        collect_local(Path('relative'), BINDING, Selection())
    with pytest.raises(ConfigError):
        collect_local(root, SourceBinding('fictional-workspace', 'live', 'fictional-org'), Selection())
    with pytest.raises(ConfigError):
        collect_local(root, BINDING, None)
    (root / 'one').rmdir()
    with pytest.raises(ConfigError):
        collect_local(root, BINDING, Selection())


def test_unreadable_and_changed_inputs(tmp_path, monkeypatch):
    root = manifest(tmp_path / 'project')
    directory = pair(root)
    original = local._Reader.read

    def changed(reader, path, limit):
        data = original(reader, path, limit)
        if path.name.endswith('.xml'):
            (directory / 'DemoService.cls').write_text('intervening edit', encoding='utf-8')
        return data

    monkeypatch.setattr(local._Reader, 'read', changed)
    with pytest.raises(OperationalError):
        collect_local(root, BINDING, Selection())
    assert (directory / 'DemoService.cls').read_text() == 'intervening edit'

    def denied(*args, **kwargs):
        raise PermissionError('sensitive diagnostic')

    monkeypatch.setattr(local.os, 'scandir', denied)
    with pytest.raises(OperationalError, match='Cannot safely read') as error:
        collect_local(root, BINDING, Selection())
    assert 'sensitive' not in str(error.value)


def test_bodies_never_opened_and_parser_failure_safe(tmp_path, monkeypatch):
    root = manifest(tmp_path / 'project')
    directory = pair(root)
    original = local.os.open

    def guarded(path, *args, **kwargs):
        assert not str(path).endswith('.cls')
        return original(path, *args, **kwargs)

    monkeypatch.setattr(local.os, 'open', guarded)
    collect_local(root, BINDING, Selection())
    (directory / 'DemoService.cls-meta.xml').write_text('<secret-malformed>', encoding='utf-8')
    with pytest.raises(ModelError) as error:
        collect_local(root, BINDING, Selection())
    assert 'secret' not in str(error.value) and str(root) not in str(error.value)


def test_fictional_multi_package_example(tmp_path):
    """The checked-in sample works after relocation without touching checkout bytes."""
    sample = Path(__file__).parents[2] / 'examples/sample_sfdx'
    root = tmp_path / 'sample'
    shutil.copytree(sample, root)
    before = snapshot(root)
    result = collect_local(root, BINDING, Selection())
    assert [component.key.full_name for component in result.components] == ['DemoExtension', 'DemoService']
    assert result.inventory_hash == 'f6ec88ca3498e1d77710fe4701e54d7e7fc26528249a57cacb7a673bb1c65270'
    assert snapshot(root) == before and result.coverage.outcome == ExitCode.SUCCESS


def test_invalid_filename_and_portable_collisions(tmp_path):
    root = manifest(tmp_path / 'project')
    directory = pair(root, name='bad-name')
    with pytest.raises(ModelError):
        collect_local(root, BINDING, Selection())
    shutil.rmtree(directory)
    directory = pair(root)
    (directory / 'demoService.cls').write_text('fictional case collision', encoding='utf-8')
    if len(list(directory.glob('*.cls'))) == 2:
        with pytest.raises(ConflictError):
            collect_local(root, BINDING, Selection())
    else:
        manifest(root, ('one', 'ONE'))
        with pytest.raises(ConflictError):
            collect_local(root, BINDING, Selection())


def test_hardlinks_refused(tmp_path):
    root = manifest(tmp_path / 'project')
    outside = tmp_path / 'outside'
    outside.write_text('fictional hardlink target', encoding='utf-8')
    os.link(outside, root / 'one/linked')
    with pytest.raises(ConfigError):
        collect_local(root, BINDING, Selection())


def test_disappearing_input_refuses_result(tmp_path, monkeypatch):
    root = manifest(tmp_path / 'project')
    directory = pair(root)
    original = local._Reader.verify

    def removed(reader):
        (directory / 'DemoService.cls').unlink()
        original(reader)

    monkeypatch.setattr(local._Reader, 'verify', removed)
    with pytest.raises(OperationalError):
        collect_local(root, BINDING, Selection())


def test_nested_manifest_and_wrong_package_kind(tmp_path):
    root = manifest(tmp_path / 'project')
    manifest_path = root / 'sfdx-project.json'
    manifest_path.write_text('[' * 1500 + '0' + ']' * 1500, encoding='utf-8')
    with pytest.raises(ConfigError):
        collect_local(root, BINDING, Selection())
    manifest(root)
    (root / 'one').rmdir()
    (root / 'one').write_text('not a directory', encoding='utf-8')
    with pytest.raises(ConfigError):
        collect_local(root, BINDING, Selection())
