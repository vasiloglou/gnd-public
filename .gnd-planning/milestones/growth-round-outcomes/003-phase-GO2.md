---
milestone: growth-round-outcomes
station: "phase-GO2"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-GO2
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
  - {obligation: "GO2-C1..C7, T1-T9 and the review regressions", disposition: run, command: "the gate above"}
  - {obligation: "broad lanes (evidence, census), report-golden replay, certification", disposition: cadence, note: "not selected: no explicit owner request"}
  - {obligation: "the whole default lane, base against head", disposition: run, note: "beast-3, six shards per tree; evidence/GO2-GO5/full-lane.md"}
evidence:
  - {path: src/gnd/evolve/outcomes.py, sha256: b41fb7a01f53d9039428fc5fee074dd2e839150dfe38c268755e37bebe400bd8}
  - {path: src/gnd/evolve/service.py, sha256: b9a0df3cfca1deb9806a5300f4479ac5c52935f67632855a2300a042ebc9da5b}
  - {path: src/gnd/evolve/models.py, sha256: e3cad91c0b36787e266a93fa1a36c78223e5935ad67108fd6b488416f28802be}
  - {path: src/gnd/evolve/cli_service.py, sha256: 78be1663446c8df4331179f4306d249a7b53ad34303e7563fa32aa1e58de237f}
  - {path: src/gnd/commands/evolve.py, sha256: 9882d818a31363a0993f0470f010607d985542d9f5cf8d413012431ccfacc69b}
  - {path: src/gnd/skills/gnd-model-evolve/references/evolution-contract.md, sha256: c79f2f1533c0ea005179d5318b1288ea6a0380bf313a8a1210932cfad8bc9d87}
  - {path: tests/test_go2_operation_outcomes.py, sha256: 077cce68655468a9431563bb0afac7d163f0a143848ee0568d00143d81e629ae}
  - {path: .gnd-planning/milestones/growth-round-outcomes/notes/phase-GO2-spec.md, sha256: a5e4b6e3c79c311817d0cb9a4a297207ee4443f51e961f683c3ccb425d220f85}
  - {path: .gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO2-r1/review.md, sha256: 750b243f7ddfe20400a5ab317554e46aef54727dfb4048e058e9c69a33ddd9e9}
  - {path: .gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO2-r1/FINDINGS.md, sha256: 81ffa2c3e7238eb119efa154624e37e0f575febd9f674189245fa27c8defd363}
  - {path: .gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO2-r2/review.md, sha256: f8860ee1136a0a3aaed11b6c6b4df7a0ed09adf12d58ca81e4f66d22e99b990a}
  - {path: .gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO2-r2/FINDINGS.md, sha256: 17b788fa840e386f9a75876012a7ceabfeb55fe72db557b7efe287c7e2fee45f}
  - {path: .gnd-planning/milestones/growth-round-outcomes/evidence/GO2/source-successors.json, sha256: e44f317a5b436def140efb4769d2bff4dd6f19183fee892c50dc9e616eaae194}
  - {path: .gnd-planning/milestones/growth-round-outcomes/evidence/GO2/query-successor.json, sha256: 5236471cdcca24983d0daf18d9aee5cf487606dcd738b70f0b57429b98aba1bf}
  - {path: .gnd-planning/milestones/growth-round-outcomes/evidence/GO2/dynamic-query-successor.json, sha256: 22be8a72405e832944814221d07b3211400a8c1276625030256a0bef5a5b4fb3}
---
# Claim

`gnd evolve preview --operation-outcomes` names an outcome for every
operation of a proposal (#227): `admitted`, `refused-by-policy`,
`refused-by-validation`, `refused-by-d12`, `dropped-with` a refused one, or
`unassessed` with the gates that did not run. A preview that is written
carries the rows in `operation_outcomes`; a refused one writes them, with the
refusal and its exit as printed, to `--outcome-report FILE`. Without the
option every preview, refusal and exit is byte-identical. D-12 collects every
refusal in one walk and still raises the first.

Authority: plan r4, delegated approval (auto=true) in `001-plan-gate.md`;
spec r1 and its r2 amendment, delegated approval (auto=true), spec §12–§13.
Agent rulings under the owner's delegation for this milestone, not the
owner's reading. Ordering: the coordinating session's "GO GO2, GO3, GO4 and
GO5" after VG1–VG5 merged on `main`. Not merged; merge needs the owner.

## Named criteria

| Criterion | Result |
|---|---|
| GO2-C1 | T1: four operations, one refused at a locatable element: no preview, the report names all four, the refusal and exit as without the option. Gate |
| GO2-C2 | T2: one case per verdict word over committed fixtures; two faults in two operations both named. Gate |
| GO2-C3 | T4: without the option, preview bytes, `proposal_sha256` and `preview_sha256` unchanged over the lane's cases. Gate |
| GO2-C4 | T6: a planted secret in constraint values and provenance reaches no row. Gate |
| GO2-C5 | T5: `apply` refuses a report given as its preview, exit 3. Gate |
| GO2-C6 | T7: a preview with rows applies; an edited row exits 11. Gate |
| GO2-C7 | T3: an operation a later gate never reached is `unassessed`, gates named in the preview's order. Gate |

## Review

Instrument: the review helper (Codex, read-only, reasoning high), D8.
**One reviewer is one reviewer; this is not a panel.** Round 1 over
`f7ec03b4`: eight findings, four blocking, all reproduced and fixed in
`9bf8bf3e` with a regression test each (`phase-GO2-r1/FINDINGS.md`). Round 2
over `9bf8bf3e`, the budget's last: five findings, three blocking, all
reproduced and fixed with a regression test each
(`phase-GO2-r2/FINDINGS.md`). The round-2 repairs were then read by the
GO3–GO5 round (`phase-GO3-GO5-r1`), whose reviewer reports they held; that
round's own repairs touch no GO2 file. Logs were sanitized for machine paths.

## Refactoring review

- One locator module (`gnd.evolve.outcomes`) holds the outcome walk; the
  service only stages it. The verdict words have one home, the evolution
  contract's "Operation outcomes".
- The dependency walk follows the ORM meta-schema (`gnd.model._load_meta_schema`,
  the reader validation already uses) instead of a list of shapes; issue
  paths are read by the validator's own path grammar, which `_PATH_HEAD`
  states whole.
- `_d12_refusals` replaces `_enforce_d12`'s body; `_enforce_d12` raises its
  first refusal, so no second D-12 walk exists.

## Implementation findings and deviations

Spec §14: pinned handlers recorded as RF5 successors; the RF1 reference
parser gains the two options; the counted roles read and the dynamic rows
are recorded in `evidence/GO2/`; the gate order follows the code; D-12
fixtures; the three rules the reviews changed (a whole-proposal closure, a
schema-guided walk, an issue located only on one unambiguous operation).

## Boundary -- what this result did NOT establish

- That every validation issue is located: an issue two operations could have
  caused leaves its row `unassessed` by design.
- Repairs after round 2 that touch GO2 files: none. No merge, release or
  publication.
