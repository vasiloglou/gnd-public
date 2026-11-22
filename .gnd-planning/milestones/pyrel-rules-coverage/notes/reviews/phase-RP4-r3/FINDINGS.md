# Findings ledger: phase-RP4-r3

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
| F1 | The name-collision check took any used `<object type>_any` relation for a generated universe, so a role-scoped rule over a fact type named `grade_any` was refused where GND decides it | yes: the `universe-named` fixture was refused before the fix; it now agrees with GND (1, 0, 2) | blocking | fixed | RP4 phase commit | universes are recorded where the lowering creates them (`_universe`), and both the rendering and the collision check read that record; a byte comparison of every fixture and example model against `f02c58d8` shows 573 accepted programs unchanged and none newly refused; `test_duckdb_program_agrees_with_gnd[universe-named-*]` (3) |
