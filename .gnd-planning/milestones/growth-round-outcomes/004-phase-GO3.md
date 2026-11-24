---
milestone: growth-round-outcomes
station: "phase-GO3"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-GO3
date: 2026-11-23
gate:
  command: "uv run pytest -q tests/test_go2_operation_outcomes.py tests/test_evolve_additive_policy.py tests/test_evolve_loading.py tests/test_evolve_source_document.py tests/test_evolve_population_check.py tests/test_evolve_shape_matches.py tests/test_mc3_evolution.py tests/test_unattended_model_growth_acceptance.py tests/test_vg2_evolve_sources.py tests/test_vg3_unattended_includes.py tests/test_vg4_seeded_growth_rounds.py tests/test_go1_evolve_parse_once.py tests/test_model_evolution.py tests/test_induced_provenance.py tests/test_unattended_growth_guidance.py tests/test_go3_narrowed_proposal.py tests/test_go5_round_summary.py tests/test_discover.py tests/test_vg5_seeded_growth_example.py --tb=short"
  exit: 0
  output: "936 passed, 1 deselected in 90.96s"
  base: "origin/main fe5fdf72, merged at a30b6192"
gates:
  - {name: "structure and inventory guards (project.md block)", command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py tests/test_rf1_cli_pins.py --tb=line", exit: 1, output: "1 failed, 813 passed, 2 deselected: the one failure is `test_reference_closure_and_declared_bootstrap` reading this machine's git-excluded `.agents/skills/review-pr/SKILL.md`, a partial local sync outside the repository; no tracked file is involved"}
  - {name: "lint, plan form", command: "uv run ruff check src tests tools", exit: 0, output: "All checks passed!"}
  - {name: "lint, whole repository", command: "uv run ruff check", exit: 0, output: "All checks passed!"}
  - {name: "component index", command: "python3 scripts/components_index.py changed --base origin/main --strict", exit: 0, output: "70 file(s) differ; 0 to fix, 0 warning(s), 2 to reread"}
selection:
  - {obligation: "GO3-C1..C4, T1-T6, the seeded-root case and the review regression", disposition: run, command: "the gate above"}
  - {obligation: "broad lanes (evidence, census), report-golden replay, certification", disposition: cadence, note: "not selected: no explicit owner request"}
  - {obligation: "the whole default lane, base against head", disposition: run, note: "beast-3, six shards per tree; evidence/GO2-GO5/full-lane.md"}
evidence:
  - {path: src/gnd/discover/narrow.py, sha256: 7ff233392d67b5348006886c3217b640fcb139a63d6beae147321dfa86e73183}
  - {path: src/gnd/evolve/models.py, sha256: e3cad91c0b36787e266a93fa1a36c78223e5935ad67108fd6b488416f28802be}
  - {path: src/gnd/evolve/__init__.py, sha256: a4714d3a3e6851b7231970e3c0bf74be5c6f6978c51d416aa390b885aafb4a0a}
  - {path: tests/test_go3_narrowed_proposal.py, sha256: eabd52fcd2288af4a2b43121959b2a2dd599178b6b36bb6b28c3c93e3aa8b8bb}
  - {path: src/gnd/skills/gnd-model-evolve/references/evolution-contract.md, sha256: c79f2f1533c0ea005179d5318b1288ea6a0380bf313a8a1210932cfad8bc9d87}
  - {path: .gnd-planning/milestones/growth-round-outcomes/notes/phase-GO3-spec.md, sha256: dace370951dde109693d10bef4eca57d2696632b5b6c8ab20d9f1c5aea1b6f4a}
  - {path: .gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO3-GO5-r1/review.md, sha256: 43bcc1ff8921e15fe53c5dca227280269e124fe1045bdc38a223928f4a08b5df}
  - {path: .gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO3-GO5-r1/FINDINGS.md, sha256: 90461e8095d7f2ce39b51f14720227c1982c5b3e3fab7fd13463aab91fdced8d}
  - {path: .gnd-planning/milestones/growth-round-outcomes/evidence/GO3-GO5/dynamic-query-successor.json, sha256: a14397e5a7558b5349005d3a1bbe761dd943801422e9fd78fd4218cec1522ee2}
---
# Claim

`gnd.discover.narrow.narrow_proposal(proposal, outcomes)` returns a new
proposal of the operations no gate refused (#227): those `admitted` or
`unassessed`, with GO2's `dropped-with` closure re-run over what is kept,
replayed over the outcomes' before model. It has its own `proposal_id`
(`<original>-narrowed`) and `narrowed_from`; a proposal without that field
keeps its bytes and `proposal_sha256`. `apply` stays whole; narrowing writes
nothing.

Authority: plan r4 and spec r1, delegated approval (auto=true), spec §12.
Agent rulings under the owner's delegation, not the owner's reading. Not
merged.

## Named criteria

| Criterion | Result |
|---|---|
| GO3-C1 | T1: from GO2-C1's report, three operations kept; the narrowed proposal previews and applies, exit 0; also from a seeded unattended root with no `documents` key (§13). Gate |
| GO3-C2 | T2: a constraint on a refused fact type is dropped and named `dropped-with`, also when a host's rows mark only the fact type. Gate |
| GO3-C3 | T3: own `proposal_id`, `narrowed_from` set, the original's bytes unchanged; the original preview is refused as today before, and exits 11 (stale) after the narrowed one is applied. Gate |
| GO3-C4 | T4: nothing kept returns `None` and one reason per operation. Gate |

## Review

The review helper (Codex), one round over `b2d67b8e` shared with GO5
(`phase-GO3-GO5-r1`). One reviewer is one reviewer. GO3's finding F1 (rows
trusted by position) was blocking, reproduced and fixed with a regression
test. The budget's second round is not run separately: **the repaired bytes
are read by the milestone's close review, and until then carry no review
opinion.**

## Refactoring review

- Reuses `discover.output.candidate_document` and `candidate_text` (the
  service's own replay) and GO2's closure; no second walk.
- `narrowed_from` is omitted by the proposal's own serializer, which every
  embedding of a proposal (a preview's `proposal`) already uses.

## Implementation findings and deviations

Spec §14: refusal order (types first); `narrowed_from` declared on every
reader; no new counted query rows; homes outside the list
(`src/gnd/evolve/__init__.py`, `tools/gnd_layers.json`, `dev/components/`).

## Boundary -- what this result did NOT establish

- A `gnd evolve narrow` command (D5 (b), out of scope until a host asks).
- That a narrowed preview is admitted: it is previewed like any other.
- No merge, release or publication.
