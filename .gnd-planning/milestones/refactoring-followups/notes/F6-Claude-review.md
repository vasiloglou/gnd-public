The test does exercise the real CLI export, both admission routes and gnd-free loading. It does not run the pinned emitted bytes, because it renders the model under an absolute, checkout-dependent name instead of the stable relative name the spec asks for. That is a small fix to the test, so I'm requesting changes.

All three SHA-256 values match the brief. The diff is empty (0 bytes), so `tests/test_refactoring_pyrel_parity.py` is the whole change. I only read and ran code. To get the emitted program in memory I also called `gnd.export.emit.render_pyrel` directly, which writes nothing.

## 1. Findings

**F1 — `tests/test_refactoring_pyrel_parity.py:38`: the program under test is not the pinned one.**
- **What's wrong:** `export(tmp_path)` passes the default `BASICS`, an absolute path (`tests/pyrel_export_support.py:11`, `:27`). The renderer puts that path into the program as `MODEL_NAME` (`src/gnd/export/emit.py`, `render_pyrel`). The spec says "Render the real program using the basics export fixture and a stable relative model name". The approval says "Keep emitted bytes fixed".
- **Consequence:** the existing byte pin (`tests/test_rf2_pre_move_pins.py:96-101`) renders `Path("tests/fixtures/pyrel-oracle/basics.orm.yaml")` from the repository root. So the parity test checks a program whose bytes differ from the pinned ones and change with where the repository is checked out. Nothing connects the parity result to the pinned digest. Both tests pass, but they cover different programs, so they don't prove that the program at the pinned bytes routes correctly.
- **Reproduce:** render once with the relative path and once with its `.resolve()`. The two sources are not equal (`False`). The absolute render contains `MODEL_NAME = '/private/tmp/gnd-followups-F6-review/tests/fixtures/pyrel-oracle/basics.orm.yaml'`.
- **Fix:** export with a relative model path from a fixed working directory. Optionally also check that the SHA-256 of `program.py` equals the RF2 pinned digest.

**F2 — test lines 40-46: few refusal cases (coverage).**
- **What's wrong:** the malformed case is only `constraints="invalid"` at the top level. The plan row for F6 says to compare results and refusals, "including absent and malformed cases".
- **What I ran:** both routes on inputs the test lacks.
  - Agreed: top-level `constraints: null`, `{}` or a list with a string item; inline `null`, absent or a string; empty top-level list; reversed `fact_types` order.
  - Disagreed: an id of `5`, a duplicate top-level id, and the id `"ünï"`. The emitted reader admits all three and lists 7 rows; GND raises `ModelValidationError`.
- **Consequence:** these are outside the spec's "common admitted domain", so they are not a defect in this test. But the claim "refusals agree" holds only for the shapes the test tried. At least the inline malformed case is cheap to add.

**Style (no observable consequence):** the probe passes parsed dicts straight to `admit_model`. It skips the emitted `_parse_document` route over `MODEL_TEXT`. This is harmless for these JSON-shaped documents.

## 2. What I checked and found true
- **Results:**
  - `pytest tests/test_refactoring_pyrel_parity.py`: 1 passed.
  - Run together with `tests/test_rf2_pre_move_pins.py` and the `test_pyrel_export*` boundary tests: 52 passed, offline.
- **Real references and admission:** the program comes from the real CLI (`python -m gnd export pyrel`). On the emitted side the probe calls `admit_model` and `_constraint_entries` from that file. On the GND side it uses `load_model_bytes` followed by `ModelIndex.for_model(...).iter_constraints()`. It compares the positional reference, the declared id and the containing fact type id.
- **Domain errors:** each route raises its own error class: `ExportInputError` from the program's own namespace, and `ModelValidationError` from GND.
- **Not vacuous:** lines 61-62 pin named inline and top-level rows. Upstream, neither route invents ids.
- **Isolation:** the subprocess runs with `-I` and adds a gnd-blocking `meta_path` finder before `runpy.run_path`. `gnd` is installed in the venv, so the blocker matters. The emitted runtime has its own `ModelIndex` and only ruamel/stdlib imports at top level. `run_path` does not trigger the `__main__` block.
- **Standing check (code fitted to its examples):** the change adds no regex, split or slice over structured text. The only special-case branch is the name-prefix test in `BlockGnd.find_spec` (`fullname == 'gnd' or startswith('gnd.')`), which covers the whole package namespace. The two `iter_constraints` implementations use `.get(..., [])` and `or []` respectively. I tried that difference with `null` lists at the top level and inline, and both routes refuse.

## 3. What I could not check
- Native database execution: it is out of scope by the spec, and `relationalai` is not exercised.
- Any lazy gnd imports inside emitted functions other than admission and enumeration: the blocker only covers code that runs.

VERDICT: CHANGES_REQUESTED
