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
runtime requirements file. Runtime dependencies are Click and `defusedxml` for
explicit offline XML DTD/entity/external-reference refusal. Jinja2 and
`ruamel.yaml` wait for the threads that use them. Development tools
are pytest, pytest-cov, Ruff, Bandit, and Twine.

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
version, installed offline acquisition/parser checks, rejection of future commands,
dependency consistency, and no
working-directory writes with external tools absent. There are no template/Bases 
assets yet; their installed resource checks belong to Threads 07 and 14. The 
checker never publishes or uploads artifacts.

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
