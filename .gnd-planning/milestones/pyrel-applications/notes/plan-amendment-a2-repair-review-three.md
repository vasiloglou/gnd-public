# Amendment A2 repair review three — junior learning path

Date: 2026-10-13
Instrument: owner-selected independent local reviewer (repair round, read-only)
Subject: `notes/plan-amendment-a2.md` r2, SHA-256 `827fbedf138aac2dc531b6d7071e20dc8e8c1de296c2b1711590052474a797fe`

**Verdict: pass with findings** (no blocking).

| # | r1 finding | Resolution |
|---|---|---|
| 1 | Expense step 3 paired the limit with a nonexistent query | Resolved: r2 D4.3 says no query enforces the limit; matches expense-native-query.txt:62-81 |
| 2 | No mechanism for Ada/night | Resolved: `--proposal FILE` is implementable. `adult-for-minor.population.json` differs from seed only in the owned `recommendation`; gnd backend `publish()` (cli.py:17-35); pyrel backend `candidate_transform` hook (applications.py:147,202-204) already used in tests/test_bookrec_pyrel_application.py:78-91 |

New finding 1 (non-blocking, pin in PA5R spec): r2 does not fix how `--proposal` behaves in the
PyRel lane — (a) skip the native query, or (b) run it and replace the candidate via
`candidate_transform`, leaving `calculation` describing a different candidate. Also: proposal bytes
are not digest-bound; under `complete.orm.yaml` the shipped file lacks derived facts (exit 3).
Spec must name backend path, file (`adult-for-minor.population.json`), model (`model.orm.yaml`),
`calculation` handling, `--user` requirement and proposal binding.

No other new blocking problems; review-three items 3–8 are addressed in r2.
