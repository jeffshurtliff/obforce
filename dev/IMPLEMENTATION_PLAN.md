# Obforce v0.1.0 implementation roadmap

**Planning baseline:** 18 October 2026

**Target release:** `0.1.0`; initial development version: `0.1.0.dev0`

**Status:** Planning only. All implementation threads are **not started**.

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

Freeze a versioned model in Thread 02 with at least:

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

Proposed generated fields include `sf_type`, `sf_full_name`, `sf_namespace`,
`sf_api_version`, `sf_status`, `sf_created_at`, `sf_created_by`,
`sf_last_modified_at`, `sf_last_modified_by`, `sf_source_mode`,
`sf_dependency_coverage`, and `sf_lifecycle`. Omit unknown audit values and explain
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

Minimal proposed TOML:

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

Proposed exit codes: `0` for a successful complete run or valid no-op, `1` for an
operational failure, `2` for invalid usage/configuration, `3` for conflicts or
recovery-required state, and `4` for a completed operation with partial/unavailable
requested coverage. An offline run can succeed at its declared local scope while
explicitly reporting that org audit/dependency coverage is unavailable by design.
Verify Click's usage behavior and freeze precedence for overlapping error classes
in Thread 02. Never return a success code for a truncated requested live scan.

## 8. Implementation threads

### Common thread contract

- Read root agent/contributor guidance, this roadmap, and the relevant contracts.
  Inspect actual dependencies and repository changes; do not rely on labels alone.
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
  do not begin it. No issue numbers are assigned by this document.

### Thread index and milestones

| ID | Thread | Dependencies | Milestone | Status |
| --- | --- | --- | --- | --- |
| 01 | Foundation and developer workflow | None | A: foundations | Not started |
| 02 | Configuration, models, and contracts | 01 | A | Not started |
| 03 | Offline Apex source | 02 | B: source data | Not started |
| 04 | Salesforce CLI process boundary | 02 | B | Not started |
| 05 | Live Apex inventory and audit enrichment | 04 | B | Not started |
| 06 | Platform relationships and normalized graph | 03, 05 | B | Not started |
| 07 | Packaged templates and note rendering | 03, 06 | C: safe proposals | Not started |
| 08 | Existing-note parsing and preservation | 07 | C | Not started |
| 09 | State validation and identity reconciliation | 08 | C | Not started |
| 10 | Read-only change planner and conflict reports | 06, 07, 08, 09 | C | Not started |
| 11 | Transaction writer and recovery | 10 | D: working lifecycle | Not started |
| 12 | Public initialization and initial build | 11 | D | Not started |
| 13 | Public refresh and missing-component lifecycle | 12 | D | Not started |
| 14 | Native dashboard and CLI usability | 13 | E: usable product | Not started |
| 15 | Platform, failure, and scale qualification | 14 | E | Not started |
| 16 | User and maintainer documentation | 15 | F: release candidate | Not started |
| 17 | v0.1.0 release preparation | 16 | F | Not started |

The default path is sequential. Threads 03 and 04 can be worked on independently
after 02 if the maintainer explicitly chooses parallel work; avoid shared-file
conflicts. Do not start extra agents or chats merely because the table permits
independent work.

Milestone demos: **A** installs and validates synthetic normalized data; **B**
produces comparable source/graph records from offline fixtures and mocked live
responses; **C** previews changes against edited fixture notes without writing;
**D** builds, edits, refreshes, and recovers a synthetic vault; **E** demonstrates
native discovery and qualified failure/platform behavior; **F** produces an
installable, documented candidate. Intermediate demos may use tests/internal
functions; public mutation commands remain unavailable until their safety gates.

### Thread 01 — Foundation and developer workflow

**Goal:** An installable, reproducible Python package with safe development defaults.

**Depends on:** None. **Status:** Not started.

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

**Copy-ready prompt:**

> Read AGENTS.md, CONTRIBUTING.md if present, and dev/IMPLEMENTATION_PLAN.md.
> Implement only Thread 01. Preserve the current license and user changes; create
> the Poetry/src foundation, contributor guidance, offline tests and CI. Validate
> fresh install artifacts and record actual evidence. Leave changes uncommitted;
> do not implement source connectors, create issues, or publish.

### Thread 02 — Configuration, models, and contracts

**Goal:** Validated configuration and versioned internal records before connectors.

**Depends on:** 01. **Status:** Not started.

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

> Implement only Thread 02 after verifying Thread 01. Freeze and document the
> proposed configuration/model/ownership contracts, add deterministic validation
> tests, and record any unresolved material decision. Do not query Salesforce or
> write a vault. Update the roadmap handoff and leave changes uncommitted.

### Thread 03 — Offline Apex source

**Goal:** A read-only local project source producing honest normalized Apex records.

**Depends on:** 02. **Status:** Not started.

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

> Implement only Thread 03. Add the offline Apex adapter and synthetic project,
> preserving source bytes and reporting limited local coverage. Verify safe XML,
> identity, and unavailable-field behavior offline. Do not write vault notes,
> inspect real metadata, or implement more component types. Leave work uncommitted.

### Thread 04 — Salesforce CLI process boundary

**Goal:** A bounded, mockable, read-only `sf` process adapter.

**Depends on:** 02. **Status:** Not started.

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

> Implement only Thread 04 using mocked sf process results. Verify current
> official command contracts and implement the bounded read-only process boundary.
> Do not install/update sf, authenticate, query an org, or build a vault. Record
> platform gaps and leave changes uncommitted.

### Thread 05 — Live Apex inventory and audit enrichment

**Goal:** Normalized live Apex records using existing CLI authorization.

**Depends on:** 04. **Status:** Not started.

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

> Implement only Thread 05 with the existing process boundary and synthetic
> responses. Add explicit org identity, Apex inventory/audit normalization, and
> tested coverage handling. Do not access a live org unless I separately authorize
> its target and operations. Leave work uncommitted and report validation limits.

### Thread 06 — Platform relationships and normalized graph

**Goal:** Useful references with explicit evidence and incomplete-coverage handling.

**Depends on:** 03, 05. **Status:** Not started.

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

> Implement only Thread 06. Verify the platform dependency contract, then add the
> provenance-aware graph and best-effort adapter with honest failure/coverage
> behavior. Use synthetic responses; no live queries are authorized by this prompt.
> Do not add a static analyzer or new component notes. Leave work uncommitted.

### Thread 07 — Packaged templates and note rendering

**Goal:** Deterministic candidate notes from normalized data without vault writes.

**Depends on:** 03, 06. **Status:** Not started.

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

> Implement only Thread 07. Add installed-package templates and deterministic
> rendering with the defined ownership and safety contract. Test synthetic output,
> overrides, escaping, and wheel/sdist resource access. Do not publish notes into
> an existing vault or implement sync. Leave changes uncommitted.

### Thread 08 — Existing-note parsing and preservation

**Goal:** Safe reading/patching of managed notes while retaining human content.

**Depends on:** 07. **Status:** Not started.

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

> Implement only Thread 08. Add managed-note parsing, baseline conflict detection,
> and in-memory preservation patches using synthetic edited notes. Verify user
> content and technical-debt fields survive. Do not add a force-overwrite escape
> hatch or write a real vault. Leave work uncommitted.

### Thread 09 — State validation and identity reconciliation

**Goal:** Reliable ownership and note-move matching independent of filenames.

**Depends on:** 08. **Status:** Not started.

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

> Implement only Thread 09. Add strict state handling and identity-based note-move
> reconciliation with synthetic vaults. Refuse ambiguous ownership, unsupported
> source switches, and absent/corrupt state. Do not implement automatic adoption,
> migration, or publication. Leave changes uncommitted.

### Thread 10 — Read-only change planner and conflict reports

**Goal:** A complete deterministic preview of a build/refresh before any write.

**Depends on:** 06, 07, 08, 09. **Status:** Not started.

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

> Implement only Thread 10. Produce complete read-only change plans with coverage,
> conflicts, no-op behavior, and accurate summaries. Verify dry-run filesystem
> preservation using synthetic vaults. Do not expose mutating build/sync commands
> before the writer safety gate. Leave changes uncommitted.

### Thread 11 — Transaction writer and recovery

**Goal:** Recoverable bounded publication primitives before public vault writes.

**Depends on:** 10. **Status:** Not started.

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

> Implement only Thread 11. Add and fault-test the bounded transaction and recovery
> primitives with temporary synthetic vaults. Preserve intervening edits and
> refuse invalid journals. Do not widen into public build/sync implementation,
> automatic deletion, or Git operations. Leave changes uncommitted.

### Thread 12 — Public initialization and initial build

**Goal:** The first complete user journey from configuration to a managed vault.

**Depends on:** 11. **Status:** Not started.

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

> Implement only Thread 12 after verifying the transaction tests. Expose init,
> initial build, and recovery using the established contracts. Demonstrate the
> offline synthetic quickstart and mocked live flow. Do not implement refresh,
> adopt arbitrary vaults, query real orgs, or publish. Leave changes uncommitted.

### Thread 13 — Public refresh and missing-component lifecycle

**Goal:** Trustworthy incremental writing that preserves knowledge over time.

**Depends on:** 12. **Status:** Not started.

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

> Implement only Thread 13. Add safe public refresh with ownership/conflict,
> note-move, coverage, no-op, and recovery behavior. Demonstrate the multi-run
> synthetic lifecycle and preserve all human fields. No force-overwrite, automatic
> note deletion, source switching, real org tests, or Git operations. Leave work
> uncommitted and report exact evidence.

### Thread 14 — Native dashboard and CLI usability

**Goal:** A discoverable administrator experience using native Obsidian features.

**Depends on:** 13. **Status:** Not started.

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

> Implement only Thread 14. Add the minimal protected native Bases dashboard and
> polish the documented CLI journey using synthetic data. Verify current Bases
> syntax, asset packaging, and edited-dashboard preservation. Do not install
> plugins, change Obsidian settings, or add new metadata types. Leave work
> uncommitted and distinguish automated from native-app validation.

### Thread 15 — Platform, failure, and scale qualification

**Goal:** Evidence for the supported platforms and realistic local operation.

**Depends on:** 14. **Status:** Not started.

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

> Implement only Thread 15. Qualify the offline lifecycle, safety, packaging, and
> synthetic scale behavior across the stated matrix, fixing bounded defects.
> Report native, hosted, mocked, skipped, and unavailable evidence separately.
> Do not broaden metadata scope, run real org/vault tests, or advertise unverified
> platform support. Leave changes uncommitted.

### Thread 16 — User and maintainer documentation

**Goal:** An accurate, maintainable path from installation through safe refresh.

**Depends on:** 15. **Status:** Not started.

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

> Implement only Thread 16. Finish and verify accurate user/contributor/security/
> release documentation and the clean-install offline tutorial. Describe actual
> limitations and evidence without promising full-org documentation. Do not build
> a hosted site, access production data, or start release preparation. Leave work
> uncommitted.

### Thread 17 — v0.1.0 release preparation

**Goal:** Reviewable `0.1.0` candidate artifacts and a concrete publication handoff.

**Depends on:** 16. **Status:** Not started.

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
live dependency API capability, exact schema/CLI contract freeze, native platform qualification, and
release acceptance. Routine internal choices may be made within a requested
thread. Changing ownership, deleting user content, weakening safety, or expanding
public scope requires a recorded maintainer decision.

## 11. Tracking and future handoff records

Thread IDs are local roadmap identifiers, not invented GitHub issue numbers.
Creating issues/milestones, posting public comments, or messaging another chat
requires a direct maintainer instruction for that action. If requested, map one
issue per bounded thread and preserve the dependency graph. Update only verified
progress; leave partial work/pending review accurately labeled.

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
