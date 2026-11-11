# GA2 · Discover guarded rules over joined facts

## 2. Provenance

The approved [plan r2](guarded-rule-authoring-plan.md), its
[review disposition](plan-review-disposition.md), [GA1](../003-phase-GA1.md),
and [GR-D10](https://github.com/vasiloglou/gnd-public/issues/181).

## 3. Obligations

| Criterion | Verification |
|---|---|
| B1 | Ordered class pairs, distinct source support, and first omitted candidate at the separate directed cap. |
| B2 | Same-class rule with and without a target marker, independent support and checker binding count. |
| B3 | Stable counterexample row IDs, a miss outside the threshold, coverage and work refusals, evolve preview and unchanged ordinary discovery. |

## 4. Standing rules

Run bounded input admission and role validation before join work. Use
discover's existing typed scalar identity and population-order fact IDs.
Keep discovery and checker results independent and compare both support
and target verdict before admission. Reuse the existing proposal builder.

## 5. Goal

One opt-in discover family emits deontic, induced, proposed guarded rules
and bounded near misses over a covered binary relation and classifier.

## 6. Design

Select `--families guarded-join` with
`--joined-relation FACT:SOURCE:TARGET` and
`--joined-classifier FACT:ENTITY:CLASS`. The relation and classifier
must be distinct, eligible binary fact types. The relation's two roles
and classifier entity role play the same object type. The optional
`--joined-marker FACT:ENTITY:VALUE=JSON` selects a covered binary target
marker for same-class implication. The marker value is a JSON scalar
checked in the selected role's primitive domain. Missing selectors,
malformed coordinates or joined-only options without the family exit 64.

Every relation endpoint must have exactly one typed class identity.
Repeated identical rows count once and preserve the first row ID.
A missing, ambiguous, opaque or uncovered input gives an explicit reason
on `joined_rules` with no joined suggestions. Refuse selected redacted
roles before reading candidate values. Guard literals use JSON-native
non-dollar scalars in the declared class or marker role.

Enumerate ordered pairs over classes present in the classifier, taking
source classes with positive outgoing support. For each pair use
`R(a,b) & C(a,K1) => absence C(b,K2)`. The denominator is the number
of distinct rows leaving K1. For same-class use
`R(a,b) & C(b,k) [ & M(b,literal) ] => C(a,k)`, using every distinct
eligible R row. No candidate with zero support is admitted. Enumerate pairs
by typed identity, with a separate `--max-directed-pairs` limit defaulting
to 256. Keep the existing `--max-pairs` control for unordered set families.
Record checked and omitted pair counts and the first omitted pair's
ordinal. The independent count and checker binding count must agree.
Near misses use the existing predicate and the first 32 violating
relation row IDs. Outside-threshold candidates are counted without a proposal.

A command-wide limit of 1,000,000 joined visits charges rows scanned and
candidate-binding visits. If it is exhausted, refuse the joined family
before emitting any of its candidates. Other requested families retain
their ordinary behavior. `joined_rules` is opt-in report metadata. Use
the existing top-level discovery arrays and evolve proposal for candidates.

## 7. Decisions

| Decision | Contract |
|---|---|
| A | Role coordinates are explicit per invocation and use the existing model vocabulary. |
| B | Complete functional classification is checked before proposal generation. |
| C | Directed and unordered pair limits are separate. Refusals are visible in the report. |

## 8. Gates

Use the [GA2 answer key](../corpus/GA2/expected.json). Run
`pytest -q tests/test_discover_guarded_join.py tests/test_discover.py` and
affected CLI, query, layer and component gates. Run one admitted proposal
through evolve preview. Record the red command before implementation.

## 9. Out of scope

Inferring which relations to join, relaxing functional classification,
general conjunction mining, and accepting an induced rule automatically.

## 10. Size

One joined-candidate module, narrow service/CLI integration, focused
corpus and documentation.

## 11. Approval instrument

Delegated under the [plan gate](../001-plan-gate.md), 2026-11-11.
The selected panel applies to plan and close. Phase diff review follows
implementation. GA1 evidence was checked before opening this gate.
