---
milestone: transition-check-performance
station: phase-TP0
skill: n/a -- repository development, not a gnd-solve station
scope: phase-TP0
date: 2026-10-16
gate:
  command: "uv run pytest -q tests/test_transition_cost_workload.py tests/test_rf1_layering.py tests/test_public_transition_contract.py"
  exit: 0
  output: "45 passed in 86.58s (Python 3.14.3); 45 passed in 122.70s (3.11.15); 45 passed in 127.63s (3.13.12)"
slow_cadence:
  command: uv run pytest -q
  trigger: explicit owner selection
  reason: TP0 changes no runtime code; the focused gate covers the new tool, tests and fixture
---

# Claim

TP0 is complete under the owner-approved spec r5
([plan gate](001-plan-gate.md), spec SHA-256 `2165ada0…1e3b` at approval; findings were
appended afterwards). Delivered:

- **Fixture:** the reporter's issue #24 workload, anonymized on import
  (`tests/fixtures/transition_cost/`).
- **Tool:** a counting and parity tool (`tools/measure_transition_cost.py`).
- **Tests:** seven approved tests (T1–T7) and five review successors
  (`tests/test_transition_cost_workload.py`).
- **Evidence:** the baseline, under `evidence/TP0/`.

Runtime bytes are unchanged: `git diff 2d1ff4d -- src/gnd` is empty.

## Gates

Focused gate (frontmatter command): exit 0 on Python 3.14.3, 3.11.15 and 3.13.12.

    45 passed in 86.58s
    45 passed in 122.70s
    45 passed in 127.63s

Lint, run over the tool, the tests and the transform script:

    uv run ruff check tools/measure_transition_cost.py tests/test_transition_cost_workload.py tests/fixtures/transition_cost/anonymize.py
    All checks passed!

Baseline: `uv run python tools/measure_transition_cost.py --out evidence/TP0 --repeat 5`, exit 0.
Import proof: `--compare-import SOURCE`, exit 0, `"equal": true` over 13 calls.

## Measurements (reporter replay, 13 calls)

| Counter | Baseline | Target (D-p1-2) |
|---|---|---|
| `checker_runs` | 25 | 19 when receipts are used (TP3) |
| `model_index_key_paths` | 540 | TP1 bound; the exact number is set in TP1's spec |
| `model_dumps_other` | 457 | must not increase (TP1) |
| `deepcopy_nodes` | 2,760,394 | ≤ 1,380,197 (TP2), same interpreter |

`course` control: 5 checker runs, exit 0 (`attempt-3`); `attempt-1` and `attempt-2` exit 1.

Timings are evidence only: 5.09 s median on 3.14.3 (an earlier run that day measured 5.79 s),
4.02 s on 3.13.12, 4.32 s on 3.11.15. The reporter measured 3.96 s.

## Independent review

One local reader reviewed the uncommitted diff
([notes](notes/phase-TP0-claude-review.md); tool SHA-256 `76c61f70…1b1e` at review time).
**One reviewer is one reviewer.** No blocking finding.

| Findings | Disposition |
|---|---|
| F1 (missing `course` admission and CLI surfaces) | Fixed. |
| F2 (no batch payload digest) | Fixed. |
| F3, F4, F7 (mutants that survived) | Each now has a killing test. |
| F5 (classmethod restored as a bound method) | Fixed. |
| F6 (first-run counts) | Warm-up added. |
| D1 rationale, T6 field name, F9 normalization wording | Recorded as spec findings 8–10. |

Each successor test was shown red against its mutant or its pre-fix code
(`evidence/TP0/review-mutants.txt`, produced by `review-mutants.py`; 5 of 5 killed). The
retained review is verbatim except one label, `MU10`, renamed so it cannot be read as a
downstream milestone ID.

## Refactoring review

**None needed.** TP0 added a tool, tests and a fixture, and changed no runtime home. It did
expose structure that TP1 must respect: the counted callables are bound by name in many
modules, for example `checker._core.check` and `values._model_digest` under several
aliases. So a per-call ModelIndex scope has to be entered at public entry points, not
patched at call sites. That is TP1's planned design (plan §2), so no refactor is deferred.

## Boundary and open questions

- **What TP0 is:** a measurement. It removes no work and claims no speedup.
- **Counters are interpreter-specific:** `deepcopy_nodes` reads 2,761,233 on 3.11, so
  node gates compare runs on the same interpreter.
- **The import proof is not reproducible from the repository alone.** The original bundle is
  not committed, so the comparison can only be re-run where that source is available. The
  committed fixture hashes are pinned by T1.
- **The CLI and batch surfaces have no branch-trace digests,** because they run in a
  subprocess.
- **Carried forward:** the TP1 exact key-path bound goes to the TP1 spec. Downstream
  acceptance (O13) goes to the reporter at milestone close.

## Evidence hashes

[
  {"path": "tools/measure_transition_cost.py", "sha256": "42e2aadacaae276175838d8400c08cf406fafb8fcc8cc1dfea4d41f1a055c63e"},
  {"path": "tests/test_transition_cost_workload.py", "sha256": "6596d2197f05a5ddbbcaaa32c5029251776c18d4727af62c0ea4c15d1da0a7e2"},
  {"path": "tests/fixtures/transition_cost/anonymize.py", "sha256": "c45ed11663c28f215af4215d60d85eee77d740eae21e879cd09a9375fc32dbc1"},
  {"path": "tests/fixtures/transition_cost/PROVENANCE.md", "sha256": "2e6244bf709d98f965c0f968d2f31d53c98eb74452850d66b560593a5a2f08d6"},
  {"path": ".gnd-planning/milestones/transition-check-performance/notes/phase-TP0-spec.md", "sha256": "ef83d1df4705cac3f6de33c236936fae8dd7601ee368525fb4b7c776d2fe7655"},
  {"path": ".gnd-planning/milestones/transition-check-performance/notes/phase-TP0-claude-review.md", "sha256": "61f4d440865a036c851f5bfef7d1be3f8cee55d4e7b7b665f92f609f2f390924"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP0/README.md", "sha256": "6a9c1f71ac9e6f7c1c41f21ede20a21b3e7147275357004f415bd7d5bbe57289"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP0/counters.json", "sha256": "e3dca209d24d9db47b06ec95275a19ccc5bf3f7a9fd3b204ddb78594942e5ca6"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP0/digests.json", "sha256": "d736d4d75fd82b7c5fd42102515d6b43eb21946326eaa3ebfd6a5223a1d4ca1c"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP0/gate-py3.11.txt", "sha256": "81edc87a6ad1c3c48ce1fb18179be15f95581c04db0639d1cba83e9cea8fb24c"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP0/gate-py3.13.txt", "sha256": "3c7de727d58ab7d6bc80be55277b42288ad1dcde7e74ebe31bb024d51f12c154"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP0/gate-py3.14.txt", "sha256": "8d0396c44c57b9c0698981f9814c3c957898375090bc9bda6f97d5edd42fd261"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP0/import.json", "sha256": "56094da254748e1c6ed4b6412538f5c78b1ba8d07b042ad6eda50c3dd02ac2ec"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP0/lint.txt", "sha256": "82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP0/review-mutants.py", "sha256": "8081d91e809ff83da5cc00df1e29502ae0dbc95c5f7061df5e9607d381e0292d"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP0/review-mutants.txt", "sha256": "603ffc330b45dbe272b2964f62486f7543b758311497e930a10206d62a90e1ca"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP0/timings.json", "sha256": "eb619a2ebffc94cdc3b7d1ef9d4ec8a69b20f6a4c8e83c0f2b26930961397ead"}
]
