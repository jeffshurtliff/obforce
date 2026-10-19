# Security and privacy

Obforce is under development. No stable release or supported-version security
maintenance window has been established. The current foundation provides local
help/version reporting; Salesforce collection and vault mutation are planned.

Report suspected vulnerabilities through GitHub Private Vulnerability Reporting
in this repository's Security tab if enabled, or an established private maintainer
contact. If neither is available, request a private channel without posting
sensitive details in a public issue. Do not assume a response-time commitment.

Never post credentials, tokens, authentication URLs, real org metadata, audit
identities, internal endpoints, vault content, state, or recovery files. Use
fictional minimal reproductions and placeholder paths. Removing an org name alone
does not sanitize metadata or human-authored documentation.

Normal generation is intended to remain local, reuse explicitly selected existing
Salesforce CLI authentication, and avoid telemetry, AI services, hosted storage,
and credential collection. These are design constraints, not claims that the
future source/writer safety boundaries are implemented. Real org or vault tests
require separate explicit authorization. Keep private material in ignored
`local/` and use independent vault backups when those workflows become available.
