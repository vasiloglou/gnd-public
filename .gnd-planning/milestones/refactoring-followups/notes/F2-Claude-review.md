Every SHA-256 in the brief matched, so I reviewed the bytes the brief names.

**Answer:** Mostly yes, but not on every legal input. The changed-policy check falsely fails v6 when the temporary path contains non-ASCII characters (F1). The surface check finds missing rows but not extra ones (F2). Removing part of the evaluator guard would go unnoticed (F3).

## 1. Findings

**F1 (correctness, reproduced). `tests/test_rf1_session_pins.py:89-90`**
- **What is wrong:** The check rebuilds the expected policy from its template with `json.dumps(value, ensure_ascii=False)`. But `build_v6` (`:259`) writes the real policy with plain `json.dumps(...)`, which defaults to `ensure_ascii=True`. So for any non-ASCII path, the expected bytes hold the raw UTF-8 character and the real file holds `\u00fc`.
- **Consequence:** An unchanged policy is reported as "RF1 declared adapter-policy bytes changed". That breaks v6 for any user whose temp directory or checkout path has a non-ASCII character. v7 and v8 pass because `canonical_json_bytes` happens to write the same way the template is expanded. The expansion is fitted to the committed examples: it assumes one escaping style, while the files use two.
- **Reproduce:** `uv run pytest -q "tests/test_rf1_pin_harness.py::test_changed_declared_policy_bytes_fail" --basetemp="/private/tmp/f2rev-ü dir"`. Result: `[6]` fails with `At index 167 diff: b'\\' != b'\xc3'`, while `[7]` and `[8]` pass. All three should pass.
- **Fix:** Expand each template with the escaping its own writer uses, or have `build_v6` write the policy with `ensure_ascii=False`.
- I did not check whether other parts of the v6 pin already failed on non-ASCII roots before this change. This assert is now the first failure.

**F2 (coverage gap, read only). `tests/test_rf1_pin_harness.py:429-446`**
- **What is wrong:** `test_rf_plan_surfaces_have_inventory_rows` reports only missing surfaces. The plan's verification row for F2 asks for a "missing/extra surface comparison", and the spec says owed rows are included. The test never looks at rows outside the list, or at `owed_by`/`status`.
- **Consequence:** A row added for a surface the plan never named would pass. So would a row whose `owed_by` changed (for example, RF5 to null).
- On the current inventory the missing-row check is sound. Each of the 35 names matches exactly one row in its phase, and none of the 35 rows is left unmatched, so deleting any one row fails the test.

**F3 (weak negative control, read only). `tests/test_rf1_pin_harness.py:419-426`**
- **What is wrong:** The guard test calls only `checker.check(None, None)`. Of the 15 names the guard patches, it observes just that one.
- **Consequence:** If the guard stopped patching `terms` or `extensions` (for example, the `evaluate_term` loop were dropped), this test would still pass. Also, the two parametrized families now point at the same function, so they no longer test the two guards independently. The test cannot show the pre-sharing comparison the plan asked for.

## 2. Checked and found true
- **`_replace_tokens` preserves behavior.** It applies the same longest-first ordering by raw needle length that all three old loops used. Its escaped-JSON mode is the old `scrub` logic exactly.
- **New escaping test catches regressions.** `test_scrub_prefers_longest_token_in_escaped_json` fails both if `json_observation` is dropped and if the order is reversed.
- **Policy tampering is detected.** Appending one byte to any of the v6/v7/v8 policies raises the error, which was the proposed negative control.
- **`witness_guard.no_evaluator` is unchanged.** Its body matches both removed copies, and the old import path `v71_witness_cases.no_evaluator` still works.
- **All 15 guarded names still exist** in `checker`, and their `extensions` and `terms` counterparts resolve, so no name is skipped silently by `hasattr`.
- **RF7 is correctly left out** of the required surfaces, since the plan says "This milestone has no RF7 criteria".
- **Regex and split check:** the diff adds no new regular expression or string split. The template replace in F1 is the one matcher I found fitted to its fixtures.
- **Tests and lint:** `pytest tests/test_rf1_pin_harness.py tests/test_rf1_session_pins.py` gave 76 passed, and `ruff check` on the six touched files passed.

## 3. Not checked
- I did not run the full default-lane pytest, for time.
- I did not run the HEAD baseline of the v6 pin on a non-ASCII root.
- I did not verify the Q3 label corrections in successor documentation, because they are outside this diff.
- Side effects: `uv run` created `.venv` in the repository, and the reproduction wrote temp directories under `/private/tmp`. No tracked file was touched.

VERDICT: CHANGES_REQUESTED
