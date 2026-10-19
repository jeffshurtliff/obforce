---
name: Maintainer CI
about: Internal CI, automation, or workflow updates for Obforce
title: "[CI] <brief description>"
labels: maintainer, ci
assignees: []
---

This template creates a public issue. Use synthetic examples and placeholder paths; never include
credentials, tokens, real org metadata, audit identities, vault content, state/recovery files, or
identifying local paths. For suspected vulnerabilities, use GitHub Private Vulnerability Reporting
(Security tab -> Report a vulnerability) if enabled, or an established private maintainer contact.
If no private channel is available, do not post sensitive details publicly.

## CI Summary

Brief description of the CI/workflow change to be made.

---

## Motivation

Why is this CI change needed?

Examples:
- Fix failing workflow behavior
- Improve reliability or speed
- Expand test matrix coverage
- Improve security scanning
- Support release automation

---

## Affected Automation / Pipelines

Check all that apply:

- [ ] GitHub Actions workflow(s)
- [ ] Test matrix / Python versions
- [ ] Release workflow / publishing
- [ ] Dependabot configuration
- [ ] CodeQL / security scanning
- [ ] Coverage reporting / uploads
- [ ] Docs validation / build automation (if configured)
- [ ] Other CI/CD configuration (please specify)

Add file paths or workflow names if known.

---

## Proposed Changes

Outline the planned CI/pipeline modifications at a high level.

Optional notes:
- Trigger changes (push, PR, tags, manual)
- Job dependency changes
- Cache behavior
- Secret/permission scope changes
- Artifact handling

---

## Validation Plan

How will this change be verified?

Examples:
- Test run on PR branch
- Matrix job success on supported versions
- Dry-run release validation
- Expected artifacts generated

---

## Risks / Rollback Considerations

Capture any risks and how to recover if the change causes failures.

Examples:
- Blocks merges if workflow misconfigured
- Requires secrets/permissions changes
- May affect fork PR behavior

---

## Checklist

- [ ] Scope confirmed
- [ ] Workflow/config changes implemented
- [ ] Validation performed
- [ ] Documentation updated (if applicable)
- [ ] Rollback considerations reviewed
- [ ] Ready to close

---

## Done When

What conditions must be met for this CI task to be considered complete?

Examples:
- Workflow behaves as intended
- CI reliability improves or issue is resolved
- Release or scanning automation runs successfully
