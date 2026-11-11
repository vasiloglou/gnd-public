# OS2 corpus r1 review (commit 0dd646d3)

This is a paper review of the enclosed artifacts only. I ran nothing, and I did not see the OS1 projection, OS0 E2 evidence, GND checker source, or the parser.

## Verdict

**All 20 hand-derived pass/fail verdicts are correct** under the readings below. The corpus is **not yet approvable as a gate for the renderer**, for two reasons:

- Several cases cannot tell the intended formula from a plausible wrong one.
- Two cases (cardinality, derivation) depend on semantics the enclosed Ossie excerpt does not establish.

## Reconstruction

Overrides replace the whole fact list or roster for that key. Everything else comes from the base population.

| Case | Effective change from base | Result | Notes |
|---|---|---|---|
| guard-fail | balance = {a1:40, a2:120} | a2 > 100, fail ✔ | Also rules out an "exists a link ≤ 100" reading |
| mandatory-fail | balance = {a1} | a2 has no tuple, fail ✔ | a2 is still an Account via flagged and recommends |
| frequency-fail | balance = {a1:10,20,30} | a1 has 3 links, fail ✔ | a2 also loses its balance, so mandatory breaks too |
| subset-fail | registered = {a2} | a1 not registered, fail ✔ | equality breaks too |
| equality-fail | registered = {a1,a2} | active ⊆ registered holds; registered ⊆ active fails on a2 ✔ | The failing direction is formula index 1, scope index 1 |
| exclusion-fail | flagged = {a1} | a1 in both, fail ✔ | Pass case rules out the global negation reading (a2 is flagged, a1 is not) |
| ring-fail | recommends = {a1→a1} | fail ✔ | |
| value-fail | classified = {a1:Wholesale} | Category population is {Wholesale, Retail}, fail ✔ | Retail is still present via category_band, so this rules out "some value allowed". Derivation also breaks. |
| cardinality-fail | roster = {a1,a2,a3} | 3 > 2, fail ✔ | Only if a roster-only a3 counts as an Account (see C1) |
| derivation-fail | account_band = {a1:premium} | derived is {a1:ordinary}, premium has no witness ✔ | |

All `-pass` cases use the unmodified base, where every rule holds.

## Changes needed before implementation

**C1. cardinality-pass / cardinality-fail (semantic).**
- The expected scope is `ontology`, but the enclosed Ossie excerpt only defines `requires` on a concept or a relationship. Either cite the pinned ontology-level hook or move cardinality to the sidecar.
- If it were placed on concept `Account`, `COUNT[Account]` would collide with the bound variable. That is the same spelling frequency uses with `Account` bound per owner.
- In cardinality-fail, a3 appears in no fact. Ossie links are the only population the excerpt describes, so a roster-only object is invisible to it. Give a3 a balance tuple. This also avoids the collateral mandatory violation. Label any roster-only variant GND-only.

**C2. frequency-pass / frequency-fail (counting scope).**
- Neither case separates per-owner counting from a global link count. Base has 2 links total against a bound of 2, and the fail case fails under both readings.
- Add a pass case with a1:{10,20} and a2:{30}, so the global count is 3 but each owner has at most 2.
- Add a boundary case at exactly 2 per owner.
- Fix frequency-fail to keep a2's balance so that only frequency breaks.
- Bounds with `min > 0` need a decision. GND's frequency is vacuous for an account with no tuples, but a concept-scoped per-owner count is not. Restrict lowering to max-only, or add a case.

**C3. derivation-pass / derivation-fail (derived join).**
- The fail case cannot detect a missing join. `premium` has no source row under any reading, so a cross product of the two relationships would still fail it.
- Add category_band (Business→premium) to the fail population, keeping a1 classified as Retail with a1:premium asserted. The correct join fails; an unjoined product passes.
- Add cases for a missing derived link (account_band = {}), a multi-row join, and an empty join.
- State the verdict definition. Ossie derived links are constructed, not asserted, so "fail" means a GND comparison of asserted against derived. The current reason covers only the unwitnessed direction, but a1:ordinary is also missing there. Pin whether the check is equality or soundness only.
- Restrict lowering to a chain whose join is the last role of atom 1 and the first role of atom 2. The head must be (atom 1 first role, atom 2 last role). Anything else goes to the sidecar, or gets cases for atom order and role order.

**C4. value-pass (coverage).**
- No pass case contains `Business`. `Category == 'Retail'` alone would match every expected verdict. Add a case with Business populated.
- Only strings are tested, so restrict lowering to strings or add integer cases.

**C5. guard-* (coverage).**
- Only `<=` against an integer literal is tested.
- Add a boundary case at exactly 100.
- Restrict lowering to that operator and literal shape, or add cases for each operator, variable-versus-variable comparisons, and string literals.

**C6. subset, equality and exclusion (coverage).**
- Only unary single-role cases exist. Binary role sequences with a swapped order are a classic error.
- Restrict to unary, or add a binary case with swapped order.
- The ring and mandatory restrictions are already implied by the candidate table. State them as fallback rules.

**C7. Role-name dependencies (semantic, bound to OS1).**
- Ossie variables default to the concept name. The formulas use `balance`, `recommended` and `(band)`, which need explicit emitted role names. The first role, `Account`, is correct by default.
- Add a gate that the formula identifiers equal the emitted role names. `(band)` would otherwise be `Band` and mismatch case-sensitively.

**C8. expected.json (format).**
- `formulas[i]` pairs with `scopes[i]` only by position. Make it explicit as `{scope, formula}` pairs, as equality needs. Give per-direction verdicts for equality.
- Four failing cases break a second rule: frequency-fail, subset-fail, value-fail and cardinality-fail. Either isolate them or declare that the replay compares only the named rule.
- Add fallback cases, since OS2-C4 expects rendered and fallback replay. The cases needed are deontic, proposed, a min-frequency or computed operand, and a partial group.

## Syntax versus semantic

**Syntax, deferred to the parser run:**
- `COUNT[...]` brackets and what it counts for a relationship path.
- `EXISTS(...)` and `NOT EXISTS(...)` over a relationship with no unbound role. Subset uses a bare `Account.account_registered`, so exclusion could be `NOT Account.account_flagged`.
- `==`, `!=` and `OR` spellings.
- Single-quote escaping, for example an apostrophe in a value.

**Semantic, resolved above:**
- Counting scope (C1, C2).
- Global versus bound negation (exclusion and mandatory already discriminate).
- Population assumptions (C1).
- The derivation verdict definition and join shape (C3).
- Role-name binding (C7).

The `Account.account_classified.category_band(band)` chain matches the excerpt's `Person.ancestor_of.parent_of(descendant)` pattern, where the last role joins the next first role. The excerpt does not define `COUNT` or `EXISTS` inside `requires`. Those two semantics rest on OS0 E2, which I did not see.
