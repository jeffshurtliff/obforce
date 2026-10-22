# -*- coding: utf-8 -*-
"""
:Module:            dev.check_artifacts
:Synopsis:          Inspects fresh distributions and checks independent installations
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     21 Oct 2026
"""

from __future__ import annotations

import argparse
import configparser
import hashlib
import json
import os
import subprocess
import tarfile
import tempfile
import tomllib
import venv
import zipfile
from email.parser import BytesParser
from pathlib import Path


def _run(command: list[str], cwd: Path, environment: dict[str, str]) -> str:
    """Run a bounded validation command and include captured output on failure.

    :param command: Executable and arguments without shell interpolation.
    :param cwd: Temporary working directory.
    :param environment: Explicit child environment.
    :returns: Standard output from a successful command.
    :raises RuntimeError: If the child exits unsuccessfully.
    :raises subprocess.TimeoutExpired: If the command exceeds its time limit.
    """
    result = subprocess.run(command, cwd=cwd, env=environment, capture_output=True, text=True, timeout=180, check=False)
    if result.returncode:
        raise RuntimeError(f'Command failed ({result.returncode}): {command}\n{result.stdout}\n{result.stderr}')
    return result.stdout


def _inspect(artifact: Path, version: str, license_bytes: bytes) -> None:
    """Enforce the explicit foundation, contract, source, CLI-boundary and graph artifact allowlist.

    :param artifact: Locally built wheel or sdist to inspect without extraction.
    :param version: Expected static project version.
    :param license_bytes: Unmodified root license for exact comparison.
    :raises ValueError: If archive contents or metadata violate the allowlist.
    """
    package_files = {'__init__.py', '__main__.py', 'cli.py', 'config.py', 'constants.py', 'errors.py', 'models.py'}
    package_files.update(
        {
            'parsers/__init__.py',
            'parsers/apex.py',
            'sources/__init__.py',
            'sources/local.py',
            'sources/sf_cli.py',
            'sources/live.py',
            'sources/relationships.py',
            'graph/__init__.py',
            'graph/dependencies.py',
            'renderer/__init__.py',
            'renderer/templates.py',
            'renderer/notes.py',
            'sync/__init__.py',
            'sync/notes.py',
            'sync/state.py',
            'sync/planner.py',
            'sync/reporting.py',
            'sync/transactions.py',
            'sync/engine.py',
            'resources/templates/apex_created.md.j2',
            'resources/templates/apex_generated.md.j2',
        }
    )
    if artifact.suffix == '.whl':
        metadata_root = f'obforce-{version}.dist-info/'
        expected = {f'obforce/{name}' for name in package_files} | {
            f'{metadata_root}{name}' for name in ('METADATA', 'WHEEL', 'entry_points.txt', 'RECORD', 'licenses/LICENSE')
        }
        with zipfile.ZipFile(artifact) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)) or set(names) != expected:
                raise ValueError(f'Unexpected wheel members: {names}')
            content = {name: archive.read(name) for name in names}
        metadata = BytesParser().parsebytes(content[f'{metadata_root}METADATA'])
        actual_license = content[f'{metadata_root}licenses/LICENSE']
        entry_points = configparser.ConfigParser()
        entry_points.read_string(content[f'{metadata_root}entry_points.txt'].decode())
        if entry_points.get('console_scripts', 'obforce') != 'obforce.cli:main':
            raise ValueError('Missing console entry point')
    else:
        root = f'obforce-{version}/'
        expected = {f'{root}src/obforce/{name}' for name in package_files} | {
            f'{root}{name}' for name in ('LICENSE', 'README.md', 'pyproject.toml', 'PKG-INFO')
        }
        with tarfile.open(artifact, 'r:gz') as archive:
            members = archive.getmembers()
            names = [member.name for member in members]
            if len(names) != len(set(names)) or set(names) != expected or not all(member.isfile() for member in members):
                raise ValueError(f'Unexpected sdist members: {names}')
            content = {}
            for member in members:
                stream = archive.extractfile(member)
                if stream is None:
                    raise ValueError(f'Unreadable archive member: {member.name}')
                content[member.name] = stream.read()
        metadata = BytesParser().parsebytes(content[f'{root}PKG-INFO'])
        actual_license = content[f'{root}LICENSE']
    if (metadata['Name'], metadata['Version'], metadata['Requires-Python'], metadata['License-Expression']) != (
        'obforce',
        version,
        '>=3.12',
        'Apache-2.0',
    ):
        raise ValueError('Unexpected distribution metadata')
    repository = Path(__file__).resolve().parents[1]
    for name in package_files:
        member = f'obforce/{name}' if artifact.suffix == '.whl' else f'{root}src/obforce/{name}'
        if content[member] != (repository / 'src/obforce' / name).read_bytes():
            raise ValueError('Packaged source/resource differs from reviewed checkout')
    if artifact.suffix != '.whl':
        for name in ('README.md', 'pyproject.toml'):
            if content[f'{root}{name}'] != (repository / name).read_bytes():
                raise ValueError('Packaged project document differs from reviewed checkout')
    if actual_license != license_bytes:
        raise ValueError('Distribution license differs from root LICENSE')
    print(json.dumps({'artifact': artifact.name, 'sha256': hashlib.sha256(artifact.read_bytes()).hexdigest(), 'files': names}))


def _check_install(artifact: Path, version: str) -> None:
    """Install an artifact into its own external environment and exercise discovery.

    Installation may download runtime and isolated build dependencies. Application
    smoke tests block Python socket operations and have no external tools on PATH.

    :param artifact: Inspected distribution to install independently.
    :param version: Expected installed version.
    :raises ValueError: If discovery, isolation, or no-write checks fail.
    :raises RuntimeError: If an installation or smoke command fails.
    """
    with tempfile.TemporaryDirectory(prefix='obforce-install-') as temporary:
        root = Path(temporary).resolve()
        environment_path = root / 'venv'
        venv.EnvBuilder(with_pip=True).create(environment_path)
        scripts = environment_path / ('Scripts' if os.name == 'nt' else 'bin')
        python = scripts / ('python.exe' if os.name == 'nt' else 'python')
        console = scripts / ('obforce.exe' if os.name == 'nt' else 'obforce')
        environment = dict(os.environ)
        for key in ('PYTHONPATH', 'PYTHONHOME'):
            environment.pop(key, None)
        environment.update(PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1', PIP_DISABLE_PIP_VERSION_CHECK='1')
        _run([str(python), '-m', 'pip', '--isolated', 'install', '--no-cache-dir', str(artifact)], root, environment)
        _run([str(python), '-m', 'pip', '--isolated', 'check'], root, environment)
        probe = (
            'import sys; from pathlib import Path; import obforce; '
            'from importlib.metadata import version; from importlib.resources import files; '
            f'assert version("obforce") == {version!r}; '
            'assert Path(obforce.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()); '
            'assert files("obforce").joinpath("cli.py").is_file(); '
            'from obforce.sources.sf_cli import Operation, _reply; '
            'reply = _reply(Operation.QUERY, 0, '
            'b\'{"status":0,"result":{"records":[],"totalSize":0,"done":false}}\', False); '
            'assert reply.done is False and reply.total_size == 0; '
            'from obforce.models import Component, ComponentKey, SourceBinding; '
            'assert len(Component(SourceBinding("demo", "local"), '
            'ComponentKey("demo", "ApexClass", None, "Example")).source_hash) == 64'
        )
        _run([str(python), '-I', '-c', probe], root, environment)
        work = root / 'work'
        work.mkdir()
        guard = root / 'guard'
        guard.mkdir()
        (guard / 'sitecustomize.py').write_text(
            'import sys\n'
            'def deny_network(event, args):\n'
            '    if event.startswith("socket.") or event in ("subprocess.Popen", "os.system", "os.posix_spawn"):\n'
            '        raise RuntimeError("Network/process access forbidden during artifact smoke tests")\n'
            'sys.addaudithook(deny_network)\n',
            encoding='utf-8',
        )
        environment.update(PATH='', PYTHONPATH=str(guard))
        # Installed code must acquire a fresh synthetic project with network blocked,
        # no external tools, and the same normalized hash/preservation contracts.
        offline_probe = """
import json
from pathlib import Path
from obforce.models import SourceBinding, Selection
from obforce.sources.local import collect_local
root = Path('synthetic-project').resolve()
classes = root / 'demo/main/default/classes'
classes.mkdir(parents=True)
(root / 'sfdx-project.json').write_text(json.dumps({'packageDirectories': [{'path': 'demo'}]}))
(classes / 'Example.cls').write_text('public class Example {}')
(classes / 'Example.cls-meta.xml').write_text(
    '<ApexClass xmlns="http://soap.sforce.com/2006/04/metadata">'
    '<apiVersion>67.0</apiVersion><status>Active</status></ApexClass>')
before = {p: (p.read_bytes() if p.is_file() else None, p.stat().st_mtime_ns) for p in root.rglob('*')}
result = collect_local(root, SourceBinding('demo', 'local'), Selection())
assert len(result.components) == 1 and len(result.inventory_hash) == 64
assert result.coverage.inventory.status == 'complete'
assert result.coverage.audit.status == 'unavailable' and not result.coverage.audit.requested
assert result.coverage.relationships.status == 'not_collected'
assert before == {p: (p.read_bytes() if p.is_file() else None, p.stat().st_mtime_ns) for p in root.rglob('*')}
"""
        # Installed live adapter uses only synthetic replies and cannot start a process.
        live_probe = """
from pathlib import Path
from unittest.mock import patch
from obforce.models import Selection
from obforce.sources.live import collect_live
from obforce.sources.sf_cli import Reply
identity = Reply({'records': [{'Id': '00D000000000001EAA'}]}, done=True, total_size=1)
empty = Reply({'records': []}, done=True, total_size=0)
with patch('obforce.sources.sf_cli.run_sf', side_effect=[identity, empty]) as process:
    result = collect_live(Path('/fictional/sf'), directory=Path.cwd(), target='fictional',
                          workspace_id='demo', selection=Selection(), include_audit_names=False)
assert process.call_count == 2 and result.components == ()
assert result.coverage.outcome == 0 and result.coverage.binding.org_id == '00D000000000001EAA'
assert result.coverage.relationships.status == 'not_collected'
assert len(result.inventory_hash) == 64
"""
        graph_probe = """
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
from obforce.models import Component, ComponentKey, Coverage, CollectionCoverage, CoverageStatus, Selection, SourceBinding
from obforce.sources.live import LiveInventory
from obforce.sources.relationships import collect_relationships
from obforce.sources.sf_cli import Reply
binding = SourceBinding('demo', 'live', '00D000000000001EAA')
complete = CollectionCoverage(CoverageStatus.COMPLETE, 'synthetic', pagination='exhausted', limit_reached=False)
not_collected = CollectionCoverage(CoverageStatus.NOT_COLLECTED, 'not-collected', requested=False)
a = Component(binding, ComponentKey('demo', 'ApexClass', None, 'ExampleA'), record_id='01p000000000001AAA')
b = Component(binding, ComponentKey('demo', 'ApexClass', None, 'ExampleB'), record_id='01p000000000002AAA')
inventory = LiveInventory((a, b), Coverage(binding, Selection(), complete, complete, not_collected))
row = {'MetadataComponentId': a.record_id, 'MetadataComponentName': 'ExampleA',
       'MetadataComponentNamespace': None, 'MetadataComponentType': 'ApexClass',
       'RefMetadataComponentId': b.record_id, 'RefMetadataComponentName': 'ExampleB',
       'RefMetadataComponentNamespace': None, 'RefMetadataComponentType': 'ApexClass'}
identity = Reply({'records': [{'Id': binding.org_id}]}, done=True, total_size=1)
edge = Reply({'records': [row]}, done=True, total_size=1)
empty = Reply({'records': []}, done=True, total_size=0)
with patch('obforce.sources.sf_cli.run_sf', side_effect=[identity, edge, empty, empty, edge]) as process:
    result = collect_relationships(Path('/fictional/sf'), directory=Path.cwd(), target='fictional', inventory=inventory)
assert process.call_count == 5 and len(result.graph.edges) == 1
assert result.graph.references(a.key) == result.graph.referenced_by(b.key)
assert result.coverage.inventory == complete and result.coverage.relationships.status == 'partial'
assert result.coverage.outcome == 4 and inventory.coverage.relationships == not_collected
paths = {a.key: 'A.md', b.key: 'B.md'}
assert result.graph.note_fingerprint(a.key, paths) != result.graph.note_fingerprint(a.key, {**paths, b.key: 'Moved/B.md'})
with patch('obforce.sources.sf_cli.run_sf', side_effect=[identity, empty, empty, empty, empty]):
    refreshed = collect_relationships(Path('/fictional/sf'), directory=Path.cwd(), target='fictional',
                                      inventory=inventory, previous=result.graph)
assert refreshed.graph.edges[0].stale and refreshed.coverage.outcome == 4
assert a.source_hash == replace(a).source_hash
"""
        # Rendering executes in each independent installation with runtime network
        # and process access blocked. Compare full candidate bytes to the reviewed
        # synthetic fixture, rather than merely asserting a self-consistent render.
        render_probe = r"""
import hashlib
import sys
from dataclasses import replace
from importlib.resources import files
from pathlib import Path
from tempfile import TemporaryDirectory
from obforce.config import Options
from obforce.models import (SourceBinding, Component, ComponentKey, FieldValue, Availability,
    Coverage, CollectionCoverage, CoverageStatus, Selection)
from obforce.graph.dependencies import DependencyGraph, Edge, Endpoint, Evidence
from obforce.renderer.templates import load_template
from obforce.renderer.notes import note_paths, render_new_note
for event in ('socket.connect', 'subprocess.Popen'):
    try:
        sys.audit(event)
    except RuntimeError:
        pass
    else:
        raise AssertionError('Runtime access guard is missing')
binding = SourceBinding('fictional', 'local')
a = Component(binding, ComponentKey('fictional', 'ApexClass', None, 'DemoService'),
    {'api_version': FieldValue(Availability.VALUE, '68.0'), 'status': FieldValue(Availability.VALUE, 'Active')})
complete = CollectionCoverage(CoverageStatus.COMPLETE, 'synthetic-local', pagination='exhausted', limit_reached=False)
audit = CollectionCoverage(CoverageStatus.UNAVAILABLE, 'offline-audit', requested=False)
relations = CollectionCoverage(CoverageStatus.NOT_COLLECTED, 'offline-relationships', requested=False)
coverage = Coverage(binding, Selection(), complete, audit, relations)
graph = DependencyGraph(binding, coverage.selection, relations)
identity = '00000000-0000-4000-8000-000000000001'
paths = note_paths([a])
candidate = render_new_note(a, coverage, graph, identity=identity, managed_paths=paths)
assert candidate == render_new_note(a, coverage, graph, identity=identity, managed_paths=paths)
assert hashlib.sha256(candidate.text.encode()).hexdigest() == EXPECTED_RENDER_HASH
assert candidate.generated.render_hash != candidate.creation_hash
for name in ('apex_created.md.j2', 'apex_generated.md.j2'):
    assert files('obforce').joinpath('resources', 'templates', name).read_text() == load_template(name).text
with TemporaryDirectory(prefix='obforce-render-') as temporary:
    directory = Path(temporary).resolve()
    generated = load_template('apex_generated.md.j2')
    (directory / generated.name).write_text(generated.text + '\nLocal presentation.\n', encoding='utf-8', newline='\n')
    assert load_template(generated.name, directory).content_hash != generated.content_hash
    assert load_template('apex_created.md.j2', directory).text == load_template('apex_created.md.j2').text
    changed = render_new_note(a, coverage, graph, identity=identity, managed_paths=paths,
        generated_template=load_template(generated.name, directory))
    assert changed.generated.render_hash != candidate.generated.render_hash
binding = SourceBinding('fictional', 'live', '00D000000000001EAA')
a = replace(a, binding=binding, record_id='01p000000000001AAA')
b = replace(a, key=replace(a.key, full_name='Other'), record_id='01p000000000002AAA')
relations = CollectionCoverage(CoverageStatus.PARTIAL, 'synthetic-platform')
coverage = replace(coverage, binding=binding, relationships=relations)
def endpoint(c):
    return Endpoint('ApexClass', None, c.key.full_name, c.record_id, c.key, 'resolved')
edge = Edge(endpoint(a), endpoint(b), (Evidence('synthetic-platform', relations, stale=True),))
graph = DependencyGraph(binding, coverage.selection, relations, (edge,))
paths = note_paths([a,b])
first = render_new_note(b, coverage, graph, identity=identity, managed_paths=paths)
moved = render_new_note(b, coverage, graph, identity=identity, managed_paths={**paths,a.key:'Moved/A.md'})
assert first.generated.source_hash == moved.generated.source_hash
assert first.generated.render_hash != moved.generated.render_hash
assert 'stale' in first.text and '[[Custom Code/Apex Classes/DemoService.md|DemoService]]' in first.text
assert binding.org_id not in first.text and a.record_id not in first.text
"""
        expected_render_hash = hashlib.sha256(
            (Path(__file__).resolve().parents[1] / 'tests/fixtures/rendered/DemoService.md').read_bytes()
        ).hexdigest()
        render_probe = render_probe.replace('EXPECTED_RENDER_HASH', repr(expected_render_hash))
        _run([str(python), '-c', render_probe], work, environment)
        # Existing-note parsing/patching runs only on embedded fictional bytes,
        # in each independent install with the same active runtime guards.
        preservation_probe = r"""
import hashlib
import sys
from dataclasses import replace
from obforce.models import (SourceBinding, Component, ComponentKey, FieldValue, Availability,
    Coverage, CollectionCoverage, CoverageStatus, Selection, NoteState)
from obforce.graph.dependencies import DependencyGraph
from obforce.renderer.notes import render_generated, note_paths
from obforce.sync.notes import parse_note, patch_note
from obforce.errors import ConflictError
for event in ('socket.connect', 'subprocess.Popen'):
    try:
        sys.audit(event)
    except RuntimeError:
        pass
    else:
        raise AssertionError('Runtime access guard is missing')
raw = NOTE_BYTES
expected = EXPECTED_PATCH_HASH
binding = SourceBinding('fictional', 'local')
a = Component(binding, ComponentKey('fictional', 'ApexClass', None, 'DemoService'),
    {'api_version': FieldValue(Availability.VALUE, '68.0'), 'status': FieldValue(Availability.VALUE, 'Active')})
complete = CollectionCoverage(CoverageStatus.COMPLETE, 'synthetic-local', pagination='exhausted', limit_reached=False)
audit = CollectionCoverage(CoverageStatus.UNAVAILABLE, 'offline-audit', requested=False)
relations = CollectionCoverage(CoverageStatus.NOT_COLLECTED, 'offline-relationships', requested=False)
coverage = Coverage(binding, Selection(), complete, audit, relations)
graph = DependencyGraph(binding, coverage.selection, relations)
identity = '00000000-0000-4000-8000-000000000001'
def candidate(component):
    return render_generated(component, coverage, graph, identity=identity, managed_paths=note_paths([component]))
original = candidate(a)
changed = candidate(replace(a, attributes={**a.attributes,
    'last_modified_at': FieldValue(Availability.VALUE, '2026-10-20T12:00:00Z')}))
def state_for(note):
    return NoteState(identity, binding, a.key, 'Custom Code/Apex Classes/DemoService.md',
        original.source_hash, original.graph_hash, original.render_hash,
        note.generated_properties, note.region_hash)
for data in (raw, raw.replace(b'\n', b'\r\n')):
    note = parse_note(data)
    state = state_for(note)
    saved = state.canonical()
    assert patch_note(data, state, note.region, original).content is data
    result = patch_note(data, state, note.region, changed)
    after = parse_note(result.content)
    assert result.changed
    assert result.content[after.front_end:after.region_start] == data[note.front_end:note.region_start]
    assert result.content[after.region_end:] == data[note.region_end:]
    assert result.generated_region_hash == after.region_hash
    assert result.generated_region == after.region
    assert after.properties['technical_debt'] is None
    assert after.properties['technical_debt_assessed'] is False
    assert after.properties['tags'] == ('my-tag', 'second')
    assert b'# custom tags' in result.content and b"type: 'team_record'" in result.content
    assert b'  Unicode: caf' in result.content
    assert state.canonical() == saved
    next_state = replace(state, generated_properties=result.generated_properties,
        generated_region_hash=result.generated_region_hash)
    assert patch_note(result.content, next_state, result.generated_region, changed).content is result.content
    if data is raw:
        assert hashlib.sha256(result.content).hexdigest() == expected
    else:
        assert result.generated_region_hash != changed.region_hash
    for edited in (data.replace(b'sf_status: Active', b'sf_status: Human'),
                   data.replace(b'## Salesforce Metadata', b'## Human edit')):
        try:
            patch_note(edited, state, note.region, original)
        except ConflictError as error:
            assert error.exit_code == 3 and 'DemoService' not in str(error)
        else:
            raise AssertionError('Generated edit accepted')
for unsafe in (b'custom: 1\ncustom: 2\n', b'custom: !unsafe private-sentinel\n',
               b'custom: &anchor [*anchor]\n', b'<<: {custom: private-sentinel}\n',
               b'custom: {nested: private-sentinel}\n'):
    try:
        parse_note(raw.replace(b'obforce_schema: 1\n', b'obforce_schema: 1\n' + unsafe))
    except ConflictError as error:
        assert 'private-sentinel' not in str(error)
    else:
        raise AssertionError('Unsafe YAML accepted')
"""
        preservation_probe += r"""
import json
import os
import tempfile
from types import SimpleNamespace
from pathlib import Path
from obforce.sync.state import SavedNote, StateDocument, parse_state, serialize_state, load_state, reconcile_vault
from obforce.sync.state import _cross_api_stamp, _stamp

# Exercise the known Windows API timestamp difference in each installed artifact.
fields = dict(st_dev=1, st_ino=2, st_mode=0o100644, st_nlink=1, st_size=3,
              st_mtime_ns=4, st_ctime_ns=10, st_birthtime_ns=10)
by_path = SimpleNamespace(**fields)
by_fd = SimpleNamespace(**{**fields, 'st_ctime_ns': 20})
assert _stamp(by_path) != _stamp(by_fd)
assert _cross_api_stamp(by_path, windows=True) == _cross_api_stamp(by_fd, windows=True)
assert _cross_api_stamp(by_path, windows=False) != _cross_api_stamp(by_fd, windows=False)

def snapshot(root):
    return {p.relative_to(root).as_posix(): (p.stat().st_mtime_ns, p.read_bytes() if p.is_file() else None)
            for p in [root, *root.rglob('*')]}

for data in (raw, raw.replace(b'\n', b'\r\n')):
    parsed = parse_note(data)
    saved = SavedNote(state_for(parsed), parsed.region)
    document = StateDocument(binding, coverage.selection, coverage, (saved,))
    wire = serialize_state(document)
    loaded = parse_state(wire)
    assert serialize_state(loaded) == wire and loaded.notes[0].generated_region == parsed.region
    assert b'technical_debt' not in wire and b'Fictional knowledge' not in wire
    with tempfile.TemporaryDirectory(prefix='obforce-state-synthetic-') as temporary:
        vault = Path(temporary).resolve()
        state_path = vault / '.obforce/state.json'
        state_path.parent.mkdir()
        state_path.write_bytes(wire)
        state_path.write_bytes(wire)
        os.utime(state_path, ns=(1_000_000_000, 1_000_000_000))
        path = vault / saved.note.path
        path.parent.mkdir(parents=True)
        path.write_bytes(data)
        (vault / 'Ordinary.md').write_text('Unrelated human narrative\n', encoding='utf-8')
        before = snapshot(vault)
        assert load_state(state_path) == loaded
        result = reconcile_vault(vault, state_path, binding, coverage.selection, excluded_roots=())
        assert not result.path_changes and serialize_state(result.state) == wire
        assert snapshot(vault) == before
        moved = vault / 'Moved.md'
        path.rename(moved)
        moved.write_bytes(data)
        os.utime(moved, ns=(1_000_000_000, 1_000_000_000))
        before = snapshot(vault)
        result = reconcile_vault(vault, state_path, binding, coverage.selection, excluded_roots=())
        assert result.path_changes[0].old_path == saved.note.path and result.path_changes[0].new_path == 'Moved.md'
        candidate = result.state.notes[0]
        assert candidate.note == replace(saved.note, path='Moved.md')
        assert candidate.generated_region == saved.generated_region
        assert patch_note(data, candidate.note, candidate.generated_region, original).content is data
        assert snapshot(vault) == before
        copy = vault / 'Copy.md'
        copy.write_bytes(data)
        before = snapshot(vault)
        try:
            reconcile_vault(vault, state_path, binding, coverage.selection, excluded_roots=())
        except ConflictError as error:
            assert error.exit_code == 3 and 'DemoService' not in str(error)
        else:
            raise AssertionError('Copied identity accepted')
        assert snapshot(vault) == before
        copy.unlink()
        moved.write_bytes(data.replace(b'sf_status: Active', b'sf_status: Human'))
        before = snapshot(vault)
        try:
            reconcile_vault(vault, state_path, binding, coverage.selection, excluded_roots=())
        except ConflictError:
            pass
        else:
            raise AssertionError('Generated edit accepted by reconciliation')
        assert snapshot(vault) == before
    for bad in (b'{"x":1,"x":1}', b'{"state_schema":99}', b'\xff', b'[' * 1000 + b']' * 1000):
        try:
            parse_state(bad)
        except ConflictError as error:
            assert error.exit_code == 3
        else:
            raise AssertionError('Unsafe state accepted')
    malicious = json.loads(wire)
    malicious['notes'][0]['note']['path'] = '../Escape.md'
    try:
        parse_state(json.dumps(malicious).encode())
    except ConflictError:
        pass
    else:
        raise AssertionError('State traversal accepted')
"""
        fixtures = Path(__file__).resolve().parents[1] / 'tests/fixtures/vaults'
        preservation_probe = preservation_probe.replace('NOTE_BYTES', repr((fixtures / 'hand_edited.md').read_bytes()))
        preservation_probe = preservation_probe.replace(
            'EXPECTED_PATCH_HASH', repr(hashlib.sha256((fixtures / 'expected_updated.md').read_bytes()).hexdigest())
        )
        _run([str(python), '-c', preservation_probe], work, environment)
        planner_probe = (Path(__file__).with_name('probe_planner.py')).read_text(encoding='utf-8')
        _run([str(python), '-c', planner_probe], work, environment)
        transaction_probe = Path(__file__).with_name('probe_transactions.py').read_text(encoding='utf-8')
        _run([str(python), '-c', transaction_probe], work, environment)
        engine_probe = Path(__file__).with_name('probe_engine.py').read_text(encoding='utf-8')
        _run([str(python), '-c', engine_probe], work, environment)
        _run([str(python), '-c', live_probe], work, environment)
        _run([str(python), '-c', graph_probe], work, environment)
        # Keep this fixture outside the entry-point no-write working directory.
        _run([str(python), '-c', offline_probe], root, environment)
        for number, command in enumerate(([str(console)], [str(python), '-m', 'obforce'])):
            _lifecycle(command, root / f'public-{number}', work, environment)
            for arguments in ([], ['--help'], ['--version']):
                output = _run(command + arguments, work, environment)
                expected = f'obforce, version {version}\n' if arguments == ['--version'] else '--help'
                if expected not in output:
                    raise ValueError(f'Unexpected entry-point output: {output}')
            for feature in ('init', 'build', 'sync', 'recover'):
                result = subprocess.run(
                    command + [feature], cwd=work, env=environment, capture_output=True, text=True, timeout=20, check=False
                )
                if result.returncode != 2:
                    raise ValueError(f'Unexpected feature command: {feature}')
        if list(work.iterdir()):
            raise ValueError('Discovery created working-directory artifacts')
        print(f'{artifact.name}: install, imports/resources, pip check, both entry points, offline/no-write checks passed')


def _lifecycle(command: list[str], root: Path, work: Path, environment: dict[str, str]) -> None:
    """Exercise actual installed console/module init/build/recover under runtime denial."""
    from probe_engine import project, snapshot

    root.mkdir()
    source = project(root)
    protected = snapshot(source)
    config = root / 'Config with spaces.toml'
    vault = root / 'New Parent/Vault'
    args = ['init', '--config', str(config), '--source', source.name, '--vault', 'New Parent/Vault', '--workspace-id', 'demo']
    before = snapshot(root)
    _run(command + args + ['--dry-run'], work, environment)
    if snapshot(root) != before:
        raise ValueError('Installed init preview wrote output')
    _run(command + args, work, environment)
    config_before = config.read_bytes(), config.stat().st_mtime_ns
    before = snapshot(root)
    _run(command + ['build', '--config', str(config), '--dry-run'], work, environment)
    if snapshot(root) != before or vault.exists():
        raise ValueError('Installed missing-destination preview wrote output')
    _run(command + ['build', '--config', str(config)], work, environment)
    before = snapshot(root)
    result = subprocess.run(
        command + ['build', '--config', str(config)],
        cwd=work,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if result.returncode != 3 or snapshot(root) != before:
        raise ValueError('Installed repeat-build refusal failed')
    for flags in ([], ['--dry-run'], ['--cleanup']):
        _run(command + ['recover', '--config', str(config)] + flags, work, environment)
        if snapshot(root) != before:
            raise ValueError('Installed recovery no-op changed output')
    if snapshot(source) != protected or (config.read_bytes(), config.stat().st_mtime_ns) != config_before:
        raise ValueError('Installed lifecycle modified source or configuration')


def main() -> None:
    """Validate exactly one fresh wheel and sdist without publishing them."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('artifact_directory', type=Path)
    arguments = parser.parse_args()
    repository = Path(__file__).resolve().parents[1]
    with (repository / 'pyproject.toml').open('rb') as stream:
        version = tomllib.load(stream)['project']['version']
    directory = arguments.artifact_directory.resolve()
    expected = {f'obforce-{version}-py3-none-any.whl', f'obforce-{version}.tar.gz'}
    if {path.name for path in directory.iterdir()} != expected:
        parser.error('Use a fresh directory containing exactly the current wheel and sdist')
    for artifact in sorted(directory.iterdir()):
        _inspect(artifact, version, (repository / 'LICENSE').read_bytes())
        _check_install(artifact, version)


if __name__ == '__main__':
    main()
