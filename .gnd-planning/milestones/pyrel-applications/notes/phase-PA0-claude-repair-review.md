Retained Claude Code stdout, 2026-10-13. No text substitutions.
One reviewer is one reviewer. Opus/high, safe mode, plan permissions, stdin,
no session persistence. Reviewer used read/search, read-only Git and inline
Python reads; no product/native/test suite execution. These opinions cover the
reviewed repair bytes; subsequent hardening fixes have separate root controls.

# PA0 repair review (round two, one reviewer)

**Verdict:** I couldn't refute repairs (3), (5), (6), (8) or (9), and I found no blocking defect. Most of (2), (7) and (10) holds. Repair (1) is correct in the data, but no test enforces it. Repair (4) is still incomplete. I'm keeping 7 findings. Two are Medium-Low and could change what PA1 relies on: F1 (the native answer key isn't enforced by any test) and F2 (13 new inputs have never been run on native PyRel). The other five are Low.

## What held up (checked read-only)

- **(1) Native expectations.** I wrote a separate inline Python recomputation for all complete-model cases, reading the files directly without GND. It recomputed `book_is_blocked_for`, `book_is_eligible` (with negation), the `all_eligible` status and witnesses, and the missing/extra derivation tuples. All of them match `expected_native_*`.
  - Across all 137 cases, every native row equals the mapped GND row (pass→satisfied, fail→violated, warning→warning), and every guarded witness equals the GND witness. The only exceptions are `constraints[3]` on `m2-book_is_eligible-extra` and on `m2-eligible-joint-omission`, which are exactly the two disagreements A1 lists.
  - Every `expected_acceptance` agrees with spec precedence: 75 rejected/1, 61 accepted/0, 1 accepted_with_warnings/0.
  - Verdict inventories are complete for each model.
- **(3) Successor mode.** `mode != 'baseline'` appends `--accept`. The r2 receipt shows all 137 cases exit 64 with empty reports, and legacy mode is used only for the baseline.
- **(5) Frozen GND witnesses.** They are compared against `offending_facts` (`tests/test_pyrel_application_corpus.py:69-70`). The drift test is live: `review-witness-red.txt` shows it was red before the fix.
- **(6) Distinct-value uniqueness siblings.** There are exactly 12, one for every non-spanning uniqueness. The two `expense_is_approved` uniquenesses are unary and correctly have no sibling. Each population really does have the same key with a different value.
  - The 124-case legacy receipt shows the legacy runtime already reports exact duplicate rows as `violated`. All 124 legacy non-`unsupported` rows agree with the native key.
- **(7) Metadata and cross-links.** kind, modality and id are checked against the model, and each lane's target, model and expected value are checked. There is a liveness test for this.
- **(8) Stories.** The finance stories now say both failures are kept. Positive stories no longer reuse violation text.
- **(9) Unknown/vacuity.** No population has an empty antecedent relation, and no computed derived antecedent is empty. All asserted relations are covered and listed. So the frozen `satisfied` rows don't contradict the vacuity rule. PA1-C2 and PA1's direct-branch list name empty, clean-zero and uncovered cases.
- **(10) Driver hygiene.**
  - The output path is checked before any native work runs.
  - Export goes through `python -m gnd export pyrel` with a relative path. The venv's `.pth` points at the working-tree `src`, and `MODEL_NAME` is relative.
  - The model hash matches the contract's representation: `_read_text` decodes raw bytes as UTF-8, there are no CRs, and re-encoding gives the same bytes.
  - Inputs are checked for stability before and after the run. Version, cap and output-preflight errors raise explicitly instead of using `assert`. Fixtures are 345 KB and 73 KB, under the 1 MiB cap.
- **Hashes, counts and source.** The matrix and answers hashes equal spec lines 276-277. There are 61 obligations, 137 cases, and 146 tests from the receipt (4 + 137 + 3 + 2). `git diff 9f4e226 -- src/` is empty.

## Findings

**F1 — The native answer key and the disagreement list are only data; no test enforces them (Medium-Low).**
- No test reads `expected_native_*` or `intentional_disagreements`; grep finds them only in the driver and the mocked driver test.
- No test pins the `answers.json` or `matrix.json` hashes. The driver records `answers_sha256` but never compares it with the approved value.
- `m2-eligible-joint-omission` isn't linked from any obligation row, so the cross-link check (`corpus.py:50`) never covers one of the two named disagreement controls.
- **Consequence:** A1 lines 29-30 and 35-43 forbid regenerating native answers from the implementation and excluding a mismatch that isn't listed. Today nothing but a manual hash comparison catches a PA1/PA2 edit that rewrites the native answers or adds a third disagreement; both the corpus gate and acceptance mode would stay green. My recomputation shows the current data is right; that check isn't retained anywhere as a test.

**F2 — The 13 new r2 inputs have never been run on native PyRel (Medium-Low).**
- `baseline-r2.json` runs 7 cases.
- `successor-r2-red.json` has 137 cases, all exiting 64 with `{}` reports.
- So the 12 distinct-value siblings and the joint-omission case have GND measurements only. The 124-case omission receipt predates them and is bound to the old hashes.
- **Consequence:** plan lines 161-162 require measuring current behavior with real PyRel and GND on the same frozen inputs. PA0-C2 (plan line 168-169) asks that expectations fail "for the actual omission". The r2 red shows only that the interface is absent. How the legacy runtime handles these 13 populations is unknown until PA1.

**F3 — The modality check can be bypassed by row placement (Low).**
- `tools/measure_pyrel_applications.py:56-68` checks modality only when the row is in the `verdicts` array. Rows from both arrays go into one `observed` map, so the inventory check at line 80 doesn't care which array a ref came from.
- A report with `verdicts: []` and every constraint row keyed by `derivation_ref` in `derivations`, with no `modality` anywhere, passes every check. The mutants in `tests/test_pyrel_application_driver.py:83-102` don't cover this.
- `id`, `constraint_type`, `reason`, and non-guarded witnesses are never checked either.
- **Consequence:** the claim that the verifier checks modality is weaker than stated. Deontic-blocking is still caught through the status and exit checks.

**F4 — A non-object report crashes the driver instead of being recorded as a failure (Low).**
- `report.pop` at lines 128-129 runs before `check_acceptance`, so a native report that is a JSON list or `null` raises `AttributeError`. The `report-not-object` branch at lines 39-40 can never run.
- Invalid JSON, or output over 4 MiB, also raises and writes no receipt.
- **Consequence:** a traceback (exit 1) looks the same as the documented "expected 1" successor red.

**F5 — Repair (4) is still incomplete for the real lookup pins (Low).**
- The inventory lists `rf1-pins/goldens/helpers` but leaves out:
  - `tests/test_rf1_semantic_pins.py:81-84,108`, which pins `ModelIndex.primitive`, `reference_value_type` and `_valid_temporal` goldens under `goldens/sem*`, plus the `goldens.sha256` manifest;
  - `tests/test_rf7_review_regressions.py:79-85` (ModelIndex primitive ambiguity);
  - `tests/test_v70_phase1_registration.py:5` (imports `PyrelOracle`).
- **Consequence:** PA-R7 (plan line 71) requires preserving actual lookup identities, and PA1 adds primitive/ref admission in the same file. A change there would break pins that no inventory routes.

**F6 — Latent liveness gaps (Low).**
- `corpus.py:123` reads `fact['constraints'][0]['roles']` instead of the row's own index. Every current uniqueness row is `constraints[0]`, so it isn't wrong yet.
- The `STATUS` map at `measure…py:15-16` is unused and untested, including `unchecked→incomplete`. A1 line 44 asks for an explicit, tested normalization map.

**F7 — Stale wording (Informational/Low).**
- The milestone `README.md:8-10` still says "124 controls" and that the successor exits 1 "for the actual guarded/derivation omissions".
- The fixtures `README.md` (hash pinned at spec line 231, unchanged) describes `answers.json` as GND observations plus target outcomes only, and doesn't mention the native-expectation, distinct or joint lanes.
- Fixture data is now 11,275 lines, under the 15,000-line ceiling but not recorded.
- The distinct stories leave out collateral failures: `m3/m4-r7-distinct` also violate `constraints[10]`, and `m4-r8-distinct` also violates `constraints[12]`. The finance stories now state both failures, so narration is inconsistent. Full-inventory checking means this can't hide a defect.

## Coverage and limits

- **Read:** the prior review, the repair prompt, A1, 003, the whole PA0 spec, the PA1 spec, plan §§2-4 (lines 110-189) and grep hits elsewhere, the complete diff since 9f4e226 (spec, driver, corpus test), the new driver test, the matrix consumers and rows, the r2 and original receipts, and the `emit.py`/`_read_text`/export CLI paths.
- **Checks run:** I used read-only git commands and inline Python that only read files. It recomputed derivations and `all_eligible`, compared native vs GND rows and witnesses, acceptance precedence, inventories, coverage, emptiness, distinct populations and lane links.
- **Not executed:** pytest, the driver, `gnd`, or any native runtime. The test counts (146) and pass results come from the receipts. I didn't recompute the receipt or population hashes, beyond the two corpus hashes.
- **Mocked tests:** I gave no native-acceptance credit to the mocked driver tests.
- I read about 10 population files directly and covered the rest through scripts. One reviewer is one reviewer, and there is no further round.
