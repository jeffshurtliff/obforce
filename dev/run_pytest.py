# -*- coding: utf-8 -*-
"""
:Module:            dev.run_pytest
:Synopsis:          Runs CI pytest with finite time, capture and diagnostic-line budgets
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     28 Oct 2026
"""

from __future__ import annotations

import argparse
import os
import queue
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

OUTPUT_BYTES = 2_097_152
LINE_BYTES = 4096
TEST_SECONDS = 2700
COLLECTION_SECONDS = 300


class _OutputLimit(Exception):
    """Signal an explicit failed diagnostic budget; never truncate and pass."""


def _stop(process: subprocess.Popen[bytes]) -> bool:
    """Reap the owned child and stop its cooperating process group/tree.

    Windows taskkill is a CI controller operation, never a Salesforce launcher.
    The outer Actions step/job deadlines remain a backstop for unconfirmed or
    escaped descendant cleanup; no hostile-process containment is promised.
    """
    confirmed = True
    if os.name == 'posix':
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        except OSError:
            confirmed = False
    elif process.poll() is None:
        system = os.environ.get('SystemRoot')
        if system:
            try:
                result = subprocess.run(
                    [str(Path(system) / 'System32/taskkill.exe'), '/PID', str(process.pid), '/T', '/F'],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=5,
                    check=False,
                )
                confirmed = result.returncode == 0
            except (OSError, subprocess.TimeoutExpired):
                confirmed = False
        else:
            confirmed = False
    try:
        if process.poll() is None:
            process.kill()
        process.wait(timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        confirmed = False
    return confirmed


def _read(stream, messages: queue.Queue, stopped: threading.Event) -> None:
    """Move bounded pipe chunks through a bounded queue, including EOF/read failure."""
    try:
        while not stopped.is_set():
            chunk = stream.read(4096)
            while not stopped.is_set():
                try:
                    messages.put(chunk or None, timeout=0.1)
                    break
                except queue.Full:
                    continue
            if not chunk:
                return
    except (OSError, ValueError):
        while not stopped.is_set():
            try:
                messages.put(OSError(), timeout=0.1)
                return
            except queue.Full:
                continue


def _run(command: list[str], log: Path, *, seconds: float, output_bytes: int = OUTPUT_BYTES, line_bytes: int = LINE_BYTES) -> int:
    """Capture combined output exclusively, fail on overflow/deadline and preserve exit status.

    Stored raw output and emitted console output each have a finite byte ceiling.
    Oversized lines are retained only in the bounded capture, never printed.
    Budget failure stops the child and labels the capture incomplete; it cannot
    be a successful or complete test/coverage result. No automatic retry.
    """
    messages: queue.Queue = queue.Queue(maxsize=4)
    stopped = threading.Event()
    pending = bytearray()
    captured = console = 0
    reason = 'complete'
    complete = False
    deadline = time.monotonic() + seconds
    exited_at = None

    def emit(raw: bytes) -> None:
        nonlocal console
        if len(raw) > line_bytes:
            raise _OutputLimit('diagnostic_line_limit')
        # The prefix prevents child text from becoming an Actions workflow command.
        text = '[pytest] ' + raw.decode('utf-8', errors='replace').rstrip('\r\n') + '\n'
        size = len(text.encode('utf-8'))
        if console + size > output_bytes:
            raise _OutputLimit('console_output_limit')
        console += size
        sys.stdout.write(text)
        sys.stdout.flush()

    with log.open('xb') as output:
        process = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=0,
            start_new_session=os.name == 'posix',
        )
        reader = threading.Thread(target=_read, args=(process.stdout, messages, stopped), daemon=True)
        reader.start()
        try:
            while True:
                now = time.monotonic()
                if now >= deadline:
                    reason = 'wall_time_limit'
                    break
                if process.poll() is not None:
                    exited_at = exited_at or now
                    if now - exited_at > 2:
                        reason = 'pipe_cleanup_limit'
                        break
                try:
                    chunk = messages.get(timeout=min(0.1, deadline - now))
                except queue.Empty:
                    continue
                if isinstance(chunk, OSError):
                    reason = 'pipe_read_failure'
                    break
                if chunk is None:
                    # Closed output does not prove that the process has exited.
                    try:
                        process.wait(timeout=max(0.001, deadline - time.monotonic()))
                    except subprocess.TimeoutExpired:
                        reason = 'wall_time_limit'
                        break
                    if pending:
                        emit(bytes(pending))
                    complete = True
                    break
                remaining = output_bytes - captured
                output.write(chunk[:remaining])
                captured += min(len(chunk), remaining)
                if len(chunk) > remaining:
                    reason = 'raw_output_limit'
                    break
                pending.extend(chunk)
                while b'\n' in pending:
                    end = pending.index(b'\n') + 1
                    emit(bytes(pending[:end]))
                    del pending[:end]
                if len(pending) > line_bytes:
                    reason = 'diagnostic_line_limit'
                    break
        except _OutputLimit as error:
            reason = str(error)
        except KeyboardInterrupt:
            reason = 'interrupted'
        finally:
            stopped.set()
            cleaned = _stop(process)
            reader.join(timeout=2)
            if reader.is_alive():
                cleaned = False
            else:
                process.stdout.close()
        # Verbose pytest flushes the next node ID before running it, without a
        # newline until its result. Keep that bounded unfinished line visible
        # after a deadline too; it is diagnostic output, never a completed test.
        if not complete and pending and len(pending) <= line_bytes:
            print('CI pytest: unfinished child output follows; no completed result implied.', flush=True)
            try:
                emit(bytes(pending))
            except _OutputLimit:
                pass  # The existing failed outcome and both output ceilings remain.
        if not cleaned:
            if complete:
                reason = 'cleanup_unconfirmed'
            complete = False
    result = max(0, process.returncode or 0) if complete and cleaned else 1
    if process.returncode is not None and process.returncode < 0:
        result = 1
    print(
        f'CI pytest: {reason}; exit={result}; captured_bytes={captured}; '
        f'capture_complete={str(complete).lower()}; cleanup_confirmed={str(cleaned).lower()}',
        flush=True,
    )
    if not complete:
        print('CI test run stopped; retained log is a bounded prefix, not complete test or coverage evidence.', flush=True)
    return result


def main() -> int:
    """Run only the selected pytest phase; these are CI budgets, not application limits."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--log', type=Path, required=True)
    parser.add_argument('--collect-only', action='store_true')
    args = parser.parse_args()
    if not args.log.is_absolute() or not args.log.parent.is_dir():
        parser.error('Select an absolute log path with an existing parent outside the checkout')
    command = [sys.executable, '-m', 'pytest', '-ra', '--tb=short', '--show-capture=no', '--maxfail=5', '--color=no']
    if args.collect_only:
        command.extend(['--collect-only', '-qq'])
    else:
        command.extend(
            [
                '-v',
                '--durations=25',
                '--cov=obforce',
                '--cov-report=term-missing',
                '--cov-config=' + str(Path(__file__).resolve().parents[1] / 'pyproject.toml'),
            ]
        )
    try:
        return _run(command, args.log, seconds=COLLECTION_SECONDS if args.collect_only else TEST_SECONDS)
    except OSError:
        print('CI pytest could not start or create its exclusive log; no successful result.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
