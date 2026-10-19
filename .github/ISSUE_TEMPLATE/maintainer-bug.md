---
name: Maintainer Bug
about: Internal bug tracking for Obforce maintainers
title: "[BUG] <brief description>"
labels: maintainer, bug
assignees: []
---

This template creates a public issue. Use synthetic examples and placeholder paths; never include
credentials, tokens, real org metadata, audit identities, vault content, state/recovery files, or
identifying local paths. For suspected vulnerabilities, use GitHub Private Vulnerability Reporting
(Security tab -> Report a vulnerability) if enabled, or an established private maintainer contact.
If no private channel is available, do not post sensitive details publicly.

## Bug Summary

Brief description of what is broken or behaving incorrectly.

---

## Observed Behavior

What is currently happening?
Include error messages or incorrect behavior at a high level.

---

## Root Cause (if known)

Describe the underlying cause of the issue.

⚠️ If the root cause is not yet known, capture initial hypotheses or investigation notes instead.

---

## Fix Plan

Outline the steps required to fix the bug.

Examples:
- Code changes needed
- Refactor or guard conditions
- Dependency or version adjustments

---

## Regression Coverage

- [ ] New test added to cover this bug
- [ ] Existing test updated
- [ ] Manual verification only (please explain)

If applicable, note the test location or scenario covered.

---

## Checklist

- [ ] Bug fixed
- [ ] Regression risk evaluated
- [ ] Tests passing
- [ ] Documentation updated (if applicable)
- [ ] Ready to close

---

## Done When

What conditions must be met for this bug to be considered resolved?

Examples:
- Repro no longer possible
- Test fails before fix and passes after
- No related regressions observed
