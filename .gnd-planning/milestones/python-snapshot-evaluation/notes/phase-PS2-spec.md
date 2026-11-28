# PS2 · Return checked derived extensions

## Sources and obligations

The ruled Python evaluation plan sections 0, 2, 4 and 9 and amendment 2 require inferred rows from the same evaluation as findings. Issue #326 supplies an asserted input with no derived claim, a false empty claim and a matching claim. PS1 established report acceptance separately from availability. The incremental-evaluation predecessor shows that cumulative cost and full replay are distinct measurements.

## Interface and boundaries

Add api.check_with_extensions(model, population, *, fact_types, max_rows=1000, unredacted=False). Return the ordinary report and an ordered collection of requested relation results. Limit a request to 64 distinct nonempty IDs, and max_rows to 0–10,000 for all returned rows combined. Reject non-sequences, duplicate IDs and booleans as limits. A known complete empty extension returns status complete and rows []. Without dependency evidence return unavailable and no rows. Unknown and asserted-only targets are unavailable. A protected requested relation emits protected with no rows or cardinality unless ordinary disclosure rules allow raw values. Output-limit consumes no rows from the remaining budget; a later smaller relation can still fit. Row order follows the checker-owned relation. The check report and its claim verdicts retain their original semantics. Input failure still returns a failing report and no computed rows.

## Implementation and verification

Observe the computed relation map already passed from the derivation checker into constraint evaluation. Scope the observation to one call and the checked model and population. Do not calculate again to obtain output. Use the existing dependency-closure walk and redaction policy. Unknown dependency completeness fails closed. Resolve each requested fact using ModelIndex. Bound conversion to public rows before materialization. Exercise the issue example and a renamed reordered model, covered empty, uncovered input, an absent claim, false and true claims, unknown and non-derived heads, protected mode with a low cap, and combined caps. Count real checker and derivation invocations and compare the report to ordinary check. The phase owns API, disclosure reference, component changes, the public export inventory and regressions.
