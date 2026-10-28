# Explicit live setup

In the current version, live collection documents selected ApexClass metadata
using a trusted Salesforce CLI on supported POSIX execution paths.
**Windows sf execution remains refused.**
Offline tests use mocked responses; they do not qualify access to your org.
The commands here are documentation examples, not executed live validation.

## Manage Salesforce CLI separately

Install and authorize sf yourself using the official
[Salesforce CLI setup guidance](https://developer.salesforce.com/docs/platform/sfdx-setup/guide/sfdx-setup-install-cli.html)
and [authorization guidance](https://developer.salesforce.com/docs/platform/sfdx-dev/guide/sfdx-dev-auth.html),
following your organization's access/security policy. Authorization and login are
outside Obforce. Obforce reuses existing CLI authorization; it does not log in,
implement OAuth, inspect credential stores or select a default org.

Authorize only read-only metadata/audit collection for the intended target.
Select an explicit alias/username, trusted absolute sf executable and existing
absolute neutral working directory outside projects/vaults/templates. No
executable or auth discovery occurs. The adapter independently queries actual
Organization identity before collection and compares it with saved state.
Aliases alone are not stable identities. Obforce does not deploy, execute Apex,
change org configuration or request Apex bodies for these notes.

## Create a separate live config

Do not convert the offline tutorial config or reuse its vault. Replace all
fictional placeholders below with reviewed selections only after authorization:

```sh
obforce init --config "/absolute/Live Workspace/live.toml" --org fictional-sandbox --vault "./Knowledge" --workspace-id fictional-live --dry-run
obforce init --config "/absolute/Live Workspace/live.toml" --org fictional-sandbox --vault "./Knowledge" --workspace-id fictional-live
obforce build --config "/absolute/Live Workspace/live.toml" --sf-executable "/absolute/trusted/bin/sf" --sf-directory "/absolute/Neutral CLI Work" --inventory-scope-id fictional-reader-v1 --dry-run
obforce build --config "/absolute/Live Workspace/live.toml" --sf-executable "/absolute/trusted/bin/sf" --sf-directory "/absolute/Neutral CLI Work" --inventory-scope-id fictional-reader-v1
```

The config parent and neutral directory must already exist. Init validates
selection without querying sf; build and its preview perform read queries.
Review config before build: `include_namespaced` defaults false and
`include_audit_names` defaults true. Set the latter false when display names are
unnecessary. Audit availability is independent of inventory. API version and
query shapes are bounded by the implementation, not user-injected SOQL.

## Refresh and comparability

```sh
obforce sync --config "/absolute/Live Workspace/live.toml" --sf-executable "/absolute/trusted/bin/sf" --sf-directory "/absolute/Neutral CLI Work" --inventory-scope-id fictional-reader-v1 --attest-comparable-inventory --dry-run
obforce sync --config "/absolute/Live Workspace/live.toml" --sf-executable "/absolute/trusted/bin/sf" --sf-directory "/absolute/Neutral CLI Work" --inventory-scope-id fictional-reader-v1 --attest-comparable-inventory
```

Use the attestation only if you can establish accessible inventory continuity
from build through every retained observation, including partial scans. It is a
human assertion, not automatic permission verification. The optional build scope
ID is immutable; sync cannot introduce or change it. A build without one can
refresh while preserving absences, but cannot later establish missing evaluation
through a scope reset/rebaseline.

Matching org/Selection/method/API, complete exhausted/no-limit/no-warning inventory
and a matching scope declaration plus attestation are all required to mark absent
components missing. Missing means unobserved in the selected accessible scope,
not proven deletion. A positive same-source observation can reactivate a missing
note without attesting absence. No component note is deleted. See
[refresh semantics](REFRESH.md) for exact refusal/preservation rules.

Inventory, audit and relationships report independent coverage. Platform
relationships remain partial/unavailable even after clean empty responses;
platform-reported references do not prove runtime behavior or full impact.
Requested incomplete results can complete with exit 4. Review all dimensions.

Live previews create no Obforce artifacts, but sf can maintain its own auth,
configuration, cache or logs. State retains private normalized facts/graph and
optional names across invocations; disabling names does not erase retained
records or recovery images. See [security](../SECURITY.md). No source-mode,
workspace, verified-org or Selection rebinding/adoption/migration is provided.
A live-only `--org` override must resolve to the same saved org; it cannot switch
an existing vault. Use a separately selected empty destination for a different
source, without claiming old UUID or human-content transfer.
