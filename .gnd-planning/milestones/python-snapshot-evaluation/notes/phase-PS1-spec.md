# PS1 · Interpret snapshot reports

Awaiting owner review.

## 2. Provenance

[Plan r1](python-snapshot-evaluation-plan.md), §§0–10, based on main 83cd4170 and [#333](https://github.com/vasiloglou/gnd-public/issues/333), [#331](https://github.com/vasiloglou/gnd-public/issues/331). Draft dated 2026-11-27. Plan and spec have received no independent review.

## 3. Harvested obligations

| Source | Obligation | Discharge |
|---|---|---|
| Plan §4, PS1 | Normalize the supported snapshot envelopes and expose the CLI vacuity acceptance option to Python. Document inventory-grounded participation with empty and missing coverage. | Design §6 and acceptance §8 |
| Plan §§0, 6 | Preserve redaction and per-target limits across envelopes, including malformed input. A failure before evaluation must never look like an empty successful check. | Boundary cases in §8 and focused regression suite |
| Plan §§5, 9 | Preserve current caller behavior and document the new contract | Reference and compatibility control in §§6, 8 |

## 4. Standing rules as applied

The boundary under test is [src/gnd/api.py](../../../../src/gnd/api.py). Validate structural inputs before computing a result. Preserve redaction and per-target limits across envelopes, including malformed input. A failure before evaluation must never look like an empty successful check. Use one traversal for all supported declarations or bindings. Compare the issue fixture and a differently named or reordered equivalent. The normative reference is [docs/reference/python-api.md](../../../../docs/reference/python-api.md). Record measured work in the fixture wherever a budget affects results.

## 5. Goal

Normalize the supported snapshot envelopes and expose the CLI vacuity acceptance option to Python. Document inventory-grounded participation with empty and missing coverage. The focused selection exits 0 with every branch below exercised.

## 6. Design proposal

Proposed api.snapshot_verdict(report) returns run status, exit code, constraints, derivations, warnings and diagnostics. Dispatch on the declared schema, read the appropriate inner report and account for outer failures first. Propose allow_vacuous=False as a keyword-only argument to api.check; preserve the individual verdict and raw envelope.

Reuse the existing components cli.api, check.service, checker.reports, witness.service and add the contract to [docs/reference/python-api.md](../../../../docs/reference/python-api.md). Implement the change at the defining layer and retain existing public call paths. Baseline control: The issue fixtures exercise raw schemas 7, 12 and 14. A missing population exits 3 with zero failed constraints. A two-target why-not request is refused. The dependency metadata pins Pydantic 2.13.4.

Keep `api.check` additive at the signature boundary. Propagate the new keyword to the same acceptance-band computation the CLI uses. Include the helper in the public export inventory. For a supported wrapped report, read inner verdicts and preserve outer diagnostics. If the input has no recognized schema, expose unknown-schema status even when its exit code is 0. Test admission and reference wrappers independently.

## 7. Owner decisions

D1 (open). Approve the accessor name, response fields and unsupported-schema status. Decide the supported worker transport and dependency test matrix before PS4.

## 8. Tests and expected results

For the #333 fixtures read plain and both wrapped reports, preserve each failure and detect a missing file even with zero fail counts. Unknown schemas return unsupported. On #331 the default remains vacuous exit 2 and opt-in exits 0; the grounded inventory still fails on missing outcomes.

Add the new cases in `tests/test_python_snapshot_evaluation_phase1.py`. Preserve [tests/test_public_api.py](../../../../tests/test_public_api.py) as an affected-consumer regression. Proposed command after implementation:

```sh
uv run pytest -q tests/test_python_snapshot_evaluation_phase1.py tests/test_public_api.py --tb=short
```

Expected pytest exit 0. Compare the old public path on the same unchanged input and record its verdict or emitted bytes.

## 9. Phase boundary

Later phases own return computed extensions, explain a batch, embed or isolate the evaluator. Hosted network service and broad dependency upgrades remains outside the milestone.

## 10. Size estimate

Estimated 160–300 source lines and 130–240 test lines. Measure the actual diff in the phase record.

## 11. Approval instrument

This draft and its case expectations are the proposed approval instrument. Record an owner decision on the plan and this spec before phase execution.

## Delegated PS1 decision, 2026-11-28

Approve snapshot_verdict(report) returning status, exit_code, constraints, derivations, warnings and diagnostics. A recognized outer evaluation failure can always be distinguished from ambiguous empty results. Reject malformed structures without including arbitrary input in diagnostics. Restrict customer access to already-issued results through a value-free projection or refusal if raw rows may be present. The existing check entry point gains allow_vacuous=False at the end of its keyword options. Reject incompatible modes before evaluation and preserve the default report. Exercise zero counts on a missing input, accepted vacuity, mixed failures, unsupported wire versions and inconsistent wrappers. Show requested inventory as the antecedent of a grounded mandatory check.
