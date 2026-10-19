# Internal Salesforce CLI process boundary

Thread 04 implements `sources/sf_cli.py`, an internal transport boundary with
mocked protocol tests and fictional Python child-process tests. It adds no
public CLI command or live source adapter. It does not verify an org, collect
Apex inventory/audit fields, normalize records, or decide collection coverage.
Thread 05 remains unstarted. Internal interfaces are not a stable Python API.
No Salesforce CLI installation or authentication is needed for tests/help/version.

Thread 04 is accepted and delivered at merge `6980b26`. Exact-commit
[run 39314787749](https://github.com/jeffshurtliff/obforce/actions/runs/39314787749)
passed all 12 Linux/macOS/Windows Python 3.12–3.15 cells: Linux/macOS each
executed 340 tests; Windows each reported 329 passed and 11 expected skips.
Every cell passed standalone checks, fresh build/Twine and both independent
artifact installations. The Windows skips include the nine POSIX collector
cases, POSIX wrapper-symlink case and existing FIFO case. These results qualify
those tests/refusals, not real CLI or Windows sf execution. Future native Windows
support is tracked in [#18](https://github.com/jeffshurtliff/obforce/issues/18),
an unstarted enhancement outside v0.1.0 that does not block Thread 05.

## Execution contract and platform boundary

A caller must separately obtain authorization for the selected live org and
operations. Constructing a request or loading a live config grants none.
`run_sf` takes one explicit absolute `Path` to a trusted CLI installation and one
existing absolute working directory. There is no executable discovery, PATH
search, default org, arbitrary command string, extra flag list, shell, stdin,
query file, output file, or plugin/auth/deploy/Apex-execution operation.

The allowlist is exactly:

| Internal operation | Arguments following the executable |
| --- | --- |
| `VERSION` | `version --json` |
| `QUERY` | `data query --json --target-org <target> --query <SELECT text>` |
| `TOOLING_QUERY` | Same query arguments, followed by `--use-tooling-api` |

Targets must be explicit, nonempty, trimmed, at most 256 characters, without
control characters or leading `-`. Spaces and shell metacharacters stay in one
argument. Queries are complete internal-caller SELECT statements, at most
16,384 characters; controls, comments, and semicolon-separated statements are
refused. This is a conservative transport gate, not a SOQL grammar validator.
Future callers must use reviewed field/query templates and validated values;
this module never interpolates user values into SOQL. No Thread 05 query
selection or org-identity logic is implemented here.

Only **POSIX direct execution** is implemented. The supplied path resolves to an
executable regular file; symlinked installations resolve to their target. Trust
in the chosen installation, its interpreter, plugins and filesystem remains the
caller's responsibility. This is not executable authenticity verification or
protection against a hostile installation/path replacement.

`.cmd`, `.bat`, `.ps1`, and `.com` command wrappers are refused, including wrappers
hidden behind symlinks. **All Windows execution, including native `.exe` paths,
fails closed** pending a safe native launcher and bounded descendant-cleanup
implementation. No wrapper parsing, inferred sibling Node launcher, `cmd /c`,
PowerShell, or `shell=True` fallback is available. Mocked Windows refusal tests
are not native qualification. Other platforms also fail closed.

The caller selects a neutral working directory outside source/vault/template
roots; it is validated but never created. No Obforce files are written. The
child receives only inherited `HOME`/`TMPDIR`, fixed language/CLI controls and
`PATH=os.defpath`. Arbitrary `SF_*`/`SFDX_*` overrides, tokens, proxies,
`NODE_OPTIONS`, Python hooks and inherited PATH entries are not forwarded.
Home is passed to let a future authorized CLI reuse its own existing auth;
Obforce never opens auth stores or `.env`. A shebang using `env node` therefore
requires a trusted Node on that standard path; other installation layouts may
fail operationally and have not been qualified. No runtime/CLI installation or
update is performed. Fixed controls disable telemetry/auto-update/update checks,
set fatal CLI logging and cap CLI query auto-fetch at 10,000 records. These are
controls for a trusted CLI, not isolation from its plugins. The CLI may itself
read/write auth/config/log/cache state or refresh authentication during future
authorized read queries. Read-only Salesforce operations do not imply a
third-party filesystem or network sandbox.

## Collection and refusal limits

| Boundary | Hard maximum |
| --- | --- |
| Process wall deadline | 60 seconds |
| Stdout | 8,388,608 bytes |
| Stderr | 65,536 bytes |
| JSON container depth | 32 |
| Accepted JSON value nodes | 100,000 |
| Returned records | 10,000 |
| Cleanup wait | 2 seconds |

Callers can reduce time/byte limits; zero, nonfinite, boolean, negative and
above-ceiling values fail. POSIX binary pipes are nonblocking and multiplexed.
Each read requests at most remaining allowance plus one overflow sentinel byte;
stdout accumulation never exceeds its allowance, and stderr is counted and
discarded. Overflow terminates the request before text decoding or JSON parsing.
There is no `communicate()` buffer, background reader thread, spool file, or
truncation-as-success behavior. The deadline covers both pipe draining and
leader exit, including closed pipes and descendants holding pipes open.
OS process creation itself cannot be forcibly interrupted by this Python gate.

A fresh process session/group is killed and the direct child reaped on success,
failure, overflow, timeout, or interruption. Pipes and selector descriptors close.
Failure to confirm cleanup is an operational error. Cooperative descendants in
the same group are covered, even after the leader exits; hostile descendants
that escape the group and OS-uninterruptible processes are outside this trusted
local executable boundary. No general process-containment guarantee is claimed.

## JSON and privacy

UTF-8 output must contain exactly one bounded JSON object. Duplicate keys,
nonfinite numbers, excessive nesting/nodes, invalid JSON/encoding, missing known
fields and wrong known-field types fail. Depth is scanned before decoding JSON;
node counts are checked on the byte-bounded parsed object. Warning texts, error
messages, stack traces, raw stdout/stderr, selectors and paths are never included
in errors or logging. No logging is performed. Errors suppress raw exception
chains and use fixed `ConfigError` (exit 2) or `OperationalError` (exit 1)
diagnostics; a CLI exit/status never becomes an Obforce exit code directly.
Two line-specific Bandit annotations cover the intentional subprocess import
and shell-free call after explicit executable/argv validation; no global rule is
disabled.

Query success requires exit 0 plus integer `status: 0`, an object `result`, an array of object
`records`, a nonnegative integer `totalSize` at least the returned count, and a
boolean `done`. `records` is an array of objects. An output-file result is
unsupported. Optional `nextRecordsUrl` must be a bounded nonempty string and is
retained as private data, never followed. Warnings accept the framework's string
or structured-object forms but expose only presence. Compatible extra query
properties remain private for a later adapter to interpret; they are not trusted
normalized facts. Version success uses the bare oclif object and retains only
`cliVersion`, `architecture`, and `nodeVersion` strings. Nonzero query errors
validate `name`, `message`, and positive integer `status`; version errors use an
`error` object with `name`/`message`. Malformed errors fail safely too.

The reply's data/continuation fields are excluded from its repr. They remain
private: callers must not serialize/log the reply or use raw fields in notes.
Stderr exposes only presence. A successful exit with an error envelope fails;
a failure exit with a success envelope also fails. Empty stdout never succeeds.

`done`, `totalSize`, returned records, continuation, and warning/stderr presence
are observations. Even `done: true` with fewer records than `totalSize`, or with
a continuation signal, remains visible to the later adapter. No success/empty
result proves complete inventory, verified org identity, accessible comparable
scope, or audit/dependency completeness. See [coverage](COVERAGE.md) and
[configuration/error precedence](CONFIGURATION.md). Coverage errors and normalized
identity remain the later adapter's responsibility.

## Official contracts reviewed on 19 October 2026

Reviewed via documentation/source reads, without executing `sf`:

- [Salesforce data query reference](https://developer.salesforce.com/docs/platform/salesforce-cli-reference/guide/cli_reference_data_query.html)
  documents query, explicit target, JSON and Tooling flags. Obforce deliberately
  omits file/output/bulk/deleted-row options and never relies on CLI default orgs.
- [Salesforce JSON support](https://developer.salesforce.com/docs/platform/sfdx-setup/guide/sfdx-dev-cli-json-support.html)
  explains command schemas and additive JSON evolution.
- Official [query implementation](https://github.com/salesforcecli/plugin-data/blob/a0cdb671f42af74e31a782c34c5cdcc22e1ea5b0/src/commands/data/query.ts)
  uses auto-fetch with a configurable limit and warns about missing records;
  [result schema](https://github.com/salesforcecli/plugin-data/blob/a0cdb671f42af74e31a782c34c5cdcc22e1ea5b0/schemas/data-query.json)
  requires records, totalSize and done. The schema is for the inner result.
- [SfCommand serialization](https://github.com/salesforcecli/sf-plugins-core/blob/efe58eff7bf546045e6beca16856104ffcc7eca9/src/sfCommand.ts)
  wraps query success in status/result/warnings.
- [oclif version](https://github.com/oclif/plugin-version/blob/fb2f672e93879a94bb3365f6d5f878715a53a2ae/src/commands/version.ts)
  returns three fields without verbose mode;
  [oclif core](https://github.com/oclif/core/blob/b5c0aefa2c68c921a5c85eadd12fce097ddc33d1/src/command.ts)
  serializes that result directly and failures under `error`.
- [Python subprocess security](https://docs.python.org/3.12/library/subprocess.html#security-considerations)
  warns that Windows batch files may invoke a system shell even with `shell=False`.
  This is the reason for wrapper refusal, not a reason to enable a shell.

These are observed official contracts, not a tested installed CLI/version pin.
No real CLI or platform support claim follows from source inspection. Refresh
contracts and obtain targeted authorization before any future live validation.
