# Phase 3 — Regression acceptance after release preparation

**Status: awaiting owner review (2026-10-03), auto=false.** The owner's
`process-phase 3` requests resumption of specification work. Implementation
waits for this revised gate. Historical delegated continuations are not reused.

## 1. Provenance

This is the current extension to [phase-3-spec.md](phase-3-spec.md), preserving
its historical specification and checkpoints. Governing inputs: public-launch
r1 §§0–10, approved r2 A1–A10, and
[the r3 amendment](public-launch-plan-r3-amendments.md), later wins.
R3 SHA-256: `ece90d1461a320730b524f80e72c0430082e0a1aa1cc46e90664855de6de6514`.
[Phase 4 preparation](../006-phase-4-preparation.md) is complete, SHA-256
`02f7d87ab1b6ff4584e2e00a173525d8dac798001b989ca0b1557cfbb1d48d9e`.
Read alongside prior records 003-phase-0, 004-phase-1 and 005-phase-2.
No panel has reviewed this extension; no implementation approval is claimed.

Observed source HEAD: `65b73ee9d687365dfabb15cc1412a4ee9b4a4111`.
Target: `<target-checkout>`, HEAD
`cf4c1d7736924fc83e28b7dd595f5cc58e532b22`, including preparation implementation
`5059dba88764cbf4be0e5a661a1fe9187a1657e8` and subsequent preparation records.
Both checkouts have extensive pending changes/deletions/untracked work. HEAD
alone does not identify the acceptance candidate. Review the pending diff and
commit only explicit selected paths before candidate freeze; preserve other work.

## 2. Obligations — current harvest

| Source | Binding obligation | Discharge |
|---|---|---|
| Thesis / §1 | Contributor can develop the generic framework without the source archive; launch, migration and retirement remain distinct | T1–T6; boundary |
| §0 R1–R12 | Preserve source and contracts, explicit content and authority, honest evidence, skills, focused verification, budgets and separate publication authority | §3; decisions |
| §2; r2 A3/A4 | Source owns migration amendments; target needs sufficient current plan/selection/records for development, with origins stated | L1, L4; no wholesale archive transfer |
| §3 | Preserve source history; reconcile actual affected source deltas and question triggers before any authority handoff | T7; D5 |
| §4 P3 deliverables | Authoring/validation, checking/transition, synth, extraction/rendering, generation/conformance, evolution/recovery, sessions/feedback, judgments/references, witnesses/replay, exports/review; inventory current commands | L1 family selection; T1/T2 |
| P3-C1 | Every advertised surface maps to current tests and necessary resources | Family record and resource/control mapping, T1/T2/T4 |
| P3-C2 | Fixture/harness collection has no undeclared source dependency | T1, T3, T5; target-only execution |
| P3-C3, amended by r3 | Keep unique current assertions; consolidate with named surviving protection; retire with concrete reason; coverage-review the earlier retained-private group | L1/T1; no per-definition completion denominator |
| P3-C4 | Both discovery roots install/doctor/uninstall in scratch roots | T3/T5 |
| P3-C5 | Examples/exports/review claims match execution; authority requires acceptance and source-delta reconciliation | T2–T7; D5 |
| P3 boundary (no Residual paragraph) | “retaining historical evidence does not recertify moved code; public CI does not silently expand to every historical or live lane.” | Repeated in record boundary |
| §5 skill surfaces | Packaged skills/references, installer-generated links, two real unmanaged twins, launcher, contributor docs, portable helpers/CI | Pin sites in L3; T3/T5 |
| §6 risks | Source drift, missing imports/resources, source-only fixtures/Git, unsafe credential intake, dual owners/publishers, copy defects, semantic rewrite, archive growth, overstated claims | §3; T1–T7 and boundary |
| §7 | No new semantic family, engine rewrite, broad historical repair, recertification or source deletion | §9 |
| §8; r2 A1 | Full harvest, explicit gate/budget, independent diff review, reproduced repairs, refactoring, record/commit | D1–D6; §10 |
| §9 P3, quoted | “Current coverage mapping, collection bootstrap, installed skills, workflows and optional dependency refusals.” | T1 mapping/bootstrap, T3/T5 skills, T2/T4 workflows/refusals |
| §10 PL-D8 | Current behavior versus historical evidence policy | D2, implementing owner r3 direction |
| r2 A2/A5/A7 + r3 | Final target-only contributor exercise; retained build-once wheel/sdist, separately checked sdist wheel; measured profiles | T4–T6; D3/D4 |
| r2 A6/A8/A9 | Scope-match external authorization; no live-review claim from offline tests; content review before target history | D4, L1, boundary |
| r2 A10 | P6/P7 are separate successor work, not launch gates | D5; §9 |
| P0/P1/P2 inheritance | Preserve original question IDs/states/owners/triggers; inspect affected origins/later rulings; source publisher and units remain owned until handoff | T7; D5 |
| P0 examples / P3 pending work | Keep useful generic import/refusal and generated BookRec/expense examples, review omitted useful regressions by coverage | L1/T2 |
| P4-preparation handoff | Preparation smokes are not final acceptance; temporary artifacts cannot be promoted; Ubuntu 3.11/macOS 3.13 are proposed profiles | T4–T6 |
| OQ-PUBLIC-LAUNCH-P2-BUILD-PROFILE | Pin uv 0.10.10 and measure proposed profiles before support claim | D3/T6 |
| OQ-V72-P1-ARTIFACT-COPIES | Inspect exported-byte/newline behavior before affected caller changes; retain v7.3 owner | T7; no automatic closure |
| OQ-V70-CLOSE-BROAD-REDS | Focused/current public acceptance does not close old broad-suite reds | Cadence and boundary |

## 3. Standing rules and risks

R1: leave source runtime/history and existing archives intact; use normal commits,
not new reconstruction machinery. R2: review selected test/fixture content and
licenses; r3 says this repository contains no private data, so a historical
retained-private label alone excludes nothing. Credentials/machine state still
do not belong in target history. R3: record ownership separately from test success.
R4: preserve assertions, exits, schemas and numerical bounds; a changed expected
answer needs an intended-behavior explanation and renewed decision if incompatible.
R5: keep every supported generic family. R6: use behavior-family decisions and
named surviving controls, not count completion. R7: current artifact hashes/results
remain distinct from historic assurance. R8: retain both roots and resource closure.
R9: focused repair gates, then expressly selected final target suite under D2.
R10: only D4's private push/CI scope; no publication. R11: concise selection/results;
source evidence size no longer drives work. R12: publishing authority unchanged.

Paid protocol rules, each bound here:

- **Totality belongs to the function:** retain hostile-input checks for loaders,
  report readers and any changed acceptance helper; no new general mapping reader.
- **An input cap bounds the document, not the algorithm:** preserve existing
  cap/scaling controls; add a bounded timing case only for newly introduced work.
- **Validation order is part of the design:** preserve product refusal order and
  cause assertions; explicitly retire the obsolete historical-accounting preflight
  from the current acceptance path, without pretending its old meaning passed.
- **One policy walk over all element kinds:** one reviewed family selection feeds
  local and CI selection; do not duplicate branch policies in the workflow.
- **Normative prose has exactly one home:** r3 owns accounting/preservation policy;
  this extension owns resumption decisions. Other documents link to those homes.
- **Resolve representation questions by measurement:** reproduce alleged failures;
  distinguish artifact equality, installed import origins and supported outcomes.

Review branch reachability, positive/refusal halves, discriminating fixtures,
repair neighbors, canonical identifiers and byte-copy callers. Do not credit
whole families from one smoke or a string-presence assertion. One reviewer is
one reviewer; no panel or proof claim follows from its reading.

## 4. Goal

The reviewed public contributor selection exits 0 from a clean target checkout;
selected installed controls exit 0 against retained release and sdist-built
wheels outside both repositories. Exact tested commit/artifact identities and
actual CI profiles are recorded for subsequent P4 sign-off. Failures remain
visible until fixed or explicitly accepted as a scope limitation by the owner.

## 5. Design and work lanes

### L1 — Review pending coverage and select families

Author target `notes/phase-3-family-selection.md` under the public-launch milestone.
Use ordinary Markdown columns: family, advertised surface, selected modules and
fixtures, keep/consolidate/retire/optional decision, reason or surviving protection,
actual result. Review source family tests, existing maps and the retained-private
classification as discovery aids; do not reconstruct every historical assertion.
There are 489 top-level target test modules at inspection, not 489 passing tests.

Required family rows and starting controls (target-relative):

| Family | Existing starting points; extend for actual advertised branches |
|---|---|
| Models / populations / checker / API | test_model_validation.py, test_model_guarded.py, test_population_load.py, test_checker_families.py, test_public_api.py |
| Transition / derivation / aggregate / temporal / opaque | test_derivation_rule.py, test_guarded_corpus.py, test_transition_mapping_totality.py, test_v70_phase3_opaque.py, test_v70_phase4_runtime.py; current v6/v7 successor modules |
| Synth / measurement | test_synth_conforming.py, test_synth_boundary.py, test_measure_offline.py |
| Extraction / rendering / fidelity | test_extract_cli.py, test_extract_projection.py, test_doccheck.py, test_fidelity_match.py |
| Codegen / conformance / generated workflows | test_codegen_emit.py, test_conformance_structural.py, test_public_generated_examples.py |
| Evolution / recovery / adoption | test_model_evolution.py, test_recovery_inventory.py, test_adopt_migration.py |
| Sessions / feedback / solve | test_exp_session_e2e.py, test_exp_feedback_derivation.py, test_solve.py, test_solve_successors.py |
| References / judgments | test_public_v71_reference_integrity.py, test_public_v71_full_judgments.py |
| Witness / exports | test_public_v71_witness_corpus.py, test_public_lean_export_successors.py, test_pyrel_export_boundaries.py; native profiles optional |
| Offline review / credentials | test_review_request.py, test_review_report.py, test_review_credential_launcher.py |
| Skills / installer / package / examples | T3–T5 modules below |

These are starting points, not permission to discard sibling unique assertions.
Explicitly review bootstrap, old-wheel materialization and frozen-failure hooks:
keep current protections; classify historical-only claims outside ordinary CI.
Selection must be complete at family/advertised-branch level before final runs.

### L2 — Ordinary acceptance path

Use standard pytest selection. Retire the 5,331-original completion requirement
from the current contributor/CI path; keep historical instrument claims distinct.
`tools/run_public_acceptance.py:36` pins ORIGINAL_COUNT=5331, and
`tests/test_public_acceptance_runner.py::test_actual_cli_refuses_incomplete_original_accounting_before_execution`
protects that superseded migration policy. Review this caller and its consumers
before changing or retiring the entry point. Preserve useful origin, timeout,
skip-reporting and optional-dependency controls as ordinary tests where needed.
Do not build another archival/receipt/coverage schema. Keep obsolete accounting
controls as explicitly historical only after verifying no current protection is lost.

Changes may affect `tests/conftest.py`, `tests/support/repository.py`, selected
fixtures/tests, `pyproject.toml` lane assignment and `.github/workflows/development.yml`.
Preserve default optional exclusions; no blanket xfail/skip conversion to get green.
No public API/signature/schema/exit changes are selected. Any necessary semantic
repair first records a reproduced finding and compatibility decision.

### L3 — Skills, package and contributor isolation

Pin sites: `tests/test_development_scaffold.py` check_twins (literal 16 skills),
`tests/test_skill_prose_sync.py`, `tests/test_packaged_skills.py`,
`tests/test_public_agents_skill_table.py`, `tests/test_public_installer.py`,
`tests/test_doctor_uninstall.py`, `AGENTS.md`, both real process-phase and
plan-review-panel directories. Measured now: 16 packaged skills; 16 symlinks plus
two real skills per discovery root. Remeasure at completion. No skill rewrite is
planned; any necessary twin edit changes both copies. Installer creates links.

Use fresh target-only checkouts and environments, no editable source install or
source archive. Check installed `gnd.__file__` and distribution origins, both
scratch-root install/doctor/uninstall lifecycles, resolved contributor references
and a labeled non-authoritative sample spec/record. Enforce absence of source
access in the isolated environment, not merely absence of a source path in docs.

### L4 — Candidate and result retention

After repairs/review, freeze explicit committed target inputs. Build the release
wheel and sdist once with uv 0.10.10; build a comparison wheel from that sdist in a
separate directory. Retain all three files plus hashes/source/tool versions in a
candidate directory and the selected CI artifact store (30-day workflow retention;
local retained copy until promotion/disposition). P4 sign-off references these
files. A package change creates a new candidate and reruns affected validation.
P4's temporary smoke outputs are not reusable candidate files.

Proposed new tests, only after approval: `tests/test_release_acceptance.py`, with
`test_retained_candidate_identity`, `test_installed_behavior_families`,
`test_installed_optional_refusals`, and `test_target_only_contributor_lifecycle`.
The module consumes an already built candidate path via `GND_CANDIDATE_DIR`; it
never rebuilds artifacts. Helpers have no new product API. Missing/altered artifact,
wrong import origin, unresolved contributor reference and unexpected skip controls
must fail the harness. Test both wheel origins independently and base versus synth
extra deliberately. Native/provider success stays unverified unless selected.

## 6. Decisions — all pending

| ID | Recommendation for approval | Alternative / cost |
|---|---|---|
| D1 | Approve this prose extension as the instrument; no optional spec panel | Corpus-first adds a separate fixture gate. Prose is justified here because product schemas/exits/validation semantics are unchanged; ordinary acceptance test design is not a new product format. New semantic contracts return to their own gate. |
| D2 / PL-D8 | Approve family-based keep/consolidate/retire/optional review and final full target default suite after selection, preserving configured exclusions | Focused-only results cannot establish the requested final contributor suite acceptance. Source exhaustive replay is not selected. |
| D3 / PL-D9 | Select Ubuntu Python 3.11 and macOS Python 3.13 with uv 0.10.10, final clean-install controls for both wheel origins | A missing profile remains unverified; narrowing support needs an owner decision. Version 0.1.0 remains provisional, publication version/ownership remains P4/P5. |
| D4 | Permit private commits/pushes and bounded CI in existing vasiloglou/gnd-public, candidate artifact retention, and one independent CLI diff reviewer with at most one repaired-diff follow-up | Local-only work leaves hosted CI acceptance incomplete. No recipients, access changes, live provider panel, upload or announcement selected. |
| D5 | Preserve source unit/publisher ownership during P3; record reconciliation and handoff readiness, leave any transfer explicit for candidate/publication decisions | Transferring now requires separate unit/question routing and cannot be inferred from a passing suite. |
| D6 | Approve §10 effort/change budgets and ordinary preservation of pending work | Material expansion returns with a concrete amendment; no silent numerical widening or disposal. |

## 7. Tests and verification-selection ledger

Commands below run from target unless stated. New acceptance nodes are proposed,
not claimed to exist. Each run retains exact command, environment, duration, exit,
selected/deselected/skipped counts and ordinary log. No inherited gate is claimed:
preparation results are historical inputs and both trees are dirty.

| Gate / obligation | Disposition; exact command and expected exit | Input boundary / justification / invalidation |
|---|---|---|
| T1 family selection and collection, C1–C3 | run: `uv run pytest --collect-only -q` → 0 after family review; manually reconcile selected modules with family record and actual CLI/API inventory | Tests/config/fixtures/docs/surfaces; no collection outcome is execution. Changes reopen selection. |
| T2 current contributor suite and advertised families, C1/C3/C5 | run, explicitly proposed D2: `uv sync --locked --group dev`, then `uv run pytest -q --tb=short` → 0 | Final target package/tests/lock/default exclusions; any changed input requires impact selection and final affected rerun. Unexplained skips fail acceptance review. |
| T3 skills and current contributor controls, C4 | run: `uv run pytest -q tests/test_public_installer.py tests/test_packaged_skills.py tests/test_skill_prose_sync.py tests/test_contributor_preparation.py tests/test_development_scaffold.py::test_twins_modes_and_generated_links tests/test_development_scaffold.py::test_non_authoritative_spec_record_exercise tests/test_review_credential_launcher.py --tb=short` → 0 | Skill resources, both roots, launcher, contributor docs, installer. Recheck changed references/pins and refusal branches. |
| T4 retained build origins / package | run: `uv build --out-dir candidate/release`; unpack the single sdist into candidate/source; `uv build --wheel candidate/source/get_nick_done-0.1.0 --out-dir "$PWD/candidate/comparison"` → 0 | Freeze commit/version first; adjust literal source directory if separately approved version changes. Assert exactly one wheel and one sdist, licenses, resources and package budget. Retain SHA-256 hashes, no automatic artifact equivalence. |
| T5 installed families/refusals/contributor exercise | run, explicit bounded distribution selection: `GND_CANDIDATE_DIR="$PWD/candidate" uv run pytest -q -o addopts='' tests/test_release_acceptance.py --tb=short` → 0 | Already built artifacts; clean per-origin venvs and isolated target-only tree. Wrong origin, changed artifact, missing resource/ref, skipped selected case must fail. No whole distribution lane. |
| T6 CI/profiles | run after D4: exact T1–T3/T5 selections in two isolated jobs, Ubuntu 3.11/macOS 3.13, uv 0.10.10; job conclusions success | Recorded target commit, workflow, artifact hashes, actual OS/tool versions; both jobs consume retained candidate, never rebuild release files. CI failures cannot be replaced by local smoke. |
| T7 source/target delta and question review | run: `git diff ac4be67afdddde0b2b2095a6cd383bc13852758c -- src/gnd pyproject.toml uv.lock` in source; compare selected target bytes and pending source work, record explicit dispositions | Command exit 0 is not reconciliation success; each relevant delta needs a reviewed disposition. Recheck affected original question origins/rulings; stop handoff on unexplained delta. |
| T8 repairs and instrumentation | run: exact changed test nodes plus affected consumers, `uv run ruff check <explicit changed Python paths>`, `git diff --check` → 0 | Record literal paths at execution; prove each review repair red on pre-fix code. Dirty controls must fail for intended cause. |
| Historical/native/provider/certification lanes | cadence: only explicit owner or separately configured CI selection | No full source default, evidence/census replay, live provider/native matrix or certification selected. Old-byte assurance unavailable for changed inputs. |

T1/T2 cover accepting and refusing branches, not merely family labels. T5 adds
real installed observations; tests of the runner alone do not discharge T5.
Review genuine optional skips separately from unexpected skips in required cases.

## 8. Implementability sweep

Completed against the inspected files: preparation has landed; current pytest
configuration supports a default suite; existing controls cover every listed
family but coverage completeness and execution remain to be reviewed. Standard
pytest avoids dependence on historical disposition completion. Existing release
workflow already separates build origins; it needs retained-artifact consumers
for final acceptance rather than reusing a temporary smoke. Both supported
profiles need hosted execution, hence D3/D4. No requirement depends on publication
or native/provider availability. No proposed predicate contradicts r3's removal
of exhaustive accounting. No tests, build, panel or external action ran for this
specification; feasibility is a structural reading, not a passing result.

## 9. Out of scope and boundary

No new semantic family, evaluator refactor, exhaustive historical repair,
compression/archive mechanism, blanket deletion, source history rewrite,
certification, provider/native success claim, unit/publisher transfer, P4 sign-off,
publication, trial outreach, visibility change or source retirement. No old
question closes merely because its code moved. Source preservation machinery is
not rebuilt to satisfy an obsolete evidence-size cap.

“retaining historical evidence does not recertify moved code; public CI does not
silently expand to every historical or live lane.” P4 candidate sign-off follows
this acceptance; P5 publication remains separately authorized. Observed profiles
are not a universal platform promise. Reviewer agreement is not proof.

## 10. Size, review and record

Estimate: 150–300 lines family/acceptance notes; 150–350 lines installed acceptance
tests/helpers; 50–150 CI/config/doc lines. Existing pending test changes are reviewed
as inherited work and measured separately, not silently counted as newly authored.
New runtime lines expected zero; a required runtime repair is a reproduced scope
amendment. Proposed incremental ceiling: 800 authored lines plus completion record;
no artificial cap on useful existing tests. Existing public size limits stand:
64 MiB tracked, 1 MiB ordinary blob, 12 MiB package payload, 2 MiB authored planning.
A conflict is reported; it never licenses retiring protection just to fit.

Budget: one family-review pass plus gap-driven follow-up; two final candidate
validation attempts (focused repairs between them); one independent diff review
and at most one follow-up. Failed attempts remain failures; budget exhaustion
reports the concrete remaining blocker rather than accepting it. No new archival
batch loop. Review fixes are reproduced/triaged with pre-fix failing controls;
refactoring review states executed changes or argues none needed from touched code.
Record actual gates, boundaries, open questions, candidate hashes and target commit
in the next available numbered P3 completion record only after acceptance. Stage
explicit paths and use the GND phase commit grammar. Keep migration originals in
source and a concise usable successor record in target.

## 11. Approval instrument and findings

Recommended instrument: this prose extension (D1), with the family selection
produced and made reviewable before execution. Approval must explicitly resolve
D1–D6 and authorize implementation; no auto delegation is assumed. If the owner
selects corpus-first, author its narrated expected outcomes before coding.

Pre-implementation finding: the existing acceptance runner's historical original
count prerequisite conflicts with r3. Retiring that current gate is a policy
adaptation, not weakening product assertions. Historical controls stay identifiable.
No runtime defect is asserted from this reading. Implementation findings will be
appended as discovered, including any refuted premise.


## Owner amendment — pull requests required, 2026-10-03

**Owner ruling:** “just make sure that any contributor must submit a PR, they
cannot edit the repo directly”. This requirement is approved by the owner;
it does not by itself approve the other pending D1–D6 execution decisions.

All contributor changes to the canonical default branch must arrive through a
pull request. Contributors may work in forks or topic branches; direct pushes,
force pushes and deletion of the default branch must be blocked. Apply this to
agent-authored changes as well. D4's proposed private pushes mean topic-branch
pushes and PR creation, not direct default-branch updates. Commit instructions
elsewhere in this spec do not authorize direct default-branch pushes.

During execution, inspect the actual GitHub default branch, repository access
roles and effective branch protection/rulesets. Configure and verify required
pull requests, required applicable CI checks and disabled contributor bypasses.
Do not grant contributors administrator or ruleset-bypass privileges. Apply the
rule to administrators where supported and avoid standing bypass exceptions.
Repository owners retain the platform's ability to change repository settings;
do not claim that a rule makes that administrative power impossible.

Add the PR-only contribution policy to target AGENTS.md and CONTRIBUTING.md,
and align workflow instructions and agent guidance. Contributor edits through
the GitHub web interface must also use a branch and PR. A passing local suite
or this phase's approval never grants an exception to the PR requirement.

Acceptance adds T9: retain the effective remote protection configuration and
verify that it requires a PR and successful applicable checks for the actual
default branch, blocks direct/force pushes and deletion, and grants no
contributor bypass. Use read-only configuration/permission evidence and an
isolated control where needed; do not test by pushing unauthorized content to
the real default branch. Documentation alone does not discharge this gate.
If repository visibility or account capabilities prevent enforcement, report
the specific limitation and a concrete alternative; do not describe the
repository as protected or change visibility without authorization.

Required approval counts, reviewer assignment and merge strategy are separate
choices; this ruling mandates PR submission and enforced checks, without
inventing a particular number of human reviewers. The final phase record must
state the observed enforcement boundary and any unresolved limitation.

## Owner approval — 2026-10-03

The owner replied **“approved”** after the business explanation and PR-only
amendment. D1–D6 are approved as recommended, including their budgets and
compatibility boundaries. Instrument: prose; optional spec panel omitted.
Approval binds the pre-approval spec SHA-256 `322cf504923be4be841f515bba733e10a1f5228f664f1081de93e3cfe2455800`.
Implementation may proceed. This is human approval, not delegated auto approval.
PR-only applies to agent changes. The initial awaiting-review line is historical.
