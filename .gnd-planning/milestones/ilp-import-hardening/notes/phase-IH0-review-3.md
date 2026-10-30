# IH0 review, reader 3 (verbatim, sanitized)

> Retained by the author. The reader returned this report as message text because the harness refuses report files from subagents; the text is otherwise verbatim. **Edited:** the session scratch path is replaced by `<scratch>`. One reader is one reader.

# IH0 reader-3: review of the ilp-learners (IL) milestone's source changes

I could not save `report.md`: the Write tool refused it ("Subagents should return findings as text"), and I did not work around that through Bash. The full report is below. Probe scripts and their saved outputs (`p1.out` to `p7.out`, `p8_private_names.out`) are in `<scratch>/IH0/reader-3/`. The subject checkout is unmodified (`git status` is clean).

**Count: blocking 0, hardening 4, completeness 3.**

I read `git diff m^1 m -- src tools` for 65fd6df, 426bd80, 75a397f, e30eec8, 70266b5, 860e651, a75b328, 7818be1 and fb03739 as one change; e30eec8 and fb03739 are empty under src and tools. No learner, solver or model was run. Every command below runs from the subject checkout.

## Findings

### H1 (hardening). Only Popper and ILASP refuse `off-threshold`; `rules` and `llm` admit a threshold the export never offered
- **Origin:**
  - 70266b5: the `rules` entry has no `vet`.
  - 75a397f: the `llm` entry has no `vet`.
  - 7818be1: added `Learner.vet` to `popper` and `ilasp` only.
- **Where:**
  - `src/gnd/export/ilp_learners.py:72-77`
  - `src/gnd/export/ilp_rules.py:117-127`: `_column` checks spelling only.
- **Reproduction:** `uv run python ../reader-3/p1_off_threshold.py` (output in `p1.out`). The rules export offers `gt_t_amount` thresholds `[35, …, 450, 500, 640, 750, 1200]`. The same rule, amount > 451, gives:
  - rules column `…gt_t_amount__451=1`: exit 0, consequent `<= 451` admitted.
  - popper `gt_t_amount__451`: exit 3, `clause 0: off-threshold`.
  - ilasp `gt_t_amount(V,451)`: exit 3, `off-threshold`.
  - llm `gt_t_amount(A,451)`: exit 0, admitted.
- **Expected vs actual:** the same off-threshold value should be refused by every adapter whose export fixes the thresholds. Instead `rules` reads a column `features.json` never wrote, and `llm` accepts a constant outside the prompt's list. GND still re-checks coverage, so this is not an unchecked admission. The IL3 record deferred this to IL2-Q3, and the close repaired IL2-Q3 for ILASP and Popper only.

### H2 (hardening). Popper's `off-threshold` check can be bypassed with a `ge`/`le` threshold or the binary IK5 spelling
- **Origin:**
  - 7818be1: `check_thresholds`.
  - 65fd6df: `_THRESHOLD` reads `ge`/`le`, and binary comparison atoms are kept.
- **Where:** `src/gnd/export/ilp_popper.py:148` checks only `>` and `<`; lines 41 and 344 hold the parser mapping.
- **Reproduction:** `p1.out`.
  - `ge_t_amount__451(V2)`: exit 0, admitted.
  - `gt_t_amount(V2,451)`: exit 0, admitted.
  - `bias.pl` declares neither a `ge_` threshold nor a binary `gt_t_amount`.
- **Expected vs actual:** `009-milestone-close.md:212` says the Popper reader's acceptance of unrendered threshold values is "fixed, R8", because Popper could not learn such a value. Popper cannot learn these two spellings either, yet the same value 451 is refused in one spelling and admitted in the other two. Bridge page line 156 limits the check to `gt_`/`lt_`, so code and page agree; it is the close record's claim that is too wide.

### H3 (hardening). `tools/ilp_comparison.py` shows an un-indexed refusal as no refusal, with every clause counted as evaluated
- **Origin:** a75b328. Its regex has drifted from `ilp.refusal_name`, which handles both forms.
- **Where:** `tools/ilp_comparison.py:56` (`_REFUSAL` needs a `clause K:` or `rule K:` prefix), lines 75-80, and lines 113-118, where `not_evaluated = 0` regardless of the exit.
- **Reproduction:** `uv run python ../reader-3/p2_comparison_unindexed.py` (output in `p2.out`). It edits only a temporary copy of the evidence. After replacing the import's stderr with an `export-mismatch` or `unparsable` refusal, the row reads `{'import_exit': 3, 'first_refusal': None, 'clauses_not_evaluated': 0}`.
- **Expected vs actual:** a binding or parse refusal should be named in the table, and unevaluated clauses should not be reported as 0. The table instead shows "—" and 0, and the tool still exits 0. The committed evidence has only indexed refusals, so today's table is correct.

### H4 (hardening). `gnd import mined-rules` loads the model and population before checking the population binding
- **Origin:** 860e651.
- **Where:** `src/gnd/export/ilp_service.py:623-626`. The docstring at lines 584-587 says the bindings come before the model and population load.
- **Reproduction:** `uv run python ../reader-3/p3_mined_order.py` (output in `p3.out`).
  - The committed amie-2 record imports with exit 0.
  - The same record with a different population that fails to load gives exit 5, "population … failed to load".
- **Expected vs actual:** the record's digest is of the population's bytes, so `population-mismatch` (exit 3) can be checked before the load, as `rules-mismatch` and `learner-mismatch` already are. The load failure (exit 5) wins instead.

### C1 (completeness). The AMIE export raises refusal names missing from `ilp_amie.EXPORT_REFUSALS`
- **Origin:** 860e651.
- **Where:** `src/gnd/export/ilp_amie.py:50`. `opaque` comes from `export_value` via `spell` at line 111; `too-large` comes from `render` at lines 194-195.
- **Reproduction:** `uv run python ../reader-3/p5_amie_export_names.py` (output in `p5.out`).
  - A real `{ $opaque: "x" }` cell through the CLI gives exit 3 with `opaque: …`.
  - With `ilp.MAX_FACTS` lowered in-process, the export refuses `too-large`, which is not in `EXPORT_REFUSALS`.
- **Expected vs actual:** the tuple `test_c8c` uses as its pin should list every name the export can refuse. The generic Export section of the doc does name both, so only the pin is incomplete.

### C2 (completeness). The export's work report leaves out the Popper and rules threshold rendering
- **Origin:** 65fd6df; the rules adapter in 70266b5 uses the same `threshold_rows`.
- **Where:** `src/gnd/export/ilp_service.py:214-221`; `src/gnd/export/ilp_popper.py:115-131` and line 163.
- **Reproduction:** `uv run python ../reader-3/p6_popper_render_work.py 20000` (output in `p6.out`), on a synthetic refunds copy with 20,000 distinct amounts.
  - The neutral and popper exports both report `work 60059 (ceiling 500008)`.
  - Popper's `bk.pl` has 700,019 lines (18.8 MB), of which 639,968 are threshold-extension lines.
- **Expected vs actual:** the work line and the Bounds table ("populations + facts") should describe the export's actual work. The threshold extensions, 32 lines per distinct value per integer type, go unreported. The work is still bounded: the 64 MiB file cap applies in `index_tree`, but only after the whole rendering is built in memory.

### C3 (completeness). The `llm` registry entry's `adapter_version` (`PROMPT_VERSION`) is never read
- **Origin:** 75a397f.
- **Where:** `src/gnd/export/ilp_learners.py:72-74`; `src/gnd/export/ilp_service.py:169-172` swaps in the bound entry first.
- **Reproduction:** `uv run python ../reader-3/p7_llm_adapter_version.py` (output in `p7.out`). Setting the field to "999" leaves the export digest unchanged (`f758a077…`).
- **Expected vs actual:** the field's docstring calls it the target's `export.json` version, but for a binding entry it is dead. No record binds the prompt version; only the golden tests track prompt changes.

## Private names across modules (noted, not counted as findings)
Source: `p8_private_names.out`.
- `tools/ilp_comparison.py:129` (a75b328) imports `ilp_service._mined_inputs`. Its `hold()` at lines 123-148 copies the import's map-and-count pipeline. I found no drift in that copy; the only drifted duplicate is the H3 regex.
- `ilp_service._mined_inputs` (860e651, line 521) imports `gnd.evolve.service._parse_model_text`. This follows the existing pattern in `_prepare` and `discover/service`, so it is not new to IL.

## Suspected, not reproduced
- **No per-rule validation in the mined import.** It has no check 10 per rule. If the whole candidate (`ilp_service.py:702`) failed validation, the user would see "invalid model" (exit 3), which blames MODEL; the labelled import treats the same case as exit 70. I found no valid input that triggers it.
- **No total work ceiling for mined rules.** The worst case is 256 × 10^6 join steps with no work report. Each rule has its own cap (IL4-D7), so this is bounded. I did not time it.

## Claims checked and found true
- **Target lists agree.** The parser `choices=` tuples, `EXPORT_TARGETS`, `IMPORT_TARGETS`, `MINED_TARGETS` and both schema enums match: `amie` is not an ilp-rules import target and `llm` is not an export target. A misused `--labels` or `--population` exits 64.
- **All four readers are total.** 30,000 random texts each raised only `IlpError` (`p4.out`), and their caps hold.
- **Writers and readers round-trip.** ILASP string escapes match the renderer. Rules column names are self-checked at render. Popper writes booleans bare and strings quoted.
- **AMIE family spelling is safe.** A cross-family join never counts as met, so it ends in `covers-nothing` or `does-not-hold`. Admission also needs the checker's `pass`; a disagreement exits 70. No mined rule is admitted unchecked.
- **Labelled admission re-checks everything.** It runs the fragment table with check 9b always on, per-clause validation, checker re-evaluation, an exact set comparison and `covers-nothing`. The work ceiling matches the reloads.
- **Refusal order matches the declared tuples**, except H4.
- **`refusal_name` parses correctly.** It reads the `clause K:`, `rule K:` and bare forms.
- **Prompt lines cannot be forged.** Host text is neutralized, data lines are ASCII JSON, and reserved lines are refused `forged-line`.
- **Repository checks pass.**
  - The IL tests (amie, asp, bridge, learners, llm, rules, il_close, il6_walk, il6_skill_census): 588 passed, 8 skipped.
  - test_gnd_arch, rf5_commands and rf1_cli_pins: 425 passed.
  - `uv run python tools/ilp_comparison.py` exits 0.
