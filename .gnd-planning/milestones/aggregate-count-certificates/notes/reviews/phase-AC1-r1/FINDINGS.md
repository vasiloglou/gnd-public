# Findings ledger: phase-AC1-r1

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
| F1 | Deep YAML snapshots reach the shared loader before a depth check. | yes | blocking | fixed | `2f906af055386ca2e7dc0e83c0be039cdb7b9061` | The two cases of `test_deep_yaml_is_refused_before_loading_snapshot` failed before the repair. Both prove bounded intake after the repair, including stale-binding precedence and replay with a current binding. A 16,000-level YAML model and population each exceeded five seconds on the original CLI. Both returned exit 3 inside two seconds on the repaired CLI. |
| F2 | Shared source scan creates a common implementation dependency between producer and replay. | yes | hardening | rejected | — | The approved plan explicitly requires one bounded scan policy. The independent frozen roster, checker differential and import-blocking replay controls address the shared dependency within this scope. The additional two-role model exercised Boolean grouping and an ordered Integer contribution against the existing evaluator. |
