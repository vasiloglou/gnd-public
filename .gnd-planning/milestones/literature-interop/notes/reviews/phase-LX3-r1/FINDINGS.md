# Findings ledger: phase-LX3-r1

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
| F1 | Equality could impose a catalog dependency on candidate rows | yes | blocking | fixed | 9e1c1d29 | `test_catalog_is_refused_before_invalid_manifest[equality]` reproduced the incorrect precedence and passes with bidirectional validation. |
| F2 | A digest-current invalid catalog was reported as stale | yes | hardening | fixed | 9e1c1d29 | `test_invalid_catalog_with_current_pin_is_input_invalid` covers both authored root shapes, production and replay. |
| F3 | A possible candidate-lineage omission on an ambiguous verdict | no | hardening | rejected | n/a | Neither checked model-level verdict produced an occurrence coordinate for this branch. There was no reproducible counterexample to the attribution rule. |
