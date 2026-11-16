# Findings ledger: phase-LD2-r1

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
| F1 | Inverse units pass the time selector | yes | blocking | fixed | 55ffa8ea | The public checker red run accepted Unicode minus and superscript rate spellings. The repaired boundary control rejects both. |
| F2 | A quantity fragment following an operator can pass | yes | blocking | fixed | 55ffa8ea | Public check accepted exponent and fractional tails on the reviewed bytes. Regressions now exercise adjacent and spaced operators, including Unicode spacing and range punctuation. |
| F3 | Installed wheel verification was unavailable in the reviewed record | yes | hardening | fixed | 55ffa8ea | The review packet lacked the separately executed installed-wheel evidence. T7 now identifies the installed command route. The completion record binds the rerun over repaired bytes. |
| F4 | Proof mutation checks only a nonzero exit and one cell | yes | hardening | fixed | 55ffa8ea | Check exit 1 and proof-invalid independently for coefficient, scale and unit mutations. |
