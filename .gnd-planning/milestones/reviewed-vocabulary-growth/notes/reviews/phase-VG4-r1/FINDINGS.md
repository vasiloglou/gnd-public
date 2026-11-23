# Findings ledger: phase-VG4-r1

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
| codex-F1 | `documents: null` passes U1's first-document rule, but the first round's `source-document` add refuses a present non-list value, so such a root validates and cannot grow | yes | hardening | fixed | 18411c92 | Reproduced: validate exit 0 with `null`; the add raised "declares no source.documents to append to". Hardening: an absent key or `[]` is what the plan describes and what a host writes. Test `test_R1_F1_a_null_documents_value_keeps_U1`, failed before 18411c92. The rule admits only an absent key or an empty list |
