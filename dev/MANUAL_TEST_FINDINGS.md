# Manual Test Findings

This document tracks findings discovered during manual testing of the Obforce functionality.
It serves as a rough punch list of items to be addressed either as part of the current 
implementation scope or in a fast-follow or future release.

---

## Findings

The findings are outlined in the sections below.

### MTF-1 - HTML character references displayed literally in generated notes

- **Internal Tracking ID**: MTF-1
- **Title**: HTML character references displayed literally in generated notes
- **Categories**: Note Rendering; Templates; User Experience
- **Proposed Release**: v0.1.0
- **Status**: Implemented locally in Thread 12 — pending corrected CI and maintainer UI acceptance
- **Impact**: Generated-note readability in Live Preview
- **GitHub Issue**: [#20](https://github.com/jeffshurtliff/obforce/issues/20)
- **Related Threads**: Thread 07 renderer; corrected in Thread 12 acceptance work for v0.1.0

#### Details

HTML numeric character references are displayed within the Obsidian Markdown notes 
when viewing the notes in the *Live Preview* mode, causing readability issues when not 
viewing notes in *Reading* mode.

For example:

- Underscores are represented as `&#95;`
- Double quotes are represented as `&#34;`
- Hyphens are represented as `&#45;`

Below is Markdown output from the **Salesforce Metadata** section of a note for an Apex class.

````markdown
## Salesforce Metadata

- ApexClass: DemoService
- Namespace: none
- Source: local
- Source provenance: local&#45;apex&#45;xml&#45;v1
- api&#95;version: &#34;67&#46;0&#34;
- created&#95;at: unavailable (not collected or accessible)
- created&#95;by: unavailable (not collected or accessible)
- last&#95;modified&#95;at: unavailable (not collected or accessible)
- last&#95;modified&#95;by: unavailable (not collected or accessible)
- status: &#34;Active&#34;
````

As end-users will likely spend most of their time in the *Live Preview* mode, ordinary metadata labels 
and values should remain readable in Obsidian Live Preview and Reading view. The solution must preserve 
protection against unintended HTML, links, embeds, generated markers, and Markdown injection.

It is also worth noting that standard double quotes (`"`) should be used instead of curly double 
quotes so that anything copied/pasted will be formatted properly.


#### Triage and correction — 22 October 2026

Address now under #12/#20 before accepting the initial-build journey; readable
notes are current acceptance scope, rather than future dashboard/CLI polish.
Renderer version 2 keeps ordinary labels, provenance, straight quotes, numeric
versions and ISO audit timestamps readable in generated source. Dangerous markup
continues to be escaped; URL-like domains/schemes do not become automatic links.
See [the rendering contract](../docs/RENDERING.md#renderer-version-2-readability-correction--mtf-1--20).

The existing state wire and baseline checks are unchanged. Synthetic legacy-v1
fixtures verify compatible generated-region-only patches with exact human YAML/
prose/technical-debt preservation; edited generated content still refuses. No
existing vault is rewritten or adopted and public build still refuses repeats.
Live Preview and Reading acceptance requires maintainer UI review; no native
Obsidian UI result is claimed by the automated tests. #20 remains open pending
review and acceptance. Thread 13 and later remain NOT STARTED.

Local verification: 1369 passed/2 existing filesystem skips on macOS ARM64 /
Python 3.14.7; fresh wheel/sdist, strict Twine, exact archive checks and both
independent guarded installs passed. Thirty-three local CommonMark payloads
remained exact text without active injected markup. Corrected Windows CI and
actual Obsidian UI review remain unavailable; these results do not close #20.
