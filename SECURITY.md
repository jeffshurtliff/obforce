# Security and privacy

Obforce is under development; no stable release or supported-version security
maintenance window has been established. The current version collects selected
ApexClass metadata read-only and publishes local documentation through guarded
recoverable writes.

Report suspected vulnerabilities through GitHub Private Vulnerability Reporting
in the repository Security tab if enabled, or an established private maintainer
contact. If neither is available, request a private channel without posting
sensitive details publicly. No response-time commitment is promised.

## Private data and authorization

Never post credentials, tokens, authentication URLs, raw CLI replies, real org
metadata, internal endpoints, audit identities, vaults, state or recovery files.
Use fictional minimal reproductions and placeholder paths. Removing an org name
alone does not sanitize metadata or human-authored documentation.

Obforce uses an explicitly selected, separately installed Salesforce CLI and its
existing authorization. It does not implement OAuth, discover credentials or
log in. Live build/sync and their previews can query Salesforce. Select the target,
trusted absolute executable and neutral directory explicitly. An alias alone is
not verified org identity or proof of permission continuity. sf can maintain its
own auth/config/cache/log files even during a preview. Windows sf execution is refused.

Normal generation has no AI service, telemetry, hosted storage or automatic
upload. Offline runtime makes no network calls. Installation/build dependencies
may require downloads; these are separate from application runtime. Keep ignored
`local/` references private and never commit secrets or real generated output.

`.obforce/state.json` is **unencrypted private local data**. It retains normalized
facts and graph evidence, including canonical org/record IDs and optional audit
display names. Recovery before-images can contain complete human notes. Turning
off audit names does not erase retained absent records or existing before-images.
Protect the whole vault, state and recovery material with appropriate local
access controls and separately managed backups. No automatic retention erasure,
backup, Git integration or migration is provided.

## Trust and refusal boundaries

Use stable trusted private local ancestry for application, source, template and
vault roots. Keep them disjoint. Avoid concurrent changes during scans; the
application intentionally refuses unexpected ancestor changes, links/junctions,
special files, collisions and unsafe ownership. Do not bypass refusals with
symlinks, control-file deletion, retries that weaken guards, or state editing.
Ordinary reads are not an atomic filesystem snapshot.

Templates are explicitly chosen local code-like input with finite interpolation
and output limits. Source metadata cannot select templates. The Jinja sandbox
alone is not a complete resource-security boundary. XML DTD/entities/external
references, unsafe YAML tags/aliases/merges, duplicate keys and unsupported
structures are refused. Bounds refuse rather than truncate. See
[rendering](docs/RENDERING.md), [note format](docs/NOTE_FORMAT.md) and
[synchronization safety](docs/SYNC_SAFETY.md).

Generated-property/body edits and dashboard edits block the complete batch.
There is no force overwrite or automatic adoption. Publication revalidates a
complete immutable plan and fresh integrity observations, takes a continuous
writer guard, stages on the same filesystem and retains recovery evidence.
Per-file replacement is not atomic multi-file publication. Cooperating locks do
not exclude hostile editors. Synthetic/native-hosted checks do not establish
power-loss durability, Windows ACL/directory-fsync guarantees, forged/coarse
change detection or arbitrary filesystem support.

Start recovery with a read-only [preview](docs/RECOVERY.md). Intervening edits,
unknown/legacy journals and ambiguous evidence are retained for manual resolution.
Do not attach them to public issues or delete them to unblock ordinary writes.
See [qualification](docs/QUALIFICATION.md) for actual results, skips and unavailable
checks. Native Obsidian preview and live Salesforce verification are separate
from offline schema/fixture tests.
