# Findings ledger: issue-286-r3

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

No findings.

After the round, one notes bullet was made more precise: it names the head roles `bind` and `head` beside `source` and `provenance`, which the round's own comparison found and `tests/test_issue_286_role_keyed_maps.py::test_a_date_term_in_a_head_is_found_whatever_the_role_is_called` covers. That sentence carries no review opinion.
