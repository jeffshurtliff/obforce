# Installation

The current candidate is `0.1.0.dev0`, not a released PyPI version. Use Python
3.12 or newer and a maintainer-reviewed local wheel or source archive. This
version covers Apex classes; additional metadata and configuration areas are
planned for future releases toward Obforce's goal of documenting an entire org.
Do not assume `pip install obforce` selects this candidate. Get the fictional examples
from the matching reviewed repository checkout; examples and developer harnesses
are deliberately excluded from distribution archives.

Create a dedicated environment outside the application checkout, source project,
template root and future vault. The parent must be a trusted, stable local
location. In the commands below, replace absolute placeholder paths with your
chosen paths; quote spaces. The environment and destination must remain disjoint.

POSIX shell:

```sh
python3.12 -m venv "/absolute/Obforce Tools/venv"
"/absolute/Obforce Tools/venv/bin/python" -m pip install "/absolute/Downloads/obforce-0.1.0.dev0-py3-none-any.whl"
"/absolute/Obforce Tools/venv/bin/python" -m pip check
. "/absolute/Obforce Tools/venv/bin/activate"
obforce --help
python -m obforce --version
```

PowerShell (offline application use):

```powershell
py -3.12 -m venv "C:\Obforce Tools\venv"
& "C:\Obforce Tools\venv\Scripts\python.exe" -m pip install "C:\Downloads\obforce-0.1.0.dev0-py3-none-any.whl"
& "C:\Obforce Tools\venv\Scripts\python.exe" -m pip check
& "C:\Obforce Tools\venv\Scripts\obforce.exe" --help
& "C:\Obforce Tools\venv\Scripts\python.exe" -m obforce --version
```

Use these absolute executables in later examples if your environment is not
activated. No activation or system execution-policy change is required. To use
a source archive instead, replace only the wheel filename with
`obforce-0.1.0.dev0.tar.gz`. Pip may download runtime and isolated build
dependencies. Installing does not authorize Salesforce access.

For contributors, [Poetry setup and checks](../CONTRIBUTING.md) use the locked
environment. For users, continue with the [offline quickstart](QUICKSTART.md).
Help/version and offline generation need no Salesforce CLI or Obsidian. Manage
sf installation and authorization separately before considering [live setup](LIVE_SETUP.md).

Ordinary local filesystem tests have passed on hosted Linux, macOS and Windows
with Python 3.12–3.15. See [qualification](QUALIFICATION.md) for exact results,
skips and observed filesystems; this does not qualify arbitrary network,
cloud-synced or removable storage. Native Obsidian dashboard preview remains
unavailable. Windows sf execution remains refused.
