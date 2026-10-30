# IH0 review, reader 4 (verbatim, sanitized)

> Retained by the author. The reader returned this report as message text because the harness refuses report files from subagents; the text is otherwise verbatim. **Edited:** the session scratch path is replaced by `<scratch>`. One reader is one reader.

The harness blocked writing `report.md`, so the full report is below and is not on disk. The probe scripts and their outputs are under `<scratch>/IH0/reader-4/` (R4 below), where `<scratch>` is `<scratch>`.

**Findings by class: blocking 0, hardening 4 (F1, F2, F4, F5), completeness 1 (F3).**

Scope: `git diff m^1 m -- src tools` for the nine named merges, read as one change; e30eec8 and fb03739 touch nothing under src or tools. No learner, solver or model was run. All commands run from the subject root. The exports came from `uv run gnd export ilp src/gnd/examples/refunds/model.orm.yaml --labels src/gnd/examples/refunds/labels.json --target T --out ../reader-4/exp-T`:

| Target | Export digest |
|---|---|
| rules | 7b455e99… (equal to the committed `learners/rules/run.json`) |
| popper | 39788cf3… |
| ilasp | 1acb8010… |
| neutral | f758a077… |

## F1 (hardening): the rules import admits a feature column the rules export never wrote

- **Commit:** 70266b5 (IL3) registered `rules` with no `vet`. 7818be1 then added the `off-threshold` vet to popper and ilasp only.
- **Where:**
  - `src/gnd/export/ilp_learners.py:73-75`: the rules entry has no `vet=`.
  - `src/gnd/export/ilp_rules.py:117-127` and `:199`: `_column` checks only the name's syntax.
- **Repro:** `R4/probe_rules_offcolumn.py`. It gets GND's coverage from a first call with an empty coverage, then re-runs with it.
  ```
  uv run python ../reader-4/probe_rules_offcolumn.py . ../reader-4/off451 '[[f_refund_amount__2__3__gt_t_amount__451=1]]'
  column written by export: False
  exit 0
  IMPORTED 1 learned clauses ... covers 5 (support 4/5)
  ```
  The same rule through the other two targets (`R4/probe_target_offthreshold.py`):
  - popper, `gt_t_amount__451(V2)`: exit 3, `clause 0: off-threshold`.
  - ilasp, `gt_t_amount(V1,451)`: exit 3, `clause 0: off-threshold`.
- **Expected:** a refusal like `off-threshold`, because wittgenstein only sees the columns in `features.json`, which has no 451.
- **Actual:** exit 0 and a proposal is written. The rule is still re-checked, so this is the reader accepting what its writer never writes, not an admission GND has not re-checked.

## F2 (hardening): the Popper `off-threshold` check can be avoided by changing the spelling

- **Commits:** 65fd6df (`_THRESHOLD` reads `ge`/`le` unary names; the binary IK5 spelling still parses) and 7818be1 (`check_thresholds` covers unary `gt`/`lt` only).
- **Where:** `src/gnd/export/ilp_popper.py:41`, `:146-148` and `:344-349`.
- **Repro:** `R4/probe_target_offthreshold.py` with target popper and digest 39788cf3…. `grep -c ge_t|le_t` on the export's `bias.pl` and `bk.pl` gives 0.
  - `ge_t_amount__501(V2)`: exit 0, IMPORTED, covers 4 (support 4/4).
  - `gt_t_amount(V2,451)`: exit 0, IMPORTED, covers 5 (support 4/5).
- **Expected:** a refusal. The docs give "Popper could not have learned it from the export" as the reason (ilp-bridge.md:156-159), and that is equally true of both spellings.
- **Actual:** both are admitted. The doc's literal wording ("a `gt_` or `lt_` threshold atom") matches the code; the check is narrower than its stated reason.

## F3 (completeness): the llm import does not hold answers to the thresholds its prompt lists

- **Commit:** 75a397f (IL5).
- **Where:**
  - `src/gnd/export/ilp_learners.py:68-70`: no `vet`.
  - `src/gnd/export/ilp_prompt.py:48-50` and `:114-116`: the prompt says "one of the thresholds listed".
- **Repro:** `R4/probe_target_offthreshold.py` with target llm, learner claude, digest f758a077…. The prompt offers `ge` thresholds [35 … 640, 750, 1200, 1500]; 641 is not among them.
  - `ge_t_amount` with constant 641: exit 0, IMPORTED, covers 3 (support 3/3).
- **Expected:** either a refusal, or docs that say llm, like neutral, accepts any constant.
- **Actual:** the constant is admitted and the docs say nothing.

## F4 (hardening): `tools/ilp_comparison.py` re-implements `gnd.export.ilp.refusal_name`, and the copy has drifted

- **Commit:** a75b328 (IL6).
- **Where:** `tools/ilp_comparison.py:56`, `:79` and `:112-117`.
- **Repro 1:** `R4/probe_refusal_parsers.py`. For `export-mismatch`, `coverage-shape`, `unparsable` and `facts-mismatch`, `refusal_name` returns the name while `_REFUSAL` returns None. Messages with a clause or rule index agree.
- **Repro 2:** `R4/probe_comparison_unindexed.py` builds a fake evidence root for a 3-clause program with import exit 3:
  - `export-mismatch` or `coverage-shape` gives `first_refusal` None and `clauses_not_evaluated` 0.
  - `clause 0: coverage-mismatch` gives `clauses_not_evaluated` 2, although every clause passed checks 1-10 before the set comparison (`ilp_service.py:353-358` versus `:387-413`).
- **Expected:** a binding-stage refusal is shown by name with 3 clauses not evaluated, and a set-comparison refusal leaves no clause unevaluated.
- **Actual:** the row shows "—", with 0 or 2 not evaluated.
- **Today:** no committed evidence triggers this, and `uv run python tools/ilp_comparison.py` exits 0.

## F5 (hardening): private names used across modules

- **Commits:** a75b328 and 860e651.
- **Where:**
  - `tools/ilp_comparison.py:129` imports `_mined_inputs` from `ilp_service`.
  - `src/gnd/export/ilp_service.py:521` adds another use of `gnd.evolve.service._parse_model_text`. That extends a pattern IK5 already had at `:144` and `discover/service.py:38`.
- **Repro:** `python3 ../reader-4/probe_private_names.py .` scans the lines each IL merge added:
  - 70266b5 `_threshold_rows`: fixed at HEAD.
  - 860e651 `_ilp._value`: fixed at HEAD (now `export_value`, confirmed by reading `ilp_amie.py:111`; the probe's own grep is a substring match).
  - 860e651 `_parse_model_text`: still present.
  - a75b328 `_mined_inputs`: still present.
- **Also:** the tool's `hold()` repeats the import's map-and-count sequence (`ilp_service.py:643-651`) through these private seams, without the run-record or facts bindings.

## Suspected, not reproduced

- **Mined import validation message:** if a mapped rule made the candidate model fail validation, the mined import would exit 3 with "invalid model: …" (`ilp_service.py:702-703`, `727-729`). That has no rule index or name, unlike the labelled path's `invalid-guarded`. I found no rule that triggers it.
- **Mined learner check:** `learner["name"] != entry.learner` (`:616`) ignores the tuple and None forms the labelled path handles (`:336-337`). That is latent drift; no mined entry uses those forms today.
- **Value spelling in `spell`:** int 1 and string "1" (and True and "true") are written the same way. A mixed-primitive population could make the count and the checker disagree, which would surface as exit 70, not as an admission. I found no such population that loads.

## Checked and found true

- **Tests:** `uv run pytest -q -o addopts='' tests/test_ilp_{amie,asp,bridge,learners,llm,rules}.py` gives 482 passed, 8 skipped. `tools/ilp_comparison.py` check mode exits 0.
- **Committed examples:**
  - refunds rules, popper and llm import with exit 0.
  - ilasp is refused `clause 0: empty-antecedent`, as documented.
  - staffing amie-2 imports with exit 0.
- **Report schemas:** every `--format json` report validates against its shipped schema: `ilp-import.schema.json`, and `mined-import.schema.json` at both the root and `#/$defs/report` (`R4/probe_report_schemas.py`).
- **Labelled import order:** clauses read, then the run record, `clauses-mismatch`, `export-mismatch`, `learner-mismatch`, `coverage-shape`, vet, fragment checks, check 10, coverage, `covers-nothing`. This matches the docstring and the docs.
- **Mined import order:** `learner-mismatch`, `rules-mismatch`, `population-mismatch`, `facts-mismatch`, then the mapping and the count. This matches `MINED_INPUT_REFUSALS`, `MAPPING_REFUSALS`, `COUNT_REFUSALS` and the docs.
- **Labelled work ceiling:** `P·(1+K)+K+2` equals the work actually counted.
- **Mined count cost:** bounded per rule. One rule at the 1M-row bound takes 0.07 s, so 256 rules take about 18 s (`R4/probe_amie_count_cost.py`). `canonical()` permutes at most 3 body atoms.
- **llm binding:** llm binds the neutral export with the neutral adapter version.
- **Mined admissions are re-checked:** each must get a checker verdict of "pass" on the candidate before the proposal is written.
- **Readers:** the Popper and ILASP readers are closed and capped, and their escape tables invert their renderers'.
