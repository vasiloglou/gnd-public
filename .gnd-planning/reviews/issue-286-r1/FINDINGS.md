# Findings ledger: issue-286-r1

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
| F1 | Role-map detection keyed on `bind`, `head` and `sample_population` alone also matched those keys inside an object type's free description extras: one extra was newly refused, another newly hidden | yes | hardening | fixed | bca9398f | The walk stops at `description`, which the format reference says is never checked. Regression: `tests/test_issue_286_role_keyed_maps.py::test_a_description_is_never_read_as_syntax` (four extras, the reviewer's two among them). The notes state the change |
