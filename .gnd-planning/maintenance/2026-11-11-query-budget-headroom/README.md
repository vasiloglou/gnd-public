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

## Behaviour change to know

A converted function given something that is not a `Model` raises
`TypeError: ModelIndex requires a Model`. Before, a duck-typed object with a
`fact_types` attribute worked. No caller in `src/` or the default lane does
this at the ten converted sites.

## Review

[One Codex reviewer](codex-review.md), disposition "revise", two findings.

| # | Finding | Disposition |
|---|---|---|
| R1 (high) | `fact_type_scope` is called with a `SimpleNamespace` by an existing test; the conversion raises `TypeError` | reproduced (1 failed in `tests/test_extract_applicable.py`); the site was reverted and replaced |
| R2 (medium) | the new tests cover three of ten functions, record no baseline bytes, accept an exception change, and cannot see mutation or indexing frequency | partly applied: the exception change is now stated and pinned, and a no-mutation test was added. Baseline bytes for all ten and a frequency control were not added; the full lane is the control for the other functions |

The bytes after these dispositions were not re-reviewed.

## Gates

On the final working tree over `793618f1`, uncommitted when run:

- **G1** `uv run pytest -q tests/test_query_budget_headroom.py tests/test_rf6_query_policy.py tests/test_rf1_layering.py tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py --tb=short -p no:cacheprovider`:
  `368 passed in 67.40s (0:01:07)`.
- **G2**, the default lane, run as four shards of the 684 `tests/test_*.py`
  files in parallel (`uv run pytest -q --tb=short -p no:cacheprovider <files>`),
  not as one command, because one unsharded run exceeds the session's
  ten-minute limit:
  - `5378 passed, 132 deselected in 1788.64s (0:29:48)`
  - `1 failed, 4652 passed, 234 deselected, 1 warning in 2506.37s (0:41:46)`
  - `4588 passed, 273 deselected in 1559.86s (0:25:59)`
  - `4404 passed, 215 deselected in 2248.93s (0:37:28)`

  The one failure is
  `tests/test_agent_cli.py::test_timeout_escalates_term_to_kill_and_awaits_descendants`,
  a process-timeout test. It passed in the earlier sharded run of this work
  and passed alone three times afterwards (`1 passed` each). It is recorded
  as a timing failure under four parallel shards, not as a clean gate: G2
  did not exit 0 in one run.
- **G3** `uv run ruff check` over the changed source and test files:
  `All checks passed!`
- **G4** `python3 scripts/components_index.py changed --base main --strict`:
  `0 to fix, 0 warning(s), 15 to reread` after
  `scripts/components_index.py write` regenerated the index. The 15 entries
  to reread were not reread.

Earlier runs of this work, kept for the account: one unsharded G2 was killed
at 58%; the first sharded G2 had 2 failures in `tests/test_rf4_peripheral.py`
(finding 9 in the spec), which the revert removed.

## Not done

- Nothing is committed and no PR is open.
- Issue 170 stays open until the owner merges.
