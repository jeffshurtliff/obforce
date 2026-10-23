# -*- coding: utf-8 -*-
"""
:Module:            dev.probe_planner
:Synopsis:          Probes installed read-only planner contracts using explicit synthetic setup
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     23 Oct 2026
"""

from __future__ import annotations

import hashlib
import os
import sys
import tempfile
from dataclasses import replace
from pathlib import Path

from obforce import constants as const
from obforce.errors import ExitCode
from obforce.graph.dependencies import DependencyGraph
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
)
from obforce.sync.notes import parse_note
from obforce.sync.planner import ActionKind, plan_changes
from obforce.sync.reporting import report_plan
from obforce.sync.state import parse_state, serialize_state


def snapshot(root: Path) -> dict:
    """Keep exact bytes, mtimes and tree independently of access-time side effects."""
    return {
        p.relative_to(root).as_posix(): (p.lstat().st_mtime_ns, p.read_bytes() if p.is_file() else None)
        for p in (root, *root.rglob('*'))
    }


def main() -> None:
    """Run source/parser/state/planner/report checks with runtime network/process denial."""
    for event in ('socket.connect', 'subprocess.Popen'):
        try:
            sys.audit(event)
        except RuntimeError:
            pass
        else:
            raise AssertionError('Runtime guard is missing')
    binding = SourceBinding('fictional', 'local')
    component = Component(
        binding, ComponentKey('fictional', 'ApexClass', None, 'Alpha'), {'status': FieldValue(Availability.VALUE, 'Active')}
    )
    inventory = CollectionCoverage(CoverageStatus.COMPLETE, 'synthetic-local', pagination='exhausted', limit_reached=False)
    audit = CollectionCoverage(CoverageStatus.UNAVAILABLE, 'offline-or-omitted-audit', requested=False)
    relations = CollectionCoverage(CoverageStatus.NOT_COLLECTED, 'synthetic-reported', requested=False)
    coverage = Coverage(binding, Selection(), inventory, audit, relations)
    graph = DependencyGraph(binding, coverage.selection, relations)
    inputs = (component.canonical(), coverage.canonical(), graph)
    with tempfile.TemporaryDirectory(prefix='obforce-planner-synthetic-') as temporary:
        vault = Path(temporary).resolve()
        state_path = vault / '.obforce/state.json'

        def plan(items=(component,), **kwargs):
            return plan_changes(vault, state_path, items, coverage, graph, excluded_roots=(), **kwargs)

        before = snapshot(vault)
        first = plan(initial=True)
        assert not first.blocked and first.outcome == ExitCode.SUCCESS and first.state_changed
        assert first == plan(initial=True)
        action = first.actions[0]
        assert action.kind == ActionKind.CREATE and action.identity == '7637447b-f5e1-54db-830d-d3ff73769182'
        assert hashlib.sha256(action.content).hexdigest() == '51dc2a9778761d3cf227e33d545937825eca887d1b05c20044b3f44ed2742177'
        assert hashlib.sha256(first.state_bytes).hexdigest() == 'ee865d97f24b1bf8a9967599b09c77d4ed0e0591f99bafb0beabef8cb240852e'
        assert parse_state(first.state_bytes) == first.state
        assert 'create: 1; update: 0; no_op: 0; move: 0; missing: 0; conflict: 0' in report_plan(first).text
        assert snapshot(vault) == before
        assert (component.canonical(), coverage.canonical(), graph) == inputs
        # Synthetic baseline setup writes are explicit, outside checkout/cwd, before snapshots.
        for ending in (b'\n', b'\r\n'):
            raw = action.content.replace(b'\n', ending)
            parsed = parse_note(raw)
            saved = replace(
                action.saved,
                note=replace(action.saved.note, generated_region_hash=parsed.region_hash),
                generated_region=parsed.region,
            )
            document = replace(first.state, notes=(saved,))
            state_path.parent.mkdir(exist_ok=True)
            wire = serialize_state(document)
            state_path.write_bytes(wire)
            state_path.write_bytes(wire)
            os.utime(state_path, ns=(1_000_000_000, 1_000_000_000))
            target = vault / action.path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            target.write_bytes(raw)
            os.utime(target, ns=(1_000_000_000, 1_000_000_000))
            (vault / 'Ordinary.md').write_bytes(b'Unowned human prose\n')
            before = snapshot(vault)
            noop = plan(previous_graph=graph)
            assert not noop.blocked and not noop.state_changed and noop.state_bytes == wire
            assert noop.actions[0].kind == ActionKind.NO_OP and noop.actions[0].content == raw
            assert snapshot(vault) == before
            assert any(o.path == target and o.content_hash == hashlib.sha256(raw).hexdigest() for o in noop.preconditions)
            changed = replace(component, attributes={'status': FieldValue(Availability.VALUE, False)})
            updated = plan((changed,), previous_graph=graph)
            assert not updated.blocked and updated.actions[0].kind == ActionKind.UPDATE
            assert parse_note(updated.actions[0].content).properties['sf_status'] is False
            assert snapshot(vault) == before
            moved_path = vault / 'Moved.md'
            target.rename(moved_path)
            moved_path.write_bytes(raw)
            os.utime(moved_path, ns=(1_000_000_000, 1_000_000_000))
            before = snapshot(vault)
            moved = plan(previous_graph=graph)
            assert not moved.blocked and moved.actions[0].kind == ActionKind.MOVE
            assert moved.actions[0].path == 'Moved.md' and moved.state.notes[0].note.path == 'Moved.md'
            assert snapshot(vault) == before
            for edited in (
                raw.replace(b'## Salesforce Metadata', b'## private-sentinel'),
                raw.replace(b'"sf_status": "Active"', b'"sf_status": "private-sentinel"'),
            ):
                moved_path.write_bytes(edited)
                before = snapshot(vault)
                blocked = plan(previous_graph=graph)
                assert blocked.blocked and blocked.outcome == ExitCode.CONFLICT
                assert blocked.state is blocked.state_bytes is blocked.graph is None and not blocked.preconditions
                assert all(a.content is a.saved is None for a in blocked.actions)
                text = report_plan(blocked, details=True).text
                assert 'private-sentinel' not in text and 'Alpha' not in text and str(vault) not in text
                assert snapshot(vault) == before
            moved_path.write_bytes(raw)
            moved_path.rename(target)
        old_limit = const.MAX_PLAN_OUTPUT_BYTES
        const.MAX_PLAN_OUTPUT_BYTES = 1
        try:
            before = snapshot(vault)
            bounded = plan(previous_graph=graph)
            assert bounded.blocked and bounded.outcome == ExitCode.INVALID and bounded.state_bytes is None
            assert snapshot(vault) == before
        finally:
            const.MAX_PLAN_OUTPUT_BYTES = old_limit
    assert (component.canonical(), coverage.canonical(), graph) == inputs


if __name__ == '__main__':
    main()
