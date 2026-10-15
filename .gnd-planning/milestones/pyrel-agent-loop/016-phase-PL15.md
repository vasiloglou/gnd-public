---
milestone: pyrel-agent-loop
station: phase-PL15
skill: "n/a -- repository development, not a gnd-solve station"
scope: phase-PL15
date: 2026-10-14
source_base: 6cde80f
gate:
  command: "uv run pytest -q -p no:cacheprovider -m \"pyrel_oracle or not pyrel_oracle\" tests/test_pyrel_rules_plans.py tests/test_pyrel_rules_calendar.py tests/test_pyrel_rules_derivations.py tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py"
  exit: 0
  output: "309 passed in 357.51s (0:05:57); after the last edit (policy-only), tests/test_pyrel_rules_plans.py: 48 passed in 127.16s"
offline_gate:
  command: "uv run pytest -q -p no:cacheprovider tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf8_structure.py tests/test_rf7_structure.py tests/test_rf1_layering.py tests/test_gnd_arch.py tests/test_rf6_query_policy.py tests/test_rf9_repairs.py tests/test_rf6_packages.py tests/test_rf3_core.py tests/test_public_pyrel_export_runtime_support.py tests/test_documentation_tutorials.py"
  exit: 1
  output: "5 failed, 915 passed; the same 5 inherited failures listed in 013-phase-PL13a.md"
tutorials:
  - {command: "GND_TUTORIAL_PYREL_PYTHON=... uv run python tools/run_tutorials.py --group runtime-pyrel --lane pyrel", exit: 0, output: "16 tutorial blocks passed"}
  - {command: "uv run python tools/run_tutorials.py --group runtime-pyrel", exit: 0, output: "6 tutorial blocks passed"}
  - {command: "uv run --group docs zensical build --strict", exit: 0, output: "No issues found"}
evidence:
  - {path: "src/gnd/export/pyrel_rules.py", sha256: "083d78759e8c1358637f36f23e0fc3a7364282aa4855cd2de826cce776d9c082"}
  - {path: "tests/test_pyrel_rules_plans.py", sha256: "97c72b7bba5ba41f2e5a300770e685e2527d08bae0db65de525dccb0d51bb894"}
  - {path: "tests/test_pyrel_rules.py", sha256: "c298b29cb04366199d3aba301dee73c554031b6e26bb8d7b3318e96131618424"}
  - {path: "tests/fixtures/pyrel-rules-plans/expected.json", sha256: "ce93e1d933ca16b54f9fefd72bee355bb8384c368b6f9390af3908b70e3ae595"}
  - {path: ".gnd-planning/milestones/pyrel-agent-loop/notes/phase-PL15-spec.md", sha256: "6287db16bf547abe6e98f885b68433c5c95d6c5f54b38f70f23f8b1686329b7a"}
  - {path: ".gnd-planning/milestones/pyrel-agent-loop/notes/phase-PL15-claude-review.md", sha256: "6caec6fefce179fed7ff7a5a9d893d3bc3c6345bca73a0b451fc22c9b53874ae"}
  - {path: "docs/runtimes/pyrel.md", sha256: "4e9e94cfb07a9e91290b6a638f8a761e2c2b89936dc20d995adf766c10318a64"}
checkpoints:
  - "C5, shown to the owner on 2026-10-14: https://claude.ai/artifact/EKhxyRnKx5SV6u5epxKqgf (the registrar bot's three plans, real runs)"
---
# Phase PL15: operation plans in the PyRel rules programs

Spec: [notes/phase-PL15-spec.md](notes/phase-PL15-spec.md), delegated approval
(auto=true) under owner ruling A1-D1 ("real operation plans"), with amendments
A1–A8 in its §12. Checkpoint C5 (above) showed the tutorial's three attempts
checked by GND and PyRel. Asked mid-phase why this was taking long, the owner
said to keep going.

## What landed

- **Plan mode.** For a model with operations, the generated program checks a
  plan: `python RULES.py --pre STATE.json --steps PLAN.steps.json`. A single
  population argument still checks a snapshot.
- **Data movement in the program's Python.** The program:
  - validates the steps document as GND's `steps.schema.json` and
    `gnd.transition` do (digests, operations, bindings, types);
  - applies GND's three coverage gates in GND's order;
  - builds every state by the transition equation, with GND's replacement
    slots; later states hold facts only.
- **Every verdict a PyRel query.** All states live in one PyRel model, with a
  `gnd_step` field on every relation.
  - Every snapshot requirement is lifted per state. Derived heads are computed
    per state: state 0 reads claims, later states read computed facts.
  - Step checks are denials over `previous(gnd_step, gnd_before)`:
    preconditions, retract targets, redundant asserts, create freshness
    (including two creates in one step) and dynamic rules (functional gate,
    pinned value roles, vacuity).
  - Compiled precondition obligations are checked on the pre-state.
  - The report uses GND's locators and the exit band 1 > 4 > 2 > 0.
- **PyRel 1.30.1 join bug, generalised.** Atoms that share variables in
  different orders are read through reordered copies, `<rel>_reverse` or
  `<rel>_as_<permutation>`.
- **Refused by name:**
  - `--post` (the frame comparison);
  - dynamic rules on derived subjects;
  - a role or parameter named `gnd_step` or `gnd_before`;
  - plans over 500 steps;
  - derived heads over reference facts in models with operations (a GND bug,
    spec D3).
- **Corpus:** `tests/fixtures/pyrel-rules-plans/` holds 3 registrar models,
  19 plans and `expected.json` from `gnd.api.transition`. `review/` holds 5
  review models.
- **Docs:** `docs/runtimes/pyrel.md` describes plan mode.

## Measured

- **Agreement:** the DuckDB program agrees with `gnd.api.transition` on exit,
  on per-step failing checks by locator and status, and on per-state verdicts
  and witnesses, for:
  - all 19 corpus plans, including the tutorial's three attempts;
  - the shipped approvals `plan-draft-1` and `plan-draft-2`;
  - 4 review plans.
- **Refusals:** the coverage gates and 14 malformed steps documents are refused
  with exit 3, like GND.
- **LQP compile count:** the registrar compiles 20 requirements (9 snapshot,
  10 step checks, 1 compiled obligation).
- **Speed:** about 0.35 s per step on a laptop. 3 steps take about 5 s and 100
  steps about 36 s.
- **Probe (harvest):** one model with a step dimension costs 1.07 s for 7
  states, against about 1 s per state with one process per state. PyRel 1.30.1
  allows one model per process.

## Mutation run

16 mutants, M81–M97, over the transition equation, step checks, state views,
banding, digests and binding checks.
- 12 were killed at first.
- M87 (functional gate), M89 (derivations judged in later states) and M90
  (state 0 reads computed facts) survived. Cases were added (`registrar-nonfunctional`,
  `attempt-1-semiderived`, `pre-claim-incomplete`), and all three are now
  killed.
- M97 (created values not added to the roster) exposed that adding them was
  wrong: GND's states hold facts only. The code it mutated was removed (spec A3).

Records are in the session scratchpad: `pl15/mutants6.out` and
`pl15/mutants6-rerun.out`.

## Review

One reviewer is one reviewer: a single Claude subagent, same model family. Its
report is retained verbatim in `notes/phase-PL15-claude-review.md`. Verdict:
REVISE. Every finding was reproduced with the reviewer's scripts. Of the
regression tests, 16 failed on the pre-review code and pass now
(`pl15/prefix-review-tests.out`).

| # | Finding | Triage | Disposition |
|---|---|---|---|
| F1, F2 | freshness read rosters; rosters carried into later states | blocking | fixed during the review (A3); confirmed by the reviewer |
| F3 | double create in one step | blocking | fixed; `review/lab3` |
| F4 | subject binding its own value role | blocking | fixed (A6); `review/dynbind` |
| F5 | coverage gates missing | blocking | fixed (A5); `review/h2`, `i1` |
| F6 | role or parameter named `step` | blocking | fixed (A7); `review/steps`, `steps2` |
| F7 | compiled obligations ignored | blocking | lifted (A4); `pre-enrolled-not-offered` |
| F8 | steps validation incomplete; exit 1 on malformed input | blocking | fixed (A5); 8 malformed shapes tested |
| H1 | dynamic witnesses when the data breaks uniqueness | hardening | boundary: the exit agrees (the state already violates uniqueness) |
| H2 | witness order | hardening | replacement slots reproduced (A8). Boundary: GND names a different cycle or duplicate order in some later states (verdict and exit agree) |
| H3 | bounds drift | hardening | spec amended (A1); the cap is refused by name |
| H4 | untracked generated programs | n/a | they predate this session and are not staged |
| C1 | `--post` not named; fixed argument order | completeness | fixed; tested |
| C2 | 200 steps over 60 s | completeness | bound amended to 100 steps, with the measured cost (A1) |
| C3 | no date rule per step in the corpus | completeness | deferred to PL16, where the clinic example needs it; the reviewer checked dates by hand, and they agreed |
| C4 | test gaps | completeness | closed by the tests above |

## Refuted premises

- **Spec §6.3, "compiled-subset operations refused".** The tutorial's own model
  compiles one, so it is lifted instead.
- **The harvest's "create adds an instance".** GND's states hold facts only
  (`transition._load_intermediate`).

## Refactoring review

Executed:
- `state_lines` is the one home for a state's verdicts, shared by the snapshot
  report and every state of a plan.
- `_unswap` is the one home for the PyRel join workaround, now covering
  permutations.
- `_at` and `_step_field` are the one way a relation takes its state argument.

Deferred:
- PL12-Q1, the checker runtime (`pyrel_runtime.py`, `applications.py`)
  adopting this lowering, moves to PL16: the example apps call the generated
  program.
- The two term renderers, `_expr` and `_operand`, remain separate.

## Boundary

- The LQP `--connection` path is still not run on an engine (PL12-Q2).
- **Plan mode only:** `--post` is refused, and plans over 500 steps are refused.
- **Witness choice:** in later states, some acyclic witnesses and uniqueness
  orders can differ from GND's (H2); verdict and exit agree.
- **Input format:** the program reads JSON populations only; GND also reads
  YAML (the approvals pre-state is converted in the test).
- **GND bugs refused or recorded:**
  - derived heads over reference facts in plan mode (D3);
  - the earlier PL13b-Q2 and PL14-Q1.

## Open questions

| # | Question | Target |
|---|---|---|
| PL12-Q1 | The checker runtime and the apps call the generated program | PL16 |
| PL12-Q2 | Run the LQP version on a RelationalAI engine | owner (engine and credentials) |
| PL15-Q1 | GND's plan walk computes reference-fed derived heads as empty in later states | checker issue, outside this milestone |
| PL15-Q2 | Precondition failures carry no witness in GND; choose one form for the bot's feedback | PL16/PL17 |
| PL15-Q3 | Witness order for acyclic and uniqueness in later states (H2) | after PL19, if it matters for a recording |
