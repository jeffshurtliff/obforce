# Internal state, reconciliation and read-only planning

## Pre-implementation contract — 20 October 2026

This internal increment accepts explicit caller-supplied vault/state paths and
normalized binding/selection inputs. It never discovers cwd/home/auth/config,
invokes source transports, adopts notes, or writes state. Public commands,
batch planning/reporting, publication, locks, journals and recovery remain later
threads. Only synthetic vaults are authorized for validation.

The accepted immutable `NoteState`, SHA-256 and source/graph/render/creation hash
contracts remain unchanged. `SavedNote` pairs a NoteState with immutable exact
saved marker-interior bytes. These bytes come from the prior accepted candidate
or patch, never from the current note to reconstruct ownership. They include
original LF/CRLF bytes. Compare both strict generated-property values and exact
region bytes before accepting a discovered note; verify the saved bytes against
the saved exact-byte SHA-256 too. Hashes are integrity aids, not authentication.
Never save user prose or user-owned properties as generated baselines. Creation
fingerprints remain creation-only and are not persisted as render hashes.

## Version-one private wire document

UTF-8 JSON without BOM, duplicate keys, nonfinite/floating numbers or coercion.
Every object has an exact key set; unknown versions/keys/types refuse. Serialization
uses existing compact canonical JSON (sorted object keys, literal Unicode), notes
sorted by canonical component key, canonical sorted selection/warnings, and one
terminal LF. Arrays of field strings retain order. No timestamps, host paths,
aliases, credentials, raw source/transport records or human regions are persisted.

Root keys: `state_schema` (integer 1), `binding`, `selection`, `scope_hash`,
`coverage`, `notes`. Binding is exactly workspace_id/mode/org_id; local requires
null org, live requires a canonical checksum-valid Organization ID independently
verified by the caller (a stored ID alone is not verification). Selection has
`types: ["ApexClass"]`, boolean include_namespaced, and unique full_names.
Scope hash is the unchanged Selection.scope_hash(binding), independently of
collection outcomes. Coverage uses the accepted Coverage.canonical() shape with
its own matching binding/selection/model_schema and three independent dimensions.
Offline audit remains unavailable/unrequested and relationships not collected/unrequested.

Each notes entry has exactly `note` (the unchanged NoteState.canonical() shape)
and `generated_region` (canonical padded ASCII base64 of exact saved bytes).
Each baseline value has exactly availability/value; absent keys remain absent,
null/false/zero/empty string/empty list/unavailable remain distinct. Only reserved
properties can appear. Required identity/source/lifecycle/coverage baseline fields
must match the supported UUID/schema/key/binding and valid enum values. Namespace
must be explicit null or exact text; no empty-to-null normalization on wire.
All note bindings and keys must match the envelope scope. Unsupported keys,
contradictory identities/baselines/scopes, invalid UUID/digests, duplicate IDs,
component mappings or portable paths refuse. No repair, migration or fallback.

## Discovery and reconciliation

The explicit existing absolute vault is the discovery root. The explicit expected
state path must be exactly vault/.obforce/state.json; only this document is read
separately. Exclude `.git`, `.obsidian`, `.obforce` directory segments under NFC
plus casefold; their contents are opaque. Validate boundary entries but do not
traverse them. Other directories are scanned completely; ordinary non-Markdown
files are stat-checked but not read. Markdown suffix matching is case-insensitive.
Read all Markdown within finite bounds. Conservative managed indicators are
case-insensitive `obforce` or any `sf_` occurrence in raw Markdown, including
malformed identity/marker/frontmatter content. Indicators require successful
Thread 08 parsing and exact tracked identity/baselines; false positives refuse
for review instead of silently ignoring a potentially damaged managed note.
Ordinary notes without indicators stay unadopted, untouched and unrecorded.

Missing state is allowed only with explicit `initial=True`, no managed indicators,
and no supplied existing document. This means an empty **managed** initial scope;
unrelated files may exist but none is adopted. Empty bytes are corrupt, not an
empty document. A valid empty notes array similarly cannot coexist with managed
notes. Missing/corrupt/unknown state never reconstructs ownership.

Reconcile only a unique canonical UUID with its exact validated source key/schema.
A unique in-vault move changes only candidate NoteState.path; UUID/key/content,
all baselines and prior hashes remain unchanged. Return immutable deterministic
paths and explicit old/new path changes for later incoming/outgoing graph/render
invalidation; do not calculate a batch plan or rehash/rewrite notes. Duplicate or
copied IDs, multiple notes per component, identity edits, vanished tracked notes,
untracked managed notes, old-path unowned collisions and ambiguous paths refuse.
No filename/text/record-ID rename inference or outside-vault search.

Caller binding and selection must exactly match saved evidence; changed scope or
workspace/local/live/org rebinding refuses. Collection outcomes can differ from
scope. No source inventory absence is evaluated here: a vanished note is a
conflict, whereas a component absent from offline/partial/unavailable/changed
source input establishes no deletion. Never delete, mark missing or refresh
relationships. Stale evidence and independent coverage remain intact.

## Read assumptions and refusal limits

Reject traversal/escape, nonabsolute roots, source/template/repository overlap
against explicit caller-supplied excluded roots, unsafe symlink/junction/reparse
ancestors/entries, special files and multiply linked regular files. Reject
portable case/NFC spelling collisions, reserved names and file/parent collisions,
including unrelated entries in the scanned tree. Managed paths also retain
Thread 07's stricter wikilink-safe .md policy. Excluded roots are explicit; callers
must supply every source/template/application root, not infer them from cwd.

Reads use lstat plus descriptor identity/size/mtime/ctime/link/mode checks,
no-follow/nonblocking flags where available, bounded reads, parent snapshots and
final whole-scan rechecks. Cross-API Windows pathname/descriptor comparisons use
explicit integer `st_birthtime_ns` for creation time alongside device/inode,
mode/link-count/size/mtime; unavailable birthtime refuses. Windows `st_ctime_ns`
can mean creation for lstat and metadata change for fstat, so those two values
are not compared to each other. Full ctime remains in repeated path observations
and descriptor-before/after checks; descriptor birthtime and safety are rechecked
after reading too. POSIX retains its full ctime comparison. See the official
[Python stat timestamp contract](https://docs.python.org/3.12/library/os.html#os.stat_result.st_birthtime_ns),
[CPython 3.14.7 pathname compatibility code](https://github.com/python/cpython/blob/v3.14.7/Modules/posixmodule.c#L2152-L2154),
[descriptor timestamp source](https://github.com/python/cpython/blob/v3.14.7/Python/fileutils.c#L1037-L1041)
and [upstream issue 157671](https://github.com/python/cpython/issues/157671).
Missing/changed files or parents, unreadable directories
and partial iteration refuse. Permission/I/O errors are redacted OperationalError
(1); unsafe/corrupt state, note/path/source conflicts are ConflictError (3);
invalid explicit caller inputs are ModelError (2). Existing exit precedence
3, 2, 1, 4, 0 remains unchanged. Display no raw JSON/YAML/content/path diagnostics.

| Refusal limit | Maximum |
| --- | --- |
| State input / serialized output | 16 MiB each |
| State JSON container depth / nodes | 16 / 250,000 |
| State text scalar / integer | 2 MiB UTF-8 / 64 magnitude bits |
| Saved notes / discovered entries | 10,000 / 50,000 |
| Discovery relative depth / path | 32 segments / 1,024 characters |
| Each portable segment | 240 UTF-8 bytes |
| Explicit absolute input path | 32,768 characters / 256 segments |
| Explicit excluded roots | 128 |
| Each Markdown read / saved region | 1 MiB / 512 KiB |
| Aggregate state plus Markdown reads | 64 MiB |
| Aggregate reconciliation result | bounded by state output plus scanned Markdown |

Thread 08's independent note/frontmatter/YAML token/node/depth/property/scalar/list
and encoding/ending limits still apply. Bounds refuse, never truncate. JSON depth
is checked lexically before decoding; node/text bounds checked before model
construction. All reads, serializations and success/no-op/failure paths create
no config/vault/state/lock/journal/log/cache/temp-publication artifacts.

These are finite read-side checks on a stable trusted local filesystem, not
hostile race isolation, an atomic snapshot, publication safety or portable access
control certification. Rechecks cannot exclude an attacker restoring observations,
ancestor swaps between checks, or changes after return. Atime updates can be an
OS read side effect; bytes, mtimes and tree structure must remain unchanged.
Network/cloud-synced/unusual filesystems and native Windows race behavior remain
unqualified. Synthetic reparse tests are not native Windows execution evidence.
Windows sf remains refused; requested platform relationships remain partial or
unavailable even when empty; offline relationships remain not collected. No new
dependencies are needed; use the standard library and accepted parser/models.

## Internal interfaces and evidence boundary

`parse_state(bytes)` validates wire data; `serialize_state(StateDocument)` returns
bytes without writing. `load_state(Path)` reads only an explicitly supplied
document and returns None only when absent. Reconciliation uses one shared read
observation set for state plus the vault, so state/parent changes detected during
note discovery refuse. `reconcile_vault(vault, state_path, binding, selection,
excluded_roots=..., initial=False)` returns candidate state, immutable component
paths, ordered PathChange(key, old_path, new_path), and in-memory parsed current
observations. The latter may contain private user content; they are never logged
or serialized into state. All private result reprs omit content.

No source inventory is accepted or evaluated here. Saved independent coverage is
retained, not replaced with a current collection outcome; selection equality alone
is no absence certificate. A note's previously rendered collection baseline is
not silently updated from another result. Unique case-only moves are allowed
when the one observed note is the sole occupant of its portable path. All other
occupied old paths remain conflicts. Conservative indicators may flag ordinary
notes that discuss Obforce or use sf_ text; refusal is intentional and no file is
adopted. Lowercase .md remains required for managed link paths, even though all
case variants of the extension are scanned for damaged managed indicators.

Fresh independent wheel/sdist probes exercise installed parser round trips, exact
LF/CRLF saved bytes feeding patch_note, loading, no-op/move candidates, edited and
duplicate identity refusal, malicious JSON/path refusal and exact bytes/mtimes/tree
preservation, including rewritten-state and renamed/rewritten-note timestamps.
Synthetic Windows cross-API stamp regressions also run from each install.
Synthetic vault setup writes are outside the checkout/cwd and precede
read snapshots. Runtime socket/process audit guards stay active. Setup/build/pip
downloads are separate network use. Actual results and native/hosted gaps are in
the [roadmap handoff](../dev/IMPLEMENTATION_PLAN.md#thread-09-handoff--20-october-2026).
Thread 09 is accepted, including delivered Windows correction `890ced2` / merge
`dff34a7`; #9 is closed. Thread 10 now supplies internal read-only planning/reporting; #10 is open pending
maintainer acceptance. Threads 11–17 and enhancement #18 remain NOT STARTED.
No release/publication or Windows sf qualification is implied.


## Thread 09 accepted delivery — 20 October 2026

The maintainer reviewed/pushed the implementation and Windows correction, confirmed
passing CI and authorized closure if complete. Correction
`890ced229722318764d87d8b525a932c72addfc7` was merged at
`dff34a7eb806622331e4770de38cbf0e470d322a`. Implementation/merge trees match; all
24 reviewed package source/resource files match the delivered checkout. #9 is
accepted and closed as completed.

Every job, required step and full command log in
[run 39502679337, attempt 1](https://github.com/jeffshurtliff/obforce/actions/runs/39502679337)
was verified at that merge. All 12 Python 3.12–3.15 cells passed:

| Host | Suite outcome per cell |
| --- | --- |
| Linux | 935 passed, no skips |
| macOS | 933 passed, 2 skipped |
| Windows | 920 passed, 15 skipped |

Every cell passed strict metadata/lock, Ruff lint/format, Bandit, fresh wheel/sdist
build, strict Twine, exact 29-wheel/28-sdist archive/license/source/resource/README/
metadata inspection, both independent installs and whitespace. All 24 installed
probes verified parser/state/patch/reconciliation, LF/CRLF, rewritten/renamed input
reads, timestamp semantics and byte/mtime/tree preservation with runtime socket/
process guards active and no cwd artifacts. Setup/download network use is separate.
No failed or skipped command is hidden by a green job summary.

The original [failed Windows run 39500770363](https://github.com/jeffshurtliff/obforce/actions/runs/39500770363)
and prior local setup/probe failures retain their outcomes. macOS's two native
case/NFC fixture skips and Windows's 15 recorded skips remain visible; quiet pytest
logs do not enumerate Windows per-test skip reasons. Native ordinary-file reads,
injected reparse/race tests and synthetic Salesforce process responses establish
only their tested boundaries. Windows sf stays refused; hostile race isolation,
public writes, locks/journals/recovery and live org behavior remain unqualified.
Platform relationships remain partial/unavailable even when empty; offline
relationships remain not collected. No new scope, dependency, state wire/hash
contract or public command is introduced by acceptance.

See the [roadmap acceptance record](../dev/IMPLEMENTATION_PLAN.md#thread-09-acceptance-and-closure--20-october-2026).
Thread 10 was subsequently authorized; its recorded contract and candidate work follow.

## Thread 10 pre-implementation planner contract — 20 October 2026

`plan_changes` accepts explicit absolute vault/state/excluded-root paths, an
immutable tuple of current normalized Components, independent Coverage, a current
DependencyGraph and optional matching prior graph, Layout/Options, already loaded
optional TemplateAssets, explicit initial intent and independently verified live
org ID. No config, cwd/home, auth or source discovery occurs. Existing notes also require
a matching previous graph whose per-note hashes match saved paths/state; graph
evidence cannot be reconstructed from hashes. `comparable_live_inventory=False`
is the default; a positive caller attestation of comparable accessible inventory
scope is additionally required for missing proposals, independently of collection
outcomes and the enforced binding/selection/method checks. Retained normalized
Components are required exactly for saved keys absent from current inventory;
each retained source hash must match saved state. State cannot reconstruct source
facts. All current and retained records must match binding and selection.

New identities use UUIDv5 with namespace `bdc896b6-c99e-571e-bf41-35e33fd18eab`
and canonical JSON of binding plus component key. This deterministic initial
policy uses no randomness, path, record ID, timestamp or collection ordering.
Existing UUIDs always win; uniqueness is checked across old and new candidates.
The UUID is an ownership identifier, not a secret or authenticity proof.

Immutable ChangeAction records carry kind, key/UUID/path, prior path, content and
state-change flags, candidate bytes and SavedNote. Actions sort by canonical key;
one primary action per component: create, move, missing, update, no_op, with that
priority when effects coexist. Move means an already observed unique in-vault
UUID move and candidate path reconciliation, never a rename operation. Missing
means a transition to missing after positively complete comparable supported live
inventory (`live-apex-keyset-v1`, exhausted, no limit); all other absences retain
prior lifecycle. No deletion exists. Changed-scope/binding inputs refuse before
absence evaluation. Each action has independent content/state flags; hash-only
invalidation may require state change without note-byte change. Existing notes
use only generated patches, even on creation-template changes. Both exact saved
properties and exact LF/CRLF region bytes gate every plan regardless of hashes.

ChangePlan carries ordered actions, refreshed immutable graph, candidate state
and serialized state bytes, state_changed, immutable read/publication preconditions,
independent coverage and a typed safe diagnostic/outcome. Planning stops at the
first invalid phase; conflict yields one global conflict action, invalid/read
failure yields none. Every blocked result discards all candidate bytes/state,
graph and preconditions, so it cannot authorize partial application. Counts are
primary-action counts only and sum to the action count, not effects or files.
Coverage incompleteness alone is outcome 4 and does not block a valid candidate;
existing precedence remains 3, 2, 1, 4, 0. Reports return strings/results internally;
there are no lifecycle CLI additions. Reports expose counts, fixed diagnostic
codes, facet status/request/warning counts and optional ordinal/UUID/action/flags.
They never expose content, source names, host/relative paths, raw warnings,
methods, audit identities, credentials or state documents. Private result reprs
omit content and paths. No automatic logging or external upload occurs.

Preconditions retain accepted lstat observations (device/inode/mode/link count,
size/mtime/ctime), exact content SHA-256 for reads, explicit missing paths, state,
note and directory/ancestor observations including excluded roots. The planner
extends the same observation set to proposed targets/parents and moved old paths,
validates existing/proposed portable spellings and file/parent occupancy together,
and rechecks the whole set after rendering and serialization. The accepted
Windows birthtime cross-API bridge and full same-API ctime checks remain intact.
A later writer must revalidate every observation/content digest and the complete
scope/binding/ownership contract under its own guard and recovery protocol.
These observations are not an atomic filesystem snapshot or write permission.

| Planner/report limit | Maximum |
| --- | --- |
| Current plus retained components / actions | 10,000 / 10,000 |
| Current/prior/refreshed graph | Existing 20,000 edges / 40,000 evidence observations each |
| Aggregate normalized source plus graph input | 16 MiB |
| Candidate note bytes plus state output | 64 MiB total; existing 1 MiB per note / 16 MiB state |
| Read/publication observations | 400,000 |
| Detailed report actions / report UTF-8 bytes | 1,000 / 256 KiB |

Existing strict state/discovery/parser/template/render/path bounds apply
independently. Limits refuse, never silently truncate. Caller models/inputs,
source files, vault bytes/mtimes/tree and state remain unchanged on success,
no-op, blocked and failure paths. Synthetic fixture setup may write before
snapshots; planning/reporting never create config/vault/state/lock/journal/log/
cache or temporary publication artifacts. No new dependency is needed.
Thread 11 and all later threads and enhancement #18 remain NOT STARTED.


## Thread 10 local candidate evidence

Local macOS/Python 3.14.7 verification passed 1,058 tests with two existing
case/NFC fixture skips (95% combined coverage), strict metadata/lock, Ruff,
Bandit, fresh builds, strict Twine, exact archive inspection and both independent
wheel/sdist installations. New installed probes compare fixed synthetic note/state
hashes and no-write preservation with runtime network/process guards active.
Thread 10 is locally implemented and #10 remains open pending maintainer
acceptance; delivery and exact-commit hosted/native platform evidence are pending.
Historical failed tests/setup/network attempts are retained in the
[Thread 10 handoff](../dev/IMPLEMENTATION_PLAN.md#thread-10-handoff--20-october-2026).
Thread 11 and later and enhancement #18 remain NOT STARTED.


## Thread 10 temporary-root CI correction

Implementation 11af258 was delivered at merge 725fe36. Exact-merge run
39507844963, attempt 1, passed 11 cells and failed macOS Python 3.12 during
initial synthetic baseline setup, before the requested late-state race. A local
instrumented reproduction identified unrelated shared system-temp ancestor
metadata changes; the hosted assertion did not preserve the specific observation.
CI now prepares a fresh root beneath runner.temp and exports TMPDIR/TEMP/TMP
before Poetry setup, so tests and independent artifact probes use quiescent
ancestry. A controlled regression proves shared-parent changes still block and
separate-root fixtures succeed. Production reader/planner and all Windows
cross-API/same-API and parent change checks are unchanged. No retry or skip is
added. The historical run remains failed; corrected hosted validation and #10
acceptance remain pending. See the [correction handoff](../dev/IMPLEMENTATION_PLAN.md#thread-10-macos-ci-correction-handoff--20-october-2026).
