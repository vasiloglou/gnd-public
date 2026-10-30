# IH0 triage: the ilp-learners source review

Four readers (IH-D4 (o)) each read IL's nine merges, `git diff m^1 m -- src
tools`, as one change, judged at `fb03739`. Each had the spec's brief verbatim and
saw no other reader's report. Their reports are retained as
[review 1](phase-IH0-review-1.md), [2](phase-IH0-review-2.md),
[3](phase-IH0-review-3.md) and [4](phase-IH0-review-4.md).

| Reader | Blocking | Hardening | Completeness |
|---|---|---|---|
| 1 | 0 | 5 | 0 |
| 2 | 0 | 6 | 2 |
| 3 | 0 | 4 | 3 |
| 4 | 0 | 4 | 1 |

**No reader reported a blocking finding,** and none survived reproduction:
every admission the readers found was re-checked by GND before it was written.

## Reproduction

The author reran the readers' probes in a detached worktree at `fb03739`
before believing them. These were rerun, all exiting 0, with output matching
their reports:
- reader 1: `p01`, `p03`, `p05`, `p06`;
- reader 2: `probe1`, `probe6`, `probe7`, `probe8`, `probe10`, `probe11`, `probe12`;
- reader 3: `p1`, `p2`, `p3`, `p5`, `p7`.

Reader 4's probe scripts did not persist. Each of its findings is reproduced
by another reader's probe for the same defect, named in the table. Reader 3's
`p6` (a 20,000-value render) was not rerun; finding K is deferred, so nothing
rests on it.

## Findings

A finding several readers report is one row. "Golden" means an approved
expected answer of an earlier corpus.

| # | Finding | Readers | Class | Reproduced by | Disposition |
|---|---|---|---|---|---|
| A | `rules` and `llm` imports admit a threshold their export never offered | 1 F1, 2 F1, 3 H1, 4 F1 and F3 | hardening | r1 `p01`, r2 `probe11`, r3 `p1` | **rules: fixed** (`ilp_rules.check_columns`, T1). **llm: held for the batched ruling (IH0-D4):** checking the LLM's constants before the fragment table moves IL5's approved case `i13-two-comparisons` from `multiple-comparisons` to `off-threshold` |
| B | Popper `off-threshold` misses other spellings of the same threshold | 1 F2, 2 F2, 3 H2, 4 F2 | hardening | r1 `p03`, r2 `probe7`, r3 `p1` | **`ge_` and `le_` names: fixed** (T1). **The binary atom, an infix comparison, and a constant beyond clingo's range: held for the batched ruling (IH0-D4):** measured with a trial check in a scratch copy: it refuses the IK5 corpus's approved cases `I2` and `F12`, and fails `test_t5_outputs_validate_against_their_schemas` and `test_t5_popper_and_neutral_runs_add_the_same_rules` |
| C | The comparison tool's refusal regex drifted from `ilp.refusal_name`, so an un-indexed refusal shows as none, with 0 clauses not evaluated | 1 F3, 2 F6, 3 H3, 4 F4 | hardening | r1 `p05`, r2 `probe6` (a), r3 `p2` | **fixed** (T2). Reader 4 also argued that a set-comparison refusal leaves no clause unevaluated. That is not adopted: the page defines the column as the clauses after the first refusal |
| D | The comparison tool crashes with a traceback and exit 1 when its reader refuses labelled output | 1 F4, 2 F7 | hardening | r1 `p06`, r2 `probe6` (b) | **fixed** (T3): exit 2 with the directory and the refusal named |
| E | `tools/ilp_comparison.py` imports the private `ilp_service._mined_inputs`; `hold()` repeats the import's map-and-count | 1 F5, 2 F8, 3 (noted), 4 F5 | hardening | r1 `p05`, r2 `probe12` | **assigned to IH1** (IH0-D3 (o)): IH1's public `load_mined_inputs` and `count_mined_rules` replace both |
| F | `gnd import mined-rules` loads the population before checking `population-mismatch`, so a bad population exits 5, not 3 | 2 F5, 3 H4 | hardening | r2 `probe8`, r3 `p3` | **assigned to IH1** (IH0-D3 (o)): it sits in `_mined_inputs`, which IH1 replaces |
| G | Popper and ILASP name a negated off-threshold literal differently (`off-threshold` versus `negation-as-failure`) | 2 F3 | hardening | r2 `probe1` | **carried as IH0-Q1:** both refuse with exit 3 by name; only which name comes first differs |
| H | An ILASP `#sum+` aggregate, or one with more than 16 elements, fails schema validation instead of `aggregate` | 2 F4 | hardening | r2 `probe10` | **fixed** (T4) |
| I | `ilp_rules._suffix` is dead code | 2 F8 | completeness | r2 `probe12` | **resolved by A:** `check_columns` uses it |
| J | `ilp_amie.EXPORT_REFUSALS` omits `opaque` and `too-large` | 3 C1 | completeness | r3 `p5` | **assigned to IH1**, which edits `ilp_amie` |
| K | The export's work report leaves out Popper's and rules' threshold rendering | 3 C2 | completeness | not rerun | **carried as IH0-Q2** |
| L | The `llm` entry's `adapter_version` is never read | 3 C3 | completeness | r3 `p7` | **carried as IH0-Q3** |
| M | `ilp_service` imports `evolve.service._parse_model_text` | 2 F8, 3, 4 F5 | — | r2 `probe12` | **out of scope:** the pattern predates IL (IK5, `discover`); IL's merge added one more use |

## Refuted premise

Reader 3 (H2) showed that the IL close record's claim at
`../ilp-learners/009-milestone-close.md` line 212 was too wide. It records the
Popper reader's acceptance of unrendered threshold values as "fixed, R8". The
`ge_`, `le_`, binary and infix spellings were still admitted. IH0 fixes the
`ge_` and `le_` names, and the rest waits on the batched ruling. The close
record is not edited: it describes its own bytes.

## Suspected, not reproduced

| Suspicion | Readers | Disposition |
|---|---|---|
| A mapped AMIE rule that fails whole-model validation is reported as "invalid model", with no rule index | 1, 3, 4 | no reader built such a rule; IH1 owns the import's order and names it |
| The count and the checker disagree on an own-reference subtype join, exiting 70 | 1, 2 | the opposite direction is reproduced (plan, IH2); IH2 owns it |
| The mined learner check ignores the tuple form | 4 | latent: no mined entry uses it; IH1 |
| `spell` writes `1` and `"1"` alike | 4 | no loading population found; IH2 |
| No total work ceiling across mined rules | 3 | bounded per rule (IL4-D7); not timed |
| The vet can name a later clause than a fragment refusal | 2 | documented order (step 2 before step 3); no change |

## Held for the owner (IH0-D4)

Two fixes would change an earlier milestone's approved expected answers. Under
IH0-D4 (o) they are put to the owner as one ruling, not applied:

1. **The LLM threshold check (A, llm).** Checking every integer constant of a
   comparison against the prompt's list moves IL5's case
   `i13-two-comparisons` from `multiple-comparisons` to `off-threshold`
   (observed: `tests/test_ilp_llm.py` failed on that case with the check in
   place).
2. **Popper's other spellings (B).** Refusing a binary threshold atom or an
   infix comparison whose constant is not rendered refuses the IK5 corpus's
   approved cases `I2` and `F12`, which are admitted today. This was measured
   with a trial check in a scratch copy, not committed.

## The fixes' review

One reviewer read the fixes' diff against `cbc97b2`
([fix review](phase-IH0-fix-review.md)); one reviewer is one reviewer. The
author reran F1's probe (`probe_import.sh` over the reviewer's subtype model)
before repairing: exit 0, admitted, and `features.json` holds no `gt_t_fee`
column. F3 and F4 are reproduced by the tests that now pin them (T2), red at
`cbc97b2`.

| # | Finding | Reviewer's class | Disposition |
|---|---|---|---|
| FR1 | `check_columns` skipped a cross-type integer column, which a value subtype lets through the fragment table | blocking | **fixed** (T6): every column of a declared `gt`/`lt` comparison at an integer position is checked. Triaged as hardening, like A: the code before IH0 admitted the same rule, and GND re-checked it. The reverse case (a subtype position with a supertype comparison) is covered by the same condition, but not run |
| FR2 | The rules section names `comparison-type` for any type clash; an integer clash is `type-confused-join` or, now, `off-threshold` | completeness | **fixed:** the sentence names a non-integer position |
| FR3 | Output the import refused at its reader could form no table row | completeness | **fixed** (T2): the row reports the import's refusal, with no clause count, when the tool's reader names the same refusal; otherwise exit 2 as before |
| FR4 | A message that names no refusal became a "name", with its newline | hardening | **fixed** (T2): such a message gives no first refusal, and no not-evaluated count |
| FR5 | The release note's "16 elements" counts terms and conditions | minor | **fixed:** the wording |

The repairs after this review carry no review opinion.
