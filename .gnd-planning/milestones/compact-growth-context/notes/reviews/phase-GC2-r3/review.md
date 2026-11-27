The repair closes the reproduced defect: once the composed vocabulary changes, the growth API stops reusing the old positional attribution. But it breaks one loader path that used to work, so changes are requested.

All 15 files named in the brief match their SHA-256 values. I only wrote my plan-mode notes file; nothing in the repository was touched.

## 1. Findings

**F1 — `src/gnd/model/__init__.py:371`: the new load-time digest crashes some composed loads that used to succeed.**
- **What is wrong:** `model._composed_vocabulary_digest = _composed_model_digest(model)` now runs on every composed load. If the model has `reference_populations`, `model_digest` goes through `reference_model_digest`, then `artifacts.canonical_json_bytes`. That function refuses non-finite floats. The loader itself accepts them: a free-form field holding `.nan` passes validation, and the same model without reference populations loads and renders.
- **What someone would see:** loading a composed root with reference populations and a `.nan` in a free-form field now fails with an uncaught `ValueError: Out of range float values are not JSON compliant: nan`. It is not a `ModelValidationError`. It happens with both `bind_references=False` (the `gnd judgments check --reference-root` route) and `bind_references=True`. It hits every composed load, not just the growth view. Before 0b0fa734, the next line (372) simply returned the model.
- **How to reproduce (in memory, no files written):** take `src/gnd/examples/seeded_growth/root.orm.yaml` and make three changes:
  - change `source` to `{kind: text-conversation, mode: one-shot, note: .nan}`;
  - append `reference_populations: [{id: links, path: x.pop.json, sha256: "<64 zeros>", fact_types: [work_has_version]}]`;
  - call `load_model_bytes_composed(bytes, source=..., root=<seeded_growth dir>, bind_references=False)`.

  The traceback runs through `__init__.py:371` → `values.py:192` → `values.py:226` → `artifacts.py:205`. Without `reference_populations` the same input loads, and the growth view renders 497 characters.
- **Suggested fix:** bind provenance with a digest that accepts every value the loader accepts, such as the `repr(model_dump)` form the non-reference path already uses. Alternatively, compute the digest only in the growth route and turn a failure into the existing `include:unresolved` refusal.

## 2. What I checked and found true

C1 holds on every case I tried:
- **In-place change:** editing an included row's reading on a loaded composed model is refused with `include:unresolved`. Reverting the edit restores the identical 497-character output.
- **Edits outside the view:** changing a constraint `rationale`, which the growth view never shows, is also refused. That is stricter than needed but consistent with the new doc line ("must be reloaded").
- **Copies:**
  - `model_copy(deep=True)` and `copy.deepcopy` carry the digest. They render unchanged and refuse once mutated, and mutating a copy does not affect the original.
  - `model_copy(update=...)` is refused.
  - Re-validating through `model_validate(model_dump())` drops the private attributes, so it is refused as before.
- **Row order:** the non-reference digest (`repr(model_dump(...))`) keeps list order, and so does the reference path's `_canonical`. Reordering or swapping rows therefore changes the digest, so positional origins cannot be reused (I confirmed this by reading the code).
- **Excluded field:** `operations` is left out of the digest, but `_includes.py:223` forbids operations inside includes, so they never carry included positions. Appending an operation skips the digest check, but re-validation still catches an invalid one (observed).
- **Other loader paths:** the digest is set only in the composed branch of `_load_model_at`, which is the only place that sets `_provenance`/`_included` (checked with grep). Flat loads skip the guard: digest `None`, no includes. The analysis `CompositionView` path also gets the digest.
- **Changed test:** `test_loaded_growth_model_refuses_invalid_role_player` moving from `root` to `seed` is intended: a mutated composed model is now refused before its role players are checked.
- **Test run:** `tests/test_growth_view.py` passes, 5/5.
- **Code fitted to its examples:** the diff adds no regular expression, string split, slice or literal-name branch. The new guard `model.includes or model._included or digest is not None` is structural. I tried it with flat, composed, copied and re-validated models, as listed above, and found no input it gets wrong.

## 3. What I could not check

- I did not check out the pre-repair commit and run F1 against it, because the review is read-only. The "used to load" claim comes from the traceback: everything before line 371 ran, and line 372 is a plain return.
- I did not build a two-row fixture with a real swap. The claim that order changes the digest comes from reading `repr` and `_canonical`.
- I did not look at whether NaN-bearing reference models also fail later in other tools that compute `reference_model_digest`.

VERDICT: CHANGES_REQUESTED
