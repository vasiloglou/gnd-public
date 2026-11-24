# Findings ledger: phase-GO2-r1

Reviewer: codex (review helper, `--subject phase`, base `81760521`, reviewed
commit `f7ec03b4`). One reviewer is one reviewer. `review.md` and `review.log`
had this machine's paths replaced by `review_tool.py sanitize`; nothing else
in them changed.

Every finding was reproduced by a regression test that fails on the reviewed
bytes of `src/gnd/evolve/outcomes.py` and `src/gnd/evolve/cli_service.py`
(both swapped back to `f7ec03b4`, the rest of the tree unchanged) and passes on
the repair.

| Reviewer | # | Finding | Reproduced | Class | Disposition | Repaired at | Notes |
|---|---|---|---|---|---|---|---|
| codex | F1 | A non-list value in `after` (`roles: 1`) turns a validation refusal into exit 70 once outcomes are on | yes: `TypeError` from `_depends_on` at `f7ec03b4` | blocking | fixed | the GO2 r1 repair commit after `038f64dc` | The option must not move a refusal (GO2-C1). Dependencies are now read by one total walk of the `after` value (`_needs`): mappings and sequences are walked, every other shape adds nothing. `test_r1_f1_a_non_list_value_in_after_is_still_a_validation_refusal` |
| codex | F2 | A refused constraint embedded in an added fact type leaves that operation `admitted` | yes: `["admitted", "admitted"]` at `f7ec03b4` | blocking | fixed | as above | A wrong `admitted` is a false outcome, and GO3 would keep the operation. The index now holds every constraint an operation writes, a constraint operation's `after` and each constraint in a fact-type `after`. `test_r1_f2_a_refused_embedded_constraint_refuses_its_fact_type` |
| codex | F3 | A validation issue is pinned on the operation that created a valid host, not on the role operation that made it invalid; two modifications of one element blame the first | yes: both at `f7ec03b4` | blocking | fixed | as above | GO2-C2 ties a refusal only to the operation that caused it. Element blame now reads only the operations that change the element's own entry (element and role operations); a `.roles[i]` step picks the role's own operation; two candidates with nothing to tell them apart locate nothing, so the row stays `unassessed`, never a guess. `test_r1_f3_an_issue_is_pinned_on_the_role_operation_not_on_its_host`, `test_r1_f3_two_changes_to_one_element_locate_nothing` |
| codex | F4 | An issue at `$.operations[i]` is never located | yes: `{}` at `f7ec03b4` | completeness | fixed | as above | The row was `unassessed`, not wrong. The located collections are now read from `ElementLocator`'s own collection literal. `test_r1_f4_an_added_operation_is_located` |
| codex | F5 | An operation that needs an element added later in the proposal is not dropped with it | yes: `unassessed` at `f7ec03b4` | hardening | fixed | as above | `dropped-with` is now a closure over the whole proposal (one pass from each refused addition through the operations that need it), not over the operations before it. `test_r1_f5_a_dependent_before_its_refused_role_player_is_dropped` (service case and a three-step chain) |
| codex | F6 | A model-level value constraint on a refused object type is not dropped with it | yes: `unassessed` at `f7ec03b4` | hardening | fixed | as above | The walk reads every key the ORM meta-schema uses to name an element (`object_type`, `value_type`, `supertype`, `subtype_of`, `subtypes`, `objectified_as`, `fact_type`) at any depth. `test_r1_f6_a_value_constraint_on_a_refused_object_type_is_dropped` |
| codex | F7 | An include-analysis refusal does not write the requested outcome report | yes: no file at `f7ec03b4` | blocking | fixed | as above | The CLI's include-analysis branch returned before the report writer. It now writes the report after the radius, and the report path joins the outputs the include inputs must not be. `test_r1_f7_an_include_analysis_refusal_writes_the_requested_report` |
| codex | F8 | `[id=...]` issue paths rescan the candidate collection: quadratic | yes: 5.2 s for 20,000 issues at `f7ec03b4`, 0.15 s after | hardening | fixed | as above | Each collection's id map is built once per call (`_Candidate`). `test_r1_f8_id_paths_are_linear` |

Four findings are blocking, so the phase's budget gives a second round, which
reads the repaired bytes (`phase-GO2-r2`).
