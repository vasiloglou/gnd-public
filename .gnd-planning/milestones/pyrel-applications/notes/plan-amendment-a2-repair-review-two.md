# Amendment A2 repair review two — claim honesty

Date: 2026-10-13
Instrument: owner-selected independent local reviewer (repair round, read-only)
Subject: `notes/plan-amendment-a2.md` r2, SHA-256 `827fbedf138aac2dc531b6d7071e20dc8e8c1de296c2b1711590052474a797fe`

**Verdict: pass with findings.** Round-one blockers 1, 2 and 6 are resolved (D0 lines and cited
runtime refusals re-checked; no hook-up point; D7 claim check plus claim listing in the junior pass).

New findings:

- **N1 (blocking, small repair).** D0 misses `README.md:16-18` ("PyRel runs locally on DuckDB or on
  Snowflake, so it is the route when your business logic and data already live in enterprise
  systems") and `docs/index.md:259` ("Snowflake deployment … are optional"). Add both to D0 and
  README.md to D7 scope. `docs/runtimes/pyrel.md:163` and `docs/runtimes/scenario.md:53` are fine.
- N2 (non-blocking). D7 fails r2's own permitted context sentence; state that the boundary
  sentence must sit in the same paragraph as any Snowflake mention.
- N3 (non-blocking). Banned terms ("scal*", "witness") over-reach on whole D0 pages
  (docs/index.md:211,217,230; docs/agents/export-and-review.md:14). Apply only the Snowflake rule
  to D0 pages; full rules to the overview, native chapters and D5 section.

Orchestrator reproduction 2026-10-13: README.md:16-18 and docs/index.md:211,217,230 checked.
