# GC4 review: PR #196, `f446f350` against `be8df4d5`

**Scope reviewed.** I read only what you supplied: the GC4 plan text (E1–E3, the retail cases, the design rules and the verification list) and the diff for these files:

- `docs/bookrec/08-guarded-rules.md`
- `docs/reference/cli.md`
- `docs/reference/rule-check-report.md`
- `src/gnd/export/emit.py`
- `src/gnd/export/ossie.py`
- `src/gnd/export/pyrel_rules.py`
- `src/gnd/ossie-loss-report.schema.json`
- `src/gnd/terms.py`
- `tests/test_guarded_clause_exports.py`

I ran nothing. Line numbers are taken from the hunk headers and are approximate.

---

### 1. The coverage gate stops the whole program and may exempt the wrong relation kind (high, report divergence)

**Where:**
- `src/gnd/export/pyrel_rules.py:1422` (`_FILTERED_COVERAGE`)
- `src/gnd/export/pyrel_rules.py:346` (`needs_coverage`)

**Problem.**
- The injected check raises a `ValueError` for the whole program as soon as any filtered rule's negated relation is uncovered. Every other rule's verdicts are lost. A rule whose positive antecedent is empty, which the core would report as vacuous, now yields exit 3.
- The predicate `not in model.derived or derivation != "semiderived"` requires coverage for asserted and fully derived relations, but exempts semiderived ones.
  - A semiderived relation has an asserted part, so absence of a row only means something under closed-world coverage.
  - This looks inverted relative to the core's rule ("A negative filter over a claimed relation requires declared coverage").

**Repro ideas.**
- (a) Use the `filters` fixture with `expense_in_category: []`, `expense_has_status` uncovered, and a second unrelated rule. Compare `gnd check` with the translated program. Today the test at about `tests/test_guarded_clause_exports.py:150` asserts the translated exit 3 but never asserts the core outcome for that population.
- (b) Negate a semiderived fact type, leave it uncovered, and assert some rows. Compare the core verdict with the translated one.

**Minimal repair.**
- Compute the coverage shortfall per rule inside the report loop, and only when that rule has surviving positive bindings. Emit the same per-rule band the core uses for unresolved bindings.
- Derive `needs_coverage` from the core checker's own coverage predicate instead of restating it.
- Add the core-side assertion to the existing test.

### 2. The filtered rewrite assumes the guard requirement is `found[0]` (high, possible mistranslation)

**Where:** `src/gnd/export/pyrel_rules.py:345–353`

**Problem.**
- The context shows `found.insert(0, Requirement(..., part="bindings", listing=True, ...))` on some branch. Its condition is not in the supplied hunk; it receives `refs`, so it may be the reference/authority-bound path that E1 requires.
- When that branch fires, `guard = found[0]` is the listing, not the requirement. The rebuilt list then turns the real check into `listing=True` with `Check("none")`, so the rule can never violate.
- The rewrite also discards any `found[1:]` entries.
- The original `bindings` listing, which feeds `vacuous_when`, never receives the filters.

**Repro idea.** Take a filtered guarded rule that satisfies the insert branch's condition, such as an authority-bound model with references, and the 2500/no-status population. The core reports `fail`; the translation should print `violated`.

**Minimal repair.**
- Select the requirement with `next(r for r in found if not r.listing)`.
- Replace that entry in place and keep every other entry.
- Apply `filters` to any existing `bindings` listing as well.
- Add an authority-bound case to the parametrized native test.

### 3. The template patches use unchecked `str.replace` (medium, template hazard)

**Where:**
- `src/gnd/export/pyrel_rules.py:2590–2595`
- `src/gnd/export/pyrel_rules.py:1414–1428`

**Problem.**
- The vacuity patch keys on the literal marker `"        status = 'violated' if rule['modality'] == 'alethic' else 'warning'"`.
- The coverage patch keys on `"    return document\n"` and is applied to every block in `out`, for both targets.
- If either marker drifts, through indentation, rewording or an f-string change, the patch silently does nothing. Filtered rules would then report `OK` where the core says vacuous, or apply closed-world negation without coverage.
- `"    return document\n"` can also match more than one block, or a block where `covers` is not in scope. That includes the LQP target, where no vacuity patch is applied.
- The injected code also relies on the names `name`, `found`, `vacuous`, `covers` and `RULES` existing in the template.

**Repro idea.**
- Re-indent `_DUCKDB_MAIN` by one level and render the `filters` fixture. The output still builds, but the 500-amount case no longer prints `vacuous`.
- Separately, count the marker occurrences in the LQP output.

**Minimal repair.**
- Add explicit hook points to `_DUCKDB_MAIN`/`_LQP_MAIN` and to the loader, for example `# @GUARDED_FILTER_VACUITY@`.
- Assert `text.count(marker) == 1` before substituting, and raise `ExportInputError` otherwise.
- Gate the coverage patch on the target as deliberately as the vacuity patch.

### 4. Helper names are checked against raw labels, not emitted identifiers (medium, naming hazard)

**Where:**
- `src/gnd/export/pyrel_rules.py:257–259` (`_membership_check`)
- the labels at lines 300, 343 and 1358
- `src/gnd/export/pyrel_rules.py:1186–1187`

**Problem.**
- The collision check compares labels such as `{id}_membership`, `{id}_where_membership_{n}` and `{head}_membership_{p}_{f}` against `model.facts`, `derived_relations` and `helpers`. The emitted identifier, however, comes from `names.relation(...)`, which sanitizes (the module imports `re`/`keyword`).
- Two labels that differ only before sanitization, such as constraint IDs `a-b` and `a_b`, both pass the check. If they map to one identifier, their literal sets merge and membership becomes a union of both lists.
- Conversely, a legitimate fact type named `policy_limit_membership` causes a refusal of an unrelated rule `policy_limit`.
- Registration is not idempotent: any second lowering of the same clause raises a spurious collision.
- An empty list renders `m.define(*[])`, which leaves the relation undefined.

**Repro ideas.**
- Two membership constraints with IDs `x-y` and `x_y` and different lists. Grep the generated source for duplicate helper identifiers, then run a value that is in only one list.
- A model containing `$a in []` together with `not in []`.

**Minimal repair.**
- Check the collision on the sanitized identifier, against the full emitted namespace, and include the `_derived` and helper suffixes.
- Key helpers by `(label, literals)` so a repeat lowering reuses the existing helper.
- Either refuse empty lists with a named reason or emit the empty-relation declaration explicitly.

### 5. The derivation-membership detector is a second, shallower walker (medium, refusal coverage / design rule 4)

**Where:**
- `src/gnd/terms.py:489` (`derivation_uses_membership`)
- its consumers at `emit.py:38`, `ossie.py:427` and `pyrel_rules.py:2420`

**Problem.**
- At `be8df4d5`, `render` used `iter_derivation_clauses`, the canonical traversal. The new helper walks only the root `where` and one level of `clauses`.
- Any derivation shape that the canonical walker reaches but this helper does not would now pass the embedded runtime and Ossie without refusal, and pass the plan gate. Examples include nested clauses and alternative rule containers.
- Separately, Ossie indexes constraints from the raw `document["constraints"]` but indexes fact types from `ModelIndex.iter_fact_types_shared()`. The `/fact_types/{i}/derivation_rule` pointers are only correct if those two orders and sets coincide.

**Repro ideas.**
- Find a derivation fixture where `iter_derivation_clauses` yields more clauses than `rule["clauses"]`, and put `in` only in the deeper clause. At `be8df4d5` the readable export was refused; check whether `render_pyrel` and `render_ossie --strict` still refuse at `f446f350`.
- For the pointer issue, use a model whose index order differs from document order.

**Minimal repair.**
- Implement the detector as `any(where_uses_membership(c.get("where")) for c in iter_derivation_clauses(rule))`.
- Enumerate Ossie fact types from the same document list that produces the pointers.

### 6. Legacy ordering change and evidence that cannot be reproduced from the supplied material (medium)

**Where:**
- `src/gnd/export/emit.py:34–45`
- `tests/test_guarded_clause_exports.py:72–83` and about line 117

**Problems.**
- **Error precedence changed.** `admit_model` now runs before `uses_temporal`. A temporal model that `admit_model` rejects now gets a different error than `"PyRel export does not support temporal models in Phase 1"`. That contradicts both "outputs of legacy models stay byte-identical" and design rule 3.
- **Plan refusals renamed.** Plan models that previously refused with `membership-unsupported` now refuse with `guarded-clauses-plan-unsupported` (`pyrel_rules.py:2425`).
- **Narrow byte pin.** The byte-stability test pins one embedded fixture and one GC base model by hash. Nothing shows the hashes were computed at `be8df4d5`, and that is not "an unchanged export corpus."
- **Native tests can silently skip.** Every native test calls `pytest.skip` when `GND_PYREL_PYTHON` is unset and never asserts the PyRel 1.30.1 / DuckDB 1.5.5 versions. An all-skip run looks green.
- **Missing artifacts.** The supplied diff contains no E3 wheel-smoke script or receipts. It also contains no E2 cross-links from the constraint reference, the verbalization reference or the packaged authoring guides, and no `representation-format.md` changes.

**Repro ideas.**
- Run `render_pyrel` on a temporal fixture at both commits and diff the messages.
- Run the GC4 file without the environment variable and count skips.

**Minimal repair.**
- Run `uses_temporal` before `admit_model`.
- Keep the old reason for membership-only plans, or document the rename.
- Generate the pins by a script at `be8df4d5` over the whole export corpus, and commit the manifest.
- Under a `GND_REQUIRE_NATIVE=1` flag, fail instead of skip, and assert both runtime versions in the subprocess.
- Attach the E3 script and receipts and the E2 link edits to the review packet.

---

## Limitations

- **Templates and core checker not visible.** I could not see `_DUCKDB_MAIN`/`_LQP_MAIN`, `_atom`, `_atom_types`, `_typed_term`, `_Names`, the condition guarding `found.insert(0, …)`, or the core checker's coverage and unresolved semantics. Findings 1, 2 and 4 therefore depend on those definitions and should be confirmed against them.
- **Routes and artifacts not reviewed.** The Lean and Soufflé routes, the retail smoke, the receipts and the representation-format home were not in the material. E1's Lean/Soufflé clause and E3 are unverified.
- **Positive check (inferred from the diff, not run).** The polarity of `in` and `not in` in both the consequent and filter positions looks correct. The filter-atom threading through `_unswapped` also looks correct.
