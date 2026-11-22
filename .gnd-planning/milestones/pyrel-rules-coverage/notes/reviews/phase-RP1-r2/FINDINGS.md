# Findings ledger: phase-RP1-r2

One row per finding the review returned, under the reviewer's own id. Fill every cell:

- Reproduced: yes or no. A finding is believed only once it is reproduced against the bytes.
- Class: blocking, hardening or completeness, assigned here, not by the reviewer
  (review-convergence.md).
- Disposition: fixed, deferred, rejected or open.
- Repaired at: for a fixed finding, the commit or tag that holds the repaired bytes. Those
  bytes are unreviewed until a later round reads them; `review_tool.py status` says which.
- Notes: the regression test for a fixed finding, the target for a deferred one, the reason
  for a rejected one.

If the review returned no findings, replace the table with the line: No findings.

| Id | Finding | Reproduced | Class | Disposition | Repaired at | Notes |
|---|---|---|---|---|---|---|
| F1 | Integers beyond 2**53 in a Float anchor (9007199254740992, 9007199254740993) merge as binary floats, so a violating pair reads as a pass | yes: program exit 0 `eu OK`, GND exit 1 | blocking | deferred | — | target: phase RP3 (plan D6, the bound on Number and Float cells, predating RP1). RP3 adds `rp3/anchor-beyond.population.json` against `rp1/numeric-anchor.orm.json` as its regression; RP1's record states the gap in its boundary until then |
| F2 | The round-1 identity key calls `as_integer_ratio()` on an infinite float (`1e400`), an uncaught `OverflowError`, exit 1 | yes: traceback, exit 1 | blocking | fixed | RP1 phase commit | the reader refuses a non-finite number first (exit 3, as GND); `test_a_non_finite_number_is_refused_with_exit_3` (duckdb, lqp) |
