---
name: Test Request
about: Request new or improved test coverage for Obforce
title: "[TEST] <short, descriptive summary>"
labels: testing
assignees: ''

---

This template creates a public issue. Use synthetic examples and placeholder paths; never include
credentials, tokens, real org metadata, audit identities, vault content, state/recovery files, or
identifying local paths. For suspected vulnerabilities, use GitHub Private Vulnerability Reporting
(Security tab -> Report a vulnerability) if enabled, or an established private maintainer contact.
If no private channel is available, do not post sensitive details publicly.

## Test Request Summary

Describe the test coverage gap or test-suite improvement you are requesting.

What behavior, edge case, or scenario should be tested?

---

## Why This Test Work Is Needed

Explain **why** this testing request matters.

Examples:
- Prevent regression for a known issue
- Increase confidence in a critical code path
- Cover edge cases not currently tested
- Reduce flaky behavior in CI

---

## Target Behavior / Scenario

Describe the behavior or conditions that should be validated.

If applicable, include:
- Inputs
- Expected outputs
- Error conditions
- Boundary/edge cases

---

## Suggested Test Scope (if known)

Check all that apply:

- [ ] Unit tests
- [ ] Regression tests
- [ ] Integration-style tests (isolated/mocked)
- [ ] Fixture improvements
- [ ] Parameterized cases
- [ ] CI reliability/flakiness checks
- [ ] I am not sure

---

## Reproduction / Example Data (Optional)

Provide a minimal example, failing scenario, or pseudocode that shows what should be tested.

```python
# Optional example scenario or expected test shape
```

Use synthetic metadata, temporary vaults, and mocked `sf` responses. Live-org or real-vault
tests require separate, explicit maintainer authorization.

⚠️ Do not include credentials, real org metadata, audit identities, vault content, or identifying paths.

---

## Acceptance Criteria (Optional)

How should maintainers know this request is complete?

Examples:
- Specific edge case is covered
- Regression test added for issue #...
- Flaky path becomes stable across repeated CI runs

---

## Additional Context

Add any other context that may help:
- Related issues or PRs
- Affected commands, source modes, metadata coverage, or note/state behavior
- Prior failures or flaky runs

---

## Willingness to Contribute

- [ ] I am willing to help write tests
- [ ] I can help reproduce or validate scenarios
- [ ] I am only reporting the coverage gap

---

## Final Notes

Thank you for helping improve test coverage and reliability in Obforce.
Focused test requests help prevent regressions and strengthen releases.
