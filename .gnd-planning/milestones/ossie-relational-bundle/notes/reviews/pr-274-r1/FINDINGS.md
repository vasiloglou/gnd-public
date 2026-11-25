# Findings ledger: pr-274-r1

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
| F1 | `close-delta.md` line 21 says plan r2 upper-cased every name; r2 states no quoting rule. | yes: plan r2 at `f5462783` has no such sentence, and amendment A14 says so | completeness (wording in a planning note; no runtime effect) | fixed | `9ba319d1` | On the owner's word ("yes" to fix and push, 2026-11-25). The sentence now names OB3's spec (E5) and normative text. The repaired line is unreviewed. |
