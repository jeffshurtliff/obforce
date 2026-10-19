# -*- coding: utf-8 -*-
"""
:Module:            tests.unit.test_sf_cli
:Synopsis:          Verifies allowlisted argv, private envelopes and process refusals offline
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     19 Oct 2026
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest
from click.testing import CliRunner

from obforce import constants as const
from obforce.errors import ConfigError, OperationalError
from obforce.sources import sf_cli as sf

FIXTURES = Path(__file__).parents[1] / 'fixtures/sf_cli'
PRIVATE = 'private-token private@example.invalid https://auth.invalid/secret'


def fixture(name='query-success'):
    """Read only a named synthetic protocol fixture."""
    return (FIXTURES / f'{name}.json').read_bytes()


@pytest.fixture
def invocation(tmp_path, monkeypatch):
    """Mock resolution and collection; no path can execute a real Salesforce CLI."""
    observed = []
    executable = tmp_path / 'trusted installation/sf'
    directory = tmp_path / 'controlled work'
    directory.mkdir()
    monkeypatch.setattr(sf, 'resolve_executable', lambda path: executable)

    def collect(argv, cwd, limits):
        observed.append((argv, cwd, limits))
        return 0, fixture('version-success' if argv[1] == 'version' else 'query-success'), False

    monkeypatch.setattr(sf, '_collect', collect)
    return executable, directory, observed


@pytest.mark.parametrize('operation', [sf.Operation.QUERY, sf.Operation.TOOLING_QUERY])
@pytest.mark.parametrize('target', ['fictional org', 'demo; & | $(echo hi) `echo hi` %PATH% ^ ! > < " \\'])
def test_exact_query_argv(invocation, operation, target):
    """Metacharacters and spaces stay in one target argument without shell evaluation."""
    executable, directory, observed = invocation
    query = "SELECT Id FROM Organization WHERE Name = 'Fictional space & org'"
    reply = sf.run_sf(executable, operation, directory=directory, target=target, query=query)
    expected = [str(executable), 'data', 'query', '--json', '--target-org', target, '--query', query]
    if operation is sf.Operation.TOOLING_QUERY:
        expected.append('--use-tooling-api')
    assert observed[0][:2] == (expected, directory)
    assert reply.done is True and reply.total_size == 1
    assert 'fictional-record' not in repr(reply)


def test_exact_version_argv(invocation):
    """Nonverbose version has no org, plugin listing, or extra flags."""
    executable, directory, observed = invocation
    result = sf.run_sf(executable, sf.Operation.VERSION, directory=directory)
    assert observed[0][0] == [str(executable), 'version', '--json']
    assert result.done is None and result.total_size is None


@pytest.mark.parametrize(
    'target', [None, '', ' ', '-o', '--target-org=x', ' demo', 'demo ', 'demo\nsecret', 'a\x00b', 'x' * 257, 3]
)
def test_invalid_target_never_collects(invocation, target):
    """An implicit/default or option-like target is refused before process creation."""
    executable, directory, observed = invocation
    with pytest.raises(ConfigError) as error:
        sf.run_sf(executable, sf.Operation.QUERY, directory=directory, target=target, query='SELECT Id FROM Organization')
    assert error.value.exit_code == 2 and not observed


@pytest.mark.parametrize(
    'query',
    [
        None,
        '',
        '--help',
        'DELETE Id FROM X',
        'SELECT Id; SELECT Id',
        'SELECT Id -- comment',
        'SELECT /*x*/ Id',
        'SELECT\nId',
        'SELECT ' + 'x' * const.MAX_SF_QUERY_CHARS,
        1,
    ],
)
def test_invalid_query_never_collects(invocation, query):
    """Command strings, file flags, multiple statements and excessive queries are refused."""
    executable, directory, observed = invocation
    with pytest.raises(ConfigError):
        sf.run_sf(executable, sf.Operation.QUERY, directory=directory, target='fictional', query=query)
    assert not observed


@pytest.mark.parametrize('operation', ['query', 'login', 'apex run', ['data', 'query'], None])
def test_operation_is_enum_only(invocation, operation):
    """Arbitrary command strings/lists cannot enter the process boundary."""
    executable, directory, observed = invocation
    with pytest.raises(ConfigError):
        sf.run_sf(executable, operation, directory=directory)
    assert not observed


@pytest.mark.parametrize('kwargs', [{'target': 'demo'}, {'query': 'SELECT Id FROM X'}])
def test_version_refuses_query_parameters(invocation, kwargs):
    """Version cannot be turned into another operation through extra values."""
    executable, directory, observed = invocation
    with pytest.raises(ConfigError):
        sf.run_sf(executable, sf.Operation.VERSION, directory=directory, **kwargs)
    assert not observed


@pytest.mark.parametrize(
    'changes',
    [
        {'timeout': 0},
        {'timeout': True},
        {'timeout': float('nan')},
        {'timeout': float('inf')},
        {'timeout': 61},
        {'timeout': 10**1000},
        {'stdout': 0},
        {'stderr': -1},
        {'stdout': True},
        {'stderr': 65537},
    ],
)
def test_limits_refuse_invalid_or_raised_ceilings(changes):
    """Callers can reduce ceilings but cannot disable or inflate bounds."""
    with pytest.raises(ConfigError):
        sf.Limits(**changes)


def test_invalid_limits_object(invocation):
    """An arbitrary object cannot override the collector's limits."""
    executable, directory, observed = invocation
    with pytest.raises(ConfigError):
        sf.run_sf(executable, sf.Operation.VERSION, directory=directory, limits='unbounded')
    assert not observed


@pytest.mark.parametrize('path', ['sf --json', Path('sf'), 'sf', None])
def test_executable_requires_absolute_path(path):
    """No command-string parsing or implicit PATH search is available."""
    with pytest.raises(ConfigError):
        sf.resolve_executable(path)


@pytest.mark.parametrize('platform', ['nt', 'posix'])
@pytest.mark.parametrize('suffix', ['.cmd', '.CMD', '.bat', '.ps1', '.com'])
def test_wrappers_fail_closed(tmp_path, monkeypatch, platform, suffix):
    """Windows command wrappers are refused before any launch, even on POSIX."""
    monkeypatch.setitem(vars(sf), 'os', SimpleNamespace(**(vars(os) | {'name': platform})))
    with pytest.raises(ConfigError, match='wrappers'):
        sf.resolve_executable(tmp_path / f'sf{suffix}')


def test_windows_native_path_also_fails_closed(tmp_path, monkeypatch):
    """Native Windows execution is explicitly unavailable pending safe cleanup support."""
    monkeypatch.setitem(vars(sf), 'os', SimpleNamespace(**(vars(os) | {'name': 'nt'})))
    with pytest.raises(ConfigError, match='platform'):
        sf.resolve_executable(tmp_path / 'sf.exe')


def test_resolve_missing_nonexecutable_directory_and_explicit_file(tmp_path, monkeypatch):
    """Only an existing regular executable at the explicit absolute path is usable."""
    monkeypatch.setitem(vars(sf), 'os', SimpleNamespace(**(vars(os) | {'name': 'posix', 'access': lambda *args: True})))
    with pytest.raises(OperationalError):
        sf.resolve_executable(tmp_path / 'absent')
    with pytest.raises(OperationalError):
        sf.resolve_executable(tmp_path)
    file = tmp_path / 'fictional cli'
    file.write_text('Synthetic nonexecuted file')
    assert sf.resolve_executable(file) == file.resolve()
    monkeypatch.setattr(sf.os, 'access', lambda *args: False)
    with pytest.raises(OperationalError):
        sf.resolve_executable(file)


@pytest.mark.skipif(os.name != 'posix', reason='POSIX symlink resolution; Windows execution is explicitly unsupported')
def test_wrapper_cannot_hide_behind_symlink(tmp_path):
    """Resolved wrapper extensions are checked in addition to the supplied name."""
    wrapper = tmp_path / 'sf.cmd'
    wrapper.write_text('never execute')
    link = tmp_path / 'sf'
    link.symlink_to(wrapper)
    with pytest.raises(ConfigError, match='wrappers'):
        sf.resolve_executable(link)


@pytest.mark.parametrize('directory', [None, 'relative', Path('relative')])
def test_cwd_must_be_explicit_absolute(directory):
    """The machine's working directory is never selected implicitly."""
    with pytest.raises(ConfigError):
        sf._working_directory(directory)


def test_missing_cwd_is_not_created(tmp_path):
    """Invalid working directories fail without side effects."""
    absent = tmp_path / 'absent'
    with pytest.raises(OperationalError):
        sf._working_directory(absent)
    assert not absent.exists()


def test_environment_drops_overrides_and_credentials(monkeypatch):
    """Ambient targets, Node hooks, tokens and arbitrary CLI overrides are not propagated."""
    for key in ('SF_TARGET_ORG', 'SFDX_DEFAULTUSERNAME', 'NODE_OPTIONS', 'SF_ACCESS_TOKEN', 'SF_FLAGS_DIR', 'PYTHONPATH'):
        monkeypatch.setenv(key, PRIVATE)
    environment = sf._environment()
    assert PRIVATE not in repr(environment)
    assert environment['PATH'] == os.defpath
    assert environment['SF_ORG_MAX_QUERY_LIMIT'] == str(const.MAX_SF_RECORDS)
    assert environment['SF_DISABLE_TELEMETRY'] == 'true'


def test_preserves_partial_counts_continuation_and_warning_presence():
    """An empty partial result retains its signals and does not imply exhaustion."""
    reply = sf._reply(sf.Operation.QUERY, 0, fixture('query-partial'), True)
    assert reply.done is False and reply.total_size == 3
    assert reply.next_records_url == '/fictional/query/continuation'
    assert reply.warnings_present and reply.stderr_present
    assert 'continuation' not in repr(reply) and 'warning' not in repr(reply.data)


def test_empty_success_is_only_an_observed_result():
    """No normalized source identity or complete inventory is invented from process success."""
    result = {'status': 0, 'result': {'records': [], 'totalSize': 0, 'done': True}}
    reply = sf._reply(sf.Operation.QUERY, 0, json.dumps(result).encode(), False)
    assert reply.data['records'] == [] and reply.done is True
    assert not hasattr(reply, 'coverage') and not hasattr(reply, 'binding')


@pytest.mark.parametrize(
    'raw',
    [
        b'',
        b'noise',
        b'{}{}',
        b'[]',
        b'null',
        b'\xff',
        b'{"status":0,"status":1}',
        b'{"x":NaN}',
        b'{"x":Infinity}',
        b'{"x":1e999}',
        b'[' * 33 + b']' * 33,
    ],
)
def test_malformed_json_is_redacted(raw):
    """Malformed, duplicate, nonfinite, deeply nested and unexpected JSON fails safely."""
    with pytest.raises(OperationalError) as error:
        sf._reply(sf.Operation.QUERY, 0, raw, False)
    assert error.value.exit_code == 1
    assert error.value.__suppress_context__


@pytest.mark.parametrize(
    'change',
    [
        {'status': True},
        {'status': 1},
        {'status': '0'},
        {'result': []},
        {'warnings': 'secret'},
        {'warnings': [1]},
        {'error': {'message': PRIVATE}},
    ],
)
def test_invalid_query_envelopes(change):
    """Unexpected/failure envelopes never pass as success."""
    envelope = json.loads(fixture()) | change
    with pytest.raises(OperationalError) as error:
        sf._reply(sf.Operation.QUERY, 0, json.dumps(envelope).encode(), False)
    assert PRIVATE not in str(error.value)


@pytest.mark.parametrize(
    'change',
    [
        {'records': [1]},
        {'totalSize': True},
        {'totalSize': -1},
        {'totalSize': 0},
        {'done': 'true'},
        {'nextRecordsUrl': None},
        {'outputFile': 'private'},
        {'records': [{}] * 10001},
    ],
)
def test_invalid_query_result(change):
    """Record/count/type/file-output mismatches are refused without truncation."""
    envelope = json.loads(fixture())
    envelope['result'].update(change)
    with pytest.raises(OperationalError):
        sf._reply(sf.Operation.QUERY, 0, json.dumps(envelope).encode(), False)


def test_depth_scan_respects_escaped_quotes_and_brackets():
    """Brackets and escaped quotes in strings do not consume nesting allowance."""
    raw = json.dumps({'x': '["\\' * 100}).encode()
    assert sf._decode(raw)['x'] == '["\\' * 100


def test_json_byte_and_node_ceilings(monkeypatch):
    """Defensive parse bounds also protect injected process results."""
    monkeypatch.setattr(const, 'MAX_SF_STDOUT_BYTES', 4)
    with pytest.raises(OperationalError, match='output limit'):
        sf._decode(b'{"x":1}')
    monkeypatch.setattr(const, 'MAX_SF_STDOUT_BYTES', 100)
    monkeypatch.setattr(const, 'MAX_SF_JSON_NODES', 2)
    with pytest.raises(OperationalError, match='JSON'):
        sf._decode(b'{"x":[1,2]}')


@pytest.mark.parametrize(
    'operation,code,raw',
    [
        (sf.Operation.QUERY, 1, fixture('expired-auth')),
        (sf.Operation.QUERY, 1, fixture()),
        (sf.Operation.QUERY, 0, fixture('expired-auth')),
        (sf.Operation.VERSION, 1, json.dumps({'error': {'name': 'Error', 'message': PRIVATE}}).encode()),
        (sf.Operation.VERSION, 0, json.dumps({'error': {'message': PRIVATE}}).encode()),
        (sf.Operation.VERSION, 0, fixture()),
        (sf.Operation.VERSION, 0, b'{"cliVersion":0}'),
    ],
)
def test_failures_never_echo_private_data(operation, code, raw, caplog, capsys):
    """Errors, repr, Click output and logs expose no raw process/auth/personal data."""
    with pytest.raises(OperationalError) as error:
        sf._reply(operation, code, raw, True)
    assert PRIVATE not in str(error.value) and PRIVATE not in repr(error.value)
    runner = CliRunner()
    import click

    @click.command()
    def command():
        raise error.value

    result = runner.invoke(command)
    assert result.exit_code == 1 and PRIVATE not in result.output
    assert not caplog.records and capsys.readouterr() == ('', '')


def test_process_start_failure_does_not_expose_os_exception(tmp_path, monkeypatch):
    """OS failures cannot reveal argv, private paths or exception chains."""

    def fail(*args, **kwargs):
        raise OSError(PRIVATE)

    monkeypatch.setattr(sf.subprocess, 'Popen', fail)
    with pytest.raises(OperationalError) as error:
        sf._collect(['fictional'], tmp_path, sf.Limits())
    assert PRIVATE not in str(error.value) and error.value.__suppress_context__


def test_group_cleanup_errors_are_redacted(monkeypatch):
    """Cleanup errors also use fixed diagnostics under mocked POSIX semantics."""
    monkeypatch.setitem(vars(sf), 'signal', SimpleNamespace(SIGKILL=9))

    def fail(*args):
        raise PermissionError(PRIVATE)

    monkeypatch.setattr(sf.os, 'killpg', fail, raising=False)
    with pytest.raises(OperationalError, match='cleanup') as error:
        sf._kill_group(SimpleNamespace(pid=123))
    assert PRIVATE not in str(error.value)


def test_missing_group_is_already_clean(monkeypatch):
    """A fully exited process group does not turn successful collection into failure."""
    monkeypatch.setitem(vars(sf), 'signal', SimpleNamespace(SIGKILL=9))

    def missing(*args):
        raise ProcessLookupError

    monkeypatch.setattr(sf.os, 'killpg', missing, raising=False)
    sf._kill_group(SimpleNamespace(pid=123))


def test_cleanup_timeout_is_redacted(monkeypatch):
    """A child that cannot be reaped is reported as an operational cleanup failure."""

    class Process:
        pid = 123
        stdout = None
        stderr = None

        def wait(self, **kwargs):
            raise subprocess.TimeoutExpired(PRIVATE, 1)

    monkeypatch.setattr(sf, '_kill_group', lambda process: None)
    with pytest.raises(OperationalError, match='cleanup') as error:
        sf._cleanup(Process())
    assert PRIVATE not in str(error.value)


def test_success_exit_cannot_hide_version_error():
    """Even a version-shaped object with error/status markers is refused."""
    envelope = json.loads(fixture('version-success')) | {'error': {'message': PRIVATE}}
    with pytest.raises(OperationalError):
        sf._reply(sf.Operation.VERSION, 0, json.dumps(envelope).encode(), False)


def test_done_true_does_not_erase_truncation_or_continuation():
    """Contradictory completion/count signals remain observations for the later adapter."""
    envelope = json.loads(fixture('query-partial'))
    envelope['result']['done'] = True
    envelope['warnings'] = [{'message': PRIVATE}]
    reply = sf._reply(sf.Operation.QUERY, 0, json.dumps(envelope).encode(), False)
    assert reply.done is True and reply.total_size == 3 and reply.data['records'] == []
    assert reply.next_records_url and reply.warnings_present
    assert PRIVATE not in repr(reply) and not hasattr(reply, 'coverage')


def test_working_directory_file_is_refused(tmp_path):
    """A regular file cannot be a process working directory."""
    file = tmp_path / 'file'
    file.touch()
    with pytest.raises(OperationalError):
        sf._working_directory(file)


def test_all_cleanup_steps_attempted_after_close_and_group_errors(monkeypatch):
    """Failure closing one pipe never leaks raw text or skips the other pipe/reap."""
    steps = []

    def failed_group(process):
        steps.append('kill')
        raise OperationalError('fixed group diagnostic')

    def failed_close():
        steps.append('stdout')
        raise OSError(PRIVATE)

    process = SimpleNamespace(
        stdout=SimpleNamespace(close=failed_close),
        stderr=SimpleNamespace(close=lambda: steps.append('stderr')),
        wait=lambda **kwargs: steps.append('reap'),
    )
    monkeypatch.setattr(sf, '_kill_group', failed_group)
    with pytest.raises(OperationalError, match='cleanup') as error:
        sf._cleanup(process)
    assert steps == ['kill', 'stdout', 'stderr', 'reap']
    assert PRIVATE not in str(error.value)
