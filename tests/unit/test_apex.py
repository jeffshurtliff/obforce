# -*- coding: utf-8 -*-
"""
:Module:            tests.unit.test_apex
:Synopsis:          Exercises safe bounded Apex metadata normalization
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     19 Oct 2026
"""

from __future__ import annotations

import socket
from pathlib import Path

import pytest

from obforce import constants as const
from obforce.errors import ModelError
from obforce.models import Availability, FieldValue
from obforce.parsers.apex import parse_apex_metadata


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    """Make any attempted network access fail during adversarial XML parsing."""

    def deny(*args, **kwargs):
        raise AssertionError('XML network access forbidden')

    monkeypatch.setattr(socket, 'socket', deny)
    monkeypatch.setattr(socket, 'getaddrinfo', deny)


def xml(body: str) -> bytes:
    """Wrap fictional child elements in a metadata root."""
    return f'<ApexClass xmlns="{const.SALESFORCE_METADATA_NAMESPACE}">{body}</ApexClass>'.encode()


def test_facts_and_unavailable_fields():
    """Only supported facts survive; no audit value is invented."""
    result = parse_apex_metadata(xml('<status>Active</status><apiVersion>67.0</apiVersion>'))
    assert result.attributes['api_version'] == FieldValue(Availability.VALUE, '67.0')
    assert result.attributes['status'] == FieldValue(Availability.VALUE, 'Active')
    assert all(
        result.attributes[key].availability == Availability.UNAVAILABLE
        for key in const.COMPONENT_ATTRIBUTES
        - {
            'api_version',
            'status',
        }
    )
    with pytest.raises(TypeError):
        result.attributes['status'] = FieldValue(Availability.NULL)
    empty = parse_apex_metadata(xml(''))
    assert all(value.availability == Availability.UNAVAILABLE for value in empty.attributes.values())
    assert empty.warnings == ('metadata_fields_unavailable',)
    deleted = parse_apex_metadata(xml('<status>Deleted</status>'))
    assert deleted.attributes['status'].value == 'Deleted'


@pytest.mark.parametrize(
    'data',
    [
        b'',
        b'not xml',
        b'<ApexClass>',
        b'<ApexClass/>',
        b'<Other/>',
        xml('<apiVersion>67</apiVersion>'),
        xml('<apiVersion>NaN</apiVersion>'),
        xml('<apiVersion>0.0</apiVersion>'),
        xml('<status>Inactive</status>'),
        xml('<status/>'),
        xml('<status>Active</status><status>Active</status>'),
        xml('<status extra="x">Active</status>'),
        xml('<apiVersion><x/></apiVersion>'),
        xml('mixed'),
        xml('<status>Active</status>mixed'),
        b'<!DOCTYPE ApexClass><ApexClass/>',
        b'<!DOCTYPE ApexClass SYSTEM "file:///fictional/private"><ApexClass/>',
        b'<!DOCTYPE ApexClass [<!ENTITY a "expanded">]><ApexClass>&a;</ApexClass>',
        b'<!DOCTYPE ApexClass [<!ENTITY a SYSTEM "https://invalid.example/test">]><ApexClass>&a;</ApexClass>',
        b'<!DOCTYPE ApexClass [<!ENTITY % a SYSTEM "file:///fictional/private">%a;]><ApexClass/>',
        b'<?xml version="1.0" encoding="unsupported"?><ApexClass/>',
    ],
)
def test_invalid_xml(data):
    """Malformed fields, roots, DTDs, and entities never produce facts."""
    with pytest.raises(ModelError):
        parse_apex_metadata(data)


def test_structure_and_byte_bounds(monkeypatch):
    """Independent limits refuse oversized or excessively structured XML."""
    with pytest.raises(ModelError):
        parse_apex_metadata(b' ' * (const.MAX_APEX_XML_BYTES + 1))
    with pytest.raises(ModelError):
        parse_apex_metadata(xml('<x>' * const.MAX_XML_DEPTH + '</x>' * const.MAX_XML_DEPTH))
    with pytest.raises(ModelError):
        parse_apex_metadata(xml('<x/>' * const.MAX_XML_ELEMENTS))
    monkeypatch.setattr(const, 'MAX_APEX_XML_BYTES', 1)
    with pytest.raises(ModelError):
        parse_apex_metadata(xml(''))


def test_unmodeled_fields_are_inert():
    """Neither audit-looking elements nor code-looking text becomes evidence."""
    result = parse_apex_metadata(
        xml('<created_at>secret</created_at><packageVersions><namespace>fake</namespace></packageVersions>')
    )
    assert result.attributes['created_at'].availability == Availability.UNAVAILABLE
    assert result.warnings == ('metadata_fields_unavailable', 'unsupported_xml_fields')
    assert 'secret' not in repr(result)


def test_fictional_attack_fixture():
    """Public fixture DTD text is refused without expansion."""
    data = (Path(__file__).parents[1] / 'fixtures/salesforce/forbidden-dtd.xml').read_bytes()
    with pytest.raises(ModelError):
        parse_apex_metadata(data)
