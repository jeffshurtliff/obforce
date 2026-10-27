# -*- coding: utf-8 -*-
"""
:Module:            tests.unit.test_pytest_safety
:Synopsis:          Regresses bounded pytest identifiers and CI output/time supervision offline
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     27 Oct 2026
"""

from __future__ import annotations

import json
import os
import runpy
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[2]
RUNNER = runpy.run_path(str(ROOT / 'dev/run_pytest.py'))
POLICY = (ROOT / 'tests/conftest.py').read_text(encoding='utf-8')
WINDOWS_LIMIT = """
import os
_original_setitem = type(os.environ).__setitem__
def limited(self, key, value):
    if key == 'PYTEST_CURRENT_TEST' and len(value.encode('utf-16-le')) // 2 > 32767:
        raise ValueError('the environment variable is longer than 32767 characters')
    return _original_setitem(self, key, value)
def pytest_sessionstart(session):
    type(os.environ).__setitem__ = limited
"""


def run_child(root: Path, code: str, policy: str, *args: str):
    """Run only synthetic pytest code with short output and no external plugins."""
    (root / 'test_payload.py').write_text(code, encoding='utf-8')
    (root / 'conftest.py').write_text(policy, encoding='utf-8')
    environment = dict(os.environ, PYTEST_DISABLE_PLUGIN_AUTOLOAD='1', PYTHONDONTWRITEBYTECODE='1')
    for name in ('PYTEST_ADDOPTS', 'PYTEST_CURRENT_TEST', 'PYTHONPATH'):
        environment.pop(name, None)
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', '-q', '--tb=no', '-rN', '--maxfail=0', *args],
        cwd=root,
        env=environment,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    assert len(result.stdout.encode()) + len(result.stderr.encode()) < 4096
    return result


def test_complete_large_payloads_execute_under_simulated_windows_environment_limit(tmp_path):
    """Keep every original boundary payload intact while publishing only bounded IDs."""
    code = """
import os, pytest
@pytest.mark.parametrize('payload', [b'x'*65537, b' '*16777217, b'x'*1048577])
def test_payload(payload):
    assert len(payload) in {65537, 16777217, 1048577}
    assert len(os.environ['PYTEST_CURRENT_TEST']) < 512
    assert 'length-' in os.environ['PYTEST_CURRENT_TEST']
"""
    result = run_child(tmp_path, code, POLICY + WINDOWS_LIMIT)
    assert result.returncode == 0 and '3 passed' in result.stdout


def test_large_unicode_parameter_uses_bounded_identifier(tmp_path):
    code = """
import os, pytest
@pytest.mark.parametrize('value', ['private-sentinel-' + '\\U0001f600'*40000])
def test_payload(value):
    assert len(value) == 40017
    assert 'private-sentinel' not in os.environ['PYTEST_CURRENT_TEST']
"""
    result = run_child(tmp_path, code, POLICY + WINDOWS_LIMIT)
    assert result.returncode == 0 and '1 passed' in result.stdout


def test_oversized_explicit_identifier_refuses_during_collection_without_echo(tmp_path):
    code = """
import pytest
@pytest.mark.parametrize('payload', [pytest.param(b'ok', id='private-sentinel-'+'x'*100000)])
def test_payload(payload):
    raise AssertionError('test body must not run')
"""
    result = run_child(tmp_path, code, POLICY + WINDOWS_LIMIT)
    assert result.returncode == 4 and 'Test identifier budget exceeded' in result.stderr
    assert 'private-sentinel' not in result.stdout + result.stderr
    assert 'test body must not run' not in result.stdout + result.stderr


def test_actual_limit_cases_have_short_descriptive_collection_ids(tmp_path):
    """Collect the real suite rather than checking a copy of the parameter labels."""
    result_path = tmp_path / 'collection.json'
    script = """
import json, pytest, sys
from pathlib import Path
class Probe:
    @pytest.hookimpl(trylast=True)
    def pytest_collection_finish(self, session):
        ids = [i.nodeid for i in session.items]
        Path(sys.argv[2]).write_text(json.dumps(ids))
raise SystemExit(pytest.main([sys.argv[1], '--collect-only', '-qq'], plugins=[Probe()]))
"""
    result = subprocess.run(
        [sys.executable, '-c', script, str(ROOT / 'tests/integration/test_qualification.py'), str(result_path)],
        cwd=tmp_path,
        env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'),
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    assert result.returncode == 0 and len(result.stdout.encode()) + len(result.stderr.encode()) < 4096
    identifiers = json.loads(result_path.read_text())
    assert max(len(value.encode()) for value in identifiers) <= 512
    for label in (
        'xml-byte-limit',
        'xml-forbidden-entity',
        'xml-depth-limit',
        'state-byte-limit',
        'state-depth-limit',
        'note-byte-limit',
    ):
        assert sum(value.endswith('[' + label + ']') for value in identifiers) == 1


@pytest.mark.parametrize('exit_code', [0, 7])
def test_ci_controller_preserves_complete_output_and_process_failure(tmp_path, capsys, exit_code):
    log = tmp_path / 'capture.log'
    result = RUNNER['_run'](
        [sys.executable, '-I', '-c', f'import sys; print("ok"); print("problem",file=sys.stderr); sys.exit({exit_code})'],
        log,
        seconds=5,
        output_bytes=4096,
        line_bytes=128,
    )
    assert result == exit_code and b'ok' in log.read_bytes() and b'problem' in log.read_bytes()
    assert 'capture_complete=true' in capsys.readouterr().out


@pytest.mark.parametrize(
    'code,output_bytes,line_bytes,reason',
    [
        ('import os; os.write(1,b"x"*10000)', 128, 4096, 'raw_output_limit'),
        ('import os; os.write(1,b"x"*10000)', 16384, 128, 'diagnostic_line_limit'),
        ('import os; os.write(1,b"\\n"*256)', 512, 128, 'console_output_limit'),
    ],
    ids=['raw-byte-budget', 'line-byte-budget', 'console-byte-budget'],
)
def test_ci_controller_output_overflow_is_failure_not_truncated_success(tmp_path, capsys, code, output_bytes, line_bytes, reason):
    log = tmp_path / 'capture.log'
    result = RUNNER['_run']([sys.executable, '-I', '-c', code], log, seconds=5, output_bytes=output_bytes, line_bytes=line_bytes)
    output = capsys.readouterr().out
    assert result == 1 and reason in output and 'capture_complete=false' in output
    assert log.stat().st_size <= output_bytes
    assert 'x' * 129 not in output and 'not complete test or coverage evidence' in output


@pytest.mark.parametrize('close_output', [False, True], ids=['open-output', 'closed-output'])
def test_ci_controller_deadline_applies_after_output_closes(tmp_path, capsys, close_output):
    code = 'import os,time; ' + ('os.close(1); os.close(2); ' if close_output else '') + 'time.sleep(30)'
    started = time.monotonic()
    result = RUNNER['_run']([sys.executable, '-I', '-c', code], tmp_path / 'capture.log', seconds=0.3)
    assert result == 1 and 'wall_time_limit' in capsys.readouterr().out
    assert time.monotonic() - started < 10


def test_ci_controller_never_overwrites_existing_evidence(tmp_path):
    log = tmp_path / 'capture.log'
    log.write_bytes(b'prior evidence')
    with pytest.raises(FileExistsError):
        RUNNER['_run']([sys.executable, '-I', '-c', 'raise AssertionError("must not run")'], log, seconds=1)
    assert log.read_bytes() == b'prior evidence'


def test_ci_controller_stops_cooperating_descendant(tmp_path, capsys):
    """Exercise the owned Python process tree, not any real external application."""
    marker = tmp_path / 'escaped.txt'
    child = f'import time; from pathlib import Path; time.sleep(1); Path({str(marker)!r}).write_text("escaped")'
    parent = f'import subprocess,sys,time; subprocess.Popen([sys.executable,"-I","-c",{child!r}]); time.sleep(30)'
    assert RUNNER['_run']([sys.executable, '-I', '-c', parent], tmp_path / 'capture.log', seconds=0.3) == 1
    assert 'wall_time_limit' in capsys.readouterr().out
    time.sleep(1.1)
    assert not marker.exists()


def test_ci_windows_cleanup_dispatch_uses_only_owned_pid_and_finite_wait():
    """Mock Windows dispatch separately from the native POSIX descendant probe."""
    from pathlib import PureWindowsPath

    child = SimpleNamespace(pid=321, returncode=None)
    child.poll = lambda: child.returncode
    child.wait = lambda timeout: child.returncode
    child.kill = lambda: setattr(child, 'returncode', 1)
    calls = []

    def stop(command, **kwargs):
        calls.append((command, kwargs))
        child.returncode = 1
        return SimpleNamespace(returncode=0)

    fake_process = SimpleNamespace(run=stop, DEVNULL=-3, TimeoutExpired=subprocess.TimeoutExpired)
    with patch.dict(
        RUNNER['_stop'].__globals__,
        {
            'os': SimpleNamespace(name='nt', environ={'SystemRoot': 'C:\\Windows'}),
            'Path': PureWindowsPath,
            'subprocess': fake_process,
        },
    ):
        assert RUNNER['_stop'](child)
    assert calls[0][0] == ['C:\\Windows\\System32\\taskkill.exe', '/PID', '321', '/T', '/F']
    assert calls[0][1]['timeout'] == 5 and calls[0][1]['check'] is False
