# Manual Test Findings

This document tracks findings discovered during manual testing of the Obforce functionality.
It serves as a rough punch list of items to be addressed either as part of the current 
implementation scope or in a fast-follow or future release.

---

## Findings

The findings are outlined in the sections below.

- MTF-1 - HTML character references displayed literally in generated notes
- MTF-2 - Adjustments to the Apex Classes dashboard

---

### MTF-1 - HTML character references displayed literally in generated notes

- **Internal Tracking ID**: MTF-1
- **Title**: HTML character references displayed literally in generated notes
- **Categories**: Note Rendering; Templates; User Experience
- **Proposed Release**: v0.1.0
- **Status**: Resolved and accepted — #20 closed as completed on 23 October 2026
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


#### Delivery and manual confirmation — 23 October 2026

The maintainer reviewed/pushed the correction and repeated the fictional
quickstart, confirming that MTF-1 is addressed. Merge 8285aca / run 39868649758
attempt 1 passed all 12 Linux/macOS/Windows Python 3.12–3.15 cells and required
artifact gates; exact job/step/command logs were verified. The preceding local
and pending-CI statements remain as historical evidence. No issue closure is
implied. A separate small nested-list spacing correction is being handled
directly in #12: use four spaces per engine-generated nested bullet level.
See [the indentation contract](../docs/RENDERING.md#four-space-generated-list-indentation--thread-12).
Human-authored spacing remains untouched; native Obsidian acceptance of that
new spacing is pending. Thread 13 onward and enhancement #18 remain NOT STARTED.


#### Accepted and closed — 23 October 2026

The maintainer confirmed the character-readability and four-space nesting fixes
and authorized completion/closure. #20 and parent Thread 12/#12 are completed.
Final delivered correction f833505ee0e17c0f048abe3786918c324962fa36 passed all 12
Linux/macOS/Windows Python 3.12–3.15 cells in run 39985255497 attempt 1: Linux
1375 passed each; macOS 1373/2 skipped each; Windows 1359/16 skipped each. Every
required check and all 24 independent installs passed. Manual Obsidian acceptance
is maintainer-reported; no automated UI or exhaustive platform/view test is claimed.

The preceding pending/local statements remain historical. Earlier local
safety-refusal failures keep their original outcomes and unconfirmed cause;
passing hosted CI does not erase them. See the
[Thread 12 acceptance record](IMPLEMENTATION_PLAN.md#thread-12-acceptance-and-closure--23-october-2026).
No remaining work for this finding in Thread 12. Thread 13 onward and enhancement
#18 remain NOT STARTED.

---

### MTF-2 - Adjustments to the Apex Classes dashboard

- **Internal Tracking ID**: MTF-2
- **Title**: Adjustments to the Apex Classes dashboard
- **Categories**: Dashboards; Properties
- **Proposed Release**: v0.1.0
- **Status**: Addressed and accepted with Thread 14; #14 closed on 27 October 2026; optional native preview unavailable
- **Impact**: User experience and overall usability
- **GitHub Issue**: [#14](https://github.com/jeffshurtliff/obforce/issues/14)
- **Related Threads**: Thread 14

#### Details

After viewing the `Dashboards/Apex Classes.base` dashboard created as part of Thread 14, 
the adjustments below have been identified and should be addressed within the thread.

- The **Note** column (currently a formula defined as `file.asLink()` which displays the full 
  file path as a link) should be merged with the **Class** column and should display only the 
  class name (e.g. `DemoExtension`) as a link to the note.
- Change the column name **Metadata status** to be **Metadata Status**.
- Change the column name **Salesforce created** to be **Created**. (see below)
- Change the column name **Salesforce modified** to be **Last Modified**. (see below)
- A column should be added for **API Version** and should display the version strings without
  them being wrapped in double quotes. (i.e. `67.0` and not `"67.0"`)
- Change the column name **Human debt assessment** to be **Technical Debt** represented as a 
  Boolean checkbox (see note below) rather than a formula.
- The **Human debt value** column should be removed.
- Change the **Debt severity** column name to be **Debt Severity**. (see note below) 
- Change the column name **Debt status** to be **Debt Status**. (see note below)
- Change the column name **Debt review date** to be **Last Reviewed**. (see note below)

**Items with scope beyond dashboards:**

- It is unclear what the **Lifecycle** property/column represents, and if it does not serve a 
  useful purpose then it should be removed from the dashboard.
- The date properties `sf_created` and `sf_last_modified` should be added to the Apex Class
  notes and should be used as the sources for the **Created** and **Last Modified** columns.
- The `technical_debt` property needs to be more strictly defined as a Boolean value (i.e. a 
  checkbox that is deselected by default) rather than allowing it to also be a custom value. 
- A property should be added to the Apex Class notes named `tech_debt_severity` as a string
  (blank by default but the documentation should recommend populating with `High`, `Medium`, 
  or `Low`) and the **Debt Severity** column should use this property as its source.
- A property should be added to the Apex Class notes named `tech_debt_status` as a string
  (blank by default) and the **Debt Status** column should use this property as its source.
- A date property (using the `YYYY-MM-DD` format by default) should be added to the Apex Class 
  notes named `last_reviewed` (blank by default) and the **Last Reviewed** column should use
  this property as its source.

#### Thread 14 response — 26 October 2026

The candidate applies the requested class-name link, labels, API Version and
human property column names. Technical Debt uses the actual Boolean property;
new notes default unchecked. New `tech_debt_severity`/`tech_debt_status` fields
are blank strings (recommend High/Medium/Low severity); `last_reviewed` is blank,
with YYYY-MM-DD recommended on review. These are creation-only defaults: existing
human properties and every `technical_debt*` value are preserved without rename,
backfill or conversion. The maintainer explicitly authorized false throughout
fictional/example/test defaults, without historical unassessed data; the candidate
uses one table and no legacy view. Human Boolean decisions remain protected.

Lifecycle is removed from the table but retained as `sf_lifecycle` in notes/state:
active/missing implements the accepted comparable live-scan absence/reactivation
workflow and is separate from Salesforce Metadata Status. The new reserved
`sf_created`/`sf_last_modified` fields project available valid audit timestamps to
UTC dates, retaining original `sf_*_at` facts. Offline/unavailable dates remain
absent. Renderer fingerprint advances to 4; exact older baselines still gate
generated-only updates. A clean saved dashboard updates through the existing
transaction/recovery protocol; edits still block the whole batch.

Official syntax/function/property documentation was read; no application or real
vault/settings access was performed. The initial maintainer observation above
is native evidence for the earlier candidate. Automated validation of this
correction is separate and cannot confirm native checkbox/date typing or visual
rendering. At that local checkpoint this finding and #14 remained pending
maintainer confirmation; the acceptance below supersedes that status. See
[the contract](THREAD_14_DASHBOARD_CONTRACT.md#explicit-maintainer-mtf-2-correction) and
[the Thread 14 roadmap](IMPLEMENTATION_PLAN.md#thread-14-mtf-2-review--26-october-2026)
for current verification and retained historical failures.

Final clarified candidate: **1537 passed / 2 existing case/normalization fixture
skips**, 108.71s, against the independently installed wheel and external synthetic
inputs. Strict metadata/lock, Ruff lint/format, Bandit, whitespace, fresh build,
strict Twine, exact 36-wheel/35-sdist archives and both independent guarded
installs passed. Runtime network/process denial and no cwd artifacts were checked
separately from setup downloads. Earlier failures and changing-ancestor observations
remain in the roadmap; this pass does not establish their uncaptured causes.
No hosted Thread 14 or native Obsidian correction result is claimed.

#### Thread 14 acceptance — 27 October 2026

The maintainer requested closure if complete after corrected CI. Verified final
Windows path correction `6d086961f07c5d36fcd8e295871b64f9f528f238` / merge
`cdf0e68eb5aa29184c2ecf51cb99c92e9c19e22f` and every required command in
[run 40517073513, attempt 1](https://github.com/jeffshurtliff/obforce/actions/runs/40517073513).
All 12 Linux/macOS/Windows Python 3.12–3.15 cells and 24 independent installs
passed: Linux 1555 passed each; macOS 1553/2 each; Windows 1539/16 each.
MTF-2's code/table/property corrections and explicit false defaults are accepted
with Thread 14; #14 is closed. Native Obsidian preview was optional in the
Thread 14 contract and was not performed by the agent. This is implementation/
automated acceptance, not a claim of native rendering or property-type validation.
Failed 40427329142 and all older evidence remain in the
[acceptance record](IMPLEMENTATION_PLAN.md#thread-14-acceptance-and-closure--27-october-2026).
