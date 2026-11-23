# Findings ledger: phase-LH4-r1

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
| codex-F1 | an admissible or reason value that is an object, a list or a non-finite number passes validation; infinity then raises ValueError after the route | yes | blocking | fixed | 4428a24d | `test_r1_a_rule_value_must_be_a_json_scalar` (eight cases); failed before the fix. `_rule_value` admits JSON scalars only |
| codex-F2 | `reasons` is required, though §3 makes it optional | yes | hardening | fixed | 4428a24d | `test_r2_reasons_are_optional`; failed before the fix |

Convergence ledger:

| Round | Seats | Per-seat counts | Self-inflicted / total | Blocking / total | Severity ceiling | Verdicts |
|---|---|---|---|---|---|---|
| r1 | codex | 2 | 0 / 2 | 1 / 2 | blocking | CHANGES_REQUESTED |

No second round: both repairs are validation checks with their own
regression tests, and the convergence rules do not call for one. The
repairs carry no review opinion.
