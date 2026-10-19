# -*- coding: utf-8 -*-
"""
:Module:            tests.unit.test_config
:Synopsis:          Verifies explicit strict configuration and source selection offline
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     19 Oct 2026
"""

import builtins
from pathlib import Path

import pytest

from obforce.config import SourceSelection, load_config, relative_path, select_source
from obforce.errors import ConfigError, OperationalError

CONFIG = """schema_version = 1
workspace_id = "demo-org"
vault = "./vault"
[source]
mode = "local"
project = "./project"
"""


def config_file(tmp_path: Path, text: str = CONFIG) -> Path:
    """Create only a synthetic explicit config fixture."""
    path = tmp_path / 'obforce.toml'
    path.write_text(text, encoding='utf-8')
    return path


def snapshot(root: Path) -> dict[str, tuple[bytes, int]]:
    """Capture fixture content/mtime to detect loading side effects."""
    return {
        str(path.relative_to(root)): (path.read_bytes(), path.stat().st_mtime_ns) for path in root.rglob('*') if path.is_file()
    }


def test_config_relative_paths_defaults_and_no_writes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Resolve config paths independent of cwd without creating any destination."""
    path = config_file(tmp_path, CONFIG + '[templates]\ndirectory = "./templates"\n')
    before = snapshot(tmp_path)
    work = tmp_path / 'unrelated'
    work.mkdir()
    monkeypatch.chdir(work)
    config = load_config(path)
    assert config.source.project == tmp_path / 'project'
    assert config.vault == tmp_path / 'vault'
    assert config.template_directory == tmp_path / 'templates'
    assert config.options.include_namespaced is False
    assert config.options.include_audit_names is True
    assert config.layout.apex_classes == 'Custom Code/Apex Classes'
    assert snapshot(tmp_path) == before
    assert not config.vault.exists()
    assert not config.source.project.exists()


def test_absolute_paths_and_explicit_false(tmp_path: Path) -> None:
    """Retain absolute paths and false options rather than substituting defaults."""
    text = CONFIG.replace('./project', (tmp_path / 'absolute-project').as_posix())
    path = config_file(tmp_path, text + '[options]\ninclude_audit_names = false\ninclude_namespaced = true\n')
    result = load_config(path)
    assert result.source.project == tmp_path / 'absolute-project'
    assert result.options.include_audit_names is False
    assert result.options.include_namespaced is True


@pytest.mark.parametrize(
    ('old', 'new'),
    [
        ('schema_version = 1', 'schema_version = 2'),
        ('schema_version = 1', 'schema_version = true'),
        ('schema_version = 1', 'schema_version = 1.0'),
        ('schema_version = 1', 'schema_version = 1\nunknown = true'),
        ('schema_version = 1', 'schema_version = 1\nschema_version = 1'),
        ('workspace_id = "demo-org"', 'workspace_id = "bad space"'),
        ('workspace_id = "demo-org"', 'workspace_id = ""'),
        ('workspace_id = "demo-org"\n', ''),
        ('vault = "./vault"', 'vault = 1'),
        ('vault = "./vault"', 'vault = ""'),
        ('mode = "local"', 'mode = "mystery"'),
        ('mode = "local"', 'mode = false'),
        ('mode = "local"', 'mode = "local"\norg = "fictional"'),
        ('project = "./project"', 'project = "./project"\ntoken = "fictional"'),
        ('project = "./project"', 'project = "./project"\n[options]\ninclude_audit_names = "false"'),
        ('project = "./project"', 'project = "./project"\n[options]\nextra = true'),
        ('project = "./project"', 'project = "./project"\n[layout]\nextra = "x"'),
        ('project = "./project"', 'project = "./project"\n[templates]\nextra = "x"'),
        ('project = "./project"', 'project = "./project"\n[templates]'),
        ('project = "./project"', 'project = "~/project"'),
        ('project = "./project"', 'project = "$HOME/project"'),
        ('project = "./project"', ''),
        ('[source]\nmode = "local"\nproject = "./project"', 'source = "local"'),
        ('schema_version = 1', 'options = false\nschema_version = 1'),
        ('schema_version = 1', 'layout = []\nschema_version = 1'),
    ],
)
def test_invalid_explicit_config_never_falls_back_or_writes(tmp_path: Path, old: str, new: str) -> None:
    """Refuse unknown keys/types/versions/selectors and preserve fixture bytes/mtimes."""
    path = config_file(tmp_path, CONFIG.replace(old, new))
    before = snapshot(tmp_path)
    with pytest.raises(ConfigError):
        load_config(path)
    assert snapshot(tmp_path) == before
    assert sorted(p.name for p in tmp_path.iterdir()) == ['obforce.toml']


@pytest.mark.parametrize(
    'path',
    [
        '../escape',
        '/absolute',
        'C:/drive',
        'a\\b',
        'a//b',
        '.',
        'A/../B',
        'CON.md',
        'x/NUL',
        'LPT1.txt',
        'bad.',
        'bad ',
        'x:y',
        'x?y',
        '',
    ],
)
def test_invalid_portable_relative_paths(path: str) -> None:
    """Reject unsafe portable layout/state paths before filesystem publication exists."""
    with pytest.raises(ConfigError):
        relative_path(path)


def test_layout_and_path_overlap_refusal(tmp_path: Path) -> None:
    """Reject traversal and source/template/config containment in either direction."""
    for text in (
        CONFIG + '[layout]\napex_classes = "../escape"\n',
        CONFIG.replace('./vault', './project/docs'),
        CONFIG.replace('./project', './vault/project'),
        CONFIG.replace('./vault', '.'),
        CONFIG + '[templates]\ndirectory = "./vault/templates"\n',
    ):
        with pytest.raises(ConfigError):
            load_config(config_file(tmp_path, text))


def test_missing_malformed_oversized_and_permission_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Distinguish invalid config from filesystem operational failures without raw input leaks."""
    with pytest.raises(ConfigError):
        load_config(tmp_path / 'absent.toml')
    for raw in (b'\xff', b'bad syntax and fictional secret', b'x' * 65_537):
        path = tmp_path / 'invalid.toml'
        path.write_bytes(raw)
        with pytest.raises(ConfigError) as failure:
            load_config(path)
        assert 'fictional secret' not in str(failure.value)
    path = config_file(tmp_path)
    with monkeypatch.context() as context:

        def denied(*args: object, **kwargs: object) -> None:
            raise PermissionError('private detail')

        context.setattr(Path, 'open', denied)
        with pytest.raises(OperationalError) as failure:
            load_config(path)
        assert type(failure.value) is OperationalError
        assert 'private detail' not in str(failure.value)


def test_live_selection_override_is_explicit_and_mode_safe(tmp_path: Path) -> None:
    """Allow explicit live alias override without claiming that alias verifies identity."""
    local = load_config(config_file(tmp_path))
    live = load_config(
        config_file(tmp_path, CONFIG.replace('mode = "local"\nproject = "./project"', 'mode = "live"\norg = "fictional-sandbox"'))
    )
    assert select_source(local) == local.source
    assert select_source(live, org='fictional-alias').org == 'fictional-alias'
    assert select_source(project=tmp_path).mode == 'local'
    assert select_source(org='fictional').mode == 'live'
    for arguments in (
        {},
        {'project': tmp_path, 'org': 'fictional'},
        {'config': local, 'org': 'fictional'},
        {'config': live, 'project': tmp_path},
        {'config': local, 'project': tmp_path},
        {'org': ''},
        {'org': '-x'},
    ):
        with pytest.raises(ConfigError):
            select_source(**arguments)
    with pytest.raises(ConfigError):
        SourceSelection('local', Path('relative'))


def test_config_loading_never_invokes_external_tools_or_network(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Forbid acquisition during config loading; only the explicit config is opened."""
    path = config_file(tmp_path)
    real_open = Path.open
    opened = []

    def explicit_only(self: Path, *args: object, **kwargs: object):
        opened.append(self)
        assert self == path
        return real_open(self, *args, **kwargs)

    def forbidden(*args: object, **kwargs: object) -> None:
        pytest.fail('Unexpected source/network/process operation')

    monkeypatch.setattr(Path, 'open', explicit_only)
    monkeypatch.setattr(builtins, 'open', forbidden)
    monkeypatch.setattr('subprocess.run', forbidden)
    monkeypatch.setattr('socket.socket', forbidden)
    load_config(path)
    assert opened == [path]


@pytest.mark.parametrize('value', ['.obsidian/settings.json', '.OBFORCE/state.json', '.git/config', 'x/\u007fy', 'x/\ud800'])
def test_control_names_and_characters_cannot_be_generated_paths(value: str) -> None:
    """Keep application control areas and Unicode controls out of candidate paths."""
    with pytest.raises(ConfigError):
        relative_path(value)


def test_symlinked_source_path_overlap_is_refused(tmp_path: Path) -> None:
    """Resolve existing aliases before overlap checks without reading source files."""
    source = tmp_path / 'project'
    source.mkdir()
    link = tmp_path / 'alias'
    try:
        link.symlink_to(source, target_is_directory=True)
    except OSError:
        pytest.skip('Host does not permit symlinks; no native symlink evidence')
    path = config_file(tmp_path, CONFIG.replace('./vault', './alias/vault'))
    with pytest.raises(ConfigError):
        load_config(path)


def test_excessive_toml_nesting_fails_with_typed_error_and_no_writes(tmp_path: Path) -> None:
    """Convert bounded-size pathological parser recursion to safe config refusal."""
    path = config_file(tmp_path, 'unknown = ' + '[' * 2000 + '0' + ']' * 2000)
    before = snapshot(tmp_path)
    with pytest.raises(ConfigError):
        load_config(path)
    assert snapshot(tmp_path) == before
