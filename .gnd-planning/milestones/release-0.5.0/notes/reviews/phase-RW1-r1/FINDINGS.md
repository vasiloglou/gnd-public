# Findings ledger: phase-RW1-r1

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
| F1 | The PyRel block omits a newly refused export: an Integer `min` or `max` (and, as reproduced here, `sum`) written into a `Float` role, which 0.4.0 exported | yes | completeness | fixed | 1d8536de | Reproduced with 0.4.0 from the package index and this tree at `cc8cdb65`: exit 0 against exit 3 for `min`, `max` and `sum` in both modes (`evidence/RW1/old-version-probes.md`, the section added 2026-11-25). The notes sentence now names the refusal and the 0.4.0 difference. No regression test: the notes' wording for PyRel has no test, and the refusal itself is tested by the pyrel-rules-coverage suites |
