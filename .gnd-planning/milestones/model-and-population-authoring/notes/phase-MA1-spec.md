# MA1 · Constraint defaults

Awaiting owner review.

## 2. Provenance

[Plan r1](model-and-population-authoring-plan.md), §§0–10, based on main 83cd4170 and [#332](https://github.com/vasiloglou/gnd-public/issues/332). Draft dated 2026-11-27. Plan and spec have received no independent review.

## 3. Harvested obligations

| Source | Obligation | Discharge |
|---|---|---|
| Plan §4, MA1 | Expand opt-in file-level defaults with local precedence and field-origin diagnostics before ordinary model validation. | Design §6 and acceptance §8 |
| Plan §§0, 6 | Route every affected declaration through the same expansion before validation. Preserve file and rule identity across includes and keep regeneration safe for authored extensions. | Boundary cases in §8 and focused regression suite |
| Plan §§5, 9 | Preserve current caller behavior and document the new contract | Reference and compatibility control in §§6, 8 |

## 4. Standing rules as applied

The boundary under test is [src/gnd/model/_parsing.py](../../../../src/gnd/model/_parsing.py). Validate structural inputs before computing a result. Route every affected declaration through the same expansion before validation. Preserve file and rule identity across includes and keep regeneration safe for authored extensions. Use one traversal for all supported declarations or bindings. Compare the issue fixture and a differently named or reordered equivalent. The normative reference is [docs/reference/formats.md](../../../../docs/reference/formats.md). Record measured work in the fixture wherever a budget affects results.

## 5. Goal

Expand opt-in file-level defaults with local precedence and field-origin diagnostics before ordinary model validation. The focused selection exits 0 with every branch below exercised.

## 6. Design proposal

Proposed defaults.constraints accepts source, status and modality. Permit provenance defaults only if each affected rule still has valid attributable evidence. Apply within the declaring file before include composition. An explicit local field wins, including an invalid value which the validator must diagnose. Preserve the author’s original file for diagnostics.

Reuse the existing components model.loading, model.validation, codegen.emit, codegen.manifest and add the contract to [docs/reference/formats.md](../../../../docs/reference/formats.md). Implement the change at the defining layer and retain existing public call paths. Baseline control: The model loader rejects file defaults and omitted readings. Generated constructors accept dictionaries in scalar roles that the checker subsequently rejects.

Use the existing structured model reader. Expand only declared constraint fields at the parse-to-validation boundary; keep raw text and explicit field locations available to errors. Never propagate a default across an include edge. Test inline and top-level constraint forms separately, even when one file uses both.

## 7. Owner decisions

D1 (open). Approve allowed defaults, provenance inheritance and include boundaries. Choose the structured-value wire shape before MA4.

## 8. Tests and expected results

Compare expanded and explicit models by checked facts and verdicts. Verify a local override, invalid override, missing evidence, unknown default key and two included files with conflicting defaults. Existing verbose fixtures retain their results.

Add the new cases in `tests/test_model_and_population_authoring_phase1.py`. Preserve [tests/test_codegen_emit.py](../../../../tests/test_codegen_emit.py) as an affected-consumer regression. Proposed command after implementation:

```sh
uv run pytest -q tests/test_model_and_population_authoring_phase1.py tests/test_codegen_emit.py --tb=short
```

Expected pytest exit 0. Compare the old public path on the same unchanged input and record its verdict or emitted bytes.

## 9. Phase boundary

Later phases own compact readings and clauses, typed populations, structured role values. General YAML alias support and migration of all existing models remains outside the milestone.

## 10. Size estimate

Estimated 160–290 source lines and 120–220 test lines. Measure the actual diff in the phase record.

## 11. Approval instrument

This draft and its case expectations are the proposed approval instrument. Record an owner decision on the plan and this spec before phase execution.
