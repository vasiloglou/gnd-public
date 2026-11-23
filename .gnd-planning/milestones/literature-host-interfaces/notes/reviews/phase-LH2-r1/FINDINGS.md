# Findings ledger: phase-LH2-r1

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
| codex-F1 | a live receipt within the response cap at run time exceeds it on replay once its two digests are added | yes | blocking | fixed | 9df661c8 | `test_r1_a_receipt_at_the_response_cap_replays`; failed before the fix (the run kept a receipt its replay refused). The run now holds the whole receipt, digests included, to the cap |
| codex-F2 | a malformed `budget_bytes` or `scenario` is checked only after run files are read | yes | hardening | fixed | 9df661c8 | `test_r2_top_level_settings_refuse_before_any_run_file` (two cases); failed before the fix |
| codex-F3 | a retained payload of the wrong shape raises KeyError | yes | hardening | fixed | 9df661c8 | `test_r3_a_malformed_retained_payload_refuses` (three cases); failed before the fix. Predates the phase in the /1 reader |

Convergence ledger:

| Round | Seats | Per-seat counts | Self-inflicted / total | Blocking / total | Severity ceiling | Verdicts |
|---|---|---|---|---|---|---|
| r1 | codex | 3 | 0 / 3 | 1 / 3 | blocking | CHANGES_REQUESTED |

No second round: the spec's budget allows one only if the convergence rules
call for it, and they do not (one blocking finding, fixed locally with its
regression test). The repairs carry no review opinion.
