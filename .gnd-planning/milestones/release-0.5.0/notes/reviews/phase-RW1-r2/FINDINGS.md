# Findings ledger: phase-RW1-r2

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
| F1 | The repaired sentence says a model that writes an `Integer` value into a `Float` or `Number` role is refused, but an Integer `count` written there is accepted | yes | completeness | fixed | 5faddf3d | Reproduced: `count-into-number.orm.json` exports with exit 0 in both modes, and so does the same model with a `Float` destination, on this tree and on 0.4.0 (`evidence/RW1/old-version-probes.md`). The sentence now follows `_refuse_inexact_head`: a value from an `Integer` role, or an `Integer` `min` or `max`, is refused; a count or a constant is accepted. Self-inflicted: the text was written by round 1's repair. No regression test, as for round 1 |
