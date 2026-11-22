# Findings ledger: phase-RP4-r4

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
| F1 | A plan's `create` effect rendered its object type's universe without recording it, so a fact type of that name was redeclared and the program failed to build (predates RP4: `f02c58d8` renders the same model) | yes: `create-named` rendered before the fix, at the base too; now refused by name | blocking | fixed | RP4 phase commit | create effects record their universe before the collision check, and rendering reads the record alone; byte comparison again 573 accepted programs unchanged, none refused; `test_a_fact_type_named_like_a_plan_created_universe_is_refused` |
