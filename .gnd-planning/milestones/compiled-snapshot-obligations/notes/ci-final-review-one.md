# Bounded final local CI follow-up review one

Inspected root-owned assurance/adaptation scope repairs and the exact RF1 CLI
successor projection. No production edits or broad suite run. **No blocking
finding; no overbroad exemption or omitted authored family reproduced.**

## Scope repair

`gnd.assurance.core._phase3_target` excludes exactly rows with snapshot surface
and compiled-subset family. Existing snapshot, applicability, composition and
historical transition predicates are otherwise untouched. The new generated
snapshot mode cannot expand the frozen Phase 3 proof roster through this path.
This is appropriately narrower than excluding every operation-related branch
or every new snapshot finding.

`semantic_adapter._FAMILIES` now uses the authored FAMILIES registry, matching
the actual adapter hooks. A focused inventory comparison found the current
live snapshot roster exceeds the authored registry by exactly compiled-subset;
there are zero authored registry families absent from the snapshot roster.
Thus the repair removes generated findings from authored-family adaptation
without shrinking existing authored coverage. The historical REGISTRY binding
is retained explicitly for compatibility.

## CLI successor

The tree comparison starts from the historical golden and inserts exactly one
fixture-pinned action at its fixed index. Every old parser, option, default and
ordering field remains compared. Only the gnd check help and exit probes select
the exact successor fixture; other parser paths continue their historical
golden checks. The fixture pins the new option as store_true, default False,
no required argument and the expected help. Unknown-input exit 64 and empty
stdout remain pinned. No RF1 golden file is changed by this diff.

The helper still delegates the same lane/key/observed payload to assert_golden
when the original capture environment is selected. It introduces no substitute
capture key or extra capture field. The successor assertion uses exact
canonical equality outside that existing capture mode, with no broad text
normalization or field stripping.

## Focused verification

Ran only the new scope test and three affected CLI successor nodes:

```text
UV_CACHE_DIR=/tmp/gnd-review-one-uv UV_PROJECT_ENVIRONMENT=/private/tmp/gnd-issue16-audit/venv uv run --no-sync --python 3.11 pytest -q tests/test_compiled_scope_boundaries.py tests/test_rf1_cli_pins.py::test_cli_tree 'tests/test_rf1_cli_pins.py::test_cli_help[gnd check]' 'tests/test_rf1_cli_pins.py::test_cli_exit_probe[gnd check]' --tb=short
```

Result: **4 passed in 0.21s**, exit 0. Authored predicates, sibling successor
repairs and complete impact groups remain root/other readers' selected gates;
this review does not claim those runs were independently repeated.

## Limits

One same-model advisory review of these narrow scope and CLI preservation
changes. No certification, historical proof extension, full CI or platform
acceptance claim. The compiled mode's established public assurance-none boundary
remains independent of this frozen-roster repair.
