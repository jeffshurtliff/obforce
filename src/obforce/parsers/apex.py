# -*- coding: utf-8 -*-
"""
:Module:            obforce.parsers.apex
:Synopsis:          Parses bounded Apex class metadata without source bodies
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     19 Oct 2026
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from defusedxml.common import DefusedXmlException
from defusedxml.ElementTree import ParseError, fromstring

from obforce import constants as const
from obforce.errors import ModelError
from obforce.models import Availability, FieldValue


@dataclass(frozen=True)
class ApexMetadata:
    """Hold only normalized allowlisted facts and non-sensitive limitation labels."""

    attributes: Mapping[str, FieldValue]
    warnings: tuple[str, ...]


def parse_apex_metadata(data: bytes) -> ApexMetadata:
    """Parse a bounded Salesforce ApexClass XML document with no external access.

    Unknown elements are ignored with a warning, never interpreted as facts or
    relationships. Missing supported fields are unavailable, not observed null.

    :param data: XML bytes only; no filenames, streams, or Apex bodies.
    :returns: Immutable normalized facts and stable warning labels.
    :raises ModelError: For unsafe, oversized, malformed, or invalid metadata.
    """
    if not isinstance(data, bytes) or not data or len(data) > const.MAX_APEX_XML_BYTES:
        raise ModelError('Apex metadata must be nonempty bounded XML bytes')
    try:
        root = fromstring(data, forbid_dtd=True, forbid_entities=True, forbid_external=True)
    except (ParseError, DefusedXmlException, ValueError, LookupError, RecursionError) as error:
        raise ModelError('Unsafe or malformed Apex metadata XML') from error
    prefix = '{' + const.SALESFORCE_METADATA_NAMESPACE + '}'
    if root.tag != prefix + 'ApexClass' or root.attrib or (root.text or '').strip():
        raise ModelError('Expected Salesforce ApexClass metadata root')
    pending = [(root, 1)]
    count = 0
    while pending:
        element, depth = pending.pop()
        count += 1
        if count > const.MAX_XML_ELEMENTS or depth > const.MAX_XML_DEPTH:
            raise ModelError('Apex metadata exceeds XML structure limits')
        pending.extend((child, depth + 1) for child in element)
    attributes = {name: FieldValue(Availability.UNAVAILABLE) for name in const.COMPONENT_ATTRIBUTES}
    warnings: set[str] = set()
    seen: set[str] = set()
    for element in root:
        if (element.tail or '').strip():
            raise ModelError('Unexpected mixed Apex metadata content')
        field = {prefix + 'apiVersion': 'api_version', prefix + 'status': 'status'}.get(element.tag)
        if field is None:
            warnings.add('unsupported_xml_fields')
            continue
        if field in seen or element.attrib or len(element):
            raise ModelError('Duplicate or structured Apex metadata field')
        seen.add(field)
        value = (element.text or '').strip()
        if (field == 'api_version' and not re.fullmatch(r'[1-9][0-9]{0,2}\.0', value)) or (
            field == 'status' and value not in {'Active', 'Deleted'}
        ):
            raise ModelError('Invalid supported Apex metadata value')
        attributes[field] = FieldValue(Availability.VALUE, value)
    if seen != {'api_version', 'status'}:
        warnings.add('metadata_fields_unavailable')
    return ApexMetadata(MappingProxyType(attributes), tuple(sorted(warnings)))
