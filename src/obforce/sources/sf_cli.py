# -*- coding: utf-8 -*-
"""
:Module:            obforce.sources.sf_cli
:Synopsis:          Bounds a fixed read-only Salesforce CLI process protocol
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     19 Oct 2026
"""

from __future__ import annotations

import json
import math
import os
import re
import selectors
import signal
import stat

# Required boundary: explicit executable, fixed argv, no shell, bounded pipes.
import subprocess  # nosec B404
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from obforce import constants as const
from obforce.errors import ConfigError, OperationalError


class Operation(Enum):
    """Allow only nonverbose version and ordinary/Tooling SOQL queries."""

    VERSION = 'version'
    QUERY = 'query'
    TOOLING_QUERY = 'tooling_query'


@dataclass(frozen=True)
class Limits:
    """Set refusal limits at or below the internal hard ceilings; never truncate."""

    timeout: float = const.SF_TIMEOUT_SECONDS
    stdout: int = const.MAX_SF_STDOUT_BYTES
    stderr: int = const.MAX_SF_STDERR_BYTES

    def __post_init__(self) -> None:
        """Reject nonfinite, coerced, nonpositive, and excessive limits."""
        if (
            type(self.timeout) not in (int, float)
            or not 0 < self.timeout <= const.SF_TIMEOUT_SECONDS
            or not math.isfinite(self.timeout)
            or type(self.stdout) is not int
            or not 0 < self.stdout <= const.MAX_SF_STDOUT_BYTES
            or type(self.stderr) is not int
            or not 0 < self.stderr <= const.MAX_SF_STDERR_BYTES
        ):
            raise ConfigError('Invalid Salesforce CLI resource limits.')


@dataclass(frozen=True)
class Reply:
    """Hold private decoded data and observed signals, without declaring inventory coverage.

    Data must be normalized by a later adapter, never logged or rendered directly.
    Warnings and stderr expose only presence, never their potentially private text.
    """

    data: dict[str, Any] = field(repr=False)
    done: bool | None = None
    total_size: int | None = None
    next_records_url: str | None = field(default=None, repr=False)
    warnings_present: bool = False
    stderr_present: bool = False


def resolve_executable(executable: Path) -> Path:
    """Resolve one explicit trusted installation path without searching PATH or invoking it.

    :param executable: Absolute path selected by the caller, not a command string.
    :returns: Resolved executable regular file on the supported POSIX path.
    :raises ConfigError: If the path/platform/wrapper is unsupported.
    :raises OperationalError: If the supplied installation is absent or inaccessible.
    """
    if not isinstance(executable, Path) or not executable.is_absolute():
        raise ConfigError('An absolute Salesforce CLI executable path is required.')
    if executable.suffix.lower() in ('.cmd', '.bat', '.ps1', '.com'):
        raise ConfigError('Salesforce CLI command wrappers are unsupported; no shell fallback is available.')
    if os.name != 'posix':
        raise ConfigError('Salesforce CLI execution is unavailable on this platform pending safe process cleanup support.')
    try:
        resolved = executable.resolve(strict=True)
        if resolved.suffix.lower() in ('.cmd', '.bat', '.ps1', '.com'):
            raise ConfigError('Salesforce CLI command wrappers are unsupported; no shell fallback is available.')
        if not stat.S_ISREG(resolved.stat().st_mode) or not os.access(resolved, os.X_OK):
            raise OperationalError('The explicit Salesforce CLI executable is not an executable regular file.')
        return resolved
    except (OSError, RuntimeError, ValueError):
        raise OperationalError('The explicit Salesforce CLI executable is unavailable.') from None


def _arguments(operation: Operation, target: str | None, query: str | None) -> list[str]:
    """Build only fixed command families; bind values as indivisible argv entries."""
    if not isinstance(operation, Operation):
        raise ConfigError('Unsupported Salesforce CLI operation.')
    if operation is Operation.VERSION:
        if target is not None or query is not None:
            raise ConfigError('Version operations do not accept an org target or query.')
        return ['version', '--json']
    if (
        not isinstance(target, str)
        or not 0 < len(target) <= const.MAX_SF_TARGET_CHARS
        or target != target.strip()
        or target.startswith('-')
        or any(ord(char) < 32 or ord(char) == 127 for char in target)
    ):
        raise ConfigError('An explicit, non-option-like Salesforce org target is required.')
    if (
        not isinstance(query, str)
        or not 0 < len(query) <= const.MAX_SF_QUERY_CHARS
        or re.match(r'\ASELECT\s', query, re.IGNORECASE) is None
        or any(ord(char) < 32 or ord(char) == 127 for char in query)
        or any(token in query for token in (';', '/*', '*/', '--'))
    ):
        raise ConfigError('A bounded single SELECT query is required.')
    args = ['data', 'query', '--json', '--target-org', target, '--query', query]
    if operation is Operation.TOOLING_QUERY:
        args.append('--use-tooling-api')
    return args


def _working_directory(directory: Path) -> Path:
    """Validate an explicit existing working directory without creating anything."""
    if not isinstance(directory, Path) or not directory.is_absolute():
        raise ConfigError('An absolute Salesforce CLI working directory is required.')
    try:
        resolved = directory.resolve(strict=True)
        if not resolved.is_dir():
            raise OSError
        return resolved
    except (OSError, RuntimeError, ValueError):
        raise OperationalError('The explicit Salesforce CLI working directory is unavailable.') from None


def _environment() -> dict[str, str]:
    """Keep only home/runtime essentials and fixed CLI controls; never inspect auth stores."""
    environment = {key: os.environ[key] for key in ('HOME', 'TMPDIR') if key in os.environ}
    environment.update(
        PATH=os.defpath,
        LANG='C.UTF-8',
        SF_DISABLE_TELEMETRY='true',
        SF_AUTOUPDATE_DISABLE='true',
        SF_SKIP_UPDATE_CHECK='true',
        SF_ORG_MAX_QUERY_LIMIT=str(const.MAX_SF_RECORDS),
        SF_LOG_LEVEL='fatal',
    )
    return environment


def _kill_group(process: subprocess.Popen[bytes]) -> None:
    """Kill remaining group members even if the leader exited; tolerate an absent group."""
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    except OSError:
        raise OperationalError('Salesforce CLI process cleanup could not be confirmed.') from None


def _collect(argv: list[str], directory: Path, limits: Limits) -> tuple[int, bytes, bool]:
    """Collect binary pipes within per-stream limits and one monotonic wall deadline.

    This POSIX implementation deliberately has no Windows pipe/thread fallback.
    It does not use communicate(), disk spooling, or unbounded background readers.
    The process group covers cooperative descendants; hostile setsid escape and
    OS-uninterruptible processes are outside this local trusted-CLI boundary.
    """
    deadline = time.monotonic() + limits.timeout
    try:
        process = subprocess.Popen(
            argv,
            cwd=directory,
            env=_environment(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            # Only validated allowlisted argv reaches this collector via run_sf.
            shell=False,  # nosec B603
            start_new_session=True,
            close_fds=True,
        )
    except (OSError, ValueError, subprocess.SubprocessError):
        raise OperationalError('Salesforce CLI could not be started.') from None
    output = bytearray()
    counts = {'stdout': 0, 'stderr': 0}
    try:
        with selectors.DefaultSelector() as selector:
            for name in ('stdout', 'stderr'):
                pipe = getattr(process, name)
                os.set_blocking(pipe.fileno(), False)
                selector.register(pipe, selectors.EVENT_READ, name)
            while selector.get_map():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise OperationalError('Salesforce CLI exceeded its time limit.')
                for key, _ in selector.select(min(remaining, 0.05)):
                    name = key.data
                    # Read at most the remaining allowance plus one sentinel byte.
                    allowance = getattr(limits, name) - counts[name]
                    chunk = os.read(key.fd, min(65_536, allowance + 1))
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    counts[name] += len(chunk)
                    if counts[name] > getattr(limits, name):
                        raise OperationalError('Salesforce CLI exceeded an output limit.')
                    if name == 'stdout':
                        output.extend(chunk)
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise OperationalError('Salesforce CLI exceeded its time limit.')
            code = process.wait(timeout=remaining)
        return code, bytes(output), counts['stderr'] > 0
    except subprocess.TimeoutExpired:
        raise OperationalError('Salesforce CLI exceeded its time limit.') from None
    except (OSError, ValueError):
        raise OperationalError('Salesforce CLI output collection failed.') from None
    finally:
        # Also runs on KeyboardInterrupt/SystemExit and successful leader exit.
        _cleanup(process)


def _cleanup(process: subprocess.Popen[bytes]) -> None:
    """Attempt every cleanup step and report only a fixed diagnostic on failure."""
    failed = False
    try:
        _kill_group(process)
    except OperationalError:
        failed = True
    for pipe in (process.stdout, process.stderr):
        if pipe is not None:
            try:
                pipe.close()
            except OSError:
                failed = True
    try:
        process.wait(timeout=const.SF_CLEANUP_SECONDS)
    except (OSError, subprocess.TimeoutExpired):
        failed = True
    if failed:
        raise OperationalError('Salesforce CLI process cleanup could not be confirmed.') from None


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Refuse duplicate keys rather than accepting ambiguous envelope fields."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError
        result[key] = value
    return result


def _invalid_constant(value: str) -> None:
    """Refuse JavaScript nonfinite extensions outside the JSON data model."""
    raise ValueError


def _decode(raw: bytes) -> dict[str, Any]:
    """Validate byte, nesting and node bounds before accepting a JSON object."""
    if len(raw) > const.MAX_SF_STDOUT_BYTES:
        raise OperationalError('Salesforce CLI exceeded an output limit.')
    try:
        # Bound container depth before the JSON decoder can recurse or allocate containers.
        depth, quoted, escaped = 0, False, False
        for byte in raw:
            if quoted:
                if escaped:
                    escaped = False
                elif byte == 92:
                    escaped = True
                elif byte == 34:
                    quoted = False
            elif byte == 34:
                quoted = True
            elif byte in (91, 123):
                depth += 1
                if depth > const.MAX_SF_JSON_DEPTH:
                    raise ValueError
            elif byte in (93, 125):
                depth -= 1
        value = json.loads(raw.decode('utf-8'), object_pairs_hook=_object, parse_constant=_invalid_constant)
        pending, nodes = [value], 0
        while pending:
            item = pending.pop()
            nodes += 1
            if nodes > const.MAX_SF_JSON_NODES or (isinstance(item, float) and not math.isfinite(item)):
                raise ValueError
            if isinstance(item, dict):
                pending.extend(item.values())
            elif isinstance(item, list):
                pending.extend(item)
        if not isinstance(value, dict):
            raise ValueError
        return value
    except (ValueError, UnicodeError, RecursionError):
        raise OperationalError('Salesforce CLI returned invalid or unsupported JSON.') from None


def _reply(operation: Operation, code: int, raw: bytes, stderr_present: bool) -> Reply:
    """Validate command-specific envelopes without copying diagnostic text to errors."""
    envelope = _decode(raw)
    # A failure exit never becomes a successful reply, irrespective of envelope status.
    if code != 0:
        error = envelope.get('error') if operation is Operation.VERSION else envelope
        valid = isinstance(error, dict) and all(isinstance(error.get(key), str) for key in ('name', 'message'))
        if operation is not Operation.VERSION:
            valid = valid and type(envelope.get('status')) is int and envelope['status'] > 0
        if not valid:
            raise OperationalError('Salesforce CLI returned an unsupported failure envelope.')
        raise OperationalError('Salesforce CLI failed; verify installation and authorized authentication separately.')
    if operation is Operation.VERSION:
        if not all(isinstance(envelope.get(key), str) and envelope[key] for key in ('cliVersion', 'architecture', 'nodeVersion')):
            raise OperationalError('Salesforce CLI returned an unsupported version envelope.')
        if 'error' in envelope or 'status' in envelope or 'result' in envelope:
            raise OperationalError('Salesforce CLI returned an unsupported version envelope.')
        return Reply({key: envelope[key] for key in ('cliVersion', 'architecture', 'nodeVersion')}, stderr_present=stderr_present)
    if type(envelope.get('status')) is not int or envelope['status'] != 0 or 'error' in envelope:
        raise OperationalError('Salesforce CLI returned a failure or unsupported query envelope.')
    result = envelope.get('result')
    warnings = envelope.get('warnings', [])
    if not isinstance(warnings, list) or not all(isinstance(warning, (str, dict)) for warning in warnings):
        raise OperationalError('Salesforce CLI returned an unsupported warning envelope.')
    if (
        not isinstance(result, dict)
        or not isinstance(result.get('records'), list)
        or len(result['records']) > const.MAX_SF_RECORDS
        or not all(isinstance(record, dict) for record in result['records'])
        or type(result.get('totalSize')) is not int
        or result['totalSize'] < len(result['records'])
        or type(result.get('done')) is not bool
        or 'outputFile' in result
    ):
        raise OperationalError('Salesforce CLI returned an unsupported query result.')
    next_url = result.get('nextRecordsUrl')
    if 'nextRecordsUrl' in result and (not isinstance(next_url, str) or not next_url or len(next_url) > const.MAX_SF_QUERY_CHARS):
        raise OperationalError('Salesforce CLI returned an unsupported continuation signal.')
    return Reply(result, result['done'], result['totalSize'], next_url, bool(warnings), stderr_present)


def run_sf(
    executable: Path,
    operation: Operation,
    *,
    directory: Path,
    target: str | None = None,
    query: str | None = None,
    limits: Limits | None = None,
) -> Reply:
    """Run one explicitly selected read-only operation through the internal boundary.

    This function grants no permission for live access. The caller must obtain
    authorization first. It never verifies org identity or inventory coverage.

    :param executable: Explicit absolute trusted CLI path; no executable discovery.
    :param operation: One member of the fixed operation enum.
    :param directory: Explicit existing absolute working directory selected by caller.
    :param target: Explicit alias/username for queries, never machine-default selection.
    :param query: Complete SELECT text from the internal caller, never interpolated here.
    :param limits: Validated byte/time ceilings; smaller limits are allowed.
    :returns: Private data and observed completion signals, not normalized inventory.
    :raises ConfigError: If invocation values or execution platform are unsupported.
    :raises OperationalError: If resolution, process collection, or JSON validation fails.
    """
    if limits is None:
        limits = Limits()
    if not isinstance(limits, Limits):
        raise ConfigError('Invalid Salesforce CLI resource limits.')
    arguments = _arguments(operation, target, query)
    resolved = resolve_executable(executable)
    working = _working_directory(directory)
    code, raw, stderr_present = _collect([str(resolved), *arguments], working, limits)
    return _reply(operation, code, raw, stderr_present)
