**Answer:** Yes to both. The cycle gate covers all three core layers (model, checking, semantics), and all 12 migrated callers keep their original lookup behaviour. Nothing here changes behaviour; the four findings below are test-coverage and scope gaps.

All 17 files match the SHA-256 values in the brief.

One disclosure first: running `uv run pytest` created `.venv/` in the repository. It is gitignored, so `git status` is unchanged. I also wrote a probe script under `/tmp/f3probe`, outside the repository, and saved this review to the plan file.

## 1. Findings

**F1 (test coverage), `tests/test_rf1_layering.py:486-492`.** `test_core_packages_import_cold` imports the three packages in one process, in forward and then reverse order. Only the first import in each run is cold. I checked what each package loads when imported alone in a fresh process:
- `gnd.model` loads only itself.
- `gnd.checker` also loads `gnd.model`.
- `gnd.assurance` also loads `gnd.model`.

So in both orders `gnd.model` is already loaded before `gnd.checker` is imported, and `gnd.checker` is never the first package imported.
- **Consequence:** a future cycle that breaks only when `gnd.checker` is imported first would pass this test. An example is a module-level `from gnd.checker import X` added inside the `gnd.model` initialization path.
- **Reproduce:** `python -I -c "import sys; sys.path.insert(0,'src'); import gnd.assurance; print('gnd.model' in sys.modules)"` prints `True`.
- **Fix:** run each package as the first import in its own fresh process.
- I did not build a failing case for this. It is reasoned from the import data above.

**F2 (test coverage), `tests/test_rf1_layering.py:479-482`.** The spec asks for a measured negative control. The test only passes a hand-written list, `["gnd.model", "gnd.checker"]`, to the filter function `_unexpected_core_cycles`. It never runs `arch.measure` on a tree that contains a new cycle, unlike `test_layer_ratchet_detects_a_new_pair`.
- I ran a measured probe: a scratch tree where `gnd.universe` and `gnd.population` (both in the model layer) import each other, plus a matching layer map. `arch.measure` reported `[['gnd.population', 'gnd.universe']]` in `parent_initialization_sccs`, and the filter flagged it.
- So the gate works today. Its measurement side just has no committed regression control.

**F3 (scope; no behaviour change), `src/gnd/diff.py:184`.** `{str(fact["id"]): fact for fact in model_b.fact_types}` is exactly the `require_id=True` pattern, but it was not migrated. It was probably missed because the inventory keys on the receiver name `model`.
- Separately, the spec says "Eleven exact sites in six consumers". `fact-map-sites.json`, `query-successor.json` and the diff all have 12 sites; `structured_extension_view` alone has 3.
- The spec text or the inventory key should be reconciled with what "complete family" means.

**F4 (style), `tests/test_rf6_index.py:251-262`.** The routing test passes if *any* call in a function matches, so the three `structured_extension_view` entries are effectively one check. If one of the three sites were reverted, this test would still pass. I expect the exact count of 3 in the query-successor policy to catch it, but I did not run a mutation to confirm.

## 2. Checked and found true

- **Gate covers the three core layers.**
  - Layer names in `tools/gnd_layers.json`: the three groups `{model, checking, semantics}` match the real layers.
  - Every module named in `CORE_INIT_GROUPS` is mapped to one of those layers.
  - The gate reads `parent_initialization_sccs`. That graph includes every direct import plus the implicit package-initialization edges, so it catches every cycle the plain runtime graph would.
  - Any measured cycle that contains a core-layer member and is not a subset of a known group fails the gate. That includes a known group that gains a new member, or two known groups merging.
- **Each migrated caller keeps its variant.** I compared all 12 sites against their old comprehension:
  - `["id"]` (missing id raises `KeyError`) → `require_id=True`: `admission.py:76`, `verbalize_population.py:174`.
  - `.get("id")` (missing id becomes the key `"None"`) → `require_id=False`:
    - `extensions.py` ×7: 1183, 1530, 1887, 2217, 2312, 2376, 2807
    - `refscheme.py:27`
    - `semantic_adapter.py:759`
    - `transition.py:1579`
- **`fact_map` body matches the old code exactly.** It is a fresh dict comprehension each call over the original rows. Row order, last-duplicate-wins, `str()` on keys and the exception type and order are unchanged. There is no caching.
- **Fact-map tests.** The new test covers duplicate (last wins), integer id (key `"3"`), missing id (key `"None"` or `KeyError('id')`) and that the returned rows are the original objects.
- **Matchers I tried** (standing check on code fitted to its examples):
  - The routing test's `ast.unparse(call.func) == "ModelIndex.fact_map"` is an AST comparison, not a regular expression. A fully qualified call would fail the test rather than slip through.
  - The `_unexpected_core_cycles` set filter, tried with the measured scratch-tree cycle from F2. It flagged it correctly.
  - The change adds no new regular expression, string split or slice.
- **Test runs.**
  - `tests/test_rf6_index.py`, `tests/test_rf6_query_policy.py` and `tests/test_rf1_layering.py`: 71 passed.
  - `ruff check` on the changed files: clean.
  - Each core package imports cleanly when it is the first import in a fresh process.

## 3. Not checked

- The affected-consumer tests (extensions, transition, admission, verbalization suites); I ran only the three focused suites.
- The strict component-inventory regeneration check; I only read the component diffs, which look consistent.
- Whether the query-policy count catches a single reverted `structured_extension_view` site (F4). A mutation would mean editing source, which this review is not allowed to do.

VERDICT: APPROVE
