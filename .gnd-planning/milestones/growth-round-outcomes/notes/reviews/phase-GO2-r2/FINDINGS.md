# Findings ledger: phase-GO2-r2

Reviewer: codex (review helper, `--subject phase`, base `038f64dc`, reviewed
commit `9bf8bf3e`, the repair of round 1). One reviewer is one reviewer. The
round ran in a clean scratch checkout of `9bf8bf3e`, so later work in the
branch's worktree could not move its pinned bytes; its folder was copied back
and its logs had machine paths replaced (`review_tool.py sanitize`, then the
scratch checkout's prefix by hand). Nothing else in them changed.

Every finding was reproduced by a regression test (`test_r2_*` in
`tests/test_go2_operation_outcomes.py`) that fails with `outcomes.py` at
`9bf8bf3e` and passes on the repair.

| Reviewer | # | Finding | Reproduced | Class | Disposition | Repaired at | Notes |
|---|---|---|---|---|---|---|---|
| codex | F1 | Semantic validation names a role by `role_name` (`.roles[region]`); the role step read only a position | yes | blocking | fixed | the GO2–GO5 commit after `038f64dc`'s successors | R1 F3's input class was half repaired: an issue on a modified role left all rows `unassessed`. The step reads a position or a name; the meta-schema's identifier grammar (`^[a-z][a-z0-9_]*$`) keeps the two apart. `test_r2_f1_a_named_role_step_is_pinned_on_the_role_operation` |
| codex | F2 | A sample row (or a provenance entry) whose key is `object_type` was read as a reference | yes | blocking | fixed | as above | A false `dropped-with`. The dependency walk now follows the ORM meta-schema node of the operation's `after`, so a reference key is read only where the schema declares that property; sample rows and provenance are free-form there and never read. `test_r2_f2_a_sample_row_is_not_a_reference` |
| codex | F3 | `fact_types[].depends_on` was not read | yes | hardening | fixed | as above | The row was `unassessed`, not wrong. `depends_on` joins the reference properties. `test_r2_f3_depends_on_is_a_dependency` |
| codex | F4 | A constraint issue that names no one constraint operation fell back to blaming the operation that changed only the host | yes | blocking | fixed | as above | A false `refused-by-validation`. An issue with a constraint step is the constraint's: it is located through the constraint or not at all. `test_r2_f4_an_unlocated_constraint_issue_never_blames_its_host` |
| codex | F5 | The constraint index scanned its list on each insert: quadratic when many operations write one constraint | yes: 40,000 operations exceed 1 s at `9bf8bf3e` | hardening | fixed | as above | Indices arrive in order, so one comparison with the last suffices. `test_r2_f5_the_constraint_index_is_linear` |

Round 2 was the phase's last round (D8: a second round only if the first
blocks; there is no third). **The round-2 repairs carry no review opinion.**
The milestone's close review reads the whole diff.
