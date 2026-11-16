# LD2 · Dimension-aware time steps and exact decimal replay

Status: delegated approval recorded in the LD2 spec gate.

## Provenance and obligations

[Plan r3](literature-depth-plan.md) and [LD1 completion](../004-phase-LD1.md)
authorize two quantity axes. LD1 measured that a plain integer anchor
cannot distinguish `2 fs` and `2 eV`. It also measured that the checked
fractional Number `0.002` cannot enter the existing witness fragment.
The independent LD1 review and the corrected installed measurements are
bound in the LD1 record.

| Source | Obligation | Control |
|---|---|---|
| Part 6 quantities, plan §4 LD2 | Admit compatible time spans and refuse a dimension mismatch | T1, T2 |
| Plan §3, §4 LD2 | Represent and independently replay the exact observed decimal time step. Preserve Float and non-integral Number refusal. | T3, T4 |
| Plan §4 LD2 and LD1 conditional scope | Carry the existing difference between percent and percentage points | T5 |
| Plan §§0, 5, 6, 9 | Preserve unrelated anchors, shape and witness wires. Exercise the installed example and affected tests. | T5, T6, T7 |
| LD1 follow-up | Reverify the three competency examples and their decision evidence | T5 |

## Design and standing rules

| Capability | Component search | Decision |
|---|---|---|
| Quantity span recognition | `numeric anchors exact quantity dimension`, `source anchors time span check` | Extend `model.anchors` through the existing recognizer dispatch. Reuse checker occurrence indexing and authenticated sidecars. |
| Exact replay | `certificate replay typed exact decimal`, `witness integer typed target binding` | Reuse the witnessed Integer and String tuple. A narrowly typed fixed-scale time-step fact makes the decimal amount exact and retains the native unsupported branches. |

Add the opt-in selector `time-fs` to the existing meta-schema `recognise`
enum and both schema copies. Model validation admits it on an Integer
role. The checked integer denotes a number of femtoseconds.

The selector admits signed decimal or integer magnitudes under the existing
numeric token grammar followed by horizontal space and a complete unit
token `fs`, `ps` or `ns`. Require a left token boundary and a right
boundary after the unit. Time scales are exactly 0, 3 and 6 decimal places
in femtoseconds. Retain a match only if conversion gives an integral
femtosecond count within the existing sidecar integer bound. The selected
range covers both number and unit. Occurrence indexes count matching
converted quantities in source order. Other numeric recognizers retain
their existing grammar and ranges.

Use one bounded scan per recognizer via the existing index. Parse under
the existing anchor input cap. The scanner bounds working conversion
digits before converting, and uses decimal exponent shifting without
rounding. T2 exercises malformed tokens and scope. T6 checks capped
occurrence retention and a long document. Existing shape and digest
validation still precedes semantic checks.

The packaged worked fact `time_step` has `coefficient` (Integer),
`places` (Integer) and `unit` (String). The anchored constraint applies
to coefficient. The example's value constraints restrict places to 3 and
unit to `ps`. The tuple `(2, 3, "ps")` means the exact decimal
`0.002 ps`. The existing witness binds the full tuple, replay authenticates
it independently, and a mutated scale or unit fails. This encoding applies
to the scoped measurements at whole-femtosecond resolution. The public
choice is made explicit in the worked example. Keep the certificate format
and scalar fragment for native Float and fractional Number.

The constraint reference owns recognition semantics. The example owns the
fixed-scale representation. Record the reasoning for the reopened quantity
axes and avoid claiming measurement precision outside the fixture.

## Decisions

| ID | Delegated disposition |
|---|---|
| D1 | Use an explicit model selector, `time-fs`, for Integer coefficients. Fractions of a femtosecond receive no matching span. |
| D2 | Witness an exact coefficient, scale and unit tuple using the existing witness format. Native Float and fractional Number remain named comparison controls. |
| D3 | Use a corpus-first gate with separate expected outcomes. No optional spec panel. |
| D4 | Limit the scope to the two LD1 findings. Preserve the percentage-point distinction control and the part 10 deferral. |

## Verification selection

| Control in `tests/test_ld2_quantities.py` | Expected result |
|---|---|
| T1 | Public check exits 0 for `2 fs`, `0.002 ps` and `0.000002 ns` independently, verifying whole-token spans and matching occurrences. |
| T2 | A span covering `2 eV`, partial time span, wrong amount or sub-femtosecond value fails the anchored constraint at exit 1. Badly formed, adjacent and out-of-bound tokens fail recognition. Selector on a String role fails validate at exit 3. |
| T3 | Witness and replay exit 0 for the exact tuple. The original source is bound by check and restored as an exact decimal by the tuple. Wrong scale and unit fail model constraints and altered proof cells fail replay. |
| T4 | Float and fractional Number controls check successfully and witness exits 2 with `fragment-unsupported`. |
| T5 | LD1 and existing anchor, witness and schema tests pass. |
| T6 | The time scanner keeps the capped range prefix for each value and completes linearly on a bounded large input. |
| T7 | Fresh installed wheel executes the same public check/witness/replay route over the packaged example. |

Run the direct LD2 tests, LD1 example tests, anchor sidecar and public
semantic boundaries, schema sync, witness compatibility, LX1–LX4 affected
gates, repository structural guards, whole-tree Ruff, and strict component
verification. Broad historical, evidence and census lanes retain their
existing cadence.

## Boundary and size

Time units in the scoped fixture and exact decimal ps results at whole-fs
resolution. Runtime changes stay in the anchor selector and its schema
admission. Estimated 45–80 source lines plus model and documentation,
and 130–190 test lines.

## Approval instrument

Corpus-first. The executable control and separate expected outcomes live
under `tests/test_ld2_quantities.py` and `tests/fixtures/ld2-quantities/`.
A red run must show the distinct unimplemented selector and scoped
witness-route expectations before source changes.

## Implementation findings

The existing sidecar and occurrence index already carry the complete unit
span. The recognizer can use a bounded decimal exponent shift, so schema
admission and the recognizer implement the new semantics without a
checker or certificate format change. The fixed-scale fact uses the
existing anchored and value constraints. Witness and replay authenticate
the coefficient, scale and unit as one tuple. The raw fractional Number
and Float controls continue to check and then return the same refusal.
