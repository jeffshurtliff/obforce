# -*- coding: utf-8 -*-
"""
:Module:            tests.unit.test_transactions
:Synopsis:          Exercises bounded synthetic publication, interruption and conservative recovery
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     21 Oct 2026
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
from dataclasses import replace

import pytest

from obforce import constants as const
from obforce.errors import ExitCode
from obforce.graph.dependencies import DependencyGraph
from obforce.models import (
    Availability,
    CollectionCoverage,
    Component,
    ComponentKey,
    Coverage,
    CoverageStatus,
    FieldValue,
    Selection,
    SourceBinding,
)
from obforce.sync import transactions as module
from obforce.sync.planner import ChangePlan
from obforce.sync.state import parse_state
from obforce.sync.transactions import TransactionInputs, TransactionStatus, publish_plan, recover_transaction


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError('Runtime network/process access forbidden')

    monkeypatch.setattr(socket, 'socket', deny)
    monkeypatch.setattr(subprocess, 'Popen', deny)


def tree(root, owner=None):
    return {
        p.relative_to(root).as_posix(): (
            p.lstat().st_mtime_ns,
            (owner.read() if owner is not None and p == owner.path else p.read_bytes()) if p.is_file() else None,
        )
        for p in (root, *root.rglob('*'))
    }


@pytest.fixture
def inputs(tmp_path):
    vault = (tmp_path / 'synthetic-vault').resolve()
    vault.mkdir()
    binding = SourceBinding('fictional', 'local')
    inventory = CollectionCoverage(CoverageStatus.COMPLETE, 'synthetic-local', pagination='exhausted', limit_reached=False)
    audit = CollectionCoverage(CoverageStatus.UNAVAILABLE, 'omitted', requested=False)
    relations = CollectionCoverage(CoverageStatus.NOT_COLLECTED, 'offline', requested=False)
    coverage = Coverage(binding, Selection(), inventory, audit, relations)
    graph = DependencyGraph(binding, coverage.selection, relations)
    components = tuple(
        Component(
            binding, ComponentKey('fictional', 'ApexClass', None, name), {'status': FieldValue(Availability.VALUE, 'Active')}
        )
        for name in ('Alpha', 'Beta')
    )
    return TransactionInputs(vault, vault / '.obforce/state.json', components, coverage, graph, (), initial=True)


def changed(inputs):
    return replace(
        inputs,
        initial=False,
        previous_graph=inputs.graph,
        components=tuple(
            replace(c, attributes={'status': FieldValue(Availability.VALUE, 'Inactive')}) for c in inputs.components
        ),
    )


def recover(inputs, preview=False):
    return recover_transaction(inputs.vault, inputs.state_path, excluded_roots=inputs.excluded_roots, preview=preview)


def test_create_update_noop_preview(inputs, monkeypatch):
    before = tree(inputs.vault)
    plan = inputs.plan()
    assert publish_plan(plan, inputs, preview=True).status == TransactionStatus.PREVIEW
    assert tree(inputs.vault) == before
    result = publish_plan(plan, inputs)
    assert result.status == TransactionStatus.COMMITTED, result.text
    assert parse_state(inputs.state_path.read_bytes()) == plan.state
    assert all((inputs.vault / a.path).read_bytes() == a.content for a in plan.actions)
    assert sorted(p.name for p in inputs.state_path.parent.iterdir()) == ['state.json', 'writer.lock']
    update = changed(inputs)
    plan = update.plan()
    result = publish_plan(plan, update)
    assert result.status == TransactionStatus.COMMITTED, result.text
    assert parse_state(inputs.state_path.read_bytes()) == plan.state
    next_inputs = replace(update, previous_graph=plan.graph)
    before = tree(inputs.vault)
    result = publish_plan(next_inputs.plan(), next_inputs)
    assert result.status == TransactionStatus.NO_OP, result.text
    assert tree(inputs.vault) == before
    assert recover(inputs).status == TransactionStatus.NO_OP


@pytest.mark.parametrize('boundary,index', [('ready', -1), ('published', 0), ('published', 1), ('published', 2), ('commit', -1)])
def test_recovery_recorded_boundaries(inputs, monkeypatch, boundary, index):
    assert publish_plan(inputs.plan(), inputs).status == TransactionStatus.COMMITTED
    original = {p.relative_to(inputs.vault).as_posix(): p.read_bytes() for p in inputs.vault.rglob('*.md')}
    original['.obforce/state.json'] = inputs.state_path.read_bytes()
    request = changed(inputs)

    def fail(name, number=-1):
        if (name, number) == (boundary, index):
            raise OSError('fictional private failure')

    monkeypatch.setattr(module, '_checkpoint', fail)
    result = publish_plan(request.plan(), request)
    assert result.recovery_required, result.text
    monkeypatch.setattr(module, '_checkpoint', lambda *args: None)
    before = tree(inputs.vault)
    preview = recover(inputs, preview=True)
    assert preview.status == TransactionStatus.PREVIEW, preview.text
    assert tree(inputs.vault) == before
    result = recover(inputs)
    assert result.status == (TransactionStatus.CLEANED if boundary == 'commit' else TransactionStatus.ROLLED_BACK), result.text
    if boundary != 'commit':
        assert all((inputs.vault / path).read_bytes() == data for path, data in original.items())
    assert recover(inputs).status == TransactionStatus.NO_OP


@pytest.mark.parametrize(
    'boundary,index',
    [
        ('preparing', -1),
        ('staging', -1),
        ('before', 0),
        ('after', 0),
        ('ready', -1),
        ('transfer', 0),
        ('replace_before', 0),
        ('replace_after', 0),
        ('published', 0),
        ('published', 1),
        ('published', 2),
        ('commit_before', -1),
        ('commit', -1),
        ('cleanup_before', 0),
        ('cleanup', 0),
        ('cleanup_final', -1),
        ('cleaned', -1),
    ],
)
@pytest.mark.parametrize('initial', [True, False])
def test_fault_boundaries_restore_or_retain(inputs, monkeypatch, boundary, index, initial):
    if not initial:
        assert publish_plan(inputs.plan(), inputs).status == TransactionStatus.COMMITTED
        request = changed(inputs)
    else:
        request = inputs
    plan = request.plan()
    before = {p: p.read_bytes() for p in inputs.vault.rglob('*') if p.is_file()}

    def fail(name, number=-1):
        if (name, number) == (boundary, index):
            raise PermissionError('fictional private detail')

    monkeypatch.setattr(module, '_checkpoint', fail)
    result = publish_plan(plan, request)
    assert result.status in {TransactionStatus.RECOVERY_REQUIRED, TransactionStatus.COMMITTED}, result.text
    assert 'fictional' not in result.text and str(inputs.vault) not in repr(result)
    monkeypatch.setattr(module, '_checkpoint', lambda *args: None)
    preserved = tree(inputs.vault)
    preview = recover(inputs, preview=True)
    assert tree(inputs.vault) == preserved
    recovered = recover(inputs)
    if recovered.recovery_required:
        assert (inputs.vault / '.obforce/journal.json').exists()
        assert tree(inputs.vault) == preserved
        blocked = publish_plan(request.plan(), request)
        assert blocked.outcome == ExitCode.CONFLICT
    else:
        assert recovered.status in {TransactionStatus.ROLLED_BACK, TransactionStatus.CLEANED, TransactionStatus.NO_OP}
        if recovered.status == TransactionStatus.ROLLED_BACK:
            for path, raw in before.items():
                assert path.read_bytes() == raw
            if initial:
                assert not list(inputs.vault.rglob('*.md')) and not inputs.state_path.exists()
    assert preview.status in {TransactionStatus.PREVIEW, TransactionStatus.RECOVERY_REQUIRED, TransactionStatus.NO_OP}


@pytest.mark.parametrize(
    'boundary,index',
    [
        ('rollback_before', 1),
        ('rollback', 1),
        ('rollback_after', 1),
        ('rollback', 0),
        ('rollback', 2),
        ('rolled_back', -1),
        ('cleanup', 0),
    ],
)
def test_rollback_interruption_can_resume_or_retains(inputs, monkeypatch, boundary, index):
    assert publish_plan(inputs.plan(), inputs).status == TransactionStatus.COMMITTED
    prior = inputs.state_path.read_bytes()
    request = changed(inputs)

    def stop(name, number=-1):
        if name == 'published' and number == 2:
            raise OSError('stop before commit')

    monkeypatch.setattr(module, '_checkpoint', stop)
    assert publish_plan(request.plan(), request).recovery_required

    def stop_rollback(name, number=-1):
        if (name, number) == (boundary, index):
            raise OSError('stop rollback')

    monkeypatch.setattr(module, '_checkpoint', stop_rollback)
    assert recover(inputs).recovery_required
    monkeypatch.setattr(module, '_checkpoint', lambda *args: None)
    result = recover(inputs)
    if result.recovery_required:
        assert (inputs.vault / '.obforce/journal.json').exists()
    else:
        assert result.status == TransactionStatus.ROLLED_BACK
        assert inputs.state_path.read_bytes() == prior


def pause_at_ready(inputs, monkeypatch, *, boundary='ready', index=-1):
    def stop(name, number=-1):
        if (name, number) == (boundary, index):
            raise OSError('synthetic interruption')

    monkeypatch.setattr(module, '_checkpoint', stop)
    result = publish_plan(inputs.plan(), inputs)
    assert result.recovery_required, result.text
    monkeypatch.setattr(module, '_checkpoint', lambda *args: None)
    return inputs.vault / '.obforce/journal.json'


@pytest.mark.parametrize(
    'edit', ['human', 'same_bytes', 'delete', 'symlink', 'hardlink', 'parent_swap', 'staging', 'journal_next', 'lock']
)
def test_intervening_recovery_edits_preserved(inputs, monkeypatch, tmp_path, edit):
    assert publish_plan(inputs.plan(), inputs).status == TransactionStatus.COMMITTED
    request = changed(inputs)
    journal = pause_at_ready(request, monkeypatch, boundary='published', index=0)
    record = json.loads(journal.read_bytes())
    target = inputs.vault / record['entries'][0]['path']
    if edit == 'human':
        target.write_bytes(target.read_bytes() + b'Human change\n')
    elif edit == 'same_bytes':
        raw = target.read_bytes()
        stamp = target.stat()
        target.write_bytes(raw)
        os.utime(target, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
    elif edit == 'delete':
        target.unlink()
    elif edit in {'symlink', 'hardlink'}:
        outside = tmp_path / 'unrelated.md'
        outside.write_bytes(b'Human outside\n')
        target.unlink()
        if edit == 'symlink':
            target.symlink_to(outside)
        else:
            os.link(outside, target)
    elif edit == 'parent_swap':
        parent = target.parent
        parent.rename(parent.with_name('Original Parent'))
        parent.mkdir()
        target.write_bytes(b'Human replacement\n')
    elif edit == 'staging':
        path = inputs.vault / '.obforce/transaction/0000.before'
        path.write_bytes(b'Forged backup\n')
    elif edit == 'journal_next':
        (journal.parent / 'journal.next').write_bytes(b'Unowned\n')
    elif edit == 'lock':
        (journal.parent / 'writer.lock').write_bytes(b'Invalid\n')
    before = tree(inputs.vault)
    assert recover(inputs, preview=True).recovery_required
    result = recover(inputs)
    assert result.recovery_required and result.outcome == 3, result.text
    assert tree(inputs.vault) == before and journal.exists()


@pytest.mark.parametrize(
    'mutator',
    [
        lambda p: replace(p, blocked=True),
        lambda p: replace(p, outcome=ExitCode.CONFLICT),
        lambda p: replace(p, actions=()),
        lambda p: replace(p, state_bytes=b'forged'),
        lambda p: replace(p, preconditions=()),
        lambda p: replace(p, state_changed=False),
        lambda p: replace(p, actions=(replace(p.actions[0], content=b'forged'), *p.actions[1:])),
        lambda p: ChangePlan((), ExitCode.SUCCESS, False),
    ],
)
def test_constructible_plan_is_not_authority(inputs, mutator):
    before = tree(inputs.vault)
    result = publish_plan(mutator(inputs.plan()), inputs)
    assert result.outcome == 3 and result.status == TransactionStatus.BLOCKED
    assert tree(inputs.vault) == before


@pytest.mark.parametrize(
    'mutation',
    [
        'version',
        'duplicate',
        'traversal',
        'absolute',
        'control',
        'unknown',
        'commit',
        'missing_state',
        'guard',
        'float',
        'uuid',
        'size',
        'deep',
        'bad_utf8',
    ],
)
def test_malicious_journal_refuses_without_writes(inputs, monkeypatch, mutation):
    journal = pause_at_ready(inputs, monkeypatch)
    raw = journal.read_bytes()
    data = json.loads(raw)
    if mutation == 'version':
        data['journal_schema'] = 99
    elif mutation == 'duplicate':
        raw = raw.replace(b'"journal_schema":1', b'"journal_schema":1,"journal_schema":1')
    elif mutation in {'traversal', 'absolute', 'control'}:
        data['entries'][0]['path'] = {'traversal': '../Outside.md', 'absolute': '/Outside.md', 'control': '.obsidian/Core.md'}[
            mutation
        ]
    elif mutation == 'unknown':
        data['unexpected'] = True
    elif mutation == 'commit':
        data['phase'] = 'committed'
    elif mutation == 'missing_state':
        data['entries'].pop()
    elif mutation == 'guard':
        data['guards'] = []
    elif mutation == 'float':
        data['entries'][0]['after']['size'] = 1.5
    elif mutation == 'uuid':
        data['transaction_id'] = 'private-invalid'
    elif mutation == 'size':
        data['entries'][0]['after']['size'] = const.MAX_NOTE_BYTES + 1
    elif mutation == 'deep':
        raw = b'[' * 1000 + b']' * 1000
    elif mutation == 'bad_utf8':
        raw = b'\xff'
    if mutation not in {'duplicate', 'deep', 'bad_utf8'}:
        raw = json.dumps(data).encode()
    journal.write_bytes(raw)
    before = tree(inputs.vault)
    result = recover(inputs)
    assert result.recovery_required and result.outcome == 3, result.text
    assert tree(inputs.vault) == before


@pytest.mark.parametrize(
    'which,boundary',
    [
        ('note', 'replace_before'),
        ('state', 'replace_before'),
        ('note', 'replace_after'),
        ('other', 'replace_before'),
        ('parent', 'replace_before'),
        ('lock', 'replace_before'),
    ],
)
def test_publication_intervening_edits_never_overwritten(inputs, monkeypatch, which, boundary):
    assert publish_plan(inputs.plan(), inputs).status == TransactionStatus.COMMITTED
    request = changed(inputs)
    plan = request.plan()
    target = inputs.state_path if which == 'state' else inputs.vault / plan.actions[0].path
    human = b'Human intervening private edit\n'
    fired = False
    rename_refused = []

    def edit(name, index=-1):
        nonlocal fired
        if name != boundary or index != 0 or fired:
            return
        fired = True
        if which in {'note', 'state'}:
            target.write_bytes(target.read_bytes() + human)
        elif which == 'other':
            (inputs.vault / 'Human.md').write_bytes(human)
        elif which == 'parent':
            (target.parent / 'Human.md').write_bytes(human)
        else:
            path = inputs.state_path.parent / 'writer.lock'
            try:
                path.rename(path.with_name('human-lock'))
            except PermissionError as error:
                if getattr(error, 'winerror', None) not in {32, 33}:
                    raise
                rename_refused.append(True)
                raise
            path.write_bytes(human)

    monkeypatch.setattr(module, '_checkpoint', edit)
    result = publish_plan(plan, request)
    assert fired and result.recovery_required, result.text
    assert result.outcome == (1 if rename_refused else 3), result.text
    monkeypatch.setattr(module, '_checkpoint', lambda *args: None)
    if rename_refused:
        assert recover(inputs).status == TransactionStatus.ROLLED_BACK
        assert not (inputs.state_path.parent / 'human-lock').exists()
        return
    before = tree(inputs.vault)
    assert recover(inputs).recovery_required
    assert tree(inputs.vault) == before
    if which in {'note', 'state'}:
        assert target.read_bytes().endswith(human)


@pytest.mark.parametrize('boundary', ['rollback_before', 'cleanup_before'])
def test_rollback_and_committed_cleanup_preserve_edits(inputs, monkeypatch, boundary):
    assert publish_plan(inputs.plan(), inputs).status == TransactionStatus.COMMITTED
    request = changed(inputs)
    pause_at_ready(
        request,
        monkeypatch,
        boundary='published' if boundary == 'rollback_before' else 'commit',
        index=0 if boundary == 'rollback_before' else -1,
    )
    target = inputs.vault / json.loads((inputs.state_path.parent / 'journal.json').read_bytes())['entries'][0]['path']
    fired = False

    def edit(name, index=-1):
        nonlocal fired
        if name == boundary and index == 0 and not fired:
            fired = True
            target.write_bytes(target.read_bytes() + b'Human change\n')

    monkeypatch.setattr(module, '_checkpoint', edit)
    result = recover(inputs)
    assert fired and result.recovery_required, result.text
    assert target.read_bytes().endswith(b'Human change\n')
    assert (inputs.state_path.parent / 'journal.json').exists()


@pytest.mark.parametrize(
    'limit',
    [
        'MAX_TRANSACTION_FILES',
        'MAX_TRANSACTION_BYTES',
        'MAX_TRANSACTION_GUARDS',
        'MAX_JOURNAL_BYTES',
        'MAX_JOURNAL_NODES',
        'MAX_TRANSACTION_DIRECTORIES',
    ],
)
def test_finite_limits_refuse_or_retain(inputs, monkeypatch, limit):
    before = tree(inputs.vault)
    plan = inputs.plan()
    monkeypatch.setattr(const, limit, 1)
    result = publish_plan(plan, inputs)
    assert result.status in {TransactionStatus.BLOCKED, TransactionStatus.RECOVERY_REQUIRED}, result.text
    assert not list(inputs.vault.rglob('*.md')) and not inputs.state_path.exists()
    if not (inputs.vault / '.obforce').exists():
        assert tree(inputs.vault) == before


@pytest.mark.parametrize('failure', ['write', 'sync', 'directory_sync', 'replace', 'unlink'])
def test_io_failure_no_silent_partial_success(inputs, monkeypatch, failure):
    plan = inputs.plan()

    def deny(*args, **kwargs):
        raise OSError('No space or permission: private text')

    if failure == 'write':
        monkeypatch.setattr(module, '_write_new', deny)
    elif failure == 'sync':
        monkeypatch.setattr(module.os, 'fsync', deny)
    elif failure == 'directory_sync':
        monkeypatch.setattr(module, '_sync_directory', deny)
    elif failure == 'replace':
        monkeypatch.setattr(module.os, 'replace', deny)
    else:
        monkeypatch.setattr(module.Path, 'unlink', deny)
    result = publish_plan(plan, inputs)
    assert result.status in {TransactionStatus.BLOCKED, TransactionStatus.RECOVERY_REQUIRED}
    assert result.outcome == ExitCode.OPERATIONAL and 'private' not in result.text


def test_lock_content_and_ownership_are_required(inputs, monkeypatch):
    assert publish_plan(inputs.plan(), inputs).status == TransactionStatus.COMMITTED
    request = changed(inputs)
    plan = request.plan()
    lock = inputs.state_path.parent / 'writer.lock'
    raw = lock.read_bytes()
    with module._Lock(lock.parent, module._Guard(plan.preconditions)) as owner:
        before = tree(inputs.vault, owner)
        result = publish_plan(plan, request)
        assert result.outcome == 3 and not result.recovery_required
        assert tree(inputs.vault, owner) == before
    assert lock.read_bytes() == raw
    lock.write_bytes(b'Invalid lock\n')
    before = tree(inputs.vault)
    assert publish_plan(request.plan(), request).outcome == 3
    assert tree(inputs.vault) == before


def test_empty_initial_state_and_recovery_preview_create_nothing(inputs):
    empty = replace(inputs, components=())
    before = tree(empty.vault)
    assert recover(empty, preview=True).status == TransactionStatus.NO_OP
    assert tree(empty.vault) == before
    assert publish_plan(empty.plan(), empty, preview=True).status == TransactionStatus.PREVIEW
    assert tree(empty.vault) == before
    assert publish_plan(empty.plan(), empty).status == TransactionStatus.COMMITTED
    assert parse_state(empty.state_path.read_bytes()).notes == ()
    next_inputs = replace(empty, initial=False, previous_graph=empty.graph)
    before = tree(empty.vault)
    assert publish_plan(next_inputs.plan(), next_inputs).status == TransactionStatus.NO_OP
    assert tree(empty.vault) == before


@pytest.mark.parametrize('ending', [b'\n', b'\r\n'])
def test_user_owned_yaml_prose_and_line_endings_preserved(inputs, ending):
    from obforce.sync.notes import parse_note
    from obforce.sync.state import serialize_state

    assert publish_plan(inputs.plan(), inputs).status == TransactionStatus.COMMITTED
    document = parse_state(inputs.state_path.read_bytes())
    notes = []
    human_regions = {}
    for saved in document.notes:
        path = inputs.vault / saved.note.path
        raw = path.read_bytes().replace(b'"technical_debt": null', b'technical_debt: false # human assessment')
        raw = raw.replace(b'"tags":', b'"tags":') + b'\n## Human narrative\nPrivate fictional context\n'
        raw = raw.replace(b'\n', ending)
        path.write_bytes(raw)
        parsed = parse_note(raw)
        notes.append(
            replace(saved, note=replace(saved.note, generated_region_hash=parsed.region_hash), generated_region=parsed.region)
        )
        human_regions[path] = raw[parsed.region_end :]
    inputs.state_path.write_bytes(serialize_state(replace(document, notes=tuple(notes))))
    request = changed(inputs)
    plan = request.plan()
    assert not plan.blocked
    assert publish_plan(plan, request).status == TransactionStatus.COMMITTED
    for path, suffix in human_regions.items():
        parsed = parse_note(path.read_bytes())
        assert path.read_bytes()[parsed.region_end :] == suffix
        assert parsed.properties['technical_debt'] is False
        assert b'# human assessment' in path.read_bytes()
        assert parsed.ending == ending
    before = tree(inputs.vault)
    assert publish_plan(request.plan(), request).status == TransactionStatus.NO_OP
    assert tree(inputs.vault) == before


def test_state_only_user_move_never_renames(inputs):
    assert publish_plan(inputs.plan(), inputs).status == TransactionStatus.COMMITTED
    document = parse_state(inputs.state_path.read_bytes())
    moved = document.notes[0]
    origin = inputs.vault / moved.note.path
    target = inputs.vault / 'Already Moved.md'
    origin.rename(target)
    before = (target.read_bytes(), target.stat().st_mtime_ns)
    request = replace(inputs, initial=False, previous_graph=inputs.graph)
    plan = request.plan()
    assert not plan.blocked and plan.state_changed
    result = publish_plan(plan, request)
    assert result.status == TransactionStatus.COMMITTED and result.files == 1, result.text
    assert (target.read_bytes(), target.stat().st_mtime_ns) == before and not origin.exists()
    assert (
        next(s for s in parse_state(inputs.state_path.read_bytes()).notes if s.note.obforce_id == moved.note.obforce_id).note.path
        == 'Already Moved.md'
    )


def test_partial_coverage_remains_valid_and_cannot_mark_absence(inputs):
    binding = SourceBinding('fictional', 'live', '00D000000000001EAA')
    relations = CollectionCoverage(CoverageStatus.PARTIAL, 'synthetic-reported')
    coverage = replace(inputs.coverage, binding=binding, relationships=relations)
    components = tuple(replace(c, binding=binding) for c in inputs.components)
    graph = DependencyGraph(binding, coverage.selection, relations)
    request = replace(inputs, components=components, coverage=coverage, graph=graph, verified_org_id=binding.org_id)
    plan = request.plan()
    assert not plan.blocked and plan.outcome == 4
    result = publish_plan(plan, request)
    assert result.status == TransactionStatus.COMMITTED and result.outcome == 4
    partial = replace(coverage, inventory=replace(coverage.inventory, status=CoverageStatus.PARTIAL, pagination='unknown'))
    next_request = replace(
        request,
        components=components[:1],
        retained_components=components[1:],
        coverage=partial,
        previous_graph=graph,
        initial=False,
    )
    plan = next_request.plan()
    assert not plan.blocked and all(a.saved.note.generated_properties['sf_lifecycle'].value == 'active' for a in plan.actions)
    result = publish_plan(plan, next_request)
    assert result.status == TransactionStatus.COMMITTED and result.outcome == 4, result.text


def test_full_unrelated_source_configuration_and_inputs_untouched(inputs, tmp_path):
    source = tmp_path / 'source'
    source.mkdir()
    (source / 'Example.cls').write_bytes(b'// Fictional\n')
    config = tmp_path / 'explicit-config.toml'
    config.write_bytes(b'# Never discovered or read\n')
    ordinary = inputs.vault / 'Ordinary.md'
    ordinary.write_bytes(b'Human unowned note\n')
    obsidian = inputs.vault / '.obsidian'
    obsidian.mkdir()
    (obsidian / 'app.json').write_bytes(b'{"synthetic": true}\n')
    request = replace(inputs, excluded_roots=(source, config))
    before = (
        tree(source),
        tree(obsidian),
        ordinary.read_bytes(),
        ordinary.stat().st_mtime_ns,
        config.read_bytes(),
        config.stat().st_mtime_ns,
    )
    data = (request.components, request.coverage.canonical(), request.graph, request.options, request.layout)
    plan = request.plan()
    assert publish_plan(plan, request).status == TransactionStatus.COMMITTED
    assert (
        tree(source),
        tree(obsidian),
        ordinary.read_bytes(),
        ordinary.stat().st_mtime_ns,
        config.read_bytes(),
        config.stat().st_mtime_ns,
    ) == before
    assert (request.components, request.coverage.canonical(), request.graph, request.options, request.layout) == data


@pytest.mark.parametrize('mutation', ['late_note', 'late_state', 'parent', 'collision', 'source_overlap', 'missing_state'])
def test_stale_and_unsafe_candidate_complete_refusal(inputs, mutation):
    assert publish_plan(inputs.plan(), inputs).status == TransactionStatus.COMMITTED
    request = changed(inputs)
    plan = request.plan()
    target = inputs.vault / plan.actions[0].path
    if mutation == 'late_note':
        target.write_bytes(target.read_bytes() + b'Human\n')
    elif mutation == 'late_state':
        inputs.state_path.write_bytes(inputs.state_path.read_bytes() + b' ')
    elif mutation == 'parent':
        (target.parent / 'Other.md').write_bytes(b'Unowned\n')
    elif mutation == 'collision':
        (inputs.vault / 'CON.md').write_bytes(b'Unowned\n')
    elif mutation == 'source_overlap':
        request = replace(request, excluded_roots=(inputs.vault,))
    elif mutation == 'missing_state':
        inputs.state_path.unlink()
    before = tree(inputs.vault)
    result = publish_plan(plan, request)
    assert result.status == TransactionStatus.BLOCKED and result.outcome == 3, result.text
    assert tree(inputs.vault) == before


def test_mandatory_lock_reads_reuse_the_owning_handle(inputs, monkeypatch):
    """Model Windows denial of a second handle reading our own locked byte."""
    path = inputs.state_path.parent / 'writer.lock'
    owner = [None]
    reopens = []
    original_read, original_close = module.os.read, module.os.close
    original_bounded_read = module._Reader.read

    def descriptor_read(descriptor, length):
        raw = original_read(descriptor, length)
        if raw.startswith(b'obforce-lock-v1 '):
            owner[0] = descriptor
        return raw

    def descriptor_close(descriptor):
        if descriptor == owner[0]:
            owner[0] = None
        return original_close(descriptor)

    def bounded_read(reader, candidate, limit):
        if candidate == path and owner[0] is not None:
            reopens.append(True)
            raise PermissionError(13, 'Synthetic mandatory byte-lock read denial')
        return original_bounded_read(reader, candidate, limit)

    monkeypatch.setattr(module.os, 'read', descriptor_read)
    monkeypatch.setattr(module.os, 'close', descriptor_close)
    monkeypatch.setattr(module._Reader, 'read', bounded_read)
    result = publish_plan(inputs.plan(), inputs)
    assert result.status == TransactionStatus.COMMITTED, result.text
    assert not reopens and owner[0] is None


def test_windows_denied_lock_rename_is_a_refused_edit(inputs, monkeypatch):
    original = module.Path.rename

    def denied(path, target):
        if path.name == 'writer.lock':
            error = PermissionError(13, 'Synthetic Windows sharing refusal')
            error.winerror = 32
            raise error
        return original(path, target)

    monkeypatch.setattr(module.Path, 'rename', denied)
    test_publication_intervening_edits_never_overwritten(inputs, monkeypatch, 'lock', 'replace_before')


@pytest.mark.parametrize('field', ['st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns'])
def test_owned_lock_retains_full_descriptor_change_guards(inputs, monkeypatch, field):
    from types import SimpleNamespace

    from obforce.errors import ConflictError

    assert publish_plan(inputs.plan(), inputs).status == TransactionStatus.COMMITTED
    request = changed(inputs)
    guard = module._Guard(request.plan().preconditions)
    with module._Lock(inputs.state_path.parent, guard) as owner:
        original = module.os.fstat

        def changed_stat(descriptor):
            value = original(descriptor)
            if descriptor != owner.descriptor:
                return value
            values = {name: getattr(value, name) for name in dir(value) if name.startswith('st_')}
            values[field] += 1
            return SimpleNamespace(**values)

        monkeypatch.setattr(module.os, 'fstat', changed_stat)
        with pytest.raises(ConflictError):
            guard.check()


def test_owned_lock_bytes_and_lifetime_are_validated(inputs):
    from obforce.errors import ConflictError

    assert publish_plan(inputs.plan(), inputs).status == TransactionStatus.COMMITTED
    request = changed(inputs)
    guard = module._Guard(request.plan().preconditions)
    with module._Lock(inputs.state_path.parent, guard) as owner:
        raw = owner.read()
        # The owning handle itself can edit the byte; validation must catch it.
        os.lseek(owner.descriptor, 0, os.SEEK_SET)
        os.write(owner.descriptor, b'X')
        with pytest.raises(ConflictError):
            guard.check()
        assert raw.startswith(b'obforce-lock-v1 ')
    assert guard.owner is None and owner.descriptor is None
    with pytest.raises(ConflictError):
        owner.read()


def test_failed_lock_entry_detaches_and_closes(inputs, monkeypatch):
    from obforce.errors import ConflictError

    assert publish_plan(inputs.plan(), inputs).status == TransactionStatus.COMMITTED
    guard = module._Guard(changed(inputs).plan().preconditions)
    owner = module._Lock(inputs.state_path.parent, guard)
    descriptors = []

    def fail(boundary, index=-1):
        if boundary == 'lock':
            descriptors.append(owner.descriptor)
            raise OSError('Synthetic entry interruption')

    monkeypatch.setattr(module, '_checkpoint', fail)
    with pytest.raises(OSError):
        with owner:
            raise AssertionError('Failed entry returned')
    assert guard.owner is None and owner.descriptor is None
    with pytest.raises(OSError):
        os.fstat(descriptors[0])
    with pytest.raises(ConflictError):
        owner.read()


@pytest.mark.parametrize('change', ['none', 'ctime', 'birthtime', 'missing_birthtime'])
def test_owned_lock_windows_cross_api_and_same_api_guards(inputs, monkeypatch, change):
    """Inject Windows pathname creation-time versus descriptor change-time semantics."""
    import stat
    from types import SimpleNamespace

    from obforce.errors import ConflictError
    from obforce.sync.state import _cross_api_stamp

    path = inputs.state_path.parent / 'writer.lock'
    raw = b'obforce-lock-v1 00000000-0000-4000-8000-000000000001\n'
    values = dict(
        st_dev=1,
        st_ino=2,
        st_mode=stat.S_IFREG | 0o600,
        st_nlink=1,
        st_size=len(raw),
        st_mtime_ns=20,
        st_ctime_ns=30,
        st_birthtime_ns=50,
    )
    pathname = SimpleNamespace(**values)
    descriptor = SimpleNamespace(**{**values, 'st_ctime_ns': 40})
    guard = module._Guard(())
    guard.stamps[path] = module._stamp(pathname)
    owner = module._Lock(path.parent, guard)
    owner.descriptor, owner._observation, owner._raw = 17, descriptor, raw
    guard.owner = owner
    calls = []

    def fstat(fd):
        assert fd == 17
        calls.append(True)
        updated = dict(descriptor.__dict__)
        if len(calls) > 1:
            if change == 'ctime':
                updated['st_ctime_ns'] += 1
            elif change == 'birthtime':
                updated['st_birthtime_ns'] += 1
            elif change == 'missing_birthtime':
                del updated['st_birthtime_ns']
        return SimpleNamespace(**updated)

    monkeypatch.setattr(module.Path, 'lstat', lambda self: pathname)
    monkeypatch.setattr(module.os, 'fstat', fstat)
    monkeypatch.setattr(module.os, 'lseek', lambda fd, pos, whence: 0)
    monkeypatch.setattr(module.os, 'read', lambda fd, length: raw)
    monkeypatch.setattr(module, '_cross_api_stamp', lambda info: _cross_api_stamp(info, windows=True))
    if change == 'none':
        assert owner.read() == raw
    else:
        with pytest.raises(ConflictError):
            owner.read()
