# Platform, failure and scale qualification

Thread 15 remains open. Correction merge `08f67b6a` / run `40603283983`, attempt 1,
passed ten cells, including Windows 3.14/3.15. Windows 3.12/3.13 reached the
unchanged 45-minute test deadline; downstream package/install gates skipped.
Those incomplete results prevent acceptance of the selected full matrix.
Bounded diagnostics and a maintainer-approved immutable batch path optimization
are local candidates pending separate delivery/exact-commit hosted verification.
Issue #21's relevant profiling has started; it is not a new prerequisite.
The accepted Thread 14 matrix remains prerequisite evidence. See the detailed
[qualification record](../dev/THREAD_15_QUALIFICATION.md) and
[roadmap](../dev/IMPLEMENTATION_PLAN.md).

## Available evidence and filesystem limits

Qualification uses synthetic temporary projects/vaults and mocked Salesforce
acquisition, with independently queried synthetic org identity. Application runtime
network and process launches are denied except for the explicitly authorized
synthetic Python interruption/concurrency/collector test harnesses. Package setup
downloads are separate from application runtime. No real sf, Obsidian, credentials,
auth, metadata, vault or settings were accessed.

The local host is macOS 27.0.1 ARM64 on observed APFS, with Python 3.12.7, 3.13.15 and
3.14.7 available. Local Python 3.15, Linux and Windows are unavailable. Native
Windows junction execution is an explicit local skip; injected reparse/timestamp
checks remain mocked evidence. Case/normalization collision fixtures unsupported
by this APFS volume remain skips, not qualification. The native POSIX permission
checks concern mode denial; they do not certify ACLs or Windows private roots.

Use stable trusted private local ancestry for both the installed application and
synthetic fixtures. Setting TMPDIR/TEMP/TMP alone does not move the application
out of a changing ancestor. Full ancestor/path/descriptor/hash checks remain;
there is no automatic race retry. No support is inferred for HFS+, case-sensitive
APFS, NTFS, ReFS, ext4, network/cloud-synced/removable storage or unobserved hosts.
Existing accepted hosted ordinary-file tests retain their own evidence class;
runner labels do not establish filesystem types.

Full synthetic process-death, concurrency, recovery and cleanup tests cover
cooperating writers and observed checkpoints. They do not establish power-loss
durability, hostile-editor exclusion, forged/coarse timestamp detection, Windows
directory fsync, atomic snapshots or atomic multi-file transactions. Windows sf
execution remains refused; #18 is outside this task. Native Obsidian preview was
optional and unavailable in Thread 14 and was not invoked here.

## Reproducing synthetic measurements

`dev/qualify_scale.py` is a developer measurement harness, excluded from packages;
it adds no public Obforce command or stable Python API. First build/install the
candidate normally into an independent environment outside the checkout. Prepare
one stable external measurement parent and a separate empty cwd. Set all three
temporary-root variables to an existing dedicated directory under that parent.
For example, on POSIX with placeholder absolute paths:

```sh
TMPDIR="/absolute/Qualification/temp" TEMP="/absolute/Qualification/temp" TMP="/absolute/Qualification/temp" PYTHONDONTWRITEBYTECODE=1 "/absolute/Qualification/venv/bin/python" "/absolute/obforce/dev/qualify_scale.py" --classes 1000 --edges 10000 --seed 15 > "/absolute/Qualification/scale.jsonl"
```

Run from the separate empty cwd, with the installed application under the stable
measurement ancestry. The script itself blocks socket/process audit events; it
never invokes sf. Do not run other validation that changes observed ancestry
while measuring. The JSON lines record exact Python/dependency/OS/architecture,
fixture topology, stage seconds, allocation metrics, typed planning outcomes,
counts and output digest. Preserve failed results and stderr as well as successes.
Review host-specific filesystem observations separately. No installed tooling,
org, service latency or HTTP request performance is measured.

The 1,000-class fixture uses 10,000 explicit seeded directed edges and independent
partial synthetic coverage. It cannot fit the **128 changed-file** publication
ceiling: notes plus dashboard/state would total 1,002 files. Actual 127-note and
1,000-note public builds separately verify write-free refusal; no split-batch
workaround exists. A separate 32-class/320-edge plan measures valid planning,
and a separate 12-note lifecycle qualifies publication. These independent fixtures
are not chunks of the large batch.

Stage peak **traced Python allocation** bytes include retained inputs; incremental
peak subtracts traced allocations at stage entry. Neither is total RSS. Where the
standard `resource` module is available, whole-process `ru_maxrss` is reported
separately, in bytes on macOS and KiB on Linux, including setup and tracer overhead.
It is a process high-water observation, not per-stage RSS. Tracing and host load
change elapsed times. Measurements are not throughput/service-level guarantees.

Live inventory/audit mock counts expose batched behavior. Relationship collection
retains its fixed per-ID outgoing/incoming probes, bounded to 101 total queries
including org identity, and reports partial coverage even for clean empty replies.
It cannot collect all 10,000 explicit synthetic edges for 1,000 selected classes.
No query/timeout/bound is raised and no additional live query form is introduced.

## Initial installed checks — 27 October 2026

Local full installed-wheel suites passed on all three available interpreters:
Python 3.12.7: **1579 passed / 3 skipped**, 852.78s; 3.13.15: same counts, 790.86s;
3.14.7: same counts, 340.33s. Each measured **92% combined statement/branch
coverage**. Skips are the two existing case/NFC fixture limits and unavailable
Windows junction execution. Six fresh independent wheel/sdist installs also
passed. The detailed record retains all failed earlier environment runs and
uncaptured causes; later passes do not explain them.

The full graph fixture rendered 1,000 candidates, then persistent planning refused
on the state structural bound without output. A separate 32-class/320-edge plan
fit as 34 changed files; actual 12-note lifecycle publication passed separately.
Peak traced Python allocations were 49,922,605 bytes; whole-process high-water RSS
was separately measured as 135,184,384 bytes. Tracing/concurrent host load limit
timing interpretation. See the complete seven-stage measurements and JSON in the
[detailed record](../dev/THREAD_15_QUALIFICATION.md#final-reproducible-scale-observation).

Fresh wheel and sdist installs each run exact source/resource/license/archive
checks, actual console/module entry points, relative/absolute config paths with
spaces, malformed/oversized config, bounded redacted output, init/build/sync/recover
and accepted lower-level probes under active runtime guards. The shared
`dev/probe_qualification.py` adds actual transaction-ceiling refusal and a bounded
lifecycle with UUID moves, user YAML/prose, unchanged `.obsidian`, no-op bytes/mtimes,
write-free previews and whole-batch edited-dashboard conflict. No cwd artifacts.
Archive membership stays exactly 36 wheel / 35 sdist entries.

The final measured results, retained failures and unavailable/skipped checks are
in the [detailed record](../dev/THREAD_15_QUALIFICATION.md#measured-environment-results-and-retained-failures).
Threads 16–17 and enhancements #18/#19 remain **NOT STARTED**.


## First ID correction local evidence — 27 October 2026

After the initial Windows failure, the full corrected suite on native macOS
27.0.1 ARM64/APFS/Python 3.14.7 passed **1593 tests / 3 skipped in 222.26s**,
with **92% combined statement/branch coverage**, through the new supervisor.
Complete raw capture was 8730 bytes; console output 9393 bytes; longest raw line
754 bytes. The 14 new regressions passed separately on Python 3.12.7 and 3.13.15.
Two fresh independent Python 3.14.7 wheel/sdist installs and all standard checks
passed. This is local evidence; the corrected native Windows/hosted matrix
remains pending. The detailed record preserves initial failures/cancellations,
simulated/mocked boundaries and all prior failed or unavailable observations.

## Bounded CI test execution

Large fixture values must stay in test values/fixtures. The three original byte
payloads became pytest IDs and exceeded Windows' 32767-character environment
value limit when pytest set `PYTEST_CURRENT_TEST`. Setup and teardown both failed;
those test bodies did not execute. Repeated IDs also produced enormous logs.
Explicit short IDs now identify those cases, with their complete payloads intact.
A shared test hook describes long automatic string/byte parameters by length;
collection refuses any remaining node ID above 512 UTF-8 bytes without printing
the offending identifier. This also covers explicitly supplied IDs.

CI runs the developer-only `dev/run_pytest.py` supervisor from the test-suite root.
For local reproduction, select fresh absolute log paths outside the checkout:

```sh
poetry run python dev/run_pytest.py --collect-only --log /absolute/isolated/collection.log
poetry run python dev/run_pytest.py --log /absolute/isolated/pytest.log
```

The supervisor retains combined stdout/stderr in an exclusively created log and
prefixes console lines to prevent child text becoming Actions workflow commands.
Its finite budgets are separate from all application safety limits:

| CI boundary | Budget / behavior |
| --- | --- |
| Automatic string/byte parameter description | Values over 96 bytes use length-based IDs; values remain intact |
| Collected test node ID | 512 UTF-8 bytes; collection error before test setup |
| Raw capture and emitted child console output | Each at most 2 MiB, plus a small fixed controller status |
| Child diagnostic line | 4096 bytes; overflow fails instead of printing the line |
| Collection wall time / Actions step | 5 / 6 minutes |
| Coverage suite wall time / Actions step | 45 / 50 minutes |
| Independent artifact install step / entire matrix job | 30 / 90 minutes |
| Failure diagnostics | Short tracebacks, no captured-output dumps, stop after five failure reports |
| Matrix / superseded runs | Fail fast; superseded runs in the same workflow/ref group cancel |

Output overflow, deadline or uncertain cleanup exits unsuccessfully and marks
the retained log as an incomplete bounded prefix. It cannot establish a complete
test or coverage pass. Existing log paths are never overwritten; there is no
automatic retry. A failed pytest exit remains failed. Cancellation and unexecuted
tests remain qualification gaps. Default pytest diagnostics are bounded in
`pyproject.toml`; the supervisor supplies the capture/time boundaries in CI.

The controller terminates its owned POSIX process group or uses Windows' native
`taskkill` for its owned pytest tree, then reaps the child. The outer Actions
deadlines backstop unconfirmed cleanup. This is ordinary CI process management,
not hostile-process containment or Windows sf execution. Native Windows cleanup
and the corrected hosted matrix still require exact-commit verification. No
application limit, filesystem guard, schema, payload, dependency or scope changed.
The supplied raw failure log stays private and unmodified; public tracking holds
only reviewed synthetic summaries and evidence boundaries.


## Runtime investigation after the bounded Windows timeouts

Ten successful cells establish their own results; they cannot fill the two
incomplete Windows interpreter cells. The supervisor reported only 1713 raw
bytes in each failure, incomplete capture and confirmed cleanup. The giant-ID
problem did not recur. Reaching 94% is not an exact test, coverage or packaging
result. Per-case verbose output and `--durations=25` now remain within the same
2 MiB/4 KiB budgets. On timeout, a bounded unfinished line can identify the last
started case; it does not establish its completion or precise internal phase.

The approved internal optimization snapshots note paths immutably for one batch.
Renderer and graph validation remain lazy at their original call sites, retaining
error precedence. Each evidence-validation invocation and each planning/replanning
pass constructs a fresh snapshot; no global or filesystem-observation cache is
added. Ordinary mapping inputs to standalone helpers still receive full checks.
Exact note bytes, hashes, graph/move invalidation and malformed/unrelated path
refusals are compared in regressions. No renderer/schema version, input payload,
128-file publication ceiling, deadline or safety guard changes. Other #21
optimizations remain proposals; Windows sf remains refused.

Profiling has instrumentation overhead. An interrupted partial baseline is not
a passing test, complete timing baseline or proof of the Windows timeout cause.
The detailed record retains it and the shared-coverage/installer-ancestry setup
errors separately from clean isolated validation. Give each concurrent local run
its own `COVERAGE_FILE`, fixture root and stable installer/application ancestry.
Use `Profile.runcall(pytest.main, ...)` with explicit propagation of pytest's exit
status for profiling: the stdlib `cProfile -m` CLI can consume `SystemExit`, so
its shell status alone cannot establish pytest success.


## Approved runtime correction local results — 28 October 2026

Full installed-candidate suites on observed native macOS 27.0.1 ARM64/APFS:

| Actual Python | Full pytest outcome | Seconds | Statement/branch coverage |
| --- | --- | ---: | ---: |
| 3.12.7 | 1605 passed, 3 skipped | 416.08 | 92% |
| 3.13.15 | 1605 passed, 3 skipped | 382.80 | 92% |
| 3.14.7 | 1605 passed, 3 skipped | 179.44 | 92% |

Captures completed under existing budgets with confirmed cleanup. The unchanged
case/NFC representation and locally unavailable Windows junction skips remain
gaps. Six fresh independent wheel/sdist installs, exact 36/35 archives and all
standard checks passed. These local results do not qualify the new runtime code
on hosted Windows/Linux/Python 3.15. #15 remains open pending exact-commit hosted
verification and acceptance; Threads 16–17 and #18/#19 remain NOT STARTED.

The [complete repeated scale JSON](../dev/evidence/thread15-scale-macos-py314-20261028.jsonl)
retains seven stages, 1000 classes/10000 explicit edges and seed 15. All candidate
bytes/hash and the valid 34-file/506545-state-byte plan exactly match the original.
Large planning still refuses its structural state bound without output. Maximum
traced Python allocation peak is 50159647 bytes; separate macOS whole-process RSS
high-water is 137265152 bytes. Tracing and concurrent host load limit timing
interpretation; direct rendering uses ordinary inputs and full per-call checks.
The [detailed record](../dev/THREAD_15_QUALIFICATION.md#bounded-timeout-review-and-approved-runtime-correction--28-october-2026)
retains the partial profiler failure, completed profile and setup/installer failures
without assigning uncaptured causes or turning later success into earlier proof.
