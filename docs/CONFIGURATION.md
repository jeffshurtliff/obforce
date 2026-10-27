# Configuration contract

Thread 02 implements an internal, read-only config loader and source selection.
Public `init`, initial `build` and `recover` are implemented in Thread 12;
Thread 13 adds [managed-vault sync](REFRESH.md) with private persistent evidence.
The approved [design](../dev/THREAD_13_PERSISTENT_EVIDENCE_DESIGN.md) records the
state-version split, live scope declarations and per-invocation attestation.
See the public command contract below and fictional
[quickstart](QUICKSTART.md). The following config also documents internal validation.
Internal Python interfaces are versioned implementation details, not a stable API.

## Explicit loading and schema

The caller passes exactly one config path to `load_config(Path(...))`. There is
no config discovery, environment-variable configuration, credential discovery,
fallback file, default Salesforce org, or directory creation. A relative config
filename is interpreted from the caller's working directory; paths *inside* it
are resolved from the config file's resolved parent directory. A symlinked config
therefore uses its target's directory internally. Public lifecycle commands
refuse symlinked configs through their stricter publication guards. Loading opens only that config file;
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
Windows unrooted relative paths may use native backslashes (for example,
`..\Team Space\Config with spaces.toml`) or forward slashes. This applies to the
explicit CLI config argument too; it is relative to cwd. Drive-relative
`C:Config.toml` and current-drive-rooted `\Config.toml` or `/Config.toml` are
ambiguous and refused. POSIX still refuses Windows relative backslash syntax.
The public lexical ancestor, spelling, overlap and filesystem guards remain.
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
The public Thread 12 commands use the same typed errors. Offline tests exercise
operational/config/conflict/coverage outcomes without real source access.
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

## Public initialization and initial build (Thread 12)

Thread 12 implements the first-build journey. Thread 13 adds [refresh](REFRESH.md).
All commands are noninteractive. `--config` is always required; there is no search
of cwd, parents, home, environment, auth or existing vaults.

```sh
obforce init --config ./obforce.toml --source ./FictionalProject --vault ../Knowledge --workspace-id fictional
obforce init --config ./preview.toml --org fictional-sandbox --vault ../OtherKnowledge --workspace-id fictional --dry-run
obforce build --config ./obforce.toml --dry-run
obforce build --config ./obforce.toml
obforce recover --config ./obforce.toml
obforce recover --config ./obforce.toml --rollback
obforce recover --config ./obforce.toml --cleanup
```

Exactly one `init` source selector is required: `--source PATH` or `--org TARGET`.
The config filename is invocation-relative; source/vault arguments are relative
to the config parent, including normal `..` roots. Native absolute paths are also
accepted. No expansion is added. Init preserves the accepted layout/options
(default audit names true, namespaces false); edit a valid config explicitly to
change these or select a known template override. Init validates selection and
paths without acquiring source metadata. A missing source can be configured but
will fail acquisition during build. Its config parent must already exist.

Init serializes escaped UTF-8 TOML values, validates the complete bytes through
the same strict schema, and creates one file exclusively with requested mode
0600. Any existing entry refuses. It never replaces a file or creates config
parents. A failure after exclusive creation may retain partial config evidence;
inspect it manually rather than overwrite it. `--dry-run` creates nothing.

Build uses the configured source. `--org TARGET` may override only a live source;
it never changes mode or workspace. Live builds, including previews, additionally
require both `--sf-executable ABSOLUTE_PATH` and `--sf-directory ABSOLUTE_PATH`.
The latter is an existing neutral directory disjoint from source/template/vault/
config/application roots. There is no executable search. Actual org identity is
verified by the accepted live adapter before graph and note planning. Real
operations require the user's authorization; implementation/tests used mocks only.
Windows sf remains refused; no wrapper or launcher workaround is added. The CLI
may change its own auth/cache/config state during authorized read queries; see
[the unchanged transport boundary](SF_CLI.md). Offline rejects live process options.

Build requires an absent or completely empty destination. All entries, including
hidden files, `.obsidian`, state, managed notes and a retained writer lock, block
initial build. It never adopts or resumes a vault. See [setup and recovery safety](SYNC_SAFETY.md#public-initial-setup-and-recovery-thread-12).
Missing destination/parents can be previewed without creation. Actual setup creates
at most 32 guarded portable directories before a freshly validated existing-vault
transaction. Refused publication can leave explicit setup/control evidence; do
not delete it automatically or retry build as a recovery operation.

Recover defaults to read-only validated preview. `--dry-run`, `--rollback`, and
`--cleanup` are mutually exclusive. Rollback applies only before recorded commit;
cleanup applies only to committed/cleaning evidence. Selection is rechecked under
the existing continuous writer lock. Recovery never collects source/templates,
invokes sf, discovers auth or reconstructs graph evidence. Missing source metadata
does not prevent recovery. No-op and previews preserve exact bytes/mtimes.

Reports contain fixed categories, bounded counts and independent coverage states,
including requested flags and warning counts. Precedence remains **3, 2, 1, 4, 0**.
Public recovery-required failures use 3 even when the internal writer retains an
original operational outcome; a valid recovery preview returns 0 with an explicit
recovery-required flag. Partial requested coverage can publish a first build with
4 and never proves absence. By-design offline audit/relationship exclusions alone
allow 0. State/journal bounds and schema-1 journal refusal remain unchanged.


Thread 12's Windows correction retains each original lexical spelling as well as
the resolved path. A resolver returning stored `VAULT` for requested `Vault` must
not erase the alias refusal. Every original segment receives the same bounded
parent-name comparison used for resolved paths, with ordinal string comparison
independent of native Path equality. This applies to config/source/template/vault
roots and missing suffixes in init/build/recover, including previews. No retry,
case normalization workaround, relaxed observation or new skip is added.


## Public refresh and private evidence (Thread 13)

`sync --config PATH [--dry-run]` requires existing managed state-document schema 2
with evidence schema 1. No automatic schema-1 upgrade/adoption is offered. NoteState
remains schema 1; journal schema 2 retains explicit legacy recovery support.
No config schema/key changes are made.

Live-only build accepts optional `--inventory-scope-id ID`. Sync accepts a matching
ID and `--attest-comparable-inventory` for this invocation's continuity assertion.
The attestation requires an explicit ID established at build; null declarations
cannot be initialized later. Offline rejects both flags. Existing explicit live
process paths/org verification rules apply. Missing transitions additionally need
complete supported comparable inventory; unknown continuity preserves absence and
reports incomplete evaluation. See [the full contract](REFRESH.md).


## Protected native dashboard (Thread 14)

Public build/sync now include one `Apex Classes.base` under `layout.dashboards`
(default `Dashboards`). No config key/schema change or additional command.
The whole file has exact saved ownership in an optional dashboard-schema-1
record within evidence-bearing state-document schema 2. Editing/moving/removing
it or changing its configured directory blocks the whole batch. A valid Thread
13 vault can add it only at an absent destination; no file adoption or note
migration. See [dashboard behavior, limits and recovery](DASHBOARDS.md).

MTF-2 adds no configuration knobs: new notes use Boolean `technical_debt: false`,
blank `tech_debt_severity`/`tech_debt_status`, and blank `last_reviewed`.
These human fields remain creation-only and are not backfilled on existing notes.
Available audit timestamps additionally supply reserved UTC `sf_created` and
`sf_last_modified` dates. Lifecycle stays in notes but leaves the default table.
