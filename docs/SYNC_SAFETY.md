# Internal state, reconciliation, planning and transactions

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
`dff34a7`; #9 is closed. Thread 10 internal read-only planning/reporting is accepted,
including correction
`a2132c3` / merge `6004c35`; #10 is closed. All 12 cells and 24 independent installs
passed in exact-merge run `39510802449`, attempt 1; see the
[acceptance record](../dev/IMPLEMENTATION_PLAN.md#thread-10-acceptance-and-closure--20-october-2026).
Thread 11 internal bounded transaction/recovery primitives are accepted, including
correction `4aaeb0f` / merge `2995f93`; #11 is closed. Final exact-merge run
`39676435834`, attempt 2, has all 12 cells and 24 independent installs passing;
see the [acceptance record](../dev/IMPLEMENTATION_PLAN.md#thread-11-acceptance-and-closure--21-october-2026) and
[transaction contract](SYNC_SAFETY.md#thread-11-pre-implementation-transaction-contract--20-october-2026).
Threads 12–17 and enhancement #18 remain NOT STARTED.
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
At that Thread 10 design checkpoint, Thread 11 and later and #18 were NOT STARTED;
the Thread 11 acceptance record below supersedes that historical status.


## Thread 10 historical local candidate evidence

Local macOS/Python 3.14.7 verification passed 1,058 tests with two existing
case/NFC fixture skips (95% combined coverage), strict metadata/lock, Ruff,
Bandit, fresh builds, strict Twine, exact archive inspection and both independent
wheel/sdist installations. New installed probes compare fixed synthetic note/state
hashes and no-write preservation with runtime network/process guards active.
At that local handoff, delivery and exact-commit hosted evidence were pending;
the acceptance record below supersedes that status without changing those results.
Historical failed tests/setup/network attempts are retained in the
[Thread 10 handoff](../dev/IMPLEMENTATION_PLAN.md#thread-10-handoff--20-october-2026).
At that local handoff, Thread 11 and later and #18 were NOT STARTED.


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
added. The historical run remains failed. Correction `a2132c3` / merge `6004c35`
is delivered and accepted after the corrected 12-cell run below. See the [correction handoff](../dev/IMPLEMENTATION_PLAN.md#thread-10-macos-ci-correction-handoff--20-october-2026).


## Thread 10 accepted delivery — 20 October 2026

The maintainer reviewed/pushed the correction and authorized closure after full
verification. Exact-merge run [39510802449](https://github.com/jeffshurtliff/obforce/actions/runs/39510802449),
attempt 1, at `6004c35cee63ac2e24b9833bd986f320d95485d3` passed all 12 cells:
Linux Python 3.12–3.15 each 1061 passed; macOS each 1059 passed/2 skipped;
Windows each 1045 passed/16 skipped. Coverage was 95% on Linux/macOS and 94%
on Windows. All required command logs were inspected: standalone strict
metadata/lock, Ruff lint/format, Bandit, pytest, fresh build, strict Twine,
exact 31-wheel/30-sdist archive checks, both guarded independent installs
per cell (24 total) and whitespace passed. No required command was skipped.

Earlier failed runs, local setup/probe failures and recorded test skips remain
historical evidence. Quiet pytest logs do not enumerate every skip reason.
Native ordinary-file reads, synthetic reparse/race tests and hosted package
probes qualify only those tested boundaries; no Windows sf, hostile-race,
writer, recovery, real org/vault or public lifecycle guarantee follows.
Requested platform relationships remain partial/unavailable even after clean
empty results; offline relationships remain not collected. No release or
publication is implied. #10 is accepted and closed. At its acceptance, Thread 11
was next eligible and NOT STARTED; the Thread 11 acceptance below supersedes that
status. Later threads and #18 remain NOT STARTED. See the full
[acceptance and handoff](../dev/IMPLEMENTATION_PLAN.md#thread-10-acceptance-and-closure--20-october-2026).

## Thread 11 pre-implementation transaction contract — 20 October 2026

This records the historical internal design before dependent implementation.
Thread 11 was then in progress; its acceptance record below is now authoritative.
Public lifecycle commands, source acquisition, graph
storage, automatic note removal, adoption, backup and Git integration stay out of
scope. No dependency or accepted NoteState/state-wire/hash change is intended.

**Explicit callers and authority.** `TransactionInputs` contains explicit absolute
vault/state/excluded paths and the same normalized components, coverage, graph,
retained components, previous graph, verified org identity, comparison attestation,
initial flag, options/layout and already loaded templates as the accepted planner.
`publish_plan(plan, inputs, preview=False)` independently plans from those inputs,
requires the complete candidate and immutable preconditions to agree, then repeats
all reads/absence/parent checks under the guard. Constructed, blocked, conflicting,
inconsistent, over-bound or stale candidates provide no authority. Outcome 4 is a
valid partial-coverage result, not evidence of absence. Only accepted preservation
patch bytes replace existing notes. Moves reconcile already user-moved UUID paths;
no filesystem rename of a managed note is requested. Prior graph remains an
explicit transient caller input. No-op and preview perform reads only, creating
nothing and preserving exact note/state bytes and mtimes.

**Guard and lifetime.** Explicit vault must already exist. The only control area is
vault/.obforce; no cwd/home/config/auth lookup. A bounded regular single-link
`writer.lock` contains a versioned canonical UUID token. POSIX nonblocking flock
or Windows nonblocking byte-range locking holds an open descriptor for the entire
mutation/recovery call. Full pathname/descriptor checks surround acquisition;
changing/removing/replacing the lock refuses. Never unlink the persistent lock:
this avoids concurrent open/unlink split-lock races. No-op/preview do not create
it. The OS releases the kernel lock on process death; no PID/time-based stale-lock
stealing or automatic deletion. An obtainable existing lock is reusable only if
its bytes/identity are valid. Any journal, staging residue or unknown control entry
blocks ordinary writes. Invalid/incomplete lock initialization requires manual
resolution. The lock coordinates cooperating Obforce writers, not arbitrary editors.

**Original private journal schema 1 (superseded by schema 2 below).** UTF-8 canonical JSON plus LF; exact keys, duplicate
key/depth/node/type/version checks, bounded before parsing. Root fields are
`journal_schema`, `transaction_id`, `lock_token`, `vault_identity`,
`control_identity`, `phase`, `entries`, `directories`, `guards`, `work_stamp`.
Phases: preparing, ready, publishing, committed, rolling_back, rolled_back,
cleaning. Entries are ordered note paths then `.obforce/state.json` last, with
before/after byte sizes and SHA-256, exact pathname stamps, deterministic numeric
blob names, published/restored stamps and an explicit operation intent. Blobs are
private complete before-images/candidates, never embedded public diagnostics.
Directory records retain intended relative paths and exact created stamps.
`guards` retain relative in-vault full same-API observations/digests outside the
opaque control area; external ancestry/exclusions are explicit caller inputs and
freshly checked during recovery. State-wire contents stay unchanged. Journal
hashes detect corruption, not malicious authentication; an attacker with control
of the trusted vault/control area can forge evidence. Recovery validates complete
schemas, paths, identities, candidate/prior state and note preservation consistency
before any change. It never guesses a path or reconstructs saved baselines.

**Order, ownership and crash windows.** Create control/guard, revalidate, persist
a preparing journal before staging. Journal updates use one exclusive bounded
`journal.next` followed by per-file replacement of `journal.json`. An incomplete
initial journal or leftover next file blocks rather than being repaired. Record
intents before creating the fixed transaction directory, note parents and blobs;
record full resulting identities/stamps afterwards. Stage on the same device as
vault/targets. Persist and sync all complete before-images and candidates plus a
ready journal before the first publication. Publish notes in deterministic order,
then corresponding state. Persist intent before each replacement and exact
published stamp after it. The persisted `committed` journal is the commit point;
no rollback after it. Per-file replacement is not an atomic multi-file operation.

A crash before an observed stamp is journaled may make ownership unprovable;
retain explicit recovery-required evidence instead of guessing. Rename can change
ctime: never round/ignore full same-API timestamps to claim ownership. Recovery
accepts an unchanged prior file, a fully recorded published file, or a fully
recorded restored file only. An unrecorded replacement remains ambiguous even
when candidate bytes/hash/inode happen to match. During an ordinary call, every
mutation checks all outstanding full observations immediately beforehand and again
afterwards. Expected parent metadata changes are accepted only with stable parent
identity/mode and an exact bounded directory-entry delta for the named owned
operation; all other entry stamps and ancestor observations must remain unchanged.
The Windows birthtime cross-API bridge and full same-API guards are retained.

**Recovery and cleanup.** `recover_transaction(vault, state_path, excluded_roots,
preview=True)` uses only local validated evidence. Preview is read-only and obtains
no lock. Actual recovery must acquire the same kernel guard and revalidate the
complete evidence. Before commit, restore changed notes (reverse note order), then
state, from exact before-images, only over fully matching recorded transaction
outputs. Remove newly created targets only with exact transaction ownership;
never overwrite an intervening edit. A conflict retains the journal/before-images
and blocks normal writes. Partial rollback has explicit intent/result records and
can be resumed only where ownership remains proven. Committed recovery performs
cleanup only. Cleanup validates each blob/target/directory, journals removal intent,
and deletes only matching owned blobs and proven empty transaction-created
directories; no recursive deletion. Final journal removal occurs only after all
owned temporary material is gone. Persistent control/lock stay. Recovery failures
are redacted and retain evidence, not partial success.

**Bounds and durability.** Maximum 128 changed files including state; 32 MiB
aggregate before plus after bytes; existing per-note 1 MiB and state 16 MiB limits;
16 MiB journal, depth 20, 300,000 JSON nodes; 50,000 saved guards, 256 created
note-parent directories, path length 1,024/depth 32/UTF-8 segment 240 (explicit vault
root at most 4,096 characters; full targets at most 5,121 including the relative path); 1 KiB fixed report. Overflow refuses, never
truncates. Existing planner/read limits also apply. File data is flushed and
fsynced before journal/publication; parent directories are fsynced on POSIX.
Failures refuse and retain recovery evidence. Windows lacks portable directory
fsync in this implementation; file fsync plus replacement does not promise
power-loss durability there. POSIX fsync is a request to the OS/filesystem, not
proof against hardware/network-filesystem failure. Local stable ordinary
filesystems and trusted same-user directory ancestry are required; no atomic
filesystem snapshot or hostile concurrent editor isolation is claimed. Immediate
checks cannot eliminate the final check-to-system-call race. Unavailable native
platform/process-death/power-loss qualification must remain explicit.

`TransactionResult` contains only fixed status, existing precedence-selected
outcome (3, 2, 1, 4, 0), recovery-required boolean, bounded file count and fixed
redacted report. No paths, content, source facts, UUIDs, exception strings or
journal/before-image data appear in diagnostics. Synthetic checkpoints and
subprocess death exercise every boundary; no source/transport/runtime network or
unapproved process access is added.

**Implementation refinements, before dependent acceptance probes:** immutable
before/after blobs are retained through publication and rollback. Each entry also
has `original` (exact prior target stamp) and `transfer` (nullable full stamp for
one deterministic numeric `.transfer` file); the transfer is a separately fsynced
copy used for replacement. This permits resumed rollback without consuming its
only evidence. Aggregate before/after bytes stay bounded at 32 MiB; at most one
additional transfer of up to 16 MiB exists, for at most 48 MiB of blob data.
Blob names/count are derived from entry index; no journal-supplied blob path is
followed. APFS locally reports directory link counts as 2 plus all entries;
POSIX mutation checks accept only the exact subdirectory-count delta or that
fully matching entry-count model. Windows requires an unchanged directory link
count. Exact named-entry deltas, full identity/mode/ancestor checks and all
unaffected observations remain mandatory. No timestamp is rounded or disabled.

New private control/blob files request mode 0600 and new directories 0700.
Publication/rollback use fresh replacement files: preservation of original
owner/group, ACLs, extended attributes, file identities or timestamps is not
promised. Note/state content and all accepted human-owned information retain the
contracts above; no-op retains original bytes/mtimes. Native Windows ACL/private
root and power-loss qualification is unavailable. Caller-selected trusted private
local roots are required; this increment is not a public lifecycle support claim.

If failure occurs before any journal/staging evidence exists, the result is
blocked with the original typed outcome. If the commit and all cleanup completed
but a final reporting/checkpoint failure occurs, the result records committed
with a non-success outcome and no recovery-required flag. It does not invent
a journal or claim silent success. Otherwise actual retained evidence is explicit.

## Thread 11 Windows lock-read correction — 21 October 2026

Before changing dependent code, the correction retains the existing lock token,
byte-zero nonblocking Windows range, POSIX flock, journal schema and state wire.
Do not move the range, unlock temporarily or skip full guards. The owning `_Lock`
will retain its descriptor and original full descriptor observation while the
kernel guard is held. `_Guard.check` will read only that lock through the owning
descriptor; all other paths still use the accepted bounded reader. Every lock
check must seek to zero, bound/read the exact canonical token bytes, verify the
expected digest, compare full same-API descriptor/path stamps before/after and
retain the Windows cross-API birthtime comparison. Detach the borrowed ownership
reference before closing on both normal exit and failed entry. The kernel lock
must remain held continuously during publication/recovery and every check.

The existing Windows run failed before fault injection, not at the requested
process-death boundary. A deterministic offline second-handle-denial regression
reproduces the same operational refusal before this correction. Microsoft states
that even the locking process cannot access the region through a second handle:
[LockFileEx remarks](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-lockfileex).
Python documents that [msvcrt.locking](https://docs.python.org/3/library/msvcrt.html#msvcrt.locking)
locks from the current descriptor position. Test snapshots made while owning a
lock must use that same validated owner handle too; OS-denied lock renames must
be recorded as refused test mutations, not skipped or treated as successful edits.
Subprocess failure diagnostics will include only fixed transaction result text
and captured bounded stderr, so a pre-checkpoint refusal stays distinguishable
from a missing checkpoint. At that correction checkpoint, no native Windows pass
was claimed; the accepted
run below now supplies hosted synthetic Windows evidence for the tested boundaries.

## Thread 11 Windows recovery observation correction — 21 October 2026

Recorded before dependent implementation. Run 39670042028 attempt 1 at merge
bde1225b51512e8eba2e5d9513f205a11c198125 exposed a safety gap: Windows pathname
ctime can remain creation time after an in-place same-byte rewrite and restored
mtime. A fresh descriptor read alone compares against the edited file, not the
historical publication observation. Recovery must retain that historical change
observation, rather than infer unchanged ownership from bytes and creation time.

Private journal **schema 2** adds required `file_guards`: bounded records of
vault-relative `path` and full seven-integer **descriptor** `stamp` (device,
inode, mode, links, size, mtime_ns, ctime_ns). Persist every hashed regular-file
observation except the self-referential journal/journal.next: notes, state,
writer.lock, immutable before/after images and live transfer copies. Exact
membership is derived from the existing journal guards and entry evidence;
missing, extra, duplicate, malformed or contradictory records refuse recovery.
The existing journal byte/depth/node/guard bounds apply to this collection too.
Schema 1 is unsupported and retained for manual resolution, without migration or
reconstruction. Accepted state JSON, NoteState, hashes and planner observations
remain unchanged. No dependency or native API binding is added.

Retain full same-API pathname and descriptor stamps independently, linked by the
accepted Windows birthtime bridge. The bounded reader exposes descriptor stamps
from its existing verified read; transaction guards retain/recheck them across
reads and recovery. Only explicitly mutated paths may acquire new descriptor
baselines. Lock reads retain the continuously held owning handle. Persist these
observations before publication and revalidate before rollback/committed cleanup,
including same-byte edits with restored mtime. Descriptor observations recovered
from the journal remain active under the writer guard. No retry, timestamp
rounding, sleep, new skip, or weakening of parent/path/content checks is allowed.

Publication order, commit point, lock lifetime, crash windows, fsync/durability,
cleanup ownership and all previous finite limits remain as recorded above.
This is conservative local-filesystem evidence, not an atomic snapshot, hostile
writer exclusion, guaranteed detection of forged/coarse filesystem timestamps,
or atomic multi-file replacement. Native Windows validation was pending at this
pre-implementation checkpoint; the acceptance record below supersedes that gate.
Windows sf remains refused; Threads 12–17 and #18 remain NOT STARTED.

References: [Python stat timestamp semantics](https://docs.python.org/3/library/os.html#os.stat_result),
[CPython Windows descriptor stamps](https://github.com/python/cpython/blob/3.12/Python/fileutils.c),
[pathname compatibility conversion](https://github.com/python/cpython/blob/3.12/Modules/posixmodule.c),
and [Windows ChangeTime](https://learn.microsoft.com/windows/win32/api/winbase/ns-winbase-file_basic_info).

Local correction verification: 1246 passed/2 existing skips on macOS ARM64 /
Python 3.14.7, 20 focused added cases, all static checks and both fresh independent
installed artifact probes passed. Hosted verification was pending at that local
handoff; the acceptance record below supersedes that gate. See the [historical handoff](../dev/IMPLEMENTATION_PLAN.md#thread-11-windows-recovery-correction-handoff--21-october-2026)
for exact evidence, retained failures/skips, hashes and acceptance gates.


## Thread 11 accepted delivery — 21 October 2026

Thread 11 is accepted and #11 is closed after maintainer-authorized verification.
Recovery correction `4aaeb0f9481f1c306a9089426f40413f0e53be69` is merged at
`2995f93949aaf298cfc6f377ac8b25aa3e17a7ad`; trees match.
[Run 39676435834, final attempt 2](https://github.com/jeffshurtliff/obforce/actions/runs/39676435834/attempts/2)
has all 12 Python 3.12–3.15 cells successful: Linux 1248 passed each; macOS
1246 passed/2 skipped each; Windows 1232 passed/16 skipped each. Every required
standalone check, fresh build/Twine/exact 32/31 archive inspection, both independent
installed probes per cell (24 total) and whitespace passed. Full command logs
were inspected, including installed same-byte recovery refusal with active runtime
socket/process guards and no cwd writes. Setup downloads are separate network use.

Eleven cells retain successful attempt-1 execution logs; macOS 3.14 completed
in attempt 2. Attempt 1 remains failed with that cell cancelled, no assigned
runner/steps and unavailable log (404 BlobNotFound); its cause is not inferred.
Earlier failed runs 39610229702 and 39670042028, skipped gates, local failures and
all skips retain their original outcomes. Historical pending status above is
superseded, not relabeled as passing evidence.

Private schema 2, full pathname and historical descriptor/birthtime/hash/parent
guards, continuous owning-lock reads and conservative rollback/cleanup are
accepted for the tested synthetic boundaries. State wire and ownership/source/
coverage/hash/UUID contracts stay unchanged. Schema 1 remains unsupported retained
evidence. No public command, source acquisition, graph storage, adoption or
automatic deletion is introduced. Hosted results do not qualify Windows sf,
private-root ACLs/directory-fsync durability, power-loss, hostile editors, forged/
coarse timestamps, atomic snapshots or atomic multi-file replacement. Ambiguous
crashes still require retained evidence/manual resolution.

See the [acceptance and handoff](../dev/IMPLEMENTATION_PLAN.md#thread-11-acceptance-and-closure--21-october-2026)
for exact gates, history and the Thread 12 launch prompt. Thread 12 is next eligible
only after a new request and remains NOT STARTED. Threads 13–17 and #18 remain
NOT STARTED. No release/publication authorization follows.
