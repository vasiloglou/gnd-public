# Findings ledger: PS1-r1

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

| Id | Finding | Reproduced | Class | Disposition | Repaired at | Notes |
|---|---|---|---|---|---|---|
| F1 | Null derivation list crashes customer projection | yes | blocking | fixed | 53f71074 | Real approvals reports in customer and internal modes, both failed before repair. |
| F2 | Anchored options combined with vacuity | yes | blocking | fixed | 53f71074 | Two pre-load refusal regressions failed before repair. |
| F3 | CLI-derived rule-ID error mentions a flag the Python caller did not use | yes | completeness | documented | 53f71074 | Reference explains model classes and ordinary wire restriction. Original CLI diagnostic remains shared. |
