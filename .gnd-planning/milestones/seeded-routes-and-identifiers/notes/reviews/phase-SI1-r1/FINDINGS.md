# Findings ledger: phase-SI1-r1

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
| F1 | Re-entry refusal label missing from extract and PyRel | yes | hardening | fixed | 8acc7b29 | Injected re-entry control failed on eight export/extract cases before repair. Each route now reports both rule IDs and writes no artifact. |
| F2 | Representation format omitted rooted witness and replay | yes | completeness | fixed | 8acc7b29 | The normative paragraph control failed before both routes were documented. |
| F3 | Timing fixture scaled only object types | yes | completeness | fixed | 8acc7b29 | The prior fixture had one constraint. The revised fixture verifies 1,001 constraints in the 2,002-type timed projection. |
