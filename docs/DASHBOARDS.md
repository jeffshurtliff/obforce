# Native Apex Classes dashboard

Build creates `Dashboards/Apex Classes.base` by default. Open it yourself in an
Obsidian installation with the native Bases feature available. Obforce never
launches Obsidian, enables features, installs plugins or changes `.obsidian`.
Ordinary Markdown notes, human sections, properties and links remain useful
without dashboards, Dataview, Obsidian CLI or community plugins.

The table includes a **Class** link labeled with the class name, Namespace,
Metadata Status, API Version, Created, Last Modified, Technical Debt, Debt
Severity, Debt Status and Last Reviewed. Links use each file's current location,
including uniquely moved notes. API Version uses the stored text value (`67.0`),
without adding quote characters. YAML quotes delimit that value in note source.
Missing audit dates stay blank; filesystem dates are not Salesforce audit dates.
Read each note's Coverage section for independent inventory/audit/relationship
limitations. `sf_lifecycle` remains in notes for accepted active/missing behavior,
but is omitted from the default table. Missing means unobserved in a comparable
accessible scope, not deletion; it differs from Salesforce Metadata Status.

Filtering uses Markdown plus reserved `obforce_id`, `obforce_schema: 1`, and
`sf_type: ApexClass`. Changing your `type` or `tags` does not hide a managed note.
The view is a convenience; its filter does not establish filesystem ownership.
Technical Debt uses the actual `technical_debt` property, suitable for a native
checkbox. Per maintainer finding MTF-2, new notes default to Boolean `false`
(unchecked); that initial default is not a metadata-derived assessment. Only
Boolean creation overrides are accepted. The maintainer explicitly replaced the
earlier unassessed-default proposal for this unreleased, fictional dataset:
examples and test baselines now use false, with one table and no legacy view.
Human Boolean decisions remain user-owned during generated-only refresh.

New notes also initialize user-owned `tech_debt_severity: ""`,
`tech_debt_status: ""` and `last_reviewed: null`. Recommend `High`, `Medium` or
`Low` severity; enter a review date as `YYYY-MM-DD`. Existing notes are never
backfilled, renamed or converted: earlier `technical_debt_severity`,
`technical_debt_status`, `technical_debt_review_date` and all other human fields
stay yours. The new columns use only the requested new names. Metadata never
sets severity, status or review dates. Created/Last Modified use reserved
`sf_created`/`sf_last_modified`, UTC date-only projections of available valid
Salesforce audit timestamps. The original `sf_*_at` values remain available.

Obsidian property types are vault-wide. If your vault already assigns another
type, you can review it yourself in Obsidian: Checkbox for `technical_debt`, Date
for the date properties, Text for API Version and human severity/status. Obforce
never changes property-type settings. Native display and existing vault type
interactions still need maintainer confirmation.

The literal packaged YAML uses documented filters, formulas and table columns.
See official [syntax](https://obsidian.md/help/bases/syntax),
[functions](https://obsidian.md/help/bases/functions) and
[table documentation](https://obsidian.md/help/bases/views/table) and
[property types](https://obsidian.md/help/properties), read on
26 October 2026. Automated schema/predicate tests do not constitute native
Obsidian preview or rendering acceptance. The maintainer's original manual
observation is recorded as MTF-2; native confirmation of this correction remains
pending. Preview was unavailable to the agent; no real vault or app was opened
by the agent.

## Destination and ownership

The existing config setting controls the parent directory:

```toml
[layout]
apex_classes = "Custom Code/Apex Classes"
dashboards = "Dashboards"
```

The filename is fixed: `Apex Classes.base`. One dashboard participates in every
public build/sync. No new config key, lifecycle command or template override exists.
After creation, changing the configured dashboard directory refuses; Obforce does
not infer a dashboard move, copy it to a second location or remove the old file.

The whole generated `.base` file is protected, including layout edits made by
Obsidian's UI. Current bytes must exactly match saved bytes before any batch can
publish. Edits, missing/moved files, duplicate managed indicators, unowned targets
(even identical content), links/hard links/reparse points, unsafe parents or
portable spelling collisions return conflict 3. One dashboard or note conflict
blocks all note, dashboard and state changes. Preserve your edits and resolve
ownership before running another preview; there is no reset, overwrite, adoption
or repair mode. For a custom view, author a separate indicator-free Base at another
path and retain the generated file unchanged. Do not copy its reserved
`obforce:dashboard` ownership comment into a user-managed view.

Valid Thread 13 state-document-schema-2 vaults have no dashboard record. Their
first sync creates the new dashboard only when its destination is absent and
there is no untracked managed dashboard indicator. It preserves existing UUIDs,
notes and human fields. It never adopts an existing file. Evidence-less legacy
sync remains refused, and build still requires an absent/empty destination.
This adds an asset, without migrating notes or reconstructing prior evidence.

## State, recovery and previews

An optional exact-shape root `dashboard` record extends evidence-bearing state
schema 2. It has `dashboard_schema: 1`, a portable relative `path`, `content_hash`
(SHA-256) and canonical base64 `content` holding exact bytes. No human note data
is added. Evidence schema 1, NoteState schema 1 and journal schema 2 remain;
MTF-2 advances the renderer fingerprint to version 4 for date projections.
Older executables reject the extra state key/new reserved date properties; use this version
for these vaults and recovery. Unknown keys/versions/types or corrupt baselines
refuse. See [the recorded contract](../dev/THREAD_14_DASHBOARD_CONTRACT.md).

Changed notes, dashboard, then complete state use the same recoverable writer.
The dashboard has the same full pathname/historical descriptor/hash/absence/parent
checks and continuous writer lock. Precommit rollback restores prior bytes/state,
or removes only a proven newly created asset; committed cleanup removes only
transaction-owned temporary material. Intervening edits retain evidence and
refuse. Valid old note-only journal-schema-2 recovery remains supported;
journal schema 1 remains refused. No atomic multi-file, hostile-race, power-loss
or Windows Salesforce execution guarantee is added.

```sh
obforce sync --config "./Demo Config.toml" --dry-run
obforce sync --config "./Demo Config.toml"
obforce recover --config "./Demo Config.toml"
```

Recovery preview names the phase-compatible `--rollback` or `--cleanup` operation.
Review it before applying that operation with the same explicit config. Ambiguous
or incomplete evidence needs manual resolution, without deleting control files to
bypass checks. All previews create no Obforce files/directories. Unchanged
notes/dashboard/state preserve exact bytes/mtimes; reads may update access times.

One dashboard is limited to 16 KiB. Every discovered `.base` is read under that
ceiling and the shared 64 MiB aggregate read ceiling. State remains at most
16 MiB; the dashboard counts inside the existing 128 changed-file, 32 MiB
before-plus-after transaction and 64 MiB candidate limits. All other entry,
path, JSON, parent and guard limits still apply. Bounds refuse, never truncate.
Reports distinguish note actions, dashboard action, state-file changes and total
changed files. Init's file count is its new config; recovery counts journaled
files; no-op is zero. Counts and coverage explanations stay bounded and omit
private names/paths/audit identities/raw warnings. Exit precedence is **3,2,1,4,0**.
Optional verbose enhancement #19 remains unstarted.

Try the [fictional quickstart](QUICKSTART.md). A read-only
[presentation sample](../examples/sample_vault/README.md) contains no private
state and is not a build/sync target. Actual local/hosted/native evidence and
acceptance status are recorded in the [roadmap](../dev/IMPLEMENTATION_PLAN.md).
