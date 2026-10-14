---
milestone: pyrel-agent-loop
station: phase-PL13a
skill: "n/a -- repository development, not a gnd-solve station"
scope: phase-PL13a
date: 2026-10-14
source_base: ab766a6
gate:
  command: "uv run pytest -q -p no:cacheprovider -m \"pyrel_oracle or not pyrel_oracle\" tests/test_pyrel_rules_families.py tests/test_pyrel_rules.py"
  exit: 0
  output: "128 passed in 99.12s (0:01:39)"
offline_gate:
  command: "uv run pytest -q -p no:cacheprovider tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf8_structure.py tests/test_rf7_structure.py tests/test_rf1_layering.py tests/test_gnd_arch.py tests/test_rf6_query_policy.py tests/test_rf9_repairs.py tests/test_rf6_packages.py tests/test_rf3_core.py tests/test_public_pyrel_export_runtime_support.py tests/test_documentation_tutorials.py"
  exit: 1
  output: "5 failed, 936 passed, 107 deselected; the 5 are the inherited failures listed in 011-phase-PL12.md (rf1 pin harness mutation rows, rf7 routing, rf6 dynamic inventory x2, rf6 checker.check body)"
tutorials:
  - {command: "GND_TUTORIAL_PYREL_PYTHON=... uv run python tools/run_tutorials.py --group runtime-pyrel --lane pyrel", exit: 0, output: "16 tutorial blocks passed"}
  - {command: "uv run python tools/run_tutorials.py --group runtime-pyrel", exit: 0, output: "6 tutorial blocks passed"}
  - {command: "uv run --group docs zensical build --strict", exit: 0, output: "No issues found"}
evidence:
  - {path: "src/gnd/export/pyrel_rules.py", sha256: "9ac8f9e4309af36d158909a1ddcf64fb93fbae5b5456614f7dab6026618d7eaa"}
  - {path: "tests/test_pyrel_rules_families.py", sha256: "a5ce7703f7c8bbe8602ec67f1068f3e2048f207ac673d897706fc3656e6012e6"}
  - {path: "tests/test_pyrel_rules.py", sha256: "19725ef1d211146f786f922793477e7a511b9e8e15322332daab26c5e70847db"}
  - {path: "tests/fixtures/pyrel-rules-families/expected.json", sha256: "4f1e6b29fbc961496e7aafb3d7902a89f945d498a961ac80d1a82d33f2134a42"}
  - {path: ".gnd-planning/milestones/pyrel-agent-loop/notes/phase-PL13a-spec.md", sha256: "85c385bbffd4f652c6c9db111debd2001245c9fde830241d5317ff1331ba8993"}
  - {path: ".gnd-planning/milestones/pyrel-agent-loop/notes/phase-PL13a-claude-review.md", sha256: "a32a1459835d205db4cdb6daa41f065de71d299533a6c4abf07f971dda4980e0"}
  - {path: "docs/runtimes/pyrel.md", sha256: "270d20abdf45ec9e609cbbe52289ecaf25180e7864f042420c75b4e0b43aadbe"}
---
# Phase PL13a: the remaining constraint families as PyRel requirements

Spec: [notes/phase-PL13a-spec.md](notes/phase-PL13a-spec.md), delegated approval
(auto=true) under [012-owner-decisions-a1.md](012-owner-decisions-a1.md), with
post-review amendments A1–A5 in its §12.

## What landed

- `src/gnd/export/pyrel_rules.py` lowers these families to PyRel requirements,
  in both the LQP and the DuckDB program, from one `Requirement` list:
  - mandatory-disjunctive (inclusive-or);
  - value ranges, alongside PL12's value lists;
  - equality and exclusion;
  - exclusive-or over single roles;
  - internal frequency;
  - every ring variant, including acyclic through a recursive closure;
  - object and role cardinality.
- Helper relations: `<fact>_reverse` (works around a measured PyRel self-join
  bug), `<fact>_closure`, `<id>_plays`, `<id>_allowed`.
- Textual rules are listed as not checked, with GND's exit 4 for an alethic one.
- The DuckDB report merges a constraint's requirements into one verdict in
  GND's witness shape and order, with GND's exit precedence: 1, then 4, then 2,
  then 0.
- Refused by name: external uniqueness and frequency, multi-role exclusive-or,
  and a fact type named like a generated helper relation.
- Corpus `tests/fixtures/pyrel-rules-families/`: 9 models, 61 populations, and
  GND's verdicts in `expected.json` (the 6 multi-role exclusive-or populations
  pin the refusal's reason); `review/` holds the review's reproductions,
  compared live with `gnd.api.check`.
- Docs: `docs/runtimes/pyrel.md` lists the covered families, the refusals and
  the exit codes.

## Measured

- The DuckDB program agrees with `gnd.api.check` on status, witness, witness
  order and exit for the 55 corpus populations of the 8 supported models and the
  8 review populations.
  The one normalisation left is value witnesses, compared as sets (GND lists one
  value per offending fact).
- The LQP program compiles the pinned number of `Require` nodes per model:
  cardinality 5, equality 4, exclusion 2, exclusive-or 2, frequency 7,
  mandatory-disjunctive 1, ring 17, value 3.
- Acyclic over a 500-edge chain with one back edge: 7.84 s against the 60 s bound.

## Mutation run

20 seeded mutants, M21–M40, over the new lowering and report. All 20 were
killed. Each mutant was run against both rules test files; the record of each
run is in the session scratchpad (`pl13a/mutants3.out`). The run came before
the review repairs; each repair carries its own failing-first test instead
(below).

## Review

One reviewer is one reviewer: a single Claude subagent, same model family, read
only on `src/` and `tests/`. Report retained verbatim in
`notes/phase-PL13a-claude-review.md`. Verdict: REVISE. Every finding was
reproduced with the reviewer's scripts before repair. Pre-fix run of the new
regression tests: "16 failed, 16 passed, 43 deselected".

| # | Finding | Triage | Disposition |
|---|---|---|---|
| F1 | grouped witnesses sorted as strings; GND sorts numbers numerically | blocking | fixed: the program uses GND's scalar order. Tests: `review/ring-integer`, `frequency-integer`, `inclusive-or-integer` |
| F2 | a value rule with only a roster was called vacuous | blocking | fixed: vacuous only with no facts and no roster members. Tests: `review/value-roster` (exit 1), `value-roster-pass` (exit 0) |
| F3 | helper names could collide with fact types | blocking | fixed by refusal by name. Test: `review/helper-collision` |
| F4 | acyclic normalisation rested on a false claim | blocking | fixed: the program reproduces GND's cycle exactly; the membership comparison is gone, and the corpus test compares cycles exactly |
| F5 | LQP cardinality minimum over an empty universe never fires; DuckDB cardinality recounts in Python rather than reading its denial rows | completeness | deferred, open question PL13a-Q1 |
| F6 | textual message, missing refusal tests, spec drift | hardening | textual implemented as listed-not-checked (the reviewer's textual fixture failed schema validation, which is where its "None:" message came from); refusal tests added for external uniqueness and frequency; stale refusal test now uses subtype-partition and value-comparison; spec amended (A1, A3); time bound tightened to the spec's 60 s |
| F7 | tautological LQP count check; corpus gaps | hardening | counts pinned by hand; numeric, roster-only and collision cases added |

## Refuted premises

- **PL12, B2 disposition.** PL12 recorded that GND treats a list missing from
  `covers` as empty for every family, and the PL12 program kept only covered
  lists. Measured in PL13a: GND reads every fact list; only mandatory and
  inclusive-or are vacuous when a needed fact type is uncovered. Fixed here.
- **Corpus README observations 3 and 5** (first draft): the acyclic cycle is
  not set-dependent, and witness order is not string order for numbers. Both
  corrected in the README.

## Refactoring review

Executed:
- `_rosters` is the one home for "which instances keys populate a type". The
  universe relation and value vacuity both use it.
- The two agreement tests share one comparison, `_assert_agrees`, replacing a
  module-level set that one test filled for the other.

Seen but deferred: the checker runtime (`pyrel_runtime.py`) and this module
still lower constraints separately (PL12-Q1, now targeted at PL13b).

## Boundary

- The LQP `--connection` path is still not run against an engine (PL12-Q2).
- Value witnesses are compared as sets, not lists.
- F5: on LQP, a cardinality minimum over an empty universe is not enforced, and
  the DuckDB report decides cardinality from its member listing in Python.
- Subtypes, derived fact types, recursion in user derivations, aggregates,
  calendar terms, reference populations and plans remain refused, not
  approximated.
- GND crashes (exit 70, "no admissible origin") on a Float value `2.0` against
  an exclusive maximum of `2`, found by the reviewer. Outside this phase.

## Open questions

| # | Question | Target |
|---|---|---|
| PL12-Q1 | One lowering for the checker runtime and the rules programs | PL13b |
| PL12-Q2 | Run the LQP version on a RelationalAI engine | owner (engine and credentials) |
| PL13a-Q1 | Cardinality as a requirement that both programs evaluate, including the empty-universe minimum on LQP | PL13b |
| PL13a-Q2 | GND's exit-70 crash on a Float at an exclusive bound | separate issue for the checker |
