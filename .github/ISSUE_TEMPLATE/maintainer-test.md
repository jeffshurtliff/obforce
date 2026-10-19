---
name: Maintainer Test
about: Internal test coverage or test-suite improvements for Obforce
title: "[TEST] <brief description>"
labels: maintainer, testing
assignees: []
---

This template creates a public issue. Use synthetic examples and placeholder paths; never include
credentials, tokens, real org metadata, audit identities, vault content, state/recovery files, or
identifying local paths. For suspected vulnerabilities, use GitHub Private Vulnerability Reporting
(Security tab -> Report a vulnerability) if enabled, or an established private maintainer contact.
If no private channel is available, do not post sensitive details publicly.

## Test Summary

Brief description of the test work to be completed.

Examples:
- Add regression coverage for a prior bug
- Improve edge-case coverage
- Refactor fixtures for reliability
- Add tests for existing undocumented behavior

---

## Motivation

Why is this test work needed?

Examples:
- Prevent regressions
- Increase confidence in critical flows
- Cover untested branches
- Improve determinism or reduce flakiness

---

## Scope of Test Changes

Check all that apply:

- [ ] Unit tests
- [ ] Integration tests (mocked / isolated)
- [ ] Regression tests
- [ ] Fixture setup/teardown changes
- [ ] Parameterized scenario expansion
- [ ] Coverage-only initiative
- [ ] Test refactor (no production code changes)

Add notes if needed. Use synthetic fixtures, temporary vaults, and mocked `sf` responses.
Live-org or real-vault tests require separate, explicit maintainer authorization.

---

## Target Scenarios / Risks

List the primary scenarios, edge cases, or risk areas this work should cover.

Examples:
- Partial inventory/dependency coverage and absent audit fields
- Moved/duplicate note identities, unsafe paths, and ownership conflicts
- User-authored prose/properties preserved during refresh
- Dry-run and no-op byte/mtime preservation
- Interrupted note/state writes and rollback preserving intervening edits

---

## Checklist

- [ ] Test scope confirmed
- [ ] Tests added or updated
- [ ] Tests are deterministic and isolated
- [ ] Flakiness risk reviewed
- [ ] CI passes
- [ ] Ready to close

---

## Done When

What conditions must be met for this test work to be considered complete?

Examples:
- Target scenarios are covered
- Regression reproduces and is protected by tests
- Test suite remains stable in CI
