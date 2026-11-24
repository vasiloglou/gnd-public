# Full default lane, base against the GO2–GO5 head

Run on beast-3 on 2026-11-23, as for GO1: six shards per tree
(`ls tests/test_*.py | sort`, one file in six per shard),
`uv run pytest -q --tb=line -p no:cacheprovider` under the default `addopts`.
uv 0.13.7 and Python 3.13.18 on that machine, not the CI pin. The shards of
the two trees differ because the head adds test files.

| Tree | Commit | Passed | Failed + errors |
|---|---|---|---|
| base | `origin/main` `fe5fdf72` | 20,416 | 4 |
| head | `a30b6192` (GO2–GO5 with `origin/main` merged) | 20,498 | 5 |

The head's one extra failure was
`tests/test_rf1_pin_harness.py::test_mutation_table_covers_every_pin_node`:
the new `gnd evolve summary` leaf's two pin nodes had no mutation row. They
are now named in the root-`prog` row of
`code-refactoring/evidence/RF9-ci-repair/mutation-retargets.json` (that
mutation renames the program every help and exit probe prints, so both turn
red), and the test passes locally with `tests/test_rf1_cli_pins.py` and
`tests/test_rf9_ci_repairs.py`. The commits after `a30b6192` (the GO3–GO5
review repairs and this fix) were run on the focused lane and the guard
block, not on the whole lane again.

Failing on both trees on that machine, so not this change:

```text
ERROR tests/test_public_optional.py::test_base_wheel_refuses_missing_synth_extra_and_still_checks
ERROR tests/test_public_optional.py::test_declared_synth_extra_is_seeded_and_loader_valid
FAILED tests/test_rule_verbalization.py::test_t3_parity_and_t3b_mutation_control
FAILED tests/test_why_not_anonymity.py::test_added_files_name_no_downstream_application
```

## Again at the close head

Run on beast-3 the same way at `32a50ed7` (head only, after the GO3–GO5
review repairs, the RF1 mutation-ledger fix and the close-review repairs), for
the close review's concern that the cited lane predated the head:
**20,509 passed; 4 failed or errored, the same four as on base** (the list
above). No head-only failure.
