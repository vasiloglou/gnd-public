---
milestone: pyrel-agent-loop
station: phase-PL12
skill: "n/a -- repository development, not a gnd-solve station"
scope: phase-PL12
date: 2026-10-14
source_base: ea035df
gate:
  command: "uv run pytest -q -p no:cacheprovider -m pyrel_oracle tests/test_pyrel_rules.py"
  exit: 0
  output: "30 passed, 17 deselected"
offline_gate:
  command: "uv run pytest -q -p no:cacheprovider tests/test_pyrel_rules.py tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf8_structure.py tests/test_rf7_structure.py tests/test_rf1_layering.py tests/test_gnd_arch.py tests/test_rf6_query_policy.py tests/test_rf9_repairs.py tests/test_rf6_packages.py tests/test_rf3_core.py tests/test_public_pyrel_export_runtime_support.py"
  exit: 1
  output: "5 failed, 857 passed; all 5 also fail on a clean worktree of ea035df (inherited from main)"
tutorials:
  - {command: "GND_TUTORIAL_PYREL_PYTHON=... uv run python tools/run_tutorials.py --group runtime-pyrel --lane pyrel", exit: 0, output: "16 tutorial blocks passed"}
  - {command: "uv run --group docs zensical build --strict", exit: 0, output: "No issues found"}
evidence:
  - {"path": ".gnd-planning/milestones/pyrel-agent-loop/notes/phase-PL12-spec.md"}
  - {"path": ".gnd-planning/milestones/pyrel-agent-loop/notes/phase-PL12-claude-review.md"}
---
# Phase PL12: the model's rules as two PyRel programs

Spec: [notes/phase-PL12-spec.md](notes/phase-PL12-spec.md). Owner direction,
2026-10-14: "write two versions, one that will require lqp and one that can run
without LQP".

## What landed

- `gnd export pyrel MODEL --rules lqp|duckdb --out FILE`, implemented in
  `src/gnd/export/pyrel_rules.py`. Both programs are rendered from one list of
  `Requirement` objects (domain, check, witness variables, modality).
  - **LQP version:** each rule is an executable
    `m.where(<domain>).require(<check>)`, with `require_mode="report"` and the
    direct LQP compiler. `--compile` shows PyRel's compiled `Require` nodes and
    checks their count. `--connection NAME` runs on a RelationalAI engine and is
    labelled ENGINE-UNVERIFIED.
  - **DuckDB version:** each rule appears as the same `require` in a comment and is
    evaluated in its denial form, `m.where(<domain>, <not check>)`. Output uses
    GND's witness shapes, vacuity and exit codes (1 violated, 2 vacuous, 0, 3
    unreadable input, 70 crash).
- Families: guarded (atom, absence, comparison), mandatory, subset including
  multi-role sequences, value lists, and non-spanning internal uniqueness.
- Refused by name: other families, subtypes, derived fact types, disconnected
  antecedents, operations, and inputs without `covers` or with repeated rows.
- `ModelIndex.constraint_roles` added so the module makes no direct model reads
  (RF6 query policy).
- Docs: "Read the rules as PyRel requirements" on `docs/runtimes/pyrel.md`, with
  runnable blocks in both lanes.

## Measured

- On local DuckDB, `require` is ignored under both `require_mode` values. The
  SQL backend lifts `Require` blocks only into the logic reasoner's payload.
- The direct LQP compiler lowers a requirement to `domain and not check => Error`.
- The DuckDB version agrees with `gnd.api.check` on status, witness and exit for:
  - 11 shipped populations;
  - 8 review-probe populations;
  - 2 cap-boundary populations;
  - one mixed-vacuity population;
  - one `!=` model.

## Review

One reviewer is one reviewer: a single Claude subagent, report retained verbatim
in `notes/phase-PL12-claude-review.md`. Verdict: revise, with six blocking
findings. Every finding was reproduced before repair. Two of them were wrong in
detail, and the repairs follow GND's measured behaviour instead:

| # | Finding | Disposition |
|---|---|---|
| B1 | a vacuous rule after a violation turned exit 1 into 2 | fixed; separate flags |
| B2 | invented `unknown` status | removed. Measured: GND treats a list missing from `covers` as empty, even when rows are present, for every family (not only mandatory, as the review suggested). The program keeps only covered lists |
| B3 | `!=` crashed the export | fixed; CLI catch-all added |
| B4 | universes ignored subtypes and entity rosters | rosters of entities identified by a reference value type added; subtypes refused by name |
| B5 | duplicates lost, spanning uniqueness silently dropped | the input is refused on repeated rows (exit 3); header and per-rule comment name spanning uniqueness |
| B6 | derived facts recomputed instead of compared | derived models refused by name (PL13) |
| H1 | disconnected antecedents cross-joined | refused by name |
| H2 | uniqueness witnesses split per key | one verdict per rule, as GND |
| H3 | `--compile` count wrong for multi-statement checks | per-rule expected count |
| H4 | labels | ENGINE-UNVERIFIED, direct compiler selected, precise warning filter, docs wording corrected, `--rules` refuses checker-only options |
| H5 | model not validated | `load_model_bytes` first; invalid model exits 3 |
| H6 | generated names could collide; crash exit equal to violation exit | reserved names with collision loop; crashes exit 70 |

Mutation run after repair, 19 mutants:
- 17 killed. M5 (guarded vacuity any/all) was killed only after the
  mixed-vacuity case was added.
- M10 is equivalent: violation pairs come in both orders.
- M1 (unsorted rows) survives because DuckDB already returns these rows in sorted
  order. The sorted-output check guards against an engine change.

## Refactoring review

Executed: model queries in the new module go through `ModelIndex` rather than
document reads. Seen but deferred: the checker runtime (`pyrel_runtime.py`) and
this module lower constraints separately. Making the runtime consume the
`Requirement` list is open question PL12-Q1, targeted at PL13.

## Boundary

- The LQP `--connection` path has not been run against an engine.
- Families beyond the five listed, subtypes, derived fact types, recursion,
  aggregates, calendar terms, reference populations and plans are refused, not
  approximated.
- The seven failures inherited from `main` are unchanged. The reference-closure
  failure seen in the main checkout comes from a stale local `.claude/worktrees/`
  folder; it does not occur in a clean worktree.

## Open questions

| # | Question | Target |
|---|---|---|
| PL12-Q1 | One lowering for the checker runtime and the rules programs | PL13 |
| PL12-Q2 | Run the LQP version on a RelationalAI engine | owner (needs an engine and credentials) |
