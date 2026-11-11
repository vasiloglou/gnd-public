# GW2 · Compare rule editions

**Delegated approval (auto=true), 2026-11-11.** The approved corpus and this
specification govern implementation.

## 2. Provenance

[Plan r3](guarded-rule-workflows-plan.md) §§0–6 and 8–10,
[plan gate](../001-plan-gate.md), [GW0 record](../003-phase-GW0.md),
[plan review disposition](plan-review-disposition.md), and
[GR-D9](https://github.com/vasiloglou/gnd-public/issues/180).
The GW0 phase left the edition comparison and combined installed smoke
to GW2.

## 3. Obligations

| Source | Obligation | Discharge |
|---|---|---|
| Plan B1 and #180 | Compare the offending bindings even if both checks fail. Pin 43 base findings, one head finding, 42 removed and one standing, then reverse direction | M1–M3, T1 |
| Plan B2 and round 2 | Pair by declared ID. Show additions, removals, anonymous rules and both modalities. Handle an added guard variable, a rename, rowless failures and collisions | M2, T1–T4 |
| Plan B3 and RC3 | Pin option precedence, ill-formed input, vocabulary mismatch, incomplete results, existing baseline and diff compatibility and work exhaustion | M1–M3, T3–T7 |
| Plan §§5, 8 and 9 | Document the surface, keep live inventories, run focused gates, review and smoke the installed candidate | T6–T8 and phase record |

## 4. Standing rules

1. **Totality belongs to the function, not the caller.** Model admission
   and the capped population loader own malformed inputs. The comparator
   only consumes admitted reports and explicitly handles missing rule
   observations and unknown verdicts (T3/T5).
2. **An input cap bounds the document, not the algorithm.** Bound additional
   comparison work. Build lookups by ID and canonical binding key. Charge
   the rule, antecedent role and witness visits before producing a delta
   (T4).
3. **Validation order is part of the design.** Option conflicts precede
   I/O. Load both models, check vocabulary, capture the population once,
   admit it under both editions, evaluate both, then compare. A refusal
   yields no rule deltas (T3/T5).
4. **A policy governing N element kinds is enforced by one walk over all N.**
   Use one rule pairing loop over both editions and one typed key builder
   (T2).
5. **Normative prose has exactly one home.** The rule-check report reference
   owns the comparison. The CLI help points to it (T7).
6. **Resolve contested representation questions by measurement.** Exercise
   added guard variables, renames, canonical numeric identity and projection
   collisions against the decisive edit (T1/T4).

## 5. Goal

`gnd check HEAD POPULATION --baseline-model BASE` exits 0 for a complete
comparison, even when the base and head check bands are 1. The decisive
control produces 42 base-only findings, one standing finding and no
head-only findings. Invalid input exits 3. Any unavailable rule comparison
or comparison budget exhaustion yields exit 4.

## 6. Design

| Capability | Consult and observed component | Decision |
|---|---|---|
| Same-population admission | Baseline finding/binding and compare models searches. Inspected `check.service`, `check.baseline` and `model.diff` | Reuse capped reads, side-specific validation, version-15 evaluation and the vocabulary digest |
| Binding deltas | Inspected the canonical key in `check.baseline` and guarded witness maps from `check.snapshot_decision` | Adapt baseline comparison utilities in place |
| CLI and report | Inspected `cli.checking_command` and the GW0 report | Adapt CLI dispatch and emit a separate edition comparison payload |

**M1.** The service `compare_rule_editions(head_path: str, population_path:
str, base_path: str) -> tuple[int, dict[str, Any]]` uses the same snapshot
route limitations as version 15. Ordinary population-header and admission
checks apply independently to both editions. The caller can omit an optional
model ID header when one population intentionally spans edition IDs. Model
and population refusals identify the side. Structured rule findings may be
reported when the ordinary rule-ID route supports the model. Derivation
findings remain in the side check band rather than the rule-pair delta.

**M2.** Pair by version-15 declared address. Anonymous rules remain
side-local and have no inferred delta. In a paired comparable rule,
compare only `fail` and `warning` witnesses using the same typed identity as
`--baseline`. A rowless failure is one null finding. Standing results
include both original witnesses. Align guarded witness variables by shared
unambiguous antecedent fact-type/role sites. If the antecedents are identical
use the same variable identities, including repeated fact types. Otherwise
use fact types that occur once on each side. Shared variables must align
one-to-one. Unmatched added variables can be projected away. Any collision
between distinct observed bindings, conflicting mapping or lack of a shared
key marks a rule incomparable and suppresses its delta. A one-sided finding
set can be compared against an independently decided empty set. A paired
family change with findings on both sides is incomparable. An unchecked
side, including an unchanged unchecked rule, yields an incomplete result.

**M3.** The CLI option is exclusive with the old baseline and other
check arms. It writes an informational JSON payload with schema tag
`gnd-rule-edition-comparison/1`, exit, reason, population digest, base and head
paths with side check bands and model digests, and rule rows. Each row has an
address, pairing, two side verdict summaries, nullable reason and nullable
delta. Deltas contain `base_only`, `head_only`, and `standing` arrays. Text
reports the same pairing, counts and directions. Use a 1,000,000-unit
comparison budget on rule, role and witness visits. Exhaustion withholds
the entire delta and returns 4 with an explicit reason.

## 7. Decisions

Delegated approval (auto=true), 2026-11-11. Retain informational exit 0,
exit 3 on a vocabulary mismatch or ill-formed side, exit 4 on any
incomparable rule or budget exhaustion, fail closed on projection
collisions, and preserve the old population baseline route and output.

## 8. Tests

| ID | Expected observation |
|---|---|
| T1 | On one captured population, old/new independent check bands are 1 with 43 and 1 offending rows. Added variable and unambiguous rename preserve the standing finding. Comparison exits 0, also after swap. |
| T2 | Declared IDs survive reorder. Added and removed rules, anonymous rules, warnings and rowless failures retain separate identities. |
| T3 | Unchecked side, including unchanged unchecked rules, and ambiguous projections exit 4. An independently decided vacuous side can produce a complete delta. |
| T4 | Collision with multiple rows for the added variable is incomparable. Canonical typed identity preserves numeric equivalence without confusing booleans. Comparison budget exhaustion exits 4 with no partial delta. |
| T5 | Malformed model on each side, incompatible vocabulary, or malformed population yields exit 3 with the stage and side. CLI conflicts exit 64 before I/O. |
| T6 | Run new direct controls, RC1/RC3/RC4, GW0, report, diff and layer/query guards with the default lane. Existing bytes and bands stay pinned. |
| T7 | Check text and JSON carry the same comparison. Update reference, help and component index. |
| T8 | Install a local candidate outside the checkout, record module origin and exercise the decisive GW0 and GW2 controls. |

## 9. Out of scope

Changes to implication or proof, comparing different vocabularies, new
rules for derivation findings, and automatic acceptance based on the
comparison.

## 10. Size

Estimate 220–340 runtime lines plus 180–260 test lines and docs.

## 11. Approval instrument

The [corpus brief](../corpus/GW2/README.md) and separate
[answer key](../corpus/GW2/expected.json) bind the decisive control.
Implementability was checked against the observed 43-to-1 reproduction
and the version-15 witness map. Optional spec panel was omitted.
