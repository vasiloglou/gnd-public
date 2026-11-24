# Findings ledger: phase-LR1-r2

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
| codex-1 | The guide says the constraint's id is at constraint_ref in the declaring file; for an include root the address is in the composed model | yes (tests/fixtures/lx1-flattening/expected.json: a root constraint at fact_type_constraints[0].constraints[0] is composed at fact_types[0].constraints[1]) | blocking | fixed | 60306a5c | step 2 says the address is in the composed model and maps it back through gnd flatten's gnd-flattening/1 origins; T1 follows that mapping to subject_has_one_label |
| codex-2 | The repaired witness list omits positional-array witnesses (ring) | yes (by the reviewer's population; T11 reproduces it) | hardening | fixed | 60306a5c | step 2 no longer enumerates shapes as a closed list; T11 lists a ring witness |
| codex-3 | T3 still accepts a field named only in prose | yes (round one codex-3, the deferred half) | hardening | deferred | n/a | residual in the phase record: no Markdown parser in the default environment; the code-read half is checked |
