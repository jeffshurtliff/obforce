# Fictional offline quickstart

This tutorial creates two ApexClass notes from the supplied fictional DX sample.
It needs [an installed candidate](INSTALLATION.md), Python 3.12+ and the matching
repository examples. Application runtime needs no network, sf, authentication,
Obsidian process or plugins. All examples here are fictional.

## Prepare a separate workspace

Choose a new absolute workspace outside the repository, the installed application,
any existing vault and any real source project. Its parent must already exist.
Use stable trusted private local ancestry. Substitute your paths below. The setup
refuses an existing workspace and copies only `examples/sample_sfdx`.

```sh
python -c "import shutil,sys; from pathlib import Path; root=Path(sys.argv[1]); root.mkdir(); shutil.copytree(Path(sys.argv[2])/'examples/sample_sfdx', root/'Fictional Project')" "/absolute/path/Fictional Workspace" "/absolute/path/obforce-checkout"
```

Use quotes on Windows too. In PowerShell invoke the installed Python explicitly
as shown in [installation](INSTALLATION.md) if it is not on PATH. These Python
setup/edit commands work on both platforms with native absolute paths.

## Preview and build once

```sh
obforce init --config "/absolute/path/Fictional Workspace/Config with spaces.toml" --source "./Fictional Project" --vault "./Knowledge" --workspace-id fictional --dry-run
obforce init --config "/absolute/path/Fictional Workspace/Config with spaces.toml" --source "./Fictional Project" --vault "./Knowledge" --workspace-id fictional
obforce build --config "/absolute/path/Fictional Workspace/Config with spaces.toml" --dry-run
obforce build --config "/absolute/path/Fictional Workspace/Config with spaces.toml"
```

Init preview creates nothing; init creates just the new config. Build preview
creates no destination or control artifacts. Build creates:

- `Knowledge/Custom Code/Apex Classes/DemoService.md` and `DemoExtension.md`;
- `Knowledge/Dashboards/Apex Classes.base`, the protected packaged view;
- private `Knowledge/.obforce/state.json` and a persistent writer lock.

Expect exit 0: inventory complete for the declared local scope, audit unavailable
and unrequested, relationships not collected and unrequested. Salesforce audit
dates, dependency facts and debt assessments are not invented. Repeating build
refuses with **3** and changes nothing. An existing destination must be completely
empty, including hidden entries. Do not remove control files to bypass refusal.

Use `python -m obforce` interchangeably with `obforce`. From an empty sibling directory under the same
parent, this quoted relative config selects the same file:

```sh
python -m obforce sync --config "../Fictional Workspace/Config with spaces.toml" --dry-run
```

Relative config paths use cwd; source/vault paths inside the file use the config
parent. Native Windows unrooted relative paths with spaces work. Ambiguous drive
paths remain refused; see [CLI paths](CLI.md).

## Add your knowledge and move a note

Edit human sections below the generated end marker, or add properties such as
`aliases`. Preserve `obforce_*`, `sf_*` and everything between generated markers.
New `technical_debt` is Boolean false; severity/status are blank and review date
is null. Those defaults are creation-only: your later choices stay yours.
For a reproducible fictional edit and unique move:

```sh
python -c "import sys; from pathlib import Path; v=Path(sys.argv[1]); p=v/'Custom Code/Apex Classes/DemoService.md'; p.write_bytes(p.read_bytes()+b'\nHuman context: reviewed for the fictional tutorial.\n'); d=v/'Reviewed'; d.mkdir(); p.rename(d/'DemoService.md')" "/absolute/path/Fictional Workspace/Knowledge"
obforce sync --config "/absolute/path/Fictional Workspace/Config with spaces.toml" --dry-run
obforce sync --config "/absolute/path/Fictional Workspace/Config with spaces.toml"
```

The moved note retains its UUID and source identity. State records its new path;
relationship links to moved targets update where evidence exists. This offline
sample has no dependency edges. Human text survives. Copying a managed note instead
of moving it duplicates its ID and blocks the whole batch.

## Change fictional metadata, then check a no-op

Only for this copied fixture, change DemoService's API version from 67.0 to 68.0:

```sh
python -c "import sys; from pathlib import Path; p=Path(sys.argv[1])/'core/main/default/classes/DemoService.cls-meta.xml'; p.write_bytes(p.read_bytes().replace(b'67.0', b'68.0'))" "/absolute/path/Fictional Workspace/Fictional Project"
python -m obforce sync --config "/absolute/path/Fictional Workspace/Config with spaces.toml" --dry-run
python -m obforce sync --config "/absolute/path/Fictional Workspace/Config with spaces.toml"
python -m obforce sync --config "/absolute/path/Fictional Workspace/Config with spaces.toml"
```

Preview leaves bytes/mtimes unchanged. Sync updates clean generated facts while
preserving the UUID and human context. The final unchanged sync is a no-op,
preserving note, dashboard and state bytes/mtimes. Obforce does not modify source.
Removing a component from the local project does not mark its note missing;
[retained facts and coverage](REFRESH.md) prevent that inference.

Continue with [safe customization](CUSTOMIZATION.md) and [recovery](RECOVERY.md).
The latter includes a bounded synthetic interruption exercise. Open Markdown or
the generated Base yourself if desired; ordinary notes work without plugins.
Do not edit the tracked Base, including via UI layout controls: that is a protected
conflict. Use a separate custom view without its reserved ownership comment.
Native Obsidian preview remains unavailable in automated verification.
