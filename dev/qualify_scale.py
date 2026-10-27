# -*- coding: utf-8 -*-
"""
:Module:            dev.qualify_scale
:Synopsis:          Measures bounded synthetic acquisition, graph, rendering and planning separately
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     27 Oct 2026
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import sys
import tempfile
import time
import tracemalloc
from collections import Counter
from dataclasses import replace
from importlib.metadata import version
from pathlib import Path
from unittest.mock import patch
from uuid import NAMESPACE_URL, uuid5

from obforce import constants as const
from obforce.config import Options
from obforce.graph.dependencies import DependencyGraph, Edge, Evidence, component_index, resolve_endpoint
from obforce.models import CollectionCoverage, CoverageStatus, Selection, SourceBinding
from obforce.renderer.notes import note_paths, render_new_note
from obforce.renderer.templates import load_template
from obforce.sources import live, relationships, sf_cli
from obforce.sources.local import collect_local
from obforce.sync import planner
from obforce.sync.planner import plan_changes
from obforce.sync.transactions import _contents

XML = (
    '<ApexClass xmlns="http://soap.sforce.com/2006/04/metadata">'
    '<apiVersion>67.0</apiVersion><status>Active</status></ApexClass>\n'
)
ORG = '00D000000000001EAA'


def project(root: Path, count: int) -> Path:
    """Create explicit fictional Apex pairs; setup is excluded from collection timing."""
    source = root / 'Synthetic Project'
    classes = source / 'package/classes'
    classes.mkdir(parents=True)
    (source / 'sfdx-project.json').write_text('{"packageDirectories":[{"path":"package"}]}', encoding='utf-8')
    for index in range(count):
        (classes / f'Class{index:04d}.cls').write_text('// Synthetic body; never read\n', encoding='utf-8')
        (classes / f'Class{index:04d}.cls-meta.xml').write_text(XML, encoding='utf-8', newline='\n')
    return source


def mocked_inventory(count: int, root: Path):
    """Exercise actual identity, pagination and batched audit normalization without a process.

    The synthetic Organization reply independently establishes the binding inside
    collect_live; a caller-created SourceBinding is never substituted for that query.
    """
    rows = [
        {
            'Id': f'01p{index + 1:012d}',
            'Name': f'Class{index:04d}',
            'NamespacePrefix': None,
            'ApiVersion': '67.0',
            'Status': 'Active',
        }
        for index in range(count)
    ]
    calls = Counter()
    cursor, selected = 0, []

    def collect(argv, cwd, limits):
        nonlocal cursor, selected
        query = argv[7]
        if query == 'SELECT Id FROM Organization LIMIT 2':
            phase, records = 'identity', [{'Id': ORG}]
        elif 'ORDER BY Id LIMIT 200' in query:
            phase, selected = 'inventory', rows[cursor : cursor + const.LIVE_PAGE_SIZE]
            cursor += len(selected)
            records = selected
        elif 'CreatedDate, LastModifiedDate' in query:
            phase = 'audit_dates'
            records = [{'Id': row['Id'], 'CreatedDate': None, 'LastModifiedDate': None} for row in selected]
        else:
            raise AssertionError('Unexpected synthetic query')
        calls[phase] += 1
        raw = json.dumps({'status': 0, 'result': {'records': records, 'totalSize': len(records), 'done': True}}).encode()
        assert len(raw) <= limits.stdout and cwd == root
        return 0, raw, False

    with patch.object(sf_cli, 'resolve_executable', lambda path: path), patch.object(sf_cli, '_collect', collect):
        result = live.collect_live(
            root / 'fictional-sf', directory=root, target='synthetic', workspace_id='scale', include_audit_names=False
        )
    pages = (count + const.LIVE_PAGE_SIZE - 1) // const.LIVE_PAGE_SIZE
    assert calls == Counter(identity=1, inventory=pages + 1, audit_dates=pages)
    assert result.coverage.binding.org_id == ORG and result.coverage.inventory.status == 'complete'
    assert len(result.components) == count
    return result, dict(calls)


def synthetic_graph(inventory, count: int, seed: int):
    """Build explicit seeded directed edges, independently of the bounded platform collector.

    A shuffled ring plus successive offsets gives distinct pairs, cycles and
    uniform degree without guessing dependencies from source text. No self edge.
    """
    components = inventory.components
    size = len(components)
    if not 0 <= count <= min(const.MAX_GRAPH_EDGES, size * (size - 1)):
        raise ValueError('Synthetic edge count outside finite fixture bounds')
    order = list(range(size))
    random.Random(seed).shuffle(order)
    index = component_index(components, inventory.coverage.binding, inventory.coverage.selection)
    endpoints = [resolve_endpoint('ApexClass', c.key.namespace, c.key.full_name, c.record_id, index) for c in components]
    coverage = CollectionCoverage(CoverageStatus.PARTIAL, 'synthetic-explicit-v1', warnings=('synthetic_fixture',))
    evidence = Evidence('synthetic-explicit-v1', coverage)
    edges = tuple(
        Edge(endpoints[order[number % size]], endpoints[order[(number % size + 1 + number // size) % size]], (evidence,))
        for number in range(count)
    )
    graph = DependencyGraph(inventory.coverage.binding, inventory.coverage.selection, coverage, edges)
    assert len(graph.edges) == count
    return graph, replace(inventory.coverage, relationships=coverage)


def render_all(inventory, coverage, graph):
    """Render every candidate without retaining a second complete output collection."""
    paths = note_paths(inventory.components)
    generated, creation = load_template('apex_generated.md.j2'), load_template('apex_created.md.j2')
    digest, total = hashlib.sha256(), 0
    for component in inventory.components:
        candidate = render_new_note(
            component,
            coverage,
            graph,
            identity=str(uuid5(NAMESPACE_URL, component.key.full_name)),
            managed_paths=paths,
            options=Options(include_audit_names=False),
            generated_template=generated,
            creation_template=creation,
        )
        raw = candidate.text.encode('utf-8')
        digest.update(raw)
        total += len(raw)
    return {'notes': len(paths), 'bytes': total, 'sha256': digest.hexdigest()}


def mocked_relationship_budget(inventory, root: Path):
    """Count actual fixed collector calls; never represent them as 10,000 collected edges."""
    calls = 0

    def collect(argv, cwd, limits):
        nonlocal calls
        calls += 1
        records = [{'Id': ORG}] if argv[7] == 'SELECT Id FROM Organization LIMIT 2' else []
        return (
            0,
            json.dumps({'status': 0, 'result': {'records': records, 'totalSize': len(records), 'done': True}}).encode(),
            False,
        )

    with patch.object(sf_cli, 'resolve_executable', lambda path: path), patch.object(sf_cli, '_collect', collect):
        result = relationships.collect_relationships(
            root / 'fictional-sf', directory=root, target='synthetic', inventory=inventory
        )
    assert calls == min(1 + 2 * len(inventory.components), const.MAX_RELATIONSHIP_QUERIES)
    assert result.coverage.relationships.status == 'partial' and not result.graph.edges
    return {'calls': calls, 'edges': 0, 'coverage': 'partial', 'warnings': list(result.coverage.relationships.warnings)}


def measure(name, operation):
    """Report elapsed seconds and traced Python allocation peak, including retained inputs.

    The incremental peak is peak minus current allocations at stage entry. Neither
    measure is total RSS; tracemalloc itself changes runtime and memory behavior.
    """
    before = tracemalloc.get_traced_memory()[0]
    tracemalloc.reset_peak()
    start = time.perf_counter()
    result = operation()
    elapsed = time.perf_counter() - start
    current, peak = tracemalloc.get_traced_memory()
    print(
        json.dumps(
            {
                'stage': name,
                'seconds': elapsed,
                'python_traced_current_bytes': current,
                'python_traced_peak_bytes': peak,
                'python_traced_incremental_peak_bytes': peak - before,
            }
        ),
        flush=True,
    )
    return result


def planning(inventory, coverage, graph, vault: Path, source: Path):
    """Retain fixed typed refusal diagnostics without bypassing any planner check."""
    failures = []
    original = planner._blocked

    def diagnostic(error, current_coverage):
        failures.append({'type': type(error).__name__, 'reason': str(error)})
        return original(error, current_coverage)

    with patch.object(planner, '_blocked', diagnostic):
        plan = plan_changes(
            vault,
            vault / '.obforce/state.json',
            inventory.components,
            coverage,
            graph,
            excluded_roots=(source, Path(live.__file__).resolve().parents[2]),
            verified_org_id=ORG,
            initial=True,
            allow_absent=True,
            persist_evidence=True,
            include_dashboard=True,
            options=Options(include_audit_names=False),
        )
    print(json.dumps({'planner_fixed_diagnostics': failures}), flush=True)
    return plan


def main() -> None:
    """Run one developer-only benchmark; no public Obforce API or command is added."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--classes', type=int, default=1000)
    parser.add_argument('--edges', type=int, default=10000)
    parser.add_argument('--seed', type=int, default=15)
    args = parser.parse_args()
    if not 2 <= args.classes <= 1000 or not 0 <= args.edges <= min(10000, args.classes * (args.classes - 1)):
        parser.error('Fixture requires 2–1000 classes and 0–10000 distinct directed edges')

    def deny(event, values):
        if event.startswith('socket.') or event in {'subprocess.Popen', 'os.system', 'os.posix_spawn'}:
            raise RuntimeError('Benchmark runtime network/process access forbidden')

    sys.addaudithook(deny)
    print(
        json.dumps(
            {
                'environment': {
                    'python': sys.version,
                    'system': platform.system(),
                    'release': platform.release(),
                    'os_version': platform.version(),
                    'machine': platform.machine(),
                    'dependencies': {name: version(name) for name in ('obforce', 'click', 'jinja2', 'ruamel.yaml', 'defusedxml')},
                },
                'fixture': vars(args),
                'topology': 'seeded permutation ring; successive forward offsets; no self edges',
                'memory_metric': 'tracemalloc Python allocations; not total RSS',
                'runtime_guard': 'socket/process audit denial',
            }
        ),
        flush=True,
    )
    with tempfile.TemporaryDirectory(prefix='obforce-scale-') as temporary:
        root = Path(temporary).resolve()
        source = project(root, args.classes)
        tracemalloc.start()
        local = measure(
            'offline_collection_normalization', lambda: collect_local(source, SourceBinding('scale', 'local'), Selection())
        )
        assert len(local.components) == args.classes
        inventory, calls = measure('mocked_live_collection_normalization', lambda: mocked_inventory(args.classes, root))
        print(json.dumps({'mocked_acquisition_calls': calls}), flush=True)
        graph, coverage = measure('explicit_synthetic_graph', lambda: synthetic_graph(inventory, args.edges, args.seed))
        rendered = measure('rendering_all_candidates', lambda: render_all(inventory, coverage, graph))
        print(json.dumps({'rendered': rendered}), flush=True)
        vault = root / 'Never Created Vault'
        plan = measure(
            'persistent_planning_attempt',
            lambda: planning(inventory, coverage, graph, vault, source),
        )
        print(
            json.dumps(
                {
                    'planning': {
                        'blocked': plan.blocked,
                        'outcome': int(plan.outcome),
                        'diagnostic': plan.diagnostic.value,
                        'actions': len(plan.actions),
                        'state_bytes': len(plan.state_bytes or b''),
                    },
                    'vault_absent': not vault.exists(),
                }
            ),
            flush=True,
        )
        assert not vault.exists()
        small, _ = mocked_inventory(32, root)
        small_graph, small_coverage = synthetic_graph(small, 320, args.seed)
        small_vault = root / 'Separate Small Vault'
        small_plan = measure(
            'persistent_planning_32_classes_320_edges', lambda: planning(small, small_coverage, small_graph, small_vault, source)
        )
        assert not small_plan.blocked and len(small_plan.actions) == 32
        entries, _ = _contents(small_vault, small_plan)
        assert len(entries) == 34 and not small_vault.exists()
        print(
            json.dumps(
                {'valid_small_plan': {'actions': 32, 'changed_files': len(entries), 'state_bytes': len(small_plan.state_bytes)}}
            ),
            flush=True,
        )
        measured = measure('mocked_fixed_relationship_budget', lambda: mocked_relationship_budget(inventory, root))
        print(json.dumps({'relationship_collector': measured}), flush=True)
        tracemalloc.stop()
        try:
            import resource
        except ImportError:
            print(json.dumps({'process_max_rss': None, 'reason': 'resource module unavailable'}))
        else:
            print(
                json.dumps(
                    {
                        'process_max_rss': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                        'unit': 'bytes'
                        if sys.platform == 'darwin'
                        else 'KiB'
                        if sys.platform.startswith('linux')
                        else 'platform-dependent',
                        'scope': 'whole process high-water including fixture setup and tracemalloc; not per-stage',
                    }
                )
            )


if __name__ == '__main__':
    main()
