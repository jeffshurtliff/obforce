# Offline Apex acquisition

These engineering details describe current implementation contracts, not a stable
public Python API. Use the [quickstart](QUICKSTART.md), [live setup](LIVE_SETUP.md)
and [CLI reference](CLI.md) for command journeys.

The supplied fictional multi-package DX sample is used in the
[offline tutorial](QUICKSTART.md); no sf process or network is needed.

## Selected local scope

The manifest must be bounded JSON with a nonempty `packageDirectories` list.
Every entry requires a portable slash-separated relative `path`; all declared
packages are scanned regardless of `default` or declaration order. The project
root is explicit and absolute; a root link/junction is refused, and its native
ancestor path is resolved once. Config loading already resolves configured root
paths; acquisition cannot reconstruct links that the caller previously resolved.
Every package must exist and be a directory inside that resolved root.

Absolute/drive paths, traversal, empty/dot segments, backslashes, reserved names,
duplicate/overlapping roots, and case/Unicode-equivalent root declarations fail.
Below the root, links, junctions/reparse points, multiply linked files, special
files, and portable filename collisions are refused, including unsupported
files. Directory enumeration/read failures refuse a result. Already observed
file/directory identities, sizes, and modification/change times are rechecked
to detect intervening changes. These checks require a stable source checkout;
they do not promise isolation from a hostile process racing filesystem operations.

For Windows path-to-descriptor comparisons, CPython can expose creation time as
pathname `st_ctime_ns` and change time as descriptor `st_ctime_ns` for the same
file ([CPython #157671](https://github.com/python/cpython/issues/157671)). Only an
exact integer descriptor `st_birthtime_ns` matching the pathname ctime can bridge
this difference, with device, inode, mode, size, and mtime unchanged. The raw
descriptor snapshot, including its own change time, is still compared before
and after reading; full pathname preconditions are rechecked independently.
No time rounding or ctime omission is used, and POSIX retains exact matching.

Only acquisition-relevant manifest fields are interpreted: package paths and the
project-level `namespace`. Unrelated DX/package settings are inert, with duplicate
JSON keys and non-JSON numeric constants still rejected. This is not full
Salesforce project-schema validation. No external `$schema`, package dependency,
login URL, script, or other setting is opened/executed. `.forceignore` rules are
not applied; this inventories available files under declared roots rather
than reproducing Salesforce deploy/retrieve selection. `.git`, `.obsidian`, and
`.obforce` directories inside packages are excluded with a warning after their
own safety checks. No directories outside the declared roots are searched.

Supported pairs are same-directory `Name.cls` and `Name.cls-meta.xml` files in
directories named exactly `classes`, anywhere below a declared package. Class
filenames use 1–40 ASCII letters/digits/underscores starting with a letter. This
validates a bounded input naming subset, not Apex syntax or deployability.
Other types/locations are excluded with `unsupported_files_excluded`. Namespace
comes only from the project manifest: absent/empty means null; otherwise it is
1–15 alphanumeric ASCII characters starting with a letter. No namespace is
inferred from filename prefixes, metadata text, package aliases, or source code.

`Selection` controls explicit namespace inclusion and optional exact class-name
filters. All supported candidates are checked for duplicates, malformed XML,
and missing pairs before filtering, so invalid or incomplete inputs cannot be
hidden by a narrower filter. Two candidate locations for the same canonical key
are a conflict, even if their bytes match or namespace selection excludes them.

## XML facts and refusal bounds

`defusedxml` is a small Python dependency introduced through Poetry for explicit
DTD, entity, and external-reference refusal. The standard library alone does not
provide those same explicit switches. See the project's
[security controls](https://github.com/tiran/defusedxml/blob/main/README.md).
Independent application bounds limit work even for documents without entities:

| Input | Refusal limit |
| --- | --- |
| Project JSON | 65,536 bytes |
| Declared packages | 128 |
| Enumerated package entries, including directories | 50,000 total |
| Relative nesting below project root | 32 segments |
| Each XML file | 65,536 bytes |
| Total supported XML bytes | 16,777,216 |
| Each `.cls` file | 1,048,576 bytes, checked by stat without opening it |
| XML elements / depth | 256 / 16, including the root |

Limits refuse the result; they never silently truncate and return complete.
Only a Salesforce metadata-namespace `ApexClass` root is accepted. DTDs/entities,
wrong roots, malformed encodings/XML, mixed content, duplicate supported fields,
attributes/nested content on supported fields, and invalid values fail with
`ModelError` (exit 2). XML parser diagnostics and input content are not included
in safe exception display strings. Operational read/change failures use exit 1;
duplicate identities/paths use conflict exit 3.

Supported facts are trimmed decimal `apiVersion` strings (`1.0`–`999.0`, a syntax
bound rather than a claim all versions exist) and status `Active` or `Deleted`.
Salesforce documents that `Inactive` is for ApexTrigger, not ApexClass; see the
[Metadata API guide](https://resources.docs.salesforce.com/latest/latest/en-us/sfdc/pdf/api_meta.pdf).
Missing supported fields remain explicitly unavailable with a warning. Unknown
XML elements (including package-version information) are bounded but ignored
with `unsupported_xml_fields`; they never supply audit facts, identity overrides,
or relationships. Apex body contents are never opened, retained, embedded, hashed,
or analyzed. This increment makes no Apex syntax/static-analysis claim.

## Coverage, hashes, and limits

Inventory completeness describes only exhaustion of available selected local
scope. Empty valid packages can be complete locally. A missing source/metadata
mate omits that candidate, reports `missing_apex_pair`, and returns **partial**
inventory/exit outcome 4. A pair with missing optional supported XML facts can
still establish inventory presence; its unavailable fields remain explicit.
Unsafe, malformed, unreadable, duplicate, or over-limit inputs return no result.

Audit is independently `unavailable`, and relationships are `not_collected`, both
with `requested=false` by design. All four audit attributes remain unavailable;
local records have no Salesforce record ID. File/Git dates never substitute for
Salesforce audit dates, and source text never establishes dependency edges.

Components are ordered by canonical key and use unchanged normalized-model validation hashes,
binding, availability wrappers, and provenance label `local-apex-xml-v1`.
Checkout location, package order, raw XML formatting, source body changes, and
filesystem timestamps do not change normalized hashes. Supported fact changes
do. Warnings/coverage are separate records and must travel with the inventory.
Existing selection scope hashes do not encode package manifests/paths; equal
hashes alone cannot prove comparable local scope. No local result authorizes
marking an org component absent/deleted, overwriting a note, or rebinding a source.

The DX subset is informed by Salesforce's
[project schema](https://github.com/forcedotcom/schemas/blob/main/sfdx-project.schema.json).
Runtime never downloads that schema. Local macOS results, hosted CI, native
Windows/Linux filesystem checks, and live lifecycle qualification are separate
evidence classes; see the [roadmap handoff](../dev/IMPLEMENTATION_PLAN.md).
