---
milestone: literature-depth
station: milestone-close
scope: milestone-close
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
date: 2026-11-16
gates:
  - command: "uv run --no-sync pytest -q tests/test_ld1_competency_examples.py tests/test_ld2_quantities.py tests/test_ld3_reading_workflow.py tests/test_lx1_flattening.py tests/test_lx4_literature_interop.py --tb=short"
    exit: 0
    output: "149 passed in 162.96s (0:02:42)"
  - command: "uv run --no-sync pytest -q tests/test_ld5_verdict.py tests/test_ld4_revision.py tests/test_li4_assertions.py tests/test_li5_lineage.py tests/test_witness_composition.py tests/test_rule_edition_comparison.py --tb=short"
    exit: 0
    output: "106 passed in 413.64s (0:06:53)"
  - command: "uv run --no-sync pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
    output: "679 passed, 2 deselected in 326.04s (0:05:26)"
  - command: ".venv/bin/ruff check --output-format=json"
    exit: 1
    output: "188 exact inherited diagnostics; changed Python files pass"
  - command: "python3 scripts/components_index.py changed --base 4e0b542f --strict"
    exit: 0
    output: "0 to fix, 0 warning(s), 0 to reread"
  - command: "python -m gnd.examples.literature.verdict replay release verdict"
    exit: 0
    output: "verified all five installed outcomes and exact report bytes"
  - command: "python -m gnd.examples.literature.reading run --out reading"
    exit: 0
    output: "five producer calls"
  - command: "python -m gnd.examples.literature.reading replay reading"
    exit: 0
    output: "zero producer calls; same reading-manifest digest"
  - command: "python -m gnd.examples.literature.revision run reading --out release"
    exit: 0
    output: "five prior queries, two current; migration worklist equals LD3"
  - command: "python -m gnd.examples.literature.revision status release/after"
    exit: 0
    output: "current"
  - command: "python -m gnd.examples.literature.revision replay release"
    exit: 0
    output: "byte-identical revision report"
  - command: "python -m gnd.examples.literature.revision replay release --snapshot before"
    exit: 0
    output: "original witness digest matches"
  - command: "python -m pytest -q 'tests/test_evolve_loading.py::test_h3_every_homes_outcome_is_unchanged[replay/changed]' 'tests/test_evolve_loading.py::test_h3_every_homes_outcome_is_unchanged[witness/changed]' --tb=short"
    exit: 1
    output: "2 failed in 1.72s"
  - command: "uv run --no-sync pytest -q 'tests/test_evolve_loading.py::test_h3_every_homes_outcome_is_unchanged[replay/changed]' 'tests/test_evolve_loading.py::test_h3_every_homes_outcome_is_unchanged[witness/changed]' --tb=short"
    exit: 1
    output: "2 failed in 1.28s"
  - command: "uv run --no-sync pytest -q -p no:cacheprovider tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap --tb=short"
    exit: 0
    output: "1 passed in 1.71s"
  - command: "UV_NO_SYNC=1 uv run python tools/run_gnd_review_panel.py .gnd-planning/milestones/literature-depth/evidence/close-request.json --out <scratch>/panel-run --reviewer-timeout 600 --overall-timeout 900"
    exit: 0
    output: "quorum established with 5 valid responses and matching before/after artifact digests"
  - command: "uv run --no-sync gnd review finalize <scratch>/panel-run <scratch>/synthesis.json --out <scratch>/PANEL-REVIEW.md"
    exit: 0
    output: "5 agreed groups, 12 divergent concerns, 5 prioritized fixes"
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/literature-depth/notes/literature-depth-plan.md sha256 216c7af0576a65a5fcb785773d34449c0e6ce0ce05ab022a21a43e5607d20539"
    exit: n/a -- ruling
    output: "accepted in-scope milestone"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: explicit owner or CI selection
  reason: the recorded focused and installed checks cover the scoped worked examples and compatibility
evidence:
  - path: .gnd-planning/milestones/literature-depth/014-close-candidate.md
    sha256: f18a4fb1d4ea9b5d1ff39e0d9e4fd9305992d3d0e3724200faeb0db46978a2dc
  - path: .gnd-planning/milestones/literature-depth/evidence/close-request.json
    sha256: 0278e18014cf39752243b3358c86d4ff9e95b6963364424eb36ef31a61e06d7d
  - path: .gnd-planning/milestones/literature-depth/evidence/close/PANEL-REVIEW.md
    sha256: 35a356340a76dade4d18074f49b166a38852f2900b77671cc58c7d5b3eddeb9c
  - path: .gnd-planning/milestones/literature-depth/evidence/close/summary.json
    sha256: 11891313e91769dc1edd1dc0567a84c4b0f465d67cfbd01c942e96c73724e6cb
  - path: .gnd-planning/milestones/literature-depth/evidence/close/synthesis.json
    sha256: da5d542b0691d314773826b3963098583703897f7ea80fa63c51fe6a18b94a9b
  - path: .gnd-planning/milestones/literature-depth/evidence/close/dispositions.md
    sha256: 2feaa6b16541bace71d5ee9a4fc393407d060475add4b3bc956fd55f82f8458f
  - path: .gnd-planning/milestones/literature-depth/015-panel.md
    sha256: b7b27800946777e82cde15d97a58a523c27c0a11c6b6e42b30de191dca18dcfd
  - path: .gnd-planning/milestones/literature-depth/notes/literature-depth-plan.md
    sha256: 216c7af0576a65a5fcb785773d34449c0e6ce0ce05ab022a21a43e5607d20539
  - path: .gnd-planning/milestones/literature-depth/002-plan-gate.md
    sha256: 74dcb67460626f7d7e5a5a39b8659b37aee5f73d2905fd69d16dceb597393d75
  - path: .gnd-planning/milestones/literature-depth/004-phase-LD1.md
    sha256: 5a226ac70ee45cdd4893d6cc4d1ea505aeb9b76a04049dbc1b61382f71bafc69
  - path: .gnd-planning/milestones/literature-depth/006-phase-LD2.md
    sha256: 58004fd9ba0a6f4f1d220cb67f48f49e694c5cb6a58d5eb2fede3a7b092b1308
  - path: .gnd-planning/milestones/literature-depth/009-phase-LD3.md
    sha256: 3637fe884e8a8e08eccb1c0538ed87152d840e5ad0c1b83d0f85cd13b064a9b4
  - path: .gnd-planning/milestones/literature-depth/011-phase-LD4.md
    sha256: e108270204a5e5817e98c14b720f9a9a5aa835816a33e6c365553c6bebe48a75
  - path: .gnd-planning/milestones/literature-depth/013-phase-LD5.md
    sha256: 2e7e133a1addf96a1e017009c450a27aee561dbb923af17a08052b8e7081eac9
  - path: .gnd-planning/milestones/literature-depth/notes/close-delta.md
    sha256: 9808af22be382daeac3e06ca3fc9d59e4e4afb778288038cb690ebf1b9eceb18
  - path: .gnd-planning/milestones/literature-depth/evidence/close-observation.json
    sha256: de420000ce13f0c346e963a39d52a5ecdf9da2b845599148e6207402f116baec
  - path: .gnd-planning/milestones/literature-depth/evidence/close/verification-supplement.json
    sha256: 6ff8efb913b85627a6b290e1916623f90e53e98acfc5088319b1ec8313bf4923
  - path: .gnd-planning/milestones/literature-depth/008-phase-LD3-amendment.md
    sha256: bc8e5de8ea6a156f17813b0c979a9628bd9b3421188f74bd3d904aa137818653
  - path: .gnd-planning/milestones/literature-depth/notes/phase-LD5-amendment.md
    sha256: d6fb86e1f3a9843fe18031c53c3e511405958ebeee1630e93eb480e69de90cfb
  - path: .gnd-planning/milestones/literature-depth/notes/phase-LD1-spec.md
    sha256: 96dcbfc91632d226c9f86897699e496155d9831b1ac7af9f1f7c8d20b469dee0
  - path: .gnd-planning/milestones/literature-depth/notes/phase-LD2-spec.md
    sha256: 2f2e8e9679dd1c0db9c1952e6fa0cf540fa74d24255501649837630d5f22cadf
  - path: .gnd-planning/milestones/literature-depth/notes/phase-LD3-spec.md
    sha256: b8cc9faac8b28cc2b6bea9c63696e1261685cb7200ff36001c775a603ee3f8d2
  - path: .gnd-planning/milestones/literature-depth/notes/phase-LD4-spec.md
    sha256: 9cd15da06777a3d5edf63302a9313249c07089159319fbbc7f7a5a9d21dfcf3b
  - path: .gnd-planning/milestones/literature-depth/notes/phase-LD5-spec.md
    sha256: a7d17a5ad2369f796c0261aa29ca9b315c9ac8119ef7ccc8b29326d5de7d6616
---

# Literature depth milestone close

The delegated ruling closes LD1–LD5 for issue #193 parts 6–8 on the topic
branch for [draft PR #203](https://github.com/vasiloglou/gnd-public/pull/203).

## Ruling

ruling: delegated (auto=true) approved .gnd-planning/milestones/literature-depth/notes/literature-depth-plan.md sha256 216c7af0576a65a5fcb785773d34449c0e6ce0ce05ab022a21a43e5607d20539

The owner's `process-milestone literature-depth auto` invocation delegated
the close decision. The owner separately authorized one standard close
panel at `5efffe84`. Its [advisory results](015-panel.md) satisfy the
four-response gate. The ruling binds the verified code, its documented
fixture scope and the exact evidence above. It adopts the final phase specification digests in the
[verification supplement](evidence/close/verification-supplement.json).
Those digests preserve the distinction from the original phase gates.

## Exit evidence

| Phase | Verified outcome |
|---|---|
| [LD1](004-phase-LD1.md) | Three runnable source-bound examples answer twelve scoped questions with positive evidence or explicit unknowns. The re-pinned swapped-citation control refuses. Measured numeric and comparability controls record their outcomes. |
| [LD2](006-phase-LD2.md) | Compatible time spans check at whole-femtosecond resolution. Public witness and replay establish the exact stepped value `0.002 ps`. The tuple `[2, 3, "ps"]` carries coefficient, decimal scale and unit. The existing percent route covers the selected percentage-point distinction. |
| [LD3](009-phase-LD3.md) | Six authenticated reading stages retain five observed producer calls. Replay has zero calls. Two of two qualifying positive matches allow the exact scoped absence. One of two withholds it. The controls cover required completion, evidence exhaustion, budget exhaustion and exact question inventory. |
| [LD4](011-phase-LD4.md) | The earlier snapshot replays independently. The whale sense split removes three false paths and preserves two valid ones. Either synthetic source certificate can replay after the peer source is removed. The migration and reading worklists agree on `study-opening` for the `method-family` edit. |
| [LD5](013-phase-LD5.md) | Two approved supports back the selected claim. One survives an independent rejection. Both verified rejections yield the unsupported result. A changed definition invalidates the old opinions, and a distinct current review and witness restore one support. |

The [integration evidence](evidence/close-observation.json) binds fresh
installed runs and the exact earlier-phase test, verdict and structural
selections. The [panel dispositions](evidence/close/dispositions.md)
record every concern and its treatment. The panel's opinions apply to
the packet and exact review-time bytes. The phase review findings apply
to their recorded original diffs. Repaired behavior is measured by the
local regressions and installed runs.

## Open questions

| Question | Disposition |
|---|---|
| Quantity, reading and revision handoffs | Resolved in LD2 through LD5. The phase records name the measurements and source conditions. |
| Revisit premise from LD3 | The earlier [amendment](008-phase-LD3-amendment.md) retains the original expected answer. The verified revisit only includes a previously inspected relevant section. The canonical plan's older-section criterion covers this correction. |
| LD5 claim and model pins | The [LD5 amendment](notes/phase-LD5-amendment.md) preserves the original opinion values and outcomes. The repaired fixture verifies the claim separately from its support list and binds the original or evolved model. |
| Ruff and changed-reference expectations | Repository maintenance retains the exact 188 diagnostics and both changed-reference failures reproduced at the milestone base and close head. The [verification supplement](evidence/close/verification-supplement.json) identifies the nodes and results. |
| Historical measure output byte pin | Carry `test_rf2_pre_move_pins.py::test_measure_output_bytes` to test-fixture maintenance. LD2's independent reviewer reproduced it at its phase base. |
| Review-helper positional prompt separator | Carry to the dev-tools maintainer at the next review-helper sync. |
| Host-scale reading and extraction | Carry to the existing literature-identity follow-up for a separately selected corpus and provider budget. |
| Issue #193 part 10 | Deferred to a future owner-selected milestone. |

## Boundary

The offline examples exercise named source or synthetic fixtures. The
scope includes the documented public compatibility routes and default
test lanes. The PR remains draft and its merge decision is separate.
