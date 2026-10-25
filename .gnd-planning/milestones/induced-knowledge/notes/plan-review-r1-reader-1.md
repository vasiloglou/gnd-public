# Reader 1 — semantics and admission safety

Reviewed plan SHA-256 `26fa91632e5ee637b1949ad4e8dd6ba25daac57180280328e3d04c1e050a1814`
and IK1 spec SHA-256 `f79d6375630e8706a9a3fe88af7669b3f0a81fcbb446ec0e1d55d4df22b8cec0`
— both match.

**Verdict: request-changes** within the semantics/admission-safety lens.

Scope: full plan and IK1 spec, AGENTS.md, issue #34; `evolve/service.py`
(`_enforce_d12` 222–259, `_surface_index`, `preview` 1096–1170, operations gate),
orm-meta schema defs, provenance-and-modality.md (D-03), representation-format.md
(derived fact types, guarded), `measure/truth.py`, `measure/score.py`,
`synth/provenance.py` `ExpectedState`, `checker/_core.py` vacuity tables,
`checker/_reports.py` `band`, `diff.py` `_implies`. No tests run.

## Findings

- **R1-F1** (blocking, high): Imported derivation rules bypass admission. Plan
  141–143, 198 (IK5-C2) vs 56 (IK-R1). `_enforce_d12` (service.py:222–259) inspects
  only `_constraints()` (203–208); a `derivation_rule` lives on fact/object types and
  the schema gives it no source/status/modality. `has_alethic_fail`
  (_reports.py:110–113) counts any derivation `fail` as alethic (band 1). An ILP
  clause imported as a structured `derivation_rule` passes `evolve preview` with no
  proposed/deontic gate and acts immediately as a hard-fail obligation. Reproduce: a
  proposal adding a fact type with a structured `derivation_rule` is never seen by
  D-12. Fix: restrict IK5 output to `guarded` constraints, or extend the gate and
  modality story to derivation rules.
- **R1-F2** (blocking, high): "Exit 0" does not prove a candidate holds. Plan 35–36
  and IK4-C1 (190); candidates are deontic (131–132). A violated deontic constraint
  is `warning` and `band()` (_reports.py:140–165) returns 0 for warnings; an
  empty-subject candidate is `vacuous` (exit 2). The soundness predicate accepts
  violated candidates and does not exclude zero-support ones. Fix: per-constraint
  verdict `pass` and support > 0.
- **R1-F3** (blocking, medium): Entailment suppression is undefined. Plan 135–136,
  IK4-C4 (193). The only catalogue, `diff.py` `_implies` (72–129), returns
  `different-modality` whenever modalities differ, so a declared alethic constraint
  never suppresses its deontic copy; it has no frequency or equality rule and nothing
  cross-family (equality ⇒ subset; frequency max 1 ≡ uniqueness; unscoped value ⇒
  role-scoped value; reference scheme ⇒ uniqueness). Frequency candidates have no
  canonical form; min 1 is trivially true over occurring groups (_core.py:867–872);
  spanning uniqueness is trivially true. Suppression counts and emitted candidates
  depend on unstated choices.
- **R1-F4** (hardening, medium): Per-fact-type discovery cannot decide mandatory or
  cross-fact set comparisons (plan 61, 130). The checker is closed-world over the
  whole object-type universe — every role of T plus `instances[T]`
  (_core.py:13–15, 820–840). A mandatory candidate judged inside one fact type can be
  emitted and then fail `gnd check`; subset/equality/exclusion across fact types
  need joins (`_JOIN_SUBJECT_SEQS`, _core.py:882–918).
- **R1-F5** (blocking, medium): IK3 reuses a truth table answering a different
  question. Plan 121–126, IK3-C2 (185), 149–150. `classify` needs
  `ExpectedState{ground_truth, expected_verdict}` (provenance.py:121–144) where
  `ground_truth` is the constraint's own state including `no-subjects`; a host class
  ("wrong plan") says whether the answer is wrong, not whether this constraint is
  violated. A correct plan where the rule has no subjects is `vacuous` → `undecided`
  if labelled satisfied; mapping classes to `no-subjects` makes the host compute GND
  evidence (contra IK-R2); inconsistent mappings raise `InconsistentExpectationError`
  (score.py:262–269). `resolve_constraint_ref` refuses `derivation:` refs
  (truth.py:88–97), so IK3 cannot score an IK5 `derivation_rule` although the plan
  says IK5 coverage reuses IK3 (149–150).
- **R1-F6** (blocking, medium): Coverage equality is insufficient for faithfulness.
  Plan 143, 199, 233. Agreement on the training examples is necessary, not
  sufficient; GND semantics that can diverge while agreeing on examples: only
  non-empty aggregate groups (no zero counts); aggregate dedup by `(over, of)`;
  stratified negation-as-failure; ground absence consequents
  (representation-format.md:685); closed-world rosters; typing (booleans never
  numeric); guarded constraints vacuous when any antecedent is empty. The polarity
  mapping (learned `wrong(P) :- body` ⇒ constraint "not body") and how a vacuous GND
  verdict counts against "not covered" are undefined. Needed: a declared
  clause-to-GND fragment with per-construct semantics and refusal outside it.
- **R1-F7** (hardening, medium): No defined path to confirm induced knowledge (plan
  15, 56). The `user-supplied` branch (service.py:243–247) accepts any modality and
  provenance, so confirming means relabelling to `user-supplied`, losing the
  `induced` marker IK2-C3 relies on; any proposal author can do this and no owner is
  recorded. Define `induced`+`confirmed` (e.g. with `reviewed_in`, as `imported`
  does) or refuse `provenance.induction` under other sources.
- **R1-F8** (completeness, low): Plan 132 "(or `sample`, per D2/D3)" contradicts D2
  (286) and the sweep (272), which keep `sample` refused; IK4-C2 ("IK2's gate
  admits") fails under that option.

## Reasons

- IK-R1's intent is right and D-12 is sound for constraints (changed constraints
  re-enter D-12, service.py:223–231) but misses derivation rules (F1) and the
  relabel path (F7).
- Soundness and entailment rest on predicates/catalogues that do not exist or do not
  behave as assumed (F2–F4).
- IK3/IK5 scoring and import contracts conflict with truth.py and derivation/guarded
  semantics (F5, F6).
- IK1 raises no admission-safety issue: descriptions are inert and outside the
  checker (spec 105–106); the surface addition is consistent with `_surface_index`.

## Limits

Code reading at `0e2ba79`, nothing reproduced by execution; coverage.py internals
checked only for absence of a provenance view; Popper/ILASP formats not checked;
PR #35 not reviewed.
