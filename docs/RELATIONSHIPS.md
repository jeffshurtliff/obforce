# Internal platform relationships and directed graph

Thread 06 adds `sources/relationships.py` and `graph/dependencies.py`, with synthetic
fixtures and mocked CLI collection. There is no public command, real org
validation, static analysis, new component note type, state loading or publication.
Internal interfaces are versioned implementation details. Thread 06 is accepted
and delivered at implementation `d1134fa` / merge `2aa8d2b`; #6 is closed as completed.

Exact-merge [run 39431345348, attempt 1](https://github.com/jeffshurtliff/obforce/actions/runs/39431345348)
passed all 12 Linux/macOS/Windows Python 3.12–3.15 cells. Linux/macOS each reported
517 passed; Windows each reported 506 passed/11 expected skips. Every cell passed
standalone metadata/lock, lint, formatting, Bandit, fresh builds, strict Twine,
both independent artifact installations and whitespace. The Windows skips are
nine POSIX collector cases, one POSIX wrapper-symlink case and the unavailable
FIFO case. Mocked graph/adapter/refusal and installed artifact checks do not
qualify Windows sf execution or actual Salesforce capability/exhaustion. The
release limitation below is retained. See the
[acceptance record](../dev/IMPLEMENTATION_PLAN.md#thread-06-acceptance-and-closure--20-october-2026).
Thread 07 now adds internal [candidate rendering](RENDERING.md); acceptance is
pending and #7 remains open.

## Direction, endpoints and provenance

`MetadataComponent*` is the **referencing source**; `RefMetadataComponent*` is the
**referenced target**. One normalized `Edge` supplies both `references(key)` and
`referenced_by(key)`. A → B therefore affects A's outgoing and B's incoming view.
Self-edges and both directions of cycles are retained without recursive traversal.
These are platform-reported references, never proof of runtime behavior or
comprehensive impact analysis.

Each private endpoint retains type, namespace, name and record ID, including null
values. Resolution requires an exact supported ApexClass ID/type/name/namespace
match against the supplied selected live inventory. Apex IDs normalize from
validated 15-character or checksum-verified 18-character form to 18 characters;
queries use only canonical 18-character IDs. Empty reported namespace normalizes
to null. Namespace/case distinctions remain significant. No name-only match,
namespace inference, default org or cross-source mapping is attempted.

Unmatched supported endpoints are `external`; missing identity/type/name data
remains `unresolved`; other component types are `unsupported`; contradictory
known-ID/name/namespace descriptors are `identity_mismatch`. All stay explicit
private descriptors. This includes unsupported **referencing** endpoints in
incoming views, such as a fictional Flow → ApexClass observation. No additional
component record/note is generated. A resolved key identifies an inventory
component, not ownership of a note; later rendering may link only through an
explicit validated managed-note mapping. There is no note discovery or adoption.

Exact directed pairs are deduplicated. Each retains a sorted set of distinct
method/coverage/stale observations, including separate outgoing/incoming probe
provenance. Contradictory descriptors remain separate edges; contradictory
coverage remains separate evidence. Response ordering, duplicates, raw attributes,
incidental endpoints and collection times do not change semantic hashes. Raw
records, warning text, stderr, selectors and URLs are not retained in graph
results or diagnostics. Endpoint descriptors and canonical payloads are private
metadata and must not be logged or copied into public reports.

The graph-specific endpoint/evidence records support unresolved sources without
changing frozen `ComponentKey`, `Relationship`, component/scope hashes, ownership
or note/state schemas. The existing Relationship record continues to represent
resolved-source evidence. State serialization/validation remains Thread 09.

## Fixed collection and independently verified identity

The caller supplies the explicit executable, neutral existing working directory,
explicit target and a normalized `LiveInventory`. It must separately obtain
live authorization for that target and those operations. The adapter reissues
Thread 05's exact `SELECT Id FROM Organization LIMIT 2` and requires consistent
complete identity evidence plus the same verified org/workspace binding as the
inventory. Incompatible prior source/selection is refused before queries.
Retargeting an alias cannot rebind the graph. Separate calls still require stable
trusted CLI/auth configuration and accessible metadata scope; they are not an
atomic metadata/auth snapshot.

For each selected, validated Apex ID, in sorted ID order, issue exactly one
outgoing and one incoming Tooling query. The fixed eight-field projection is:

```sql
SELECT MetadataComponentId, MetadataComponentName,
       MetadataComponentNamespace, MetadataComponentType,
       RefMetadataComponentId, RefMetadataComponentName,
       RefMetadataComponentNamespace, RefMetadataComponentType
FROM MetadataComponentDependency
WHERE MetadataComponentId = '<validated 18-character Apex ID>'
  AND MetadataComponentType = 'ApexClass'
```

Actual queries are single-line; incoming probes use `RefMetadataComponentId` and
`RefMetadataComponentType` in the same equality structure. Unselected opposite
endpoints are retained as external/unsupported descriptors. An anchor outside
the query's fixed ID/type filter is a conflict. A conflicting anchor name or
namespace remains unresolved evidence with explicit contradiction coverage.
Missing projected keys, unexpected fields or malformed values cause typed
validation refusal. Reported null remains distinct from a missing key.

No body, symbol table, unrelated User/customer data, name filter, keyset/range,
IN, COUNT, ORDER BY, OFFSET, arbitrary endpoint, continuation, Bulk API, query file
or alternative transport is used. The accepted [CLI boundary](SF_CLI.md) retains
its executable/target/working-directory controls, JSON/byte/time gates, cleanup,
redaction and Windows refusal. `_Session` now accepts internal budget overrides;
Thread 05 defaults and offline acquisition behavior remain unchanged.

| Application boundary | Maximum |
| --- | --- |
| Queries, including identity | 101 total; at most 100 relationship probes |
| CLI replies per selected ID/direction | 1; no supported continuation strategy |
| Returned relationship rows before deduplication | 10,000 total |
| Stdout per query | 1,048,576 bytes |
| Stderr per query | 65,536 bytes |
| Collection wall budget | 300 seconds |
| Per-process wall budget | Lesser of 60 seconds and remaining collection budget |
| Endpoint descriptor text | 512 characters per field; an application bound |
| In-memory graph | 20,000 directed pairs, 40,000 supplied observations |

Budgets are internal, finite and not exposed tuning options. A record-budget
exceeding reply contributes safe page evidence but no accepted edges from that
reply. At the documented 2,000-row query cap, coverage records possible truncation;
the cap is never an exhaustion certificate. Query/time exhaustion stops further
calls; failures count against the query budget. Graph overflow refuses rather
than dropping prior evidence. CLI internal auto-fetch and column requests mean
CLI invocation counts are not exact HTTP request counts. Process creation and
cleanup retain the limits documented in SF_CLI.md.

## Coverage and stale refresh

Inventory, audit and relationship coverage remain independent. This optional
adapter returns a new coverage record without changing the supplied inventory,
audit coverage or component facts/hashes. Offline relationships remain
`not_collected`, `requested=false`, with no call to this adapter.

**Release limitation:** The current fixed read-only allowlist cannot independently
prove MetadataComponentDependency exhaustion, complete type support or permission
visibility. Every usable probe, including consistent empty results, yields
`partial` requested relationship coverage. No usable probe or no selected endpoint
yields `unavailable`. Both produce outcome 4 under the existing coverage contract.
There is no caller switch that can make platform collection complete. Actual
request API version stays unknown, rather than inferred from class compilation
ApiVersion or the reviewed documentation version.

Count/done/continuation/warning/stderr/extra-result-field contradictions are
retained as safe `PageEvidence` booleans/counts and fixed warning codes; later
clean replies cannot clear them. A continuation is never executed. Optional
process/envelope failures become `query_unavailable`; the redacted boundary does
not distinguish permission, unsupported object/field, authentication, timeout or
cleanup failure. Required identity failures remain operational/coverage errors.
Validation/config/conflict errors propagate with unchanged precedence
**3, 2, 1, 4, 0**. No fallback broadens access.

`refresh_graph` accepts only validated in-memory snapshots with exactly matching
binding and Selection. Partial, failed, unsupported or uncollected refreshes
retain prior non-reaffirmed evidence as stale with original provenance/coverage.
Exact current evidence reaffirms a previous observation; changed evidence coexists
with the old stale observation. Prior resolved identities are retained on stale
edges even when absent from a later inventory; this is historical evidence, not
proof of current presence, absence or deletion. Explicit note paths still govern
link eligibility. Repeated identical failures do not grow evidence indefinitely.
A complete **synthetic** snapshot can test authoritative empty replacement; the
platform collector never generates such completeness. No state file is loaded,
reconstructed, adopted or written.

Each note fingerprint includes incident outgoing/incoming evidence, graph-wide
coverage, matching source/scope and relevant supplied note paths. It composes the
unchanged legacy graph helper with graph-specific descriptors (including unresolved
sources). Moving either managed endpoint invalidates the neighbor's graph hash;
unrelated path moves do not. No component source hash changes. Coverage changes
can invalidate all notes that need to display the changed collection limitation.
Fingerprints provide invalidation evidence, not permission to overwrite notes.

## Official contracts reviewed on 19 October 2026

Documentation/source reads only; no real `sf` invocation:

- The [Tooling API guide](https://resources.docs.salesforce.com/latest/latest/en-us/sfdc/pdf/api_tooling.pdf),
  version 68.0, Winter '27, updated 9 October 2026, printed pp. 643–648, specifies
  the eight nullable endpoint fields, direction and Apex/cycle examples. It still
  labels Dependency API Beta/evaluation-only; Tooling query starts at API 43.0,
  has a 2,000-row cap and excludes reports. The object-specific limitations forbid
  ORDER BY, COUNT, queryMore, OFFSET, name filters and range operators. Its general
  SOQL summary/field property flags are inconsistent with some specific restrictions;
  this adapter follows the restrictive object-specific contract. Neither examples
  nor those field flags establish a comprehensive supported-type matrix.
- [API permissions](https://developer.salesforce.com/docs/platform/api-rest/guide/intro-rest-compatible-editions.html)
  require org API access and API Enabled. The Tooling guide printed pp. 2–3 says
  permissions differ by endpoint/object; the MCD chapter gives no precise additional
  permission guarantee. Permission discovery and broader describe/auth calls are
  outside this adapter; no View All Data/Author Apex permission claim is inferred.
- [REST Query](https://developer.salesforce.com/docs/platform/api-rest/guide/resources-query.html)
  describes general records/totalSize/done/continuation signals and variable batch
  sizes. Generic queryMore guidance cannot override MCD's explicit restriction.
- [CLI query flags](https://developer.salesforce.com/docs/platform/salesforce-cli-reference/guide/cli_reference_data_query.html),
  [JSON evolution](https://developer.salesforce.com/docs/platform/sfdx-setup/guide/sfdx-dev-cli-json-support.html),
  official [query source](https://github.com/salesforcecli/plugin-data/blob/a0cdb671f42af74e31a782c34c5cdcc22e1ea5b0/src/commands/data/query.ts)
  and [result schema](https://github.com/salesforcecli/plugin-data/blob/a0cdb671f42af74e31a782c34c5cdcc22e1ea5b0/schemas/data-query.json)
  were rechecked. Current plugin-data main resolves to that source commit. It uses
  auto-fetch/maxFetch, warns about missing records and can issue column-metadata
  requests; records/totalSize/done form the inner result. The accepted transport
  validates the outer status/result/warnings envelope; current
  [SfCommand source](https://github.com/salesforcecli/sf-plugins-core/blob/efe58eff7bf546045e6beca16856104ffcc7eca9/src/sfCommand.ts)
  reconfirms that wrapper and string/structured warnings. These are source contracts,
  not verified installed CLI/Node/plugin versions or native execution evidence.

Synthetic tests and installed mocks verify local behavior. They cannot establish
actual org permissions, supported-type coverage, live exhaustion or Windows sf
execution. Future live validation requires separate authorization for its target
and operations. Enhancement #18 and Threads 08–17 remain not started.

Thread 07 projects both graph directions into candidate notes with explicit
managed paths, method/coverage/staleness and unresolved labels. No endpoint ID or
raw payload is rendered. Existing per-note graph fingerprints remain unchanged;
rendering composes them with independent coverage to catch audit/inventory-only
output changes. This adds no collection, adoption, state or publication capability.
