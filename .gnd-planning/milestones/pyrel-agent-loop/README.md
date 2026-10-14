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

PL5 pages are implemented and locally checked, including replay tamper controls
and the actual repaired Expense candidate. Independent PL5 review remains
pending: the prior Claude reviewer stopped at the session limit, and automatic
approval review rejected sending unpublished changes to the gpt-6-sol reviewer.
The explicit review authorization question is pending. No successful independent
review or milestone close is claimed.

PL6's [spec](notes/phase-PL6-spec.md) retains the final installed check and the
failure-classification boundary. Seven refactoring failures reproduce on clean
main a9a2f08 and on the candidate. Reference closure passes in a clean candidate;
the eighth failure in the prior broad run came from scanning an old nested
Claude worktree. That broad run's wrapper lost pytest's exit code.

Preparation checkpoint: [007](007-phase-PL5-preparation.md).

Fresh-wheel acceptance exited 0: [008](008-phase-PL6-preparation.md).
Next: retain a draft PR, then complete the independent phase and close reviews
once authorized. Literal
Claude-session completion remains an explicit owner decision.
