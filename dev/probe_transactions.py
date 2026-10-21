# -*- coding: utf-8 -*-
"""
:Module:            dev.probe_transactions
:Synopsis:          Probes independently installed transaction/recovery with synthetic explicit inputs
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     20 Oct 2026
"""

from __future__ import annotations

import sys
import tempfile
from dataclasses import replace
from pathlib import Path

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
from obforce.sync import transactions as module
from obforce.sync.notes import parse_note
from obforce.sync.state import parse_state, serialize_state
from obforce.sync.transactions import TransactionInputs, TransactionStatus, publish_plan, recover_transaction


def make_inputs(vault: Path, *, initial: bool = True) -> TransactionInputs:
    """Build normalized fictional records; caller supplies the existing synthetic vault."""
    binding = SourceBinding('fictional', 'local')
    inventory = CollectionCoverage(CoverageStatus.COMPLETE, 'synthetic-local', pagination='exhausted', limit_reached=False)
    audit = CollectionCoverage(CoverageStatus.UNAVAILABLE, 'omitted', requested=False)
    relations = CollectionCoverage(CoverageStatus.NOT_COLLECTED, 'offline', requested=False)
    coverage = Coverage(binding, Selection(), inventory, audit, relations)
    graph = DependencyGraph(binding, coverage.selection, relations)
    components = tuple(
        Component(
            binding,
            ComponentKey('fictional', 'ApexClass', None, name),
            {'status': FieldValue(Availability.VALUE, 'Active' if initial else 'Inactive')},
        )
        for name in ('Alpha', 'Beta')
    )
    return TransactionInputs(
        vault,
        vault / '.obforce/state.json',
        components,
        coverage,
        graph,
        (),
        initial=initial,
        previous_graph=None if initial else graph,
    )


def snapshot(root: Path) -> dict:
    """Compare complete byte/mtime/tree evidence, excluding read-atime side effects."""
    return {
        p.relative_to(root).as_posix(): (p.stat().st_mtime_ns, p.read_bytes() if p.is_file() else None)
        for p in (root, *root.rglob('*'))
    }


def main() -> None:
    """Exercise installed publication/recovery with active runtime network/process guards."""
    for event in ('socket.connect', 'subprocess.Popen'):
        try:
            sys.audit(event)
        except RuntimeError:
            pass
        else:
            raise AssertionError('Runtime guard is missing')
    with tempfile.TemporaryDirectory(prefix='obforce-transactions-synthetic-') as temporary:
        root = Path(temporary).resolve()
        vault = root / 'vault'
        vault.mkdir()
        source = root / 'source'
        source.mkdir()
        (source / 'Example.cls').write_bytes(b'// Fictional source, never acquired\n')
        obsidian = vault / '.obsidian'
        obsidian.mkdir()
        (obsidian / 'app.json').write_bytes(b'{"fictional":true}\n')
        (vault / 'Ordinary.md').write_bytes(b'Human ordinary note\n')
        request = replace(make_inputs(vault), excluded_roots=(source,))
        inputs_before = (request.components, request.coverage.canonical(), request.graph)
        protected = (snapshot(source), snapshot(obsidian), (vault / 'Ordinary.md').stat().st_mtime_ns)
        first = request.plan()
        before = snapshot(vault)
        assert publish_plan(first, request, preview=True).status == TransactionStatus.PREVIEW
        assert snapshot(vault) == before
        assert publish_plan(replace(first, state_bytes=b'forged'), request).outcome == 3
        assert snapshot(vault) == before
        assert publish_plan(first, request).status == TransactionStatus.COMMITTED
        assert parse_state(request.state_path.read_bytes()) == first.state
        # A moved UUID is already user-moved; this step is explicit fixture setup.
        path = vault / first.actions[0].path
        raw = (path.read_bytes() + b'\nHuman prose retained\n').replace(b'\n', b'\r\n')
        path.write_bytes(raw)
        parsed = parse_note(raw)
        document = parse_state(request.state_path.read_bytes())
        notes = tuple(
            replace(saved, note=replace(saved.note, generated_region_hash=parsed.region_hash), generated_region=parsed.region)
            if saved.note.obforce_id == first.actions[0].identity
            else saved
            for saved in document.notes
        )
        request.state_path.write_bytes(serialize_state(replace(document, notes=notes)))
        moved = vault / 'Moved Alpha.md'
        path.rename(moved)
        next_request = replace(request, initial=False, previous_graph=first.graph)
        moved_plan = next_request.plan()
        assert not moved_plan.blocked
        assert publish_plan(moved_plan, next_request).status == TransactionStatus.COMMITTED
        assert moved.read_bytes().endswith(b'Human prose retained\r\n') and not path.exists()
        stable = next_request.plan()
        before = snapshot(vault)
        assert publish_plan(stable, next_request).status == TransactionStatus.NO_OP
        assert snapshot(vault) == before
        updated = replace(make_inputs(vault, initial=False), excluded_roots=(source,))
        candidate = updated.plan()
        baseline = {vault / a.path: (vault / a.path).read_bytes() for a in candidate.actions}
        baseline[request.state_path] = request.state_path.read_bytes()
        original_checkpoint = module._checkpoint

        def stop(boundary, index=-1):
            if boundary == 'published' and index == 0:
                raise OSError('Synthetic interruption')

        module._checkpoint = stop
        try:
            assert publish_plan(candidate, updated).recovery_required
        finally:
            module._checkpoint = original_checkpoint
        before = snapshot(vault)
        preview = recover_transaction(vault, request.state_path, excluded_roots=(source,))
        assert preview.status == TransactionStatus.PREVIEW
        assert snapshot(vault) == before
        result = recover_transaction(vault, request.state_path, excluded_roots=(source,), preview=False)
        assert result.status == TransactionStatus.ROLLED_BACK, result.text
        assert all(path.read_bytes() == content for path, content in baseline.items())
        assert publish_plan(updated.plan(), updated).status == TransactionStatus.COMMITTED
        before = snapshot(vault)
        assert publish_plan(updated.plan(), updated).status == TransactionStatus.NO_OP
        assert snapshot(vault) == before
        assert (request.components, request.coverage.canonical(), request.graph) == inputs_before
        assert (snapshot(source), snapshot(obsidian), (vault / 'Ordinary.md').stat().st_mtime_ns) == protected


if __name__ == '__main__':

    def deny(event, args):
        if event.startswith('socket.') or event in {'subprocess.Popen', 'os.system', 'os.posix_spawn', 'os.spawn'}:
            raise RuntimeError('Runtime network/process access forbidden')

    sys.addaudithook(deny)
    main()
