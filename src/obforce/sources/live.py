# -*- coding: utf-8 -*-
"""
:Module:            obforce.sources.live
:Synopsis:          Collects bounded explicit-org Apex facts through the accepted CLI boundary
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     19 Oct 2026
"""

from __future__ import annotations

import math
import re
import time
import unicodedata
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from obforce import constants as const
from obforce.errors import ConfigError, ConflictError, CoverageError, ModelError, OperationalError
from obforce.models import (
    Availability,
    CollectionCoverage,
    Component,
    ComponentKey,
    Coverage,
    CoverageStatus,
    FieldValue,
    Selection,
    SourceBinding,
    component_fingerprint,
    require_same_source,
    validate_identities,
)
from obforce.sources import sf_cli

_IDENTITY_QUERY = 'SELECT Id FROM Organization LIMIT 2'
_INVENTORY_FIELDS = 'Id, Name, NamespacePrefix, ApiVersion, Status'
_DATE_FIELDS = {'CreatedDate': 'created_at', 'LastModifiedDate': 'last_modified_at'}
_NAME_FIELDS = {'CreatedBy': 'created_by', 'LastModifiedBy': 'last_modified_by'}


@dataclass(frozen=True)
class PageEvidence:
    """Retain safe request signals, including contradictions, without raw diagnostics or URLs."""

    phase: str
    returned: int
    reported_total: int | None
    done: bool | None
    continuation: bool
    warning: bool
    stderr: bool
    unexpected_fields: bool

    @property
    def problems(self) -> tuple[str, ...]:
        """Translate observations to fixed diagnostic codes without private text."""
        signals = {
            'count_mismatch': self.reported_total != self.returned,
            'done_not_true': self.done is not True,
            'continuation_present': self.continuation,
            'cli_warning_present': self.warning,
            'stderr_present': self.stderr,
            'unexpected_result_fields': self.unexpected_fields,
        }
        return tuple(key for key, present in signals.items() if present)


@dataclass(frozen=True)
class LiveInventory:
    """Hold private normalized facts and independent coverage, with no publication side effects."""

    components: tuple[Component, ...] = field(repr=False)
    coverage: Coverage = field(repr=False)
    evidence: tuple[PageEvidence, ...] = ()

    @property
    def inventory_hash(self) -> str:
        """Use the unchanged canonical component fingerprint."""
        return component_fingerprint(self.components)


class _Session:
    """Bound the entire operation as well as each accepted process invocation."""

    def __init__(
        self,
        executable: Path,
        directory: Path,
        target: str,
        *,
        max_queries: int | None = None,
        timeout: int | None = None,
        stdout: int | None = None,
    ) -> None:
        self.executable, self.directory, self.target = executable, directory, target
        self.max_queries = const.MAX_LIVE_QUERIES if max_queries is None else max_queries
        self.stdout = const.MAX_LIVE_STDOUT_BYTES if stdout is None else stdout
        self.deadline = time.monotonic() + (const.LIVE_TIMEOUT_SECONDS if timeout is None else timeout)
        self.calls = 0
        self.evidence: list[PageEvidence] = []

    def query(self, query: str, phase: str) -> tuple[list[dict[str, Any]], tuple[str, ...]]:
        """Execute only a fixed SELECT through run_sf; never follow returned endpoints."""
        remaining = self.deadline - time.monotonic()
        if remaining <= 0 or self.calls >= self.max_queries:
            raise CoverageError('Live collection budget exhausted before coverage was established.')
        self.calls += 1
        reply = sf_cli.run_sf(
            self.executable,
            sf_cli.Operation.QUERY if phase == 'identity' else sf_cli.Operation.TOOLING_QUERY,
            directory=self.directory,
            target=self.target,
            query=query,
            limits=sf_cli.Limits(timeout=min(remaining, const.SF_TIMEOUT_SECONDS), stdout=self.stdout),
        )
        records = reply.data['records']
        evidence = PageEvidence(
            phase,
            len(records),
            reply.total_size,
            reply.done,
            reply.next_records_url is not None,
            reply.warnings_present,
            reply.stderr_present,
            bool(reply.data.keys() - {'records', 'totalSize', 'done', 'nextRecordsUrl'}),
        )
        self.evidence.append(evidence)
        return records, evidence.problems


def _id(value: object, prefix: str) -> str:
    """Validate 15/18-character Salesforce IDs and normalize to checksum-verified 18 characters."""
    if not isinstance(value, str) or not re.fullmatch(prefix + r'[A-Za-z0-9]{12}(?:[A-Z0-5]{3})?', value):
        raise ModelError('Invalid Salesforce identity field.')
    base = value[:15]
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ012345'
    suffix = ''.join(
        alphabet[sum(1 << offset for offset, char in enumerate(base[start : start + 5]) if 'A' <= char <= 'Z')]
        for start in (0, 5, 10)
    )
    if len(value) == 18 and value[15:] != suffix:
        raise ModelError('Invalid Salesforce identity checksum.')
    return base + suffix


def _text(value: object, limit: int) -> str:
    """Refuse malformed/oversized private text using only a fixed diagnostic."""
    if (
        not isinstance(value, str)
        or not 0 < len(value) <= limit
        or value != value.strip()
        or any(unicodedata.category(char) in {'Cc', 'Cs'} for char in value)
    ):
        raise ModelError('Invalid Salesforce text field.')
    return value


def _date(value: object) -> str:
    """Normalize explicit Salesforce ISO timestamps to UTC without inventing dates."""
    if not isinstance(value, str) or not re.fullmatch(
        r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:?\d{2})', value
    ):
        raise ModelError('Invalid Salesforce audit timestamp.')
    if value[-1] != 'Z':
        offset = value[-6:].lstrip('+-').replace(':', '') if ':' in value[-6:] else value[-5:].lstrip('+-')
        if len(offset) != 4 or int(offset[:2]) > 23 or int(offset[2:]) > 59:
            raise ModelError('Invalid Salesforce audit timestamp offset.')
    try:
        parsed = datetime.fromisoformat(value).astimezone(UTC)
        return parsed.isoformat(timespec='microseconds').replace('+00:00', 'Z')
    except (ValueError, OverflowError):
        raise ModelError('Invalid Salesforce audit timestamp.') from None


def _component(record: dict[str, Any], binding: SourceBinding) -> Component:
    """Validate only the fixed inventory projection before constructing frozen records."""
    fields = {'Id', 'Name', 'NamespacePrefix', 'ApiVersion', 'Status'}
    if record.keys() - fields - {'attributes'} or not fields <= record.keys():
        raise ModelError('Unsupported or missing Apex inventory fields.')
    record_id = _id(record['Id'], '01p')
    name = _text(record['Name'], 255)
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,254}', name):
        raise ModelError('Invalid Apex class name.')
    namespace = record['NamespacePrefix']
    if namespace is not None and (not isinstance(namespace, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9]{0,14}', namespace)):
        raise ModelError('Invalid Apex namespace.')
    version = record['ApiVersion']
    if type(version) not in (int, float, str) or (type(version) is float and not math.isfinite(version)):
        raise ModelError('Invalid Apex API version.')
    version = str(version)
    if re.fullmatch(r'[1-9][0-9]{0,2}(?:\.0)?', version) is None:
        raise ModelError('Invalid Apex API version.')
    version = version.split('.')[0] + '.0'
    if record['Status'] not in ('Active', 'Deleted'):
        raise ModelError('Invalid Apex class status.')
    return Component(
        binding,
        ComponentKey(binding.workspace_id, 'ApexClass', namespace, name),
        {'api_version': FieldValue(Availability.VALUE, version), 'status': FieldValue(Availability.VALUE, record['Status'])},
        record_id,
        (const.LIVE_APEX_METHOD,),
    )


def _audit_value(record: dict[str, Any], key: str, names: bool) -> FieldValue:
    """Distinguish unavailable fields, observed nulls and validated display names/dates."""
    if key not in record:
        return FieldValue(Availability.UNAVAILABLE)
    value = record[key]
    if names and value is not None:
        if not isinstance(value, dict) or value.keys() - {'Name', 'attributes'}:
            raise ModelError('Unsupported audit relationship fields.')
        if 'Name' not in value:
            return FieldValue(Availability.UNAVAILABLE)
        value = value['Name']
    if value is None:
        return FieldValue(Availability.NULL)
    return FieldValue(Availability.VALUE, _text(value, 255) if names else _date(value))


def _audit(session: _Session, components: list[Component], names: bool, warnings: set[str]) -> tuple[list[Component], bool]:
    """Collect optional fields only for selected Apex IDs; never scan or query unrelated Users."""
    if not components:
        return components, True
    fields = _NAME_FIELDS if names else _DATE_FIELDS
    projection = ', '.join(key + '.Name' if names else key for key in fields)
    # These IDs have already passed strict prefix/length/checksum validation.
    ids = {component.record_id for component in components}
    literals = ', '.join(f"'{record_id}'" for record_id in sorted(ids))
    # Fixed projection and checksum-validated alphanumeric IDs; no free-text SOQL values.
    query = f'SELECT Id, {projection} FROM ApexClass WHERE Id IN ({literals})'  # nosec B608
    phase = 'audit_names' if names else 'audit_dates'
    rows: dict[str, dict[str, Any]] = {}
    complete = True
    try:
        records, problems = session.query(query, phase)
        warnings.update(phase + ':' + problem for problem in problems)
        complete = not problems
    except CoverageError:
        records, complete = [], False
        warnings.add(phase + ':budget_exhausted')
    except OperationalError as error:
        # Config/model/conflict errors must keep their existing higher-precedence meaning.
        if type(error) is not OperationalError:
            raise
        records, complete = [], False
        warnings.add(phase + ':query_unavailable')
    for record in records:
        if record.keys() - {'Id', 'attributes', *fields} or 'Id' not in record:
            raise ModelError('Unsupported or missing Apex audit fields.')
        record_id = _id(record['Id'], '01p')
        if record_id not in ids:
            raise ConflictError('Audit response contains an unselected Apex identity.')
        if record_id in rows:
            raise ConflictError('Duplicate Apex audit identity.')
        rows[record_id] = record
    result = []
    for component in components:
        record = rows.get(component.record_id, {})
        values = {normalized: _audit_value(record, key, names) for key, normalized in fields.items()}
        if any(value.availability is Availability.UNAVAILABLE for value in values.values()):
            complete = False
            warnings.add(phase + ':fields_unavailable')
        result.append(
            Component(
                component.binding,
                component.key,
                {**component.attributes, **values},
                component.record_id,
                tuple(sorted({*component.provenance, const.LIVE_AUDIT_METHOD})),
            )
        )
    return result, complete


def collect_live(
    executable: Path,
    *,
    directory: Path,
    target: str,
    workspace_id: str,
    selection: Selection | None = None,
    include_audit_names: bool = True,
    configured_binding: SourceBinding | None = None,
    state_binding: SourceBinding | None = None,
) -> LiveInventory:
    """Collect selected live Apex facts without writes or implicit source rebinding.

    This internal entry point grants no live authorization. Callers must separately
    obtain authorization for the target and read queries. Tests mock the accepted
    process boundary; Windows execution remains refused by that boundary.

    :param executable: Explicit absolute trusted CLI installation, never discovered.
    :param directory: Explicit existing neutral working directory passed to run_sf.
    :param target: Explicit org selector, never used as stable identity.
    :param workspace_id: Configured logical workspace identity.
    :param selection: Existing namespace/name selection; defaults exclude namespaces.
    :param include_audit_names: Query scoped display names only when true.
    :param configured_binding: Previously verified configured identity, when present.
    :param state_binding: Existing validated state identity, when present.
    :returns: Private normalized records, independent coverage and safe page evidence.
    :raises ConflictError: For source mismatch or duplicate/ambiguous identities.
    :raises ModelError: For invalid observed field values; no raw values are echoed.
    :raises OperationalError: For required query/process/envelope failures.
    :raises CoverageError: If org identity exhaustion cannot be established.
    """
    selection = Selection() if selection is None else selection
    if not isinstance(selection, Selection) or type(include_audit_names) is not bool:
        raise ConfigError('Invalid live collection selection or privacy option.')
    SourceBinding(workspace_id, 'local')  # Validate logical identity before any process call.
    for expected in (configured_binding, state_binding):
        if expected is not None:
            if not isinstance(expected, SourceBinding):
                raise ConfigError('Expected a validated source binding.')
            if expected.mode != 'live' or expected.workspace_id != workspace_id:
                raise ConflictError('Live source does not match the configured/state binding.')
    session = _Session(executable, directory, target)
    identity, problems = session.query(_IDENTITY_QUERY, 'identity')
    if problems or len(identity) != 1:
        raise CoverageError('Actual org identity could not be established from complete query evidence.')
    if identity[0].keys() - {'Id', 'attributes'}:
        raise ModelError('Unsupported org identity fields.')
    binding = SourceBinding(workspace_id, 'live', _id(identity[0].get('Id'), '00D'))
    for expected in (configured_binding, state_binding):
        if expected is not None:
            require_same_source(expected, binding)
    components: list[Component] = []
    observed: list[Component] = []
    inventory_warnings: set[str] = set()
    audit_warnings: set[str] = set()
    exhausted, limited, audit_complete = False, False, True
    cursor: str | None = None
    for _ in range(const.MAX_LIVE_PAGES):
        predicates = [] if selection.include_namespaced else ['NamespacePrefix = null']
        if cursor is not None:
            predicates.append(f"Id > '{cursor}'")
        where = ' WHERE ' + ' AND '.join(predicates) if predicates else ''
        # Fixed fields/predicates/limit; cursor comes only from validated Salesforce IDs.
        query = f'SELECT {_INVENTORY_FIELDS} FROM ApexClass{where} ORDER BY Id LIMIT {const.LIVE_PAGE_SIZE}'  # nosec B608
        try:
            records, problems = session.query(query, 'inventory')
        except CoverageError:
            limited = True
            inventory_warnings.add('collection_budget_exhausted')
            break
        inventory_warnings.update(problems)
        if len(records) > const.LIVE_PAGE_SIZE:
            raise ModelError('Apex page exceeds the selected query limit.')
        page = [_component(record, binding) for record in records]
        observed.extend(page)
        validate_identities(observed)
        if len(observed) > const.MAX_LIVE_RECORDS:
            # No over-limit records become accepted inventory.
            limited = True
            inventory_warnings.add('record_budget_exhausted')
            break
        if any(component.key.namespace is not None for component in page) and not selection.include_namespaced:
            inventory_warnings.add('namespace_scope_contradiction')
            problems = (*problems, 'namespace_scope_contradiction')
        selected = [
            component
            for component in page
            if (selection.include_namespaced or component.key.namespace is None)
            and (not selection.full_names or component.key.full_name in selection.full_names)
        ]
        selected, dates_complete = _audit(session, selected, False, audit_warnings)
        names_complete = True
        if include_audit_names:
            selected, names_complete = _audit(session, selected, True, audit_warnings)
        audit_complete = audit_complete and dates_complete and names_complete
        components.extend(selected)
        if problems:
            break
        if not records:
            exhausted = True
            break
        # Server Id ordering determines the anchor; never guess Salesforce ID collation in Python.
        cursor = page[-1].record_id
    else:
        limited = True
        inventory_warnings.add('page_budget_exhausted')
    complete = exhausted and not inventory_warnings
    inventory = CollectionCoverage(
        CoverageStatus.COMPLETE if complete else CoverageStatus.PARTIAL,
        const.LIVE_APEX_METHOD,
        pagination='exhausted' if complete else 'incomplete',
        limit_reached=True if limited else (False if complete else None),
        warnings=tuple(sorted(inventory_warnings)),
    )
    available_audit = any(
        value.availability is not Availability.UNAVAILABLE
        for component in components
        for key, value in component.attributes.items()
        if key in {'created_at', 'last_modified_at', 'created_by', 'last_modified_by'}
    )
    audit_status = (
        CoverageStatus.COMPLETE
        if complete and audit_complete
        else CoverageStatus.PARTIAL
        if available_audit
        else CoverageStatus.UNAVAILABLE
    )
    if not complete:
        audit_warnings.add('inventory_not_exhausted')
    audit = CollectionCoverage(
        audit_status,
        const.LIVE_AUDIT_METHOD,
        pagination='exhausted' if complete and audit_complete else 'incomplete',
        limit_reached=False if complete and audit_complete else None,
        warnings=tuple(sorted(audit_warnings)),
    )
    relationships = CollectionCoverage(CoverageStatus.NOT_COLLECTED, 'not-collected', requested=False)
    coverage = Coverage(binding, selection, inventory, audit, relationships)
    return LiveInventory(tuple(sorted(components, key=lambda component: component.key.token)), coverage, tuple(session.evidence))
