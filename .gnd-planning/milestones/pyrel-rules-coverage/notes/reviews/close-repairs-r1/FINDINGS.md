# Findings ledger: close-repairs-r1

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
| F1 | A float literal compared with an Integer value (an Integer sum against `1e16`) compares in binary in PyRel and exactly in GND; program 1, GND 0 (predates the close) | yes: the export accepted `rp3/sum-float-literal` before the fix | blocking | fixed | close commit | `_refuse_float_next_to_integer` in the guarded and derivation comparison paths; `test_a_float_literal_compared_with_an_integer_sum_is_refused`; the all-model comparison shows no previously accepted program newly refused (plan §11 A13) |
| F2 | `close-results.md` cites `007-milestone-close.md`, which did not exist yet | yes | completeness | fixed | close commit | the close record is written in the same commit |
| F3 | The page still qualified empty-list vacuity of a disconnected join as DuckDB only | yes: the repaired LQP report prints `vacuous`, exit 2 | completeness | fixed | close commit | qualifier removed. F2 and F3 concern the close's own text, a self-inflicted ratio of 2/3, so review rounds stop here |
