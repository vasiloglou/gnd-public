# Query-budget headroom, 2026-11-11

Issue 170: both exact query-policy budgets were full (365 of 365 occurrences,
310 of 310 on the original metric), so the next direct read of `fact_types`
or `roles` under `src/gnd` would fail `tests/test_rf6_query_policy.py`.

The owner chose to move reads behind `gnd.model_index.ModelIndex` rather than
raise a ceiling ("Move reads"), and approved [spec r1](spec.md) with D1 to D4
as proposed ("Approve as proposed"), both on 2026-11-11.

## Outcome

Ten read-only `model.fact_types` reads now go through
`ModelIndex.for_model(model).iter_fact_types_shared()`. The budgets stand at
**355 of 365** and **300 of 310**; no ceiling, baseline or guard code changed.
The exact delta is [query-successor.json](query-successor.json).

Four of the spec's ten primary sites were dropped and replaced by its four
reserve sites (spec, implementation findings 1, 9, 10 and 11): three are
command bodies whose syntax an RF4 or RF5 guard pins, and one is called by a
test with a stand-in object.

## Behaviour changes to know

- **A non-`Model` is refused.** A converted function given something that is
  not a `Model` raises `TypeError: ModelIndex requires a Model`. Before, a
  duck-typed object with a `fact_types` attribute worked. No caller in `src/`
  or the default lane does this at the ten converted sites.
- **The index reads a dump of the model, not its live rows** (review R3,
  reproduced). For a model loaded from a file the two are equal: all 225
  loadable fixtures agree. For a `Model` built in code whose rows hold a
  value that `model_dump()` alters, such as a dataclass instance, a converted
  function sees the dumped value. This is true of every `ModelIndex` read in
  the repository; it is recorded here, not repaired.

## Evidence that outputs did not move

`evidence/compare_outputs.py` runs six of the converted functions over every
loadable model under `examples/` and `tests/fixtures/`, once against the
source of `793618f1` and once against head, and digests each output or
exception. The 1,350 digests are equal
([outputs-head.json](evidence/outputs-head.json)). It does not cover
`_run_transition_raw`, `read_session_contract`, `evaluate_judgments` or
`build_measurement_report`, which need more than a model to call; the default
lane is their only control.

## Review

Two rounds, one Codex reviewer each. One reviewer is one reviewer.

| # | Round | Finding | Disposition |
|---|---|---|---|
| R1 (high) | [1](codex-review.md) | `fact_type_scope` is called with a `SimpleNamespace` by an existing test; the conversion raises `TypeError` | reproduced; the site was reverted and replaced |
| R2 (medium) | 1 | the new tests cover three of ten functions, record no baseline bytes, accept an exception change, and cannot see mutation or indexing frequency | applied: the exception change is stated and pinned; a no-mutation test, the base-versus-head comparison and a frequency test were added. Four command-internal functions remain covered by the default lane only |
| R3 (medium) | [2](codex-review-2.md) | for a `Model` built in code with a value the dump alters, `_structured` changes its answer | reproduced; recorded as a limit above, not repaired |
| R4 (medium) | 2 | the frequency test never ran the skill-document read, counted reads and not index constructions, and covered five readers | partly applied: a structured model, six readers and a negative control. It still counts reads, not constructions |
| R5 (low) | 2 | the README's gate results were not bound to commits and one sentence was stale | applied below |

The second round reviewed `git diff 793618f1 bbe4d3c3`. The answers to R3,
R4 and R5 were not reviewed.

## Gates

- **G1** `uv run pytest -q tests/test_query_budget_headroom.py tests/test_rf6_query_policy.py tests/test_rf1_layering.py tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py --tb=short -p no:cacheprovider`,
  on the final tree (source as at `bbe4d3c3`, test file as committed after
  it): `369 passed in 59.08s`.
- **G2**, the default lane, run as four shards of the 684 `tests/test_*.py`
  files (`uv run pytest -q --tb=short -p no:cacheprovider <files>`), not as
  one command, because one unsharded run exceeds the session's ten-minute
  limit. Source as at `2c82a9af`, four shards in parallel:
  - `5378 passed, 132 deselected in 1788.64s (0:29:48)`
  - `1 failed, 4652 passed, 234 deselected, 1 warning in 2506.37s (0:41:46)`
  - `4588 passed, 273 deselected in 1559.86s (0:25:59)`
  - `4404 passed, 215 deselected in 2248.93s (0:37:28)`

  The one failure was
  `tests/test_agent_cli.py::test_timeout_escalates_term_to_kill_and_awaits_descendants`,
  a process-timeout test. That shard, rerun on its own at `bbe4d3c3` (same
  source): `4653 passed, 234 deselected, 1 warning in 957.33s (0:15:57)`. So
  every shard has exited 0, the second one only when not run beside three
  others. No single run of the whole lane exited 0.
- **G3** `uv run ruff check` over the changed source and test files and
  `evidence/compare_outputs.py`: `All checks passed!`
- **G4** `python3 scripts/components_index.py changed --base main --strict`:
  0 to fix after `scripts/components_index.py write` regenerated the index.
  The entries it lists to reread were not reread.

Earlier runs, kept for the account: one unsharded G2 was killed at 58%; the
first sharded G2 had 2 failures in `tests/test_rf4_peripheral.py` (finding 9
in the spec), which the revert removed.

## Not done

- PR 187 is open and not merged.
- Issue 170 stays open until the owner merges.
