# Findings ledger: phase-LX4-r1

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
| F1 | Re-pinned forged extraction or rendering producer metadata passed verification | yes | blocking | fixed | a3463627 | Both variants of `test_repinning_cannot_make_forged_handoff_evidence_valid` reproduce that acceptance and verify exact fixture handoff bytes. |
| F2 | A changed indexed verbalization passed verification | yes | blocking | fixed | a3463627 | The verbalization variant reproduces acceptance and refuses after a fresh public extraction reconstructs every indexed artifact. |
| F3 | A forged unbound advisory could retain the expected filename | yes | blocking | fixed | a3463627 | The unexpected-report variant reproduces acceptance with a re-pinned false flag. Verification now joins the flag to file presence. |
| F4 | The original-population and sidecar copy counts were constant | yes | hardening | fixed | a3463627 | `test_layout_measures_copies_of_all_original_artifacts` changes the actual copies. The bounded census now groups each artifact's bytes by physical identity. |
| F5 | The temporal failure control reused old rebinds and the order test lacked a temporal failure input | yes | completeness | fixed | a3463627 | The exact plan pairing is a closure criterion. `test_temporal_constraint_distinguishes_checking_model` rebinds under the valid altered root, observes an actual violation, then pairs that root with a stale rebind and proves the earlier refusal. |
| F6 | Like-precision day values in the same year receive a year-comparison pass | yes | completeness | rejected | n/a | The 2020 January and December control returned pass. Plan §2 requires a publication-year comparison at equal precision, which the documented result implements. |
