# F3 · Package initialization and model queries

Delegated spec gate, 2026-11-25. Provenance is r2 §§0, 3, 4, 9 and 10 and the measured F3-readiness note. The owner retained the eight-phase structure and delegated the architectural decision after the 294-row inventory and sibling-import result were reported.

## Evidence and rulings

D1 (#298) retains the existing three core groups as named upper bounds and adds a regression gate for every new core member or group. The graph adds package initialization edges even when executing code inside the already-initialized parent. All three groups already use sibling imports. Moving existing private implementations to unrelated top-level modules solely to reduce this synthetic count would invalidate patch and source-scan contracts. Exercise cold imports in fresh processes in both orders. The zero-core target was a proposal; report actual memberships at close.

D2 (#305) prioritizes the complete duplicated model fact-ID mapping family. Eleven exact sites in six consumers produce two variants. Route each through ModelIndex.fact_map(model, *, require_id: bool), with live rows, last duplicate wins, str-converted keys, missing id as None or KeyError according to the historical call. The snapshot index otherwise returns detached first-match rows and cannot replace these variants. Bind each moved occurrence to its owner and decrement that entry only. Preserve the entire remaining exact policy and reasons. Keep #305 open for traversal families whose consumer-specific behavior still awaits a pin, including standalone/raw IR selectors. Residual owner is GND model-query maintainers; next trigger is a consumer-specific characterization and compatible query contract.

D3 adds the two-parent closure and committed rejected-proposal/deontic-note cache controls. Include positional references in the focused existing index suite as the F6 dependency.

## Design, rules and gates

Use the same public compatibility pattern as ModelIndex.object_map, with an explicit mandatory/optional ID choice. Correctness includes missing, duplicate and non-string ids, original row identity and single-pass behavior. No new untrusted parser, recursive algorithm or policy walk. Preserve row order and mapping exception order. The source method is the single contract home. Compare both variants against the old comprehension before changing each caller. Keep old import names and primitive resolver ownership. Add a measured negative control for a new package cycle. Verify with tests/test_rf6_index.py, tests/test_rf6_query_policy.py, tests/test_rf1_layering.py, focused affected-consumer tests, ruff and strict component inventory. Expected exit 0. Runtime/fixture budgets follow the focused default lane. Estimate 15–30 source lines plus replacements, 50–100 test lines. Review the phase diff with Claude Code. F7 owns removal of shims.
