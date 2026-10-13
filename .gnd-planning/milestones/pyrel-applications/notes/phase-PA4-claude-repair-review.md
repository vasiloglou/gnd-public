Retained independent Claude Code bounded repair output. Edited: reviewer grep tokens for home/operator identifiers replaced with generic placeholders; all findings otherwise retained. Raw output SHA-256: 5e088f4fde89b58e1418553d6906209da41acb91b2632ce3fd7f96f344c4d48f. One reviewer; no third pass.

# PA4 bounded repair review: one new finding, F1–F7 confirmed

I found one new problem: the README edit broke its resource table. Every F1–F7 disposition matches the code I read, and none of the repairs could publish a bad candidate or leak arithmetic from a refused run.

**Process:** I only read files, searched, and ran read-only `git diff`/`git show`, plus `grep`, `sed` and `wc`. I ran no Python, tests, native tools, providers or agents, and read no `.env` or credential files. This is one reviewer. Plan mode asked for a plan file and an exit call, but neither tool was available, so this review exists only in this message.

## New finding

**R1 (Low, docs): the README edit splits the resource table.**
- The new prose (`src/gnd/examples/expense/README.md:43-63`) was inserted in the middle of the table. Three rows now sit after the prose (`README.md:64-66`):
  - `currency_reporting.py`
  - `currency.architecture.contract.yaml`
  - `prepare_currency.py`
- In GitHub-flavored Markdown those three lines no longer have a table header. They render as pipe-filled text attached to the paragraph before them.
- `docs/expense/01-model.md:57` sends readers to this README for "the full resource inventory", so the damage reaches users.
- No test parses the table, which is why nothing caught it.
- **Repair:** move lines 64–66 up to just after line 41, then put the prose after the table. This only moves text; no code changes.

## F1–F7 dispositions I confirmed

- **F1:**
  - **Rule IDs exist:** all ten I checked are in the model files. `supported_currency` and `required_expense_has_currency` are only in `currency.orm.json`, which is the model the currency tests use. `one_expense_is_approved` is a uniqueness rule on `expense` (`model.orm.json:182-185`), so appending a second 103 tests it directly.
  - **Currency-edit test:** adding `expense_has_currency` to `owned_relations` makes `_preserve_source` skip that relation (`applications.py:127-129`). Without it, the edit refuses with exit 3, as the test comment says. The source is all EUR, so the EUR guard (`native_query.py:51`) doesn't fire first and the checker is what refuses.
  - **No new CLI feature:** the CLI still owns only the approval and chain relations (`extension.py:60`).
  - **Missing submitter, approving 102:** the source still lists 102 as submitted, so the guard passes and the checker reports witness `[[101]]`.
- **F2:**
  - The literal `'EUR'` stays at `native_query.py:51`.
  - The spec records it as the application's supported-unit boundary, saying a future model that only expands its enum still needs deliberate work.
  - All three successor reasons now say "shared parent performs no model-policy evaluation. EUR-only reporting is an explicit application feature boundary." That drops the old overclaim.
- **F3:**
  - The parametrized case now removes one row (`[1:]`), and the first currency row is 101, so `[[101]]` is correct.
  - The shipped `currency-missing.population.json` keeps only 103, which matches `[[101],[102]]`.
  - The fully empty relation is pinned as exit 2 with `vacuous` and `incomplete`.
  - The 20/22 run, the owner and the future item name are all in the spec.
- **F4:** `extension.py:68` removes `calculation` for every outcome, and only an accepted report copies `report`. The approval test asserts `calculation` is absent.
- **F5:**
  - `source_binding` is set from the captured bytes right after hashing (`applications.py:170`), before the query runs.
  - The checker is still bound to the exact candidate bytes by SHA (`applications.py:234-235`).
  - The early results (output already exists, bad guard declarations) carry no binding. That's fine: no bytes have been captured at that point.
- **F6:**
  - **Declaration check:** it runs before the output check, the interpreter check and the child process (`applications.py:152-156`). The `isinstance` and regex checks short-circuit before `set()`, so an unhashable item can't crash it.
  - **Lists are accepted:** this is consistent with `owned_relations`, but it means the non-tuple test exercises only a non-sequence (a bare string).
  - **Other controls:** the reason-length and reason-type controls, the crash-plus-leftover-guard → 70 control, and the named rule IDs for unknown-chain, meal-cap, category and nonpositive are all present.
- **F7:** the spec now describes native enumeration with Python result-presence checks, the same as BookRec. It no longer credits that check as native.
- **F8:** `grep` finds no `<home-prefix>` or `<operator-name>` in any PA4 evidence file, and no `<operator-stem>` in any `*.txt` (case-insensitive). The digests themselves are not verified; your plan keeps that check for completion.
- **F9:** unchanged, which is consistent with PA3.
- **Budgets:** query 103, tests 318 (249 + 69) and parent 245 match your stated figures. `extension.py` grew by 25 lines.
- **Default backend:** the `gnd` path in `extension.py` is unchanged after the `pyrel` branch.

## Reading limits

- I read the review file, the full diff of `src`, `tests` and the spec since b4bbf4f, all of `native_query.py`, `applications.py:100-245`, the README, the first 125 lines of the expense test file, and the rule and fixture rows above.
- I did not read the `run_simulated` or `simulated_child` helpers:
  - **Bad-declarations test:** its `called == []` check would pass trivially if `run_simulated` replaced the `_child` patch. The test's exit-3 assertion and exact error message still tell the cases apart.
  - **Crash test:** I didn't verify that the wrapped `simulated_child` writes the leftover guard file.
- I did not read the plan, the PA3 record, the `.agents/skills/` directory, the repair-review prompt, or the evidence files beyond the `grep`s above.
- I can't tie any untracked receipt to the current source bytes, and I don't credit any pass count you quoted (10 targeted checks, 64 parent checks, 23 cases).

Fix R1 by moving the three rows before the full run. No other repair is needed in this round.
