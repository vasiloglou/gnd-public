All 20 files the brief names match their SHA-256 values, so I read the intended bytes. The working tree also has an untracked `phase-GC1-r3/` folder that the brief doesn't list (`BRIEF.md`, `FINDINGS.md`, `brief.json`; `review.md` and `review.log` are empty). I left it untouched.

C1 holds. Derived and independent objects now keep their distinctions, and rule bodies stay out of the output. Both defects from r2 are fixed. I found one hardening issue and one test gap, neither blocking.

## 1. Findings

**F1 (hardening): an optional field only appears when the author wrote it, so two models that mean the same thing can give different bytes.**
- **Where:** `src/gnd/model_verbalization.py:605-608` for object types, `:614-616` for fact types.
- **What's wrong:** object `derivation`, `independent` and `storage`, and fact `objectification_independent` and `storage`, are copied only if the source has them. Fact `derivation`, by contrast, is always filled in with `"asserted"` when missing (`:618`). This rule-by-rule difference was added in this round's repair.
- **What you'd see:**
  - The same fixture lists `permanent_employee` with `"derivation":"asserted"` but other asserted objects with no `derivation` key. A host has to know that a missing key means the default.
  - Two equivalent models can give different bytes. That weakens the spec's "bind canonical bytes" rule.
- **Reproduce (run):** on `tests/fixtures/models/full_vocabulary.orm.yaml`:
  - Remove `derivation: asserted` from `permanent_employee`: the bytes change.
  - Add `independent: false` to `employee`: the bytes change.
  - Add `derivation: asserted` to `employee_has_name`: the bytes stay the same.
- **Possible fixes:** fill in defaults for every such field, or omit the default value everywhere, fact `derivation` included.

**F2 (test coverage, style): fact-level fields are never checked against the source.**
- **Where:** `tests/test_growth_projection.py:64`.
- **What's wrong:** the test compares `reference`, `derivation`, `storage` and `independent` exactly for every object row, which fixes the subset-only check r2 reported. Nothing compares fact `derivation`, `storage` or `objectification_independent` with the source. No fixture the test reads uses `objectification_independent`.
- **Consequence:** dropping one of these fields from the fact field list would fail only through the pinned digest, if at all. The test would not say which field was lost.

## 2. Checked and true

- **r2 F1 is fixed (ran).** Changing `contractor_employee` from derived to asserted now changes the bytes. Changing derived to semiderived also changes them.
- **r2 F2 is fixed (ran).** `independent: true` on `employee` changes the bytes. `objectification_independent: true` on the objectified fact in `tests/fixtures/rmap/cases/17-objectification/model.yaml` also changes them.
- **No rule body is disclosed (ran):**
  - Changing `contractor_employee`'s `derivation_rule` text leaves the bytes the same.
  - The key `derivation_rule` and the rule text never appear in the output.
  - Textual `expression` and `formal_expression` are left out. Guarded constraints show only path, fact type and sorted role names.
- **A structured rule without `derivation` can't reach the view (ran).** Dropping `derivation` from a fact with a structured rule (`reaches` in `tests/fixtures/v70-phase2/model.orm.yaml`) is refused at load: "a structured derivation rule requires derivation 'derived' or 'semiderived'".
- **A free-text rule without `derivation` (ran; observation, not a finding):**
  - On objects, `contractor_employee` with `derivation` removed loads and projects with no `derivation` key. Its row looks like any asserted object's, while the default renderer still prints "Derivation rule: …".
  - On facts, it loads without an error. The ordinary renderer says "This fact type is derived", and the view says `"derivation":"asserted"`.
  - The evaluator (`extensions.py`, `diff.py`, `composition_resolution.py`) also reads only the `derivation` field, so treating these as asserted matches how the model is computed.
- **Tests (ran):**
  - `tests/test_growth_projection.py`: 8 passed.
  - `pytest tests -k "successor or layer"`: 281 passed. This covers the new successor-evidence entry.
- **Standing check, code fitted to its examples:**
  - The change adds no regular expression, string split or slice over structured text.
  - The field lists are explicit names checked against the schema's `$defs/object_type` and `$defs/fact_type`, not text matching.
  - `entry['sha256'][:12]` slices a hex digest and was already there.
  - `sorted(atom_bind(atom))` and `_iter_guarded_atoms` are existing helpers.
  - No branch names a fixture literal.
  - Inputs I tried: rule present with `derivation` missing (objects and facts); explicit default vs. missing for `independent`, `derivation` and `objectification_independent`; a changed rule body.

## 3. Not checked

- I didn't run the whole suite or lint, only the projection tests and the successor/layer selection.
- I didn't check whether a fact's `storage` has a default the projection should fill in; the schema doesn't state one.

I kept my probe scripts in `/tmp/gc1r3probe/`, outside the repository, and wrote the review summary to the plan file `~/.claude/plans/review-brief-a-functional-catmull.md`. I didn't change anything in the repository.

VERDICT: APPROVE
