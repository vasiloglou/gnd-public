---
milestone: induction-skill
station: IS2-recording-gate-2
scope: IS2-recording-gate
date: 2026-11-26
source_base: c083e1b6adebf583bd8c5cef33bcab9cf511b8f3
evidence:
  - path: tools/record_induce_sessions.py
    sha256: 6d75298fee37bb32cc864b49d50c2556e2e3cee513826d712624a1eecb0a9578
  - path: src/gnd/skills/gnd-induce/SKILL.md
    sha256: 8517e32d0c10c35f22652e01e2b798bbeca00bd773b47a23980279f734eec5f0
  - path: .gnd-planning/milestones/induction-skill/notes/phase-IS2-spec.md
    sha256: 84c1219405004feee2b18afc825c229cf30cd3f8a7b685eb4f0a15fa0a27a9e9
  - path: .gnd-planning/milestones/induction-skill/evidence/IS2/owner-statements-c1.txt
    sha256: 51aaad66cbadc660956a79e253ff88ae53be1349905baf92b1787b760b54e9b7
---

# induction-skill IS2 recording gate, re-recording

The second set of paid IS2 recordings, after checkpoint C1 (spec section 14).
It names the re-runs that [record 003](003-IS2-recording-gate.md) left to an
amendment; record 003 is unchanged and its first attempt stays evidence in
`evidence/IS2/attempt-1/`.

| Item | Declared |
|---|---|
| authority | the owner's D11 ruling ([owner-statements.txt](evidence/IS2/owner-statements.txt)) and the owner's C1 answer, quoted whole in [owner-statements-c1.txt](evidence/IS2/owner-statements-c1.txt): "Fix and re-record" |
| model | as record 003: Claude Code `--model haiku`, Claude Code's own login, no `ANTHROPIC_*` or `OPENROUTER_*` variables, no repository `.env` |
| conversations | the nine of `CONVERSATIONS` at `c083e1b6`, with their declared turns unchanged from record 003, over the amended skill at the SHA-256 above |
| run bound | one re-run per conversation, nine runs; at most four turns each, 900 seconds a turn; a conversation whose run folder exists is refused |
| cost ceiling | the D11 ceiling, USD 10 in total, unchanged. It counts the USD 1.53 already spent (attempt 1, USD 1.446; F2, USD 0.084), which the recorder now sums (spec finding F7) |
| keeping | as record 003: the leak gate first, otherwise only `results.json` stays |
| home | `src/gnd/examples/refunds/skill-sessions/<id>/claude-haiku/run-1/` |
| re-runs | none beyond these nine; a further run needs another record that names it |

This record authorizes the runs it lists and nothing else: no other model,
no learner but the example's stand-in, no merge or publication.
