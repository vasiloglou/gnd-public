# Findings ledger: phase-SI3-r1

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
| F1 | A different logical key could produce a wrong link | yes | blocking | fixed | 70f7c696 | Unit versus direct and same-kind different-target fixtures refuse the mismatch. Removing only the target comparison reproduces a false link. |
| F2 | The composite-parent test did not exercise relational mapping | yes | completeness | fixed | 70f7c696 | Added a fact played by the subtype and asserted the incompatible logical key is explicitly listed. |
| F3 | A single unit-based parent did not supply the new identifier | yes | hardening | fixed | 70f7c696 | Before the repair the valid child lacked identify_by. The successor fixture checks the inherited Decimal and the resulting link. |
