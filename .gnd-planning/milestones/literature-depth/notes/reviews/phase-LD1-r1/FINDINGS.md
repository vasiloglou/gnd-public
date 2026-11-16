# Findings ledger: phase-LD1-r1

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
| F1 | Fixed percent trigger | yes | blocking | fixed | 11493f45 | Explicit points and relative change, and test_percent_trigger_detects_a_point_recognized_as_percent. |
| F2 | Float control cannot establish fractional Number support | yes | blocking | fixed | 11493f45 | Checked fractional Number refuses, integral Number proves and replays in test_decimal_observation_tracks_the_checked_value. |
| F3 | Compatible time-unit control absent | yes | blocking | fixed | 11493f45 | test_quantity_observations_are_discriminating checks the reported and equivalent time spans and the wrong-dimension span. |
| F4 | Re-pinning the support digest admits a substituted citation | yes | blocking | fixed | 11493f45 | test_source_support_binding_refuses_tampering[citation] re-pins the support bytes and refuses using the independently pinned question roster. |
| F5 | Identity and relationship control does not establish an occurrence | yes | hardening | fixed | 11493f45 | The stable subject coordinate resolves against the checked population. Relation tests pin all three predicates and translate a moved component to an unknown answer. |
| F6 | Missing-score comparison omitted from the fixture | yes | hardening | fixed | 11493f45 | test_experiment_comparisons tests a missing score with complete context. |
| F7 | Report uses a fixed checked decimal | yes | hardening | fixed | 11493f45 | Reproduced a stale 0.002 report with a 0.003 fixture. test_decimal_observation_tracks_the_checked_value binds the observation to the checked value. |
