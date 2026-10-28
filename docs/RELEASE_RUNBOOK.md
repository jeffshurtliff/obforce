# Maintainer release runbook

This is a procedure for a future explicitly authorized release. Current metadata
is `0.1.0.dev0`; this document does not prepare or authorize publication. Keep
candidate review, acceptance, Git delivery, CI execution, documentation hosting
and package publication as separately authorized actions.

## Before preparing v0.1.0

- Follow the [approved usable stable release plan](../dev/STABLE_010_RELEASE_PLAN.md).
  R1–R8 / [#23](https://github.com/jeffshurtliff/obforce/issues/23)–[#30](https://github.com/jeffshurtliff/obforce/issues/30)
  require maintainer inputs, real discovery before concrete design approval,
  vault-owned config, DX presence/warnings/dashboard, successful 1,000-class
  build/refresh/no-op/recovery and actual sf compatibility. No stable version
  promotion or publication before mandatory product acceptance. These targets
  remain unsatisfied; the roadmap change is not feature or qualification evidence.
- Obtain [R8/#30](https://github.com/jeffshurtliff/obforce/issues/30) maintainer
  acceptance of actual DX on claimed platforms, actual live on macOS/Linux,
  native Obsidian Reading/Live Preview/property behavior and scale/artifact
  results. Windows sf stays deferred in #18. Synthetic/refusal-only evidence
  cannot replace these required real/native/successful-publication gates.
- Obtain acceptance of the documentation/tutorial candidate in
  [#16](https://github.com/jeffshurtliff/obforce/issues/16).
- Complete and accept the release-blocking Sphinx/ReadTheDocs styling and reviewed
  repository cleanup in [#22](https://github.com/jeffshurtliff/obforce/issues/22).
  Inspect the actual Obfuscidian, SalesPyForce and PyDPlus conventions. Approve a
  retention plan before removing development notes, scripts or evidence. Preserve
  historical failures/skips/unavailable observations and full measurements in an
  approved maintainer record. Do not delete required reproducible verification.
  Final #22 acceptance follows R8 and integrates the revised delivered behavior;
  #16 retains its original documentation-review scope.
- Obtain a separate instruction to begin
  [release preparation](https://github.com/jeffshurtliff/obforce/issues/17), which
  remains NOT STARTED, blocked by #16, #22 and R8/#30. Broader optional optimization
  and Windows sf support are separate work and do not silently become release capabilities.

## Review the candidate

Read the current contributor/security guidance and inspect Git status/diff and
untracked files. Preserve maintainer edits. Confirm the current release's
ApexClass-only scope, commands and version matrix; do not advertise inferred debt/dependencies,
adoption/migration, backup/Git integration, atomic snapshots, atomic multi-file
writes or unverified filesystem support. Review every public example for fictional
provenance and every source/archive for private `local/`, secrets, metadata,
vaults/state/recovery, absolute machine paths and development-only material.

Review static PEP 621 version and classifier metadata, lock consistency, Apache
license, changelog, README, documentation navigation and matching sample version.
Make version/dependency/lock changes only within the separately authorized
candidate work. Use Poetry for dependencies; never hand-edit its lockfile.
Internal Python modules are not a stable public API.

## Validate before delivery

Use [contributor checks](../CONTRIBUTING.md) with stable external fixture and
application ancestry, separate installer/coverage roots, fresh exclusive logs
and active runtime guards. Run the applicable metadata/lock, Ruff lint/format,
Bandit, bounded full pytest statement/branch/subprocess coverage, whitespace,
fresh build, strict Twine, exact archive inspections, independent wheel and sdist
installs and every fictional offline tutorial. Verify both actual console and
module entry points from outside checkout/cwd, space paths, previews, no-op
bytes/mtimes, ownership conflicts and synthetic interruption/recovery.

Record exact source revision and artifact SHA-256/file lists. At this candidate
baseline the allowlists are **36 wheel / 35 sdist files**. Any intentional package
change needs reviewed allowlist updates and independent checks. Inspect README
rendering in package metadata as well as documentation output. No stale `dist/`
validation. No live services are needed for the ordinary offline checks above.

Separately verify the mandatory R8 actual-input/native evidence against the
candidate. Record exact code/artifact identities, sf/Node/plugin versions,
environments and limitations privately, with public-safe summaries. Requalify
affected scenarios after material candidate changes; do not infer a real pass
from mocks or an earlier code revision. Required live missing/reappearance uses
maintainer-prepared or separately authorized org changes, never implicit deploy/
deletion permission. The [maintainer-input checklist](../dev/STABLE_010_RELEASE_PLAN.md#maintainer-inputs-and-design-approval)
defines what is needed before real trials and implementation.

After separately authorized delivery/CI, inspect **each required command log** at
the exact candidate/merge SHA and attempt. A green job summary is insufficient.
Verify all selected Linux/macOS/Windows Python 3.12–3.15 cells, complete captures,
cleanup, coverage, metadata/lock, Ruff, Bandit, fresh build/Twine/archive lists and
both independent installs per cell. Retain skipped, cancelled, timed-out,
unacquired and unavailable observations. Skips do not qualify Windows sf,
filesystems, ACLs, power-loss or native Obsidian rendering. Compare actual results
with [qualification](QUALIFICATION.md); preserve earlier failures and uncaptured
causes rather than assigning explanations from later passes.

## Approval and publication

An alpha such as `0.1.0a1` is optional and needs separate preparation/publication
approval. Completion of the old thread list does not trigger stable promotion.
An alpha may state open product gaps accurately, but cannot waive preservation
defects. No alpha issue, artifact or release is created merely by this runbook.

Prepare a concrete reviewable release candidate and evidence checklist. Obtain
maintainer acceptance and explicit permission for each consequential delivery
step: stage/commit, push/PR/merge, tag/release, package upload and hosted-docs
publication. An instruction for one does not authorize the others. Do not expose
tokens or raw private data in logs. Follow current contributor/release templates
and trusted publishing configuration as verified at execution time; never guess
credential or account setup. No credentials belong in config or the repository.

After an authorized publication, verify the exact public artifact/version and
install it independently, check links and release notes, and document accurate
support limits. Preserve a private evidence record and a public-safe summary.
Define security maintenance/version policy explicitly before promising one.
