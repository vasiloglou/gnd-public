---
milestone: ilp-import-hardening
station: phase-IH0
skill: "n/a -- repository development via process-phase, not a gnd-solve station over a domain model"
scope: phase-IH0
date: 2026-10-29
gate:
  command: "uv run pytest -q -o addopts='' <15 files, evidence/IH0/gate.txt>"
  exit: 0
  output: "1076 passed, 8 skipped in 55.47s"
  note: >-
    The IH0 regressions plus the focused tests of every touched module and
    their documented consumers: the six ILP adapter suites, test_il_close,
    test_il6_walk, test_il6_skill_census, test_gnd_arch,
    test_development_scaffold, test_rf5_commands, test_rf1_cli_pins and
    test_release_docs. tools/ilp_comparison.py exits 0, and ruff is clean on
    the seven changed Python files.
slow_cadence:
  command: "uv run pytest -q"
  trigger: "the milestone close (IH-R3), or explicit owner selection"
  reason: "outside IH0's impact closure; the reduced selection was run"
evidence:
  - path: .gnd-planning/milestones/ilp-import-hardening/notes/phase-IH0-spec.md
    sha256: ed8dd3dcda7b82b6873918ed5c76ed6d4b3484e5e2cd0325c3333b5327fceeb1
  - path: .gnd-planning/milestones/ilp-import-hardening/notes/phase-IH0-triage.md
    sha256: e9a2a65104fd165778a181336ea9108987b84333041ec25d42424e47163c0cf6
  - path: .gnd-planning/milestones/ilp-import-hardening/notes/phase-IH0-review-1.md
    sha256: 57fa01f8f5c95a1075316e7bc27b413ff54c3d419745345a5ffe493199958e20
  - path: .gnd-planning/milestones/ilp-import-hardening/notes/phase-IH0-review-2.md
    sha256: 09674f5440675b5868610078af643873cbaa030f8b026508a2364afc71edc965
  - path: .gnd-planning/milestones/ilp-import-hardening/notes/phase-IH0-review-3.md
    sha256: d182b7b60fe9e9f45e7d6cb564474016cbe95646560c3ccbfb23de1a9c57a84a
  - path: .gnd-planning/milestones/ilp-import-hardening/notes/phase-IH0-review-4.md
    sha256: c13ffa6b95dc660794b5683c8f1f54236522671a57ac59e28902a54d24576644
  - path: .gnd-planning/milestones/ilp-import-hardening/notes/phase-IH0-fix-review.md
    sha256: 426db25eb95ff20a6c9326bca07c1049e7213882e2eed2f70e4f4a873930ec8a
  - path: .gnd-planning/milestones/ilp-import-hardening/evidence/IH0/red.txt
    sha256: ddab892040455be964b9ce06541a136344995404b84dd39a8176728034ade936
  - path: .gnd-planning/milestones/ilp-import-hardening/evidence/IH0/gate.txt
    sha256: 70b14232a99a1b1bf510fe11a227b6b949f65a77fef9e69742c85318036de396
  - path: tests/test_ih0_review.py
    sha256: 5269fafb5832c06f6f7d881d7bf6122febfa4ca1e9a4d8376a9b949629531781
---

# Phase IH0: review of the ilp-learners source changes

**The owner gate.** The plan gate ([001-plan-gate.md](001-plan-gate.md))
ruled every IH0 decision. On 2026-10-29 the owner selected the phase: "Start
IH0" (o). That selection is taken as approval of IH0 spec r2
(`ed8dd3dcda7b82b6873918ed5c76ed6d4b3484e5e2cd0325c3333b5327fceeb1`, unchanged
since the plan gate). The approval instrument is the spec's prose.

## What shipped

**The review.** Four readers (IH-D4 (o)) each read IL's nine merges as one
change, judged at `fb03739`, from the spec's verbatim brief. None saw
another's report. Together they reported 0 blocking, 19 hardening and 6
completeness findings, which collapse to the 13 rows of the
[triage](notes/phase-IH0-triage.md). The author reran the readers' probes at
`fb03739` before triage; every finding reproduced.

**The fixes**, each with a test in `tests/test_ih0_review.py`:
- **A, rules (T1, T6):** `ilp_rules.check_columns`, the rules entry's new
  `vet`, refuses `clause K: off-threshold` for a column of a declared `gt`/`lt`
  comparison at an integer position that `features.json` does not hold. Every
  other malformed column is left to the fragment table, so IL3's approved
  corpus is unchanged. `ilp_rules.IMPORT_REFUSALS` names it.
- **B, Popper `ge_`/`le_` (T1):** `ilp_popper.check_thresholds` refuses every
  unrendered threshold name of a declared comparison, not only `gt_` and
  `lt_`.
- **C, the comparison tool's refusal (T2):**
  - The tool reads a refusal's name with `ilp.refusal_name`, not its own regex.
  - An un-indexed refusal is shown without a clause.
  - A refusal before clause 0 (a binding or the threshold check) counts every
    proposed clause as not evaluated.
  - A message that names no refusal gives none.
- **D, the tool's reader (T2, T3):**
  - Output that the import refused at its reader is a row: the refusal, with
    no clause count.
  - Any other output the tool cannot read exits 2 with the directory named,
    not a traceback.
- **H, ILASP aggregates (T4):** `#sum+` is carried as `sum_plus` and an
  aggregate's elements are cut to the schema's 16, so the clause is refused
  `aggregate` by the fragment table, not by a schema error.

**Docs (IH-R4):**
- `docs/reference/ilp-bridge.md`, Import step 2: the threshold check per
  adapter, LLM and neutral named as not checked.
- The same page, Boolean rule sets: the rules refusal; `comparison-type` named
  for a non-integer position.
- The same page, Comparing the learners: the columns.
- `docs/release-notes.md`: one new section.
- T5 pins `off-threshold` in the Import and Boolean rule sets sections.
- IL3's `test_t13_the_reference_section_matches_the_code` admits
  `ilp_rules.IMPORT_REFUSALS` among the documented names. That widens a
  documentation pin; no approved answer changes.

**No golden moved.** The committed comparison table, the committed live-run
evidence and every approved corpus answer are unchanged
(`tools/ilp_comparison.py` exits 0). Each committed learner output used a
threshold its export offered: Popper `gt_t_amount__500`, rules `…__450`, LLM
`ge_t_amount` 640.

## Gate output (verbatim)

From [evidence/IH0/gate.txt](evidence/IH0/gate.txt):

```
$ uv run pytest -q -o addopts='' tests/test_ih0_review.py tests/test_ilp_amie.py tests/test_ilp_asp.py tests/test_ilp_bridge.py tests/test_ilp_learners.py tests/test_ilp_llm.py tests/test_ilp_rules.py tests/test_il_close.py tests/test_il6_walk.py tests/test_il6_skill_census.py tests/test_gnd_arch.py tests/test_development_scaffold.py tests/test_rf5_commands.py tests/test_rf1_cli_pins.py tests/test_release_docs.py
1076 passed, 8 skipped in 55.47s
exit: 0
$ uv run python tools/ilp_comparison.py
exit: 0
$ uv run ruff check src/gnd/export/ilp_rules.py src/gnd/export/ilp_popper.py src/gnd/export/ilp_asp.py src/gnd/export/ilp_learners.py tools/ilp_comparison.py tests/test_ih0_review.py tests/test_ilp_rules.py
All checks passed!
exit: 0
```

`uv run ruff check src tools tests` exits 1, on findings only in files IH0
does not touch; CI does not run ruff.

**Red at the fix's parent.** The 20 tests of `tests/test_ih0_review.py` were
run against `cbc97b2`, whose `src` and `tools` are byte-identical to
`fb03739`: 16 failed and 4 passed ([evidence/IH0/red.txt](evidence/IH0/red.txt)).
The 4 that pass are controls:
- an offered threshold passes the check, for rules and for Popper;
- a fragment refusal's count was already right;
- the Import section already named `off-threshold`.

All 20 pass after the fix. A 21st test, added after the red run, is the
spec's widened privacy check over this milestone's directory; it is a pin, not
a finding's regression.

## Review

**The source review:** four readers, retained verbatim and sanitized as
[review 1](notes/phase-IH0-review-1.md), [2](notes/phase-IH0-review-2.md),
[3](notes/phase-IH0-review-3.md) and [4](notes/phase-IH0-review-4.md). The
harness refused the readers' report files, so each report arrived as message
text. Reader 4's probe scripts did not persist; each of its findings is
reproduced by another reader's probe.

**The fixes' review:** one reviewer over the fix diff
([fix review](notes/phase-IH0-fix-review.md)); one reviewer is one reviewer.
It found one wrong admission in the new rules check (FR1), reproduced by the
author and fixed with T6. It also found two documentation errors and two tool
gaps, all fixed. It confirmed that:
- the aggregate truncation cannot turn a refusal into an admission;
- the threshold check runs before any clause is rewritten;
- the red run is exactly as recorded.

**The repairs after the fix review carry no review opinion.**

## Refactoring review

**Refactor executed:**
- The tool's drifted copy of the refusal-name parser (finding C) is replaced
  by the public `ilp.refusal_name`.
- `ilp_rules._suffix`, dead since IL3, is now the one spelling of a
  threshold in `check_columns`.

Both landed behind the gate above.

**Seen and deferred:**
- **The offered-threshold check now has three forms:** Popper by name, ILASP
  by constant, rules by column. They agree on the cases tested. A shared home
  is worth it only if the held LLM and Popper-spelling checks land; the
  question is carried as IH0-Q4 to the batched ruling.
- **The tool's `hold()` still parses rule refusals with `_REFUSAL`** and
  imports `_mined_inputs`. IH1 replaces both (finding E).

## Boundary -- what this phase does NOT establish

- **A review is a disagreement locator, not a proof.** Tests, docs and
  evidence were out of the readers' scope (IH-D2 (o)). (Residual, copied
  forward from the plan.)
- **One reviewer is one reviewer** for the fix review, and its repairs are
  unreviewed.
- **Two fixes are held, not applied:** the LLM threshold check and Popper's
  binary and infix spellings, below. Until the owner rules, an LLM answer and
  a binary or infix Popper comparison can still use an unoffered threshold.
  GND still re-checks every such clause before admission.
- **The reverse subtype case** of FR1 is covered by the same condition, but
  not run.
- **Reader 3's `p6`** (export work at 20,000 values) was not rerun; finding K
  is deferred.
- **No learner, solver or model ran** (IH-R1).
- **Coverage:** the readers judged `fb03739` only. This record certifies
  nothing about IL's tests or docs.

## Held for the owner (IH0-D4 (o))

Two fixes would move approved answers of earlier corpora. Each was measured,
not committed:
1. **The LLM threshold check.** It is applied to the LLM import the way ILASP's
   is. It moves IL5's `i13-two-comparisons` from `multiple-comparisons` to
   `off-threshold`.
2. **Popper's binary and infix spellings.** Refusing an unrendered threshold
   in those spellings refuses the IK5 corpus's `I2` and `F12`, and fails two
   IK5 T5 tests.

## Open questions

| ID | Question | Target |
|---|---|---|
| IH0-Q1 | Popper and ILASP name a negated off-threshold literal differently (G) | this milestone's close, for assignment |
| IH0-Q2 | The export's work report leaves out threshold rendering (K) | this milestone's close, for assignment |
| IH0-Q3 | The `llm` entry's `adapter_version` is never read (L) | this milestone's close, for assignment |
| IH0-Q4 | One home for the offered-threshold check | the batched ruling (IH0-D4) |
| — | E, F and J are assigned to IH1; the own-reference suspicions to IH2 | IH1, IH2 |

## Refuted premises

- **IL's close record (`../ilp-learners/009-milestone-close.md`, line 212)
  lists Popper's unrendered thresholds as "fixed, R8".** Reader 3 showed the
  `ge_`, `le_`, binary and infix spellings were still admitted. IH0 fixes
  `ge_` and `le_`; the rest is held. The IL record is not edited.
