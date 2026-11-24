# RF1 mutation coverage, 2026-11-23

`tools/rf1_pins.py mutate` refused to start on `main`: "26 pin nodes have no
mutation row". The mutation table, `tests/fixtures/rf1-pins/mutations.json`,
was frozen at RF9-ci-repair, where its digest was bound into
`mutation-retargets.json`. Pin nodes added after that had nowhere to be named,
and no test ran the tool's coverage check, so nothing reported them.

## The 26 nodes

- **24** are the help and exit-probe pins of the twelve parsers added since
  RF1: `compose`, `discover`, `export ilp`, `export ossie`, `flatten`,
  `import ilp-rules`, `import mined-rules`, `import ossie`, `replay-count`,
  `verbalize model`, `why-not` and `witness-count`. The table's
  `M-CLI-root-prog` row covers the same two pins for the 52 parsers RF1 walked.
- **2** are `test_mc3_cli_successor_rejects_missing_or_changed_flag[remove]`
  and `[metavar]`. Each damages a successor comparison in memory, so no change
  to `src/gnd` can make it fail. `test_inventory` already lists them as meta.

## What changed

- The ledger, `mutation-retargets.json`, may now carry `added_rows` and
  `added_exempt`. An added row is a table row plus a reason and passes the
  same row check as the table; it cannot reuse a table id. An added exemption
  cannot repeat an exempt node. The table and its digest are untouched.
- One row is added, `M-CLI-root-prog-later-parsers`: the mutation of
  `M-CLI-root-prog`, expecting the 24 nodes red. Two exemptions are added.
- `tests/test_rf1_pin_harness.py::test_mutation_table_covers_every_pin_node`
  runs the coverage check in the default lane. It failed before the additions.
- `tests/test_rf9_ci_repairs.py` gains eight refusal cases for malformed
  additions.

## Gate

`uv run python tools/rf1_pins.py mutate --out DIR --jobs 6` over the whole
table exited 0: 168 rows, 168 killed, and the control of 374 nodes green.
[mutation-report.json](mutation-report.json) and [control.txt](control.txt)
are that run's output, under Python 3.14 on the development machine.

## Not established

- The run used one interpreter. RF1's goldens are keyed for three.
- A new parser's pins are named only when someone adds them to the row. The
  new test reports the gap; it does not close it.
