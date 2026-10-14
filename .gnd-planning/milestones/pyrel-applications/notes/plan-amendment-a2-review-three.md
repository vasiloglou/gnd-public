# Amendment A2 review three — junior learning path

Date: 2026-10-13
Instrument: owner-selected independent local reviewer (read-only)
Subject: `notes/plan-amendment-a2.md`, SHA-256 `555a0e76ed41364bb05c9db34897727c85a556640171de01e363b07b6589c3d1`

**Verdict: fail** (two blocking, each with a small repair; direction sound).

1. **Blocking.** D4 step 3 pairs `approval_limit_team_lead` with a PyRel query that does not exist.
   The Expense query only counts/sums/groups and appends the given chain unchecked
   (expense-native-query.txt:47-81). Repair: for Expense show the model rule next to the
   count/sum query and say plainly that no query enforces the limit; GND's check does.
   BookRec `age_appropriate` ↔ blocked relation + `not_` is valid.
2. **Blocking.** D4 step 5 has no mechanism for the agent to propose Ada/night: the native query
   filters it, and the BookRec CLI has no candidate-injection option (cli.py:38-48).
   Repair: name the mechanism — a shipped bad-proposer option or candidate file through the
   app's publish path, or present `--chain` explicitly as the agent's proposal — and show
   witness `{"$u":"ada","$b":"night"}`.
3. Non-blocking. Ada/night is already shown in chapters 2 and 5 (02-facts.md:79-84,
   05-repair.md:13-31); decide whether native chapters stand alone; overview links to chapter 1.
4. Non-blocking. D5 must provision both a gnd-importable venv and the PyRel env, with hello checks.
5. Non-blocking. D7 undefined: write the term list and length limit; allow exit codes only in
   the troubleshooting table with plain meanings; junior review fails on any stuck step;
   show receipt time honestly.
6. Non-blocking. Move "who does what" to step 1; keep step 8 as recap.
7. Non-blocking. Keep clause: six figures with source captions, exact witnesses, input-unchanged
   guarantee, filtering-vs-checking in step 5, advisory/strict and currency in step 7 or "go further".
8. Non-blocking. D3 should allow checked excerpts/summary lines; tests assert the full output.

Orchestrator reproduction 2026-10-13: findings 1, 2 and 3 checked against the cited lines.
