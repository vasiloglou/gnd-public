## Decision: approve with required changes

The scope, role-binding, supported-shape and all-or-extension logic held up. I could not refute any of them from the source. I found one concrete defect (R1) and several shapes the renderer accepts but no reviewed case covers (R2–R5). The independent implementation-diff review is not yet closed.

## Required changes

**R1. Defect: unmodelled constraint keys are labeled `requires/formula`.**
- `_METADATA` is `{id, modality, source, status, provenance, rationale, remedy}` (`ossie_formulas.py:43`).
- `constraint_common` also allows `owner` and `allowed_fixes` (`orm-meta.schema.json:1167-1186`).
- `_metadata.visit` gives any unmapped child of a `requires` row the fallback `("requires","formula")` (`ossie.py:388-403`, `visit(..., disposition == "requires")`).
- So `/constraints/N/owner` and `/constraints/N/allowed_fixes[/k]` are reported as carried by the formula. They are not, so the loss report over-claims.
- Repro: add `"owner":"host","allowed_fixes":["add-fact"]` to `balance_ceiling` in the r2 corpus model and render. Expected `extension`; the code gives `requires`.
- Fix: map these keys to `extension` (or derive the set from the schema) and add the case to `test_ossie_formulas.py`.

**R2. Reserved-word guard is case-sensitive, and fact ids and role names are always lowercase.**
- `_RESERVED` is uppercase only (`ossie_formulas.py:21-38`).
- Fact ids, role names and the identifier pattern are `^[a-z][a-z0-9_]*$` (`orm-meta.schema.json:246-249`).
- So `_identifier` can never reject a role or fact named `count`, `min`, `max`, `sum`, `or`, `not`, `exists`, `true`, `false`. Those spellings feed `token(1)`, `path()` and the derivation chain.
- Nothing I could read shows whether the pinned lexer matches keywords case-insensitively. The only reserved-name test uses concept name `COUNT`.
- Repro: rename `balance` to `count` in the corpus guard (role and formula) and run it through `oracle.parse`. Same for a fact id such as `exists` used by a subset.
- Fix: probe the pinned parser. Either extend the guard or add a reviewed case.

**R3. Derivation chain accepts multiple clauses, but only a single clause was reviewed.**
- `_derived_chain` loops over `normalize_derivation_clauses` and emits one `derived_by` entry per clause (`ossie_formulas.py:192-220`).
- The meaning of a multi-element `derived_by` (union or something else) is not in the corpus. All 11 derivation cases use one clause.
- Repro: give `account_band` `clauses:[c1,c2]`, each a valid two-atom chain. The renderer emits two expressions, which no reviewed case covers.
- Fix: restrict to one clause, or add a reviewed multi-clause case.

**R4. All formula-bearing corpus players are String value types, but the code does not require that.**
- `Account` is `kind: value` in the corpus.
- `_cardinality`, `_membership` and the derivation do not check player kind or subtype status. Value and guard shapes do check the primitive.
- Entity players, subtype players and supertypes of subtypes are therefore accepted for `COUNT[X]`, `Owner.rel`, `NOT EXISTS(...)` and derived chains. GND's universe and instance counting for those cases is unreviewed.
- Repro: make `account` an entity with a reference mode, or give it `subtype_of`, then render the cardinality and subset cases.
- Fix: restrict to the reviewed kinds, or extend the corpus and replay.

**R5. Test gaps.**
- All-or-extension for equality is not actually tested.
  - In `binary-membership` (`test_ossie_formulas.py:132-137`), both directions fail, so a per-direction implementation would also pass.
  - A test needs exactly one direction to fail, for example one fact id that `_identifier` rejects, since `path()` checks only the right side.
  - Atomicity is correct in code (`_placements` builds lists, and `place` mutates only after the list completes).
- Role permutation is not tested for any formula shape. The `ManyToOne` reorder (`ossie.py:119-135`) can make the owner the second declared role. The code binds by role name (`ProjectedRelation.arguments`, `ossie_formulas.py:59-61`) and looks correct, but no test covers it, including derivation where owner and join can swap.
- The time-bound test (`test_ossie_formulas.py:160-172`) scales only `value`, with an absolute 4s wall-clock bound. Guarded, membership, ring and derivation scaling are unexercised, and there is no structural check.
- `constraint_context` and `constraint_requirements` have no direct tests. They are exercised only through Ossie and the parity manifest.

## Checked claims

Checked by reading the source and records. I ran nothing.

- **Scope and role binding.**
  - Each placement's scope comes from the projected relation: `relation.target` for guarded, ring, membership and derivation, the concept for value, and the ontology root for cardinality (`ossie_formulas.py:104,134,151,165`).
  - Tokens use the owner concept name for position 0 and the projected role name otherwise.
  - Owner/role-name collisions are refused (`ossie_formulas.py:96,66-67`).
  - `lower_rule_atom` args follow `_Model._roles`, which matches `fact["roles"]` order; role names are validated unique (`_validation.py:578`), so `zip(..., strict=True)` cannot raise.
- **Supported-shape restrictions.**
  - Guarded is one binary antecedent, `<=`, a `type is int` literal, and an Integer value type bound to the second projected role.
  - Ring is irreflexive over one type.
  - Membership is a unary same-player, one-atom domain whose check atom has the same variable.
  - Value is a String enum with a regex-closed string set.
  - Cardinality is object scope, `<=`, a count, and a group of exactly one non-listing requirement.
  - Derivation is a positive, asserted-body, `derived` head, two distinct-variable binary atoms with a join on last-first, head `(x, y)` and type-consistent.
- **All-or-extension.**
  - `place` computes requirements and placements first and mutates `target["requires"]` and `mapped` only afterward.
  - Mixed min/max cardinality falls back (tested). The code also falls back for min-only, 0-bounds and listing-only groups.
- **Dispositions.**
  - They come from one `mapped` table and one `visit` walk, so they are deterministic and one row per pointer.
  - `test_census_export` asserts rows equal the pointer walk and sidecar keys equal the non-refused rows with no duplicates, on all 38 census inputs.
  - R1 is the only mislabel I found.
- **Bounded work.**
  - `_Model` indexes facts, roles and rosters once, and `plays` is cached.
  - There is no per-constraint rescan of the model.
  - A large enum is linear in its size; I did not check how the external parser handles a very long `OR` chain.
- **PyRel compatibility.**
  - `relationalai` imports in `pyrel_runtime.py` are lazy, so Ossie rendering does not require PyRel.
  - `pyrel-observations.json` contains 162 entries, 32 of them refusals, matching the record's 130 + 32.
  - The refusal message text is part of each observation.
- **Parser acceptance vs. semantics.**
  - The pinned parser's acceptance is syntactic: `parser-observations.json` shows exit 0 for the ten authored groups, including the two deliberately divergent ones.
  - Semantic assumptions rest on the hand-authored corpus and the GND-checker replay.
  - The independent reviewer read r1 only (`phase-OS2-corpus-review.md:3`). It worked from an excerpt and said it did not see the parser or `ontology.md`.
  - The r2 shapes were not independently reviewed: record 012 line 45 says so, and record 011 relies on delegated approval.
  - The r2 claim that `COUNT[Account]` at ontology scope counts roster-plus-fact instances rests on a parser fixture that confirms the form is legal. That shows legality, not meaning.

## Limits

- **No diff, no HEAD check.**
  - I could not run git. The worktree's `.git` is a pointer file, so I could not confirm the tree is at `337267e8` or read the `a0c0ac7d..337267e8` diff.
  - I reviewed final-state files only.
  - PyRel behavior preservation rests on the committed parity manifest. I checked its counts but could not recompute or compare SHA-256 `198e4ba5…`, and the baseline-package manifest is not in the repo.
- **No execution.** The "180 passed", "44 passed" and parity-script results are as recorded in 012, not reproduced.
- **Pinned parser and `ontology.md` not read.** I stayed within the named scope, so keyword case rules (R2) and `derived_by` list meaning (R3) are open.
- **Hashes.** I did not recompute the approved spec or manifest SHA-256 values. No test pins `manifest.json` or the spec hash. The test checks only the files listed inside the manifest.
