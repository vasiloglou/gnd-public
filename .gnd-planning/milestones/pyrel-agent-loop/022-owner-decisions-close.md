---
milestone: pyrel-agent-loop
station: owner-gate
skill: process-milestone
scope: milestone-close
date: 2026-10-15
---
# Owner decisions at the close

Close readers one and two raised two blocking findings that need an owner ruling,
and one hardening finding. The owner answered in the session on 2026-10-15.

| # | Question | Owner's ruling |
|---|---|---|
| CD1 | Predicate 1 ("readable commands") is not met on BookRec ch. 7 and Expense ch. 4: they name the PyRel interpreter variable and use bare `python -c` lines. Record 002 says it holds | Amend it and carry it forward. The new tutorials meet predicate 1; the two older chapters carry to PL18-Q1 (move them to Reference). Record 002's claim is corrected by this record |
| CD2 | Predicate 4 asks for a recorded Claude Code session on each chapter; the two older chapters show Codex only, as disclosed (PL4-Q1) | Accept the current evidence. Codex covers the two older chapters, and Claude Code is shown by the recorded sessions on the course tutorial (`gnd-model-from-text`, `gnd-model-evolve`) and the 50 Claude plan-app runs. PL4-Q1 is closed |
| CD3 | Untracked files: five `src/gnd/examples/bookrec/*.population.rules.py`, and `rules.py`, `my_rules.py`, `rules_lqp.py` at the root. They predate the milestone and are not in git | Leave them. They are noted in the close record; the PR and CI never see them |

**Correction to record 002.** Its statement that predicate 1 holds was false for
BookRec ch. 7 and Expense ch. 4 (close-reading-one, B1). Record 002 is not edited;
this record carries the correction.
