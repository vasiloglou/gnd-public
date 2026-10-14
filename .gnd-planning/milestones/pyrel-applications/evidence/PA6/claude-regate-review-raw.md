**Verdict:** Credit run E. Nothing I found blocks it. The initial review's findings 1–7 are fixed in the committed harness. The new constants match the receipts exactly. Run E's receipt binds the committed bytes. The CI repair fixed the causes of the failures and didn't widen any guard. Findings 8–10 from the initial review are only partly fixed, and there are a few provenance and record gaps (listed below).

## Answers to the four questions

**(1) Initial-review repairs, checked against `tools/accept_pyrel_applications_install.py` at c0039e4:**
- **F1 (artifacts not bound):** fixed at lines 182–185. The receipt binds the step receipts, both isolation programs and their JSON outputs, both corpora, `tools/`, `docs/`, `overrides/`, `site/`, `zensical.toml` and the work trees (565 artifacts).
- **F2 (source identity late and coarse):** fixed at lines 96 and 186–188. Identity is captured at the start and re-checked at the end, and the harness was committed before the run.
- **F3 (skipped native blocks would pass):** fixed at lines 57–77.
- **F4 (native install differs from docs):** fixed at line 117, which now uses `--locked --only-group tutorial-runtimes --python 3.13`.
- **F5 (C2 numbers not asserted):** fixed at lines 165–167 (137/137, 2,321 comparable rows, exactly two A1 differences).
- **F6 (GND137 completeness):** fixed at lines 148–150 and 158.
- **F7 (implicit SVG inventory):** fixed at lines 16 and 175–180 (explicit list of six, rendered twins, graphic URLs present).
- **F8 (environment hygiene):** partly fixed. The environment is now allowlisted (line 97) and base versions are recorded (line 189).
- **F9 (narrow isolation probe):** partly fixed. The Expense probe was added (lines 171–172).
- **F10 (weak red evidence):** partly fixed. The 12 MiB cap now has a test (`tests/test_pyrel_applications_install.py:74-79`).

**(2) Constants:** they match the receipts exactly.

| Group | Pages | Native lane | Offline lane | Native blocks |
|---|---|---|---|---|
| BookRec | 7 | 59/59 passed | 51 passed, 8 explicitly skipped | 8 |
| Expense | 4 | 45/45 passed | 35 passed, 10 explicitly skipped | 10 |

- Every pyrel-lane row ran under `tutorials/runtimes/.venv/bin/python` with exit 0 and its output checked.
- Every `count` field equals the number of passed rows.
- These numbers match 011's gate (59/45/51/35).

**(3) Receipt binding:**
- **Commit:** `c0039e4` (current HEAD).
- **Harness:** `68a1a63d…` equals the committed blob, as do the three copied tools and `zensical.toml` (`f8b3ce86…`).
- **Sources:** all 550 source hashes equal the committed blobs. 550 is exactly the tracked file count under `docs/`, `overrides/` and `src/gnd`, so the tracked code was clean.
- **Lock:** `2b84d816…` equals the committed runtime lock.
- **Evidence copies:** the native and GND corpus files, the four step files and both isolation JSONs in `evidence/PA6/e-*` hash to the receipt's values.
- **Native corpus:** binds matrix `4fbb82a5…` and answers `db902a38…`, both equal to what `approval.json` records. It also binds runtime source `6748717f…`, which equals the committed `pyrel_runtime.py`.
- **PA6-C1:** the learning-path receipts above.
- **PA6-C2:** 137/137 on both sides and 2,321 of 2,321 rows matching. The two A1 differences are `m2-book_is_eligible-extra` and `m2-eligible-joint-omission`.
- **PA6-C3:**
  - 67 wheel resources bound.
  - Both isolation exports report `accepted`, exit 0, `duckdb-local`.
  - 7,561 local links checked.
  - The six SVG twins and `site/pyrel-apps/index.html` are bound.
- **PA6-C4:** this reading.

**(4) CI repair (3783051):** no guard was weakened.
- **rf7:** the `json.loads` calls were removed rather than allowlisted. `_rows` already yields `_jsonable` values, so deduplicating by canonical text is equivalent. Run E reached 2,321/2,321 on the new program bytes.
- **rf9:** the policy check is still exact, and the injected-`getattr` mutation must still raise. The test now reads the same effective policy rf6 uses.
- **rf6:** PA5R swaps one row for one row, and the counts stay at 293 rows / 362 occurrences.
- **Doctor:** the exact file pins and per-name assertions are kept. All 8 pinned files exist, and both roots' copies are byte-identical.

## Findings

1. **Hardening: 3783051 rewrote closed PA5R evidence in place.**
   - `evidence/PA5R/pyrel-successor.json` had its "after" hash changed from `56c4e7c2…` to `60a263a1…`, but its PA5R-only reason text was left unchanged.
   - The new PA5R `dynamic-query-successor.json` carries the PA5R reason but includes rows that came from the CI repair (`_derive canonical[key]` at :65, `guarded witnesses[key]` at :83).
   - `011-phase-PA5R.md:85` still binds that file at `e8f81f84…`; it is now `527dc501…`.
   - The guards still pin exact bytes, but the provenance is misattributed. Either add a separate CI-repair successor link, or mark 011's line as superseded by 012.
2. **Hardening: the source identity leaves out the wheel build inputs** (root `pyproject.toml`, `uv.lock`, README) and the copied `tests/fixtures/pyrel_applications` (`accept_pyrel_applications_install.py:84-87`, `:125`). The wheel SHA and the matrix/answers hashes cover most of this, but `approval.json` itself is unbound.
3. **Hardening: a residual from F8.** The base install (line 108) and zensical's transitive dependencies (line 173) are still resolved without a lock. The resolved versions are now recorded, so this is a disclosed residual.
4. **Completeness: the learning-path test only mutates the pyrel lane** (`tests/test_pyrel_applications_install.py:61-71`). Two refusals have no red control:
   - the offline-lane check that native blocks are skipped (harness line 74);
   - the count-mismatch check (line 76).
5. **Completeness: a residual from F9.** The probe at line 169 doesn't catch a bare `tests` module, and the AST check is still a substring match.
6. **Completeness: a residual from F10.** `regate-red.txt` and `regate-green.txt` are one line each and record no command or selection. "2 failed, 13 deselected" is plausibly the two inventory cases, but the file doesn't show that.
7. **Completeness: the review count isn't documented.** `notes/phase-PA6-repair-review-prompt.md` (19:08, written for run D) exists, but no repair reading is retained. Record that it was never dispatched, so this reading is provably the second and last. The empty `claude-regate-review-raw.md` and `-stderr.txt` placeholders were created at 23:20.
8. **Completeness: the 012 record has gaps.**
   - Its gates are quoted, but no transcripts are retained.
   - The full-suite run in the local CI mirror on the final commit is still pending.
   - The doctor tests pass only with the venv on PATH.
   - 011's open-question row about the PA6 re-gate constants should be closed with a reference to the re-gate.

## Reading bounds

I read the spec, the initial review, 011, 012 and both commit diffs. I also read the harness and test in full, `install-regate-e.txt`, and the `e-*.json` files through `jq` summaries. I compared hashes with read-only `git show | shasum -a 256`.

I did not:
- run Python, tests, native tools or providers;
- open the run-E target under `/private/tmp`, so I didn't recompute the wheel SHA;
- open `.env` files, credentials or `.agents/skills`;
- read the rendered pages or the per-case native rows beyond the headers;
- edit anything. That includes the plan file: you asked for no edits, so this message is the whole report.
