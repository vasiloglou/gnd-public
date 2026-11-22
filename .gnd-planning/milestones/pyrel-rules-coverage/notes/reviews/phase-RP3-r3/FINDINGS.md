# Findings ledger: phase-RP3-r3

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
| F1 | An aggregate result written into a Float or Number head role escaped D6: a sum of Integers beyond 2**53, or of Floats, is computed in binary by PyRel and exactly by GND | yes by reading `_clause_lines` (binary contexts came from the body only); the regression test confirms the refusal | blocking | fixed | RP3 phase commit | `_refuse_inexact_head`: a Float or Number head role takes a Float or Number value, a count, a min or max of such values, or a constant; a sum over or into one is refused; the result joins the binary contexts for comparisons. `test_a_sum_into_a_number_head_is_refused`, `test_a_count_into_a_number_head_still_exports` |
