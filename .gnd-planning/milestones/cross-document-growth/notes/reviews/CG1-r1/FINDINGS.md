# Findings ledger: CG1-r1

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
| F1 | Service applied a previously refused preview when evidence was added | yes | blocking | fixed | 9ffa5a89 | test_service_preserves_reviewed_refusal |
| F2 | Narrowed excerpt reused one source occurrence | yes | blocking | fixed | 9ffa5a89 | test_shorter_citation_for_same_tuple_is_redundant and disjoint-interval control |
| F3 | Several policy refusals share one diagnostic; outside-workspace error named the wrong input | yes | hardening | deferred | 9ffa5a89 | Paths now identify sample documents. The existing fact_types.modify cell continues to aggregate failed append checks. Its distinct reasons are documented in the evolution contract. |
| F4 | Missing included-target, repeated occurrence, recovery and public service coverage | yes | completeness | fixed | 9ffa5a89 | The focused file covers each named case through the CLI or service. |

The helper failed before a reviewer answered. The independent review used the project hook with the same brief on stdin. Its output is in independent-review.md. The reviewer verified the 15 hashes in the brief. The repairs are independently unreviewed. One round was budgeted.
