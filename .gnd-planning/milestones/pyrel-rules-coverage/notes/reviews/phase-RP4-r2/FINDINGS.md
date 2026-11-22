# Findings ledger: phase-RP4-r2

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
| F1 | A role-scoped domain over a fact type whose name ends in `_any` was taken for an object-type universe, so the export failed (`unknown object type`) where GND decides the rule | yes: the `any-named` fixture raised before the fix; it now agrees with GND (1, 0, 2) | blocking | fixed | RP4 phase commit | universes exclude relations that are fact types; `test_duckdb_program_agrees_with_gnd[any-named-*]` (3) |
