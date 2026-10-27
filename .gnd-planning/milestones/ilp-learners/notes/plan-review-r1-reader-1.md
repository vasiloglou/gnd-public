# Reader 1: semantics and admission safety

**Digests:** both match.
- `ilp-learners-plan.md` = `6cb10d97…8e463`
- `phase-IL1-spec.md` = `59629173…6b027`

**Verdict: request-changes**, within my lens.

**Scope.** I read both subjects in full, plus these files:
- `src/gnd/export/ilp.py`, `ilp_service.py`, `ilp_rewrite.py`, `ilp_popper.py` (`_unquote`)
- `docs/reference/ilp-bridge.md`
- `representation-format.md` §Guarded constraints and `provenance-and-modality.md` (induced rows)
- `$defs.induction` and the induced `provenance_policy` in `orm-meta.schema.json`
- `src/gnd/discover/output.py` and `support.py`
- `src/gnd/evolve/service.py` `_enforce_d12`
- `src/gnd/model/_validation.py` (the guarded rule set)
- IK plan §0 (IK-R1 to R12) and Request 5

I ran three probes, all read-only, writing only under the scratchpad `review/reader-1/` directory:
- (a) `uv run gnd validate` on a copy of the refunds model with one extra cross-type guarded constraint added.
- (b) `ilp_rewrite.rewrite` on single-feature clauses.
- (c) Python arithmetic on the T4 octal values.

**What holds (verified, not findings).** Nothing an adapter emits can reach `confirmed` or `alethic` without review:
- `_enforce_d12` (`evolve/service.py:287-345`) refuses any new `induced` constraint that is not `proposed`/`deontic`.
- Confirmation is allowed only as a reviewed status change of an existing proposed predecessor.
- `ilp_service._envelope` (`:235-237`) hard-codes `induced`/`proposed`/`deontic`.
- `derivation_rule` output is out of scope (plan:336).

The problems below are about whether meaning is preserved and whether the re-check gates can be falsified, not about modality escape.

## Findings

- **R1-F1** (blocking, high): IL4's "support" counts the wrong thing.
  - **Claim.** AMIE's support and standard confidence count distinct head pairs (x, y). GND's guarded evaluator counts complete antecedent bindings, and those include body-only variables. For `r1(x,z), r2(z,y) ⇒ r(x,y)`, GND's natural counts are over (x, y, z). So either the live run refuses every rule that has a body-only variable as `support-mismatch`, or the oracle and the provenance silently record a quantity that is neither AMIE's nor documented.
  - **Plan.** Plan:173-176 and IL4-C3 (plan:273-274) say "GND support … standard confidence" and never define either. IK-R2 requires "per-family definitions fixed in the phase spec".
  - **Source.**
    - `representation-format.md:535-547`: evaluation enumerates the antecedent's variable bindings.
    - `representation-format.md:570-575`: `offending_facts` is keyed by every `$` variable.
    - `verbalize.py:616`: `bindings={binding_count}`.
    - IK5 and discover each give `support` a different meaning: covered negatives over covered (`ilp_service.py:400`), satisfying subjects over subjects (`discover/output.py:49-50`).
  - **Reproduce.** Compare the guarded message for a two-atom antecedent with one body-only variable against the AMIE definition.
  - **Repair.** Make the plan fix IL4's definition, for the IL4 spec to elaborate:
    - numerator = |{(x,y) : ∃z body ∧ head}|
    - denominator = |{(x,y) : ∃z body}|
    - `confidence.value` = numerator / denominator, with a named `formula`
    - counted over distinct head-variable projections
    - the IL4-C3 oracle uses the same definition
    - state that only counts are compared, since AMIE emits no sets; this is weaker than IK5's set comparison (`ilp-bridge.md:117-118`).

- **R1-F2** (blocking, medium): A rule that joins values of different object types is admitted, and GND agrees with it.
  - **Claim.** Three of the new learners do not respect GND's types:
    - AMIE triples are untyped (plan:166-169).
    - The LLM writes free clauses through `--target neutral` (plan:184-186).
    - The ILASP mode bias is unspecified on typing (plan:139-140).

    A learner can therefore join, say, a refund id with an amount when the values coincide. GND's guarded validation has no rule that checks the object types of a variable's join sites. The type-compatibility rule exists only for derivations, and the rewriter uses role types only for comparisons. So the re-check reproduces the learner's type confusion and the rule enters as a valid proposal. The plan's control row (plan:325, "a fragment table per adapter") does not cover this.
  - **Source.**
    - `_validation.py:4393` (`_rule_derivation_term_type`) applies to structured derivations only.
    - The guarded rules (`representation-format.md:1382-1388`) contain no join-type rule.
    - `ilp_rewrite.py:128-133`: `role_type` is used only by check 5.
  - **Reproduce.** I appended to a scratch copy of `src/gnd/examples/refunds/model.orm.yaml` a guarded `induced`/`proposed`/`deontic` constraint that binds `$x` as `refund_amount.amount` and as `refund_by.refund`. `uv run gnd validate` returned "is a valid GND ORM model", exit 0.
  - **Repair.**
    - Add an import-side fragment check, `type-confused-join`, using the same ancestor-closure compatibility as `semantic:op-term-type-compat`, applied in the shared rewriter so that every adapter, `neutral` included, gets it.
    - Require typed exports: AMIE entities spelled with an object-type prefix, and typed ILASP `#modeb` placeholders.

- **R1-F3** (blocking, medium): IL3's "single feature maps to a clause" is false for features without a threshold.
  - **Claim.** A feature with no threshold is `exists f(_, …)` (plan:153-154). As a clause it is `wrong(X) :- f(X, …)`: one atom and no comparison. The rewriter's designation step needs an atom whose variables are all bound by other atoms, so it refuses `non-ground-absence`. That holds for every such feature, so IL3-C2 (plan:258-260) and completion item 3 (plan:46-48) cannot hold for half the feature kinds. The current fragment has no "false" consequent that could express "any f fact implies wrong".
  - **Source.** `ilp_rewrite.py:147-157`.
  - **Reproduce.**

    ```
    rewrite(wrong(X) :- f_refund_amount(X,_,A), gt_t_amount(A,100))   → guarded, comparison <= 100
    rewrite(wrong(X) :- f_refund_amount(X,_,_))                       → REFUSED non-ground-absence
    rewrite(wrong(X) :- f_refund_amount(X,R,A))                       → REFUSED non-ground-absence
    ```
  - **Repair.** Do one of two things:
    - restrict the IL3 feature vocabulary to thresholded features; or
    - state in the plan that unthresholded single-feature rules refuse `non-ground-absence` and count them as expected refusals.

    Do not claim "maps to one clause" for them.

- **R1-F4** (hardening, high): Rule-set learners emit negated features, and the plan never names their refusal.
  - **Claim.** Binarized rule-set learners routinely emit `feature = 0` or `feature <= 0.5`. For an existential feature `∃A: f(_,A) ∧ A > t`, the negation is the universal `∀A: A ≤ t` (or "no f fact"). A naive reader that maps it to `A <= t` would invert the quantifier, so the admitted rule would mean something the learner did not learn. Plan:156-162 and IL3-C2 list only `propositional-conjunction` and `ordered-rule-list` as refusals.
  - **Repair.**
    - Fix a feature polarity table in the plan: true literal maps to the clause; false or negated literal refuses `negation-as-failure`.
    - Require a test per learner output spelling, including `<= 0.5` on binary columns.
    - Have the feature schema declare each column's literal meaning, so the reader cannot reinterpret a threshold.

- **R1-F5** (completeness, medium): The ILASP task leaks facts across examples.
  - **Claim.** Plan:137-140 puts "background from the neutral facts" and also each population's facts as context. Every neutral fact is tagged with its example (`ilp.py:176-196`), and the export has no population-independent facts. If background holds the tagged facts, a hypothesis can match another population's facts, so ILASP coverage differs from GND's per-population evaluation. If it holds untagged facts, every context sees every population's facts.
  - **Repair.**
    - State that background holds only the comparison definitions.
    - Put each population's facts, without the example argument, only in its own context.
    - Make `#modeb` arities equal the predicate arity minus 1, so the reader's "thread X" step (plan:141-142) inverts the rendering exactly.
    - Add a golden that pins this.

- **R1-F6** (hardening, medium): The ASP reader's refusal list is incomplete, and ASP constants have three identities.
  - **Claim.** IL2-C2 (plan:245-248) lists constraint, choice, weak, `not`, aggregate and disjunction. It omits:
    - classical negation `-p(X)`
    - arithmetic terms (`X+1`)
    - intervals and pools (`1..3`, `;` in terms)
    - `#show` and other directives
    - and it does not distinguish symbolic constants (`card`) from strings (`"card"`).

    An unhandled `-p` could be read as a predicate name, and `card` versus `"card"` could be silently unified with GND's string. The Popper fragment table has a constants row (`ilp-bridge.md:181`); ASP needs its own, with three kinds.
  - **Repair.** Extend IL2-C2 with these constructs, each with a name and a test, plus a fragment-table row that fixes how the export renders strings and how the reader maps each constant kind.

- **R1-F7** (hardening, medium): LLM proposals are indistinguishable in provenance, and their inducer name is unchecked.
  - **Claim.** IL5 imports through `--target neutral`, so `method` is `ilp-neutral` (`ilp_service.py:328`, `ilp-bridge.md:165`). For `neutral` the learner check is skipped: `target in LEARNER` is false at `ilp_service.py:319-321`, and the spec's registry sets `learner: None` for neutral (spec:67). A run record can therefore name itself `popper`, and the admitted rule then says Popper learned it. The model loader accepts `inducer: popper, method: ilp-neutral`; probe (a) loaded exactly that.
  - **Repair.** Give the LLM proposer its own registry entry:
    - `target: llm`, `parse: None`, `method: ilp-llm`
    - learner name constrained to the agent adapter id
    - model id recorded in `inducer.version` or the evidence

    Alternatively, refuse a neutral record whose learner name is a registered learner's name (`learner-mismatch`). Either way, IL5-C3's "named agent and model" becomes machine-readable rather than prose-only.

- **R1-F8** (hardening, medium): The coverage "claim" may not be independent of GND, which would make IL-R4 untestable.
  - **Claim.** Learners do not emit sets:
    - IL1 computes coverage "by evaluating the program in SWI" (spec:104-106).
    - The IL5 run record has to be built by the script, because an LLM cannot produce `clauses_sha256`.

    The plan never forbids the evidence script from deriving `covered` with GND itself. If it does, `coverage-mismatch` compares GND with GND and IL5-C2's gate can never fail on real output. Popper's own printed counts (tp/fp), which are the learner's actual claim, are not compared at all.
  - **Repair.**
    - Make IL-R2 or IL-R4 require that every run record's coverage come from the learner or from an evaluator that is not GND (SWI, clingo, the learner's own `predict`), named in the record.
    - Have IL1 also compare Popper's printed counts with GND's counts.
    - Call the SWI sets "an independent evaluation", not "the learner's claim".

- **R1-F9** (hardening, medium): IL4 admits low-confidence regularities as deontic norms, and leaves the decision until after results.
  - **Claim.** Plan:178-180 admits a mined rule with counterexamples, and IL4-D1 is left open. AMIE's defaults (`minHC` 0.01, PCA-confidence pruning) admit rules with very low standard confidence. As a deontic guarded constraint, such a rule is a norm: it immediately warns on the population it was mined from, which contradicts plan:172, "states what the data does".
  - Two further gaps:
    - **Closed world versus `covers`.** Guarded atom consequents ignore `covers` (`representation-format.md:548-551`), so for a head fact type the population does not declare complete, the "counterexamples" may only be unknowns.
    - **Example ids.** `examples` and `counterexamples` must be opaque or manifest-relative (IK-R11; `induction_example_id`). The plan does not say what an (x, y) pair id is; discover uses first-fact ids (`discover/support.py:91-110`).
  - **Repair.**
    - Decide IL4-D1 in the plan before IL4 results (IK-R12): either discover parity (holds only) or a confidence floor stated as a number.
    - Refuse or flag rules whose head fact type is not in the population's `covers`.
    - Fix pair ids as opaque fact ids, never raw values, with a hostile test.

- **R1-F10** (completeness, medium): Partial admission contradicts IK5's all-or-nothing rule, and nobody decided the change.
  - **Claim.** The current import is all-or-nothing (IK5-D9; `ilp_service.py:15-16`; `ilp-bridge.md:99-100`). Yet the plan says IL3 "maps each admissible conjunct … and refuses every other shape" (plan:47-48), and IL6-C1 / completion item 6 tabulate per adapter "proposed, admitted and refused" (plan:57-60, 290-292). Either IL3 and IL4 silently change the admission rule, or the comparison table's "admitted" column is always all or nothing. IL-R7 says nothing about the change.
  - **Repair.** State in §2 and §0 whether each adapter's import stays all-or-nothing. If any adapter admits a subset, make that a named owner decision with its semantic argument. For a DNF rule set, admitting a subset of disjuncts is sound per disjunct. For an ordered list it is not.

- **R1-F11** (blocking, low): T4 classifies a valid code point as "beyond Unicode".
  - **Claim.** `'\4000000\'` is octal 4000000 = U+100000, a valid scalar (supplementary private use). The first value beyond Unicode is `\4200000\`. As written, T4 forces the parser to refuse a valid code point, or it fails against a correct implementation.
  - **Spec vs source.** Spec:138 vs the same scalar check used for the hex form (`ilp_popper.py:255`, `code > 0x10FFFF`). The surrogate case `\154000\` (U+D800) is correct.
  - **Reproduce.** `int('4000000', 8) == 0x100000`.
  - **Repair.** Use `'\4200000\'` for "beyond Unicode", and add `'\4177777\'` (U+10FFFF) as an accepted boundary case.

- **R1-F12** (completeness, low): IL1 allows an adapter fix after the live run, but IL1-C1 forbids any golden change.
  - **Claim.** Spec:113-116 puts a rendering or parser fix "in scope" after the live Popper run. But IL1-C1 (plan:226-227) and IL-R7 (plan:82) require the Popper rendering and every IK5/IK6 golden to stay byte-identical unless a phase spec names the change and its version bump. A rendering fix decided after seeing results therefore makes C1 unsatisfiable, or turns the change into a post-measurement edit outside IK-R12's amendment path.
  - **Repair.** State that a rendering or wire-affecting fix after the live run requires an owner-recorded amendment naming the changed goldens and the `adapter_version` bump. A parser-only fix that leaves goldens unchanged stays in scope.
