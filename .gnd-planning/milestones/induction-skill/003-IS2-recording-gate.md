---
milestone: induction-skill
station: IS2-recording-gate
scope: IS2-recording-gate
date: 2026-11-25
source_base: b4f4a6011cb08dc7cd6486fd8ecd04eb65b7ecae
evidence:
  - path: tools/record_induce_sessions.py
    sha256: 70b347c6eb34ca788c491605c0245f86bc4ad5ef0dd0e8f9a6d4be87b57a5575
  - path: .gnd-planning/milestones/induction-skill/notes/phase-IS2-spec.md
    sha256: faf96c99278f02d756b6731aee283ea84b0102f286fc75ed5b94ae2c840a7155
  - path: .gnd-planning/milestones/induction-skill/evidence/IS2/owner-statements.txt
    sha256: 31bcf5d71d2850267a93fbf76fec59819b92a0eccd48cfc2b0c0e380be104faf
---

# induction-skill IS2 recording gate

The paid recordings of IS2 (spec section 6.3, plan D11). The recorder
`tools/record_induce_sessions.py` refuses to start unless `--authorized-by`
names this file.

| Item | Declared |
|---|---|
| authority | the owner's D11 ruling, quoted whole in [owner-statements.txt](evidence/IS2/owner-statements.txt): "approved D11" |
| model | Claude Code `--model haiku`, Claude Code's own login; the recorder drops `ANTHROPIC_*` and `OPENROUTER_*` from the environment and reads no repository `.env` |
| conversations | the nine of `CONVERSATIONS` in `tools/record_induce_sessions.py` at `b4f4a6011cb08dc7cd6486fd8ecd04eb65b7ecae`, with their declared turns: `score`, `learn`, `import`, `faulty`, `discover`, `recheck`, `absent-learner`, `existing-output`, `make-it-pass` |
| run bound | one run per conversation, nine runs; at most four turns each, 900 seconds a turn; a conversation whose run folder exists is refused |
| cost ceiling | USD 10 in total, by the turns' reported `total_cost_usd`. Already spent: USD 0.084 by the test bug of spec finding F2, before this record, counted here. The recorder stops before a conversation that would start at or above USD 10 and ends a conversation that crosses it |
| keeping | a run is kept only after the leak gate (local paths, keys, the git identity); otherwise only its `results.json` stays |
| home | `src/gnd/examples/refunds/skill-sessions/<id>/claude-haiku/run-1/` |
| re-runs | none under this record; a further run needs an amendment that names it |

This record authorizes the runs it lists and nothing else: no other model,
no learner but the example's stand-in, no merge or publication.
