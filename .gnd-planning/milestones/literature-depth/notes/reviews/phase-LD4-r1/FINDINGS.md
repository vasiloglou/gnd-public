# Findings ledger: phase-LD4-r1

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
| F1 | Two dependency edges pointed in the reverse direction | yes | blocking | fixed | `238e8ce8` | The graph now follows source resolution to canonical decisions and proposal to evolved model. The regression asserts expected consumers independently of the graph. |
| F2 | Corroboration replay required the unrelated whale-a source | yes | blocking | fixed | `238e8ce8` | Each replay rechecks its own source, old judgment and witness against a separately pinned reviewed resolution and rule. The test removes each source in turn. |
| F3 | The migration depended on untracked prior artifacts | yes | blocking | fixed | `238e8ce8` | The after manifest pins exact prior composition and population bytes. Changed and missing predecessor inputs stale dependent migration and claims without staling independent supports. |
| F4 | The rule comparison might accept changed vocabulary | no | hardening | rejected | — | Public `gnd check --baseline-model` refuses exit 3 for changed vocabulary. The negative fixture demonstrated this both before and after the repair. The value-rule comparison is a separate selected control in D6. |
| F5 | The snapshot name alone staled scoped absence | yes | blocking | fixed | `238e8ce8` | The covered predicate's actual changed occurrences supply the shared LD3 worklist key. An unrelated-only edit preserves coverage and yields an empty revisit. |
| F6 | Any additive policy refusal could satisfy the control | yes | hardening | fixed | `238e8ce8` | A wrong-operation refusal passed in the reviewed candidate. The repair checks the exact operation, cell and predicate reference. |
