# -*- coding: utf-8 -*-
"""
:Module:            tests.integration.test_entrypoints
:Synopsis:          Exercises installed entry points offline outside the checkout
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     19 Oct 2026
"""

from __future__ import annotations

import os
import subprocess
import sys
import sysconfig
from importlib.metadata import version
from pathlib import Path

import pytest


@pytest.mark.parametrize('entrypoint', ['console', 'console-via-python', 'module'])
@pytest.mark.parametrize('arguments', [[], ['--help'], ['--version'], ['build']])
def test_entrypoint_without_external_tools(entrypoint: str, arguments: list[str], tmp_path: Path) -> None:
    """Run with no external tools, block network calls, and leave the work directory untouched."""
    guard = tmp_path / 'guard'
    guard.mkdir()
    (guard / 'sitecustomize.py').write_text(
        'import sys\n'
        'def deny_network(event, args):\n'
        '    if event.startswith("socket."):\n'
        '        raise RuntimeError("Network access forbidden in offline CLI tests")\n'
        'sys.addaudithook(deny_network)\n',
        encoding='utf-8',
    )
    work = tmp_path / 'work'
    work.mkdir()
    environment = dict(os.environ, PATH='', PYTHONPATH=str(guard), PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1')
    if entrypoint == 'module':
        command = [sys.executable, '-m', 'obforce']
    else:
        # Poetry's editable install writes a Python script and a Windows .cmd
        # wrapper, while pip-installed executables are checked by check_artifacts.py.
        script = Path(sysconfig.get_path('scripts')) / 'obforce'
        assert script.is_file(), 'The installed Poetry console script is missing'
        command = [sys.executable, str(script)] if os.name == 'nt' or entrypoint == 'console-via-python' else [str(script)]
    result = subprocess.run(
        command + arguments, cwd=work, env=environment, capture_output=True, text=True, timeout=20, check=False
    )
    assert result.returncode == (2 if arguments == ['build'] else 0), result.stderr
    if arguments == ['--version']:
        assert result.stdout == f'obforce, version {version("obforce")}\n'
    elif arguments == ['build']:
        assert 'Error:' in result.stderr
    else:
        assert '--version' in result.stdout
        assert 'planned for later' in result.stdout
    assert list(work.iterdir()) == []
