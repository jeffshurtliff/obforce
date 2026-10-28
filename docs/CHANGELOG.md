# Changelog

All notable changes to this project are documented here using
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
The current package is `0.1.0.dev0`; no stable release has been published.

## [Unreleased]

### Added

- Explicit, noninteractive `init`, initial-only `build`, managed-vault `sync` and
  local `recover`, with console/module help and installed-version reporting.
- Read-only offline ApexClass inventory from declared Salesforce DX packages and
  explicit live inventory/audit collection through separately authorized sf on
  POSIX. Verified org identity, bounded fixed queries and independent inventory,
  audit and relationship coverage. Windows sf execution remains refused.
- Directed platform-reported relationship evidence with reciprocal links,
  unresolved labels, partial/unavailable coverage and stale-evidence preservation.
  No inferred dependency or runtime-impact claims.
- Bounded installed Jinja defaults and explicit finite per-template overrides,
  readable generated Markdown and YAML, persistent UUIDs and unique note-move
  reconciliation. Creation templates initialize only new notes.
- Strict note parsing and generated-property/body baselines, supported human
  YAML/comment/prose preservation, whole-batch conflict refusal and byte/mtime-stable
  no-op behavior. Unsafe YAML, malformed markers and unsupported schemas refuse.
- Private state-document schema 2 with evidence schema 1 for retained normalized
  facts/graph, exact NoteState-schema-1 baselines and immutable optional live
  inventory scope declarations. Explicit per-sync comparable-scope attestation
  gates missing evaluation; partial/offline absences preserve prior facts.
- Guarded recoverable notes/dashboard/state publication, continuous writer lock,
  same-filesystem staging, journal-schema-2 before-images, preview, conservative
  precommit rollback and committed cleanup. Intervening edits preserve evidence.
- A tracked packaged Apex Classes Base with exact dashboard-schema-1 ownership,
  class-name links and audit/API/debt columns. UI layout edits are conflicts too.
  Ordinary Markdown works without plugins; no `.obsidian` settings are changed.
- Creation-only Boolean `technical_debt: false`, blank human severity/status and
  null review date, with all existing human values preserved afterward.
- Fictional multi-package DX and presentation samples; complete installation,
  offline/live, CLI, customization, coverage, ownership, dashboard and recovery
  guides; contributor/security guidance and a documentation-only release runbook.
- Executable offline guide verification in fresh independent wheel/sdist installs,
  using both actual entry points, quoted space paths, active runtime guards,
  previews/no-op snapshots, UUID moves, template creation, conflicts and synthetic
  interruption/recovery. Examples use only fictional data.
- Synthetic platform/failure/scale qualification and bounded CI collection/test
  supervision with exclusive logs, finite deadlines/output budgets, owned-child
  cleanup and concise per-case/slow-duration diagnostics. Complete historical
  results and measurement limits remain in the maintainer evidence records.

### Changed

- Revised the stable 0.1.0 roadmap and tracking with R1–R8 requirements/design,
  real-input discovery, vault-owned config, distinct DX presence/warnings,
  successful 1,000-class lifecycle and actual/native release acceptance gates.
  These are planned requirements, not delivered runtime behavior; optional alpha
  publication remains separate. Historical Thread 01–15 acceptance is retained.
- Clarified Obforce's goal of documenting an entire Salesforce org's metadata
  and configuration, with Apex classes as the current version's scope and
  additional areas planned for future releases.
- Reused immutable note-path validation within one batch without caching filesystem
  observations. Each evidence-validation/planning/replanning pass creates a fresh
  snapshot; bytes, hashes, error precedence and independent integrity guards remain.
- Renderer fingerprint is 4 for readable escaped metadata, four-space generated
  nesting and reserved UTC audit-date projections. Note/marker/config/model remain
  1; state-document/evidence/NoteState/journal/dashboard remain 2/1/1/2/1.
- Product and maintenance instructions describe current behavior rather than
  development sequence. Release-site styling and reviewed repository cleanup are
  tracked separately as [a v0.1.0 release blocker](https://github.com/jeffshurtliff/obforce/issues/22).

### Fixed

- Native unrooted Windows relative config paths with spaces, while retaining
  refusal of ambiguous drive paths and portable case/Unicode collisions.
- Windows lexical alias validation retains original caller spelling; LF checkout
  and explicit LF template fixtures preserve platform-independent exact bytes.
- Unreadable config errors use bounded redacted operational diagnostics without
  premature path disclosure from Click readability checks.
- Oversized pytest parameter IDs no longer exceed Windows environment-value
  limits; complete fixture payloads remain unchanged and collection bounds IDs.
- Same-byte/restored-mtime concurrent changes retain full historical descriptor
  and pathname guards; recovery never treats byte equality alone as authority.

### Security

- No credential discovery, custom OAuth, telemetry, AI service, runtime network in
  offline mode, force overwrite, automatic adoption/migration, automatic deletion,
  backup/Git integration or stable public Python API.
- Bounds refuse rather than truncate. Source/workspace/org/scope binding, exact
  ownership, complete batch validation and fresh writer integrity checks remain.
  Exit precedence is 3, 2, 1, 4, 0. Legacy evidence-less sync and journal-schema-1
  recovery remain refused. Private retained state/before-images are unencrypted.
- [Qualification](QUALIFICATION.md) separates local, hosted, native, mocked,
  skipped and unavailable evidence. Tests do not establish atomic snapshots,
  atomic multi-file writes, power-loss/hostile-race or arbitrary filesystem/ACL
  guarantees. Native Obsidian preview remains unavailable. Earlier failures,
  cancellations and uncaptured causes are retained in maintainer evidence.
