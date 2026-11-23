# Findings ledger: phase-LH1-r2

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
| codex-F1 | a long saved receipt still exceeds the recorded cap, inside payload-4 | yes | blocking | fixed | 59fd62f0 | `test_r5_a_long_saved_receipt_refuses_before_any_call`; failed before the fix. Saved receipts are held to `response_bytes` at input time, so the payload-4 bound holds. Self-inflicted: it attacks round 1's bound |
| codex-F2 | an empty basis or a malformed excerpt digest in a saved receipt refuses only after the calls | yes | blocking | fixed | 59fd62f0 | `test_r6_a_saved_receipt_knowably_wrong_refuses_before_any_call` (four cases); failed before the fix. Decision, basis, excerpt digest and digest shape are checked at input time. Self-inflicted: it attacks round 1's preflight |
| codex-F3 | a source or span that is not UTF-8 raises UnicodeDecodeError | yes | hardening | fixed | 59fd62f0 | `test_r7_a_source_that_is_not_utf8_refuses` (two cases); failed before the fix. Predates the phase (the packaged code had it) |
| codex-F4 | a roster row missing `superseded_by` or `selection` raises KeyError | yes | hardening | fixed | 59fd62f0 | `test_r8_a_roster_row_missing_a_key_refuses` (four cases, two of which failed before the fix). Predates the phase |

Convergence ledger:

| Round | Seats | Per-seat counts | Self-inflicted / total | Blocking / total | Severity ceiling | Verdicts |
|---|---|---|---|---|---|---|
| r1 | codex | 4 | 0 / 4 | 4 / 4 | P1 | CHANGES_REQUESTED |
| r2 | codex | 4 | 2 / 4 | 2 / 4 | P1 | CHANGES_REQUESTED |

Round two was the last round declared. Its repairs carry no review opinion;
the phase record says so.
