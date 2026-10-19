# Obforce
Create and maintain living documentation for your Salesforce org within an Obsidian vault

Under development: the `0.1.0.dev0` foundation provides help and installed-version
reporting. Salesforce inputs, note generation, and safe refresh are planned in
the [implementation roadmap](dev/IMPLEMENTATION_PLAN.md).

For development, use Python 3.12+ and Poetry 2.4+ within Poetry 2.x:

```sh
poetry install --with dev
poetry run obforce --help
poetry run obforce --version
poetry run python -m obforce --help
poetry run python -m obforce --version
```

Help/version need no Salesforce CLI, authentication, or running Obsidian.
See [CONTRIBUTING.md](CONTRIBUTING.md) for checks and fresh artifact validation,
[AGENTS.md](AGENTS.md) for agent rules, and [SECURITY.md](SECURITY.md) for private
reporting. The existing [Apache 2.0 license](LICENSE) applies. Platform targets
and configured CI are distinct from verified support; actual evidence is recorded
in the roadmap handoff.
