# Findings ledger: phase-IR2-r1

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
| F1 | --out naming a regular file exited 11, not 74 | yes | blocking | fixed | 1311ae6d | tests/test_ir2_flatten.py::test_F1_output_path_that_is_a_file_exits_74, red on the reviewed bytes |
| F2 | the flatten hint changed other consumers' temporal refusal for an include root | yes | hardening | fixed | 1311ae6d | tests/test_ir2_flatten.py::test_F2_other_consumers_keep_the_historical_temporal_message, red on the reviewed bytes |
| F3 | a NUL in --out raised an uncaught ValueError | yes | hardening | fixed | 1311ae6d | tests/test_ir2_flatten.py::test_F3_unrepresentable_output_path_exits_74, red on the reviewed bytes |
