# Findings ledger: phase-LH3-r1

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
| codex-F1 | handles are Python keys, so `true` and `1` are one assertion | yes | blocking | fixed | 04cf7bef | `test_r1_a_boolean_handle_is_not_a_number`; failed before the fix. Handles are keyed with `gnd.synth.identity.scalar_identity`, the public twin of the checker's `gnd.values._identity_key`; `test_r1_one_and_one_point_zero_are_one_number` pins the other half |
| codex-F2 | a malformed `includes` raises TypeError; a missing include raises ArtifactError | yes | hardening | fixed | 04cf7bef | `test_r2_a_malformed_include_list_refuses` (four cases, two of which failed before), `test_r2_a_missing_include_refuses`; failed before the fix |
| codex-F3 | a legal format-version-2 opaque value refuses the whole call | yes | blocking | fixed | 04cf7bef | `test_r3_an_opaque_value_is_an_ordinary_value`; failed before the fix. Row values are the population loader's to judge (R0.7); the walk keys any value |
| codex-F4 | `covers` searched a list for each fact type, quadratic in the fact types | yes | hardening | fixed | 04cf7bef | `test_r4_covers_is_linear_in_the_fact_types` (40,000 fact types, 3.4 s before, under 1.5 s after) |

Convergence ledger, declared before round two:

| Round | Seats | Per-seat counts | Self-inflicted / total | Blocking / total | Severity ceiling | Verdicts |
|---|---|---|---|---|---|---|
| r1 | codex | 4 | 0 / 4 | 2 / 4 | blocking | CHANGES_REQUESTED |

Round budget: two rounds over the LH3 diff. Round two reads only the repair
(base dcd3a61c) and is the last.
