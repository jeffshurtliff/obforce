# Obforce

Create and safely refresh documentation of your Salesforce org's metadata and
configuration in an Obsidian vault, while keeping your own knowledge alongside
generated facts.

Obforce's goal is to document the metadata and configuration of an entire
Salesforce org. The current version is scoped to **Apex classes (`ApexClass`)**;
support for additional metadata and configuration areas is planned for future
releases.

Obforce is under development at `0.1.0.dev0`; v0.1.0 has not been released.
It supports explicit offline Salesforce DX projects and read-only live collection
through a separately installed and authorized Salesforce CLI. Python 3.12+ is
required. Windows supports the offline workflow; **Windows `sf` execution is refused**.

Stable 0.1.0 is gated by the [approved product release plan](dev/STABLE_010_RELEASE_PLAN.md):
actual DX/live workflows, vault-owned configuration, project-presence warnings,
successful operation at 1,000 classes and native Obsidian acceptance. These are
remaining requirements; current commands retain their documented external-config
and offline-absence behavior. Stable release awaits these acceptance gates;
any alpha is optional and separately approved.

Start with [installation](docs/INSTALLATION.md), then follow the
[fictional offline quickstart](docs/QUICKSTART.md). No Salesforce account, `sf`,
Obsidian process or plugin is needed for that journey. Installation may download
dependencies; offline application commands make no network calls.

```sh
obforce --help
python -m obforce --version
```

Initialize a new config, preview and build an absent or completely empty
vault, then use `sync` to refresh it. All lifecycle commands require an explicit
config. No config, default org, credential or vault discovery occurs.

Obforce preserves human prose and properties, stable note UUIDs and unique
in-vault moves. It updates only clean generated properties and the marked body
region. Edits to generated notes or the tracked dashboard block the whole batch.
Publication uses guarded replacements, private state and recoverable journals;
it is not an atomic snapshot or an atomic multi-file transaction. Keep independent
vault backups under your own management.

| Guide | Purpose |
| --- | --- |
| [Offline quickstart](docs/QUICKSTART.md) | First build, human edits, move, update, preview and no-op |
| [CLI reference](docs/CLI.md) | Commands, options, paths and exit codes |
| [Live setup](docs/LIVE_SETUP.md) | Separately managed sf authorization and explicit read-only selection |
| [Configuration](docs/CONFIGURATION.md) | TOML schema, root separation and source binding |
| [Refresh](docs/REFRESH.md) | Retained facts, missing/stale/reactivation and comparability |
| [Note ownership](docs/NOTE_FORMAT.md) | Generated boundaries and human content |
| [Customization](docs/CUSTOMIZATION.md) | Safe templates and technical-debt conventions |
| [Dashboard](docs/DASHBOARDS.md) | Packaged Base, ownership and ordinary Markdown use |
| [Coverage](docs/COVERAGE.md) | Independent inventory, audit and relationship limitations |
| [Recovery](docs/RECOVERY.md) | Preview, rollback, cleanup and conservative refusal |
| [Qualification](docs/QUALIFICATION.md) | Demonstrated platforms, historical results and limits |

The current version supports only ApexClass notes. Local files do not prove
full-org inventory, Salesforce audit dates, runtime dependencies or technical debt. Requested platform
relationships remain partial/unavailable. No adoption/migration, force overwrite,
backup/Git integration or stable public Python API is provided.

See [contribution guidance](CONTRIBUTING.md), [security](SECURITY.md),
[maintainer release runbook](docs/RELEASE_RUNBOOK.md) and
[changelog](docs/CHANGELOG.md). The [Apache 2.0 license](LICENSE) applies.
