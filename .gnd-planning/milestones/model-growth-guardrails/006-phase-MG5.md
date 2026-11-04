---
milestone: model-growth-guardrails
station: "phase-MG5"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-MG5
date: 2026-11-04
gate:
  command: "uv run pytest -q tests/test_unattended_mode.py tests/test_schema_sync.py tests/test_rf1_cli_pins.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py tests/test_model_validation.py tests/test_model_v2.py tests/test_induced_provenance.py tests/test_rf1_pin_harness.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_skill_prose_sync.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_public_api.py tests/test_rf3_core.py tests/test_rf4_peripheral.py tests/test_public_built_inventory.py tests/test_atom_bind.py tests/test_checker_families.py tests/test_codegen_identifiers.py tests/test_derivation_rule.py tests/test_model_guarded.py tests/test_object_type_description.py tests/test_public_aggregate_surface_corpus_controls.py tests/test_public_distribution.py tests/test_public_distribution_runtime.py tests/test_public_float_corpus_guards.py tests/test_public_phase4_transition_support.py tests/test_public_transition_review_controls.py tests/test_reference_population_corpus.py tests/test_rf1_semantic_pins.py tests/test_synth_oracle_value_range.py tests/test_v71_phase1_dates.py tests/test_verification_fixes.py tests/test_m3_population_schema.py tests/test_popvalidate.py tests/test_public_admission_schema_mutations.py tests/test_public_alias_schema_guards.py tests/test_v62_phase1_validation.py tests/test_v62_phase2_validation.py tests/test_v62_phase3_validation.py tests/test_v62_phase4_validation.py tests/test_v62_phase5_validation.py tests/test_v62_phase6_validation.py"
  exit: 0
  output: "3006 passed, 57 deselected in 243.03s (0:04:03)"
  note: >-
    The plan's section 9 MG5 row (test_model_semantic and
    test_imported_provenance do not exist) and the impact closure: every test
    file that loads the schema, the validation suites and the pins. Run after
    the review fixes. 57 deselected by the default lane filter.
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "outside MG5's impact closure; the corpus parity table covers every model file"
evidence:
  - path: .gnd-planning/milestones/model-growth-guardrails/notes/phase-MG5-spec.md
    sha256: 994b7e39efa05e9301a254006dc3a5ca3f1e93df213cd844a299a6a9af9cd7a4
  - path: .gnd-planning/milestones/model-growth-guardrails/notes/phase-MG5-claude-review.md
    sha256: 7322ae53ea9f1f626f80173b5b7c182d14aaaf408a8f97981d613adcc9ab2c38
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/MG5/capture_parity.py
    sha256: 82935b7f10b77ecf543a05a7d32e3fdc691f4ba34328750496003627aa5392d2
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/MG5/parity-before.json
    sha256: 66da798888d03c49aeef866eda7a9eca09c30dbab78e62ce353d701f6ee68983
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/MG5/parity-after.json
    sha256: bde9366ba6b0aaa11d52d84f0981ec522a59434e251253be9da3f16b408cd16b
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/MG5/dynamic-query-successor.json
    sha256: 134d2e725ebf21872d139f03bb888d11047630808746f68798f520605b6d89f3
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/MG5/mutants.json
    sha256: 365e04a28f2f714e38ac99b79e1b72c38277013612dff5025127e572e019e78f
  - path: src/gnd/model/_validation.py
    sha256: 58b3c4e86a41f1f92ba666a44ddcd0bdd1f8c9a3c9737c610b2026dbf4291771
  - path: src/gnd/commands/checking.py
    sha256: 2e74fee2d0ed2a8ab659fca85c2794bb766fb2c27ac8c332c861ee3b74824183
  - path: src/gnd/schema/orm-meta.schema.json
    sha256: eb626252f7eaf5ce8dc2580b9b387289a46d66da923358d2a4fcbb4a81292353
  - path: tests/test_unattended_mode.py
    sha256: c3c0b3afc440e5250dfac14cd210daca0814a0aeeb30a1feac236c9ce8b2f92f
  - path: tests/fixtures/unattended/conforming.orm.yaml
    sha256: 1b96aab4972c55968bedd31a9bb2d2c2ed6ec754e1df702a0bb064ce5216a38b
  - path: tests/fixtures/unattended/source.txt
    sha256: 6cec7fe354bc7c620fccfeece167c43dec11096669d934a54ce5ef8fffd155e8
  - path: src/gnd/skills/gnd-orm-core/references/representation-format.md
    sha256: 5f2a7ceed77bab19d5122f1ca50e9f055a57919e9be73d764d19d7d75848a5ef
  - path: src/gnd/skills/gnd-model-from-text/SKILL.md
    sha256: bae9a1e3d581b9f4ff65624bd65246274f09c28d22ba8c2dfe207c9927a842b8
---

# Phase MG5: unattended model-from-text

**Claim.** A model whose `source.mode` is `unattended` is refused by `gnd
validate` (exit 3, `semantic:unattended-u1` … `-u8`) when it lacks the
no-reviewer header and declared documents, marks anything `confirmed` or
`explicit`/`user-supplied`, leaves an element, a non-common-sense
constraint or a sample row without a well-formed span of a declared
document, or claims an unreviewed constraint `alethic`. `gnd validate
--document DOC` re-hashes the spans in code points of the NFC text and
exits 3 on an undeclared document, an out-of-range span or a different
excerpt. Every one of the 322 corpus models validates with byte-identical
output to `9b069e2`. The focused gate exits 0.

**Authority.** Plan r3 `(a1)`. Spec r1 under **delegated approval
(auto=true)** `(d1)` 2026-11-04 over SHA-256
`91d2657027800db1d64c41a72cc28b9d353936cfda6a12af2e118105f165e566`; an agent
ruling under the owner's "process-milestone model-growth-guardrails auto",
not the owner's reading. Issue #74.

## What shipped

- `_rule_unattended` and `unattended_span_issues` in `gnd.model._validation`,
  appended last to `_SEMANTIC_RULES`; one walk, rule ids passed explicitly.
- `$defs.source_span` in both schema copies; `spans` on the closed induced
  provenance (D3, the MG-R1 exception below).
- `gnd validate --document PATH` (repeatable), with the model's warnings
  kept on a refusal and the 10 MiB cap applied before hashing.
- Fixture `tests/fixtures/unattended/` and `tests/test_unattended_mode.py`
  (87 cases); eleven mutants, all killed.
- Pins: `gnd validate` RF1 goldens, `tree.json`, manifest; the semantic-rule
  inventory pin; the skill link count; one RF6 dynamic successor.
- Docs: "Unattended source" in `representation-format.md` (normative) and
  eight Layer 2 rows; the skill's Unattended mode; CLI row; Unreleased note.

## Gate and other commands

| Command | Result |
|---|---|
| focused gate (front matter) | `3006 passed, 57 deselected in 243.03s (0:04:03)`, exit 0 |
| `uv run python tools/run_tutorials.py` | `257 tutorial blocks passed`, exit 0 |
| `uv run --group docs zensical build --strict` | `Build finished in 0.51s`, no issues |
| `uv run python tools/check_docs.py site` | `13181 local links/assets/anchors checked`, exit 0 |
| `capture_parity.py` at `9b069e2` and after | 322 shared models identical; one new row, the conforming fixture, exit 0; the reviewer reproduced 0 differences from a `git archive 9b069e2` tree |
| mutation tables MG3, MG4, MG5 with `PYTHONDONTWRITEBYTECODE=1` | every mutant `KILLED` (10, 9, 11) |
| ruff over the changed source and tests | `All checks passed!` |
| anonymity scan over added and changed files | 0 matches |

## Coverage against the branch table

| Branch | Case |
|---|---|
| U1 five branches, U2 constraint and operation, U3 two sources, U4 two element kinds, U5 four sources, U6 two plus row identity, U7 three, U8 four | T2 (21 parametrized), the direct-call test, R-F1, R-F5, R-F6 |
| each edit without the mode, exit and ids | T2b, R-F13; M1 |
| conforming model 0; common-sense pre-empted at layer 1 | T2c, T2e; M4 |
| hostile shapes | T2d |
| `--document`: match, mismatch, out of range, undeclared, bytes against code points, NFD, missing, no mode, text, cap, warnings kept | T3 (nine), R-F3, R-F4; M2, M6, M11 |
| no document text in output | T5 |
| cost | T10 |

## Adversarial review

One reviewer is one reviewer:
[phase-MG5-claude-review.md](notes/phase-MG5-claude-review.md), retained
verbatim; probes in `evidence/MG5/review-probes/`. Verdict approve-with-fixes,
nothing blocking; fourteen findings dispositioned in the spec: nine fixed with
cases or docs, R-F2 and R-F14 accepted with reasons, R-F7, R-F10 and R-F11
recorded as MG5-Q1 to Q3.

## Refactoring review

**None needed**, argued from what MG5 touched: one rule family appended to the
existing registry, using the existing provenance walk and the anchors' text
normalization rather than a copy; one CLI option beside the existing
validate path.

## Refuted premises

- §2.5's "without `mode: unattended`, validation is unchanged" holds for
  every corpus model but not for every possible model: `spans` on induced
  provenance is now admitted in any mode (R-F2, the one MG-R1 exception).
- The plan's corpus counts (112 with `source.mode`, 16 one-shot confirmed)
  were re-measured as 349 files and 163 (spec `(d1)`).

## Open questions

| ID | Question | Target |
|---|---|---|
| MG5-Q1 | `--document` re-hash cost per full-length span | milestone close |
| MG5-Q2 | Schema for the unattended `source` keys | milestone close |
| MG5-Q3 | Count spans over declared but unsupplied documents | milestone close |

## Boundary

- One reviewer is one reviewer. GND validates the model; the host runs the LLM.
- Spans prove that an excerpt exists, not that it supports the claim.
- The broad historical lanes did not run.
- No push, pull request, merge, release, publication or certification is
  claimed by this record.
