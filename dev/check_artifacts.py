# -*- coding: utf-8 -*-
"""
:Module:            dev.check_artifacts
:Synopsis:          Inspects fresh distributions and checks independent installations
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     19 Oct 2026
"""

import argparse
import configparser
import hashlib
import json
import os
import subprocess
import tarfile
import tempfile
import tomllib
import venv
import zipfile
from email.parser import BytesParser
from pathlib import Path


def _run(command: list[str], cwd: Path, environment: dict[str, str]) -> str:
    """Run a bounded validation command and include captured output on failure.

    :param command: Executable and arguments without shell interpolation.
    :param cwd: Temporary working directory.
    :param environment: Explicit child environment.
    :returns: Standard output from a successful command.
    :raises RuntimeError: If the child exits unsuccessfully.
    :raises subprocess.TimeoutExpired: If the command exceeds its time limit.
    """
    result = subprocess.run(command, cwd=cwd, env=environment, capture_output=True, text=True, timeout=180, check=False)
    if result.returncode:
        raise RuntimeError(f'Command failed ({result.returncode}): {command}\n{result.stdout}\n{result.stderr}')
    return result.stdout


def _inspect(artifact: Path, version: str, license_bytes: bytes) -> None:
    """Enforce the explicit foundation and internal-contract artifact allowlist.

    :param artifact: Locally built wheel or sdist to inspect without extraction.
    :param version: Expected static project version.
    :param license_bytes: Unmodified root license for exact comparison.
    :raises ValueError: If archive contents or metadata violate the allowlist.
    """
    package_files = {'__init__.py', '__main__.py', 'cli.py', 'config.py', 'constants.py', 'errors.py', 'models.py'}
    if artifact.suffix == '.whl':
        metadata_root = f'obforce-{version}.dist-info/'
        expected = {f'obforce/{name}' for name in package_files} | {
            f'{metadata_root}{name}' for name in ('METADATA', 'WHEEL', 'entry_points.txt', 'RECORD', 'licenses/LICENSE')
        }
        with zipfile.ZipFile(artifact) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)) or set(names) != expected:
                raise ValueError(f'Unexpected wheel members: {names}')
            content = {name: archive.read(name) for name in names}
        metadata = BytesParser().parsebytes(content[f'{metadata_root}METADATA'])
        actual_license = content[f'{metadata_root}licenses/LICENSE']
        entry_points = configparser.ConfigParser()
        entry_points.read_string(content[f'{metadata_root}entry_points.txt'].decode())
        if entry_points.get('console_scripts', 'obforce') != 'obforce.cli:main':
            raise ValueError('Missing console entry point')
    else:
        root = f'obforce-{version}/'
        expected = {f'{root}src/obforce/{name}' for name in package_files} | {
            f'{root}{name}' for name in ('LICENSE', 'README.md', 'pyproject.toml', 'PKG-INFO')
        }
        with tarfile.open(artifact, 'r:gz') as archive:
            members = archive.getmembers()
            names = [member.name for member in members]
            if len(names) != len(set(names)) or set(names) != expected or not all(member.isfile() for member in members):
                raise ValueError(f'Unexpected sdist members: {names}')
            content = {}
            for member in members:
                stream = archive.extractfile(member)
                if stream is None:
                    raise ValueError(f'Unreadable archive member: {member.name}')
                content[member.name] = stream.read()
        metadata = BytesParser().parsebytes(content[f'{root}PKG-INFO'])
        actual_license = content[f'{root}LICENSE']
    if (metadata['Name'], metadata['Version'], metadata['Requires-Python'], metadata['License-Expression']) != (
        'obforce',
        version,
        '>=3.12',
        'Apache-2.0',
    ):
        raise ValueError('Unexpected distribution metadata')
    if actual_license != license_bytes:
        raise ValueError('Distribution license differs from root LICENSE')
    print(json.dumps({'artifact': artifact.name, 'sha256': hashlib.sha256(artifact.read_bytes()).hexdigest(), 'files': names}))


def _check_install(artifact: Path, version: str) -> None:
    """Install an artifact into its own external environment and exercise discovery.

    Installation may download runtime and isolated build dependencies. Application
    smoke tests block Python socket operations and have no external tools on PATH.

    :param artifact: Inspected distribution to install independently.
    :param version: Expected installed version.
    :raises ValueError: If discovery, isolation, or no-write checks fail.
    :raises RuntimeError: If an installation or smoke command fails.
    """
    with tempfile.TemporaryDirectory(prefix='obforce-install-') as temporary:
        root = Path(temporary).resolve()
        environment_path = root / 'venv'
        venv.EnvBuilder(with_pip=True).create(environment_path)
        scripts = environment_path / ('Scripts' if os.name == 'nt' else 'bin')
        python = scripts / ('python.exe' if os.name == 'nt' else 'python')
        console = scripts / ('obforce.exe' if os.name == 'nt' else 'obforce')
        environment = dict(os.environ)
        for key in ('PYTHONPATH', 'PYTHONHOME'):
            environment.pop(key, None)
        environment.update(PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1', PIP_DISABLE_PIP_VERSION_CHECK='1')
        _run([str(python), '-m', 'pip', '--isolated', 'install', '--no-cache-dir', str(artifact)], root, environment)
        _run([str(python), '-m', 'pip', '--isolated', 'check'], root, environment)
        probe = (
            'import sys; from pathlib import Path; import obforce; '
            'from importlib.metadata import version; from importlib.resources import files; '
            f'assert version("obforce") == {version!r}; '
            'assert Path(obforce.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()); '
            'assert files("obforce").joinpath("cli.py").is_file(); '
            'from obforce.models import Component, ComponentKey, SourceBinding; '
            'assert len(Component(SourceBinding("demo", "local"), '
            'ComponentKey("demo", "ApexClass", None, "Example")).source_hash) == 64'
        )
        _run([str(python), '-I', '-c', probe], root, environment)
        work = root / 'work'
        work.mkdir()
        guard = root / 'guard'
        guard.mkdir()
        (guard / 'sitecustomize.py').write_text(
            'import sys\n'
            'def deny_network(event, args):\n'
            '    if event.startswith("socket."):\n'
            '        raise RuntimeError("Network forbidden during artifact smoke tests")\n'
            'sys.addaudithook(deny_network)\n',
            encoding='utf-8',
        )
        environment.update(PATH='', PYTHONPATH=str(guard))
        for command in ([str(console)], [str(python), '-m', 'obforce']):
            for arguments in ([], ['--help'], ['--version']):
                output = _run(command + arguments, work, environment)
                expected = f'obforce, version {version}\n' if arguments == ['--version'] else '--help'
                if expected not in output:
                    raise ValueError(f'Unexpected entry-point output: {output}')
            for feature in ('init', 'build', 'sync', 'recover'):
                result = subprocess.run(
                    command + [feature], cwd=work, env=environment, capture_output=True, text=True, timeout=20, check=False
                )
                if result.returncode != 2:
                    raise ValueError(f'Unexpected feature command: {feature}')
        if list(work.iterdir()):
            raise ValueError('Discovery created working-directory artifacts')
        print(f'{artifact.name}: install, imports/resources, pip check, both entry points, offline/no-write checks passed')


def main() -> None:
    """Validate exactly one fresh wheel and sdist without publishing them."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('artifact_directory', type=Path)
    arguments = parser.parse_args()
    repository = Path(__file__).resolve().parents[1]
    with (repository / 'pyproject.toml').open('rb') as stream:
        version = tomllib.load(stream)['project']['version']
    directory = arguments.artifact_directory.resolve()
    expected = {f'obforce-{version}-py3-none-any.whl', f'obforce-{version}.tar.gz'}
    if {path.name for path in directory.iterdir()} != expected:
        parser.error('Use a fresh directory containing exactly the current wheel and sdist')
    for artifact in sorted(directory.iterdir()):
        _inspect(artifact, version, (repository / 'LICENSE').read_bytes())
        _check_install(artifact, version)


if __name__ == '__main__':
    main()
