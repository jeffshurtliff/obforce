# Apex candidate rendering

Build renders new candidates; sync renders only generated candidates for existing
notes and applies strict baseline-preserving patches. Creation templates are
creation-only. The current renderer fingerprint is 4, with four spaces per nested
list level. These modules are internal implementation details, not a stable API.

## Inputs, identity and output

The caller supplies an accepted normalized ApexClass component, independent
Coverage, a matching DependencyGraph, explicit managed-note paths, normalized
layout/privacy options and a persistent canonical lowercase UUID. The renderer
does not invent/regenerate identity, inspect a vault, load state, acquire source,
invoke Salesforce/Obsidian, or discover authentication. Supplied bindings,
selection, namespace options and relationship coverage must agree. Offline
graphs must remain empty and relationships explicitly `not_collected`.

`note_paths` proposes new portable paths under the configured Apex directory:
`DemoService.md` or `fictional_package/DemoService.md`. These proposals do not
establish existing-note ownership. Names retain case/Unicode/namespace; unsafe
segments fail rather than being silently renamed. Explicit managed paths may
represent moved notes, but only the caller's previously validated mapping can
establish that fact. The renderer does not verify filesystem ownership.

Paths require `.md`, at most 1,024 characters, 32 segments, and 240 UTF-8 bytes per
segment, in addition to the shared portable/reserved-name rules. Wikilink control
characters (`#[]^%&;` plus backticks, `!` and braces) are refused. Full paths and
all shared directory spellings are compared under NFC plus casefold; file/parent
collisions are refused too. Two different namespace spellings cannot silently
share a portable directory. No destination is inspected or created.

`render_generated` returns only the marker-interior string, exact reserved
property values and source/graph/render/region hashes. `render_new_note` additionally
returns a complete new-note string, explicit path and a separate creation hash.
Candidate strings have UTF-8/LF semantics and one terminal newline. The engine
serializes sorted, quoted property keys and JSON-encoded scalar/list values,
a valid flat YAML subset. Quoted keys also preserve names such as `null`/`false`.
There are no YAML tags, aliases, nested mappings or duplicate keys. The renderer does not parse existing frontmatter; the preservation layer does.

The engine owns UUID/schema, the frozen `sf_*` allowlist, and exactly one ordered
marker pair on separate lines. Templates cannot supply frontmatter or markers.
Unknown `sf_*` names and attempts to supply reserved creation defaults fail.
Optional creation defaults are explicit flat user properties; all remain
user-owned after creation. Defaults are `type: salesforce_component`,
`tags: [salesforce]`, Boolean `technical_debt: false`, blank strings
`tech_debt_severity`/`tech_debt_status`, and `last_reviewed: null`.
Only Boolean debt overrides are accepted for new notes; other supported custom
human values remain distinct. Boolean human decisions remain preserved during
patching; metadata never assesses technical debt. Creation requires
Business Context, Known Issues / Technical Debt, and Additional Information
exactly once. Generated sections require Salesforce Metadata, Coverage,
References and Referenced By exactly once.

Unavailable, absent and observed-null audits are omitted from properties and
explained separately in the generated body. Audit-name omission removes available
names from both output contexts and properties. No body, org ID, record ID,
internal endpoint, raw response or incidental collection timestamp is projected
into output. Metadata strings use the bounded inline escaping contract below;
property strings use YAML-compatible JSON quoting. Internal wikilinks use
only separately validated explicit paths and escaped display labels. Explicit
user creation defaults are authored content, not source metadata or inferred facts.

## Installed assets and explicit overrides

The two known names are:

- `apex_generated.md.j2`: generated-section presentation.
- `apex_created.md.j2`: initial human body after the generated region.

`load_template(name, directory)` checks only that known filename in an explicit
absolute override root. A missing root/file falls back **per template** to
`importlib.resources.files('obforce')` packaged assets. Existing invalid overrides,
unsafe roots/files and read failures do not fall back. There is no cwd search,
metadata-based template discovery, Jinja filesystem loader, recursive scanning,
include, import or inheritance. Other files in the root are never discovered.

Save overrides as UTF-8 with LF line endings on every platform. Carriage returns
(including CRLF), other unsupported control characters and reserved structure are
refused without normalization or fallback. For a Python-created override, use
`path.write_text(text, encoding='utf-8', newline='\n')`; checkout attributes do not
control line endings of files created at runtime.

Root ancestors and known files are checked with lstat; links/reparse points,
special files and multiply linked template files are refused. Bounded reads
compare pathname/descriptor identity, size and mtime and recheck parents. POSIX
no-follow/nonblocking open flags are used where available. These are read-side
checks requiring a stable trusted local override tree, not hostile filesystem
race isolation or later publication qualification. Config paths already resolved
by the loader cannot reveal links that were resolved before rendering.

Overrides are user-selected local code-like input. The sandbox alone does not
prevent CPU/memory exhaustion. This implementation therefore accepts a finite
**interpolation-only Jinja subset**: literal Markdown and exactly one
`{{ name | section }}` for each engine-produced generated section. The available
names are `metadata`, `coverage`, `references`, `referenced_by`. The `section`
filter accepts only serialized engine strings. Reorder sections and add ordinary
presentation text; retain their required headings. Creation templates are literal
human-section Markdown with no context slots. Supply flat creation property
defaults through the explicit caller argument, never template YAML.

For example, this fictional generated override retains every required slot:

```jinja
{{ metadata | section }}

{{ references | section }}

{{ referenced_by | section }}

{{ coverage | section }}
```

StrictUndefined remains enabled. Globals/tests/default filters are cleared;
Python attributes and callables are denied. AST validation refuses loops,
conditionals, calls, arithmetic, attributes, indexing, constants/expressions,
macros, imports/includes, filters other than `section`, missing/duplicate slots
and unknown names. There are no model/Path objects, IDs, arbitrary dicts,
filesystem/process/network helpers or side effects in template contexts.
Errors are typed and redacted, without template/source contents or local paths.

| Refusal bound | Maximum |
| --- | --- |
| Each UTF-8 template | 16,384 bytes |
| Each template AST | 256 nodes |
| Each normalized input string | 4,096 characters |
| Aggregate primitive input per candidate | 2 MiB / 100,000 nodes |
| Supplied components or managed paths | 10,000 |
| Incident directed edges | 2,000 |
| Creation properties | 128 total, including reserved/default keys |
| Aggregate section context / each rendered section | 512 KiB |
| Complete new-note candidate | 1 MiB |

Bounds refuse, never truncate. Finite interpolation precludes template-controlled
loops, recursion, expression amplification and unbounded iterator execution;
output size is checked before candidate acceptance. This is not an OS CPU/memory
isolation facility. Read errors are OperationalError; invalid templates/structure
are ConfigError; invalid normalized inputs are ModelError; identity/scope/path
ambiguity is ConflictError. Existing error/exit precedence is unchanged.

## Relationships and invalidation

References and Referenced By derive from the same accepted directed graph.
Supported exact resolved endpoints become links only with explicit validated
managed paths. Unmapped, unsupported, external, unresolved and identity-mismatch
endpoints stay labeled text; no extra component notes are created. Self-edges,
cycles, namespaces, each distinct method/coverage observation and stale evidence
are retained without recursion. Endpoint IDs are never display labels.

Inventory, audit and relationship coverage are displayed independently with
method, requested status, pagination, limits, API version and warnings. Each edge
also retains its original method/coverage/staleness. These are platform-reported
references, not runtime proof or comprehensive impact analysis. The accepted
collector cannot establish exhaustion: requested platform relationships remain
partial/unavailable even after clean empty replies. Offline relationships remain
not collected; no collection or transport changes are made.

Source hashes and all existing hash helper contracts remain unchanged. The
candidate retains the accepted per-note graph fingerprint (including incident
edges and explicit paths). For generated invalidation, the renderer composes
that graph digest with the complete independent Coverage record and passes the
result to the existing `render_fingerprint` helper. This additional composition
prevents inventory/audit-only coverage changes from producing a false no-op.
It does not change the accepted graph fingerprint or component source hash.

Exact generated-template bytes, graph/path and relevant coverage changes affect
the generated render hash. A creation-template change affects only the separate
new-note `creation_fingerprint`. No override root, checkout path, template mtime,
response ordering, incidental timestamp or newly generated identity enters output.
An incoming-only edge or neighboring move invalidates affected output even when
the component source hash stays unchanged. Hash equality never authorizes
replacing edited generated content; note preservation compares both saved property and
exact-byte body baselines before patching.

## Readable escaped metadata

The renderer retains plain ordinary inline punctuation (straight quotes,
hyphens, commas, semicolons, apostrophes and parentheses), intraword underscores
and non-domain periods. Whole ISO-shaped timestamp scalars retain colons. Thus
`api_version`, `local-apex-xml-v1`, `"67.0"`, `"Active"` and audit timestamps remain
readable. Serialization does not introduce curly quotes or normalize human data.
Periods immediately before letters and scheme colons stay encoded to avoid
activating bare domains/URLs. All remaining syntax-capable punctuation retains
numeric references: brackets/embeds, emphasis-boundary underscores, asterisks,
HTML angles/ampersands, backticks, hashtags, math, block IDs, highlights/comments
and pipes. Existing control/newline/reserved-marker refusal and finite bounds stay.

This serializer is used only within engine-owned single-line prefixes or validated
intentional wikilink display labels; it is not a general block, target-path or HTML
attribute encoder. Known reference targets keep their separate strict path gates.
The [CommonMark reference rules](https://spec.commonmark.org/0.31.2/#entity-and-numeric-character-references)
do not reinterpret decoded character references as Markdown syntax. Synthetic
source snapshots and a local independent CommonMark parser verify ordinary text
and hostile payloads. Native display is a separate evidence class; see
[qualification](QUALIFICATION.md).

## Four-space generated list indentation

Engine-generated Markdown uses four spaces per nested bullet level, consistently
for every coverage warning under inventory, audit and relationships. Top-level
bullets stay flush left. This is a shared internal rendering convention, not a
new configuration option. Explicit template slots receive the same formatted
sections; template-authored literals, YAML properties and human note regions
retain their own spacing. No whole-document reindent pass runs.

The current renderer fingerprint includes this formatting convention. Exact saved
property/body baselines still gate generated-only patches; human lists and
properties retain their original content.

## Literal native dashboard

`renderer/dashboards.py` reads exactly one bounded installed literal
`resources/bases/apex_classes.base` through `importlib.resources`. It uses no
source data, Jinja, override discovery, external tool or publication side effect.
The destination is the existing configured dashboard directory plus the fixed
filename. Renderer fingerprint 4 is used for reserved
`sf_created`/`sf_last_modified` UTC `YYYY-MM-DD` projections of valid available
audit timestamps. Absent/null/unavailable/invalid dates yield no projection;
original `sf_*_at` facts and source/graph hashes remain. Exact old baselines still
gate generated-only patches; existing human fields are not backfilled. No schema,
acquisition, ownership or transaction bound changes.
[Dashboard syntax, human debt semantics and ownership](DASHBOARDS.md)
are tested independently from native Obsidian rendering (unavailable).

Native Obsidian preview remains unavailable. See [qualification](QUALIFICATION.md)
for evidence and platform limits.

<!-- Compatibility targets for retained maintainer evidence links. -->
<a id="renderer-version-2-readability-correction--mtf-1--20"></a>
<a id="four-space-generated-list-indentation--thread-12"></a>
