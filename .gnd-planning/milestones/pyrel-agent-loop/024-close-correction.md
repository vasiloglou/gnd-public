---
milestone: pyrel-agent-loop
station: correction
skill: process-milestone
scope: milestone-close
date: 2026-10-15
---
# Correction to the close: who created the BookRec rules files

Record [022](022-owner-decisions-close.md) (ruling CD3) and the close record
[023](023-milestone-close.md) say the five untracked
`src/gnd/examples/bookrec/*.population.rules.py` files "predate the milestone".
That is false. The owner ruled "leave them" on that wrong claim.

**What happened.** The PL12 review subagent was launched read-only on
2026-10-14 at 19:07 UTC. At 19:10:52 UTC it ran its scratch harness on the
BookRec populations. The harness writes each generated program next to its
population (`Path(population).with_suffix('.rules.py')`), so it wrote all five
files into the repository. They were never committed, and nothing used them.

**Disposition.** At the owner's request (2026-10-15) the five files were deleted
from the working copy, and this record corrects 022 and 023. Records 022 and 023
are not edited. The other untracked items stay as traced:

| Item | Created by |
|---|---|
| `rules.py`, `rules_lqp.py`, `my_rules.py` | the owner's terminal |
| `.claude/launch.json` | an earlier Claude session |
| the PA6 zip | the `pyrel-applications` acceptance run; record 013 keeps it local |
| `.playwright-mcp/` and `.agents/skills/` | no Claude Code session on this machine |

**Lesson for review agents.** "Read-only on the repository" did not stop a
harness that derived its output path from its input path. Review briefs now need
to say that every output, including derived paths, must go to the scratch
folder.
