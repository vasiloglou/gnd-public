# IH0 review, reader 1 (verbatim, sanitized)

> Retained by the author. The reader returned this report as message text because the harness refuses report files from subagents; the text is otherwise verbatim. **Edited:** the session scratch path is replaced by `<scratch>`. One reader is one reader.

I could not write `<scratch>/IH0/reader-1/report.md`: the harness refused report files from a subagent. The full report is below. All probe scripts are under `<scratch>/IH0/reader-1/`, and each was run from the subject checkout as `uv run python ../reader-1/<probe>.py`.

**Count: 0 blocking, 5 hardening, 0 completeness.**

Baseline before probing: the six IL test files gave 482 passed and 8 skipped. The layer tests plus `test_il_close.py` gave 75 passed. `uv run python tools/ilp_comparison.py` exited 0. I ran no learner, solver or model. `common.py` holds the shared helpers: in-process `gnd` calls, and an import that first reads GND's own coverage from the `coverage-mismatch` message and then reports it back.

## Findings

### F1 (hardening): the `rules` and `llm` imports admit thresholds their export never offered
- **Originating commits:** 70266b5 (IL3, `rules`) and 75a397f (IL5, `llm`). The two targets fell out of step at 7818be1, which gave `popper` and `ilasp` an off-threshold `vet` but not these two.
- **Where:** `src/gnd/export/ilp_learners.py:72-77` (no `vet=` on either entry). `src/gnd/export/ilp_rules.py:117-138` (`_column` and `_clause` accept any threshold up to 32 digits).
- **Reproduction:** `p01_rules_off_threshold.py` imports threshold 451 through each target. 451 is not among the exported thresholds.
- **Observed:**
  - `451 column rendered? False`
  - rules: `exit 0 IMPORTED 1 learned clauses ... covers 5 (support 4/5`
  - popper: `exit 3 clause 0: off-threshold: gt_t_amount__451 ...`
  - ilasp: `exit 3 clause 0: off-threshold: gt_t_amount compares with 451 ...`
  - The prompt's `gt_t_amount` thresholds list has no 451, yet llm gives `exit 0`.
- **Expected:** the reader refuses a column or threshold its own writer (the feature table or the prompt) never offered, as Popper and ILASP do under ILC-D6.
- **Actual:** both imports admit it. GND still re-checks coverage, so this is not a wrong admission.

### F2 (hardening): Popper's off-threshold check misses spellings the v3 bias never declares
- **Originating commit:** 7818be1. Its `check_thresholds` vets only `gt_`/`lt_` threshold names, and `clingo_integer` was added to the renderer but not the reader.
- **Where:** `src/gnd/export/ilp_popper.py:133-150` and `:334-337`. Compare `ilp_asp.py:391-392`, which refuses the out-of-range integer.
- **Reproduction:** `p03_popper_int_range.py`.
- **Observed:**
  - The Popper reader yields `{'const': 3000000000}`. ILASP gives `unparsable: ... outside clingo's 32-bit integer range`.
  - `V2 > -3000000000` imports with exit 0.
  - `bias declares ge_t_amount__451? False | any ge_ threshold? False`, yet both `ge_t_amount__451(V2)` and the binary `gt_t_amount(V2,451)` import with exit 0.
- **Expected:** a Popper import refuses constants and spellings that adapter version 3 cannot produce ("Popper could not have learned it from the export").
- **Actual:** all of them are admitted. The docs deliberately scope step 2 to `gt_`/`lt_` names, so this is a coverage gap, not a contradiction. Coverage is still re-checked.

### F3 (hardening): the comparison tool's refusal regex has drifted from `ilp.refusal_name`
- **Originating commits:** a75b328 (the tool) and 7818be1 (`refusal_name`).
- **Where:** `tools/ilp_comparison.py:56`, `:75-80` and `:113-118`.
- **Reproduction:** `p05_comparison_tool.py` builds a fake evidence root: a two-clause Popper program whose import exited 3.
- **Observed:** for `learner-mismatch`, `export-mismatch`, `clauses-mismatch` and `unparsable`, `refusal_name` returns the name but the tool shows `first_refusal=None not_evaluated=0`. An `off-threshold` refusal on clause 1 also shows `not_evaluated=0`, although the vet refuses before clause 0 is rewritten.
- **Expected:** the row names the refusal and reports 2 clauses not evaluated.
- **Actual:** the row shows "—" and 0 not evaluated. The committed table is unaffected because all its refusals are indexed.

### F4 (hardening): the comparison tool crashes when its own reader refuses labelled evidence
- **Originating commit:** a75b328.
- **Where:** `tools/ilp_comparison.py:96-103` (`_proposed`) and `:236-240`, where only `ComparisonError` is caught. The unlabelled path converts `IlpError` (`:160-165`); the labelled path does not.
- **Reproduction:** `p06_comparison_tool_unparsable.py` points `--root` at a fake root whose Popper program holds `gt_t_amount__0500`.
- **Observed:** `exit 1`, with a traceback ending `gnd.export.ilp.IlpError: unparsable: line 1, column 56: a threshold name the renderer never writes: gt_t_amount__0500`.
- **Expected:** a named refusal and exit 2 (as on the AMIE path), or a row recording `refused:unparsable`.
- **Actual:** an uncaught traceback and exit 1, which the tool defines as "differs". Invalid-JSON LLM output would crash the same way.

### F5 (hardening): a private service name is imported across modules
- **Originating commit:** a75b328.
- **Where:** `tools/ilp_comparison.py:129`, `from gnd.export.ilp_service import _mined_inputs`. `hold()` (`:123-148`) also re-implements the import's map-and-count pipeline; it has not drifted yet.
- **Reproduction:** the AST scan in `p05_comparison_tool.py`.
- **Observed:** `private import: tools/ilp_comparison.py:129 from gnd.export.ilp_service import _mined_inputs`.
- **Expected:** a public seam.
- **Actual:** the tool depends on a private helper.

## Suspected, not reproduced
1. **`import mined-rules` names a validation failure `invalid model:`** (`ilp_service.py:702-703`, `727-729`). It validates the whole candidate once and reports a failure that way, not as a per-rule `invalid-guarded` like check 10. I could not build a mapped rule that passes `type-confused-join` and still fails validation.
2. **Count and checker disagreeing, giving exit 70** (`ilp_service.py:708-712`). I found no spelling collision and no join that the count makes and the checker rejects. The reverse case exists, a cross-family join that the count never meets. It is conservative (a refusal) and documented (ILC-D1, the `ownref` fixture).

## Claims checked and found true
- **Registry, CLI and schemas agree.** CLI choices, the `EXPORT_TARGETS` / `IMPORT_TARGETS` / `MINED_TARGETS` tuples, and both schema target enums match. `llm` never exports and binds the `neutral` export.
- **The IL4 post-parse check exits 64** in all four cases, with the argparse messages (`p07_cli_usage.py`). An unknown target is also 64.
- **`ilp-rules` refusal order matches the docs:** clauses-mismatch, export-mismatch, learner-mismatch, coverage-shape, then off-threshold before any rewrite, then the fragment table, then re-evaluation.
- **`mined-rules` order matches its docstring and the docs:**
  - the reader;
  - learner, rules, population, then facts mismatch;
  - every rule's mapping, in `MAPPING_REFUSALS` order;
  - per rule: too-large, covers-nothing, support-mismatch;
  - does-not-hold over all rules;
  - then the checker must say `pass`.
- **Every admitted labelled clause is re-evaluated by GND,** including check 10 per clause and for the whole set. A JSON boolean comparison constant is refused `invalid-guarded` (`p02_bool_threshold.py`).
- **AMIE counting is bounded:** at most 1,000,000 body rows per rule. `p04_amie_count_cost.py` measured 0.23 s and about 300 MiB peak per rule at the bound, so about one minute for 256 rules in the worst case. The reader's caps and `canonical` (at most 3! body orders) are bounded.
- **Recursion and size caps** hold in the Popper, ILASP and rules readers. The clauses schema caps clauses at 32.
- **Rules column names round-trip** through the reader, or the export refuses `column-name`.
- **Redacted roles are refused for every target,** AMIE included.
- **The earlier cross-module private names are fixed:** `_threshold_rows` and `_ilp._value` are gone. The `_parse_model_text` import predates IL.
- **These duplicates have not drifted:** `ilp_asp._INT_RANGE` and `ilp._CLINGO_INTEGERS`; the two `_suffix` helpers; the leading-zero and `m0` rules.
- **The LLM prompt and ILASP offer the empty max/min thresholds that Popper and rules omit.** This follows a recorded decision (IL1-A2-D2), not a defect.
- **`tools/gnd_layers.json` covers every new `ilp_*` module.**

Files are in `<scratch>/IH0/reader-1/`:
- common.py
- p01_rules_off_threshold.py
- p02_bool_threshold.py
- p03_popper_int_range.py
- p04_amie_count_cost.py
- p05_comparison_tool.py
- p06_comparison_tool_unparsable.py
- p07_cli_usage.py
