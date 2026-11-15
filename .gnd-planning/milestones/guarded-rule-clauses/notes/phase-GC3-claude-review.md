# GC3 review: 20172ace vs 84120554

This is a static review of the supplied diff and GC3 spec only. I ran nothing and did not open any repository file outside the diff.

## Findings, ordered by severity

### 1. High: the reference and the indexed evaluator use different cost models for the "shared" ceiling, so `verdict_of` disagrees with the public verdict at modest sizes

**Where:** `semantic_spec._reference_guarded_disjunction` compared with `correspondence._indexed_guarded_disjunction`, `_indexed_guarded_verdict` and `_indexed_guarded_exists_verdict`.

**Problem:**
- **Atom and absence alternatives, reference side.** The reference charges `len(relations[atom.fact_type].rows)` for every binding, which costs O(bindings × rows).
- **Same alternatives, indexed side.** The indexed path charges `1 + len(row)` once per row while it builds the index, plus `1 + len(bindings)`. That is O(rows + bindings).
- **Exists alternatives.** The reference rescans every relation for each binding and charges `nodes + operations` for each `where` comparison. The indexed path adds `result.nodes` and `result.operations` only to `counts`, not to `budget`.
- **Comparison alternatives.** The indexed path never charges per-binding term work to the budget.

**Repro:** Use the population from `test_indexed_disjunction_handles_wide_consequent`, or any population with N ≈ 450 expenses, each `travel`, `1500` and `review`, with `any_of: [LOW, atom review]`. Pass it through `_check_and_reference`.
- Reference cost is about N·(2+N) ≈ 203k, which exceeds 200k. Result: `unchecked / guarded-disjunction-work-limit`.
- Indexed cost is about 5N ≈ 2.3k. Result: `pass`.
- No current test compares the two above about 20 bindings.

**Minimal repair:**
- Define one cost function in `semantic_spec`: rows prepared once per alternative, one unit per (binding, alternative) evaluation, and term nodes plus operations. Both paths should call it.
- In the reference, build one set or index per atom alternative instead of charging a scan per binding.
- Add parity tests just below and just above the threshold.

### 2. High/Medium: the temporal sub-ceiling is cumulative across all bindings and alternatives, and it sits outside the shared work total

**Where:** `semantic_spec.GuardedDisjunctionBudget.comparison_state` and `guarded_exists_comparison`. The new `terms.compare_terms(temporal_work=…)` passes the same list everywhere.

**Problem:**
- `temporal_work` is a single list for the whole disjunction, checked against a hard-coded `10_000`.
- I assume `evaluate_term` treats the list as a running counter, which is what passing a shared list implies. Under that assumption, a temporal comparison alternative stops at roughly 10k cumulative temporal operations across all bindings. The 200k shared ceiling is never reached for this work.
- A single-form consequent with the same comparison has no such cap across bindings.
- Temporal work is never added to `budget.work`, so this is not one shared ceiling as Standing rule 2 requires.

**Repro:** Scale `test_temporal_comparison_alternative` to about 10–20k bindings, each with a `Date` amount for which `date_add` holds.
- With `any_of` the result is expected to be `unchecked / guarded-disjunction-work-limit`, even though alternative 0 is true for every binding.
- The same comparison as a plain consequent gives `pass`.

**Minimal repair:**
- Charge the temporal delta of each call to `budget.charge`.
- Give each evaluation a fresh temporal counter with the single-form limit.
- Import the limit constant from `terms` instead of repeating `10_000`.

### 3. Medium: the opt-in v17 rendering zips `offending_facts` with `guarded_alternatives` using `strict=True`, but nothing makes their lengths match

**Where:** `checking_service._run_check_raw`. The tuples are built in `correspondence._indexed_guarded_disjunction` and carried through `project_finding`.

**Problem:**
- `diagnostics` is aligned with `_canonical_rows(witness)`.
- `offending_facts` comes from projection. Any truncation, deduplication or redaction-driven reshaping there would make the strict zip raise `ValueError` and crash `--guarded-diagnostics`.
- Alternatively, a matching length with a different order would attach the wrong details to a binding.
- The diff gives the projection layer no guarantee to align the two.

**Repro:** Create a violating `any_of` with more failing bindings than any witness or offending-facts cap, or with bindings that project to equal dicts. Run `check --guarded-diagnostics --format json`.

**Minimal repair:**
- In `project_finding`, carry each binding's diagnostics together with its witness row, so the same cap and order apply to both.
- At render time, key on binding identity instead of relying on a positional strict zip.

### 4. Medium: validation totality regression in `_iter_guarded_consequent_terms`

**Where:** `model/_validation.py::_iter_guarded_consequent_terms`.

**Problem:**
- The old `isinstance(bind, dict)` guard is gone. The code now calls `atom_bind(atom).items()` directly.
- A malformed or non-`bind` atom raises `AttributeError` during semantic validation instead of producing a named refusal. This affects single-form models too, not only `any_of`, if semantic rules can see such atoms.
- When called on a whole constraint that contains `any_of`, the helper silently skips the alternatives' `atom`/`absence` binds. It handles only top-level kinds and comparisons.

**Repro:** Use a guarded consequent `{"atom": {"fact_type": "x", "bind": ["$e"]}}`, or the same shape inside `any_of[0]`, and run `validate`.

**Minimal repair:**
- Restore the `isinstance(bind, dict)` check.
- Iterate through `_guarded_alternatives`, so a caller that passes the whole constraint still sees every alternative.

### 5. Medium/Low: the synthesis disjunction path bypasses the single-form shape guard, and the A4 evidence never checks generated cases

**Where:** `synth/guarded_cases._disjunction_pair` and `build_pair`.

**Problem:**
- `build_pair` returns `unsupported-shape` for comparisons that have function or temporal sides. `_disjunction_pair` sends those comparisons straight to `_assignment` and `prepare_comparisons`.
- Only `SearchLimit` and `UnsupportedShape` are caught there, so other errors can escape `synth`, or the result can be unsound.
- `test_mixed_disjunction_synthesizes_and_verbalizes` checks only the verdicts the manifest declares about itself. The spec (A4) requires running `check` on both manifest cases.
- Without that check, a generated `fail` case whose atom or exists relations are not covered would come out as `unchecked`, and nothing would notice.

**Repro:** Run `synth --guarded-cases` on the model from `test_temporal_comparison_alternative`. Separately, run `check` on the `fail` case that the mixed test generates.

**Minimal repair:**
- Apply the same function-term guard to each alternative.
- Add a test that checks both emitted cases and asserts `fail`/`pass` with `binding_count > 0`.

### 6. Low: alternative scoping duplicates antecedent-level diagnostics in `_rule_temporal_language`

**Where:** the per-scope loop in `_rule_temporal_language`.

**Problem:**
- `observed` is rebuilt for each alternative from antecedent, negate and local atoms together.
- An antecedent-only Duration/other-primitive conflict is therefore reported once per alternative, at `…consequent.any_of[i]`, instead of once at the constraint path.
- This breaks the identity part of Standing rule 3 for `any_of` models.

**Repro:** Bind `$d` to a Duration role and a Date role in the antecedent, with three alternatives. The expected result is three issues instead of one.

**Minimal repair:**
- Check the antecedent and negate atoms once, at `path`.
- For each alternative, emit only conflicts that involve that alternative's local atoms.

## What I checked

- **Unknown and witness precedence.** Inside an exists alternative, an undefined candidate takes precedence over a witness: the indexed `antecedent_undefined` flag and the reference `unknown` flag agree. At the binding level the order is true, then unknown, then false (`guarded_disjunction_state`). At the constraint level, unknown takes precedence over fail in both paths. Work-limit takes precedence over everything.
- **Per-binding state alignment.** States line up with bindings in `_indexed_guarded_disjunction`, and unavailable alternatives become `[-1] * n`.
- **Availability and coverage.** I checked `guarded_alternative_available` and how missing-atom diagnostics are built from antecedent-shared keys.
- **Report compatibility.** The default report keeps its field set because the field is excluded. The version is 16 or 17 depending on whether the model has `any_of`, and `_declared_from_payload` accepts 17.
- **Lexical scopes.** Validation scopes are applied through `_iter_guarded_scopes`, including keys for literal-domain sites, paths for grounding issues, and per-alternative primitives in both the adapter and synthesis.
- **Other parts of the diff.** I also read the CNL composition, the exporter refusals, `universe._family_implemented_guarded`, and the updated tests against the spec.

## Limitations

1. **Non-Python files were not supplied.** I could not see `report.schema.json`, the representation-format and rule-check-report docs, or the model schema. A1's checks on nesting and arity, and v17 schema acceptance, are unverified.
2. **Diff context hides some bodies.**
   - In `_indexed_guarded_exists_verdict`: whether the `where` loop short-circuits on a false comparison. If it does, it would disagree with the reference, which evaluates every comparison, on false-then-undefined cases. I also could not see any `continue` before `states.append`.
   - The tail of `_indexed_guarded_verdict`.
   - Whether `verbalize.guarded_message` accepts the `"any_of"` kind.
3. **Possible missing imports.** `lean.py` and `pyrel_rules.py` use `ModelIndex`, but the diff adds no import for it. Only `souffle.py` gains one. Lint (F821) or the exporter test would show whether this is a `NameError`.
4. **Behaviour I inferred instead of read.** These depend on code outside the diff:
   - Finding 2 depends on how `terms.evaluate_term` accounts temporal work.
   - Finding 3 depends on whether projection caps or reshapes the offending facts.
5. **Not verifiable from the diff.** The validation rule registry order (Standing rule 3), the full issue #171 exporter list, and other readers of `schema_version`.
6. **Minor items that did not make the six.**
   - `unchecked_reason_of` returns `guarded-disjunction-undecidable` before any more specific reason. Separately, the undecidable message says "unavailable alternative" even when the cause is an undefined term such as `mod` by zero.
   - Text output prints each binding as a Python dict repr.
   - No test in this diff asserts v16 for an unchanged model under `--guarded-diagnostics`.
