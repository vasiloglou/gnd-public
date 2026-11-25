# Findings ledger: issue-286-r2

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
| F1 | A sample row's free values could hold a nested `head` or `bind` key, which the walk took for a role-keyed container, so a previously accepted model was refused | yes | hardening | fixed | c24b06e8 | Not self-inflicted: it attacks the original change (rows read as role maps), not round 1's repair. The walk no longer enters `sample_population`. Regression: `tests/test_issue_286_role_keyed_maps.py::test_a_sample_row_value_is_data_whatever_it_holds` (four values, the reviewer's among them). Round budget, declared here before round 3: one more round over this repair, then stop |
