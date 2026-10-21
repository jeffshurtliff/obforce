# Configuration contract

Thread 02 implements an internal, read-only config loader and source selection.
The CLI still supports only help/version. The `init`, `build`, `sync`, and
`recover` workflows remain planned for Threads 12–13; the following config is a
fictional input for internal validation, not a working generation tutorial.
Internal Python interfaces are versioned implementation details, not a stable API.

## Explicit loading and schema

The caller passes exactly one config path to `load_config(Path(...))`. There is
no config discovery, environment-variable configuration, credential discovery,
fallback file, default Salesforce org, or directory creation. A relative config
filename is interpreted from the caller's working directory; paths *inside* it
are resolved from the config file's resolved parent directory. A symlinked config
therefore uses its target's directory. Loading opens only that config file;
path resolution may inspect filesystem path components, without reading source
files, templates, notes, or state.

UTF-8 TOML is limited to 65,536 bytes. Duplicate keys, malformed TOML, unknown
keys/tables at any level, wrong types, excessive parser nesting, and unsupported schema versions fail.
No parser error includes raw TOML or a potentially sensitive value. TOML has no
null literal. Omit an optional value instead of providing a placeholder null.
A missing explicit file is a configuration error; permission/read failures are
operational errors. No invalid explicit file is ignored in favor of a default.

```toml
schema_version = 1
workspace_id = "demo-org"
vault = "./DemoKnowledge"

[source]
mode = "local"
project = "./sample-sfdx"

[layout]
apex_classes = "Custom Code/Apex Classes"
dashboards = "Dashboards"

[options]
include_namespaced = false
include_audit_names = true

# Optional explicit override root; internal candidate rendering only (Thread 07).
[templates]
directory = "./demo-templates"
```

| Table | Accepted keys and requirements |
| --- | --- |
| Root | Required `schema_version` (integer exactly 1), `workspace_id`, `vault`, `source`; optional `layout`, `options`, `templates` |
| `source` | Required `mode`; local requires `project` and forbids `org`; live requires `org` and forbids `project` |
| `layout` | Optional `apex_classes`, `dashboards`; defaults shown above |
| `options` | Optional boolean `include_namespaced` (false), `include_audit_names` (true); explicit false is retained |
| `templates` | When present, requires only `directory`; an empty table is invalid |

`workspace_id` contains 1–128 ASCII letters, digits, underscores, or hyphens.
Strings cannot be empty, have surrounding whitespace, or contain control
characters. Arbitrary Salesforce field/type selection, command configuration,
credentials, API versions, logging, and force-overwrite settings are unsupported
config keys. The supported component type is ApexClass only. Optional internal
name filters in the normalized selection record are not exposed config options.

## Paths and selectors

`vault`, `source.project`, and `templates.directory` accept native absolute paths
or config-relative paths. `..` in these root paths resolves normally; it does not
permit traversal in generated relative paths. `~`, `$` and `%` expansion forms
are rejected; use literal paths. Non-native drive/backslash paths fail rather
than being interpreted as local relative names. Paths need not exist at this
stage. Loading does not validate an SFDX project or contact Salesforce.
The separate [offline acquisition](OFFLINE_SOURCE.md) phase validates declared
DX package roots and supported Apex pairs using the loaded project path,
logical workspace binding, and explicit namespace selection.

Layout directories and note-state paths use `/`, remain relative to the vault,
and reject empty/`.`/`..` segments, drive/absolute paths, backslashes, control
characters, Windows reserved device names, invalid Windows filename characters,
and trailing dots/spaces. These relative paths also exclude `.git`, `.obsidian`,
and `.obforce` control-directory segments. Root paths are resolved before overlap
checks: vault and source/template roots must be disjoint, and config cannot be inside the
vault. This is an early refusal, not a safe-write certification. Repository
separation, links/junctions, special files, collisions, permissions, parent
changes, and concurrency must be checked again by later publication threads.

For example, `/fictional/work/obforce.toml` with `project = "./sample-sfdx"`
means `/fictional/work/sample-sfdx` regardless of the caller's working directory.
For a live config, replace the whole source table with:

```toml
[source]
mode = "live"
org = "fictional-sandbox"
```

Live targets must be explicit, nonempty, and cannot begin with `-`. The selector
is an alias/username for the internal [live adapter](LIVE_SOURCE.md), not verified
org identity or permission to query it. Loading never inspects authentication or invokes `sf`.

Precedence for supported selection is explicit invocation, config, then listed
non-selector defaults. Future initialization requires exactly one absolute
project path or live target; both or neither fail. Given a config, only a live
`org` override is supported. A project override or local/live switch fails.
The adapter verifies the actual org ID with a minimal query before inventory;
the live override must subsequently match the verified state org binding; an
alias change alone does not establish a new source. No rebinding workflow is
implemented. See [coverage and identity](COVERAGE.md).

## Errors and exits

Typed internal exceptions use Click's existing exception display/exit protocol.
There are no new production CLI options or commands. Test-only Click commands
exercise operational/config/conflict/coverage errors without source access.
Callers provide concise safe diagnostics, never raw responses or note content.

| Code | Meaning | Error type |
| --- | --- | --- |
| 0 | Complete selected operation or valid no-op | Success outcome |
| 1 | Operational/read/process failure | `OperationalError` |
| 2 | Invalid usage, config, or normalized input | Click usage errors, `ConfigError`, `ModelError` |
| 3 | Ownership/identity conflict or recovery required | `ConflictError` |
| 4 | Completed operation with requested incomplete/unavailable coverage | `CoverageError` or coverage outcome |

Normally validation stops at the first failing phase. If outcomes must be
combined, precedence is **3, 2, 1, 4, 0**, independent of encounter order or numeric
magnitude. Recovery/conflicts must not be hidden by a later generic failure.
A truncated requested live inventory cannot return success. By-design offline
audit/dependency exclusions are reported explicitly but do not alone force 4.
See [the independent coverage contract](COVERAGE.md).

The internal [renderer](RENDERING.md) now loads only the two documented known
assets from this explicit root, falling back per absent file to installed defaults.
Invalid existing overrides refuse. No public generation command is introduced.


Thread 08 [parses and patches caller-supplied note bytes](NOTE_FORMAT.md#internal-existing-note-parsing-and-preservation-thread-08)
using in-memory state/baselines only. It adds no config keys, command, file loading
or vault discovery. Unsupported/edited managed content raises redacted conflict
3; invalid caller contracts use 2. Existing precedence and source controls remain.


Thread 09 separately accepts explicit absolute vault/state paths and normalized
binding/selection for internal [read-only reconciliation](SYNC_SAFETY.md). It never
loads/discovers config, resolves auth/default orgs, or uses cwd/home discovery.
The caller must supply disjoint source/template/application roots for overlap
refusal and independently verified canonical org identity for live bindings.
No public config/state initialization or migration command is added.

Thread 10's internal `plan_changes` takes explicit normalized source/coverage/
graph inputs and absolute vault/state/excluded roots. Templates are already
loaded explicit assets; no config/source/template/auth discovery occurs during
planning. Existing saved graph and retained absent-component facts are explicit
inputs, never reconstructed from current notes. The comparable accessible-live-
inventory attestation defaults false. See the [planner contract](SYNC_SAFETY.md#thread-10-pre-implementation-planner-contract--20-october-2026)
for finite bounds, immutable preconditions, blocked results and safe report fields.
`report_plan` returns text/outcome without printing or writing. No new config
key or public command is introduced; outcome precedence remains 3, 2, 1, 4, 0.

Thread 11 adds internal transaction/recovery calls with explicit absolute paths and
caller-supplied planner inputs. No config key, discovery, public command or auth
access is added. A persistent private writer.lock may remain after an actual
transaction; no-op and both previews create nothing. Recovery receives explicit
vault/state/excluded roots and reads only validated local journal evidence. See
[transaction safety](SYNC_SAFETY.md#thread-11-pre-implementation-transaction-contract--20-october-2026).
