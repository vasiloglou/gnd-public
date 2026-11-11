# Guarded rule workflows · plan r1

**Status — draft, 2026-11-11.** Plan review did not run because no review
instrument was selected. Owner approval is pending. Execution defaults to
`auto=false`.

## Goal and completion predicates

Give rule authors a way to exercise a rule on deliberately constructed data,
see the findings an edit removes or adds, and propose rules from existing
data. Support both discovery inside GND and import of externally mined rules.

- GW1 imports the named-category rule from #182, checks the typed guarded
  clause and independently verifies distinct head-pair support.
- GW2 accounts for 42 removed bindings in a 43-to-1 narrowing while both
  editions still report an alethic failure. Added rules, removed rules and
  undecided outcomes are individually identifiable.
- GW3 emits a checker-confirmed failure and active pass for each served rule.
  An unserved rule has a named reason and does not suppress otherwise
  constructible cases for unrelated constraints.
- GW4 emits holding and near-miss candidates for both requested shapes,
  with independently checked denominators and attributable counterexamples.
- Phase evidence covers focused public commands, negative controls, docs,
  compatibility, and an installed-candidate smoke. The close record accounts
  for every criterion and carries any residual explicitly.

## 0. Binding design rules

Apply the six design rules in the
[project hook](../../../../.codex/skills/process-phase/references/project.md)
by name in each spec. Bound reads and input-proportional work. Pin refusal
precedence. Use one walk for a policy shared across atom sites or constraint
families. Assign each contract one normative home and measure disputed behavior
with discriminating fixtures. Keep induction advisory and keep expected-state
generation independent of checker verdicts. Follow ModelIndex and family
dispatch policy, preserve shims, and keep the runtime layer allowance at zero.

## 1. Scope, sources and authority

The public baseline is `793618f1`, the commit cited in the four issues. The
issue reproductions are reporter evidence. Source and test inspection establish
the seams below. Phase gates will reproduce the behavior with tracked fixtures.
This is framework development. A model's experiment-claim census cannot
establish the runtime coverage of these CLI workflows.

| Source and location | Obligation or observed dependency | Phase and gate |
|---|---|---|
| [#182, Asked for](https://github.com/vasiloglou/gnd-public/issues/182) | Typed literals in all four atom positions, reserved dollar prefix refusal, independent support equality and full confidence | GW1 A1–A4 |
| [#180, Asked for](https://github.com/vasiloglou/gnd-public/issues/180) | Same facts, two editions, declared identity, directional binding deltas, ill-formed and undecided behavior | GW2 B1–B3 |
| [#179, Asked for](https://github.com/vasiloglou/gnd-public/issues/179) | Matched pass, targeted failure, ID, checker confirmation, reason and other-family continuity | GW3 C1–C3 |
| [#181, Asked for](https://github.com/vasiloglou/gnd-public/issues/181) | Opt-in forbidden class pairs and same-class rules with optional target filter, support, bounds, near-misses and evolve proposals | GW4 D1–D4 |
| [Rule-check adoption close](../../rule-check-adoption/012-milestone-close.md) and [RC3 spec](../../rule-check-adoption/notes/phase-RC3-spec.md) | Version-15 rule identity and canonical baseline rows. Preserve the existing one-model comparison and refusal ordering | GW2 B2–B3 |
| [Rule-check followups close](../../rule-check-followups/007-milestone-close.md) | Preserve population admission and derived-ring extent | GW2 B3, GW3 C3 |
| [Rule-check release close](../../rule-check-release/005-milestone-close.md) and [0.3.0 close](../../release-0.3.0/007-milestone-close.md) | Use public command paths and validate an installed candidate. Existing release evidence is scoped to its shipped bytes | GW4 D4 and close |
| [Open questions](../../../open-questions.md) and 0.3.0 follow-up register | Existing questions retain their homes. Issues #169–#177 retain their own scope. Use affected-scope lint and check exact query-policy budgets when touching those sites | All phase records |
| [Project hook](../../../../.codex/skills/process-phase/references/project.md) and [CONTRIBUTING](../../../../CONTRIBUTING.md) | Owner gates, independent review, affected checks, component index and topic PR | All phases and close |

Two baseline conflicts need explicit rulings. The #182 example shares a body
and head predicate, which AMIE import currently refuses as `recursion`. A
guarded check over asserted facts can compare that predicate without deriving
facts. GW1 proposes a narrow exception for a constant-bearing head and retains
the variable-only refusal. The #179 repro goes through synth's independent
oracle invariant. GW3 must preserve that invariant while making unsupported
guarded rules local to the new case workflow and keeping ordinary constraint
generation usable on the same mixed model.

## 2. Contract proposal and product behavior

**GW1.** Accept role-typed constants using the existing export spelling,
including its subtype-family prefix and escapes. Bind them as JSON scalars.
A literal never supplies a variable binding or connects two antecedent atoms.
Body literals filter rows, head literals fill grounded head positions. Distinct
head pairs still determine support, including where several body matches
produce one head pair. Proposal admission remains atomic.

**GW2.** Propose opt-in `gnd check HEAD POPULATION --baseline-model BASE`,
mutually exclusive with `--baseline`. Evaluate one captured population under
two independently admitted same-vocabulary models. Pair declared IDs and list
added and removed rules even when their findings are empty. Use separate
side-local positions for anonymous rules and expose their unpaired status.
Compare typed offending rows without using aggregate bands as a shortcut.
Retain the two side verdicts and modalities. Mark rows with an undecided side
as incomparable and suppress inferred additions or removals for those rows.
Proposed command exit precedence is ill-formed 3, then 4 for any undecided
comparison, then 0 for a completed comparison. The two check bands belong in
the result. GW2 must settle binding identity when a guarded edit adds or
renames variables. Its fixtures must distinguish extra diagnostic columns from
a change in the actual finding. If the existing witnesses cannot establish a
shared projection, return an explicit incomparable reason for the affected
rule and specify the comparable projection that covers #180.

**GW3.** Propose an opt-in `gnd synth` rule-case mode with a separate,
ID-keyed manifest. It emits normal population files and records matched
antecedent evidence, target verdict and per-rule refusal reasons. Build cases
from role domains, preserving literals and repeated variables. Add a forbidden
fact for absence, omit the required fact or matching existential witness for
failure, and choose a typed falsifying assignment for comparisons. Construct
a positive consequent witness or assignment for the active pass. Prove both
target expectations independently before checker confirmation. Require
population admission, and report structural conflicts and other alethic
failures rather than claiming a conforming population. GW3 must prove
continuity by running ordinary generation for independently labelable
constraints on the same mixed model. A scoped generator view may support
construction, but artifacts must identify the checked model and cannot claim
full-model conformance or measurement truth for an unserved rule.

**GW4.** Propose an explicit relation/classifier role selector and optional
target marker role and literal. Require asserted, covered binary facts and
compatible role identities. First version proposes single-valued classifiers
and reports unmatched endpoints and ambiguous classifiers explicitly. Count
distinct R rows leaving K1 for each ordered forbidden pair (including rows
that leave K1 and end outside K2). Require positive support and covered
class membership for the counted domain. For same-class candidates count
eligible R rows whose target has a class (and passes the marker filter if
selected). A covered but missing source membership violates the implication.
Test missing endpoint cases against the generated guards before finalizing
this first-version scope. Near-miss reports retain ordered opaque counterexample
IDs. Use existing induced provenance, proposal and near-miss admission
policies and preserve discover defaults.

## 3. Dependencies and artifact homes

All four phases can begin from the shipped framework once individually approved.
GW1 is first because it is a bounded extension of a typed, tested importer.
GW2 and GW3 do not need GW1. GW4 does not need the miner, but owns the
integration smoke after GW1–GW3. The close waits on all four.

| Capability | Observed component and decision |
|---|---|
| Rule cases | Reuse `synth.pool`, `synth.values`, `synth.guarded` and checker admission. Adapt `synth.service` and the independent oracle boundary. The current guarded oracle covers selected existential shapes, leaving broader case construction to GW3. |
| Edition comparison | Reuse `check.baseline` canonical row identity, `check.service` evaluation and the vocabulary check used in `src/gnd/diff.py`. Adapt comparison orchestration for two address maps. The current diff's cross-model verdict-gap path keys on band differences and cannot express B1 by itself. |
| Joined discovery | Reuse `discover.population_view` for typed cell identity and stable fact IDs, and `discover.output` for proposals. Adapt `discover.service` and add a candidate family alongside `discover.candidates`. |
| Constants in mined rules | Adapt `export.mined_rules`; reuse `export.ilp_service` for captured inputs, counts and atomic proposal validation. Use `export.ilp_rewrite` for existing variable joins and the reserved-prefix precedent. |

Consult searches covered synth/guarded witnesses, baseline/bindings,
model comparison, joined discovery/proposals and AMIE/mined ILP. The index
review reported 60 descriptions older than their code. These are review leads.
The plan relies on the inspected runtime paths and tests. A separate
component-index Review remains available for owner selection.

## 4. Phases, deliverables and named criteria

| Phase | Acceptance criteria |
|---|---|
| **GW1 · A1–A4** | A1 literal in each body/head subject/object slot, plus the exact same-predicate category example. A2 role/prefix, canonical spelling, reserved prefix and variable-safety refusals. A3 distinct head-pair evidence and the zero, mismatch, does-not-hold and capped cases. A4 unchanged export bytes and variable-only behavior, proposal preview and independent checker parity. |
| **GW2 · B1–B3** | B1 one retained and 42 removed in the same band, and reverse direction. B2 reorder, deletion, addition, warning/modality flip, rowless failure, typed identity and guarded binding projection controls. B3 ill-formed input on either side, vocabulary mismatch, undecided on either side, coverage and option precedence, existing baseline and diff parity. |
| **GW3 · C1–C3** | C1 generated active pass and target failure for atom, absence, exists and comparison on declared IDs, for alethic and deontic rules. C2 vacuity, impossible or unsupported shapes, coverage, budget and checker/oracle disagreement with distinct reasons. C3 mixed-model generation on the shipped rule-check example, including mandatory and ring cases, plus ordinary synth/measure compatibility. |
| **GW4 · D1–D4** | D1 ordered forbidden pairs with an independent source support count, nonempty support and capped pair selection. D2 same-class and marker-filtered controls, including false implications. D3 near-miss IDs, uncovered, missing and ambiguous class controls, deterministic work caps, proposal validation and default-family parity. D4 installed-candidate smoke exercising all four CLI paths from outside the checkout. |

## 5. Documentation, skill and compatibility surfaces

GW1 owns the mapping table in `docs/reference/ilp-bridge.md`. GW2 owns the
edition comparison contract in `docs/reference/rule-check-report.md`. GW3
owns the artifact and exit contract in the synth reference. GW4 owns joined
family semantics in `docs/reference/discover.md`. Each phase updates the CLI
reference and affected packaged guidance where it is an entry point, linking
back to the normative home. Any new report fields or separate schema require
compatibility controls. Regenerate the component index where affected and
maintain real skill twins and installer-managed links under repository rules.

## 6. Risks and required controls

- Literal spellings can collide with variables or with a different primitive.
  Round-trip through the existing export codec and test each rejected spelling.
- A binding delta keyed by position or by a whole diagnostic tuple can hide
  removals or manufacture them after an edit. Test ID reorder and guard
  changes that retain some semantic subjects.
- A vacuous pass and checker-derived ground truth can both conceal a bad
  fixture. Prove a match and independent consequent outcome, then compare
  against the checker.
- Missing coverage can masquerade as a holding absence. Require coverage and
  test incomplete classifications, repeated values and typed joins.
- Pair enumeration, join fanout and retry loops can exceed reasonable time
  under legal byte caps. Pin pre-work bounds and exercise boundary controls.

## 7. Out of scope

External dev-tools changes, native miner runs, generalized Horn mining,
unbounded generation, automatic rule acceptance, publication and
certification are outside this milestone. A rule revision across a vocabulary
migration belongs to a separate contract.

## 8. Execution, approval and review protocol

Obtain the plan review and record the owner gate over identified bytes. Use the
project review bar and bounded convergence, with an explicitly selected
instrument. Each phase then takes its own spec owner gate, implementation,
focused verification, independent diff review, refactoring review and record.
Use topic PRs and separate owner merge authorization. At close retain the
plan/spec revisions, public command outputs, deterministic fixture digests,
installed-candidate evidence, review dispositions, and the issue-to-criterion
sweep. Run the project close review and record owner acceptance separately.

## 9. Per-phase verification story

| Phase | Focused lane and affected consumers |
|---|---|
| GW1 | Spec §8 names exact commands and expected results for AMIE importer, learner extraction, counting and guarded consumers. |
| GW2 | New edition CLI/schema tests plus `tests/test_rc3_baseline.py`, `tests/test_rc1_rule_ids.py` and the current diff/guarded controls. Pin deterministic directional payloads, exits and absence of misleading deltas. |
| GW3 | New generated-case tests plus synth expectation independence, conforming generation, guarded matrix and measure consumers. Use the shipped example and synthetic typed controls with a discriminating pass/fail pair for each supported consequent. |
| GW4 | New joined-family tests plus `tests/test_discover.py`, the fact-type family controls and evolve proposal preview. Assert work bounds and byte stability across hash seeds. Build a local candidate and retain module origin plus the four public command results from a clean target. |

GW2–GW4 select exact gates, test file names and any new runtime ceilings in
their specs before implementation. Every phase uses the default pytest lane,
affected Ruff checks and the component-index PR check. Historical evidence,
native/provider lanes and certificates follow their separate owner triggers.

## 10. Owner decisions and open questions

All decisions are proposed on 2026-11-11.

| ID | Decision for the owner gate |
|---|---|
| GW-O1 | Approve GW1's narrow same-predicate fragment and constant decoding. The current recursion refusal rejects the issue's own example even after literal decoding. See the GW1 spec. |
| GW-O2 | Settle the comparison entry point, informational exit and shared guarded binding projection. A CI ratchet exit could reuse baseline precedence, but would conflate two distinct workflows unless independently selected. |
| GW-O3 | Settle the synth artifact contract and mixed-model generation scope. A regular synth corpus extension also requires proof of `measure`'s full expectation contract. |
| GW-O4 | Settle classifier selector syntax, ambiguous/missing memberships and the pair/work ceilings. These choices change support and candidate eligibility. |
| GW-O5 | Select the plan/close review instrument under the project hook. No panel evidence exists for r1. |
