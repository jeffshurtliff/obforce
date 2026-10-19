---
name: Feature Request
about: Suggest a new feature or enhancement for Obforce
title: "[FEATURE] <short, descriptive summary>"
labels: enhancement
assignees: ''

---

This template creates a public issue. Use synthetic examples and placeholder paths; never include
credentials, tokens, real org metadata, audit identities, vault content, state/recovery files, or
identifying local paths. For suspected vulnerabilities, use GitHub Private Vulnerability Reporting
(Security tab -> Report a vulnerability) if enabled, or an established private maintainer contact.
If no private channel is available, do not post sensitive details publicly.

## Feature Summary

Provide a clear and concise description of the feature or enhancement you are requesting.

What problem does this solve, or what capability does it add?

---

## Motivation and Use Case

Explain **why** this feature is needed.

Consider including:
- The real-world scenario you are trying to support
- Current limitations or workarounds
- Who would benefit from this feature (e.g., Salesforce administrators, developers, knowledge maintainers)

---

## Proposed Solution

Describe how you envision this feature working.

If applicable, include:
- New or modified CLI commands/options
- Expected inputs and outputs
- Configuration options
- Behavioral changes

---

## Example Usage (if applicable)

Provide an example of how this feature might be used.

```python
# Example of proposed usage
```

⚠️ This is illustrative only — implementation details may change.

---

## Alternatives Considered

Describe any alternative approaches or solutions you have considered, including:
- Existing Obforce functionality
- Existing Salesforce documentation or Obsidian tools
- Other libraries or custom implementations

---

## Impact and Scope

Please indicate the expected impact of this feature:

- [ ] Backward-compatible
- [ ] Requires a breaking change
- [ ] Affects Salesforce access, note ownership, or refresh/recovery safety
- [ ] Introduces new dependencies
- [ ] Impacts performance, metadata coverage, or input/output limits

Add details where relevant.

---

## Salesforce / Vault Context (if applicable)

If this feature relates to metadata generation or refresh, include synthetic, high-level context:

- Command / mode involved:
- Source mode (live Salesforce or offline DX project):
- Metadata type(s), scope, and coverage limitations:
- Note ownership, user-content preservation, or template considerations:
- Operating system / filesystem constraints:

⚠️ Do not include credentials, real org metadata, audit identities, vault content, or identifying paths.

---

## Additional Context

Add any other context that may be helpful:
- Links to Salesforce, Obsidian, Click, Jinja2, or YAML documentation
- Prior discussions or related issues
- Screenshots or diagrams (if applicable)

---

## Willingness to Contribute

- [ ] I am willing to help implement this feature
- [ ] I can help with testing or documentation
- [ ] I am only proposing the idea

---

## Final Notes

Thank you for taking the time to suggest an improvement to Obforce.
Thoughtful feature requests help guide the project’s roadmap and priorities.
