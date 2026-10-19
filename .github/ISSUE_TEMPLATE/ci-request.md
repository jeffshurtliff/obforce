---
name: CI Request
about: Request a CI/workflow improvement or report a non-code pipeline issue for Obforce
title: "[CI] <short, descriptive summary>"
labels: ci
assignees: ''

---

This template creates a public issue. Use synthetic examples and placeholder paths; never include
credentials, tokens, real org metadata, audit identities, vault content, state/recovery files, or
identifying local paths. For suspected vulnerabilities, use GitHub Private Vulnerability Reporting
(Security tab -> Report a vulnerability) if enabled, or an established private maintainer contact.
If no private channel is available, do not post sensitive details publicly.

## CI Request Summary

Describe the CI/workflow issue or enhancement request.

Examples:
- Failing GitHub Actions workflow
- Slow or flaky pipeline step
- Missing automation or release check
- Matrix/configuration improvement

---

## Current Behavior

What is happening now?

If applicable, include:
- Workflow/job name
- Trigger type (push, PR, tag, manual)
- Failure mode or unexpected behavior

---

## Desired Outcome

Describe what should happen instead.

Examples:
- Job should pass under supported versions
- New CI check should run on pull requests
- Release workflow should validate artifacts before publish

---

## Affected CI Areas (if known)

Check all that apply:

- [ ] GitHub Actions workflows
- [ ] Test matrix / Python versions
- [ ] Release automation
- [ ] Dependabot
- [ ] Security scanning (CodeQL/Bandit/etc.)
- [ ] Coverage reporting
- [ ] Docs build automation
- [ ] I am not sure

---

## Logs / Error Output (Redacted)

Paste relevant excerpts from CI logs or error messages.

```text
Paste CI log excerpts here (redacted)
```

⚠️ Do not include secrets, tokens, or private repository details.

---

## Trigger / Environment Context (Optional)

Add any context that may affect reproduction:
- Branch or PR type
- Fork vs repository branch
- Python version(s)
- OS runner (ubuntu, macos, windows)
- Event trigger (push/pull_request/workflow_dispatch/tag)

---

## Additional Context

Add links to failed runs, related issues, or prior PRs if available.

---

## Willingness to Contribute

- [ ] I am willing to help diagnose or test a fix
- [ ] I can provide additional logs or reproduction details
- [ ] I am only reporting the CI issue/request

---

## Final Notes

Thank you for helping improve CI reliability and automation quality.
Clear CI reports help maintainers diagnose pipeline issues quickly.
