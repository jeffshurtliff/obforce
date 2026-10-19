# Normalized identity and coverage

Thread 02 supplies immutable internal records, canonical serialization/hashing,
and validation helpers. Thread 03 now implements the internal
[offline Apex source](OFFLINE_SOURCE.md), using these unchanged contracts.
Live connectors, dependency collection, and graph building remain planned.
All examples below are fictional. These are
versioned internal contracts, not a stable public Python API.

## Records and identities

| Record | Version-one contents |
| --- | --- |
| `SourceBinding` | Workspace ID, `local`/`live` mode, verified live org ID or null |
| `ComponentKey` | Workspace, literal `ApexClass`, namespace, full name |
| `Component` | Binding/key, optional live record ID, allowlisted facts and field availability, sorted provenance labels, optional incidental collection time |
| `Selection` | ApexClass type, explicit namespace inclusion, sorted optional internal full-name filters |
| `CollectionCoverage` | One dimension's status, method, request intent, pagination, limit result, API version, sorted warnings |
| `Coverage` | Binding/selection plus independent inventory, audit, relationship coverage |
| `Relationship` | Directed source/resolved target keys or an unresolved target label, kind, evidence method, coverage, stale flag |
| `NoteState` | Persistent UUID, binding/key, relative note path, source/graph/render hashes, exact generated-property baseline and region hash, state schema |

Model version is 1. Canonical component identity is structured JSON, for example:

```json
["demo-org","ApexClass",null,"DemoService"]
```

This avoids delimiter collisions. Identity preserves case, namespace, and Unicode
code points: `DemoService`, `demoservice`, and a namespaced class remain distinct.
An empty namespace normalizes to null. Filename equivalence is a separate
constraint: supplied note paths collide conservatively under NFC normalization
plus casefold, including on a host whose filesystem permits both names.

Duplicate component keys, duplicate live record-ID mappings, note IDs, note-key
mappings, or equivalent paths cause conflict; identical duplicates are refused
too. A record ID supplements the source key and never changes it into a filename.
Similar names/text do not establish a rename. A persistent note UUID survives a
unique move; reconciliation of discovered notes is Thread 09, not implemented by
these supplied-record validators.

Bindings contain no machine path or live alias. A local workspace is the explicit
configured logical identity; moving its checkout does not inherently change it.
The later live adapter must supply the actual verified org ID. Merely constructing
a binding does not verify an ID. `require_same_source` refuses workspace, mode,
or verified-org changes. Local/live rebinding and automatic adoption are
unsupported. Changing local scope cannot establish live absence/deletion.

## Field availability and allowed facts

Normalized component attributes are exactly `api_version`, `status`, `created_at`,
`created_by`, `last_modified_at`, and `last_modified_by`. Additional raw API fields,
class bodies, endpoints, arbitrary business data, and credentials are rejected.
Adapters must normalize values before constructing records; this model does not
implement Salesforce field validation or API response parsing.

An attribute omitted from the mapping is **absent**. A present field is one of:

```json
{"availability":"unavailable","value":null}
{"availability":"null","value":null}
{"availability":"value","value":false}
{"availability":"value","value":""}
{"availability":"value","value":[]}
```

These are all different, as is integer zero. Available values can be strings,
booleans, integers, or immutable ordered tuples of strings (serialized as arrays).
Use strings for decimal API versions and normalized audit dates. Null is an
explicitly observed null; unavailable means not obtainable/collected, without
inventing a value. No filesystem or Git date becomes a Salesforce audit date.
Technical debt remains a user decision; an unset assessment is never false.

## Independent collection coverage

Each dimension uses `complete`, `partial`, `unavailable`, or `not_collected`.
`requested` records whether that dimension was part of the requested operation.
Methods, API versions, warnings, and evidence remain explicit. `pagination` is
`not_applicable`, `exhausted`, `incomplete`, or `unknown`; `limit_reached` is false,
true, or null when unknown. Complete requires positive exhaustion/non-applicability
and `limit_reached = false`. A successful process or empty array proves neither.

An offline result can have complete inventory **for the declared local scope**,
unavailable audit, and uncollected relationships by design, with the latter two
marked `requested = false`. Its status is successful with limitations reported.
If an explicitly requested dimension is partial/unavailable/uncollected, the
coverage outcome is 4. Operational failures and conflicts take precedence as
specified in [configuration](CONFIGURATION.md).

The scope fingerprint includes model version, binding, ApexClass selection,
namespace inclusion, and internal name filters. It excludes collection outcomes;
therefore a complete and partial result may share scope, but their full coverage
records differ. Namespace exclusion is explicit and must be reported. Complete
inventory alone never means complete audit or dependency coverage. Later threads
must also verify accessible comparable scope before marking a component missing;
Thread 02 implements no missing/deletion planner.

Platform-reported references are evidence of reported relationships, not proof
of runtime behavior or comprehensive impact analysis. Unresolved endpoints stay
labeled text and do not create component notes. Offline XML alone supplies no
Apex code-reference proof. Failed refreshes must preserve prior edges as stale;
this record can represent stale evidence but does not perform that refresh.
Current API capabilities/limits remain for Threads 04–06 to verify.

## Deterministic fingerprints

`canonical_json` accepts null, strings, booleans, integers, string-keyed dicts,
and lists/tuples. It emits compact JSON with sorted object keys, literal Unicode,
and UTF-8 hashing using SHA-256 lowercase hexadecimal digests. Floats (including
NaN/infinity), sets, paths, custom objects, and non-string object keys are refused.
Do not silently stringify unsupported values. Arrays retain order; constructors
explicitly sort unordered filters/provenance/warnings. Duplicate entries are
refused rather than silently merged.

Component source hashes include model version, binding, structured key, optional
record ID, allowlisted field values/availability, and normalized provenance
labels. They exclude collection timestamps; real audit-date changes remain
semantic changes. Callers pass method labels, never host paths or incidental
CLI data, as provenance. The inventory hash sorts validated components by key,
so response ordering does not matter. An empty inventory hash does not prove a
complete scan; coverage is always separate.

The graph fingerprint sorts supplied relationship evidence and relevant resolved
note paths. Direction, incoming/outgoing edges, coverage, staleness, unresolved
labels, or a target move can change it without changing a component's own source
hash. The later graph layer must supply all relevant incident edges/locations;
this helper does not collect or derive them. Exact duplicate evidence is refused.

The generated render fingerprint includes source/graph fingerprints, generated
template content hash, model/note/marker/renderer versions, layout directories,
and namespace/audit-name options. No template directory path or mtime participates.
A separate `creation_fingerprint` combines it with a creation-template content
hash for **new-note candidates only**. Save the generated-only fingerprint in
note state even on initial creation, so a creation-template edit never invalidates
existing notes. No hashes grant permission to overwrite an edited baseline.
Hash equality is an integrity aid, not authentication, encryption, or proof of
safe publication. See [note ownership](NOTE_FORMAT.md).
