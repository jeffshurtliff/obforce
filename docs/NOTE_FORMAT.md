# Note ownership and state contract

Thread 13 [public refresh](REFRESH.md) now publishes generated-only patches and
exact source/graph evidence through the accepted writer. Its state-document
envelope is schema 2; NoteState remains schema 1 with unchanged UUID/property/body
baselines. Legacy evidence-less public refresh refuses without adoption/migration.
The dated internal increments below retain their original contract boundaries.

Thread 02 freezes constants, normalized state records, and fingerprint inputs.
Thread 07 [renders candidate strings](RENDERING.md); Thread 08 now parses and
patches caller-supplied managed-note bytes internally as described below. State
loading/discovery and unique move reconciliation are internal Thread 09 work
([safety contract](SYNC_SAFETY.md)); Thread 10 adds internal read-only planning.
Accepted Thread 11 publication/recovery is connected to public initial build by
Thread 12. Refresh remains Thread 13. This fictional note illustrates the
version-one contract; initial build never adopts or regenerates an existing note.

```markdown
---
obforce_id: "00000000-0000-4000-8000-000000000001"
obforce_schema: 1
sf_type: "ApexClass"
sf_full_name: "DemoService"
sf_source_mode: "local"
sf_dependency_coverage: "not_collected"
sf_lifecycle: "active"
type: "salesforce_component"
tags: ["salesforce"]
technical_debt: false
tech_debt_severity: ""
tech_debt_status: ""
last_reviewed: null
---

<!-- obforce:generated:start -->
## Salesforce Metadata

Fictional local-scope facts. Salesforce audit values are unavailable.
Dependencies were not collected from this offline input.
<!-- obforce:generated:end -->

## Business Context

Human-authored context belongs here.

## Known Issues / Technical Debt

Leave assessment to a person.

## Additional Information
```

## Exact ownership and versions

`obforce_id` is a persistent canonical lowercase UUID, independent of its path;
`obforce_schema` is integer 1, not a boolean or string. Model, note, state,
config, and marker versions start at 1, as does the initial renderer-contract
version. The marker version is tracked internally; it is not an extra note key.
Unsupported schemas require refusal, never automatic migration or repair.

The exact generator-owned property allowlist is:

| Identity | Salesforce facts | Collection/lifecycle |
| --- | --- | --- |
| `obforce_id` | `sf_type`, `sf_full_name`, `sf_namespace` | `sf_source_mode` |
| `obforce_schema` | `sf_api_version`, `sf_status` | `sf_dependency_coverage` |
| | `sf_created_at`, `sf_created_by` | `sf_lifecycle` |
| | `sf_last_modified_at`, `sf_last_modified_by` | |
| | `sf_created`, `sf_last_modified` (UTC dates) | |

The whole `sf_*` namespace is reserved. An unknown `sf_*` key is unsupported and
must be refused rather than adopted or overwritten. Every other key belongs to
the user after creation, including `type`, `tags`, `aliases`, business fields,
all `technical_debt*` fields, and arbitrary custom properties. Creation defaults
do not transfer their ownership. MTF-2 changes new-note `technical_debt` to a strict
Boolean, false by default; this is an initial checkbox default, not an inferred
assessment. The maintainer authorized false throughout fictional/example/test
defaults, without retaining historical unassessed data or a legacy view.
New `tech_debt_severity` and `tech_debt_status` strings default blank; `last_reviewed`
defaults null, with `YYYY-MM-DD` recommended for a human review date. These and
earlier human key names are never renamed or backfilled on existing notes.

Owned property values are flat scalars or lists supported by Obsidian. Unknown
audit values are omitted and their availability explained in the generated
region. A null namespace means no namespace, not an invented package. Lifecycle
is `active` or `missing`; missing only means unobserved in a comparable complete
accessible live scope, not proven deletion. Dependency coverage uses the four
statuses in [COVERAGE.md](COVERAGE.md). Audit display names are optional via
`include_audit_names`; exclude unnecessary emails, usernames, org/record IDs,
internal URLs, raw API data, and class bodies from notes. Quote wikilinks when
stored as YAML values. Serialization/escaping is implemented for new candidates in Thread 07.

## Generated region

The exact reserved marker strings are:

```text
<!-- obforce:generated:start -->
<!-- obforce:generated:end -->
```

There must be exactly one ordered pair, each on its own line. Repeated, nested,
missing, reversed, inline, or otherwise malformed markers are conflicts. Marker
strings may not occur in source values or template content in a way that creates
an extra marker or ambiguous boundary. Thread 07 validates its own generated/new candidates against this structure;
Thread 08 independently validates supplied existing bytes too.

Only the bytes strictly between the validated marker lines are replaceable.
Preserve the marker lines and all user body bytes outside them, including line
endings. A creation template initializes new notes and user sections. Refresh
must never render the whole existing note from that template.

Generated properties and the generated body each have saved baselines. An edit
to either is a conflict even when Salesforce facts are unchanged. Identity edits,
duplicate IDs/mappings, unknown schema, invalid markers, duplicate YAML keys,
unsafe tags, malformed frontmatter, and unsupported YAML structures block the
batch before any publication. No fallback destructive repair or force mode.
User prose and supported custom YAML structure/comments/types/quoting must be
preserved. Universal byte-identical frontmatter preservation is not promised;
Thread 08 supports the bounded round-trip forms below and refuses unsafe forms.

## Internal state and invalidation

`NoteState` stores UUID, binding, structured component key, portable vault-relative
path using `/`, source/graph/generated-render hashes, exact owned-property
baseline, and generated-region SHA-256. Baseline values use the normalized
availability wrapper, distinguishing an absent key, null, empty, false, and
unavailable. Identity/schema baseline entries must exactly match the note UUID
and supported note schema. User-owned properties are forbidden in that baseline.

Mappings are copied and read-only so callers cannot mutate a previously hashed
record. State schema/UUID/path/digest validation exists for supplied records.
The private `.obforce/state.json` wire envelope is implemented internally in
Thread 09, including strict duplicate-key/ID/path validation, bounded loading,
missing/corrupt state refusal and identity reconciliation. It wraps the unchanged
NoteState with exact saved generated-region bytes encoded as canonical base64;
see [SYNC_SAFETY](SYNC_SAFETY.md). Constructing a `NoteState`
is not evidence of a valid discovered vault or safe recovery state.

A unique moved note retains its UUID and source key. Its changed path invalidates
affected links/graph/render fingerprints. Copied IDs, multiple notes for one
component, portable path collisions, edited identities, vanished managed notes,
and ambiguous mapping cause refusal rather than recreation, adoption, or deletion.
Workspace/live-org bindings cannot silently switch; see [source identity](COVERAGE.md).

Render fingerprints include all relevant graph/path, generated-template,
schema/renderer-version, layout, and privacy inputs. A separate creation-only
candidate fingerprint never replaces the generated render hash saved in state.
Collection times, host paths, and response ordering do not enter source hashes;
actual audit dates do. No-op bytes/mtimes must remain unchanged when later sync
is implemented. Notes and their state must ultimately publish through the same
recoverable transaction; per-file replacement alone is insufficient. This thread
provides no vault writes, locks, journals, recovery, or publication commands.

## Relationship invalidation boundary

Thread 06's [internal graph](RELATIONSHIPS.md) derives References and Referenced By
from one directed evidence set, retaining unresolved/unsupported endpoints as labels.
Only explicitly supplied managed-note paths can supply link locations. Graph-only
changes or a neighboring note move change graph fingerprints without changing
component facts/source hashes or note ownership. Coverage/stale changes participate
in invalidation too. Thread 07 renders these explicit mappings; Thread 08 supplies
in-memory preservation. Thread 09 adds read-only state/move discovery; publication remains later work;
this graph neither adopts notes nor writes state.

See [internal rendering](RENDERING.md) for engine-owned YAML/markers, finite Jinja
overrides, candidate bounds, separate creation/generated hashes and independent
coverage invalidation. Whole-new-note candidates must never replace existing notes.


## Internal existing-note parsing and preservation (Thread 08)

`sync/notes.py` accepts immutable caller-supplied note bytes. `parse_note` returns
an immutable observation with exact generated-region bytes and hash, properties,
and byte offsets. `patch_note` also requires a validated **in-memory** `NoteState`,
the exact saved generated-region bytes, and an accepted Thread 07
`GeneratedCandidate`. A whole `NewNoteCandidate` is refused. There is no file/path
input, state-file loading, note/vault discovery, adoption, move reconciliation,
batch planner, publication, locking, journal, recovery or public lifecycle command.
The source binding/selection and provenance of the accepted renderer candidate
remain the caller's responsibility; candidate hashes are not authentication.

The parser verifies an existing canonical lowercase UUID, integer schema 1,
the exact reserved allowlist above, and one ordered generated marker pair at
column zero on separate terminated lines. Unknown `sf_*` keys and any other
`obforce:` occurrence are ambiguous and refused, including occurrences in YAML,
inline/repeated/reversed/nested/malformed markers. It never invents an ID or
infers a rename. Identity/schema edits and source-key/mode mismatches refuse.

Before every patch, **both** current owned properties and current marker-interior
bytes must equal their saved baselines. The saved bytes must also match the
state's SHA-256. FieldValue comparisons retain exact types and presence:
absent, null, false, integer zero, empty string and empty list differ. An
unavailable baseline entry cannot stand in for a present null note property.
Even unchanged metadata, matching incoming source/render hashes, or a current
body hash matching a modified state digest cannot bypass the exact byte comparison.
There is no force mode or destructive fallback.

### Supported frontmatter and finite parsing

A note must be UTF-8 without a BOM/preamble, NUL or bare CR, starting with an exact
`---` line and ending its frontmatter with another exact `---` line. Delimiters
must be terminated. Alternate YAML document delimiters, directives and multiple
YAML documents are unsupported. Unescaped Unicode newline characters/BOM inside
frontmatter are refused; ordinary Unicode text is supported.

The root is a block mapping with simple, nonempty, single-line string keys at
column zero. Quoted keys are supported, including `"null"` and `"false"`; explicit
`?` keys, complex keys and non-string keys are refused. Duplicate keys are refused.

| Form | Supported behavior |
| --- | --- |
| User scalars | Strings, null, booleans, integers up to 64 magnitude bits, finite floats and YAML dates/datetimes; exact original spelling stays in the note |
| Owned scalars | String, null, boolean or bounded integer; strict normalized types match the existing FieldValue contract |
| Lists | Empty or strings only, flow or block; arbitrary lists/nested lists/maps are refused |
| Strings | Plain/single/double quoted, literal/folded multiline, Unicode, chomping/indentation indicators accepted by the parser |
| Comments/presentation | Supported comments, blank lines, order, quoting, indentation and multiline style in user entries are retained by leaving their source bytes untouched |
| Unsupported YAML | All explicit tags, including standard tags, anchors, aliases, merge keys, sets, binary, nested maps, nonfinite floats and arbitrary object constructors are refused |

`ruamel.yaml` is resolved by Poetry as `ruamel-yaml >=0.19.1,<0.20.0`, locked to
0.19.1 without an optional C extension. Each pass uses fresh pure Python
`YAML(typ='rt')` instances, quotes preserved and duplicate keys disabled. The
round-trip loader derives from its safe loader and adds no Python constructors.
A bounded token scan rejects references/tags/directives before loading. Streaming
events enforce depth, node and scalar limits before composition/construction;
the library's own depth guard counts scalar leaves too. Loaded values are
validated against the flat subset, never silently stringified or discarded.

| Refusal bound | Maximum |
| --- | --- |
| Input note / output note | 1 MiB each |
| Input frontmatter / output frontmatter | 64 KiB each |
| Properties | 128 |
| Scanner tokens | 8,192 |
| Parse nodes | 4,096 |
| Collection depth | 2 (root mapping plus a flat sequence) |
| Each scalar / key | 16 KiB UTF-8 |
| Each list | 1,024 strings |

Incoming candidates retain Thread 07's stricter rendering bounds, section/template
validation, scalar types, hashes and required owned identity/source fields.
Bounds refuse rather than truncate. This is finite in-process parsing, not OS
resource isolation or universal YAML support. Official contracts reviewed on
20 October 2026: [round-trip API](https://yaml.dev/doc/ruamel.yaml/api/),
[preservation details](https://yaml.dev/doc/ruamel.yaml/detail/),
[publisher metadata](https://pypi.org/project/ruamel.yaml/),
[YAML 1.2.2](https://yaml.org/spec/1.2.2/) and
[Obsidian properties](https://obsidian.md/help/properties).

### Patch and byte policies

Round-trip node/token source spans select only changed owned values or omitted
owned key/value entries. Changed values use the accepted flat JSON-compatible
YAML encoding. Existing owned key positions remain; newly available keys append
in sorted order. Unchanged owned entries also retain their original bytes.
Comments inside replaced/deleted owned spans survive as standalone comments in
place; an unsupported comment boundary refuses. A comment attached to a deleted
owned value may therefore lose that association, while retaining its text/order.
No user entry is passed through a YAML dumper or the creation template.
This is a precise supported-subset guarantee, not universal byte-identical
frontmatter: changed/deleted/new owned entries can change spelling/spacing and
comment placement. No-op returns the original bytes object exactly. A generated-
body-only update leaves the complete frontmatter bytes untouched.

Both frontmatter (including delimiters) and the marker/interior envelope must be
individually uniform LF or CRLF. They may use different uniform conventions.
Mixed endings within either envelope refuse, including a mixed generated region
that happens to match its baseline. Mixed LF/CRLF in human body regions is allowed
and preserved verbatim. Incoming LF generated text is adapted only to the existing
marker ending. Marker-line bytes, all outside-body bytes, the final newline's
presence/absence and human whitespace remain exact; no document-wide normalization.
The returned baseline/hash cover the resulting exact interior bytes, so a CRLF
output normally differs from the renderer's LF `region_hash`.

`NotePatch` contains only candidate bytes, the next exact property/body baselines,
exact region SHA-256, unchanged candidate source/graph/render digests, and a
byte-change flag. It neither writes nor constructs a state document. The entire
candidate is reparsed and checked against incoming properties/region and retained
user values before return. All nonreserved properties remain user-owned, including
custom `type`, tags, aliases, business fields and every `technical_debt*` property.
Absent/null/false assessments, severity/status and review dates are never inferred
or replaced with creation defaults. Unavailable/absent/null incoming audits follow
the accepted renderer's omission contract: remove omitted owned keys, rather than
inventing null. Audit-name omission remains effective in properties and generated
text; human-authored content is preserved.

Malformed/unsupported notes, invalid markers, edited baselines and identity
conflicts raise concise redacted `ConflictError` (3). Invalid caller/candidate
contracts raise `ModelError` (2), with identity conflicts retaining 3. Parser
messages, note snippets and local paths are never displayed. Existing outcome
precedence stays 3, 2, 1, 4, 0. Thread 08 is accepted at implementation `d79f5e2` /
merge `dba53ab`; #8 is closed. Exact-merge run `39453887153`, attempt 1, passed all
12 Linux/macOS/Windows Python 3.12–3.15 cells: 744 passed per Linux/macOS cell,
732 passed/12 expected skips per Windows cell. Every standalone gate, fresh
build/Twine and all 24 independent guarded installs passed. See the
[acceptance record](../dev/IMPLEMENTATION_PLAN.md#thread-08-acceptance-and-closure--20-october-2026)
for actual evidence and retained historical failures/skips. No real sf/org/vault
access or Windows sf execution qualification follows. Thread 09 internal
[state reconciliation](SYNC_SAFETY.md) is accepted, including correction `890ced2` /
merge `dff34a7`; #9 is closed. Exact-merge run `39502679337`, attempt 1, passed
all 12 cells and all 24 independent installs; see the
[acceptance record](../dev/IMPLEMENTATION_PLAN.md#thread-09-acceptance-and-closure--20-october-2026).
Thread 10 internal read-only planning/reporting is accepted, including correction
`a2132c3` / merge `6004c35`; #10 is closed. All 12 cells and 24 independent installs
passed in exact-merge run `39510802449`, attempt 1; see the
[acceptance record](../dev/IMPLEMENTATION_PLAN.md#thread-10-acceptance-and-closure--20-october-2026).
Thread 11 internal bounded transaction/recovery primitives are accepted, including
correction `4aaeb0f` / merge `2995f93`; #11 is closed. Final exact-merge run
`39676435834`, attempt 2, has all 12 cells and 24 independent installs passing;
see the [acceptance record](../dev/IMPLEMENTATION_PLAN.md#thread-11-acceptance-and-closure--21-october-2026) and
[transaction contract](SYNC_SAFETY.md#thread-11-pre-implementation-transaction-contract--20-october-2026).
Thread 12 is implemented locally pending acceptance; Threads 13–17 and
enhancement #18 remain NOT STARTED.

Thread 10's existing-note candidates always call the preservation patcher after
strict reconciliation; they never use whole-new-note templates. Lifecycle
validation accepts only the already supported `active` and `missing` values;
the planner alone proposes missing after the positive comparable supported live
inventory gate in [SYNC_SAFETY](SYNC_SAFETY.md#thread-10-pre-implementation-planner-contract--20-october-2026).
Both strict owned-property and exact saved-byte comparisons still gate changes.
Source/graph/render hashes retain their meanings; lifecycle candidate values are
compared directly too. User-only changes and creation-template edits cause no
note/state churn. Hash-only generated invalidation can update candidate state
while retaining exact original note bytes. No publication is implemented.

Thread 11's internal writer independently replans explicit inputs before accepting
existing-note patch bytes. It never applies a creation template to an existing
note. Saved properties/exact generated bytes, all user-owned YAML/comments/prose
and technical_debt fields retain the accepted contract. Unique moves are already
user-moved paths; transaction publication reconciles state without renaming notes.
Before-images are private recovery material, never public note baselines.


## Dashboard view of human properties (Thread 14)

The [native dashboard](DASHBOARDS.md) filters only reserved identity/schema and
`sf_type`, with a Markdown extension gate. User `type`, tags and aliases stay
yours and do not control eligibility. The table uses the actual Boolean Technical
Debt property. MTF-2's Boolean false default and blank
human fields apply only to new notes. Date projections extend the reserved
allowlist and renderer fingerprint to version 4, preserving original timestamp
facts and all older exact baselines. The dashboard is a separate whole-file owned asset; note templates,
UUIDs, exact generated baselines and human YAML/prose preservation are unchanged.
