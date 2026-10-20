# Internal state and identity reconciliation (Thread 09)

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
final whole-scan rechecks. Missing/changed files or parents, unreadable directories
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
preservation. Synthetic vault setup writes are outside the checkout/cwd and precede
read snapshots. Runtime socket/process audit guards stay active. Setup/build/pip
downloads are separate network use. Actual results and native/hosted gaps are in
the [roadmap handoff](../dev/IMPLEMENTATION_PLAN.md#thread-09-handoff--20-october-2026).
Thread 09 remains pending maintainer acceptance; Threads 10–17 and enhancement #18
are NOT STARTED. No release/publication or Windows sf qualification is implied.
