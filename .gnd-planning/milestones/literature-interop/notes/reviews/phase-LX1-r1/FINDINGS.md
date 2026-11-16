# Findings ledger: phase-LX1-r1

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

| F1 | Similar output-overlap checks | no | completeness | rejected | n/a | Evolve's helper lives in a separate lane and checks a different input set. A dependency that disappears after model admission should abort publication, since the output would be stale. The review did not reproduce a wrong outcome within LX1. |
| F2 | Composed-address order is described without a comparator | yes | completeness | rejected | n/a | The order can be reproduced by comparing [10] and [2] lexically. The current producer and verifier agree. The normative text now states Unicode code-point ordering as a clarification with unchanged behavior. |
