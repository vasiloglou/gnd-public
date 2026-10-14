Retained reviewer output; edited only to replace any operator home path with <operator-home>. One reviewer is one reviewer. The reviewer disclosed two empty interpreter calls, violating the prompt no-execution instruction; no project code/tests/native execution were claimed.

I found one blocker you can reproduce (entity universes go stale after derivation, which can give false accepts) plus three minor findings. I couldn't refute any of the other claims. Nothing was executed except two empty interpreter calls I ran by mistake (an empty `python3` heredoc and `python3 -c ""`). Neither ran any code.

## Finding 1 (blocker): entity universes are cached before derivation, so computed rows never reach them

**Where:** `src/gnd/export/pyrel_runtime.py:1475-1482`, together with `PyrelOracle.__init__` at `:154-164` and `universe_values` at `:223-247`.

`ApplicationOracle.__init__` empties every derived relation, then calls `super().__init__`. The parent loops over all entity object types and calls `universe_values(oid)`, which stores its result in `_universe_values`. After that, `_derive` sets `self.facts[name] = calculated`, but the cache is never cleared.

The result depends on the object type's kind:
- **Value types** are computed lazily after derivation, so their universes include computed rows.
- **Entity types** are frozen at the asserted-only population.

Three places read the stale cache: `_mandatory` (`:1527`), the mandatory and value vacuity checks (`:1616`, `:1618`), and `_value` through `universe()`. PA1 didn't have this problem because nothing was emptied before construction.

**Consequence:** a mandatory or enum-value check can accept (exit 0) where the expected answer is reject (exit 1). Changing a relation from asserted to derived silently removes its values from the closed-world universe. GND's `_instance_values_of` (`src/gnd/universe.py:343`) scans every fact type in the population.

**Discriminating case.** The model is valid under GND: the join is allowed by `_rule_derivation_term_type`'s ancestor closure.
- Object types:
  - `name` is a String value type.
  - `party` is an entity with reference `name`.
  - `person` is an entity with `subtype_of: [party]` and `inherits_reference: true`.
- Fact types:
  - `seen(who: party)` is asserted.
  - `active(who: person)` is derived and computed: body `[seen{who:$p}]`, head `{who:$p}`.
  - `tagged(who: person)` is asserted, with an inline `mandatory` on `who`.
- Population: `seen=[{who:a}]`, `tagged=[{who:b}]`, `active=[{who:a}]`.

| Run | person universe | Result |
|---|---|---|
| Native, current code | `{b}` (`party` roles don't contribute to `universe(person)`) | satisfied, accepted, exit 0 |
| Expected (also GND) | `{a, b}` | violated, exit 1 |
| Control: same data, `active` declared asserted | `{a, b}` | violated, exit 1 |
| Control: `person` changed to a value type | `{a, b}` | violated, exit 1 |

Swapping the mandatory for `value allowed:['b']` on `person` shows the same split.

The frozen 137-case corpus can't catch this: the BookRec derived heads draw their values from asserted roles of the same entity type.

**Bounded repair:** add `self._universe_values.clear()` after the `_derive` loop. No `_universes` exist yet at that point, and `entity_concepts` is unused on the profile path. Add this case as a native control, then rerun the 137-case gate. This keeps claims isolated, because the universe is rebuilt from computed rows, not claimed ones.

## Minor findings (not blockers)

1. **Typing is looser than GND's.** `_profile_derivations` reuses the PA1 binder, which only checks that primitives match (`:1248-1254`). GND rejects variables that join unrelated object types. `emit.render_pyrel` only calls `admit_model`, so an exported program will compute a rule like `head(who: person) :- book_row(id: $x)`, where both roles are String, even though GND rejects that model. This is within the spec's "typed via PA1 binder" wording, but it is an admitted fragment wider than GND's. That should be stated or narrowed.
2. **`native.json` has no source or tool digest.** I matched it to the current bytes indirectly:
   - Its per-case `program_sha256` values equal those in `native-initial.json`.
   - The runtime was last modified at 16:03:44.
   - The measurement tool was modified at 16:10:13, and `native.txt` was created at 16:13:52.

   That supports crediting it, but it's an inference from timestamps, not a binding.
3. **`check_acceptance` silently skips the computed comparison** when `expected_native_computed` is missing (`tools/measure_pyrel_applications.py:106`). `measure()` always supplies it, so this is only a trap for future callers.

## Claims checked and not refuted

- **Claim isolation:** derived rows are emptied before construction (`:1477`). The forged blocked-claim case computes availability from native rows. Duplicate claims are compared as keyed sets.
- **Order and cycles:** ordering is topological over both positive and negative dependencies, sorted and independent of declaration order. Self-reference and mutual cycles refuse.
- **Grammar:**
  - Literal heads refuse, and so do unbound or wrongly typed heads.
  - An unbound variable in a negated atom refuses.
  - Body is limited to 1–8 atoms and `negate` to 0–8.
  - Rules must use exactly the keys `body`, `head` and optionally `negate`.
  - Version 1, semiderived and stored-derived declarations refuse.
- **Unknown negative or head data with an empty positive body:** coverage and listing are checked in `_profile_admit` before any native import. A known empty extension is accepted.
- **Ceilings:**
  - Derivation work uses `max(1, n)` over the body and negated atoms with computed predecessor counts.
  - The result limit goes through `_rows`.
  - Guarded work is rechecked in `guarded()` against computed counts, and admission skips the check only when a guarded constraint touches a derived relation.
  - Inline uniqueness, mandatory and subset are aggregation or anti-joins, so there is no quadratic blowup even at 10,000 computed rows.
- **Multiplicity:** distinct ordinals make `count(ordinal).per(label)` see both tuples. Collapsing every ordinal to 0 would fail the test.
- **Exit codes:** a refusal in the constructor marks all rows incomplete (exit 2). A native exception gives `runtime_failure` (exit 70). Derivation rows count toward the overall status even when there are no constraints.
- **Accounting:** the completed `native.json` reports 137/137, 2323 native rows, 2321 comparable and 2321 matched. The two listed A1 rows both have GND exit 1. The exit mutant, missing, extra, duplicate and unlisted controls are all present.
  - The computed-tuple formula (claims ∪ missing − extra) is the exact set identity, given that the frozen missing/extra sets are exact.
- **Red evidence:** 19 grammar failures and 1 native refusal, recorded in commit `3bf57ca`.
- **Frozen inputs:** fixtures and PA1 evidence have no diff. Legacy `PyrelOracle` methods are unchanged.
- **Successor chain:** PA2's predecessors are the PA1 files. The query policy shows 359 occurrences against the 365 ceiling, and the original metric is 304 against 310.

## Limitations

- Nothing was executed, so Finding 1 comes from tracing the code; the native case above hasn't been run.
- I didn't verify GND's own exit code on that case.
- The red→green ordering of the computed verifier can't be read from timestamps: both evidence files were created in the same second as the tool edit.
- The four new native tests and the three-way coverage test were written after the implementation, not red-first, which matches what you claimed.
