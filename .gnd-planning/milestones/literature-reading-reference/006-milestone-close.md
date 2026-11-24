---
milestone: literature-reading-reference
station: "milestone-close"
skill: "n/a -- repository development via process-milestone auto=true, not a gnd-solve station over a domain model"
scope: milestone-close
date: 2026-11-23
gates:
  - command: "uv run python tools/run_gnd_review_panel.py review-request.json --out panel-run --reviewer-timeout 600 --overall-timeout 900"
    exit: 0
    note: "full GND panel over the plan (r4 with A1-A5), close-results.md and close-delta.md at 4f3e45da; the owner's word for close review: \"Full panel, both\""
  - command: "uv run gnd review finalize panel-run synthesis.json --out PANEL-REVIEW.md"
    exit: 0
  - command: "uv run pytest -q tests/test_lr1_verify_failure_listing.py tests/test_lr2_quote_scope.py tests/test_lr3_reference_set.py tests/test_ld3_reading_workflow.py tests/test_ld4_revision.py tests/test_ld5_verdict.py tests/test_li1_literature_corpus.py tests/test_li1_assurance_report.py tests/test_lh1_reading_host.py tests/test_lh2_reading_replay.py tests/test_lh3_admission_shape.py tests/test_lh4_admission_rules.py tests/test_verify_cli.py tests/test_anchor_sidecar_v2.py tests/test_public_extraction_prose_policy.py tests/test_extract_guidelines.py tests/test_documentation_tutorials.py --tb=short"
    exit: 0
    output: "544 passed in 838.37s (0:13:58)"
  - command: "the project.md structure and inventory guard block (12 files)"
    exit: 0
    output: "679 passed, 2 deselected in 155.46s (0:02:35)"
  - command: "uv run ruff check"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base origin/main --strict"
    exit: 0
    output: "changed against origin/main (6b0a7e5): 220 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
  - command: "ruling: delegated (auto=true) close of literature-reading-reference over .gnd-planning/milestones/literature-reading-reference/notes/literature-reading-reference-plan.md sha256 6dcf10929081330322d385c83cc3c21347a7ab6bc54c270ed44663eef7654098"
    exit: "n/a -- ruling"
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "the broad controls are outside this milestone's impact closure"
evidence:
  - path: .gnd-planning/milestones/literature-reading-reference/notes/literature-reading-reference-plan.md
    sha256: 6dcf10929081330322d385c83cc3c21347a7ab6bc54c270ed44663eef7654098
  - path: .gnd-planning/milestones/literature-reading-reference/notes/close-results.md
    sha256: 7d6f47ad56f4f60460d42b31bc12ebe7314bb494f0585a8b423d50f591d4c61a
  - path: .gnd-planning/milestones/literature-reading-reference/notes/close-delta.md
    sha256: 5c8ae9e547bce246778f130649693b72efa86652fca699efc5302eb01a3d05d4
  - path: .gnd-planning/milestones/literature-reading-reference/notes/issue-reply.md
    sha256: c698f5a98bdc739e48fe94e51df59ee3943883bfbe2817e460cc06505659eb2c
  - path: .gnd-planning/milestones/literature-reading-reference/evidence/close-review/PANEL-REVIEW.md
    sha256: 56d4fd6709db7be511e679d72186cc745838bc76052f785000cfded30918d9dd
  - path: .gnd-planning/milestones/literature-reading-reference/evidence/close-review/review-request.json
    sha256: d360e59a6d1fb9021d3e528e3e2210e1100935bf5e6d7e0058b12d3a8bba802f
  - path: .gnd-planning/milestones/literature-reading-reference/evidence/close-review/synthesis.json
    sha256: d0898567540e2c35a0bce8d8f9e118cd4ed1d5f8d0c9b273ba3e9bd64847b3c0
  - path: .gnd-planning/milestones/literature-reading-reference/evidence/close/final-gate.txt
    sha256: bc166a017b39b666dc59dfc3651a2e08d7cf81f1fd7e21c8ad31893716bde1e7
  - path: .gnd-planning/milestones/literature-reading-reference/notes/reviews/close-r1/review.md
    sha256: cb158aea56225425d01b06eb15e223db026d0a3c8bc2920c1dcf05eafd5d9e88
  - path: .gnd-planning/milestones/literature-reading-reference/notes/reviews/close-r1/FINDINGS.md
    sha256: b88d05f7b1daa49210be8184a07a9580a2a1f2c8f725b70371c11c03a15bfef6
  - path: src/gnd/examples/literature/reference_fixture/labels.json
    sha256: f3fddf0ea58c7e8cac303b0c0c1d0e5155f830c9e801622626f03feefb8698dc
  - path: src/gnd/examples/literature/reference_fixture/score.json
    sha256: 08c4830c3fefe901f6452aa62af4ceddf86b3a281cc14b264d162adbe3bec2dc
---

# Milestone close: literature-reading-reference

Date: 2026-11-23. `auto=true`. Closed at the LR3 branch: the close fixes
`8baf0eda`, the gates above at that commit, and this record's commit after
it. **Locally complete. Not merged and not released**: PRs 243, 244 and 252
wait on the owner.

## Phase records

| Phase | Record | PR |
|---|---|---|
| plan gate | [001-plan-gate.md](001-plan-gate.md) | 243 |
| LR1 | [002-phase-LR1.md](002-phase-LR1.md) | 243 |
| LR2 | [003-phase-LR2.md](003-phase-LR2.md) | 244 |
| D3 ruling | [004-ruling-D3.md](004-ruling-D3.md) | 244 |
| LR3 | [005-phase-LR3.md](005-phase-LR3.md) | 252 |

## Exit predicates

The plan closes the milestone when each phase has its record and the close
record cites green focused gates for LR1–LR3, the guards, `uv run ruff
check`, the component-index check, a drafted reply to #226, and a close
review on the D6 instrument:

- Phase records: all three, above.
- Gates: the lane above runs every LR1, LR2 and LR3 test file with their
  affected consumers, at `8baf0eda` with `main` `6b0a7e5` merged in
  (`evidence/close/final-gate.txt`). The guard block, ruff and the
  component check are green there too.
- Reply: drafted for all three requests, `notes/issue-reply.md`. Not posted.
- Close review: the full GND panel (D6, "Full panel, both"); below.

Each criterion's result is in [close-results.md](notes/close-results.md),
and each departure in [close-delta.md](notes/close-delta.md). Every
criterion is met, except LR1-C3, which is met in part: a field named only in
the guide's prose is unchecked.

## Close review

**Panel.** Full GND panel, one round, over the amended plan, close-results
and close-delta at `4f3e45da`, run from a clean clone. Run digest
`01db1810bb3dc40be6349acc024c006890bd1c91f966de15ab01c46986e2c885`.

- Four of six seats succeeded (Claude, Codex, Qwen, GLM), all voting
  `revise`. Gemini and Kimi were `malformed`. Qwen read the three records
  inline only. Claude and GLM share one CLI codebase.
- Agreed concerns: LR3-C1's per-source licence was one note (Claude, Codex,
  GLM), and the close records were not exhaustive (Claude, Qwen).
- Other reproduced findings:
  - two labels unreachable at section grain (their work identifier is only
    in the opening section);
  - anchors keyed without their document;
  - both passes using one prompt, unstated;
  - the reply's misses and merge wording wrong;
  - the corpus digests unchecked by `build()`.

All five prioritized fixes landed in `8baf0eda` (close-delta X12–X18). **The
recorded figures did not change.**

**Final Codex round** (`notes/reviews/close-r1/`), over the whole milestone
diff at `8baf0eda`. It read the phases' last repairs and the close fixes,
which no reviewer had read before. It re-derived the 16 built files, the 31
scopes, the score and the 46 responses, and probed the matchers. One
finding: the close claimed gates in a record that did not yet exist. This
record discharges it.

**Convergence.** No further close round. The panel's fixes are
documentation, label scope and checks, each re-read by the final Codex round
or held by a test that fails on the pre-fix code. The last round's only
finding was a sequencing one.

## Delegated close ruling (auto=true)

Under the owner's milestone delegation ("they should both start with
/process-milestone auto"), this is a delegated close ruling, not the owner's
reading:

| Field | Value |
|---|---|
| Plan | r4 with close amendments A1–A5, SHA-256 `6dcf10929081330322d385c83cc3c21347a7ab6bc54c270ed44663eef7654098` |
| Scope | the whole milestone: LR1, LR2, LR3 |
| Instrument | the full GND panel (owner), and one Codex reviewer per phase plus a final round (owner: "Review helper, both") |
| Budget | panel rounds: plan ×2, close ×1. Producer: USD 0.30 of the owner's USD 50 (D3) |
| Ruling | closed locally. Merge, release and posting the reply stay with the owner |

## Question sweep

| Question | Disposition |
|---|---|
| Plan §10: LR1 snippet or prose | resolved: a runnable Python block, executed by the tutorial runner (002) |
| Plan §10: LR2 `block_id` for the shown section | resolved: yes, LR2-D1 (003) |
| Plan §10: LR3 set size; precision for facts outside the gold | resolved: 12 documents, 31 labels; outside rows count (LR3-D3), and none occurred (005) |
| D1–D9 | ruled at the plan gate; D3 and its transport by the owner (004, A5) |
| LR1: prose field names unchecked (codex-3) | **carried**, as an accepted residual. Target: a later documentation-tests change that brings a Markdown section reader into the test environment. `tests/support/markdown_sections.py`, which VG5 added on `main`, may serve it; not this milestone |
| LR3: a public run-attempts accessor in `reading.py` | **carried**. Target: a later literature milestone; `reading.py` has its own writer |
| `project.md` line 25, "There is no component index", contradicts its later section | **carried**: a follow-up outside this milestone; reported to the coordinator |
| Re-record LR3 after PR 245 | **retired**: the run satisfies PR 245's rule and replays identically on `main` `f7fad6a1`; re-recording stays the owner's option |
| Wrong predicate compares values, not role names | **accepted residual**, stated in the reference README |

## Plan repairs

The plan amendments A1–A5 (§13) carry the refuted premises of 002 and 005
and the owner's transport ruling, with their provenance and the prior
wording kept. The plan's SHA-256 is above.

## Boundaries

- The reference figure is one run of `claude-sonnet-5-5` over 12 short
  synthetic paraphrases, scored at section grain. It says nothing about
  other papers, models or prompts, and it is not comparable as-is to #226's
  quote-scored figures. The page and the README say so.
- Both passes share one prompt; the passes differ only in which sections
  they read.
- The labels are one author's (the corpus's `answers/README.md`).
- Nothing is merged or released, and the reply is not posted.
