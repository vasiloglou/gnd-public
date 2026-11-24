---
milestone: reviewed-vocabulary-growth
station: "milestone close"
skill: process-milestone
scope: milestone-close
date: 2026-11-23
gates:
  - command: "uv run pytest -q tests/test_vg1_object_type_scaling.py tests/test_reference_universe.py tests/test_subtype_universe.py tests/test_public_semantic_adapter.py tests/test_tp1_index_scope.py tests/test_ir1_judgments_includes.py tests/test_rf1_semantic_pins.py tests/test_vg2_evolve_sources.py tests/test_evolve_additive_policy.py tests/test_evolve_loading.py tests/test_unattended_growth_guidance.py tests/test_unattended_mode.py tests/test_induced_provenance.py tests/test_vg3_unattended_includes.py tests/test_unattended_span_coverage.py tests/test_mc1_model_includes.py tests/test_mc1_guards.py tests/test_include_root_close.py tests/test_vg4_seeded_growth_rounds.py tests/test_mc3_evolution.py tests/test_evolve_source_document.py tests/test_evolve_population_check.py tests/test_unattended_model_growth_acceptance.py tests/test_vg5_seeded_growth_example.py tests/test_growth_example.py tests/test_mc3_source_observations.py --tb=line -rf"
    exit: 0
  - command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py tests/test_release_text.py tests/test_gate_guard_list.py --tb=line"
    exit: 0
  - command: "uv run ruff check src tests tools"
    exit: 0
  - command: "uv run ruff check"
    exit: 0
  - command: "python3 scripts/components_index.py changed --base origin/main --strict"
    exit: 0
  - command: "uv run python tools/run_gnd_review_panel.py --light .gnd-planning/milestones/reviewed-vocabulary-growth/evidence/close-review/review-request.json --out panel-run --effort high --reviewer-timeout 600 --overall-timeout 900"
    exit: 0
  - command: "uv run gnd review finalize panel-run .gnd-planning/milestones/reviewed-vocabulary-growth/evidence/close-review/synthesis.json --out .gnd-planning/milestones/reviewed-vocabulary-growth/evidence/close-review/PANEL-REVIEW.md"
    exit: 0
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviewed-vocabulary-growth-plan.md sha256 6e4ce43013d7b337a3f8e14369f376225ea36b20790153fc914ff86d61340773"
    exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviewed-vocabulary-growth-plan.md
    sha256: 6e4ce43013d7b337a3f8e14369f376225ea36b20790153fc914ff86d61340773
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/001-plan-gate.md
    sha256: a32f3757b3bbe593648f3861b93100edef219e44f77a20ba1f7fbeaea0796c51
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/002-phase-VG1.md
    sha256: e034c1380f95c72f51d4e6d6b6aa680866a2616954d6f09a41605a5fb00cb6dd
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/003-phase-VG3.md
    sha256: b8ad9cf7578fd96954143e90eb4bdf9c60edfc5179526152edcf4e046f9cfd2b
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/004-phase-VG2.md
    sha256: cb744e8014b69497aed2d947c5fcf974641a37796d066013a67f55f08b04b0b0
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/005-phase-VG4.md
    sha256: c70a1c5d3fcec4c0c48e2ea41cd91e3df1a325f1a48986c8f1dffdfd353c35b3
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/006-phase-VG5.md
    sha256: f059905ff5ba067505c2cde56d1b4366cdbd139813a9af2df3ef116e9576470e
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/notes/close-results.md
    sha256: 5935e4b7f7b8542e5ecdf521c38dbbcb5f346507d31c71cad44344006592e8c3
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/notes/close-delta.md
    sha256: a016c1138c71c7d86209995c2fbf77142cfb718a4ebf1e35880eee0312876dfe
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/notes/issue-replies.md
    sha256: 972f2af3dd59fe786220296a247569ab72237510085a9fcf83ae72f2ba612044
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/evidence/close-review/PANEL-REVIEW.md
    sha256: d17901e41a413274d1459fce8f555c5d16d58178b6d109b731fa4ad546c22371
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/evidence/close-review/disposition.md
    sha256: 42c0e133d895451cdb16b7b9683fc095aff4433d1fb77d8e63adb3f7242a624d
---

# Claim

All five mandatory phases of reviewed-vocabulary-growth have their records
and green gates and are on `main` (pull request 239 as `7952ee9e`, pull
request 240 as `8fea6da5`). The milestone's exit gates exited 0 on `main` at
`f7fad6a1` (union lane 1365 passed; guard block 715 passed; ruff over `src
tests tools` and over the whole repository; component index), and the
panel-light close review exited 0 with four of six seats, no agreed concern
and no blocking one. The close is ruled by **delegated approval (auto=true)**
over plan r6.

## Gate output (verbatim)

Union of the five phase lanes and the files the phases added to them, on
`main` at `f7fad6a1`:

    1365 passed in 332.67s (0:05:32)
    exit=0

Guard block with `tests/test_release_text.py` and `tests/test_gate_guard_list.py`:

    715 passed, 2 deselected in 167.68s (0:02:47)
    exit=0

    uv run ruff check src tests tools
    All checks passed!
    exit=0

    uv run ruff check
    All checks passed!
    exit=0

    python3 scripts/components_index.py changed --base origin/main --strict
    changed against origin/main (f7fad6a): 0 file(s) differ; 0 to fix, 0 warning(s), 0 to reread
    exit=0

Known red, outside this milestone: `tests/test_ir3_pyrel_includes.py`
`5 failed, 30 passed`, red on `main` at `1f403b07` before the milestone
began (IR3's goldens predate RP3's `EXACT_FLOAT` line); a separate fix is
proposed to the owner.

Close review, panel light, over plan r5 with `notes/close-results.md` and
`notes/close-delta.md` at `d95dc418`: exit 0, `run_sha256`
`c2e9ff49866979e6e7b8147e5d211fb6ac89aca24f96f7f1be4f3263d31d007b`,
`quorum-established`, four of six successes (Qwen timed out, Gemini
returned no JSON); finalize exit 0, `synthesis_sha256`
`7ffe0ffcf08b238954a88029fdb9f497407bc1924d6418571e4efcda8923ea15`, no agreed
concern, four divergent views, none blocking
([disposition](evidence/close-review/disposition.md)).

## Close ruling

Delegated approval (auto=true), 2026-11-23. Authorization: the owner's
`/process-milestone reviewed-vocabulary-growth auto` in this session, and
the owner's "Run the close" of the same day, with the GND panel light the
plan gate selected for the close review (D8). This is the driving agent's
ruling, not the owner's reading of the artifacts.

    approved: milestone reviewed-vocabulary-growth closed over plan r6,
    sha256 6e4ce43013d7b337a3f8e14369f376225ea36b20790153fc914ff86d61340773,
    with the close amendments (c1) and the review repairs (c2) of its section 11.

## Phases

| Phase | Record | Result |
|---|---|---|
| VG1 | [002-phase-VG1.md](002-phase-VG1.md) | `gnd check` cost about linear in the number of object types (#221) |
| VG3 | [003-phase-VG3.md](003-phase-VG3.md) | an unattended root may include a reviewed vocabulary (#222) |
| VG2 | [004-phase-VG2.md](004-phase-VG2.md) | `gnd evolve` admits `sample` and `common-sense` constraints (#218) |
| VG4 | [005-phase-VG4.md](005-phase-VG4.md) | a seeded root grows through `gnd evolve` (#222, case 3) |
| VG5 | [006-phase-VG5.md](006-phase-VG5.md) | the seeded-growth example, the pages, the drafted replies |

## Goal predicates

Each predicate's evidence is in `notes/close-results.md`, "Goal
predicates"; every one is met. The replies are drafted and not posted.

## Plan repair

Plan r6 carries every repair in §11: five `(c1)` rows from the phase
records (the extra homes of VG2, VG3 and VG5, the whole-repository ruff, the
VG1 tables) and two `(c2)` rows from the close review (VG4's composed
reading, VG3's compatibility reach), with `(c2)` additions to row 5 and to
§7. Each keeps the r4 wording it amends and names the record that raised it.
The repaired bytes carry no review opinion.

## Refuted premises

- Plan r4 §2 said U1's first-document test "cannot be read on the composed
  document"; VG4 reads it there with VG3's origin set, and its per-section
  cases measure the equivalence (`005-phase-VG4.md`, the close review).
- VG1's spec said the tables read "the index's dump of the model"; the
  cached dump can belong to another model (`002-phase-VG1.md`).
- Plan r4 H27: the whole-repository ruff was red; at the close it exits 0.

## Open-questions sweep

Every open question in `001`–`006`, plan §10 and the close review:

| Question | Raised in | Disposition |
|---|---|---|
| `ModelIndex`'s cache key admits two models whose values differ (other readers; the VG1 tables past the routed reader's caps) | `002-phase-VG1.md` | carried: a maintenance pass, the owner to file |
| a subtype chain hundreds of types deep stays slow | plan D12 | carried: successor question |
| `gnd judgments check` runs the checker twice | plan D10 | carried: successor question |
| VG1-D5, the witness oracle's walk | `002-phase-VG1.md` | closed: `gnd verify` 0.40 s at 1,000 |
| `remap_issues` reads composed addresses by pattern | `003-phase-VG3.md` | carried: a maintenance pass, if the owner wants one |
| U1's first-document rule | `003-phase-VG3.md` | closed by `005-phase-VG4.md` |
| the evolve exit classifier maps refusals by message | `004-phase-VG2.md` | carried: a maintenance pass, if the owner wants one |
| a census of every CLI route against include roots | `006-phase-VG5.md` | carried: a maintenance pass, if the owner wants one |
| the five red IR3 PyRel tests | `003-phase-VG3.md` | carried: the separate fix proposed to the owner |
| MC1 T22's timing flake | `005-phase-VG4.md` | carried: a maintenance pass |
| `project.md`'s stale lines (D11) | plan D11 | carried: the owner's |
| posting the three replies | plan §5 | carried: the owner's |
| plan §10's spec-level questions, VG4's "how the root's own document reaches U1" included | plan §10; the close review | closed by VG1-D1, VG3-D1, VG3-D2, VG4-D2 and the VG4 spec §6 |
| the four close-review concerns | `evidence/close-review/` | closed: repaired in plan r6 and the close bundle |

## Boundary -- what this close does NOT establish

- The close review is advisory: four of six seats, and the repaired bytes
  (plan r6, the results, the delta) carry no review opinion.
- Each phase's review was one reviewer, and each phase's fix commit was not
  re-reviewed.
- Nothing is released: the changes are on `main`, not in 0.4.0.
- The replies are drafted, not posted.
- The include trust limit stands: GND checks an include's bytes against the
  pin and cannot know who reviewed them (plan §6).
- The absolute time bounds of VG1 were judged on one machine, beast-3.
