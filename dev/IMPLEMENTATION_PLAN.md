# Obforce v0.1.0 implementation roadmap

**Planning baseline:** 18 October 2026

**Target release:** `0.1.0`; initial development version: `0.1.0.dev0`

**Status:** Thread 01 is **accepted and complete**, including the delivered
Windows test correction and all 12 passing hosted CI cells. Issue #1 is closed
as completed. Thread 02 is **accepted and complete**, including delivered
correction `65305fb` and all 12 passing hosted cells with standalone Windows
formatting checks. Issue #2 is closed as completed. Thread 03 is **accepted and
complete**, including delivered correction merge `6154b74` and all 12 passing
hosted cells. Issue #3 is closed as completed. Thread 04 is **accepted and complete**, delivered at merge `6980b26` with all
12 hosted cells passing their applicable checks. Issue #4 is closed as completed.
Thread 05 is **accepted and complete**, delivered at merge `85ba7cd` with all
12 hosted cells passing their applicable checks. Issue #5 is closed as completed.
Thread 06 is **accepted and complete**, delivered at merge `2aa8d2b` with all
12 hosted cells passing their applicable checks. Issue #6 is closed as completed.
Thread 07 is **accepted and complete**, delivered at merge `eedeff4` with all
12 exact-merge hosted cells passing applicable checks. Issue #7 is closed as
completed. Thread 08 is **accepted and complete**, delivered at merge `dba53ab`
with all 12 exact-merge hosted cells passing applicable checks. Issue #8 is closed
as completed. Thread 09 is **accepted and complete**, including Windows correction
`890ced2` / merge `dff34a7` and all 12 exact-merge hosted cells. Issue #9 is closed
as completed. Thread 10 implementation is **delivered; CI correction pending acceptance**; #10 remains open.
Threads 11–17 remain **not started**.
Windows sf execution remains refused; future support is tracked separately in #18.

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
| 03 | Offline Apex source | 02 | B: source data | [#3](https://github.com/jeffshurtliff/obforce/issues/3) | Accepted; closed; corrected 12/12 hosted cells passed |
| 04 | Salesforce CLI process boundary | 02 | B | [#4](https://github.com/jeffshurtliff/obforce/issues/4) | Accepted; closed; 12/12 hosted cells passed; Windows sf refused |
| 05 | Live Apex inventory and audit enrichment | 04 | B | [#5](https://github.com/jeffshurtliff/obforce/issues/5) | Accepted; closed; 12/12 hosted cells passed; Windows sf refused |
| 06 | Platform relationships and normalized graph | 03, 05 | B | [#6](https://github.com/jeffshurtliff/obforce/issues/6) | Accepted and complete; #6 closed |
| 07 | Packaged templates and note rendering | 03, 06 | C: safe proposals | [#7](https://github.com/jeffshurtliff/obforce/issues/7) | Accepted and complete; issue closed |
| 08 | Existing-note parsing and preservation | 07 | C | [#8](https://github.com/jeffshurtliff/obforce/issues/8) | Accepted and complete; issue closed |
| 09 | State validation and identity reconciliation | 08 | C | [#9](https://github.com/jeffshurtliff/obforce/issues/9) | Accepted and complete; corrected 12/12 hosted cells passed; issue closed |
| 10 | Read-only change planner and conflict reports | 06, 07, 08, 09 | C | [#10](https://github.com/jeffshurtliff/obforce/issues/10) | Delivered; macOS CI correction pending |
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
is accepted with delivered Windows correction and passing hosted CI; Thread 04
is next eligible and remains not started.

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

**Depends on:** 02. **Status:** Accepted and complete; issue #3 closed.
The [original handoff](#thread-03-handoff--19-october-2026) and Windows follow-up
are historical. Current evidence is in the
[acceptance record](#thread-03-acceptance-and-closure--19-october-2026): correction
`20bff7f`, merged at `6154b74`, passed all 12 exact-commit hosted cells, including
every Windows test/build/Twine/independent-install step. Thread 04 remains not started.

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

**Depends on:** 02. **Status:** Accepted and complete; #4 closed; all 12 hosted cells passed applicable checks.
Windows sf execution remains refused; future support is tracked in [#18](https://github.com/jeffshurtliff/obforce/issues/18).

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
> Read AGENTS.md, CONTRIBUTING.md, dev/IMPLEMENTATION_PLAN.md, and the configuration,
> coverage, and note contracts. Check relevant local/vendor_docs/ if present.
> Verify prerequisite code and exact-commit CI before implementation. Thread 04's
> direct prerequisite is Thread 02 / #2. Current baseline merge
> 6154b745ed56c819cad179daa61d0ba606bede3b includes the accepted Thread 03 Windows
> correction 20bff7f. Run 39302343644 passed all 12 Linux/macOS/Windows cells for
> Python 3.12–3.15: 220 tests per Linux/macOS cell; 219 passed and the existing
> FIFO test skipped per Windows cell; standalone formatting, build, strict Twine,
> and both independent artifact installs passed everywhere. Preserve historical
> failed runs and recheck current code/CI; report any new blocker before coding.
> Thread 03's closure does not add a new direct dependency to Thread 04.
>
> Implement only Thread 04: the internal, bounded, mockable, read-only Salesforce
> CLI process boundary in sources/sf_cli.py and focused tests/fixtures/docs.
> Verify current official CLI command/JSON contracts without invoking real sf.
> Record material executable/platform/envelope decisions before dependent code.
>
> Implement safe explicit executable resolution and a fixed allowlist of supported
> read-only query/version operations. Construct subprocess argument lists with
> explicit targets for org-sensitive operations, controlled working directories,
> timeouts, and bounded stdout/stderr enforced during collection, before decoding
> or JSON parsing. Refuse arbitrary command strings, shell input, and implicit
> machine-default org selection. Handle Windows command wrappers explicitly;
> refuse unsupported execution paths when safe invocation cannot be established.
> Do not enable shell=True or interpolate user input to make a wrapper work.
>
> Validate bounded JSON success/error envelopes and preserve pagination/completion
> signals without treating empty output or process success as complete inventory.
> Use the existing typed errors and exit-code contracts. Redact diagnostics so raw
> stdout/stderr, credentials, auth URLs, org details, and personal data cannot leak
> through errors or logging. Do not implement Thread 05's org identity verification,
> Apex inventory, or audit enrichment in this process-boundary thread.
>
> Use synthetic fixtures, mocked process interfaces, and small fictional child
> processes only where needed to verify bounds and cleanup. Test exact argv,
> spaces/metacharacters and option-like selectors, Windows wrappers, success and
> failure envelopes, missing executables, expired-auth responses, malformed or
> oversized JSON, excessive stdout/stderr, timeouts, process cleanup, and safe
> redaction. Do not invoke real sf, discover authentication, inspect credential
> stores/.env, install/update CLI or plugins, authenticate, query an org, execute
> Apex, deploy, or access real metadata/vaults. Keep runtime tests offline.
>
> For every new or changed Python header, preserve Created By and use exactly:
> :Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
> with the current local date in the existing date format.
> Do not update unrelated headers.
>
> Preserve maintainer changes, Apache licensing, normalized identity/hash/coverage
> contracts, and the existing offline source. Add no public lifecycle commands,
> live inventory adapter, graph collection, rendering, or state/vault publication.
> Justify dependency additions through Poetry; never hand-edit poetry.lock.
> Update applicable docs, docs/CHANGELOG.md, and the roadmap handoff. Run relevant
> checks and fresh build/Twine/archive-inspection/independent wheel and sdist
> installation checks for package/dependency changes, extending the explicit
> artifact allowlist deliberately. Separate local, mocked, hosted, skipped, and
> unavailable evidence; mocked Windows execution is not native qualification.
>
> Leave changes unstaged/uncommitted and #4 open for acceptance. Do not create
> issues, stage, commit, push, open a PR, close issues, rerun CI, or publish.
> Leave Thread 05 and all later threads explicitly not started.

### Thread 05 — Live Apex inventory and audit enrichment

**Goal:** Normalized live Apex records using existing CLI authorization.

**Depends on:** 04. **Status:** Accepted and complete; #5 closed as completed.
Delivered implementation `a5b7269` / merge `85ba7cd` passed all 12 exact-commit
hosted cells in run `39325616681`, attempt 1. See the
[acceptance record](#thread-05-acceptance-and-closure--19-october-2026); earlier
[local handoff](#thread-05-handoff--19-october-2026) remains historical.
Future Windows support in #18 is not an additional prerequisite.

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
> Read AGENTS.md, CONTRIBUTING.md, dev/IMPLEMENTATION_PLAN.md, docs/CONFIGURATION.md,
> docs/COVERAGE.md, docs/NOTE_FORMAT.md, and docs/SF_CLI.md. Check relevant
> local/vendor_docs/ if present. Verify prerequisite code and exact-commit CI
> before implementation; report any new blocker before coding. Thread 05's direct
> prerequisite is Thread 04 / #4, now accepted and closed. Reviewed implementation
> 09a701169f80f875052359ff0b84476da3c36942 was merged at
> 6980b26bc539779fb9be2b7fb1cc6ae7f655f418. Run 39314787749, attempt 1, passed all
> 12 Linux/macOS/Windows Python 3.12–3.15 cells: 340 tests per Linux/macOS cell;
> 329 passed and 11 expected skips per Windows cell. Standalone formatting,
> fresh builds, strict Twine, and both independent artifact installs passed in
> every cell. Recheck current code/CI and preserve historical failed runs.
>
> Implement only Thread 05: an internal live Apex inventory/audit adapter using
> the accepted sources/sf_cli.py process boundary and synthetic, mocked responses.
> Add no public lifecycle command. Verify current official Salesforce API/CLI
> field, query, permission, pagination and JSON contracts through documentation
> and source reads without invoking real sf. Record material query, enumeration,
> identity, audit-privacy and coverage decisions before dependent implementation.
>
> Require an explicit target. Verify the actual org identity with a minimal
> non-secret read query, construct the established live SourceBinding, and refuse
> configured/state identity mismatches before accepting inventory. An alias is
> not stable identity. Do not add credential-bearing org-display operations,
> custom OAuth, auth discovery, or automatic rebinding/state adoption.
>
> Query only allowlisted ApexClass identity, namespace, API version, status and
> creation/modification audit fields. Never request Body, tokens, auth URLs,
> usernames, emails, customer records or unrelated User data. Support optional,
> scoped audit display-name enrichment and explicit name omission; preserve
> unavailable/null/absent distinctions without inventing audit values or technical
> debt assessments. Normalize into the existing component/selection/coverage
> contracts, with accurate provenance and deterministic hashes.
>
> Handle complete enumeration, pagination, namespace selection, empty results,
> truncation, missing permissions, unavailable fields and required-versus-optional
> failures. Establish a bounded enumeration strategy compatible with the fixed
> read-only operation allowlist; do not add arbitrary endpoint/continuation-URL
> execution. Retain contradictory completion/count/continuation/warning signals;
> a successful process, empty result or done flag alone never proves completeness.
> If exhaustion cannot be established, report precise incomplete coverage under
> the existing typed-error and exit-precedence contracts. Track inventory, audit
> and relationship coverage independently; relationship collection remains Thread
> 06. Do not infer deletion or change the frozen scope/hash/ownership contracts.
>
> Preserve explicit executable/target/working-directory controls, byte/time limits,
> cleanup and diagnostic redaction. Windows sf execution remains refused. Issue
> #18 tracks future Windows support outside v0.1.0; it is not a new prerequisite
> or authorization to implement Windows transport in this thread. Do not enable
> shell=True, wrapper workarounds, default-org selection or unbounded collection.
>
> Use realistic synthetic fixtures and mocked process interfaces. Test verified
> identity/target mismatch, multi-page enumeration, empty success, contradictory
> or truncated pages, namespace inclusion/exclusion, permission loss, unavailable
> audit fields, audit-name omission, invalid IDs/dates/versions, duplicate records,
> privacy/redaction, deterministic hashes and unchanged offline behavior. Keep
> runtime tests offline. Do not invoke real sf, inspect credential stores/.env,
> install/update CLI or plugins, authenticate, query an org, execute Apex, deploy,
> or access real metadata/vaults. Any future live validation requires separate
> explicit authorization for its target and operations.
>
> For every new or changed Python header, preserve Created By and use exactly:
> :Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
> with the current local date in the existing date format. Do not update unrelated
> headers. Preserve maintainer changes and Apache licensing. Justify dependency
> additions through Poetry; never hand-edit poetry.lock.
>
> Update applicable docs, docs/CHANGELOG.md and the roadmap handoff. Run relevant
> checks and fresh build/Twine/archive-inspection/independent wheel and sdist
> installation checks for package/dependency changes, extending the explicit
> artifact allowlist deliberately. Separate local, mocked, hosted, skipped and
> unavailable evidence; Windows CI/refusal tests are not Windows sf execution
> qualification. Leave changes unstaged/uncommitted and #5 open for acceptance.
> Do not create issues, stage, commit, push, open a PR, close issues, rerun CI or
> publish. Leave Thread 06 and all later threads, and enhancement #18, explicitly
> not started.

### Thread 06 — Platform relationships and normalized graph

**Goal:** Useful references with explicit evidence and incomplete-coverage handling.

**Depends on:** 03, 05. **Status:** Accepted and complete; #6 closed as completed.
Implementation `d1134fa` / merge `2aa8d2b` passed all 12 exact-merge hosted cells
in run `39431345348`, attempt 1. See the
[acceptance record](#thread-06-acceptance-and-closure--20-october-2026); the
[local handoff](#thread-06-handoff--19-october-2026) remains historical.
The recorded MCD exhaustion limitation and Windows sf refusal remain in force.

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

> Read GitHub issue https://github.com/jeffshurtliff/obforce/issues/6 and its linked prerequisite issues. Keep this existing issue updated with start/progress, verified checklist, and handoff evidence, synchronized with the roadmap. Leave it open pending maintainer acceptance; do not create duplicate tracking issues.
>
> Read AGENTS.md, CONTRIBUTING.md, dev/IMPLEMENTATION_PLAN.md, docs/CONFIGURATION.md, docs/COVERAGE.md, docs/NOTE_FORMAT.md, docs/OFFLINE_SOURCE.md, docs/SF_CLI.md, and docs/LIVE_SOURCE.md. Check relevant local/vendor_docs/ if present. Verify prerequisite code and exact-commit CI before implementation; report any new blocker before coding.
>
> Thread 06 directly depends on Threads 03 / #3 and 05 / #5, both accepted and closed. Thread 03 correction 20bff7fb0dd3bcace76ceec05c2564725d3bde00 was merged at 6154b745ed56c819cad179daa61d0ba606bede3b; run 39302343644, attempt 1, passed all 12 cells. Thread 05 implementation a5b7269cb4f50594489fe3b77f5350d21a523573 was merged at 85ba7cd725e2f246f39d6b11d18d431f4cc73d38; run 39325616681, attempt 1, passed all 12 Linux/macOS/Windows Python 3.12–3.15 cells: 441 tests per Linux/macOS cell; 430 passed and 11 expected skips per Windows cell. Standalone formatting, fresh builds, strict Twine, and both independent artifact installs passed in every cell. Recheck current code/CI and preserve historical failed runs. Windows skips/refusal tests do not qualify Windows sf execution.
>
> Implement only Thread 06: an internal provenance-aware directed graph and best-effort platform relationship adapter using the accepted sf_cli.py boundary and verified live source identity, with synthetic fixtures and mocked responses. Add no public lifecycle command. Verify current official MetadataComponentDependency/API/CLI field, permission, supported-type/endpoint, filtering, pagination and JSON contracts through documentation and source reads without invoking real sf. Do not inherit historical beta/limit claims. Record material direction, query, enumeration, endpoint resolution, prior-edge reuse and coverage decisions before dependent implementation. If capability/exhaustion cannot be established within the fixed read-only allowlist, report precise unavailable/partial coverage and a release limitation rather than inventing support or broadening transport.
>
> Represent source as the referencing component and target as the referenced component. Normalize and deduplicate reported edges while preserving namespace, type, provenance, coverage and contradictory evidence. Derive outgoing References and incoming Referenced By views from the same graph. Resolve only matching supported managed Apex identities; keep unsupported, external or unresolved endpoints explicitly labeled without generating new component notes. Handle self-references and cycles deterministically. Platform-reported references are not proof of runtime behavior or comprehensive impact analysis. Add no static analyzer, regex/AI dependency guesses, Apex Body collection or new metadata note types.
>
> Keep inventory, audit and relationship coverage independent. Offline relationships remain explicitly not collected. Preserve prior matching-source/scope edges as stale on failed, unsupported or partial refreshes; never erase them by treating failure/truncation as authoritative emptiness. Refuse incompatible binding/scope reuse. A successful process, empty array or done flag alone never proves exhaustion. Retain count/continuation/warning contradictions, enforce finite query/page/record/byte/time bounds, and use existing typed errors/exit precedence. Do not execute arbitrary endpoints or continuation URLs, select a default org, rebind/adopt state, infer deletion or weaken frozen identity/hash/ownership contracts. Graph-only changes must invalidate both affected endpoints without changing component source hashes; moved target paths must change relevant graph fingerprints. State loading and publication remain later threads.
>
> Preserve explicit executable/target/working-directory controls, cleanup and diagnostic redaction. Windows sf execution remains refused; enhancement #18 is outside v0.1.0, not a prerequisite or authorization to implement Windows transport. Runtime tests must remain offline. Do not invoke real sf, inspect credential stores/.env, discover auth, install/update CLI/plugins, authenticate, query an org, execute Apex, deploy, access real metadata/vaults, or upload private data. Future live validation requires separate explicit authorization for its target and operations.
>
> Test synthetic A -> B outgoing/incoming changes, duplicate/reordered edges, self-edges/cycles, namespaces, unresolved/unsupported endpoints/types, source identity/scope mismatch, pagination/truncation/count contradictions, permission/capability failures, complete-empty versus incomplete results, stale-edge preservation, privacy/redaction, deterministic graph hashes, graph-only and moved-path invalidation, unchanged component hashes and unchanged offline behavior.
>
> For every new or changed Python header, preserve Created By and use exactly:
> :Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
> with the current local date in the existing date format. Preserve maintainer changes and Apache licensing. Justify dependency additions through Poetry; never hand-edit poetry.lock. Update applicable docs, docs/CHANGELOG.md and the roadmap handoff. Run relevant checks and, for package/dependency changes, fresh build/Twine/archive-inspection/independent wheel and sdist installation checks with a deliberately extended artifact allowlist. Separate local, mocked, hosted, skipped and unavailable evidence.
>
> Leave changes unstaged/uncommitted and #6 open for acceptance. Do not create issues, stage, commit, push, open a PR, close issues, rerun CI or publish. Leave Thread 07 and all later threads, and enhancement #18, explicitly not started. Do not create or message other chats or spawn subagents.

### Thread 07 — Packaged templates and note rendering

**Goal:** Deterministic candidate notes from normalized data without vault writes.

**Depends on:** 03, 06. **Status:** Accepted and complete; issue #7 closed.
See the [acceptance record](#thread-07-acceptance-and-closure--20-october-2026).
Both accepted/closed prerequisites, actual code and all exact-commit CI command
logs were reverified before implementation; see the Thread 07 start/handoff record.

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

> Read GitHub issue https://github.com/jeffshurtliff/obforce/issues/7 and its linked prerequisite issues. Keep this existing issue updated with start/progress, verified checklist, and handoff evidence, synchronized with the roadmap. Leave it open pending maintainer acceptance; do not create duplicate tracking issues.
>
> Read AGENTS.md, CONTRIBUTING.md, dev/IMPLEMENTATION_PLAN.md, docs/CONFIGURATION.md, docs/COVERAGE.md, docs/NOTE_FORMAT.md, docs/OFFLINE_SOURCE.md, docs/LIVE_SOURCE.md, and docs/RELATIONSHIPS.md. Check relevant local/vendor_docs/ if present. Verify prerequisite code and exact-commit CI before implementation; report any new blocker before coding.
>
> Thread 07 directly depends on Threads 03 / #3 and 06 / #6, both accepted and closed. Thread 03 correction 20bff7fb0dd3bcace76ceec05c2564725d3bde00 was merged at 6154b745ed56c819cad179daa61d0ba606bede3b; run 39302343644, attempt 1, passed all 12 cells. Thread 06 implementation d1134fad0c9dfe2b83a28d411f403f04c9582333 was merged at 2aa8d2be362c86c3d8288f757b852bc98a867b2e; run 39431345348, attempt 1, passed all 12 Linux/macOS/Windows Python 3.12–3.15 cells: 517 tests per Linux/macOS cell; 506 passed and 11 expected skips per Windows cell. Standalone formatting, fresh builds, strict Twine, and both independent artifact installs passed in every cell. Recheck current code/CI and preserve historical failed runs. Windows skips/refusal tests do not qualify Windows sf execution.
>
> Implement only Thread 07: internal packaged creation and generated-section Jinja templates and deterministic candidate rendering for supported ApexClass notes. Use the accepted normalized source, coverage, graph, identity/ownership/marker and hash contracts. Add no public lifecycle command, existing-note parser/patcher, state loading, note discovery/adoption, change planner, publication or recovery. Record material template/context/loading/serialization/path/bounds decisions before dependent implementation.
>
> Load installed default assets through importlib.resources, independent of the checkout and working directory. Resolve each known template from an explicitly configured local override first; absent override files may fall back to packaged defaults, but existing invalid overrides must fail. Restrict template names, loaders, roots and contexts; refuse traversal, unsafe links/escapes and untrusted discovery. Use strict undefined handling, a restricted Jinja sandbox and explicit filters with primitive normalized data only. No arbitrary imports, side-effecting Python objects, filesystem/process/network helpers or templates discovered from metadata. Treat explicit templates as user-selected local code-like input; document that sandboxing alone does not prevent resource exhaustion. Enforce finite input/template/render/output bounds and safe typed failures before any candidate is accepted.
>
> Keep creation and generated rendering separate. The engine controls caller-supplied persistent note identity, reserved properties and exactly one valid generated marker pair; templates cannot redefine ownership, duplicate reserved keys, invent identities or remove required structure. Creation initializes Business Context, Known Issues / Technical Debt, and Additional Information. Existing-note preservation remains Thread 08: never rerender or overwrite an existing whole note through the creation template. Keep all user properties, tags, aliases and technical_debt* fields user-owned after creation; unassessed debt remains absent/null, never inferred or coerced to false.
>
> Serialize valid flat YAML and context-appropriate escaped Markdown/wikilinks. Validate complete new-note candidates and generated-region candidates against the frozen property/schema/marker contracts. Refuse duplicate keys, unsafe structures, marker injection, invalid identities/paths and ambiguous namespace/case/Unicode/reserved-name collisions. Omit unavailable audit values and explain availability; preserve absent/null/false distinctions and audit-name omission. Do not include Apex bodies, org/record IDs, internal URLs, raw responses or unnecessary personal data in note output.
>
> Derive References and Referenced By from the same accepted directed graph, preserving provenance, staleness and independent coverage. Only matching supported endpoints with explicit validated managed-note paths may become internal links; unsupported, unresolved, external or unmapped endpoints remain clearly labeled text without new component notes. Platform-reported references are not runtime proof or comprehensive impact analysis. Preserve Thread 06's release limitation: requested platform relationships remain partial/unavailable because exhaustion cannot be established under the fixed allowlist, including clean empty results. Offline relationships remain explicitly not collected. Do not broaden collection or transport.
>
> Use the existing source/graph/render/creation fingerprints without changing their contracts. Generated-template content and relevant graph/path changes invalidate generated output; creation-template changes affect new-note candidates only. Keep output deterministic across response ordering, repeated renders, checkout location and installed artifacts; do not add incidental timestamps or regenerate identity during rendering. Hash equality never authorizes overwriting edited generated content.
>
> Test synthetic deterministic Apex candidates, namespaced/unresolved/stale/cyclic references, incoming-only and moved-target invalidation, unchanged component hashes, missing/null/omitted audits, null debt defaults, reserved-property and marker enforcement, YAML/link/Markdown injection, namespace/path collisions, override precedence/fallback/error behavior, strict undefined/context restrictions, traversal/unsafe links and bounded rendering failures. Verify installed templates and rendering from fresh independent wheel and sdist installs outside the checkout, with no network/process access during runtime tests and no unintended working-directory artifacts.
>
> Preserve maintainer changes, Apache licensing and unchanged offline/source/transport behavior. Add justified rendering dependencies through Poetry, using verified current official documentation/source contracts; never hand-edit poetry.lock or invent pins. Follow AGENTS.md Python headers, preserving Created By, using the actual generating model in Jeff Shurtliff (via <actual-model-identifier>) and the current local date. Update applicable docs, docs/CHANGELOG.md and the roadmap handoff. Run applicable metadata/lock, Ruff, pytest, Bandit, whitespace and fresh build/Twine/archive-inspection/independent installation checks, deliberately extending asset/package allowlists. Separate local, mocked, hosted, skipped and unavailable evidence.
>
> Keep runtime tests offline and synthetic. Do not invoke real sf or Obsidian, inspect credentials/.env, discover auth, install/update CLI/plugins, authenticate, query an org, execute Apex, deploy, access real metadata/vaults, alter .obsidian settings or upload private data. Windows sf execution remains refused; enhancement #18 is outside v0.1.0 and is not a prerequisite or authorization for Windows transport.
>
> Leave changes unstaged/uncommitted and #7 open for acceptance. Do not create issues, stage, commit, push, open a PR, close issues, rerun CI or publish. Leave Thread 08 and all later threads, and enhancement #18, explicitly not started. Do not create or message other chats or spawn subagents.

### Thread 08 — Existing-note parsing and preservation

**Goal:** Safe reading/patching of managed notes while retaining human content.

**Depends on:** 07. **Status:** Accepted and complete; #8 closed as completed.
Implementation `d79f5e2` / merge `dba53ab` passed all 12 exact-merge hosted cells in
run `39453887153`, attempt 1. See the
[acceptance record](#thread-08-acceptance-and-closure--20-october-2026); the
[local handoff](#thread-08-handoff--20-october-2026) remains historical.
Thread 07 is accepted/closed at merge `eedeff4`; see its
[acceptance record](#thread-07-acceptance-and-closure--20-october-2026).
Actual source and exact-commit CI rechecked before code; see the
[Thread 08 start record](#thread-08-start-and-decisions--20-october-2026).

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

> Read GitHub issue https://github.com/jeffshurtliff/obforce/issues/8 and its linked prerequisite issues. Keep this existing issue updated with start/progress, verified checklist, and handoff evidence, synchronized with the roadmap. Leave it open pending maintainer acceptance; do not create duplicate tracking issues.
>
> Read AGENTS.md, CONTRIBUTING.md, dev/IMPLEMENTATION_PLAN.md, docs/NOTE_FORMAT.md, docs/RENDERING.md, docs/COVERAGE.md, and docs/CONFIGURATION.md. Check relevant local/vendor_docs/ if present. Verify prerequisite code and exact-commit CI before implementation; report any new blocker before coding.
>
> Thread 08 directly depends on Thread 07 / #7, accepted and closed. Implementation b4658eb0f878c71698e580801c118733a16b86df was merged at eedeff425bcd4921bef8756412826ce5a93b0165. Run 39440606470, attempt 1, passed all 12 Linux/macOS/Windows Python 3.12–3.15 cells: 618 passed per Linux/macOS cell; 606 passed and 12 expected skips per Windows cell. Every standalone metadata/lock, Ruff lint/format, Bandit, fresh build, strict Twine, both independent artifact installs and whitespace check passed. Recheck actual code and full command logs; preserve historical failed runs and earlier local probe failures. Windows skips/refusal and synthetic reparse tests do not qualify Windows sf execution.
>
> Implement only Thread 08: internal bounded parsing of caller-supplied managed-note bytes, generated-property/body baseline conflict detection, and in-memory preservation patches in sync/notes.py with synthetic fixtures. Add no public lifecycle command, vault/note discovery or adoption, state-file loading, identity/move reconciliation, batch change planner, filesystem publication, locking, journal or recovery. Caller-supplied validated NoteState/baselines are in-memory inputs only. Do not begin Threads 09 or 10.
>
> Before dependent implementation, record the supported YAML/frontmatter forms, parser/round-trip dependency and official contracts, byte/encoding/line-ending policies, marker rules, baseline comparisons and finite size/depth/node/output limits. Use a safe YAML round-trip approach justified for supported comments/order/quoting/scalar/list/multiline forms. Refuse unsupported forms explicitly; no arbitrary Python constructors, unsafe/custom tags, duplicate keys, complex keys, or unbounded alias/merge expansion. Do not silently normalize, repair, discard or stringify unsupported user information. Add justified dependencies through Poetry; never hand-edit poetry.lock or invent pins.
>
> Validate the existing persistent canonical obforce_id, supported integer schema, exact reserved property allowlist and exactly one ordered generated marker pair on separate lines. Refuse missing, inline, repeated, reversed, nested or malformed markers, ambiguous frontmatter, unsupported schemas, unknown sf_* keys, identity mismatches and unsafe structures. Do not invent identity, adopt notes or infer renames. Use existing typed failures and preserve error/exit precedence with concise redacted diagnostics, never raw note content or local/private data.
>
> Extract exact generated-region bytes and owned-property values, preserving absent/null/false/empty distinctions and strict value types. Compare BOTH current generated properties and current generated body with their saved baselines before patching. Edits to either are conflicts even when incoming metadata is unchanged or hashes match. Identity/schema edits are conflicts too. Hash equality never authorizes overwriting edited content. There is no force-overwrite or destructive fallback.
>
> Construct candidate patches using accepted Thread 07 generated candidates only. Never rerender an existing whole note through the creation template. Update only clean generator-owned properties and bytes strictly between validated marker lines. Preserve marker-line bytes and all body bytes outside the generated region, including human prose, whitespace and original line endings. Preserve supported user YAML values, comments, ordering, quoting and multiline styles; document precise round-trip limits rather than promising universal byte-identical frontmatter. A true no-op must return the original note bytes unchanged. Define/test LF, CRLF and mixed-ending behavior without silently rewriting the document.
>
> All nonreserved properties remain user-owned, including type, tags, aliases, business fields and every technical_debt* field. Preserve absent/null/false and human assessment/status/severity/review dates; never infer debt or turn an unset assessment into false. Preserve supported custom properties even when they differ from creation defaults. Omit unavailable incoming audits according to the accepted candidate contract without confusing omitted, unavailable and explicitly null values. Keep audit-name omission effective.
>
> Preserve Thread 07's source/graph/render/creation hash contracts and its renderer-local graph-plus-independent-Coverage composition. Generated-region baselines hash exact marker-interior bytes. Creation-template edits affect new notes only. Preserve accepted template/loading/bounds and explicit managed-path rules; do not broaden rendering, graph collection or transport. Requested platform relationships remain partial/unavailable because exhaustion cannot be established, including clean empty results; offline relationships remain not collected. Platform-reported references are not runtime proof or comprehensive impact analysis.
>
> Test synthetic hand-edited notes: generated audit updates with exact outside-body byte preservation; custom properties/tags/aliases/prose; technical-debt absence/null/false; comments/order/quotes/multiline/Unicode; LF/CRLF and declared mixed-ending policy; unchanged no-op bytes; edited generated fields/body/identity/schema; duplicate keys, malformed frontmatter/markers, unknown reserved properties, unsafe YAML/tags/aliases/merges and bounded parsing/output failures. Verify typed/redacted failures and input immutability. Deliberately extend package allowlists and verify the parser/patcher from fresh independent wheel and sdist installs outside the checkout with runtime network/process access blocked and no unintended cwd artifacts.
>
> Preserve maintainer changes, Apache licensing and source/transport behavior. Follow AGENTS.md Python headers: preserve Created By, use Jeff Shurtliff (via GPT-6.1 Sol) for changed/new Last Modified headers and the current local date. Update applicable docs, docs/CHANGELOG.md and the roadmap handoff. Run applicable Poetry metadata/lock, Ruff, pytest, Bandit, whitespace and fresh build/Twine/archive-inspection/independent installation checks. Separate local, synthetic/mocked, hosted, skipped and unavailable evidence.
>
> Keep runtime tests offline and synthetic. Do not invoke real sf or Obsidian, inspect credentials/.env, discover auth, install/update CLI/plugins, authenticate, query an org, execute Apex, deploy, access real metadata/vaults, alter .obsidian settings or upload private data. Windows sf execution remains refused; enhancement #18 is outside v0.1.0 and is not a prerequisite or authorization for transport work.
>
> Leave changes unstaged/uncommitted and #8 open for acceptance. Do not create issues, stage, commit, push, open a PR, close issues, rerun CI or publish. Leave Thread 09 and all later threads, and enhancement #18, explicitly NOT STARTED. Do not create or message other chats or spawn subagents.

### Thread 09 — State validation and identity reconciliation

**Goal:** Reliable ownership and note-move matching independent of filenames.

**Depends on:** 08. **Status:** Accepted and complete; #9 closed.
Windows correction 890ced2 / merge dff34a7 passed all 12 exact-merge hosted cells;
see the [acceptance record](#thread-09-acceptance-and-closure--20-october-2026).
Thread 08 is accepted/closed at merge `dba53ab`; see its
[acceptance record](#thread-08-acceptance-and-closure--20-october-2026).
Recheck actual source and exact-commit CI before implementing Thread 09.

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

> Read GitHub issue https://github.com/jeffshurtliff/obforce/issues/9 and its linked prerequisite issues. Keep this existing issue updated with start/progress, verified checklist, and handoff evidence, synchronized with the roadmap. Leave it open pending maintainer acceptance; do not create duplicate tracking issues.
>
> Read AGENTS.md, CONTRIBUTING.md, dev/IMPLEMENTATION_PLAN.md, docs/NOTE_FORMAT.md, docs/RENDERING.md, docs/COVERAGE.md, docs/CONFIGURATION.md and docs/RELATIONSHIPS.md. Check relevant local/vendor_docs/ if present. Verify prerequisite code and exact-commit CI before implementation; report any new blocker before coding.
>
> Thread 09 directly depends on Thread 08 / #8, accepted and closed. Implementation d79f5e2a1a8ddb7b5c00857c2cfe73556e96586e was merged at dba53abdeae578789739f19d1b0366ad72feda00. Run 39453887153, attempt 1, passed all 12 Linux/macOS/Windows Python 3.12–3.15 cells: 744 passed per Linux/macOS cell; 732 passed and 12 expected skips per Windows cell. Every standalone metadata/lock, Ruff lint/format, Bandit, fresh build, strict Twine, archive inspection, both independent artifact installs and whitespace check passed. Recheck actual code and full command logs; preserve historical failed runs and earlier local probe/setup failures. Windows skips/refusal and synthetic reparse tests do not qualify Windows sf execution.
>
> Implement only Thread 09: internal strict versioned state serialization/validation, bounded read-only state loading and managed-note discovery, identity-based reconciliation of uniquely moved notes, and in-memory candidate state/path updates using synthetic vaults. Use sync/state.py and focused supporting code/tests; add docs/SYNC_SAFETY.md. No public lifecycle command, batch change planner/reporting, filesystem publication, state-file writes, locking, journal, recovery, automatic adoption/migration, or new source/transport work. Do not begin Thread 10 or later threads.
>
> Before dependent implementation, record the state wire schema and minimum private fields, scope/binding representation, encoding and deterministic serialization rules, discovery root/exclusion/managed-indicator policy, missing/empty-state cases, move/conflict rules, read-side filesystem assumptions and finite byte/depth/node/entry/path/aggregate-read/output limits. Preserve the accepted immutable NoteState and hash contracts. Record how the wire envelope retains the exact saved generated-region bytes required by patch_note, alongside the strict property baseline and exact-byte SHA-256, without reconstructing baselines from current notes. Never persist human prose or user-owned properties as generated baselines. Refuse unknown schemas/keys/types, duplicate JSON keys/IDs/component mappings/portable paths, invalid hashes/UUIDs and contradictory baseline/identity/scope records; no coercion, repair, adoption or destructive fallback. Justify dependencies through Poetry if needed; never hand-edit poetry.lock or invent pins.
>
> Use explicit caller-supplied vault/state inputs, never cwd/home/auth discovery or a real vault. Loading/serialization/discovery/reconciliation must create no config, vault, state, lock, journal, log, cache or temporary publication artifacts. Missing, corrupt or unsupported state alongside managed notes is a conflict, never an invitation to reconstruct ownership. Define a genuinely empty initial scope explicitly without adopting unrelated files. Treat state and paths as untrusted. Bound traversal and reads; reject traversal/escape/overlap, unsafe symlinks/junctions/reparse points, special files, unsafe hard links, case/Unicode/reserved-name and file/parent collisions, unreadable/partial scans and unexpected parent/file changes. Exclude control directories from note discovery; handle only the explicit expected state document separately. Record native/read-race limitations honestly.
>
> Reuse Thread 08's bounded managed-note parser and supported YAML/marker/encoding/line-ending policies. Recognize managed indicators conservatively: malformed managed content or missing/edited identity must not silently become an ignored ordinary note. Leave unrelated notes untouched and unadopted. Match only a unique persistent canonical obforce_id with its validated state/source key. A unique in-vault move retains its UUID, key, content and baselines and changes only the candidate relative path. Refuse duplicate/copied IDs, multiple notes for one component, identity/key/schema mismatches, vanished tracked notes, ambiguous mappings, outside-vault moves and unowned collisions. Do not infer renames or moves from filenames, similar text or record IDs alone.
>
> Enforce exact workspace/source-mode/verified-org bindings; aliases are selectors, never stable org identity. No local/live or org/workspace rebinding. Retain comparable selection/scope evidence independently from collection outcomes. Changed scope, partial/unavailable input and offline local scope cannot establish component absence or deletion. Distinguish a vanished tracked note from a component not observed in source. Never delete notes, automatically mark components missing or replace stale relationships in this thread; lifecycle/change planning remains later work.
>
> Return deterministic in-memory reconciled mappings and candidate state/path changes for later consumers. Expose the path changes needed to invalidate neighboring incoming/outgoing links and graph/render fingerprints without implementing the batch planner or rewriting notes. Preserve accepted source/graph/render/creation hashes and renderer-local graph-plus-independent-Coverage composition. Compare both current generated-property values and exact generated bytes against saved baselines before accepting managed notes; hashes never authorize overwriting edited content or rebasing edits. Preserve absent/null/false/empty distinctions, audit-name omission and every user-owned property, including type/tags/aliases/business fields and all technical_debt* assessments/status/severity/review dates. Creation-template edits affect new notes only.
>
> Test synthetic state/vault fixtures for deterministic round trips and candidate mappings; unique moves and neighboring link invalidation inputs; duplicate JSON keys/IDs/mappings/paths; malicious or excessive state; missing/corrupt/unknown state; malformed managed notes and edited generated fields/body/identity/schema; vanished notes; source/org/workspace/scope mismatches; partial traversal, links/reparse/special files, portable collisions and outside-vault escapes; ordinary-note non-adoption; strict baseline distinctions and exact LF/CRLF saved bytes. Verify redacted typed failures and existing exit precedence, input immutability, and exact file bytes/mtimes/tree preservation during all reads and no-op/failure paths. Deliberately extend package allowlists and verify state/parser/reconciliation behavior from fresh independent wheel and sdist installs outside the checkout, with runtime network/process access blocked and no cwd artifacts.
>
> Preserve maintainer changes, Apache licensing and source/transport behavior. Follow AGENTS.md Python headers: preserve Created By, use Jeff Shurtliff (via GPT-6.1 Sol) for changed/new Last Modified headers and the current local date. Update applicable docs, docs/CHANGELOG.md and the roadmap handoff. Run applicable Poetry metadata/lock, Ruff, pytest, Bandit, whitespace and fresh build/Twine/archive-inspection/independent installation checks. Separate local, synthetic/mocked, hosted, skipped and unavailable evidence.
>
> Keep runtime tests offline and synthetic. Do not invoke real sf or Obsidian, inspect credentials/.env, discover auth, install/update CLI/plugins, authenticate, query an org, execute Apex, deploy, access real metadata/vaults, alter .obsidian settings or upload private data. Windows sf execution remains refused. Requested platform relationships remain partial/unavailable because exhaustion cannot be established, including clean empty results; offline relationships remain not collected. Enhancement #18 is outside v0.1.0 and is not a prerequisite or authorization for transport work.
>
> Leave changes unstaged/uncommitted and #9 open for acceptance. Do not create issues, stage, commit, push, open a PR, close issues, rerun CI or publish. Leave Thread 10 and all later threads, and enhancement #18, explicitly NOT STARTED. Do not create or message other chats or spawn subagents.

### Thread 10 — Read-only change planner and conflict reports

**Goal:** A complete deterministic preview of a build/refresh before any write.

**Depends on:** 06, 07, 08, 09. **Status:** DELIVERED; macOS CI correction pending; not accepted.
All four prerequisites are accepted/closed; recheck actual code and exact-commit
CI before implementation, including Thread 09 correction merge dff34a7 / run 39502679337.

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

> Read GitHub issue https://github.com/jeffshurtliff/obforce/issues/10 and its linked prerequisite issues #6, #7, #8 and #9. Keep this existing issue updated with start/progress, verified checklist and handoff evidence synchronized with the roadmap. Leave #10 open pending maintainer acceptance; do not create duplicate tracking issues.
>
> Read AGENTS.md, CONTRIBUTING.md, dev/IMPLEMENTATION_PLAN.md, docs/SYNC_SAFETY.md, docs/NOTE_FORMAT.md, docs/RENDERING.md, docs/COVERAGE.md, docs/CONFIGURATION.md and docs/RELATIONSHIPS.md. Check relevant local/vendor_docs/ if present. Verify actual prerequisite code, issue/dependency state and exact-commit CI command logs before implementation; report any new blocker before coding.
>
> Thread 09 / #9 is accepted and closed, including its Windows timestamp correction. Initial implementation 08e967a was merged at ff05ef6; failed run 39500770363 remains historical. Correction 890ced229722318764d87d8b525a932c72addfc7 was merged at dff34a7eb806622331e4770de38cbf0e470d322a. Run 39502679337, attempt 1, passed all 12 Linux/macOS/Windows Python 3.12–3.15 cells: Linux 935 passed each; macOS 933 passed/2 skipped each; Windows 920 passed/15 skipped each. Every standalone metadata/lock, Ruff lint/format, Bandit, fresh build, strict Twine, exact archive inspection, both independent artifact installs and whitespace check passed. Recheck this evidence; retain historical failed runs, skipped checks and local probe/setup failures. Native Windows read tests and synthetic reparse results do not qualify Windows sf execution.
>
> Implement only Thread 10: an internal complete deterministic read-only change planner and bounded conflict/action reporting. Use sync/planner.py and focused supporting code/tests. Combine explicit normalized source results, independent coverage, accepted graph/render candidates, current managed-note observations and validated prior state into typed create/update/no-op/move/missing/conflict actions, candidate state/content and publication preconditions. No public lifecycle command, filesystem publication, state writes, staging, locks, journal, recovery, adoption/migration, backup/Git integration or new source/transport work. Do not begin Thread 11 or later threads.
>
> Before dependent implementation, record the planner/action/result schemas, stable new-note UUID policy, caller inputs, action ordering/count rules, blocked-plan semantics, safe reporting fields, publication preconditions and finite component/edge/path/content/action/report/output limits. Preserve accepted NoteState/state-wire/hash contracts and renderer-local graph-plus-independent-Coverage composition. Reuse strict bounded state/discovery/reconciliation and note parsing/patching, including the Windows cross-API birthtime correction and same-API change guards. Do not weaken checks or reconstruct saved baselines from current notes. Justify any necessary dependencies through Poetry; never hand-edit poetry.lock or invent pins.
>
> Use explicit caller-supplied inputs and synthetic vaults only, with no cwd/home/config/auth discovery. Planning and reporting must create no config, vault, state, lock, journal, log, cache or temporary publication artifacts. Retain byte/mtime/tree and input immutability on success, no-op, blocked and failure paths. Preserve explicit initial-empty-managed-scope rules; never adopt ordinary files. Refuse missing/corrupt/unknown state alongside managed notes, edited identities/schemas/baselines, duplicate IDs/component mappings/portable paths, vanished tracked notes, unsafe links/junctions/reparse/special/hard-linked files, traversal/overlap/escape, unreadable/partial scans and observed file/parent changes. Validate existing and proposed paths together, including occupied unowned targets, case/Unicode/reserved-name and file/parent collisions.
>
> Compare both strict generated-property values and exact saved generated-region bytes, including LF/CRLF and SHA-256, even when hashes suggest a no-op. Preserve human prose, supported YAML/comments and every user-owned property, including type/tags/aliases/business fields and all technical_debt* assessments/status/severity/review dates. Keep absent/null/false/zero/empty/unavailable distinctions and audit-name omission. Patch only accepted clean owned fields/generated regions; creation templates initialize new notes only. Existing notes must never be replaced by whole-new-note candidates. Stable source/graph/render/creation fingerprints retain their existing meanings.
>
> Consume only unique UUID-based in-vault moves; do not infer renames from filenames, similar text or record IDs. A user-moved note needs candidate state/path reconciliation and affected incoming/outgoing link invalidation, not an automatic filesystem rename. Re-render affected neighbors for graph-only changes, moved targets, generated-template/options/coverage/renderer-contract changes even when their source facts are unchanged. Creation-template edits affect new-note candidates only. Ignore incidental collection timestamps and ordering; unchanged and user-only edits must not cause note/state churn.
>
> Enforce exact workspace/source-mode/verified-org bindings and comparable selection/scope evidence independently from collection outcomes. A vanished tracked note is a conflict, distinct from a component unobserved in source. Internal missing proposals require positively complete comparable supported live inventory; local/offline, changed-scope, partial or unavailable input cannot establish absence/deletion. Never delete notes. Preserve stale relationship evidence under incomplete refreshes using accepted graph semantics. Requested platform relationships remain partial/unavailable even after clean empty results; offline relationships stay not collected. Public lifecycle application remains later work.
>
> Preflight the complete bounded change set before returning a publishable candidate plan; any conflict blocks the whole plan and cannot authorize a partial apply. Define immutable preconditions for later writer revalidation, including note/state/parent observations, but do not implement a writer or claim an atomic filesystem snapshot. Provide deterministic action counts, bounded opt-in local details, independent coverage warnings and existing outcome precedence 3, 2, 1, 4, 0. Keep diagnostics redacted; do not expose raw note/source/state content, credentials or unnecessary audit identities. Return internal reporting results without adding public build/sync/init/recover commands.
>
> Test synthetic stable/repeated plans and an unchanged next-baseline no-op scenario using explicit synthetic fixture setup, never publication code. Cover generated-property/body conflicts blocking the batch, graph-only and both-direction neighboring move invalidation, generated versus creation-template changes, user-only edits, privacy/absence distinctions, valid initial creates, missing/duplicate/ambiguous notes/state/paths, scope/org/workspace switches, complete versus partial/offline absence decisions, stale-edge retention, collisions, read races, finite limits, redacted typed failures and deterministic counts/outcomes. Prove exact no-write bytes/mtimes/tree/input preservation, including failures and Windows timestamp semantics. Deliberately extend package allowlists and verify planner/report/parser/state behavior from fresh independent wheel and sdist installs outside the checkout, with runtime network/process access blocked and no cwd artifacts.
>
> Preserve maintainer changes, Apache licensing and source/transport behavior. Follow AGENTS.md Python headers: preserve Created By, use Jeff Shurtliff (via GPT-6.1 Sol) for changed/new Last Modified headers and the current local date. Update applicable docs, docs/CHANGELOG.md and roadmap handoff. Run applicable Poetry metadata/lock, Ruff, pytest, Bandit, whitespace and fresh build/Twine/archive/independent-install checks. Separate local, synthetic/mocked, hosted, skipped and unavailable evidence.
>
> Keep runtime tests offline and synthetic. Do not invoke real sf or Obsidian, inspect credentials/.env, discover auth, install/update CLI/plugins, authenticate, query an org, execute Apex, deploy, access real metadata/vaults, alter .obsidian settings or upload private data. Windows sf execution stays refused; enhancement #18 is outside v0.1.0 and is not a prerequisite or authorization for transport work.
>
> Leave changes unstaged/uncommitted and #10 open for acceptance. Do not create issues, stage, commit, push, open a PR, close issues, rerun CI or publish. Leave Thread 11 and all later threads, and enhancement #18, explicitly NOT STARTED. Do not create or message other chats or spawn subagents.

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

### Thread 03 acceptance and closure — 19 October 2026

**Status:** Accepted and complete. The maintainer reviewed/pushed the correction,
reported passing CI, and explicitly requested verification, docs/issue updates,
and closure when appropriate. Delivered code and all hosted follow-up gates
are verified; issue #3 is closed as completed. Thread 04 is next eligible;
**Threads 04–17 remain not started**. This supersedes pending/open/undelivered
wording in historical handoffs while preserving original failures and hashes.

**Exact delivery:** Core `d2a8a50` / merge `1f86032` is followed by correction
[`20bff7fb0dd3bcace76ceec05c2564725d3bde00`](https://github.com/jeffshurtliff/obforce/commit/20bff7fb0dd3bcace76ceec05c2564725d3bde00),
merged at [`6154b745ed56c819cad179daa61d0ba606bede3b`](https://github.com/jeffshurtliff/obforce/commit/6154b745ed56c819cad179daa61d0ba606bede3b).
Clean local `main`, `origin/main`, live GitHub main, and the tested run head all
matched that merge before this prose-only update. Actual code contains the
exact Windows birthtime bridge, independent raw descriptor change-time guard,
and namespace-dictionary test patches. Maintainer annotations/headers are retained.

**Verified hosted acceptance:** Inspected every job/required step and full log
in [run 39302343644, attempt 1](https://github.com/jeffshurtliff/obforce/actions/runs/39302343644)
at exact head `6154b74`. All 12 cells passed:

| Cells | Actual outcome |
| --- | --- |
| Ubuntu/macOS, Python 3.12–3.15 (8) | 220 tests per cell, no skips |
| Windows, Python 3.12–3.15 (4) | 219 passed, 1 skipped per cell; existing unavailable native FIFO case |
| Every cell | Standalone metadata/lock, Ruff lint/format (46 files already formatted), Bandit, fresh wheel/sdist, strict Twine, both independent installs, and whitespace passed |

All cells report 96% combined statement/branch coverage. All 24 independent
artifact installations passed exact allowlists/license/imports/resources/model
hashing/dependency consistency, installed offline acquisition, console/module
entry points, future-command refusal, blocked sockets/absent tools, source
preservation and no discovery writes. Every Windows build/Twine/install step
that was skipped in the failed run actually executed successfully this time.
No required workflow step was skipped, and no command-level formatter/test
failure appears behind a green summary.

**Acceptance checklist:**

- [x] All four original Thread 03 tasks and the synthetic multi-package demo.
- [x] Read-only/coverage/hash/source-binding/XML/path safety contracts preserved.
- [x] Reviewed core and Windows correction delivered at verified commits.
- [x] Corrected Windows 3.12–3.15 tests and previously skipped artifact gates pass.
- [x] Full 12-cell CI, docs/checklist/handoff, and final maintainer authorization.

**Retained limits:** FIFO refusal remains unexecuted on Windows because the
native facility is unavailable; no new skip was introduced. Symlink/hardlink
cases ran in the hosted suite, but this is not general junction/reparse,
filesystem/ACL, hostile-race, scale, full lifecycle, real-org/vault/Obsidian,
renderer/graph/template, state/publication or recovery qualification. Local
Python 3.15 remains unexecuted; hosted 3.15 passed separately. No release or
stable public Python API promise follows. Failed run `39298411328` stays failed,
and old `39275023920` retains its masked Windows formatter failures.

**Docs/Git/handoff:** Updated current roadmap status/index, Thread 03 evidence,
Thread 04 eligibility and exact copy-ready prompt (including the requested
`GPT-6.1 Sol` header identifier), contributor guidance and changelog. This is a
prose-only tracking update: local links/fences/consistency/privacy/whitespace and
tracked/untracked review are checked; no new test/build/dependency run is needed.
Only `CONTRIBUTING.md`, `docs/CHANGELOG.md` and this roadmap remain
unstaged/uncommitted on `main` at `6154b74`. No new source/test change, commit,
push, PR, rerun, release, publication, Salesforce/auth/vault access or later work.
Remote source/correction is already delivered; these final docs await separate
delivery. #3's original metadata and reciprocal native dependencies are retained.

**Next eligible thread:** Thread 04 / #4, explicitly **not started**. Its direct
prerequisite remains Thread 02 / #2; Thread 03 closure does not alter that graph.
The exact kickoff prompt above authorizes only Thread 04 when separately used;
no chat was created or messaged and Thread 05 or later work was not started.

**Closure evidence:** [Final verified acceptance/closure comment](https://github.com/jeffshurtliff/obforce/issues/3#issuecomment-6274600473).
Read back #3 as closed with reason completed, implementation/follow-up gates
checked, original labels/assignment/milestone and reciprocal dependencies
preserved. #4 remains open and not started with its existing prerequisite #2.

### Thread 04 start and process-boundary decisions — 19 October 2026

Thread 04 started — 19 October 2026. Clean HEAD `63a78dc214647eada65fcfaa17cc4e23464ad748` (current
GitHub main) differs from tested merge `6154b745ed56c819cad179daa61d0ba606bede3b` only in
contributor/changelog/roadmap docs. Application, tests, package/lock, artifact checker and workflow
match exactly. No run exists for the docs-only HEAD. Rechecked run 39302343644 attempt 1, all 12
job/step records and command logs: 220 tests per Linux/macOS cell; Windows 219 passed plus existing
FIFO skip; standalone formatting, fresh builds, strict Twine and all 24 independent artifact
installations passed. Historical failures remain unchanged. No new prerequisite blocker.

Read #4, direct prerequisite #2 and transitive #1, repository guidance and
configuration/coverage/note contracts. #2 is accepted/closed; native reciprocal #2 -> #4 -> #5 links
remain unchanged. #3 is not a new direct prerequisite. No local/vendor_docs directory exists.

Material decisions recorded before implementation:

- Internal enum allowlist: nonverbose version, data query, Tooling data query only; fixed argv,
  explicit non-option-like target, SELECT-only query text, no shell/extra flags/file/output
  operations. No Thread 05 query templates, identity verification or inventory adapter.
- Explicit absolute executable path, no PATH/default-org search. Resolve/check only the supplied
  executable; reject command wrappers. POSIX direct execution only, nonblocking bounded binary
  stdout/stderr collection with wall timeout, process-session/group termination and child reap.
  Windows execution fails closed pending a safe native launcher/descendant-cleanup implementation;
  simulated Windows refusal is not qualification. No shell workaround.
- Controlled explicit absolute working directory, stdin closed; child environment excludes arbitrary
  inherited CLI/Node overrides, disables telemetry/update notices and caps query auto-fetch. CLI may
  still use/write its own auth/config/log state in future authorized live runs; read-only queries
  are not a third-party no-write guarantee.
- Official query reference/schema/source and SfCommand verify status/result/warnings and
  records/totalSize/done; oclif version uses a bare architecture/cliVersion/nodeVersion result.
  Preserve completion/continuation/count signals; never grant inventory completeness.
  Duplicate-key/nonfinite/deep/malformed/oversized envelopes fail. Discard stderr and raw
  diagnostics; emit only fixed operational/config diagnostics without raw exception chains or
  logging.
- Standard library only; no dependency changes. Synthetic fixtures/mock process interfaces and
  fictional children only. No sf invocation, auth discovery, real org/vault,
  install/update/login/query/Apex/deploy, public commands or later-thread work.

Local roadmap synchronized. Changes remain unstaged/uncommitted; #4 stays open pending maintainer
acceptance. Thread 05 and all later threads remain explicitly not started. No CI rerun or Git
delivery authorized/performed.

### Thread 04 implementation progress — 19 October 2026

Thread 04 progress — internal implementation complete locally; final verification/review continues.

- Added fixed version/query/Tooling operations, explicit absolute executable and working directory,
  explicit non-option-like org selectors, argument-list binding, limited SELECT input and no
  shell/extra flags/default org.
- POSIX nonblocking stdout/stderr collection enforces independent byte caps before decoding, one
  wall deadline and process-group kill/direct-child reap. Cleanup attempts both pipes and reap even
  after a cleanup error. Windows/native wrappers fail closed as recorded before coding.
- Official command/schema/framework sources distinguish Salesforce query envelopes from bare oclif
  version output. Bounded UTF-8/JSON validation rejects duplicate/nonfinite/deep/malformed/oversized
  output; replies retain counts/done/continuation and warning/stderr presence without claiming
  inventory coverage. Diagnostics contain only fixed safe text.
- Synthetic fixtures and mocked interfaces cover argv, metacharacters, option-like targets, Windows
  refusal, errors/expired auth/redaction and envelope bounds. Fictional Python children exercise
  both pipe limits, concurrent drain, timeout, interruption, reap/closed handles and descendants
  holding pipes. No sf process, auth discovery or real org/vault access.
- Latest full local macOS ARM64 Python 3.14.7 suite: 339 passed, no skips. Earlier 335-test suites
  passed Python 3.12.7 and 3.13.15; final suites will be refreshed after review additions. Ruff and
  strict Poetry lock passed. Bandit passes with two narrow reviewed annotations for the intentional
  subprocess import and validated shell-free invocation; no global suppression.
- Fresh r2 wheel/sdist strict Twine, exact 17/16-member archive allowlists and independent clean
  Python 3.14.7 installs outside checkout passed, including installed synthetic-envelope validation.
  Final cleanup hardening requires rebuilt artifacts. Initial sandbox build could not reach PyPI;
  network-enabled isolated build/install succeeded. Runtime tests remain offline.

Docs/changelog and roadmap are being synchronized for final handoff. No
dependency/lock/workflow/license/normalized/offline-source changes or public commands. Hosted
evidence remains baseline-only; no Thread 04 hosted/native Windows/real CLI execution is claimed.
All changes remain unstaged/uncommitted; #4 stays open pending acceptance, Ready to merge/release
unchecked. Thread 05 and all later threads remain not started.

### Thread 04 handoff — 19 October 2026

**Implemented and verified locally; pending maintainer acceptance.** #4 remains open; Ready to
merge/release remains unchecked. Current changes are unstaged/uncommitted on existing `main` at
`63a78dc`. No Thread 04 hosted CI, delivery, acceptance, or publication is claimed.

Implemented only the internal `sources/sf_cli.py` transport, shared bound constants, synthetic
fixtures, focused unit/fictional-process tests, `docs/SF_CLI.md`, contributor/README/changelog
guidance and the deliberate artifact-allowlist/smoke extension. No new dependency, public command,
org identity verification, live inventory/audit adapter, graph, renderer, or state/vault operation.
Existing config/models/errors/offline source, license, lockfile and workflow are unchanged.

### Verified checklist

- [x] Explicit absolute executable resolution without PATH discovery; fixed version/query/Tooling
  allowlist; explicit non-option-like org targets and indivisible argv values.
- [x] Controlled explicit working directory, closed stdin, restricted environment, finite wall
  deadline and independent byte ceilings enforced during binary collection before decoding/parsing.
- [x] POSIX process-group cleanup, direct-child reap, pipe/selector closure on
  success/failure/overflow/timeout/interruption; cleanup continues after individual errors.
- [x] Bounded command-specific success/error JSON, malformed/duplicate/nonfinite/deep/oversized
  refusals, preserved done/count/continuation signals, no inferred complete inventory, fixed
  diagnostics and no raw output/auth/personal-data logging.
- [x] Spaces/metacharacters, option-like targets, missing executable, expired auth,
  malformed/oversized JSON, excessive stdout/stderr, timeout, process cleanup and redaction tested
  offline.
- [x] Windows/native execution and wrappers fail closed; no shell workaround; explicit platform
  limits and official contract references documented before dependent implementation.
- [x] Docs/changelog, compatibility/privacy review, fresh artifacts, independent installs and roadmap handoff completed.
- [ ] Maintainer acceptance, separately authorized delivery and exact-commit hosted Thread 04 verification.

### Actual local evidence

Native macOS 27.0.1 ARM64, Poetry 2.4.2:

| Check | Result |
| --- | --- |
| Full pytest, Python 3.12.7 / 3.13.15 / 3.14.7 | **340 passed each, no skips**; 120 new cases |
| 3.14.7 combined statement/branch coverage | **97% overall; 99% CLI boundary**, remaining gaps visible |
| Strict Poetry metadata/lock; Ruff lint/format (50 files) | Passed |
| Bandit | Passed; two line-specific reviewed subprocess annotations, no global rule disabled |
| Fresh final r4 wheel/sdist / strict Twine | Passed both |
| Independent clean artifact installations | Wheel and sdist each passed outside checkout on Python 3.14.7 |
| Archive contents | Exact **17-member wheel / 16-member sdist**; only `sources/sf_cli.py` added to allowlist; source/README/pyproject/license bytes match checkout |
| Installed probes | Import/resource/model hashing, synthetic partial CLI envelope, dependency consistency, both entry points, future-command refusal, offline source preservation and no discovery writes |
| Review | Local Markdown links/fences, privacy/scope/contracts, all changed/untracked files, exact headers and whitespace passed; index remains empty |

Final artifacts: `<temporary>/obforce-thread04-candidate-20261019-r4/`.

| Artifact | SHA-256 |
| --- | --- |
| `obforce-0.1.0.dev0-py3-none-any.whl` | `cd3dcdfd428e103870f9da01e787e1619b918f428ddbe6374e013919df2f9f64` |
| `obforce-0.1.0.dev0.tar.gz` | `2a04d804318cafe5c6c8707039c2d81f0add1d4f9b1b53e6b37d8507b758d887` |

The first sandbox build could not reach PyPI; network-enabled isolated build/install succeeded.
Passed r2/r3 candidates are superseded by r4 after cleanup hardening and a regression fix rejecting
enormous timeout integers before float conversion. Setup/build/install used network; application
tests used only synthetic data, mocked process interfaces and fictional Python children. No `sf`
executable was invoked or discovered.

### Prerequisite, limitations and next work

Verified #2 and transitive #1 acceptance/code, current docs-only HEAD `63a78dc`, tested merge
`6154b745ed56c819cad179daa61d0ba606bede3b` containing `20bff7f`, and run
[39302343644](https://github.com/jeffshurtliff/obforce/actions/runs/39302343644), attempt 1. Every
job/required step and command log passed: eight Linux/macOS cells with 220 tests each; four Windows
cells with 219 passed/one existing FIFO skip each; standalone formatting/build/Twine/all 24
independent installs. Application/tests/tooling/workflow are identical between merge and current
docs-only HEAD, which has no separate run. Historical failed/masked runs remain unchanged. #3
closure creates no direct #4 dependency.

**Retained gaps:** No real installed CLI/Node/plugin execution, authentication, org metadata, vault,
native Linux/Windows or local Python 3.15 Thread 04 run. Windows execution is unavailable; POSIX
process/symlink tests are explicitly gated on unsupported hosts and Windows-refusal tests are
mocked. Baseline hosted Windows evidence qualifies neither the new transport nor Windows live
execution. Trusted installation/interpreter/plugin behavior, OS-uninterruptible spawn/processes and
hostile descendants escaping a POSIX process group are outside this boundary. The CLI may have its
own auth/config/log/cache side effects in a future authorized live run. No source/model/coverage or
stable public API promise is expanded.

**Tracking/Git:** Existing labels (`enhancement`, `codex`, `maintainer`, `security`), assignment,
milestone and reciprocal #2 -> #4 -> #5 links are preserved. No duplicate issue, stage, commit,
push, PR, issue closure, CI rerun or publishing. Work remains reviewable and uncommitted; #4 remains
open for acceptance. **Next eligible after acceptance/delivery verification and a new request:
Thread 05 / #5, explicitly NOT STARTED. Threads 06–17 also remain NOT STARTED.**

**Issue evidence:** [Start and prerequisite/decision record](https://github.com/jeffshurtliff/obforce/issues/4#issuecomment-6274953209),
[implementation progress](https://github.com/jeffshurtliff/obforce/issues/4#issuecomment-6275092739),
and [verified checklist/handoff](https://github.com/jeffshurtliff/obforce/issues/4#issuecomment-6275133652).
The issue body marks all four implementation tasks and verified local checks;
Ready to merge/release remains unchecked. #4 remains open for maintainer acceptance.

### Thread 04 acceptance and closure — 19 October 2026

**Accepted and complete.** The maintainer reviewed/pushed Thread 04, confirmed passing CI and
explicitly requested issue closure when appropriate. Delivered code and all hosted acceptance gates
are verified. Closing #4 as completed; no release/publication is implied. Thread 05 is next eligible
and remains **not started**.

**Delivered identity:** Implementation `09a701169f80f875052359ff0b84476da3c36942`, merged at
`6980b26bc539779fb9be2b7fb1cc6ae7f655f418`. Clean local main, origin/main and live GitHub main match
the merge; all packaged source bytes match the reviewed final r4 candidate. Actual code retains
fixed operations/explicit targets, bounded pre-decode pipe collection, process-group cleanup,
private envelopes/redaction and Windows refusal. No maintainer changes were discarded.

**Exact-commit hosted evidence:** Inspected every job/required step and full command logs in [run
39314787749, attempt 1](https://github.com/jeffshurtliff/obforce/actions/runs/39314787749), head
`6980b26bc539779fb9be2b7fb1cc6ae7f655f418`:

| Cells | Verified outcome |
| --- | --- |
| Linux/macOS, Python 3.12–3.15 (8) | **340 passed per cell, no skips**; 97% combined coverage |
| Windows, Python 3.12–3.15 (4) | **329 passed, 11 skipped per cell**; 93% combined coverage |
| Every cell | Standalone strict metadata/lock, Ruff lint/format (50 files), Bandit, fresh wheel/sdist build, strict Twine, both independent artifact installs and whitespace passed |

All 24 independent artifact installations passed exact archive/license/import/resource/model,
synthetic CLI-envelope, dependency, entry-point, offline-source and no-discovery-write checks. No
required workflow step was skipped and no hidden formatter/command failure appears behind the green
summary. Two narrow reviewed subprocess Bandit annotations remain explicit.

The 11 Windows skips are deliberate and retained: nine POSIX process-collector cases, one POSIX
wrapper-symlink case and the existing unavailable native FIFO case. Windows refusal/envelope/argv
tests and installed smoke checks passed; they do **not** qualify Windows sf execution. Linux/macOS
fictional-child transport tests executed successfully. No real sf/Node/plugin/authenticated
org/vault execution or full lifecycle qualification is claimed; trusted-installation,
OS-interruption and escaped-descendant limitations remain.

**Related future work:** The maintainer associated [#18 — Native Windows support for the Salesforce
CLI process boundary](https://github.com/jeffshurtliff/obforce/issues/18). Verified its existing
cross-reference to #4, open backlog status and explicit outside-v0.1.0 scope/eventual-v1.0.0 intent.
It is not a new prerequisite for #4/#5 and does not block this closure or authorize implementation.
Windows execution remains fail-closed. #18 is **not started**; no new dependency edge or
milestone/schedule was added.

### Verified acceptance gates

- [x] All four original Thread 04 implementation tasks and offline acceptance scenario.
- [x] Maintainer review and exact delivered implementation/merge identity verified.
- [x] All 12 hosted suites and standalone check/build/Twine/independent-install gates passed, with
  actual Windows skips preserved.
- [x] Existing normalized config/identity/hash/coverage/note/offline-source contracts preserved; no
  public command or new dependency.
- [x] Windows limitation linked to existing #18 without expanding v0.1.0 or changing the prerequisite graph.
- [x] Maintainer authorized closure; current roadmap/docs/checklist/handoff synchronized.

**Docs/Git/handoff:** Updated current roadmap status/index, Thread 04 acceptance record, Thread 05
eligibility/exact kickoff prompt, CLI-boundary/contributor guidance and changelog. Earlier
start/progress/local handoffs, candidate hashes and failed CI history remain historical evidence.
This is a prose-only update: local links/fences/consistency/privacy/whitespace and tracked/untracked
review checked; no new application tests/builds/dependency installation needed. Final acceptance
docs remain unstaged/uncommitted on main at `6980b26`; delivered code is already merged/pushed. No
new issue, commit, push, PR, rerun, release, publication, Salesforce/auth/vault access or later
implementation.

Existing #4 labels/assignment/milestone and reciprocal #2 -> #4 -> #5 native relationships are
retained. #4 is closed as completed. **Next eligible: Thread 05 / #5, explicitly NOT STARTED.
Threads 06–17 and enhancement #18 also remain NOT STARTED.**

**Closure evidence:** [Final verified acceptance/closure comment](https://github.com/jeffshurtliff/obforce/issues/4#issuecomment-6276129493).
#4 is closed as completed with implementation/acceptance gates checked, original
metadata and reciprocal native dependencies preserved. #18 remains open backlog;
#5 remains open and not started.

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

### Thread 05 start and adapter decisions — 19 October 2026

Thread 05 started — 19 October 2026. Implementing only the internal live Apex inventory/audit adapter, with synthetic fixtures and mocked process responses; no live Salesforce access is authorized or performed.

Prerequisites verified: read #4 and transitive #2/#1, current guidance/contracts and accepted process/model/offline code. Initial clean checkout HEAD `a4d248c95d38a3991e00aacb206a7ebbb97856d7` matches GitHub main and differs from tested merge `6980b26bc539779fb9be2b7fb1cc6ae7f655f418` only in four documentation files. Rechecked run [39314787749, attempt 1](https://github.com/jeffshurtliff/obforce/actions/runs/39314787749), every job/step and full command logs: eight Linux/macOS cells each 340 passed; four Windows cells each 329 passed/11 expected skips; standalone checks, fresh build/Twine and 24 independent installs passed. Historical failed runs remain unchanged. No new prerequisite blocker. Native reciprocal #4 -> #5 -> #6 links, labels/assignment/milestone retained; #18 is not a prerequisite. No local/vendor_docs directory exists.

Material decisions before implementation:

- Use only the accepted QUERY/TOOLING_QUERY operation families. First query `SELECT Id FROM Organization LIMIT 2` with an explicit target; require one validated org ID and consistent completion/count/no-continuation/no-warning evidence. Construct the existing SourceBinding and compare any configured/state binding before accepting inventory. No auth discovery, org display, default org, adoption or rebinding.
- Enumerate ApexClass with fixed allowlisted identity/namespace/API-version/status fields, server `ORDER BY Id`, `LIMIT 200`, and subsequent validated `Id > '<cursor>'` filters. Exclude namespaces server-side when selected; apply optional existing name filters locally without interpolating them. Follow no continuation URL, use no OFFSET/bulk/extra operation. Require a final empty page AND consistent count/done/no-continuation/no-warning evidence on every page. Never treat one done flag, empty array or process success alone as completeness. Retain safe per-request observed signals; contradictions stop inventory as partial. No snapshot/deletion proof.
- Bound the entire collection to 300 seconds, 156 queries, 51 inventory pages and 10,000 enumerated records; each query retains the accepted process byte/time/cleanup limits with a reduced 262,144-byte stdout cap. A full boundary without exhaustion yields explicit partial coverage, never silent truncation.
- Required inventory/identity query failures remain typed operational failures; malformed required or observed audit values are validation errors, duplicate mappings/source mismatches conflicts. Optional audit query process failures yield unavailable/partial audit coverage with safe fixed diagnostics; they cannot erase inventory evidence. Do not guess whether a redacted CLI failure means permission or field availability.
- Query audit dates separately, and optional `CreatedBy.Name`/`LastModifiedBy.Name` only on selected Apex IDs. No User scan/IDs/usernames/emails, Body, source, tokens or auth URLs. Name omission makes name facts absent and sends no name query; requested missing fields are unavailable and explicit null stays null. No invented dates or debt. API request version remains unknown because the accepted transport intentionally does not select/report it; class ApiVersion is separate.
- Use unchanged component/selection/hash/ownership/exit contracts, explicit provenance and independent inventory/audit/relationship coverage. Relationships remain uncollected/unrequested for Thread 06. Preserve Windows refusal, process controls and offline behavior; standard library only, no dependency changes or public commands.

Official current documentation and source reads (no sf execution) confirm CLI JSON/target/Tooling flags, auto-fetch/count/warning behavior, ApexClass fields and system audit relationships, Organization query support, filter-based pagination and endpoint-specific permission limits. HTML object pages lacked readable bodies; official current Salesforce PDFs supplied those sections. The CLI source is still `salesforcecli/plugin-data@a0cdb671f42af74e31a782c34c5cdcc22e1ea5b0`. Detailed references/limitations will accompany adapter docs.

Changes will remain unstaged/uncommitted and #5 open pending maintainer acceptance. No new issue, stage/commit/push/PR/closure/rerun/publication. Thread 06, all later threads and #18 remain explicitly not started.

### Thread 05 implementation progress — 19 October 2026

Thread 05 progress — 19 October 2026. Internal implementation and synthetic process-response regression coverage are complete locally; final review/artifact verification continues. #5 remains open pending maintainer acceptance.

- Added `sources/live.py`: minimal explicit-target Organization identity query, unchanged SourceBinding checks before inventory, allowlisted Apex fields, bounded SELECT/ID-filter pages with terminal probe, safe contradictory signal evidence and independent coverage. No continuation endpoint execution, deletion inference, public command or dependency change.
- Scoped date/display-name queries use only selected validated Apex IDs. Explicit omission sends no name query and leaves name facts absent; missing requested facts remain unavailable and explicit null remains null. Operational required failures, optional unavailable coverage and higher-precedence validation/conflict failures stay distinct. Dates/versions/IDs normalize deterministically; unrelated/private response fields are refused.
- Current local macOS ARM64 suites pass **434 tests each on Python 3.12.7, 3.13.15 and 3.14.7**, no skips. Python 3.14 combined statement/branch coverage: **97% overall / 98% live adapter**. The initially selected bare 3.12/3.13 interpreters lacked pytest; existing isolated test environments then passed both full suites. No unavailable attempt is counted as a pass.
- Strict Poetry metadata/lock and Ruff lint/format pass. Bandit passes with the existing two subprocess annotations plus two narrowly reviewed B608 annotations for fixed SOQL structure with checksum-validated alphanumeric IDs; injection-shaped response-ID regressions stop before subsequent query construction. No global lint/security suppression.
- Fresh r1 build, strict Twine, exact 18-member wheel / 17-member sdist allowlists and independent Python 3.14 installs passed. Installed smoke includes the live adapter under a mocked run_sf boundary, with network blocked and no external tools, plus existing offline preservation and help/version checks. Rebuild final artifacts after the subsequent annotation change; r1 is superseded for source-byte review.
- Added live adapter limits/contracts/current official references and synchronized applicable docs/changelog. Existing process transport, model/hash/ownership contracts, offline code, lock/dependencies, workflow and license remain unchanged.

Hosted evidence remains the verified Thread 04 baseline only. No Thread 05 hosted result, native Linux/Windows run, local Python 3.15, real CLI/Node/plugin/org/vault access or Windows sf execution qualification is claimed. No sf invocation/auth/credential/.env discovery or CLI/plugin install/update occurred. Separate CLI calls do not provide a metadata/auth snapshot or whole-org permission proof. Thread 06/later threads and enhancement #18 remain explicitly not started. Changes remain unstaged/uncommitted; no new issue, stage/commit/push/PR/closure/rerun/publication.

### Thread 05 handoff — 19 October 2026

Thread 05 handoff — 19 October 2026. **Implemented and verified locally; pending maintainer acceptance.** #5 remains open; Ready to merge/release remains unchecked.

Implemented only the internal live Apex inventory/audit adapter, shared finite limits, realistic synthetic envelope fixture, 101 new mocked-process regression cases, adapter/contract/contributor/changelog docs and the deliberate artifact allowlist/installed-smoke extension. No public lifecycle command, real Salesforce access or dependency addition. The accepted sf process boundary, offline source/parser, frozen config/models/errors/hash/scope/ownership contracts, lockfile/package metadata, workflow and Apache license are byte-unchanged.

Verified checklist:

- [x] Explicit target and minimal non-secret Organization.Id query; validated canonical org identity; configured/state mismatch refusal before inventory; no automatic adoption/rebinding.
- [x] Fixed allowlisted Apex projection and scoped optional date/display-name queries; no Body, User scan, usernames/emails/tokens/auth URLs; name omission, absent/unavailable/null distinctions and deterministic provenance/hashes.
- [x] Bounded multi-page SELECT enumeration with terminal probe, explicit namespace/name scope, finite record/page/query/time/byte limits and no arbitrary continuation execution. Contradictory count/done/continuation/warning signals retained; requested incompleteness yields existing outcome 4.
- [x] Required operational failures, optional audit unavailability, malformed values and higher-precedence identity/config/model conflicts remain distinct; inventory/audit/relationships are independent. Relationships remain uncollected.
- [x] Mocked identity/target mismatches, multiple pages, empty/truncated/contradictory results, namespace selection, permission loss, audit omission/unavailability/null, invalid IDs/dates/versions, duplicates, privacy/injection refusal, stable hashes, record-ceiling terminal probe and no-work-artifact preservation verified. Existing offline suite unchanged.
- [x] Current official query/field/permission/JSON/pagination contracts read without sf execution; decisions recorded before code. Docs/changelog/roadmap synchronized and package artifacts independently verified.
- [ ] Maintainer acceptance, separately authorized delivery and exact-commit hosted Thread 05 validation.

Actual local evidence — native macOS 27.0.1 ARM64, Poetry 2.4.2:

| Check | Result |
| --- | --- |
| Full pytest, Python 3.12.7 / 3.13.15 / 3.14.7 | **441 passed each, no skips** |
| Python 3.14 combined statement/branch coverage | **97% overall / 98% live adapter**; remaining gaps visible |
| Strict Poetry metadata/lock; Ruff lint/format | Passed; 53 files formatted |
| Bandit | Passed; four narrow reviewed annotations: existing subprocess pair plus fixed SOQL construction pair; no global suppression |
| Fresh final r2 wheel/sdist / strict Twine | Passed both |
| Archive inspection | Exact **18-member wheel / 17-member sdist**; every packaged source byte matches checkout; sdist README/metadata/license match |
| Independent clean artifact installs | Both passed on Python 3.14.7 outside checkout: imports/resources/hash, mocked live adapter, synthetic envelope, offline source immutability, pip check, both entry points and future-command refusal |
| Application smoke controls | Network blocked, no external tools; live installed smoke mocks run_sf; no discovery/work-directory writes |
| Review | Local Markdown links/fences, exact four Python headers, privacy/scope/frozen-contract and tracked/untracked diff review, whitespace and empty index checked |

Final candidate: `<temporary>/obforce-thread05-candidate-20261019-r2/`.

- Wheel SHA-256: `06b2e5a19e3e142949ba581385817d2db27b9394d5f233171a5f6fd618d972d5`
- Sdist SHA-256: `6fa6e32a8e0f2a951cd70bd6a470a171b5ad38201bcb4f58faf9f0d400e3e489`

The earlier passing r1 artifacts are superseded after the final two reviewed source annotations and README wrapping. Initial bare Python 3.12/3.13 interpreters lacked pytest; existing isolated test environments subsequently passed the final suites. Initial Bandit findings were reviewed and constrained with injection-refusal tests plus two line-specific B608 annotations. Bandit emits informational nosec AST notices for these f-strings but reports no findings. Build/install setup used the network; runtime tests remained offline.

Prerequisite evidence: #4 and transitive #2/#1 accepted/closed and actual source verified; reviewed `09a7011` / merge `6980b26bc539779fb9be2b7fb1cc6ae7f655f418`. Re-read all jobs/steps/full logs of [run 39314787749, attempt 1](https://github.com/jeffshurtliff/obforce/actions/runs/39314787749): all 12 cells passed; eight Linux/macOS cells each 340 tests, four Windows cells each 329 passed/11 expected skips; standalone formatting, fresh builds/Twine and all 24 independent installs passed. Current baseline HEAD `a4d248c95d38a3991e00aacb206a7ebbb97856d7` differs only in four docs files and has **zero** workflow runs; source/tests/tooling/workflow match that tested merge. Historical failed/masked runs are preserved. This is prerequisite evidence, not hosted Thread 05 evidence.

Retained gaps: no Thread 05 hosted CI, local Python 3.15, native Linux/Windows, real installed sf/Node/plugin, actual org permissions/live metadata or vault validation. Windows sf execution remains refused; prerequisite CI/refusal tests do not qualify it. CLI calls are bounded read queries but may have the CLI's own auth/config/log side effects in a future authorized run. Separate identity/keyset calls are not an atomic auth/metadata snapshot, whole-org permission certification or deletion proof. Request API version remains unknown rather than inferred from class ApiVersion. No remaining implementation blocker identified; acceptance/delivery/hosted checks remain separate gates.

Git/tracking: work remains unstaged/uncommitted at baseline HEAD on the existing `feature/5-thread-05-live-apex-inv-and-audit-enrichment` branch. No branch was created or switched by the agent. Existing #5 labels/assignment/v0.1.0 milestone and native reciprocal #4 -> #5 -> #6 relationships are retained; #6 also retains prerequisite #3. No duplicate issue, stage, commit, push, PR, closure, CI rerun, publication, sf invocation, auth/credential/.env discovery, installation/update or real org/vault access.

**Next eligible after Thread 05 acceptance/delivery verification and a new request: Thread 06 / #6, explicitly NOT STARTED. Threads 07–17 and enhancement #18 also remain NOT STARTED.**

Issue evidence: [start/decisions](https://github.com/jeffshurtliff/obforce/issues/5#issuecomment-6276257245), [implementation progress](https://github.com/jeffshurtliff/obforce/issues/5#issuecomment-6276378837). Final verified checklist/handoff is synchronized with this roadmap; issue #5 stays open for acceptance.

**Final issue evidence:** [Verified checklist/handoff](https://github.com/jeffshurtliff/obforce/issues/5#issuecomment-6276453506).
The existing issue body checks all four implementation tasks and local verification,
with Ready to merge/release unchecked and #5 open pending maintainer acceptance.

### Thread 05 acceptance and closure — 19 October 2026

**Accepted and complete.** The maintainer reviewed/pushed Thread 05, confirmed passing CI and requested issue closure when done. Delivered code and all hosted gates are verified; #5 is closed as completed. No release/publication is implied. Thread 06 is next eligible and remains **not started**.

**Delivered identity:** Implementation `a5b7269cb4f50594489fe3b77f5350d21a523573`, merged at `85ba7cd725e2f246f39d6b11d18d431f4cc73d38`. Clean local main, origin/main and live GitHub main matched the merge. All 13 packaged source files match the reviewed final r2 wheel bytes; implementation and merge trees match. The actual adapter retains explicit target/org verification, configured/state mismatch refusal, bounded SELECT pages, private scoped optional audits, precise coverage/provenance/hashes and unchanged Windows transport refusal. No maintainer changes were discarded.

**Exact-commit hosted evidence:** Inspected every job/required step and full command logs in [run 39325616681, attempt 1](https://github.com/jeffshurtliff/obforce/actions/runs/39325616681), head `85ba7cd725e2f246f39d6b11d18d431f4cc73d38`:

| Cells | Verified outcome |
| --- | --- |
| Linux/macOS, Python 3.12–3.15 (8) | **441 passed per cell, no skips**; 97% combined coverage |
| Windows, Python 3.12–3.15 (4) | **430 passed, 11 expected skips per cell**; 94% combined coverage |
| Every cell | Standalone strict metadata/lock, Ruff lint/format (53 files), Bandit, fresh wheel/sdist build, strict Twine, both independent artifact installs and whitespace passed |

All 24 independent artifact installations passed exact archive/license/import/resource/model checks, mocked live adapter and CLI-envelope smoke checks, dependency consistency, both entry points, offline source preservation and no-discovery-write probes. All required steps ran successfully; no hidden formatter failure appears behind the job conclusions. Four narrow reviewed Bandit annotations remain: the existing subprocess pair and the fixed-structure, validated-ID SOQL pair. The informational f-string nosec notices are not scanner findings.

The 11 Windows skips remain explicit: nine POSIX collector cases, one POSIX wrapper-symlink case and the unavailable FIFO case. Windows mocked live-adapter, argv/envelope/refusal and installed artifact smoke checks passed; these do **not** qualify Windows sf execution. Linux/macOS fictional-child process tests executed. No real sf/Node/plugin/authentication/org metadata/vault execution or full lifecycle qualification is claimed. Separate CLI identity/keyset calls are not an atomic auth/metadata snapshot or whole-org permission/deletion proof. Request API version remains unknown rather than inferred from class ApiVersion. Enhancement #18 remains open/unstarted outside v0.1.0 and is not a new prerequisite.

### Verified acceptance gates

- [x] All four original Thread 05 implementation tasks and synthetic acceptance scenario.
- [x] Maintainer review, delivered implementation/merge identity and final candidate source bytes verified.
- [x] All 12 exact-merge hosted suites plus standalone checks/build/Twine/24 independent installs passed, with actual Windows skips retained.
- [x] Existing config/model/hash/scope/ownership/offline/process contracts retained; no public command, dependency or Windows execution expansion.
- [x] Maintainer authorized closure; current docs/roadmap/checklist and exact Thread 06 kickoff prompt synchronized.

**Docs/Git/handoff:** Updated current roadmap status/index, Thread 05 acceptance record, Thread 06 eligibility/exact prompt, live-adapter/contributor guidance and changelog. Earlier start/progress/local candidate evidence, initial unavailable interpreter attempts, reviewed Bandit findings and historical failed CI runs remain historical evidence. This closure is prose-only: local links/fences/consistency/privacy/whitespace and tracked/untracked diff review are checked; no new application tests/builds/dependency installation are needed. Final acceptance documentation remains unstaged/uncommitted on main at `85ba7cd`; implementation is already merged/pushed. No new issue, stage, commit, push, PR, rerun, release, publication, live Salesforce/auth/vault access, chat creation/message, delegation or later implementation occurred.

Existing #5 labels/assignment/v0.1.0 milestone and native reciprocal #4 -> #5 -> #6 links are retained. #6 retains its other prerequisite #3 and dependents #7/#10. #3 is accepted/closed with its existing exact-commit evidence; this tracking update does not alter the dependency graph. **Next eligible: Thread 06 / #6, explicitly NOT STARTED. Threads 07–17 and enhancement #18 also remain NOT STARTED.**

**Closure evidence:** [Final verified acceptance/closure comment](https://github.com/jeffshurtliff/obforce/issues/5#issuecomment-6280345436).
Read back #5 as closed with reason completed, implementation/acceptance gates checked,
original metadata and reciprocal native dependencies preserved. #6 remains open
and not started with prerequisites #3 and #5 accepted/closed.
### Thread 06 start, prerequisite gate and decisions — 19 October 2026

Starting only Thread 06 under the maintainer's request; #6 stays open for acceptance. Read #6 and prerequisite #3/#5, repository guidance, roadmap and configuration/coverage/note/offline/CLI/live contracts. No local/vendor_docs directory exists. Existing labels, assignment, v0.1.0 milestone and native reciprocal prerequisites #3/#5 and dependents #7/#10 match the roadmap.

**Prerequisite gate passed before implementation:** Current main `61e442357a97618ae096924973ce69bf398650ab` contains accepted #3 correction `20bff7f` / merge `6154b74` and #5 implementation `a5b7269` / merge `85ba7cd`. Current source/tests/dependencies/workflow/artifact checker match the tested #5 merge; intervening changes are documentation only. Current HEAD has no separate run. Re-read every required step and full logs in exact-merge runs [39302343644, attempt 1](https://github.com/jeffshurtliff/obforce/actions/runs/39302343644) and [39325616681, attempt 1](https://github.com/jeffshurtliff/obforce/actions/runs/39325616681): all 12 cells passed standalone checks and fresh build/Twine/two independent installs. #3 Linux/macOS: 220 passed; Windows: 219 passed/1 skip per cell. #5 Linux/macOS: 441 passed; Windows: 430 passed/11 expected skips per cell. Historical failures are retained. Windows refusals/skips do not qualify Windows sf execution.

**Material capability limitation, recorded before code:** Current official Tooling guide v68.0, Winter '27, updated 9 October 2026, printed pp. 643–648, still labels MetadataComponentDependency Beta/evaluation-only, allows Tooling queries from API 43.0, caps them at 2,000 records, excludes reports, and disallows ORDER BY, queryMore, COUNT(), OFFSET, name filters and range operators. Its general SOQL summary and field property flags contradict some object-specific restrictions; follow the specific restrictions. Apex examples establish direction/possible endpoints, not a comprehensive supported-type or permission matrix. General API Enabled/org access is required; the object chapter supplies no precise additional permission guarantee. No permission or capability discovery is authorized. Official CLI query source/schema at current main `a0cdb671f42af74e31a782c34c5cdcc22e1ea5b0` still auto-fetches, warns on missing records, and returns records/totalSize/done; it can make extra column-metadata requests. No installed CLI/Node/plugin capability is verified.

**Decisions before dependent implementation:**

- Source means referencing MetadataComponent*, target means referenced RefMetadataComponent*. Query exactly the eight endpoint fields through unchanged run_sf TOOLING_QUERY. Reverify Organization identity with Thread 05's fixed minimal query before relationships and require equality with the supplied live inventory binding; never trust alias alone.
- Probe each selected validated 18-character Apex ID once in each direction using only ID equality AND fixed ApexClass type equality. No name interpolation, IN/range/keyset/ORDER BY/COUNT/OFFSET, arbitrary endpoint/continuation, Bulk API or transport expansion. Enumerate IDs deterministically with fixed query/record/byte/time budgets; one reply per probe, no unsupported pagination.
- **Release limitation:** The allowlist cannot independently prove MCD exhaustion/type/permission completeness. Even clean empty replies and done=true remain partial, requested coverage (exit 4); no usable probe is unavailable. At the documented cap or any contradictory count/continuation/warning/extra-field signal, retain fixed safe evidence. Never manufacture complete platform coverage. A separate synthetic graph snapshot can exercise complete-empty semantics without granting the platform collector a completeness switch.
- Preserve both endpoint descriptors, namespace/type/provenance and contradictory observations, including unsupported/unresolved/external referencing endpoints in incoming views. Add a graph-specific evidence record rather than changing frozen ComponentKey/Relationship/hash/ownership contracts. Only exact type/ID/name/namespace matches resolve supported Apex keys; links later require explicit validated managed-note paths. No new notes or source body analysis.
- Deduplicate exact evidence deterministically; retain distinct evidence/coverage and stale records. Derive outgoing/incoming views from one graph, including self/cyclic edges. Prior in-memory graph reuse requires exactly matching verified source and selection; partial/unavailable refresh retains previous evidence stale with original provenance/coverage. State loading and publication remain later threads.
- Per-note graph fingerprints include incident evidence, graph coverage and relevant supplied note locations. Graph changes invalidate both endpoints; moves invalidate neighbors without changing component source hashes. Offline acquisition remains unchanged/not_collected. Standard library only, no dependency additions or public commands.

All runtime tests remain synthetic/offline. No real sf, auth/credential/.env discovery, CLI/plugin install/update, org/vault access, Windows transport, state loading or publication. Work remains unstaged/uncommitted; no stage/commit/push/PR/rerun/closure/publication or other chats/subagents. Thread 07–17 and enhancement #18 remain explicitly NOT STARTED.
### Thread 06 implementation progress — 19 October 2026

Implemented the internal graph and selected-ID two-direction relationship adapter. It reverifies actual org identity through the accepted process boundary, retains unresolved/unsupported/external endpoints on either side, deduplicates exact directed pairs with distinct provenance/coverage observations, preserves non-reaffirmed prior matching-source/scope evidence stale, and supplies reciprocal views plus graph/path/coverage invalidation. Existing component/source/scope/ownership contracts and offline behavior are unchanged. No new public command, note type, dependency or Windows transport.

The preimplementation release limitation remains: current MCD restrictions prevent independently verified exhaustion. Platform collection always reports requested partial/unavailable coverage, even for clean empty replies, and never erases prior edges as authoritative emptiness. Query/page/record/byte/time limits, safe contradictory page evidence and existing typed error precedence are retained. Added relationship documentation and explicit artifact allowlist/installed graph-mock extensions.

Current local macOS ARM64 suites: **507 passed each on Python 3.12.7, 3.13.15 and 3.14.7, no skips**. Strict Poetry metadata/lock, Ruff lint/format (58 files), and Bandit pass; combined 3.14 coverage is 96% (graph 89%, relationship adapter 91%, visible remaining gaps). Synthetic tests cover both directions/invalidation, cycles/self-edges, namespaces, unsupported/unresolved endpoints, scope/org conflicts, count/continuation/warning contradictions, cap/budget/failure/stale handling, privacy and source-hash stability. Final review and fresh build/Twine/archive/independent installation checks remain in progress; these counts are progress evidence, not acceptance.

Hosted evidence remains the verified prerequisite baseline only. No hosted Thread 06, native Linux/Windows Thread 06, local Python 3.15, real sf/Node/plugin/auth/org/vault execution, Windows sf qualification, rendering/state/publication or lifecycle evidence is claimed. All work remains unstaged/uncommitted; #6 stays open. Threads 07–17 and enhancement #18 remain explicitly NOT STARTED.
### Thread 06 handoff — 19 October 2026

**Implemented locally and ready for maintainer review; #6 stays OPEN pending acceptance.** Only Thread 06 was implemented. No maintainer acceptance, delivered commit, hosted Thread 06 pass or publication is implied.

**Prerequisite evidence:** Before coding, verified accepted/closed #3 and #5, actual code and all required steps/full logs for exact-merge runs `39302343644` / `6154b745ed56c819cad179daa61d0ba606bede3b` and `39325616681` / `85ba7cd725e2f246f39d6b11d18d431f4cc73d38`, attempt 1 each. Both passed all 12 cells. Current baseline `61e442357a97618ae096924973ce69bf398650ab` has documentation-only differences from the tested #5 merge and no separate run. Historical failed runs and Windows skips/refusals remain distinct evidence.

**Changes:** `graph/dependencies.py` supplies explicit private endpoints and directed edges, exact Apex resolution, distinct provenance/coverage observations, reciprocal views, deterministic self/cycle/dedup behavior, matching-source/scope stale refresh and incident/path/coverage fingerprints. `sources/relationships.py` uses unchanged run_sf operations and reverified org identity, fixed eight-field selected-ID/type equality probes in each direction and finite budgets. `_Session` accepts internal budget overrides with unchanged Thread 05 defaults. Graph records support unresolved referencing sources without changing frozen ComponentKey/Relationship/component/source/scope/hash/ownership/state contracts. No component facts are mutated, note types invented, bodies collected or static guesses added. Prior resolved endpoints on retained stale evidence are historical mappings, not proof of current presence. Offline remains uncollected and unchanged.

**Recorded release limitation:** Official current v68 Tooling guide pp. 643–648 confirms the 2,000-row Tooling cap, Beta/evaluation-only status, report exclusion and unsupported ORDER BY/queryMore/COUNT/OFFSET/name/range queries. Exact endpoint/type completeness and additional permission guarantees remain unverified. Generic field flags/SOQL summaries cannot override these restrictions. The fixed transport cannot independently prove exhaustion; every usable result, including clean empty replies, remains requested partial coverage, otherwise unavailable. No platform completeness switch or transport broadening is added. Prior non-reaffirmed matching-scope evidence is preserved stale; distinct contradictory evidence survives. Synthetic complete-empty replacement is tested separately and does not qualify live completeness.

**Verified local checklist:**

- [x] Current official API fields/direction/filter/endpoint/permission/pagination and CLI source/schema/wrapper reviewed; capability gaps and query/scope/prior-edge/coverage decisions recorded before code.
- [x] Bounded best-effort adapter with explicit source recheck, honest partial/unavailable outcomes and unchanged typed errors/exit precedence; no arbitrary endpoint, default org or Windows execution.
- [x] A → B reciprocal updates, duplicate/reordered observations, self/cycles/namespaces, unsupported/unresolved sources/targets, binding/scope mismatch, cap/budget/permission/capability/contradiction handling and stale preservation verified.
- [x] Graph-only and moved-path invalidation, unchanged component hashes/offline behavior, privacy/redaction, canonical ID/injection refusal and no working-directory artifacts verified.
- [x] Coverage/live/note/contributor/README/relationship docs, changelog and roadmap synchronized; no dependencies added; Apache license and lockfile unchanged.
- [x] Fresh wheel/sdist allowlists deliberately extended; both independently installed and exercised outside the checkout.
- [ ] Maintainer acceptance and delivery/exact-commit hosted Thread 06 validation.
- [ ] Ready to merge/release acceptance gate; release publication remains separately authorized.

**Actual local evidence — macOS 27.0.1 ARM64 / Poetry 2.4.2:**

| Check | Result |
| --- | --- |
| Full offline pytest, Python 3.12.7 / 3.13.15 / 3.14.7 | **517 passed each, no skips**; 76 new Thread 06 cases |
| Python 3.14.7 combined statement/branch coverage | **96% overall**; graph **90%**, relationship adapter **93%**; remaining gaps visible, no coverage suppressions |
| `poetry check --lock --strict`, Ruff lint/format, Bandit | Passed; 59 files formatted; no scanner findings |
| Fresh r2 build, strict Twine, exact archive inspection | Passed; **21 wheel / 20 sdist members**, exact unchanged Apache license and current packaged-source/README/pyproject byte matches |
| Independent wheel and sdist clean Python 3.14.7 installs | **Both passed**: imports/resources/model hashes, synthetic CLI/live/relationship graph/stale/move checks, dependency consistency, both entry points, offline preservation and no-write probes |
| Documentation/local links/fences, changed Python headers, privacy/diff and whitespace review | Passed; every changed/new Python header retains Created By and requested GPT-6.1 Sol / 19 Oct 2026 attribution |

The first sandbox build could not reach PyPI; the fresh r2 build and independent installation setup succeeded with network-enabled build/dependency acquisition. Runtime checks remained offline and synthetic. One new line-specific B608 annotation covers the fixed projection/prefix and strictly validated alphanumeric 18-character ID interpolation; the accepted four annotations remain. Informational f-string nosec notices are not findings.

Final r2 candidates remain in a temporary directory outside the checkout:

| Artifact | SHA-256 |
| --- | --- |
| Wheel | `f2faea9b8281bee2ae27cc943a590def3b87692bac374fe87e2d11e866471a9a` |
| Sdist | `8dadad007f90091065888558f042e02dc612d9e9db3690df34fef9d5049eb18e` |

**Gaps and boundaries:** No hosted Thread 06, native Linux/Windows Thread 06 or local Python 3.15 result; no real sf/Node/plugin/auth/permission/type/live-exhaustion/org/vault or Windows sf execution qualification. No real sf invocation, credentials/.env/auth discovery, CLI/plugin installation/update or private data upload occurred. Source inspection is not installed capability evidence. No renderer, note/state discovery/loading/adoption/publication, deletion, recovery, public lifecycle or comprehensive impact/runtime proof is supplied. These remain separate evidence/tasks; #18 is outside v0.1.0 and not a prerequisite.

**Git/tracking:** All 17 changed/new files remain unstaged/uncommitted on existing main at `61e4423`. No branch switch/create, stage/commit/push/PR/merge/tag/rerun/closure/release/publication/automation, duplicate issue, other chat or subagent. #6's implementation/test/docs/compatibility checklist is verified; Ready to merge/release remains unchecked. Existing enhancement/codex/maintainer labels, assignee, v0.1.0 milestone and native reciprocal #3/#5 → #6 → #7/#10 dependencies are preserved and read back. Local roadmap and public issue evidence agree; remote source/roadmap delivery remains pending maintainer action.

**Next eligible after Thread 06 acceptance/delivery verification and a new request: Thread 07 / #7, explicitly NOT STARTED. Threads 07–17 and enhancement #18 remain NOT STARTED.**
### Thread 06 acceptance and closure — 20 October 2026

**Accepted and complete.** The maintainer reviewed/pushed Thread 06, confirmed passing CI and requested closure if complete. Actual implementation, delivered identity and all hosted gates are verified; #6 is closed as completed. Thread 07 is next eligible and remains **not started**. No release/publication is implied.

**Delivered identity:** Implementation `d1134fad0c9dfe2b83a28d411f403f04c9582333`, merged at `2aa8d2be362c86c3d8288f757b852bc98a867b2e`. Clean local main, origin/main and live GitHub main matched that merge before this documentation update. Implementation/merge trees match, and all 16 packaged Python source files match the reviewed final r2 wheel bytes. Directed graph/provenance/reciprocal/stale/invalidation behavior, fixed read-only relationship queries and verified source binding remain as reviewed; no maintainer changes were discarded.

**Exact-commit hosted evidence:** Inspected every job, required step and full command log in [run 39431345348, attempt 1](https://github.com/jeffshurtliff/obforce/actions/runs/39431345348), head `2aa8d2be362c86c3d8288f757b852bc98a867b2e`:

| Cells | Verified outcome |
| --- | --- |
| Linux/macOS, Python 3.12–3.15 (8) | **517 passed per cell, no skips**; 96% combined coverage |
| Windows, Python 3.12–3.15 (4) | **506 passed, 11 expected skips per cell**; 93% combined coverage |
| Every cell | Standalone strict metadata/lock, Ruff lint/format (59 files), Bandit, fresh wheel/sdist build, strict Twine, both independent artifact installs and whitespace passed |

All 24 independent artifact installations passed exact archive/license/import/resource/model checks, mocked CLI/live/relationship graph/stale/moved-path smoke checks, dependency consistency, console/module entry points, offline source preservation and no-discovery-write probes. All required steps ran successfully; job conclusions conceal no formatter failure. Five narrow reviewed Bandit annotations remain (the subprocess pair, inventory/audit SOQL pair and fixed relationship SOQL); informational f-string nosec notices are not findings. Historical failed CI and earlier local candidate/build attempts remain recorded.

The 11 Windows skips remain nine POSIX collector cases, one POSIX wrapper-symlink case and the unavailable FIFO case. Hosted Windows mocked adapter/graph/envelope/refusal and installed artifact results do **not** qualify Windows sf execution. Linux/macOS fictional-child collector tests executed; no real sf/Node/plugin/auth/org/vault or full lifecycle evidence follows. The MCD exhaustion/type/permission limitation remains: requested platform relationships are partial/unavailable, even for clean empty replies. Complete-empty graph replacement is synthetic contract testing only. Offline relationships remain uncollected. No static guesses, Body collection, new metadata notes, transport expansion or runtime-impact/comprehensive coverage claim is added. Enhancement #18 remains outside v0.1.0 and is not a prerequisite.

**Verified acceptance gates:**

- [x] All four original implementation tasks and synthetic A → B/stale-failure acceptance criteria met, with precise collection limitations retained.
- [x] Maintainer review/push and actual implementation/merge/final candidate source identity verified.
- [x] All 12 exact-merge hosted suites, required standalone checks, fresh build/Twine and 24 independent installs passed; actual Windows skips retained.
- [x] Frozen config/identity/hash/scope/ownership, offline behavior and accepted transport/refusal contracts preserved; no dependencies or public commands added.
- [x] Maintainer authorized closure; existing issue checklist, documentation, roadmap status/index and exact Thread 07 kickoff prompt synchronized.

**Docs/Git/handoff:** Updated current roadmap status/index, Thread 06 acceptance record, Thread 07 eligibility/exact prompt, relationship/live/contributor guidance and changelog. Earlier start/progress/local handoff records remain historical, including their then-pending delivery/hosted evidence. This acceptance update is prose-only: local links/anchors/fences/consistency/privacy/whitespace and tracked/untracked diff review passed. No new application tests, builds or dependency installations were needed. Five documentation files remain unstaged/uncommitted on main at `2aa8d2b`; implementation is already delivered. No stage/commit/push/PR/merge/tag/rerun/release/publication, Salesforce/auth/vault access, other-chat action, delegation or later implementation occurred.

Existing #6 enhancement/codex/maintainer labels, assignee, v0.1.0 milestone and native reciprocal #3/#5 → #6 → #7/#10 links are retained. #7 keeps its other prerequisite #3 and remains open/not started. No duplicate tracking issue or new prerequisite is introduced. **Next eligible: Thread 07 / #7 under a new request, explicitly NOT STARTED. Threads 07–17 and enhancement #18 remain NOT STARTED.**

### Thread 07 start and pre-implementation decisions — 20 October 2026

Started under the maintainer's explicit Thread 07 request. #7 stays OPEN pending acceptance; no duplicate issue or later thread is started.

Prerequisites verified before code: #3/#6 accepted/closed, native #3/#6 → #7 → #8/#10 links, actual prerequisite code, and every required step/full command log in exact-merge runs 39302343644 (`6154b745ed56c819cad179daa61d0ba606bede3b`) and 39431345348 (`2aa8d2be362c86c3d8288f757b852bc98a867b2e`), attempt 1 each. All 12 cells in each passed metadata/lock, lint/format, tests, Bandit, fresh builds/Twine and both independent installs. Thread 03: Linux/macOS 220 passed, Windows 219 passed/1 skip. Thread 06: Linux/macOS 517 passed, Windows 506 passed/11 expected skips. Baseline `b75fb19` differs from the accepted Thread 06 merge only in acceptance documentation; runtime/tests/package inputs match. Historical failures remain historical. No new prerequisite blocker. Windows sf execution remains refused.

Material decisions recorded before dependent implementation:

- Exactly two known assets: `apex_created.md.j2` (new human body) and `apex_generated.md.j2` (generated facts/coverage/reciprocal references). Read defaults through importlib.resources. Explicit absolute override root only; known missing files fall back, invalid existing files/root/read failures refuse. Reject links/reparse points, multiply linked/special files, traversal and changed read identities; inspect known paths only.
- Use Jinja2 with StrictUndefined, an immutable restricted sandbox, empty globals/tests/loader and explicit filters. Support only bounded text plus named section interpolation: no loops, calls, arithmetic, attributes, indexing, includes/imports/macros or arbitrary expressions. Required sections appear exactly once. The context contains only engine-produced primitive strings, with no model objects, IDs, raw data or helpers. This deliberately finite grammar prevents template-driven amplification; sandboxing alone is not a resource-security guarantee.
- The engine constructs flat YAML using JSON scalar/list encodings (a YAML-compatible subset), validates the complete exact new envelope and owns caller-provided canonical UUID/schema/allowlisted sf_* properties and marker lines. No general YAML parser or ruamel.yaml dependency is needed here; existing-note YAML preservation stays Thread 08. Creation initializes the three required human sections and null technical_debt; explicit user defaults remain user-owned.
- Portable paths use validated namespace directories and full-name filenames, with conservative NFC/casefold, prefix/file-directory and reserved-name collision refusal; explicit managed paths alone authorize link targets. Labels are escaped separately from path grammar; no new notes for unsupported/unresolved/external/unmapped endpoints. Graph evidence includes method, coverage and staleness without record/org IDs.
- Bound template bytes (16 KiB each), AST nodes (256), primitive input text (4 KiB each), total input (2 MiB), mappings/components (10,000), incident edges (2,000), path depth/length, context (512 KiB), generated/body output (512 KiB each), and complete note (1 MiB). Fail with redacted typed errors before accepting any candidate; no truncation.
- Reuse unchanged source/graph/render/creation hashes. Generated-template and incident/path changes invalidate generated output; creation changes affect new candidates only. No incidental dates or identity generation. Hashes never authorize overwriting edits.

Official Jinja API/sandbox/changelog and publisher package metadata reviewed: https://jinja.palletsprojects.com/en/stable/api/ , https://jinja.palletsprojects.com/en/stable/sandbox/ , https://jinja.palletsprojects.com/en/stable/changes/ , https://pypi.org/project/Jinja2/ . Add the rendering dependency through Poetry, retaining its generated lock. No local/vendor_docs directory is present.

Only internal candidate rendering is authorized. No existing-note parser, discovery/adoption, state loading, planner, publication/recovery, public lifecycle, real sf/Obsidian/auth/org/vault or transport expansion. Runtime tests remain synthetic/offline. Changes remain unstaged/uncommitted; Threads 08–17 and enhancement #18 remain NOT STARTED.

**Thread 07 coverage invalidation clarification, before note implementation:**
The accepted generated fingerprint takes source/graph/template inputs; component
source hashes deliberately exclude coverage, while the accepted per-note graph
fingerprint includes relationship coverage only. Rendering all three independent
coverage records therefore needs a renderer-local composition: hash the accepted
per-note graph fingerprint together with full normalized Coverage, then supply
that digest as the existing render helper's graph input. Retain the original graph
fingerprint separately on the candidate. This preserves every existing helper and
source/graph contract while preventing inventory/audit-only coverage changes from
leaving generated output falsely unchanged. No state format/loading or planner is
introduced; a later consumer must retain the candidate's generated render hash.
### Thread 07 progress — 20 October 2026

Internal rendering is implemented, with 101 new synthetic cases and **618 passed/no skips** locally on macOS ARM64 / Python 3.14.7. Strict Poetry metadata/lock, Ruff lint/format and Bandit pass. No source/transport behavior or existing hash helper contract changed.

The finite interpolation-only Jinja contract, engine-owned flat YAML/UUID/markers, required human/generated sections, audit omission/availability, reciprocal graph provenance/staleness, explicit link mappings and conservative namespace/path collisions are tested. Independent YAML parsing also verifies Unicode and keys such as `null`/`false`. Template defaults are installed resources; invalid existing overrides refuse rather than fall back.

Coverage invalidation clarification recorded in the roadmap before note implementation: retain the accepted per-note graph fingerprint separately; compose it with complete independent Coverage for the existing render helper's graph input. This catches inventory/audit-only changes without changing source/graph/helper contracts. Creation-template edits affect only the new-note creation hash.

Fresh wheel/sdist build and strict Twine passed. Exact archive/license/source/resource inspection and **both independent clean installations outside the checkout passed**, including full candidate-byte comparison, override/fallback, stale/incoming/move/hash/privacy checks, both entry points, unchanged source checks and no cwd artifacts. Runtime sockets/process launches are blocked; setup/downloads use the network. The first installed probe exposed a test-harness newline escape error; it was fixed without changing runtime code and both installs then passed. Final guard/portable-LF probe tightening is being rechecked before handoff. Archive allowlists now contain 26 wheel / 25 sdist members.

Hosted evidence remains prerequisite-only: no hosted Thread 07 or native Linux/Windows/Python 3.15 rendering qualification is claimed. One new POSIX unsafe-link fixture is explicitly skipped on Windows; reparse refusal is separately synthetic, never native qualification. Real sf/Obsidian/auth/org/vault access is not used. Requested platform relationships remain partial/unavailable, including clean empty results; offline relationships remain not collected. Windows sf execution remains refused.

Docs/changelog and roadmap are synchronized. All changes remain unstaged/uncommitted on the existing Thread 07 branch. #7 stays OPEN pending maintainer acceptance; no delivery/merge/release gate is checked. Threads 08–17 and enhancement #18 remain NOT STARTED.

### Thread 07 handoff — 20 October 2026

**Implemented locally; #7 stays OPEN pending maintainer acceptance, delivery and exact-commit hosted validation.** Only Thread 07 was implemented. All changes remain unstaged/uncommitted on the existing Thread 07 branch at baseline `b75fb1988e59920b709be7013ddc8a49871d4b27`. No stage, commit, push, PR, merge, CI rerun or publication occurred.

**Prerequisites:** Before coding, rechecked accepted/closed #3/#6, actual prerequisite source and every required step/full log in exact-merge runs `39302343644` / `6154b745ed56c819cad179daa61d0ba606bede3b` and `39431345348` / `2aa8d2be362c86c3d8288f757b852bc98a867b2e`, attempt 1 each. All 12 cells per run passed applicable checks/builds/Twine/both installs; actual Windows skips and historical failed runs remain distinct. Current baseline differs from the accepted #6 merge only in acceptance docs. No new prerequisite blocker.

**Changes:** Added `renderer/templates.py`, `renderer/notes.py`, two installed Jinja assets and a reviewed synthetic new-note fixture. Creation and generated rendering remain separate; the engine owns caller-supplied persistent UUID/schema, exact reserved flat YAML and marker envelope. Templates use bounded interpolation-only Jinja with strict undefined/sandbox/explicit filter and primitive serialized sections. Known explicit overrides precede defaults; absent files fall back, invalid existing files/roots and unsafe links fail. Unsafe paths, case/Unicode/namespace collisions, marker/ownership injection and excessive input/template/output fail before acceptance. Required human sections initialize with null debt; user-owned defaults retain explicit null/false/empty distinctions. Missing/null/unavailable audits are explained and unknown values omitted; privacy omission excludes audit names. Directed graph reciprocal views preserve method/coverage/staleness; only exact mapped supported endpoints become links. No body/org/record ID/raw endpoint projection.

**Recorded decisions:** Material grammar/context/loading/serialization/path/bounds choices were recorded before implementation. The finite subset intentionally excludes general Jinja loops/calls/expressions/imports and model objects; sandboxing alone is not resource isolation. Standard-library JSON-compatible flat YAML avoids a runtime YAML parser. Poetry generated the Jinja2 `>=3.1.6,<4` lock addition (3.1.6, transitive MarkupSafe 3.0.4) after official contract review. Existing source/graph/render/creation helpers are unchanged. The candidate keeps the accepted per-note graph digest separately and composes it with independent full Coverage for the existing render helper's graph input, catching audit/inventory-only invalidation. Creation changes affect new candidates only; hashes never authorize overwrites.

**Verified checklist:**

- [x] All four implementation tasks and deterministic candidate acceptance scenario, including installed resources outside checkout/cwd, completed locally.
- [x] 101 new synthetic rendering/security/availability/graph/path/template tests, including incoming-only/moved-target invalidation without source-hash changes; full suite **618 passed, no skips** on macOS 27.0.1 ARM64 / Python 3.14.7 / Poetry 2.4.2.
- [x] Strict metadata/lock, Ruff lint/format (66 files), Bandit and whitespace passed; no new scanner suppressions/findings. Existing five transport/query annotations remain. Coverage run: 95% overall, notes 90%, templates 93%; gaps remain visible.
- [x] Final fresh r2 wheel/sdist build, strict Twine, exact 26/25-member archive lists, unchanged Apache license and current packaged source/resource bytes passed.
- [x] Both final independent clean Python 3.14.7 installs outside the checkout passed dependency consistency, imports/resources, complete synthetic candidate-byte comparison, overrides/fallback, stale/incoming/moved-path/hash/privacy checks, console/module entry points, offline preservation and no cwd writes. Runtime socket/process guards explicitly verified active. Network used only for setup/build/dependency acquisition.
- [x] README/contributor/config/coverage/note/offline/live/relationship/rendering docs, changelog, roadmap status/index/decisions and handoff synchronized; changed Python headers retain Created By and requested GPT-6.1 Sol / 20 Oct 2026 attribution.
- [x] Frozen model/config/source/parser/graph/CLI code and Apache license unchanged from the accepted merge; no offline/transport broadening.
- [ ] Maintainer acceptance, delivery and exact-commit hosted Thread 07 validation.
- [ ] Ready to merge / release acceptance gate; publication requires separate authorization.

**Final r2 artifacts (temporary, not published):**

| Artifact | SHA-256 |
| --- | --- |
| Wheel | `4e567b4931328f3bc4c6574a316a55bd1ec890af843dfd35c3d6aa63db31160c` |
| Sdist | `1825e449877f80a27f8443663f69aabdd828b758b21b6637e0d3e6f5cd697936` |

The first installed rendering probe failed on an escaped-newline error in the test-only harness; it was corrected and both independent installs passed. Final portable-LF/active-guard tightening was then verified in both final installs. Earlier local runs/build attempts remain historical evidence, not relabeled successes.

**Limits:** No hosted Thread 07, native Linux/Windows rendering, or local Python 3.12/3.13/3.15 execution was performed. One new POSIX unsafe-link fixture is expected to skip on Windows; reparse checks remain synthetic. Prerequisite Windows mock/refusal/installed results do not qualify Windows sf execution. No real sf/Obsidian/credentials/.env/auth discovery, CLI/plugin installation/update, org/metadata/vault access or private upload. Platform requested relationship coverage remains partial/unavailable because the allowlist cannot establish exhaustion, including clean empty results; offline remains explicitly not collected. No existing-note parser/patcher, discovery/adoption, state loading, planner, publication/recovery or public lifecycle command. Override reads require a stable local tree; no hostile filesystem race or OS resource isolation guarantee.

**Tracking/Git:** Existing #7 labels, assignee, v0.1.0 milestone and reciprocal native #3/#6 → #7 → #8/#10 links are preserved. No duplicate issue, other chat or subagent was created. There are 23 intentional changed/new files, all unstaged/uncommitted; no application working-directory artifacts. The issue's implementation/test/docs/compatibility checklist is verified, with acceptance/readiness left unchecked.

**Next eligible after Thread 07 acceptance/delivery verification and a new request: Thread 08 / #8, explicitly NOT STARTED. Threads 08–17 and enhancement #18 remain NOT STARTED.**
### Thread 07 acceptance and closure — 20 October 2026

**Accepted and complete.** The maintainer reviewed/pushed Thread 07, confirmed passing CI and authorized closure if complete. Actual implementation, delivery identity and all hosted gates are verified. #7 is closed as completed; Thread 08 is next eligible and remains **NOT STARTED**. No release/publication is implied.

**Delivered identity:** Implementation `b4658eb0f878c71698e580801c118733a16b86df`, merged at `eedeff425bcd4921bef8756412826ce5a93b0165`. Clean local main and live GitHub main matched the merge before this acceptance update. Implementation and merge trees are identical. All 21 packaged Python/resource files match the reviewed final r2 wheel bytes; no maintainer changes were discarded. All four Thread 07 tasks and the deterministic installed-candidate acceptance scenario are met.

**Exact-commit hosted evidence:** Inspected every job, required step and full command log in [run 39440606470, attempt 1](https://github.com/jeffshurtliff/obforce/actions/runs/39440606470), head `eedeff425bcd4921bef8756412826ce5a93b0165`:

| Cells | Verified outcome |
| --- | --- |
| Linux/macOS, Python 3.12–3.15 (8) | **618 passed per cell, no skips**; 95% combined statement/branch coverage |
| Windows, Python 3.12–3.15 (4) | **606 passed, 12 expected skips per cell**; 93% combined coverage |
| Every cell | Standalone strict metadata/lock, Ruff lint/format (66 files), Bandit, fresh wheel/sdist build, strict Twine, exact archive/license/source/resource inspection, both independent artifact installs and whitespace passed |

All **24 independent artifact installations** passed dependency/import/resource/model/entry-point checks, complete synthetic candidate-byte comparison, template override/fallback, graph/stale/incoming/moved-path/hash/privacy probes, offline preservation and no cwd artifacts. Runtime socket/process guards were active; setup/build downloads remain separate network use. Every required step ran successfully with no masked formatter/test failure. The existing five narrow transport/query Bandit annotations remain; no new finding/suppression was added. Historical failed runs and earlier local installed-probe newline failure remain recorded with their original outcomes.

The 12 Windows skips are nine POSIX collector cases, one POSIX wrapper-symlink case, unavailable FIFO case and POSIX unsafe-template-link fixture. Synthetic reparse/refusal and native hosted candidate/install results do **not** qualify Windows sf execution. Linux/macOS fictional child-process tests executed; no real sf/Node/plugin/auth/org/vault/Obsidian capability follows. Read-side template checks require a stable trusted tree; no hostile filesystem race or OS resource isolation guarantee is claimed. The finite interpolation-only Jinja contract is unchanged.

**Preserved boundaries:** Source/graph/render/creation helper contracts, engine-owned UUID/schema/reserved properties/markers, separate creation/generated paths, absent/null/false/debt/privacy behavior and renderer-local graph-plus-independent-Coverage composition remain as reviewed. Requested platform relationships stay partial/unavailable because exhaustion cannot be established under the allowlist, including clean empty results; offline relationships remain not collected. No new collection/transport, public lifecycle, existing-note parser/patcher, state/discovery/adoption/planner/publication/recovery or additional note type. Enhancement #18 remains outside v0.1.0 and is not a prerequisite.

**Verified acceptance gates:**

- [x] All original Thread 07 implementation tasks and synthetic candidate/resource/override/escaping/bounds acceptance criteria met.
- [x] Maintainer review/push, implementation/merge tree identity and exact reviewed candidate source/resource bytes verified.
- [x] All 12 exact-merge hosted suites and required standalone checks, fresh builds/Twine and 24 independent installs passed; actual Windows skips retained.
- [x] Frozen source/transport/hash/ownership/privacy/coverage and Apache licensing preserved; Poetry-generated Jinja2/MarkupSafe lock addition accepted with the delivered increment.
- [x] Maintainer authorized closure; existing issue checklist, current docs, roadmap status/index/acceptance and exact Thread 08 prompt synchronized.

**Docs/Git/tracking/handoff:** Updated roadmap current/index/thread status and acceptance record, exact Thread 08 kickoff/eligibility, contributor/rendering/relationship guidance and changelog. Earlier start/progress/local handoff records are historical, including their then-pending hosted evidence. This acceptance update is prose-only: local link/anchor/fence/consistency/privacy/whitespace and tracked/untracked diff review passed. No application tests/builds/dependency installations were rerun. Five documentation files remain unstaged/uncommitted on main at `eedeff4`; implementation is delivered. No stage/commit/push/PR/merge/tag/CI rerun/release/publication/real Salesforce/auth/vault access, other chat, subagent or later-thread implementation occurred.

Existing #7 enhancement/codex/maintainer labels, assignee, v0.1.0 milestone and reciprocal native #3/#6 → #7 → #8/#10 links are preserved. #8 remains open/not started with direct prerequisite #7; no duplicate issue or new prerequisite is introduced. **Next eligible: Thread 08 / #8 under a new request, explicitly NOT STARTED. Threads 08–17 and enhancement #18 remain NOT STARTED.**

### Thread 08 start and decisions — 20 October 2026

Started under the explicit maintainer request; #8 remains OPEN pending acceptance.
Before code, rechecked #8 and direct prerequisite #7 (accepted/closed), its linked
#3/#6 records, native prerequisite links, actual renderer/model/source inputs and
all jobs, required steps and full command logs in run `39440606470`, attempt 1,
head `eedeff425bcd4921bef8756412826ce5a93b0165`. All 12 cells passed: Linux/macOS
618 each; Windows 606 passed/12 expected skips each. Every standalone lock/lint/
format/Bandit/build/Twine/archive/both-install/whitespace gate passed. Implementation
`b4658eb` and merge trees match; current `761beb8` differs only in acceptance docs.
Historical failures and earlier local probe failures retain their original status.
No new prerequisite blocker. No `local/vendor_docs/` directory is present.

Material contract recorded before dependent implementation:

- Internal caller-supplied immutable UTF-8 bytes, validated in-memory NoteState and
  accepted Thread 07 GeneratedCandidate only. No filesystem reads/writes, discovery,
  adoption, state loading, identity/move reconciliation, planner or lifecycle command.
- Add `ruamel.yaml` through Poetry using the publisher's available current release;
  record the actual resolved version/constraint after resolution. Use a fresh pure
  Python `YAML(typ='rt')` per parse, duplicate keys disabled, quotes preserved. Its
  round-trip API derives from the safe loader, without arbitrary Python constructors.
  Reject all explicit tags/directives, anchors, aliases and merge keys before load.
- One initial `---` line and one exact closing `---` line; no BOM, preamble, bare CR,
  NUL or invalid UTF-8. Root is an implicit block mapping with simple string keys.
  Support flat string/null/boolean/64-bit integer/finite float/date/datetime user
  scalars and lists of strings, flow/block lists, comments, order, quoted/plain and
  literal/folded multiline strings. Refuse nested/complex keys/maps/lists, custom
  tags, sets, binary, nonfinite values and unsupported forms without coercion.
- Finite refusal limits: note/output 1 MiB; frontmatter/output 64 KiB; 128 properties;
  8,192 scanner tokens; 4,096 parse nodes; depth 2 (root map plus flat sequence);
  scalar text 16 KiB and lists 1,024 items. Check before constructing YAML objects;
  no alias/merge expansion. Byte, token, event and output bounds are independent.
- Preserve supported user YAML bytes through round-trip parser source-span splices,
  not whole-document dumping. Replace changed owned values with JSON-compatible
  flat YAML; retain comments from changed spans as standalone comment lines if
  necessary. Delete omitted owned keys, retaining their comments. Append newly
  available owned keys deterministically. Reparse/validate the entire result and
  verify unchanged user values before returning. Changed owned presentation can
  normalize; no promise of universally byte-identical frontmatter.
- Validate canonical persistent UUID, integer schema 1 and exact owned allowlist;
  unknown sf_* names, identity/schema edits and invalid structures are conflicts.
  Validate exactly one ordered marker pair at column zero on separate lines;
  any other obforce: occurrence is ambiguous and refused. Preserve marker bytes.
- Compare BOTH strict FieldValue owned-property baselines (absent/null/false/empty
  remain distinct) AND exact generated-interior bytes with caller-supplied saved
  bytes and NoteState SHA-256, before accepting even a hash-matching incoming update.
  Identity/schema/source-key mismatch refuses; hashes never override edited content.
- Frontmatter and marker/interior endings must each be uniform LF or CRLF and agree
  within those generated boundaries; refuse mixed frontmatter/interior endings.
  Human body may mix LF/CRLF and is preserved exactly. Incoming LF region is adapted
  to the existing marker ending; save/hash the resulting exact bytes. A true no-op
  returns the original bytes object, regardless of hash/template presentation changes.
- All nonreserved properties remain user-owned, including every technical_debt*
  value, review date, tags, aliases and type. Do not infer assessments or defaults.
  Candidate audit omission removes owned keys without inventing nulls. Creation
  templates never participate. Retain all accepted source/graph/render/creation
  contracts and independent-Coverage composition; no transport/collection change.
- Invalid managed content/baseline edits use redacted ConflictError (exit 3); invalid
  caller/candidate contracts use ModelError (exit 2). No raw content, paths or parser
  diagnostics in displayed errors; existing outcome precedence is unchanged.

Official contracts checked on 20 October 2026:
[ruamel round-trip API](https://yaml.dev/doc/ruamel.yaml/api/),
[preservation details](https://yaml.dev/doc/ruamel.yaml/detail/),
[publisher metadata](https://pypi.org/project/ruamel.yaml/),
[YAML 1.2.2](https://yaml.org/spec/1.2.2/) and
[Obsidian properties](https://obsidian.md/help/properties).
Runtime tests remain offline/synthetic; setup/dependency acquisition can use network.
Windows sf execution remains refused; platform relationships remain partial/unavailable,
including empty results, and offline relationships not collected. No real Salesforce,
Obsidian, credentials, metadata or vault access. Changes stay unstaged/uncommitted;
Threads 09–17 and enhancement #18 remain explicitly NOT STARTED.


**Thread 08 dependency/line-ending clarification:** Poetry resolved
`ruamel-yaml >=0.19.1,<0.20.0` to 0.19.1, without optional C extensions. The first
restricted-network resolver attempt failed; the authorized network-enabled Poetry
retry generated the lock and installed successfully. Frontmatter and marker/interior
envelopes are each uniform, independently LF or CRLF; they may differ from each
other. Mixed human body endings are opaque/preserved. Structural depth 2 is enforced
by events; ruamel's additional guard is 3 because it also counts scalar leaves.
The initial local parser probe exposed that distinction and was corrected before
all 96 focused synthetic tests passed. No prerequisite or scope blocker was found.
### Thread 08 progress — 20 October 2026

The internal parser/patcher and synthetic fixtures are implemented. Full local suite: **744 passed, no skips**, macOS ARM64 / Python 3.14.7 / Poetry 2.4.2, including **126 new preservation cases**; combined coverage 95%, sync/notes 94%. Strict Poetry metadata/lock, Ruff lint/format (71 files), Bandit and whitespace passed. Existing five narrow transport/query scanner annotations remain; no new findings/suppressions.

Both strict property and exact-byte region baselines gate patches, independent of incoming hashes. Safe-derived pure round-trip YAML uses bounded scanner/events and exact source spans; unknown reserved keys, tags/references/merges, duplicate/complex/nested structures, malformed markers, identity/schema edits and excessive inputs/outputs refuse with redacted typed diagnostics. Supported custom YAML, comments/order/quotes/multiline/Unicode, user prose, technical-debt absence/null/false and review decisions survive; CRLF outputs return exact adapted-byte baselines. No-op returns original bytes. Audit omission/privacy and creation-only template changes are tested.

Extended edge probes found block-scalar header comments use a different round-trip token representation and indentless lists need an indentation adjustment when replaced by scalar values. Both are handled and now covered in LF/CRLF regressions. An intermediate local edit accidentally classified scalar tokens as forbidden; that local test run failed, was corrected, and all 744 tests subsequently passed. Initial parser depth and restricted-network setup/build failures remain historical, not relabeled successes.

Poetry resolved/locked `ruamel-yaml >=0.19.1,<0.20.0` to 0.19.1 without optional C extensions. Fresh r2 wheel/sdist build and strict Twine passed; exact allowlists deliberately include both sync modules. Independent installed probes are in progress with synthetic byte snapshots, active runtime network/process guards and no cwd artifacts. Setup/build/dependency downloads may use network.

Docs/changelog/roadmap are synchronized. Accepted source/graph/render/creation helpers, renderer-local graph-plus-independent-Coverage composition, source/transport behavior and Apache licensing remain unchanged. Platform relationships remain partial/unavailable, including clean empty results; offline remains not collected. Windows sf execution remains refused. No real sf/Obsidian/auth/org/vault/private-data access or public lifecycle/state/discovery/adoption/planner/publication/recovery.

#8 stays OPEN pending maintainer acceptance and new exact-commit hosted evidence. Work remains unstaged/uncommitted; no CI rerun or delivery action. Threads 09–17 and enhancement #18 remain explicitly NOT STARTED.

### Thread 08 handoff — 20 October 2026

**Implemented locally; #8 remains OPEN pending maintainer acceptance, delivery and exact-commit hosted validation.** Only Thread 08 was implemented. All 17 changed/new files remain unstaged/uncommitted on main at baseline `761beb8`. No stage, commit, push, PR, merge, CI rerun, package upload or publication occurred.

**Prerequisites:** Before implementation, rechecked #8, accepted/closed #7 and its linked #3/#6 prerequisites, native dependency links, actual source/model/render inputs, implementation `b4658eb0f878c71698e580801c118733a16b86df` / merge `eedeff425bcd4921bef8756412826ce5a93b0165` tree identity, and every job/required step/full command log in run `39440606470`, attempt 1 at that merge. All 12 cells passed standalone gates/builds/Twine/both installs: Linux/macOS 618 passed each; Windows 606 passed/12 expected skips each. Current baseline changes only acceptance docs. No new prerequisite blocker; no vendor-doc directory. Historical failed runs/local probes retain their actual outcomes.

**Changes and acceptance behavior:** Added internal `sync/notes.py` and its package header, finite parsing constants, 126 synthetic regression cases and two fictional hand-edited/expected note fixtures. The parser accepts caller-supplied immutable bytes only; the patcher requires validated in-memory NoteState, exact saved region bytes and an accepted GeneratedCandidate. Canonical persistent UUID/integer schema, frozen reserved allowlist and exact ordered marker pair are validated. Both strict property values and exact generated-body bytes must match saved baselines before patching, regardless of incoming hashes. Identity/source-key/schema edits, malformed markers/frontmatter, unknown sf_* properties, duplicate/complex/nested YAML, explicit tags/references/merges, unsupported types and excessive input/output refuse with concise redacted typed failures. No identity invention, adoption, rename inference, force mode or fallback repair.

Pure round-trip YAML source spans replace only clean owned values/omitted entries and marker interiors. Supported user YAML values/comments/order/quotes/multiline/Unicode, custom type/tags/aliases/business fields, every technical_debt* value and review decision survive. Changed/deleted owned entries can normalize representation or retain their comments as standalone lines; no whole-note creation template or YAML dumping. Exact marker/outside-body bytes and no-op original bytes survive. Uniform LF/CRLF envelopes are independent, mixed generated/frontmatter envelopes refuse, and mixed human endings remain opaque. Returned body baselines/hash cover actual adapted bytes, including CRLF. Audit omission removes keys per the accepted candidate contract; privacy and absent/null/false/empty distinctions remain intact. No hashes/helper semantics changed.

**Recorded contract/dependency:** Supported YAML/forms, safe-derived round-trip API, official sources, encoding/endings/marker rules, baseline comparisons and finite byte/property/token/node/depth/scalar/list/output limits were recorded before dependent implementation. Poetry generated `ruamel-yaml >=0.19.1,<0.20.0`, locked 0.19.1 without optional C extensions. No lockfile hand-edit or unrelated dependency update. Precise round-trip limits are documented in NOTE_FORMAT; no universal YAML, OS resource isolation or frontmatter byte-identity promise.

**Verified checklist:**

- [x] All four original implementation tasks and synthetic audit-update/preservation/conflict acceptance scenario completed locally.
- [x] Full final suite **744 passed, no skips**, including **126 new** preservation cases; macOS 27.0.1 ARM64 / Python 3.14.7 / Poetry 2.4.2. Combined coverage 95%; sync/notes 94%; uncovered defensive paths remain visible.
- [x] Strict Poetry metadata/lock, Ruff lint/format (71 files), Bandit and whitespace passed. No new scanner findings/suppressions; five existing source/transport query annotations remain. New/untracked files were independently whitespace-checked too.
- [x] Fresh r2 wheel/sdist build, strict Twine and exact **28 wheel / 27 sdist** member/license/source/resource inspection passed; both sync modules deliberately allowlisted.
- [x] Both final independent clean Python 3.14.7 installs outside checkout/cwd passed dependency/import/resource/model/entry-point/source/graph/render checks and complete expected preservation output, CRLF baselines/no-op, custom YAML/debt/comments, conflicts and unsafe-input refusal. Runtime socket/process guards explicitly active; no cwd artifacts. Setup/build/dependency downloads use network only outside runtime probes.
- [x] Docs/changelog/roadmap status/index/start/progress/contracts/handoff and #8 checklist synchronized; frozen model/config/errors/source/parser/graph/renderer/resource/CLI code and Apache license unchanged. All changed/new Python headers use requested GPT-6.1 Sol / 20 Oct 2026 attribution.
- [ ] Maintainer acceptance, delivery and exact-commit hosted Thread 08 validation.
- [ ] Ready to merge / release acceptance gate; separate authorization required for delivery/publication.

**Final r2 artifacts (temporary; not published):**

| Artifact | SHA-256 |
| --- | --- |
| Wheel | `dba4ff5842afaadce192cfbce4a4acd941f94caed43972529b3a4a7e7674df20` |
| Sdist | `cb8ca01bd813e3c975e4d722ce4b2c2082e6b8ac86dc54efdb62d7d48af11e72` |

Initial restricted-network Poetry/build/install attempts failed during setup, then authorized network-enabled retries passed. The initial depth probe exposed ruamel counting scalar leaves; intermediate block-comment/indentless probes exposed supported-form gaps. Those gaps and an intermediate scalar-token classification edit were corrected; their failed local outcomes remain historical. All final gates above passed. A final fixture whitespace cleanup moved deliberate trailing-space input construction into a test; focused tests and both independent installed probes then passed again. No application behavior was weakened to clear a check.

**Limits and preserved boundaries:** No hosted Thread 08, native Linux/Windows preservation run or local Python 3.12/3.13/3.15 execution was performed. Prerequisite Windows skips/refusals and synthetic reparse checks do not qualify Windows sf execution, which remains refused. Requested platform relationships remain partial/unavailable because exhaustion cannot be established, including clean empty results; offline relationships remain not collected. Accepted source/graph/render/creation helpers and renderer-local graph-plus-independent-Coverage composition are unchanged. Candidate source-binding/selection provenance remains the caller's responsibility; hashes are not authentication. No public lifecycle, vault/note discovery/adoption, state loading, identity/move reconciliation, batch planner, filesystem publication, locking, journal or recovery. No real sf/Obsidian/auth/credential/.env/org/metadata/vault access, CLI/plugin installation/update, private upload, other chat or subagent.

**Tracking/Git/next:** Existing #8 labels, assignee, v0.1.0 milestone and native #7 → #8 → #9/#10 links preserved; no duplicate tracking issue. All implementation/test/docs/compatibility gates are checked locally, readiness/acceptance remain unchecked and #8 remains OPEN. Reviewable diff and untracked files inspected; all 17 files unstaged/uncommitted. Next eligible after Thread 08 acceptance/delivery verification and a new request: **Thread 09 / #9, explicitly NOT STARTED. Threads 09–17 and enhancement #18 remain NOT STARTED.**

### Thread 08 acceptance and closure — 20 October 2026

**Accepted and complete.** The maintainer reviewed/pushed Thread 08, confirmed passing CI and requested issue closure if appropriate. All implementation, delivery and hosted gates are verified; #8 is closed as completed. Thread 09 is next eligible and remains **NOT STARTED**. No release/publication is implied.

**Delivered identity:** Implementation `d79f5e2a1a8ddb7b5c00857c2cfe73556e96586e`, merged at `dba53abdeae578789739f19d1b0366ad72feda00`. Clean local main and live GitHub main match that merge before this acceptance update; implementation/merge trees are identical. All 23 packaged Python/resource files match the reviewed final r2 wheel bytes. Maintainer dependency-list formatting and the development-only `certifi` lock refresh from 2026.10.18 to 2026.10.19 are retained and covered by the exact-merge metadata/lock/install checks. No maintainer changes were discarded. All four Thread 08 tasks and the synthetic audit-update/preservation/conflict acceptance scenario are met.

**Exact-commit hosted evidence:** Rechecked every job, required step and full command log in [run 39453887153, attempt 1](https://github.com/jeffshurtliff/obforce/actions/runs/39453887153), head `dba53abdeae578789739f19d1b0366ad72feda00`:

| Cells | Verified outcome |
| --- | --- |
| Linux/macOS, Python 3.12–3.15 (8) | **744 passed per cell, no skips**; 95% combined coverage |
| Windows, Python 3.12–3.15 (4) | **732 passed, 12 expected skips per cell**; 93% combined coverage |
| Every cell | Standalone strict metadata/lock, Ruff lint/format (71 files), Bandit, fresh wheel/sdist build, strict Twine, exact archive/license/source/resource inspection, both independent installs and whitespace passed |

All **24 independent artifact installations** passed dependency/import/resource/model/entry-point/source/graph/render checks plus complete expected preservation output, exact CRLF baselines/no-op, user YAML/debt/comments, generated-edit conflicts and unsafe-input refusal. Runtime socket/process guards were explicitly active and no cwd artifacts appeared. Setup/build/dependency downloads remain separate network use. All required steps ran without masked failures. No new Bandit findings/suppressions; the five existing narrow query/transport annotations remain. Historical failed CI and local depth/comment/list/token/setup/probe failures keep their original outcomes; the start/progress/local handoff records remain historical.

The 12 Windows skips remain nine POSIX collector cases, one POSIX wrapper-symlink case, the unavailable FIFO case and POSIX unsafe-template-link fixture. Synthetic reparse/refusal and native hosted parser/patcher/installed results do **not** qualify Windows sf execution. No real Salesforce/Obsidian/auth/org/metadata/vault access was used. Finite supported YAML parsing is not universal YAML or OS resource isolation, and future read-side filesystem safety does not establish publication safety.

**Preserved contracts:** Canonical persistent UUID/integer schema/exact reserved allowlist, exact marker boundaries, both saved strict property and exact-byte region baselines, no-force refusal, user ownership/debt/privacy/absence distinctions, supported source-span preservation and no-op bytes are accepted as delivered. LF/CRLF envelope policy and exact adapted-byte output baselines remain explicit. Creation templates never replace existing notes. Source/graph/render/creation helper contracts and renderer-local graph-plus-independent-Coverage composition are unchanged. Requested platform relationships stay partial/unavailable because exhaustion cannot be established, including clean empty results; offline remains not collected. No state loading/discovery/adoption/identity reconciliation/planner/publication/locking/journal/recovery or public lifecycle was added. Windows sf remains refused; #18 remains outside v0.1.0 and is not a prerequisite.

**Verified acceptance gates:**

- [x] All four Thread 08 implementation tasks and synthetic preservation/conflict acceptance criteria met.
- [x] Maintainer review/push, implementation/merge tree identity and all reviewed packaged source/resource bytes verified.
- [x] All 12 exact-merge hosted suites and standalone checks, fresh builds/Twine/archive inspection and 24 independent installs passed; actual Windows skips retained.
- [x] Accepted ownership/privacy/hash/source/coverage/transport and Apache contracts preserved; delivered dependency/lock inputs verified.
- [x] Maintainer authorized closure; #8 checklist/current status, current docs, roadmap status/index/acceptance and exact Thread 09 prompt synchronized.

**Docs/Git/tracking/handoff:** This acceptance update changes six documentation files only, with local link/anchor/fence/consistency/privacy/whitespace and diff/untracked review. No application tests/builds/dependency installs were rerun; hosted evidence above validates the delivered application. Docs remain unstaged/uncommitted on main at `dba53ab`; implementation is delivered. No stage/commit/push/PR/merge/tag/CI rerun/release/publication, real Salesforce/auth/vault access, other chat, subagent or later-thread implementation occurred. Existing #8 labels, assignee, v0.1.0 milestone and native #7 → #8 → #9/#10 links are preserved; #9 remains open/not started with direct prerequisite #8, without duplicate tracking. **Next eligible: Thread 09 / #9 under a new request, explicitly NOT STARTED. Threads 09–17 and enhancement #18 remain NOT STARTED.**


### Thread 09 start and contract — 20 October 2026

Only Thread 09 is started, under explicit maintainer authorization. Rechecked #9,
its native #8 prerequisite and #10 dependent, accepted #8 and linked #7/#3/#6
records, actual immutable models, parser, renderer and graph contracts. Exact
implementation d79f5e2 / merge dba53ab trees match; current c3a5402 changes only
acceptance docs. Every job, required step and full command log in run 39453887153,
attempt 1 at dba53ab was rechecked: Linux/macOS 744 passed per cell, Windows 732
passed/12 expected skips per cell; all 12 standalone gates, fresh builds/Twine,
archive checks and 24 independent installs passed. No new prerequisite blocker.
Vendor-doc directory absent; GitMCP returned no documentation; authenticated gh
provided issue/log evidence after an initial restricted-network failure. Prior
failed CI/local setup/parser/probe outcomes remain historical.

Before dependent code, recorded the exact wire/minimum-fields, saved exact-byte
baseline envelope, binding/selection/coverage, deterministic encoding, discovery
indicators/exclusions/empty-state/moves/conflicts, filesystem assumptions and all
finite limits in [SYNC_SAFETY](../docs/SYNC_SAFETY.md). NoteState and accepted hash
contracts remain unchanged. No dependency addition. No writes/public lifecycle,
batch planner, adoption/migration, transport, locking/journal/recovery. Tests use
synthetic vaults only; all changes stay unstaged/uncommitted and #9 stays open.
Windows sf remains refused; partial/unavailable platform and uncollected offline
relationships unchanged. Threads 10–17 and enhancement #18 explicitly NOT STARTED.


### Thread 09 progress — 20 October 2026

Implemented internal sync/state.py: unchanged immutable NoteState plus exact saved
bytes, strict finite wire validation/serialization, explicit read-only state/vault
inputs, conservative managed indicators, complete bounded discovery, redacted
conflicts and deterministic unique-move path candidates. No source absence or
publication decisions. Added synthetic property/body/identity/schema/source/scope,
links/reparse/special/hard-link, traversal/race/partial-read, portable collision,
empty-state/non-adoption and LF/CRLF regressions. Neighbor graph invalidation uses
both directions and preserves saved source/graph/render hashes. Extended exact
package allowlist and guarded installed parser/state/reconciliation probe.

First focused run: 135 passed, 2 skipped, 4 failures (three test tuple mutations
and missing serialization note-count recheck). Corrected all four. An expanded
run exposed a graph fixture missing its required endpoint ID and discovered-path
errors retaining ModelError; fixed fixture and changed discovered-path refusal to
ConflictError. Subsequent full suite: 910 passed, 2 filesystem-representation
skips, 95% aggregate/94% state coverage. Synthetic case/NFC collision tests pass
independently. An intermediate formatter check failed after a test edit and was
corrected. Further offline-evidence/invalid-text refinements are under final
verification. Metadata/lock, lint, Bandit and whitespace passed; existing scanner
annotations unchanged. Initial fresh r1 build failed during restricted-network
PyPI setup; final fresh build/install verification pending. No failure is relabeled
as a pass; historical prerequisite failures are retained.

#9 remains open pending acceptance; work unstaged/uncommitted. Runtime tests are
offline and synthetic. Windows sf remains refused, requested platform coverage
partial/unavailable even when empty, offline relationships not collected.
Threads 10–17 and enhancement #18 explicitly NOT STARTED.


### Thread 09 handoff — 20 October 2026

**Implemented locally; #9 stays OPEN pending maintainer acceptance, delivery and
exact-commit hosted validation.** Only Thread 09 was implemented. All 14 changed/
new files remain unstaged/uncommitted on main at baseline c3a5402. No stage,
commit, push, PR, merge, tag, CI rerun, package upload or publication occurred.

**Prerequisites:** Before code, read #9, accepted/closed #8 and linked prerequisite
records, native #8 → #9 → #10 links, repository guidance and requested design docs.
Rechecked actual parser/model/renderer/graph code and implementation d79f5e2 /
merge dba53ab tree identity. Every job/required step/full command log in run
39453887153 attempt 1 at that merge passed: Linux/macOS 744 passed per cell,
Windows 732 passed/12 expected skips per cell, all standalone checks, fresh
builds/Twine/archive inspection and 24 independent guarded installs. Current
baseline changes only acceptance docs. No prerequisite blocker. No vendor-doc
directory. Historical failed CI/local/setup/probe outcomes remain historical.

**Changes:** Added internal sync/state.py, finite constants, 173 synthetic test
cases and docs/SYNC_SAFETY.md. Strict version-one UTF-8 JSON uses exact key/type/
schema checks, duplicate-key detection, lexical depth and primitive/node/byte
bounds, canonical sorted deterministic output and canonical base64 exact saved
LF/CRLF generated bytes. The unchanged immutable NoteState and strict generated
property baseline/SHA-256 remain intact. Both current generated values and exact
saved bytes must match; no digest authorizes rebase/overwrite. Unknown/contradictory
state, invalid IDs/hashes/bindings/scope and duplicate IDs/keys/paths refuse.
No human regions or user-owned properties are serialized as baselines.

Explicit bounded read-only state loading and full vault discovery reject unsafe
ancestors, links/junctions/reparse/special files/hard links, portable collisions,
partial scans/read failures and observed file/parent changes. Control directories
are excluded; only the explicit expected state document is read separately.
Conservative obforce/sf_ indicators require valid tracked ownership, including
malformed/edited identities. Ordinary notes remain unadopted. Missing state is
allowed only with explicit initial=True and an empty managed scope; corrupt/empty/
unknown state never establishes ownership. All read/no-op/failure paths preserve
bytes/mtimes/tree. Atime and native/read-race limits are documented honestly.

Unique in-vault UUID moves retain key/content/baselines/prior hashes and change
only candidate paths. Deterministic immutable paths and explicit key/old/new
changes feed existing incoming/outgoing graph and render invalidation. Tests
verify both neighboring directions change fingerprints while source hashes stay
unchanged. No source inventory/absence decision is evaluated; vanished tracked
notes conflict independently of source observation. Exact workspace/local/live/
canonical verified org/selection matches are enforced. Saved independent scope
and coverage evidence remain intact; offline audit unavailable and relationships
not collected. No component is deleted/marked missing or stale edges replaced.
Creation-template behavior and renderer-local graph-plus-independent-Coverage
composition remain unchanged.

**Verified checklist:**

- [x] All four original Thread 09 implementation tasks and unique-move/conflict/non-adoption acceptance scenario completed locally.
- [x] Final full suite **915 passed, 2 skipped**, including **171 passed / 2 skipped new cases**; macOS 27.0.1 ARM64, Python 3.14.7, Poetry 2.4.2. Combined coverage 95%, sync/state 93%; defensive uncovered paths remain visible.
- [x] The two skips are native case/NFC fixture creation on this filesystem; independent synthetic case/NFC collision refusals pass. Native FIFO, symlink/hardlink and injected reparse/read-race tests pass locally; injection is not Windows qualification.
- [x] Strict Poetry metadata/lock, Ruff lint/format (74 files), Bandit and tracked/new-file whitespace checks passed. No new findings/suppressions; five existing narrow source/transport annotations remain.
- [x] Final fresh **r4** wheel/sdist build, strict Twine and exact **29 wheel / 28 sdist** member/license/source/resource inspection passed; sync/state.py deliberately allowlisted. Sdist README/pyproject bytes also match checkout.
- [x] Both final independent clean artifact installs outside checkout/cwd passed dependency/import/resource/model/entry-point/source/graph/render/parser/state/loading/reconciliation probes, exact LF/CRLF baselines feeding patch_note, no-op/moves, edited/copied identity and malicious JSON/path refusal, exact byte/mtime/tree snapshots and no cwd artifacts. Socket/process audit guards explicitly active; setup/build/pip downloads are separate network use.
- [x] Requested docs/changelog/roadmap and existing #9 start/progress/checklist/handoff synchronized. Accepted NoteState/hash/config/errors/source/parser/graph/renderer/CLI/resource code, Poetry metadata/lock, Apache licensing and maintainer changes preserved; no runtime dependency added. All changed/new Python headers retain requested GPT-6.1 Sol / 20 Oct 2026 attribution.
- [ ] Maintainer acceptance, delivery and exact-commit hosted Thread 09 validation.
- [ ] Ready to merge / release acceptance gate; no delivery/publication authorization implied.

**Final r4 artifacts (temporary; not published):**

| Artifact | SHA-256 |
| --- | --- |
| Wheel | `0d1fa2ffffd00d1c80294678bd72d9a331e1af18785bcf86dc5096ffd55d1c07` |
| Sdist | `a30b7da012241f8740ba24e1aa93ecbb81bcebd26ef6932ef2b5867b0ff1ea9e` |

Initial restricted-network GitHub/build/install setup attempts failed; authenticated
network-enabled retries passed. GitMCP returned no docs and the GitHub connector
could not post (403); authorized gh reads/comments succeeded. First test failures
(tuple-mutation fixture, missing serializer note-count recheck, missing graph
endpoint ID and discovered-path error class) were corrected, retaining their
actual failed outcomes. An intermediate formatter failure was corrected. r2/r3
build candidates were superseded after validation/document refinements; r3
install setup failed under restricted network, and archive review found its README
predated the concurrent docs edit. The checker now verifies README/pyproject too.
Final r4 was built after packaged inputs settled and both independent installs
passed. No failed setup/probe is reported as runtime success. Final test review added a
synthetic reserved-name scan and explicit native Windows symlink-privilege/reserved-
fixture skips when those fixtures cannot be created; these are capability gaps,
not qualification evidence. Final full suite then passed 915/2 as recorded above.

**Limits:** No hosted Thread 09 run, native Linux/Windows state run or local Python
3.12/3.13/3.15 run. No live sf/Obsidian/auth/credentials/.env/org/metadata/real-vault
access or CLI/plugin changes. Windows sf stays refused; prerequisite skips and
synthetic reparse results do not qualify execution. Requested platform
relationships remain partial/unavailable because exhaustion cannot be established,
including clean empty results; offline stays not collected. Finite read checks
require a stable trusted local tree and are not hostile race isolation, an atomic
snapshot or publication safety. Conservative indicators can refuse ordinary notes
for review; they never adopt them. All explicit source/template/application roots
must be caller-supplied for overlap refusal.

**Tracking/Git/next:** Existing #9 labels, assignee, v0.1.0 milestone and native
#8 → #9 → #10 dependencies preserved; no duplicate issue. #9 remains OPEN pending
acceptance. Diff/untracked/status reviewed; all 14 files unstaged/uncommitted on
main at c3a5402. No public lifecycle, batch planner/reporting, filesystem/state
publication, locks, journals, recovery, adoption/migration, transport work or other
chat/subagent. **Next eligible after Thread 09 acceptance/delivery verification and
a new request: Thread 10 / #10, explicitly NOT STARTED. Threads 10–17 and
enhancement #18 remain NOT STARTED.**


### Thread 09 Windows CI investigation — 20 October 2026

The maintainer reviewed/pushed implementation 08e967a, merged at
ff05ef61a817591ccaa2efd4e108d365a57e1772, and requested investigation/fixes for
Windows CI. Read the supplied traceback, clean current checkout and every job/
required step/full command log in run 39500770363 attempt 1 at that merge.
Linux Python 3.12–3.15: 917 passed each, no skips; macOS: 915 passed/2 native
filesystem-representation skips each. All eight passed standalone gates and both
independent installs. Windows Python 3.12: 6 failed/896 passed/15 skipped;
3.13: 9/893/15; 3.14: 7/895/15; 3.15: 6/896/15. Every failure is the same
ConflictError at the pathname/descriptor stamp comparison. Metadata/lock, lint,
format and Bandit passed on Windows; later build/Twine/independent installation/
whitespace steps were skipped, not passed. No other exception class was found.
Skip reasons were not enumerated by this quiet pytest invocation. Keep the failed
run and previous local-only handoff as historical evidence; #9 remains open.

A new synthetic regression reproduces the exact failure before correction.
CPython's Windows pathname stat/lstat compatibility layer reports creation time
as st_ctime_ns, while fstat can report metadata change time; they need not match
for an unchanged file. Verified official os documentation, CPython 3.14.7 source
and upstream issue 157671. Before dependent correction, record this internal
comparison policy: cross-API Windows observations compare matching device/inode,
mode/link-count/size/mtime and explicit birthtime_ns, refusing unavailable birthtime;
retain full ctime stamps for same-API path rechecks and descriptor-before/after
checks. POSIX comparisons stay unchanged. This corrects an invalid comparison;
no bypass, fallback, sleep/retry, identity/baseline/hash, ownership or transport
change. Add positive and adversarial regression coverage plus installed probes.
Native corrected Windows evidence will require a newly pushed exact-commit run;
no push/commit/CI rerun is authorized here. Windows sf stays refused and Thread 10,
later threads and #18 remain NOT STARTED. Changes remain unstaged/uncommitted.


### Thread 09 Windows correction handoff — 20 October 2026

**Corrected locally; #9 remains OPEN pending corrected exact-commit hosted
validation and maintainer acceptance.** Maintainer-delivered implementation
08e967a / merge ff05ef61a817591ccaa2efd4e108d365a57e1772 trees match. The six-file
correction remains unstaged/uncommitted on main at ff05ef6. No stage, commit,
push, PR, CI rerun, closure, publication, other chat or subagent action occurred.

**Failed hosted evidence retained:** Reviewed the supplied traceback and every
job/required step/full command log in [run 39500770363, attempt 1](https://github.com/jeffshurtliff/obforce/actions/runs/39500770363)
at ff05ef6. Linux Python 3.12–3.15 passed 917 tests per cell; macOS passed 915/2
skipped per cell. All eight passed standalone checks/builds/Twine/archive inspection
and both independent installs. Windows all passed strict lock, lint, format and
Bandit, then failed at the same invalid pathname/descriptor stamp comparison:

| Windows Python | Failed | Passed | Skipped |
| --- | --- | --- | --- |
| 3.12 | 6 | 896 | 15 |
| 3.13 | 9 | 893 | 15 |
| 3.14 | 7 | 895 | 15 |
| 3.15 | 6 | 896 | 15 |

Every reported exception was ConflictError('Read descriptor changed'); no other
exception class was found. Later Windows build/Twine/independent-install/whitespace
steps were skipped after pytest failure. The quiet logs do not enumerate skip
reasons, and skipped checks are not passed evidence. This run stays failed;
original local-only and older prerequisite failures keep their actual outcomes.

**Cause and correction:** Official CPython source and upstream issue 157671 show
that Windows lstat ctime can be creation time while fstat ctime can be metadata
change time. The original state reader compared these different quantities.
A deterministic synthetic test reproduced the exact failure before the fix.
The correction compares device/inode, mode, link count, size, mtime and explicit
integer birthtime across the Windows APIs, refusing missing/invalid birthtime.
Repeated pathname/parent observations and descriptor-before/after checks retain
full ctime; descriptor birthtime and safe type/reparse/hard-link constraints are
rechecked after reading too. POSIX full-ctime comparison remains unchanged.
This follows the existing offline source's recognized Windows semantic split
without changing that accepted source/transport code. No fallback, timing sleep,
retry, rounding, baseline adoption or overwrite bypass.

**Changes:** Focused sync/state.py correction; 18 new regression cases in
unit/test_state.py; installed helper and rewritten-state/renamed-rewritten-note
probes in dev/check_artifacts.py; SYNC_SAFETY, CHANGELOG and this roadmap updated.
Positive native/synthetic cases preserve exact bytes/mtimes/tree and input records.
Adversarial cases still refuse changed device/inode/mode/link-count/size/mtime/
birthtime, missing/noninteger birthtime, same-API path/parent/descriptor ctime
changes, post-read birthtime changes and injected reparse flags. No skips added.

**Verified local checklist:**

- [x] Reproduced the old failure before coding the correction; cause/policy recorded before implementation.
- [x] Focused state suite **189 passed, 2 native filesystem-representation skips**; final full suite **933 passed, 2 skipped** on macOS 27.0.1 ARM64 / Python 3.14.7 / Poetry 2.4.2. Combined coverage 95%; state 93%.
- [x] Strict Poetry metadata/lock, Ruff lint/format (74 files), Bandit and whitespace passed. Five existing narrow source/transport annotations unchanged; no new findings/suppressions.
- [x] Fresh corrected wheel/sdist build, strict Twine, exact 29-wheel/28-sdist member/license/source/resource/README/metadata inspection and both independent clean installs outside checkout/cwd passed. Runtime socket/process guards, installed timestamp regression/probes and no-cwd-artifact/byte/mtime/tree assertions all passed; setup/build/pip download network use stays separate.
- [x] Saved state wire/NoteState/property/byte/hash, identity/ownership/user/debt/privacy, graph/render/coverage, config/CLI, source/transport, dependency/lock and Apache contracts preserved. Changed Python headers retain requested GPT-6.1 Sol / 20 Oct 2026 attribution.
- [x] Existing #9 investigation/checklist/handoff synchronized; metadata/native dependencies preserved. All six files remain unstaged/uncommitted; no duplicate tracking.
- [ ] Corrected native Windows/Linux hosted exact-commit tests/builds/independent installs and other Python versions; no new CI was run.
- [ ] Maintainer acceptance and closure readiness; #9 remains open.

**Fresh correction artifacts (temporary; not published):**

| Artifact | SHA-256 |
| --- | --- |
| Wheel | `2eb677eaa462faaba053d559186474c1e0ac0ca18e7ef7d4c2552144688d2f32` |
| Sdist | `c84284d1e85d71271be6dadfcf4aa8b0e451292952b5be257f9b0857d0e1d1f7` |

**Remaining evidence and scope:** Synthetic Windows API observations on macOS
are regression evidence, not a native corrected Windows result. A new maintainer-
pushed commit/run must establish the fix on all four Windows cells and reach the
previously skipped artifact steps; no commit/push/rerun is authorized here.
Read-side stable trusted-tree/race limitations remain; no public lifecycle,
planner, state/vault publication, locking, journal, recovery or adoption/migration
was introduced. No real sf/Obsidian/auth/credential/.env/org/metadata/vault access.
Windows sf remains refused. Platform relationships remain partial/unavailable
even after clean empty results; offline relationships remain not collected.
**Next eligible after Thread 09 acceptance/delivery verification and a new request:
Thread 10 / #10, explicitly NOT STARTED. Threads 10–17 and enhancement #18 remain
NOT STARTED.**


### Thread 09 acceptance and closure — 20 October 2026

**Accepted and complete.** The maintainer reviewed/pushed the Windows correction,
confirmed passing CI and authorized closure if complete. All original Thread 09
tasks, correction regressions, delivery and exact-commit hosted gates are verified;
#9 is closed as completed. Thread 10 is next eligible and explicitly NOT STARTED.
No release/publication is implied.

**Delivered identity:** Initial implementation
08e967a7ac2fda50ffc72a334fb82569c5d4889f / merge ff05ef6; Windows correction
890ced229722318764d87d8b525a932c72addfc7 / merge
dff34a7eb806622331e4770de38cbf0e470d322a. Correction/merge trees match. Clean local
main and live GitHub main matched dff34a7 before this docs update. All 24 reviewed
package source/resource files match the delivered checkout. Maintainer changes
are retained; no source, dependency, lock, license or runtime contract changes
are made by this acceptance update.

**Exact-commit hosted evidence:** Verified every job, required step and full
command log in [run 39502679337, attempt 1](https://github.com/jeffshurtliff/obforce/actions/runs/39502679337)
at dff34a7:

| Cells | Verified outcome per cell |
| --- | --- |
| Linux Python 3.12–3.15 (4) | 935 passed, no skips; 95% combined coverage |
| macOS Python 3.12–3.15 (4) | 933 passed, 2 skipped; 95% combined coverage |
| Windows Python 3.12–3.15 (4) | 920 passed, 15 skipped; 93% combined coverage |
| Every cell | Standalone strict metadata/lock, Ruff lint/format (74 files), Bandit, fresh build, strict Twine, exact 29-wheel/28-sdist archive/license/source/resource/README/metadata inspection, both independent installs and whitespace passed |

All **24 independent artifact installs** passed import/resource/model/entry-point/
source/graph/render/parser/state/reconciliation probes, exact LF/CRLF saved bytes
feeding patch_note, no-op/move/conflict/non-adoption, malicious-state/path refusal,
rewritten-state/renamed-note timestamp checks, byte/mtime/tree preservation and
no-cwd-artifact assertions. Runtime socket/process guards were explicitly active;
setup/build/pip downloads remain separate network use. All required steps ran;
there were no hidden failed/skipped commands. Five existing narrow source/transport
Bandit annotations remain; no new findings/suppressions.

**Accepted bounded behavior:** Immutable NoteState and strict versioned wire/schema/
binding/scope rules, duplicate/type/path/hash/UUID refusal, conservative managed
indicators, bounded complete read-only discovery, exact saved generated bytes and
strict property comparisons, unique canonical UUID moves and deterministic path
invalidation outputs meet the synthetic acceptance scenario. Both baselines gate
acceptance regardless of incoming hashes; current notes cannot reconstruct
ownership. Human prose, user properties/debt decisions and absence/privacy
semantics remain protected. Native Windows creation/change timestamp semantics
are handled without rounding/retry/bypass, retaining same-API change guards and
explicit birthtime/safety checks. Source/graph/render/creation hashes and renderer-
local graph-plus-independent-Coverage composition are unchanged.

**Historical failures and limits:** Original [run 39500770363](https://github.com/jeffshurtliff/obforce/actions/runs/39500770363)
at ff05ef6 remains failed: all four Windows suites failed descriptor comparisons,
and downstream artifact gates were skipped. Prior local implementation/correction
handoffs and failed setup/probe outcomes remain historical. A local acceptance
log-matching probe initially missed Twine's wrapped artifact-name lines; corrected
matching verified both PASSED results per cell without changing CI outcomes.
macOS's two case/NFC fixture skips and Windows's 15 recorded skips remain visible;
quiet pytest logs do not enumerate individual Windows skip reasons. Native hosted
ordinary-file read/installed results and synthetic reparse/race cases do not
qualify hostile race isolation, public writes or Windows sf execution. Windows sf
stays refused. Requested platform relationships remain partial/unavailable even
when empty; offline stays not collected. No live sf/Obsidian/auth/credential/.env/
org/real-metadata/vault access occurred. No state writes, lifecycle command,
planner, locking, journal, recovery, adoption/migration or transport work was added.

**Verified acceptance checklist:**

- [x] All four Thread 09 implementation tasks and unique-move/conflict/non-adoption acceptance criteria met.
- [x] Maintainer review/push, delivered correction/merge tree identity and all 24 reviewed package files verified.
- [x] All 12 exact-merge hosted suites and standalone gates/builds/Twine/archive checks and 24 independent guarded installs passed; actual skips retained.
- [x] Accepted identity/baseline/state/ownership/privacy/source/graph/hash/coverage/transport and Apache contracts preserved.
- [x] Maintainer authorized closure if complete; #9 status/checklists/acceptance and current docs/roadmap synchronized.
- [x] Exact Thread 10 prompt prepared in its roadmap section; direct prerequisites #6/#7/#8/#9 accepted and closed, #10 remains open/NOT STARTED.

**Docs/Git/handoff:** Seven documentation files changed only. Local link/anchor,
fence, consistency, privacy and whitespace checks plus diff/untracked/index/status
review passed. No application tests/builds/dependency installs were rerun; the
verified delivered application is covered by the hosted evidence above. Docs stay
unstaged/uncommitted on main at dff34a7. No stage/commit/push/PR/merge/tag/CI rerun/
release/publication, other chat or subagent occurred. Existing #9 labels, assignee,
v0.1.0 milestone and native #8 → #9 → #10 links are preserved; no duplicate issue.
#10 itself was inspected, not edited or started. **Next eligible under a new
request: Thread 10 / #10. Threads 10–17 and enhancement #18 remain NOT STARTED.**

### Thread 10 start and contract — 20 October 2026

Maintainer authorized only internal read-only complete planning and bounded
reporting; #10 remains open pending acceptance. Clean baseline 0409da6 differs
from accepted correction merge dff34a7 only in documentation. Before coding,
rechecked #6/#7/#8/#9 acceptance/closure, native prerequisites and #10 → #11,
actual graph/render/parser/state code and all 48 jobs/required steps/full logs in
exact-merge runs 39431345348, 39440606470, 39453887153 and 39502679337. All gates,
Twine/archive checks and both independent installs passed per cell; #9 counts
match Linux 935, macOS 933/2 skips, Windows 920/15 skips. Historical failed run
39500770363, skips and prior local probe/setup failures remain historical. No new
prerequisite blocker; local/vendor_docs absent. Connector comments returned 403;
authorized existing-issue updates use authenticated gh instead.

Recorded schemas, UUIDv5 policy, explicit caller/retained-source inputs, action
order/counts, blocked semantics, redacted reports, publication preconditions and
finite limits in [SYNC_SAFETY](../docs/SYNC_SAFETY.md#thread-10-pre-implementation-planner-contract--20-october-2026)
before dependent implementation. Accepted NoteState/wire/hash and renderer-local
graph-plus-independent-Coverage contracts remain. Supporting parser lifecycle
validation will accept the two already supported saved lifecycle values; only
the planner may propose missing under the documented positive live evidence.
No writer, publication, state write, public command, source/transport or real
Salesforce/Obsidian/vault work. Thread 11 and later and #18 remain NOT STARTED.

### Thread 10 handoff — 20 October 2026

**Locally implemented; pending maintainer acceptance.** Existing #10 remains OPEN.
The roadmap index/thread status, existing issue start/progress/checklist/handoff
and applicable docs are synchronized. Direct prerequisites #6/#7/#8/#9 remain
accepted/closed; native dependencies and #10 → #11 are preserved. No duplicate
issue, other-chat action or subagent was used.

**Implementation:** `sync/planner.py` combines explicit bounded normalized current
and retained facts, independent coverage, matching previous/current graph evidence,
accepted renderer candidates, strict reconciliation and preservation patches.
Immutable typed actions cover create/update/no_op/move/missing/conflict, ordered
by canonical component key with one primary action and independent content/state
flags per component. Stable UUIDv5 creation never replaces saved IDs. Whole-batch
preflight validates existing/proposed paths/parents together, retains immutable
same-API read/content-digest/missing-path preconditions and rechecks after rendering.
Blocked results expose no candidate state/content/graph/preconditions. Unique moves
reconcile observed paths without rename operations; missing proposals require
positive comparable supported complete-live inventory. There is no deletion.
`sync/reporting.py` returns bounded counts, fixed diagnostics, independent coverage
warnings and opt-in UUID/action details with existing 3/2/1/4/0 precedence.

Supporting state changes retain exact original state bytes plus immutable read
observations in reconciliation results; no-op plans preserve even a valid
noncanonical state serialization. Accepted NoteState/state wire/hash helpers,
renderer-local graph-plus-independent-Coverage composition, exact saved LF/CRLF
baselines, source/transport behavior and Apache licensing are unchanged. The
patcher accepts exactly active/missing lifecycle values; both strict owned-value
and exact saved-body checks remain mandatory. Existing notes never use complete
new-note candidates. Human prose, supported YAML/comments and all user properties,
including technical-debt assessments/status/severity/review dates, remain owned
by the user. Previous graph and absent-component normalized facts are required
explicitly and verified against saved hashes; state is never reconstructed.
No dependency, pyproject or lockfile change was necessary.

**Local synthetic/offline evidence:** macOS ARM64 / Python 3.14.7 / Poetry existing
locked environment. Full suite **1,058 passed, 2 skipped**, 95% combined coverage;
**125 new cases** include planner/report tests and the shared artifact probe.
The skips are the existing case/NFC filesystem fixtures, not blanket planner or
Windows skips. A final focused **124 passed** after strengthening failure-path
snapshots revalidated source/vault bytes/mtimes/tree and input preservation.
Strict metadata/lock, Ruff lint/format (79 files), Bandit and whitespace passed.
Bandit retains five pre-existing source/transport annotations, with no findings
or new suppressions. Tests cover stable/reordered/time-independent creates,
explicit next-baseline no-op, generated-property/body/identity/schema conflicts,
user-only edits, LF/CRLF, graph-only and both-direction neighbor move invalidation,
stale retention, generated/creation/options/layout/renderer/coverage changes,
absence/privacy distinctions, positive versus incomplete/offline/noncomparable
absence, bindings/scopes/retained facts, collisions/unsafe entries/read races,
finite bounds, redacted typed failures and deterministic counts/outcomes.

**Fresh package evidence:** A new empty external candidate directory supplied
fresh wheel/sdist artifacts. Strict Twine, exact **31 wheel / 30 sdist** archive
member/license/source/resource/README/metadata checks, `pip check`, both entry
points and both independent outside-checkout installs passed. All installed
source/graph/render/parser/state probes and the new `dev/probe_planner.py` passed.
The planner probe checks fixed full synthetic note/state SHA-256, UUID stability,
LF/CRLF no-op/update/move/conflict, state round trips, bounded redacted reporting,
rewritten state/note timestamps, exact bytes/mtimes/tree/input preservation and
no cwd artifacts. Runtime socket/process audit guards are active and explicitly
probed; setup/build/pip network use is separate. Artifact hashes:

- Wheel `obforce-0.1.0.dev0-py3-none-any.whl`: `0cab07da8e52cce86a9a1cc8be5294b97b1706aa68d219e179ebb93ee61b99cd`.
- Sdist `obforce-0.1.0.dev0.tar.gz`: `b4236347d254a0611144f598a5b7ad2ac71aa9ab9a81d4694e8e15cc05cda906`.

**Retained failures/gaps:** Initial local fixture mistakes (synthetic endpoint IDs,
empty-bound inputs, expected link extension/UUID) failed before correction.
Some shared-temporary-root development probes also returned blocked plans;
the exact conflicting observation was not captured, so its cause remains
unconfirmed. No guards were relaxed. Final complete/focused runs used
an explicit isolated temporary test root. The first fresh build could not connect
to PyPI and produced no accepted artifact; an authorized network-enabled fresh
build/install retry passed. GitHub connector comments returned 403; authenticated
`gh` posted only authorized existing-issue updates. Historical prerequisite failed
run 39500770363 and its Windows/downstream skipped gates, all accepted correction
run skips and earlier local setup/probe failures remain historical.

No hosted/native Linux/Windows or Python 3.12/3.13/3.15 Thread 10 result is claimed;
no CI was rerun. Synthetic Windows birthtime/path-descriptor/same-API change tests
preserve accepted semantics, but do not establish native planner or sf execution.
Windows sf stays refused. Relationships remain partial/unavailable when requested
and not collected offline. Immutable observations are not an atomic filesystem
snapshot or hostile race isolation. Future writers must revalidate all observations
and digests under qualified guard/recovery rules. Graph persistence, publication,
state writes, staging, locks, journals, recovery, adoption/migration, backups/Git
integration and public lifecycle commands are not implemented by this thread.

**Verified local checklist:**

- [x] All four Thread 10 implementation tasks and synthetic acceptance scenarios.
- [x] Pre-implementation schemas/policy/inputs/counts/limits/report/precondition contracts recorded.
- [x] Focused tests, complete local suite, strict checks and fresh independent installed artifacts.
- [x] Source/transport/hash/state-wire/privacy/ownership/Apache compatibility reviewed.
- [x] Applicable docs/changelog/roadmap and existing issue evidence synchronized.
- [ ] Maintainer acceptance, delivery and exact-commit hosted Thread 10 evidence.

**Git/next:** All changes are unstaged/uncommitted on the existing branch
`feature/10-thread-10-read-only-change-planner-and-conflict-reports` at baseline 0409da6.
No stage/commit/push/PR/merge/tag/release/upload/publication, real sf/Obsidian,
credential/.env/auth discovery, org/real metadata/vault access or `.obsidian`
settings changes occurred. Diff/untracked files/status reviewed. After Thread 10
maintainer acceptance/delivery verification and a new request, the next thread
is **Thread 11 / #11, explicitly NOT STARTED**. All later threads and enhancement
#18 remain **NOT STARTED**.

### Thread 10 macOS CI correction start — 20 October 2026

Maintainer reviewed/pushed implementation 11af258, merged at
725fe36875bc095f2745153d5d944afe37aa480c, and requested correction of the failed
macOS Python 3.12 cell. Read all 12 job/step/full command logs in run 39507844963,
attempt 1: Linux 1060 passed each; macOS 3.13–3.15 1058 passed/2 skipped each;
Windows 1044 passed/16 skipped each. All standalone/build/Twine/archive/both-install
checks passed in the 11 successful cells. macOS 3.12 had 1 failed/1057 passed/2
skipped; build/Twine/install/whitespace were skipped. Its failure was the initial
setup candidate before the test's late-state mutation, not that mutation's check.
The historical failed run remains failed; #10 remains open.

Before editing, a local instrumented loop reproduced a blocked initial plan at
iteration 124 and captured the exact changed full lstat stamp on the shared
system temporary ancestor. This establishes a concrete local environmental race;
the old hosted assertion did not retain its conflicting path, so the same exact
hosted cause cannot be proven retrospectively. The workflow let Python/pytest
and installed probes use the OS-wide shared temp root, violating their quiescent
synthetic-fixture assumption. The correction will give all CI steps after Python
setup a fresh dedicated root beneath runner.temp via TMPDIR/TEMP/TMP. This avoids
the busy system-temp ancestry for both tests and independent installed probes.
Production reader/planner/Windows timestamp/parent checks will remain unchanged:
no retries, timestamp rounding, skipped guard or relaxed comparison. Add a
controlled sibling-churn regression and safe blocked-setup diagnostic; validate
locally on Python 3.12 and the existing environment. Thread 11 and later and #18
remain NOT STARTED. Changes stay unstaged/uncommitted on the existing fix branch.

### Thread 10 macOS CI correction handoff — 20 October 2026

**Correction ready for review; not delivered or accepted.** Implementation 11af258
is delivered at merge 725fe36875bc095f2745153d5d944afe37aa480c. Existing issue #10
remains OPEN. The failed exact-merge run 39507844963 attempt 1 remains failed:
11 cells passed every required command and both installs (Linux 1060 passed;
macOS 3.13–3.15 1058/2 skips; Windows 1044/16 skips), while macOS 3.12 had one
blocked baseline setup, 1057 passed/2 skips and skipped downstream artifact gates.
No failed/skipped command is counted as passed.

**Cause/evidence:** The failing assertion precedes the test's injected late-state
mutation. Local instrumented reproduction captured a full lstat change in the
shared system-temp ancestor at initial-plan iteration 124. This proves a local
shared-ancestor race matching the hosted symptom; the hosted assertion did not
retain its particular observation, so that exact cause remains inferred there.
The full parent guard was correctly refusing an unstable read environment.

**Correction:** The workflow creates a fresh root under runner.temp after Python
setup and exports TMPDIR/TEMP/TMP through GITHUB_ENV before Poetry installation.
All later commands, fixtures, build setup and independent installed probes inherit
it. A controlled regression verifies sibling churn still blocks a descendant
vault and leaves a vault under a separate temporary ancestry clean. Baseline setup
assertions now show only the bounded redacted plan report. No production source,
reader/planner/stat comparison, Windows birthtime bridge, same-API guard, dependency,
lockfile, package allowlist, source/transport, state wire/hash or license changed.
No retry, guard bypass, rounding or new skip was added.

**Executed checks:** Local macOS ARM64, separate locked Python **3.12.7** environment
and existing **3.14.7** environment each passed **1059 tests / 2 existing case/NFC
fixture skips**, 95% combined coverage. Both full suites passed under an explicit
workspace temporary root; an earlier Python 3.12 full suite also passed under a
/private/tmp-based root. Focused planner tests passed **125**. The workflow's exact
POSIX shell/Python setup was executed against synthetic GITHUB_ENV; all three
exports and Python 3.12 tempfile selection were checked. Metadata/strict lock,
Ruff lint/format (79 files), Bandit and whitespace passed; Bandit retains five
existing source/transport annotations and no findings/new suppressions.

A fresh Python 3.12 build under the workspace temp environment passed strict
Twine, exact 31-wheel/30-sdist archive/license/source/resource/README/metadata
inspection, pip consistency, both entry points and both independent installed
source/graph/render/parser/state/planner/report probes outside checkout/cwd.
Runtime socket/process guards were active; build/pip setup network use is separate.
Unchanged artifact SHA-256: wheel
`0cab07da8e52cce86a9a1cc8be5294b97b1706aa68d219e179ebb93ee61b99cd`;
sdist `b4236347d254a0611144f598a5b7ad2ac71aa9ab9a81d4694e8e15cc05cda906`.

**Retained attempts/limits:** An early VIRTUAL_ENV-only setup selected an existing
3.14 environment and is not Python 3.12 evidence; explicit temporary Poetry env
selection subsequently verified 3.12.7. A guarded /private/tmp-based stress probe
blocked at iteration 33 without capturing its specific conflicting observation;
a later instrumented **1000-plan** run passed. Thus merely nesting under a busy
system-temp location is not a guarantee of quiescent ancestry. The workflow
instead uses workspace runner.temp; guards still intentionally refuse any actual
ancestor change. The old hosted Python is 3.12.10, distinct from local 3.12.7.
PowerShell/native Windows/Linux and corrected hosted matrix execution remain
unavailable locally; no CI rerun was requested/performed. Historical failures,
skips and prior local setup/probe attempts retain their original status. Windows
sf stays refused; partial/unavailable requested relationships and offline not-
collected behavior are unchanged. No live org/auth/credential/.env/Obsidian/real
metadata/vault access, publication or later lifecycle work occurred.

**Tracking/Git/next:** Docs/changelog and existing #10 progress/checklist/handoff
are synchronized. Six focused files remain unstaged/uncommitted on
`fix/10-thread-10-address-failed-macos-py312-ci-run` at 725fe36. No stage/commit/push/
PR/merge/tag/release/publication, other-chat action or delegation occurred. After
correction delivery, exact hosted verification and maintainer acceptance plus a
new request, next is **Thread 11 / #11, NOT STARTED**. All later threads and #18
remain **NOT STARTED**.
