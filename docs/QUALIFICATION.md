# Platform, failure and scale qualification

Thread 15 is a local qualification candidate. #15 remains open for maintainer
acceptance. New tests have no exact-commit hosted result until delivery and
verification are separately authorized. The accepted Thread 14 hosted matrix is
prerequisite evidence; it does not qualify subsequent changes. See the detailed
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

## Installed checks and current results

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
