# -*- coding: utf-8 -*-
"""
:Module:            tests.unit.test_cli
:Synopsis:          Verifies CLI discovery and explicit required arguments
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     25 Oct 2026
"""

from __future__ import annotations

from importlib import import_module
from importlib.metadata import version

import pytest
from click.testing import CliRunner

from obforce.cli import main


@pytest.mark.parametrize('arguments', [[], ['--help'], ['-h']])
def test_discovery(arguments: list[str]) -> None:
    """Show useful help without collecting a source or writing a vault."""
    result = CliRunner().invoke(main, arguments)
    assert result.exit_code == 0
    assert '--help' in result.output
    assert '--version' in result.output
    assert 'sync' in result.output and 'recover' in result.output


def test_installed_version() -> None:
    """Use distribution metadata as the single version source."""
    result = CliRunner().invoke(main, ['--version'])
    assert result.exit_code == 0
    assert result.output == f'obforce, version {version("obforce")}\n'


def test_module_import_does_not_run_cli(capsys: pytest.CaptureFixture[str]) -> None:
    """Allow importing the module entry point without executing the CLI."""
    import_module('obforce.__main__')
    captured = capsys.readouterr()
    assert captured.out == captured.err == ''


@pytest.mark.parametrize('argument', ['sync', '--org', '--source', '--unknown'])
def test_missing_arguments_and_unknown_options_are_usage_errors(argument: str) -> None:
    """Reject missing required selectors and unsupported top-level options."""
    result = CliRunner().invoke(main, [argument])
    assert result.exit_code == 2
    assert 'Error:' in result.output
