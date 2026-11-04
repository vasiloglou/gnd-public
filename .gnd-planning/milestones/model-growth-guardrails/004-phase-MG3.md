---
milestone: model-growth-guardrails
station: "phase-MG3"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-MG3
date: 2026-11-04
gate:
  command: "uv run pytest -q tests/test_evolve_shape_matches.py tests/test_evolve_additive_policy.py tests/test_model_evolution.py tests/test_evolution_conformance.py tests/test_evolve_loading.py tests/test_evolve_references.py tests/test_public_evolution_drift_readers.py tests/test_public_evolution_legacy_readers.py tests/test_public_evolution_version_graph.py tests/test_public_legacy_evolution.py tests/test_rf1_cli_pins.py tests/test_disclosure_mode.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py tests/test_object_type_description.py tests/test_model_v2.py tests/test_exp_bands.py tests/test_verification_fixes.py tests/test_rf1_pin_harness.py tests/test_disclosure_docs.py tests/test_skill_prose_sync.py tests/test_public_binding_prose.py tests/test_packaged_skills.py tests/test_measure_offline.py tests/test_conformance_payload.py tests/test_ik_close.py tests/test_rf3_core.py tests/test_rf4_peripheral.py tests/test_extract_applicable.py tests/test_extract_vocabulary.py"
  exit: 0
  output: "1941 passed in 156.81s (0:02:36)"
  note: >-
    The plan's section 9 MG3 row (the MG2 gate plus
    tests/test_evolve_shape_matches.py) and MG2's impact closure, with the two
    extract tests that import gnd.refscheme. Run on the bytes after the review
    fixes and amendment r2.
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "outside MG3's impact closure: one opt-in preview option, one advice module, one helper, pins and docs"
evidence:
  - path: .gnd-planning/milestones/model-growth-guardrails/notes/phase-MG3-spec.md
    sha256: 7a94e35d19edc98dc0a1b01602ea60f2be8f52bb92d229dab3b20c30a358e780
  - path: .gnd-planning/milestones/model-growth-guardrails/notes/phase-MG3-claude-review.md
    sha256: 004c52c897d55de2a431595c24c43850658e60256a5e018da1d7ea6a99713a06
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/MG3/capture_parity.py
    sha256: bce120db2f9ba4809f2da2f824b525576e6c7f71099fc644c2847f70a2590bb0
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/MG3/parity-before.json
    sha256: 8abffb5bc88ed2b64c2ccdfa60b2c1f7be65c1ec457f6c28e1df849dd8bac88f
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/MG3/parity-after.json
    sha256: 8abffb5bc88ed2b64c2ccdfa60b2c1f7be65c1ec457f6c28e1df849dd8bac88f
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/MG3/dynamic-query-successor.json
    sha256: d21caf7a30f3d101f9ee542e1868ca2bfebd85f8455e8f4edfc9daf91eb9b98f
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/MG3/mutants.json
    sha256: 61d70616a8fabb0e9d117572b5669b56ec70836010b050bd43fa09788b6e3164
  - path: src/gnd/evolve/shapes.py
    sha256: 3831ec3239530936544d4ac8103d3e8a3dea436e202be1023ce109ff868fd205
  - path: src/gnd/evolve/models.py
    sha256: 1197cf0bd8d52e989d2bd47d5b28b3a8cee166a13ca3a9d85a36fe1b7f07605d
  - path: src/gnd/evolve/service.py
    sha256: a87486b980f1acd1e156086331d0b10964225ffff64b96a379e379fa4371b75d
  - path: src/gnd/evolve/cli_service.py
    sha256: 24eb583672c73e84ece158a3facfd6ee9da0bbf60eaf49fc35eef63692b4d115
  - path: src/gnd/refscheme.py
    sha256: 8a94071f3585e93344e678cb612e97c5b4929ca2ac39caf6c4d2633f0e85ac4e
  - path: tests/test_evolve_shape_matches.py
    sha256: f61e6a76f5a65ee594ed42fccb9da55baf8d0a85df90f27c5854937ff5635d3e
  - path: src/gnd/skills/gnd-model-evolve/references/evolution-contract.md
    sha256: 21a9183d8d9d310d597f79dca9e61771e2a93eb6d899cea1e8f1d500bc36cafe
---

# Phase MG3: duplicate-shape report on gnd evolve preview

**Claim.** `gnd evolve preview --shape-report` writes `shape_matches`: one
group per role-player signature that an added fact type has, holding the
added fact types and the current model's fact types with that signature,
their readings, and how each entity role player is identified. The report
changes no exit, `breaking`, blast radius, `affected_references` or policy
field, and its size is linear in the model. Without the option, every
preview and apply over the eight evolve fixtures is byte-identical to
`9b069e2`. `apply` rebuilds the report when the reviewed preview carries one,
so an edited report exits 11. The focused gate exits 0.

**Authority.** Plan r3 approved `(a1)`. Spec r1 under **delegated approval
(auto=true)** `(d1)` 2026-11-04 over SHA-256
`722f31121b8c327a7a76bdf712c31c7bdb53524765222bf325bd611024954879`, and
amendment r2 `(d2)` after review finding R-F1, both recorded in the spec.
The authorization is the owner's "process-milestone model-growth-guardrails
auto" in this session; the rulings are agent rulings under it, not the
owner's reading. Issue #76.

## What shipped

- `gnd.refscheme`: `role_player_signature` (the one home of the shape rule,
  shared with MG4 and later CT4), `fact_type_signatures` (through
  `ModelIndex.role_object_types`), `entity_reference`.
- `src/gnd/evolve/shapes.py`, new, lane `evolve`: one bucket index, one
  `setdefault` probe per fact type, groups in order of first added member.
- `src/gnd/evolve/models.py`: `ShapeMember`, `ShapeAdded`, `ShapeReference`,
  `ShapeGroup`; the optional `shape_matches` field, omitted when unset; a
  reader check against the proposal's operations.
- `service.preview(shape_report=...)` after the policy; `--shape-report` on
  `gnd evolve preview`; apply passes it to both rebuilds; the retry branch's
  identity excludes it.
- `tests/test_evolve_shape_matches.py` (37 cases); ten mutants, all killed.
- Pins: six RF1 goldens, the `tree.json` hunk, `goldens.sha256`,
  `MANIFEST_SHA256`; one RF6 dynamic successor.
- Docs: the contract's "Shape report" section (normative), SKILL.md, the
  reference page section, CLI row, Unreleased note.

## Gate and other commands

| Command | Result |
|---|---|
| focused gate (front matter) | `1941 passed in 156.81s (0:02:36)`, exit 0 |
| `uv run python tools/run_tutorials.py` | `257 tutorial blocks passed`, exit 0 |
| `uv run --group docs zensical build --strict` | `No issues found`, `Build finished in 0.51s` |
| `uv run python tools/check_docs.py site` | `13177 local links/assets/anchors checked`, exit 0 |
| `capture_parity.py` at `9b069e2` and after | 8 fixtures, all `stable`; after byte-identical to before (and to MG2's after) |
| mutation table `evidence/MG3/mutants.json` | M1 to M10 each `KILLED` |
| `uv run ruff check src/gnd/evolve src/gnd/refscheme.py tests/test_evolve_shape_matches.py` | `All checks passed!` |
| anonymity scan over added and changed files | 0 matches |
| `uv run pytest -q tests/test_il6_skill_census.py`, after the commit | in the commit body |

## Coverage against the branch table

| Branch | Case |
|---|---|
| equal and unequal signatures (order, multiplicity, subtype, primitive) | T1, M1, M2 |
| existing and added members; two identical ADDs | T2, T1b, M5 |
| entity references direct, composite, unmatchable; value players absent | T2, `test_t2_composite_and_unmatchable_references` |
| modified, deleted, deleted-and-re-added existing fact types; added-then-deleted | R-F3, T2d, R-F5, R-F2; M7 |
| with and without the option; no fact-type ADD | T3b, T3c, M6 |
| advice changes no gate field, admitted, refused and breaking, with and without policy | T4 (6 cases), M4 |
| order after the policy | T4b |
| apply: report, report plus policy, edited (11), stripped (0), breaking rebuild, retry identity | T5, T5b, R-F4; M3, M8 |
| reader refusals | T3d (12 edits), M10 |
| linear cost and size | T7 (spread and single bucket), CLI under the read cap, M9 |
| no value in the report | T9 |

## Adversarial review

One reviewer is one reviewer:
[phase-MG3-claude-review.md](notes/phase-MG3-claude-review.md), a local
agent with the repository read-only, retained verbatim; its probes are in
`evidence/MG3/review-probes/`. It ran 121 MG3 and layering tests, 345 evolve
and disclosure tests, a parity re-capture and its probes; not the docs
commands, RF1 or the mutants. Verdict approve-with-fixes; seven findings,
dispositioned in the spec:

- **R-F1, blocking, fixed by amendment r2:** a quadratic report pushed a
  preview past the 10 MiB read cap, so apply exited 74. The reviewer's own
  repro now previews and applies with 0.
- R-F2, R-F3, R-F5, R-F6 hardening, R-F4 a doc contradiction fixed in code,
  R-F7 completeness: each fixed with a case, several with a mutant.

## Refactoring review

**None needed**, argued from what MG3 touched. The helper joins
`gnd.refscheme`, which already owned reference identity, and reads through
an existing `ModelIndex` accessor. The report is one new module called from
one seam in `preview`, and apply reuses its existing rebuild.

**MG2-Q3 closed (spec D4 (a)):** the shape report adds one
`role_object_types` pass over the before and the candidate model; merging it
with the policy's two walks would couple three signatures for no measured
cost.

## Refuted premises

- The plan's §2.3 shape ("for every ADD ... each existing fact type ... with
  its id and reading") is quadratic in a shape bucket and, near the read cap,
  changes apply's exit. Amendment r2 keeps its content and makes it linear.

## Open questions

| ID | Question | Target |
|---|---|---|
| MG2-Q1 | `--policy` plus `--shape-report` preview applies | **closed:** `test_t5_with_policy_and_shape_report_applies` |
| MG2-Q3 | Merge the before-model walks | **closed:** D4 (a), above |
| MG2-Q4 | RF6 headroom | **closed:** no counted read added (364 of 365) |
| MG3-Q1 | RF1 fresh capture drifts in about 60 unrelated goldens | milestone close |
| MG3-Q2 | A proposal of only ADD/DELETE pairs fails `BlastRadiusReport` (`too_short`), independent of MG3 | milestone close |

## Boundary

- One reviewer is one reviewer; the four-reader bar is for the close.
- A match is a candidate, never a duplicate verdict. The reader does not
  recompute signatures; apply's rebuild is the check.
- The broad historical lanes did not run (slow cadence above).
- No push, pull request, merge, release, publication or certification is
  claimed by this record.
