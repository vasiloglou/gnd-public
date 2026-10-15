# PyRel agent loop

Opened 2026-10-14 after the owner reviewed the PyRel tutorial pages shipped by
`pyrel-applications` (PR #21) and rejected them. The owner's words:

> I reviewed the documentation files. They are not good. You focus mostly on
> the python code of how to call gnd. First of all your calls like that look
> ugly ... The whole documentation looks too messy ... not informative at all.
> This is raw python going over lists of files. We need more educational,
> pedagogical material. You need to emphasize more on how the rules are
> written. Also I was expecting rules and constraints written in pyrel as
> well. Then keep in mind that GND is to be used with an LLM or a coding
> assistant. You need to show how to use it with them. You need to show what
> the LLM outputs, how this is checked by the GND and what it feeds back. You
> need to show how to use the skills, you need to show reasoning.

The [milestone plan](notes/pyrel-agent-loop-plan.md) is draft r1, approved by
the owner by default ([001](001-plan-gate.md)). Phases PL0–PL6; the first
implementable spec is [PL1](notes/phase-PL1-spec.md). Owner rulings PL-D1–D6
are in plan section 10. Records go here, one per material event; specs,
reviews and readings go in `notes/`; evidence in `evidence/<phase>/`.

Branch: `codex/pyrel-agent-loop` from `origin/main` (`a9a2f08`). PL6 prepares
the pull request; merge remains the owner's explicit decision. The separate
live-recording gate is recorded in [005](005-recording-gate.md).

## Resume status, 2026-10-14

PL1–PL4 are recorded in [002](002-phase-PL1.md), [003](003-phase-PL2.md),
[004](004-phase-PL3.md) and [006](006-phase-PL4.md). PL4 recorded Codex only;
Claude Code evidence remains owner-blocked (PL4-Q1).

PL5's independent review and bounded repair reading are retained in
[009](009-phase-PL5-review-repairs.md). Both initial blockers were repaired;
the bounded reader reported zero blockers and two hardening items, subsequently
fixed with local controls. The old preparation records remain historical.

The review fixes are available in [draft PR22](https://github.com/vasiloglou/gnd-public/pull/22).
Fresh-wheel acceptance on the repaired bytes passed: [010](010-phase-PL5-current-validation.md).
The latest focused run passes 224 tests; both native chapter paths and all
137 corpus cases pass. Documentation is ready for owner review.
The missing Claude recording, four-reader milestone-close review and seven
inherited refactoring failures remain explicit open work. No merge is authorized.

## Status at the close, 2026-10-15

The owner rejected the PL5 pages a second time. [Amendment A1](notes/plan-amendment-a1.md),
with the owner's decisions in [012](012-owner-decisions-a1.md), replaced the
remaining phases:

| Phases | Records | What they did |
|---|---|---|
| PL12–PL15 | [011](011-phase-PL12.md), [013](013-phase-PL13a.md), [014](014-phase-PL13b.md), [015](015-phase-PL14.md), [016](016-phase-PL15.md) | rules as PyRel requirements: families, derived facts, dates, references, operation plans |
| PL16 | [017](017-phase-PL16.md) | five plan apps whose bots answer with checked plans |
| PL17 | [018](018-recording-gate-PL17.md) (gate), [020](020-phase-PL17.md) | real models behind the apps, every run kept |
| PL18 | [019](019-recording-gate-PL18-skills.md) (gate), [021](021-phase-PL18.md) | GSD-style tutorials, how-to and explanation pages, with recorded replays |
| PL19 | [022](022-owner-decisions-close.md) (owner rulings), [023](023-milestone-close.md) (close) | four close readers, local CI, open questions carried forward |

[024](024-close-correction.md) corrects 022 and 023 on who created the five
untracked BookRec rules files: the PL12 review subagent did, not an earlier session;
they were deleted.

The owner ruled on the close findings in [022](022-owner-decisions-close.md),
which also closes PL4-Q1. On 2026-10-15 the owner authorized pushing and
merging PR #22 once the local CI had run.
