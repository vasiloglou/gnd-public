# Findings ledger: phase-RP1-r3

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
| F1 | The r2 finite check covered fact rows only; an instances roster or a plan binding could still carry NaN or infinity into a Float cell | yes: a roster `[1e400]` was admitted by both readers; GND exits 3 | blocking | fixed | RP1 phase commit | the check moved into the shared `check_cell`, which rosters, fact cells and plan bindings all call; `test_a_non_finite_roster_value_is_refused_with_exit_3` (duckdb, lqp), `test_check_cell_refuses_non_finite_numbers_for_every_caller` (NaN, ±inf) |
| F2 | The record that r2-F1's deferral names did not exist, and RP3's spec and tests did not schedule the deferred regression | yes: no `003-phase-RP1.md`; no `anchor-beyond` in RP3's spec or tests | completeness | fixed | RP1 phase commit | `003-phase-RP1.md` written with the boundary; RP3 spec obligation row and T11, `test_rp1_deferred_float_anchors_beyond_2_53_are_refused` |
