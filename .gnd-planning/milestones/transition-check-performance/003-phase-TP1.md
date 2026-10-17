---
milestone: transition-check-performance
station: phase-TP1
skill: n/a -- repository development, not a gnd-solve station
scope: phase-TP1
date: 2026-10-16
gate:
  command: "uv run pytest -q tests/test_transition_cost_workload.py tests/test_tp1_index_scope.py tests/test_rf6_index.py tests/test_rf1_layering.py tests/test_public_transition_contract.py tests/test_popvalidate.py"
  exit: 0
  output: "179 passed in 98.70s (3.14.3); 179 passed in 119.85s (3.11.15); 179 passed in 135.34s (3.13.12)"
slow_cadence:
  command: uv run pytest -q
  trigger: explicit owner selection
  reason: focused gate plus 813 affected-consumer tests cover the touched homes
---

# Claim

TP1 is complete under the owner-approved spec ([spec](notes/phase-TP1-spec.md), approved
2026-10-16 as "approved"; SHA-256 `531f8016…56b1`; findings were appended afterwards).

**What changed:** a per-call index scope in `gnd.model_index` (`index_scope` and the
`scoped` decorator), entered at five entry points: `checking_service._run_check`,
`api._run_transition`, `batch.check_population_directory`,
`population.load_population_bytes` and `checker._core._check_dispatch`.

**Results on the reporter replay:**

- `model_index_key_paths`: 540 → 26, exactly as predicted.
- `model_dumps_other`: 457, unchanged.
- `checker_runs`: 25, unchanged.
- Every TP0 digest is unchanged.

## Gates

- **Focused gate:** exit 0 on three interpreters (frontmatter).
- **Affected consumers:**
  - public API, signature, and RF1/RF2/RF6/RF7 pins: 249 passed;
  - transition, preparation, compiled-snapshot, batch and runtime suites: 564 passed and
    16 deselected.
- **Lint:** All checks passed!
- **Red first:** 5 of 8 failed before implementation (`evidence/TP1/red.txt`).

## Measurements

| Counter (reporter replay) | TP0 | TP1 |
|---|---|---|
| `model_index_key_paths` | 540 | 26 |
| `model_dumps_other` | 457 | 457 |
| `checker_runs` | 25 | 25 |
| `deepcopy_nodes` | 2,760,394 | 2,760,394 |

**Wall time:** the in-process A/B (`evidence/TP1/ab_scope.py`) measured 4.01 s without the
scope and 2.81 s with it, −30%. That matches the plan's simulation. Separately launched
medians drift with machine load and are not compared (spec finding 4).

## Independent review

One local reader ([notes](notes/phase-TP1-claude-review.md)). **One reviewer is one
reviewer.** Nothing blocking: 0 stale hits in 22,029 in-scope lookups across 786 tests.

- **F1 (hardening, low):** the decorators covered for each other, so removing one went
  unnoticed. Fixed with a counted test per route.
- **F2:** D3 had no case. Fixed with its own test.

Six mutants were each shown red (`evidence/TP1/review-mutants.txt`). The redundant
`load_population` decorator was removed (spec finding 8).

## Refactoring review

**None needed.** The change is additive: one module scope plus one decorator line per
entry point, with no call site edited. Review F1 showed that `load_population` is a thin
file reader over `load_population_bytes`, and the redundant decorator was removed in this
phase. No other structure was revealed as needing change.

## Boundary and open questions

- **Within a call, the index assumes model content does not change.** Verified by an
  oracle over 22,029 hits. Concurrent mutation of a shared model from another thread is
  not supported, as before.
- **TP0 spec D5 was amended:** the hang guard went from 120 s to 600 s, after a
  reproduced timeout under concurrent load. One earlier failure's cause is not established
  (spec finding 5).
- **Open, for the framework maintainer:** a signal-delivered exception during semantic-rule
  evaluation is reported as a "defective rule". This predates the milestone.
- **Unrelated:** two pre-existing `test_rf6_query_policy` failures on `main`.
- **Next:** TP2 (deep copies), then TP3 (receipts).

## Evidence hashes

[
  {"path": "src/gnd/model_index.py", "sha256": "a395ded629911dd1d95cec7b6b50ed2ec8b9f80014441e7be6957f7a3b9182c9"},
  {"path": "src/gnd/api.py", "sha256": "003f11fc5be7819f32ed0348716c4927b0d6575e0d17f6f7d71f104b8a6b5636"},
  {"path": "src/gnd/batch.py", "sha256": "ffafab1ffed8fd4c6de402ea2bd268dedda3a737aaeb5c3321d295d4a40425ea"},
  {"path": "src/gnd/population.py", "sha256": "58397be425bff02e669a5457d9d91f545f63a90de56fbba59e5321d45195deba"},
  {"path": "src/gnd/checking_service.py", "sha256": "3d973dcba18e4a059ca4e773cdb20dc3b59ead43375eca7963969868d95596d7"},
  {"path": "src/gnd/checker/_core.py", "sha256": "fe3bfeb27996509bc050b756fabe44d9e9d793e7a6a98b65fa106ed489e8baa8"},
  {"path": "tests/test_tp1_index_scope.py", "sha256": "df47f2526d76086622a33b5570642fd05f213e5bb38523fac572d6a901d730d3"},
  {"path": "tests/test_transition_cost_workload.py", "sha256": "e620f7a3f662e49bed479e95b7b82564237c35ae1bd9d67db77dffdf3aa68480"},
  {"path": ".gnd-planning/milestones/transition-check-performance/notes/phase-TP1-spec.md", "sha256": "4e2afed8f5b5c2c641d4efeddfcba8b7c7202e874002601a436684c06270faa1"},
  {"path": ".gnd-planning/milestones/transition-check-performance/notes/phase-TP1-claude-review.md", "sha256": "09124ea02421dd8cb1dfc6fee87c4de5d7097bf65b977e23611a5f3d7d9a51c5"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP1/ab_scope.py", "sha256": "ea1139a2f0682ec5429e9788e20eb71e81e11a4580907dcbb6f71dcdbb17690f"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP1/ab_scope.txt", "sha256": "cbad7366530e52ebf1cf3e70f4f2b3b6747c2a1a09f4e0961375ddd205135d61"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP1/consumers-1.txt", "sha256": "3ace4a69625e031a24d9a3a2831896a8ac463488a87391c4c7a6834da2666417"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP1/consumers-2.txt", "sha256": "dfe02f0ece4b2cf437de36b59a1511d7fdaed1eddb4116753e4088eb17772208"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP1/counters.json", "sha256": "40989f99c92aff8313f0c8250b8b13358611cf5c5836899b8fdad1c1e2d81cfd"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP1/digests.json", "sha256": "d736d4d75fd82b7c5fd42102515d6b43eb21946326eaa3ebfd6a5223a1d4ca1c"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP1/gate-py3.11.txt", "sha256": "2069d93e1b60add58f4305c7c35c9fb6c6dd7e42d78be6b150d79ba0829acfa7"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP1/gate-py3.13.txt", "sha256": "70fcfc6cfa0d7060324f89737fb5fc16b5369e52998cd0def37983f83897dda7"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP1/gate-py3.14.txt", "sha256": "9c976d345039c75f86af86cca6cf07927dcb9d6124377307815b3975df581620"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP1/lint.txt", "sha256": "82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP1/red.txt", "sha256": "950d9845d5e39cde1b01a32058be3c2998a6112a9b190eff2348f917601903d6"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP1/review-mutants.py", "sha256": "87b91cc43ef3e496b272e5a79257dbd29b584a7915288ee83cbc8b275c16ea69"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP1/review-mutants.txt", "sha256": "9d6c982998b1690932dc20193cdd9020e3ae9071ca314a102d917a7fc6edcf63"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP1/timings.json", "sha256": "55fa02d5ebc2380acf852591fb31b7a929e2f065972f413f213eaad6213cadd6"}
]
