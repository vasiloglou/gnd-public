---
milestone: pyrel-agent-loop
station: phase-PL13b
skill: "n/a -- repository development, not a gnd-solve station"
scope: phase-PL13b
date: 2026-10-14
source_base: 2bc86f5
gate:
  command: "uv run pytest -q -p no:cacheprovider -m \"pyrel_oracle or not pyrel_oracle\" tests/test_pyrel_rules_derivations.py tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py"
  exit: 0
  output: "208 passed in 168.98s (0:02:48)"
offline_gate:
  command: "uv run pytest -q -p no:cacheprovider tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf8_structure.py tests/test_rf7_structure.py tests/test_rf1_layering.py tests/test_gnd_arch.py tests/test_rf6_query_policy.py tests/test_rf9_repairs.py tests/test_rf6_packages.py tests/test_rf3_core.py tests/test_public_pyrel_export_runtime_support.py tests/test_documentation_tutorials.py"
  exit: 1
  output: "5 failed, 915 passed; the same 5 inherited failures listed in 013-phase-PL13a.md"
tutorials:
  - {command: "GND_TUTORIAL_PYREL_PYTHON=... uv run python tools/run_tutorials.py --group runtime-pyrel --lane pyrel", exit: 0, output: "16 tutorial blocks passed"}
  - {command: "uv run python tools/run_tutorials.py --group runtime-pyrel", exit: 0, output: "6 tutorial blocks passed"}
  - {command: "uv run --group docs zensical build --strict", exit: 0, output: "No issues found"}
evidence:
  - {path: "src/gnd/export/pyrel_rules.py", sha256: "70b3f80901da918c30d2773f4fdaaf00434ce3e749a38c87dd34148d3063e21c"}
  - {path: "tests/test_pyrel_rules_derivations.py", sha256: "182330092745595a88f86a114bf651073413e63b44a5ace64676b67556064b40"}
  - {path: "tests/test_pyrel_rules_families.py", sha256: "0d05615507a8a3b6aaa965db5c8d02a0d08fc85d218c9817493c4f73127f3cb3"}
  - {path: "tests/test_pyrel_rules.py", sha256: "61390a12035f1e1604f38c812c9e01782a4ba00b6b443b0cfc02c6fa484970d7"}
  - {path: "tests/fixtures/pyrel-rules-derivations/expected.json", sha256: "615706d54ebd71323ae1b18f46e258b8891a15d76091ada07bdea256943cdba2"}
  - {path: ".gnd-planning/milestones/pyrel-agent-loop/notes/phase-PL13b-spec.md", sha256: "3ac8f69558b72df37ecc238b646d47f0cdf71a71d21e70493fa55e93af80766c"}
  - {path: ".gnd-planning/milestones/pyrel-agent-loop/notes/phase-PL13b-claude-review.md", sha256: "aa088b0e2032c5923f776da825fa77bcdcf8961de789428f6d3c41037c05b668"}
  - {path: "docs/runtimes/pyrel.md", sha256: "3c36e98ffc40be9218bca3d7fa1dc384036b95373c4bf644a5bc3c7e5fe6614a"}
checkpoints:
  - "C3, shown to the owner on 2026-10-14: https://claude.ai/artifact/AQJdYK3XHSJYMkKEX322eJ (registrar prerequisite chain and credit totals, real runs)"
---
# Phase PL13b: derived fact types as PyRel rules

Spec: [notes/phase-PL13b-spec.md](notes/phase-PL13b-spec.md), delegated approval
(auto=true) with post-review amendments A1–A6 in its §12. The owner asked to
see PyRel work at checkpoints; C3 (above) showed this phase on the registrar
example before the record.

## What landed

- **Derived fact types.** Each structured derived head is computed by PyRel
  `define` rules into `<head>_derived`, lower strata first. The lowering covers:
  - joins with constants;
  - negation;
  - `where` comparisons;
  - several clauses;
  - self and mutual recursion;
  - `count`, `sum`, `min` and `max`, with GND's deduplication;
  - Integer arithmetic heads.
- **The derivation check is two requirements:** every computed fact is claimed;
  every claimed fact is computed (`derived` only). The DuckDB report prints
  GND's verdict:
  - missing then extra fact, each the first by GND's identity tokens;
  - unchecked (exit 4) for a head not in `covers`;
  - exit 3 for claim rows outside `covers`.
- **Constraints read GND's view:**
  - the claim for a covered `derived` head;
  - nothing for an uncovered one;
  - the computed facts for a `semiderived` head, including in vacuity and
    acyclic witnesses.
- **Guarded rules** are vacuous when any antecedent fact type is empty, derived
  ones included.
- **PL13a-Q1 cardinality:**
  - the DuckDB report decides from the count requirements' rows;
  - the LQP minimum has no outer domain, so it also applies to an empty
    universe.
- **Readable variables (owner review of C1):**
  - role names for role sequences, and object type names for single-variable
    rules;
  - each variable gets a distinct Python name.
- **PyRel 1.30.1 join bug:** a binary atom with swapped variables is read
  through `<relation>_reverse`, in derivation bodies and in every requirement.
  This also repairs a PL13a crash on exclusions over swapped sequences.
- **Input checks:** cells are type-checked against their roles and opaque cells
  are refused by name, both with exit 3.
- **Corpus:** `tests/fixtures/pyrel-rules-derivations/`, with 4 models, 33
  populations and `expected.json` from GND. `review/` holds 9 models and
  populations, compared live.
- **Docs:** `docs/runtimes/pyrel.md` lists derived facts and the new refusals.

## Measured

- **Agreement:** the DuckDB program agrees with `gnd.api.check` on status,
  witness and exit for:
  - all 33 corpus populations;
  - 10 review reproductions;
  - the shipped `bookrec/complete` and release_governance `patched` and
    `repaired` populations.
- **LQP compile counts:** registrar-derived 6, registrar-semiderived 5,
  orders 16, mutual 4.
- **Time bound:** the 125,250-fact closure of a 500-edge chain is computed and
  compared in 8.03 s (bound 60 s).
- **Probes:**
  - `aggregates.sum(over..., of).per(group)` sums over distinct (over, of)
    tuples, which is GND's deduplication (7 and 9 on GND's own example);
  - a recursive define with negation over a completed lower relation agrees.

## Mutation run

16 mutants, M41–M58, over the derivation lowering, report, vacuity and
cardinality. All 16 were killed (session scratchpad `pl13b/mutants4.out`). The
run came before the review repairs. Each repair carries failing-first tests:
14 failed on the pre-review code and pass now (`pl13b/prefix-tests.out`).

## Review

One reviewer is one reviewer: a single Claude subagent, same model family. Its
report is retained verbatim in `notes/phase-PL13b-claude-review.md`. Verdict:
REVISE. Every finding was reproduced with the reviewer's scripts before repair.

| # | Finding | Triage | Disposition |
|---|---|---|---|
| F1 | acyclic witness over a semiderived head read the claim | blocking | fixed; `review/ring` (3 populations) |
| F2 | Float arithmetic binary in PyRel, exact in GND | blocking | refused by name (A1); `review/fl`, `review/num` |
| F3 | semiderived emptiness read before a recursive group was complete | blocking | fixed by ordering (A4); `review/scc` |
| F4 | swapped self-join crashed (PyRel bug) | blocking | fixed with a reversed copy (A2); `review/rec_swap` |
| F5 | two variables could share a Python name | hardening | fixed; `review/names3` |
| F6 | Float/Integer variable comparison crashed | hardening | refused by name; `review/misc` |
| F7 | Integer results beyond DECIMAL(38) crash with exit 70 | completeness | boundary; exit 70 is never read as a verdict |
| F8 | opaque cells and mistyped cells crashed | hardening | refused by name with exit 3 (A5). Mistyped cells now match GND's exit 3; opaque cells differ (GND evaluates them) |
| F9 | exclusion over swapped sequences crashed (since PL13a) | hardening | fixed by the same rewrite; `review/xswap` |
| F10 | test gaps | completeness | review cases, float-tier and computed-aggregate refusal tests added. LQP empty-universe behaviour stays engine-unverified (PL12-Q2) |

## Refuted premises

- **PL12 guarded vacuity.** PL12 excluded derived antecedents from a guarded
  rule's vacuity, because derived models were refused then. GND counts them;
  measured by `registrar-derived-uncovered`.
- **Spec §6.3.** The spec admitted `add`, `sub`, `mul`, `neg` and `abs`
  without regard to type. GND evaluates them as exact rationals, so over Floats
  PyRel cannot agree (review F2).

## Refactoring review

Executed:
- `_unswap` is one home for the PyRel join workaround. Ring rules, derivation
  bodies and every other requirement go through it.
- `_helpers` renders by kind and once, so reverse relations can precede the
  derivation clauses that use them.
- `_assert_agrees` is shared by the three agreement test files. Per-line
  families are compared as sets there, as PL12's test already did.

Seen but deferred: PL12-Q1, the checker runtime adopting this lowering, is now
targeted at PL15 (spec D1). The application profile differs from GND on the
constraint view, value identity and coverage.

## Boundary

- The LQP `--connection` path is still not run on an engine (PL12-Q2); that
  includes the domain-free cardinality minimum.
- **Refused by name:**
  - `avg`, `div`, `round`, `mod`, `sqrt`, `floor`, `ceil` and `haversine`;
  - arithmetic on Floats;
  - Float/Integer variable comparisons;
  - opaque derivation rules;
  - semiderived heads with aggregates;
  - opaque cells.
- **Input refused, GND accepts:** a population that repeats a fact is refused
  (PL12, B5). The shipped release_governance `cycle.pop.json` is one; pinned as
  an expected refusal.
- **Other limits:**
  - Integer results beyond DECIMAL(38) stop the program with exit 70.
  - Dates, operations and plans remain later phases.

## Open questions

| # | Question | Target |
|---|---|---|
| PL12-Q1 | One lowering for the checker runtime and the rules programs | PL15 |
| PL12-Q2 | Run the LQP version on a RelationalAI engine | owner (engine and credentials) |
| PL13a-Q2 | GND exits 70 on a Float at an exclusive bound | checker issue, outside this milestone |
| PL13b-Q1 | Accept repeated facts where no rule depends on multiplicity, as GND does | PL16 (if an example needs it) |
| PL13b-Q2 | GND exits 70 on a semiderived head with an aggregate ("derived origin lineage missing"), and on an unavailable semiderived head | checker issue, outside this milestone |
| PL13b-Q3 | Exact Float arithmetic and the float-tier functions | PL14 |
