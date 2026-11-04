---
milestone: model-growth-guardrails
station: "phase-MG4"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-MG4
date: 2026-11-04
gate:
  command: "uv run pytest -q tests/test_extract_guidelines.py tests/test_extract_applicable.py tests/test_extract_cli.py tests/test_extract_manifest.py tests/test_extract_projection.py tests/test_extract_vocabulary.py tests/test_public_extract_boundary.py tests/test_public_extract_controls.py tests/test_public_extraction_prose_policy.py tests/test_v51_phase2_extraction_controls.py tests/test_v51_phase2_extraction_scope.py tests/test_fidelity_stub_gate.py tests/test_public_legacy_codegen_pins.py tests/test_rf1_cli_pins.py tests/test_disclosure_mode.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py tests/test_rf1_pin_harness.py tests/test_disclosure_docs.py tests/test_skill_prose_sync.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_rf3_core.py tests/test_rf4_peripheral.py tests/test_evolve_shape_matches.py"
  exit: 0
  output: "1533 passed in 98.77s (0:01:38)"
  note: >-
    The plan's section 9 MG4 row and the spec's impact closure, with the MG3
    shape tests for the shared signature helper. Run after the review fixes.
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "outside MG4's impact closure: one opt-in extract option and one generator"
evidence:
  - path: .gnd-planning/milestones/model-growth-guardrails/notes/phase-MG4-spec.md
    sha256: 473f737decad7c1d4cdaca8b2b0c54c5ec27ad925976bfeda245c46644a3d999
  - path: .gnd-planning/milestones/model-growth-guardrails/notes/phase-MG4-claude-review.md
    sha256: 0bf92cbc84ddcd79c2f0edd1c656fbafdfa54f7ec41a1209bb5a6b24d4e3202f
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/MG4/capture_parity.py
    sha256: b2c7bb125dd1cad6da2be96e5c7d296644d66d7d247f69a6549fe6d063109e8a
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/MG4/parity-before.json
    sha256: 00d6abec07a7de4da1446e93576ce0307af627a68662927c2ea06abb0bfa3305
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/MG4/parity-after.json
    sha256: 00d6abec07a7de4da1446e93576ce0307af627a68662927c2ea06abb0bfa3305
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/MG4/dynamic-query-successor.json
    sha256: d3a6cd551e9040d7f50e57fee979d9e391aaa74a068be785e1d6be5e9e52d5db
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/MG4/mutants.json
    sha256: cbdaf5b3104bcba8d24d962d977a4ad51449fa5d7822f2848464d88dc27ff69b
  - path: src/gnd/extract/guidelines.py
    sha256: e0d6410d4d6146f25137220d16f6bf2d3d33e128a816814df50cb4e1725dfa9e
  - path: src/gnd/extract/service.py
    sha256: c28a2c1458914f94d85ea429307864d75405cbb72a48dbc669c03b15ea1de265
  - path: src/gnd/commands/extract.py
    sha256: a29b88c5a23dbf4d1fc9faab3edf6a9be3da080fbc258ca6468c6742639f9da2
  - path: tests/test_extract_guidelines.py
    sha256: 4fffb8e06d04beba5fe0cc6200935f8e1d7ce168593f914ca2433f29d4a4a8e8
  - path: src/gnd/skills/gnd-extract/references/extraction-contract.md
    sha256: ebfafabe1c4490eb3a1331218493dfd42835254fb10603ab635964f12ad3f46b
  - path: src/gnd/skills/gnd-extract/SKILL.md
    sha256: 34726c22cd5a83e007e609c536a8eb1615b4cbc7929bd9f7f0cd52d1ef925240
---

# Phase MG4: extraction guidelines

**Claim.** `gnd extract MODEL --out DIR --guidelines` exits 0 and writes
`<stem>.guidelines.md`, recorded with its SHA-256 in `<stem>.artifacts.json`:
per fact type its readings and the fact types with the same role players,
per role the object type, its description core keys, how an entity is
identified and the primitive. No constraint other than an anchoring external
uniqueness changes its bytes. Without the flag every bundle over the 238
corpus models is byte-identical to `9b069e2`, with equal exits. The focused
gate exits 0.

**Authority.** Plan r3 `(a1)`. Spec r1 under **delegated approval
(auto=true)** `(d1)` 2026-11-04 over SHA-256
`d0a753ffaef6fca199dbae58c4f1ee0667a51647de3c963d6bb667a1f2849c8e`; an agent ruling under the owner's
"process-milestone model-growth-guardrails auto", not the owner's reading.
Issue #78.

## What shipped

- `src/gnd/extract/guidelines.py`, new, lane `extract`: `render_guidelines`,
  reading through `ModelIndex`; `gnd.refscheme.role_player_signature` (MG3)
  for "Same role players as"; one identity lookup per entity per render.
- `_cmd_extract(..., guidelines=)` and `gnd extract --guidelines`.
- `tests/test_extract_guidelines.py` (22 cases); nine mutants, all killed.
- Pins: two RF1 goldens, the `tree.json` hunk, `goldens.sha256`,
  `MANIFEST_SHA256`; one RF6 dynamic successor.
- Docs: contract §4a (normative layout, the O20 sentence), SKILL.md, the
  documents guide, CLI row, Unreleased note. Codegen unchanged (MG-D11).

## Gate and other commands

| Command | Result |
|---|---|
| focused gate (front matter) | `1533 passed in 98.77s (0:01:38)`, exit 0 |
| `uv run python tools/run_tutorials.py` | `257 tutorial blocks passed`, exit 0 |
| `uv run --group docs zensical build --strict` | `Build finished in 0.74s`, no issues |
| `uv run python tools/check_docs.py site` | `13179 local links/assets/anchors checked`, exit 0 |
| `capture_parity.py` before (at `9b069e2` code for extract) and after | 238 models, exits 0: 177, 3: 61; byte-identical; the reviewer re-captured both from a `git archive 9b069e2` tree and the working tree, equal |
| mutation table `evidence/MG4/mutants.json` | M1 to M9 each `KILLED` |
| `uv run ruff check src/gnd/extract tests/test_extract_guidelines.py` | `All checks passed!` |
| anonymity scan over added and changed files | 0 matches |

## Coverage against the branch table

| Branch | Case |
|---|---|
| flag on and off; the other files equal | T1, T1b, T1c; M4, M5 |
| reading, inverse reading, same role players present and absent | T2, T2b; M6 |
| entity identity direct, composite, unmatchable; value types | T2, T2d |
| primitive source equals `resolve_primitive` | T2c |
| every constraint family, inline and top-level, non-anchoring external uniqueness | T3 (four fixtures), R-F2; M1, M8 |
| no value literal or sample row | T3b; M9 |
| heading and delimiter forgery | T4, T4b; M2, M3 |
| index consumers end to end | T6 (fidelity, doccheck, verify); helper direct |
| refused model | T6b |
| cost, value and entity players | T12 (two); M7 |
| O20 documented | T9 |

## Adversarial review

One reviewer is one reviewer:
[phase-MG4-claude-review.md](notes/phase-MG4-claude-review.md), retained
verbatim, probes in `evidence/MG4/review-probes/`. It stripped constraints
from all 172 strippable accepted corpus models (bytes equal), forged with
seven separator and markup shapes, checked determinism across hash seeds,
re-captured parity from `9b069e2`, ran the consumers end to end and the
mutants. Verdict approve-with-fixes, nothing blocking; R-F1 to R-F9 are
dispositioned in the spec (seven fixed with cases or docs, R-F5 documented,
the R-F6 residual cost recorded).

## Refactoring review

**None needed**, argued from what MG4 touched: one new generator over
existing homes (`ModelIndex`, `refscheme`, `verbalize`), one optional
artifact entry in the existing staged write. **Seen and deferred:**
`reference_identity`'s cost with many external uniqueness constraints is
shared with the flag-free verbalization (MG4-Q2).

## Refuted premises

- Plan §2.4 says the guideline is unchanged by every constraint. An anchoring
  external uniqueness is a reference scheme and changes `- Identified by:`
  (spec D2 ruled it reference content; the contract says so).

## Open questions

| ID | Question | Target |
|---|---|---|
| MG4-Q1 | Escape raw HTML in descriptions, or keep "plain text, not rendered" | milestone close |
| MG4-Q2 | `reference_identity` cost with many external uniqueness constraints | milestone close |

## Boundary

- One reviewer is one reviewer. The guideline digest is recorded, not
  verified by any consumer (`(p1)` S).
- A description can restate a rule; the guideline repeats it.
- The broad historical lanes did not run.
- No push, pull request, merge, release, publication or certification is
  claimed by this record.
