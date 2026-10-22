# -*- coding: utf-8 -*-
"""
:Module:            tests.unit.test_engine
:Synopsis:          Verifies explicit public lifecycle with synthetic projects and guarded refusals
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     21 Oct 2026
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from obforce import constants as const
from obforce.cli import main
from obforce.config import load_config
from obforce.errors import ConflictError
from obforce.sources import sf_cli
from obforce.sync import engine, transactions
from obforce.sync.notes import parse_note
from obforce.sync.state import parse_state


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError('Application runtime network/process access forbidden')

    monkeypatch.setattr(socket, 'socket', deny)
    monkeypatch.setattr(subprocess, 'Popen', deny)


def snapshot(root):
    return {
        p.relative_to(root).as_posix(): (p.lstat().st_mtime_ns, p.read_bytes() if p.is_file() else None)
        for p in (root, *root.rglob('*'))
    }


def invoke(*args):
    return CliRunner().invoke(main, [str(a) for a in args])


@pytest.fixture
def project(tmp_path):
    root = tmp_path.resolve()
    source = root / 'Fictional Project'
    source.mkdir()
    (source / 'sfdx-project.json').write_text('{"packageDirectories":[{"path":"package"}]}')
    classes = source / 'package/classes'
    classes.mkdir(parents=True)
    (classes / 'Alpha.cls').write_text('// Fictional, never parsed for dependencies')
    (classes / 'Alpha.cls-meta.xml').write_text(
        '<ApexClass xmlns="http://soap.sforce.com/2006/04/metadata">'
        '<apiVersion>67.0</apiVersion><status>Active</status></ApexClass>'
    )
    return root, source


def init(project, vault='New Parent/Vault', **extra):
    root, source = project
    config = root / 'config with spaces.toml'
    args = ['init', '--config', config, '--source', source.name, '--vault', vault, '--workspace-id', 'fictional']
    result = invoke(*args, *extra.get('args', []))
    assert result.exit_code == 0, (result.output, result.exception)
    return config, root / vault


@pytest.mark.parametrize('existing', [False, True])
def test_initial_journey_and_write_free_previews(project, existing):
    root, source = project
    before = snapshot(root)
    config, vault = init(project, args=['--dry-run'])
    assert not config.exists() and not vault.exists() and snapshot(root) == before
    config, vault = init(project)
    parsed = load_config(config)
    assert parsed.source.project == source and parsed.vault == vault
    assert parsed.options.include_audit_names and not parsed.options.include_namespaced
    if existing:
        vault.mkdir(parents=True)
    before = snapshot(root)
    result = invoke('build', '--config', config, '--dry-run')
    assert result.exit_code == 0, result.output
    assert 'inventory=complete' in result.output and 'audit=unavailable' in result.output
    assert 'relationships=not_collected' in result.output
    assert snapshot(root) == before
    protected = snapshot(source), config.read_bytes(), config.stat().st_mtime_ns
    result = invoke('build', '--config', config)
    assert result.exit_code == 0, (result.output, result.exception)
    state = parse_state((vault / '.obforce/state.json').read_bytes())
    assert len(state.notes) == 1 and state.binding.workspace_id == 'fictional'
    note = parse_note((vault / state.notes[0].note.path).read_bytes())
    assert note.properties['technical_debt'] is None
    assert (snapshot(source), config.read_bytes(), config.stat().st_mtime_ns) == protected
    before = snapshot(root)
    for args in (('build',), ('build', '--dry-run'), ('recover',), ('recover', '--dry-run'), ('recover', '--cleanup')):
        result = invoke(*args, '--config', config)
        assert result.exit_code == (3 if args[0] == 'build' else 0), result.output
        assert snapshot(root) == before


@pytest.mark.parametrize('selector', [[], ['--source', 'Project', '--org', 'fictional']])
def test_init_exclusive_source_selection(project, selector):
    root, _ = project
    before = snapshot(root)
    result = invoke('init', '--config', root / 'new.toml', '--vault', 'Vault', '--workspace-id', 'demo', *selector)
    assert result.exit_code == 2 and snapshot(root) == before


@pytest.mark.parametrize('raw', ['bad"\n[evil]', 'bad\x00name', '../demo', '', 'x' * 129])
def test_init_refuses_invalid_workspace_without_toml_injection(project, raw):
    root, source = project
    before = snapshot(root)
    result = invoke('init', '--config', root / 'new.toml', '--source', source.name, '--vault', 'Vault', '--workspace-id', raw)
    assert result.exit_code == 2 and snapshot(root) == before


def test_literal_quotes_serialize_and_paths_use_config_parent(project, monkeypatch):
    root, source = project
    configs = root / 'Configs'
    configs.mkdir()
    config = configs / 'fictional.toml'
    # TOML quoting of explicit aliases is exercised without contacting any org.
    result = invoke(
        'init', '--config', config, '--org', 'fictional "quoted" org', '--vault', '../Vault', '--workspace-id', 'demo'
    )
    assert result.exit_code == 0, result.output
    assert load_config(config).source.org == 'fictional "quoted" org'
    config.unlink()
    result = invoke('init', '--config', config, '--source', '../' + source.name, '--vault', '../Vault', '--workspace-id', 'demo')
    assert result.exit_code == 0, result.output
    monkeypatch.chdir(configs)
    result = invoke('build', '--config', './fictional.toml', '--dry-run')
    assert result.exit_code == 0, (result.output, result.exception)
    assert not (root / 'Vault').exists()


@pytest.mark.parametrize('entry', ['human.md', '.obsidian/app.json', '.obforce/state.json', 'Custom Code/Alpha.md', '.hidden'])
def test_nonempty_destinations_preserve_all_human_data(project, entry):
    root, _ = project
    config, vault = init(project)
    path = vault / entry
    path.parent.mkdir(parents=True)
    path.write_text('Human information including technical_debt_status')
    before = snapshot(root)
    for dry in ([], ['--dry-run']):
        result = invoke('build', '--config', config, *dry)
        assert result.exit_code == 3, result.output
        assert snapshot(root) == before


@pytest.mark.parametrize('option', ['--org', '--sf-executable', '--sf-directory'])
def test_offline_refuses_live_options(project, option):
    root, _ = project
    config, _ = init(project)
    before = snapshot(root)
    result = invoke('build', '--config', config, option, str(root))
    assert result.exit_code == 2 and snapshot(root) == before


@pytest.mark.parametrize('destination', ['Fictional Project', 'Fictional Project/inside', '.', 'CON', 'bad.', '.obsidian'])
def test_init_overlap_and_unsafe_roots(project, destination):
    root, source = project
    before = snapshot(root)
    result = invoke(
        'init', '--config', root / 'new.toml', '--source', source.name, '--vault', destination, '--workspace-id', 'demo'
    )
    assert result.exit_code in {2, 3}, result.output
    assert snapshot(root) == before


@pytest.mark.parametrize('config_bytes', [b'', b'schema_version = 99', b'[[[', b'vault="private-secret"', b'\xff'])
def test_invalid_config_is_bounded_and_write_free(project, config_bytes):
    root, _ = project
    config = root / 'invalid.toml'
    config.write_bytes(config_bytes)
    before = snapshot(root)
    for command in ('build', 'recover'):
        result = invoke(command, '--config', config)
        assert result.exit_code == 2, result.output
        assert 'private-secret' not in result.output and snapshot(root) == before


def test_missing_config_and_source_prerequisites(project):
    root, source = project
    assert invoke('build', '--config', root / 'absent.toml').exit_code == 2
    config, vault = init(project)
    (source / 'sfdx-project.json').unlink()
    before = snapshot(root)
    result = invoke('build', '--config', config)
    assert result.exit_code != 0 and snapshot(root) == before and not vault.exists()
    # Recovery does not collect missing/invalid source metadata.
    vault.mkdir(parents=True)
    result = invoke('recover', '--config', config)
    assert result.exit_code == 0, result.output


def test_config_exclusive_creation_and_changed_observation(project, monkeypatch):
    root, _ = project
    config, _ = init(project)
    before = snapshot(root)
    assert invoke('init', '--config', config, '--org', 'demo', '--vault', 'Vault', '--workspace-id', 'demo').exit_code == 3
    assert snapshot(root) == before
    config.unlink()

    def intervene(boundary):
        if boundary == 'config_ready':
            config.write_bytes(b'human config')

    monkeypatch.setattr(engine, '_checkpoint', intervene)
    result = invoke('init', '--config', config, '--org', 'demo', '--vault', 'Vault', '--workspace-id', 'demo')
    assert result.exit_code == 3 and config.read_bytes() == b'human config'


@pytest.mark.parametrize('intervention', ['file', 'same_config_bytes', 'ancestor', 'directory_edit'])
def test_setup_intervening_changes_are_preserved(project, monkeypatch, intervention):
    root, _ = project
    config, vault = init(project)

    def intervene(boundary):
        if boundary == ('directory_created' if intervention == 'directory_edit' else 'setup_ready'):
            if intervention == 'file':
                vault.parent.mkdir()
                (vault.parent / 'human.txt').write_text('human')
            elif intervention == 'same_config_bytes':
                stamp = config.stat()
                config.write_bytes(config.read_bytes())
                os.utime(config, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
            elif intervention == 'ancestor':
                (root / 'human.txt').write_text('human')
            else:
                (vault.parent / 'human.txt').write_text('human')

    monkeypatch.setattr(engine, '_checkpoint', intervene)
    result = invoke('build', '--config', config)
    assert result.exit_code == 3, (result.output, result.exception)
    assert not list(root.rglob('state.json'))
    if intervention != 'same_config_bytes':
        assert next(root.rglob('human.txt')).read_text() == 'human'


def test_guarded_setup_cleanup_does_not_remove_existing_parents(project, monkeypatch):
    root, _ = project
    config, vault = init(project)

    def fail(boundary):
        if boundary == 'publication_ready':
            raise OSError('private failure')

    monkeypatch.setattr(engine, '_checkpoint', fail)
    result = invoke('build', '--config', config)
    assert result.exit_code == 1, (result.output, result.exception)
    assert not vault.parent.exists() and config.exists() and root.exists()


@pytest.mark.parametrize('boundary,index', [('ready', -1), ('published', 0), ('published', 1), ('commit', -1)])
def test_public_recovery_selection_and_previews(project, monkeypatch, boundary, index):
    root, _ = project
    config, vault = init(project)

    def fail(name, number=-1):
        if (name, number) == (boundary, index):
            raise OSError('private fault')

    monkeypatch.setattr(transactions, '_checkpoint', fail)
    result = invoke('build', '--config', config)
    assert result.exit_code == 3 and 'recovery_required: true' in result.output, result.output
    monkeypatch.setattr(transactions, '_checkpoint', lambda *a: None)
    before = snapshot(root)
    assert invoke('recover', '--config', config).exit_code == 0
    assert snapshot(root) == before
    wrong, right = ('--rollback', '--cleanup') if boundary == 'commit' else ('--cleanup', '--rollback')
    assert invoke('recover', '--config', config, wrong).exit_code == 3
    assert snapshot(root) == before
    result = invoke('recover', '--config', config, right)
    assert result.exit_code == 0, result.output
    assert not (vault / '.obforce/journal.json').exists()
    if boundary != 'commit':
        assert not list(vault.rglob('*.md')) and not (vault / '.obforce/state.json').exists()
    assert invoke('build', '--config', config).exit_code == 3


def test_recovery_human_edits_and_unsupported_journal_retained(project, monkeypatch):
    root, _ = project
    config, vault = init(project)

    def fail(name, index=-1):
        if (name, index) == ('published', 0):
            raise OSError('fault')

    monkeypatch.setattr(transactions, '_checkpoint', fail)
    assert invoke('build', '--config', config).exit_code == 3
    monkeypatch.setattr(transactions, '_checkpoint', lambda *a: None)
    note = next(vault.rglob('*.md'))
    note.write_text('Human intervening technical_debt information')
    before = snapshot(root)
    assert invoke('recover', '--config', config, '--rollback').exit_code == 3
    assert snapshot(root) == before
    journal = vault / '.obforce/journal.json'
    data = json.loads(journal.read_bytes())
    data['journal_schema'] = 1
    journal.write_text(json.dumps(data))
    before = snapshot(root)
    result = invoke('recover', '--config', config)
    assert result.exit_code == 3 and snapshot(root) == before
    assert len(result.output.encode()) <= const.MAX_TRANSACTION_REPORT_BYTES


@pytest.mark.parametrize('flags', [('--rollback', '--cleanup'), ('--dry-run', '--rollback'), ('--dry-run', '--cleanup')])
def test_recovery_mutually_exclusive_operations(flags):
    assert invoke('recover', '--config', 'fictional.toml', *flags).exit_code == 2


def test_live_orchestration_uses_real_adapters_mocked_transport(project, monkeypatch):
    root, _ = project
    config = root / 'live.toml'
    result = invoke('init', '--config', config, '--org', 'fictional', '--vault', 'Live Vault', '--workspace-id', 'demo')
    assert result.exit_code == 0
    neutral = root / 'Neutral'
    neutral.mkdir()
    pending = json.loads((Path(__file__).parents[1] / 'fixtures/live/session.json').read_bytes())
    # Relationship adapter reverifies the exact inventory org then probes each ID.
    pending += [pending[0]] + [{'status': 0, 'result': {'records': [], 'totalSize': 0, 'done': True}}] * 4
    calls = []
    monkeypatch.setattr(sf_cli, 'resolve_executable', lambda p: p)

    def collect(argv, cwd, limits):
        calls.append(argv)
        assert cwd == neutral
        return 0, json.dumps(pending.pop(0)).encode(), False

    monkeypatch.setattr(sf_cli, '_collect', collect)
    result = invoke('build', '--config', config, '--sf-executable', root / 'fictional-sf', '--sf-directory', neutral)
    assert result.exit_code == 4, (result.output, result.exception)
    assert not pending and len(calls) > 5
    state = parse_state((root / 'Live Vault/.obforce/state.json').read_bytes())
    assert state.binding.org_id == '00D000000000001EAA' and state.coverage.relationships.status == 'partial'


def test_live_missing_explicit_process_options_refuses(project):
    root, _ = project
    config = root / 'live.toml'
    assert (
        invoke('init', '--config', config, '--org', 'fictional', '--vault', 'Live Vault', '--workspace-id', 'demo').exit_code == 0
    )
    before = snapshot(root)
    assert invoke('build', '--config', config).exit_code == 2
    assert snapshot(root) == before


@pytest.mark.parametrize(
    'limit,value',
    [
        ('MAX_TRANSACTION_FILES', 1),
        ('MAX_TRANSACTION_BYTES', 1),
        ('MAX_TRANSACTION_DIRECTORIES', 1),
        ('MAX_SETUP_DIRECTORIES', 1),
    ],
)
def test_over_bound_plan_refuses_before_setup(project, monkeypatch, limit, value):
    root, _ = project
    config, vault = init(project)
    before = snapshot(root)
    monkeypatch.setattr(const, limit, value)
    for flags in ([], ['--dry-run']):
        result = invoke('build', '--config', config, *flags)
        assert result.exit_code == 2, (result.output, result.exception)
        assert snapshot(root) == before and not vault.exists()


@pytest.mark.parametrize('spelling', ['VAULT', 'Vau\u0301lt'])
def test_case_unicode_output_aliases_refuse(project, spelling):
    root, _ = project
    (root / spelling).mkdir()
    target = 'Vault' if spelling == 'VAULT' else 'Vaúlt'
    before = snapshot(root)
    result = invoke('init', '--config', root / 'config.toml', '--org', 'fictional', '--vault', target, '--workspace-id', 'demo')
    assert result.exit_code == 3, result.output
    assert snapshot(root) == before


def test_parent_file_and_application_overlap_are_write_free(project):
    root, _ = project
    (root / 'occupied').write_text('human')
    before = snapshot(root)
    for vault in ('occupied/Vault', str(engine._application() / 'Vault')):
        result = invoke('init', '--config', root / 'new.toml', '--org', 'demo', '--vault', vault, '--workspace-id', 'demo')
        assert result.exit_code == 3 and snapshot(root) == before


def test_partial_offline_inventory_is_explicit_and_publishes_only_valid_notes(project):
    root, source = project
    (source / 'package/classes/Unpaired.cls').write_text('fictional')
    config, vault = init(project)
    result = invoke('build', '--config', config)
    assert result.exit_code == 4 and 'inventory=partial' in result.output, result.output
    state = parse_state((vault / '.obforce/state.json').read_bytes())
    assert len(state.notes) == 1 and state.coverage.inventory.status == 'partial'


@pytest.mark.parametrize('phase', ['publication_ready', 'config_created'])
def test_race_on_publication_boundary_preserves_intervening_human_data(project, monkeypatch, phase):
    root, source = project
    if phase == 'publication_ready':
        config, vault = init(project)

        def intervene(boundary):
            if boundary == phase:
                (vault / 'Human.md').write_text('human note')

        monkeypatch.setattr(engine, '_checkpoint', intervene)
        result = invoke('build', '--config', config)
        assert result.exit_code == 3, result.output
        assert (vault / 'Human.md').read_text() == 'human note'
        assert not (vault / '.obforce').exists()
    else:
        config = root / 'new.toml'

        def intervene(boundary):
            if boundary == phase:
                config.write_text('human config edit')
                raise ConflictError('Intervening config edit')

        monkeypatch.setattr(engine, '_checkpoint', intervene)
        result = invoke('init', '--config', config, '--source', source.name, '--vault', 'Vault', '--workspace-id', 'demo')
        assert result.exit_code == 3 and config.read_text() == 'human config edit'


def test_public_paths_refuse_symlink_and_lexical_link_escape(project, monkeypatch):
    root, source = project
    link = root / 'link'
    if os.name == 'nt':
        # Inject a rejected reparse observation, without requiring link privilege.
        original = engine._Reader.observe

        def observe(self, path, **kwargs):
            if path == link:
                raise ConflictError('Synthetic reparse path refused')
            return original(self, path, **kwargs)

        monkeypatch.setattr(engine._Reader, 'observe', observe)
    else:
        link.symlink_to(source, target_is_directory=True)
    config = root / 'new.toml'
    for path in ('link', 'link/../Fictional Project'):
        result = invoke('init', '--config', config, '--source', path, '--vault', 'Vault', '--workspace-id', 'demo')
        assert result.exit_code == 3 and not config.exists(), result.output


def test_config_hardlink_refused(project):
    root, _ = project
    config, _ = init(project)
    os.link(config, root / 'hardlinked.toml')
    before = snapshot(root)
    for command in ('build', 'recover'):
        assert invoke(command, '--config', config).exit_code == 3
        assert snapshot(root) == before


def test_neutral_directory_overlap_and_unverified_live_identity_refuse(project, monkeypatch):
    root, source = project
    config = root / 'live.toml'
    assert invoke('init', '--config', config, '--org', 'fictional', '--vault', 'Vault', '--workspace-id', 'demo').exit_code == 0
    before = snapshot(root)
    result = invoke('build', '--config', config, '--sf-executable', root / 'fake', '--sf-directory', engine._application())
    assert result.exit_code == 3 and snapshot(root) == before
    neutral = root / 'Neutral'
    neutral.mkdir()
    monkeypatch.setattr(sf_cli, 'resolve_executable', lambda p: p)
    monkeypatch.setattr(
        sf_cli, '_collect', lambda *a: (0, b'{"status":0,"result":{"records":[],"totalSize":0,"done":true}}', False)
    )
    before = snapshot(root)
    result = invoke('build', '--config', config, '--sf-executable', root / 'fake', '--sf-directory', neutral)
    assert result.exit_code == 4 and snapshot(root) == before and not (root / 'Vault').exists()


def test_missing_config_parent_is_not_created(project):
    root, source = project
    before = snapshot(root)
    result = invoke(
        'init',
        '--config',
        root / 'Absent/config.toml',
        '--source',
        str(source),
        '--vault',
        str(root / 'Vault'),
        '--workspace-id',
        'demo',
    )
    assert result.exit_code == 3 and snapshot(root) == before


@pytest.mark.parametrize(
    'operation,phase,checkpoint', [('rollback', 'published', 'rollback_before'), ('cleanup', 'commit', 'cleanup_before')]
)
def test_edits_during_public_recovery_preserve_human_information(project, monkeypatch, operation, phase, checkpoint):
    root, _ = project
    config, vault = init(project)

    def fail(name, index=-1):
        if name == phase and (name != 'published' or index == 0):
            raise OSError('fictional interruption')

    monkeypatch.setattr(transactions, '_checkpoint', fail)
    assert invoke('build', '--config', config).exit_code == 3
    note = next(vault.rglob('*.md'))

    def edit(name, index=-1):
        if name == checkpoint and index == 0:
            note.write_text('Human technical_debt_status: reviewed; preserve me')

    monkeypatch.setattr(transactions, '_checkpoint', edit)
    result = invoke('recover', '--config', config, '--' + operation)
    assert result.exit_code == 3, result.output
    assert note.read_text() == 'Human technical_debt_status: reviewed; preserve me'
    assert (vault / '.obforce/journal.json').exists()


def test_recovery_selection_is_revalidated_under_continuous_lock(project, monkeypatch):
    root, _ = project
    config, _ = init(project)

    def fail(name, index=-1):
        if name == 'ready':
            raise OSError('fictional interruption')

    monkeypatch.setattr(transactions, '_checkpoint', fail)
    assert invoke('build', '--config', config).exit_code == 3
    monkeypatch.setattr(transactions, '_checkpoint', lambda *a: None)
    original, acquired = transactions._Lock.__enter__, []

    def enter(self):
        result = original(self)
        acquired.append(True)
        return result

    monkeypatch.setattr(transactions._Lock, '__enter__', enter)
    validate, calls = transactions._recovery_operation, []

    def selected(journal, operation):
        calls.append(bool(acquired))
        validate(journal, operation)

    monkeypatch.setattr(transactions, '_recovery_operation', selected)
    result = invoke('recover', '--config', config, '--rollback')
    assert result.exit_code == 0 and calls == [False, True], result.output


def test_absent_preview_never_authorizes_existing_vault_writer(project, monkeypatch):
    root, _ = project
    config, vault = init(project)
    calls = []
    original = engine.plan_changes

    def capture(*args, **kwargs):
        plan = original(*args, **kwargs)
        calls.append(plan)
        return plan

    monkeypatch.setattr(engine, 'plan_changes', capture)
    assert invoke('build', '--config', config, '--dry-run').exit_code == 0
    assert calls and not calls[0].blocked and not vault.exists()
    # The ordinary planner/writer defaults still require an existing explicit vault.
    from obforce.graph.dependencies import DependencyGraph
    from obforce.models import Selection, SourceBinding
    from obforce.sources.local import collect_local
    from obforce.sync.transactions import TransactionInputs, publish_plan

    inventory = collect_local(load_config(config).source.project, SourceBinding('fictional', 'local'), Selection())
    graph = DependencyGraph(inventory.coverage.binding, Selection(), inventory.coverage.relationships)
    inputs = TransactionInputs(
        vault,
        vault / '.obforce/state.json',
        inventory.components,
        inventory.coverage,
        graph,
        engine._excluded(load_config(config)),
        initial=True,
    )
    assert inputs.plan().blocked
    before = snapshot(root)
    assert publish_plan(calls[0], inputs).outcome == 3
    assert snapshot(root) == before


def test_oversized_config_retains_invalid_outcome_without_source_or_output(project):
    root, _ = project
    config = root / 'oversized.toml'
    config.write_bytes(b' ' * (const.MAX_CONFIG_BYTES + 1))
    before = snapshot(root)
    for command in ('build', 'recover'):
        assert invoke(command, '--config', config).exit_code == 2
        assert snapshot(root) == before


@pytest.mark.parametrize('outcome', [1, 2, 3])
def test_setup_revalidation_keeps_typed_outcome_and_cleans_only_owned_parents(project, monkeypatch, outcome):
    root, _ = project
    config, vault = init(project)
    from obforce.errors import ExitCode
    from obforce.sync.planner import ChangePlan

    monkeypatch.setattr(transactions.TransactionInputs, 'plan', lambda self: ChangePlan((), ExitCode(outcome), True, None))
    result = invoke('build', '--config', config)
    assert result.exit_code == outcome, result.output
    assert not vault.parent.exists() and config.exists()
