# Customize notes safely

After [the quickstart](QUICKSTART.md), add business context below the end marker
and ordinary properties such as tags, aliases and review decisions. Every
nonreserved property remains yours after creation. Never edit identity/schema,
`sf_*` fields, markers or the generated body to customize output: those changes
are protected conflicts, even when metadata has not changed.

## Technical-debt conventions

| Human property | Creation default | Suggested use |
| --- | --- | --- |
| `technical_debt` | Boolean `false` | Set true after a human assessment; false is an unchecked default, not proof of no debt |
| `tech_debt_severity` | Empty string | `High`, `Medium` or `Low` |
| `tech_debt_status` | Empty string | Your team's status vocabulary |
| `last_reviewed` | Null/blank | `YYYY-MM-DD` after review |

Metadata never sets severity, review status or dates. Defaults apply only when
creating a note. Existing absent/null/custom human values, older field names and
all `technical_debt*` properties stay untouched; no rename, coercion or backfill
occurs. `tags`, `aliases`, `type` and business properties are human-owned too.

## Explicit template overrides

The public CLI uses the packaged defaults unless config explicitly selects a
root. Only two known files are read, with per-file fallback when absent:

- `apex_generated.md.j2`: presentation of the generated sections;
- `apex_created.md.j2`: initial human body, used only for new notes.

Create `Templates` beside the tutorial config with Python:

```sh
python -c "import sys; from pathlib import Path; p=Path(sys.argv[1])/'Templates'; p.mkdir(); (p/'apex_generated.md.j2').write_text('{{ metadata | section }}\n\n{{ references | section }}\n\n{{ referenced_by | section }}\n\n{{ coverage | section }}\n', encoding='utf-8', newline='\n'); (p/'apex_created.md.j2').write_text('## Business Context\n\nFictional team context.\n\n## Known Issues / Technical Debt\n\nReview manually.\n\n## Additional Information\n', encoding='utf-8', newline='\n')" "/absolute/path/Fictional Workspace"
```

Append this table **once** to `Config with spaces.toml` (or add it in an editor):

```toml
[templates]
directory = "./Templates"
```

Then preview and apply:

```sh
obforce sync --config "/absolute/path/Fictional Workspace/Config with spaces.toml" --dry-run
obforce sync --config "/absolute/path/Fictional Workspace/Config with spaces.toml"
obforce sync --config "/absolute/path/Fictional Workspace/Config with spaces.toml"
```

The generated sections are reordered, human text remains, and the last sync is a
byte/mtime-stable no-op. The creation text does not replace existing human sections.
To see that text on new notes, select the same template root in a separate config
and build a separate empty destination; do not rebuild or recreate existing notes.
The CLI exposes no arbitrary creation-property injection option.

Use UTF-8 and **LF**, including on Windows. Each template is at most 16 KiB.
Generated templates must contain each of the four shown slots exactly once;
retain the required engine headings. Creation templates are literal Markdown
with Business Context, Known Issues / Technical Debt and Additional Information
headings exactly once. No frontmatter or managed markers belong in templates.
No loops, calls, imports/includes, conditionals, object access or other filters
are accepted. Existing invalid overrides refuse; they never silently fall back.
A creation-only invalid file is not needed when there are no new notes.

The loader does not discover other files or templates from metadata. Keep the
selected tree trusted and stable; no links, special or multiply linked files.
The [rendering contract](RENDERING.md) explains input/AST/section/candidate limits.
A sandbox alone does not guarantee resource isolation. Changing a generated
template never permits overwriting an edited generated baseline.

## Dashboard customization

Keep the tracked `Dashboards/Apex Classes.base` unchanged, including UI column or
layout edits. Its exact bytes are owned. Author a separate Base at another path
without the reserved `obforce:dashboard` comment for your own view. Do not move or
delete the generated Base. [Dashboard conflicts](DASHBOARDS.md) block the entire
batch, just like generated note edits. Markdown remains useful without Bases or
community plugins; Obforce changes no `.obsidian` settings.
