---
name: Maintainer Refactor
about: Internal refactor tracking for Obforce maintainers
title: "[REFACTOR] <brief description>"
labels: maintainer, refactor
assignees: []
---

This template creates a public issue. Use synthetic examples and placeholder paths; never include
credentials, tokens, real org metadata, audit identities, vault content, state/recovery files, or
identifying local paths. For suspected vulnerabilities, use GitHub Private Vulnerability Reporting
(Security tab -> Report a vulnerability) if enabled, or an established private maintainer contact.
If no private channel is available, do not post sensitive details publicly.

## Refactor Summary

Brief description of the internal refactor or structural improvement.

---

## Motivation

Why is this refactor needed?
Examples:
- Reduce complexity or duplication
- Improve maintainability or readability
- Improve testability
- Prepare for future feature work
- Normalize patterns across modules

---

## Current Pain Points

Describe the current technical debt, design issue, or code smell being addressed.

Examples:
- Overly large module or function
- Repeated logic across classes
- Inconsistent error handling
- Tight coupling that blocks testing

---

## Proposed Scope / Approach

High-level notes on how the refactor should be performed.

Optional considerations:
- Modules, classes, or functions to restructure
- Extraction or consolidation targets
- Naming or organization changes
- Migration sequencing (if needed)

⚠️ Capture implementation intent, not a full design document.

---

## Behavior Preservation

Document the expectations for behavioral stability.

- [ ] No CLI, note-format, or state-schema changes expected
- [ ] No runtime behavior changes expected
- [ ] Test suite should pass unchanged (aside from refactor-related test updates)
- [ ] Behavior changes are intentional and documented (if applicable)

Add notes if any exceptions apply.

---

## Checklist

- [ ] Refactor scope confirmed
- [ ] Implementation complete
- [ ] Tests added or updated (if applicable)
- [ ] Regression risk reviewed
- [ ] Documentation updated (if applicable)
- [ ] Ready to close

---

## Done When

What conditions must be met for this refactor to be considered complete?

Examples:
- Code duplication removed or reduced
- Structure is clearer and easier to maintain
- Tests pass with no behavioral regressions
