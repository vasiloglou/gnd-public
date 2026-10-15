---
milestone: pyrel-agent-loop
station: phase-PL16
skill: "n/a -- repository development, not a gnd-solve station"
scope: phase-PL16
date: 2026-10-15
source_base: 294e53d
gate:
  command: "uv run pytest -q -p no:cacheprovider -m \"pyrel_oracle or not pyrel_oracle\" tests/test_plan_apps.py tests/test_plan_app_recordings.py"
  exit: 0
  output: "77 passed in 126.45s (0:02:06)"
rules_gate:
  command: "uv run pytest -q -p no:cacheprovider -m \"pyrel_oracle or not pyrel_oracle\" tests/test_pyrel_rules_plans.py tests/test_pyrel_rules_calendar.py tests/test_pyrel_rules_derivations.py tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py"
  exit: 0
  output: "309 passed in 402.65s (0:06:42)"
offline_gate:
  command: "the affected-consumer list of 013-phase-PL13a.md (14 files)"
  exit: 1
  output: "first run 10 failed, 910 passed: 5 new RF6 query-policy failures from plan_apps/core.py reading document fact_types, fixed by reading through ModelIndex.iter_constraints; rerun of the 5 policy files: 5 failed, 340 passed, the same 5 inherited failures listed in 013-phase-PL13a.md"
tutorials:
  - {command: "GND_TUTORIAL_PYREL_PYTHON=... uv run python tools/run_tutorials.py --group runtime-pyrel --lane pyrel", exit: 0, output: "16 tutorial blocks passed"}
  - {command: "uv run python tools/run_tutorials.py --group runtime-pyrel", exit: 0, output: "6 tutorial blocks passed"}
  - {command: "uv run --group docs zensical build --strict", exit: 0, output: "No issues found"}
evidence:
  - {path: "src/gnd/examples/plan_apps/core.py", sha256: "68c6551ba50de532931ba740e29beab80830f45c7b0eb543f0bf9afb1e1e527b"}
  - {path: "src/gnd/export/pyrel_rules.py", sha256: "65a90f8860adc85ab8f73cff5f4a29b863f303721ee83c2503d1a0b3930c61c9"}
  - {path: "tests/test_plan_apps.py", sha256: "8a6cebc1bfd76b9ff649402e4e87384af39605d008e538cf143591cc9896ce25"}
  - {path: "docs/runtimes/pyrel.md", sha256: "75deb5c76fb809c3ce25d3c30b0130b1478d142f26d738535c9b5d656e5f7a17"}
  - {path: ".gnd-planning/milestones/pyrel-agent-loop/notes/phase-PL16-spec.md", sha256: "c5fbdb219b7920bf41a376eed65b0dbcb49b7b50a705becbca4abc94f44ae521"}
  - {path: ".gnd-planning/milestones/pyrel-agent-loop/notes/phase-PL16-claude-review.md", sha256: "54e286287eb271171790842bd38214225ac905ff3a70438f1daf1446f5a6f47a"}
checkpoints:
  - "C6, shown to the owner on 2026-10-14: https://claude.ai/artifact/SzuCRURd1hkRrQfnDg983L (the course app on both checkers). Owner: \"I would show the rules expressed in pyrel\""
  - "C7, 2026-10-15: https://claude.ai/artifact/XJJ5searFHytKmeESwtegh (the course rules in English and PyRel; the PL17 runs)"
---
# Phase PL16: five example apps whose bots answer with checked plans

Spec: [notes/phase-PL16-spec.md](notes/phase-PL16-spec.md), delegated approval
(auto=true) under owner rulings "implement all five examples" and "real
operation plans". Amendments A1–A9 are in its §12.

## What landed

- **`src/gnd/examples/plan_apps/`.** Five apps: course, access, lease, clinic
  and trip. Each has its rules as written (`rules.md`), its model, a state,
  the documented attempts, a stand-in bot, a launcher and a README.
- **`core.py`, shared by all five.** It provides:
  - the ask, check, feed back and execute loop;
  - the GND and PyRel backends with one failure shape;
  - grouped feedback, which names the rule, the states and the facts, and shows
    each failed rule's PyRel line once;
  - `rules`, which prints every rule, derived fact, precondition and dynamic
    rule as PyRel;
  - atomic publishing.
- **The bot interface.** JSON on stdin, then on stdout one of: a plan, a plan
  with a note, or a decline with a reason. Any other answer is a failed
  attempt, with the reason fed back.
- **`--emit-post` on the generated program.** It writes the last state with
  its computed derived facts. An unwritable path exits 74 after the verdict.
- **Docs.** `docs/runtimes/pyrel.md` describes `--emit-post`.

## Measured

- **Documented attempts.** GND gives every documented attempt its documented
  exit (course 1,1,0; access 1,1,0; lease 1,0; clinic 1,1,0; trip 1,1,0).
- **Agreement.** The PyRel backend agrees with GND on exit and on the failing
  (check, status) pairs for every attempt.
- **Posts.** `ask` on PyRel publishes the same post-state as on GND, and GND
  accepts it.
- **Real models.** PL17's 260 recorded attempts were checked by PyRel, and GND
  re-checks every recorded plan with the same exit.

## Mutation run

10 mutants (M101, M102, M104–M107, M109–M112), over grouping, rule lookup, publish, the attempt bound,
junk answers and `--emit-post`. All were killed after two tests were added
(M110 and M112 survived at first; records in the session scratchpad, `pl16/mutants7.out` and `pl16/mutants7-rerun.out`). The files were restored, checked against
`pl16/before-mutants.sha`.

## Review

One reviewer is one reviewer: a single Claude subagent, same model family. Its
report is retained verbatim in
`notes/phase-PL16-claude-review.md`. Verdict: REVISE. The findings were
reproduced with the reviewer's scripts. 17 regression tests failed on the
pre-fix code (`pl16/prefix-review-tests.out`, with the pre-fix SHA-256 values)
and pass now.

| # | Finding | Triage | Disposition |
|---|---|---|---|
| F1 | GND exit 3 reached the bot with no reason | blocking | fixed (A4); 3 tests |
| F2 | two-space values broke the PyRel output parser | blocking | fixed with `parse_pyrel_output` (A4); 3 tests |
| F3 | a plan that empties a fact type ends in exit 2 and is never accepted | hardening | boundary (A6): only exit 0 publishes, per GND's guidance |
| F4 | `--emit-post` OSError exited 1 | hardening | exit 74 (A5); 3 tests |
| F5 | `--out` problems surfaced after the loop; temp file left on a link race | hardening | checked first; try/finally (A5); 2 tests |
| F6 | CLI crashed on missing or bad input | hardening | usage errors (A5); 3 tests |
| F7 | clinic refills never update `last_refill` | hardening | deferred: PL16-Q1 |
| F8 | trip budget vacuous without activities | hardening | deferred: PL16-Q1 |
| F9 | course `no_retake` blocks grading an enrolled course | hardening | deferred: PL16-Q1 |
| F10 | the `rules` view shows the LQP program, not the DuckDB one | hardening | stated in the view and the docstring; 1 test |
| F11 | timeout crash, temp path in feedback, no plan bound, no cache | hardening | fixed, except the cache, which was withdrawn (A7, 0.03 s); 2 tests |
| C1 | rules.md and state disagree on Frank's approver | completeness | fixed (A9); 1 test |
| C2 | Lease "value ranges" | completeness | spec amended (A8) |
| C3, C4 | unknown entities pass; `admit` is not observable | completeness | boundary: the rules as written do not forbid them |
| C5 | stand-in bots carry hard-coded repairs | completeness | boundary: they are labelled scripted; PL17 puts real models in their place |
| C6 | test gaps | completeness | closed by the tests above; the agreement test still compares (check, status) sets |
| C7 | RF7 routing failure | n/a | inherited, not caused by PL16 |

## Refuted premises

- **Spec §6.1, "cached per model digest".** A render takes 0.03 s, so a cache
  buys nothing (A7).
- **Spec §6.3, Lease "value ranges".** The model needs none (A8).

## Refactoring review

Executed:
- `parse_answer` is the one reader of a bot's answer, used by `ask`, by
  `check`/`execute` for plan files, and by the recordings test.
- `parse_pyrel_output` is the one reader of the PyRel program's report.
- `_constraint_ids` reads through `ModelIndex.iter_constraints` (RF6
  policy), not the raw document.

Deferred:
- The PyRel backend parses the human-readable report. A machine-readable
  verdict file from the generated program would remove the parser (PL16-Q2).

## Boundary

- Only exit 0 is accepted and executed (A6).
- The `rules` view shows the LQP program's requirements; the DuckDB program
  checks the same rules as violation queries.
- For preconditions, GND's feedback carries a sentence and PyRel's the step's
  bindings. Both name the facts.
- The models' fidelity to their rules text is limited where F7–F9 say.

## Open questions

| # | Question | Target |
|---|---|---|
| PL16-Q1 | Model fidelity: clinic `last_refill` (F7), trip budget totals (F8), course `no_retake` while enrolled (F9) | after PL19; the PL17 recordings are bound to the current models |
| PL16-Q2 | A machine-readable verdict file from the generated program | after PL19 |
| PL13b-Q2, PL14-Q1, PL15-Q1, the verbalizer Path crash, `computed_post` without derived facts | GND checker issues found on the way | checker, outside this milestone |
