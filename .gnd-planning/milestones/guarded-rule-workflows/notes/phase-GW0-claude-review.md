# Adversarial review: GW0 @ 24c72d86 (base 25ff87e9)

This is one pass over the supplied diff and spec only, with no tools. I treated both as untrusted. Where I could not see surrounding code, the finding says so and names the check that would settle it.

## Findings

**1. Default-route guarded join now reads a different snapshot (E4 preservation).**
- **Symbol:** `correspondence._evaluate_constraint`. The call changed from `_indexed_guarded_bindings(constraint, semantic_snapshot, …)` to `adapted.snapshot`.
- **Why it matters:** This runs on every guarded check, with or without the flag. Nothing in M1 asks for it. If `semantic_snapshot` is an alias-resolved or derived view, atoms on aliased fact types now fail `snapshot_fact_index`. That makes `guarded_valid=False` and changes verdicts on the plain route. If `semantic_snapshot` is still assigned and now unused, Ruff F841 should fail. If it is used elsewhere, the two paths now disagree.
- **Repro:** On the base and head commits, run `tests/test_public_semantic_guarded_join.py` and any guarded fixture that uses alias or subtype fact types. Assert `semantic_snapshot is adapted.snapshot` at the call site.
- **Action:** Revert the argument or justify it with a test.

**2. Antecedent availability is decided ad hoc instead of by the decision path (E1, "unknown → null/null").**
- **Symbol:** `_indexed_guarded_bindings`, specifically `available = … not relation.refusals and (bool(relation.rows) or atom.fact_type in snapshot.covers)`, plus the `_evaluate_constraint` override that only nulls on `constraint.refused == "opaque-value"`.
- **Repro (a):** Use explicit `covers` that omits a populated antecedent relation. The open-world rows are partial, but the report publishes a numeric "exact" count. If the count is 0, it also publishes `first_empty_atom_index`. The spec says omitted coverage gives null/null.
- **Repro (b):** Use any `constraint.refused` code other than `opaque-value` where the join still completes. The verdict is `unchecked` for an antecedent reason, but the count is numeric.
- **Repro (c):** Use default coverage (no `covers` key) with an empty antecedent relation. If `snapshot.covers` is not materialised, this gives null/null instead of the required 0/null.
- **Also check:** the first-atom branch sets `first_empty = 0` unconditionally. If that branch is gated by `not bound_positions` rather than `atom_index == 0`, then a literal-only atom 0 that matches, followed by an empty atom 1, would report index 0.

**3. The v16 rows are attached by position, not by identity.**
- **Symbol:** the `build` closure in `checking_service._run_check_raw`, specifically `zip(payload["verdicts"], report.verdicts, strict=True)` with the guard read from the *report* side.
- **Why it matters:** Suppose `build_check_payload` sorts, filters, redacts or expands rows (for example multi-scope findings, the baseline ratchet, or `--unredacted` differences).
  - If the lengths differ, you get a `ValueError`, i.e. exit 70.
  - If the order differs, `guarded_antecedent` lands on a non-guarded row. That violates the v16 `else: not required` clause, or silently gives one rule another rule's count.
- **Repro:** Use a model whose report order differs from the payload order, e.g. guarded rules interleaved with other families plus a baseline whose findings disappear.
- **Action:** Key by `constraint_ref` and assert the row's own `constraint_type`.

**4. The version-16 schema drops version-15 invariants.**
- **Symbol:** `report.schema.json`, `$defs/verdict_v16` and `$defs/guarded_diagnostics_report`.
- **Why it matters:** Both re-declare only `properties/*` via `$ref`. Any object-level `if/then/allOf` on `verdict_v15` or `rule_ids_report` is not inherited. Examples would be the D-12 rule "reason_code non-null iff unchecked" and outcome/exit_code/baseline couplings. So v16 accepts payloads v15 rejects, and "Validate new schema output" proves less than it claims.
- **Repro:** Take a valid v16 payload, set a pass verdict's `reason_code` to a string, and validate it. Compare with the same mutation at v15.
- **Also:** the diff rewrites every `\u2014` escape to a literal em-dash. That is unrelated churn that changes the schema digest the phase record must pin.

**5. Moving `canonical_scalar` risks check-semantics drift and layer inversion.**
- **Symbols:** `values.canonical_scalar`, the `semantic_adapter.canonical_scalar` alias, and `model._validation._rule_guarded_literal_domain`.
- **Semantics:** The moved body hardcodes `("Integer","Float","Number")` where the original used `semantic_adapter._NUMERIC`. If `_NUMERIC` holds any other primitive (e.g. Decimal or Real), a boolean cell on such a role now canonicalises to a boolean instead of `None`, which changes check verdicts.
- **Layering:** `values.py` is documented as the "shared dependency home". It now imports `semantic_ir` and `input_policy` at module level. Separately, `_validation` reaches `semantic_spec` and `model_queries._resolve_reference` through function-local imports. That pattern usually hides a reverse dependency that the spec forbids.
- **Repro:** Compare `_NUMERIC` with the literal tuple, then run the layer and import-linter gates. Their results are not shown.

**6. The domain lint has false positives and inconsistent exclusion (E3/T5).**
- **Symbol:** `_rule_guarded_literal_domain.excluded`.
- **(a) Ranges ignored when `allowed` is present:** If a non-empty `allowed` list exists, `ranges`/`range` is never consulted. If the model schema admits a mixed enumeration plus range (e.g. `{1,2} ∪ 5..10`), a literal `7` is warned as excluded.
- **(b) Type mismatch treated differently by domain kind:** A boolean literal on an `Integer` role warns under `allowed:[0,1]`. Under `ranges:[{min:0}]` it is silent, because `canonical_scalar(True,"Integer")` returns `None` and therefore "no exclusion". T5's "boolean versus number" can only pass for one of the two forms.
- **Repro:** Run the existing `test_domain_walk_…` fixture twice, once adding `"allowed":[4]` alongside the ranges with literal `5`, and once with literal `true` and ranges only.

## Claims checked (no defect found in the shown code)

- The join adds O(1) state: `first_empty`, `populated`, `available`. There is no second report join. `project_reference_limit` nulls both fields.
- The index is published only when count is 0, in `_evaluate_constraint`. The schema enforces index null whenever count ≠ 0.
- `ConstraintVerdict` fields are `exclude=True`, so no-flag v15 JSON is byte-shape-preserving. The test pops the field and compares against `--rule-ids`.
- The CLI conflict check runs in `handle` before I/O. The API `_run_check` refuses admission and compiled routes.
- `--baseline` and `--allow-vacuous` still pass through when `wire_version == 15`. The v7 refusal path stays v7.
- The lint uses `_iter_guarded_atoms`, is registered last, and skips variables, non-scalars, unresolved roles, malformed bounds and items.
- The memo key is `(domain_ref, identity_kind, token)`. Every domain application, item, range and supertype step is charged. Exhaustion inside `domains_for_type` is caught, emits one work-limit warning, and returns earlier warnings.
- The text renderer reads only payload fields, not its own computation.
- The advisory-rule exemption in `test_every_registered_guarded_error_rule_has_a_rejecting_case` is keyed by rule name.

## Not established by the material

- Focused-gate, Ruff, layer and component-index results.
- Whether `print_vacuous_acceptance` and other readers gate on `schema_version == 15`. If they do, `--allow-vacuous --guarded-diagnostics` text silently drops the acceptance line.
- The T8 stress and timeout test.
- Docs for `rule-check-report.md`, which M4 requires but is absent from the diff.

**REVISE**. Finding 1 becomes BLOCK if `semantic_snapshot` differs from `adapted.snapshot` on any supported model.
