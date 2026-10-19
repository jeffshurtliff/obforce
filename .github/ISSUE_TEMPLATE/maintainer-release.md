---
name: Maintainer Release
about: Internal tracking for preparing an Obforce stable release candidate and separately authorized publication
title: "[CHORE] Prepare Obforce <version> stable release"
labels: maintainer, chore
assignees: []
---

This template creates a public issue. Use synthetic examples and placeholder paths; never include
credentials, tokens, real org metadata, audit identities, vault content, state/recovery files, or
identifying local paths. For suspected vulnerabilities, use GitHub Private Vulnerability Reporting
(Security tab -> Report a vulnerability) if enabled, or an established private maintainer contact.
If no private channel is available, do not post sensitive details publicly.

## Release Summary

Prepare a reviewable release candidate. Stable-version promotion and publication
require separate, explicit maintainer instructions.

- Current version (from): `X.Y.Z.devN`
- Target stable version (to): `X.Y.Z`
- Target release date, if agreed: `YYYY-MM-DD`

Follow [AGENTS.md](https://github.com/jeffshurtliff/obforce/blob/main/AGENTS.md) and
[the implementation roadmap](https://github.com/jeffshurtliff/obforce/blob/main/dev/IMPLEMENTATION_PLAN.md).
Review root `CONTRIBUTING.md` and `docs/maintainers/releasing.md` when established;
resolve missing release guidance or tooling before preparing candidate artifacts.

---

## Motivation

Why is this release being prepared now? Link completed work, relevant
issues, and pull requests. Identify any remaining release blockers.

---

## Release Facts to Confirm

Resolve values from actual metadata, code, and validation; do not guess.

- Distribution name: `obforce`
- Primary branch (verify against the repository):
- Previous stable tag, if any:
- Target tag and tag convention (confirm before tagging):
- Release branch (confirm contributor conventions): `codex/chore/prepare-<version>-release` for Codex;
  include an issue number only when an actual linked issue exists
- Next development version, if separately requested:
- Supported Python versions and dependency floors: current `pyproject.toml` and CI
- Note/state schema compatibility, user-content preservation, recovery, and security considerations:
- Offline/live inventory, audit, and dependency coverage limitations:
- External publishing prerequisites still unconfigured or unverified:

---

## Change Set Since Last Stable Tag

Summarize features, fixes, security work, breaking changes, dependency changes,
and Python support changes. For the first release, describe the initial scope
without inventing a previous stable tag.

---

## Authorization Checkpoints

An issue or preparation request does not grant any of these permissions. Record
explicit maintainer authorization for each action separately:

- [ ] Promote the development version to the requested stable version
- [ ] Stage changes
- [ ] Commit changes
- [ ] Push the release branch
- [ ] Open the preparation pull request
- [ ] Merge the preparation pull request
- [ ] Create a release tag
- [ ] Push the release tag
- [ ] Upload distributions to TestPyPI (optional rehearsal)
- [ ] Upload distributions to production PyPI
- [ ] Create a GitHub Release
- [ ] Publish a GitHub Release
- [ ] Configure or activate external publication automation

Prepare a concrete manual publication procedure for maintainer review. Verify the actual
repository workflows and external prerequisites; no publishing automation is assumed to exist.
Any automation requires separate authorization before configuration or activation.

---

## Checklist

Preparation (local and reviewable):

- [ ] Dependencies verified; scope, version and publication method confirmed
- [ ] Base branch verified; existing user changes preserved
- [ ] Version edits limited to explicitly requested changes; lock regenerated through Poetry if needed
- [ ] Changelog, docs, version metadata, and compatibility policy reviewed
- [ ] Available Poetry lock, Ruff lint/format, pytest, Bandit, documentation, and whitespace checks pass
- [ ] One fresh wheel and sdist built in an isolated candidate directory
- [ ] Strict Twine checks, archive contents, metadata, and checksums verified
- [ ] Each artifact installed with dependencies outside the checkout
- [ ] Installed console/module help and synthetic offline build/edit/refresh/no-op/recovery lifecycle verified
- [ ] Packaged templates and Bases resources verified from both installed artifact formats
- [ ] No credentials, real org metadata, vault data, state/recovery files, or private clutter in candidate archives
- [ ] Maintainer runbook and safe publication workflow proposal reviewed
- [ ] Unexecuted hosted checks and external prerequisites reported explicitly

Publication (only through the separately authorized, reviewed procedure):

- [ ] Required CI and release checks pass for the exact release commit
- [ ] Tag, version, changelog, and verified artifacts agree
- [ ] Authorized distribution upload completed and clean installation verified
- [ ] Authorized GitHub Release completed with verified artifacts
- [ ] Documentation publication verified if separately authorized
- [ ] Next development cycle handled as separate work if requested

---

## Done When

State whether this issue covers preparation only or separately authorized
publication. Preparation is complete when candidate artifacts and the runbook
are validated and remaining external blockers are explicit. Publication is
complete only after the authorized steps are verified; do not close a
publication milestone on the strength of local preparation alone.
