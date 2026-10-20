# Note ownership and state contract

Thread 02 freezes constants, normalized state records, and fingerprint inputs.
It does not render or parse Markdown/YAML, discover notes, load state documents,
reconcile moves, or publish files. Thread 07 now [renders candidate strings](RENDERING.md); existing-note parsing,
state/discovery, planning and publication remain Threads 08–13. This fictional note illustrates the version-one contract, not generated
output from a working command.

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
technical_debt: null
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

The whole `sf_*` namespace is reserved. An unknown `sf_*` key is unsupported and
must be refused rather than adopted or overwritten. Every other key belongs to
the user after creation, including `type`, `tags`, `aliases`, business fields,
all `technical_debt*` fields, and arbitrary custom properties. Creation defaults
do not transfer their ownership. Unassessed technical debt may be absent or null;
it is never automatically converted to false, a severity, or a review decision.

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
existing-note parsing remains Thread 08.

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
Thread 08 must establish supported round-trip forms and refuse unsafe forms.

## Internal state and invalidation

`NoteState` stores UUID, binding, structured component key, portable vault-relative
path using `/`, source/graph/generated-render hashes, exact owned-property
baseline, and generated-region SHA-256. Baseline values use the normalized
availability wrapper, distinguishing an absent key, null, empty, false, and
unavailable. Identity/schema baseline entries must exactly match the note UUID
and supported note schema. User-owned properties are forbidden in that baseline.

Mappings are copied and read-only so callers cannot mutate a previously hashed
record. State schema/UUID/path/digest validation exists for supplied records.
The future `.obforce/state.json` document remains private, with schema validation,
duplicate-key/ID/path detection, bounded loading, missing/corrupt state refusal,
and identity reconciliation belonging to Thread 09. Constructing a `NoteState`
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
in invalidation too. Thread 07 renders these explicit mappings; state/move discovery, preservation
and publication remain later threads; this graph neither adopts notes nor writes state.

See [internal rendering](RENDERING.md) for engine-owned YAML/markers, finite Jinja
overrides, candidate bounds, separate creation/generated hashes and independent
coverage invalidation. Whole-new-note candidates must never replace existing notes.
