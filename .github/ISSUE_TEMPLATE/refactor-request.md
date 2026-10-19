---
name: Refactor Request
about: Suggest an internal refactor or maintainability improvement for Obforce
title: "[REFACTOR] <short, descriptive summary>"
labels: refactor
assignees: ''

---

This template creates a public issue. Use synthetic examples and placeholder paths; never include
credentials, tokens, real org metadata, audit identities, vault content, state/recovery files, or
identifying local paths. For suspected vulnerabilities, use GitHub Private Vulnerability Reporting
(Security tab -> Report a vulnerability) if enabled, or an established private maintainer contact.
If no private channel is available, do not post sensitive details publicly.

## Refactor Summary

Describe the maintainability, readability, or internal design improvement you are proposing.

What part of Obforce would benefit from restructuring?

---

## Motivation and Problem Statement

Explain **why** this refactor would help.

Consider including:
- Current pain points (duplication, complexity, coupling, unclear boundaries)
- How the current structure affects testing, debugging, or future work
- Why this is a refactor rather than a bug fix or feature request

---

## Proposed Refactor (Optional)

Describe a possible approach at a high level.

Examples:
- Split a large module into focused modules
- Extract shared logic into helper functions/utilities
- Standardize internal error handling
- Reorganize internal abstractions

⚠️ Keep this high level unless you are confident in the implementation details.

---

## Affected Areas (if known)

Please list any relevant modules, classes, functions, or docs areas.

- Code paths:
- Tests:
- Documentation:

---

## Behavior Expectations

Please check all that apply:

- [ ] No CLI, note-format, or state-schema changes expected
- [ ] No runtime behavior changes expected
- [ ] May improve internal performance without changing outputs
- [ ] May require test updates
- [ ] I am not sure

If you expect user-visible behavior changes, consider filing a feature request or bug report instead.

---

## Risks / Tradeoffs

Describe any known risks, migration concerns, or tradeoffs.

Examples:
- Short-term churn for long-term maintainability
- Renaming or moving internal modules
- Potential merge conflicts with active work

---

## Additional Context

Add any additional context that may help:
- Related issues or PRs
- Code references
- Prior discussions

---

## Willingness to Contribute

- [ ] I am willing to help implement this refactor
- [ ] I can help with testing or validation
- [ ] I am only proposing the idea

---

## Final Notes

Thank you for suggesting maintainability improvements.
Well-scoped refactor requests help keep Obforce healthy over time.
