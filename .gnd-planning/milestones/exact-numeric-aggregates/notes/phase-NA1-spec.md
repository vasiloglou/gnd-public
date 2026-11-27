# NA1 · Explicit count domains

Awaiting owner review.

## 2. Provenance

[Plan r1](exact-numeric-aggregates-plan.md), §§0–10, based on main 83cd4170 and [#336](https://github.com/vasiloglou/gnd-public/issues/336). Draft dated 2026-11-27. Plan and spec have received no independent review.

## 3. Harvested obligations

| Source | Obligation | Discharge |
|---|---|---|
| Plan §4, NA1 | Evaluate count over a declared finite catalog of groups including members with zero contributions. | Design §6 and acceptance §8 |
| Plan §§0, 6 | Bound cardinality and numeric bit growth separately. Never parse exact decimals through binary64 or turn uncovered input into a zero. | Boundary cases in §8 and focused regression suite |
| Plan §§5, 9 | Preserve current caller behavior and document the new contract | Reference and compatibility control in §§6, 8 |

## 4. Standing rules as applied

The boundary under test is [src/gnd/extensions.py](../../../../src/gnd/extensions.py). Validate structural inputs before computing a result. Bound cardinality and numeric bit growth separately. Never parse exact decimals through binary64 or turn uncovered input into a zero. Use one traversal for all supported declarations or bindings. Compare the issue fixture and a differently named or reordered equivalent. The normative reference is [docs/reference/formats.md](../../../../docs/reference/formats.md). Record measured work in the fixture wherever a budget affects results.

## 5. Goal

Evaluate count over a declared finite catalog of groups including members with zero contributions. The focused selection exits 0 with every branch below exercised.

## 6. Design proposal

Propose aggregate.domain as a positive catalog atom binding precisely the group variables. Validate binding and type agreement first. Resolve coverage and enumerate distinct domain keys, then accumulate ordinary contributions per key. A covered domain member with no contributions yields integer zero. Leave the existing aggregate path intact when domain is absent.

Reuse the existing components checker.evaluate, model.validation and add the contract to [docs/reference/formats.md](../../../../docs/reference/formats.md). Implement the change at the defining layer and retain existing public call paths. Baseline control: An explicit zero count fails on a catalog member with no readings. Float sum is refused, and two distinct decimal tokens in the issue fixture collapse under Number identity.

Extend analysis and schema validation alongside `_aggregate_bindings` in `extensions.py`. Enumerate catalog keys separately from matching contribution rows. Use the existing aggregate identity policy for grouping; preserve wildcard/coverage handling before filling any group with zero. Pin a legal second key type, duplicate catalog keys and a member outside the catalog.

## 7. Owner decisions

D1 (open). Approve domain syntax and treatment of contributing keys absent from the catalog (proposed exclusion). Before NA2 choose exact wire encodings and conversion/rounding rules.

## 8. Tests and expected results

Two catalog members with zero and two contributions yield counts 0 and 2. Duplicate catalog rows do not create extra groups. A covered-empty domain yields no rows; uncovered inputs remain unavailable. Legacy models without a domain reproduce the current empty-extension result.

Add the new cases in `tests/test_exact_numeric_aggregates_phase1.py`. Preserve [tests/test_derivation_rule.py](../../../../tests/test_derivation_rule.py) as an affected-consumer regression. Proposed command after implementation:

```sh
uv run pytest -q tests/test_exact_numeric_aggregates_phase1.py tests/test_derivation_rule.py --tb=short
```

Expected pytest exit 0. Compare the old public path on the same unchanged input and record its verdict or emitted bytes.

## 9. Phase boundary

Later phases own exact scalar identity, non-integer aggregates. Changing legacy Number arithmetic or existing certificate scope remains outside the milestone.

## 10. Size estimate

Estimated 130–250 source lines and 100–210 test lines. Measure the actual diff in the phase record.

## 11. Approval instrument

This draft and its case expectations are the proposed approval instrument. Record an owner decision on the plan and this spec before phase execution.
