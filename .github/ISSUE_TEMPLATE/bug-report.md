---
name: Bug Report
about: Report a bug or unexpected behavior in Obforce
title: "[BUG] <short, descriptive summary>"
labels: bug
assignees: ''

---

This template creates a public issue. Use synthetic examples and placeholder paths; never include
credentials, tokens, real org metadata, audit identities, vault content, state/recovery files, or
identifying local paths. For suspected vulnerabilities, use GitHub Private Vulnerability Reporting
(Security tab -> Report a vulnerability) if enabled, or an established private maintainer contact.
If no private channel is available, do not post sensitive details publicly.

## Bug Description

Provide a clear and concise description of the bug.
What happened, and what did you expect to happen instead?

---

## Steps to Reproduce

Please provide **exact steps** so the issue can be reproduced reliably.

1. …
2. …
3. …

If applicable, include:
- Command and mode used
- Relevant options with placeholder paths
- Source mode (live Salesforce or offline DX project); use a fictional org alias if needed
- Inventory/dependency coverage warnings, if any
- Whether user-authored content, generated content, or both were affected

---

## Expected Behavior

Describe what you expected to happen.

---

## Actual Behavior

Describe what actually happened, including any error messages or unexpected results.

---

## Code Sample (if applicable)

Please include a **minimal, reproducible example**.

```python
# Example code that triggers the issue
```

⚠️ **Do not include secrets or private data** (tokens, org metadata, audit identities, vault content, identifying paths, etc.).

---

## Environment Details

Please complete the following information:

- **Obforce version**:
- **Python version** (e.g. 3.12.7):
- **Salesforce CLI version** (live mode, if applicable):
- **Obsidian version** (display/link issues, if applicable):
- **Operating system**:
- **Installation method**:
  - [ ] pip
  - [ ] Poetry
  - [ ] Other (please specify)
- **Virtual environment**:
  - [ ] venv
  - [ ] virtualenv
  - [ ] Conda
  - [ ] Poetry
  - [ ] Other (please specify)
  - [ ] None

---

## Traceback / Logs

If applicable, include the **sanitized traceback or relevant logs** below.

```text
Paste redacted traceback or logs here
```

---

## Security Considerations

- [ ] I have verified this issue does **not** expose credentials or sensitive data
- [ ] This issue is **not** a security vulnerability (if it is, please do **not** file a public issue)

If this may be security-related, please report it responsibly instead of filing a public issue.

---

## Additional Context

Add any other context that may help diagnose the problem:
- Workarounds you’ve tried
- Related issues or PRs
- Source-project/vault layout and filesystem constraints (at a high level; synthetic)

---

## Acknowledgements

Thanks for taking the time to report this issue — detailed reports help make Obforce better for everyone.
