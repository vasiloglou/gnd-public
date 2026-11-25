# Findings ledger: phase-SI1-r2

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
| F1 | Two existing link multiplicities can offset in the aggregate count | yes | hardening | deferred | n/a | The working-tree reviewer reproduced this with an in-memory mutation. Carry per-edge multiplicity to packaged skill link-guard maintenance. Exact edge membership remains asserted. |
| F2 | The named SI1 edge has no provenance comment | yes | completeness | rejected | n/a | This ledger and the phase repair record cite the guide paragraph and normative target. The test constant already names SI1. |
