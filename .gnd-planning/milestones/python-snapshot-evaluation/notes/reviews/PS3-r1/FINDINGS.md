# Findings ledger: PS3-r1

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
| F1 | Derived negative input incorrectly classed uncovered in why-not | yes | blocking | fixed | 3084a159 | Why-not explains actual derivation. Covered absence is established separately by the proof kernel. |
| F2 | Uncovered negative branch suppressed an independent positive derivation | yes | blocking | fixed | 3084a159 | Alternative-clause and derived-negative cases now agree with the evaluator. |
| F3 | Two single-wire census expectations treated the new batch as a singleton | yes | blocking | fixed | 3084a159 | Pin the ordered two-result successor alongside independent old singletons. |
| F4 | Opaque negative-source branch lacked public-path evidence | yes | hardening | fixed | 3084a159 | Version-2 population with an opaque role yields unknown. Rebinding the previous proof yields unsupported in the independent kernel. |
