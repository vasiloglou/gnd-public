---
milestone: model-growth-guardrails
station: "phase-MG2"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-MG2
date: 2026-11-04
gate:
  command: "uv run pytest -q tests/test_evolve_additive_policy.py tests/test_model_evolution.py tests/test_evolution_conformance.py tests/test_evolve_loading.py tests/test_evolve_references.py tests/test_public_evolution_drift_readers.py tests/test_public_evolution_legacy_readers.py tests/test_public_evolution_version_graph.py tests/test_public_legacy_evolution.py tests/test_rf1_cli_pins.py tests/test_disclosure_mode.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py tests/test_object_type_description.py tests/test_model_v2.py tests/test_exp_bands.py tests/test_verification_fixes.py tests/test_rf1_pin_harness.py tests/test_disclosure_docs.py tests/test_skill_prose_sync.py tests/test_public_binding_prose.py tests/test_packaged_skills.py tests/test_measure_offline.py tests/test_conformance_payload.py tests/test_ik_close.py tests/test_rf3_core.py tests/test_rf4_peripheral.py"
  exit: 0
  output: "1895 passed in 177.44s (0:02:57)"
  note: >-
    The plan's section 9 MG2 row plus the spec's impact closure, with
    tests/test_ik_close.py, test_rf3_core.py and test_rf4_peripheral.py added
    for the handler source scans. tests/test_il6_skill_census.py is in the
    impact closure but runs after the commit (spec F9); its result is in the
    body. Docs commands and the parity capture are listed in the body.
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "the broad historical lanes are outside MG2's impact closure: two opt-in evolve options, one policy module, pins and docs"
evidence:
  - path: .gnd-planning/milestones/model-growth-guardrails/notes/phase-MG2-spec.md
    sha256: 3ceabfaead9600707986752f683ba08f8078eb4d93ee73697452ea6e71317985
  - path: .gnd-planning/milestones/model-growth-guardrails/notes/phase-MG2-claude-review.md
    sha256: 84fd700038fd11780c9e91697a01d91a63d6c86e6628cbf0c1669843a4f42cbe
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/MG2/capture_parity.py
    sha256: b3b4a50b0837687ab02d3a6d0f72413ac0e789ca85fa0c11553fdbf8e334314d
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/MG2/parity-before.json
    sha256: 8abffb5bc88ed2b64c2ccdfa60b2c1f7be65c1ec457f6c28e1df849dd8bac88f
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/MG2/parity-after.json
    sha256: 8abffb5bc88ed2b64c2ccdfa60b2c1f7be65c1ec457f6c28e1df849dd8bac88f
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/MG2/query-successor.json
    sha256: e614010b162b950af31fd143c57e3fdd66657b1de2bb7469402dbcb3ec406d2c
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/MG2/dynamic-query-successor.json
    sha256: 6dc3da453b49e2bb3f99c9b6eb7c6f49a71692cd7f082e8be51a949a841856a8
  - path: src/gnd/evolve/policy.py
    sha256: 78a04cc2327c35d85e71f59022c666f23fee2ec101dd68b2e7b05656baed8726
  - path: src/gnd/evolve/models.py
    sha256: bc9912f4b8f382f856df83a0e6738dfe02cd12374d4738593b86538fc793cce3
  - path: src/gnd/evolve/service.py
    sha256: ca58acc1a1e090711d34c2aac2fc0908aa630bc037d3b0bc039a0dc89545afc1
  - path: src/gnd/evolve/cli_service.py
    sha256: 4d06396ca9b2d1c99c0af0476cf98948a70aae41c1935e997ad516833674ffa3
  - path: tests/test_evolve_additive_policy.py
    sha256: 6acd30d2050fee57f947ee41085922d8fa6eea1ff57a1773e2438b5b3943c760
  - path: tests/fixtures/evolve-policy/base.orm.yaml
    sha256: b7c5713d33f5cd57cea7fe6745f1a4b3d2d17f50090bfad9774bf1a0c26e1fe6
  - path: src/gnd/skills/gnd-model-evolve/references/evolution-contract.md
    sha256: 57d780708501e230a98ee95eeead72bd8b3233c5bbef2748c085ef5285c83966
---

# Phase MG2: additive policy on gnd evolve preview and apply

**Claim.** `gnd evolve preview --policy additive` refuses, with exit 3 and a
written preview, any operation that would leave facts admitted under the
current model uninterpretable. That covers a rename, delete or out-of-list
modify of an existing object type, fact type or role; a model identity
change; and a new or stronger constraint on a populated fact type. `apply`
must repeat the preview's options, re-runs the policy on the bytes it
publishes, and exits 11 when the populated set changed in between. Without
`--policy`, every preview and apply over the eight evolve fixtures is
byte-identical to `d5f6e9e` and exits as before. The focused gate exits 0.

**Authority.** Plan r3 approved `(a1)` ([001-plan-gate.md](001-plan-gate.md));
spec r1 approved `(s1)` 2026-11-04 over SHA-256
`f04f2cf6c88275e627f81127524c4260bd5e34545ac1d127d16b59fdfd75449d`, with
rulings D1 (b) prose, D2 to D4 (a), D5 as stated, D6 to D8 (a), quoted in the
spec header. `auto=false`. The owner selected `process-phase MG2` ("Start MG2
spec", then "Approve MG2 spec"). Issue #75.

## What shipped

- `src/gnd/evolve/policy.py`, new, in the layering map's evolve lane:
  - `effective_populated`: sample rows, reference-population ownership,
    `population` artifact references and `--populated`, which must name a
    declared fact type.
  - `diff_paths` and `constraint_change`: the closed strengthening table.
    `roles` follows the subset rule for uniqueness only (review R-F2).
  - `additive_policy_issues`: the matrix over locator kind and operation kind.
    Element MODIFY allow-lists are prefix-closed. A model-hosted constraint's
    subjects are every fact type its before and after sides name (R-F1).
- `src/gnd/evolve/models.py`: `PolicyIssue` and the `PolicyCell` literal; four
  optional preview fields, set together, omitted when absent, so a
  policy-free preview has no new key.
- `src/gnd/evolve/service.py`: `EvolutionPolicyRefusedError`; `preview`
  runs the policy after D-12; `apply` re-runs it on the live model.
- `src/gnd/commands/evolve.py` and `cli_service.py`: `--policy additive` and
  repeatable `--populated` on both commands; the option check before the
  retry branch; the refusal maps to exit 3 by type.
- Fixture `tests/fixtures/evolve-policy/base.orm.yaml` and
  `tests/test_evolve_additive_policy.py` (75 cases).
- Pins: 12 RF1 help and exit-probe goldens, `tree.json`, the manifest and
  `MANIFEST_SHA256`. RF6: a counted query successor and a dynamic-read
  successor.
- Docs: the contract's "Additive policy" section and command table, the
  SKILL.md section, the new `docs/reference/evolve-policy.md` with its nav
  entry, CLI reference rows and an Unreleased release note.

## Gate and other commands

| Command | Result |
|---|---|
| focused gate (front matter) | `1895 passed in 177.44s (0:02:57)`; pytest exit 0 |
| `uv run python tools/run_tutorials.py` | `257 tutorial blocks passed`, exit 0 |
| `uv run --group docs zensical build --strict` | `Build finished in 0.87s`, no issues |
| `uv run python tools/check_docs.py site` | `13170 local links/assets/anchors checked`, exit 0 |
| `capture_parity.py …/parity-after.json` | 8 fixtures, every one `stable`; `parity-after.json` is byte-identical to `parity-before.json` captured at `d5f6e9e` |
| `uv run pytest -q tests/test_il6_skill_census.py`, after the commit | `9 passed in 4.98s`, exit 0 |
| anonymity scan over added and changed files | 0 matches |
| `uv run ruff check src/gnd/evolve tests/test_evolve_additive_policy.py` | `All checks passed!` |

## Coverage against the branch table

| Branch | Case |
|---|---|
| each matrix cell, refused and admitted | T1, one case per cell with its mutant; `reach` says whether the service or only the function can reach it |
| cells pre-empted before the policy | T1e (constraint RENAME), T1 role ADD and DELETE (candidate validation), T2a (D-12) |
| each strengthening item and its weakening reverse | T2, T2a, the `bound.max` added variant, the `max_inclusive` variant |
| "neither" | T2b, T12 hostile pairs, R-F2 |
| each populated source and the unpopulated control | T2c, R-F3 |
| model-hosted "any" against "every", and both sides of a MODIFY | T2d, R-F1 (two cases) |
| CLI option agreement, retry-branch order, written preview | T3, T3a, T3b, T3c |
| populated set changed before apply | the populated-stale case, exit 11 |
| no value in `detail` | T6 |
| parity without the options | T4, T5 |
| cell literal, contract table and emitted cells agree | T14 |
| linear cost | T13 |

## Adversarial review

One reviewer is one reviewer:
[phase-MG2-claude-review.md](notes/phase-MG2-claude-review.md), a local agent
reading the diff with the repository read-only. It ran the gate subset, five
probe scripts and 22 mutants, but not the docs commands, the IL6 census or a
fresh RF1 recapture. Verdict reject: two blocking findings, two hardening,
three completeness. Each was reproduced, and the dispositions are in the
spec's "Review dispositions" section:

- **Blocking, fixed with regressions shown red before the fix:** R-F1, a
  hosted constraint re-pointed onto a populated fact type, and R-F2, a wider
  frequency projection. R-F2 was confirmed by `gnd check` on a population
  that passes before and fails after.
- **Hardening, cases added:** R-F3 and R-F4.
- **Completeness:** R-F5 dead line removed, R-F6 wording corrected, R-F7
  documented.

Re-running the surviving mutants on the fixed bytes found one more gap. A
mutant that drops the before side of a hosted MODIFY survived the first R-F1
case, so a second case now pins that direction. Every non-equivalent mutant
is now killed.

## Refactoring review

**None needed**, argued from what MG2 touched. The policy is one new module
that reads through `ModelIndex` and plain dicts and is called from two
existing seams in `service.py`. The service and CLI changes add branches
beside the operations gate and the existing type-based exit mapping rather
than reshaping them. No helper was written twice.

**Seen and deferred:** `effective_populated` and `additive_policy_issues`
each walk the before model's fact types once. Merging them would couple
their signatures; MG3 touches the same preview path (MG2-Q3).

## Refuted premises

- The plan's matrix has constraint RENAME cells. Proposal validation refuses
  a constraint RENAME at read, so they are pre-empted with exit 3 (F1,
  MG2-Q2).
- The spec treated role ADD and DELETE on an existing fact type as reachable
  through the service. Candidate validation needs one reading placeholder per
  role, so neither reaches the policy alone (F6).
- The approved strengthening table said a `roles` proper superset is a
  weakening for every family. Review R-F2 refuted it for frequency.

## Open questions

| ID | Question | Target |
|---|---|---|
| MG2-Q1 | C3's "preview made with `--policy` and `--shape-report` applies (0)" needs MG3's option | MG3 spec |
| MG2-Q2 | Constraint RENAME cells are pre-empted by proposal validation | plan repair at milestone close |
| MG2-Q3 | Merge the two walks of the before model | MG3 |
| MG2-Q4 | RF6 headroom is one counted read (364 of 365) and one on the original metric (309 of 310); MG3's helper must read through `ModelIndex` only | MG3 spec |

## Boundary

- One reviewer is one reviewer. The plan's four-reader bar applies to the
  milestone close, not this phase.
- "Populated" is a set of ids, not a population read; MG2 checks no
  population against the candidate.
- A preview stripped of every policy field and applied without `--policy`
  publishes as a policy-free preview. The guarantee is the caller's to repeat.
- The broad historical lanes did not run (slow cadence above).
- No push, pull request, merge, release, publication or certification is
  claimed.
