# Obforce
Create and maintain living documentation for your Salesforce org within an Obsidian vault.

Under development: the `0.1.0.dev0` foundation provides help and installed-version
reporting. Public live Salesforce workflows, note generation, and safe refresh are planned in
the [implementation roadmap](dev/IMPLEMENTATION_PLAN.md).

Internal configuration and normalized-record validation are implemented with
offline tests. See the [configuration](docs/CONFIGURATION.md),
[coverage](docs/COVERAGE.md), and [note ownership](docs/NOTE_FORMAT.md) contracts.
Internal [offline Apex acquisition](docs/OFFLINE_SOURCE.md) inventories supported
pairs in declared DX packages with bounded safe XML and explicit local coverage.
The fictional multi-package sample is testable without Salesforce CLI or network.
The internal [Salesforce CLI process boundary](docs/SF_CLI.md) is tested offline;
Windows execution currently fails closed. The internal [live Apex adapter](docs/LIVE_SOURCE.md)
adds explicit verified org identity, bounded inventory and optional scoped audit names,
validated with synthetic mocked responses only. There are no source acquisition,
rendering, or vault-writing CLI commands yet.

For development, use Python 3.12+ and Poetry 2.4+ within Poetry 2.x:

```sh
poetry install --with dev
poetry run obforce --help
poetry run obforce --version
poetry run python -m obforce --help
poetry run python -m obforce --version
```

Help/version need no Salesforce CLI, authentication, or running Obsidian.
The internal [relationship graph](docs/RELATIONSHIPS.md) retains platform provenance,
reciprocal references and stale evidence. Current collection cannot prove exhaustion
and reports partial/unavailable coverage; runtime tests use synthetic replies only.
The internal [candidate renderer](docs/RENDERING.md) adds installed Jinja defaults,
bounded explicit overrides and deterministic new-note/generated-section strings.
It preserves identity/ownership and coverage contracts without reading or writing notes.
Internal [note preservation](docs/NOTE_FORMAT.md#internal-existing-note-parsing-and-preservation-thread-08)
parses caller-supplied bytes, checks both saved generated baselines and constructs
in-memory patches while preserving supported user content. It adds no discovery,
state loading, filesystem publication or public command.
Thread 09 adds internal [state validation and identity reconciliation](docs/SYNC_SAFETY.md):
bounded read-only explicit synthetic-vault/state inputs, strict saved baselines
and unique moved-note path candidates. Thread 10 adds internal complete read-only
change plans, publication preconditions and bounded redacted reports. Plans retain
strict ownership, coverage and no-write checks; no public lifecycle command,
adoption, state write or filesystem publication is exposed. Thread 10 is accepted
and [#10](https://github.com/jeffshurtliff/obforce/issues/10) is closed after all 12
exact-merge CI cells passed; see the
[acceptance record](dev/IMPLEMENTATION_PLAN.md#thread-10-acceptance-and-closure--20-october-2026).
Thread 11 is next eligible and not started; later threads remain not started.

See [CONTRIBUTING.md](CONTRIBUTING.md) for checks and fresh artifact validation,
[AGENTS.md](AGENTS.md) for agent rules, and [SECURITY.md](SECURITY.md) for private
reporting. The existing [Apache 2.0 license](LICENSE) applies. Platform targets
and configured CI are distinct from verified support; actual evidence is recorded
in the roadmap handoff.
