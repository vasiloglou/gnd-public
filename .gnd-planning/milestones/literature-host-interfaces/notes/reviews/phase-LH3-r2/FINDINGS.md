# Findings ledger: phase-LH3-r2

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
| codex-F1 | a missing model, population, policy or receipts file of a shaped call raises ArtifactError with the path | yes | hardening | fixed | f718b572 | `test_r5_a_missing_primary_input_refuses_without_its_path` (four cases); failed before the fix. Shaped calls refuse `input:read`; the packaged call is unchanged. Not self-inflicted: it is round-1 F2's other half, in code the repair did not touch |

Convergence ledger:

| Round | Seats | Per-seat counts | Self-inflicted / total | Blocking / total | Severity ceiling | Verdicts |
|---|---|---|---|---|---|---|
| r1 | codex | 4 | 0 / 4 | 2 / 4 | blocking | CHANGES_REQUESTED |
| r2 | codex | 1 | 0 / 1 | 0 / 1 | hardening | CHANGES_REQUESTED |

Round two was the last round declared. Its repair carries no review opinion.
