# Thread 15 qualification record

Thread 15 / [#15](https://github.com/jeffshurtliff/obforce/issues/15) only, authorized
27 October 2026, with a scoped runtime correction approved on 28 October.
Current status: **ACCEPTED AND COMPLETE; #15 closed**, 28 October 2026.
Implementation `3771c16` / merge `178bf98`, run `40721222520`, attempt 2, passed
all twelve selected cells and twenty-four independent installs. Earlier dated
handoffs remain historical. Thread 16 is eligible but **NOT STARTED**; Thread 17
and enhancements #18/#19 remain **NOT STARTED**. The approved #21 path scope is
delivered/verified; broader optional work remains open and proposed. No release
or platform provisioning.

## Prerequisite and scope

Read the existing issue, closed prerequisite #14, its acceptance comments, current
native #14 → #15 → #16 dependencies, required reference documents and actual code.
Checkout began clean at documentation commit `35b1036`, descending from accepted
Windows path correction `6d08696` / merge `cdf0e68`. The existing acceptance docs
were already committed; they were preserved. No `local/vendor_docs/` exists.

Re-read every job's command log in exact-merge
[40517073513, attempt 1](https://github.com/jeffshurtliff/obforce/actions/runs/40517073513):
all 12 Python 3.12–3.15 Linux/macOS/Windows cells, every required standalone gate,
exact 36/35 archive lists and 24 independent installs passed. Counts remain Linux
1555 each, macOS 1553/2 each, Windows 1539/16 each. These are **prerequisite**
hosted results, not verification of this candidate. No CI run was requested.

Failed `40427329142` remains failed: each Windows cell 2 failed/1521 passed/16
skipped; downstream package/install/whitespace gates skipped. `40235515146` and
all older failed/skipped/unavailable observations remain in the roadmap. Causes
of the original template-refresh conflict 3 and Thread 12's
2-failed/1371-passed/2-skipped run remain uncaptured. Neither later passes nor
separate Windows CRLF/relative-path defects explain them.

Preserve state-document/evidence/NoteState/journal/dashboard/renderer versions
**2/1/1/2/1/4**, note/marker/config 1 and exit precedence **3,2,1,4,0**. No new
metadata type, command/API, dependency, limit, retry, publication splitting,
adoption/migration, inferred fact/debt, backup or Git integration.

## Finite-bound design, before dependent benchmark work

`MAX_TRANSACTION_FILES` is **128**, including changed notes, dashboard and state.
A 1,000-note initial build would change **1,002 files** and cannot publish. Even
127 initial notes exceed the ceiling (129 files). Independent state/evidence,
node, path, byte, render and planner bounds may refuse earlier. No bound is raised,
no evidence is truncated and no batches are split to evade whole-batch safety.

Developer script `dev/qualify_scale.py` measures separately:

1. Local collection/normalization of 1,000 fictional Apex XML/source pairs. Bodies
   are never read; setup precedes timing.
2. Actual live-adapter normalization through mocked binary replies, including its
   independent minimal synthetic Organization query, terminal inventory probe and
   batched dates with audit-name collection disabled. No real process or service.
3. A **separate explicitly synthetic** 10,000-edge graph. Seed 15 shuffles a
   permutation of 1,000 vertices; each source connects to the next ten forward
   offsets on the ring. Distinct directed pairs, cycles, ten incoming/outgoing
   edges per vertex, no self edge. Evidence is labeled synthetic and partial;
   source text never supplies edges. This is not platform acquisition evidence.
4. Rendering all 1,000 candidates with the complete explicit mapping, installed
   templates, deterministic fixture UUIDs and an aggregate output hash/byte count.
5. Full persistent planning attempt, reporting the actual typed refusal if an
   independent bound is reached. A separate 32-class/320-edge plan verifies valid
   persistent planning and its 34 changed files without publishing.
6. The actual fixed relationship collector under empty mocked replies. It stops at
   101 queries including identity, after 50 classes' two-direction probes; partial
   coverage and zero collected edges remain explicit. This cannot collect the
   separately supplied 10,000-edge synthetic graph for 1,000 classes.

The script enforces application socket/process audit denial, uses no external
process for environment discovery, writes only its synthetic temporary inputs,
and reports JSON lines with elapsed seconds, current/peak traced allocations and
incremental peak above stage-entry allocations. **Tracemalloc is Python allocation
tracking, not total RSS** and changes measured timing. Supported POSIX hosts also
report whole-process `ru_maxrss` high-water separately (macOS bytes, Linux KiB),
including setup, retained inputs and tracing overhead; it is not per-stage RSS.
It emits dependency/interpreter/OS/architecture, seed/topology, counts and complete
outcomes, not raw source/graph/state or host paths. Timings are observations, not
throughput or service-level promises; uncontrolled host load remains a limitation.

`dev/probe_qualification.py` independently exercises actual 127-note publication
refusal, complete tree preservation and absent output parents; a separate 12-note
build/sync/move/human-field/dashboard-conflict/recover/no-op lifecycle fits the
existing contract. The suite additionally checks the full 1,000-note public
refusal with default limits. Each case is independent, not a chunk of a larger
publication. Both fresh distributions run the shared probe with runtime guards.

## Boundary audit and evidence classes

| Boundary | Qualification mechanism | Limits on interpretation |
| --- | --- | --- |
| Paths and object types | Native public source/config/vault hard-link, symlink and FIFO refusals; existing case/NFC/reserved/overlap/lexical-link checks | Initial nonempty-vault cases test repeat/nonempty refusal; existing native reconciliation cases test managed-vault link/type rejection. Availability/skips reported individually; injected reparse stays mocked |
| Windows junction | Python `_winapi.CreateJunction` on a synthetic directory; no shell | Unavailable locally; no Windows result claimed for new test |
| Permissions and privacy | Actual POSIX mode denial where identity cannot bypass it; injected Click access-denial regression on every host; installed console/module invalid/over-byte inputs | POSIX modes are not native ACL or Windows access-control qualification |
| CRLF and human content | Existing exact LF/CRLF baseline/patch tests, new bounded lifecycle, installed lower-level probes | Unsupported mixed owned envelopes still refuse; no whole-note creation refresh |
| Locks/concurrency/interruption | Existing synthetic Python process death, held owning-handle lock, competing writer and intervening-edit tests | Cooperating writers only; no hostile-race, power-loss or atomic snapshot/multi-file claim |
| XML/YAML/templates | Actual byte/depth/DTD ceilings plus existing scanner/event/node/scalar/property/AST/context tests | Finite in-process bounds, not OS CPU/memory isolation or arbitrary YAML/Jinja support |
| State/evidence/journal | Actual oversized/deep input plus existing exact key/version/node/hash/descriptor semantic tests and artifact probes | No evidence reconstruction, legacy sync migration or journal-schema-1 recovery |
| Time/output/process cleanup | Actual hard-ceiling rejection; existing bounded synthetic Python pipe/timeout/descendant/interruption tests | POSIX trusted process-group boundary; Windows sf still refused; no real sf/HTTP request measurement |
| Publication/cleanup | Actual 127/1,000-note refusal and separate 12-note lifecycle; existing constrained rollback/committed-cleanup tests | Same-filesystem staging/full guards unchanged; no limit increase or broad deletion |
| Source/config/templates/inputs/ordinary/.obsidian | Complete synthetic snapshots before/after previews/no-ops/conflicts and installed probes | Atime is an ordinary read side effect; bytes/mtimes/tree are the preservation evidence |
| Packaging/entry points | Fresh exact 36-wheel/35-sdist inspection, both independent guarded installs, console/module relative/absolute space paths | Setup downloads separate from denied application runtime; no native Obsidian preview |

Qualification exposed Click's preliminary readability error echoing an explicit
private config path and returning usage 2 before the guarded engine read.
`cli.py` now leaves readability to the existing engine/transport reads using
`readable=False` on Click path conversion. The guarded read supplies operational
1 with fixed redacted text. Native Path conversion, lexical/parent/descriptor/
birthtime/hash/absence checks and all engine/transport validation remain. No
read is allowed merely because Click no longer performs an `os.access` check.

CI now prints `-ra` skip summaries and ignores only Markdown under `dev/`, so
qualification/probe/checker Python changes trigger the existing matrix on future
authorized delivery. No matrix/interpreter pin, dependency or timeout changed.

## Measured environment, results and retained failures

Verified results and the final validation handoff follow below. Local
filesystem observation: APFS, native macOS ARM64. No HFS+, case-sensitive APFS,
NTFS, ReFS, ext4, network/cloud-synced/removable filesystem result is inferred.
Stable trusted private local ancestry is required; changing ancestors still
refuse. Local Python 3.12.7/3.13.15/3.14.7 are available; 3.15, Linux and Windows
are unavailable locally. Availability does not itself qualify a cell.

Initial development history is retained: sandboxed build-backend download failed;
separate authorized setup succeeded. The first benchmark environment probe was
denied when `platform.platform()` attempted `uname`; process-free calls replaced
it without weakening the guard. A second harness invocation exposed a missing
Selection argument before collection; corrected. These are harness failures,
not application/runtime qualification. Initial focused tests: 2 failed/20 passed/
1 unavailable-Windows-junction skip (43.24s): an uncaptured public planning
conflict 3 and Click's captured unreadable-path leak/outcome. A subsequent focused
run was 1 failed/25 passed/1 skip (83.80s), because an incorrect expectation of
conflict 3 contradicted the actual transaction-bound invalid outcome 2. That
expectation was corrected; future unexpected planner refusals now retain fixed
typed diagnostic reasons. No cause is inferred for the earlier uncaptured
conflict. No refused application operation was retried within an invocation.


## Identified cost and acquisition opportunities

Code inspection identifies repeated whole-input work without changing semantic
contracts in this candidate:

- `renderer.notes.render_generated` validates the complete V-path mapping for
  each of V candidates. `DependencyGraph.note_fingerprint` independently validates
  it again: O(V²) path validation, rather than one bounded immutable batch view.
- `references`, `referenced_by`, incident rendering and per-note fingerprinting
  scan all E edges repeatedly: O(VE) edge visits. An internal immutable adjacency
  index could avoid unrelated-edge scans while preserving exact ordering,
  hashes, unresolved incoming endpoints, stale evidence and move invalidation.
- Persistent state/evidence validation repeats per-note fingerprints at several
  construction/serialization gates. A future internal optimization must preserve
  every independent validation boundary, input immutability and exact wire/hash
  outputs; a mutable/shared cache cannot silently substitute for validation.
- An over-bound initial build currently renders/plans before the final writer
  file-count gate. A separately reviewed early count preflight could avoid that
  work, while retaining earlier identity/conflict validation and whole-batch
  outcomes. This qualification does not change phase ordering or failure precedence.
- Mocked inventory/audit demonstrates batching, not one process per component:
  1,000 classes, 200/page, names off: one org query, six inventory queries including
  terminal empty query, five date queries. No unnecessary per-component inventory
  or audit call was observed. Source inspection shows that names-on adds one names query per selected page;
  the benchmark explicitly omits names.
- The relationship collector does use two per-component probes. This is the
  accepted restrictive query contract, not authorization to add IN/range/COUNT/
  continuation, another transport or broader platform access. Its 101-query cap
  means only the first 50 selected IDs can receive both probes in this fixture.
  Coverage remains partial; the 10,000 explicit synthetic edges come from the
  separate fixture. Query broadening would require a material scope/contract
  proposal and authorization before implementation; no such change was made.

No optimization is hidden behind weakened guards, raised budgets or dropped
information. Traced timings can locate expensive stages, but are not a controlled
comparative performance experiment. No speedup or future service level is claimed.


### First full local runs and observation diagnosis

The first Python 3.14 full installed-wheel run finished **2 failed / 1575 passed /
3 skipped / 2 setup errors**, 190.42s. One new public scale-refusal check captured
`Read path changed during observation`; baseline refresh-bound/dashboard setup
and a recovery symlink test also refused before their intended checkpoints.
Their original detailed changing observations were not captured, so no shared
cause is inferred for them. The three skips were native Windows junction
unavailable and the existing case/NFC representation limits.

A separate diagnostic run of the 1,000-note test was **1 failed**, 40.67s. An
external delegating reader wrapper captured the shared system-temp ancestor's
full pathname stamp: device/inode/mode/link-count/size unchanged, mtime_ns and
ctime_ns changed. That exact observation explains only this diagnostic refusal.
Both the installed application and synthetic fixtures were then relocated under
a separate temporary ancestry, with independent TMPDIR/TEMP/TMP per interpreter.
No retry inside an application invocation, guard change or skip was added.
Earlier exploratory/full failures remain failures. Diagnostic wrappers delegate
to the original reader/failure functions and only record a failure's observations.

The exploratory scale run completed: local normalization 1.446014s; mocked live
normalization 0.285681s; graph 1.292542s; rendering 142.933921s; planning attempt
200.492716s (blocked 3, no vault); fixed collector 0.075094s. It rendered 1,000
notes/6,855,000 bytes with SHA-256
`5d6f8dcca8e105a43ff3a32fae1adf48b44eb380d181af8b94c90d2e4768a7a5`.
Largest per-stage traced Python peak: 49,863,861 bytes during planning;
whole-process max RSS: 116,555,776 bytes. Concurrent development/validation and
changing temp ancestry limit interpretation. Its generic planning refusal did
not capture the exact original reason and is not relabeled by a later run.
The final isolated benchmark below retains its typed reason and measures the
separate valid 32-class plan as well.


### Additional changing-ancestry observations

The first shared system-temp full Python 3.12 run: **5 failed / 1568 passed /
3 skipped / 6 setup errors**, 509.04s. Python 3.13: **6 failed / 1573 passed /
3 skipped**, 469.13s. Preserve these outcomes; detailed original changing stamps
were not captured for their individual failures. Their coverage runs did not
load the project branch/subprocess coverage configuration from the separate cwd;
no combined branch-coverage percentage is claimed for those checkpoints.

The alternate per-user temporary ancestry also produced refusals. A separate
small diagnostic was **1 failed / 1 passed**, 3.64s. Its external delegating
wrapper captured a full stamp change on that ancestry's temporary ancestor:
identity/mode/link-count/size unchanged, mtime_ns/ctime_ns changed. This explains
only that diagnostic refusal. The fresh artifact checker in this ancestry
inspected the wheel but failed its dashboard probe during initial build; the
original detailed reason was not retained there. No complete independent wheel
install pass or sdist install pass is claimed from that attempt.

A private synthetic directory under a separate standard temporary parent was
created with mode 0700, outside both observed changing ancestors. Both installed
applications and synthetic fixtures moved there; console scripts were reinstalled
from the same candidate without dependency downloads. The preliminary native
initial-journey checks passed **2/2** in 0.81s with unchanged guards. Full runs now
explicitly select the project coverage configuration, including branch and
subprocess coverage. No system policy, platform or real user data was changed.


### Further retained temporary-ancestry results

Per-user-temp Python 3.14 full run: **15 failed / 1544 passed / 3 skipped /
20 setup errors**, 414.48s. Alternate-temp Python 3.14 full run: **4 failed /
1575 passed / 3 skipped**, 311.07s. Alternate-temp Python 3.13: **5 failed /
1570 passed / 3 skipped / 4 setup errors**, 661.91s. All nine completed exploratory full
outcomes are retained below.

A diagnostic 1,000-note check in the alternate ancestry was **1 failed**, 57.94s.
It captured that standard temporary parent's stamp changing only mtime_ns and
ctime_ns while device/inode/mode/link-count/size stayed unchanged. This explains
only that diagnostic refusal. All three standard temporary ancestry choices
therefore have observed instability here. The private mode-0700 synthetic root
was moved outside those three ancestors; actual filesystem there is also APFS.
No ancestor permissions or system policy changed; no automatic operation retry.
The preliminary initial journey there passed **2/2**, 0.78s.

### Current verified local results

Local host: **macOS 27.0.1 (26A434), Darwin 27.0.0, ARM64, APFS**.
Poetry 2.4.2; runtime Click 8.5.0, defusedxml 0.7.1, Jinja2 3.1.6,
MarkupSafe 3.0.4 and ruamel.yaml 0.19.1. Test environments use pytest 9.1.1,
pytest-cov 7.1.0, coverage 7.17.0 and PyYAML 6.0.3. No dependency/lock change.
The installed code and external public synthetic test copies are isolated from
checkout/cwd, with per-interpreter temp roots. Full coverage explicitly loads
project branch/subprocess configuration. Synthetic process harnesses retain their
own runtime guards and authorized Python-only child operations.

- Python 3.14.7 full suite: **1579 passed / 3 skipped**, **340.33s**, **92% combined
  statement/branch coverage** (4693 statements, 2070 branches). No full-suite
  failure remains in this run. Skips: existing native case/NFC representation
  limits and unavailable Windows junction execution.
- Final stronger native refusal assertions: Python 3.12.7 **9 passed / 1 skipped /
  17 deselected**, 0.40s; 3.13.15 same counts, 0.38s; 3.14.7 same counts, 0.32s.
  The one skip is the unavailable Windows junction. These targeted runs validate
  exact invalid 2 for unsafe source entries and conflict 3 for config/initial
  nonempty vault refusals, after tightening the original aggregate assertion.
- Fresh final build, strict Twine, exact complete **36-wheel / 35-sdist** archive/
  source/resource/license/metadata inspection and both independent installs passed
  on **each of Python 3.12.7/3.13.15/3.14.7**: **six independent installs**.
  Active socket/process denial, installed assets, actual console/module paths with
  spaces, malformed/over-byte/unreadable config redaction, init/build/sync/recover,
  finite-bound/lifecycle and accepted lower-level probes, no cwd artifacts.
  Setup/build dependencies used separately authorized downloads; runtime did not.
- Strict Poetry metadata/lock, Ruff lint/format, Bandit and whitespace passed.
  Bandit retains five existing line-specific suppressions and no new issues.
- Documentation review currently covers 9 changed/new Markdown files, 172 local
  links/anchors, no missing targets; final handoff is reviewed again after results.

Final artifacts:

| Artifact | SHA-256 |
| --- | --- |
| Wheel | `1652dc1f7ed6e3b063d1c2d0a6e08a6f3fceda2739869bc820d65c36a326407b` |
| Sdist | `4d46c49d79b0d71e80db3e62dbb7857d22d968b8d7066343cd5942cf81b2eafb` |

These are local candidate results, not maintainer acceptance or hosted evidence.
Windows/Linux/new Python 3.15 tests remain unavailable locally and require
separately authorized delivery/exact-commit hosted verification. Optional native
Obsidian preview remains unavailable and was not invoked.

### Final reproducible scale observation

[Complete public-safe JSON lines](evidence/thread15-scale-macos-py314.jsonl):
16 complete records, seven measured stages, exit 0, empty stderr. Native
macOS 27.0.1/APFS/ARM64, Python 3.14.7 and runtime versions above. A separate
installed benchmark application avoided coverage setup/teardown changes; code
and fixtures were outside all captured changing standard temporary ancestors.
Other validation was concurrent, so times reflect that load, not a controlled
speed comparison or throughput promise. Host load was not measured.

| Stage | Seconds | Peak traced Python bytes | Incremental peak above stage entry |
| --- | ---: | ---: | ---: |
| Offline collection/normalization, 1,000 pairs | 2.479343 | 7,067,247 | 7,067,079 |
| Mocked live collection/normalization, 1,000 records | 0.453992 | 3,902,421 | 2,150,705 |
| Explicit synthetic graph, 10,000 edges | 2.219986 | 8,427,515 | 5,669,713 |
| Render all 1,000 candidates | 229.426298 | 5,598,091 | 1,204,664 |
| Large persistent planning attempt, refused | 255.376856 | 49,922,605 | 45,318,979 |
| Separate valid 32-class/320-edge persistent plan | 1.544702 | 11,931,988 | 6,953,920 |
| Actual fixed relationship collector under mocks | 0.068367 | 6,490,034 | 506,112 |

The large graph plan captured **ConflictError: State exceeds structural bound**,
outcome **3**, one global conflict action, no state/candidate publication and an
absent vault. That reason applies only to this observation; no earlier generic
conflict acquires a retroactive cause. The independent offline public 1,000-note
case reaches the unchanged transaction aggregate gate with invalid **2**; the
127-note installed case independently exceeds 128 changed files as 129. Both
preview and actual build refuse without creating output parents/artifacts.

The separate 32-class graph plan was valid: **32 note actions / 34 changed files**,
**506,545 state bytes**, no output creation. The separate 12-note installed probe
qualifies actual within-bound publication/lifecycle, not a piece of the large
batch. No note/state/evidence is dropped or split to fit a bound.

Rendering produced **1,000 notes / 6,855,000 bytes**, aggregate SHA-256
`5d6f8dcca8e105a43ff3a32fae1adf48b44eb380d181af8b94c90d2e4768a7a5`,
matching the earlier same-interpreter fixture observation. No cross-version or
cross-platform byte-reproducibility promise follows. Mocked inventory/audit used
**1 identity + 6 inventory + 5 date calls**, with names explicitly omitted. The
separate fixed relationship collector used **101 calls / 0 edges / partial
coverage**, with collection-budget/exhaustion/supported-type warnings retained.
No real sf or HTTP request count was measured.

Whole-process high-water RSS was **135,184,384 bytes** on macOS, including setup,
retained inputs and tracing overhead. It is separate from traced Python peaks
and is not per-stage RSS. No total offline build/render/plan wall deadline exists:
finite input/output/AST/node bounds do not establish a time service level.
Transport/session deadlines remain 60/300 seconds within their own contracts,
not whole-lifecycle budgets; no timeout was raised.

Harness SHA-256:
`d1ca8083c87954a8258ad81882880fef398b330743429e6163ba75717e007a0d`.

### Complete retained exploratory matrix outcomes

These distinct environment runs used fresh synthetic test fixtures and stopped
refused application invocations immediately. Subsequent environment qualification
is not an internal operation retry or adoption of retained output. Every original
failed/skipped result remains below. Diagnostic ancestor observations explain only
the specifically captured diagnostic cases, not each failure in these matrices.

| Observed ancestry / Python | Full outcome | Seconds |
| --- | --- | ---: |
| Shared system temporary / 3.12.7 | 5 failed, 1568 passed, 3 skipped, 6 setup errors | 509.04 |
| Shared system temporary / 3.13.15 | 6 failed, 1573 passed, 3 skipped | 469.13 |
| Shared system temporary / 3.14.7 | 2 failed, 1575 passed, 3 skipped, 2 setup errors | 190.42 |
| Per-user temporary / 3.12.7 | 34 failed, 1503 passed, 3 skipped, 42 setup errors | 1113.89 |
| Per-user temporary / 3.13.15 | 36 failed, 1513 passed, 3 skipped, 30 setup errors | 1037.58 |
| Per-user temporary / 3.14.7 | 15 failed, 1544 passed, 3 skipped, 20 setup errors | 414.48 |
| Alternate standard temporary / 3.12.7 | 5 failed, 1573 passed, 3 skipped, 1 setup error | 735.28 |
| Alternate standard temporary / 3.13.15 | 5 failed, 1570 passed, 3 skipped, 4 setup errors | 661.91 |
| Alternate standard temporary / 3.14.7 | 4 failed, 1575 passed, 3 skipped | 311.07 |

The first group did not load branch/subprocess coverage from the external cwd;
no combined percentage is claimed for it. Later groups explicitly selected the
project configuration. The three repeated skips remain case/NFC fixture
representation limits and unavailable native Windows junction execution, never
qualification. The artifact attempt under per-user temporary ancestry failed
before complete wheel/sdist verification; the six successful independent installs
are separate later evidence under their actually stable observation windows.


### Final full-suite matrix and review state

| Local native environment | pytest outcome | Seconds | Combined statement/branch coverage |
| --- | --- | ---: | ---: |
| macOS 27.0.1 ARM64 / APFS / Python 3.12.7 | 1579 passed, 3 skipped | 852.78 | 92% |
| macOS 27.0.1 ARM64 / APFS / Python 3.13.15 | 1579 passed, 3 skipped | 790.86 | 92% |
| macOS 27.0.1 ARM64 / APFS / Python 3.14.7 | 1579 passed, 3 skipped | 340.33 | 92% |

All three commands exited 0. Coverage totals are 4693 statements and 2070 branches;
the final stronger native assertions were additionally verified separately on
all three interpreters as recorded above. The same three explicit skips remain
in each full run; no skip is counted as platform qualification. All exploratory
failed runs retain their separate outcomes. Six independent wheel/sdist checks
also exited 0; current repository package bytes/README still match those archives.

No new Linux, Windows, Python 3.15, native Windows junction/ACL/sf, power-loss,
hostile-race, network/cloud/removable filesystem or native Obsidian evidence.
The three available Python versions are exact observations, not claims about
unmeasured patch releases. Existing prerequisite hosted results remain distinct
from these uncommitted local changes. New exact-commit hosted verification requires
separate delivery authorization; none was performed or rerun here.

**Review state:** Thread 15 implementation/qualification candidate is complete
locally, with its matrix/native gaps explicit. #15 stays **OPEN** for maintainer
acceptance. All changes remain unstaged/uncommitted on the existing checkout;
no branch, stage, commit, push, PR, merge, tag, release, upload or publication.
No real sf/Obsidian/auth/credentials/.env/org/vault/settings access, private upload,
platform provisioning, system-policy change or delegation. Private synthetic
validation scratch and full diagnostic logs remain outside the checkout.
**Next eligible after #15 acceptance: Thread 16, NOT STARTED.** Thread 17 and
enhancements #18/#19 remain **NOT STARTED**.


### Tracking verification and final receipt

The [public-safe final handoff](https://github.com/jeffshurtliff/obforce/issues/15#issuecomment-6451593585)
and existing #15 body/checklist are synchronized. Readback confirms **OPEN**,
unchanged `ci`, `codex`, `maintainer`, `security`, `testing` labels, maintainer
assignee and v0.1.0 milestone; native closed #14 → open #15 → open #16 links
remain intact. New full hosted matrix, CI passes and ready-to-close checkboxes
remain unchecked. No duplicate tracking issue or later-thread work.

The prospective Windows junction fixture's argument order was source-checked
against CPython's [v3.12.7 native junction test](https://github.com/python/cpython/blob/v3.12.7/Lib/test/test_os.py).
This is source inspection only; it does not replace the unavailable native result.


Final local documentation/privacy/consistency review: **9 Markdown files / 179
local links and anchors / 0 errors**, complete 16-record benchmark JSON, Ruff
lint/format and whitespace passed. Git status confirms all **16 changed/new
files remain unstaged/uncommitted**; no unrelated or staged file, Git delivery,
CI rerun, closure, publication or later-thread action.

Existing branch retained: `test/15-thread-15-platform-failure-and-scale-qualification`.
No branch was created or renamed.


## Windows CI failure and bounded correction — 27 October 2026

### Exact hosted evidence and cause

Maintainer-delivered implementation `a259fc4`, merge
`ae44a2cf3873ba7f16076a9bf577c7bd9f4721fd`, ran as
[40575562800, attempt 1](https://github.com/jeffshurtliff/obforce/actions/runs/40575562800).
This is initial Thread 15 evidence, separate from accepted Thread 14 and the
correction below. Exact commit and required commands were read in each of the
eight successful job logs, alongside native step conclusions. All eight passed
metadata/lock, Ruff lint/format, Bandit, coverage pytest, fresh build, strict Twine,
exact archive checks, both independent installs and whitespace: 16 installs.
Runner labels alone do not identify tested filesystems or prove native ACLs.

| Hosted cell | Job | pytest outcome | Reported seconds |
| --- | --- | --- | ---: |
| Linux / Python 3.12 | 122440940110 | 1581 passed, 1 skipped | 1504.76 |
| Linux / Python 3.13 | 122440940288 | 1581 passed, 1 skipped | 1865.76 |
| Linux / Python 3.14 | 122440940405 | 1581 passed, 1 skipped | 572.14 |
| Linux / Python 3.15 | 122440939910 | 1581 passed, 1 skipped | 319.82 |
| macOS / Python 3.12 | 122440940355 | 1579 passed, 3 skipped | 1271.91 |
| macOS / Python 3.13 | 122440940222 | 1579 passed, 3 skipped | 1094.51 |
| macOS / Python 3.14 | 122440940545 | 1579 passed, 3 skipped | 311.40 |
| macOS / Python 3.15 | 122440940408 | 1579 passed, 3 skipped | 453.75 |
| Windows / Python 3.14.9 | 122440940091 | 1557 passed, 22 skipped, 6 errors | 1627.34 |
| Windows / Python 3.12.10 | 122440940286 | 1557 passed, 22 skipped, 6 errors | 2617.11 |
| Windows / Python 3.13 | 122440940763 | Cancelled; no complete qualification result | Unavailable |
| Windows / Python 3.15 | 122440940237 | Cancelled; no complete qualification result | Unavailable |

Windows Python 3.14's complete maintainer-supplied raw log is **71,652,081 bytes**,
SHA-256 `2e7d99c8eb040bdc41c73d5aad7479b7971bf83327e7ecd95dea18deec45b31e`.
The original private file remains unmodified and is not uploaded or packaged.
Bounded local scanning found 12 lines over 32767 bytes, maximum 16,777,430 bytes;
only short reviewed summaries are public. A separate direct read of Windows
Python 3.12.10 job 122440940286 confirms the same three setup/teardown cases and
six environment-value errors: 1557 passed/22 skipped/6 errors in 2617.11s. That
raw log is 71,652,034 bytes, SHA-256
`c62d832c4fae3d929de9809a8fa0c3b2b221de28f7d1b234c2625e8ad4c1fc66`; it also
stays private. The first gh read refused terminal escape sequences; the second
explicitly saved raw bytes to a file for bounded inspection, never rendering
them in a terminal. Windows metadata/lock, Ruff and Bandit
passed; failed/cancelled pytest left downstream build/Twine/archive/install/
whitespace gates unqualified. The Python 3.13 job snapshot still showed pending
steps although its job conclusion was cancelled; none is counted as passed.
No cancellation or CI rerun was initiated in this correction session.

Three byte values without explicit pytest IDs caused the six Python 3.14 errors:
65,537-byte XML, 16,777,217-byte state, and 1,048,577-byte note payloads. Pytest
expanded each complete value into a node ID and set `PYTEST_CURRENT_TEST` in both
setup and teardown. Windows rejected the environment value above 32767 characters.
The test bodies therefore never executed. Error headings and summaries repeated
the huge IDs. Pytest reported 1627.34s while oversized diagnostics continued
arriving much later; the exact runner/transport bottleneck was not isolated.
This test metadata defect does not explain any earlier unrelated failures.

### Correction and safeguards

- Explicit short IDs describe all six parser-limit cases without shrinking or
  changing payloads. A shared hook describes large automatic string/byte values
  by length; a 512-byte UTF-8 node-ID ceiling rejects oversized explicit IDs at
  collection without echoing payloads.
- Default pytest reports use short tracebacks, no captured-output dumps and a
  five-failure-report stopping point. Unexecuted tests remain gaps.
- Developer-only `dev/run_pytest.py` first supervises collection, then coverage.
  Raw capture and emitted child console output each have a 2 MiB ceiling; lines
  have a 4096-byte ceiling. Logs are exclusively created outside the checkout in
  CI and never overwrite old evidence. Console lines are prefixed against Actions
  workflow-command injection. Overflow fails and labels any retained prefix
  incomplete; it cannot turn truncated evidence into a pass.
- Collection/test child deadlines are 5/45 minutes, with 6/50-minute Actions step
  deadlines; artifact installs have 30 minutes and each complete job 90 minutes.
  Matrix fail-fast and workflow/ref concurrency stop redundant work. There is no
  automatic retry, timeout increase or application bound change.
- Cleanup targets only the owned pytest process group/tree, reaps the child and
  fails on unconfirmed cleanup. Windows taskkill is CI process management, not
  application sf transport. Outer Actions deadlines backstop escaped descendants
  or blocked controller output; hostile-process containment is not promised.

The complete [CI policy and reproduction](../docs/QUALIFICATION.md#bounded-ci-test-execution)
is documented. No source/runtime/package asset, lock/dependency/schema/renderer,
identity/ownership/human-field, transaction limit/guard/recovery or CLI behavior
changed in this correction. The developer runner and test hooks are not packaged.

### Correction development observations

A small synthetic subprocess before the fix enforced Windows' UTF-16 environment
value ceiling on this macOS host: **6 errors in 0.11s**, exit 1, 98 output bytes
with traceback/summary suppression. This reproduces setup/teardown failure but
is simulated, not native Windows evidence. New regression tests execute all
three complete original payload sizes under the same simulated ceiling, refuse
100000-character explicit IDs without echo, handle Unicode, collect actual
parser cases, and exercise flood/deadline/exit/log preservation/child cleanup.
Windows cleanup dispatch has a separate mock; POSIX descendant cleanup executes
native synthetic Python children. Neither is native Windows cleanup qualification.

Exploratory development outcomes remain: 1 failed/11 passed in 1.35s, then
1 failed/13 passed in 2.79s. The console-overflow probe emitted enough raw newlines
to hit the raw-byte budget first; its input was reduced to isolate console
expansion. No production budget was changed. Subsequent focused result:
**14 passed in 2.84s**. Actual parser boundary subset: **7 passed / 20 deselected
in 0.08s**. Compact full collection: **1596 tests**, 1074 raw bytes, exit 0,
complete capture/confirmed cleanup; maximum audited node ID 177 UTF-8 bytes.

The first external full-suite command ran from an empty work directory and
collected no tests: exit 5, 0.01s, no coverage; the controller correctly preserved
that failure. The corrected command runs from the external suite root. The first
sandboxed fresh-build attempt could not reach PyPI for isolated build setup; it
produced no artifact. Separately authorized setup network access was then used.
No application runtime network or external sf/Obsidian process was allowed.

### Corrected local validation and handoff

Local native **macOS 27.0.1 (26A434), ARM64, APFS, Python 3.14.7** used the
previously verified installed application and a fresh external public synthetic
suite copy. Both application and fixtures stayed under quiescent ancestry; all
TMPDIR/TEMP/TMP variables selected a dedicated root. Poetry 2.4.2, pytest 9.1.1,
pytest-cov 7.1.0 and coverage 7.17.0; runtime versions match the earlier record.
The complete corrected suite through the actual CI supervisor exited 0:
**1593 passed / 3 skipped in 222.26s**, **92% combined statement/branch coverage**
(4693 statements, 2070 branches). Capture was complete, cleanup confirmed,
**8730 raw bytes / 9393 console bytes**, longest raw line **754 bytes**. This
exercises the controller with real coverage output as well as synthetic failures.
Skips remain case/NFC filesystem representation and unavailable native Windows
junction execution; no skip is qualification. Python 3.12.7 and 3.13.15 focused
new regressions each passed **14 tests**, 3.28s and 3.29s respectively; full suites
were not repeated on those interpreters for this test/CI-only correction.

Strict Poetry metadata/lock, Ruff lint/format (113 Python files), Bandit (zero
findings, five existing suppressions), whitespace, fresh build and strict Twine
passed. Both fresh Python 3.14.7 independent wheel/sdist installs passed exact
source/resource/license/metadata checks and all installed probes: both actual
console/module entry points; absolute/relative config paths with spaces;
malformed/oversized/unreadable inputs; bounded private output; init/build/sync/
recover; finite bounds and 12-note lifecycle; lower-level safety; active runtime
network/process guards; no application cwd artifacts. Setup downloads remained
separate. Archive membership stayed exactly **36 wheel / 35 sdist**, no new asset.

| Fresh artifact | SHA-256 |
| --- | --- |
| Wheel | `557e527155b649c93840260f9fb0b8c451c31a3d6b8484cd263be80d6dcd08cf` |
| Sdist | `acc1ac95d2f2b156a49dd7d43ad9fedae26d066b61c0776f07b8971876589a65` |

Workflow structure retains 12 cells and verifies the intended limits; five
changed Markdown files initially checked 98 local links/anchors with no errors.
Final readback/whitespace/privacy/status review follows. The original large
failure log and bounded local diagnostic logs stay private and outside artifacts.
No accepted failure/skip/unavailable observation is removed or explained by later
success: `40427329142`, `40235515146`, template-refresh conflict 3 and Thread 12's
uncaptured 2-failed/1371-passed/2-skipped causes all remain.

Correction is **locally verified, unstaged/uncommitted**, at maintainer HEAD
`f252844` on existing `fix/15-thread-15-fix-and-prevent-windows-ci-run-crash`.
No branch creation, stage/commit/push/PR/merge, CI cancellation/rerun, issue closure
or publication by this session. #15 remains open pending separately authorized
corrected delivery/exact-commit hosted matrix and maintainer acceptance. Native
Windows corrected execution/cleanup, Python 3.15 local execution, native ACL/sf,
Obsidian preview, power-loss and hostile-race evidence remain unavailable.
Threads 16–17 and enhancements #18/#19 remain **NOT STARTED**.


Final correction tracking receipt: [public-safe handoff](https://github.com/jeffshurtliff/obforce/issues/15#issuecomment-6455944150)
and #15 body/checklist are synchronized. Readback retains OPEN, the five original
labels, maintainer assignee, milestone 1 and native closed #14 → open #15 → open
#16 links. Corrected hosted matrix and maintainer acceptance stay unchecked.

Final correction review: five changed Markdown files, 99 local links/anchors,
zero missing targets; metadata/lock, Ruff lint/format and whitespace rechecked.
All 11 changed/new files remain unstaged/uncommitted; no staged or unrelated file.


## Bounded timeout review and approved runtime correction — 28 October 2026

### Acceptance decision and exact hosted evidence

Thread 15 is **not ready for acceptance**. Read all 12 complete command logs and
step conclusions in [40603283983, attempt 1](https://github.com/jeffshurtliff/obforce/actions/runs/40603283983),
exact merge `08f67b6a0ca62fdd8d38afb541e6ae17e6eba7a0`, implementation `9ca7450`.
Ten cells passed metadata/lock, Ruff lint/format, Bandit, full pytest coverage,
fresh build, strict Twine, exact 36/35 archives, both independent installs and
whitespace: **20 independent installs**. Their actual setup interpreters follow.
These establish their own results, not the two incomplete cells or later code.

| Hosted cell / actual Python | Job | pytest result | Seconds |
| --- | --- | --- | ---: |
| Linux 3.12.15 | 122536447734 | 1595 passed, 1 skipped | 1823.61 |
| Linux 3.13.16 | 122536447333 | 1595 passed, 1 skipped | 1834.78 |
| Linux 3.14.8 | 122536447692 | 1595 passed, 1 skipped | 339.34 |
| Linux 3.15.2 | 122536447612 | 1595 passed, 1 skipped | 556.94 |
| macOS 3.12.10 | 122536447774 | 1593 passed, 3 skipped | 1091.74 |
| macOS 3.13.16 | 122536447765 | 1593 passed, 3 skipped | 1045.00 |
| macOS 3.14.8 | 122536447728 | 1593 passed, 3 skipped | 461.42 |
| macOS 3.15.2 | 122536447641 | 1593 passed, 3 skipped | 455.50 |
| Windows 3.14.9 | 122536447769 | 1574 passed, 22 skipped | 1983.74 |
| Windows 3.15.1 | 122536447682 | 1574 passed, 22 skipped | 1863.31 |
| Windows 3.12.10 | 122536447622 | Incomplete: wall_time_limit | 2700 budget |
| Windows 3.13.16 | 122536447788 | Incomplete: wall_time_limit | 2700 budget |

Both incomplete jobs passed collection and all preceding gates, then reported
`exit=1; captured_bytes=1713; capture_complete=false; cleanup_confirmed=true`.
Build/Twine/archive/install/whitespace gates skipped. No completed pytest count
or coverage is inferred from 94%. Linux/macOS successful coverage was 92%; the
two successful Windows cells measured 91%. Windows skips include existing POSIX
collector/FIFO/symlink/mode-denial and filename fixture limits; skips do not
qualify Windows sf, ACLs or unsupported native operations. The native junction
case was not skipped in those successful Windows cells. No filesystem name is
inferred from runner labels. The oversized-ID error did not recur in these logs;
bounded output/deadline/cleanup safeguards behaved as designed.

The [acceptance blocker receipt](https://github.com/jeffshurtliff/obforce/issues/15#issuecomment-6470765238)
and [#21 narrow profiling start](https://github.com/jeffshurtliff/obforce/issues/21#issuecomment-6470765626)
retain this decision. #21 is an existing follow-up, not a new native prerequisite,
acceptance gate, duplicate issue or milestone. The maintainer explicitly approved
the focused immutable batch path optimization on 28 October; broader acquisition,
adjacency indexing, early refusal and test-harness changes remain proposals.

### Implemented scope and preservation

- Bounded per-case pytest output and `--durations=25` identify slow completed
  setup/call/teardown phases. A bounded unfinished child line is emitted on
  deadline without implying a completed result or exact internal phase.
- A private renderer batch snapshots caller paths into an immutable mapping.
  Renderer and graph checked views are lazy at their original call sites,
  preserving error precedence. Graph fingerprinting selects relevant locations
  directly instead of rescanning every location after validation.
- Each planning/replanning pass and each independent evidence validation creates
  fresh snapshots. No global cache, filesystem-observation cache, reuse of old
  authorization, skipped guard or weakened independent integrity check.
- Ordinary standalone mapping inputs still validate fully. New regressions check
  exact candidate equality/bytes/hashes, caller mutation isolation, invalid
  unrelated paths, case/namespace/parent/reserved collisions, workspace/key
  mismatches, combined error precedence, and fresh moved-note evidence checks.
- All schemas/renderer/config versions, 128-file publication ceiling, complete
  1000-class fixtures, original preview and actual refusal, public commands,
  source/org/scope/identity/coverage/human-content and transaction/recovery
  contracts remain unchanged. No new dependency or packaged file. No earlier
  refusal, batch splitting, deadline increase, matrix reduction or automatic retry.

### Profiling evidence and retained local failures

The [public-safe profile summary](evidence/thread15-path-profile-20261028.json)
records a synthetic offline 1000-class, zero-edge publication refusal workload,
including preview and actual build; it is distinct from the 10000-edge benchmark.
Raw pstats/logs remain private because they contain local source paths.

The baseline Python 3.12.7 cProfile/coverage attempt was deliberately interrupted:
pytest **1 failed / KeyboardInterrupt, 597.33s**; its first interruption aborted
an in-progress build and a second interrupted coverage collection. No complete
baseline pass or coverage is claimed. The stdlib `cProfile -m` CLI consumed
pytest's SystemExit and returned outer 0; that outer status is not a test pass.
The post-change harness explicitly propagates `pytest.main`'s status and uses a
600-second child deadline, separate coverage/fixture roots and bounded capture.
It completed **1 passed in 78.90s**, test call 78.06s, full capture/cleanup.

| Instrumented function work | Interrupted baseline | Complete optimized workload |
| --- | ---: | ---: |
| Rendered candidates | 1872 | 2000 |
| `relative_path` calls | 4773121 | 44033 |
| Renderer `_paths` dispatch calls | 1881 (full validations) | 2014 (mostly cached dispatch) |
| Graph fingerprint calls | 2871 | 4000 |
| Graph complete-map validator calls | Previously inline | 4 fresh batch/boundary validations |

The incomplete baseline accumulated 1,963,370,495 profiled calls versus
246,369,792 in the complete optimized workload. Baseline renderer path validation
had 294.575425 cumulative seconds; optimized dispatch 2.077446s. Cumulative times
overlap and are not additive or CPU measurements. Instrumentation and concurrent
host load affect elapsed times. No timing ratio, throughput promise, complete
before/after baseline, or exact native Windows timeout cause is inferred.

Additional exploratory observations remain explicit:

- The repository Brain brief could not open its lock in the sandbox; recall
  returned with degraded vitality recording. Code/impact retrieval succeeded but
  correctly identified a committed-tree index; current source/tests govern.
- The initial scoped native process lookup was unavailable in the sandbox; a
  privileged lookup identified only the synthetic profiler for interruption.
  A later guarded stop found it already exited and sent no kill signal.
- One new diagnostic command used a relative log path and was refused with exit
  2 before pytest; its output remains. A subsequent absolute-path run passed.
- The initial profile and exploratory full suite shared default `.coverage`.
  The exploratory full suite passed 1594/3 in 220.77s, but its coverage is not
  accepted because isolation was incomplete. The clean repeat used explicit
  `COVERAGE_FILE`: **1594/3, 222.32s, 92%**, complete raw 181205 bytes. Its
  unchanged 1000-class test call was 85.71s. Optimized 3.14 call: 14.86s; these
  individual observations have differing host load, not a service guarantee.
- Focused new diagnostic tests: **15 passed, 3.96s**. Initial new batch tests
  failed **5/1 in 0.19s**, stopping at maxfail 5 because a test used `name` instead
  of `full_name`; the fixture was corrected. No production behavior changed for
  that test error. Final renderer/graph/planner/state subset: **457/2, 5.46s**.
- A parallel Python 3.13 independent-artifact attempt returned recovery_required
  during the transaction probe. Installer ancestry was shared and mutable;
  the precise failed stamp was not captured. Do not assign it an inferred cause.
  The failed log is retained. Separate stable installer parents were prepared
  before new independent wheel/sdist checks on both 3.12 and 3.13. The original
  parallel 3.12 check passed but also used that shared parent; it remains
  exploratory and is excluded from the final isolated six-install selection.
  No guard or retry mechanism changed; both earlier outcomes remain separate evidence.

### Final installed-candidate local validation

Native local environment remains macOS 27.0.1 (26A434), ARM64, observed APFS;
Poetry 2.4.2, pytest 9.1.1, pytest-cov 7.1.0 and coverage 7.17.0. Runtime versions
remain Click 8.5.0, Jinja2 3.1.6, MarkupSafe 3.0.4, ruamel.yaml 0.19.1 and
defusedxml 0.7.1. Candidate wheels were installed without dependency changes in
existing external test environments; tests/application/fixtures were outside the
checkout under stable ancestry with separate coverage databases and all three
temp variables set. Application runtime network/process guards remained active.

| Actual local Python | Full suite | Seconds | Statement/branch coverage | 1000-class call |
| --- | --- | ---: | ---: | ---: |
| 3.12.7 | 1605 passed, 3 skipped | 416.08 | 92% | 40.61s |
| 3.13.15 | 1605 passed, 3 skipped | 382.80 | 92% | 39.31s |
| 3.14.7 | 1605 passed, 3 skipped | 179.44 | 92% | 14.86s |

All three supervisor commands exited 0 with complete capture and confirmed
cleanup; 4737 statements, 2074 branches. Raw captures respectively
182858/182591/182816 bytes, console 198130/197845/198088; longest raw line 754
bytes. Three skips per run retain case/NFC filesystem representation and locally
unavailable native Windows junction execution. No skip is qualification.

Strict metadata/lock, Ruff lint/format, Bandit (zero findings, five existing
suppressions), whitespace, fresh build and strict Twine passed. Exact unchanged
**36-wheel / 35-sdist** source/resource/license/metadata allowlists and **six
fresh independent installs** passed across 3.12.7/3.13.15/3.14.7, including actual
console/module entry points, relative/absolute space paths, bounded/private
invalid and unreadable inputs, installed assets, init/build/sync/recover,
within-bound lifecycle, over-bound write-free refusal, lower-level guards and no
application cwd artifacts. Setup downloads remain separate from runtime.

Wheel SHA-256 `fdb408f81f56796093d369ebb42efecec421188e6f1633cc40c1b32461aeddda`;
sdist `78bdb0cf85470a90324e5614522bba0ad8694030a76afcdcdb169956c57859a8`.

### Complete repeated synthetic scale observation

The [complete repeated 16-record JSON](evidence/thread15-scale-macos-py314-20261028.jsonl)
retains the same seed 15, 1000 classes/10000 explicit directed edges and all seven
stages, native Python 3.14.7/environment versions and active runtime audit guards.
The developer-only controller bounded this measurement to 900 seconds without
changing any application or CI limit. It exited 0, full 2976-byte raw capture,
confirmed cleanup. The direct rendering phase retains ordinary mapping inputs;
it still performs full per-call validation and is not a batch-cache speed test.

| Stage | Seconds | Peak traced Python allocation bytes |
| --- | ---: | ---: |
| Offline collection/normalization | 1.932047 | 8014708 |
| Mocked live collection/normalization | 0.288214 | 3918789 |
| Explicit graph | 1.637072 | 8434046 |
| All candidate rendering | 153.065636 | 5605017 |
| Large persistent planning attempt | 48.836131 | 50159647 |
| Separate 32-class/320-edge planning | 1.369052 | 11913047 |
| Mocked fixed relationship budget | 0.070892 | 6513871 |

All 1000 candidates still produce **6855000 bytes**, exact unchanged SHA-256
`5d6f8dcca8e105a43ff3a32fae1adf48b44eb380d181af8b94c90d2e4768a7a5`.
The large plan still refuses ConflictError/state structural bound, outcome 3,
without creating the vault. Separate valid planning remains **34 changed files /
506545 state bytes**; public lifecycle fixtures still validate whole-batch
127/1000-note refusals and a separate 12-note publication. No split batches.
Inventory/audit calls remain identity 1/inventory 6/audit 5; relationship calls
remain 101, zero returned edges and partial coverage. No new acquisition form.

Maximum **traced Python allocation** peak 50159647 bytes is not RSS. The separate
whole-process `resource.ru_maxrss` high-water is **137265152 bytes on macOS**,
including setup/tracing; no per-stage RSS is claimed. Prior JSON/results/failures
remain intact. Host load and tracing preclude throughput/service-level promises.

### Current review and next step

All approved local changes remain unstaged/uncommitted on existing `main` at
maintainer HEAD `639a53823c23d9a709b578111e6e685fa927cc97`; no branch, commit,
push, PR, merge, CI rerun/cancellation, issue closure or publication by this
session. Maintainer Entire/ignore/instruction changes are preserved. The scoped
#21 work is in progress, not accepted or a new prerequisite/milestone.

**Pending:** separately authorized delivery and exact-commit verification of all
claimed hosted cells, especially Windows 3.12/3.13, including their downstream
package/install gates, then maintainer acceptance. The precise native timeout
hotspot remains unmeasured until per-case/duration evidence is delivered there.
No new native Windows/Linux/Python 3.15 result for this uncommitted runtime change,
Windows sf/ACL/power-loss/hostile-race/native Obsidian or new filesystem claim.
Every historical failure/skip/unavailable and uncaptured cause remains, including
40575562800, 40427329142, 40235515146, original template conflict 3 and Thread 12's
2-failed/1371-passed/2-skipped. Later passes do not explain those failures.
**#15 remains OPEN. Thread 16 is next only after acceptance, NOT STARTED.**
Thread 17 and enhancements #18/#19 remain **NOT STARTED**.


Tracking receipt: [#15 runtime handoff](https://github.com/jeffshurtliff/obforce/issues/15#issuecomment-6471628796)
and [#21 scoped handoff](https://github.com/jeffshurtliff/obforce/issues/21#issuecomment-6471629396)
are posted. The bodies/checklists preserve OPEN status, original labels, #15
assignee/milestone 1, and #21's unassigned/no-milestone state. Native closed #14
→ open #15 → open #16 remains; #21 has no native blocked-by/blocking edges.
Corrected hosted verification and maintainer acceptance remain unchecked.


Final review receipt: six selected fresh independent installs are confirmed under
quiescent installer ancestry (dedicated 3.12/3.13 repeats; earlier separate 3.14
checks). Exploratory parallel outcomes remain excluded/separate. Six changed
Markdown files / 131 local links and anchors / zero missing targets; both new
public evidence files parse completely and contain no identifying local paths.
Metadata/lock, Ruff lint/format and whitespace rechecked; all 16 changed/new files
remain unstaged/uncommitted, with no unrelated or staged file.

## Final accepted hosted qualification — 28 October 2026

The maintainer reviewed/pushed the candidate and explicitly requested closure if
all required gates passed. Verified implementation
`3771c16f133703bd76615d1af383e88d7d8dbf08`, merge
`178bf98a53f910364eb0985d201a372f3fe8cd7e`, and
[40721222520, **attempt 2**](https://github.com/jeffshurtliff/obforce/actions/runs/40721222520/attempts/2).
The implementation and merge trees match; the initial checkout was clean at that
merge. Every attempt-2 job command log, exact checkout SHA, required standalone
command and step conclusion was read. **All twelve cells and twenty-four
independent wheel/sdist installs passed.** No formatter/security/package gate was
masked or skipped.

| Hosted cell | Actual setup Python | Job | pytest |
| --- | --- | --- | --- |
| macos-latest / 3.12 | 3.12.10 | [123020849907](https://github.com/jeffshurtliff/obforce/actions/runs/40721222520/job/123020849907) | 1605 passed, 3 skipped in 517.26s |
| macos-latest / 3.13 | 3.13.16 | [123020929007](https://github.com/jeffshurtliff/obforce/actions/runs/40721222520/job/123020929007) | 1605 passed, 3 skipped in 534.17s |
| macos-latest / 3.14 | 3.14.9 | [123020913589](https://github.com/jeffshurtliff/obforce/actions/runs/40721222520/job/123020913589) | 1605 passed, 3 skipped in 228.80s |
| macos-latest / 3.15 | 3.15.2 | [123020848348](https://github.com/jeffshurtliff/obforce/actions/runs/40721222520/job/123020848348) | 1605 passed, 3 skipped in 337.57s |
| ubuntu-latest / 3.12 | 3.12.15 | [123020930144](https://github.com/jeffshurtliff/obforce/actions/runs/40721222520/job/123020930144) | 1607 passed, 1 skipped in 901.53s |
| ubuntu-latest / 3.13 | 3.13.16 | [123020901931](https://github.com/jeffshurtliff/obforce/actions/runs/40721222520/job/123020901931) | 1607 passed, 1 skipped in 778.09s |
| ubuntu-latest / 3.14 | 3.14.9 | [123020911656](https://github.com/jeffshurtliff/obforce/actions/runs/40721222520/job/123020911656) | 1607 passed, 1 skipped in 385.00s |
| ubuntu-latest / 3.15 | 3.15.1 | [123020848663](https://github.com/jeffshurtliff/obforce/actions/runs/40721222520/job/123020848663) | 1607 passed, 1 skipped in 206.61s |
| windows-latest / 3.12 | 3.12.10 | [123020901226](https://github.com/jeffshurtliff/obforce/actions/runs/40721222520/job/123020901226) | 1586 passed, 22 skipped in 2389.33s |
| windows-latest / 3.13 | 3.13.16 | [123020850801](https://github.com/jeffshurtliff/obforce/actions/runs/40721222520/job/123020850801) | 1586 passed, 22 skipped in 2261.48s |
| windows-latest / 3.14 | 3.14.9 | [123020850651](https://github.com/jeffshurtliff/obforce/actions/runs/40721222520/job/123020850651) | 1586 passed, 22 skipped in 1561.83s |
| windows-latest / 3.15 | 3.15.1 | [123020851078](https://github.com/jeffshurtliff/obforce/actions/runs/40721222520/job/123020851078) | 1586 passed, 22 skipped in 1689.65s |

Every cell passed strict Poetry metadata/lock, Ruff lint/format (115 Python
files), Bandit (no issues; five existing narrow suppressions), bounded collection,
full pytest with branch/subprocess coverage, fresh build, strict Twine for both
artifacts, exact **36-wheel/35-sdist** source/resource/license/required-metadata
checks, both independent installed probes and whitespace. Linux/macOS measured
92% combined statement/branch coverage; Windows 91% (4737 statements,
2074 branches). Both collection/suite captures were complete, exit 0 and cleanup
confirmed. Suite raw captures span 179714–182951 bytes under the unchanged 2 MiB
and 4096-byte line ceilings. The 2700-second test deadline, outer deadlines,
fail-fast and concurrency protections were retained.

The [structured job/gate/hash manifest](evidence/thread15-ci-40721222520-attempt2.json)
records all twelve source/command checks and actual per-cell artifact hashes.
Hashes differ by cell; exact package content/metadata/install checks passed,
without a reproducible-build cause or guarantee being inferred. Independent
installs exercised actual console/module entry points, relative/absolute paths
with spaces, installed assets, privacy/bounds, init/build/sync/recover,
within-bound lifecycle and lower-level preservation/recovery under runtime
network/process guards and without application cwd artifacts. Setup downloads
remain separate from application runtime.

**Attempt 1 remains separate failed/unavailable evidence.** Its run conclusion
is failure; job metadata reports eleven successful jobs and cancelled macOS
3.15 job `122932342732`, runner_id 0, no steps. Check annotations state that no
hosted runner acquired the job and identify macOS ARM64 capacity constraints.
The command log returns 404 BlobNotFound; no application execution or test pass
is inferred for that job. The agent did not cancel or rerun either attempt.

Prior `40603283983` Windows 3.12/3.13 2700-second incomplete captures remain,
as do `40575562800`'s two completed Windows oversized-ID failures and cancelled
cells. The latter run's current overall conclusion is cancelled; that does not
erase its captured per-cell failures. Cancelled `40597252222` and `40697576055`
are retained without new application qualification. `40427329142`,
`40235515146`, every older failed/skipped/unavailable observation, the original
template-refresh conflict 3 and Thread 12's uncaptured
2-failed/1371-passed/2-skipped causes remain. Later passes do not identify those
causes or the precise older Windows timeout case.

**Evidence boundaries:** Linux's one skip is unavailable native Windows
junction execution. macOS's three retain case/NFC fixture representation and
junction limits. Windows's twenty-two retain POSIX collector/FIFO/symlink/mode
and filename fixture gaps; the native junction refusal case passed there.
Skips are not qualification. Existing mocked descriptor/reparse/permission
checks remain mocked; native Windows ACL/sf, power-loss, hostile races, atomic
snapshots/multi-file publication and native Obsidian preview are not established.
Only the locally observed APFS is named as filesystem evidence; runner labels
do not prove hosted filesystem types. Windows sf remains refused, and optional
Obsidian preview remains unavailable. New Windows duration observations
(1000-class case: 105.04/97.89/22.36/34.66s on 3.12/3.13/3.14/3.15) are measured
case times, not the cause of an earlier incomplete run or a throughput promise.

**Acceptance:** all requested Thread 15 scope/gates are met with unsupported and
unperformed paths explicitly gated/documented. **#15 is accepted, complete and
closed as completed under the maintainer's conditional authorization.** The
approved #21 immutable path scope is delivered and verified; broader optional
profiling/acquisition/adjacency/early-refusal proposals remain open and
unscheduled, outside the prerequisite graph. No extra #21 implementation or
closure was authorized here.

**Handoff:** Thread 16 is next eligible, explicitly **NOT STARTED**. The
[exact kickoff prompt](THREAD_16_KICKOFF.md) captures accepted source/run evidence,
scope, privacy/preservation contracts, clean-install tutorial verification and
delivery limits. Thread 17 and enhancements #18/#19 remain **NOT STARTED**.
Preparing this prompt and updating #16 eligibility do not start documentation
implementation or release preparation.

This acceptance pass changes documentation/evidence only. Local verification
covers links/anchors, evidence JSON, privacy/consistency, whitespace and Git
review; no application test/build/install or dependency setup was repeated for
prose. Acceptance documentation remains unstaged/uncommitted on existing
`main` at `178bf98`; source delivery was performed by the maintainer, not this
session. No branch/stage/commit/push/PR/merge/CI rerun/publication, real sf/Obsidian/
auth/org/vault/settings access, platform/policy change or delegation.


Acceptance tracking receipt: [#15 acceptance and closure](https://github.com/jeffshurtliff/obforce/issues/15#issuecomment-6478886856)
and [#21 delivered-scope update](https://github.com/jeffshurtliff/obforce/issues/21#issuecomment-6478887268)
are posted. #15 readback is CLOSED/completed; #16 and #21 remain OPEN. #15/#16
labels, maintainer assignees and milestone 1 are unchanged; #21 remains unassigned
with its original labels/no milestone. Native #14 → #15 → #16 → #17 links are
retained, with #15 now closed; #21 has no native prerequisites/dependents.
Thread 16 remains NOT STARTED; its implementation checklist is unchanged.

Final acceptance review: 10 Markdown files / 188 local links and anchors / zero
errors; complete 12-job evidence JSON, privacy/new-file formatting and whitespace
passed. All 11 changed/new acceptance files remain unstaged/uncommitted; no staged
or unrelated file and no source/test/lock/workflow change in this acceptance pass.
