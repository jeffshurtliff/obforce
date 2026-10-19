# Obforce v0.1.0 implementation roadmap

**Planning baseline:** 18 October 2026

**Target release:** `0.1.0`; initial development version: `0.1.0.dev0`

**Status:** Thread 01 is **accepted and complete**, including the delivered
Windows test correction and all 12 passing hosted CI cells. Issue #1 is closed
as completed. Thread 02 is **accepted and complete**, including delivered
correction `65305fb` and all 12 passing hosted cells with standalone Windows
formatting checks. Issue #2 is closed as completed. Thread 03 is **delivered;
Windows CI correction locally verified; corrected hosted CI pending**, with acceptance withheld. Issue #3 remains
open. Threads 04–17 are **not started**.

**Repository location:** `dev/IMPLEMENTATION_PLAN.md`

This document describes Obforce's purpose, product boundaries, proposed technical
contracts, and a sequence of bounded implementation threads. It is intended to
be maintained alongside the code as implementation and decisions evolve.
[Root AGENTS.md](../AGENTS.md) governs agent participation. Read root
`CONTRIBUTING.md` when it exists; Thread 01 establishes it if absent.

The plan is a design proposal, not evidence of working functionality or blanket
authorization to implement it. Asking for one thread authorizes that thread and
its necessary subtasks. It does not start later threads, authorize live Salesforce
access, or authorize commits, publication, or release operations.

## 1. Purpose and intended outcomes

Obforce creates and maintains living documentation for a Salesforce org within an
Obsidian vault. It combines facts available from Salesforce metadata with the
institutional knowledge administrators add themselves. The result should help an
administrator understand what exists, how components relate, who changed them,
and what business context or technical debt deserves attention.

The long-term objective is broad org documentation and mapping. The first release
is a useful, deliberately limited foundation for that objective; it must not
claim to document every Salesforce metadata type or discover every dependency.

### Primary users and workflows

- **Salesforce administrators:** Select an already authenticated org, generate
  useful component notes with minimal setup, and refresh them as the org changes.
- **Developers and architects:** Document a local Salesforce DX project offline,
  inspect relationships and provenance, and enrich component notes with design
  decisions, business ownership, and operational knowledge.
- **Knowledge maintainers:** Search, follow links and backlinks, use native
  Obsidian properties and Bases, and trust that their writing survives refreshes.

### Product objectives

1. Produce readable Markdown with YAML properties and useful internal links.
2. Describe components rather than copy Apex source code into documentation.
3. Support both a live Salesforce input and a local project input through one
   normalization, rendering, and synchronization pipeline.
4. Preserve user properties and narrative content during every refresh.
5. Explain missing information, partial coverage, and relationship provenance.
6. Keep operation local, deterministic, testable, and independent of AI services.
7. Minimize total cost of ownership: one Python package, existing Salesforce CLI
   authentication, a small dependency set, and no hosted infrastructure.
8. Allow useful customization without requiring users to learn templates before
   their first successful build.

### Observable success for v0.1.0

A user can install Obforce, point it at a synthetic local project or an explicitly
selected authenticated org, preview a build, and create one note per supported
Apex class. They can add business context, custom properties, and technical debt
notes; move a note within the vault; then preview and apply a refresh without
losing those edits. Unchanged output remains untouched. Conflicts and incomplete
inputs produce clear results. Interrupted publication can be recovered safely.

## 2. Evidence, decisions, and planning assumptions

### Source discussions

This roadmap synthesizes the project conversations titled **Salesforce Obsidian
Architecture Advice** and **Obforce Recommended File Structure**, including the
technical-debt-property discussion. The Obfuscidian implementation roadmap was
used as an organizational example: central contracts, dependency-aware threads,
acceptance criteria, validation, prompts, and handoff records. Its encryption,
backup format, release history, and project-specific rules do not transfer here.

Some prior answers contained rendered diagrams or examples that were not included
in the accessible conversation text. The concrete contracts below fill those
gaps as new proposals; they are not verbatim recovered decisions.

### Explicit direction and observed repository baseline

| Area | Evidence or direction |
| --- | --- |
| Project intent | Generate and refresh Salesforce component documentation in an Obsidian vault; combine metadata with human knowledge |
| Content | Component facts, creation/modification audit information where available, usage, dependencies, links, and searchability; exclude Apex source from notes |
| Tooling | Maintainer specified Poetry and Python 3.12 or newer |
| Repository | Local checkout contains `README.md`, `.gitignore`, `LICENSE`, and Git metadata; no application package or `pyproject.toml` was present at planning review |
| License | Existing root `LICENSE` contains Apache License 2.0; preserve it and align future package metadata |
| Contributor guidance | No root `AGENTS.md` or `CONTRIBUTING.md` existed in that checkout at review |
| Private references | `local/vendor_docs/` was absent at review; check again when implementing |
| Implementation evidence | No Obforce application tests or builds existed to run; none are claimed by this planning handoff |

These observations are a dated baseline. Reinspect the actual checkout before
implementation and preserve changes made since this review.

### Confirmed v0.1.0 scope

**Maintainer decision — 18 October 2026:** Use the focused Apex-first release:
Apex class notes, live Salesforce and offline project inputs, dependency links
where available, and safe initial build/refresh workflows. Additional metadata
note types are deferred to later releases. This confirmation sets the product
scope; all 17 implementation threads remain not started.

### Proposed implementation defaults

The following defaults implement the confirmed scope. Detailed technology,
schema, CLI, and workflow choices remain recommendations informed by the earlier
discussions unless explicitly confirmed above. A direct maintainer correction
supersedes them. Record material changes before implementing dependent work.

| Decision | Proposed v0.1.0 baseline |
| --- | --- |
| Product form | Python CLI with reusable internal modules; no stable public Python API promise yet |
| First metadata type | `ApexClass` (confirmed scope); additional note types follow in later releases |
| Inputs | Live org through existing `sf` authentication; local Salesforce DX source project without network access |
| Live acquisition | Query selected ApexClass audit/identity attributes through Salesforce CLI; avoid retrieving class bodies when they are unnecessary |
| Relationships | Best-effort platform-reported relationships through an isolated adapter; no comprehensive Apex static analyzer |
| Presentation | Markdown, flat YAML properties, wikilinks, and a small native Bases dashboard |
| Templates | Bundled Jinja2 defaults plus explicitly configured local overrides |
| Synchronization | Generated-field/region ownership, persistent note identities, hashes, preflight plans, and recoverable writes |
| Missing components | Mark as missing only after a comparable complete supported scan; never delete notes automatically |
| Technical debt | User-managed Boolean, optional severity/status/review date, and narrative section; unset means unassessed |
| Configuration | One TOML file; relative paths resolve from its directory |
| Platform target | Linux, macOS, and Windows; target stable Python 3.12–3.15, verifying interpreter/dependency availability and recording gaps |
| Release | Prepare `0.1.0` after acceptance; publication requires a separate explicit instruction |

**Scope gate:** The focused Apex-first release is confirmed. Adding objects,
fields, Flows, or LWC to `0.1.0` requires a new maintainer decision and revisions
to the scope table, component contracts, acceptance matrix, and thread
dependencies before coding. Do not insert additional metadata types into a
parser thread without that decision.

### In scope for v0.1.0

- Installable Poetry package using `src/obforce/`, with `obforce` and
  `python -m obforce` entry points.
- Explicit source and destination configuration, preflight, actionable errors,
  and noninteractive operation without hidden prompts.
- Offline Apex class inventory from the package directories declared in
  `sfdx-project.json`, including their `.cls-meta.xml` metadata.
- Live Apex class identity, namespace, API version, status, audit dates, and
  creator/modifier labels when available and permitted.
- Platform dependency edges when supported and available, with coverage and
  provenance; reciprocal links between documented classes.
- Safe initial build and refresh, user-owned content preservation, note-move
  detection, no-op behavior, explicit conflict reporting, and crash recovery.
- Custom creation/generated-section templates, default user sections, a small
  dashboard, synthetic examples, docs, and offline automated tests.

### Explicitly deferred

- Other component note types: objects/fields, triggers, Flows, LWC/Aura, permission
  sets/profiles, reports/dashboards, layouts, integrations, and installed-package
  internals. Keep the model extensible without claiming support.
- Exhaustive impact analysis, runtime dependency guarantees, Apex parsing/static
  analysis, Bulk API dependency collection, and AI-generated explanations.
- Hybrid live enrichment of local projects, automatic identity reconciliation
  across orgs, automatic Salesforce component rename detection, and multiple orgs
  managed by one vault. Use separate vaults in the first release.
- Incremental Salesforce retrieval/source tracking, background watchers,
  scheduling, hosted services, an Obsidian plugin, an AI skill, or an `sf` plugin.
- Customer/business record exports, Apex execution, org deployment or mutation,
  custom OAuth/token storage, and automatic Salesforce authentication.
- General Markdown three-way merging, automatic overwrite of conflicts,
  automatic note deletion, Git branch/worktree management, commits, or pushes.
- A stable public Python library API, automatic state migrations, template export
  command, dedicated technical-debt records, or required Dataview integration.

## 3. Architecture and repository organization

### Processing boundaries

```text
Local DX project ----+
                    +--> source result --> normalized components + coverage
Salesforce CLI -----+                              |
                                                   v
                                       dependency graph + provenance
                                                   |
                                                   v
Packaged/local templates -----------------------> renderer
                                                   |
Current notes + prior state --> preservation --> change planner
                                                   |
                                   dry-run report / validated change set
                                                   |
                                                   v
                                    transaction writer + recovery
                                                   |
                                                   v
                                       Markdown vault + state
```

Sources do not generate Markdown. Templates do not interpret raw Salesforce
responses or XML. The renderer proposes output; only the synchronization writer
publishes it. Keep the CLI thin and the core usable from deterministic tests.

### Target repository layout

Create modules only when their thread needs them; this is not a request for empty
scaffolding in every directory.

```text
obforce/
  AGENTS.md
  CONTRIBUTING.md
  README.md
  LICENSE
  SECURITY.md
  pyproject.toml
  poetry.lock
  dev/
    IMPLEMENTATION_PLAN.md
  docs/
    CHANGELOG.md
    CONFIGURATION.md
    COVERAGE.md
    NOTE_FORMAT.md
    SYNC_SAFETY.md
    maintainers/
      releasing.md
  src/obforce/
    __init__.py
    __main__.py
    cli.py
    config.py
    constants.py
    errors.py
    models.py
    sources/
      local.py
      sf_cli.py
      live.py
    parsers/
      apex.py
    graph/
      dependencies.py
    renderer/
      templates.py
      notes.py
      dashboards.py
    sync/
      notes.py
      state.py
      planner.py
      transactions.py
      engine.py
    resources/
      templates/
        apex_class.create.md.j2
        apex_class.generated.md.j2
      bases/
        apex_classes.base
  tests/
    unit/
    integration/
    fixtures/
      salesforce/
      vaults/
  examples/
    obforce.example.toml
    sample_sfdx/
    sample_vault/
  .github/workflows/
    test.yml
  local/                         # ignored private material, if needed
```

Use `models.py` for a few focused dataclasses initially. Split it only when the
actual implementation benefits. Likewise, one graph module and one Apex parser
are sufficient; avoid a plugin framework before a second source/type requires it.

### Packaging and dependency policy

Use Poetry 2.x, `poetry-core`, static PEP 621 metadata, Python `>=3.12`, a checked-in
Poetry-generated lockfile, and one authoritative runtime dependency declaration.
Keep version metadata in one source. Resolve and test actual package versions in
Thread 01 rather than copying illustrative constraints from prior conversations.

Python 3.15 is already stable at this planning date; see the official
[Python 3.15.0 release](https://www.python.org/downloads/release/python-3150/).
Evaluate its stable CI interpreter availability and dependency compatibility in
Thread 01 rather than carrying forward another project's older matrix. The
target is Python 3.12 and newer; unavailable or failing matrix cells remain
explicit qualification gaps, never assumed passes or advertised support.

Proposed runtime dependencies are Click, Jinja2, `ruamel.yaml` for comment-aware
frontmatter editing, and `defusedxml` for bounded, non-expanding XML parsing.
Evaluate a small maintained cross-platform locking dependency only if required
by Thread 11; do not implement a general lock service. Use standard-library TOML,
JSON, hashing, paths, subprocesses, and package resources elsewhere. Keep pytest,
coverage, Ruff, Bandit, and Twine in development groups.

Templates and Bases must be available from installed wheels and sdists, not only
from the checkout. Explicitly verify both artifact formats: Poetry's `include`
entries default to sdist unless formats are specified. See the official
[Poetry packaging configuration](https://python-poetry.org/docs/pyproject/#exclude-and-include).
Load assets using
[importlib.resources](https://docs.python.org/3.12/library/importlib.resources.html),
without assuming a working directory or writable installation directory.

## 4. Sources, normalized data, identity, and coverage

### Source contract

Each source returns normalized components, source identity, a selection/scope
fingerprint, field availability, warnings, and explicit collection coverage.
Never infer completeness from an empty list or a successful process exit alone.

**Offline source:** Read `sfdx-project.json` and supported source-format metadata
under its declared package directories. Read inputs without modifying them.
Validate package paths, duplicate components, XML structure, sizes, and metadata
pairs. A local checkout is evidence of what it contains, not a complete org scan.
Filesystem creation/modification times and Git commit dates are not Salesforce
audit dates. Missing audit fields remain unavailable, not fabricated.

**Live source:** Require an explicit org alias/username selected in configuration
or the invocation; do not silently use the machine's default target. Reuse `sf`
authentication and obtain org identity through a minimal read-only query that
does not request credentials. Query selected ApexClass fields, pagination, and
audit labels without requesting `Body`. The official
[ApexClass field reference](https://developer.salesforce.com/docs/platform/field-reference/references/field-reference/salesforce-field-reference-apexclass.html)
lists the identity, namespace, API version, status, and audit fields that inform
this selection. Verify actual permissions and response shapes during the live
adapter thread.

Use subprocess argument lists, an identified executable, fixed command families,
explicit timeouts, bounded output, and JSON results. No shell interpolation or
arbitrary command configuration. The documented
[`sf data query`](https://developer.salesforce.com/docs/platform/salesforce-cli-reference/guide/cli_reference_data_query.html)
supports explicit targets, JSON, and Tooling API queries; the adapter must test
the installed command/plugin behavior rather than assume a response envelope.

Do not run login, token display, Apex execution, deploy, destructive metadata,
plugin install/update, or Salesforce configuration changes. Live integration
testing requires explicit authorization for the selected org and operations.

The first release does not need whole-org source retrieval merely to document
Apex audit facts. Future retrieval adapters must write into disposable Obforce
staging rather than a user's source checkout: Salesforce documents that
[`project retrieve start`](https://developer.salesforce.com/docs/platform/salesforce-cli-reference/guide/cli_reference_project_retrieve_start.html)
can overwrite local files and depends on a project context.

### Normalized component and relationship records

Thread 02 implements the version-one internal model below; exact normalization,
availability, and hash inputs are frozen in [COVERAGE.md](../docs/COVERAGE.md).
Acquisition, graph construction, rendering, and persisted-state loading remain
with their owning later threads.

| Record | Required concepts |
| --- | --- |
| Component | Source/workspace identity, metadata type, namespace, full name, optional Salesforce record ID, allowlisted attributes, field availability, provenance, canonical source hash |
| Coverage | Selected types and filters, scope fingerprint, completion/partial/unavailable state, pagination/limit outcome, warnings, API version, collection method |
| Relationship | Source and target canonical keys, relationship kind, evidence method, coverage, and unresolved endpoint information |
| Note state | Persistent Obforce note ID, source identity mapping, vault-relative path, source/graph/render fingerprints, last generated-property baseline and generated-region hash |

Canonicalization must preserve meaningful distinctions. Use unambiguous structured
serialization for keys and hashes, not delimiter concatenation that can collide.
Exclude volatile collection timestamps, response ordering, machine paths, and
incidental CLI data from content hashes. Distinguish unavailable, empty, and
known-false values. Keep attributes allowlisted; do not dump arbitrary API fields
into frontmatter.

### Persistent identity and note moves

- Bind each managed vault to one configured `workspace_id`. A live source also
  binds it to the verified org ID; an alias is not an org identity.
- Give every component note a persistent `obforce_id` independent of its filename.
  Map it to a canonical source key of workspace, type, namespace, and full name,
  supplemented by a Salesforce record ID when available.
- Preserve case and namespace distinctions in identities even on filesystems
  that cannot represent all names distinctly; report naming collisions.
- Match moved/renamed Markdown files through their unique `obforce_id` within the
  configured vault, then update state and generated links to the actual location.
- Duplicate note IDs, duplicate canonical component mappings, edited identities,
  and ambiguous matches block the run before publication.
- A Salesforce component rename is distinct from moving a note. Do not infer it
  from similar names or source text in v0.1.0.
- Switching between live and offline sources is not automatically safe. Require
  an explicit configuration/rebinding decision and verified identity mapping;
  refuse unsupported switches rather than creating duplicates or retiring notes.
- A vanished managed note is a conflict, not permission to recreate or delete it.
  Resolve it explicitly; never silently adopt an unrelated preexisting note.

### Dependency graph and truthfulness

Maintain directed edges and derive reciprocal **References** and **Referenced
By** sections from the same graph. If class A begins referencing B, B may require
regeneration even if B's own metadata hash is unchanged. Include relevant graph
and target-location changes in render invalidation.

For v0.1.0, collect platform-reported edges when available. Render an internal
link only when an endpoint resolves to a managed note. Present unsupported or
unresolved endpoints as clearly labeled text, with type and provenance, rather
than manufacturing empty notes or promising those components are documented.
Do not label a platform-reported relationship as a proven runtime dependency.

The current `MetadataComponentDependency` reference was not readable beyond its
page shell during this planning review. Prior discussions mentioned beta status
and query limits; **those exact claims are not treated as currently verified**.
Thread 06 must verify API availability, supported types, permissions, limits,
filtering, and pagination against the official
[MetadataComponentDependency reference](https://developer.salesforce.com/docs/atlas.en-us.api_tooling.meta/api_tooling/tooling_api_objects_metadatacomponentdependency.htm)
and the installed CLI. Never use a fixed presumed record limit as evidence that
all edges were collected. Truncation, unsupported queries, and permission failures
produce explicit partial/unavailable dependency coverage.

Offline Apex XML does not establish Apex code references. Report relationships
as not collected for that source instead of claiming there are none. If a later
live dependency refresh fails, preserve prior known edges as stale with their
previous provenance; do not erase them by treating a failed query as an empty
graph. Basic component documentation may proceed when optional relationship
collection is unavailable, but the command must report that limitation.

## 5. Vault, templates, and content ownership

### Generated vault layout

Keep generated customer/org documentation separate from the application repo.
Default example, with configurable note and dashboard folders:

```text
Org Knowledge/
  Custom Code/
    Apex Classes/
      OrderProcessingService.md
  Dashboards/
    Apex Classes.base
  .obforce/
    state.json
    transactions/               # only while applying/recovering a write
```

Do not create, install, or alter `.obsidian/` settings or community plugins.
User templates may live anywhere explicitly configured and safe; a vault
`Templates/` directory is optional and user-owned. Caches, raw org responses,
journals, and generated org documentation do not belong in the application repo.
Document the privacy and backup implications of `.obforce/` rather than silently
editing a user's Git ignore rules.

### Frontmatter ownership

| Properties | Owner and update policy |
| --- | --- |
| `obforce_id`, `obforce_schema` | Reserved identity/schema fields; validate and preserve identity |
| `sf_*` | Generator-owned Salesforce facts and explicitly documented collection/lifecycle fields; update only against the saved baseline |
| `type` | Optional creation default such as `salesforce_component`; user-owned after creation |
| `tags`, `aliases`, business fields, arbitrary other keys | User-owned; preserve on refresh |
| `technical_debt*` | User-owned; never inferred from metadata or automatically classified |

Use flat Obsidian-compatible scalars and lists. Quote wikilinks stored as YAML
values, consistent with the official
[Obsidian properties guidance](https://obsidian.md/help/properties). Keep complex
graph/provenance objects in internal state and the generated body rather than
unsupported nested property structures.

The exact version-one generated Salesforce fields are `sf_type`, `sf_full_name`, `sf_namespace`,
`sf_api_version`, `sf_status`, `sf_created_at`, `sf_created_by`,
`sf_last_modified_at`, `sf_last_modified_by`, `sf_source_mode`,
`sf_dependency_coverage`, and `sf_lifecycle`. Unknown reserved `sf_*` properties
require refusal. See [NOTE_FORMAT.md](../docs/NOTE_FORMAT.md) for the frozen
ownership/schema contract; parsing/rendering remain planned. Omit unknown audit values and explain
their availability in the generated section. Exclude unnecessary emails,
usernames, URLs, org IDs, and raw record IDs from notes; state may retain the
minimum identities needed for matching. Allow audit-name omission for privacy.

Defaults for new user fields may include `business_owner`, `documentation_status`,
`reviewed_by`, and the following optional technical debt fields:

| Field | Suggested convention |
| --- | --- |
| `technical_debt` | Boolean when assessed; omit or leave null when unassessed |
| `technical_debt_severity` | `low`, `medium`, `high`, `critical` |
| `technical_debt_status` | `identified`, `planned`, `in_progress`, `resolved`, `accepted` |
| `technical_debt_reviewed` | Date of the human review |

These are helpful conventions, not permission to rewrite user values or reject
an otherwise valid note because a user chose a different business vocabulary.
Unset is not equivalent to `false`.

### Body ownership and template contract

The creation template creates initial user sections such as **Business Context**,
**Known Issues / Technical Debt**, and **Additional Information**. A separate
generated-section template produces the replaceable facts and relationship
sections. Refresh must never render a whole existing note from its creation
template.

The engine assigns identity, serializes reserved properties, and validates the
marker structure. Templates may change presentation and creation defaults, but
cannot redefine ownership, invent identities, remove required fields/markers,
or introduce duplicate reserved properties. Validate a complete rendered
candidate before it can enter a change plan.

Use one exact, versioned marker pair in v0.1.0:

```markdown
<!-- obforce:generated:start -->
## Salesforce Metadata
Generated facts and references appear here.
<!-- obforce:generated:end -->

## Business Context

## Known Issues / Technical Debt

## Additional Information
```

Content outside the pair is user-owned. Repeated, nested, missing, reordered, or
otherwise invalid markers are conflicts. Reserve the marker strings and reject
their use inside templates/data where it would make parsing ambiguous.

Use saved baselines for both the generated body and owned properties. A user edit
to either is a conflict even if the source has not changed. User-owned property
changes and narrative edits are preserved. Duplicate YAML keys, unsafe YAML tags,
malformed frontmatter, or an unsupported note schema stop the run without repair
or destructive fallback.

Preserve body bytes outside the generated region, including line endings.
Use round-trip YAML handling to preserve user keys, comments, ordering, types,
and quoting as far as supported. Do not promise universal byte-for-byte
frontmatter preservation: the
[ruamel.yaml round-trip documentation](https://yaml.dev/doc/ruamel.yaml/detail/)
describes formatting normalization limitations. Test the supported forms and
refuse unsupported structures that cannot be preserved safely.

### Template loading and safety

Resolve each known template from an explicitly configured override directory
first, otherwise from packaged defaults. A missing override file may fall back;
an existing but invalid override must fail clearly rather than be ignored.
Restrict loaders to intended template roots, block traversal/link escapes, use
strict undefined-variable handling, and pass only primitive normalized data.
Do not auto-load templates found in an arbitrary source repository or vault.

Use an appropriately restricted Jinja sandbox with a small explicit filter set;
no arbitrary imports, Python objects with side effects, or filesystem helpers.
Treat custom templates as user-selected local code-like input. The official
[Jinja sandbox guidance](https://jinja.palletsprojects.com/en/stable/sandbox/)
warns that sandboxing alone does not prevent resource exhaustion. Bound rendering
and output, catch failures before publication, and document the trust boundary.
Escaping YAML and wikilinks remains the renderer's responsibility.

Template changes invalidate generated output through a render fingerprint that
also includes schema/renderer versions and relevant layout configuration.
Creation-template changes affect new notes only. Neither kind of change grants
permission to overwrite user edits.

## 6. Synchronization, filesystem safety, and recovery

### Plan before publication

Every build or refresh must first validate configuration, source identity,
coverage, existing notes/state, rendered output, target paths, and a complete
change set. No managed note or state changes occur during this phase.

| Situation | v0.1.0 action |
| --- | --- |
| New supported component | Propose a new note at a collision-safe configured path |
| Unchanged source, graph, rendering, and baseline | Leave note bytes and modification time untouched |
| Source facts or relevant graph changed | Replace only clean owned properties and generated content |
| User changed narrative/custom properties | Preserve them and apply clean generated updates |
| User changed generated facts/region or identity | Report conflict; publish nothing from that run |
| Managed note moved within the vault | Reconcile unique ID; update state and affected generated links |
| Managed note absent or duplicated | Report conflict; do not recreate, adopt, or delete automatically |
| Missing from local/partial/unavailable input | Preserve note and prior known facts; report incomplete coverage |
| Missing from comparable complete supported live scan | Mark `sf_lifecycle: missing`; retain note and all user content |
| Previously missing component reappears | Return to `active` after identity/baseline validation |
| Optional dependency query unavailable | Preserve prior edges as stale or report uncollected; no false completeness |
| Template/render/path validation fails | Publish nothing |
| Writer fails or process stops | Retain recovery evidence; block ordinary writes pending recovery |

Marking missing means **not observed in this selected, accessible scope**. It does
not assert that Salesforce has permanently deleted the component. Changes in
filters, namespaces, source mode, org, API access, or selection scope invalidate
absence comparisons. Completeness is tracked separately for component inventory,
audit enrichment, and dependency collection. Never delete a note automatically.

### State contract

Use versioned `.obforce/state.json` containing only required identity, coverage,
path, hash, and baseline information. Treat state as untrusted input: validate
schema, duplicate keys/IDs/paths, bounds, and relative paths. Reject unsupported
versions; do not silently rebuild missing or corrupt state against existing
managed notes. Recovery/adoption/migrations require a separate design decision.

Store paths relative to the vault using `/`. Do not store credentials, raw class
bodies, complete CLI responses, or unnecessary personal data. State is private
operational metadata, not a portable proof that a second checkout is the same
org. If it is backed up or versioned, notes and state must remain consistent.

Update state only after corresponding note updates are successfully applied in
the same recoverable transaction. A no-op run does not rewrite state merely to
record a current timestamp. Report check times in terminal output; persist a
publication timestamp only with an actual committed change set. Hash equality
is an integrity/conflict aid, not encryption or protection from a hostile user.

### Filesystem and concurrency rules

- Reject traversal, unsafe absolute paths from inputs, path overlap, symlinks or
  junction escapes, special files, and case/Unicode/Windows-reserved collisions.
  Validate existing and planned parent components and recheck before replacement.
- Keep source projects, override-template roots, and output roots appropriately
  separate; sources and templates must never be overwritten by generated output.
- Do not overwrite unowned files. An occupied new-note path is a conflict, not a
  request to adopt or truncate it. Filename disambiguation must be deterministic.
- Confine note discovery to the configured vault, excluding `.git`, `.obsidian`,
  `.obforce`, and other explicitly documented non-note areas. Detect traversal
  errors; do not treat unreadable directories as a complete scan.
- Use a single-writer guard per managed vault and revalidate expected current
  file hashes/identities immediately before replacement. A concurrent user edit
  must stop publication rather than be overwritten.
- Stage on the destination filesystem and use atomic replacement per file.
  Do not claim an entire multi-file run is filesystem-atomic.
- Test on normal local filesystems first. Network shares, cloud-synced active
  vaults, unusual filesystems, and concurrent Obsidian/backup writers require
  documented limits; do not imply locks coordinate unrelated applications.

### Recoverable write protocol

Thread 11 must establish and test the following before public build/sync writes:

1. Complete a read-only plan and validate all rendered notes/state.
2. Acquire the vault writer guard, revalidate the plan's preconditions, and stage
   new bytes plus before-images in an Obforce-owned transaction directory.
3. Write a versioned journal recording intended paths and progress. Publish each
   note through atomic replacement, then publish matching state.
4. Mark the transaction committed only after the note/state pair is consistent.
   Clean only the transaction's own temporary material after a successful commit.
5. On failure, attempt a safe rollback only where current bytes match the
   transaction's expected versions. Otherwise retain before-images/journal and
   report a recovery-required result. Never overwrite intervening user edits.
6. On startup, refuse ordinary writes while an incomplete journal exists. A
   dedicated recovery workflow validates the journal and previews/applies the
   safe rollback. Invalid or ambiguous journals require manual resolution.

Crash recovery is not a substitute for independent vault backups or historical
version control. Before-images can include private human documentation; protect
them like the vault. Do not copy them into fixtures, issues, or application Git.
Recovery may remove only files it can prove that transaction created and that
have not since changed. It never performs broad directory deletion.

### Dry-run semantics

`--dry-run` runs the same validation and produces the same proposed actions as
the corresponding write. It does not create or alter vault notes, directories,
state, locks, transaction journals, config files, or Obforce log/cache files.
Conflicts and invalid inputs still produce a nonzero result.

A live dry run may perform explicitly selected read-only Salesforce queries;
Salesforce CLI can manage its own authentication/cache/log state. Do not promise
that a live preview is network-free or that third-party tools never touch their
own files. Offline dry runs must not invoke `sf` or any network service.

## 7. Proposed CLI and configuration contract

Names and examples here are planned until their implementation thread passes.
Expose no placeholder command that pretends to implement safe writes.

| Command | Responsibility |
| --- | --- |
| `obforce --help`, `--version` | Product discovery and installed version |
| `obforce init` | Validate explicit source/vault selection and create a minimal new configuration without replacing an existing file |
| `obforce build` | Initial managed build into an empty destination; refuse nonempty/unmanaged output and direct users to documented setup/refresh rules |
| `obforce sync` | Refresh an already initialized managed vault; never bootstrap absent/corrupt state automatically |
| `obforce recover` | Preview or apply validated rollback of an interrupted Obforce transaction; no Salesforce query |

`init`, `build`, `sync`, and `recover` support `--dry-run` where they can write.
`build`, `sync`, and `recover` use `--config PATH`. Live org selection is explicit;
`--org` may override a live target only after its verified org identity matches
the state binding. `--source` selects offline input during initialization.
`init` requires one source selector, a vault path, and a workspace ID. Existing
vault support in v0.1.0 means a vault previously built by Obforce with user edits
and additional notes; adopting an arbitrary preexisting vault is deferred.

Example offline journey:

```sh
obforce init --config ./obforce.toml --source ./sample-sfdx --vault ../OrgKnowledge --workspace-id demo-org
obforce build --config ./obforce.toml --dry-run
obforce build --config ./obforce.toml
obforce sync --config ./obforce.toml --dry-run
obforce sync --config ./obforce.toml
```

Example live journey, after the user separately installs and authenticates `sf`:

```sh
obforce init --config ./obforce.toml --org demo-sandbox --vault ../OrgKnowledge --workspace-id demo-org
obforce build --config ./obforce.toml --dry-run
obforce build --config ./obforce.toml
```

Version-one TOML supported by the internal loader (public lifecycle commands remain planned):

```toml
schema_version = 1
workspace_id = "demo-org"
vault = "../OrgKnowledge"

[source]
mode = "local"
project = "./sample-sfdx"

[layout]
apex_classes = "Custom Code/Apex Classes"
dashboards = "Dashboards"

[options]
include_namespaced = false
include_audit_names = true

# Optional; omit to use packaged defaults.
# [templates]
# directory = "./my-templates"
```

For live mode, use `mode = "live"` and `org = "demo-sandbox"` instead of `project`.
Namespace filtering is explicit and part of the scope fingerprint; default
exclusion must be reported so users do not mistake it for complete org coverage.

Resolve paths relative to the configuration file, not an incidental working
directory. Precedence: explicit supported CLI override, then config, then
documented defaults. Invalid explicit configuration fails; no fallback to another
org, source, vault, or template. No credentials belong in this file.

Use concise terminal summaries of created/updated/unchanged/missing/conflicted
notes plus source and dependency coverage. Detailed paths/names are opt-in where
practical; never print raw API responses, credentials, or note content. Persisted
logging and machine-readable report files are deferred.

Frozen exit codes: `0` for a successful complete run or valid no-op, `1` for an
operational failure, `2` for invalid usage/configuration, `3` for conflicts or
recovery-required state, and `4` for a completed operation with partial/unavailable
requested coverage. An offline run can succeed at its declared local scope while
explicitly reporting that org audit/dependency coverage is unavailable by design.
Thread 02 verifies Click's usage/error behavior and freezes overlapping outcome
precedence as **3, 2, 1, 4, 0**. Exact keys, path rules, selectors, and typed errors
are in [CONFIGURATION.md](../docs/CONFIGURATION.md). Never return a success code
for a truncated requested live scan. This contract adds no public commands.

## 8. Implementation threads

### Common thread contract

- Read root agent/contributor guidance, this roadmap, and the relevant contracts.
  Inspect actual dependencies and repository changes; do not rely on labels alone.
- Read the thread's linked GitHub issue and prerequisite issues before work.
  Verify dependency code and validation, not just issue state. Keep the existing
  issue and this roadmap synchronized with a start comment, meaningful progress
  and blocker/decision updates, verified task checkboxes, and a public-safe handoff.
  The maintainer's 18 October 2026 tracking request authorizes these routine
  updates when implementation of that named thread is explicitly requested;
  renewed permission for each progress update is unnecessary. It does not
  authorize starting implementation merely because an issue exists.
  Leave partial work and pending review open; close only after acceptance criteria
  are met and the maintainer approves completion or requests closure. If GitHub
  access fails, record the unsent update and report the limitation accurately.
- Implement one requested thread. If its work cannot fit a reviewable thread,
  propose a documented `NN.a`/`NN.b` split before continuing into another boundary.
- Add focused behavior/regression tests and necessary help/docs. Use synthetic
  metadata, temporary vaults, and mocked `sf` responses. No automatic live org or
  real-vault tests.
- After Thread 01, run relevant checks from `AGENTS.md`, including whitespace
  checks. Run the broader suite when integration changes warrant it. Report
  local, hosted, skipped, and unavailable evidence separately.
- Update `docs/CHANGELOG.md` under `[Unreleased]` and the status/handoff record as
  appropriate. Planned examples remain labeled until usable.
- Leave changes reviewable and uncommitted. Identify the next eligible thread;
  do not begin it. Use the linked existing issue; do not create duplicate tracking.

### Thread index, implementation phases, and GitHub issues

| ID | Thread | Dependencies | Phase | GitHub issue | Status |
| --- | --- | --- | --- | --- | --- |
| 01 | Foundation and developer workflow | None | A: foundations | [#1](https://github.com/jeffshurtliff/obforce/issues/1) | Accepted; closed; 12/12 hosted cells passed |
| 02 | Configuration, models, and contracts | 01 | A | [#2](https://github.com/jeffshurtliff/obforce/issues/2) | Accepted; closed; corrected 12/12 hosted cells passed |
| 03 | Offline Apex source | 02 | B: source data | [#3](https://github.com/jeffshurtliff/obforce/issues/3) | Delivered; local Windows correction ready; hosted gate pending; open |
| 04 | Salesforce CLI process boundary | 02 | B | [#4](https://github.com/jeffshurtliff/obforce/issues/4) | Not started |
| 05 | Live Apex inventory and audit enrichment | 04 | B | [#5](https://github.com/jeffshurtliff/obforce/issues/5) | Not started |
| 06 | Platform relationships and normalized graph | 03, 05 | B | [#6](https://github.com/jeffshurtliff/obforce/issues/6) | Not started |
| 07 | Packaged templates and note rendering | 03, 06 | C: safe proposals | [#7](https://github.com/jeffshurtliff/obforce/issues/7) | Not started |
| 08 | Existing-note parsing and preservation | 07 | C | [#8](https://github.com/jeffshurtliff/obforce/issues/8) | Not started |
| 09 | State validation and identity reconciliation | 08 | C | [#9](https://github.com/jeffshurtliff/obforce/issues/9) | Not started |
| 10 | Read-only change planner and conflict reports | 06, 07, 08, 09 | C | [#10](https://github.com/jeffshurtliff/obforce/issues/10) | Not started |
| 11 | Transaction writer and recovery | 10 | D: working lifecycle | [#11](https://github.com/jeffshurtliff/obforce/issues/11) | Not started |
| 12 | Public initialization and initial build | 11 | D | [#12](https://github.com/jeffshurtliff/obforce/issues/12) | Not started |
| 13 | Public refresh and missing-component lifecycle | 12 | D | [#13](https://github.com/jeffshurtliff/obforce/issues/13) | Not started |
| 14 | Native dashboard and CLI usability | 13 | E: usable product | [#14](https://github.com/jeffshurtliff/obforce/issues/14) | Not started |
| 15 | Platform, failure, and scale qualification | 14 | E | [#15](https://github.com/jeffshurtliff/obforce/issues/15) | Not started |
| 16 | User and maintainer documentation | 15 | F: release candidate | [#16](https://github.com/jeffshurtliff/obforce/issues/16) | Not started |
| 17 | v0.1.0 release preparation | 16 | F | [#17](https://github.com/jeffshurtliff/obforce/issues/17) | Not started |

All 17 issues are assigned to `jeffshurtliff` and associated with the
[`v0.1.0` GitHub milestone](https://github.com/jeffshurtliff/obforce/milestone/1). They carry `maintainer`, `codex`,
and the category labels from their selected maintainer templates, with additional
`ci`/`security` labels where relevant. A–F are internal implementation phases,
not separate GitHub milestones. Thread IDs in the dependency column map to the
issues in this table; GitHub's native blocked-by/blocking relationships mirror
the exact 21 direct prerequisite edges, including redundant direct prerequisites
that the roadmap lists explicitly. Issue creation does not start implementation.

The default path is sequential. Threads 03 and 04 can be worked on independently
after 02 if the maintainer explicitly chooses parallel work; avoid shared-file
conflicts. Do not start extra agents or chats merely because the table permits
independent work.

Phase demos: **A** installs and validates synthetic normalized data; **B**
produces comparable source/graph records from offline fixtures and mocked live
responses; **C** previews changes against edited fixture notes without writing;
**D** builds, edits, refreshes, and recovers a synthetic vault; **E** demonstrates
native discovery and qualified failure/platform behavior; **F** produces an
installable, documented candidate. Intermediate demos may use tests/internal
functions; public mutation commands remain unavailable until their safety gates.

### Thread 01 — Foundation and developer workflow

**Goal:** An installable, reproducible Python package with safe development defaults.

**Depends on:** None. **Status:** Accepted and complete; issue #1 closed.
Correction delivered at `72471d2`; all 12 hosted cells passed.

**GitHub issue:** [#1](https://github.com/jeffshurtliff/obforce/issues/1)

**Issue template:** [`maintainer-chore.md`](https://github.com/jeffshurtliff/obforce/blob/main/.github/ISSUE_TEMPLATE/maintainer-chore.md)

**Blocked by:** None.

**Blocks:** [#2](https://github.com/jeffshurtliff/obforce/issues/2)

1. Inspect the real baseline; preserve the existing Apache license and maintainer
   edits. Establish Poetry/PEP 621, `src/obforce/`, static `0.1.0.dev0`, console and
   module entry points, and Python `>=3.12`. Generate the lockfile through Poetry.
2. Add Click and justified initial dependencies/dev groups. Configure Ruff for
   130 columns, single-quoted ordinary strings, triple-double docstrings, spaces,
   and LF. Add unit/integration directories and entry-point tests.
3. Establish root `CONTRIBUTING.md`, `SECURITY.md`, `docs/CHANGELOG.md`, and focused
   ignore rules for private `local/`, fixtures' scratch output, caches, and builds.
   Retain `poetry.lock` in version control; keep the two planning files linked.
4. Add an offline test workflow for the initial stable Python matrix and inspect
   package exclusions. Do not add or activate publication automation.

**Locations:** `pyproject.toml`, `poetry.lock`, `src/obforce/{__init__,__main__,cli}.py`,
`tests/`, root guidance, `.gitignore`, `.github/workflows/test.yml`.

**Acceptance/demo:** A clean install runs help/version through both entry points;
there is no fake build/sync command or accidental dependency on `sf`/Obsidian.

**Validation:** Poetry metadata/lock checks, Ruff, entry-point tests, `poetry build`,
strict Twine checks of fresh artifacts, installation outside the checkout, and
artifact privacy/content inspection. No live connections.

**Current evidence:** See the [accepted completion record](#thread-01-acceptance-and-closure--19-october-2026).
The foundation and Windows test correction are reviewed and delivered. Corrected
commit `72471d2` passed all 12 Linux/macOS/Windows cells for Python 3.12–3.15,
including 24 tests and independent wheel/sdist installs in each. Earlier failed
and local-only evidence remains recorded below as history. Issue #1 is closed.

**Copy-ready prompt:**

> Read GitHub issue https://github.com/jeffshurtliff/obforce/issues/1 and its linked
> prerequisite issues. Keep this existing issue updated with start/progress,
> verified checklist, and handoff evidence, synchronized with the roadmap. Leave
> it open pending maintainer acceptance; do not create duplicate tracking issues.
>
> Read AGENTS.md, CONTRIBUTING.md if present, and dev/IMPLEMENTATION_PLAN.md.
> Implement only Thread 01. Preserve the current license and user changes; create
> the Poetry/src foundation, contributor guidance, offline tests and CI. Validate
> fresh install artifacts and record actual evidence. Leave changes uncommitted;
> do not implement source connectors, create issues, or publish.

### Thread 02 — Configuration, models, and contracts

**Goal:** Validated configuration and versioned internal records before connectors.

**Depends on:** 01. **Status:** Accepted and complete; issue #2 closed.
See the [Thread 01 completion record](#thread-01-acceptance-and-closure--19-october-2026).
Rechecked actual code/current CI before implementation; see the Thread 02 start record below.
The [original Thread 02 handoff](#thread-02-handoff--19-october-2026) is historical.
The [delivery/CI follow-up](#thread-02-delivery-and-ci-follow-up--19-october-2026)
retains the earlier masked failures. Current evidence is in the
[acceptance record](#thread-02-acceptance-and-closure--19-october-2026): delivered
correction `65305fb` passed all 12 cells, including standalone Windows formatting,
117 tests per cell, and both independent artifact installs per cell. Thread 03
is delivered with a locally verified Windows correction awaiting delivery/CI;
Thread 04 remains not started.

**GitHub issue:** [#2](https://github.com/jeffshurtliff/obforce/issues/2)

**Issue template:** [`maintainer-feature.md`](https://github.com/jeffshurtliff/obforce/blob/main/.github/ISSUE_TEMPLATE/maintainer-feature.md)

**Blocked by:** [#1](https://github.com/jeffshurtliff/obforce/issues/1)

**Blocks:** [#3](https://github.com/jeffshurtliff/obforce/issues/3), [#4](https://github.com/jeffshurtliff/obforce/issues/4)

1. Implement TOML loading, strict schema/selection checks, config-relative path
   resolution, source-mode validation, and typed operational errors.
2. Define component, coverage, relationship, and note-state records; canonical
   serialization/hashing; namespace/scope identity; and field availability.
3. Specify exact owned property names, marker/schema versions, source switching
   refusal, render fingerprints, and the exit-code precedence contract.
4. Document these in `docs/CONFIGURATION.md`, `docs/COVERAGE.md`, and
   `docs/NOTE_FORMAT.md` with synthetic examples and explicit planned features.

**Locations:** `config.py`, `models.py`, `constants.py`, `errors.py`, contract docs,
`tests/unit/test_config.py`, `test_models.py`.

**Acceptance/demo:** Equivalent synthetic inputs produce identical canonical
records/hashes; invalid explicit config fails without fallback or filesystem writes.

**Validation:** Relative/absolute paths, unknown keys/versions, source-selector
conflicts, absent/null/false distinctions, identity collisions, ordering, and
timestamp-independent hashes. CLI usage/operational exit-code tests.

**Copy-ready prompt:**

> Read GitHub issue https://github.com/jeffshurtliff/obforce/issues/2 and its linked
> prerequisite issues. Keep this existing issue updated with start/progress,
> verified checklist, and handoff evidence, synchronized with the roadmap. Leave
> it open pending maintainer acceptance; do not create duplicate tracking issues.
>
> Read AGENTS.md, CONTRIBUTING.md, and dev/IMPLEMENTATION_PLAN.md, including
> the 19 October Thread 01 acceptance/closure record. Verify foundation merge
> `7f3ceb1` and delivered correction `72471d2` against actual code. Run
> `39266996850` passed all 12 Linux/macOS/Windows cells for Python 3.12–3.15,
> including 24 tests and both artifact installs per cell. Recheck current-commit
> CI and report any new prerequisite blocker before implementation. Preserve
> the earlier failed run as historical evidence; issue closure alone is not proof.
>
> Implement only Thread 02: strict TOML loading and config-relative paths, source
> selection and typed errors; normalized component/coverage/relationship/note-state
> records and deterministic canonical keys/hashes; exact ownership/marker/schema,
> source-switching, render-fingerprint, and exit-code precedence contracts.
> Document these in docs/CONFIGURATION.md, docs/COVERAGE.md, and
> docs/NOTE_FORMAT.md with fictional examples. Add focused offline tests for
> invalid/unknown config, path resolution, selector conflicts, absent/null/false
> distinctions, identity collisions, ordering, and timestamp-independent hashes.
> Record material decisions before dependent implementation.
>
> Preserve maintainer changes and the Apache license. Do not implement connectors,
> rendering, vault/state publication, or public mutation commands; do not access
> Salesforce or a real vault. Run applicable checks, update the changelog and
> roadmap handoff, and report actual local/hosted/skipped evidence separately.
> Leave changes unstaged/uncommitted. Do not create issues, commit, push, open a PR,
> close tracking issues, or publish. Leave Threads 03 and 04 explicitly not started.

### Thread 03 — Offline Apex source

**Goal:** A read-only local project source producing honest normalized Apex records.

**Depends on:** 02. **Status:** Core delivered; Windows correction locally verified,
pending delivery and corrected exact-commit CI.
Acceptance remains pending. The [original handoff](#thread-03-handoff--19-october-2026)
is historical; see the follow-up record below for current evidence.

**Windows correction decision — 19 October 2026 (before coding):** Run
`39298411328` at delivered merge `1f86032` has eight passing Ubuntu/macOS cells
and four Windows failures. Pathname ctime can mean creation time while descriptor
ctime means change time in supported Windows CPython. Permit only an exact
descriptor birthtime bridge to path ctime when all other identity fields match.
Keep raw descriptor before/after snapshots (including change time), exact path
checks, links/containment guards, and bounded reads. Add synthetic regressions;
do not round timestamps, bypass checks, or introduce skips. Preserve maintainer
annotations. Corrected native Windows CI remains a delivery/acceptance gate.

**Prerequisite gate satisfied:** Thread 02 core merged at `785b45d`; correction
`65305fb` passed exact-commit run `39278236478`, including every standalone
Windows formatting/test/artifact check. See the
[Thread 02 acceptance record](#thread-02-acceptance-and-closure--19-october-2026).
The copy-ready prompt below remains valid: its repair-verification requirement
is satisfied by that delivery/run. Recheck actual code/current CI in the new
thread; a green summary or closed issue alone is insufficient. Re-verified all
12 corrected job logs before starting this requested Thread 03. Current main
`5e86e03` differs from correction `65305fb` only in documentation; source, tests,
dependencies, workflow, and artifact checker are identical. No pass is claimed
for that later documentation SHA.

**Decisions recorded before coding — 19 October 2026:** Validate only the
acquisition-relevant DX manifest subset; unrelated settings remain inert.
Declared package roots must exist, be contained/disjoint, and use safe portable
relative paths. Scan class pairs in `classes` directories, independent of default
package order. Project-level namespace supplies local identity; filenames do not
imply namespaces. Missing pairs mean partial local inventory; unsafe, malformed,
duplicate, unreadable, or over-limit inputs fail closed. Empty valid packages
prove only an exhausted local scan. Add `defusedxml` through Poetry with explicit
DTD/entity/external-reference refusal plus separate byte/structure/scan bounds.
Never parse/retain/hash Apex bodies. Preserve normalized models and canonical
hashes; audit is unavailable and relationships uncollected by design. No public
CLI behavior or later thread is started.

**GitHub issue:** [#3](https://github.com/jeffshurtliff/obforce/issues/3)

**Issue template:** [`maintainer-feature.md`](https://github.com/jeffshurtliff/obforce/blob/main/.github/ISSUE_TEMPLATE/maintainer-feature.md)

**Blocked by:** [#2](https://github.com/jeffshurtliff/obforce/issues/2)

**Blocks:** [#6](https://github.com/jeffshurtliff/obforce/issues/6), [#7](https://github.com/jeffshurtliff/obforce/issues/7)

1. Validate `sfdx-project.json`, declared package roots, namespace options, and
   supported Apex source/metadata pairs without modifying source files.
2. Parse bounded `.cls-meta.xml` with safe XML handling, normalize supported
   fields, and detect duplicates/malformed pairs. Do not embed `.cls` contents.
3. Return local-scope coverage and unavailable audit/relationship information;
   never substitute filesystem/Git dates or declare org-wide absence.
4. Add a fictional DX sample and focused parser/source fixture tests.

**Locations:** `sources/local.py`, `parsers/apex.py`, `examples/sample_sfdx/`,
`tests/fixtures/salesforce/`, unit and source integration tests.

**Acceptance/demo:** Inventory a multi-package synthetic project deterministically
with no `sf` executable, authentication, or network access.

**Validation:** Source tree snapshots before/after; XML entity/DTD attacks,
malformed/oversize files, links/escapes, namespaces, duplicates, empty/partial
packages, unknown types, and missing audit data.

**Copy-ready prompt:**

> Read GitHub issue https://github.com/jeffshurtliff/obforce/issues/3 and its linked
> prerequisite issues. Keep this existing issue updated with start/progress,
> verified checklist, and handoff evidence, synchronized with the roadmap. Leave
> it open pending maintainer acceptance; do not create duplicate tracking issues.
>
> Read AGENTS.md, CONTRIBUTING.md, dev/IMPLEMENTATION_PLAN.md, and the Thread 02
> configuration/coverage/note contracts. Verify prerequisite code and exact-commit
> CI before implementing. Thread 02 was merged at `785b45d`; run `39275023920`
> reports success but all four Windows cells contain a failed Ruff format check
> masked by a later command. Require delivery of the LF-checkout/single-command
> CI correction and verify actual formatter, tests, build, Twine, and independent
> wheel/sdist checks at the corrected commit. If still pending/failing/unverified,
> report the blocker in #3 and the roadmap and do not start implementation.
>
> Implement only Thread 03: a read-only offline Apex source and bounded safe XML
> parser. Validate `sfdx-project.json`, declared package directories, containment,
> namespace selection, and supported `.cls`/`.cls-meta.xml` pairs. Normalize into
> the existing Thread 02 identity/component/selection/coverage records and typed
> errors; preserve its canonical hashes and source-binding contracts. Do not
> embed Apex bodies or infer dependencies from source text. Record material
> decisions before dependent implementation; justify dependencies through Poetry
> and never hand-edit the lockfile.
>
> Add a small fictional multi-package DX project and focused offline tests for
> deterministic ordering/hashes, source bytes/mtimes unchanged, package paths,
> traversal/links/escapes, XML entities/DTDs, malformed/oversized files, missing
> pairs, duplicate identities, namespaces, empty/partial packages, unsupported
> types, and unavailable fields. Inventory coverage means the available local
> scope only. Keep audit/relationship coverage independently unavailable or
> uncollected by design; never substitute filesystem/Git dates, claim org-wide
> absence, or turn a partial scan into complete coverage.
>
> Keep runtime/tests offline with synthetic inputs; do not invoke sf, discover
> authentication, access real metadata/vaults, or add live adapters, graph
> collection, rendering, state/vault publication, or public mutation commands.
> Preserve maintainer changes and the Apache license. Update applicable docs,
> changelog, and roadmap handoff. Run relevant checks and fresh wheel/sdist
> inspection/independent-install checks for package/dependency changes; extend
> the explicit artifact allowlist deliberately. Report local, hosted, skipped,
> and unavailable evidence separately.
>
> Leave changes unstaged/uncommitted and #3 open for acceptance. Do not create
> duplicate issues, stage, commit, push, open a PR, close issues, or publish.
> Leave Thread 04 and all later threads explicitly not started.

### Thread 04 — Salesforce CLI process boundary

**Goal:** A bounded, mockable, read-only `sf` process adapter.

**Depends on:** 02. **Status:** Not started.

**GitHub issue:** [#4](https://github.com/jeffshurtliff/obforce/issues/4)

**Issue template:** [`maintainer-feature.md`](https://github.com/jeffshurtliff/obforce/blob/main/.github/ISSUE_TEMPLATE/maintainer-feature.md)

**Blocked by:** [#2](https://github.com/jeffshurtliff/obforce/issues/2)

**Blocks:** [#5](https://github.com/jeffshurtliff/obforce/issues/5)

1. Resolve the explicit executable safely on supported systems, inspect supported
   command behavior, and define an allowlist for read-only query/version calls.
2. Invoke argument lists with explicit targets, timeouts, bounded outputs, and
   controlled working directories; reject arbitrary command/shell input.
3. Validate JSON success/error envelopes and pagination/completion information;
   sanitize user-facing errors without echoing raw responses or auth details.
4. Build mocked process fixtures for success, failure, missing executable,
   expired auth, malformed JSON, timeout, and unexpected output.

**Locations:** `sources/sf_cli.py`, `tests/unit/test_sf_cli.py`, sanitized fixture
responses, CLI prerequisite documentation.

**Acceptance/demo:** Process-boundary tests prove exact safe argv construction and
bounded failure behavior without executing an authenticated command.

**Validation:** Spaces/metacharacters in selectors, Windows command wrappers,
error/output redaction, resource bounds, and no shell/deploy/login invocation.
Report actual executable/platform coverage, not assumed compatibility.

**Copy-ready prompt:**

> Read GitHub issue https://github.com/jeffshurtliff/obforce/issues/4 and its linked
> prerequisite issues. Keep this existing issue updated with start/progress,
> verified checklist, and handoff evidence, synchronized with the roadmap. Leave
> it open pending maintainer acceptance; do not create duplicate tracking issues.
>
> Implement only Thread 04 using mocked sf process results. Verify current
> official command contracts and implement the bounded read-only process boundary.
> Do not install/update sf, authenticate, query an org, or build a vault. Record
> platform gaps and leave changes uncommitted.

### Thread 05 — Live Apex inventory and audit enrichment

**Goal:** Normalized live Apex records using existing CLI authorization.

**Depends on:** 04. **Status:** Not started.

**GitHub issue:** [#5](https://github.com/jeffshurtliff/obforce/issues/5)

**Issue template:** [`maintainer-feature.md`](https://github.com/jeffshurtliff/obforce/blob/main/.github/ISSUE_TEMPLATE/maintainer-feature.md)

**Blocked by:** [#4](https://github.com/jeffshurtliff/obforce/issues/4)

**Blocks:** [#6](https://github.com/jeffshurtliff/obforce/issues/6)

1. Verify org identity through a minimal non-secret read query; require an
   explicit target and prevent mismatches with configured/state identity.
2. Query allowlisted ApexClass fields and permitted audit labels, excluding
   source bodies and unrelated User/customer data. Support audit-name omission.
3. Handle complete enumeration, paging, selected namespace scope, missing
   permissions, field unavailability, and required-versus-optional failures.
4. Add realistic synthetic response fixtures producing the same normalized model
   as offline input while accurately retaining additional field provenance.

**Locations:** `sources/live.py`, `sources/sf_cli.py`, live adapter tests,
`docs/COVERAGE.md`.

**Acceptance/demo:** Mocked multi-page live data produces audit-enriched records
and a precise scope/completeness result; a partial page is never a complete scan.

**Validation:** Target mismatch, namespace filtering, empty success, truncation,
permission loss, invalid dates, no `Body`/token request, privacy, and deterministic
hashes. Actual org testing is opt-in and separately authorized, not required for
ordinary offline CI.

**Copy-ready prompt:**

> Read GitHub issue https://github.com/jeffshurtliff/obforce/issues/5 and its linked
> prerequisite issues. Keep this existing issue updated with start/progress,
> verified checklist, and handoff evidence, synchronized with the roadmap. Leave
> it open pending maintainer acceptance; do not create duplicate tracking issues.
>
> Implement only Thread 05 with the existing process boundary and synthetic
> responses. Add explicit org identity, Apex inventory/audit normalization, and
> tested coverage handling. Do not access a live org unless I separately authorize
> its target and operations. Leave work uncommitted and report validation limits.

### Thread 06 — Platform relationships and normalized graph

**Goal:** Useful references with explicit evidence and incomplete-coverage handling.

**Depends on:** 03, 05. **Status:** Not started.

**GitHub issue:** [#6](https://github.com/jeffshurtliff/obforce/issues/6)

**Issue template:** [`maintainer-feature.md`](https://github.com/jeffshurtliff/obforce/blob/main/.github/ISSUE_TEMPLATE/maintainer-feature.md)

**Blocked by:** [#3](https://github.com/jeffshurtliff/obforce/issues/3), [#5](https://github.com/jeffshurtliff/obforce/issues/5)

**Blocks:** [#7](https://github.com/jeffshurtliff/obforce/issues/7), [#10](https://github.com/jeffshurtliff/obforce/issues/10)

1. Verify current platform dependency API behavior, limits, permissions, supported
   endpoints, and CLI result handling. Record accessible official evidence and
   unresolved capability gaps; do not inherit historical numeric assumptions.
2. Implement best-effort platform collection with bounded queries/paging and
   explicit partial/unavailable outcomes. Unsupported capability degrades honestly.
3. Normalize/deduplicate directed edges and derive reciprocal relationships,
   unresolved endpoint records, stale-edge handling, and graph fingerprints.
4. Test graph invalidation when incoming references change and maintain separate
   component versus dependency coverage. Offline source returns uncollected edges.

**Locations:** `graph/dependencies.py`, live adapter extensions, graph/dependency
tests, `docs/COVERAGE.md`.

**Acceptance/demo:** Synthetic A → B updates both outgoing and incoming views;
failed/truncated collection produces a warning and cannot erase prior edges as
if they were authoritatively absent.

**Validation:** Duplicates, cycles, namespaces, unsupported endpoints/types,
limits, permission failures, stale data, and no runtime/completeness overclaim.
If API support remains unverified, keep collection explicitly unavailable and
record the release limitation; do not invent results or substitute static guesses.

**Copy-ready prompt:**

> Read GitHub issue https://github.com/jeffshurtliff/obforce/issues/6 and its linked
> prerequisite issues. Keep this existing issue updated with start/progress,
> verified checklist, and handoff evidence, synchronized with the roadmap. Leave
> it open pending maintainer acceptance; do not create duplicate tracking issues.
>
> Implement only Thread 06. Verify the platform dependency contract, then add the
> provenance-aware graph and best-effort adapter with honest failure/coverage
> behavior. Use synthetic responses; no live queries are authorized by this prompt.
> Do not add a static analyzer or new component notes. Leave work uncommitted.

### Thread 07 — Packaged templates and note rendering

**Goal:** Deterministic candidate notes from normalized data without vault writes.

**Depends on:** 03, 06. **Status:** Not started.

**GitHub issue:** [#7](https://github.com/jeffshurtliff/obforce/issues/7)

**Issue template:** [`maintainer-feature.md`](https://github.com/jeffshurtliff/obforce/blob/main/.github/ISSUE_TEMPLATE/maintainer-feature.md)

**Blocked by:** [#3](https://github.com/jeffshurtliff/obforce/issues/3), [#6](https://github.com/jeffshurtliff/obforce/issues/6)

**Blocks:** [#8](https://github.com/jeffshurtliff/obforce/issues/8), [#10](https://github.com/jeffshurtliff/obforce/issues/10)

1. Add packaged creation and generated-section Jinja templates with audit facts,
   coverage, references, and human-owned context/debt/additional sections.
2. Implement package-resource loading and per-template overrides, strict undefined
   handling, restricted contexts/filters, containment, and rendering bounds.
3. Serialize valid flat YAML and escaped links/labels; use deterministic safe
   paths, namespace disambiguation, and source/graph/render fingerprints.
4. Verify resources in clean wheel/sdist installs and add synthetic rendered
   snapshots without Apex bodies or private org data.

**Locations:** `renderer/{templates,notes}.py`, `resources/templates/`, package
inclusion rules, rendering/artifact tests.

**Acceptance/demo:** The same fictional component renders identically outside the
checkout, with valid properties/markers and no dependency on a running Obsidian.

**Validation:** Overrides/fallback/error behavior, marker injection, YAML/link
escaping, undefined fields, missing/unknown audits, null debt defaults, namespace
and filename collisions, template traversal, and bounded rendering failures.

**Copy-ready prompt:**

> Read GitHub issue https://github.com/jeffshurtliff/obforce/issues/7 and its linked
> prerequisite issues. Keep this existing issue updated with start/progress,
> verified checklist, and handoff evidence, synchronized with the roadmap. Leave
> it open pending maintainer acceptance; do not create duplicate tracking issues.
>
> Implement only Thread 07. Add installed-package templates and deterministic
> rendering with the defined ownership and safety contract. Test synthetic output,
> overrides, escaping, and wheel/sdist resource access. Do not publish notes into
> an existing vault or implement sync. Leave changes uncommitted.

### Thread 08 — Existing-note parsing and preservation

**Goal:** Safe reading/patching of managed notes while retaining human content.

**Depends on:** 07. **Status:** Not started.

**GitHub issue:** [#8](https://github.com/jeffshurtliff/obforce/issues/8)

**Issue template:** [`maintainer-feature.md`](https://github.com/jeffshurtliff/obforce/blob/main/.github/ISSUE_TEMPLATE/maintainer-feature.md)

**Blocked by:** [#7](https://github.com/jeffshurtliff/obforce/issues/7)

**Blocks:** [#9](https://github.com/jeffshurtliff/obforce/issues/9), [#10](https://github.com/jeffshurtliff/obforce/issues/10)

1. Parse supported frontmatter/markers with duplicate-key and unsafe-tag
   rejection, schema validation, size bounds, and explicit malformed-note errors.
2. Extract identity, owned-property values, generated bytes, and user regions;
   compare generated properties/body to the saved baseline.
3. Construct candidate patches that update only owned fields/region, preserving
   outside-body bytes and supported YAML comments/types/order/quoting.
4. Add hand-edited note fixtures covering business context, custom tags/aliases,
   multiline fields, technical-debt values, Unicode, and CRLF/LF variations.

**Locations:** `sync/notes.py`, `tests/fixtures/vaults/`, note preservation tests,
`docs/NOTE_FORMAT.md`.

**Acceptance/demo:** Updating a generated audit fact preserves custom fields and
human prose; editing generated material produces a conflict instead of a patch.

**Validation:** Exact outside-body byte comparisons; semantic/comment preservation
for supported YAML; missing/duplicate/nested markers, duplicate keys, unexpected
schemas, generated-property edits, and unsafe content. No filesystem publication.

**Copy-ready prompt:**

> Read GitHub issue https://github.com/jeffshurtliff/obforce/issues/8 and its linked
> prerequisite issues. Keep this existing issue updated with start/progress,
> verified checklist, and handoff evidence, synchronized with the roadmap. Leave
> it open pending maintainer acceptance; do not create duplicate tracking issues.
>
> Implement only Thread 08. Add managed-note parsing, baseline conflict detection,
> and in-memory preservation patches using synthetic edited notes. Verify user
> content and technical-debt fields survive. Do not add a force-overwrite escape
> hatch or write a real vault. Leave work uncommitted.

### Thread 09 — State validation and identity reconciliation

**Goal:** Reliable ownership and note-move matching independent of filenames.

**Depends on:** 08. **Status:** Not started.

**GitHub issue:** [#9](https://github.com/jeffshurtliff/obforce/issues/9)

**Issue template:** [`maintainer-feature.md`](https://github.com/jeffshurtliff/obforce/blob/main/.github/ISSUE_TEMPLATE/maintainer-feature.md)

**Blocked by:** [#8](https://github.com/jeffshurtliff/obforce/issues/8)

**Blocks:** [#10](https://github.com/jeffshurtliff/obforce/issues/10)

1. Implement strict versioned state serialization/validation and persist only
   the minimum identity, scope, path, hash, and generated baseline data.
2. Discover managed notes within the bounded vault scope, reject ambiguous IDs or
   mappings, and reconcile unique moved notes without adopting unrelated files.
3. Enforce workspace/org bindings, missing-state refusal, source-switch rules,
   path safety, and changed-scope restrictions on absence decisions.
4. Add candidate state updates for note moves and link target changes; publication
   remains deferred to the transaction writer.

**Locations:** `sync/state.py`, state/identity integration fixtures and tests,
`docs/SYNC_SAFETY.md`.

**Acceptance/demo:** A uniquely moved synthetic note retains its identity and user
content; duplicate IDs, missing notes/state, and org mismatches are refused.

**Validation:** Corrupt/unknown state, duplicate JSON keys, malicious paths, case
and namespace collisions, outside-vault moves, unreadable traversal, and exact
non-adoption behavior. State parsing never writes or repairs automatically.

**Copy-ready prompt:**

> Read GitHub issue https://github.com/jeffshurtliff/obforce/issues/9 and its linked
> prerequisite issues. Keep this existing issue updated with start/progress,
> verified checklist, and handoff evidence, synchronized with the roadmap. Leave
> it open pending maintainer acceptance; do not create duplicate tracking issues.
>
> Implement only Thread 09. Add strict state handling and identity-based note-move
> reconciliation with synthetic vaults. Refuse ambiguous ownership, unsupported
> source switches, and absent/corrupt state. Do not implement automatic adoption,
> migration, or publication. Leave changes uncommitted.

### Thread 10 — Read-only change planner and conflict reports

**Goal:** A complete deterministic preview of a build/refresh before any write.

**Depends on:** 06, 07, 08, 09. **Status:** Not started.

**GitHub issue:** [#10](https://github.com/jeffshurtliff/obforce/issues/10)

**Issue template:** [`maintainer-feature.md`](https://github.com/jeffshurtliff/obforce/blob/main/.github/ISSUE_TEMPLATE/maintainer-feature.md)

**Blocked by:** [#6](https://github.com/jeffshurtliff/obforce/issues/6), [#7](https://github.com/jeffshurtliff/obforce/issues/7), [#8](https://github.com/jeffshurtliff/obforce/issues/8), [#9](https://github.com/jeffshurtliff/obforce/issues/9)

**Blocks:** [#11](https://github.com/jeffshurtliff/obforce/issues/11)

1. Combine source results, graph, rendered candidates, notes, and prior state into
   typed create/update/no-op/move/missing/conflict actions with preconditions.
2. Re-render when incoming graph edges, target note locations, templates, or
   renderer contracts change; avoid churn from collection timestamps/order.
3. Apply coverage-aware missing/stale behavior and all-or-nothing preflight:
   any conflict blocks publication of the entire planned run.
4. Render concise action counts, opt-in details, coverage warnings, and defined
   exit results; expose no writing CLI until Threads 11–13 qualify it.

**Locations:** `sync/planner.py`, reporting helpers, planner integration tests.

**Acceptance/demo:** A synthetic edited vault yields a stable change plan; a
second unchanged plan is all no-op, and a generated-region edit blocks the batch.

**Validation:** Filesystem snapshots proving no directories/state/locks/logs are
created, graph-only invalidation, changed scope, partial live inputs, collision
refusal, template changes, and deterministic count/result precedence.

**Copy-ready prompt:**

> Read GitHub issue https://github.com/jeffshurtliff/obforce/issues/10 and its linked
> prerequisite issues. Keep this existing issue updated with start/progress,
> verified checklist, and handoff evidence, synchronized with the roadmap. Leave
> it open pending maintainer acceptance; do not create duplicate tracking issues.
>
> Implement only Thread 10. Produce complete read-only change plans with coverage,
> conflicts, no-op behavior, and accurate summaries. Verify dry-run filesystem
> preservation using synthetic vaults. Do not expose mutating build/sync commands
> before the writer safety gate. Leave changes uncommitted.

### Thread 11 — Transaction writer and recovery

**Goal:** Recoverable bounded publication primitives before public vault writes.

**Depends on:** 10. **Status:** Not started.

**GitHub issue:** [#11](https://github.com/jeffshurtliff/obforce/issues/11)

**Issue template:** [`maintainer-feature.md`](https://github.com/jeffshurtliff/obforce/blob/main/.github/ISSUE_TEMPLATE/maintainer-feature.md)

**Blocked by:** [#10](https://github.com/jeffshurtliff/obforce/issues/10)

**Blocks:** [#12](https://github.com/jeffshurtliff/obforce/issues/12)

1. Implement the single-writer guard, same-filesystem staging, before-images,
   versioned journal, immediate precondition rechecks, and per-file replacement.
2. Publish matching note/state changes together through the documented protocol;
   refuse unowned targets and preserve intervening user changes on failure.
3. Implement validated recovery preview/rollback for incomplete transactions;
   prevent ordinary writes while recovery is required, and constrain cleanup to
   verified transaction-owned material.
4. Add fault injection and subprocess interruption tests at each journal/note/
   state boundary, including newly created files and committed cleanup.

**Locations:** `sync/transactions.py`, transaction/recovery integration tests,
`docs/SYNC_SAFETY.md`.

**Acceptance/demo:** An interrupted multi-note synthetic update restores the
previous consistent state or retains an explicit recoverable journal; an
intervening human edit is never overwritten by rollback.

**Validation:** Disk/permission errors, process death, concurrent writers, changed
paths/hashes, malicious journals, symlink/junction replacement, partial state
publication, and recovery no-op/dry-run behavior. Record native platform gaps.

**Copy-ready prompt:**

> Read GitHub issue https://github.com/jeffshurtliff/obforce/issues/11 and its linked
> prerequisite issues. Keep this existing issue updated with start/progress,
> verified checklist, and handoff evidence, synchronized with the roadmap. Leave
> it open pending maintainer acceptance; do not create duplicate tracking issues.
>
> Implement only Thread 11. Add and fault-test the bounded transaction and recovery
> primitives with temporary synthetic vaults. Preserve intervening edits and
> refuse invalid journals. Do not widen into public build/sync implementation,
> automatic deletion, or Git operations. Leave changes uncommitted.

### Thread 12 — Public initialization and initial build

**Goal:** The first complete user journey from configuration to a managed vault.

**Depends on:** 11. **Status:** Not started.

**GitHub issue:** [#12](https://github.com/jeffshurtliff/obforce/issues/12)

**Issue template:** [`maintainer-feature.md`](https://github.com/jeffshurtliff/obforce/blob/main/.github/ISSUE_TEMPLATE/maintainer-feature.md)

**Blocked by:** [#11](https://github.com/jeffshurtliff/obforce/issues/11)

**Blocks:** [#13](https://github.com/jeffshurtliff/obforce/issues/13)

1. Implement `init` with mutually exclusive explicit sources, config-relative
   paths, non-overwriting config creation, and a write-free preview.
2. Connect `build` to source/graph/render/plan/writer, requiring an absent or empty
   destination and refusing source/template overlap or unrelated existing files.
3. Expose `recover` with validated preview/rollback and no source acquisition;
   provide clear messages for incomplete journals and unresolved user edits.
4. Add a small offline quickstart and end-to-end build tests; mock the live path
   without using credentials or altering an org.

**Locations:** `cli.py`, `sync/engine.py`, lifecycle integration tests,
`README.md`, `examples/obforce.example.toml`.

**Acceptance/demo:** A new user can initialize, preview, and build the fictional
project, then open readable notes; an existing nonempty destination is untouched.

**Validation:** Console/module invocation, absolute/relative paths with spaces,
missing prerequisites, noninteractive use, repeat-build refusal, rollback, dry-run
tree snapshots, clean installed package, and source-tree preservation.

**Copy-ready prompt:**

> Read GitHub issue https://github.com/jeffshurtliff/obforce/issues/12 and its linked
> prerequisite issues. Keep this existing issue updated with start/progress,
> verified checklist, and handoff evidence, synchronized with the roadmap. Leave
> it open pending maintainer acceptance; do not create duplicate tracking issues.
>
> Implement only Thread 12 after verifying the transaction tests. Expose init,
> initial build, and recovery using the established contracts. Demonstrate the
> offline synthetic quickstart and mocked live flow. Do not implement refresh,
> adopt arbitrary vaults, query real orgs, or publish. Leave changes uncommitted.

### Thread 13 — Public refresh and missing-component lifecycle

**Goal:** Trustworthy incremental writing that preserves knowledge over time.

**Depends on:** 12. **Status:** Not started.

**GitHub issue:** [#13](https://github.com/jeffshurtliff/obforce/issues/13)

**Issue template:** [`maintainer-feature.md`](https://github.com/jeffshurtliff/obforce/blob/main/.github/ISSUE_TEMPLATE/maintainer-feature.md)

**Blocked by:** [#12](https://github.com/jeffshurtliff/obforce/issues/12)

**Blocks:** [#14](https://github.com/jeffshurtliff/obforce/issues/14)

1. Expose `sync` and `--dry-run` using validated existing state and full preflight;
   apply only clean owned-region/property changes through the writer.
2. Preserve user sections/fields, handle unique note moves and affected backlink
   targets, and refuse generated-content edits or ambiguous ownership.
3. Implement comparable-complete-scan missing/reactivation rules, partial-source
   preservation, stale dependency behavior, and accurate incomplete result codes.
4. Add multi-run integration scenarios spanning build, human edits, source/graph
   changes, conflict refusal, recovery, and a byte/mtime-stable no-op refresh.

**Locations:** `cli.py`, `sync/engine.py`, planner/state refinements,
`tests/integration/test_sync_lifecycle.py`, user refresh docs.

**Acceptance/demo:** Add human context/debt fields, move one note, change a class
fact and incoming edge, then sync: edits survive, links resolve, and the next run
changes no managed bytes or modification times. Partial scans never retire notes.

**Validation:** Source/graph/template-only changes, empty complete versus failed
scans, missing/reactivated classes, changed filters/org, no state churn, conflict
batch refusal, and failures after some notes were published.

**Copy-ready prompt:**

> Read GitHub issue https://github.com/jeffshurtliff/obforce/issues/13 and its linked
> prerequisite issues. Keep this existing issue updated with start/progress,
> verified checklist, and handoff evidence, synchronized with the roadmap. Leave
> it open pending maintainer acceptance; do not create duplicate tracking issues.
>
> Implement only Thread 13. Add safe public refresh with ownership/conflict,
> note-move, coverage, no-op, and recovery behavior. Demonstrate the multi-run
> synthetic lifecycle and preserve all human fields. No force-overwrite, automatic
> note deletion, source switching, real org tests, or Git operations. Leave work
> uncommitted and report exact evidence.

### Thread 14 — Native dashboard and CLI usability

**Goal:** A discoverable administrator experience using native Obsidian features.

**Depends on:** 13. **Status:** Not started.

**GitHub issue:** [#14](https://github.com/jeffshurtliff/obforce/issues/14)

**Issue template:** [`maintainer-feature.md`](https://github.com/jeffshurtliff/obforce/blob/main/.github/ISSUE_TEMPLATE/maintainer-feature.md)

**Blocked by:** [#13](https://github.com/jeffshurtliff/obforce/issues/13)

**Blocks:** [#15](https://github.com/jeffshurtliff/obforce/issues/15)

1. Package a minimal Apex Classes `.base` view filtered by reserved managed-note
   identity/type, showing class, namespace, status, audit dates, and human debt
   fields. Keep ordinary notes useful without any dashboard/plugin.
2. Install the dashboard through the same planner/writer. Track its generated
   ownership/hash; user edits or path collisions cause conflicts, not replacement.
3. Polish command help, examples, privacy-aware counts/details, coverage warnings,
   and actionable conflict/recovery messages. Avoid hidden interactive prompts.
4. Verify keyboard-friendly plain terminal output and optional real Obsidian
   preview of a synthetic sample without changing user app settings or plugins.

**Locations:** `resources/bases/`, `renderer/dashboards.py`, CLI/reporting tests,
`examples/sample_vault/`.

**Acceptance/demo:** A fictional vault offers an Apex table and useful links;
unassessed debt remains distinguishable from false, and edited dashboards are
protected. No Dataview, Obsidian CLI, or community plugin is required.

**Validation:** YAML/schema checks against current official Bases syntax, packaged
asset access, dashboard conflict/no-op tests, path collisions, and help/example
consistency. Report separately whether a native app preview was actually done.

**Copy-ready prompt:**

> Read GitHub issue https://github.com/jeffshurtliff/obforce/issues/14 and its linked
> prerequisite issues. Keep this existing issue updated with start/progress,
> verified checklist, and handoff evidence, synchronized with the roadmap. Leave
> it open pending maintainer acceptance; do not create duplicate tracking issues.
>
> Implement only Thread 14. Add the minimal protected native Bases dashboard and
> polish the documented CLI journey using synthetic data. Verify current Bases
> syntax, asset packaging, and edited-dashboard preservation. Do not install
> plugins, change Obsidian settings, or add new metadata types. Leave work
> uncommitted and distinguish automated from native-app validation.

### Thread 15 — Platform, failure, and scale qualification

**Goal:** Evidence for the supported platforms and realistic local operation.

**Depends on:** 14. **Status:** Not started.

**GitHub issue:** [#15](https://github.com/jeffshurtliff/obforce/issues/15)

**Issue template:** [`maintainer-test.md`](https://github.com/jeffshurtliff/obforce/blob/main/.github/ISSUE_TEMPLATE/maintainer-test.md)

**Blocked by:** [#14](https://github.com/jeffshurtliff/obforce/issues/14)

**Blocks:** [#16](https://github.com/jeffshurtliff/obforce/issues/16)

1. Run offline tests and isolated wheel/sdist resource/entry-point checks across
   Linux/macOS/Windows and the selected stable Python matrix, targeting
   3.12–3.15 at this baseline. Verify interpreter/dependency availability before
   adding claims and retain unavailable cells as qualification gaps.
2. Harden path/link/junction, permissions, CRLF, Unicode/case, locking, interruption,
   and concurrent-edit boundaries on native platforms where possible.
3. Exercise a reproducible synthetic scale fixture, initially 1,000 classes and
   10,000 edges. Record elapsed time, peak memory, and environment; identify
   avoidable quadratic graph work or unnecessary per-component CLI calls.
4. Audit time/output/XML/YAML/template/state bounds, privacy, retries, and cleanup.
   Document selected supported filesystems and remaining native/live gaps.

**Locations:** CI workflow, targeted platform/integration tests,
`docs/COVERAGE.md`, `docs/SYNC_SAFETY.md`, qualification handoff.

**Acceptance/demo:** The offline lifecycle, preservation, and recovery checks pass
on the claimed matrix, or specific unsupported paths remain gated and documented.
Scale evidence is measured, not an invented throughput/service-level promise.

**Validation:** Full offline suite, Ruff/Bandit, fresh artifacts, native failure
cases and exact hosted evidence when runs are authorized. Mocked/native/live
evidence are distinct; a skip is never qualification.

**Copy-ready prompt:**

> Read GitHub issue https://github.com/jeffshurtliff/obforce/issues/15 and its linked
> prerequisite issues. Keep this existing issue updated with start/progress,
> verified checklist, and handoff evidence, synchronized with the roadmap. Leave
> it open pending maintainer acceptance; do not create duplicate tracking issues.
>
> Implement only Thread 15. Qualify the offline lifecycle, safety, packaging, and
> synthetic scale behavior across the stated matrix, fixing bounded defects.
> Report native, hosted, mocked, skipped, and unavailable evidence separately.
> Do not broaden metadata scope, run real org/vault tests, or advertise unverified
> platform support. Leave changes uncommitted.

### Thread 16 — User and maintainer documentation

**Goal:** An accurate, maintainable path from installation through safe refresh.

**Depends on:** 15. **Status:** Not started.

**GitHub issue:** [#16](https://github.com/jeffshurtliff/obforce/issues/16)

**Issue template:** [`maintainer-docs.md`](https://github.com/jeffshurtliff/obforce/blob/main/.github/ISSUE_TEMPLATE/maintainer-docs.md)

**Blocked by:** [#15](https://github.com/jeffshurtliff/obforce/issues/15)

**Blocks:** [#17](https://github.com/jeffshurtliff/obforce/issues/17)

1. Complete README and user guides for installation, separately managed `sf`
   authorization, offline/live setup, build/preview/refresh, note ownership,
   template overrides, dashboard use, and technical-debt conventions.
2. Document coverage limitations, selected namespaces, missing/stale semantics,
   identity/source-switch restrictions, supported platforms, and recovery.
3. Finish contribution/security guidance, synthetic example provenance, and a
   maintainer release runbook. Keep raw metadata/private outputs out of examples.
4. Execute every offline tutorial from a clean installation with the fictional
   sample. Add only documentation tooling justified by current needs; a large
   hosted Sphinx site is optional later rather than a v0.1.0 prerequisite.

**Locations:** `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `docs/`, `examples/`.

**Acceptance/demo:** A fresh user can follow the offline journey, customize safe
fields/templates, recognize coverage limits, and recover an interrupted fixture
run without reading implementation code.

**Validation:** Links, command examples/help, artifact install, privacy, selectable
sample data, and consistency among docs, note schemas, roadmap, and actual tests.
No dependency installation or application refactoring merely to check prose.

**Copy-ready prompt:**

> Read GitHub issue https://github.com/jeffshurtliff/obforce/issues/16 and its linked
> prerequisite issues. Keep this existing issue updated with start/progress,
> verified checklist, and handoff evidence, synchronized with the roadmap. Leave
> it open pending maintainer acceptance; do not create duplicate tracking issues.
>
> Implement only Thread 16. Finish and verify accurate user/contributor/security/
> release documentation and the clean-install offline tutorial. Describe actual
> limitations and evidence without promising full-org documentation. Do not build
> a hosted site, access production data, or start release preparation. Leave work
> uncommitted.

### Thread 17 — v0.1.0 release preparation

**Goal:** Reviewable `0.1.0` candidate artifacts and a concrete publication handoff.

**Depends on:** 16. **Status:** Not started.

**GitHub issue:** [#17](https://github.com/jeffshurtliff/obforce/issues/17)

**Issue template:** [`maintainer-release.md`](https://github.com/jeffshurtliff/obforce/blob/main/.github/ISSUE_TEMPLATE/maintainer-release.md)

**Blocked by:** [#16](https://github.com/jeffshurtliff/obforce/issues/16)

**Blocks:** None within v0.1.0.

1. Verify the acceptance matrix, dependency/license metadata, accurate platform
   claims, current changelog, and absence of unresolved preservation blockers.
2. Prepare final `0.1.0` metadata/changelog and only necessary lock updates;
   build fresh candidate wheel/sdist files in an isolated output directory.
3. Run strict artifact checks, inspect file lists for secrets/private content,
   and install each artifact in separate clean environments. Exercise help,
   offline build/edit/sync/no-op, recovery, templates, and dashboard resources.
4. Prepare public-safe release notes and the exact proposed manual publication
   steps. Record candidate checksums, environments, executed checks, and live/
   native limitations. Stop with the candidate for maintainer review.

**Locations:** Version metadata, `docs/CHANGELOG.md`, release runbook, fresh local
candidate artifacts and handoff; no committed build outputs.

**Acceptance/demo:** Both candidate distributions pass the required checks and the
installed offline lifecycle. The handoff clearly distinguishes prepared artifacts
from a published release.

**Validation:** Full relevant offline/security/docs checks; strict Twine checks;
isolated wheel and sdist installs; artifact resource/privacy/license audit.
Publication, tagging, release creation, pushes, and activation of workflows are
not part of this thread without separate direct authorization.

**Copy-ready prompt:**

> Read GitHub issue https://github.com/jeffshurtliff/obforce/issues/17 and its linked
> prerequisite issues. Keep this existing issue updated with start/progress,
> verified checklist, and handoff evidence, synchronized with the roadmap. Leave
> it open pending maintainer acceptance; do not create duplicate tracking issues.
>
> Implement only Thread 17 after verifying the release acceptance matrix. Prepare
> and validate fresh v0.1.0 candidates, release notes, and a reviewable publication
> handoff. Report checksums and actual evidence. Do not stage/commit, push, tag,
> create a release, upload to an index, or activate publishing automation. Leave
> the candidate and changes for review.

## 9. Acceptance matrix and validation strategy

| Release requirement | Primary threads | Required evidence |
| --- | --- | --- |
| Clean install, console/module entry points, Apache metadata | 01, 17 | Fresh wheel and sdist installs outside checkout |
| Python 3.12+ and honest supported-platform claims | 01, 15 | Actual stable matrix results; gaps retained explicitly |
| Offline input without network or source mutation | 03, 12 | Mock network/process prohibition and before/after source snapshots |
| Explicit live target and audit normalization | 04, 05 | Mocked multi-page/permission/error fixtures; opt-in live checks separately labeled |
| Honest dependency coverage and reciprocal links | 06, 07, 13 | Directed/reciprocal graph, unsupported endpoint, stale/partial cases |
| Bundled defaults and custom templates | 07, 17 | Installed resources, override/fallback/error tests |
| Human prose/properties/debt survive refresh | 08, 13 | Exact outside-body comparisons and supported YAML preservation tests |
| Stable identity and moved-note links | 09, 13 | Unique move reconciliation and duplicate/missing-note refusals |
| No destructive actions from incomplete scans | 06, 10, 13 | Partial/empty/changed-scope absence tests |
| Dry run performs no Obforce filesystem writes | 10, 12, 13 | Tree/hash/mtime snapshots and write-call assertions |
| No-op avoids note/state churn | 10, 13 | Repeated runs retain bytes and modification times |
| Conflict and unsafe-path refusal | 08–13, 15 | Generated edits, malformed inputs, overlap/collision/link/concurrency tests |
| Recoverable note/state publication | 11–13, 15 | Fault injection and process interruption at publication boundaries |
| Useful native dashboard without plugin dependency | 14 | Asset/schema tests and optional clearly labeled native preview |
| Safe onboarding and privacy | 16, 17 | Executed offline tutorial, source/artifact/log review |

Use pytest with deterministic unit and synthetic integration fixtures. Ordinary
tests run offline, never discover credentials, and never query a real org. Any
live test must be explicitly enabled and authorized for a named target, with
read-only operations and a separate report. The developer's own vault is not a
test fixture.

Tests should assert observable safety/behavior, not duplicate implementation.
Use temporary directories and real local subprocess/file interactions where
they establish recovery or packaging behavior. Mock Salesforce process results,
but distinguish those tests from actual platform validation. Keep snapshot
fixtures small enough for meaningful review.

Configured CI is not evidence of a passed run. Release support claims require
inspected results for the relevant code/artifacts. A release can document
best-effort dependency coverage, but cannot waive preservation, conflict, or
recovery failures by calling the release experimental.

## 10. Risks, decisions, and rollback

| Risk or edge case | Required handling |
| --- | --- |
| Scope grows toward every metadata type | Keep the Apex-first gate; add approved type-specific threads later |
| Dependency API unavailable or capped | Surface coverage and stale facts; verify limits; never infer complete impact analysis |
| Offline data lacks org audit facts | Leave unavailable and explain; no filesystem/Git-date substitution |
| Human edits overlap generated content | Detect against property/body baselines; refuse the batch |
| YAML round-tripping changes formatting | Define supported forms, test preservation, refuse unsafe structures |
| Alias changes, source switches, or reused names | Verify source identity; refuse ambiguous mapping |
| Moved/duplicated/deleted note | Reconcile unique ID or report conflict; never silently recreate/adopt |
| Partial scan resembles deletion | Require comparable complete scoped inventory before missing marking |
| Cloud sync or another editor races a write | Recheck before replacement, retain recovery evidence, document supported limits |
| Interrupted notes/state publication | Journal/before-images, safe rollback, startup recovery gate |
| Template or source injects paths/markers/links | Validate containment, serialization, escaping, markers, and bounded output |
| Metadata/audit facts expose internal details | Local storage, allowlists, optional audit labels, no raw logs/public fixtures |
| Custom templates exhaust resources | Explicit local trust, restricted context, bounded rendering, fail before writes |
| Work is described as done too early | Separate proposed, implemented locally, validated, accepted, and published states |

For application-code changes, retain the working tree diff for review and keep
previous releases available through ordinary version control; do not reset or
discard maintainer changes as a rollback shortcut. For a failed vault operation,
use only the validated transaction recovery procedure. For a successfully
completed generation that the user later dislikes, use their independent backup
or version history; v0.1.0 is not a general historical vault rollback tool.

The focused metadata scope is confirmed. Remaining material decision points are
live dependency API capability, supported YAML/template forms and public CLI delivery, native platform qualification, and
release acceptance. Routine internal choices may be made within a requested
thread. Changing ownership, deleting user content, weakening safety, or expanding
public scope requires a recorded maintainer decision.

## 11. Tracking and future handoff records

Each of the 17 roadmap threads now has a real linked GitHub issue in
[`v0.1.0`](https://github.com/jeffshurtliff/obforce/milestone/1); Thread 01 maps to issue #1 through Thread 17 to
issue #17. Each issue contains its four implementation subtasks, acceptance/demo,
validation, the appropriate maintainer-template sections, actual prerequisite
and dependent issue links, and progress/handoff guidance.

**Maintainer tracking authorization — 18 October 2026:** When implementation of
a named roadmap thread is requested, keep its existing issue updated throughout
that work as described in the common thread contract. This scoped authorization
covers start/progress/blocker/handoff comments and truthful checklist updates;
it does not authorize new issues, other-chat messages, closure without approval,
or Git/release/publication actions. If authorization is later narrowed for a
particular task, follow that instruction. Update only verified progress and
leave partial work or pending review accurately labeled.

Use status labels such as **Not started**, **In progress**, **Implemented locally;
validation gaps remain**, **Ready for maintainer review**, and **Accepted**.
Track commit/merge/publication evidence separately rather than overloading
"complete." Never mark a dependency ready solely because its issue is closed.

For each future thread, append a compact record:

```text
Thread / date:
Authorized scope:
Repository baseline and dependency evidence:
Files and behavior changed:
Acceptance criteria met / remaining:
Checks executed (environment, result):
Skipped or unavailable checks:
Privacy / data-preservation evidence:
Maintainer decisions or deviations:
Git state / review state:
Next eligible thread (not started):
```

**Planning handoff — 18 October 2026:** Prepared this proposed roadmap and root
agent guidance from the two accessible Obforce project conversations and the
dated local checkout. The Obfuscidian plan supplied structure, not transferred
feature requirements. No Obforce application implementation, dependencies,
Salesforce access, vault changes, issue updates, commits, or publication were
performed. All 17 implementation threads remain not started.

**Scope confirmation — 18 October 2026:** The maintainer selected the focused
Apex-first release, confirming live Salesforce and offline project inputs,
dependency links where available, and safe build/refresh workflows. Updated this
roadmap and root agent guidance to record that decision. Detailed implementation
defaults remain proposed; no implementation thread was started.

**Housekeeping handoff — 18 October 2026:** Adapted all 16 copied GitHub issue
templates for Obforce, preserving their categories, labels, and general structure.
Replaced encryption/backup examples with Salesforce source, coverage, note
ownership, refresh, and recovery context; updated privacy guidance and removed
links to absent contributor/release guides. Release preparation now follows this
roadmap without assuming another project's publishing automation. Local macOS
review checked YAML frontmatter/required fields, repository link targets against
local files, obsolete references, Markdown fences, privacy, and whitespace
(including the untracked templates). GitHub rendering and application/live/native
qualification were not exercised for this prose-only task. The templates remain
untracked and all changes are unstaged/uncommitted, pending maintainer review;
no external actions were taken. No scope decision or implementation blocker was
introduced. Thread 01 remains the next eligible thread, explicitly not started.

**GitHub roadmap tracking — 18 October 2026:** At the maintainer's explicit
request, verified the source roadmap, root agent guide, and selected maintainer
templates against `main` at `d80cad5d59623f8cdf41e9e5bd5ecd7e5152c8fe`.
The prior housekeeping work and templates were already committed in that
baseline; its earlier uncommitted handoff wording is historical.

Created issues [#1](https://github.com/jeffshurtliff/obforce/issues/1)–[#17](https://github.com/jeffshurtliff/obforce/issues/17), one per implementation
thread, using `maintainer-chore.md`, `maintainer-feature.md`,
`maintainer-test.md`, `maintainer-docs.md`, and `maintainer-release.md` according
to the work category. All issues are open, assigned to `jeffshurtliff`, labeled
with `maintainer`, `codex`, and the applicable category/supplementary labels, and
associated with [milestone `v0.1.0`](https://github.com/jeffshurtliff/obforce/milestone/1). Added the 21 exact direct
blocked-by relationships through GitHub's dependency API and cross-linked both
prerequisites and dependents in the issue bodies. The release issue covers
preparation only and retains separate publication authorization checkpoints.

Verified the live issue metadata, final bodies, and native blocked-by/blocking
relationships against the roadmap. Updated the thread index, all 17 thread
references, kickoff prompts, and progress/handoff contract while preserving all
68 implementation subtasks, scope, acceptance criteria, validation, and the
existing housekeeping record. Document structure, links, privacy, and whitespace
checks passed; no application tests were appropriate for this tracking-only work.
The connected GitHub app could not access the private repository; the requested
changes were completed through the authenticated GitHub CLI.

The updated plan was prepared as a replacement file outside the checkout for
the maintainer to add to the repository. No repository files, application code,
Salesforce org, or vault were changed; no commit/push/publication was performed.
**All 17 implementation threads remain not started. Thread 01 / issue #1 is next.**

**Thread 01 start — 18 October 2026:** Authorized foundation implementation against
clean baseline `4ce3d28`. Read root agent guidance, this roadmap, and issue #1;
no prerequisite issues exist (verified body and native blocked-by API). Root
`CONTRIBUTING.md` and `local/vendor_docs/` are absent. Work is limited to packaging,
help/version, offline tooling/tests, test-only CI, and guidance. Preserve the
Apache license; leave changes uncommitted and issue #1 open pending acceptance.
Threads 02–17 remain not started.

**Thread 01 implementation decisions — 18 October 2026:** Use Click alone at
runtime; defer rendering/YAML/XML dependencies to their owning threads. Current
PyPI metadata verified Click 8.5.0 and poetry-core 2.5.0 before resolution.
Poetry 2.4.2 is the local/CI tool baseline; build isolation uses poetry-core
`>=2.5,<3` for current SPDX metadata. Static PEP 621 is the sole version source.
Official `actions/python-versions` manifest lists stable 3.15.0 artifacts for
Linux, macOS, and Windows; configure the 3.12–3.15 test matrix without claiming
passed hosted cells. Official Actions releases verify checkout v7.0.1 and
setup-python v7.0.0; use their v7 majors. No template/Bases assets or source
connectors are added; installed asset behavior remains with Threads 07/14.
These are routine foundation choices, with no scope or ownership change.

**Thread 01 progress — 18 October 2026:** Foundation files are implemented
locally. Initial macOS ARM64 / Python 3.14.7 run: 19 offline tests, Poetry
metadata/lock, Ruff lint/format, Bandit, fresh build/strict Twine, and independent
wheel/sdist installs passed. Complete archive lists and unchanged Apache license
were checked; installed entry points passed outside checkout without external
tools or runtime socket access. A checker-only metadata-whitespace assumption
was corrected. Subprocess coverage and an additional import-safety test were
added; final suite/artifact checks and other available local interpreters remain
pending. No hosted CI/live/native Windows/Linux evidence is claimed. Issue #1
has matching start/progress comments; it remains open. Work is unstaged and
uncommitted; Thread 02 remains not started.

### Thread 01 handoff — 18 October 2026

**Status:** Ready for maintainer review; issue #1 remains open. Local validation
meets the foundation demo; hosted/platform gaps below are retained.

**Authorized scope/baseline:** Thread 01 only, starting from clean `main` at
`4ce3d28`. Issue #1 and its native blocked-by list have no prerequisites. Root
agent guidance, full roadmap, and issue were read; no contributor guide or vendor
docs existed. No source connectors or later-thread modules were implemented.

**Verified implementation checklist:**

- [x] Preserved Apache license and maintainer files; added Poetry/PEP 621 static
  `0.1.0.dev0`, Python `>=3.12`, `src/obforce/`, both entry points, and a
  Poetry-generated lockfile. Version reporting uses installed metadata.
- [x] Added Click alone at runtime, justified locked dev tools, configured Ruff,
  unit/integration tests, offline socket guards, and subprocess-aware coverage.
- [x] Added `CONTRIBUTING.md`, `SECURITY.md`, `docs/CHANGELOG.md`, focused ignores,
  README discovery instructions, and links between guidance and roadmap.
- [x] Added test-only 12-cell CI and inspected fresh artifact exclusions. No
  publishing/upload/deploy steps or credential-dependent tests exist.

**Files/behavior:** `pyproject.toml`, `poetry.lock`, `src/obforce/`, `tests/`,
`.github/workflows/test.yml`, `dev/check_artifacts.py`, root guidance, README,
changelog, and ignores. Only help/version and no-argument discovery are available;
`init`, `build`, `sync`, and `recover` fail with usage code 2. No stable public
Python API is promised. The artifact checker's small Thread 01 allowlist must be
extended deliberately when later threads add packaged modules/assets.

**Checks actually executed:** Native macOS 27.0.1 ARM64; Poetry 2.4.2. Locked
pytest 9.1.1, pytest-cov 7.1.0, Ruff 0.17.1, Bandit 1.9.4, Twine 7.0.0, Click
8.5.0. Python 3.14.7 is the repository `.venv`; 3.12.7 and 3.13.15 used separate
temporary locked Poetry environments.

| Local check | Actual result |
| --- | --- |
| `poetry check --lock --strict` | Passed |
| Ruff lint and format check | Passed; only UP009 excluded to retain required encoding headers |
| `pytest -q` on 3.12.7 / 3.13.15 / 3.14.7 | 20 passed on each; no skips |
| 3.14.7 suite with subprocess coverage | 20 passed; 100% statement/branch coverage of the small foundation package |
| `bandit -r src/obforce` | Passed, no findings/suppressions |
| Fresh `poetry build` and strict Twine | Both final r2 artifacts passed |
| Independent wheel and sdist installs | Both passed separately on each of 3.12.7 / 3.13.15 / 3.14.7 (six clean installs outside checkout) |
| Installed smoke checks | Import provenance, installed metadata/resources, `pip check`, both help/version entry points, future-command refusal, no runtime sockets/external tools or working-directory writes |
| Workflow/docs/diff review | YAML structure and 12-cell matrix, links/fences, new-file LF/whitespace/privacy, tracked diff, untracked file list, `git diff --check` passed |

**Artifact evidence:** Final candidates are retained outside the checkout under
`<temporary>/obforce-thread01-candidate-r2/`. Full lists were inspected: the wheel
has three package Python files plus METADATA, WHEEL, entry points, RECORD, and
license (8 members); the sdist has those three source files plus LICENSE, README,
pyproject, and PKG-INFO (7 members). Exact allowlists reject extra/duplicate paths
and sdist links/special files. Neither artifact contains private `local/`, vaults,
state/recovery data, tests, developer tools, workflow files, or planning records.
Both include byte-identical root LICENSE and Apache-2.0 metadata.

| Final artifact | SHA-256 |
| --- | --- |
| `obforce-0.1.0.dev0-py3-none-any.whl` | `127cb347b01fde3edc41b8b26e23cefdaee88198a7c66ddfde5e373a4a52af5d` |
| `obforce-0.1.0.dev0.tar.gz` | `9b0fe8a1b9290e7735b44a64ba88d9fc1d03e7d7bef32c8f61548cb962810095` |

**Gaps/limits:** No hosted workflow execution, native Linux/Windows test, or local
Python 3.15 run was performed. Stable 3.15 runner availability was verified, not
execution compatibility. No real Salesforce/org/vault/Obsidian tests were run or
authorized. Installed template/Bases tests wait for Threads 07/14. Setup and
isolated pip/build dependency acquisition used the network; application smoke
tests blocked Python socket operations. No platform support qualification is
claimed from configured CI or the limited foundation tests.

**Decisions/deviations:** No material scope/ownership deviation or unresolved
implementation decision. Initial lint/format findings were corrected, retaining
the required encoding headers through a targeted Ruff exception. A checker-only
entry-point whitespace assumption was fixed. Initial candidates remain superseded
by final r2 after coverage configuration changed; no failed check is claimed as
a pass. Maintainer confirmed the Python-header model name as `GPT-6.1 Sol`.

**Privacy/review/Git:** No credentials, real metadata, or vaults were inspected.
`LICENSE`, `AGENTS.md`, and existing issue templates are unchanged. Start/progress
and verified checklist/handoff evidence are recorded in existing issue #1 using
the authenticated CLI (the connector could not access this repository). All
repository changes remain unstaged/uncommitted on `main`; no branch, issue, PR,
commit, push, publication, or workflow activation was created/performed.

**Issue evidence:** [Start](https://github.com/jeffshurtliff/obforce/issues/1#issuecomment-6258959653),
[progress](https://github.com/jeffshurtliff/obforce/issues/1#issuecomment-6259017940),
and [final handoff](https://github.com/jeffshurtliff/obforce/issues/1#issuecomment-6259052477)
were posted; verified task/test/doc checkboxes are checked and Ready to close is
unchecked. The GitHub main-branch roadmap remains the prior baseline until
separately authorized delivery of this uncommitted local roadmap.

**Next eligible thread:** Thread 02 / issue #2, after maintainer acceptance and
verification of this foundation. **Explicitly not started.**

### Thread 01 merge and CI follow-up — 19 October 2026

**Current status:** Foundation reviewed, committed, merged, and pushed by the
maintainer. A Windows test correction is prepared and validated locally; delivery
and post-fix Windows CI remain pending. Issue #1 remains open. This record
supersedes the original handoff's uncommitted/unrun current-state wording without
changing its historical evidence or candidate hashes.

**Delivery evidence:** Foundation commit
[`789f5ef35ef4c018f0f64c6dd0f97fb0b2536b76`](https://github.com/jeffshurtliff/obforce/commit/789f5ef35ef4c018f0f64c6dd0f97fb0b2536b76)
was merged through
[`7f3ceb1cc06d91c81e4a8f89efb451f33d85d6f1`](https://github.com/jeffshurtliff/obforce/commit/7f3ceb1cc06d91c81e4a8f89efb451f33d85d6f1).
Local `main`, local `origin/main`, and GitHub's live `main` matched that merge;
the checkout was clean before follow-up. The maintainer's new workflow path
filters are preserved. Review/merge/push do not turn failed CI into qualification.

**Hosted evidence:** Inspected all 12 job conclusions, step outcomes, and test
summaries in push run
[`39261152793`, attempt 1](https://github.com/jeffshurtliff/obforce/actions/runs/39261152793)
at the merge SHA. The overall conclusion is **failure**.

| Hosted cells | Verified outcome on merged foundation |
| --- | --- |
| Ubuntu / Python 3.12, 3.13, 3.14, 3.15 | Four jobs passed: 20 tests each, strict build/artifact checks, independent wheel/sdist installs, and whitespace checks |
| macOS / Python 3.12, 3.13, 3.14, 3.15 | Four jobs passed: 20 tests each, strict build/artifact checks, independent wheel/sdist installs, and whitespace checks |
| Windows / Python 3.12, 3.13, 3.14, 3.15 | Four jobs failed: 4 console cases failed and 16 tests passed per job; build/Twine/artifact-install steps were skipped |

The [linked Windows 3.12 job](https://github.com/jeffshurtliff/obforce/actions/runs/39261152793/job/118088823617)
failed before process startup with `FileNotFoundError: [WinError 2]` for the
assumed `Scripts/obforce.exe`. All four Windows job logs show this same failure.
Poetry 2.4.2's installed and
[tagged editable builder](https://github.com/python-poetry/poetry/blob/2.4.2/src/poetry/masonry/builders/editable.py)
write an extensionless Python script plus `.cmd` on Windows; pip's isolated wheel
install uses a separate executable launcher. This was an incorrect test-path
assumption, not a demonstrated CLI behavior failure. Windows artifact operation
remains unverified because its checks did not run.

**Bounded correction / files:** `tests/integration/test_entrypoints.py` now invokes
Poetry's real installed script using the active interpreter on Windows, fails if
that script is absent, and retains native console dispatch on POSIX. Four added
cross-platform `console-via-python` cases exercise this invocation on local hosts.
No test is skipped or replaced with `python -m obforce`. The separate
`dev/check_artifacts.py` still directly exercises pip's installed executable on
Windows. `CONTRIBUTING.md` explains the distinction; `docs/CHANGELOG.md` records
the fix. There are no application, dependency, lockfile, package-resource, license,
or workflow changes in this follow-up.

**Local follow-up validation:** Native macOS ARM64, Python 3.12.7 / 3.13.15 /
3.14.7: **24 tests passed on each**, no skips. The 3.14.7 subprocess-aware coverage
run reports 100% statements/branches for the foundation package. Poetry
metadata/lock, Ruff lint/format, Bandit (no findings), docs link/fence checks,
and `git diff --check` passed. These runs validate the interpreter-driven script
route on macOS; they are not a native Windows result. No new build was needed
for the test/docs-only correction; the eight successful hosted cells above are
evidence for the merged code, not for this uncommitted follow-up.

**Remaining gates / handoff:** Commit/push of this correction requires separate
maintainer action or authorization. Inspect a new run for the corrected commit,
including all four Windows suites and their previously skipped artifact steps,
before marking the CI defect resolved or #1 ready to close. Do not rerun the old
merge and claim it tests the correction. No real org/vault/native Obsidian tests
were performed. No new issues, commits, pushes, PRs, or CI reruns were created by
this follow-up. All follow-up changes remain unstaged/uncommitted on `main`.

**Issue evidence:** [Follow-up start](https://github.com/jeffshurtliff/obforce/issues/1#issuecomment-6268655813)
and [follow-up handoff](https://github.com/jeffshurtliff/obforce/issues/1#issuecomment-6268713199)
were posted. Issue #1's body/checklist now records delivery of the foundation,
reopens implementation-complete for the pending correction, and leaves Ready to
close unchecked; the issue remains open. The new local roadmap follow-up is
uncommitted and does not yet replace the GitHub main-branch version.

**Next thread:** Thread 02 / issue #2, after the prerequisite repair is delivered
and verified. Its copy-ready prompt above includes that gate. Thread 02 and all
later threads remain **not started**.

### Thread 01 acceptance and closure — 19 October 2026

**Status:** Accepted and complete. The maintainer reviewed and pushed the
correction, reported passing CI, and explicitly authorized updating/closing #1
when verified. All Thread 01 acceptance and follow-up gates are satisfied;
issue #1 is closed as completed. Thread 02 is next eligible and **not started**.
This record supersedes pending/uncommitted wording in the historical handoffs.

**Verified delivery:** Local `main`, local `origin/main`, and GitHub's live main
matched correction commit
[`72471d2a478e37ff7e93f095858d95bc619ec566`](https://github.com/jeffshurtliff/obforce/commit/72471d2a478e37ff7e93f095858d95bc619ec566).
It includes the launcher test correction and follow-up docs after foundation
merge `7f3ceb1`. The checkout was clean before this tracking-only update.

**Hosted acceptance evidence:** Inspected completed push run
[`39266996850`, attempt 1](https://github.com/jeffshurtliff/obforce/actions/runs/39266996850),
its exact head SHA, all 12 job conclusions and required step results, and full
logs. Every Ubuntu/macOS/Windows cell on Python 3.12, 3.13, 3.14, and 3.15 passed:

- 24 tests per cell, including the corrected Windows console-script cases.
- Poetry metadata/lock, Ruff lint/format, and Bandit source checks.
- Fresh wheel/sdist builds and strict Twine checks.
- Independent wheel and sdist installations, imports/package-file access,
  dependency consistency, console/module smoke tests, future-command refusal,
  blocked runtime sockets, and unchanged working directory (24 artifact installs
  across the 12 cells). Windows artifact steps ran and passed this time.
- Whitespace checks. No required verification step was skipped.

The original failed run `39261152793` remains historical evidence; it has not
been rewritten as a pass. The corrected run closes the specific Windows CI gap.
These are hosted foundation results, not full future lifecycle/native filesystem
qualification. Real Salesforce, vault, Obsidian, recovery, templates, dashboards,
and scale checks remain outside Thread 01 and with their owning threads.

**Closure evidence:** [Final issue handoff](https://github.com/jeffshurtliff/obforce/issues/1#issuecomment-6269433510); read back
issue #1 as `closed` with reason `completed`, all checklist gates checked, and
its direct dependent #2 still open.

**Tracking/checks/Git:** Updated the roadmap's current status/index, Thread 01
acceptance, and Thread 02 prerequisite/prompt. Updated #1's status/checklist,
recorded the exact commit/run evidence, and closed it using the maintainer's
explicit authorization. Preserved all historical comments, failures, and local
candidate hashes. Documentation link/fence/privacy/consistency and
`git diff --check` checks passed; no application tests or rebuild were needed for
this tracking-only change. Only this roadmap update is unstaged/uncommitted on
`main`; no new commit, push, PR, CI rerun, release, org access, or vault work was
performed. The remote roadmap remains at its pushed version until this local
tracking update is delivered separately. No implementation blocker remains for
Thread 02, whose implementation is explicitly left to the new chat.

### Thread 02 start and contract decisions — 19 October 2026

**Baseline/gate:** Clean checkout, local `main`, and `origin/main` match live main
`fc9e2b7e055b3efe60fbfcb411c5d74b94f860ab`. Foundation merge `7f3ceb1` is an
ancestor of delivered correction `72471d2`. Re-read #2 and its sole direct
prerequisite #1, including the native dependency edge and reciprocal link.
Inspected run `39266996850` at the correction: all 12 jobs and every required
test/build/Twine/independent-install step passed, including Windows 3.12–3.15.
Original run `39261152793` remains a failure (eight Linux/macOS passes, four
Windows failures). Current `fc9e2b7` has no workflow run/checks: the only change
since the tested correction is this roadmap, excluded by preserved workflow
filters. Application, tests, package tooling, and workflow are identical to the
tested correction. This is verified prerequisite-code evidence, not a claim
that CI ran at `fc9e2b7` or on the forthcoming uncommitted Thread 02 changes.

**Scope:** Internal configuration/records/contracts and offline tests/docs only.
No connectors, rendering, note parsing, state loading/publication, mutation
commands, live org/vault access, or new dependencies. Threads 03/04 not started.

**Decisions recorded before implementation:**

- Schema/model/note/state/marker versions start at 1. Explicit config only;
  required source mode and selector; strict keys/types at every TOML table;
  no environment expansion/discovery/fallback. Root paths resolve from config
  location; layout paths are portable vault-relative paths. Later publication
  threads must perform filesystem/link/concurrency preflight too.
- Freeze the proposed note property names and exact marker pair in constants;
  all other properties remain user-owned. Unrecognized reserved `sf_*` fields
  require refusal, not silent adoption. Note parsing remains Thread 08.
- Canonical JSON is UTF-8, sorted object keys, compact separators, no nonfinite
  numbers; record-owned unordered collections sort explicitly. Structured
  workspace/type/namespace/name keys preserve case and Unicode. Reject duplicate
  identities rather than deduplicating conflicting records. Distinguish absent,
  unavailable, explicit null, empty, and false. Only allowlisted normalized
  attributes enter source hashes; collection timestamps and host paths do not.
- Bind workspace plus mode and verified live org ID (never alias); local source
  identity is the configured workspace, not its machine path. Refuse cross-mode,
  workspace, or org rebinding. No automatic live/offline reconciliation.
- Render fingerprints include source, incoming/outgoing relationship and resolved
  target-path inputs, generated template content, renderer/schema versions,
  and relevant layout/options. Creation template content affects new notes only.
- Exit precedence is conflict/recovery (3), invalid usage/config (2), operational
  failure (1), requested incomplete coverage (4), then success (0). Validation
  normally stops at the earliest failing phase; precedence resolves aggregated
  outcomes without hiding recovery behind another error. Offline by-design
  unavailable enrichment is reported without itself forcing exit 4.
- Typed errors use Click's existing exception protocol for consistent terminal
  exits; they perform no I/O and add no public commands. These remain private,
  versioned internal contracts, not a stable public Python API.

**Tracking/Git:** Issue #2 remains open pending acceptance; changes will remain
unstaged/uncommitted. Exact verified checklist and final evidence follow after
validation. Maintainer confirmed header model `GPT-6.1 Sol` for this chat.

### Thread 02 handoff — 19 October 2026

**Status/scope:** Ready for maintainer review, not accepted or delivered. Existing
issue #2 stays open. Implemented only internal configuration, models, constants,
typed errors, deterministic hashes, and contracts with offline tests. Production
CLI still exposes help/version only. Threads 03 and 04 explicitly **not started**.

**Prerequisite:** The start record above verifies foundation merge `7f3ceb1`,
delivered Windows correction `72471d2`, and all 12 successful jobs/required steps
in exact-commit run `39266996850`. Original run `39261152793` remains failed.
Baseline `fc9e2b7` has no run/checks and differs only in the roadmap; this is not
reported as a current-SHA CI pass. No hosted CI exists for this uncommitted work.

**Files/behavior:** `src/obforce/{config,constants,errors,models}.py` provide strict
bounded explicit TOML loading, config-relative native/portable relative paths,
selector/overlap refusal, immutable normalized records, field availability,
structured source identities, source binding, collision checks, canonical JSON
and SHA-256, independent coverage/request intent, exact ownership/version/marker
constants, render/graph/path invalidation, and exit precedence 3 > 2 > 1 > 4 > 0.
`tests/unit/test_{config,models,errors}.py` exercise the contracts offline.
`docs/{CONFIGURATION,COVERAGE,NOTE_FORMAT}.md` specify exact behavior and future
boundaries with fictional examples. README, contributor guidance, changelog, and
this roadmap are synchronized. `dev/check_artifacts.py` deliberately extends its
exact allowlist to the four modules and probes installed model construction/hash.
No new dependencies, source adapters, template rendering, note parsing, state
document loading, vault publication, or public mutation commands were added.

**Verified local acceptance:**

- [x] Strict schema/key/type/source selection, config-relative/absolute paths,
  no fallback, and no source/vault writes on valid or invalid explicit config.
- [x] Component/coverage/relationship/note-state records, structured identity and
  namespace/scope, allowlisted facts, independent unavailable/null/false/empty/zero,
  collisions, ordering, and timestamp-independent semantic hashes.
- [x] Exact property/marker/schema/source-switch/render contracts and tested Click
  usage/operational outcomes and precedence, with production CLI unchanged.
- [x] Three contract docs, changelog, reviewed compatibility, and synchronized
  issue/roadmap evidence. No published stable contract was changed.
- [ ] Maintainer acceptance, authorized delivery, and hosted Thread 02 validation.

**Actual local evidence:** Native macOS 27.0.1 ARM64, Poetry 2.4.2. Reused the
existing locked temporary environments on Python 3.12.7/3.13.15; repository `.venv`
uses Python 3.14.7. No org, vault, Obsidian, or `sf` was accessed.

| Check | Result |
| --- | --- |
| `poetry check --lock --strict` | Passed; dependency/lock bytes unchanged |
| Ruff lint / format check | Passed; no new suppressions |
| Offline pytest on 3.12.7 / 3.13.15 / 3.14.7 | **117 passed on each; no skips** |
| Subprocess-aware 3.14.7 coverage | **96% combined statement/branch coverage**; 456 statements, 170 branches, remaining gaps reported, not hidden |
| Bandit over `src/obforce` | Passed; no findings/suppressions |
| Final fresh r4 build / strict Twine | Wheel and sdist passed |
| Independent wheel/sdist installs | Two clean Python 3.14.7 environments outside checkout passed |
| Artifact checks | Full exact file lists, imports/model hashing, package-file access, pip check, console/module help/version, future-command refusal, blocked runtime sockets/external tools, no working-directory writes |
| Docs/review | Local links, fences, fictional TOML examples loaded without destination writes, exact ownership allowlist, LF/whitespace/privacy and changed/untracked review passed |
| Preservation | Apache LICENSE, AGENTS.md, pyproject, lock, workflow, and existing CLI bytes match baseline |
| `git diff --check` | Passed |

**Artifact evidence:** Final candidates remain outside the checkout at
`<temporary>/obforce-thread02-candidate-20261019-r4/`. Wheel: 12 members (seven
source modules plus standard metadata/entry points/license); sdist: 11 members
(seven source modules plus LICENSE, README, pyproject, PKG-INFO). Exact allowlists
reject extras, duplicates, and sdist special/link members. No private `local/`,
org/vault/state/recovery data, tests, developer tools, planning records, or
workflow files are included. Both preserve root license bytes/Apache-2.0 metadata.

| Final candidate | SHA-256 |
| --- | --- |
| `obforce-0.1.0.dev0-py3-none-any.whl` | `d1e84c5f989e863b183b1c2a2076411e20ebd13ff93d7e6f59e7fd7988863b54` |
| `obforce-0.1.0.dev0.tar.gz` | `4e0a1a0867ac2e33017fd9db2125a985e98dc20a51fddd4efebbcfb76bb4a581` |

**Findings/decisions:** No material scope/ownership deviation or unresolved
decision. Recorded contract choices before coding. Review corrected boolean/int
baseline equality, mixed-workspace batches, and a reproduced excessive-TOML-nesting
raw recursion failure; focused regression tests pass. Creation-only candidate
fingerprints are separate from the generated render hash saved on first build,
avoiding a refresh invalidation caused solely by a creation-template change.
Initial sandbox build r1 failed to reach PyPI; approved isolated dependency
acquisition succeeded. Passed r2/r3 builds remain superseded by final r4 after
README/review corrections; none is represented as the final artifact. Setup/build/
installation used network access; application tests/smoke checks were offline.

**Gaps/limits:** No hosted Thread 02 run, native Linux/Windows run, or local Python
3.15 run. The symlink refusal case ran locally without skipping; other hosts may
skip only that case if native symlink creation is unavailable, which must remain
an explicit gap. No real Salesforce/vault/Obsidian, connector/process mocks,
rendering, YAML preservation, transaction/recovery, scale, or full lifecycle
qualification was performed; those belong to later threads. The foundation's
passing hosted matrix does not qualify these new contracts across platforms.

**Tracking/review/Git:** Existing issue #2 has start/progress and final verified
checklist/handoff evidence; Ready to merge/release stays unchecked. Native
prerequisite/dependent links, labels, assignment, and milestone are retained.
Local roadmap status/index/contracts and this handoff are synchronized; its new
changes are not on GitHub main until separately authorized delivery. All 15
changed/new files remain unstaged/uncommitted on the existing
`feature/2-thread-02-config-models-and-contracts` branch at `fc9e2b7`; no new
issue, branch, commit, push, PR, closure, CI rerun, release, or publication.
Final status/reflog review identified the existing feature branch; this work did
not create or switch it. Earlier issue progress/handoff branch wording was
corrected. `main`, `origin/main`, and checkout HEAD still share baseline `fc9e2b7`.

**Issue evidence:** [Start/prerequisite verification](https://github.com/jeffshurtliff/obforce/issues/2#issuecomment-6269605100),
[progress](https://github.com/jeffshurtliff/obforce/issues/2#issuecomment-6269805026),
and [final checklist/handoff](https://github.com/jeffshurtliff/obforce/issues/2#issuecomment-6269881873).
Read back #2 as open with all four implementation tasks and the verified
implementation/tests/docs/compatibility checklist checked; Ready to merge/release
unchecked. Original maintainer/codex/enhancement labels, maintainer assignment,
v0.1.0 milestone, prerequisite #1, and direct dependents #3/#4 are preserved.

**Next eligible work after acceptance/delivery verification and a new request:**
Thread 03 / #3; Thread 04 / #4 also depends directly on this thread and may be
requested independently. Both are explicitly **not started**.

### Thread 02 delivery and CI follow-up — 19 October 2026

**Status:** Core reviewed and delivered by the maintainer. Closure is withheld:
Windows formatter failures invalidate the apparent all-green CI result. Issue
#2 remains open and Threads 03/04 are not started. This record supersedes the
historical handoff's undelivered/current-evidence wording while preserving it.

**Delivery/code verification:** Clean local `main`, `origin/main`, and live
GitHub main matched merge
[`785b45d5fdbd03dc877d85a84d3f24bc0654e9f1`](https://github.com/jeffshurtliff/obforce/commit/785b45d5fdbd03dc877d85a84d3f24bc0654e9f1),
containing implementation
[`3cb1bc485631763463a3759063a132096394e66e`](https://github.com/jeffshurtliff/obforce/commit/3cb1bc485631763463a3759063a132096394e66e).
All seven delivered Python package modules match the reviewed local r4 wheel
bytes. The maintainer's prior `cc68b17` workflow path-filter edits are preserved.
The maintainer explicitly requested issue updates/closure if justified after
review; no new implementation/publication authority for later threads is implied.

**Hosted evidence:** Inspected exact-head push run
[`39275023920`, attempt 1](https://github.com/jeffshurtliff/obforce/actions/runs/39275023920),
all 12 job/step conclusions, and full logs. GitHub reports overall success and
all jobs/required steps as successful, but command-level evidence differs:

| Hosted cells | Actual verified commands |
| --- | --- |
| Ubuntu/macOS, Python 3.12–3.15 (8 jobs) | 117 tests each, no skips; metadata/lock, Ruff lint/format, Bandit, fresh build/Twine, both independent artifact installs and whitespace checks passed |
| Windows, Python 3.12–3.15 (4 jobs) | 117 tests each, no skips; metadata/lock, Ruff lint, Bandit, fresh build/Twine, both independent artifact installs and whitespace checks passed; **Ruff formatting failed: 18 files would be reformatted, 20 already formatted** |

All cells report 96% combined coverage. The 24 independent installs passed their
installed import/model/resource, dependency, entry-point, future-command refusal,
offline/no-write checks. This is real hosted execution, not full lifecycle or
filesystem/recovery qualification. Historical foundation failures and local
candidate hashes remain unchanged.

**Failure mechanism:** On Windows, the multi-command `Validate metadata and
source` PowerShell step runs Bandit after Ruff formatting. The final successful
native command masks the earlier formatter exit code. The Windows logs show
line-ending-only formatter diffs for 18 repository Python/Markdown files. The
repository had no checkout line-ending attributes. A local CRLF fixture reproduces
Ruff exit 1; identical LF bytes pass. This is more specific than inferring a
pass from the step badge. Example affected Windows job:
[`118136961590`, Python 3.12](https://github.com/jeffshurtliff/obforce/actions/runs/39275023920/job/118136961590).

**Bounded follow-up prepared:** `.gitattributes` uses `* text=auto eol=lf` to retain
LF repository text while preserving automatic binary detection. The workflow
splits environment selection, locked installation, metadata/lock, Ruff lint,
Ruff formatting, and Bandit into individual single-command steps. Exact commands,
order, matrix, actions, permissions, and maintainer path filters are retained.
Contributor guidance and changelog record this gate. No Python package, tests,
dependencies, source adapters, or public CLI behavior changed.

**Local verification:** Native macOS ARM64 / Python 3.14.7. Ruff lint/format and
`git diff --check` passed. Parsed workflow YAML verifies the same command sequence
and unchanged non-step settings, with one command per run step. Read-only Git
checkout-filter simulation with `core.autocrlf=true` retains LF for all 18 affected
tracked paths under the new attributes. The CRLF/LF formatter reproduction passed.
These are local simulations, not native Windows or hosted correction results.
No dependency installation, application test rerun, or rebuild was needed for
this repository-text/CI/docs-only follow-up. Documentation links, fences,
consistency/privacy, and tracked/untracked diff checks are reviewed before handoff.

**Remaining gate:** Maintainer review/delivery of this follow-up, then inspect
the new exact-commit run. Require actual successful standalone formatting checks
on Windows 3.12–3.15 plus all other required matrix commands/tests/artifact checks;
do not rerun `785b45d` and claim it tests this correction. Only then close #2 and
allow a separately requested Thread 03/04. No real org/vault/Obsidian tests were
performed; no broader platform support claim follows.

**Tracking/Git/handoff:** Issue #2 records delivered core work, verified hosted
test/artifact success, actual Windows format failures, and pending correction;
Ready to merge/release remains unchecked. Native dependency edges and original
labels/assignment/milestone are preserved. Five local follow-up files remain
unstaged/uncommitted on `main` at `785b45d`: `.gitattributes`, workflow, contributor
guide, changelog, and this roadmap. No new issue, commit, push, PR, closure, rerun,
release, or publication. Thread 03's copy-ready prompt now includes the explicit
repair gate; Threads 03 and 04 remain **not started**.

**Issue evidence:** [Delivery/CI follow-up and remaining gates](https://github.com/jeffshurtliff/obforce/issues/2#issuecomment-6270681428).
Read back #2 as open, core implementation tasks checked, implementation-complete
reopened for the bounded follow-up, and Ready to merge/release unchecked. Labels,
assignment, milestone, and native prerequisite/dependent relationships remain
unchanged. No acceptance/closure or corrected Windows pass is claimed.

### Thread 02 acceptance and closure — 19 October 2026

**Status:** Accepted and complete. The maintainer reviewed/pushed the correction,
reported passing CI, and requested verification, issue/docs updates, and closure.
All Thread 02 implementation and follow-up gates are satisfied. Issue #2 is
closed as completed. Thread 03 is next eligible; Threads 03/04 remain **not
started**. This supersedes historical pending/open wording without rewriting
the earlier failures or local artifact evidence.

**Verified delivery:** Core implementation `3cb1bc4`, merged as `785b45d`, is
followed by correction
[`65305fb62d0c4f25c12e2c533834a13b506e6854`](https://github.com/jeffshurtliff/obforce/commit/65305fb62d0c4f25c12e2c533834a13b506e6854).
Actual code contains LF checkout attributes and individual single-command setup/
validation steps. Clean local `main`, `origin/main`, and live GitHub main matched
`b686fcb21e181edf9a200c00e92423a1a598f735` before this tracking update. That later
commit changes only README punctuation; application/tests/workflow match the
tested correction. It has no workflow run because README is path-filtered;
do not describe that unrun SHA as a passed CI run.

**Hosted acceptance evidence:** Inspected push run
[`39278236478`, attempt 1](https://github.com/jeffshurtliff/obforce/actions/runs/39278236478)
at exact correction SHA `65305fb`, every required step in all 12 jobs, and full
logs. Ubuntu/macOS/Windows on Python 3.12–3.15 all passed:

- Standalone environment selection, locked install, metadata/lock, Ruff lint,
  **Ruff formatting**, and Bandit checks. All 12 formatter logs confirm
  **38 files already formatted**, including all four Windows jobs.
- **117 tests per cell, no skips**, with 96% combined coverage.
- Fresh wheel/sdist builds, strict Twine, and **24 independent artifact installs**
  across the matrix, including import/model/resource checks, dependency
  consistency, console/module smoke checks, future-command refusal, runtime
  socket prohibition, absent external tools, and unchanged working directory.
- Whitespace checks; no required step skipped. No masked formatter failures
  remain. The old `39275023920` run still contains real Windows format failures
  despite its green summary; it is retained as historical evidence, not relabeled.

**Acceptance/limits:** The original four implementation tasks, local normalized
contract tests/docs, reviewed core delivery, and corrected Windows CI gates are
satisfied. These are hosted contract/foundation results, not full lifecycle,
native filesystem/recovery, live Salesforce/vault/Obsidian, renderer, graph,
template, or scale qualification. No release publication is implied.

**Docs/prompt/handoff:** Updated current roadmap status/index, Thread 02 evidence,
Thread 03 eligibility, contributor guidance, and the changelog to remove current
pending-fix claims. Historical handoffs remain intact. The previously supplied
Thread 03 prompt can be used unchanged: it requires verifying the correction,
which is now delivered and verified. Its scope remains offline Apex acquisition
and safe XML only; it does not start Thread 04 or later work.

**Checks/Git/tracking:** This is a prose-only acceptance update; local link,
fence, privacy/consistency, preserved maintainer-content, tracked/untracked diff,
and whitespace checks are performed before handoff. No application rerun,
dependency install, or rebuild is warranted for these documentation edits.
Updated #2's verified completion/CI checklist, posted exact delivery/run evidence,
and closed it under the maintainer's explicit authorization. Existing labels,
assignment, milestone, and native prerequisite/dependent edges are preserved.
Only three docs (`CONTRIBUTING.md`, `docs/CHANGELOG.md`, and this roadmap) remain
unstaged/uncommitted on `main` at `b686fcb`; no new commit, push, PR, rerun,
release, Salesforce/vault access, or later-thread implementation. The remote
roadmap retains its prior wording until this tracking update is delivered.

**Next eligible thread:** Thread 03 / #3, explicitly **not started**. Thread 04
also has its direct prerequisite satisfied but requires its own new request.

**Closure evidence:** [Final verified acceptance/closure comment](https://github.com/jeffshurtliff/obforce/issues/2#issuecomment-6271939652).
Read back issue #2 as `closed` with reason `completed`, completion and follow-up
gates checked, original labels/assignment/milestone preserved, and #3's native
prerequisite pointing to closed #2. No issue #3/#4 implementation or closure.

### Thread 03 handoff — 19 October 2026

**Status:** Locally implemented and verified; **not accepted or delivered**.
Issue #3 remains open. Only Thread 03 was implemented. Threads 04–17 remain
**not started**; no live access or public mutation command was introduced.

**Prerequisites re-verified before coding:** Read #3, #2, transitive prerequisite
#1, agent/contributor guidance, roadmap, and all three Thread 02 contract docs.
Verified delivered LF/single-command correction `65305fb` after merge `785b45d`
and all 12 required jobs/steps/full logs in exact-commit
[run 39278236478, attempt 1](https://github.com/jeffshurtliff/obforce/actions/runs/39278236478).
Every formatter reported 38 files already formatted; each job passed 117 tests,
fresh build/Twine and both independent artifact installs. Original run
`39275023920` still contains four real Windows formatter failures. Baseline local
HEAD/live main `5e86e03` differs from tested `65305fb` only in docs; no hosted pass
is claimed for that later path-filtered documentation SHA or this new local work.

**Implemented checklist:**

- [x] Explicit bounded DX manifest subset, existing/disjoint/contained declared
  packages, project namespace/Selection, safe paths and supported Apex pairs.
- [x] `defusedxml` through Poetry (`0.7.1` locked; no manual lock edits), explicit
  DTD/entity/external refusal, independent XML/scan limits, typed safe failures.
- [x] Existing immutable normalized records, canonical hashes and logical source
  binding; no source body reads, timestamps as audit facts, or dependency guesses.
- [x] Complete/partial **local** inventory; independent unavailable audit and
  uncollected relationships by design. Missing pairs omit candidates and yield
  partial outcome 4, even before selection filtering. Unsafe inputs refuse results.
- [x] Fictional two-package project, attack fixture, focused tests, acquisition
  documentation, existing docs/changelog updates and exact artifact allowlists.
- [ ] Maintainer acceptance, authorized delivery, and hosted Thread 03 evidence.

**Local evidence:** Native macOS 27.0.1 ARM64, Poetry 2.4.2. Reused existing
temporary Python 3.12.7/3.13.15 environments, adding only the cached XML wheel
after verifying its SHA-256 against the Poetry lock. Repository `.venv` uses
Python 3.14.7. Runtime source tests prohibit sockets/process creation and remove
external tools from PATH. No `sf`, authentication, real metadata/vault, or
Obsidian access occurred.

| Check | Actual result |
| --- | --- |
| `poetry check --lock --strict` | Passed |
| Ruff lint / format | Passed; 45 files already formatted; no new suppressions |
| Offline pytest 3.12.7 / 3.13.15 / 3.14.7 | **199 passed each, no skips** |
| Subprocess-aware 3.14.7 coverage | **95% combined statement/branch**; 710 statements, 280 branches; parser 100%, source 93%; gaps visible |
| Bandit over source | Passed, no findings/suppressions |
| Fresh final r4 wheel/sdist / strict Twine | Passed both |
| Independent final artifact installations | Two clean Python 3.14.7 environments outside checkout passed |
| Artifact content | Exact 16-member wheel / 15-member sdist; source, packaged README/pyproject and root license bytes match current checkout |
| Installed checks | Imports/resources, model hashes, dependency consistency, source/parser acquisition, both CLI entry points, future-command refusal, blocked sockets/absent tools, input preservation and no discovery writes |
| Docs/review | Local links/fences, scope/limits/privacy/consistency, full changed/untracked review and whitespace passed |
| Preservation | Apache LICENSE, AGENTS.md, existing CLI/config/models/errors, LF policy and maintainer workflow unchanged |

**Final artifacts:** `<temporary>/obforce-thread03-candidate-20261019-r4/`.
Exact allowlists add only `parsers/{__init__,apex}.py` and
`sources/{__init__,local}.py`. No samples/tests/dev/private local/org/vault/state/
recovery data enter the archives. Wheel and sdist independently retain Apache-2.0
metadata and unchanged license bytes.

| Artifact | SHA-256 |
| --- | --- |
| `obforce-0.1.0.dev0-py3-none-any.whl` | `380edf12ce439645b7bb02ad55f95558a61c0c15dff37bb8e7534baabed58e86` |
| `obforce-0.1.0.dev0.tar.gz` | `658e405fa772801698f5dadc7db68dfb552d7374f0d919234b2aa03cb30e6a02` |

**Decisions/review:** Decisions were recorded above and in the issue start
comment before coding. Unrelated project settings are inert; this is not full DX
schema validation or deploy/retrieve selection (`.forceignore` is not applied).
Unknown bounded XML fields warn and remain unmodeled. Apex bodies are stat-checked
only; source hashes cover normalized facts, not source-code changes. The existing
scope hash excludes package manifests/paths and cannot prove comparable local
scope. No local result establishes org absence. Stable-source preconditions are
checked, without claiming isolation from hostile filesystem races. Review fixed
unknown XML encoding escaping as a raw `LookupError`, portable root overlap, and
stale README capability wording. Initial sandbox dependency/build acquisition
could not reach PyPI; authorized isolated setup/build succeeded. Earlier r2/r3
builds remain superseded; r3 passed independent checks before the final packaged
README correction. Final r4 matches the final source/docs. Setup/build/install
uses network; runtime probes and tests remain offline.

**Gaps:** No hosted Thread 03 run, native Linux/Windows run, local Python 3.15,
native Windows junction/reparse qualification, or live/org/vault/lifecycle tests.
Symlink/hardlink/FIFO refusal ran locally without skips. Read-permission and
intervening-edit failures are controlled synthetic injections. Full lifecycle,
renderer, graph, templates, state/publication and recovery remain later work.
No new platform-support or stable public Python API promise is made.

**Git/tracking/handoff:** All changes remain unstaged/uncommitted on existing
`main` at `5e86e03`. No new issue, branch, stage, commit, push, PR, closure, CI
rerun, release, publication, or automation. Existing issue #3 retains its labels,
assignment, milestone and native prerequisite/dependent graph. Its start,
progress, verified checklist and handoff are synchronized with this roadmap;
remote code/roadmap delivery remains for the maintainer. Acceptance and Ready to
merge/release remain unchecked. Next eligible requested work is Thread 04 / #4,
explicitly **not started**; all later threads are also **not started**.

**Issue evidence:** [Start and prerequisite/decision record](https://github.com/jeffshurtliff/obforce/issues/3#issuecomment-6272708445),
[implementation progress](https://github.com/jeffshurtliff/obforce/issues/3#issuecomment-6272832645),
and [verified checklist/handoff](https://github.com/jeffshurtliff/obforce/issues/3#issuecomment-6272921606).
Read back #3 as open with all four implementation tasks and verified local
implementation/tests/docs/compatibility checks marked; Ready to merge/release
unchecked. Original labels/assignment/milestone and native dependency edges are
preserved. No maintainer acceptance or closure is claimed.

### Thread 03 Windows CI follow-up — 19 October 2026

**Status:** Core reviewed and delivered by the maintainer; bounded Windows
correction prepared and locally verified. **Corrected delivery/hosted CI and
final acceptance remain pending; #3 stays open.** This supersedes current-state
wording in the historical Thread 03 handoff without changing its results/hashes.

**Delivered baseline:** Clean local `main`, `origin/main`, and live GitHub main
match merge [`1f86032bb08248e825417614f6aef0243e9d8fb0`](https://github.com/jeffshurtliff/obforce/commit/1f86032bb08248e825417614f6aef0243e9d8fb0),
containing `d2a8a50`. Maintainer added postponed annotations and adjusted existing
headers/code; all those changes are retained. Changed Python headers use the
explicitly requested `GPT-6.1 Sol` identifier and 19 Oct 2026 date.

**Actual hosted evidence:** Inspected every job/required step and full log in
[run 39298411328, attempt 1](https://github.com/jeffshurtliff/obforce/actions/runs/39298411328)
at exact merge SHA `1f86032`:

| Cells | Verified outcome |
| --- | --- |
| Ubuntu/macOS, Python 3.12–3.15 (8) | 199 tests each, no skips; metadata/lock, Ruff lint/format, Bandit, fresh build, strict Twine, 16 independent artifact installs, whitespace passed |
| Windows 3.12 | 12 failed, 186 passed, 1 skipped |
| Windows 3.13 | 21 failed, 177 passed, 1 skipped |
| Windows 3.14 | 12 failed, 186 passed, 1 skipped |
| Windows 3.15 | 19 failed, 179 passed, 1 skipped |

Every formatter passed (45 files already formatted), including Windows. All four
Windows jobs failed in offline tests; build/Twine/independent installs/whitespace
were skipped. The sole test skip is the existing unavailable native FIFO case.
Failures are the path/descriptor pre-read refusal or its downstream edit-test
assertion. No skipped artifact step is represented as a pass.

**Cause and correction:** Supported Windows CPython can expose creation time in
pathname `st_ctime_ns` and change time in descriptor `st_ctime_ns` for the same
file; see [CPython #157671](https://github.com/python/cpython/issues/157671).
Comparing them directly caused timing-dependent false refusals. The edit test
could stop before its intended edit injection and then fail its preservation
assertion. The narrow helper permits only a Windows descriptor birthtime that
exactly matches path ctime with device/inode/mode/size/mtime unchanged. No rounding,
skip, retry, or blanket ctime removal. Path snapshots remain exact; a separate
raw descriptor snapshot now preserves its change-time guard before/after reading.
The final descriptor is also matched against the path. Links/containment/limits,
normalized records/hashes and offline/no-body-read boundaries remain unchanged.

**Regression evidence:** A temporary isolated copy of delivered HEAD fails the
new stable Windows-semantics read test with the exact original error. Corrected
code passes it. Added 21 synthetic regression cases for Windows-only bridging,
missing/incorrect/noninteger birthtime, all other identity fields, raw descriptor
ctime/mtime/inode changes and birthtime changes, byte/mtime preservation and
closed descriptors. These are deterministic local simulations, not native
Windows execution. Existing source/XML safety tests remain enabled.

**Actual local verification:** macOS 27.0.1 ARM64; Poetry 2.4.2. Full suites on
Python 3.12.7 / 3.13.15 / 3.14.7 each report **220 passed, no skips**. Strict
Poetry lock, Ruff lint/format (46 files), Bandit and whitespace pass. Combined
3.14.7 statement/branch coverage is **96%** (766 statements, 282 branches;
remaining gaps visible). Fresh correction r1 build/strict Twine, exact 16-member
wheel/15-member sdist inspections, and two independent clean Python 3.14.7
installs outside checkout pass the existing import/resource/model/dependency,
offline source/parser, entry-point/refusal/no-write checks. Artifacts match
current source and packaged README/pyproject/LICENSE bytes. No dependency,
lockfile, workflow, license, other runtime module, or public command changed.

**Correction candidates:** `<temporary>/obforce-thread03-windows-candidate-20261019-r1/`.

| Artifact | SHA-256 |
| --- | --- |
| `obforce-0.1.0.dev0-py3-none-any.whl` | `91f12594bdbbe0ce3108038db9199a04e97ea99c5f4189b526af34701a9e4c5e` |
| `obforce-0.1.0.dev0.tar.gz` | `9125a427fc4175b1161c34e5ce69c1ded0c02099049c081bc21566bdfbe7ebbe` |

**Remaining gate:** Maintainer reviews/delivers this correction; inspect a new
exact-commit run proving all four Windows Python 3.12–3.15 suites and their
previously skipped build/Twine/independent-install checks, plus the other eight
cells, pass. Rerunning old `1f86032` would not test this patch. No corrected
hosted/native Windows result or local Python 3.15 result is claimed; native
junction/reparse and full lifecycle gaps remain. No real org/vault/`sf` access.

**Tracking/Git/handoff:** Six changed/new files remain unstaged/uncommitted on
existing `main` at `1f86032`: source, integration/unit regressions, offline docs,
changelog and this roadmap. #3 records the delivered core, actual failures/skips,
local correction, and pending gate; implementation-complete is reopened for this
follow-up and Ready to merge/release stays unchecked. Existing metadata and
native dependencies are preserved. No issue creation, stage/commit/push, PR,
closure, rerun, publication or later implementation. Thread 04 is next eligible
under a separate request; **Threads 04–17 remain not started**.

**Issue evidence:** [Investigation/start and correction decision](https://github.com/jeffshurtliff/obforce/issues/3#issuecomment-6273969222).
The [verified correction handoff](https://github.com/jeffshurtliff/obforce/issues/3#issuecomment-6274046673)
records the same local evidence, original failures/skips, and remaining gates.
Read back #3 as open with implementation-complete/Ready to merge/release
unchecked, verified local follow-up gates checked, and original issue metadata
and native dependency links preserved.

**IDE inspection follow-up — 19 October 2026:** Confirmed `local.os` is the
imported standard-library module; PyCharm's unresolved-reference warning on
the test's dynamic patch is not a missing import. Changed only the integration
and unit namespace patches to `monkeypatch.setitem(vars(local), 'os', ...)`,
which retains pytest restoration and module-local Windows emulation without
changing shared `os.name` or runtime code. Focused source/identity tests and
Ruff/whitespace checks pass locally. Python headers retain `GPT-6.1 Sol`.
Existing artifact candidates are unaffected; corrected hosted Windows CI remains
pending. All changes remain unstaged/uncommitted; Threads 04–17 not started.

## 12. Reference notes for implementers

Official documentation was reviewed on 18 October 2026 where readable. Follow the
links at the relevant contract above, and refresh version-sensitive details in
the thread that uses them. Do not copy dependency versions, API limits, or
supported-interpreter claims from this plan without implementation-time checks.

- [Poetry project configuration](https://python-poetry.org/docs/pyproject/): package
  metadata and resource inclusion in wheels/sdists.
- [Python package resources](https://docs.python.org/3.12/library/importlib.resources.html):
  installed asset loading independent of checkout paths.
- [Salesforce data query](https://developer.salesforce.com/docs/platform/salesforce-cli-reference/guide/cli_reference_data_query.html):
  explicit target, Tooling API selection, and JSON command output.
- [Salesforce ApexClass fields](https://developer.salesforce.com/docs/platform/field-reference/references/field-reference/salesforce-field-reference-apexclass.html):
  source field availability; validate actual access separately.
- [Salesforce dependency object](https://developer.salesforce.com/docs/atlas.en-us.api_tooling.meta/api_tooling/tooling_api_objects_metadatacomponentdependency.htm):
  reference target for Thread 06; page body was inaccessible at planning review.
- [Obsidian properties](https://obsidian.md/help/properties) and
  [internal links](https://obsidian.md/help/links): property types and link syntax.
- [Obsidian Bases syntax](https://obsidian.md/help/bases/syntax): native dashboard
  asset format; validate actual app behavior separately.
- [Jinja sandbox](https://jinja.palletsprojects.com/en/stable/sandbox/): restricted
  rendering and its resource/trust limitations.
- [ruamel.yaml round-trip details](https://yaml.dev/doc/ruamel.yaml/detail/): comment
  preservation capabilities and formatting limitations.
