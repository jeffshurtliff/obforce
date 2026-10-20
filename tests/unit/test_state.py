# -*- coding: utf-8 -*-
"""
:Module:            tests.unit.test_state
:Synopsis:          Exercises strict private state and read-only synthetic identity reconciliation
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     20 Oct 2026
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import socket
import stat
import subprocess
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from obforce import constants as const
from obforce.errors import ConflictError, ExitCode, ModelError, OperationalError, exit_code
from obforce.models import (
    Availability,
    CollectionCoverage,
    ComponentKey,
    Coverage,
    CoverageStatus,
    FieldValue,
    NoteState,
    Selection,
    SourceBinding,
)
from obforce.sync import state as module
from obforce.sync.notes import parse_note
from obforce.sync.state import SavedNote, StateDocument, load_state, parse_state, reconcile_vault, serialize_state

FIXTURE = Path(__file__).parents[1] / 'fixtures/vaults/hand_edited.md'


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError('Runtime network/process forbidden')

    monkeypatch.setattr(socket, 'socket', deny)
    monkeypatch.setattr(subprocess, 'Popen', deny)


@pytest.fixture
def example():
    raw = FIXTURE.read_bytes()
    parsed = parse_note(raw)
    binding = SourceBinding('fictional', 'local')
    complete = CollectionCoverage(CoverageStatus.COMPLETE, 'synthetic-local', pagination='exhausted', limit_reached=False)
    audit = CollectionCoverage(CoverageStatus.UNAVAILABLE, 'offline-audit', requested=False)
    relations = CollectionCoverage(CoverageStatus.NOT_COLLECTED, 'offline-relationships', requested=False)
    coverage = Coverage(binding, Selection(), complete, audit, relations)
    note = NoteState(
        parsed.properties['obforce_id'],
        binding,
        ComponentKey('fictional', 'ApexClass', None, 'DemoService'),
        'Apex/DemoService.md',
        'a' * 64,
        'b' * 64,
        'c' * 64,
        parsed.generated_properties,
        parsed.region_hash,
    )
    return raw, StateDocument(binding, coverage.selection, coverage, (SavedNote(note, parsed.region),))


def tree(root):
    return {
        str(p.relative_to(root)): (p.lstat().st_mtime_ns, p.read_bytes() if p.is_file() else None)
        for p in [root, *root.rglob('*')]
    }


def symlink(path, target, *, directory=False):
    """Keep native privilege gaps distinct from synthetic reparse refusal."""
    try:
        path.symlink_to(target, target_is_directory=directory)
    except OSError as error:
        if os.name == 'nt' and getattr(error, 'winerror', None) == 1314:
            pytest.skip('Native symlink creation privilege unavailable')
        raise


def vault_at(tmp_path, example, *, moved=False):
    raw, document = example
    vault = (tmp_path / 'synthetic-vault').resolve()
    vault.mkdir()
    state_path = vault / '.obforce/state.json'
    state_path.parent.mkdir()
    state_path.write_bytes(serialize_state(document))
    path = vault / ('Moved/Service.md' if moved else document.notes[0].note.path)
    path.parent.mkdir(parents=True)
    path.write_bytes(raw)
    return vault, state_path, path


def reconcile(vault, state_path, document, **kwargs):
    return reconcile_vault(vault, state_path, document.binding, document.selection, excluded_roots=(), **kwargs)


@pytest.mark.parametrize('ending', [b'\n', b'\r\n'])
def test_roundtrip_exact_bytes_and_private_minimum(example, ending):
    raw, document = example
    raw = raw.replace(b'\n', ending)
    parsed = parse_note(raw)
    note = replace(document.notes[0].note, generated_region_hash=parsed.region_hash)
    document = replace(document, notes=(SavedNote(note, parsed.region),))
    wire = serialize_state(document)
    restored = parse_state(wire)
    assert serialize_state(restored) == wire
    assert restored.notes[0].generated_region == parsed.region
    assert restored.notes[0].note.canonical() == note.canonical()
    assert wire.endswith(b'\n') and not wire.endswith(b'\n\n')
    assert b'Human' not in wire and b'technical_debt' not in wire and b'aliases' not in wire
    assert b'fictional human' not in repr(restored).encode()
    with pytest.raises(TypeError):
        restored.notes[0].note.generated_properties['tags'] = FieldValue(Availability.VALUE, ())


def test_move_and_noop_preserve_tree_inputs_and_hashes(example, tmp_path, monkeypatch):
    _, document = example
    vault, state_path, path = vault_at(tmp_path, example, moved=True)
    (vault / 'Unrelated.md').write_text('Human ordinary note\n')
    before, wire = tree(vault), serialize_state(document)
    monkeypatch.chdir(tmp_path)
    result = reconcile(vault, state_path, document)
    saved = result.state.notes[0]
    assert saved.note == replace(document.notes[0].note, path='Moved/Service.md')
    assert saved.generated_region == document.notes[0].generated_region
    assert tuple(result.paths.items()) == ((saved.note.key, 'Moved/Service.md'),)
    assert result.path_changes == (module.PathChange(saved.note.key, 'Apex/DemoService.md', 'Moved/Service.md'),)
    assert result.observations[saved.note.obforce_id].raw == path.read_bytes()
    assert serialize_state(document) == wire and tree(vault) == before
    assert sorted(p.name for p in tmp_path.iterdir()) == ['synthetic-vault']
    with pytest.raises(TypeError):
        result.paths[saved.note.key] = 'Other.md'
    # A second read of the same unmoved synthetic tree is a true no-op candidate.
    path.rename(vault / 'A.md')
    result2 = reconcile(vault, state_path, document)
    assert result2.paths[saved.note.key] == 'A.md'


def test_noop_state_bytes_and_mtimes(example, tmp_path):
    _, document = example
    vault, state_path, _ = vault_at(tmp_path, example)
    before = tree(vault)
    result = reconcile(vault, state_path, document)
    assert not result.path_changes
    assert serialize_state(result.state) == state_path.read_bytes()
    assert load_state(state_path) == result.state
    assert tree(vault) == before


@pytest.mark.parametrize('initial', [False, True])
@pytest.mark.parametrize('state_kind', ['missing', 'empty', 'invalid', 'unknown', 'empty-notes'])
def test_missing_or_bad_state_never_adopts(example, tmp_path, initial, state_kind):
    _, document = example
    vault, state_path, _ = vault_at(tmp_path, example)
    data = json.loads(serialize_state(document))
    if state_kind == 'missing':
        state_path.unlink()
    elif state_kind == 'empty':
        state_path.write_bytes(b'')
    elif state_kind == 'invalid':
        state_path.write_bytes(b'{private broken')
    elif state_kind == 'unknown':
        data['state_schema'] = 99
        state_path.write_text(json.dumps(data))
    else:
        data['notes'] = []
        state_path.write_text(json.dumps(data))
    before = tree(vault)
    with pytest.raises(ConflictError):
        reconcile(vault, state_path, document, initial=initial)
    assert tree(vault) == before


def test_empty_initial_scope_does_not_adopt_unrelated_files(example, tmp_path):
    _, document = example
    vault = tmp_path.resolve()
    (vault / 'Ordinary.md').write_text('Human narrative\n')
    (vault / 'opaque.bin').write_bytes(b'private')
    before = tree(vault)
    result = reconcile(vault, vault / '.obforce/state.json', document, initial=True)
    assert result.initial and result.state is None and not result.paths and not result.observations
    assert tree(vault) == before and load_state(vault / '.obforce/state.json') is None
    with pytest.raises(ConflictError):
        reconcile(vault, vault / '.obforce/state.json', document)
    empty = replace(document, notes=())
    (vault / '.obforce').mkdir()
    (vault / '.obforce/state.json').write_bytes(serialize_state(empty))
    assert reconcile(vault, vault / '.obforce/state.json', empty).state == empty


@pytest.mark.parametrize(
    'mutation',
    [
        'duplicate-id',
        'duplicate-key',
        'duplicate-path',
        'namespace-spelling',
        'file-parent',
        'bad-uuid',
        'bad-hash',
        'unknown-note-key',
        'unknown-root-key',
        'unknown-binding-key',
        'bad-schema',
        'bool-schema',
        'bad-scope',
        'wrong-workspace',
        'key-workspace',
        'bad-mode',
        'baseline-id',
        'baseline-schema',
        'baseline-name',
        'baseline-mode',
        'baseline-namespace',
        'baseline-user',
        'baseline-unknown',
        'baseline-lifecycle',
        'baseline-coverage',
        'missing-identity',
        'extra-field-key',
        'bad-availability',
        'bad-value',
        'empty-namespace',
        'unknown-selection',
        'bad-types',
        'duplicate-filter',
        'namespace-selection',
        'name-selection',
        'coverage-selection',
        'coverage-binding',
        'coverage-schema',
        'coverage-complete',
        'extra-coverage',
        'float',
        'nonfinite',
        'bad-base64',
        'noncanonical-base64',
        'bad-region-hash',
        'bad-region',
        'scalar-notes',
        'large-integer',
        'array-binding',
        'array-properties',
        'array-region',
        'string-boolean',
    ],
)
def test_strict_wire_refusals(example, mutation):
    _, document = example
    data = json.loads(serialize_state(document))
    note = data['notes'][0]['note']
    fields = note['generated_properties']
    if mutation.startswith('duplicate-') and mutation not in {'duplicate-filter'}:
        other = json.loads(json.dumps(data['notes'][0]))
        if mutation != 'duplicate-id':
            other['note']['obforce_id'] = '00000000-0000-4000-8000-000000000002'
            other['note']['generated_properties']['obforce_id']['value'] = other['note']['obforce_id']
        if mutation == 'duplicate-path':
            other['note']['key'][3] = 'Other'
            other['note']['generated_properties']['sf_full_name']['value'] = 'Other'
            other['note']['path'] = note['path'].upper()
        data['notes'].append(other)
    elif mutation in {'namespace-spelling', 'file-parent'}:
        other = json.loads(json.dumps(data['notes'][0]))
        other['note'].update(obforce_id='00000000-0000-4000-8000-000000000002')
        other['note']['generated_properties']['obforce_id']['value'] = other['note']['obforce_id']
        other['note']['key'][3] = 'Other'
        other['note']['generated_properties']['sf_full_name']['value'] = 'Other'
        other['note']['path'] = 'apex/Other.md' if mutation == 'namespace-spelling' else note['path'] + '/Child.md'
        data['notes'].append(other)
    elif mutation == 'bad-uuid':
        note['obforce_id'] = 'PRIVATE-invalid'
    elif mutation == 'bad-hash':
        note['render_hash'] = 'A' * 64
    elif mutation == 'unknown-note-key':
        note['private'] = 1
    elif mutation == 'unknown-root-key':
        data['private'] = 1
    elif mutation == 'unknown-binding-key':
        data['binding']['alias'] = 'private'
    elif mutation == 'bad-schema':
        data['state_schema'] = 2
    elif mutation == 'bool-schema':
        data['state_schema'] = True
    elif mutation == 'bad-scope':
        data['scope_hash'] = 'd' * 64
    elif mutation == 'wrong-workspace':
        data['binding']['workspace_id'] = 'other'
    elif mutation == 'key-workspace':
        note['key'][0] = 'other'
    elif mutation == 'bad-mode':
        data['binding']['mode'] = 'alias'
    elif mutation.startswith('baseline-'):
        name, value = {
            'baseline-id': ('obforce_id', '00000000-0000-4000-8000-000000000002'),
            'baseline-schema': ('obforce_schema', True),
            'baseline-name': ('sf_full_name', 'Other'),
            'baseline-mode': ('sf_source_mode', 'live'),
            'baseline-namespace': ('sf_namespace', ''),
            'baseline-user': ('technical_debt', False),
            'baseline-unknown': ('sf_unknown', 'private'),
            'baseline-lifecycle': ('sf_lifecycle', 'deleted'),
            'baseline-coverage': ('sf_dependency_coverage', 'yes'),
        }[mutation]
        fields[name] = {'availability': 'value', 'value': value}
    elif mutation == 'missing-identity':
        del fields['obforce_id']
    elif mutation == 'extra-field-key':
        fields['sf_status']['private'] = 1
    elif mutation == 'bad-availability':
        fields['sf_status']['availability'] = 'unknown'
    elif mutation == 'bad-value':
        fields['sf_status']['value'] = {'private': 1}
    elif mutation == 'empty-namespace':
        note['key'][2] = ''
    elif mutation == 'unknown-selection':
        data['selection']['private'] = 1
    elif mutation == 'bad-types':
        data['selection']['types'] = ['Other']
    elif mutation == 'duplicate-filter':
        data['selection']['full_names'] = ['DemoService', 'DemoService']
    elif mutation in {'namespace-selection', 'name-selection'}:
        if mutation == 'namespace-selection':
            note['key'][2] = 'pkg'
            fields['sf_namespace'] = {'availability': 'value', 'value': 'pkg'}
        else:
            data['selection']['full_names'] = ['Other']
            data['coverage']['selection'] = data['selection']
            data['scope_hash'] = Selection(full_names=('Other',)).scope_hash(document.binding)
    elif mutation == 'coverage-selection':
        data['coverage']['selection']['include_namespaced'] = True
    elif mutation == 'coverage-binding':
        data['coverage']['binding']['workspace_id'] = 'other'
    elif mutation == 'coverage-schema':
        data['coverage']['model_schema'] = True
    elif mutation == 'coverage-complete':
        data['coverage']['inventory']['pagination'] = 'unknown'
    elif mutation == 'extra-coverage':
        data['coverage']['private'] = 1
    elif mutation == 'float':
        fields['sf_status']['value'] = 1.0
    elif mutation == 'nonfinite':
        fields['sf_status']['value'] = float('nan')
    elif mutation == 'bad-base64':
        data['notes'][0]['generated_region'] = '!!!'
    elif mutation == 'noncanonical-base64':
        data['notes'][0]['generated_region'] += '='
    elif mutation == 'bad-region-hash':
        note['generated_region_hash'] = 'd' * 64
    elif mutation == 'bad-region':
        region = b'private\x00\n'
        note['generated_region_hash'] = hashlib.sha256(region).hexdigest()
        data['notes'][0]['generated_region'] = base64.b64encode(region).decode()
    elif mutation == 'scalar-notes':
        data['notes'] = 'private'
    elif mutation == 'large-integer':
        fields['sf_status']['value'] = 2**65
    elif mutation == 'array-binding':
        data['binding'] = []
    elif mutation == 'array-properties':
        note['generated_properties'] = []
    elif mutation == 'array-region':
        data['notes'][0]['generated_region'] = []
    elif mutation == 'string-boolean':
        data['selection']['include_namespaced'] = 'false'
    with pytest.raises(ConflictError) as error:
        parse_state(json.dumps(data).encode())
    assert 'PRIVATE' not in str(error.value) and 'DemoService' not in str(error.value)


@pytest.mark.parametrize(
    'raw',
    [
        b'{"state_schema":1,"state_schema":1}',
        b'{"x":{"a":1,"a":2}}',
        b'[]',
        b'null',
        b'',
        b'\xef\xbb\xbf{}',
        b'\xff',
        b'{} trailing',
        b'[' * 1000 + b']' * 1000,
        b'{"x":"\\ud800"}',
    ],
)
def test_malformed_json_is_typed_and_redacted(raw):
    with pytest.raises(ConflictError):
        parse_state(raw)


@pytest.mark.parametrize(
    'path',
    [
        '../Escape.md',
        '/Escape.md',
        'C:/Escape.md',
        'A\\Escape.md',
        'A//B.md',
        './B.md',
        'CON.md',
        'a/COM1.txt/B.md',
        'a./B.md',
        'a /B.md',
        'a/../B.md',
        '.obsidian/B.md',
        '.git/B.md',
        '.obforce/B.md',
        'a#b.md',
        'a/B.txt',
        'a/\u2028B.md',
        'a/' + 'b' * 241 + '.md',
    ],
)
def test_wire_paths_refuse(example, path):
    _, document = example
    data = json.loads(serialize_state(document))
    data['notes'][0]['note']['path'] = path
    with pytest.raises(ConflictError):
        parse_state(json.dumps(data).encode())


@pytest.mark.parametrize(
    'limit,value',
    [
        ('MAX_STATE_BYTES', 2),
        ('MAX_STATE_DEPTH', 2),
        ('MAX_STATE_NODES', 2),
        ('MAX_STATE_TEXT_BYTES', 2),
        ('MAX_STATE_NOTES', 0),
    ],
)
def test_state_limits_refuse(example, monkeypatch, limit, value):
    raw = serialize_state(example[1])
    monkeypatch.setattr(const, limit, value)
    with pytest.raises(ConflictError):
        parse_state(raw)
    with pytest.raises(ConflictError):
        serialize_state(example[1])


@pytest.mark.parametrize(
    'kind',
    [
        'copy',
        'vanished',
        'outside',
        'unowned-old',
        'parent-file',
        'edited-id',
        'edited-schema',
        'edited-name',
        'edited-property',
        'edited-region',
        'missing-id',
        'missing-all-id',
        'bad-yaml',
    ],
)
def test_discovered_conflicts_preserve_tree(example, tmp_path, kind):
    _, document = example
    vault, state_path, path = vault_at(tmp_path, example, moved=kind in {'unowned-old', 'parent-file'})
    if kind == 'copy':
        (vault / 'Copy.md').write_bytes(path.read_bytes())
    elif kind == 'vanished':
        path.unlink()
    elif kind == 'outside':
        path.rename(tmp_path / 'Outside.md')
    elif kind == 'unowned-old':
        target = vault / document.notes[0].note.path
        target.parent.mkdir()
        target.write_text('ordinary')
    elif kind == 'parent-file':
        (vault / 'Apex').write_text('ordinary')
    else:
        raw = path.read_bytes()
        replacements = {
            'edited-id': (document.notes[0].note.obforce_id.encode(), b'00000000-0000-4000-8000-000000000002'),
            'edited-schema': (b'obforce_schema: 1', b'obforce_schema: 2'),
            'edited-name': (b'sf_full_name: DemoService', b'sf_full_name: Other'),
            'edited-property': (b'sf_status: Active', b'sf_status: Changed'),
            'edited-region': (b'## Salesforce Metadata', b'## Changed Metadata'),
            'missing-id': (b'obforce_id:', b'former_id:'),
            'missing-all-id': (b'obforce', b'former'),
            'bad-yaml': (b'---\n', b'bad\n'),
        }
        before, after = replacements[kind]
        assert before in raw
        path.write_bytes(raw.replace(before, after))
    before = tree(vault)
    with pytest.raises(ConflictError):
        reconcile(vault, state_path, document)
    assert tree(vault) == before


@pytest.mark.parametrize('kind', ['workspace', 'mode', 'org', 'scope', 'name-scope'])
def test_caller_binding_scope_refusal(example, tmp_path, kind):
    _, document = example
    vault, state_path, _ = vault_at(tmp_path, example)
    binding, selection = document.binding, document.selection
    if kind == 'workspace':
        binding = SourceBinding('other', 'local')
    elif kind in {'mode', 'org'}:
        binding = SourceBinding('fictional', 'live', '00D000000000001EAA')
    elif kind == 'scope':
        selection = Selection(True)
    else:
        selection = Selection(full_names=('Other',))
    with pytest.raises(ConflictError):
        reconcile_vault(vault, state_path, binding, selection, excluded_roots=())


@pytest.mark.parametrize('name', ['.git', '.obsidian', '.obforce'])
def test_control_contents_are_excluded(example, tmp_path, name):
    _, document = example
    vault, state_path, _ = vault_at(tmp_path, example)
    control = vault / name
    control.mkdir(exist_ok=True)
    (control / 'NotRead.md').write_bytes(b'obforce private malformed')
    assert reconcile(vault, state_path, document).state == document


@pytest.mark.parametrize('kind', ['symlink', 'hardlink', 'directory-link', 'state-link', 'parent-link', 'fifo', 'reparse'])
def test_unsafe_filesystem_refuses(example, tmp_path, monkeypatch, kind):
    _, document = example
    vault, state_path, path = vault_at(tmp_path, example)
    target = vault / 'Unsafe.md'
    if kind == 'symlink':
        symlink(target, path)
    elif kind == 'hardlink':
        os.link(path, target)
    elif kind == 'directory-link':
        symlink(target, vault, directory=True)
    elif kind == 'state-link':
        other = tmp_path / 'state.json'
        state_path.rename(other)
        symlink(state_path, other)
    elif kind == 'parent-link':
        link = tmp_path / 'link'
        symlink(link, vault, directory=True)
        vault, state_path = link, link / '.obforce/state.json'
    elif kind == 'fifo':
        if not hasattr(os, 'mkfifo'):
            pytest.skip('Native FIFO unavailable')
        os.mkfifo(target)
    else:
        original = Path.lstat

        def reparse(p):
            info = original(p)
            if p == path:
                return SimpleNamespace(
                    **{
                        **{n: getattr(info, n) for n in dir(info) if n.startswith('st_')},
                        'st_file_attributes': stat.FILE_ATTRIBUTE_REPARSE_POINT,
                    }
                )
            return info

        monkeypatch.setattr(Path, 'lstat', reparse)
    with pytest.raises(ConflictError):
        reconcile(vault, state_path, document)


@pytest.mark.parametrize('kind', ['entry', 'aggregate', 'note-bytes', 'path-depth', 'case', 'unicode', 'reserved'])
def test_discovery_limits_and_portable_collisions(example, tmp_path, monkeypatch, kind):
    _, document = example
    vault, state_path, path = vault_at(tmp_path, example)
    if kind == 'entry':
        monkeypatch.setattr(const, 'MAX_VAULT_ENTRIES', 1)
    elif kind == 'aggregate':
        monkeypatch.setattr(const, 'MAX_VAULT_READ_BYTES', 1)
    elif kind == 'note-bytes':
        monkeypatch.setattr(const, 'MAX_NOTE_BYTES', 2)
    elif kind == 'path-depth':
        monkeypatch.setattr(const, 'MAX_RENDER_PATH_DEPTH', 1)
    elif kind == 'case':
        other = vault / 'apex'
        try:
            other.mkdir()
        except FileExistsError:
            pytest.skip('Filesystem cannot represent case collision')
    elif kind == 'unicode':
        (vault / '\u00e9').mkdir()
        try:
            (vault / 'e\u0301').mkdir()
        except FileExistsError:
            pytest.skip('Filesystem cannot represent normalization collision')
    else:
        if os.name == 'nt':
            pytest.skip('Native reserved-name fixture unavailable')
        (vault / 'NUL.md').write_text('ordinary')
    with pytest.raises(ConflictError):
        reconcile(vault, state_path, document)


@pytest.mark.parametrize('kind', ['iteration', 'read', 'parent-change', 'file-change', 'partial-read'])
def test_partial_or_changed_read_refuses(example, tmp_path, monkeypatch, kind):
    _, document = example
    vault, state_path, path = vault_at(tmp_path, example)
    before = tree(vault)
    if kind == 'iteration':
        original = os.scandir

        def fail(p):
            if p == vault:
                raise PermissionError('PRIVATE path')
            return original(p)

        monkeypatch.setattr(os, 'scandir', fail)
    elif kind == 'read':
        original = os.open

        def fail(p, *args, **kwargs):
            if p == path:
                raise PermissionError('PRIVATE path')
            return original(p, *args, **kwargs)

        monkeypatch.setattr(os, 'open', fail)
    elif kind == 'partial-read':
        original = os.fdopen

        class Partial:
            def __init__(self, stream):
                self.stream = stream

            def __enter__(self):
                return self

            def __exit__(self, *args):
                self.stream.close()

            def fileno(self):
                return self.stream.fileno()

            def read(self, limit):
                return self.stream.read(1)

        monkeypatch.setattr(os, 'fdopen', lambda *a, **kw: Partial(original(*a, **kw)))
    else:
        original = module._stamp
        calls = {}
        target = vault if kind == 'parent-change' else path
        target_inode = target.stat().st_ino

        def changed(info):
            stamp = original(info)
            if info.st_ino == target_inode:
                calls[target_inode] = calls.get(target_inode, 0) + 1
                if calls[target_inode] >= 3:
                    return (*stamp[:-1], stamp[-1] + 1)
            return stamp

        monkeypatch.setattr(module, '_stamp', changed)
    with pytest.raises(OperationalError) as error:
        reconcile(vault, state_path, document)
    assert 'PRIVATE' not in str(error.value)
    monkeypatch.undo()
    assert tree(vault) == before


def test_explicit_inputs_and_overlap(example, tmp_path):
    _, document = example
    vault, state_path, _ = vault_at(tmp_path, example)
    for root in (vault, vault.parent, vault / 'source'):
        with pytest.raises(ConflictError):
            reconcile_vault(vault, state_path, document.binding, document.selection, excluded_roots=(root,))
    with pytest.raises(ModelError):
        reconcile(Path('relative'), state_path, document)
    with pytest.raises(ModelError):
        reconcile(vault, vault / 'other.json', document)
    with pytest.raises(ModelError):
        parse_state('private')
    with pytest.raises(ModelError):
        serialize_state({})
    assert exit_code([ExitCode.INVALID, ExitCode.CONFLICT, ExitCode.OPERATIONAL, ExitCode.INCOMPLETE]) == ExitCode.CONFLICT


@pytest.mark.parametrize('value', [None, False, 0, '', (), 'observed'])
def test_baseline_distinctions_roundtrip_and_reconcile(example, tmp_path, value):
    raw, document = example
    encoded = json.dumps(value).encode()
    raw = raw.replace(b'sf_status: Active', b'sf_status: ' + encoded)
    parsed = parse_note(raw)
    note = replace(document.notes[0].note, generated_properties=parsed.generated_properties)
    current = replace(document, notes=(SavedNote(note, parsed.region),))
    wire = serialize_state(current)
    assert parse_state(wire).notes[0].note.generated_properties['sf_status'] == parsed.generated_properties['sf_status']
    vault, state_path, path = vault_at(tmp_path, (raw, current))
    assert reconcile(vault, state_path, current).state == current
    path.write_bytes(raw.replace(b'sf_status: ' + encoded, b'sf_status: Different'))
    with pytest.raises(ConflictError):
        reconcile(vault, state_path, current)


def test_unavailable_absent_null_and_user_edits(example, tmp_path):
    raw, document = example
    raw = raw.replace(b'sf_status: Active\n', b'')
    parsed = parse_note(raw)
    absent = replace(document.notes[0].note, generated_properties=parsed.generated_properties)
    fields = {**absent.generated_properties, 'sf_status': FieldValue(Availability.UNAVAILABLE)}
    unavailable = replace(document, notes=(SavedNote(replace(absent, generated_properties=fields), parsed.region),))
    assert parse_state(serialize_state(unavailable)).notes[0].note.generated_properties['sf_status'].availability == 'unavailable'
    current = replace(document, notes=(SavedNote(absent, parsed.region),))
    vault, state_path, path = vault_at(tmp_path, (raw, current))
    assert reconcile(vault, state_path, current).state == current
    state_path.write_bytes(serialize_state(unavailable))
    with pytest.raises(ConflictError):
        reconcile(vault, state_path, unavailable)
    state_path.write_bytes(serialize_state(current))
    # User fields/debt prose are opaque ownership and must not become baseline data.
    edited = raw.replace(b'technical_debt: null', b'technical_debt: false').replace(
        b'Fictional knowledge that must survive.', b'Human changed knowledge.'
    )
    path.write_bytes(edited)
    before = tree(vault)
    result = reconcile(vault, state_path, current)
    assert result.state == current and result.observations[absent.obforce_id].raw == edited
    assert tree(vault) == before
    path.write_bytes(edited.replace(b'sf_lifecycle:', b'sf_status: null\nsf_lifecycle:'))
    with pytest.raises(ConflictError):
        reconcile(vault, state_path, current)


@pytest.mark.parametrize('ending', [b'\n', b'\r\n'])
def test_loaded_saved_bytes_feed_accepted_patcher(example, tmp_path, ending):
    from obforce.config import Options
    from obforce.graph.dependencies import DependencyGraph
    from obforce.models import Component
    from obforce.renderer.notes import render_generated
    from obforce.sync.notes import patch_note

    raw, document = example
    raw = raw.replace(b'\n', ending)
    parsed = parse_note(raw)
    saved = replace(document.notes[0].note, generated_region_hash=parsed.region_hash)
    current = replace(document, notes=(SavedNote(saved, parsed.region),))
    vault, state_path, _ = vault_at(tmp_path, (raw, current), moved=True)
    result = reconcile(vault, state_path, current)
    loaded = result.state.notes[0]
    component = Component(current.binding, saved.key, {'api_version': FieldValue(Availability.VALUE, '69.0')})
    graph = DependencyGraph(current.binding, current.selection, current.coverage.relationships)
    candidate = render_generated(
        component,
        current.coverage,
        graph,
        identity=saved.obforce_id,
        managed_paths=result.paths,
        options=Options(include_audit_names=False),
    )
    patch = patch_note(raw, loaded.note, loaded.generated_region, candidate)
    assert patch.changed and parse_note(patch.content).region == patch.generated_region
    assert b'technical_debt_review_date: 2026-10-20' in patch.content
    assert b'sf_created_by' not in patch.content and b'sf_last_modified_by' not in patch.content
    assert patch.generated_region.count(ending) == patch.generated_region.count(b'\n')


def test_live_org_exact_binding_and_partial_scope_evidence(example, tmp_path):
    raw, document = example
    raw = raw.replace(b'sf_source_mode: local', b'sf_source_mode: live')
    parsed = parse_note(raw)
    binding = SourceBinding('fictional', 'live', '00D000000000001EAA')
    partial = CollectionCoverage(CoverageStatus.PARTIAL, 'synthetic', pagination='unknown')
    coverage = replace(document.coverage, binding=binding, inventory=partial, relationships=partial)
    note = replace(document.notes[0].note, binding=binding, generated_properties=parsed.generated_properties)
    current = StateDocument(binding, document.selection, coverage, (SavedNote(note, parsed.region),))
    vault, state_path, _ = vault_at(tmp_path, (raw, current))
    result = reconcile(vault, state_path, current)
    assert result.state.coverage == coverage and result.state.selection == current.selection
    assert result.state.notes[0].note.generated_properties['sf_lifecycle'].value == 'active'
    for other in (SourceBinding('fictional', 'live', '00D000000000002EAA'), SourceBinding('fictional', 'local')):
        with pytest.raises(ConflictError):
            reconcile_vault(vault, state_path, other, current.selection, excluded_roots=())
    for org in ('alias', '00D000000000001', '00D000000000001AAA', '001000000000001AAA'):
        data = json.loads(serialize_state(current))
        data['binding']['org_id'] = org
        with pytest.raises(ConflictError):
            parse_state(json.dumps(data).encode())


def test_move_invalidates_both_graph_directions_and_render_only(example, tmp_path):
    from obforce.graph.dependencies import DependencyGraph, Edge, Endpoint, Evidence
    from obforce.models import Component
    from obforce.renderer.notes import render_generated, render_new_note

    _, document = example
    binding = SourceBinding('fictional', 'live', '00D000000000001EAA')
    partial = CollectionCoverage(CoverageStatus.PARTIAL, 'synthetic-platform', pagination='unknown')
    coverage = replace(document.coverage, binding=binding, relationships=partial)
    components = [Component(binding, ComponentKey('fictional', 'ApexClass', None, name)) for name in ('A', 'B', 'C')]
    endpoints = [
        Endpoint('ApexClass', None, c.key.full_name, f'01p00000000000{index}', c.key, 'resolved')
        for index, c in enumerate(components, 1)
    ]
    graph = DependencyGraph(
        binding,
        coverage.selection,
        partial,
        (
            Edge(endpoints[0], endpoints[1], (Evidence('synthetic', partial),)),
            Edge(endpoints[1], endpoints[2], (Evidence('synthetic', partial),)),
        ),
    )
    paths = {c.key: f'Apex/{c.key.full_name}.md' for c in components}
    vault = tmp_path.resolve()
    notes = []
    for index, component in enumerate(components, 1):
        identity = f'00000000-0000-4000-8000-{index:012}'
        candidate = render_new_note(component, coverage, graph, identity=identity, managed_paths=paths)
        raw = candidate.text.encode()
        parsed = parse_note(raw)
        note = NoteState(
            identity,
            binding,
            component.key,
            paths[component.key],
            candidate.generated.source_hash,
            candidate.generated.graph_hash,
            candidate.generated.render_hash,
            parsed.generated_properties,
            parsed.region_hash,
        )
        notes.append(SavedNote(note, parsed.region))
        path = vault / note.path
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(raw)
    current = StateDocument(binding, coverage.selection, coverage, tuple(reversed(notes)))
    assert current.notes == tuple(notes)
    state_path = vault / '.obforce/state.json'
    state_path.parent.mkdir()
    state_path.write_bytes(serialize_state(current))
    old = paths[components[1].key]
    new = 'Moved.md'
    (vault / old).rename(vault / new)
    before = tree(vault)
    result = reconcile(vault, state_path, current)
    assert result.path_changes == (module.PathChange(components[1].key, old, new),)
    for component in components:
        assert graph.note_fingerprint(component.key, paths) != graph.note_fingerprint(component.key, result.paths)
        identity = current.notes[components.index(component)].note.obforce_id
        old_render = render_generated(component, coverage, graph, identity=identity, managed_paths=paths)
        new_render = render_generated(component, coverage, graph, identity=identity, managed_paths=result.paths)
        assert old_render.render_hash != new_render.render_hash and old_render.source_hash == new_render.source_hash
        assert result.state.notes[components.index(component)].note.source_hash == component.source_hash
    for saved, candidate in zip(current.notes, result.state.notes, strict=True):
        assert candidate.note.graph_hash == saved.note.graph_hash
        assert candidate.note.render_hash == saved.note.render_hash
    assert tree(vault) == before


@pytest.mark.parametrize('indicator', [b'OBFORCE', b'obforce_id: edited', b'sf_full_name: Unknown', b'<!-- obforce broken -->'])
def test_conservative_indicators_are_not_ordinary_notes(example, tmp_path, indicator):
    _, document = example
    vault, state_path, _ = vault_at(tmp_path, example)
    (vault / 'Suspicious.MD').write_bytes(indicator)
    with pytest.raises(ConflictError):
        reconcile(vault, state_path, document)


@pytest.mark.parametrize(
    'kind',
    [
        'case',
        'unicode',
        'reserved',
        'iteration',
        'excluded-link',
        'root-file',
        'state-directory',
        'control-file',
        'control-case',
        'ancestor-file',
        'load-permission',
    ],
)
def test_synthetic_filesystem_edges(example, tmp_path, monkeypatch, kind):
    _, document = example
    vault, state_path, path = vault_at(tmp_path, example)
    if kind in {'case', 'unicode', 'reserved', 'iteration'}:
        original = os.scandir

        class Entries:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

            def __iter__(self):
                if kind == 'iteration':
                    yield SimpleNamespace(name='Apex')
                    raise PermissionError('PRIVATE partial scan')
                if kind == 'reserved':
                    yield SimpleNamespace(name='NUL.md')
                    return
                yield SimpleNamespace(name='Name' if kind == 'case' else '\u00e9')
                yield SimpleNamespace(name='name' if kind == 'case' else 'e\u0301')

        monkeypatch.setattr(os, 'scandir', lambda p: Entries() if p == vault else original(p))
        original_lstat = Path.lstat
        monkeypatch.setattr(
            Path,
            'lstat',
            lambda p: (
                original_lstat(path)
                if p.parent == vault and p.name in {'Name', 'name', '\u00e9', 'e\u0301', 'NUL.md'}
                else original_lstat(p)
            ),
        )
    elif kind == 'excluded-link':
        link = tmp_path / 'source-link'
        symlink(link, vault, directory=True)
        with pytest.raises(ConflictError):
            reconcile_vault(vault, state_path, document.binding, document.selection, excluded_roots=(link,))
        return
    elif kind == 'root-file':
        vault, state_path = path, path / '.obforce/state.json'
    elif kind == 'state-directory':
        state_path.unlink()
        state_path.mkdir()
    elif kind == 'control-file':
        state_path.unlink()
        state_path.parent.rmdir()
        state_path.parent.write_text('ordinary')
    elif kind == 'control-case':
        (vault / '.Obsidian').mkdir()
    elif kind == 'ancestor-file':
        with pytest.raises(ConflictError):
            load_state(path / 'state.json')
        return
    else:
        original = os.open

        def fail(p, *a, **kw):
            if p == state_path:
                raise PermissionError('PRIVATE state')
            return original(p, *a, **kw)

        monkeypatch.setattr(os, 'open', fail)
        with pytest.raises(OperationalError) as error:
            load_state(state_path)
        assert 'PRIVATE' not in str(error.value)
        return
    with pytest.raises(OperationalError):
        reconcile(vault, state_path, document)


def test_case_only_unique_move_is_candidate_path_change(example, tmp_path):
    _, document = example
    vault, state_path, path = vault_at(tmp_path, example)
    moved = path.with_name('DEMOSERVICE.md')
    path.rename(moved)
    result = reconcile(vault, state_path, document)
    assert result.path_changes[0].new_path == 'Apex/DEMOSERVICE.md'


def test_missing_state_path_changed_during_scan_refuses(example, tmp_path, monkeypatch):
    _, document = example
    vault = tmp_path.resolve()
    original = module._Reader.finish

    def changed(reader):
        # Synthetic observation mismatch; no mutation of the fixture itself.
        reader.snapshots[vault / '.obforce'] = (1,)
        original(reader)

    monkeypatch.setattr(module._Reader, 'finish', changed)
    with pytest.raises(ConflictError):
        reconcile(vault, vault / '.obforce/state.json', document, initial=True)


@pytest.mark.parametrize('facet', ['audit', 'relationships'])
def test_local_scope_cannot_assert_collected_evidence(example, facet):
    _, document = example
    data = json.loads(serialize_state(document))
    data['coverage'][facet]['requested'] = True
    with pytest.raises(ConflictError):
        parse_state(json.dumps(data).encode())


def test_exact_body_saved_bytes_cannot_be_rebased_by_digest(example, tmp_path):
    raw, document = example
    vault, state_path, path = vault_at(tmp_path, example)
    changed = raw.replace(b'## Salesforce Metadata', b'## Human metadata edit')
    path.write_bytes(changed)
    data = json.loads(serialize_state(document))
    # Changing just the digest to match the current note cannot supply the saved bytes.
    data['notes'][0]['note']['generated_region_hash'] = parse_note(changed).region_hash
    state_path.write_text(json.dumps(data))
    before = tree(vault)
    with pytest.raises(ConflictError):
        reconcile(vault, state_path, document)
    assert tree(vault) == before


def test_deterministic_property_and_wire_order_and_actual_byte_limit(example):
    _, document = example
    raw = serialize_state(document)
    data = json.loads(raw)
    data['notes'][0]['note']['generated_properties'] = dict(reversed(data['notes'][0]['note']['generated_properties'].items()))
    assert serialize_state(parse_state(json.dumps(dict(reversed(data.items()))).encode())) == raw
    with pytest.raises(ConflictError):
        parse_state(b' ' * (const.MAX_STATE_BYTES + 1))
    fields = {**document.notes[0].note.generated_properties, 'sf_status': FieldValue(Availability.VALUE, '\ud800')}
    with pytest.raises(ConflictError):
        SavedNote(replace(document.notes[0].note, generated_properties=fields), document.notes[0].generated_region)
