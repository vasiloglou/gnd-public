Retained reviewer output; edited only to replace any operator home path with <operator-home>. One reviewer is one reviewer. The disclosed no-op Python command violated the no-execution instruction; no project code or tests were executed.

# PA1 repair review (single reviewer, final bounded round)

**Verdict:** None of the seven repair claims is refuted, and I found no blocking issue. One Low finding remains, which a sentence in the spec can settle, plus two minor notes that need no action. I would not hold PA1 for any of them.

**Deviation:** while reading evidence files I accidentally included a no-op `python3 -c 1` in one shell pipeline. It read no data and executed no project code, but it does break the no-execution rule. Everything else was read, grep, stat, shasum, and read-only `git diff`/`show`/`status`. I also read the installed `relationalai` source under `tutorials/runtimes/.venv`, read-only, to check the negation question in claim 2. I ran no tests, native tools, agents or providers, and did not read `.env` or credentials.

## Finding

### L1 (Low): top-level unary subset doesn't check role type compatibility, so `--accept` can accept a model GND calls ill_formed
- **Where:** the subset branch of `_profile_admit` (`pyrel_runtime.py:1393-1408`) checks only that the fact and role exist. `_one_direction` then reuses the subset side's refs for the superset pattern.
- **GND:** `_rule_role_seq_type_compat` (`model/_validation.py:1078`) is in `_SEMANTIC_RULES` and is error severity by default (`errors.py`, `ValidationIssue.severity = "error"`). Roles whose object types share no supertype therefore make the model ill_formed.
- **Not caught at export:** `render_pyrel` (`export/emit.py`) calls only `admit_model` and runs no checker, so such a model exports and runs.
- **Discriminating case:** add a String value type `t` and a fact `q(z:t, y:n)` to `toy()`. Use the top-level subset `r.x ⊆ q.z`, with `r=[{x:'a',y:7}]`, `q=[{z:'a',y:7}]` and everything covered. I expect `gnd check` to give `ill_formed` (`semantic:role-seq-type-compat`) and the runtime to give accepted/0. That expectation comes from reading the code; I didn't run either.
- **Consequence:** this is the same class as the pre-review inline-guarded/subset acceptance, which `review-native-confirmed-red.txt` shows as `accepted: True`. That was fixed by refusing those shapes. It is not a false policy verdict about the population, which is why it is Low.
- **Bounded options:**
  - add a spec sentence saying acceptance assumes a GND-valid model and that the PA3 publisher must gate on validation; or
  - add a one-line admission refusal unless both roles have the same object type or share an ancestor (the `descendants` walk already exists).

## Minor notes (no action needed)
- **N1, embedded-model size:** the oversize-model branch (`:1602-1603`) changed in the repair from 3 to `ProfileRefusal`/2 with no report, and no test covers it. The amendment's "unread population can't have an honest digest" reasoning doesn't apply to the model, which is fully in memory. Because the check runs before the population read, a missing population returns 2 here rather than 66. Practical impact is negligible.
- **N2, exit-code classification:** non-dict subset elements and non-dict guarded atoms/binds still refuse with 2 rather than 3. Unhashable selectors now give 3. Both fail closed, nothing crashes, and this design predates the repair.

## Claims checked
1. **F1:** confirmed.
   - Diff against the retained pre-review bytes shows inline refusals for guarded (`:1362`), value (`:1386`) and subset (`:1393`), and mandatory host-empty returning vacuous (`:1503`). There is no top-level value vacuity change.
   - Inline uniqueness and mandatory are still admitted, as designed.
   - The value-roster rebuttal test asserts that GND passes and the runtime accepts.
   - `review-native-confirmed-red.txt`, run on the pre-review bytes:
     - the roster case passed;
     - inline value, subset and guarded were accepted;
     - inline mandatory was rejected/1;
     - the repeated-call case was `runtime_failure`.
2. **Overrides:** confirmed.
   - The two overrides differ from the legacy functions only in using `self.m.not_`.
   - The `evaluate` handler table dispatches to bound methods, so the overrides do take effect.
   - The legacy `PyrelOracle` bytes are unchanged.
   - Neighbour checked:
     - the module-level `not_` goes through `_check_model()`, which raises "Ambiguous model" once more than one model exists;
     - `count`, used by legacy uniqueness, is a model-independent library aggregate (`std/aggregates.py:70-73`);
     - no other single-model convenience call is on the profile path.
3. **Totality:** confirmed. I walked every lookup in `_profile_admit` and `_profile_guard` and found no remaining path to a `TypeError` or `KeyError`. Inline role names are already checked by `_constraints`. The three malformed cases were red against the pre-review bytes (traceback at line 1374).
4. **Size and context:** confirmed.
   - The `startswith` prefix matches the `_read_text` message at `:914`.
   - Context refusal goes through `acceptance_document` before `version()` or any `relationalai` import.
   - `--config` is refused.
   - The spec (lines 232-240) amends the early raw-size exception explicitly, and no partial digest is produced.
5. **Output, status and work:** confirmed.
   - A missing output parent gives 70. Other `OSError`s fall through to the generic handler and also give 70; an existing path still gives 11.
   - Unknown statuses are blocked twice: per row (`:1562`) and in the final composition (`:1585`).
   - Consequent multiplicity is included via `max(1, len)`.
6. **Receipts:**
   - The regression tests were red against pre-review bytes `51674b42…`, the same runtime hash I recorded in the first review.
   - `review-parent-final` (80 passed / 8 deselected) and `review-native-final` (18 passed / 23 deselected, 16.64s) both post-date the runtime's last edit (15:33:29) and the final edit of the regression test file. Sub-second birth time shows parent-final started 1 ms after that edit.
   - The counts are consistent: 18 = 10 native-file tests + 8 native regressions, and 23 = the non-native regressions.
   - Budgets: about +416 runtime lines against 650; tests are 269 + 166 + 62 + 242 = 739 against 750, plus 13 routing lines.
7. **Successors:**
   - RF6 counts only `fact_types`/`roles` expressions and the repair adds none, so 356/287/301 stays correct.
   - The dynamic inventory was refreshed to 5800/7315 and is bound to its predecessor's sha256.
   - The RF2 rendered-byte successor is authenticated in the same way.
   - RF9 and compiled evidence are referenced, not edited.

## Limits
- Nothing was executed. L1's GND outcome comes from reading the code.
- I did not count the dynamic inventory or rendered digests by hand.
- `repaired-focused.txt` (357 passed), `native-repaired.*` and `current-byte-bindings.json` now exist. The bindings file records the current runtime sha256 `d8c21fd1…`. As instructed, I did not credit any of them.
- The inline ill_formed premise tests check the outcome but not which rule fired. The same scaffolding passes for the other shapes, which makes an unrelated cause unlikely.
- This is one reviewer's pass.
