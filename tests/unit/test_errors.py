# -*- coding: utf-8 -*-
"""
:Module:            tests.unit.test_errors
:Synopsis:          Verifies Click operational exits and aggregated outcome precedence
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     19 Oct 2026
"""

from __future__ import annotations

from itertools import permutations

import click
import pytest
from click.testing import CliRunner

from obforce.cli import main
from obforce.errors import ConfigError, ConflictError, CoverageError, ExitCode, ModelError, OperationalError, exit_code


@pytest.mark.parametrize(
    ('error_type', 'expected'), [(OperationalError, 1), (ConfigError, 2), (ModelError, 2), (ConflictError, 3), (CoverageError, 4)]
)
def test_typed_operational_failures_use_click_exit_protocol(error_type: type[OperationalError], expected: int) -> None:
    """Exercise actual Click exception handling through a test-only command."""

    @click.command()
    def command() -> None:
        raise error_type('Fictional safe diagnostic')

    result = CliRunner().invoke(command)
    assert result.exit_code == expected
    assert result.stderr == 'Error: Fictional safe diagnostic\n'
    assert 'Traceback' not in result.output


def test_precedence_is_order_independent_and_recovery_is_not_hidden() -> None:
    """Choose severity by frozen contract, never numeric maximum or encounter order."""
    for codes in permutations(ExitCode):
        assert exit_code(codes) == ExitCode.CONFLICT
    assert exit_code([]) == ExitCode.SUCCESS
    assert exit_code([ExitCode.INCOMPLETE, ExitCode.OPERATIONAL]) == ExitCode.OPERATIONAL
    assert exit_code([ExitCode.OPERATIONAL, ExitCode.INVALID]) == ExitCode.INVALID
    assert exit_code([ExitCode.SUCCESS, ExitCode.INCOMPLETE]) == ExitCode.INCOMPLETE
    with pytest.raises(ValueError):
        exit_code([99])


def test_production_cli_retains_click_usage_code_and_no_mutation_commands() -> None:
    """Internal contracts do not expose fake lifecycle/config commands."""
    runner = CliRunner()
    for arguments in [['--unknown'], ['--config', 'fictional.toml'], ['init'], ['build'], ['sync'], ['recover']]:
        assert runner.invoke(main, arguments).exit_code == 2
    assert runner.invoke(main, ['--help']).exit_code == 0
