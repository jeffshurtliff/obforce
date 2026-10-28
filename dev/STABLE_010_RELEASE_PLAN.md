# Usable stable 0.1.0 release plan

**Approved direction:** 28 October 2026. **Current package:** `0.1.0.dev0`.
**Status:** Documentation/tracking revision only; R1–R8 are **NOT STARTED**.
This document supplements the [implementation roadmap](IMPLEMENTATION_PLAN.md)
and supersedes its earlier synthetic-only or optional-live/native release gates.
It describes required future behavior, not new capabilities delivered by this revision.

## Release contract and current gaps

The first stable release must be useful with actual Salesforce DX projects and
direct live-org input, scoped to ApexClass notes. Completed Threads 01–15 remain
accepted foundation work; their historical acceptance is not revised or erased.
Thread 16/#16 remains under review against its original current-capability scope.
Its acceptance alone cannot establish the revised product's release readiness.

| Area | Current implementation/evidence | Required before stable 0.1.0 |
| --- | --- | --- |
| DX input | General DX reader and installed build/sync; fictional automated corpus | Successful actual-project workflow and findings that inform design |
| Salesforce CLI | POSIX process boundary and live adapters, synthetic/mock verification | Actual sf installation compatibility and authorized nonproduction trials on macOS/Linux |
| Human ownership | Generated-only patches, UUIDs/moves, conflicts, recovery and no-op checks | Preserve these protections in realistic and scale acceptance |
| Project absence | Offline sync preserves prior lifecycle and facts | Managed project-presence property, generated warning, dashboard visibility and reappearance |
| Configuration | Arbitrary explicit external config; vault-contained config refused | `<vault>/.obforce/obforce.toml` with guarded initialization/build/sync/recovery |
| Capacity | 128 changed-file ceiling; 1,000-class refusal tests; independent state limits | Successful 1,000-class installed lifecycle including substantial refresh and recovery |
| Obsidian | Automated Base validation; optional native preview; lifecycle hidden in default table | Mandatory native note/Base/property review, including absence presentation |

A complete comparable DX scan can establish that a class is not found in that
project. It cannot establish deletion from Salesforce. Project presence, live
accessible-scope lifecycle, and Salesforce metadata status must remain distinct.
Current code still enforces the earlier live-only missing gate until R5 implements
the separately reviewed project-presence contract.

Stable `0.1.0` promotion and publication are blocked until the revised product
acceptance, final documentation and candidate checks pass. `0.1.0a1` is optional,
requires separate preparation/publication approval, and cannot waive preservation
defects. Completing the old thread list never automatically promotes a stable version.

Windows requires the DX workflow for 0.1.0. Native Windows sf remains deferred in
[#18](https://github.com/jeffshurtliff/obforce/issues/18). Live support requires real
macOS and Linux evidence. Metadata facts plus human context remain the content
scope; Apex source analysis, automatic retrieval, hybrid enrichment and automatic
cross-source reconciliation remain deferred. DX and live vaults remain separate.

## Work packages and dependencies

All new issues use the existing maintainer templates, `maintainer`/`codex` plus
category labels, assignment to `jeffshurtliff`, and the existing
[v0.1.0 milestone](https://github.com/jeffshurtliff/obforce/milestone/1).
R1 and R3 also use `question` for maintainer requirements/design decisions.

| ID / issue | Work | Direct prerequisites | Acceptance result |
| --- | --- | --- | --- |
| R1 / [#23](https://github.com/jeffshurtliff/obforce/issues/23) | Stable-release requirements and maintainer inputs | Approved roadmap | Maintainer accepts the contract and supplies/resolves required inputs |
| R2 / [#24](https://github.com/jeffshurtliff/obforce/issues/24) | Real DX and nonproduction-org discovery | R1 plus target/operation authorization | Private actual-input findings and public-safe gaps inform design |
| R3 / [#25](https://github.com/jeffshurtliff/obforce/issues/25) | Product design package and maintainer approval | R2 | Concrete examples/contracts and every blocking decision approved |
| R4 / [#26](https://github.com/jeffshurtliff/obforce/issues/26) | Vault-owned configuration and initialization | R3 | Approved config/init/build/sync/recovery journey works safely |
| R5 / [#27](https://github.com/jeffshurtliff/obforce/issues/27) | DX project presence and retained-note lifecycle | R4 | Removed/restored project classes update presence without human-data or UUID loss |
| R6 / [#28](https://github.com/jeffshurtliff/obforce/issues/28) | Successful 1,000-class lifecycle | R5 | Installed build, substantial refresh, no-op and recovery publish successfully |
| R7 / [#29](https://github.com/jeffshurtliff/obforce/issues/29) | Real Salesforce CLI compatibility and live workflow | R6 | Actual authorized live workflow on macOS/Linux with honest coverage |
| R8 / [#30](https://github.com/jeffshurtliff/obforce/issues/30) | Integrated product acceptance | R4, R5, R6, R7 | Maintainer accepts real/native/scale/artifact evidence and final support matrix |
| 16b / [#22](https://github.com/jeffshurtliff/obforce/issues/22) | Final documentation site and reviewed cleanup | #16 and R8 | Final accepted behavior documented; required reproducible evidence retained |
| 17 / [#17](https://github.com/jeffshurtliff/obforce/issues/17) | Stable candidate preparation | #16, #22 and R8 | Exact candidate and publication handoff ready for separate approval |

Native GitHub blocked-by/blocking links mirror these direct edges, including the
four explicit R8 prerequisites. Preserve historical #15 → #16 → #17 and
#16 → #22 → #17 relationships. Execution defaults to sequential; task completion
does not authorize the next package. Issue creation does not start a task.

#16 can finish review of existing behavior independently. #22 retains the approved
Sphinx/ReadTheDocs styling/reference-project and reviewed-retention scope, but its
final acceptance follows R8 and includes the revised behavior. #17 stays unstarted.
[#19](https://github.com/jeffshurtliff/obforce/issues/19) remains optional verbose
output; required actionable default messages belong in the product packages.
[#21](https://github.com/jeffshurtliff/obforce/issues/21) remains the existing optional
optimization follow-up; relevant findings may support R6 but do not satisfy its
successful-publication gate. No closed thread is reopened by this revision.

## Maintainer inputs and design approval

R1 records confirmed direction and obtains the following inputs before dependent
work. Private paths, target identities, permissions and raw findings belong in an
approved private record, not GitHub issue bodies. A missing answer stays explicit;
neither elapsed time nor a configured alias supplies permission.

| Input/decision | What the maintainer supplies or approves | Gate |
| --- | --- | --- |
| Actual DX project | Nominated project, manifest/Apex-metadata inspection permission, disposable output/copy location | R1 → R2 |
| Live assessment | Named nonproduction target, allowed read operations, approved executable/runtime and audit-name choice | R1 → live R2/R7/R8 |
| Environments | Available macOS/Linux/Windows hosts and Obsidian environment; missing required platforms stay blockers | R1; qualification in R7/R8 |
| Evidence handling | Private evidence location; explicit review of any sanitized public examples | R1 onward |
| Product design | Exact commands, config/path rules, properties/sections/tree, absence semantics, templates and dashboard customization | R3 → R4 onward |
| Compatibility/capacity | Current development-vault/config treatment, any versioned changes, finite capacity budgets | R3 → R4/R6 |

An already available DX project can be assessed without enabling Salesforce
access. R2 performs only authorized inspection and trials of the existing
installed application against disposable output. Source remains read-only;
class removal/restoration tests use a disposable copy. Small real corpora can
establish realistic behavior, supplemented by generated scale fixtures. Record
actual refusals as findings rather than weakening guards to produce a demo.

R3 must produce a decision-complete package, not an approval of abstract goals:

- **CLI/config:** Exact vault/control/template tree and TOML schema, commands from
  arbitrary cwd, path resolution, guarded creation of `.obforce/obforce.toml`,
  recognized initialized-empty build state, non-overwriting init and artifact-free
  previews. Source/vault separation and Salesforce-independent recovery remain.
- **Compatibility:** Explicit treatment of current external configs and development
  vaults, preserving human content/UUIDs and recovery evidence. No silent relocation,
  reconstruction/adoption, identity replacement or destructive fallback. Any needed
  controlled compatibility work requires an approved design before code.
- **Presence:** Review `obf_found_in_project` as a proposed Boolean name; it is
  currently user-owned, not newly reserved by this document. Define collision and
  ownership/version behavior before adding it. Persist enough source/package/
  selection evidence for comparability; today's scope hashes omit package paths.
- **Absence/reappearance:** False requires a successful complete comparable project
  scan. Missing packages, incomplete pairs, failed reads, changed selection and
  ambiguous binding cannot establish absence. Preserve note/UUID/known facts and
  human content; the warning stays inside the generated region. Reappearance
  restores presence and removes that warning in the existing note. Live-only notes
  cannot imply an unperformed project observation.
- **Presentation:** Complete present/absent/reappeared/partial/live examples with
  exact names/types/values, section names, markers, directories and template rules.
  Project absence is visible in the default Base. Review whole-file Base ownership
  and normal UI customization explicitly. Offline unavailable audits/dependencies
  remain truthful; source-code-only edits need not change metadata notes.
- **Capacity:** Approved finite budgets/representations for 1,000-class acquisition,
  planning, state/evidence, journals, staging, publication and recovery. A fresh
  1,000-note build currently needs 1,002 changed files before other limits. Preserve
  full-batch preflight and recoverable publication; no truncation, evidence eviction
  or silent splitting into independently committed batches to evade a limit.
- **Actual sf:** Supported executable/Node/plugin layouts and restricted child
  environment validated against R2 findings; explicit identity, queries, bounds,
  cleanup and privacy remain. Current contracts/limits must be rechecked when used.

Every unresolved material decision needs an owner, required input, affected work
and explicit acceptance. R4 onward stays blocked until R3 has maintainer approval;
routine internal choices may then follow the approved contract.

## Required release acceptance

Deterministic fictional fixtures and mocked CI remain the normal automated tests.
Add separately authorized real-input and native-app evidence; mocks do not replace it.

| Scenario | Required evidence |
| --- | --- |
| Actual DX build | Independently installed CLI creates notes/Base from an existing project into a new destination; source snapshots unchanged |
| Human refresh/moves | Custom properties, supported YAML/comments, prose/debt, moved-note UUIDs and affected links survive generated updates |
| Project absence/reappearance | Removing/restoring a pair in a disposable copy changes flag/warning/Base with retained facts, exact human content and the same UUID |
| Complete versus partial scope | Complete-empty comparable scan is tested separately from missing package, incomplete pair, unreadable input, selection drift and ambiguous source |
| Successful scale | Build 1,000 classes, refresh all affected notes, repeat no-op, interrupt publication and exercise rollback/committed cleanup at that scale |
| Actual live | Explicit authorized nonproduction target and actual sf on macOS/Linux; verified identity, audit availability/omission, useful notes and truthful relationship coverage |
| Native Obsidian | Reading and Live Preview, links/callouts, Base display, checkbox/date types and behavior after normal dashboard use |
| Preservation/refusal | Generated edits, unsafe paths, concurrent changes and interruptions refuse/recover without overwriting intervening human edits |
| Installed release candidate | Fresh wheel/sdist console/module journeys, relevant exact-commit CI, docs/privacy/resource checks and candidate hashes |

Require actual DX workflow evidence on claimed macOS/Linux/Windows environments,
and actual live evidence on macOS/Linux. Retain the selected Python matrix and
its honest limits; do not infer native/live qualification for each interpreter
from another evidence class. Record which combinations actually ran. Windows
live remains refused, without weakening that gate to make the matrix appear complete.

For each result, record application revision, artifact hashes, CLI/runtime/plugin
versions where relevant, host/environment, exact operation, outcome, source/human
preservation and remaining limitations. Raw metadata/vault/state/recovery evidence
stays private. Missing mandatory real/native/scale results block stable release.
Historical green CI and safe-refusal benchmarks retain their original meanings.

Org mutations needed to demonstrate live missing/reappearance must be prepared by
the maintainer or separately authorized. Read-only trials do not authorize login,
deploy/delete, Apex execution, CLI/plugin installation/update, platform provisioning
or changes to real vault/settings. Obsidian review does not authorize changing
settings/plugins or overwriting a user's existing knowledge vault.

R8 acceptance feeds final docs into #22; #17 verifies the complete gate/evidence
set against the actual candidate before preparing stable metadata. Git delivery,
tagging, release creation, index uploads, hosting and automation remain separately
authorized steps. This roadmap revision performs none of them.

## Next work and review state

The approved current task implements documentation/tracking only. The existing
Thread 16 unstaged work and complete historical evidence are preserved. No runtime,
tests, package/dependency/lock/schema or resource behavior changes are authorized
here. R1/#23 is next eligible, **NOT STARTED**; nomination/authorization and later
design approval remain maintainer actions. R2–R8, #22 and #17 are **NOT STARTED**.
