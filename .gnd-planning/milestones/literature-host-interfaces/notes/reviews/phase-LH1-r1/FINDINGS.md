# Findings ledger: phase-LH1-r1

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
| codex-F1 | the retained-file cap is not an upper bound: long roster strings and a padded saved table exceed it | yes | blocking | fixed | 5b098df4 | `test_r1_long_roster_strings_stay_under_the_recorded_cap`, `test_r1_a_padded_saved_table_stays_under_the_recorded_cap`; both failed before the fix. `_retained_cap` now bounds each file from the measured roster strings, header, input pins and saved files |
| codex-F2 | a lone surrogate or a 5,000-digit integer in an answer or receipt escapes `run()` as UnicodeEncodeError or ValueError | yes | blocking | fixed | 5b098df4 | `test_r2_an_unserializable_answer_refuses[surrogate]`, `[huge-int]`, `test_r2_an_unserializable_receipt_refuses`; failed before the fix. One serializer, `_canonical`, refuses with ExampleError for answers, receipts and every decoded caller input |
| codex-F3 | a structurally invalid saved `reviews.json` refuses only after the producer calls | yes | blocking | fixed | 5b098df4 | `test_r3_a_malformed_saved_review_refuses_before_any_call`; failed before the fix. The saved receipts' shape is checked at input time |
| codex-F4 | a required question superseded across sources is charged to its successor's source | yes | blocking | fixed | 5b098df4 | `test_r4_a_superseded_required_question_stays_with_its_own_source`; failed before the fix. `_stops` keeps each required question with its own section's source |

Convergence ledger, declared before round two:

| Round | Seats | Per-seat counts | Self-inflicted / total | Blocking / total | Severity ceiling | Verdicts |
|---|---|---|---|---|---|---|
| r1 | codex | 4 | 0 / 4 | 4 / 4 | P1 | CHANGES_REQUESTED |

Round budget: two rounds over the LH1 diff. Round two reads only the repair
(base 83de2846). Review stops after round two; it also stops if round two's
findings are more than half self-inflicted or none is blocking.
