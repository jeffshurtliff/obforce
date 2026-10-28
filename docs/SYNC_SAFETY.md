# Synchronization safety

Obforce plans and validates a complete batch before publication. A conflict in
any managed note, dashboard, state, path or binding blocks the entire batch.
There is no force-overwrite, automatic adoption, migration or reset mode.
Use the [quickstart](QUICKSTART.md), [refresh](REFRESH.md) and
[recovery guide](RECOVERY.md) for the command workflow. Python modules are internal
implementation details, not a stable API.

## State and ownership

Private `.obforce/state.json` uses state-document schema **2**, embedded evidence
schema **1**, NoteState schema **1**, and optional dashboard schema **1**. Journal
schema is **2**, renderer fingerprint **4**, and note/marker/config/model versions
are **1**. Unknown shapes, keys, types, duplicate JSON keys, IDs or paths, invalid
hashes/UUIDs/base64 and contradictory baselines refuse rather than repair.

State stores binding/Selection/scope and per-note UUID, component key, portable
path, source/graph/render hashes, exact generated-property baselines and exact
marker-interior bytes encoded as canonical base64 with SHA-256. Human prose and
user properties are not generated baselines. Embedded evidence retains exact
normalized facts for tracked components and directed graph/coverage required to
validate those hashes across independent invocations. It is not reconstructed
from Markdown or hashes. Loading rederives integrity against saved paths.

A unique in-vault move retains UUID/source key and invalidates affected incoming
and outgoing links, including neighbors with unchanged metadata. Duplicate/copied
IDs, vanished tracked notes, ambiguous mappings, generated edits and unowned
collisions refuse. Unrelated notes remain unadopted. Existing notes receive only
validated generated-property/body patches, never a complete creation candidate.
Both exact saved body bytes and owned-property values must match before patching.
All human fields, comments and outside-body bytes stay protected under the
[supported YAML/line-ending subset](NOTE_FORMAT.md).

Workspace, source mode, verified live org and Selection cannot be silently
switched. Live aliases are selectors, not identities. Missing/unknown/corrupt
state with managed notes refuses. Legacy evidence-less state-document-schema-1
sync refuses before acquisition, including dry-run. Valid legacy state images
inside supported schema-2 journals retain version-specific recovery semantics;
this is not migration. Journal-schema-1 recovery remains refused and retained.

## Roots, observation and bounds

Keep vault, source project, template root and application installation disjoint;
config cannot be inside the vault. Use explicit stable trusted private local
roots. Lexical ancestors are checked before resolution so `link/..` cannot hide
links. Root `..` remains config-relative; generated relative paths reject traversal.
Unsafe links/junctions/reparse points, special/multiply linked files, portable
case/NFC/reserved-name aliases, file/parent collisions and unexpected parent
changes refuse. No automatic race retry or weaker observation is provided.

Read guards retain full pathname and historical descriptor/birthtime/size/mtime
observations, hashes, absence and parent snapshots. They do not create an atomic
filesystem snapshot or exclude hostile final-syscall races. Ordinary reads may
update access times. Stable ancestry includes the installed application as well
as fixtures. Isolate each installer/coverage run; setting temporary variables
alone does not isolate a busy application ancestor.

| Independent refusal bound | Maximum |
| --- | --- |
| Config / explicit root | 64 KiB / 4,096 characters |
| Observed entries per parent / initial setup directories | 50,000 / 32 |
| Note / frontmatter / dashboard | 1 MiB / 64 KiB / 16 KiB |
| State / nested evidence | 16 MiB / 8 MiB |
| Tracked components / graph edges / graph observations | 10,000 / 20,000 / 40,000 |
| Aggregate reads / complete candidates | 64 MiB each |
| Changed files, including dashboard and state | 128 |
| Transaction before-plus-after images | 32 MiB |
| New note-parent directories | 256 |

JSON node/depth, path, parser, template and section limits also apply independently;
see [note parsing](NOTE_FORMAT.md) and [rendering](RENDERING.md). A smaller batch
can hit an earlier bound. Overflow refuses without truncation, automatic evidence
eviction, partial batch publication, batch splitting or public limit overrides.
The measured 1,000-class/10,000-edge graph is not a supported publication size:
1,000 notes plus dashboard/state require 1,002 files; even 127 notes require 129.
Actual bounded public previews/builds refuse before destination setup.

## Complete planning and fresh integrity checks

Reconciliation verifies prior graph evidence at saved paths before rendering
against unique reconciled paths. Every absent component requires retained facts
matching its saved source hash. Every existing plan requires matching prior graph,
coverage and paths. Partial/offline absence preserves prior facts/lifecycle;
unconfirmed relationships retain provenance as stale. Missing evaluation requires
all [comparable complete live-scope gates](REFRESH.md). No note is automatically deleted.

A plan contains deterministic complete candidate bytes/state and explicit
publication preconditions. Proposed note/dashboard paths and parent roles are
validated together. The writer independently replans explicit inputs against
guarded observations and requires candidate equality before publication. Saved
hashes alone do not authorize writes. No global or filesystem cache is used to
bypass integrity. A pass can reuse a validated view of its own immutable note-path
snapshot; **each independent evidence validation, planning and replanning pass
creates a fresh snapshot**. Rendering, malformed-input error precedence and
all filesystem/transaction/recovery checks retain their independent boundaries.

## Initial setup and guarded publication

Build accepts only an absent or completely empty destination, checking again
before publication. It refuses every existing entry, including `.obsidian`,
unrelated notes, state or post-rollback control/lock. Preview validates an absent
root without creating a temporary stand-in vault. After candidate and writer-bound
validation, actual setup creates missing directories individually with guarded
exact-entry deltas and requested private mode 0700, rechecks unaffected ancestry,
requires empty output and regenerates an equal plan against the existing vault.
Caught setup failure removes only still-empty directories proven created and
fully observed by that call. Existing parents, intervening edits and unobserved
creation survive. Process death before journal authority can need manual resolution.

Publication establishes a continuous owning-handle kernel single-writer guard,
same-filesystem staging, before-images, journal and precondition rechecks. Changed
notes, then dashboard, then complete state/evidence use individual guarded
replacements. State is last, not an extra post-publication evidence/cache write.
The transaction is marked committed only after outputs and state agree. A persistent
private writer lock can remain after successful publication/recovery. A no-op or
preview creates no lock, journal, staging or other Obforce artifact.

Failure attempts rollback only when current targets still match expected owned
versions; intervening edits retain recovery-required evidence. Ordinary writes
refuse while incomplete recovery evidence exists. Committed cleanup removes only
proven owned temporary material. Precommit rollback restores complete prior
notes/dashboard/state or removes only unchanged proven new files. The dashboard
must match its exact tracked path/content association; no asset move, removal or
adoption through state-only changes is allowed. Unchanged assets are validated too.

## Recovery, no-op and evidence limits

Recovery preview reads validated local config/journal/state evidence without
source acquisition, template execution or a writer lock. Applying rollback or
cleanup validates the phase before and under the continuous writer guard.
Wrong-phase selection, incomplete/unknown/schema-1 journals, unsafe targets or
intervening edits refuse with 3 and preserve evidence. Surviving target/blob rules
are phase-specific; missing before-images are not fabricated. No broad recursive
cleanup or automatic recovery is provided. Preview can return 0 while reporting
that explicit recovery is required. Without pending evidence it is a write-free
no-op. Control/lock retained after rollback means repeat build still refuses.

Dry-run creates no config, vault, state, lock, journal, log, cache or staging
artifacts. No-op preserves note/dashboard/state bytes and mtimes, including
human-only edits and differently formatted valid state JSON. First stale/coverage/
path changes can legitimately update output/state; repeated unchanged observations
stabilize. No timestamp is rewritten just to record a check. Requested incomplete
coverage can return 4 even on a no-op. Outcome precedence remains **3, 2, 1, 4, 0**.

Publication is recoverable, not atomic across files. Cooperating lock/checkpoint/
process-death tests do not establish power-loss durability, hostile-editor
exclusion, forged/coarse timestamp detection, Windows directory fsync/private-root
ACL behavior or arbitrary filesystem support. No real sf or Obsidian result is
inferred from mocks. Windows sf stays refused and native Obsidian preview remains
unavailable. See [qualification](QUALIFICATION.md) for actual evidence and
[security](../SECURITY.md) for private retained facts and before-images.

<!-- Compatibility targets for retained maintainer evidence links. -->
<a id="thread-10-pre-implementation-planner-contract--20-october-2026"></a>
<a id="thread-11-pre-implementation-transaction-contract--20-october-2026"></a>
<a id="thread-11-windows-lock-read-correction--21-october-2026"></a>
<a id="thread-11-windows-recovery-observation-correction--21-october-2026"></a>
