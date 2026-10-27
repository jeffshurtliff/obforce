# Thread 14 dashboard contract

Recorded before dependent implementation on 26 October 2026 under the maintainer's
Thread 14 implementation authorization. This is the bounded design for #14;
acceptance, native Obsidian preview and delivery are separate gates.

## Destination, defaults and presentation

One installed resource, `resources/bases/apex_classes.base`, supplies literal UTF-8/LF
YAML. No Jinja, metadata interpolation, network, process, override discovery or new
dependency. The output is `<layout.dashboards>/Apex Classes.base`, default
`Dashboards/Apex Classes.base`. Reuse the existing config schema 1/layout setting;
no command, flag or config key is added. One dashboard is always included in public
build/sync. Ordinary notes and links remain useful without Bases or any plugin.

Official documentation read on 26 October 2026:
[Bases syntax](https://obsidian.md/help/bases/syntax),
[functions](https://obsidian.md/help/bases/functions), and
[table view](https://obsidian.md/help/bases/views/table).
Use global `filters.and`, string formulas, property display names and one table's
`order`. Filter Markdown, nonempty string `obforce_id`, integer `obforce_schema == 1`
and `sf_type == "ApexClass"`; never user `type`/tags or a path restriction that
would lose moved notes. The view is a convenience, not ownership validation.
`file.asLink()` gives note links; show class, namespace, metadata status, lifecycle,
available Salesforce audit dates and human debt/severity/status/review-date fields.
No filesystem timestamp substitutes for an unavailable audit value. A formula
checks absent/null first, then typed true/false, otherwise labels a custom human
value; never coerce empty/unset to false or assess debt from metadata.

## Explicit versioned state extension proposal

Keep state-document schema **2**, evidence schema **1**, NoteState schema **1**,
renderer version **3**, and journal schema **2**. Add exactly one optional root
`dashboard` object to evidence-bearing schema-2 documents. Its exact shape is:

```text
dashboard: {
    dashboard_schema: 1,
    path: <portable vault-relative .base path>,
    content_hash: <lowercase SHA-256 of exact content bytes>,
    content: <canonical padded base64 of those exact bytes>
}
```

Absence means a valid Thread 13 document with no dashboard ownership. Present
null, unknown schema/keys/types, invalid paths/base64/hash/content or collision
with any note/file-parent is a whole-batch conflict. No human content enters this
record. The content starts with the reserved `# obforce:dashboard:apex_classes:v1`
comment. That marker is an ambiguity indicator, not authority to adopt a file.
Older executables refuse the extra key; use this executable for these vaults and
recovery. Existing schema-1 and schema-2 exact shapes remain readable; legacy
evidence-less public sync still refuses. This explicitly versioned feature
extension adds asset ownership, without converting note/evidence/journal schemas,
adopting files or migrating notes. No backward-writer compatibility is claimed.

## Ownership, existing vaults and complete planning

Public build stays absent/empty-only. On the first sync of a valid Thread 13 vault,
create the dashboard only if its destination is absent and discovery finds no
untracked managed dashboard indicator. Publish the added asset and its record in
one transaction; rollback restores the exact Thread 13 state. Existing notes keep
UUIDs, baselines, human fields and creation-only template behavior.

Discovery reads bounded `.base` files alongside Markdown, under the same full
read/parent/descriptor guards. Any case-insensitive `obforce:dashboard` indicator
requires exactly the tracked path and exact saved bytes. Missing/moved tracked
files, edited bytes (including UI layout edits), duplicate indicators, an unowned
destination (even identical bytes), changed configured destination, portable
case/Unicode aliases, reserved paths and file-parent collisions block the batch.
Do not recreate a missing dashboard, infer moves by hash, adopt a copy, remove an
old dashboard or offer force/reset. Unrelated indicator-free Bases remain untouched.
Users can author an independent indicator-free Base at another path; retaining a
modified generated file requires manual resolution outside automatic sync.

The planner keeps note actions/counts separate from one dashboard action, validates
combined proposed paths/parents, includes asset bytes in aggregate budgets and
all asset observations in preconditions, then serializes the complete state.
An edited note or dashboard blocks **all** changes. The writer independently
replans the whole candidate under continuous ownership; no partial bypass exists.

## Bounds, publication and recovery

One dashboard, at most **16 KiB** exact UTF-8/LF bytes, inside existing 16 MiB state,
64 MiB vault read/candidate, 128 changed-file including state, 32 MiB before-plus-
after transaction, 256 created-parent, 50,000 entry/guard and all path limits.
Read every `.base` within the per-file ceiling; overflow refuses without truncation.
No retries, new skips, bound increases or weaker filesystem guards.

Publish changed notes, then changed dashboard, then complete state, with the same
same-filesystem staging/before-images/journal protocol. The journal's exact shape
and schema 2 remain; semantic validation additionally allows only a `.base` target
associated with the saved dashboard record, exact before/after bytes/hashes and
unchanged tracked path. A dashboard cannot be dropped from state, adopted by a
before-image, or changed through a state-only entry. Recovery validates unchanged
assets too. Phase-permitted removed blobs use existing surviving-target rules;
never fabricate missing evidence. Legacy journal-schema-2 note-only transactions
retain their accepted semantics; journal schema 1 remains refused.

Precommit rollback restores the old dashboard/state, or removes only a proven new
asset. Committed recovery cleans only owned temporary evidence. Intervening asset,
note, state or parent edits retain recovery-required evidence. Full pathname and
historical descriptor stamps, Windows birthtime bridge, owning-handle lock reads,
immediate hash/absence checks and exact parent deltas are mandatory. No atomic
snapshot, atomic multi-file, hostile-editor or power-loss guarantee is added.

Previews create nothing, including absent output parents. Unchanged asset/note/
state no-ops preserve bytes/mtimes; no run timestamps. Precedence stays **3,2,1,4,0**.
Summaries use bounded fixed categories, separate note/dashboard/state counts,
independent coverage explanations and actionable recovery/conflict guidance.
Optional verbose enhancement #19 remains unstarted. Threads 15–17 and #18 remain
NOT STARTED. No real sf/Obsidian/org/vault/settings access is authorized here;
automated YAML/schema tests are not native Obsidian rendering evidence.

## MTF-2 triage and correction plan — 26 October 2026

Maintainer finding committed at `0ad3add` requests dashboard presentation and new
note properties within Thread 14. Preserve that finding and the existing candidate.
No later thread, real app/vault access, settings change or automatic migration.

- Merge Note/Class into a Class link via `file.asLink(note.sf_full_name)`; keep
  location-independent links. Add API Version from the existing version string,
  without JSON/string quoting as presentation. Apply requested column labels.
- Remove Lifecycle from the default table. Retain `sf_lifecycle` in notes/state:
  active/missing supports accepted comparable-scan absence/reactivation behavior;
  it is not Salesforce Metadata Status or a safe field to delete from that contract.
- Add reserved date-only projections `sf_created` and `sf_last_modified` from
  available valid timestamp facts already retained as `created_at` and
  `last_modified_at`. Preserve existing `sf_*_at` timestamps, facts/evidence,
  source/graph hashes and acquisition. Never use filesystem dates or collect more
  fields. Unavailable/absent/null/non-date values do not produce invented dates.
- New human defaults: `tech_debt_severity: ""`, `tech_debt_status: ""`,
  `last_reviewed: null` (blank, later YYYY-MM-DD). Recommend High/Medium/Low severity
  without constraining or overwriting human choices. Use those names in the Base.
  Existing `technical_debt*` and other human keys stay untouched; no automatic
  rename, copy, backfill or transfer of ownership. New defaults apply only during
  creation; existing notes remain generated-only patches.
- The requested Boolean debt default conflicts with the original absent/null
  unassessed default. Asked the maintainer whether to use false for new notes
  while preserving/distinguishing legacy null/custom values, or retain unassessed
  creation defaults. That dependent decision remains pending at this checkpoint.
  No existing human assessment will be converted, dropped or overwritten.
- Proposed renderer fingerprint version **4** for new generated date properties;
  note/marker/config/model/NoteState/state-document/evidence/journal/dashboard
  schemas remain unchanged. Legacy exact baselines remain readable and gate every
  patch; property/body edits remain conflicts. A clean dashboard updates only by
  exact saved-byte ownership through the accepted transaction with complete state.
- Current official Bases function/property documentation rechecked: optional
  `asLink` display text, native true/false checkbox values, date YYYY-MM-DD values
  and vault-wide property typing. No `.obsidian` property-type settings may be
  written. Native rendering of these changes remains unavailable to the agent;
  the maintainer's initial manual observation is distinct evidence.

This checkpoint records the intended correction before dependent implementation.
The new renderer/date projection and human defaults require focused preservation,
legacy-baseline, dashboard schema/filter/column, no-op/recovery, installed-asset
and fresh artifact checks. Historical failures and qualification limits remain.

### Preliminary MTF-2 default resolution (superseded below)

The finding itself explicitly requests a Boolean unchecked default, and the
maintainer directly authorized action on that finding. The earlier clarification
was unnecessary for new-note creation; no answer or approval is inferred from
elapsed time. Apply `technical_debt: false` only to new notes and require actual
Boolean creation overrides. Existing absent/null/custom values remain valid
human content and are never converted or refused merely for that value.

The main table uses the actual `note.technical_debt` column, labeled Technical
Debt, without the previous assessment/raw-value pair. A second small table,
Unassessed or legacy debt, filters non-Boolean values and labels absent/null
Unassessed and other existing values Custom value. It preserves the original
requirement to distinguish those from false despite native checkbox ambiguity.
Its global managed identity/type filters remain identical. No property settings
are written. Renderer version **4** and the new reserved date aliases supersede
the initial version-3 presentation contract above; other schema versions/bounds
and all accepted transaction/ownership behavior stay unchanged. Earlier executables
refuse new reserved date fields as well as the dashboard state extension.

### Explicit maintainer MTF-2 correction

The maintainer answered the clarification: use `technical_debt: false` throughout
the fictional/example/test data without preserving historical data. This is
explicit authorization to supersede the initial unassessed-default contract for
this unreleased dataset. Use one table and no debt-assessment formula or legacy
view. The actual Technical Debt property is Boolean, false by default; human true
remains valid. Update synthetic baselines directly, without adding an old-v3
data snapshot or a separate historical expected-output fixture. Accepted older
generated-region/state readability tests remain, using Boolean fictional data.

This does not authorize real-vault migration/adoption, automatic human-field
conversion or whole-note recreation. All other bounds, ownership, baseline,
publication/recovery and version-4 date projection decisions remain unchanged.

## Acceptance — 27 October 2026

Thread 14 is accepted and #14 closed at Windows path correction `6d08696` /
merge `cdf0e68`. Exact-merge run `40517073513`, attempt 1, passed every required
command in all 12 Linux/macOS/Windows Python 3.12–3.15 cells and 24 independent
installs. The final contract includes the explicit MTF-2 Boolean false defaults,
single table, renderer 4 date projections and unchanged transaction safety/bounds.
Native Obsidian preview was optional and remains unavailable, not a rendering
pass. Earlier proposals and failures above remain historical. See the
[acceptance record and Thread 15 handoff](IMPLEMENTATION_PLAN.md#thread-14-acceptance-and-closure--27-october-2026).
Thread 15 and later/enhancements #18/#19 remain NOT STARTED.
