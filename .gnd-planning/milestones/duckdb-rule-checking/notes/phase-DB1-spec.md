# DB1 · Correlated guarded existence

Awaiting owner review.

## 2. Provenance

[Plan r1](duckdb-rule-checking-plan.md), §§0–10, based on main 83cd4170 and [#330](https://github.com/vasiloglou/gnd-public/issues/330). Draft dated 2026-11-27. Plan and spec have received no independent review.

## 3. Harvested obligations

| Source | Obligation | Discharge |
|---|---|---|
| Plan §4, DB1 | Compile a guarded existential over a joint assignment and expose violating antecedent bindings. | Design §6 and acceptance §8 |
| Plan §§0, 6 | Use a read-only engine transaction. Validate relation identifiers and projection types before executing a rule. Bound counterexample rows independently of scan size. | Boundary cases in §8 and focused regression suite |
| Plan §§5, 9 | Preserve current caller behavior and document the new contract | Reference and compatibility control in §§6, 8 |

## 4. Standing rules as applied

The boundary under test is [src/gnd/export/pyrel_rules.py](../../../../src/gnd/export/pyrel_rules.py). Validate structural inputs before computing a result. Use a read-only engine transaction. Validate relation identifiers and projection types before executing a rule. Bound counterexample rows independently of scan size. Use one traversal for all supported declarations or bindings. Compare the issue fixture and a differently named or reordered equivalent. The normative reference is [docs/reference/capabilities.md](../../../../docs/reference/capabilities.md). Record measured work in the fixture wherever a budget affects results.

## 5. Goal

Compile a guarded existential over a joint assignment and expose violating antecedent bindings. The focused selection exits 0 with every branch below exercised.

## 6. Design proposal

Retain gnd export pyrel MODEL --rules duckdb --out FILE. Bind the antecedent once, correlate shared variables into a single existential join, and project antecedent identities for which no joint tuple exists. Apply ordinary coverage checks before computing absence.

Reuse the existing components export.pyrel_rules, check.service, check.constraint_families and add the contract to [docs/reference/capabilities.md](../../../../docs/reference/capabilities.md). Implement the change at the defining layer and retain existing public call paths. Baseline control: The guarded rule fixture passes native checking with an approved outcome and fails with an unrelated one. PyRel export currently refuses an existential consequent. A SQLite cursor is rejected by api.check.

In `export/pyrel_rules.py`, follow the guarded consequent dispatch and rule-block emitter. Reuse its model-derived names and requirement identities. Bind consequent-only variables inside the joined relation. An empty consequent match is a violation only for an applicable, covered antecedent binding. Verify a variable shared by two consequent atoms, as well as one shared with the antecedent.

## 7. Owner decisions

D1 (open). Approve the guarded fragment and native execution environment. DB2 must choose an explicit NULL mapping and transaction identity before accepting relation bindings.

## 8. Tests and expected results

One matching outcome passes; an approved value belonging to another request fails. Two atoms satisfied by distinct values cannot satisfy one shared variable. Covered-empty and uncovered inputs produce the native verdict in each case. Other unsupported consequents retain the existing refusal.

Add the new cases in `tests/test_duckdb_rule_checking_phase1.py`. Preserve [tests/test_pyrel_rules.py](../../../../tests/test_pyrel_rules.py) as an affected-consumer regression. Proposed command after implementation:

```sh
uv run pytest -q tests/test_duckdb_rule_checking_phase1.py tests/test_pyrel_rules.py --tb=short
```

Expected pytest exit 0. Compare the old public path on the same unchanged input and record its verdict or emitted bytes.

## 9. Phase boundary

Later phases own read-only relation bindings, backend parity. Other SQL engines and general SQL compilation remains outside the milestone.

## 10. Size estimate

Estimated 130–260 source lines and 120–230 test lines. Measure the actual diff in the phase record.

## 11. Approval instrument

This draft and its case expectations are the proposed approval instrument. Record an owner decision on the plan and this spec before phase execution.
