# CG1 · Located additions

Ruled by delegated decision, 2026-11-28.

## 2. Provenance

[Plan r1](cross-document-growth-plan.md), §§0–10, based on main 83cd4170 and [#338](https://github.com/vasiloglou/gnd-public/issues/338). Draft dated 2026-11-27. Plan and spec have received no independent review.

## 3. Harvested obligations

| Source | Obligation | Discharge |
|---|---|---|
| Plan §4, CG1 | Append located rows to a locally owned fact under additive preview and apply. Keep prior rows and spans intact and validate the extended population. | Design §6 and acceptance §8 |
| Plan §§0, 6 | Document and check every new sample span against the cited document before CAS. Count duplicate evidence separately from distinct rows. | Boundary cases in §8 and focused regression suite |
| Plan §§5, 9 | Preserve current caller behavior and document the new contract | Reference and compatibility control in §§6, 8 |

## 4. Standing rules as applied

The boundary under test is [src/gnd/evolve/policy.py](../../../../src/gnd/evolve/policy.py). Validate structural inputs before computing a result. Document and check every new sample span against the cited document before CAS. Count duplicate evidence separately from distinct rows. Use one traversal for all supported declarations or bindings. Compare the issue fixture and a differently named or reordered equivalent. The normative reference is [docs/reference/evolve-policy.md](../../../../docs/reference/evolve-policy.md). Record measured work in the fixture wherever a budget affects results.

## 5. Goal

Append located rows to a locally owned fact under additive preview and apply. Keep prior rows and spans intact and validate the extended population. The focused selection exits 0 with every branch below exercised.

## 6. Design proposal

Reuse the existing fact_types.modify operation and its digest-bound before/after values. Compare row and span prefixes, validate new occurrence references and constraints, then use ordinary CAS apply. Identical rows with distinct supporting documents need an explicit provenance ruling.

Reuse the existing components evolve.policy, evolve.population_check, evolve.service, evolve.round_summary and add the contract to [docs/reference/evolve-policy.md](../../../../docs/reference/evolve-policy.md). Implement the change at the defining layer and retain existing public call paths. Baseline control: Existing guidance sends later rows to open questions. The compact inventory identifies vocabulary but omits sample rows. The corpus counts in #338 and #339 come from the reporter.

CG1 changes the fact-type branch of `additive_policy_issues`. The existing `_FACT_TYPE_MODIFY_KEYS` also admits rationale edits. Keep that path. A blanket addition of `sample_population` to its allowed-key set would permit replacement and deletion. Check the old prefix and span-to-row correspondence explicitly. Resolve two new equal tuples from distinct documents under D1 before comparing keys.

## 7. Owner decisions

D1 (delegated). Implement the root-owned append contract and distinct-observation rule in plan amendment §§1–2. Introduce repeatable --sample-document PATH on preview and apply; require explicit workspace-local regular files and bind each to the declared digest. Use the ordinary model population loader and checker on all available sample rows. Only the verdicts for constraints touching an appended fact determine admission. Fail closed on unknown applicability. Preserve raw operation identity and all other policy cells.

## 8. Tests and expected results

Append a located row from document B to a fact introduced by A; preview and apply succeed and both citations resolve. Editing or reordering an old row, omitting its new citation, or violating uniqueness refuses publication. A stale preview leaves the model byte-identical.

Add the new cases in `tests/test_cross_document_growth_phase1.py`. Preserve [tests/test_evolve_additive_policy.py](../../../../tests/test_evolve_additive_policy.py) as an affected-consumer regression. Proposed command after implementation:

```sh
uv run pytest -q tests/test_cross_document_growth_phase1.py tests/test_evolve_additive_policy.py --tb=short
```

Expected pytest exit 0. Compare the old public path on the same unchanged input and record its verdict or emitted bytes.

## 9. Phase boundary

Later phases own candidate discovery, reviewed consolidation loop. Paid grower effectiveness and cross-model alignment remains outside the milestone.

## 10. Size estimate

Estimated 180–320 source lines and 140–250 test lines. Measure the actual diff in the phase record.

## 11. Approval instrument

This draft and its case expectations are the proposed approval instrument. Record an owner decision on the plan and this spec before phase execution.
