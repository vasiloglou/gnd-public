# Compiled operation obligations in snapshot checks

Draft r1, 2026-10-12. Milestone: `compiled-snapshot-obligations`.
Source: [gnd-public issue #16](https://github.com/vasiloglou/gnd-public/issues/16).
Inspection baseline: `0c3a5a7`. Planning only; owner approval, plan review,
phase execution, implementation and publication have not occurred.

## Problem and completion predicates

Issue #16 reports that `filter_compare.pre_numeric` appears as compiled in
`validate --trace`, but a population describing a string-role numeric comparison
has no corresponding failure in `api.check` or `check --populations`. A full
operation walk rejects the comparison. The reporter checked consistent derived
claims and recorded zero derivation failures. An exit of 2 is not a passing
result; the discrepancy is the absent applicable alethic obligation.

The report used GND `75eda93f314e7ef82578ab4ee212d5e6d964fd71` and gnd-apps
`efc9c0e`. Its reproduction and results are external evidence, not a reproduction
performed during this planning task:

- [Driver](https://github.com/vasiloglou/gnd-apps/blob/efc9c0e/.gnd-analytics/milestones/M3/evidence/audit-driver.py)
- [Results](https://github.com/vasiloglou/gnd-apps/blob/efc9c0e/.gnd-analytics/milestones/M3/evidence/phase-01-compiled-snapshot-gap.json)
- [Trace](https://github.com/vasiloglou/gnd-apps/blob/efc9c0e/.gnd-analytics/milestones/M3/evidence/phase-01-expense-trace.txt)

Current source confirms a contract boundary, not yet a reproduced runtime bug:

- `src/gnd/model/_operations.py:compile_operation` creates in-memory projected
  subset obligations. It explicitly limits their use to walks because ordinary
  populations may lack operational provenance.
- `src/gnd/transition.py:_compiled_verdicts` evaluates them against a walk's
  pre-state; it skips uncovered relations and emits only failing/warning rows.
- `src/gnd/checking_service.py` routes public single checks to the checker;
  `src/gnd/batch.py:check_population_directory` also calls the checker.
- The packaged `orm-meta.schema.json` says snapshot checking ignores operations.
  `representation-format.md` promises unchanged snapshot reports when operations
  are stripped, yet describes compiled obligations as checkable without a walk.

**Proposed outcome:** an explicit, opt-in public snapshot checking mode for the
eligible compiled subset obligations, available to single and batch callers,
with the existing default contract preserved and trace terminology clarified.
The caller opts into treating those operational implications as standing
obligations of this population. GND does not infer historical provenance from
the population. This proposal requires the owner's semantic ruling CS-D1.

The milestone can close when:

1. The report is reproduced on current bytes with a self-contained fixture and
   admitted numeric-role controls. Baseline evidence pins the actual failed
   obligation sets, derivation failures, coverage and exit codes on each surface.
2. In the approved mode, the issue's invalid population produces a named alethic
   `filter_compare.pre_numeric` failure on single and batch surfaces and exit 1
   under existing band precedence. Its correct derivations remain correct.
3. Eligible compiled obligations have matching single/batch outcomes, including
   deontic, uncovered, vacuous and typed-identity cases. Missing coverage cannot
   become a clean compiled-obligation result.
4. Default snapshot results, operation/model digests and ordinary walk semantics
   remain unchanged, except for expressly approved trace clarification.
5. Documentation states the supported agreement boundary: compiled standing
   subset obligations, not all temporal preconditions, dynamic rules, effects,
   intermediate-state checks or frame obligations.
6. Focused gates, independent diff review and the milestone question sweep are
   recorded; a PR is submitted and owner acceptance is recorded separately.

## 0. Binding design rules

| Rule | Requirement |
|---|---|
| CS-R1 — Explicit contract | Preserve default snapshots. The opt-in mode asserts standing obligations; no silent provenance assumption or full-walk equivalence claim. |
| CS-R2 — One evaluation home | Shared compiled-obligation evaluation serves single, batch and walk routes with explicit policies where their coverage/reporting contracts differ. Do not import transition internals into a lower checker layer. |
| CS-R3 — Stable compiler | Retain literal/conjunction/shared-parameter, sole-asserter and no-retract guards. Compilation remains in memory; do not append generated constraints to authored YAML, operation dictionaries or `Model.constraints`. |
| CS-R4 — Honest outcomes | Preserve alethic/deontic grading and band precedence. In snapshot opt-in mode, uncovered or unsupported applicable obligations must have an explicit unchecked/refusal disposition. Transition-only entries are separately identified as outside this mode. |
| CS-R5 — Stable identities | Use typed fact identity, all role pairs and every eligible asserted effect. Pin operation-qualified obligation identities, deterministic ordering and deduplication. |
| CS-R6 — Approval and evidence | `auto=false`. Plan authorship is not implementation approval. Preserve existing records and historical byte-bound evidence; no inherited certification. |

Each phase spec also names or argues inapplicable every paid-for rule in
`.codex/skills/process-phase/references/standing-rules.md`: totality, algorithmic
bounds, validation order, complete policy traversal, one normative home and
measurement of contested representations. Follow the current layer map,
ModelIndex policy, family registry and compatibility-shim inventory.

## 1. Scope and authority

This is a semantic successor to behavior-preserving `code-refactoring`, not a
retroactive change to its approved plan or records. RF9 repair/CI records and
RF6/RF7 query, family and restriction carryovers must be read during phase
harvesting for the actual touched homes. Existing PROJECT.md and milestone
records are retained. No domain model is being opened or evolved, so a
`gnd coverage MODEL` census would not decide this framework milestone's scope.

## 2. Contract proposal

CS0 must settle exact API/CLI activation syntax and report representation before
implementation. Prefer a keyword on `api.check` and an equivalent `check` flag
accepted for both a single population and `--populations`. Reject conflicting
transition-mode combinations with a named usage error. Unsupported consumers
must not accept the option and silently ignore it.

Preserve existing JSON schemas where their fields can faithfully carry generated
obligation references and counts. Otherwise propose a versioned schema change
and enumerate consumers before approval. Include operation ID, precondition ID,
compiled effect/projection identity and source locator without collisions with
authored constraints. Batch `failing_constraints` must carry stable references to
compiled failures; single reports must carry their witnesses and reasons.

Do not merely concatenate verdicts after projection: `checker.band` can derive
its result from `snapshot_projection`, so report counts, semantic projection,
band selection and assurance applicability must all see the approved obligation
set. Redaction and references must use the same existing public boundaries.

## 3. Dependencies

CS0 -> CS1 -> CS2 is a hard sequence. Phase specs and owner gates precede each
implementation. No phase depends on optional provider review, external app
execution, package publication or a certification run. The gnd-apps report is
input; a portable local fixture is required for development and CI.

## 4. Phases

### CS0 — Reproduce and approve the semantic contract

Write `notes/phase-CS0-spec.md` under `process-phase`; use corpus-first approval.
After that gate, author the self-contained issue fixture, narrated expected
outcomes and a baseline driver. Inspect external source as data; do not execute
an unreviewed downloaded driver or import private evaluator APIs.

Criteria:

- CS0-C1: reproduce the string-role comparison, numeric control, consistent
  derived claims and walk failure through public interfaces on current GND.
- CS0-C2: pin both current behavior and proposed successor expectations; new
  expectations fail on baseline for the missing obligation, not malformed inputs.
- CS0-C3: inventory compiled and retained entries; approve CS-D1 through CS-D5,
  exact flags/signatures, schema/branch identities, coverage and work limits.
- CS0-C4: retain baseline commands/results and digests; any failure to reproduce
  is a refuted premise returning to the owner before CS1.

### CS1 — Shared evaluation and public single/batch integration

Write and approve `notes/phase-CS1-spec.md`, then implement the approved contract
through actual defining homes. Extend semantic/report/applicability registration
as needed. Preserve walk behavior through policy-specific controls.

Criteria:

- CS1-C1: the exact same invalid fixture produces the named failure and band 1
  through `api.check`, single CLI and batch CLI; admitted controls gain no false
  failures. Correct derivations do not become failures.
- CS1-C2: exercise missing coverage on each side, empty antecedent, multiple
  asserted effects, repeated variables/all role pairs, duplicate facts, typed
  scalar distinctions and operation/constraint name collisions.
- CS1-C3: exercise alethic fail, deontic warning, unchecked and vacuity precedence;
  assert counts, witnesses, stable references, schemas and redaction, not exits
  alone. Preserve batch loading/refusal and aggregate precedence.
- CS1-C4: compiler guards and default snapshots/digests/walk controls remain green;
  no new layer allowance, mutable model contamination or cached-mode leakage.
- CS1-C5: pin work limits for any new join path; exceeding them is an honest
  unchecked/refusal outcome. Every declared branch has a discriminating case.

### CS2 — Trace contract, docs and consumer regression evidence

Write and approve `notes/phase-CS2-spec.md`, then clarify `validate --trace`, CLI
help, API reference, transition guide and canonical packaged ORM reference.

Criteria:

- CS2-C1: trace distinguishes compiled eligibility, runtime activation and retained
  transition-only reasons; default and opt-in examples state what each checks.
- CS2-C2: a bounded matrix shows 100% normalized single/batch agreement for all
  local fixture compiled obligations, with denominator and excluded obligation
  inventory recorded. Compare with walk failures only where the fixture's
  snapshot representation preserves those precondition meanings.
- CS2-C3: retained transition-only, intermediate-state and frame counterexamples
  demonstrate why passing this mode cannot establish full-walk correctness.
- CS2-C4: give gnd-analytics an executable public-interface regression recipe and
  exact GND commit identity; its downstream fast-path acceptance remains the app
  owner's gate. Do not claim its M3 gate ran unless it actually did.

## 5. Skill and documentation surface

Canonical semantics live in
`src/gnd/skills/gnd-orm-core/references/representation-format.md` and its schema
description; public guides link to that home. Inventory every conflicting
snapshot/operations sentence during CS0. Packaged discovery links remain
installer-owned; never edit symlinks manually. If real development skill twins
change, preserve byte equality and executable modes across discovery roots.
No unrelated skill rewrite is required.

## 6. Risk register

| Risk | Required control |
|---|---|
| Operational implications falsely asserted over arbitrary data | Explicit opt-in contract; a population without operational provenance control; no default change. |
| Missed obligations masked by inadequate status or derivation success | Assert qualified failed-obligation sets and counts in addition to bands. |
| Covered/unknown relations silently treated as empty | Separate coverage cases for both relations and bound reference populations. |
| New reports disagree with projection or assurance | Bind composed semantic outcomes, emitter schemas, branch identities and applicability to the same obligation inventory. |
| Batch option is parsed but not evaluated | Same bytes through API, single CLI and batch CLI; mutation/removal changes results. |
| Compiler generalization breaks soundness | Sole-asserter, no-retract, literal, conjunction and all-role-pair controls. |
| Scope expands to full transition equivalence | Explicit excluded classes and negative equivalence examples. |
| Repairs break compatibility or layered architecture | Actual lookup controls, unchanged defaults/digests and zero-allowance layer gate. |

## 7. Out of scope

No automatic full-walk replacement, provenance inference, compiler broadening,
new temporal logic, batch per-warning-detail enhancement, external app edits,
package publication, CI/protection changes, certification or merging. A
documentation-only resolution is an alternative owner decision, not completion
of the proposed opt-in checking work.

## 8. Execution and review protocol

This plan is unreviewed. The plan/close four-reviewer bar from the development
protocol remains pending; provider panel execution needs explicit selection of
the maintained panel, with no automatic sibling handoff. Review-round bounds and
residual dispositions must follow `review-convergence.md`.

After plan acceptance, invoke `process-phase CS0 compiled-snapshot-obligations`
with default `auto=false`. For every phase: harvest the whole effective plan and
carryovers, write the spec, obtain owner decisions, implement and verify, perform
independent diff and refactoring review, then record and commit on authorization.
Reproduce review findings; regression tests must fail on pre-fix bytes. Complete
the close question sweep separately. Changes use a topic branch and PR; merge
requires owner authorization. No commit/publication authority is inferred here.

## 9. Verification selection

These are future obligations, not checks already run. Exact nodes/commands belong
in each approved spec. New test filenames are proposals and do not exist yet.
Keep the default pytest lane exclusions; no exhaustive historical replay.

| Phase | Mandatory gate, expected exit 0 when complete | Starting points |
|---|---|---|
| CS0 | Public reproduction and admitted controls match narrated baseline; successor expectations are demonstrated red for the omitted obligation | Proposed `tests/test_compiled_snapshot_obligations.py`; existing `tests/test_public_transition_contract.py` |
| CS1 | All approved compiled branches, single/batch agreement, default compatibility, schema/band/redaction/applicability and affected references pass | Proposed issue tests; selected `tests/test_v61_phase1_batch.py`, `tests/test_report_json.py`, `tests/test_public_transition_walks.py`, `tests/test_rf1_layering.py` and affected family/reference/branch nodes |
| CS2 | Trace activation/boundary examples and bounded agreement matrix pass; all touched documentation contracts agree | `tests/test_public_transition_trace.py`; new regression-recipe/trace cases and CS1 issue tests |

Select affected consumers by actual changed contracts. Existing fixtures claiming
unchanged default bytes stay unchanged; opted-in successor results have separate
expectations. Selected current-byte controls restore only their specific claims;
old certificates do not certify this change. This planning-only edit requires
file/link/whitespace checks, not runtime suites.

## 10. Owner decisions and open questions

All rows are proposals; none is an owner ruling.

| ID | Proposed default | Resolve by |
|---|---|---|
| CS-D1 — Meaning of the fix | Add explicit opt-in compiled snapshot obligations and clarify trace. Alternatives: transition-only clarification with no fast path, or a separately approved breaking default change. | Plan gate, before CS0 implementation |
| CS-D2 — Activation/provenance contract | Caller asserts standing operational implications through explicit single/batch API/CLI activation; GND makes no provenance inference. Pin exact interface and unsupported combinations. | CS0 |
| CS-D3 — Missing coverage and limits | Explicit unchecked/refusal in opted-in snapshots; preserve walk policy. Set exact reason codes, bands and join budget. | CS0 |
| CS-D4 — Report compatibility | Reuse schema only if stable qualified references, counts and semantic projection can represent the new outcomes faithfully; otherwise version with consumer inventory. | CS0 |
| CS-D5 — Agreement boundary | Require full agreement for eligible compiled obligations in a declared finite corpus; list transition-only and other walk-only exclusions. No promise of gnd-analytics full-plan equivalence. | CS0 |
| CS-D6 — Review selection | Select the plan review instrument explicitly; no live paid review has been invoked. | Plan gate |

Next actionable step after plan acceptance: author the CS0 spec and its approval
instrument. Issue #16 stays open until the implemented outcome and accepted
contract are recorded; a planning PR must reference it without auto-closing it.

## Close amendment — delegated disposition, 2026-10-13

The draft statuses above describe the original planning bytes. The owner later
approved the opt-in CS0 contract and explicitly delegated remaining milestone
gates (auto=true), four local subagent readers instead of the pending plan
panel, commits and the runtime-fix PR. The four local plan readers accepted
bounded implementation with the obligations recorded in 001-phase-CS0.md.
No maintained provider panel or certificate is claimed.

CS2-C2 is amended under that delegation: public batch output exposes exit,
counts and failed references, so its agreement claim is limited to those exact
observable fields (2/2 fixture populations, 23 compiled entries each). Full
single rows and adversarial warnings/unknowns remain covered by focused tests.
Per-warning batch identity enhancement remains excluded under section 7.
This repairs the original unmeasurable demand for all per-row batch outcomes.
The supported public regression recipe and exact candidate identity live in
notes/app-regression-recipe.md. App adoption, merge, release and human acceptance
remain separate owner actions. The close record supplies the question sweep;
its local review findings and delegated disposition are separately retained.
