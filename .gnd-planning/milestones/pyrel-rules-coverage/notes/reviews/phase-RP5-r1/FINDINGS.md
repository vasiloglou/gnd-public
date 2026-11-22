# Findings ledger: phase-RP5-r1

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
| F1 | The page and T3 omitted RP3's refusal of an Integer value written into a Float or Number head role | yes by reading; the new test prints it | completeness | fixed | RP5 phase commit | page entry, T3 row, `test_an_integer_min_into_a_number_head_prints_the_documented_refusal` |
| F2 | "one of these reasons" claimed a complete list; GND's other not-checked reasons (covers, dates, guarded filters, plan dynamic rules) were missing | yes by reading the report branches | completeness | fixed | RP5 phase commit | the list is the milestone's reasons, and a paragraph names the others |
| F3 | DuckDB-only reporting (date classification, missing covers, disconnected vacuity) was stated for both targets | yes by reading `_LQP_MAIN` and the reports | blocking | fixed | RP5 phase commit | each statement names the DuckDB version; the LQP version's behaviour is stated (disconnected: exit 4 where GND gives 2, as RP1's record says) |
| F4 | The plan command was shown without saying only the DuckDB version takes `--pre`/`--steps` | yes by reading `_LQP_MAIN` (one population argument) | completeness | fixed | RP5 phase commit | the page says the DuckDB version checks plans |
| F5 | Exclusive-or over role sequences was said to be refused; only multi-role sequences are | yes: `_exclusive_or` lowers single-role sequences | completeness | fixed | RP5 phase commit | "multi-role sequences" |
