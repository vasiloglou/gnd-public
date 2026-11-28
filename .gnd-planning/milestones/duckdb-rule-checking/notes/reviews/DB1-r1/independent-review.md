The DuckDB lowering keeps variables correlated across the consequent atoms and matches native on every case the phase tests. It still diverges from native on two inputs it accepts. I ran both against the PyRel 1.30.1 / DuckDB 2.0.1 interpreter at `/private/tmp/gnd-six-native-duckdb`. All eight SHA-256 values in the brief match the files I read.

## 1. Findings

**F1. A shared variable across roles of different types is not refused, and the program crashes.** `src/gnd/export/pyrel_rules.py:380-388` (the existential branch of `_guarded`) and `:1162-1169` (`_types`, which keeps the first role's type)
- **What's wrong:** nothing checks that a consequent variable has one type wherever it appears. The spec's revision 2 says "Require joint typed bindings", and its plan says to validate projection types before running a rule.
- **Consequence:** the model renders without complaint, then the generated program exits 70 with `[TyperError] Type errors detected during type inference`. Native gives a verdict:
  - `outcome.result` is a String and `approved.code` is an Integer, bound as `$r` in both atoms, with values `"1"` and `1`: native fail/1.
  - `outcome.result` is a Float and `approved.code` is an Integer, with values `1.0` and `1`: native pass/0.
- **To reproduce:** change the role type in the fixture as above, render with `--rules duckdb` and run the program on that population.

**F2. The DuckDB report has no counterpart to native's existential work limit.** `src/gnd/export/pyrel_rules.py:1666-1683` (`_EXISTS_REPORT`), compared with `GUARDED_EXISTS_WORK_LIMIT = 200_000` in `src/gnd/correspondence.py:44`
- **Consequence:** native returns unchecked/4 with `guarded-exists-work-limit`, while DuckDB reports `fan  OK`, exit 0. That is "not checked" against "passed" on the same input.
- **To reproduce:** use the rule `requested($i) → exists [tag(code=$c), outcome(id=$i, result=$c)]`. Give it 500 rows each of `requested`, `tag` and `outcome`; the population is 29,690 bytes. The first atom shares no variable with the antecedent, so native's work grows as requested × tag.
- **The limit, in numbers:**
  - The 500×500 case above (29,690 bytes) diverges.
  - At 200×200 both sides pass.
  - The generated program refuses populations over 1 MiB (exit 3), which caps the inputs that can diverge.
  - A flat 200,001-row consequent therefore can't reach DuckDB at all; native says unchecked/4 there too.
- **Fix:** either reproduce the native ceiling in the report or refuse this shape. Either way, `docs/reference/capabilities.md` should state the limit.

## 2. Checked and found true

- **Joint correlation:** the generated rule is `not_(outcome(i, r_), approved(r_))` with `.select(i)`. An approved value belonging to another item fails, matching native.
  - A literal in a consequent atom and a variable repeated inside one atom both fail as native does.
  - The same relation with its variables reversed (`link($p,$q) → exists link($q,$p)`) and two relations with reversed order both match native for pass and fail.
  - The consequent atoms skip the `_unswap` reordering step, but I found no PyRel compile failure from that. This is style only, with no input that breaks.
- **Evidence and coverage:**
  - The reported witness holds only antecedent variables (`$i`, or `$p`/`$q`); consequent-only variables never appear.
  - A missing consequent relation with active antecedent bindings gives unchecked/4 with the same reason code as native. This includes a listed but uncovered `approved` that would have satisfied the rule; native is also 4 there.
  - A covered empty consequent fails, and no antecedent rows gives vacuous/2.
- **Report output:** 150 violations print 100 lines plus a `truncated (showing 100 of 150 bindings)` line, and the exit code is unaffected.
  - When an existential rule and a filtered guarded rule are in the same model, both report sections are inserted and both rules report.
- **Refusals:** LQP refuses with `guarded-exists-duckdb-snapshot-only`. Disconnected atoms and existential `where` filters are refused in the exporter.
  - Partially bound consequent atoms and `where: []` are rejected earlier by model validation, so they never reach the exporter.
- **Existing behaviour:** `uv run pytest -q tests/test_duckdb_rule_checking_phase1.py tests/test_pyrel_rules.py` gave 25 passed and 39 deselected. The DuckDB test was run with `GND_TUTORIAL_PYREL_PYTHON` set, so it executed rather than skipped.
- **Code fitted to its examples:**
  - The payload check `set(payload) != {"atoms"}` is a dictionary-key test, not text parsing.
  - The coverage list is built from the requirement's own atom relations, not literal names.
  - The tests cover renamed roles and reversed atom order.
  - The report-section insertion is guarded to happen exactly once.
  - No regular expression or string split was added, and nothing branches on one literal name.

## 3. Not checked

- The counts in `query-successor.json` (8465 distinct rows, 10516 occurrences): I didn't rerun the query inventory that produces them.
- A model with operations using an existential rule: I only read the refusal at `pyrel_rules.py:2773-2775`; I didn't run it.
- Date, Boolean and external-entity roles as consequent variables.
- Deontic modality: the code prints `warning` and doesn't count it as a violation, but I didn't run it.

No repository files were changed. My only write was the review summary at `~/.claude/plans/review-brief-a-elegant-river.md`. The probes passed models and populations in memory or through pipes, and the generated programs used their own self-removing temporary directory.

VERDICT: CHANGES_REQUESTED
