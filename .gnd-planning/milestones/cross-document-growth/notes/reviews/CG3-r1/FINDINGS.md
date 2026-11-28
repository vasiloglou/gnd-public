# Findings ledger: CG3-r1

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
| F1 | Unrelated unsampled facts could be removed | yes | blocking | fixed | d69d106c | Only selected facts or facts participating in the object rewrite can be removed. |
| F2 | Object merge rewrote an old role to a third object | yes | blocking | fixed | d69d106c | Positive and negative public object-merge tests. |
| F3 | A removed declaration could lose unique cited evidence | yes | blocking | fixed | 6696d546 | Carry every original source location to a selected survivor or moved row. |
| F4 | Multiple spans on one row collapsed to the last | yes | blocking | fixed | 6696d546 | Located row identities now retain the sorted multiset of all spans for that row. |
| F5 | A concurrent model edit wedged an unstaged pending decision | yes | blocking | fixed | 6696d546 | Serialize recovery with a directory lock and retire stale intents only before the first evolution evidence leaf. Divergence after staging requires reconciliation. |
| F6 | A named parent directory alias failed root containment | yes | hardening | fixed | 6696d546 | Resolve the parent while preserving the leaf symlink check. |
| S1 | Deliberately rewritten journal could replace its own decision and digest | no | hardening | deferred | local trust boundary | The workspace and its durable journal are trusted local inputs. No claim of protection against a writer with full workspace access. |

One reviewer is one reviewer. The reviewer reconstructed and verified the original briefed implementation for its probes. The output is preserved verbatim in independent-review.md. The repairs have executable regression evidence and no second independent verdict.
