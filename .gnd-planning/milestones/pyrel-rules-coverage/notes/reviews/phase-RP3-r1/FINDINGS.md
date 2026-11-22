# Findings ledger: phase-RP3-r1

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
| F1 | The D6 derivation guard called `types.get(t)` on a function term, a `TypeError` that broke every integer-arithmetic derivation | yes: `int-arithmetic` (score Integer) raised `TypeError`; it exported at `6b9dc077` | blocking | fixed | RP3 phase commit | the guard reads variables only (`_term_variables`); `test_integer_arithmetic_still_exports`, and `test_inexact_arithmetic_is_refused_by_name[misc]` passes again |
| F2 | Constants nested in a function term, and constants in a derived head, bypassed D6 | yes: `nested-beyond` and `head-beyond` exported | blocking | fixed | RP3 phase commit | every literal at any depth is checked when a Float or Number variable takes part; head constants against the head's role types; `test_a_nested_or_head_constant_beyond_2_53_is_refused` (2) |
| F3 | Facts of an embedded reference population skipped the cell checks | yes by reading: the merge ran after the validation loop; the regression test confirms the repair (program 3, GND 1) | blocking | fixed | RP3 phase commit | reference facts and rosters take `check_cell`; `test_reference_facts_beyond_2_53_are_refused` |
| F4 | The changed message broke two existing refusal tests | yes: `fl`, `num` failed in `test_pyrel_rules_derivations.py` | blocking | fixed | RP3 phase commit | expectations updated to `arithmetic on Float or Number values`; the cumulative lane now includes that file's run |
