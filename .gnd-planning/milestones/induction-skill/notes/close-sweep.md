# induction-skill close: open-questions sweep

2026-11-26, under `process-milestone induction-skill auto=true`. Every record in
this milestone directory was re-read: the plan gate [001](../001-plan-gate.md),
IS1 [002](../002-phase-IS1.md), the recording gates
[003](../003-IS2-recording-gate.md) and [004](../004-IS2-recording-gate.md), and
IS2 [005](../005-phase-IS2.md), with the plan's §4 residual clauses and §10.
Each row is **closed** (citing what closed it), **carried** (naming the next
owner) or **retired** (with the reason).

The owner approved the proposed dispositions and the filing of two issues
([receipt](../evidence/close/owner-statements.txt)). The rows were then revised
after the close's four reader reports; those revisions are delegated
(auto=true) rulings, not the owner's reading.

## Inherited from the plan and the plan gate

| Id | Question | Disposition |
|---|---|---|
| IK6-Q1 | The induced-knowledge close (its record 012) left "a packaged skill for the induction loop" to its own milestone | **closed** by this milestone: `gnd-induce` ships (record 002), and every learn-rules step is a skill prompt (record 005) |
| 001: IS1 base commit and D8 pin | to be named at the IS1 gate | **closed**: record 002 names the base (`source_base: 1e6083f3…`); the D8 pin needed no edit, because the census already reads the IK milestone's own commits ([IS1 spec r4](phase-IS1-spec.md), §6.3 row; record 002, IS1-C6). The red control the plan expected from the census test does not exist (plan §11 A4) |
| 001: the PR #54 scaffold row | an ordinary `run` once #54 is in the IS1 base | **closed** by the [IS1 spec r4](phase-IS1-spec.md) verification ledger: #54 merged, and the scaffold test passed whole in a clean clone |
| 001: checkpoint C0 | shown before the skill text is final | **closed** by record 002 (IS1-C8, "Keep them apart") |
| 001: D11, the recordings | open until the IS2 gate | **closed** by records 003 and 004. The USD 10 ceiling was declared by the author in record 003 under the owner's D11 approval and shown to the owner at checkpoint C1 |
| Plan §4, IS2-C1: branches without a recorded turn | "Any declared branch left without a recorded turn (for example exit 6 in expected-state mode) is named as a residual." Record 005 names none. No conversation records the expected-state score (exit 6 on a checker defect), the `--target llm` refusal, the rule miner (`--target amie`, `gnd import mined-rules`) or the "fix the inputs first" refusals. The neutral export offered after the absent-learner stop is recorded (`absent-learner`, turn 2) but not shown on the page | **carried** to the owner: recording them is paid work that needs a new gate record (records 003 and 004 are used up), after #318's leak fixes |
| Plan §4, carried limitations | no real learner runs; a recording is not a benchmark | **retired** as stated limitations, not questions: the page and the recordings' README say both. Plan §11 A1 corrects only the Popper premise |

## From IS1 (record 002)

| Id | Question | Disposition |
|---|---|---|
| IS1-Q1 | The global invocation guard: floor 29 of 41, substring option match, backtick fences only | **carried** to [#319](https://github.com/vasiloglou/gnd-public/issues/319), fixed on branch `claude/issue-319-guards` (PR pending the owner's word) |
| IS1-Q2 | The induce-skill test residuals of IS1 round 2 that IS2 did not discharge | **carried** to [#318](https://github.com/vasiloglou/gnd-public/issues/318), item 4 and the close-review comment on it (F3's test half, F6 and F7 parts the issue body lacked). Its target was "at the latest IS2"; IS2 discharged two of them (spec 6.9), so the close moves the rest instead of deferring to a phase that has passed |
| IS1-Q3 | One regenerated `EXPECTED_RELATIVE_LINKS` literal | **carried** to [#319](https://github.com/vasiloglou/gnd-public/issues/319), fixed on the same branch |
| IS1-Q4 | SI1 merged with `test_packaged_skills.py` red | **retired**: the red edge was pinned by PR 314 and the file is green on main; the rule that prevents a repeat already exists (`project.md`, "Structure and inventory guards": a phase that changes a file outside `.gnd-planning/` runs the guard list and records its summary) |
| IS1-Q5 | `review-r1-mutations.py` labels any failure CAUGHT | **retired**: the caveat is stated beside the evidence, the outcomes were reproduced independently, and nothing uses the runner again |

## From IS2 (record 005)

| Id | Question | Disposition |
|---|---|---|
| IS2-Q1 | Round 2's eleven deferred findings in the recorder and the page tests | **carried** to [#318](https://github.com/vasiloglou/gnd-public/issues/318): F1 to F3 (leak safety) are fixed on branch `claude/issue-318-recorder` (PR pending); the per-command argv and exit log is next |
| IS2-Q2 | The installed docs check fails at the guarded-rules `gnd synth` block | **closed** at the close (commits `4e1ae32c`, `1c4bc454`): each origin runs the extra-free groups on the bare wheel and the groups whose pages name an extra with that extra. Measured in the close record, which also records what the bare pass then found (plan §11 A2) |
| IS2-Q3 | The keep rule drops a learner call prefixed by `timeout` | **carried** to [#318](https://github.com/vasiloglou/gnd-public/issues/318), item 2, widened in the close-review comment to commands joined with `&&`; the page now gives both causes |
| IS2-Q4 | Commit `1cbbc18d` held local paths | **carried** to the owner: the commit is an ancestor of both PR 317 and the close branch, and both are pushed, so it is on GitHub already. A squash merge keeps it out of main; removing it from GitHub (a history rewrite, or GitHub support for the PR refs) is the owner's decision, not a delegated one |

## Refuted premises and controls

| Record | Premise | Disposition |
|---|---|---|
| 002 | "The Popper branch is unproven on the refunds example" (plan §2) | **plan repair** §11 A1 |
| 002 | "Six fenced `gnd` lines"; "15 new edges" (spec) | **retired**: spec text, measured and fixed in IS1 |
| 002 | Round 1's first T8 and T17 tests | **retired**: replaced in IS1 |
| close | "The IK census test goes red on a tree with the skill added" (plan predicate 1, IS1-C6) | **plan repair** §11 A4 |
| close | IS-R7's single exception (replay transcripts) | **plan repair** §11 A3: a fence equal to a declared turn may name the learner's invocation |
| 005 | The spec's `done` table versus the first recorder | **retired**: spec text, restored in IS2 round 1 |
| 005 | "The skill's sentences hold on Haiku" | **retired** as a recorded finding, not a question: six of nine re-recorded conversations hold, one run each, and the page now says three did not follow the skill fully. Spec §15 adds two departures no check measures (the actor sentence read as proposal-scoped; `recheck` wrote files). Any skill rewording would need a new recording to test it, which the owner would gate (the branch row above) |
| 005 | "`said` equal to the declared turns" | **retired**: spec text, amended in IS2 spec §15 |
| 005 | The 12 MiB wheel budget | **retired**: the owner raised it to 13 MiB at checkpoint C2; two copies of the cap that IS2 missed were raised at the close (commit `bfc2495e`) |
| IS2 spec §13 F2 | "A gate record precedes every paid call" (plan IS2-C1, §6): a test started one paid Haiku call (USD 0.084) before any gate record existed | **retired**: the spend counts against the ceiling (`UNRECORDED_USD`), and the repaired T6 fails if any subprocess starts |

## Refactoring review

Record 002 executed none and deferred one: regenerating `EXPECTED_RELATIVE_LINKS`
as one literal (IS1-Q3), carried to #319 and done on its branch. Record 005
executed none and deferred one: replacing the recorder's shell reader with a
per-command log (IS2-Q1), carried to #318. Both have named targets.
