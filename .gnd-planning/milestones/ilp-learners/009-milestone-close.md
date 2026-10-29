---
milestone: ilp-learners
station: milestone-close
skill: "n/a -- repository development under the approved close plan (notes/close-plan.md), not a gnd-solve station"
scope: IL-close
date: 2026-10-29
source_base: a75b328
gate:
  command: "uv run pytest -q -p no:randomly <evidence/IL-close/gate-files.txt>"
  exit: 0
  output: "1281 passed, 24 deselected in 273.13s (0:04:33)"
  note: >-
    The part A gate (008): IL6's 23-file gate, which is cumulative over IL1
    to IL6, plus tests/test_il_close.py, run after the review fixes (cbc6432;
    a ruff import-order fix followed, no behaviour). T9 on the same bytes:
    both wheel origins, 229 tutorial blocks each. The gate was re-run on the
    final close bytes, after parts B to D (evidence/IL-close/close-gate.txt);
    its test_ilp_learners T8 scans this directory for private paths. After
    the predicate-7 review's fixes the same gate gave 1290 passed, 24
    deselected in 148.58s (evidence/IL-close/p7-gate.txt).
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner selection or separately configured CI"
  reason: "outside the milestone's impact closure; the reduced v6.3 selection was run"
---

# ILP learners -- milestone close

**Status: closed pending owner acceptance.** The close review (part D) ran
over the draft and its findings are applied below. Owner acceptance is recorded
separately, after the PR; this record does not claim it.

The close follows the [close plan](notes/close-plan.md), approved by the owner
on 2026-10-29: A repairs, B plan repairs, C the question sweep, D the close
review, E this record and the PR.

## What the milestone shipped

Five learners on one bridge, each run for real, with every result re-checked
by GND (`002` to `008`, PRs #56, #57, #58, #60, #61, #62 and this close):

| Adapter | Learner | Runs | Outcome of the run of record |
|---|---|---|---|
| `popper` | Popper 5.0.1 | 3 (2 and 3 owner-ruled) | `rendering-rejected`; invocation 3 admitted |
| `ilasp` | ILASP 4.4.1 | 1 | refused `empty-antecedent` (recorded as is, IL2-F7) |
| `llm` | the `claude` agent | 1 | admitted |
| `rules` | wittgenstein RIPPER | 1 | admitted, support 4/5 |
| `amie` | AMIE 4.0.0 | 2 (2 owner-ruled) | refused `does-not-hold`; invocation 2 admitted |

- **One learner registry** (IL1), with the join check 9b and SWI octal escapes.
- **ILASP** export and closed ASP reader (IL2); **rule sets** feature export and
  reader (IL3); **AMIE** typed triples, `gnd import mined-rules` and GND's own
  head-pair count (IL4); the **LLM proposer** (IL5).
- **The comparison** (IL6): `tools/ilp_comparison.py`, the table in
  `docs/reference/ilp-bridge.md`, and `docs/how-to/compare-ilp-learners.md`,
  which replays every run from committed outputs.
- **The close repairs** (`008`): subtype joins counted by family; the mined
  run record binds the facts the miner read; infix comparison joins; ILASP
  `off-threshold`; the Popper extractor and booleans; public names; the
  comparison tool fails loudly.

## Completion predicates (plan, "Goal, status and completion predicates")

| # | Predicate | Verdict | Where |
|---|---|---|---|
| 1 | IL1: one registry; IK5/IK6/RF1 goldens byte-identical except D12/D13 refusals; join check; octal escapes; one real Popper run, replayed | MET WITH DEVIATION, owner-ruled: the IL1 amendments moved named IK5 goldens, and the IL1-F1 ruling dropped the neutral `learner-mismatch` refusal, so the neutral target accepts any learner name | `002` |
| 2 | IL2: ILASP task golden under two seeds; learned rules through the shared checker; one run replayed | MET; FastLAS was not integrated: IL2-D1 was ruled (a), "ILASP 4.4.1 only" | `003`; `notes/phase-IL2-spec.md` §13 |
| 3 | IL3: thresholded feature export; positive single-feature conjuncts; refusals by name; all-or-nothing; one run replayed | MET. The milestone goal's "integer-programming or certifiable" family was **not delivered**: IL3-D1 (a), owner-ruled, integrated RIPPER instead. One run is read as the rule-set result although RIPPER is not deterministic under its seed (IL3-F5, carried) | `005` |
| 4 | IL4: typed relations; `guarded` import; GND support and confidence; `support-mismatch`; holds only; one run replayed | MET WITH DEVIATION: the count compared is AMIE's Support, not a positive-example count, which AMIE does not print (IL4-F4). Joins through a reference-inheriting subtype were false refusals until `008`; through an own-reference subtype they still are (carried) | `006`, `008` |
| 5 | IL5: `llm` entry; JSON through the shared re-check; one run after D8 | MET WITH RESIDUAL: the agent's `learner.version` is `unreported` and the model id is an unverified claim (IL5-F7, IL5-Q6 carried) | `004` |
| 6 | IL6: the walk exits as recorded; the comparison table; docs, skills, entry points with census checks | MET WITH DEVIATION, owner-ruled: `amie` runs on the staffing fixture, not refunds (IL4-D4 (o)) | `007` |
| 7 | Every phase: approval, focused checks, one reviewer, refactoring review, a record | MET, after the predicate-7 review (below): the code that changed after its phase's review (IL1's review fixes, amendment-2 rendering and refactor, `002`; IL2's fixes, D13/D14 code and step 5 refactors, `003`) now has one reviewer's opinion, and its three findings are fixed. One reviewer is one reviewer. Neither review read the milestone diff as a whole (below) | `002`–`008`; `notes/phase-IL-close-p7-review.md` |
| 7 | Close: four-reviewer evidence; question sweep; PR; owner acceptance recorded separately | review: five reviewers over the plan, this record and the close plan, not the diff; sweep below; PR and acceptance pending | this record |

## Plan notes (part B)

Added to `notes/ilp-learners-plan.md` at the owner's direction without
review (plan §8, p2). Each is an italic `(c)` note after the approved text,
which stays as approved. The first draft rewrote approved criteria instead;
the close review found that changed their intent (agreed group G1, below), so
the approved wording was restored and each deviation is now stated beside it
with the ruling that allowed it.

| Row | Note |
|---|---|
| IL3-Q4 | §1: IL3-D1 (a) integrated RIPPER; no integer-programming or certifiable learner was integrated |
| IL4-Q5 | Goal 6 and IL6-C1: `amie` ran on the staffing fixture (IL4-D4 (o)) |
| IL4-Q5 | §4 IL4: the count compared is AMIE's Support (IL4-F4) |
| IL2-Q4 | IL-R9: ILASP, RIPPER, AMIE and the agent CLIs have no timeout of their own |
| IL1-Q7 | Goal 1 and the §9 IL1 row: the IL1 amendments moved named IK5 goldens |
| IL1-F1 | IL1-C2 and §5: the neutral `learner-mismatch` refusal was dropped |
| IL6 refuted premise 2 | §5: a third pin site, gnd-solve's Station 6 |
| Status | The header gives the approved digest from `001-plan-gate.md` and says these bytes are r3 plus the notes |

## Question sweep (part C)

Every open-question row from `002` to `008`.

| Row | Disposition |
|---|---|
| IL1-Q1 | **fixed** in `008` (C4) |
| IL1-Q2 | **discharged**: IL5 added `binds`, and `contract` varies by entry (IL4) |
| IL1-Q3 | **discharged**: IL2 refuses threshold names the renderer never writes (IL2-D8), and the predicate-7 review's fix refuses a Popper threshold value outside the export's set as `off-threshold`, as `008` does for ILASP (R8) |
| IL1-Q4 | **fixed** in `008` (C6) |
| IL1-Q5 | **fixed** in `008` (C8a, C8b) |
| IL1-Q6 | **carried**: reproducibility and a larger domain, to a later evaluation milestone (owner, 2026-10-29) |
| IL1-Q7 | **plan noted** (part B) |
| IL2-Q1 | **fixed** in `008` (C7); ILC-F5 accepted |
| IL2-Q2 | **carried**: the ILASP bias amendment and a rerun, to a later evaluation milestone |
| IL2-Q3 | **fixed** in `008` (C5) |
| IL2-Q4 | **plan noted** (part B) |
| IL5-Q1, IL5-Q2, IL5-Q3 | **closed**: ruled 2026-10-28 |
| IL5-Q4 | **discharged** in IL3 (`live_common`) |
| IL5-Q5 | **carried**: to the milestone that owns verbalization (owner: "Defer both") |
| IL5-Q6 | **carried**: to the milestone that owns `gnd.agents` |
| IL3-Q1 | **closed**: the census row is enough (owner) |
| IL3-Q2 | **fixed** in `008` (C9) |
| IL3-Q3 | **carried**: RIPPER's run-to-run variation, to a later evaluation milestone |
| IL3-Q4 | **plan noted** (part B) |
| IL4-Q1 | **partly fixed** in `008` (C1, R1, R2): joins through a reference-inheriting subtype count as the checker does. Joins through an own-reference subtype are still refused `support-mismatch`, a false refusal: **carried** |
| IL4-Q2 | **fixed** in `008` (C2, R4, R6) |
| IL4-Q3 | **partly fixed**: `ilp.export_value` is public (C9). Moving the per-rule provenance into `ilp_amie` was not in the ruled scope; **carried** with IL-close-Q1 |
| IL4-Q4 | **discharged** in IL6: invocation 2 ran and was admitted |
| IL4-Q5 | **plan noted** (part B) |
| IL6-Q1 | **fixed** in `008` (C8c) |
| IL6-Q2 | **fixed** in `008` (C3, R5) |
| IL6-Q3 | **carried**: one outcome schema across live-run records, to a later milestone |
| `007` refactoring deferral | `tools/ilp_comparison.hold()` imports the private `ilp_service._mined_inputs`. **Carried** with IL-close-Q1: a public "count mined rules" entry serves the tool and the import |
| ILC-F5, ILC-F6 | **accepted** by the owner, 2026-10-29 |
| ILC-F9 | **returned to the owner**: an IL2 extractor test's expectation moved to the recorded IL2-F8 rule (predicate-7 review, finding 3) |
| IL-close-Q2 | **carried**: whether clingo reads `_1` and `-2147483648` as the ASP reader does (predicate-7 review, not reproduced without clingo) |
| IL-close-Q1 | **carried**: one rendering pass for `facts-mismatch` and the count |

**Carried forward, for the successor:**

| Row | Target |
|---|---|
| IL1-Q6, IL2-Q2, IL3-Q3, IL6-Q3 | a later evaluation milestone: reproducibility, the ILASP bias rerun, RIPPER's variation, one outcome schema |
| IL5-Q5 | the milestone that owns verbalization |
| IL5-Q6 | the milestone that owns `gnd.agents` |
| IL4-Q3 (remainder), IL-close-Q1, the `hold()` import | the next milestone that changes the mined import: one public counting entry, one rendering pass |
| IL4-Q1 (own-reference subtypes) | the same milestone: count a join through an own-reference subtype, or refuse it by name |
| IL-close-Q2 | the same milestone as IL2-Q2's rerun: run clingo over the two readings and refuse what it reads differently |
| The milestone diff as a whole | the owner's call at acceptance: a diff review of `07f4d45^..HEAD` before or after merge |

## Close review (part D)

**Instrument.** The maintained six-seat panel, launched with
`uv run python tools/run_gnd_review_panel.py close-review-request.json --out panel-run --reviewer-timeout 900 --overall-timeout 1200`
from a disposable worktree at `24e0e14`, after the launcher's credential and
OpenRouter checks passed. Request kind `spec-results-delta`: the plan (spec),
this record's draft (results) and the close plan (delta), with a six-criterion
rubric. **Exit 0, quorum established.** Six attempted, **five succeeded**
(claude, codex, gemini, kimi, glm); qwen exited nonzero. The reviewed
artifacts were unchanged after the run. `gnd review finalize` exited 0: 4
agreed concerns, 7 divergent, 4 prioritized fixes. Evidence:
`evidence/IL-close/panel/` (request, run directory, synthesis,
`PANEL-REVIEW.md`). The panel is advisory: five models agreeing is not
acceptance.

**One retained stream is sanitized.** codex's `stderr` named the scratch
directory, whose path holds a home-directory token that IL-R10's privacy test
refuses (the panel had already masked the username). The path was replaced by
`<scratch>/panel-tree`. Its envelope still binds the original bytes, so that
one stream no longer re-verifies against the run; the synthesis and
`PANEL-REVIEW.md` were finalized over the original bytes.

| File | SHA-256 as run (bound by the envelope) | SHA-256 committed |
|---|---|---|
| `evidence/IL-close/panel/panel-run/reviewers/codex/stderr` | `28dbe867b5ed4bc499ab467b7ff52d17e39314c6db22810e3c43f91a49ce0b94` | `73b2407c06d1b24f1af95c7c6b4ff612a962189e16636fd804cd4d379f54f2c8` |

**The bar.** The plan asks for four reviewers at close; five succeeded. **The
input was narrower than the close plan committed.** The close plan named "the
milestone diff `07f4d45^..HEAD`"; a panel request names one spec, one result
and one delta, so the diff was not offered (claude, divergent). Reviewers read
the phase records for context, not the code. The code that never had a review
opinion is named under predicate 7, and a diff review is left to the owner at
acceptance.

All five seats asked for revisions. Every agreed group was reproduced against
the bytes it cites and applied:

| Group | Supporters | Concern | Disposition |
|---|---|---|---|
| G1, high | claude, codex, gemini, glm | The draft's plan repairs rewrote approved criteria (the rule-set family, the walk, the miner's count) or left them contradicting each other, and verdicts read MET against the rewritten text | **applied (F1)**: approved wording restored, each deviation an italic `(c)` note with its ruling; IL1, IL4 and IL6 now MET WITH DEVIATION; IL3 states the family was not delivered |
| G2, medium | claude, codex | IL4-Q1 marked fixed with the own-reference residual uncarried | **applied (F2)**: partly fixed; carried |
| G3, medium | claude, codex | IL1-Q3 marked discharged with its out-of-set half open | **applied (F3)**: partly discharged; carried |
| G4, low | claude, glm | The gate claim did not cover the final bytes, and dropped 008's qualifier | **applied (F4)**: the qualifier is kept; the gate re-ran on the final bytes |

| Divergent view | Disposition |
|---|---|
| claude: Part D's input dropped the milestone diff | **accepted as a residual**, stated above; the owner decides on a diff review |
| claude: predicate 7 overstated review coverage | **applied**: MET WITH RESIDUAL, naming the code |
| claude: predicate 1 omitted the IL1-F1 drop | **applied**: in predicate 1 and as plan notes at IL1-C2 and §5 |
| claude: the status line was untagged and blurred the approved bytes | **applied**: tagged, with the approved digest |
| claude: IL5's unreported version | **applied**: MET WITH RESIDUAL |
| claude: IL-R9's note listed only some learners | **applied**: all four named |
| kimi: FastLAS attributed to IL2-D1 without record support | **applied**: cites the IL2 spec's §13 ruling |

## Predicate-7 review (after part E)

At the owner's request, before acceptance, one reviewer read the five commits
that landed after their phase's review: `16cbbe1`, `c03ff94`, `b906749`,
`58704ed` and `b8caf6c` (predicate 7 named the last four; `16cbbe1` also
landed after IL1's review). The report, its reproduction and the triage are in
[`notes/phase-IL-close-p7-review.md`](notes/phase-IL-close-p7-review.md).
One reviewer is one reviewer.

| Finding | Class | Disposition |
|---|---|---|
| The Popper export wrote integers clingo would wrap | hardening | **fixed, R7**: one range check, `gnd.export.ilp.clingo_integer`, for both ASP-grounded adapters (IL2-D14) |
| The Popper reader accepted threshold values the export never rendered | hardening | **fixed, R8**: `off-threshold`, as for ILASP; discharges IL1-Q3 |
| The ILASP extractor stopped at the first blank line, against IL2-F8 and the docs | completeness | **fixed, R9**; ILC-F9 |
| A home-directory token in this record failed IL-R10's privacy test | outside scope | **fixed** |
| Two clingo readings, not reproduced without clingo | — | **carried**, IL-close-Q2 |

The regressions were red against `3c01567` (`evidence/IL-close/p7-red.txt`).
The RF6 census successor was regenerated over the fixed code, and the close
gate passed on these bytes: 1290 passed, 24 deselected
(`evidence/IL-close/p7-gate.txt`). **The close
panel (part D) did not see these changes** or this section.

## Boundary -- what the milestone does NOT establish

- **Which learner is better.** Each row is one run on one small example.
- **Reproducibility.** No run was repeated to measure it.
- **Any learner in CI.** Tests replay committed outputs; nothing installs or
  runs a learner.
- **That an own-reference subtype's joins are counted.** They are refused,
  never admitted (`008`, ILC-F8).
- **Acceptance.** The owner's acceptance is a separate record.
