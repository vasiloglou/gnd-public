# FU1 corpus: version-7 derivation reasons (issue 113)

The approval instrument for phase FU1 of rule-check-followups. Answers are in
`expected/answers.json`; the harness is `tests/test_fu1_term_reasons.py`.

## The story

A plain `gnd check` writes report version 7. When a derivation's head term
cannot be computed for a fact (a zero divisor, a negative square root, a
coordinate off the globe), the derivation is `unchecked` and its
`reason_code` names why, e.g. `term:mod-zero`. Version 7's schema only knows
three older reasons, so these reports fail their own schema. FU1 widens the
schema; no report changes.

`models/terms.orm.yaml` has five input fact types, each feeding one derived
fact type whose head uses one term function: `mod`, `div`, `sqrt`,
`haversine`, and a deep `mul` product. Each population fills exactly one
input with one fact.

## CLI cases (each: exit 4, version 7, one unchecked derivation, valid after FU1)

| Case | Input | Why the term fails | Expected reason |
|---|---|---|---|
| mod-zero | `in_mod` a=7, b=0 | `mod(7, 0)` | `term:mod-zero` |
| div-zero | `in_div` a=7, b=0 | `div(7, 0)` | `term:div-zero` |
| sqrt-negative | `in_sqrt` a=-4 | `sqrt(-4)` | `term:sqrt-negative` |
| haversine-coordinate-range | `in_hav` a=91 | latitude 91 is off the globe | `term:haversine-coordinate-range` |
| float-overflow | `in_sqrt` a=10^400 | 10^400 is exact but not a binary64 | `term:float-overflow` |
| exact-value-too-wide | `in_wide` a=b=10^4000 | a^6 exceeds the exact tier's 65,536-bit budget | `term:exact-value-too-wide` |

Today (before FU1) each report is otherwise correct but fails the schema with
one error.

## Schema cases (no CLI route)

Two of version 15's reasons cannot reach a version-7 derivation, measured
while authoring this corpus: `term:dependency-unavailable` (a derivation over
an unchecked derivation reports the original reason instead) and
`derived-unknown` (a constraint reason on the anchored route). The harness
validates a derivation row carrying each of the eight reasons directly
against every schema branch whose reason enum comes from
`derivation_verdict`: `derivation_verdict`, `derivation_verdict_v9`, and the
derivation rows of `legacy_reference_report` and
`temporal_admission_report`. The three older reasons stay valid,
`derivation_verdict_v15` stays valid (non-regression), and an unknown
reason, `term:not-a-reason`, stays refused.
