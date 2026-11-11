# Guarded rule workflows · plan r3

**Status — draft, 2026-11-11.** The owner set the issue order. The owner selected the
standard GND review panel for plan and close and delegated this milestone’s
approval gates with `auto=true`. Round 1 reviewed r2. The revised r3 bytes
await round 2 and the delegated plan gate. See the [review
disposition](plan-review-disposition.md).

## Goal and completion predicates

Show which guarded rules had a binding to judge, surface literals outside
declared value domains, then expose the findings a rule edit hides or adds.

- GW0 reports a count for each guarded verdict on the selected rule-check
  surface, and names the first antecedent prefix that yields zero bindings
  when all its source relations are populated and available. Model validation
  diagnoses the mistyped literal in either of the issue's atom positions.
- GW2 accounts for 42 removed bindings in a 43-to-1 narrowing even when both
  editions report an alethic failure. Added and removed rules and undecided
  outcomes are individually identifiable.
- Both phases retain focused public command evidence, compatibility checks
  and docs. GW2 runs one installed-candidate smoke covering both issues.
  Closure accounts for both issue
  criteria and records the three deferred items.

## 0. Binding design rules

Apply the six design rules in the
[project hook](../../../../.codex/skills/process-phase/references/project.md)
by name in each spec. Bound reads and input-proportional work. Pin refusal
precedence. Use one walk for a policy across all guarded atom sites. Assign
each contract one normative home and measure disputed behavior with
discriminating fixtures. Use ModelIndex and family dispatch, preserve shims
and branch evidence identities, and keep the runtime layer allowance at zero.

## 1. Scope, sources and authority

The public reproduction baseline is `793618f1` (GND 0.3.0). The issuer's
priority update relayed by the owner on 2026-11-11 supersedes r1's phase
order and active scope. r1 is retained in PR #184 commit `6a76afec`. Existing
phase IDs still identify their original deliverables. The new phase is GW0.
This is framework development. An experiment-claim census cannot establish
coverage of these public runtime commands.

| Source and location | Obligation or inherited constraint | Phase and gate |
|---|---|---|
| [#183, Asked for](https://github.com/vasiloglou/gnd-public/issues/183) | Antecedent binding count, first zero-match atom over populated relations, out-of-domain literal finding in validate | GW0 E1–E4 |
| [#180, Asked for](https://github.com/vasiloglou/gnd-public/issues/180) | Same facts, two editions, declared identity, directional binding deltas, ill-formed and undecided behavior | GW2 B1–B3 |
| [RC3 baseline spec](../../rule-check-adoption/notes/phase-RC3-spec.md) and [RC4 vacuous spec](../../rule-check-adoption/notes/phase-RC4-spec.md) | Version-15 identity, canonical baseline rows and established vacuity/exit behavior | GW0 E4, GW2 B2–B3 |
| [Rule-check followups close](../../rule-check-followups/007-milestone-close.md) | Preserve population admission and derived-ring extent | GW2 B3 |
| [0.3.0 close](../../release-0.3.0/007-milestone-close.md), [open questions](../../../open-questions.md) | Existing release evidence stays scoped to its shipped bytes. The separate #169–#177 follow-ups retain their scope. Use affected-scope lint and verify exact query budgets when touching those sites | Both phases and close |
| [Project hook](../../../../.codex/skills/process-phase/references/project.md) and [CONTRIBUTING](../../../../CONTRIBUTING.md) | Owner gates, independent review, affected checks, component index and topic PR | Both phases and close |

The [author's correction on #179](https://github.com/vasiloglou/gnd-public/issues/179#issuecomment-6805758864)
explains why generated cases are deferred. A generator using a rule's own
literal can exercise the misspelling successfully. The new validation finding
is what detects a consequent literal outside the declared vocabulary.

## 2. Contract proposal and product behavior

**GW0.** Carry diagnostic metadata from the bounded authoritative antecedent
evaluation into an opt-in plain rule-check report. Use the number of
distinct completed bindings that would be considered by the consequent.
Represent unknown join results explicitly. With complete and populated
antecedent sources, identify the first declared-order prefix whose join
result is empty, including a populated atom that loses the join through
incompatible bindings. Keep the current pass/vacuous distinction and exit
bands. Use the shared semantic validator to report a warning at the
literal's atom binding path when an applicable declared value constraint
definitively excludes it. Cover antecedent, positive and absence consequent
atoms, and existential witness atoms. The GW0 draft proposes the exact
fields, scoping and format.

**GW2.** Propose `gnd check HEAD POPULATION --baseline-model BASE`,
mutually exclusive with `--baseline`. Evaluate one captured population under
two independently admitted same-vocabulary models. Pair by declared ID and
list added and removed rules even when their findings are empty. Expose
anonymous rules as unpaired with side-local references. Compare typed
offending bindings independently of the run bands, and retain each side's
verdict and modality. Use the guarded witness's named bindings and a stable
shared projection for a narrowing edit. Derive the mapping from unchanged
antecedent atom/role sites, verified against unambiguous renamed variables;
added diagnostic variables must not turn the retained binding into a false
addition or removal. The phase spec must pin the comparable fragment and
test an ambiguous projection. Require that the shared projection preserve
distinct binding identity within each side’s witness set. Mark a rule
incomparable if a projection collides, alignment is ambiguous, or a side
is undecided. Suppress inferred deltas for that rule. Proposed command precedence
is 3 for ill-formed input, then 4 for an incomplete comparison, then 0 for
a completed comparison, including widening and a vacuous side. The two
check bands belong in the result. The edition comparison is informational.
The existing population baseline retains its ratchet exit behavior.

## 3. Dependencies and artifact homes

GW0 comes first by the owner's issue order. GW2 follows it and can share
its public report plumbing. Binding identity in GW2 comes from evaluated
witnesses and role sites. The GW0 count alone cannot identify a binding.
Neither active phase depends on deferred work.

| Capability | Observed component and decision |
|---|---|
| Guarded binding diagnostics | Adapt `check.snapshot_decision` and `checker.evaluate` to carry metadata from the existing indexed join in `correspondence.py`. Reuse `checker.reports` and `check.service` to project it. The existing message formatter performs a separate join for presentation. |
| Literal-domain finding | Adapt `model.validation` using its existing atom walk, warning path and role queries from `model.query_index`. Reuse typed identity and range semantics from `semantics.snapshot_spec` or their existing shared lower-level helpers, subject to the layer gate. |
| Edition comparison | Reuse `check.baseline` canonical row identity, `check.service` evaluation, and the vocabulary check in `src/gnd/diff.py`. Adapt comparison orchestration for two independent address maps. Existing diff population gaps cannot express B1 by themselves. |

Component consult covered guarded antecedents, snapshot decisions, model
validation, role domains, baseline and model comparison. The prior consult's
index review found 60 descriptions older than their code. That count is a
review lead from r1. The plan uses inspected runtime paths and tests. A
separate component-index Review can be selected independently.

## 4. Phases, deliverables and named criteria

| Order | Phase | Acceptance criteria |
|---|---|---|
| 1 | **GW0 · E1–E4** | E1 reports exact counts for matching, failing and empty antecedents. E2 identifies the first empty prefix over populated sources and preserves unavailable, coverage and empty-relation distinctions. E3 emits located domain findings in both typo fixtures and covers role/type scope, ranges and typed identity. E4 preserves existing report behavior, validates the new wire and text output, and gates diagnostic join overhead and literal-domain validation work. |
| 2 | **GW2 · B1–B3** | B1 reports 42 removed bindings and one standing binding in the same band, and reports 42 additions when models are swapped. Both completed comparisons exit 0. B2 covers reorder, deletion, addition, warning/modality flip, rowless failure, typed projection, and collisions between distinct bindings. B3 covers ill-formed input, vocabulary mismatch, undecided on either side, option precedence, a vacuous side, baseline/diff parity, comparison work exhaustion, and an installed-candidate smoke of both issues. |

## 5. Documentation, skill and compatibility surfaces

The rule-check report reference owns both report contracts. The ORM
constraint reference owns the literal-domain finding. The CLI reference
and affected packaged guidance point to those homes. Keep prior report
variants readable and verify schema and text/JSON parity. Update component
entries where behavior changes and retain installer-managed link ownership.

## 6. Risks and required controls

- An unavailable join can look empty. Record zero only for an observed empty
  result or a covered empty relation, and test the omitted and refused cases plus the evaluator’s internal
  work-limit path.
- Diagnostic work can duplicate joins or change existing branch outcomes.
  Carry observations through the existing evaluation and keep the report
  projection cheap. Test join cost and legacy report bytes.
- Comparing values by Python equality can equate boolean and numeric values.
  Use existing typed normalization and range rules, including open endpoints.
- Pairing by position or by the entire witness tuple can hide removals or
  manufacture changes after an edit. Test stable IDs, side-local anonymous
  positions, renamed bindings and a guard that adds a variable.

## 7. Deferred and out of scope

| Original phase | Deferred request | Revisit when |
|---|---|---|
| GW3 | [GR-D8 · generated cases](https://github.com/vasiloglou/gnd-public/issues/179) | Someone needs generated synth/measure coverage or mixed-model corpus continuity. Hand-written examples serve current rule tests and preserve author intent. |
| GW4 | [GR-D10 · relational discovery](https://github.com/vasiloglou/gnd-public/issues/181) | A project asks for joined-rule suggestions. |
| GW1 | [GR-D11 · mined-rule constants](https://github.com/vasiloglou/gnd-public/issues/182) | The owner selects the miner route. The [r1 draft spec](phase-GW1-spec.md) retains the typed constants design and same-predicate open decision. |

These items are outside the completion gate. External dev-tools changes,
live miner runs, vocabulary migration, publication and certification are
also outside this milestone.

## 8. Execution, approval and review protocol

Use the explicitly selected project review instrument and bounded
convergence. Record the plan review and owner ruling over identified bytes.
Each phase requires its spec owner gate, implementation, focused
verification, independent diff and refactoring reviews, and phase record.
Use topic PRs and separate owner merge authorization. The close requires
both phase records, public command outputs, fixture and candidate digests,
review dispositions, and the issue-to-criterion sweep. Record close review
and owner acceptance separately.

## 9. Per-phase verification story

| Phase | Focused lane and affected consumers |
|---|---|
| GW0 | The [GW0 spec](phase-GW0-spec.md) names guarded semantic/validation tests, rule IDs, baseline/vacuity consumers, report schema and exact fixture outcomes. |
| GW2 | New edition CLI/schema tests plus RC3 baseline, RC1 rule IDs, guarded witness and diff consumers. Pin directional payloads and exits, then exercise both issues against an installed candidate from a clean target. |

GW2's spec will select exact commands and work ceilings before
implementation. Use two evaluations plus hash-based comparison over their
witnesses. Gate the new work separately with a high-fanout control and a
predeclared comparison budget. Exhaustion yields exit 4 and explicit
incompleteness. Both phases use the default pytest lane, affected Ruff
checks and the strict component-index change check. Historical
evidence/native/provider lanes and certification have separate triggers.

## 10. Owner decisions and open questions

| Decision | Status |
|---|---|
| Priority and active scope | Owner direction, 2026-11-11. GR-D12 first, GR-D9 second. GR-D8 and GR-D10 deferred. GR-D11 has no execution priority assigned and is carried with them. |
| GW0 report and validation contract | Proposed. Select opt-in wire version, preserve zero-binding pass and use a located validation warning. See GW0 §7 for the tradeoffs. |
| GW2 interface and comparison identity | Proposed. Approve the entry point and exit policy, then pin comparable guarded binding projections and ambiguous-case handling in its spec. |
| Plan and close review | Standard GND review panel selected by the owner. Round 1 reviewed r2. See the [review disposition](plan-review-disposition.md) for outcomes and the two-round plan budget. |
