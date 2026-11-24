---
milestone: growth-round-outcomes
station: "phase-GO4"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-GO4
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
  - {obligation: "GO4-C1..C3, T1-T3 and the review regressions", disposition: run, command: "the gate above"}
  - {obligation: "broad lanes (evidence, census), report-golden replay, certification", disposition: cadence, note: "not selected: no explicit owner request"}
  - {obligation: "the whole default lane, base against head", disposition: run, note: "beast-3, six shards per tree; evidence/GO2-GO5/full-lane.md"}
evidence:
  - {path: src/gnd/skills/gnd-model-from-text/references/unattended-growth.md, sha256: 396bf5ef138218ea41ffc1ce768759a441943a45ad575a7160e88616a9eea630}
  - {path: tests/test_unattended_growth_guidance.py, sha256: 36a0ff643678b2c7dc9b15526ad2452ebc6dbd35068e599dbe6eb6a531da82f5}
  - {path: tests/support/markdown_sections.py, sha256: 665f1e2d3d6980b656c64a34b09328d25eeb7037bcc3e155aa084dfecf35ac18}
  - {path: .gnd-planning/milestones/growth-round-outcomes/notes/phase-GO4-spec.md, sha256: cb5649d8c330b0c42a950394f5785236d0ca9d294fccefb26da99bfbf1950b50}
  - {path: .gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO4-r1/review.md, sha256: 69f5848fa92183fb80d2f6bec971288d4e667d57eb9c0272dc17afa8c1b56751}
  - {path: .gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO4-r1/FINDINGS.md, sha256: 78da75496e2452928f01413503e80270aae667d4c23a1c7c37b99f4c138b8814}
---
# Claim

"The reply shape" in `unattended-growth.md` says a reply names an element
the model already has, its own or included, by id only and never repeats it,
and routes rows for an existing fact type to `open_questions`, since the
additive policy refuses a changed sample row (#227). The example reuses
`party` and `policy_has_holder`. "Acting on a shape match" now says the same
for a reused fact type. A guard fails when any of those statements is
reversed, deleted, narrowed or hidden.

Authority: plan r4, spec r1 and its r2 amendment, delegated approval
(auto=true). Agent rulings, not the owner's reading. Not merged.

## Named criteria

| Criterion | Result |
|---|---|
| GO4-C1 | T1: the prose, the element row, the rows row and the shape-match bullet state the rule as whole sentences; the example names a reused host. Gate |
| GO4-C2 | T2: eleven edits (removal, reversal, the old wording, a narrowed qualification, the shape-match bullet) each fail the guard, a no-op control passes; an HTML comment, inline or not, hides a rule; equivalent Markdown reads the same. Gate |
| GO4-C3 | T3: neither packaged growth example adds an element its before-model has or changes one. Gate |

## Review

The review helper (Codex): round 1 over `038f64dc` (`phase-GO4-r1`), three
findings, all reproduced and fixed; F1 and F3 blocking. The GO3–GO5 round
then read those repairs and found two more in the shared Markdown reader
(an inline comment, a tab-closed heading), both fixed with tests. One
reviewer is one reviewer. **The last repairs carry no review opinion until
the close review.**

## Refactoring review

- The guard reads Markdown through the repository's reader,
  `tests/support/markdown_sections.py`, which gains a block reader beside
  its section reader; no new string-split matcher.

## Implementation findings and deviations

Spec §14 records the refuted D3(a) premise and the amendment. A
contradiction the review found ("write its facts against the existing one")
is repaired on the page; the plan's GO4 home list covers it.

## Boundary -- what this result did NOT establish

- That a host's LLM follows the page: the guard checks the page, not replies.
- No merge, release or publication.
