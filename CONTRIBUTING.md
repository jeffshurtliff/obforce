# Contributing to Obforce

Obforce's long-term purpose is to document the metadata and configuration of an
entire Salesforce org. The current version is scoped to Apex classes; additional
areas are planned for future releases and require separately approved work.

Read [AGENTS.md](AGENTS.md), the current [implementation roadmap](dev/IMPLEMENTATION_PLAN.md)
and the relevant issue before changing behavior. Maintainer instructions define
the authorized scope. Preserve existing changes; keep work focused and reviewable.
The user-facing workflow is in the [quickstart](docs/QUICKSTART.md) and
[CLI reference](docs/CLI.md). Python modules are internal, not a stable public API.

## Development setup

The [approved stable-release plan](dev/STABLE_010_RELEASE_PLAN.md) adds R1–R8
requirements/design, real-input discovery and product acceptance before release.
Its vault config/project-presence/1,000-class targets are not current features.
Routine CI remains offline; separately authorized real DX/live and native
Obsidian checks are mandatory release evidence, with Windows live deferred.
Preserve the Thread 16 review and historical results; do not implement a later
package or promote a stable version merely because foundation threads passed.

Use Python 3.12+ and Poetry 2.4+ within Poetry 2.x. From the checkout:

```sh
poetry env use python3.12
poetry install --with dev
poetry run obforce --help
poetry run python -m obforce --version
```

Static version/license metadata live in `pyproject.toml`. Use Poetry to manage
justified dependency changes and its generated lockfile; never hand-edit
`poetry.lock` or maintain a parallel runtime requirements list. Runtime dependencies
are Click, Jinja2, defusedxml and pure ruamel.yaml; tests/tools are locked in the
dev group. Package resources must work from independently installed artifacts.

Follow PEP 8/257, boundary type hints compatible with Python 3.12, 130 columns,
single-quoted ordinary strings, triple-double docstrings and LF. Use shared
constants, pathlib and subprocess argument lists. Follow the repository Python
header convention with actual generating model and current local date; preserve
Created By and unrelated headers. Do not broadly reformat or suppress lint.

Keep CLI orchestration, read-only sources/parsers, graph evidence, candidate
rendering and synchronization ownership/publication boundaries separate. No new
metadata type, command/API, adoption/migration, backup/Git integration or weakening
of safety/ownership is implied by routine documentation or fixes.

## Offline verification

Use small fictional fixtures and synthetic temporary vaults, deterministic mocks
and separately controlled verification subprocesses. Never invoke real sf or
Obsidian, discover auth/credentials, read `.env`, query an org, execute Apex,
deploy, touch real vaults/settings or install/update CLIs/plugins without separate
explicit authorization. Source/private state and recovery material never belong
in public tests, logs or issues. See [security](SECURITY.md).

Use a stable trusted external parent for both the installed application and
fixtures. Set **TMPDIR, TEMP and TMP** to its dedicated existing fixture root
before Poetry/build/install/tests. Keep coverage and installer ancestry separate
when running concurrent checks. Give each run its own `COVERAGE_FILE` and fresh
exclusive log paths; never share a busy system temp ancestry. Full ancestor guards
can correctly refuse unrelated parent changes. Fix isolation, not production
checks; no race retries, weaker guards or skipped failures.

Run applicable checks from the checkout (substitute fresh absolute log paths):

```sh
poetry check --lock --strict
poetry run ruff check .
poetry run ruff format --check .
poetry run bandit -r src/obforce
poetry run python dev/run_pytest.py --collect-only --log /absolute/isolated/collection.log
poetry run python dev/run_pytest.py --log /absolute/isolated/pytest.log
git diff --check
```

The supervisor runs pytest with combined statement/branch/subprocess coverage.
It enforces 5-minute collection and 45-minute test deadlines, separate 2 MiB raw
and console budgets, 4 KiB lines and exclusive bounded logs. Overflow, timeout or
uncertain child cleanup is an incomplete failure, never a truncated pass.
Collection refuses node IDs over 512 UTF-8 bytes. Use short IDs without shrinking
fixture values. Short tracebacks, no captured dumps and five failure reports bound
diagnostics; case names and slowest 25 durations assist diagnosis. See
[qualification and reproduction](docs/QUALIFICATION.md#bounded-ci-test-execution).

For full candidate qualification, build/install the wheel in a dedicated external
environment, copy tests/developer harnesses separately outside checkout, and run
the supervisor there with its external interpreter. Do not accidentally exercise
an editable checkout. Local tests, native platform probes, mocks, hosted CI, skips
and unavailable checks are separate evidence classes.

## Fresh artifacts and tutorials

Build into a **new empty external directory**, never accumulated `dist/` output.
Use a separate dedicated temporary installer root with stable ancestry. With
TMPDIR/TEMP/TMP set as described above:

```sh
poetry build --output /absolute/isolated/fresh-artifacts
poetry run twine check --strict /absolute/isolated/fresh-artifacts/*
poetry run python dev/check_artifacts.py /absolute/isolated/fresh-artifacts
```

The checker enforces exactly the current wheel/sdist, complete allowlists (36/35
files), metadata/license and reviewed source/resource bytes. It installs each
independently in a fresh external virtual environment, checks pip consistency,
installed imports/resources, actual console/module help/version, space paths,
privacy/bounds, offline sources and synthetic live/graph/parser/planner/transaction/
dashboard/lifecycle probes. Active Python socket/process audit guards and an empty
external-tool PATH apply during application runtime; setup dependency downloads
and authorized synthetic verification children are separate. Nothing is uploaded.

The checker also runs `dev/verify_tutorials.py` support against both actual entry
points in **each independent install**, copying the supplied fictional DX sample.
It verifies every offline guide journey: init/build previews, repeat refusal,
human edits, UUID move, metadata refresh, template override/new-note creation,
no-op bytes/mtimes, whole-batch conflicts and synthetic interruption/recovery.
For the same complete artifact/tutorial exercise directly:

```sh
poetry run python dev/verify_tutorials.py /absolute/isolated/fresh-artifacts
```

Both commands perform independent installs; choose one rather than repeating a
successful run needlessly. All application/fixture setup stays outside checkout
and the empty invocation cwd. Native Windows paths/entry points are established
only by actually running on Windows; local POSIX success is not that evidence.
Native Obsidian rendering/property typing remains unavailable to these checks.

## Evidence, review and delivery

Review prose links, command/help consistency, fictional provenance, privacy and
whitespace for documentation changes. Behavior/support code changes need focused
meaningful verification, applicable tooling and fresh artifact checks. Preserve
all failed/skipped/unavailable observations and uncaptured causes; later passes
do not explain earlier failures. Full benchmark/profile evidence distinguishes
traced allocation from RSS and records instrumentation/host-load limits.

After authorized delivery/CI, inspect each required command log at the exact SHA
and attempt; green summaries can mask failed native commands. Configured matrix
cells are not passed results. No skip qualifies unsupported sf operations,
filesystems, ACLs, power-loss or hostile races. Use
[qualification](docs/QUALIFICATION.md) and the retained maintainer records for
actual results. No runtime network or live access is needed for ordinary checks.

Update help/user docs when behavior changes, the [changelog](docs/CHANGELOG.md)
under Unreleased, the existing authorized issue and roadmap handoff. Report
checks/environment, skipped/unavailable evidence, blockers and accurate Git state.
Keep work unstaged/uncommitted unless instructed. Use `codex/<type>/<description>`
when branch creation is authorized/needed; authorized commits use past tense and
reference the issue (and filename for a one-file commit). Follow current templates.
Posting issues/comments, staging/commit/push/PR/merge, tags/releases/package uploads,
hosted docs and consequential automation require relevant explicit authorization.
A task does not authorize dependent work. Leave acceptance to the maintainer.
Use the [release runbook](docs/RELEASE_RUNBOOK.md) for future release gates.
