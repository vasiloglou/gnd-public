# PA5R independent diff review

**Verdict: PA5R is partly refuted, with five blocking findings (B1–B5).** The public seam, the shared checker stage, the runner grammar, the D0 wording and both F-claims (F2, F3) hold up. Two claims fail: the CLI's `--proposal` option keeps the input unchanged on every backend, and `format_result` is total. Two A2 D2 obligations are not met, and the junior-reader pass gets stuck. I ran nothing and edited no repository file; the report is also saved in the plan file `~/.claude/plans/independent-pa5r-diff-steady-plum.md`.

## Blocking

**B1. With the default backend, `--proposal` skips the input-preservation check.**
- **Evidence:** `src/gnd/examples/bookrec/extension/bookrec/cli.py:76-78`.
  - Without `--backend pyrel` (the default is `gnd`), the CLI calls `publish(model, json.loads(proposal), output)`.
  - `--input` is never read and `_preserve_source` never runs.
- **What can go wrong:** a proposal that deletes Ada's `user_is_minor` fact and recommends `night` passes `api.check` and gets published.
- **What this contradicts:** PA-R5, the spec's "--proposal (pyrel and gnd backends)", and the troubleshooting row "a proposal may only change `recommendation`" (`07-native.md:254`). No test covers this path.
- **Smallest repair:** call `parser.error` unless `--backend pyrel`, or run `gnd.export.applications._preserve_source` against `--input` before `publish`. Add one test.

**B2. The Expense chapter does not use chapter 2's setup, but says it does (A2 D2 and the spec's own obligation).**
- **Evidence:** `docs/expense/04-native.md:32-50` copies the example folder and runs a different install loop. There is no `gnd codegen`, and `architecture.contract.yaml` and the generated `model_orm/` are missing.
- **What it should match:** chapter 2 runs `gnd codegen` and its own install loop (`docs/expense/02-application.md:15,36-50`).
- **The false claim:** "This is the same layout chapter 2 installed" (line 32-34).
- **Smallest repair:** run chapter 2's codegen and install loop word for word, plus `native_query.py`. Otherwise, reword the sentence and record a ruling.

**B3. The meal-cap step edits a JSON path in code, which A2 forbids.**
- **What A2 says:** `plan-amendment-a2.md:125-128` bans hand-editing JSON paths. The fallback to a reader-local copy applies only if the `gnd evolve` path cannot make the change.
- **What happened:** spec D2-a measured that `gnd evolve` does support `modify`, so the fallback condition was not met. The page still sets `rule["consequent"]["comparison"]["right"] = 50` (`04-native.md:198-200`).
- **Smallest repair:** either ship a small evolve proposal file and use `gnd evolve preview/apply`, or record an explicit ruling that overrides that A2 sentence.

**B4. `format_result` is not total (standing rule 1).**
- **Evidence:** `src/gnd/export/applications.py:319` and `:336` loop over the value before checking its type.
  - `{'calculation': {'selected_pairs': 5}}` raises `TypeError`.
  - `{'policy': {'verdicts': 5}}` raises `TypeError`.
  - A verdict with `{'status': []}` fails at `row.get('status') in {...}` (unhashable list).
- **Why T3 missed it:** its hostile cases cover none of these shapes.
- **Smallest repair:** guard with `isinstance(x, list)` before looping, and `isinstance(status, str)`. Add these three cases to the test.

**B5. Junior pass: the blocks cannot be pasted in order into one terminal.**
- **Repeated `cd`:** every app block starts with `cd bookrec-native/extension` (`07-native.md:98,125,145,…`) or `cd expense-native` (`04-native.md:94,113,…`). The second block in the same shell fails with "No such file or directory".
- **Python blocks:** the chapters never say how or with which interpreter to run the Python blocks (`07-native.md:37`, `04-native.md:37,194`).
- **Smallest repair:** wrap each command as `( cd … && … )` and add one sentence: run Python blocks with `"$GND_TUTORIAL_GND_PYTHON"`.

## Hardening
1. **Receipts can say "passed" when the output differed.** `tools/run_tutorials.py` sets `status='passed'` from the exit code alone and appends the receipt before the output comparison. Move the comparison earlier, or set `status` after it.
2. **`check_proposal` has no size cap on the re-serialized candidate.** The `len(candidate_bytes) > INPUT_CAP` check stays only in `execute_application` (`applications.py:243`). Move it into `_check_and_publish`.
3. **Refusal reasons break the output line, and one troubleshooting row is wrong for BookRec.**
   - The NOT RUN reason is stderr with its trailing newline, so `format_result` returns a "line" containing `\n`.
   - On BookRec's query path, missing coverage shows `NOT RUN (ProfileRefusal: coverage-not-declared…)`. The troubleshooting row (`07-native.md:253`) says `NOT ACCEPTED (some rules could not be decided)`, which never appears there.
   - Fix: strip and flatten the reason, and correct the row.
4. **The seam and summary drift from the spec.** `NativeApp.source` is the parsed document itself, not the deep copy the spec promises (`pyrel_runtime.py:1648`). `format_result` drops the spec's `kind=` parameter. Either fix the code or record the drift.
5. **The meal-cap check proves nothing.** The block prints a hard-coded "(was 75)" (`04-native.md:202`). Assert the old value before changing it.
6. **A `text` block after an unchecked command is silently ignored by the runner.** Refuse it.
7. **The D7 gate is weaker than A2 asks.**
   - The exit-code test passes if any table row contains the digit 2 or 3.
   - The overview's setup commands show no output and the gate never checks them.
   - The gloss on first use of "witness" is checked only in the chapters.
   - Nothing checks for the next-steps links.
8. **D0 wording.**
   - "not **yet** supported" hints at a roadmap; it is honest, since the exporter returns 64 for a named connection (`pyrel_runtime.py:1876-1880`).
   - `docs/agents/index.md:23` still says "…or enterprise data".
9. **F3 evidence is prose only, and the rf7 failure hides later offenders.**
   - Both failures are plausible. HEAD's `pyrel_runtime.py` has `json.loads` at lines 1524 and 1612, from PA1/PA2. The only new `json.loads` in the diff is in `cli.py`, which is excluded from that test.
   - Still, no transcript from a clean HEAD is kept. `test_complete_routing_and_dirty_controls` stops at the first offending file, so it would hide any new one.
   - The ring `rel_reflexive` disagreement between the native checker and the oracle is a real semantic mismatch the milestone close needs to address.
   - F2 is fine: `RENDER_PHASES` extends only the rendered-bytes chain, and the successor is authenticated against PA4.

## Completeness
1. **Step 10 "Next steps" is incomplete on all three pages.** None links to `gnd-model-from-text`. The overview links `gnd exp run` without saying it is a separate session contract the reader writes (D6).
2. **The Expense "who does what" table has no plain-Python row** (`04-native.md:20-24`).
3. **The seam is documented nowhere in the docs** (A2 D1 asks for "one documented entry point"). `app.match`, `app.relationship` and `app.rows` appear only in the collapsed source.
4. **The screenshot set covers 7 of the 12 page × width × theme combinations the spec's verification step asks for.**
   - BookRec: no mobile dark.
   - Expense: no desktop dark, no mobile light.
   - Overview: no desktop light, no mobile dark.
   - PA5-C6's "both themes per page" is met.
5. **F1's "candidate bytes" check is BookRec-only.** The Expense identity test never compares candidate bytes.

## Junior-reader stuck list
1. **Overview setup, `python3 -m venv`:** on macOS this is often Python 3.9. GND needs 3.11 or newer (`pyproject.toml:11`), and the page says 3.13 but never selects it.
2. **Where to work:** the pages never say to stay in the folder where `gnd-env` and `pyrel-env` were created.
3. **Python blocks:** how to run them, and with which interpreter (B5).
4. **Second `cd` fails** (B5).
5. **BookRec step 3:** `app`, `app.match`, `reader`, `book`, `.define` and `app.relationship` are never introduced; only `m`, `String.ref()` and `m.not_` are.
6. **Witness keys:** `{"$b": …, "$u": …}` — what do the `$` names mean?
7. **BookRec steps 5–6:** is `ben/night` new or already there? The "corrected" proposal drops the bad pairs but also adds `cosmos` and `map`, and it comes from an unexplained `checkpoints/advisory.candidate.json`.
8. **Troubleshooting by exit code:** the text output never shows an exit code, and `echo $?` is never mentioned. "Coverage list" is never explained.
9. **BookRec missing-coverage case:** the screen shows a split `NOT RUN (…` line that matches no troubleshooting row.
10. **Expense step 6:** "An approval cannot override a category cap … even though no approval is involved" reads as a contradiction.
11. **Expense step 2:** says "same layout as chapter 2", but chapter 2 used `gnd codegen` (B2).
12. **Expense step 7:** `rule["consequent"]["comparison"]["right"]` assumes the reader knows the model's JSON structure.

## Claim table

| Claim | Evidence |
|---|---|
| Nothing is saved unless the rules pass; warnings still save | `applications.py:146-174`; `verify_policy_report` warns only on deontic (should) rules |
| Bad proposals return the exact facts that broke a rule | `applications.py:349-357`, plus runner-checked outputs |
| The check is a PyRel program generated from the model | `emit.py:31-34`; `_check_and_publish` runs `runtime --accept` |
| PyRel 1.30.1 / DuckDB 1.5.5, local, no account | `pyrel_runtime.py` `open_app` version pin; `runtime-environment/pyproject.toml:8` |
| The applications runtime refuses non-local connections | `pyrel_runtime.py:~1860` ("requires in-memory local"); the seam has no connection parameter |
| The two environments need different versions of a shared library | `docs/runtimes/scenario.md:46-47` (Pydantic) |
| Package `get-nick-done==0.1.0` | `pyproject.toml:5-6`; whether it is on PyPI is not verified |
| Python 3.13 and uv are needed | Partial: the command does not select 3.13 |
| No query ran in step 5; only the check caught it | `check_proposal` has no query stage |
| Ben is an adult | Supported indirectly: the output shows only Ada's witness |
| The corrected proposal drops both bad pairs | Partial: it is a different candidate |
| Same query and facts; only the rule changed | `strict.orm.yaml` run; checked outputs |
| Changing a limit is a model change, not a code change | Expense step 7 run (but see B3) |
| An unknown fact list is never treated as empty | Supported in code (`open_app` coverage refusal; `acceptance_document` "incomplete"); not shown on any page |
| Input files are never modified | The code re-reads sources and refuses if they changed (`applications.py:~167`); this detects changes, it does not prevent them; not shown on a page |
| A proposal may change only `recommendation` | pyrel backend: `_preserve_source`. gnd backend: **unsupported** (B1) |
| The Expense report is shown only after an accepted check | `extension.py:66-71` |
| USD is refused by the app before any check | `native_query.py` guard; `execute_application` returns early |
| "Same layout chapter 2 installed" | **Unsupported / false** (B2) |
| Meal cap "was 75" | Hard-coded print; the figure caption agrees |
| "No module named cli" | Approximate: the real message is `No module named 'cli'` |
| The six figures are bound to checkpoints | The SVGs are unchanged in the diff; the existing graphic tests were not re-read |
| Snowflake is "not yet supported by gnd export" | Exporter returns 64 for a named connection (`pyrel_runtime.py:1876-1880`) |

## Reading bounds
- **Read:**
  - A2 (r3) and its gate record (`010`).
  - The PA5R spec, F1–F10.
  - The full diffs of `applications.py`, `pyrel_runtime.py`, both `native_query.py` files, both CLIs, `run_tutorials.py`, the successor support module, `test_bookrec_pyrel_application.py`, the D0 pages and `zensical.toml`.
  - All four new test files and the three pages, in full.
- **Read in parts:** the oracle helpers and `ApplicationOracle`, `_preserve_source`, `execute_application`, chapter 2's install section, `test_rf7_structure.py`, and these evidence files: `pyrel-successor.json`, `preexisting-failures.txt`, `seam-red`, `focused-*`, the `*-pyrel.txt` tails, and `selection.txt`.
- **Not read or not done:**
  - The screenshots were not viewed.
  - The query `.txt` twins and the SVGs were not opened.
  - The checkpoint JSON files and the receipt contents were not opened.
  - Earlier tutorial chapters beyond chapter 2 were not read.
  - Nothing was executed.
  - Empty files `claude-review-raw.md` and `claude-review-stderr.txt` already exist in `evidence/PA5R`.

## Refactoring suggestions
1. Move the candidate size cap and the shared result/`except` tail into `_check_and_publish`, or into a small wrapper, so `execute_application` and `check_proposal` stop repeating them.
2. In `format_result`, add a `_list(v)` helper returning `v` if it is a list, else `[]`, plus a `_text(v)` helper that flattens to one line. That makes totality structural.
3. In the BookRec CLI, route both backends' `--proposal` through one input-preservation step.
4. In the runner, decide `status` once, after both the exit-code and output checks, and refuse a stray `text` block.
5. Extend the D7 gate to cover the next-steps links, the overview's setup output, and exit-code rows that carry a plain meaning.
