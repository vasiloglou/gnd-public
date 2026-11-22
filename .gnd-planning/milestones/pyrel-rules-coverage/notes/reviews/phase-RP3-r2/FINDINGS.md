# Findings ledger: phase-RP3-r2

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
| F1 | A constant computed by arithmetic (`add(9007199254740992, 1)`) facing a Number variable passed the literal check, and PyRel computes it in binary | yes by reading: each literal is exact, their sum is not; the regression test confirms the refusal | blocking | fixed | RP3 phase commit | where a Float or Number value takes part, any arithmetic term is refused by name (and every literal bounded), in guarded comparisons, derivation comparisons and Float or Number head roles; `test_a_nested_computed_or_head_constant_beyond_2_53_is_refused[computed-beyond]` |
| F2 | A variable's type came from its first role only, so a Number role behind an Integer antecedent hid the context | yes by reading `_atom_types` (`setdefault`); the regression test confirms the refusal | blocking | fixed | RP3 phase commit | `_binary_variables` reads every role a variable fills; `[order-beyond]` |
