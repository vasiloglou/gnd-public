# Findings ledger: phase-RP3-r5

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
| F1 | An Integer aggregate result compared with a Float or Number variable escaped the mixed-comparison refusal, because the guard's types held body variables only; PyRel then compared a rounded sum | yes: the guard accepted `sum-compared` with body-only types (direct call), and the export now refuses it | blocking | fixed | RP3 phase commit | the guard registers the aggregate result's type (`count` Integer, else its `of` type); `test_an_integer_sum_compared_with_a_number_value_is_refused` |
