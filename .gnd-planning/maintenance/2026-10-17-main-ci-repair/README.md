# Main CI repair, 2026-10-17

The owner asked for this repair after a local replay of `.github/workflows/development.yml`
on `main`. The replay found 7 regression failures and a failing release-acceptance job that
predate the `transition-check-performance` milestone. In each case, already-merged work had
changed pinned code without updating the matching pin record. Each fix below uses the
repository's own mechanism and names the commit it accounts for. No pin is loosened and no
check is removed.

| Failure | Cause | Repair (mechanism) |
|---|---|---|
| `test_rf1_pin_harness::test_mutation_table_rows_of_their_own` | `analytics-m3-repairs` phase 8 (`65b6de0`) changed the first statement of `population._schema_issues`, so the RF1 mutation snippet no longer occurs | A retarget row in `code-refactoring/evidence/RF9-ci-repair/mutation-retargets.json`. The original `old`, `new` and `expect_red` meaning is kept; the row adds the new snippet and its reason |
| `test_rf4_peripheral` ×2 (`_run_check_raw` body and the live successor control) | `analytics-m3-repairs` phase 11 (`512ed63`) changed `_run_check_raw` after its recorded CS1 successor | The RF4 row's `after` and `reason` are extended in `compiled-snapshot-obligations/evidence/CI/source-successors.json` |
| `test_rf6_packages[gnd.checker.check]` | The same commit, `512ed63`, changed `checker.check` | The RF6b row's `after` and `reason` are extended in the same registry |
| `test_rf6_query_policy` ×2 (dynamic inventory) | Merged work after PA5R added 376 dynamic-syntax occurrences (334 distinct rows), and removed 5. Sources: `analytics-m3-repairs` phases 9–12, `pyrel-agent-loop` PL12–PL16, `transition-check-performance` TP3 | A new chained, authenticated delta, [dynamic-query-successor.json](dynamic-query-successor.json), whose predecessor is the PA5R delta, plus `tests/support/pyrel_application_successors.py`, which reads that link. This is a census only; the exact query policy is unchanged and already passing |
| `test_rf7_structure::test_complete_routing_and_dirty_controls` | `analytics-m3-repairs` phase 12 (`35af996`) added `population_shape.py`, which calls `json.loads` directly, against the RF7 JSON-routing rule | **Code fix:** `population_shape._prepared` decodes through `gnd.input_policy.loads`. Its input is the module's own `json.dumps(..., allow_nan=False)` output, so results are unchanged; the population-shape and schema tests pass |
| `test_release_acceptance` (installed job) | `uv build` writes a `.gitignore` into every output folder it creates, and `verify_files` treated it as an unexpected artifact. This fails identically on `main` | `verify_files` ignores exactly that file name. Every listed artifact is still hashed and counted |

## Pinned evidence files touched (disclosed)

- `code-refactoring/evidence/RF9-ci-repair/mutation-retargets.json` is pinned by
  `code-refactoring/017-phase-RF9-ci-repair.md`. One row is appended; no existing row changes.
- `compiled-snapshot-obligations/evidence/CI/source-successors.json` is pinned by
  `compiled-snapshot-obligations/007`. Two existing rows have `after` and `reason` extended,
  which is the only update the registry allows (one row per identity, chained).

Historical records keep their original hashes. They describe the bytes they were written
against.

## Verification

See the PR description for the exact commands and results.
