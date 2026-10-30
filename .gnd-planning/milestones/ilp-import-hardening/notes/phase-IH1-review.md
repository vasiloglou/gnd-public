# IH1 review (verbatim, sanitized)

> Retained by the author. One reviewer read the IH1 diff against `d9b274c`
> (process-phase step 4); one reviewer is one reviewer. It returned this report
> as message text, because the harness refuses report files from subagents; the
> text is otherwise verbatim. **Edited:** the session scratch path is replaced
> by `<scratch>`. The repairs made after this review carry no review opinion.

## IH1 adversarial review: report

**Verdict: no blocking finding.** I reproduced nothing that admits wrongly, crashes, gives a wrong exit, or changes bytes on valid input. I found 2 hardening findings and 3 completeness findings, listed below.

How I checked: I extracted HEAD's `src` and `tools` with `git archive` into `<scratch>/IH1/review/old/`. A differential harness then ran each input through the old and the new code, using `.venv/bin/python` with and without `PYTHONPATH=old/src`; I confirmed that `gnd.__file__` resolves to the right tree each time. For every case it compared:
- the exit code, stdout and stderr of `gnd import mined-rules`, in text and in `--format json`;
- the proposal bytes;
- `gnd export ilp --target amie`: exit, streams and every byte of the output tree.

The harness scripts are `diff.py`, `more.py`, `more2.py` and `hold.py` in `<scratch>/IH1/review/`. Nothing in the worktree was edited.

### Findings

**H1 (hardening). `hold()` turns a table-building error into a rule-less, misleading ComparisonError.**
- Where: `tools/ilp_comparison.py:160-167` and `src/gnd/export/ilp_service.py:582-600`.
- Cause: `count_mined_rules` with `tables=None` now builds `mined_tables` inside `hold()`'s `try`. Before, `relation_table`, `pairs` and `schema` ran outside it, so an `opaque`, `unrepresentable` or schema IlpError raised while spelling the population is now caught.
- Repro: run `hold.py` on staffing with one `works_in` value replaced by `{"$opaque": "x"}`.
  - Old: `IlpError opaque: fact type 'works_in' holds an opaque value the export cannot render`
  - New: `ComparisonError opaque: GND cannot count this rule; the table does not report it`
- Expected: the population fault is named. Actual: it is blamed on an unnamed "this rule", and the detail is dropped.
- Related: the `count_mined_rules` docstring says it "Raises only the mapping refusals and `too-large`". With `tables=None` it can also raise `opaque` and `unrepresentable`.
- Committed evidence is not affected.

**H2 (hardening, very minor). Spec Design 4 is only partly met.**
- `hold()` still uses `_REFUSAL` to extract the rule index (`tools/ilp_comparison.py:163`). Design 4 says it names a refusal "with `ilp.refusal_name`, not `_REFUSAL`".
- The name itself does come from `refusal_name`, so the output is correct.

**C1 (completeness). Nothing pins IH1-D4 on the import.**
- The only test of the new order is T7, which goes through `hold()`. The only existing mined `too-large` test (`tests/test_ilp_amie.py:333`) has a single rule.
- No test has `covers-nothing` or `support-mismatch` on an earlier rule and `too-large` on a later one. A mutant that brought back interleaved per-rule checks in `_cmd_import_mined_rules` would pass the selection.
- This is suspected from a grep of the tests; I did not run that mutant. My differential case `cn_then_toolarge`, which shows the D4 change, could serve as the pin.

**C2 (completeness, wording). The docs describe the new order inexactly.**
- `docs/release-notes.md` says the import "maps every rule before counting any". That was already true at HEAD, where all mapping ran first. The new behaviour is "counts every rule before any admission check". The consequence the note states is accurate.
- The AMIE section of `docs/reference/ilp-bridge.md` does not state either change:
  - that `population-mismatch` is checked before the population is parsed;
  - that every rule's `too-large` comes before any rule's `covers-nothing` or `support-mismatch`. The counting prose ("bounded before it runs … Then, in this order") still reads per rule.

**C3 (completeness, wording). The RF6 successor's `reason` text is inaccurate.**
- `evidence/IH1/dynamic-query-successor.json` says "Removed: _mined_inputs". `_mined_inputs` is kept as an identity alias.
- What the census actually removed is `_Mined`'s row, `render`'s `facts[name]` and the import's inline provenance rows. The data rows themselves are consistent.

### Checked and found true

1. **IH-R2, behaviour preservation.** Old and new were identical (SAME) on every one of these inputs:

   | Group | Cases |
   |---|---|
   | Admitting runs | amie invocation-2 (admitted); invocation-2 with its rules reversed; invocation-1 (`does-not-hold`) |
   | Provenance | duplicate and reordered `based_at` head rows (examples use first rows, e.g. `ft2#1` for s01); a subtype family (`contractor` subtype of `staff`, inheriting the reference, with a duplicate `contracted_at` row): both admitted with byte-identical proposals and the same examples |
   | Facts-digest block (proposals and exports) | `opaque`, `no-relations`, `unrepresentable`: same facts-mismatch text and the same export refusals (`opaque:`, `no-relations:`, `unrepresentable:`) |
   | Mapping refusals | `reflexive-atom`, `open-world-head`, `unknown-predicate` |
   | Count and admission refusals | `covers-nothing`, `support-mismatch`, `does-not-hold` |
   | Unchanged orderings | `too-large` then `covers-nothing`; `too-large` then a mapping refusal (the mapping refusal wins in both); `does-not-hold` |
   | Input bindings | `population-mismatch` with a valid population; a broken population that is the bound one (exit 5 in both); `facts-mismatch` with a wrong digest, alone and combined with an unmappable rule |

   - `relation_table` and `render_tables` refuse exactly as the old `render` did, in the same order. `Population.covers` is always a list, so `list(population.covers)` cannot differ from `getattr(..., None) or []`.
   - `ADAPTER_VERSION` is `"2"`, and `export.json` reports `"2"`.
   - `uv run python tools/ilp_comparison.py` exits 0.

2. **Only the two approved changes differ.**
   - IH1-D4 (`cn_then_toolarge`): old gave `rule 0: covers-nothing`, new gives `rule 1: too-large`, exit 3 in both.
   - IH1-D4 (`supmis_then_toolarge2`): old gave `rule 0: support-mismatch`, new gives `rule 1: too-large`, exit 3 in both.
   - IH1-D5 (`popmis_broken`): old gave exit 5 with a YAML parse error, new gives exit 3 with `population-mismatch: … binds population <record>, not <actual>`. Text and json formats agree.
   - No other case differed.

3. **Build once, no discover edge.** An admitting import calls `relation_table` once and `pairs` once (T2 passes, and the import no longer calls `render`). `ilp_amie` imports nothing from `gnd.discover`; `fact_id` is passed in.

4. **`hold()` counts.** Old and new `hold()` both return 2 and 2 for AMIE invocations 1 and 2. For `rule N: name:` messages, `refusal_name` matches the old regex group, so refusals are named the same.

5. **Tests and evidence.**
   - `tests/test_ih1_counting.py` passes.
   - `red.txt` shows 7 red and 4 green at d9b274c. The 4 green are T4 and the T5 pins, as the spec intends.
   - `mutant.txt`'s reflexive-atom failure is what that mutant would produce. I did not re-run it, because the mutant copy was not retained.
   - Each test has a real failure mode. T6's duplicate pair checks first-row choice. T7 uses a 1,001-staff population instead of lowering `MAX_JOIN_ROWS`; it still reaches `too-large` (1,002,001 > 1,000,000).

6. **Docs, RF6 chain and suites.**
   - The new `opaque` and `too-large` sentence in the bridge page matches the observed export refusals.
   - The successor's `predecessor_sha256` (c23a6118…) matches IH0's file.
   - These pass: `tests/test_rf6_query_policy.py`, `tests/test_gnd_arch.py`, `tests/test_development_scaffold.py`, `tests/test_ilp_amie.py`, `tests/test_il_close.py`, `tests/test_ih0_review.py` and `tests/test_release_docs.py`.
   - Ruff is clean on the 4 changed Python files.

### Suspected, not reproduced
- C1's mutant was not run.
- Runtime: the import now counts every rule, up to the 1M-row bound each, before the first `covers-nothing`. Before, it stopped at the first failing rule. That is slower on refused sets but bounded, and I did not measure it.
