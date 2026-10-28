# Command reference

Both entry points accept the same arguments: `obforce` and `python -m obforce`.
Commands are noninteractive. `--help` works at the root and on each command;
root `--version` reports installed distribution metadata. No other commands or
stable Python API are provided.

| Command | Required selection | Other options |
| --- | --- | --- |
| `init` | `--config PATH`, exactly one of `--source PATH` / `--org TARGET`, `--vault PATH`, `--workspace-id ID` | `--dry-run` |
| `build` | `--config PATH` | `--dry-run`, live-only `--org TARGET`, `--sf-executable PATH`, `--sf-directory PATH`, `--inventory-scope-id ID` |
| `sync` | `--config PATH` | Same live options as build, plus `--attest-comparable-inventory` |
| `recover` | `--config PATH` | At most one of `--dry-run`, `--rollback`, `--cleanup` |

`init` creates only a new config, exclusively; its parent must already exist.
It never queries Salesforce or replaces a config. `build` is initial-only and
requires an absent or completely empty destination. Any entry, including
`.obsidian` or old control files, refuses; repeating build returns conflict 3.
Use `sync` for an evidence-bearing managed vault. Sync does not initialize,
adopt, migrate or repair missing/corrupt state. `recover` uses only validated
local evidence, without acquiring source data; its default is read-only preview.

A relative `--config` is relative to cwd. Paths inside the config and `init`
source/vault arguments are relative to the config parent. Absolute paths work
from another directory. Quote every path containing spaces. Native unrooted
Windows relative paths work with backslashes or forward slashes; drive-relative
`C:config.toml` and current-drive-rooted `\config.toml` or `/config.toml` are
ambiguous and refused. On POSIX, Windows backslash/drive syntax is refused.
No tilde or environment-variable expansion is performed inside configuration.

Offline example, after copying the fictional project as in the quickstart:

```sh
obforce init --config "../Fictional Workspace/Config with spaces.toml" --source "./Fictional Project" --vault "./Knowledge" --workspace-id fictional
obforce build --config "../Fictional Workspace/Config with spaces.toml" --dry-run
obforce build --config "../Fictional Workspace/Config with spaces.toml"
python -m obforce sync --config "../Fictional Workspace/Config with spaces.toml" --dry-run
python -m obforce sync --config "../Fictional Workspace/Config with spaces.toml"
obforce recover --config "../Fictional Workspace/Config with spaces.toml"
```

Previews perform full applicable validation but create no Obforce config, vault,
state, lock, journal, cache, log or staging artifacts. No-op preserves managed
bytes and modification times; reads may change access times. Ordinary Python
bytecode caching can be disabled separately with `PYTHONDONTWRITEBYTECODE=1`.
Live previews can perform authorized reads and sf can alter its own local state.

| Exit | Meaning |
| --- | --- |
| 0 | Complete selected operation or valid no-op |
| 1 | Operational/read/process failure |
| 2 | Invalid usage, config or input |
| 3 | Conflict, identity/ownership refusal or recovery required |
| 4 | Completed operation with requested incomplete/unavailable coverage |

Combined outcome precedence is **3, 2, 1, 4, 0**, not numeric order. Offline audit
and relationships are unrequested by design and do not alone force 4. A no-op can
still return 4 for requested incomplete coverage. A failed acquisition does not
publish a partial result as success.

Reports provide bounded counts, independent coverage and recovery guidance, with
no raw metadata, private names/paths, audit identities or warning text. File
totals include config for init; changed notes, dashboard and state for ordinary
publication; journaled files for recovery. No verbose or machine report option
is implemented. See [live selection](LIVE_SETUP.md), [refresh](REFRESH.md) and
[recovery](RECOVERY.md) before selecting live or recovery options.
