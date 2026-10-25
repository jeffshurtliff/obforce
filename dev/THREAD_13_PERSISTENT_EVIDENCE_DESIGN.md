# Thread 13 private refresh evidence — design proposal

**Review date:** 23 October 2026. **Approval:** All four decisions approved
25 October 2026; Thread 13 implementation authorized. The proposal below is retained
as the reviewed design; implementation acceptance remains separate. The maintainer authorized proposing persistent normalized facts and
graph evidence inside the managed vault for ordinary independent CLI invocations.
The 23 October design authorization superseded the transient-only requirement;
the 25 October approval now also authorizes implementation of all four decisions.
Neither authorization permits
real Salesforce access, CLI/plugin installation, Git delivery, publication or later threads.

## Recommended storage and explicit version changes

Embed one evidence snapshot in the existing `.obforce/state.json`. Avoid a second
evidence file and another cross-file association/publication dependency. Preserve
the current state path, SavedNote baselines, persistent UUIDs and note mappings.

| Contract | Proposed change |
| --- | --- |
| Private state document envelope | `state_schema: 2`; require a new `evidence` object |
| Nested persistent evidence | New `evidence_schema: 1`, defined below |
| NoteState record | Keep its existing schema 1 and exact canonical shape |
| Config/model/note/marker schemas | Keep version 1; no config key required |
| Source/graph/render hashing and UUID policy | Unchanged algorithms and semantic inputs |
| Renderer | Keep version 3 and generated four-space nesting; creation remains creation-only |
| Recovery journal | Keep schema 2 and its exact shape, target rules and `file_guards`; extend semantic validation to explicit state-document versions |

Separate the private document-envelope version constant from the existing
`STATE_SCHEMA_VERSION` used by NoteState; do not globally change that constant
and accidentally invalidate every NoteState. New envelope version 2 means a new
private state format, not a note migration. Older executables will refuse it;
use a matching/newer executable for recovery. No backward-writer compatibility
is claimed. No journal version 3 is needed for this proposal because evidence
is inside the existing state blob and journal fields/order/ownership do not change.

The root retains exactly `state_schema`, `binding`, `selection`, `scope_hash`,
`coverage`, `notes`, and adds exactly `evidence`. Its new object has exactly:

```text
evidence_schema: 1
components: [exact normalized Component canonical records]
graph:
    coverage: exact normalized relationship CollectionCoverage
    edges: [directed source/target endpoint records and evidence observations]
inventory_scope: null OR {scope_id, method, api_version}
```

This is a structural description, not executable JSON or an implemented fixture.
Graph binding/Selection come from the validated containing envelope rather than
being duplicated. Component canonical records retain their existing model/binding
fields so their source hashes can be rederived without changing that contract.
`evidence_schema` versions the graph/component/scope wire shapes together.

## Minimum retained information and privacy

- One Component per tracked note, including currently absent/missing components:
  exact key/binding, optional canonical live record ID, allowlisted attribute
  values with absent/null/unavailable distinctions, and normalized provenance.
  Omit incidental `collected_at`; it is excluded from existing semantic hashes.
  An observed component replaces its prior record; an absent one keeps the exact
  prior record. Do not merge guessed field values or retain a second history.
- The exact accepted **refreshed** DependencyGraph used for the saved note hashes:
  directed endpoints (including unresolved/unsupported/external descriptors),
  resolved keys, private record IDs, every distinct method/coverage/stale
  observation and graph-wide relationship coverage. Incoming views derive from
  those edges; do not store a second backlink graph. Keep stale historical endpoint
  mappings as historical evidence, not current identity assertions.
- The optional inventory-scope declaration described below. Binding/Selection,
  independent collection coverage and managed paths already reside in the envelope;
  do not add path copies, per-run timestamps, counters or random generation IDs.

No raw CLI replies, Apex bodies, credentials, auth selectors/endpoints, permission
dumps, host/source paths or user prose/properties are added. Live record/org IDs
and previously collected audit display names can be necessary private hash inputs;
they must never appear in reports, issues, examples or uploads. Audit-name collection
remains optional. Disabling it removes names from newly observed normalized records
and rendered output; it cannot promise erasure of names in absent retained records
or existing recovery before-images. A separate purge/migration is not proposed.

The snapshot replaces itself only through the guarded writer, with its existing
private file/directory mode requests (0600/0700), same-filesystem staging and
constrained cleanup. It is private local data, not encryption or a portable ACL
guarantee. No new sharing, telemetry, logging, backup or Git integration. Existing
recovery before-images may contain human note content; they retain their accepted
private lifecycle and are never promoted into source evidence.

## Untrusted-input validation and finite bounds

Use bounded no-follow/descriptor/path/parent reads of the complete state file.
Parse version-specific exact key sets; reject duplicate/unknown keys, unsupported
versions, invalid UTF-8/BOM, nonfinite/floating numbers, coercions, excessive
nesting/nodes and invalid types before constructing normalized records. Do not
deserialize Python objects. Use existing immutable models and standard-library
JSON; no new runtime dependency is proposed.

Reject duplicate component keys/live-ID mappings, repeated edge pairs or repeated
observations on wire before constructors could silently deduplicate them. Require
canonical identity/scope/field representations, valid availability wrappers,
bounded descriptors and provenance, known resolution/status enums and exact
normalized round trips. Serialize deterministic sorted arrays, canonical object
keys and one LF. Preserve an already valid state's original bytes on semantic no-op.

Cross-check all of the following before any candidate can authorize publication:

1. Evidence component keys equal the tracked-note key set exactly. Each binding
   and selection matches the envelope, and each exact Component.source_hash equals
   its NoteState.source_hash. No extra/untracked facts or missing retained facts.
2. Graph coverage equals saved relationship coverage, independent of inventory and
   audit. Its per-note fingerprint equals every saved graph hash using **saved**
   paths. Deserialize real evidence; never reconstruct it from hashes/Markdown.
   Resolve current observations separately; do not rewrite historical stale keys.
3. Offline graph stays empty/not-collected; live collected relationships remain
   partial/unavailable under accepted collector limitations. Persisting them
   cannot turn clean empty replies into complete relationship coverage.
4. Existing exact generated-property/body baselines, source binding/verified-org,
   UUID/key/path uniqueness, Selection and all filesystem controls still validate.
   Renderer fingerprints keep their accepted meaning; template bytes are not
   reconstructed from render hashes. Human generated edits block the entire batch.

| Independent refusal ceiling | Proposed maximum |
| --- | --- |
| Complete state input/output | Existing 16 MiB |
| Nested evidence canonical UTF-8 bytes | New 8 MiB, counted inside the 16 MiB state limit |
| JSON depth / total state nodes / text scalar | Existing 16 / 250,000 / 2 MiB |
| Tracked components / notes | Existing 10,000 each |
| Graph edges / total observations | Existing 20,000 / 40,000 |
| Component text / endpoint descriptor | Existing renderer 4,096 characters / graph 512 characters |
| Aggregate current plus prior normalized planning input | Existing 16 MiB |
| Note / all candidate note bytes plus state | Existing 1 MiB / 64 MiB |
| Changed files, including state / before-plus-after bytes | Existing 128 / 32 MiB |
| Journal / guards / new note-parent directories | Existing 16 MiB / 50,000 / 256 |

All existing parser/render/path/discovery/report/transport limits also apply.
These are independent ceilings: node, input or transaction budgets can refuse
before a component/edge ceiling is reached. No bound increase, truncation, evidence
eviction, automatic note deletion or partial publication is proposed. Repeated
unchanged failures/stale evidence deduplicate through accepted graph semantics;
genuinely accumulating distinct evidence can eventually exhaust a bound and refuse.

## Build, sync, publication and recovery

**Build:** Keep absent/empty-only output and repeat-build refusal. Acquire synthetic
or separately authorized source/graph inputs through existing adapters. Plan notes
and version-2 state together. Save the exact selected normalized components and
the plan's accepted refreshed graph, including empty offline inventory/graph cases.
Evidence/state must validate before setup or publication. No post-build cache write.

**Sync:** Require an existing explicit version-2 managed state before acquisition.
Validate evidence against saved paths first, then reconcile unique moved-note IDs.
For the planner supply prior graph directly from validated state, exact saved
Components for precisely the tracked keys absent from current input, independent
current coverage/graph, and explicitly evaluated comparability. Current components
plus retained components and the refreshed graph become the next evidence snapshot.
All tracked notes remain represented, including missing ones. Reactivation requires
positive current observation in the same binding/Selection; absence never deletes.

The engine's evidence is part of the same immutable complete ChangePlan/inputs as
the note patches/state. The writer independently replans/rechecks evidence from
the observed state, compares the full candidate, and validates outstanding state
hashes and historical descriptor/path/parent stamps under continuous writer
ownership. Any changed observation refuses; do not adopt a newer state or retry.
No source query or template reload is needed during recovery.

**One transaction:** Existing deterministic note replacements occur first and the
complete state+evidence blob last. Stage before/after images for the complete blob,
fsync through existing operations, journal before publication, record exact intents
and resulting stamps, and use the persisted committed phase as the commit point.
Hash-only or evidence-only updates still require a journaled state change. There
is no atomic multi-file or atomic filesystem snapshot claim.

**Recovery:** Extend semantic state validation to check the complete embedded
evidence/NoteState association on every available version-2 before/after blob.
Recheck saved source and graph hashes/paths, exact preservation patches, unchanged
note baselines, no removed tracked identities, and unchanged binding/Selection/
scope declaration across noninitial transactions. Reject mixed envelope versions
in a purported refresh. Rollback restores old notes and the entire prior state+
evidence; initial rollback removes only proven newly created outputs. Committed
recovery cleans proven transaction-owned material only. Intervening edits or
unrecorded replacements retain recovery-required evidence, even if bytes match.
Phase-allowed already removed blobs remain governed by the existing surviving-
target rules; never fabricate unavailable evidence to finish cleanup.

Keep journal schema 2, full `file_guards`, Windows birthtime bridging and continuous
owning-handle lock reads. Read/recover legacy schema-2 journals with schema-1 state
using their existing version-specific semantics; this is recovery compatibility,
not state upgrade. Journal schema 1 stays unsupported retained evidence. Unknown
future state/journal versions refuse. Tests must prove these separate dispatches.

**Dry-run/no-op:** Perform the same bounded validation/planning with candidate
evidence only in memory. No state, lock, journal, config, log, cache, staging or
vault creation. When normalized facts, graph/staleness, coverage, paths and output
are unchanged, preserve note and complete state bytes/mtimes. Do not record each
check/attestation or change a schema on a no-op. A first stale transition or real
coverage change may legitimately update output/state; repeating it must stabilize.
Source/config/templates/caller inputs/unrelated files and `.obsidian` stay untouched.

## Existing vaults and missing evidence

Valid schema-1 state lacks the source/graph facts needed to upgrade safely.
Propose conflict 3 for public sync, including dry-run, before acquisition or writes,
with a redacted unsupported-refresh-evidence diagnostic. Missing, corrupt, unknown
or internally inconsistent schema-2 evidence likewise blocks the complete batch.
An empty schema-1 state also does not acquire a silent version upgrade. Never infer
old facts from current observations, generated Markdown, saved hashes or journals;
never adopt/rebuild existing notes or offer force/bootstrap flags.

Continue to allow explicitly selected legacy schema-2 journal recovery under its
own rules. An old vault remains intact and can be kept/read as-is. A new build into
a different absent/empty destination can create evidence-bearing notes, but cannot
automatically transfer its old human content or assert old UUID continuity.
A controlled old-vault evidence migration is a separate future scope decision,
not part of this Thread 13 proposal. No existing-vault recovery capability is
removed merely because ordinary sync cannot proceed.

## Comparable accessible live inventory

Persistence solves prior evidence supply; it does not prove stable permissions.
Keep the existing verified Organization query and Selection/method/API-version/
exhaustion checks. Do not add auth/principal/permission queries or credential reads.
Neither a stored org ID, alias, scope hash nor a successful empty query certifies
unchanged accessible metadata scope.

Propose these **live-only** invocation options, with no implicit config defaults:

```sh
# Planned options only; normal explicit live executable/directory options also apply.
obforce build --config ./live.toml --inventory-scope-id fictional-reader-scope-v1
obforce sync --config ./live.toml --inventory-scope-id fictional-reader-scope-v1 --attest-comparable-inventory
```

The optional scope ID is a maintainer-chosen opaque logical label (1–128 ASCII
letters/digits/underscores/hyphens), never an account name, credential or permission
fingerprint. Live build stores it with the actual inventory method/API version as
an immutable scope reference bound to the envelope's verified org and Selection.
Omitting it stores null and still permits build/refresh with preserved lifecycle;
that vault cannot subsequently enable missing transitions without a separately
reviewed scope-baseline change. No initial missing proposal occurs, even on a
complete empty build. Offline rejects both options and stores null.

On **each** attested sync, require the same explicit scope ID plus
`--attest-comparable-inventory`. The attestation means the maintainer has verified
that accessible inventory scope remained comparable from the declared build
reference through all retained component evidence, including intervening partial
runs. It is a caller assertion, not automatic platform verification. Do not save
an enduring true flag, timestamp, principal identity or permission dump. Stored
scope ID alone never authorizes future absence decisions; declaration cannot
silently change or be added to an old/null reference during sync.

Only the conjunction of matching validated reference, this invocation's explicit
attestation, independently verified same org/Selection, matching saved/reference
inventory method/API version and complete supported exhausted/no-limit/no-warning
live inventory may set planner comparability true. A partial build can establish
a declared observation scope, but only a later complete attested scan can establish
absence within it. Unknown request API version stays explicit null and must match;
do not infer it from class compilation version.

| Observation | Proposed result |
| --- | --- |
| All absence gates satisfied | Mark unobserved tracked notes missing; retain facts, edges and human content; complete empty inventory can mark all tracked notes missing |
| No declaration, omitted attestation or scope continuity cannot be established | Preserve absent notes/lifecycle and stale relationships; report missing evaluation unavailable; completed run with absent tracked keys returns at least 4 |
| Current inventory partial/unavailable | Preserve absent lifecycle/facts; requested incomplete coverage returns 4 |
| Required collection fails | Operational 1, no candidate publication; do not turn failure into an authoritative empty result |
| Changed/ambiguous org, workspace, Selection, declared scope ID, or declared method/API reference | Conflict 3, complete-batch refusal; no rebinding/rebaselining |
| Present previously missing component | Reactivate from positive same-source observation; absence attestation is unnecessary for presence |
| Offline absent component | Preserve prior facts/lifecycle; report local scope; by-design exclusions alone do not force 4 |

Public orchestration must check declared method/API drift before planning; lower-
level conservative absence predicates remain necessary too. Reject malformed flag
combinations with invalid usage 2. Lifecycle-ineligibility reports are a separate
outcome facet; do not falsify inventory Coverage with synthetic permission facts
or change its completeness to smuggle an attestation. The full candidate/outcome
is independently revalidated. Precedence stays **3, 2, 1, 4, 0**. A valid no-op can
return 4 for requested incomplete evidence without rewriting state. Live platform
relationships still prevent a claim of complete dependency coverage.

## Review decisions and implementation acceptance gates

The maintainer approved all four recommendations below on 25 October 2026:

1. Approve embedded state-document schema 2/evidence schema 1, preserving NoteState
   schema 1 and journal schema 2 with explicit version-specific recovery validation.
2. Approve the 8 MiB nested evidence ceiling inside existing overall budgets.
3. Approve refusal of evidence-less legacy vault refresh with no migration/adoption.
4. Approve the optional immutable live scope label and per-invocation attestation,
   including preservation/exit 4 when absent tracked keys cannot be evaluated and
   no silent later initialization of a null scope reference.

Implementation would require focused state/graph deserialization and planner/engine/
transaction semantic refinements, command/help/docs changes, and synthetic multi-run
and interruption tests. Validate current+retained source and graph round trips,
tampering/duplicate/limit refusals, old renderer baselines, human debt/YAML/prose,
moves and backlinks, stale stabilization, partial/complete-empty/missing/reactivation,
null/matching/mismatching scope declarations, live mocks, every publication/rollback/
cleanup boundary and legacy recovery. Prove no-op/dry-run byte/mtime/tree preservation.
Then run full applicable local gates, fresh exact archives and independent installed
commands under active runtime network/process guards. Existing CI counts/artifacts
remain historical evidence until new delivered code is tested at its exact commit.

**Historical 23 October review outcome:** This review added no runtime behavior,
executable fixture, schema implementation,
dependency or real Salesforce operation. #13 remains open; implementation and
acceptance remain pending. Threads 14–17 and enhancement #18 remain NOT STARTED.
