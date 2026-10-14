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

Branch: `codex/pyrel-agent-loop` from `origin/main` (`a9a2f08`). Pull request
and merge remain the owner's decision. The live-recording step in PL4 runs the
owner's `claude` and `codex` CLIs and stops for an explicit go-ahead.

Next: `process-phase PL1 pyrel-agent-loop`.
