# Findings ledger: phase-SI2-r1

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
| F1 | Eight-case review fixture exceeded the initial seven-case ledger | yes | completeness | fixed | 9e42b37c | Added the exact re-run with six red and two green baseline cases. |
| F2 | The chosen preferred key can be unmatchable | yes | completeness | fixed | 9e42b37c | Tested an admitted nested-composite case and corrected its missing normative behavior. |
| F3 | Timing fixture does not establish linear scaling | yes | completeness | rejected | — | The stated gate is a five-second bound at one scale. It carries no linearity claim. |
