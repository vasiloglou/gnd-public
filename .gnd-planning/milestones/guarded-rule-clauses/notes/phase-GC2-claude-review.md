Claude Code reviewed commit `b4e84af4`. The retained response follows verbatim.

# Independent review of GC2 commit `b4e84af4` (patch read as data, no tools)

## Findings

### 1. Structural early returns mark the guard unchecked before any definite exclusion is tried (high)

**Where:** `semantic_spec.guarded_filtered_bindings`, in the `prepared` loop.

**Issue:** The function returns `(), "guarded-filter-coverage-missing"` for the whole guard in two cases:
- `fact is None or relation is None`
- `set(ordered) != {role.name ...}`, meaning the negative atom does not bind every role

Both returns happen before any binding is examined. So a `where` that is definitely false for every binding, or another negative atom that really matches, never gets to exclude anything. That breaks "without a definite exclusion → unchecked."

Validation does not reject a negative atom that binds only some roles. `_rule_guarded_filters` only checks unbound variables and primitive types. So that shape is accepted and then always unchecked, with a misleading "coverage-missing" reason even when the relation is fully covered.

Synthesis disagrees with the checker here. `_outcome` uses `_join(facts, [atom], budget, binding)`, which treats a partial bind as "some matching row exists."

**Repro:**
1. Write a negative atom that binds only `expense` on `expense_has_status`, and add `where: [{"operator": "=", "left": "$a", "right": -1}]`.
2. Cover all relations.
3. Expected: `vacuous`, since `where` excludes every binding. I expect `unchecked` / `guarded-filter-coverage-missing`.
4. Run `synth --guarded-cases` on the same rule without the `where`. The manifest verdicts will not match what `check` returns.

### 2. Adding any filter silently turns off the temporal evaluator (high)

**Where:** `correspondence._evaluate_constraint`, line `temporal = None if filtered_guard else evaluate_temporal_guard(...)`.

**Issue:** A guard with a temporal consequent plus `negate`/`where` goes down the non-temporal path, and nothing refuses it. Meanwhile `_rule_temporal_language` now explicitly allows temporal nodes inside `.where[...]`. Those nodes are evaluated by `guarded_pair_state` → `guarded_operand_value`, which is not the temporal evaluator.

Diagnostics go wrong too. `_family_message_guarded` checks `is_temporal_node` before the filter branch, so filtered temporal guards get the temporal message rather than the definite-survivor count. No test covers this combination.

**Repro:**
1. Take an existing temporal guarded fixture with a decided `pass` or `fail`.
2. Add `where: [{"operator": "=", "left": "$x", "right": "$x"}]`, where `$x` is any antecedent variable.
3. The verdict should not change. I expect `unchecked`.
4. Separately, put a temporal term in `where`. I expect it to be always `guarded-filter-term-unavailable`.

### 3. `computed_available` is only passed through `check_legacy` (medium-high)

**Where:**
- `checker/_core.py` (`check_legacy`)
- `semantic_adapter.adapt_snapshot`, where the default is `frozenset()`
- `semantic_spec.verdict_of`

**Issue:** Every other way of building a snapshot treats semiderived (computed-extension) negative relations as uncovered. The obvious example is the reference path `verdict_of(adapt_snapshot(model, population))`. Without `effective_facts`, that snapshot's rows also lack the calculated rows.

So for semiderived negative relations, the reference and the checker diverge. The seeded equivalence test puts the semiderived helper only on the positive side and calls the reference only on the native model. Semiderived negation is never tested. Nor is "uncovered but really matched excludes": the `(covered=False, claimed=True)` case is missing.

**Repro:**
1. Put a negative atom on a semiderived relation whose calculation is available.
2. Use one binding with no matching row, and one binding matched only by a calculated row.
3. Compare `check(...)` against `verdict_of(c, adapt_snapshot(m, p))`. I expect `pass`/`fail` from `check` and `unchecked` from the reference.

### 4. Synthesis does not guarantee a passing case that excludes a would-be violation (medium)

**Where:** `synth/guarded_cases._pass_with_excluded_binding` and `build_pair`.

**Issue:**
- **Silent fallback.** When the merged candidate does not evaluate to pass, the function returns the original `passing` case with no reason or marker. Causes include:
  - cross-joins between the passing and failing facts
  - colliding IDs that make the added negative rows exclude every binding
- **`where`-only rules.** These never get an exclusion example, because the function returns immediately when `negate` is empty.
- **Discarded check.** `_domains(model, index, negate, ...)` is called and its result thrown away. Negative rows are then written as asserted facts even into fully derived relations, which separately makes the derivation-consistency verdict fail in the "passing" case.
- **Missing work charge.** `confirmation_work` does not charge filter work.
- **Test coverage.** Only seed 19 is tested.

**Repro:**
1. Loop seeds 0–99 on the `_case` model.
2. For each passing case, remove `negate` and re-check it. Some cases should come back `pass` rather than `fail`.
3. Do the same with a `where`-only rule, removing the `where`. I expect no case to flip to `fail`.

### 5. `where` memberships are probably validated twice (medium; confirm)

**Where:**
- `model/_validation.py`: `_iter_guarded_memberships` now includes `.where[...]`
- `_rule_guarded_filters` also calls `_membership_comparison_issues` on the same comparisons

**Issue:** If the existing consumer of `_iter_guarded_memberships` emits membership issues, then each bad `where` membership is reported twice at the same path. Rule order is normative, so this would change the issue list.

**Repro:** Use `where: [{"operator": "in", "left": "$a", "right": ["x", "x"]}]`, with `$a` numeric. Run `validate --format json` and count issues at `.where[0]`.

### 6. Work budget and survivor counts are reported inconsistently (low-medium)

**Where:** `_GUARDED_FILTER_WORK_LIMIT` and `correspondence` (`binding_count = len(guarded_bindings)`).

**Issue:**
- **Flat budget.** The 100k limit covers index building plus `bindings × (1 + |terms|)`. The positive join cap is only enforced when `reference_populations` is present. So adding a trivially true `where` to an unreferenced guard with about 50k bindings turns a decided verdict into `unchecked`, at a size the unfiltered guard handles fine.
- **Counts.** The early return on the work limit or structure (finding 1) reports `binding_count = 0`. The normal unchecked path reports the partial definite-survivor count. The same population therefore gets different counts depending on where the loop stopped.
- **Mislabeled reason.** An unavailable operand inside a negative atom is reported as `coverage-missing`, not `term-unavailable`.
- **Test coverage.** No test asserts diagnostic counts.

**Repro:** Use 50k positive bindings, one negative atom, and `where: $a = $a`. I expect `unchecked` / `guarded-filter-work-limit` with `binding_count` 0. Without the `where`, the guard is decided.

## Claims checked

| Claim | Result |
|---|---|
| Filters consume only positive bindings | Holds. Scopes come from `.antecedent[` only; unbound filter variables raise `guarded-filter-unbound`. |
| A real negative match excludes even when uncovered | Holds (`key in keys` is checked before `covered`). Untested for derived relations. |
| A definitely false comparison excludes, with exclusion beating deferral | Holds within the per-binding loop. Broken by the early returns (finding 1). |
| Unavailable comparison or uncovered negative relation leads to unchecked | Holds. The reason is the first deferred binding's reason. |
| Filter-only emptiness is vacuous; positive-empty keeps legacy vacuity | Holds in both `correspondence` (`vacuous-filter-empty` branch) and `verdict_of`. |
| Negative relations stay out of positive vacuity at runtime | Holds. Not verifiable for validation rules that consume `_iter_guarded_atoms`, which now yields negative atoms; those consumers need an audit. |
| Covered fully derived relation reads its claim; consistency reported separately | Holds per the parametrized test. Semiderived does not hold outside `check_legacy` (finding 3). |
| Diagnostics count definite survivors | Holds on the normal path; inconsistent at the edges (findings 2 and 6). |
| Synth emits active passing and failing cases | Holds: `if not distinct: return None` keeps cases active. The exclusion example is not guaranteed (finding 4). |
| Legacy compatibility | Holds. All new behavior is gated on `negate`/`where`. `if not distinct` cannot fire for legacy rules. `computed_available` is read only by filter code. Unverified: whether `SnapshotIR` is ever serialized or hashed, since a `frozenset` field would break JSON. |
| Unsupported exports | Lean, Soufflé (reason propagated) and PyRel refuse with `guarded-antecedent-filters-unsupported`. Ossie returns `False`, which gives the generic reason. Only PyRel is tested. Exporters outside the diff were not checked. |
| Schema | Both copies are identical; `minItems: 1` makes the truthiness gating and key-presence gating agree. |
