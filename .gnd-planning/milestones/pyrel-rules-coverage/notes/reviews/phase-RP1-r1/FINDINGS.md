# Findings ledger: phase-RP1-r1

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
| F1 | Rows equal by GND's numeric identity (`1`, `1.0`) pass the reader's JSON duplicate guard and merge in the set, so a repeated fact reads as a pass | yes: program exit 0 `eu OK`, GND exit 1; the same for inline uniqueness on a Float role (predates RP1) | blocking | fixed | RP1 phase commit | the reader keys rows by GND's identity (`as_integer_ratio`); `test_numerically_repeated_facts_are_refused_not_merged` (external, inline) |
| F2 | A disconnected rule's vacuity read the fact lists, not the computed view of semiderived types | yes: program exit 4 not checked, GND exit 2 vacuous | blocking | fixed | RP1 phase commit | reads `computed:<ref>` as the main path does; `test_disconnected_vacuity_reads_computed_semiderived_relations` |
| F3 | The LQP program's `main` let a refused cell escape as a traceback, exit 1 | yes: exit 1 with `ValueError` (predates RP1 for every cell refusal) | blocking | fixed | RP1 phase commit | returns 3 as the DuckDB version does; `test_lqp_refuses_a_non_string_external_id_with_exit_3` |
