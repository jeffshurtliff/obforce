# -*- coding: utf-8 -*-
"""
:Module:            tests.integration.test_transaction_process
:Synopsis:          Injects synthetic process death and concurrent kernel-lock ownership
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     21 Oct 2026
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

from obforce.sync.transactions import TransactionStatus, recover_transaction

_HELPERS = Path(__file__).resolve().parents[2] / 'dev/probe_transactions.py'
_SETUP = _HELPERS.read_text(encoding='utf-8').rsplit("if __name__ == '__main__':", 1)[0]
_GUARD = """
def deny(event, args):
    if event.startswith('socket.') or event in {'subprocess.Popen', 'os.system', 'os.posix_spawn', 'os.spawn'}:
        raise RuntimeError('Runtime network/process access forbidden')
sys.addaudithook(deny)
"""


@pytest.mark.parametrize(
    'boundary,index',
    [
        ('staging', -1),
        ('before', 0),
        ('after', 0),
        ('ready', -1),
        ('transfer', 0),
        ('journal_next', -1),
        ('replace_before', 0),
        ('replace_after', 0),
        ('published', 0),
        ('replace_before', 1),
        ('replace_after', 1),
        ('published', 1),
        ('replace_before', 2),
        ('replace_after', 2),
        ('published', 2),
        ('commit_before', -1),
        ('commit', -1),
        ('cleanup_before', 0),
        ('cleanup', 0),
        ('cleanup_final', -1),
        ('cleaned', -1),
    ],
)
@pytest.mark.parametrize('initial', [False, True])
def test_process_death_retains_or_recovers(tmp_path, boundary, index, initial):
    if initial and boundary == 'before':
        boundary = 'after'
    vault = (tmp_path / 'synthetic-vault').resolve()
    vault.mkdir()
    script = (
        _SETUP
        + _GUARD
        + """
import base64, json, os
vault = Path(sys.argv[1])
initial = sys.argv[4] == 'true'
if not initial:
    request = make_inputs(vault)
    setup = publish_plan(request.plan(), request)
    assert setup.status == TransactionStatus.COMMITTED, setup.text
baseline = {p.relative_to(vault).as_posix(): base64.b64encode(p.read_bytes()).decode('ascii')
            for p in vault.rglob('*') if p.is_file()}
(vault.parent / 'baseline.json').write_text(json.dumps(baseline))
request = make_inputs(vault, initial=initial)
def die(boundary, index=-1):
    if (boundary, index) == (sys.argv[2], int(sys.argv[3])):
        os._exit(97)
module._checkpoint = die
result = publish_plan(request.plan(), request)
raise AssertionError('Death boundary was not reached; ' + result.text)
"""
    )
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    process = subprocess.run(
        [sys.executable, '-I', '-c', script, str(vault), boundary, str(index), str(initial).lower()],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        timeout=30,
        check=False,
    )
    assert process.returncode == 97, process.stderr.decode()
    state = vault / '.obforce/state.json'
    result = recover_transaction(vault, state, excluded_roots=(), preview=False)
    if result.recovery_required:
        assert (vault / '.obforce/journal.json').exists()
        assert result.outcome == 3
    else:
        assert result.status in {TransactionStatus.ROLLED_BACK, TransactionStatus.CLEANED, TransactionStatus.NO_OP}
        if result.status == TransactionStatus.ROLLED_BACK:
            import base64

            baseline = json.loads((vault.parent / 'baseline.json').read_bytes())
            assert all((vault / path).read_bytes() == base64.b64decode(raw) for path, raw in baseline.items())
            if initial:
                assert not list(vault.rglob('*.md')) and not state.exists()
    assert not (tmp_path / '.obforce').exists()


def test_kernel_lock_releases_on_process_death(tmp_path):
    vault = (tmp_path / 'synthetic-vault').resolve()
    vault.mkdir()
    script = (
        _SETUP
        + _GUARD
        + """
import os, time
vault = Path(sys.argv[1])
request = make_inputs(vault)
setup = publish_plan(request.plan(), request)
assert setup.status == TransactionStatus.COMMITTED, setup.text
(vault.parent / 'baseline-lock').write_bytes((vault / '.obforce/writer.lock').read_bytes())
request = make_inputs(vault, initial=False)
with module._Lock(vault / '.obforce', module._Guard(request.plan().preconditions)):
    (vault.parent / 'ready').write_bytes(b'ready')
    time.sleep(20)
"""
    )
    process = subprocess.Popen(
        [sys.executable, '-I', '-c', script, str(vault)], cwd=tmp_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    child_output = (b'', b'')
    try:
        deadline = time.monotonic() + 10
        while not (tmp_path / 'ready').exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.01)
        if not (tmp_path / 'ready').exists():
            if process.poll() is None:
                process.kill()
            child_output = process.communicate(timeout=10)
            raise AssertionError('Lock holder was not ready; ' + child_output[1].decode()[:4096])
        contender = (
            _SETUP
            + _GUARD
            + """
vault = Path(sys.argv[1])
request = make_inputs(vault, initial=False)
# Windows denies reading another owner's locked byte. Snapshot its full
# pathname stamp here; compare its exact pre-lock bytes after owner death below.
def contender_snapshot():
    lock = vault / '.obforce/writer.lock'
    return {p: (module._lstat(p), p.read_bytes() if p.is_file() and p != lock else None)
            for p in (vault, *vault.rglob('*'))}
before = contender_snapshot()
result = publish_plan(request.plan(), request)
assert result.status == TransactionStatus.BLOCKED and result.outcome == 3, result.text
assert contender_snapshot() == before
"""
        )
        second = subprocess.run(
            [sys.executable, '-I', '-c', contender, str(vault)], cwd=tmp_path, capture_output=True, timeout=15, check=False
        )
        assert second.returncode == 0, second.stderr.decode()
    finally:
        if process.poll() is None:
            process.kill()
        child_output = process.communicate(timeout=10)
    assert (vault / '.obforce/writer.lock').read_bytes() == (tmp_path / 'baseline-lock').read_bytes()
    # The same persistent lock inode/token is reusable after the kernel released it.
    resume = (
        _SETUP
        + _GUARD
        + """
vault = Path(sys.argv[1])
request = make_inputs(vault, initial=False)
setup = publish_plan(request.plan(), request)
assert setup.status == TransactionStatus.COMMITTED, setup.text
"""
    )
    final = subprocess.run(
        [sys.executable, '-I', '-c', resume, str(vault)], cwd=tmp_path, capture_output=True, timeout=20, check=False
    )
    assert final.returncode == 0, final.stderr.decode()
