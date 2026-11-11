# Review of OS2 candidate 337267e8

**Decision: request changes.** The structure is sound. A formula group is placed only after every requirement in it lowers, so partial groups fall back to the sidecar. The `requirements()` refactor reads as behavior-preserving. But I found four issues that should be fixed or disproved before this merges, and several test gaps.

I read only the named patch and ran nothing. Where a finding depends on code outside the diff, I say so. References are diff line numbers.

## Must fix

1. **The pinned-parser test is weaker than it looks** (L560-574).
   - It runs only `oracle.parse`. The neighbouring test runs both `validate` and `parse`. If the pinned JSON schema restricts `requires` or `derived_by` on concepts, relationships or the ontology root, nothing here would catch it.
   - The negative control corrupts only the top-level `document["requires"]`. It proves the parser reads that list. It does not prove the parser reads concept-level `requires`, relationship-level `requires`, or `derived_by`, which is where most placements land.
   - Fix: add `oracle.validate`, and add one corrupted-expression control per scope.

2. **Polarity is not checked in `_comparison` and `_cardinality`** (L171-193, L232-243).
   - `_value_enum` and `_membership` require `req.check.kind == "holds"` or handle `"absent"`. The other two read only `check.compare`. If the shared IR can represent a negated comparison or count, this emits `balance <= 100` for the opposite rule.
   - Fix: assert `kind == "holds"` in both, and add a test.

3. **Uncaught exceptions can crash the export instead of falling back to the sidecar.**
   - `place` and the derivation loop catch only `ExportInputError` and `_Unprojected` (L345, L358).
   - `_derived_chain` does hard lookups: `context.facts[atom.relation]` and `relations[first.relation]` (L275-279). `ProjectedRelation.arguments` uses `zip(strict=True)` (L138). `_value_enum` and `_cardinality` index `components[...]` (L217, L242).
   - If `lower_rule_atom` returns a renamed relation for a derived body atom, such as a `<head>_derived` helper, a derived-on-derived rule raises `KeyError`. I can't see `_atom` in this patch, so confirm that.
   - No test covers derived-on-derived, negated, `where`, aggregate or multi-clause rules. The only derivation variation is `reversed-join`.
   - Fix: convert these lookups to `_Unprojected`, or widen the `except`. Then add the missing cases.

4. **The Ossie path bypasses the shared `requirements()` pipeline** (L433-479 against L482-538).
   - `requirements()` calls `_refuse_unsupported_model(doc)` and post-processes with `_unswapped(model, r)`. `constraint_requirements` and `place_formulas` do neither.
   - Ossie compensates with its own `source_roles` to `projected_roles` remap. Nothing shows the two paths agree on role-reversed facts, or that the refusal guard isn't needed.
   - Fix: add a parity test. For the corpus plus a role-reordered fact, the requirements from `constraint_requirements` should equal those from `requirements()`. If `_refuse_unsupported_model` matters, call it.

## Should fix

5. **Reserved words are matched case-sensitively** (L99-116, L148-151). `count`, `exists`, `or`, `where` and `true` pass `_identifier`. The only test uses upper-case `COUNT`. Either confirm from the spec that keywords are case-sensitive, or fold case. Add a lower-case variation.

6. **Id-less constraints all get the id `"_ossie_rule"`** (L341), and they share one `_Model`. Helper or listing names keyed by constraint id could collide. There is no test with two id-less constraints. Use a unique id, such as the path.

7. **Loss-report fallback can over-claim** (L47-68). Any unmapped child under a `requires` node is reported as `requires`, such as an unknown key like `note` or `x-*`, or extra keys in `derivation_rule`. The test shows `consequent/comparison/right` is retained in the sidecar, so this is probably a labelling problem and not data loss. A reader of the loss report would still think the key was consumed by the formula. Add a test with an unmodelled key. Consider an explicit allowlist of consumed children.

8. **The `plays()` rewrite has no direct test** (L396-414).
   - It now builds a lazy cache from `self._roles`. The old version iterated `self.facts` and `self.roles()`. If `roles()` ever includes helper or derived relations that `_roles` lacks, the results differ.
   - The cache is never invalidated.
   - I'd want an old-versus-new equivalence test on a model with reference widening.
   - There is also a stray third blank line after the function (L415-417) that a linter may flag.

9. **Other test gaps.**
   - Guarded with `>=` or `<`.
   - A non-Integer value type.
   - A `True` right operand.
   - Non-irreflexive ring variants.
   - Binary subset, equality and exclusion.
   - Duplicate identical constraints, which would append duplicate `requires` entries.
   - A constraint with `status` omitted. It is currently refused silently (L309), which is conservative but a coverage gap.

## Minor notes

- `_SAFE_STRING` (L117) allows U+0085 and U+2028/2029. Consider rejecting them.
- `listing` rows are dropped before the "complete group" check (L247). Confirm that dropping them loses no meaning.
- Tests depend on `.gnd-planning/.../evidence/OS2/corpus-r2` (L599). Confirm that directory ships in CI and release checkouts.
- The 4.0 s wall-clock bound (L752) can be flaky on loaded CI. It also exercises only value constraints, not derivation or ring scaling, and times `_ontology` but not `_metadata`.
- `ossie.py` now imports `pyrel_rules` at module level. Confirm that module needs no optional PyRel dependency, since the project positions PyRel as optional.
- The docstring edit at L485 (`` ``model`` `` to `` `model` ``) is unrelated churn.

## What looks good

- Placement is all-or-nothing, and every `_supported_shape` gate fails closed.
- The `requirements()` refactor keeps the same branch order and the same error messages.
- `type(...) is int` correctly excludes booleans.
- Provenance and metadata keys are explicitly kept as `extension`.
- The corpus is pinned by a manifest hash and a hand-authored expected file, so the main test is not circular.

Re-review after items 1-4 are addressed or shown not to apply. I'd then confirm 5-8 against the surrounding code.
