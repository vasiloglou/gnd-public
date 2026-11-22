# Findings ledger: phase-RP5-r2

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
| F1 | The page said disconnected rule bodies are refused; only disconnected guarded antecedents are, and a derivation may join disconnected components | yes by reading `_guarded` (the `_connected` refusal) and the derivation path | completeness | fixed | RP5 phase commit | "disconnected guarded antecedents" |
| F2 | The page said a listed must-rule gives exit 4 without saying LQP `--compile` exits by compilation | yes by reading `compile_only` | completeness | fixed | RP5 phase commit | exit 4 is stated for checking a population; `--compile` is stated separately |
