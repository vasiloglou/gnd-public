# Amendment A2 review two — claim honesty and positioning

Date: 2026-10-13
Instrument: owner-selected independent local reviewer (read-only)
Subject: `notes/plan-amendment-a2.md`, SHA-256 `555a0e76ed41364bb05c9db34897727c85a556640171de01e363b07b6589c3d1`

**Verdict: pass with findings** (three blocking, all repairable in the amendment).

1. **Blocking.** Existing pages already claim Snowflake execution: docs/index.md:241–242,
   docs/tour.md:157–158, docs/agents/export-and-review.md:16, docs/agents/index.md:25–26.
   The repository contradicts them: docs/runtimes/pyrel.md:160–161 ("Named remote connection
   execution is also unavailable"); src/gnd/export/pyrel_runtime.py:1770–1775 returns 64.
   Repair: add a deliverable rewriting those sentences conditionally; add the pages to D7 scope.
2. **Blocking.** The "Snowflake hook-up point" does not exist: applications-v1 refuses non-local
   execution (pyrel_runtime.py:1752–1754, pin at 1676–1677); both native_query.py files use
   `local_config()`. Repair: say Snowflake is outside this tutorial and outside applications-v1;
   forbid a connection parameter on the D1 seam.
3. Non-blocking. With `--backend pyrel` the PyRel query itself builds the candidate; the scripted
   proposer `library.recommend` runs only on the gnd backend (cli.py:64–84). Repair: name the slot
   "the candidate producer"; one component produces, GND checks.
4. Non-blocking. Neither producer ever yields Ada/night (library.py:13–21); the chapter must say the
   reader injects it to simulate a faulty agent.
5. Non-blocking. `gnd exp run` runs a separate session contract (docs/agents/dev-session.md:39–41,
   90–123); the link must not suggest it drives these CLIs.
6. **Blocking.** No test or review enforces the honesty rules. Repair: D7 claim check (Snowflake
   sentences must carry "not tested"/"outside"; measured-runtime sentence and passing-check caption
   required verbatim; block "governed", "certified", "enterprise-ready", "production", "scal*"),
   and give the independent review the job "list every claim and its evidence".
7. Non-blocking. "governed ontology" only in conditional form, never describing GND output.

Not a finding: the measured-runtime rule is backed by the hard pin; D2, D3, D5 make no new claims.

Orchestrator reproduction: findings 1, 2 and 4 checked against the cited lines on 2026-10-13.
