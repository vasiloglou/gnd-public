# IH0 fix review (verbatim, sanitized)

> Retained by the author. One reviewer read the IH0 fixes' diff against
> `cbc97b2` (process-phase step 4); one reviewer is one reviewer. It returned this
> report as message text, because the harness refuses report files from
> subagents; the text is otherwise verbatim. **Edited:** the session scratch
> path is replaced by `<scratch>`. The repairs made after this review carry no
> review opinion.

## Adversarial review of the IH0 fix (diff against cbc97b2, plus tests/test_ih0_review.py)

I made no edits to the worktree. Probe scripts and models are in `<scratch>/IH0/fix-review/`: `probe_import.sh`, `probe_tool.py`, `sub/` (subtype model), `nosub/`, and `head/` (a `git archive HEAD` copy).

During my run, `git status` started showing untracked files under `.gnd-planning/milestones/ilp-import-hardening/` (evidence/, review-1..4, triage). I did not create them and did not touch them.

### Findings

**F1. Blocking (wrong admission): `check_columns` skips a cross-type integer column, and the fragment table admits it under value subtyping.**
- Where: `src/gnd/export/ilp_rules.py` `check_columns`, the `continue` when `comparisons.get(comparison["predicate"]) != types[position]` (about line 253).
- Claim 1 says this branch is left to the fragment table, which refuses it. The fragment table only refuses it when the two types are unrelated.
- Fragment check 5 only requires every type involved to be an integer type. Check 9b (`type-confused-join`) passes whenever the closures intersect.
- Reproduction: I took refunds and added `fee` (Integer value type, `subtype_of: [amount]`, `inherits_reference: true`) and a fact type `refund_fee`. I re-bound `labels.json` to the new model digest and exported `--target rules`. `features.json` holds no `fee` column at all.
- I then imported `[[f_refund_amount__2__3__gt_t_fee__451=1]]` with coverage `["south","harbor","market","airport","station"]`.
  - Observed: `IMPORTED 1 learned clauses ... clause 0 constraints[1]: covers 5 (support 4/5)`, exit 0. The proposal holds `refund_amount ... consequent $v_v2 <= 451`.
  - Expected: refused. Either `off-threshold`, since the column is not in `features.json`, or `comparison-type`, which the Boolean rule sets section promises for "a comparison whose type differs from its position's".
- Control, same model without the subtype: refused `clause 0: type-confused-join: variable V2 joins amount and fee`, exit 3.
- The same skip should also admit the reverse case (a `fee` position with `gt_t_amount__451`). I did not run that one; it would need fee facts.
- Suggested fix: refuse `off-threshold` for any column not in `written` whose position type and comparison type are both integer types. Leave only non-integer positions (IL3 case i6), unknown predicates, arity mismatches and undeclared comparisons to the fragment table.

**F2. Completeness (docs): the documented refusal for a type clash is wrong.**
- Where: `docs/reference/ilp-bridge.md`, the Boolean rule sets paragraph after the new off-threshold text. The sentence predates this diff, but the new check relies on it.
- A clash between two unrelated integer types is refused `type-confused-join`, not `comparison-type` (nosub reproduction above). `comparison-type` only fires for a non-integer position (i6).
- With subtyping the column is admitted (F1).

**F3. Completeness (docs/tool): a reader refusal never becomes a table row, although the docs say it does.**
- Docs, "Comparing the learners": "a refusal before the first clause, at a binding, the reader or the threshold check, leaves every clause unevaluated".
- The tool reads the same output as the import, so any output the reader refused already makes `_proposed` raise. The tool then exits 2 and builds no row.
- Reproduction (`probe_tool.py`, case 1): I set the rules row's `ruleset.txt` to `[[f_refund_amount__2__3__gt_t_amount__500=0]]` and its stderr to `clause 0: negation-as-failure: ...`.
  - Observed: exit 2, `IL3/live/invocation-1: clause 0: negation-as-failure: ...: GND cannot read this output; the table does not report it`.
- This is a legitimate live outcome: the import named the refusal cleanly, and `=0` is a FALSE spelling wittgenstein can print. The table cannot report it.
- HEAD crashed here, so this is no regression. But the "reader" case in the docs and the T2 `reader` parametrization cannot happen in real evidence: that test pairs a parsable `program.pl` with an `unparsable` stderr.
- Whether this exit 2 counts as a wrong exit on valid input is an owner decision.

**F4. Hardening: `_first_refusal` → `refusal_name` gives a non-name, with its trailing newline, for messages that are not in `name: detail` form.**
- Where: `tools/ilp_comparison.py` `_first_refusal`, and `gnd.export.ilp.refusal_name`.
- Reproduction (`probe_tool.py`, cases 2 and 3):
  - stderr `clause 0: nesting deeper than 8\n` (the real `_read_clauses` message) gives `{'name': 'nesting deeper than 8\n', 'index': None}`. The markdown cell is rendered with an embedded newline.
  - `invalid model: ...` gives name `invalid model`.
- `not_evaluated = proposed` happens to be correct for the depth case. The name is wrong, and the newline breaks the table.

**F5. Minor (docs): the release note says "more than 16 elements", but the cap is applied to flat args.**
- Where: `docs/release-notes.md`, and `ilp_asp.py` `args[:_AGGREGATE_ARGS]`.
- The cap counts flattened args: terms plus condition literals. An aggregate with 9 elements of two items each also hits it.
- The refusal is still `aggregate`, so this is wording only.

### Checked and found true
- **Claim 1, corpus:** `uv run pytest -q -o addopts='' tests/test_ih0_review.py tests/test_ilp*.py` gives 499 passed, 8 skipped. All skips are env-gated live runs (`GND_IL*`), so no IL3 corpus answer changes. The doc-referencing tests (`test_il6_walk`, `test_release_docs`, `test_il_close`, ...) give 519 passed, 5 skipped.
- **Claim 1, exact type:** for exact-type columns the check is correct.
  - `__451` is refused `clause 0: off-threshold`. A second rule is refused as clause 1.
  - `__450` passes the check and reaches `coverage-mismatch`.
  - `_prepare` renders the target first, so `_columns` inside `check_columns` cannot raise a new un-indexed `column-name` at import.
  - The rebuilt column name is byte-identical to the input: the regex forbids leading zeros and `m0`.
- **Claim 2:** `ge_`/`le_` unary names of a declared comparison are refused `off-threshold`. The binary spelling is not checked, as stated: `gt_t_amount(V2,451)` passes the check and reaches `coverage-mismatch`. Popper's check is name-based, so the F1 subtype bypass does not apply to it.
- **Claim 3, truncation:** it cannot turn a refusal into an admission.
  - Anything that parses as an aggregate is refused at fragment check 2, or earlier by `head-shape`/`not`/`or`.
  - The only consumers before check 2 are the depth check and the ILASP threshold check. The threshold check only inspects top-level atoms. The depth check runs after schema validation, which refused these clauses at HEAD anyway.
  - Truncation only drops elements that are never looked at. At most it changes which refusal is named, never refusal versus admission.
  - The `#sum+` → `sum_plus` rename matches the schema pattern.
- **Claim 4:**
  - `uv run python tools/ilp_comparison.py` exits 0.
  - Un-indexed refusals are shown without an index.
  - `off-threshold` counts every clause as not evaluated, and that is right for all three checks, which run before any clause is rewritten.
  - Exit 2 carries a named message and no traceback.
- **Claim 5:** step 2 and its per-adapter bullets match the code order: bindings, then coverage-shape, then the threshold check, then the fragment table. The exceptions are F2 and F3.
- **Claim 6:** against a `git archive HEAD` copy with the new test file, the result is exactly 13 failed, 4 passed. The 4 passes are the two "offered passes the threshold check" controls, `t2[fragment]`, and `t5[Import]` (that section already named `off-threshold` at HEAD). All 17 pass after the fix.

### Suspected, not reproduced
- The reverse subtype case of F1 (a subtype position with a supertype comparison) should be admitted the same way.
- An ILASP clause whose dropped aggregate elements are nested deeper than MAX_DEPTH would now be named `aggregate` instead of a depth error. That is harmless, and I did not run it.
