# Internal live Apex inventory and audit adapter

Thread 05 implements `sources/live.py`, tested with synthetic CLI envelopes and
mocked process collection only. It adds no public command, authentication,
renderer, graph collector, state adoption, deletion planner, or vault writes.
Internal interfaces are not a stable Python API. The CLI still exposes only
help/version. Windows `sf` execution remains refused by the unchanged
[process boundary](SF_CLI.md); [enhancement #18](https://github.com/jeffshurtliff/obforce/issues/18)
is outside v0.1.0 and is not a prerequisite for this adapter.

Thread 05 is accepted and delivered at merge `85ba7cd`. Exact-commit
[run 39325616681, attempt 1](https://github.com/jeffshurtliff/obforce/actions/runs/39325616681)
passed all 12 Linux/macOS/Windows Python 3.12–3.15 cells: Linux/macOS each
reported 441 passed; Windows each reported 430 passed/11 expected skips. Every
cell passed standalone checks, fresh build/Twine and both independent artifact
installations. The Windows skips cover nine POSIX collector cases, the POSIX
wrapper-symlink case and the unavailable FIFO case. Mocked adapter/refusal checks
and hosted Windows results do not qualify Windows sf execution. See the
[acceptance record](../dev/IMPLEMENTATION_PLAN.md#thread-05-acceptance-and-closure--19-october-2026).
Thread 06 and later work remain not started.

## Invocation and verified identity

The internal caller supplies the explicit absolute trusted executable, existing
neutral working directory, target, logical workspace, existing `Selection`,
privacy option, and any previously verified configured/state `SourceBinding`.
There is no executable/default-org/auth/config/state discovery. A caller must
separately obtain authorization for the target and read operations before a real
invocation. No real CLI or org was invoked to implement or validate this thread.

The first query is ordinary `SELECT Id FROM Organization LIMIT 2`. Exactly one
valid `00D` Salesforce ID, `done=true`, matching count, no continuation, no warning
or stderr, and no unexpected result fields are required. An unavailable query is
an operational failure; ambiguous/incomplete identity evidence is coverage exit 4.
Only the ID is requested, never organization names, endpoints, credentials, or an
org-display operation. Customer Portal users cannot query Organization according
to the official reference; this adapter never attempts another identity source.

IDs use strict object prefixes, alphanumeric 15-character form or checksum-valid
18-character form, and normalize to 18 characters. The resulting existing live
binding contains workspace/mode/verified org ID, never alias. Every supplied
configured/state binding must match exactly before inventory starts; a different
workspace, mode, or org is a conflict (3), without adoption/rebinding. Bindings
supplied by callers must already use the canonical org-ID representation; this
adapter does not migrate existing state. State-document validation remains Thread
09. Missing bindings mean an initial internal collection, not permission to adopt
managed notes or reconstruct missing state.

An alias is merely the explicit CLI selector. These separate CLI calls assume a
trusted stable CLI/auth configuration and stable accessible metadata scope during
collection. Identity verification and filter pagination are observations, not an
atomic org/auth snapshot. Concurrent alias/auth/permission/metadata changes can
invalidate comparability. Complete here means exhaustion of this observed,
selected accessible scope, never whole-org visibility or deletion proof. Later
missing-note decisions still require their own comparable-scope checks.

## Fixed queries and finite enumeration

Apex inventory uses Tooling queries with exactly:

```sql
SELECT Id, Name, NamespacePrefix, ApiVersion, Status
FROM ApexClass WHERE NamespacePrefix = null ORDER BY Id LIMIT 200
```

Actual query strings are single-line. Namespace inclusion omits that predicate.
Subsequent queries add `Id > '<validated previous page final ID>'`; no raw name,
selector, namespace, endpoint or continuation string is interpolated. Server ID
ordering selects the cursor; the implementation does not invent an ID collation.
The existing optional internal `full_names` filter is applied locally to the
class Name, as in offline acquisition, and never inserted into SOQL. Selection
still distinguishes namespace in the structured component key. Unexpected
namespaces in an exclusion query are retained as a scope contradiction, excluded
from output, and block complete inventory. Duplicate component keys or canonical
record IDs, even identical records or repetitions across pages, cause conflict.

Every page must have consistent returned count/`totalSize`, `done=true`, no
continuation, warnings or stderr, and no unexpected result properties. All these
observations remain in safe `PageEvidence` records, including contradictory ones.
Only their booleans/counts/fixed diagnostic codes are retained; no warning text,
raw result or endpoint is exposed. Unknown result fields conservatively prevent
completeness. Malformed envelope types and impossible `totalSize < returned`
remain operational refusals in the accepted boundary.

A full **or short** page requires another bounded query. Inventory is complete
only after a consistent terminal empty query and consistent evidence for every
prior page, following verified identity. One empty array, successful process or
done flag alone is insufficient. Contradictory pages stop enumeration as partial;
returned valid selected rows can remain in the private result but confer no
absence/deletion evidence. A returned continuation is never executed or removed
by a later successful query. There is no arbitrary endpoint, OFFSET, bulk export,
query-file operation, shell, default target, or wrapper workaround.

| Boundary | Maximum |
| --- | --- |
| Inventory page | 200 records |
| Inventory page queries, including terminal probe | 51 |
| Enumerated records before selection | 10,000 |
| All query invocations, including identity/audit | 156 |
| Collection wall budget | 300 seconds |
| Each process wall budget | Lesser of 60 seconds and remaining collection time |
| Each process stdout | 262,144 bytes |
| Each process stderr | 65,536 bytes |

The final terminal probe fits after 50 full pages at the record ceiling. Records
beyond the ceiling are not accepted, and exhausting page/query/record/time budgets
before exhaustion returns partial inventory with explicit fixed reasons and exit
4. Limits are internal constants, not public tuning options. Existing pipe/JSON
bounds, cleanup and Windows refusal stay unchanged. Process spawning itself and
cleanup have the limitations described in [SF_CLI.md](SF_CLI.md); this deadline
does not make OS-uninterruptible operations interruptible. At most 156 bounded
outputs are processed sequentially; raw responses are not accumulated in results.
The CLI may also make its own auto-fetch and column-metadata requests internally;
156 bounds CLI invocations, not a promise about exact HTTP request consumption.

## Audit privacy, normalization and optional failures

After each inventory page, query dates only for selected validated Apex IDs:

```sql
SELECT Id, CreatedDate, LastModifiedDate FROM ApexClass WHERE Id IN ('<selected ID>')
```

When `include_audit_names=true`, a separate scoped query uses exactly
`Id, CreatedBy.Name, LastModifiedBy.Name` and the same selected Apex-ID set. The
field projection, WHERE structure and validated ID literals are generated
internally; there is no User scan/query, User ID collection, username, email,
Body, SymbolTable, FullName, Metadata, unrelated customer data or technical-debt
assessment. FullName/Metadata have per-query restrictions and are unnecessary
for the established Name/namespace identity. The CLI itself can perform column
metadata requests as documented in its official source.

Dates are strict ISO timestamps with explicit timezone, validated calendar and
offset, normalized to UTC with six fractional digits. Class ApiVersion accepts
finite integral JSON numbers or equivalent version strings and normalizes to
`N.0`, under the same 1–999 syntax as offline XML. This is the class compilation
version, **not** evidence of the API version used for the request. The transport
neither selects nor exposes a request version; coverage `api_version` stays null.
Statuses are Active/Deleted, matching offline normalization; Inactive is unused
for ApexClass in the official reference and is refused. Required identity,
namespace, version or status fields missing/malformed are validation exit 2.

The unchanged availability contract is applied deliberately:

- Name omission sends no name query and leaves `created_by`/`last_modified_by`
  **absent**; requested date coverage is still tracked.
- Missing requested audit keys/rows/nested Names are **unavailable**; requested
  display names are not inferred from IDs, aliases, auth identities or other fields.
- Explicit null date, relationship, or Name is an observed **null**, not unavailable.
- Available dates/display names are validated; unexpected projected/relationship
  fields or malformed observed values fail with safe validation diagnostics.

Optional date/name process or envelope failures become fixed `query_unavailable`
audit warnings with unavailable facts; the boundary has intentionally redacted
the raw cause, so the adapter does not guess permission loss versus unsupported
field versus timeout/authentication. No fallback query broadens access and no
retry scans Users. Partial optional envelopes retain their contradictory signals;
missing records/fields remain unavailable. An unselected audit ID or duplicate
audit mapping is a conflict. Config/model/conflict errors are not swallowed as
optional failures. Required identity/inventory failures remain operational exit
1; a later required permission failure does not return a completed collection.

Inventory, audit, and relationship coverage remain independent. Audit is complete
only if inventory is exhausted and all requested date/name queries and fields
are complete (observed null is known). With some known facts it is partial;
otherwise unavailable. Complete empty scope has vacuously complete requested
audit. Relationships are `not_collected`, `requested=false`; Thread 06 has not
started. Any requested incomplete dimension produces outcome 4 through the
existing coverage contract. Combined errors retain precedence 3, 2, 1, 4, 0.
Consumers must inspect coverage/outcome; returned rows or their hash are never a
completeness certificate.

Source hashes use the existing component/inventory functions without contract
changes. Canonical IDs, normalized dates/version, validated facts/availability,
and fixed inventory/audit provenance labels are semantic inputs. Collection
ordering, alias, host paths, raw JSON/attributes/URLs, diagnostics and wall time
are excluded. Audit fact changes affect source hashes; name omission and
namespace/name selection remain explicit privacy/scope inputs. No fields alter
ownership, source-key identity, lifecycle, or human technical-debt decisions.

## Official contracts checked on 19 October 2026

Documentation/source reads only, without executing `sf`:

- [Current Tooling API Developer Guide](https://resources.docs.salesforce.com/latest/latest/en-us/sfdc/pdf/api_tooling.pdf):
  System Fields (printed p. 55) defines Id, CreatedDate, LastModifiedDate and User
  relationships; ApexClass (pp. 111–114) defines query support, Name (255), namespace
  (15), ApiVersion, Status and the single-record FullName/Metadata restrictions.
- [Current Object Reference](https://resources.docs.salesforce.com/latest/latest/en-us/sfdc/pdf/object_reference.pdf):
  ApexClass (pp. 574–577) corroborates fields/status; Organization (p. 4065) permits
  SELECT/query and excludes Customer Portal users. The corresponding HTML object
  pages returned no readable body, so the official PDF text was used.
- [API permission requirements](https://developer.salesforce.com/docs/platform/api-rest/guide/intro-rest-compatible-editions.html)
  and the Tooling guide require appropriate API/org/object access; endpoint-specific
  permission rules differ. Do not transfer ApexClassMember's View All Data/Author
  Apex requirement to ApexClass or treat successful accessible queries as whole-org
  permission certification. No permission/auth discovery is implemented.
- [Filter-based pagination guidance](https://help.salesforce.com/s/articleView?id=000387840&language=en_US&type=1)
  documents sorting/filter anchors including Id rather than OFFSET beyond its
  2,000-row ceiling. Applying that general guidance to the fixed ApexClass SELECTs
  is this adapter's design choice, validated with mocks, not a live qualification.
- [REST Query](https://developer.salesforce.com/docs/platform/api-rest/guide/resources-query.html)
  defines records/totalSize/done/nextRecordsUrl and variable batch sizes; the
  adapter checks the CLI's aggregated result rather than assuming an HTTP batch.
- [CLI query reference](https://developer.salesforce.com/docs/platform/salesforce-cli-reference/guide/cli_reference_data_query.html)
  documents explicit target/query/JSON/Tooling flags. Official
  [implementation](https://github.com/salesforcecli/plugin-data/blob/a0cdb671f42af74e31a782c34c5cdcc22e1ea5b0/src/commands/data/query.ts)
  and [inner result schema](https://github.com/salesforcecli/plugin-data/blob/a0cdb671f42af74e31a782c34c5cdcc22e1ea5b0/schemas/data-query.json)
  confirm auto-fetch/maxFetch, truncation warnings, aggregated records/count/done
  and additional column-metadata requests. Current main still resolved to that
  source commit during this review; it is not an installed CLI/version pin.

Synthetic fixture/test evidence does not establish actual Salesforce permission,
installed CLI/Node/plugin compatibility, live exhaustion, native Windows sf
execution, or full lifecycle safety. Those require separately authorized work.
