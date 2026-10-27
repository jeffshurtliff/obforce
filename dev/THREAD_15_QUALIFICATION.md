# Thread 15 qualification record

Thread 15 / [#15](https://github.com/jeffshurtliff/obforce/issues/15) only, authorized
27 October 2026. Local candidate; maintainer acceptance and separately authorized
delivery/exact-commit hosted verification remain pending. Threads 16–17 and
enhancements #18/#19 are **NOT STARTED**. No release or platform provisioning.

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
