# Changelog

All notable changes to this project will be documented in this file, following
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Internal read-only offline Apex acquisition, bounded safe XML via
  Poetry-managed `defusedxml`, declared DX package/path validation, duplicate
  refusal, source-preservation checks, and explicit local/partial coverage.
- A fictional multi-package DX example, adversarial offline source/parser tests,
  and acquisition limits/availability documentation. Apex bodies are never read
  or used to infer dependencies; no public command or live access is added.
- Artifact allowlists and independent installed smoke checks for offline source
  and parser modules in both wheel and sdist installations.
- Internal strict version-one TOML loading, config-relative paths, explicit source
  selection, typed errors, and frozen terminal exit precedence.
- Immutable component, independent coverage, relationship, and note-state records;
  structured identities, collision refusal, availability-aware canonical hashes,
  source binding, and graph/path/template invalidation fingerprints.
- Configuration, coverage, and note ownership/schema contracts with fictional
  examples and focused offline regression tests. No connectors, renderer,
  state/vault publication, or public lifecycle commands are introduced.
- Fresh artifact checks now explicitly include the four internal-contract modules
  and exercise installed model imports/hashing in independent wheel/sdist installs.
- Poetry/PEP 621 `0.1.0.dev0` foundation with Python `>=3.12`, Apache 2.0 metadata,
  and console/module help and installed-version reporting.
- Offline CLI tests, Ruff/pytest/coverage/Bandit tooling, and fresh wheel/sdist
  inspection and independent installation checks.
- Test-only CI targeting stable Python 3.12–3.15 on Linux, macOS, and Windows;
  configured matrix cells do not establish platform support.
- Contributor/security guidance and explicit foundation limitations.

### Fixed

- Offline reads now handle Windows CPython's pathname creation-time versus
  descriptor change-time semantics through an exact birthtime comparison,
  preserving all other identity fields, raw descriptor before/after guards,
  and independent pathname checks. Regression tests cover stable reads and
  refusal of changed metadata without introducing platform skips. Delivered
  correction `20bff7f` / merge `6154b74` passed all 12 hosted Python 3.12–3.15
  cells, including Windows tests/build/Twine/independent installs; the existing
  unavailable Windows FIFO case remains explicitly skipped.
- Enforced LF repository text checkouts and separated setup/validation commands
  into individual CI steps so Windows Ruff failures cannot be masked by a later
  successful command. Correction `65305fb` passed standalone checks and artifact
  validation across Linux/macOS/Windows on Python 3.12–3.15.
- Entry-point integration tests now use Poetry's installed Python launcher on
  Windows instead of assuming its editable install creates `obforce.exe`. Added
  cross-platform regression coverage for interpreter-driven console invocation;
  independent pip artifact checks retain direct executable validation.
