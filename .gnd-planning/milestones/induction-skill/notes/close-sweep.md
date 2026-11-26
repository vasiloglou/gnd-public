# induction-skill close: open-questions sweep

2026-11-26, under `process-milestone induction-skill auto=true`. Every record in
this milestone directory was re-read: the plan gate [001](../001-plan-gate.md),
IS1 [002](../002-phase-IS1.md), the recording gates
[003](../003-IS2-recording-gate.md) and [004](../004-IS2-recording-gate.md), and
IS2 [005](../005-phase-IS2.md), with the plan's §4 residual clauses and §10.
Each row is **closed** (citing what closed it), **carried** (naming the next
owner) or **retired** (with the reason). The owner chose these dispositions on
2026-11-26 ("yes do the first"), after they were proposed in the session.

## Inherited from the plan and the plan gate

| Id | Question | Disposition |
|---|---|---|
| IK6-Q1 | The induced-knowledge close (its record 012) left "a packaged skill for the induction loop" to its own milestone | **closed** by this milestone: `gnd-induce` ships (record 002), and every learn-rules step is a skill prompt (record 005) |
| 001: IS1 base commit and D8 pin | to be named at the IS1 gate | **closed**: record 002 names the base (`source_base: 1e6083f3…`); the D8 pin needed no edit, because the census already reads the IK milestone's own commits ([IS1 spec r4](phase-IS1-spec.md), §6.3 row; record 002, IS1-C6) |
| 001: the PR #54 scaffold row | an ordinary `run` once #54 is in the IS1 base | **closed** by the [IS1 spec r4](phase-IS1-spec.md) verification ledger: #54 merged, and the scaffold test passed whole in a clean clone |
| 001: checkpoint C0 | shown before the skill text is final | **closed** by record 002 (IS1-C8, "Keep them apart") |
| 001: D11, the recordings | open until the IS2 gate | **closed** by records 003 and 004 |
| Plan §4, IS2-C1: branches without a recorded turn | "Any declared branch left without a recorded turn (for example exit 6 in expected-state mode) is named as a residual." Record 005 names none. The nine conversations do not record: the expected-state score (exit 6 on a checker defect), the `--target llm` refusal, the rule miner (`--target amie`, `gnd import mined-rules`), the neutral export offered after the absent-learner stop, and the "fix the inputs first" refusals | **carried** as a named residual: no further paid recording is authorized (gate records 003 and 004 are used up). A later recording milestone owns them, after #318 |
| Plan §4, carried limitations | no real learner runs; a recording is not a benchmark | **carried** as stated limitations, unchanged; plan §11 A1 corrects only the Popper premise |

## From IS1 (record 002)

| Id | Question | Disposition |
|---|---|---|
| IS1-Q1 | The global invocation guard: floor 29 of 41, substring option match, backtick fences only | **carried** to [#319](https://github.com/vasiloglou/gnd-public/issues/319) |
| IS1-Q2 | The induce-skill test residuals of IS1 round 2 that IS2 did not discharge | **carried** to [#318](https://github.com/vasiloglou/gnd-public/issues/318). Its target was "at the latest IS2"; IS2 discharged two of them (spec 6.9), so the close moves the rest instead of deferring to a phase that has passed |
| IS1-Q3 | One regenerated `EXPECTED_RELATIVE_LINKS` literal | **carried** to [#319](https://github.com/vasiloglou/gnd-public/issues/319) |
| IS1-Q4 | SI1 merged with `test_packaged_skills.py` red | **retired**: closed by PR 314 (the seeded-routes-and-identifiers close); the structure-guard question belongs to that milestone |
| IS1-Q5 | `review-r1-mutations.py` labels any failure CAUGHT | **retired**: the caveat is stated beside the evidence, the outcomes were reproduced independently, and nothing uses the runner again |

## From IS2 (record 005)

| Id | Question | Disposition |
|---|---|---|
| IS2-Q1 | Round 2's eleven deferred findings in the recorder and the page tests | **carried** to [#318](https://github.com/vasiloglou/gnd-public/issues/318): F1 to F3 (leak safety) before any further paid recording, then a per-command argv and exit log in place of reading shell text |
| IS2-Q2 | The installed docs check fails at the guarded-rules `gnd synth` block | **closed** at the close by commit `4e1ae32c`: each wheel origin installs the extras the wheel declares; measured in the close record (plan §11 A2) |
| IS2-Q3 | The keep rule drops a learner call prefixed by `timeout` | **carried** to [#318](https://github.com/vasiloglou/gnd-public/issues/318), item 2; the page already says so beside the `learn` replay |
| IS2-Q4 | Commit `1cbbc18d` on the IS2 topic branch held local paths | **carried** as an accepted residual: a squash merge of PR 317 keeps it out of main, and the branch is deleted after the merge; GitHub keeps the commit reachable from the PR page. No history rewrite |

## Refuted premises

| Record | Premise | Disposition |
|---|---|---|
| 002 | "The Popper branch is unproven on the refunds example" (plan §2) | **plan repair** §11 A1 |
| 002 | "Six fenced `gnd` lines"; "15 new edges" (spec) | **retired**: spec text, measured and fixed in IS1 |
| 002 | Round 1's first T8 and T17 tests | **retired**: replaced in IS1 |
| 005 | The spec's `done` table versus the first recorder | **retired**: spec text, restored in IS2 round 1 |
| 005 | "The skill's sentences hold on Haiku" | **carried** as a finding of the milestone: six of nine re-recorded conversations hold, one run each; the plan claims no pass rate (§11) |
| 005 | "`said` equal to the declared turns" | **retired**: spec text, amended in IS2 spec §15 |
| 005 | The 12 MiB wheel budget | **retired**: the owner raised it to 13 MiB at checkpoint C2; the plan states no budget |

## Refactoring review

Record 002 executed none and argued none needed. Record 005 executed none and
deferred one: replacing the recorder's shell reader with a per-command log. It
has an open-questions row (IS2-Q1) with a named target, now
[#318](https://github.com/vasiloglou/gnd-public/issues/318).
