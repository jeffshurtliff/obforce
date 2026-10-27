# -*- coding: utf-8 -*-
"""
:Module:            obforce.cli
:Synopsis:          Exposes explicit initialization, initial build and local recovery
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     26 Oct 2026
"""

from __future__ import annotations

from pathlib import Path

import click

from obforce.errors import OperationalError
from obforce.sync import engine
from obforce.sync.transactions import TransactionResult


@click.group(invoke_without_command=True, context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(package_name='obforce', prog_name='obforce')
def main() -> None:
    """Create Salesforce documentation from an explicit source.

    Initialize a configuration, preview/build an empty destination, then sync
    managed notes and a protected native Apex Classes dashboard.
    Commands are noninteractive; no config, vault or auth discovery occurs.

    Offline example (quote paths with spaces):
    obforce init --config ./obforce.toml --source "./Demo Project" --vault ./Knowledge --workspace-id demo
    Preview with build --config ./obforce.toml --dry-run, then build --config ./obforce.toml.
    Refresh with sync --config ./obforce.toml. Recover previews local journal evidence.
    Exit codes: 0 complete/no-op, 1 operation, 2 input, 3 conflict/recovery, 4 incomplete coverage.
    """
    if click.get_current_context().invoked_subcommand is None:
        click.echo(click.get_current_context().get_help())


def _finish(result: TransactionResult, summary: str = '') -> None:
    click.echo(summary + result.text, nl=False)
    click.echo('File totals include config (init), journaled targets (recovery), or changed notes/dashboard/state.')
    if result.status.value == 'no_op':
        click.echo('No changes; managed bytes and modification times preserved.')
    elif result.status.value == 'preview':
        click.echo('Preview only; no Obforce files or directories created.')
    elif result.status.value == 'blocked':
        click.echo('Batch refused; resolve the reported conflict/input before previewing again. No force/adoption mode.')
    if result.recovery_required:
        if result.outcome == 0:
            selection = (
                f'next operation: recover --config PATH --{result.recovery_operation}'
                if result.recovery_operation is not None
                else 'select --rollback or --cleanup to match the recorded commit phase'
            )
            click.echo(f'Validated local recovery preview; {selection}. Run only after reviewing this preview.')
        else:
            click.echo(
                'Recovery evidence retained; run recover --config PATH first. '
                'Use only the phase-matching --rollback or --cleanup; ambiguous evidence needs manual resolution.'
            )
    click.get_current_context().exit(int(result.outcome))


def _operational(error: OSError) -> None:
    raise OperationalError('Explicit filesystem operation failed; retained output may require manual resolution') from error


@main.command('init')
@click.option('--config', 'config_path', type=click.Path(path_type=Path), required=True)
@click.option('--source', help='Offline project root, relative to the config parent or absolute.')
@click.option('--org', help='Explicit live target; initialization never queries it.')
@click.option('--vault', required=True, help='Destination root, relative to the config parent or absolute.')
@click.option('--workspace-id', required=True)
@click.option('--dry-run', is_flag=True, help='Validate without creating any file or directory.')
def initialize(config_path: Path, source: str | None, org: str | None, vault: str, workspace_id: str, dry_run: bool) -> None:
    """Create a new config exclusively; its parent must already exist."""
    try:
        _finish(engine.initialize(config_path, source=source, org=org, vault=vault, workspace_id=workspace_id, preview=dry_run))
    except OSError as error:
        _operational(error)


@main.command()
@click.option('--config', 'config_path', type=click.Path(path_type=Path), required=True)
@click.option('--dry-run', is_flag=True, help='Plan without config/vault/control/staging artifacts.')
@click.option('--org', help='Override the target of a live config only; identity is independently verified.')
@click.option('--sf-executable', type=click.Path(path_type=Path), help='Explicit absolute trusted live CLI executable.')
@click.option(
    '--sf-directory', type=click.Path(path_type=Path), help='Explicit existing absolute neutral live working directory.'
)
@click.option('--inventory-scope-id', help='Optional immutable logical live inventory scope declaration.')
def build(
    config_path: Path,
    dry_run: bool,
    org: str | None,
    sf_executable: Path | None,
    sf_directory: Path | None,
    inventory_scope_id: str | None,
) -> None:
    """Build once into an absent or completely empty destination.

    Live previews perform read queries and sf may change its own local state.
    Windows sf execution remains refused. Offline builds need no external tool.
    Preview first with build --config "./Demo Config.toml" --dry-run.
    Use sync for a previously built vault; build never adopts or replaces it.
    """
    try:
        result, summary = engine.build(
            config_path,
            preview=dry_run,
            org=org,
            executable=sf_executable,
            directory=sf_directory,
            inventory_scope_id=inventory_scope_id,
        )
        _finish(result, summary)
    except OSError as error:
        _operational(error)


@main.command()
@click.option('--config', 'config_path', type=click.Path(path_type=Path), required=True)
@click.option('--dry-run', is_flag=True, help='Validate the complete refresh without creating artifacts.')
@click.option('--org', help='Override only a live target; actual org must match saved identity.')
@click.option('--sf-executable', type=click.Path(path_type=Path), help='Explicit absolute trusted live CLI executable.')
@click.option('--sf-directory', type=click.Path(path_type=Path), help='Explicit existing absolute neutral live directory.')
@click.option('--inventory-scope-id', help='Must match the immutable live build declaration.')
@click.option(
    '--attest-comparable-inventory',
    is_flag=True,
    help='Attest accessible live inventory scope continuity from build through retained observations.',
)
def sync(
    config_path: Path,
    dry_run: bool,
    org: str | None,
    sf_executable: Path | None,
    sf_directory: Path | None,
    inventory_scope_id: str | None,
    attest_comparable_inventory: bool,
) -> None:
    """Refresh existing managed notes while preserving human content.

    Missing proposals require comparable complete supported live inventory.
    Live previews can query sf and affect its own local state; Windows sf refuses.
    Preview first with sync --config "./Demo Config.toml" --dry-run.
    Generated note/dashboard edits block the whole batch; human note content stays owned by you.
    """
    try:
        result, summary = engine.sync(
            config_path,
            preview=dry_run,
            org=org,
            executable=sf_executable,
            directory=sf_directory,
            inventory_scope_id=inventory_scope_id,
            attest_comparable_inventory=attest_comparable_inventory,
        )
        _finish(result, summary)
    except OSError as error:
        _operational(error)


@main.command()
@click.option('--config', 'config_path', type=click.Path(path_type=Path), required=True)
@click.option('--dry-run', is_flag=True, help='Validate recovery evidence without writes (also the default).')
@click.option('--rollback', is_flag=True, help='Explicitly roll back a validated precommit transaction.')
@click.option('--cleanup', is_flag=True, help='Explicitly clean a validated committed transaction.')
def recover(config_path: Path, dry_run: bool, rollback: bool, cleanup: bool) -> None:
    """Preview, roll back or clean local evidence without acquiring a source.

    Start with recover --config PATH. Use --rollback before commit, --cleanup
    after commit. Unsafe/incomplete evidence is retained for manual resolution.
    """
    if sum((dry_run, rollback, cleanup)) > 1:
        raise click.UsageError('Recovery operation flags are mutually exclusive')
    try:
        _finish(engine.recover(config_path, operation='rollback' if rollback else 'cleanup' if cleanup else None))
    except OSError as error:
        _operational(error)
