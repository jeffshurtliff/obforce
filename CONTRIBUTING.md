# Contributing to Obforce

Read [AGENTS.md](AGENTS.md) and the [implementation roadmap](dev/IMPLEMENTATION_PLAN.md)
before changing files. They define scope, safety contracts, and the current thread.
The production CLI exposes help and version only; public collection workflows,
rendering, and vault mutation remain planned. The internal Python modules are not a stable public API.

Thread 02 adds internal config/model validation; see [configuration](docs/CONFIGURATION.md),
[coverage](docs/COVERAGE.md), and [note ownership](docs/NOTE_FORMAT.md) for frozen
contracts and their implementation boundaries. The production CLI is unchanged.
Thread 03 adds internal [offline Apex acquisition](docs/OFFLINE_SOURCE.md) and a
fictional multi-package DX sample; it adds no public command or live access.
The delivered Windows identity correction passed all 12 hosted cells, including
Windows tests and independent artifact installations. Thread 03 is accepted;
see its [acceptance record](dev/IMPLEMENTATION_PLAN.md#thread-03-acceptance-and-closure--19-october-2026)
for exact commit/run evidence and the retained FIFO/native-lifecycle limits.

Thread 04 adds an internal [bounded Salesforce CLI process boundary](docs/SF_CLI.md),
with synthetic protocols and fictional child-process tests only. POSIX direct
execution is implemented; Windows execution fails closed pending safe launcher
and cleanup support. No public command or live inventory adapter is added.
Thread 04 is accepted with exact-merge CI verified across all 12 cells; Windows
skips/refusals do not establish Windows sf execution support. See the
[acceptance record](dev/IMPLEMENTATION_PLAN.md#thread-04-acceptance-and-closure--19-october-2026).
Future Windows execution is tracked in [#18](https://github.com/jeffshurtliff/obforce/issues/18),
outside v0.1.0 and without blocking Thread 05.

Thread 05 adds the internal [live Apex inventory/audit adapter](docs/LIVE_SOURCE.md),
with explicit verified identity, bounded SELECT pagination, scoped optional audit
queries and independent coverage. Tests mock process collection; no real sf/org
access or Windows transport qualification is claimed. No public command is added;
Thread 05 is accepted with all 12 exact-merge hosted cells passing; see the
[acceptance record](dev/IMPLEMENTATION_PLAN.md#thread-05-acceptance-and-closure--19-october-2026)
for actual counts/skips and artifact evidence.

Thread 06 adds the internal [platform relationship graph](docs/RELATIONSHIPS.md),
using bounded equality probes and exact source verification. Current MCD restrictions
prevent exhaustion proof, so requested platform coverage remains partial/unavailable.
Graph/stale/invalidation tests use synthetic metadata and mocked processes. No public
command, dependency or Windows transport is added. Thread 06 is accepted at merge
`2aa8d2b`: all 12 exact-merge hosted cells passed checks/builds/Twine and both
independent installs. Linux/macOS each passed 517 tests; Windows each passed
506 with 11 expected skips, without qualifying Windows sf execution. See the
[acceptance record](dev/IMPLEMENTATION_PLAN.md#thread-06-acceptance-and-closure--20-october-2026).
Thread 07 adds internal [candidate rendering](docs/RENDERING.md) with packaged
Jinja defaults and explicit bounded overrides. Thread 07 is accepted at
implementation `b4658eb` / merge `eedeff4`; exact-merge run `39440606470`, attempt 1,
passed all 12 cells: Linux/macOS 618 passed each, Windows 606 passed/12 expected
skips each. All checks/builds/Twine and 24 independent installs passed; Windows
sf execution remains refused. See the
[acceptance record](dev/IMPLEMENTATION_PLAN.md#thread-07-acceptance-and-closure--20-october-2026).
Thread 08 adds internal [managed-note byte parsing/preservation](docs/NOTE_FORMAT.md#internal-existing-note-parsing-and-preservation-thread-08)
with bounded safe round-trip YAML, strict saved property/body comparisons and
source-span patches. Thread 08 is accepted at implementation `d79f5e2` / merge
`dba53ab`; run `39453887153`, attempt 1, passed all 12 cells: Linux/macOS 744 passed
each; Windows 732 passed/12 expected skips each. Every standalone check, fresh
build/Twine and all 24 independent installs passed; Windows sf remains refused.
See its [acceptance record](dev/IMPLEMENTATION_PLAN.md#thread-08-acceptance-and-closure--20-october-2026).
Thread 09 is next eligible; Threads 09–17 and enhancement #18 remain NOT STARTED.

## Development setup

Use Python 3.12 or newer and Poetry 2.4.x or newer within Poetry 2.x. From the
checkout, select your installed interpreter and install the locked development tools:

```sh
poetry env use python3.12
poetry install --with dev
poetry run obforce --help
poetry run python -m obforce --version
```

The static version lives in `pyproject.toml`; CLI version reporting reads installed
distribution metadata. Commit `poetry.lock` with approved dependency changes. Use
`poetry add` or `poetry update`; never hand-edit the lockfile or add a parallel
runtime requirements file. Runtime dependencies are Click, Jinja2 (candidate
templates/sandbox), and `defusedxml` for explicit offline XML DTD/entity/external-
reference refusal. Thread 08 adds `ruamel-yaml >=0.19.1,<0.20.0` (locked 0.19.1)
for bounded pure round-trip parsing and source spans; no optional C extension.
Candidate serialization continues to use a flat YAML-compatible JSON subset. Development
tools are pytest, pytest-cov, Ruff, Bandit, and Twine.

## Checks

```sh
poetry check --lock --strict
poetry run ruff check .
poetry run ruff format --check .
poetry run pytest -q
poetry run pytest --cov=obforce --cov-report=term-missing
poetry run bandit -r src/obforce
git diff --check
```

Tests are deterministic and offline, using temporary directories and synthetic
inputs. They never discover Salesforce authentication or use a real vault. The
entry-point integration tests block Python socket operations and remove external
tools from `PATH`. Dependency installation can require network access; installed
help/version operation does not. Do not install or invoke Salesforce CLI or
Obsidian for foundation tests.

Poetry's editable install generates an extensionless Python console script and,
on Windows, a `.cmd` wrapper. Integration tests invoke that installed Python
script through the active interpreter on Windows, with the same invocation
tested on other platforms. They fail if the script is missing. The separate
artifact checker directly runs pip-installed console executables (`obforce.exe`
on Windows) from clean wheel/sdist environments; neither check substitutes the
module entry point for the console script or skips Windows coverage.

Ruff targets Python 3.12, 130 columns, single-quoted ordinary strings,
triple-double-quoted docstrings, spaces, and LF. Use type hints at boundaries and
the Python headers in AGENTS.md, with the actual generating model and local date.

The repository `.gitattributes` keeps text checkouts LF on Windows as well as
POSIX hosts, retaining automatic binary detection. Each CI environment-selection,
installation, and validation command runs in its own step so a later successful
native command cannot mask an earlier failure in PowerShell. A green job summary
is insufficient when command logs show a failed check. The Windows formatter
correction is delivered and verified; see the roadmap's
[Thread 02 acceptance record](dev/IMPLEMENTATION_PLAN.md#thread-02-acceptance-and-closure--19-october-2026)
for the exact commit and hosted evidence.

## Fresh artifact validation

Build into a **new, empty directory** outside the checkout (substitute your own
temporary absolute path). Do not reuse accumulated `dist/` contents:

```sh
poetry build --output /tmp/obforce-candidate
poetry run twine check --strict /tmp/obforce-candidate/*
poetry run python dev/check_artifacts.py /tmp/obforce-candidate
```

Use an appropriate temporary path on Windows. The checker inspects complete
wheel/sdist file lists and metadata, checks the unchanged root license against
both archives, and installs each artifact independently in a fresh temporary
virtual environment outside the checkout. Installation may download runtime and
isolated build dependencies. It then checks imports, package-file access through
`importlib.resources`, installed internal model hashing, console/module help and
version, installed offline acquisition/parser and synthetic CLI-envelope/live-adapter/
relationship-graph checks, rejection of future commands, dependency consistency, and no
working-directory writes with external tools absent. Thread 07 adds renderer
modules and two explicitly allowlisted installed Jinja assets, full synthetic
output comparison and runtime network/process refusal. Thread 08 deliberately
adds both sync modules and installed synthetic parsing/patching probes, complete
expected-output comparison, exact CRLF baselines, user preservation
and typed conflict/unsafe-input checks under the same runtime guards. Bases assets
remain Thread 14. The checker never publishes or uploads artifacts.

The test-only workflow targets stable Python 3.12–3.15 on Linux, macOS, and
Windows. Configured cells are not qualification evidence. See the roadmap handoff
for actual local results, hosted gaps, and review status. Runner setup and package
installation use the network; the application tests use no live services.

## Scope, privacy, and review

Use small fictional fixtures under `tests/fixtures/` when needed; keep scratch
output under `tests/fixtures/_scratch/` or temporary directories. Private vendor
references may live in ignored `local/vendor_docs/`; never copy real metadata,
credentials, audit identities, vaults, state, or recovery files into public files.
See [SECURITY.md](SECURITY.md) for private reporting.

Keep changes focused, update [the changelog](docs/CHANGELOG.md) under `[Unreleased]`,
and synchronize the roadmap with the existing thread issue when authorized.
Preserve the Apache 2.0 license and maintainer changes. Leave agent work unstaged
and uncommitted unless explicitly requested. Do not create issues, PRs, push,
publish, or close tracking issues without explicit authorization.

For authorized branch creation, use `codex/<type>/<description>` for Codex work.
When commits are authorized, use past-tense messages and reference the issue;
mention the filename for a single-file commit. A requested thread does not
authorize its dependent thread. Maintainer acceptance remains separate from
local checks or configured CI.
