# -*- coding: utf-8 -*-
"""
:Module:            tests.unit.test_templates
:Synopsis:          Exercises installed template loading and finite sandbox refusal
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     20 Oct 2026
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from jinja2 import UndefinedError

from obforce import constants as const
from obforce.errors import ConfigError, OperationalError
from obforce.renderer import templates
from obforce.renderer.templates import TemplateAsset, load_template

CREATED = 'apex_created.md.j2'
GENERATED = 'apex_generated.md.j2'


def test_packaged_and_override_precedence(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    default = load_template(GENERATED)
    assert load_template(GENERATED, tmp_path).text == default.text
    override = default.text + '\nExplicit local presentation.\n'
    (tmp_path / GENERATED).write_text(override, encoding='utf-8', newline='\n')
    assert load_template(GENERATED, tmp_path).text == override
    assert load_template(CREATED, tmp_path).text == load_template(CREATED).text
    assert load_template(CREATED, tmp_path / 'absent').text == load_template(CREATED).text
    assert sorted(p.name for p in tmp_path.iterdir()) == [GENERATED]


@pytest.mark.parametrize('name', ['../x', '/x', 'unknown.j2', 'a/apex_created.md.j2', '..\\x'])
def test_unknown_names_refused(name):
    with pytest.raises(ConfigError, match='Unknown'):
        load_template(name)


@pytest.mark.parametrize(
    'content', [b'\xff', b'{{ undefined }}', b'\x00', b'\r', b'---\nsf_type: fake', b'<!-- obforce:generated:end -->']
)
def test_invalid_existing_override_never_falls_back(tmp_path, content):
    (tmp_path / CREATED).write_bytes(content)
    with pytest.raises(ConfigError):
        load_template(CREATED, tmp_path)


@pytest.mark.parametrize(
    'expression',
    [
        '{{ metadata }}',
        '{{ metadata | safe }}',
        '{{ missing | section }}',
        '{{ metadata | section | section }}',
        '{{ metadata.__class__ | section }}',
        '{{ metadata[0] | section }}',
        '{{ range(100) | section }}',
        '{{ "x" * 999999999 | section }}',
        '{{ 2 ** 99999999 | section }}',
        '{{ metadata | section(1) }}',
        '{% include "apex_created.md.j2" %}',
        '{% import "x" as x %}',
        '{% extends "x" %}',
        '{% for x in metadata %}{{ x }}{% endfor %}',
        '{% if metadata %}x{% endif %}',
        '{% macro x() %}x{% endmacro %}',
        '{% set x=1 %}',
        '{{ cycler.__init__.__globals__ | section }}',
    ],
)
def test_finite_syntax_refuses_capabilities(expression):
    with pytest.raises(ConfigError):
        TemplateAsset(GENERATED, expression + load_template(GENERATED).text)


def test_required_slots_once():
    text = load_template(GENERATED).text
    for invalid in (text.replace('{{ metadata | section }}', ''), text + '{{ metadata | section }}'):
        with pytest.raises(ConfigError, match='required section'):
            TemplateAsset(GENERATED, invalid)


def test_strict_undefined_and_no_default_capabilities():
    environment = templates._environment()
    assert environment.loader is None and not environment.globals and not environment.tests
    assert set(environment.filters) == {'section'}
    with pytest.raises(UndefinedError):
        environment.from_string('{{ missing }}').render()
    assert environment.is_safe_attribute('', 'upper', str.upper) is False
    assert environment.is_safe_callable(str) is False


def test_context_and_output_bounds(monkeypatch):
    asset = load_template(GENERATED)
    context = {name: name for name in const.TEMPLATE_SLOTS[GENERATED]}
    assert asset.render(context) == asset.render(dict(reversed(list(context.items()))))
    for invalid in (
        {},
        {**context, 'org_id': 'private'},
        {**context, 'metadata': Path('/private')},
        {**context, 'metadata': object()},
    ):
        with pytest.raises(ConfigError):
            asset.render(invalid)
    monkeypatch.setattr(const, 'MAX_RENDER_SECTION_BYTES', 10)
    with pytest.raises(ConfigError, match='context'):
        asset.render(context)
    asset = TemplateAsset(CREATED, 'x' * 11)
    with pytest.raises(ConfigError, match='section'):
        asset.render({})


def test_template_byte_and_ast_limits(tmp_path, monkeypatch):
    (tmp_path / CREATED).write_bytes(b'x' * (const.MAX_TEMPLATE_BYTES + 1))
    with pytest.raises(ConfigError, match='byte bound'):
        load_template(CREATED, tmp_path)
    with pytest.raises(ConfigError, match='byte bound'):
        TemplateAsset(CREATED, 'x' * (const.MAX_TEMPLATE_BYTES + 1))
    monkeypatch.setattr(const, 'MAX_TEMPLATE_NODES', 1)
    with pytest.raises(ConfigError, match='syntax bound'):
        load_template(GENERATED)


def test_template_roots_and_special_files(tmp_path):
    with pytest.raises(ConfigError, match='absolute'):
        load_template(CREATED, Path('relative'))
    root_file = tmp_path / 'root-file'
    root_file.touch()
    with pytest.raises(ConfigError):
        load_template(CREATED, root_file)
    (tmp_path / CREATED).mkdir()
    with pytest.raises(ConfigError):
        load_template(CREATED, tmp_path)


@pytest.mark.skipif(os.name == 'nt', reason='POSIX unsafe-link fixture; Windows reparse refusal tested with stat evidence')
def test_links_and_hardlinks_are_refused(tmp_path):
    target = tmp_path / 'target'
    target.write_text('text')
    link = tmp_path / CREATED
    link.symlink_to(target)
    with pytest.raises(ConfigError, match='Unsafe'):
        load_template(CREATED, tmp_path)
    link.unlink()
    os.link(target, link)
    with pytest.raises(ConfigError, match='Unsafe'):
        load_template(CREATED, tmp_path)
    root_link = tmp_path / 'root-link'
    root_link.symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(ConfigError, match='Unsafe'):
        load_template(GENERATED, root_link)


def test_reparse_evidence_refused():
    import stat
    from types import SimpleNamespace

    with pytest.raises(ConfigError, match='Unsafe'):
        templates._check_stat(
            SimpleNamespace(st_mode=stat.S_IFREG, st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT), directory=False
        )


def test_read_errors_do_not_fall_back(tmp_path, monkeypatch):
    (tmp_path / CREATED).write_text('text')

    def fail(*args, **kwargs):
        raise PermissionError('sensitive path')

    monkeypatch.setattr(templates.os, 'open', fail)
    with pytest.raises(OperationalError, match='Cannot read explicit') as error:
        load_template(CREATED, tmp_path)
    assert 'sensitive' not in str(error.value)


def test_changed_file_refused(tmp_path, monkeypatch):
    (tmp_path / CREATED).write_text('text')
    original = templates._identity
    calls = 0

    def changed(info):
        nonlocal calls
        calls += 1
        result = original(info)
        return (*result[:-1], result[-1] + calls)

    monkeypatch.setattr(templates, '_identity', changed)
    with pytest.raises(ConfigError, match='changed'):
        load_template(CREATED, tmp_path)
