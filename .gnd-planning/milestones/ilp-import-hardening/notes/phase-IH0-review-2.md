# IH0 review, reader 2 (verbatim, sanitized)

> Retained by the author. The reader returned this report as message text because the harness refuses report files from subagents; the text is otherwise verbatim. **Edited:** the session scratch path is replaced by `<scratch>`. One reader is one reader.

I found no blocking defects in the ilp-learners changes: 6 are hardening and 2 are completeness. The report file `<scratch>/IH0/reader-2/report.md` does not exist, because the harness refused the Write ("subagents should return findings as text"). The full report is below.

The 13 probe scripts are in `<scratch>/IH0/reader-2/` and their captured output is in `<scratch>/IH0/reader-2/probe-outputs.txt`. To rerun one, from `<scratch>/IH0/subject`, run `uv run python ../reader-2/probeN_*.py`. The probes call `gnd.cli.main` in-process and write only into a temp directory under reader-2, which they delete. No learner, solver or model was run, and `git status` in the subject checkout is empty.

The scope was `git diff m^1 m -- src tools` for each listed merge. e30eec8 and fb03739 have no changes under `src` or `tools`.

## Findings

### F1 (hardening): the `rules` import admits a feature the export never wrote
- **Commit:** 70266b5 (IL3). It became out of step when 65fd6df (Popper) and 7818be1 (ILASP, ILC-D6) added `off-threshold`.
- **File:** `src/gnd/export/ilp_learners.py:75` — the `rules` entry has no `vet`. `src/gnd/export/ilp_rules.py:213` (`parse_ruleset`) maps any well-formed column name to a clause.
- **Repro:** `probe3_rules_off_feature.py`. The column is not in `features.json` (thresholds written: 35…450, 500, 640…). The import of `[[f_refund_amount__2__3__gt_t_amount__501=1]]` exits 0, IMPORTED 1, support 4/4, consequent `<= 501`. The same rule through Popper exits 3 `off-threshold`.
- **Expected:** refused, as Popper and ILASP refuse it, because the learner could not have learned it from this export.
- **Actual:** admitted, with provenance naming wittgenstein and this export.
- **Mitigation:** GND does re-check the rule. IL3 spec T5b chose this on purpose ("as for every target"), and ILC-D6 later made that premise false.
- **Same pattern:** `probe11_llm_off_threshold.py` admits `gt_t_amount(A, 641)` (exit 0). 641 is not among the thresholds the prompt lists, and nothing documents whether that is intended.

### F2 (hardening): the Popper `off-threshold` refusal depends on spelling
- **Commit:** 65fd6df.
- **File:** `src/gnd/export/ilp_popper.py:148`.
- **Repro:** `probe7_popper_binary_bypass.py`. `bias.pl` declares neither binary `gt_t_amount/2` nor `gt_t_amount__501`:
  - `gt_t_amount__501(C)` exits 3 `off-threshold`;
  - `gt_t_amount(C,501)` exits 0, admitted;
  - `C > 501` exits 0, admitted;
  - `ge_t_amount__502(C)` exits 0, admitted.
- **Expected:** all four refused, since adapter v3 never declares any of them. ILASP refuses its analogues (`unparsable` or `builtin-comparison`).
- **Actual:** one spelling is refused and three are admitted. The docstring calls this deliberate.

### F3 (hardening): the two duplicated threshold vets disagree on nested comparisons
- **Commits:** 65fd6df (Popper vet) and 7818be1 (ILASP vet).
- **File:** `src/gnd/export/ilp_asp.py:475-478` checks only top-level atoms. `ilp_popper.py:148` also checks atoms inside `\+` and aggregates.
- **Repro:** `probe1_nested_threshold.py`. The Popper rule `\+ gt_t_amount__999(C)` gives 3 `off-threshold`. The ILASP rule `not gt_t_amount(V2,999)` gives 3 `negation-as-failure`.
- **Expected:** one refusal name for the same construct. The bridge page says ILASP checks "each comparison's constant".
- **Actual:** the two adapters give different names.

### F4 (hardening): the ILASP reader writes an aggregate name the clause schema rejects
- **Commit:** 426bd80.
- **File:** `src/gnd/export/ilp_asp.py:57` includes `"sum+"`. The name pattern in `src/gnd/ilp-clauses.schema.json:193` is `^[a-z][A-Za-z0-9_]{0,63}$`.
- **Repro:** `probe10_sum_plus.py`. `#sum+{…}` exits 3 with "… is not valid under any of the given schemas". `#sum` exits 3 `clause 0: aggregate`.
- **Expected:** `clause 0: aggregate`, as the IL2 spec's "carried so the checker names it" promises.
- **Actual:** a schema failure with no refusal name.
- **Not probed:** an aggregate with more than 16 elements (the schema's `maxItems`) would likely take the same path.

### F5 (hardening): the mined import loads the population before checking its binding
- **Commit:** 860e651.
- **File:** `src/gnd/export/ilp_service.py:623`. `_mined_inputs` loads the population and exits 5 on failure; the digest comparison comes after, at :624.
- **Repro:** `probe8_exits.py`, with an unloadable population and a run record bound to the staffing population's digest. It exits 5.
- **Expected:** exit 3 `population-mismatch`. The docstring at :582-587 orders bindings before loading the model and population, and the digest needs only the bytes.
- **Actual:** exit 5.

### F6 (hardening): the comparison tool's refusal regex has drifted from `ilp.refusal_name`
- **Commit:** a75b328.
- **File:** `tools/ilp_comparison.py:56` and :75-81 duplicate `src/gnd/export/ilp.py:67`. `refusal_name` is used only by tests.
- **Repro:** `probe6_comparison_tool.py` case (a), on a synthetic evidence root whose import refused with `unparsable: line 2…`. `refusal_name` gives `unparsable`. The tool's row is `import_exit 3, clauses_proposed 2, first_refusal None, clauses_not_evaluated 0, clauses_admitted 0`.
- **Expected:** the refusal is named and both clauses count as not evaluated.
- **Actual:** two clauses are unaccounted for. The committed evidence is unaffected, since the tool's check exits 0.

### F7 (completeness): the comparison tool's "review 5" guard covers unlabelled rows only
- **Commit:** 7818be1.
- **File:** `tools/ilp_comparison.py:111`. `labelled_row` → `_proposed` calls the reader with no guard.
- **Repro:** `probe6_comparison_tool.py` case (b). An unparsable `program.pl` raises an uncaught `IlpError`, because `main` catches only `ComparisonError`.
- **Expected:** exit 2 with a named `ComparisonError`, as AMIE rows get.
- **Actual:** a traceback and exit 1, which the tool also uses for "table differs".

### F8 (completeness): private names used across modules, and a dead duplicate
- **Commits:** a75b328, 860e651, 70266b5.
- **Repro:** `probe12_private_names.py` (an AST scan) finds:
  - `tools/ilp_comparison.py:129` imports `ilp_service._mined_inputs`;
  - `ilp_service.py:521` adds a second use of `evolve.service._parse_model_text`, copying a pattern that predates IL;
  - `ilp_rules._suffix` (`ilp_rules.py:58`) duplicates `ilp_popper._suffix` and is never called.
- **Expected:** these follow ILC-D8's public-name rule.

## Suspected, not reproduced
- **AMIE count vs checker on subtypes.** For a subtype with its own reference scheme, `ilp_amie.count` spells values under a separate family. If the checker joins those values differently, a rule could reach the `RuntimeError` at `ilp_service.py:711` and exit 70 on valid input. I did not build such a model; the count-refuses direction is documented (review 1).
- **Refusal order across clauses.** The adapter vet runs before clause 0's fragment checks, so the first refusal can name a later clause (`probe2_vet_order.py`: clause 1 `off-threshold` is reported while clause 0 is `recursion`). This order is documented (step 2 before step 3). It makes the comparison tool's "not evaluated" count approximate.

## Checked and true
- **Registry pins** (`probe13`): the registry tuples equal the CLI `choices` and both schema `target` enums.
- **Argument exits** (`probe8`): 64 for each wrong `--labels`/`--population` pairing and for `--target llm` on export; 66 for a missing population; 5 for an unloadable one; 3 `learner-mismatch` for a wrong learner name.
- **Committed staffing runs** (`probe5`):
  - `amie` exits 3 `does-not-hold`;
  - `amie-2` exits 0, and its JSON report validates against `mined-import.schema.json`.
- **AMIE count work** (`probe4`): a join at the full 1M-row product takes about 0.17 s at 222 MB peak, so 256 rules project to under a minute. Bounded.
- **ILASP reader constructs** (`probe9`): it carries `not` and `#count` through to the fragment table's own names, caps nesting at 4, and reads `_` as clingo does.
- **Re-check before admission:** every admission path re-checks with GND first (`score_populations` plus the set comparison; the AMIE count plus the checker). None of the admissions in F1, F2 or the llm case skipped it.
- **Existing tests:** the six `tests/test_ilp_*.py` suites give 482 passed and 8 skipped. `test_il_close` plus the two layer tests give 75 passed. `tools/ilp_comparison.py` exits 0.

Count: 0 blocking, 6 hardening, 2 completeness.
