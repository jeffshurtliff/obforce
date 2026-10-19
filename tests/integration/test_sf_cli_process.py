# -*- coding: utf-8 -*-
"""
:Module:            tests.integration.test_sf_cli_process
:Synopsis:          Exercises bounded pipe collection with fictional Python children only
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     19 Oct 2026
"""

from __future__ import annotations

import os
import subprocess
import sys
import time

import pytest

from obforce.errors import OperationalError
from obforce.sources import sf_cli as sf

pytestmark = pytest.mark.skipif(os.name != 'posix', reason='POSIX collector only; Windows execution explicitly fails closed')


@pytest.fixture
def processes(monkeypatch):
    """Record fictional children to assert closed pipes and reaped leaders on every path."""
    children = []
    original = subprocess.Popen

    def spawn(argv, **kwargs):
        assert argv[:3] == [sys.executable, '-I', '-c']
        assert kwargs['shell'] is False and kwargs['start_new_session'] is True
        assert kwargs['stdin'] == subprocess.DEVNULL and kwargs['close_fds'] is True
        child = original(argv, **kwargs)
        children.append(child)
        return child

    monkeypatch.setattr(sf.subprocess, 'Popen', spawn)
    yield children
    for child in children:
        assert child.poll() is not None
        assert child.stdout.closed and child.stderr.closed


def collect(script, tmp_path, **limits):
    """Execute the active Python interpreter as a fictional transport test, never sf."""
    return sf._collect([sys.executable, '-I', '-c', script], tmp_path, sf.Limits(**limits))


def test_binary_pipe_success_exact_limit_and_stderr(tmp_path, processes):
    """Exactly-at-limit output passes without truncating; stderr becomes only presence."""
    code, raw, stderr = collect('import os; os.write(1,b"1234"); os.write(2,b"secret")', tmp_path, stdout=4, stderr=6)
    assert (code, raw, stderr) == (0, b'1234', True)
    assert len(processes) == 1 and list(tmp_path.iterdir()) == []


@pytest.mark.parametrize('descriptor', [1, 2])
def test_excessive_output_kills_and_reaps_before_parsing(tmp_path, processes, monkeypatch, descriptor):
    """A noisy stream cannot escape byte caps even while the other stream is idle."""
    monkeypatch.setattr(sf, '_decode', lambda raw: pytest.fail('oversized data reached JSON decoder'))
    script = f'import os\nwhile True: os.write({descriptor}, b"x" * 8192)'
    started = time.monotonic()
    with pytest.raises(OperationalError, match='output limit'):
        collect(script, tmp_path, stdout=64, stderr=64, timeout=3)
    assert time.monotonic() - started < 5
    assert processes[0].returncode is not None


def test_both_streams_drained_without_deadlock(tmp_path, processes):
    """Concurrent stdout/stderr collection does not deadlock on a full stderr pipe."""
    script = 'import os\nfor n in range(100):\n os.write(2,b"x"*512)\n os.write(1,b"y"*512)'
    assert collect(script, tmp_path) == (0, b'y' * 51200, True)


@pytest.mark.parametrize('script', ['import time; time.sleep(30)', 'import os,time; os.close(1); os.close(2); time.sleep(30)'])
def test_timeout_with_open_or_closed_pipes(tmp_path, processes, script):
    """The deadline also applies when the child closes pipes and continues running."""
    started = time.monotonic()
    with pytest.raises(OperationalError, match='time limit'):
        collect(script, tmp_path, timeout=0.15)
    assert time.monotonic() - started < 3


def test_nonzero_exit_is_preserved_by_transport(tmp_path, processes):
    """Envelope handling receives the actual exit status, never success by empty output."""
    assert collect('raise SystemExit(7)', tmp_path) == (7, b'', False)


def test_interruption_closes_pipes_and_reaps(tmp_path, processes, monkeypatch):
    """Interrupts propagate after group cleanup without hiding cancellation."""

    original = sf.selectors.DefaultSelector

    class InterruptedSelector:
        def __enter__(self):
            self.inner = original()
            return self

        def __exit__(self, *args):
            self.inner.close()

        def register(self, *args):
            return self.inner.register(*args)

        def get_map(self):
            return self.inner.get_map()

        def select(self, *args):
            raise KeyboardInterrupt

    monkeypatch.setattr(sf.selectors, 'DefaultSelector', InterruptedSelector)
    with pytest.raises(KeyboardInterrupt):
        collect('import time; time.sleep(30)', tmp_path)


def test_descendant_holding_pipes_is_bounded_and_killed(tmp_path, processes):
    """A leader exiting while its child holds pipes cannot evade the wall deadline."""
    marker = tmp_path / 'must-not-be-written'
    descendant = f'import time; from pathlib import Path; time.sleep(1); Path({str(marker)!r}).write_text("escaped")'
    script = f'import subprocess,sys; subprocess.Popen([sys.executable,"-I","-c",{descendant!r}])'
    with pytest.raises(OperationalError, match='time limit'):
        collect(script, tmp_path, timeout=0.2)
    # One bounded wait proves the child cannot later perform its fictional write.
    time.sleep(1.1)
    assert not marker.exists()
