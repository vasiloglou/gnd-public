---
milestone: growth-round-outcomes
station: "phase-GO5"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-GO5
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
  - {obligation: "GO5-C1..C4, T1-T8, the command and the review regressions", disposition: run, command: "the gate above"}
  - {obligation: "broad lanes (evidence, census), report-golden replay, certification", disposition: cadence, note: "not selected: no explicit owner request"}
  - {obligation: "the whole default lane, base against head", disposition: run, note: "beast-3, six shards per tree; evidence/GO2-GO5/full-lane.md"}
evidence:
  - {path: src/gnd/evolve/summary.py, sha256: 19320c73a85ddc3d9761613cc270bf033f08181a0bf07a82901834e407e97789}
  - {path: src/gnd/evolve/cli_service.py, sha256: 78be1663446c8df4331179f4306d249a7b53ad34303e7563fa32aa1e58de237f}
  - {path: src/gnd/commands/evolve.py, sha256: 9882d818a31363a0993f0470f010607d985542d9f5cf8d413012431ccfacc69b}
  - {path: src/gnd/disclosure.py, sha256: 2068729ead18c619e45d25ef404be0ea5701263b93bbaf9df2502459fe77e331}
  - {path: tests/test_go5_round_summary.py, sha256: b102883704febd096c64571e562e1e15dfa6637a1b8ad03c9d6b2a6d5e1795ab}
  - {path: tests/fixtures/round-summary/README.md, sha256: a458083a1c7aceabf3a045e27b4d11ac9c1899ef8e815c353fb2f016c8843b26}
  - {path: tests/fixtures/round-summary/known-mix.round.json, sha256: ff7b4c2b4c5c59c7343a4e0e24f9b0351b4a235f459d9692d5a0b552c10c1605}
  - {path: tests/fixtures/round-summary/known-mix.expected.json, sha256: cf36bc939a39d49369074ac3f5b1e7c3c38a1265ed3ffc60feb3d766d3f765c5}
  - {path: tests/test_rf1_cli_pins.py, sha256: f59d3ec3f91dae6661bc06f2b78e795c89310cb64bb341c93e60893cc7654f8b}
  - {path: src/gnd/skills/gnd-model-evolve/references/evolution-contract.md, sha256: c79f2f1533c0ea005179d5318b1288ea6a0380bf313a8a1210932cfad8bc9d87}
  - {path: .gnd-planning/milestones/growth-round-outcomes/notes/phase-GO5-spec.md, sha256: c351b1eaf4ba6cf0f091f0fece582447fee2d3e09e2dcedec19f83f05e3b0431}
  - {path: .gnd-planning/milestones/growth-round-outcomes/notes/issue-replies.md, sha256: 67f110fd470d4626ba884062edfb0819822272c2feace217149631de66de11d1}
  - {path: .gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO3-GO5-r1/review.md, sha256: 43bcc1ff8921e15fe53c5dca227280269e124fe1045bdc38a223928f4a08b5df}
  - {path: .gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO3-GO5-r1/FINDINGS.md, sha256: 90461e8095d7f2ce39b51f14720227c1982c5b3e3fab7fd13463aab91fdced8d}
---
# Claim

`gnd evolve summary ROUND_FILE [--proposal P] [--preview V | --outcome-report R] [--record D]`
prints one `gnd-round-summary/1` document per growth round (#227, #228): what
it reused, what the host dropped and why (verbatim), the operations proposed
by kind and collection, each verdict's count, the shape matches, and the
elements the applied record added. Each artifact must bind the one before
it, and the outcome rows must be the proposal's operations. It writes no
file; `apply` is unchanged.

Authority: plan r4 and spec r1, delegated approval (auto=true), spec §12.
Agent rulings, not the owner's reading. Not merged.

## Named criteria

| Criterion | Result |
|---|---|
| GO5-C1 | T1: three rounds of the acceptance replay, `proposed.total` equals the sum of outcomes and `added` equals the applied operations. T2: the committed known-mix round gives the README's counts. **Partly refuted** (spec §13.1): `dropped-with` cannot share a written preview with a shape match, so it is counted in its own case over an outcome report. Gate |
| GO5-C1b | T3: previewed and not applied adds nothing; a narrowed-then-applied round reports the narrowed additions and `narrowed_from`. Gate |
| GO5-C2 | T4: an empty round and a round listing reused ids differ; the empty one is zero in every count. Gate |
| GO5-C3 | T5: host drops under `host_drops`, verbatim; T6: hostile round files and unbound artifacts refused by name. Gate |
| GO5-C4 | `notes/issue-replies.md` drafts both replies; the owner posts them |

## Review

The review helper (Codex), one round over `b2d67b8e` shared with GO3
(`phase-GO3-GO5-r1`). GO5's findings F2 (blocking: incomplete outcomes
counted), F4 (bindings), F5 (host text stripped) were reproduced and fixed
with tests. One reviewer is one reviewer. **The repaired bytes carry no
review opinion until the close review.**

## Refactoring review

- Reads every artifact through the evolve readers and the bounded strict JSON
  reader (`gnd.input_policy`); one closed model per document.
- The command lives with the other `gnd evolve` subcommands; the module is
  registered in the layer map, the component index and the disclosure table
  (`value-free`).

## Implementation findings and deviations

Spec §13: T2's mix is not one round (refuted premise, a plan repair at
close); a preview and a report are exclusive; `added.constraints` by
operation id; the RF1 successor and the parser count (65).

## Boundary -- what this result did NOT establish

- A summary across rounds, or any judgment of the host's reasons.
- The replies are drafts; nothing is posted. No merge, release or publication.
