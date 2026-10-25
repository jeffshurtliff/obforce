# Fictional offline first build

This journey uses the repository's fictional Apex sample and no Salesforce CLI,
authentication, network, Obsidian process or plugins. Public Thread 12 commands
are accepted and complete, including maintainer confirmation of character
readability and four-space generated nesting. See the
[acceptance record](../dev/IMPLEMENTATION_PLAN.md#thread-12-acceptance-and-closure--23-october-2026).
Thread 13 adds [refresh](REFRESH.md) for evidence-bearing managed vaults.
Use an installed development package (`poetry install --with dev` from the checkout)
and Python 3.12+. Package/dependency installation is separate from offline runtime.

Choose a **new absolute workspace outside this repository**, any source checkout,
existing vault, template root or application installation. Substitute the two
absolute paths below. The selected workspace parent must already exist; this
setup refuses to replace an existing workspace. Python's `shutil` copies only
the supplied fictional sample, never real metadata.

```sh
python -c "import shutil,sys; from pathlib import Path; root=Path(sys.argv[1]); root.mkdir(); shutil.copytree(Path(sys.argv[2])/'examples/sample_sfdx', root/'Fictional Project')" "/absolute/path/Fictional Workspace" "/absolute/path/obforce-checkout"

obforce init --config "/absolute/path/Fictional Workspace/obforce.toml" --source "./Fictional Project" --vault "./Knowledge" --workspace-id fictional --dry-run
obforce init --config "/absolute/path/Fictional Workspace/obforce.toml" --source "./Fictional Project" --vault "./Knowledge" --workspace-id fictional
obforce build --config "/absolute/path/Fictional Workspace/obforce.toml" --dry-run
obforce build --config "/absolute/path/Fictional Workspace/obforce.toml"
```

`python -m obforce` accepts the same options as `obforce`; both are noninteractive.
The absolute config path works from any directory. Source/vault paths inside it
resolve from its parent. Preview commands create no config, vault, state, lock,
journal, log, cache or staging artifacts. Init creates only a new config, with
an existing parent. Ordinary Python bytecode caching can be disabled separately
with `PYTHONDONTWRITEBYTECODE=1`; reads may affect filesystem access times.

The final command creates two readable ApexClass notes under
`Knowledge/Custom Code/Apex Classes`, plus `.obforce/state.json` and the persistent
writer lock. It reports local inventory complete, audit unavailable/unrequested,
and relationships not collected/unrequested, with exit 0. No Salesforce audit
dates, authoritative dependency edges or technical-debt assessment are invented.
You can open the notes yourself; Obforce does not launch or configure Obsidian.
User prose/properties, including every `technical_debt*` field, belong to you.

After adding human context or moving a note uniquely within the vault, preview
and refresh through the same explicit config:

```sh
obforce sync --config "/absolute/path/Fictional Workspace/obforce.toml" --dry-run
obforce sync --config "/absolute/path/Fictional Workspace/obforce.toml"
```

With unchanged source/graph/templates, these operations preserve exact note and
state bytes/mtimes, including human-only edits. New builds save private normalized
refresh evidence inside `.obforce/state.json`; legacy vaults without it refuse
refresh rather than guessing old facts. No source/Obsidian settings are changed.


Build is **initial-only**. Repeating it returns conflict 3 without altering the
vault. Any existing destination entry, including unrelated notes, `.obsidian` or
managed history, refuses. Do not delete control files to bypass this check.
Use a new explicitly selected destination for another fictional first build;
Use `sync` to refresh this newly created managed vault.

Recovery needs only the explicit config and local evidence:

```sh
obforce recover --config "/absolute/path/Fictional Workspace/obforce.toml"
# Select only the operation matching the validated journal phase:
obforce recover --config "/absolute/path/Fictional Workspace/obforce.toml" --rollback
obforce recover --config "/absolute/path/Fictional Workspace/obforce.toml" --cleanup
```

The default is validated read-only preview. `--dry-run` is equivalent.
Rollback refuses committed evidence; cleanup refuses precommit evidence. Without
pending evidence, recovery is a write-free no-op. An edit or incomplete/unsafe
journal refuses and preserves evidence for manual resolution. Setup interrupted
before a journal can leave directories whose ownership cannot be reconstructed;
no automatic recursive removal or build retry adopts them. A successful rollback
retains the control/lock, so it does not turn the old destination into a new build.


## Exit codes

| Exit Code | Description                                            |
|-----------|--------------------------------------------------------|
| 0         | complete selected operation/no-op                      |
| 1         | operational failure                                    |
| 2         | invalid usage/config/input                             |
| 3         | conflict/recovery required                             |
| 4         | completed operation with requested incomplete coverage |

Requested partial inventory can produce a bounded
partial first build with 4; it does not prove missing components. Precedence is
3, 2, 1, 4, 0. See [configuration](CONFIGURATION.md#public-initialization-and-initial-build-thread-12)
and [setup/recovery limits](SYNC_SAFETY.md#public-initial-setup-and-recovery-thread-12).


## Additional Information

Windows sf execution, native ACL/durability, power-loss and hostile-race guarantees
are not established by this offline example or hosted synthetic tests.
