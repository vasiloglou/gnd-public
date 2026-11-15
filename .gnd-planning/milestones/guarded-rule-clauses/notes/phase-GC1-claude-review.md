Claude Code reviewed candidate `62c45016`. The retained response follows verbatim.

# GC1 review at 62c45016

I reviewed the diff only. Nothing was executed, so each finding has a confidence level and a repro to confirm it.

**Scope gap first.** The diff does not touch `gnd/semantic_ir.py`, but `terms.py` imports `MembershipSet` from it and `semantic_adapter` builds `IROperand(..., membership=...)`. The diff also does not touch `gnd/model_verbalization.py`, yet `test_guarded_membership_verbalizes_the_ordered_values` expects "is one of" and "is none of". If neither existed before this commit, the import fails or that test is red. I assumed both exist.

## Findings

**1. Membership left-term errors are lost in derivation `where` and mislabelled in guards.** High confidence.
- **Where:** `_membership_comparison_issues` sets `rule_id=left.issue`, which is a raw `analyze_term` reason, not a `semantic:*` ID.
- **Derivation `where`:** issues only surface through `_filter_derivation_term_issues`. `_rule_derivation_membership` keeps only `membership-list` and `membership-duplicate`, so a bad left term reaches no filter and the model validates clean.
- **Guarded sites:** the same issue appears under the guarded-comparison-type rule with a non-catalog ID, alongside whatever `_rule_guarded_term_ref` already reports.
- **Repro:** derivation `where: [{operator: in, left: {fn: add, args: ["$e"]}, right: [1]}]` (wrong arity). Do the same with an unbound `$zzz`. Expect no error.
- **Fix:** map left-term failures to the same semantic IDs the legacy branch uses.

**2. Derivation filters take the left operand's type from the list, not the declared type.** Medium-high confidence.
- **Where:** in `compare_terms`, a variable left with no `left_primitive` gets `primitive = members.domain`. All three `extensions.py` call sites pass no `left_primitive`.
- **Why it matters:** the guarded path decodes by scalar kind, and the exists path uses `left.primitive`. Validation also skips the incompatibility check whenever `membership_domain(left.primitive)` is `None` (unresolved or unmapped primitives).
- **Effect:** the derivation path can say "member" where the guarded path says "undecidable".
- **Repro:** a variable whose primitive does not resolve to String, Date or Number, compared with `in [{"date": "2024-02-29"}]`, with the runtime value `"2024-02-29"`. The derivation path matches it because it is treated as Date. The guarded direct path returns -1.
- **Fix:** thread the declared primitive into `prepare_comparisons` or `compare_terms`, and reject a `None` domain statically.

**3. The reference spec now uses the production membership code, so the correspondence check cannot catch membership bugs.** High confidence; this is a design defect.
- **Where:** `semantic_spec.guarded_comparison_state` calls `gnd.terms.membership_verdict`.
- **Same helper everywhere:** `_membership_key` and `membership_verdict` also back the temporal guard, the correspondence exists path and the derivation filters.
- **Effect:** a bug in key normalisation, such as numeric exactness or Boolean/number separation, passes every spec-vs-runtime check. The only independent oracle is the derived-helper test, which uses integers only.
- **Fix:** give the spec its own small membership decision and keep the production one separate.

**4. Synthesis puts raw list members in as candidate values, and its proofs are narrow.** Medium confidence.
- **Raw members:** `_assignment` uses `members[1:ATTEMPTS]` unnormalised. That means tagged `{"date": …}` or `{"duration_days": …}` dicts, or `1500.0` in an Integer role. A dict value then looks like a member: the dict branch of `_membership_key` returns a Date key, so the in-memory outcome disagrees with what the emitted population would check to.
- **Exists rows:** `_outcome` returns `None` when any row is undecidable, even if another row already proves existence.
- **Boolean proof:** it only runs for `kind == "comparison"`, so an exists clause over a Boolean domain never gets the named one-sided reason.
- **Test gap:** `test_synth_membership_*` never feeds the generated cases back through `check` to confirm one fails and one passes.

**5. Soufflé does not refuse guarded membership, and the Lean and Soufflé refusals are untested.** Medium confidence.
- **Soufflé:** `souffle.admit` only checks clause `where`. Unlike Lean and PyRel it never calls `guard_uses_membership`, so if it admits guarded comparisons, `in` passes through. An aggregate `where` with membership is refused as "scalar filters" rather than with a membership reason.
- **Tests:** only `pyrel_rules` has a refusal test.
- **PyRel ordering:** its check now runs before `_bind_reference`, against the inline comment. A model with a broken reference now reports `membership-unsupported` instead of the reference error.

**6. Some work is not counted, and the timing test can be flaky.** Medium confidence.
- **Compile cost hidden:** `prepare_comparisons` runs inside the evaluation loops in `_evaluate_stratified_extensions` and `_exact_extension_calculator`. A prepared list then reports `operations == 1`, so up to 1024 compile steps per pass are never counted.
- **Per-binding analysis:** `compare_terms` calls `analyze_term(left, {})` for every binding when the left side is a function term, and that is also uncounted.
- **Perf test:** `test_membership_precompiles_for_many_bindings` only covers a variable left with a set compiled once, and asserts against wall-clock time (`< 5.0`), which can flake on slow CI.
- **Fix:** compile once per clause and charge the cost, and resolve the left primitive once.

## Claims covered

| Claim | Status |
|---|---|
| Static empty, over-cap, variable, nested and mixed lists are invalid; Boolean list vs Number left is invalid | Covered (CLI, guarded direct only) |
| Static validation at exists and derivation sites | Admission only; no invalid cases there |
| `in`/`not in` verdicts for direct and exists guards | Covered (integers) |
| `1` = `1.0`; Boolean, plain text, tagged date and duration are distinct | Unit-level (`compare_terms`); not through guard or spec paths |
| Non-integral numeric identity (e.g. `0.1`) | **Not covered** on any path |
| Unavailable or incompatible terms are undecidable | Unit-level only; no check-level undecidable verdict |
| Legacy equality (`True = 1`) kept | Covered |
| Date and Duration membership, including `date_add` | Covered for `in`/pass only |
| Derivation `where` membership | `in` pass only; no `not in`, no failing population |
| Synthesis gives both cases; Boolean one-sided reason | Direct only; cases not re-checked (finding 4) |
| Unsupported exports refuse | PyRel only (finding 5) |
| Work bounds | Partial (finding 6) |
| Duplicate and outside-domain warnings at member paths | Covered (guarded direct) |
