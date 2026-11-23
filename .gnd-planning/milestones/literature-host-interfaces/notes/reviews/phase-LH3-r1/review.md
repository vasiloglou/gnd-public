<!-- Edited by review_tool.py sanitize: 4 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All listed SHA-256 hashes matched.

1. **Findings**

   **F1 — Assertion identities conflate booleans and numbers.**  
   [assertion_admission.py:253](<repo>/src/gnd/examples/literature/assertion_admission.py:253), also lines 267–279.

   Handles are used directly as Python dictionary/set keys, so `true` and `1` become the same assertion. GND’s existing `gnd.values.identity_key` distinguishes them.

   **Reproduced:** Use a `claim` entity with a unit-based reference and unary `claim_seen` rows `[{"claim": true}, {"claim": 1}]`. Both model and population pass the standard loaders.
   - Approve only row 0: the standard judgment evaluator admits that target; the projection keeps **both rows**, admitting the untargeted assertion.
   - Approve row 0 and reject row 1: the evaluator reports admitted flags `[true, false]`; the projection removes **both rows** and emits one failed stage entry.

   This breaks C1 and C2. The followed-instance index uses the same unsafe identity representation.

   **F2 — Malformed includes escape as exceptions instead of `Refusal`.**  
   [assertion_admission.py:179](<repo>/src/gnd/examples/literature/assertion_admission.py:179).

   The code iterates `includes` before checking its type.

   **Reproduced:** `_include_paths(b'{"includes":1}')` raises `TypeError: 'int' object is not iterable`; `includes: true` likewise raises `TypeError`. Calling `admit()` with snapshot reads supplied in memory reproduces the uncaught exception without reaching publication. A real missing input also escapes as `ArtifactError` containing its filename.

   Callers catching the promised value-free `Refusal` receive an unexpected exception instead. This breaks C3.

   **F3 — Legal opaque values reject an otherwise supported assertion.**  
   [assertion_admission.py:240](<repo>/src/gnd/examples/literature/assertion_admission.py:240).

   Every covered role value must satisfy the new scalar-only predicate, excluding legal format-version-2 opaque markers.

   **Reproduced:** Supply an approved `claim_seen` row for `"c1"` and an untargeted attached `claim_note` row:

   ```json
   {"claim": "c1", "note": {"$opaque": "unreadable-note"}}
   ```

   With `format_version: 2`, the standard population loader accepts the population and the standard judgment evaluator admits the target. `project_shaped()` nevertheless raises `Refusal("input:invalid-contextual-population")`, preventing the required attached-row projection. This breaks C1.

   **F4 — Coverage construction is quadratic.**  
   [assertion_admission.py:229](<repo>/src/gnd/examples/literature/assertion_admission.py:229).

   Each fact type searches the `attached` list. With one row per attached fact type, coverage construction takes quadratic time in the row count.

   **Reproduced:** Projection timings for 2,000 / 4,000 / 8,000 / 16,000 attached unary fact types were approximately **0.011 / 0.038 / 0.155 / 0.527 seconds**. The 16,000-type model and population also passed the standard loaders. This disproves C4’s linearity claim; it does not establish a deadline violation.

2. **Checked and found true**

   - Fixture projection preserves the expected attached/followed rows, filters rejected claim links, and excludes unlisted entity facts.
   - Ordinary multi-target support, outside-shape target refusal, declared shape refusals, invalid `max_rows`, and parent-path refusal behaved as specified.
   - The 65,536-row fixture projection completed in approximately **0.048 seconds**; reducing its cap by one refused.
   - All four packaged outputs, captured in memory, matched the base implementation byte-for-byte and matched all H18 digest prefixes.
   - `test_li4_assertions.py`, `test_li5_lineage.py`, and `lineage_run.py` are unchanged. Lineage imports and LI4’s maximum-projection test passed.
   - Reviewed the added regex/split/slice cases; no new production regex or string split was introduced.

3. **Could not check**

   The read-only brief prevented running the file-writing integration suites, actual publication/failure cleanup, and the complete 65,536-row admission timing test. Executed checks used memory and existing files; publication was intercepted where necessary.

VERDICT: CHANGES_REQUESTED