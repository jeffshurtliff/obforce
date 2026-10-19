---
name: Security Report
about: Report a potential security concern in Obforce (public fallback; sanitize details)
title: "[SECURITY] <short, sanitized summary>"
labels: security
assignees: ''

---

This template creates a public issue. Use synthetic examples and placeholder paths; never include
credentials, tokens, real org metadata, audit identities, vault content, state/recovery files, or
identifying local paths. For suspected vulnerabilities, use GitHub Private Vulnerability Reporting
(Security tab -> Report a vulnerability) if enabled, or an established private maintainer contact.
If no private channel is available, do not post sensitive details publicly.

## Important: Public Issue Warning

This issue template creates a **public GitHub Issue**.

For real or suspected vulnerabilities, use **GitHub Private Vulnerability Reporting** (Security tab
-> **Report a vulnerability**) if enabled. If unavailable, use an established private
maintainer contact. If neither is available, withhold sensitive details; availability is not assumed.

Use this public template only if:
- You are sharing a **sanitized, non-sensitive** security concern / hardening suggestion, and
- The report contains no sensitive vulnerability details, even if private reporting is unavailable

⚠️ Do **not** include secrets, proof-of-concept exploit payloads, private endpoints, real vault
content, state/recovery files, audit identities, or identifying local paths, or step-by-step exploit instructions.

---

## Reporter Checklist

- [ ] I understand this issue will be public
- [ ] I have not included secrets or sensitive data
- [ ] I have sanitized logs, examples, and environment details
- [ ] This report is safe to discuss publicly at a high level

If any box cannot be checked, please use a private reporting channel instead.

---

## Security Concern Summary (Sanitized)

Provide a short, high-level description of the concern.

Examples:
- Potential input validation weakness
- Sensitive data may be logged under certain conditions
- Insecure default configuration or behavior

---

## Potential Impact (High Level)

Describe the possible impact without including exploit details.

Examples:
- Salesforce credential, private metadata, or audit-identity exposure risk
- Loss or overwrite of user-authored notes/properties
- Injection risk
- Privilege or access control weakness
- Data leakage in logs/errors

---

## Affected Versions / Components (if known)

- Obforce version(s):
- Python version(s):
- Affected module(s) / functionality:
- Environment constraints:

---

## Reproduction Context (High Level Only)

Describe the general conditions under which the issue may occur.

Do **not** include:
- Secrets or tokens
- Full exploit payloads
- Detailed attack instructions
- Identifying local paths or real vault content

```text
High-level reproduction context (sanitized)
```

---

## Evidence / Logs (Redacted, Optional)

If helpful, include **sanitized** log excerpts or error messages.

```text
Paste redacted logs or messages here
```

---

## Suggested Mitigation / Hardening (Optional)

If you have ideas for a fix or mitigation, describe them at a high level.

Examples:
- Input sanitization/validation
- Redaction of sensitive fields in logs
- Safer defaults
- Additional permission checks

---

## Coordination Preference (Optional)

- [ ] I can provide additional details privately if a maintainer requests them
- [ ] I am willing to help validate a fix
- [ ] I prefer not to be contacted beyond issue updates

---

## Additional Context

Add any other context that may help triage this report safely.

---

## Acknowledgements

Thank you for taking the time to report security concerns responsibly.
Sanitized reports and private disclosures both help improve Obforce safely.
