---
milestone: induced-knowledge
station: phase-IK4
skill: "n/a -- repository development via process-phase, not a gnd-solve station over a domain model"
scope: phase-IK4
date: 2026-10-25
gate:
  command: "uv run pytest -q -p no:randomly <the IK4 file list, evidence/IK4/gate-files.txt>"
  exit: 1
  output: "1 failed, 6640 passed, 234 deselected, 1 warning in 571.72s (0:09:31)"
  note: >-
    Direct IK4 tests (tests/test_discover.py: the approved 20-case corpus,
    T3-T5, T10, T11 and the review regressions; tests/test_ik4_indexed_set_families.py:
    oracle parity for the three new checker fast paths) plus the impact
    closure: IK2's repair gate (IK2's 90 files, every tests/test_rf*.py,
    test_gnd_arch.py), every test naming equality, exclusion, frequency,
    semantic_rows or the family registry, the checker suites, docs and
    packaged-invocation guards. The one failure, tests/test_incremental_performance.py::test_prepared_policy_rechecks_live_hashability, also fails on main 3b65d15 (IK4-Q5); the one warning is pre-existing. Lint: ruff check on every changed Python file, All checks passed!
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner selection or separately configured CI"
  reason: "outside IK4's impact closure; the reduced v6.3 selection was run"
evidence:
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK4/build_dynamic_successor.py
    sha256: 009a3ee9f3fe32305bbaf93e1506d297f43f0977ea9e3ca0209045d6f855c7cd
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK4/dynamic-query-successor.json
    sha256: 136ae23c98147a7142cf75a29a456be0e877161728dcc32fc0a5e6d9294be0ac
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK4/final-gate.txt
    sha256: c1c98dd9bfbf4cf342df2998aa4dd7cf7af78c91f206a770dada55d2f2aea941
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK4/gate-files.txt
    sha256: 0cbed5bac32d12d9361f058dcc73a89560067f4895eb2b1ef4fb8b98546e719e
  - path: .gnd-planning/milestones/induced-knowledge/notes/induced-knowledge-plan.md
    sha256: 8afbdcbd4a7757053c8775cc4faaade1225534664ccd7cdb6ad22ae5b54cd51a
  - path: .gnd-planning/milestones/induced-knowledge/notes/phase-IK4-agent-review.md
    sha256: 9b7ecb01cbb35f2dca57f7db565db1dcde31db01bfbd7c094fc7c73f55ee3389
  - path: .gnd-planning/milestones/induced-knowledge/notes/phase-IK4-spec.md
    sha256: 675a625f647be3c210273684db97f2aeb3d7e83779763404bb7a055a4abe3edb
  - path: docs/reference/capabilities.md
    sha256: 0b316155067cc2340d8e0c7392317d2cce20fe9e5ea571e2944ee390f7787f66
  - path: docs/reference/cli.md
    sha256: 9c3deb4f8590d5a1660e8d2b1be272f4c2a7ed87f2f3858178c8b1c35e6d24e5
  - path: docs/reference/discover.md
    sha256: ef2bee12900699f5fe2d47a3026bc1eed54b01d9cca6ff0811cc6fcf0fe4894e
  - path: src/gnd/cli.py
    sha256: 5fd5555e6709a8dba5d3d3e8bbd589c51c3219f448640d3718cfcd20d04e5b6b
  - path: src/gnd/commands/discover.py
    sha256: d1ca521240aba18517b2fe84cd69bbae77fa9b50dad8ac3f159fb22872694ce1
  - path: src/gnd/constraint_families.py
    sha256: 28772968671b6298fa2a24cb047551239547ddcb52637f5d150ba443e2651196
  - path: src/gnd/discover.schema.json
    sha256: 1101070ce845d3642997dad5a2dc681774cc57937001221d9e89ca02604183e4
  - path: src/gnd/discover/__init__.py
    sha256: 2637fb2bce3e15babdb57d71a2c92f180f44b16262c06564b42e97fa5645ab2d
  - path: src/gnd/discover/candidates.py
    sha256: c3093a04b942c913e97802dba538d40513f33e5d9c347145c1bf30a25a717989
  - path: src/gnd/discover/output.py
    sha256: 942c02e18fcd9a82f824b3bce4c224cc6c0b0efdc7278696031718f2273a97b8
  - path: src/gnd/discover/service.py
    sha256: 6cd5999f2af3840a1bb0e443beefec4c55760153a583aff68b62720cd9b33b2a
  - path: src/gnd/discover/support.py
    sha256: 5cc2df401d1620a3b31992796697fef8a88e79a9ba385335ed8273fd384f1756
  - path: src/gnd/model/_induction.py
    sha256: cb0220eb0d93748757f72f92eb082442fa814b9094abd995b6cb2cfa9d862849
  - path: src/gnd/semantic_rows.py
    sha256: a3ed1885f3dbb6d7a4e2edbf92ac9bd91f5a46fdc9b8deafd1a3a7f1899bf3e4
  - path: src/gnd/skills/gnd-model-evolve/SKILL.md
    sha256: 2fcb54cfa42934cbc37dbd0f92a3eb5111483120e8f27424c09296dd84e9b9df
  - path: src/gnd/skills/gnd-solve/SKILL.md
    sha256: a45530b0b60233dc90b6850c9eaa9e5903eefbdc89e87ac4465bc83dad5ba1b7
  - path: tests/fixtures/rf1-pins/goldens.sha256
    sha256: decf43ce9c6001a578b20683354830b12381f088014263a9a08e02ed262f418b
  - path: tests/fixtures/rf1-pins/goldens/cli/tree.json
    sha256: 0cb07e1b394189e44b61358d5d219e962f0760fdb014f36100b7c6547f4f301c
  - path: tests/support/pyrel_application_successors.py
    sha256: d7911acbd74f4bc16fc9c2541495648979151d4594db9b1f3b45f83c635eb411
  - path: tests/support/rf5_sources.py
    sha256: 941772898a86348f373e14730bc24175f41c3ed840236286d3ccb49b7856f495
  - path: tests/support/runtime_schema_inventory.py
    sha256: 304743fe2b0a663f50f1e91e6050590cc5e1df3ab2e35d0bcdff5e0ac438e596
  - path: tests/test_discover.py
    sha256: 6e8bea131ab4f2ad96e7c52ebcddba01b3a38ce50b7c44db4d2203dec956a738
  - path: tests/test_ik4_indexed_set_families.py
    sha256: 4ab891494334bc9dab8102112f22842de5d08fcb3d81ac5da8415c7bd9f16b33
  - path: tests/test_incremental_prepared_policy.py
    sha256: cca1c8395afb92f411cfd4c834e700a7112236d587cc18f85c1aaaec5f769e2d
  - path: tests/test_incremental_sessions.py
    sha256: 9929ff8db53d91b27ceea11cbc4fc77a7a18c2beb6eb0826a9df9d00050eb23b
  - path: tests/test_induced_provenance.py
    sha256: d0aba0141c4cc3a18b0b4a4ca179274997d52a39879789988c04a604d077a623
  - path: tests/test_m3_indexed_subset.py
    sha256: 2c2cfa61e0ff7fe97f170dd79efb15e4df25a36ff1acf9351fdbcc9c0bd324d0
  - path: tests/test_public_built_inventory.py
    sha256: 3e57b003597277746a987892b95f41d09162acbf70960537b908f6121bf60c10
  - path: tests/test_rf1_cli_pins.py
    sha256: 505cd6370f6aa2b00596bc406301f70bd59e7b3516957a4ee0e1f2ba5712852d
  - path: tests/test_rf1_pin_harness.py
    sha256: 134110076e43db13d988332adc7af2628e6d5883cd85e644e312b2ef274fdc9e
  - path: tests/test_rf5_commands.py
    sha256: 78ba583ec43f996c2011f702fe4c93bf333e6721033d796443334e62c363e8b5
  - path: tools/gnd_arch.py
    sha256: 44637bd210f479873fc83208736c21da7ee4d74032468c03cffb2243baa82879
  - path: tools/gnd_entrypoints.json
    sha256: 60531f5bdeb159f70b5f073bcfd7355ca3e9b2fc554898c48b22d3465d78bc2c
  - path: tools/gnd_layers.json
    sha256: b094a964243ef4ae567dfeeacea9cf3a60f0c2fc0c37b684ece2c2e4f16e112b
  - path: zensical.toml
    sha256: f89f6b996fca408d7ab3c70b6cbcca7aacbb66786e111ee5afbf6eb31c04857d
---

# Phase IK4 — constraint discovery

**Claim.** IK4-C1 to C5 hold on the evidence below, under the owner rulings
recorded in spec §15 to §17.
- `gnd discover MODEL POPULATION` suggests single-role constraints of seven
  families. Each one passes `gnd check` with support > 0, and none is declared
  in or entailed by the model.
- The suggestions are written as an evolve proposal of induced, proposed,
  deontic constraints, together with a report.
- Every refusal, skip and suppression is counted.

## What shipped

- **The `discover` lane:**
  - `src/gnd/discover/{support,candidates,output,service}.py`;
  - the handler `src/gnd/commands/discover.py`;
  - the report schema `src/gnd/discover.schema.json` (`gnd-discover/1`);
  - the contract page `docs/reference/discover.md`.
- **Admission:**
  - one `gnd check` run over every surviving candidate;
  - support computed from the population with the checker's typed identity;
  - a candidate the checker passes but discovery saw violated is exit 70;
  - the IK4-D3 near-miss rule.
- **Suppression:** the closed catalogue in precedence order. A declared
  frequency with `max: 1` also suppresses superkeys (R12 (o)). After admission,
  the redundancy rules apply.
- **Skips, each counted:**
  - fact types an operation references, and derived or semiderived fact types;
  - value rules on redacted roles (R5 (o));
  - value rules on opaque or unrepresentable columns;
  - mandatory rules on object types a derived fact type plays;
  - candidates past the proposal size budget.
- **Output:** a schema-3 evolve proposal built with evolve's own replay, written
  as JSON, or as block YAML when JSON cannot spell the model. The report states
  every bound and skip, the work, and its corrected ceiling (R11 (o)).
- **Checker fast paths (owner rulings F2):** `indexed_equality_verdict`,
  `indexed_exclusion_verdict` and `indexed_frequency_verdict`, registered as
  `production=` hooks, with oracle parity.
- **IK2 fix (F13):** YAML integer forms (`0`, `1_000`, hex) count as exact
  support integers.
- **Registration:**
  - lane, RF5 group, entry points and the CLI wiring;
  - CLI goldens for the new command only, the census delta and the schema
    packaging inventory;
  - CLI and capability rows, a nav entry and two skill lines.

## Gate output (verbatim)

```
$ uv run pytest -q -p no:randomly <IK4 file list; evidence/IK4/gate-files.txt>
FAILED tests/test_incremental_performance.py::test_prepared_policy_rechecks_live_hashability
1 failed, 6640 passed, 234 deselected, 1 warning in 571.72s (0:09:31)
$ uv run ruff check <changed .py files>
All checks passed!
```

Also run during the phase:
- **Corpus:** committed red at `3e1ef3e` (18 failed, 3 passed by design); all
  20 cases pass on the implementation. N1, the near-cap case, takes about 15 s.
- **Fast-path parity and measurement:**
  - 90, then 113, then 116 parity tests over random typed snapshots;
  - the reviewer separately ran 26,465 differential comparisons and found no
    divergence;
  - N1 at full size went from infeasible (390 s at 1/20 scale) to about 38 s
    profiled.
- **Review regressions:**
  - all 18 fail on a copy of `a6947a4`'s source and pass after the fixes;
  - the R13 tests kill the reviewer's surviving mutants D1, D3, D7 and D11 (4 of
    4), and pass on the unmutated copy.
- **First IK4 gate on `a6947a4`:** 6,610 passed and 3 failed.
  - Fixed: the schema packaging inventory, and a fallback-evaluator test that
    swapped a pure path the fast path now bypassed.
  - Pre-existing: the hashability test.
- **Second run:** 6,639 passed and 2 failed. The CLI tree golden had changed
  with `--actor`'s new validator; the `discover` entry was refreshed and the
  RF1 pins then passed (148). The other failure is the pre-existing hashability
  test.

## Criteria

| Criterion | Result | Tests |
|---|---|---|
| C1 | met | corpus K01–K08, T3 (every emitted ref passes check), T4 (a wrong discoverer fails T3; a pass with counted violations is exit 70), R1–R7 |
| C2 | met for every model evolve can preview | K08 preview exit 0 and T6 replay; R7 replay equality. Reference-bearing and YAML-only-valued models cannot be previewed by evolve itself (F12, IK4-Q2/Q3) |
| C3 | met | T5 brute-force oracle on six cases, R1 typed identities, opaque ids `ft<k>#<i>` / `ot<k>#<i>` |
| C4 | met | K04, K07, N1 (work ≤ 74,531,600 and population ≤ 10 MiB), R11 (work ≤ the corrected ceiling on adversarial shapes), R13 exact counts, T13 determinism |
| C5 | met | K09 (every catalogue row, including an alethic declared constraint suppressing its deontic twin), R12, R13 minimal keys |

No bound was moved after implementation. The work-ceiling formula was corrected
by owner ruling, with its arithmetic in spec §17; the approved N1 number is
unchanged.

## Adversarial review

One local reviewer agent read `git diff 3e1ef3e a6947a4`. **One reviewer is one
reviewer.**

**What it found:**
- seven blocking defects: R1 identity mismatch, R2 opaque cells with a stderr
  leak, R3 references, R4 derived rosters, R5 redacted values, R6 size cap and
  R7 YAML-only values;
- three hardening defects (R8–R10), plus R11, which needed a spec ruling;
- two completeness gaps (R12–R13).

**Disposition:**
- The author reproduced the blocking findings before fixing them.
- The owner ruled R5, R11 and R12 as recommended.
- Everything is fixed with regression tests, except the two evolve limits and
  the checker defect, which predate IK4 and are carried as open questions.
- The report is retained verbatim with its disposition in
  [phase-IK4-agent-review.md](notes/phase-IK4-agent-review.md).

**What held:**
- the three fast paths equal the oracle on 26,465 comparisons;
- `gnd check` output is unchanged at the base on 120 fixture pairs;
- 900 fuzzed end-to-end models all exit 0, with passing refs, correct support
  and 246 previews at exit 0;
- discovery is idempotent on its own output.

## Refactoring review

**Refactors EXECUTED:**
- **One replay home.** The proposal's candidate is built by evolve's
  `_apply_declared_operations`, not a second implementation of replay.
- **Shared fast-path skeleton.** `_indexed_set_rows` and `_set_family_close`
  carry the applicability, validity, canonical-row and vacuity steps for
  equality and exclusion. Frequency follows the same order. Subset's existing
  body is unchanged.
- **One identity function.** `support.identity` is the checker's
  `canonical_scalar`, used by every scan and by the suppression catalogue,
  replacing the first draft's JSON-text keys.
- **One capped reader** for both inputs.

**Seen but deferred:**
- **IK4-Q2:** evolve cannot preview reference-bearing models, because it
  validates a temp copy without the reference files.
- **IK4-Q3:** evolve cannot preview models with YAML-only values such as dates,
  because it serializes them as JSON.
- **IK4-Q4:** a checker witness can lack an admissible origin for mandatory
  rules over computed rosters. This predates IK4.
- **IK2-Q3, carried:** `_evolve_service_exit`'s substring mapping.

## Boundary — what this phase does NOT establish

- One reviewer is one reviewer; the broad lanes were not run (`slow_cadence`).
- **Support is a recorded claim** tied to the population digest. Rules that hold
  in one population may not hold in another, and owner review decides.
- **Single-role sequences only.** External uniqueness and frequency, and
  multi-role subset, equality and exclusion, are out of scope (spec §9).
- **One population** of at most 10 MiB in memory. YAML is also capped at
  1,000,000 parse events, so a large population should be JSON (F1).
- **Two evolve limits** stop some proposals from being previewed (F12).
- **An existing `--out`** is refused at exit 11 before any write (IK4-Q1, owner
  ruling, spec §18).
- **Pre-existing red:** `tests/test_incremental_performance.py::test_prepared_policy_rechecks_live_hashability`
  fails on `main` too (IK4-Q5).

## Open questions

| ID | Question | Target |
|---|---|---|
| IK4-Q1 | Refuse or remove an existing `--out` when nothing is emitted (review R9 remainder) | **owner-ruled 2026-10-25 (o)**: refused at exit 11 before anything is written (spec §18). Closed |
| IK4-Q2 | Let `gnd evolve preview` handle reference-bearing models | **owner-ruled (o)**: schedule before IK6's walk |
| IK4-Q3 | Let `gnd evolve preview` handle YAML-only model values such as dates | **owner-ruled (o)**: milestone close |
| IK4-Q4 | Checker witness "has no admissible origin" for mandatory rules over computed rosters (pre-existing at `3b65d15`) | **owner-ruled (o)**: milestone close |
| IK4-Q5 | `test_prepared_policy_rechecks_live_hashability` fails on `main` | **owner-ruled (o)**: separate maintenance |

## Refuted premises

- **"One `gnd check` run is cheap enough at the 10 MiB cap" (implicit in §6 and
  N1).** It was quadratic for equality, exclusion and frequency until the owner
  approved fast paths (F2).
- **"`W ≤ R × 18 + 2 P R_max` bounds discovery's work" (IK4-D7).** It
  undercounts per-role and roster scans; the bound was corrected by owner
  ruling (R11).
- **"Discovery may key values by their JSON text" (first draft).** It must use
  the checker's typed identity, or it disagrees with the checker it defers to
  (R1).
