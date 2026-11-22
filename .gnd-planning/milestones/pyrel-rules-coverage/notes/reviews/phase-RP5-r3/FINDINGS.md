# Findings ledger: phase-RP5-r3

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
| F1 | The round-2 sentence on exit 4 did not say a violation takes precedence (exit 1) | yes by reading `band` and `lqp_report` | completeness | fixed | RP5 phase commit | "exit 4 when the program checks a population and no rule is violated (a violation gives exit 1)"; the finding concerns this phase's own round-2 edit, a self-inflicted ratio of 1/1, so review rounds stop here |
