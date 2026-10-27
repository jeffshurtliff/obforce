# Internal Apex candidate rendering

Thread 13 [public refresh](REFRESH.md) uses this renderer only for generated
candidates on existing notes, followed by exact baseline-preserving patches.
Persisted private graph/fact evidence supplies historical inputs; renderer version
3, four-space generated nesting and all existing fingerprint/escaping contracts
remain. Creation templates still apply only to new notes; human prose/YAML is
never regenerated or reindented.

Thread 07 implements deterministic **candidate** rendering in
`renderer/templates.py` and `renderer/notes.py`. This is an internal interface,
not a stable public Python API. Thread 12 connects it to public initial build. The renderer reads no existing note and performs no patching,
adoption or publication. Thread 09 separately adds internal read-only
[state/move reconciliation](SYNC_SAFETY.md); Thread 10 adds internal read-only
planning; accepted Thread 11 publication/recovery and Thread 12 public orchestration
compose these existing primitives.
A complete new-note candidate must never be applied to an existing note.
Thread 08 separately supplies
[bounded in-memory preservation](NOTE_FORMAT.md#internal-existing-note-parsing-and-preservation-thread-08)
for caller-supplied bytes and saved baselines.

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
There are no YAML tags, aliases, nested mappings or duplicate keys. This thread
needs no runtime YAML parser dependency; it does not parse existing frontmatter.

The engine owns UUID/schema, the frozen `sf_*` allowlist, and exactly one ordered
marker pair on separate lines. Templates cannot supply frontmatter or markers.
Unknown `sf_*` names and attempts to supply reserved creation defaults fail.
Optional creation defaults are explicit flat user properties; all remain
user-owned after creation. Defaults are `type: salesforce_component`,
`tags: [salesforce]`, Boolean `technical_debt: false` (MTF-2), blank strings
`tech_debt_severity`/`tech_debt_status`, and `last_reviewed: null`.
Only Boolean debt overrides are accepted for new notes; other supported custom
human values remain distinct. Boolean human decisions remain preserved during
patching; metadata never assesses technical debt. The maintainer authorized false
throughout fictional/example/test defaults without historical unassessed data.
Creation requires
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
replacing edited generated content; Thread 08 compares both saved property and
exact-byte body baselines before patching.

## Dependency and verification evidence

Poetry adds `Jinja2 >=3.1.6,<4`, resolving Jinja2 3.1.6 and transitive MarkupSafe
3.0.4 in the generated lockfile. Jinja supplies the explicitly requested template
syntax and sandbox; serialization uses the standard library. No runtime YAML
parser is added. Official contracts reviewed on 20 October 2026:
[Jinja API](https://jinja.palletsprojects.com/en/stable/api/),
[sandbox](https://jinja.palletsprojects.com/en/stable/sandbox/),
[changes](https://jinja.palletsprojects.com/en/stable/changes/) and
[publisher package metadata](https://pypi.org/project/Jinja2/). The
[Obsidian internal-link contract](https://obsidian.md/help/links),
[flat properties and quoted links](https://obsidian.md/help/properties), and
[YAML 1.2.2 JSON compatibility](https://yaml.org/spec/1.2.2/) were also checked;
no running Obsidian or real vault was used.

Tests use synthetic fixtures, blocked network/process access, independent YAML
parsing via Bandit's already locked development dependency, and explicit
installed-resource/output checks. The fresh-artifact checker deliberately
allowlists both assets and renderer modules, compares all packaged source/resource
bytes to the checkout, then independently installs wheel and sdist outside it.
Each installed probe compares complete rendering with the reviewed synthetic
fixture, checks overrides/fallback, graph staleness/moves and absence of cwd
artifacts with sockets/process launches blocked. Setup/build/dependency downloads
may use the network; runtime probes do not.

Actual local, hosted and native gaps are recorded in the
[roadmap handoff](../dev/IMPLEMENTATION_PLAN.md). No live sf/org/vault or Windows
sf execution qualification follows. Thread 09 internal state reconciliation is
accepted; #9 is closed. Thread 10 planning is described below; Threads 11–17 and enhancement #18 remain not started.


## Thread 07 accepted delivery — 20 October 2026

Thread 07 is accepted and complete; #7 is closed under maintainer authorization.
Implementation `b4658eb0f878c71698e580801c118733a16b86df` was merged at
`eedeff425bcd4921bef8756412826ce5a93b0165`. All 21 packaged source/resource files
match the reviewed final candidate, and implementation/merge trees match.

Every required step and full command log in
[run 39440606470, attempt 1](https://github.com/jeffshurtliff/obforce/actions/runs/39440606470)
was verified. All 12 Linux/macOS/Windows Python 3.12–3.15 cells passed. Linux/macOS
passed 618 tests each without skips (95% coverage); Windows passed 606 with 12
expected skips each (93% coverage). Every cell passed standalone strict lock,
Ruff lint/format, Bandit, fresh build, strict Twine, exact archive/license/source/
resource inspection, both independent installations and whitespace checks.
All 24 installed probes passed full candidate-byte/resource/override/fallback/
graph/move/privacy checks with active runtime socket/process guards and no cwd
artifacts. Setup/download network use remains separate from offline runtime tests.

The 12 Windows skips are nine POSIX collector cases, the POSIX wrapper-symlink
case, unavailable FIFO case and POSIX unsafe-template-link fixture. Reparse
refusal is synthetic. This does not qualify Windows sf execution, real Salesforce,
hostile filesystem races, arbitrary Jinja, OS resource isolation or the later
preservation/publication lifecycle. Relationship coverage limitations and all
scope/privacy contracts remain unchanged. Historical local probe failures and
older CI evidence retain their original status.

See the [acceptance record](../dev/IMPLEMENTATION_PLAN.md#thread-07-acceptance-and-closure--20-october-2026).
Thread 08 supplies accepted [bounded supplied-byte preservation](NOTE_FORMAT.md),
delivered at merge `dba53ab`; #8 is closed. Its exact-merge 12-cell acceptance is
recorded in the [roadmap](../dev/IMPLEMENTATION_PLAN.md#thread-08-acceptance-and-closure--20-october-2026).
Thread 09 adds accepted internal [state/move reconciliation](SYNC_SAFETY.md),
including correction `890ced2` / merge `dff34a7`. #9 is closed; exact-merge run
`39502679337`, attempt 1, passed all 12 cells and 24 independent installs. See the
[acceptance record](../dev/IMPLEMENTATION_PLAN.md#thread-09-acceptance-and-closure--20-october-2026).
Thread 10 internal read-only planning/reporting is accepted, including correction
`a2132c3` / merge `6004c35`; #10 is closed. All 12 cells and 24 independent installs
passed in exact-merge run `39510802449`, attempt 1; see the
[acceptance record](../dev/IMPLEMENTATION_PLAN.md#thread-10-acceptance-and-closure--20-october-2026).
Thread 11 internal bounded transaction/recovery primitives are accepted, including
correction `4aaeb0f` / merge `2995f93`; #11 is closed. Final exact-merge run
`39676435834`, attempt 2, has all 12 cells and 24 independent installs passing;
see the [acceptance record](../dev/IMPLEMENTATION_PLAN.md#thread-11-acceptance-and-closure--21-october-2026) and
[transaction contract](SYNC_SAFETY.md#thread-11-pre-implementation-transaction-contract--20-october-2026).
Thread 12 is accepted and complete; #12/#20 are closed. Threads 13–17 and
enhancement #18 remain NOT STARTED.
No release is published.

Thread 10 always renders accepted generated candidates for existing notes against
all reconciled/current paths and independently supplied coverage, then applies
only preservation patches. This catches source, incoming/outgoing graph, moved
target, generated-template, options/layout and renderer-contract invalidation.
Equal hashes never bypass baseline checks. Whole-note creation and its separate
fingerprint apply only to new components; existing notes ignore creation assets.
The planner retains stale graph evidence with the accepted refresh helper.
See [complete read-only planning](SYNC_SAFETY.md#thread-10-pre-implementation-planner-contract--20-october-2026)
for caller inputs, output limits and the publication boundary.

Thread 11 consumes only complete independently revalidated planner candidates;
rendering still performs no publication itself. Existing-note publication uses the
accepted preservation patch, not creation-template regeneration. Renderer-local
graph-plus-independent-Coverage and creation-only hash contracts remain unchanged.
No graph snapshot is persisted in state or reconstructed during recovery.


## Renderer version 2 readability correction — MTF-1 / #20

Assigned to the current Thread 12 correction for v0.1.0, because readable first
build notes are already an acceptance requirement. No Thread 13/14 work is started.
The original blanket numeric escaping made underscores, quotes and hyphens appear
as literal references in reported Obsidian Live Preview output.

Renderer version 2 retains plain ordinary inline punctuation (straight quotes,
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
and hostile payloads. The maintainer subsequently confirmed the fictional
quickstart's readability and nesting in Obsidian. This is manual acceptance, not
automated execution or an exhaustive view/platform test; agent validation opened
no real vault or Obsidian.

Only the existing renderer-version fingerprint input advances (1 to 2). Source/
graph hashes, hash algorithms, state/model/note/marker schemas and journal schema 2
are unchanged. Legacy rendered/preservation fixtures are retained and old saved
state still round-trips. The accepted lower-level patcher validates exact old
generated-property/body baselines before replacing only the generated region;
custom YAML/comments/prose/aliases/tags/technical_debt* remain user-owned. A human
edit still blocks. Public build refuses repeats, and no migration/repair/whole-note
rerender or public refresh capability is introduced.


## Four-space generated list indentation — Thread 12

Engine-generated Markdown uses four spaces per nested bullet level, consistently
for every coverage warning under inventory, audit and relationships. Top-level
bullets stay flush left. This is a shared internal rendering convention, not a
new configuration option. Explicit template slots receive the same formatted
sections; template-authored literals, YAML properties and human note regions
retain their own spacing. No whole-document reindent pass runs.

Renderer version 3 advances the existing fingerprint input from 2, making this
presentation change visible to planning without changing source/graph hashes,
hash algorithms, UUIDs or state/note/marker/journal schemas. Exact legacy-v2
property and generated-region baselines still validate before a generated-only
patch; intervening generated edits still refuse. Two-space human lists and all
user properties remain unchanged. Public initial build still refuses an existing
vault; this does not add refresh, migration or automatic note rewriting.

The maintainer confirmed the preceding MTF-1 character correction through the
fictional quickstart on 23 October 2026. Its delivered merge `8285aca` passed all
12 exact-commit hosted cells in run `39868649758`, attempt 1. Four-space rendering
was delivered at `f833505` and passed all 12 hosted cells and 24 independent
installs in run `39985255497`, attempt 1. The maintainer tested and accepted the
indentation; #12 and #20 are completed. See the
[acceptance record](../dev/IMPLEMENTATION_PLAN.md#thread-12-acceptance-and-closure--23-october-2026)
for the retained local safety-refusal failures and precise evidence limits.


## Literal native dashboard (Thread 14)

`renderer/dashboards.py` reads exactly one bounded installed literal
`resources/bases/apex_classes.base` through `importlib.resources`. It uses no
source data, Jinja, override discovery, external tool or publication side effect.
The destination is the existing configured dashboard directory plus the fixed
filename. MTF-2 advances the renderer fingerprint from 3 to 4 for reserved
`sf_created`/`sf_last_modified` UTC `YYYY-MM-DD` projections of valid available
audit timestamps. Absent/null/unavailable/invalid dates yield no projection;
original `sf_*_at` facts and source/graph hashes remain. Exact old baselines still
gate generated-only patches; existing human fields are not backfilled. No schema,
acquisition, ownership or transaction bound changes.
[Dashboard syntax, human debt semantics and ownership](DASHBOARDS.md)
are tested independently from native Obsidian rendering (unavailable).
