# growth-round-outcomes · close results

At the head of pull request 261 (branch `claude/growth-round-outcomes-specs`),
with `origin/main` `fe5fdf72` merged. GO1 merged earlier by its own pull
request. Each criterion is the plan r4 §4 text; the evidence is the named
tests, all in the focused lane (936 passed) unless marked.

## GO1 (#228): one parse per model text per reader

| Criterion | Result | Evidence |
|---|---|---|
| GO1-C1 | `apply` 2 parses (was 22), `preview` 2 (was 6), at two sizes and for `.json` | `tests/test_go1_evolve_parse_once.py` T1 |
| GO1-C2 | identical bytes, messages and exits, scope on and off, seven cases | T2, T4 |
| GO1-C3 | the write check at every scope close over the lane | autouse fixture in `tests/conftest.py`, T3 |
| GO1-C4 | stale model refused as today; a second command parses again | T4, T6, T7 |
| GO1-C5 | ratio 0.31 at 604 object types (bound 0.6), recorded | `evidence/GO1/t8-ratio.json` |
| GO1-C6 | the #228 table at the head | `002-phase-GO1.md` |

## GO2 (#227): an outcome for every operation

| Criterion | Result | Evidence |
|---|---|---|
| GO2-C1 | no preview; the report names all four, the refusal and exit unchanged | `tests/test_go2_operation_outcomes.py::test_t1_*` |
| GO2-C2 | each verdict word reached; two faults in two operations both named | `test_t2_*` |
| GO2-C3 | a preview without the option is byte-identical, digests included | `test_t4_without_the_flag_nothing_changes` |
| GO2-C4 | no value reaches a row | `test_t6_no_constraint_value_reaches_an_outcome` |
| GO2-C5 | `apply` refuses a report as its preview | `test_t5_apply_refuses_an_outcome_report` |
| GO2-C6 | a preview with rows applies; an edited row exits 11 | `test_t7_apply_replays_the_outcomes_setting` |
| GO2-C7 | an operation no later gate reached is `unassessed`, gates named | `test_t2_unassessed_names_the_gates_not_run`, `test_t3_*` |

The locator (`src/gnd/evolve/outcomes.py`) was repaired twice by diff review:
13 findings, each with a `test_r1_*` or `test_r2_*` case.

## GO3 (#227): the admitted part as a new proposal

| Criterion | Result | Evidence |
|---|---|---|
| GO3-C1 | three operations kept; previews and applies, exit 0; also on a seeded root | `tests/test_go3_narrowed_proposal.py::test_t1_*` |
| GO3-C2 | a constraint on a refused fact type dropped and named | `test_t2_*` |
| GO3-C3 | own id, `narrowed_from`, original bytes kept; original preview refused as today before, stale (11) after | `test_t3_*` |
| GO3-C4 | nothing kept: `None` and a reason per operation | `test_t4_*` |

## GO4 (#227): what a reply carries for an existing element

| Criterion | Result | Evidence |
|---|---|---|
| GO4-C1 | the rule stated in prose, table and the shape-match bullet; the example reuses a host | `tests/test_unattended_growth_guidance.py::test_go4_t1_*` |
| GO4-C2 | eleven edits each fail the guard; hidden rules are missing; equivalent Markdown reads the same | `test_go4_t2_*`, `test_go4_r1_f2_*`, `test_go4_r2_*` |
| GO4-C3 | the packaged examples add no existing element | `test_go4_t3_*` |

## GO5 (#227): one summary per round

| Criterion | Result | Evidence |
|---|---|---|
| GO5-C1 | counts add up over three replay rounds; the known-mix round gives its README's counts. **Partly refuted:** `dropped-with` cannot share one round with a shape match (see the delta, D4) | `tests/test_go5_round_summary.py::test_t1_*`, `test_t2_*` |
| GO5-C1b | not applied adds nothing; narrowed-then-applied reports the narrowed additions | `test_t3_*` |
| GO5-C2 | an empty and a covered round differ; the empty one is zero | `test_t4_*` |
| GO5-C3 | host drops verbatim; hostile files and unbound artifacts refused by name | `test_t5_*`, `test_t6_*`, `test_r1_*` |
| GO5-C4 | both replies drafted, not posted | `notes/issue-replies.md` |

## Whole lane

beast-3, six shards per tree: base 20,416 passed, head (before the last
repairs) 20,498; the one head-only failure is fixed
(`evidence/GO2-GO5/full-lane.md`).
