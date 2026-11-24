---
milestone: literature-host-interfaces
station: "milestone-close"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: milestone-close
date: 2026-11-23
gates:
  - command: "uv run python tools/run_gnd_review_panel.py review-request.json --out panel-run --reviewer-timeout 600 --overall-timeout 900"
    exit: 0
    note: "full GND panel over the plan (amended), close-results.md and close-delta.md at 9abb436a; the owner's word: \"full\""
  - command: "uv run gnd review finalize panel-run synthesis.json --out PANEL-REVIEW.md"
    exit: 0
  - command: "uv run pytest -q tests/test_lh1_reading_host.py tests/test_lh2_reading_replay.py tests/test_lh3_admission_shape.py tests/test_lh4_admission_rules.py tests/test_ld3_reading_workflow.py tests/test_ld4_revision.py tests/test_ld5_verdict.py tests/test_li1_assurance_report.py tests/test_ld1_competency_examples.py tests/test_li4_assertions.py tests/test_li5_lineage.py --tb=short"
    exit: 0
    output: "381 passed in 376.71s (0:06:16)"
  - command: "uv run python tools/run_tutorials.py --group literature"
    exit: 0
    output: "15 tutorial blocks passed"
  - command: "the project.md structure and inventory guard block (12 files)"
    exit: 0
    output: "679 passed, 2 deselected in 128.70s (0:02:08)"
  - command: "uv run ruff check"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base origin/main --strict"
    exit: 0
    output: "changed against origin/main (11a7ebf): 203 file(s) differ; 0 to fix, 0 warning(s), 1 to reread"
    note: "the reread line is examples.literature_depth, whose entry is still accurate"
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/literature-host-interfaces/notes/literature-host-interfaces-plan.md sha256 7ca294b7c2c3a9d0f2f17b98ba7b174ceeec478c46f1e4784f771169dd5189fb"
    exit: "n/a -- ruling"
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "the broad controls are outside this milestone's impact closure"
evidence:
  - path: .gnd-planning/milestones/literature-host-interfaces/notes/literature-host-interfaces-plan.md
    sha256: 7ca294b7c2c3a9d0f2f17b98ba7b174ceeec478c46f1e4784f771169dd5189fb
  - path: .gnd-planning/milestones/literature-host-interfaces/notes/close-results.md
    sha256: 67ef191a2692a61d45d7284c99ec51be723459d209c8ada4893428cfad3e1733
  - path: .gnd-planning/milestones/literature-host-interfaces/notes/close-delta.md
    sha256: 4dbf57b242d1daa83da3fa64c9fb85438ad86a59bdfb85af5918180b6ebef350
  - path: .gnd-planning/milestones/literature-host-interfaces/notes/issue-replies.md
    sha256: cb18a957191b905315cf7dab56f58c6e085719bb2b0a1498ed73cf3fe7d4d3a2
  - path: .gnd-planning/milestones/literature-host-interfaces/evidence/close-review/PANEL-REVIEW.md
    sha256: 8cedf248637c78128d43cb5125ef1a52c4eeb54988f00f1642d94c42d769d4b3
  - path: .gnd-planning/milestones/literature-host-interfaces/evidence/close-review/synthesis.json
    sha256: 809c577e09af0b0f98deb379a43c49f83838ce6cf8c49fbcc7ed5fe82110cd40
  - path: .gnd-planning/milestones/literature-host-interfaces/evidence/close-review/review-request.json
    sha256: ed12630bb4312fc126e48fda4db237a40ff13a82a1ff590c9e01a464f37aaaa5
  - path: .gnd-planning/milestones/literature-host-interfaces/notes/reviews/close-repairs-r1/review.md
    sha256: 07f0f2e355b975502d72efa1c4700cd0f7dc7f1f6049396f7e03fc6b2974f1ab
  - path: .gnd-planning/milestones/literature-host-interfaces/notes/reviews/close-repairs-r1/FINDINGS.md
    sha256: 050369d2bac033719797aa7e04c59aa0cae155b8f5ab38769e85072c32e70f91
  - path: src/gnd/examples/literature/reading.py
    sha256: eab24386547692957fbc1df3a749d5d82251c5efccadc47b9fab03849e3bda22
  - path: src/gnd/examples/literature/assertion_admission.py
    sha256: bc78375fb84d95f8497e519dce67ca8dd55a376764c0b03ad907b363e37856a6
---

# Milestone close: literature-host-interfaces

## Claim

All four phases have their records: `002-phase-LH1.md`, `003-phase-LH2.md`,
`004-phase-LH3.md`, `005-phase-LH4.md`. Every goal predicate of the plan
holds at the close tree, as `notes/close-results.md` sets out with its
measurements. The plan is closed as r6 with close amendments A1 to A4 (plan
§11). The departures from its letter are listed in `notes/close-delta.md`.
The replies to #216 and #215 are drafted in `notes/issue-replies.md` and
are not posted.

## Close review

- **Instrument:** the full GND panel, chosen by the owner in this session
  on 2026-11-23 with the word "full". The milestone-coordinator session
  later relayed an owner answer of "light". This session kept the owner's
  direct word, said so to the owner and to the coordinator, and offered to
  switch if the owner said "light" here; the owner did not.
- **What it read:** the amended plan, `close-results.md` and
  `close-delta.md` at `9abb436a`, as a spec, results and delta request. The
  run used a disposable clone at that commit; the panel source matched HEAD
  and `gnd` imported from the clone. Run digest
  `b8753de76a701cc9f1333b556afdfa62cdecbb146b97d9690b02092737bd10df`.
- **Seats:** four of six succeeded, so quorum held:
  - Gemini: `approve`.
  - Codex and Kimi: `revise`. Kimi's response is retained as incomplete,
    and one of its concerns is unanchored.
  - Qwen: `block`. Qwen read only the three artifacts given to it inline,
    as that seat always is, and read no code.
  - Claude and GLM timed out.
- **Code coverage:** Codex, Gemini and Kimi read the code, including the
  four phase repairs no phase reviewer had read.

### Dispositions

Each fix ranked in `PANEL-REVIEW.md`, with its disposition:

| Fix | Concern (reviewers) | Disposition |
|---|---|---|
| 1 | an accepted answer with an empty fact list marked its question supported (Codex, blocking) | **fixed** at `19a53466`: such an answer refuses, and support needs rows. `test_r10_an_empty_fact_list_is_not_support` failed before the fix |
| 2 | close-results asserts predicates whose evidence is not checkable at `9abb436a` (Qwen, Kimi; agreed) | **fixed**: close-results quotes the close gates and the packaged digests, and this record exists. At the reviewed commit the record could not exist yet, because a close record follows its review |
| 3 | the Qwen seat could not read the code (Qwen, blocking) | **accepted as a limit of the seat**, not a defect of the milestone. The record and close-results name the three seats that read code, and Qwen's opinion covers the three artifacts only |
| 4 | handle equality had no documentation home (Qwen) | **fixed**: the admission README's "Identity" bullet, and close-results' LH3 row cites the tests |
| 5 | the delta did not state the retained bound's response term, and omitted the `test_ld1` lane (Qwen, Kimi) | **fixed**: delta items 5 and 11 |
| 6 | the amended plan's status block, §3 and §11 disagreed with its amendments (Qwen) | **fixed**: amendments A2 (§3) and A4 (status block); §11 now points at the delta as the complete list |

### The close repair's own read

The close panel's repair had one Codex read
(`notes/reviews/close-repairs-r1/`), one reviewer being one reviewer. It
tested a 36-case matrix and found no runtime counterexample. Its two
findings were both about the close documents: this record and the scope of
the Qwen seat. Both are fixed here.

## Gate (close ruling)

Delegated approval (auto=true), 2026-11-23, under the owner's
`/process-milestone literature-host-interfaces auto`. It closes the
milestone on the gates above and binds the amended plan at sha256
`7ca294b7…89fb`. The owner chose the close review's instrument ("full");
the delegation chose nothing about it. This ruling is the agent's, under
delegation, and is not the owner's personal reading of the artifacts.

## Open-questions sweep

| Raised in | Question | Disposition |
|---|---|---|
| `003-phase-LH2.md` Q1 | plan D4 and §2 still say 64 MiB | **closed** by plan amendment A1 |
| `002-phase-LH1.md` | none opened | — |
| `004-phase-LH3.md` | none opened | — |
| `005-phase-LH4.md` | none opened | — |
| plan H20 | the corpus and provider-budget run | **carried**, to the literature-identity follow-up, as the literature-depth close assigned it |
| plan §5 | posting the replies to #216 and #215 | **carried**, to the owner: the replies are drafted, not posted |
| literature-reading-reference LR3 | it needs LH1 and LH2 on `main` | **carried**, to the owner's merge of #241 and that milestone's own session |

## Refuted premises

**Plan D4's 64 MiB retained-file ceiling.** Every JSON reader in the
repository refuses JSON over 10 MiB, so a larger retained file could never
be read back. This was refuted in LH2 and is repaired by A1.

## Refactoring review

Every phase record carries its own refactoring review, and none deferred a
refactor, so no deferred refactor needs an open-questions row.

## Residuals

- **Unread repairs:**
  - The four phase repairs no phase reviewer read (`59fd62f0`, `9df661c8`,
    `f718b572`, `4428a24d`) were read by three code-reading seats of the
    close panel.
  - The close repair was read by one Codex round.
  - The last edits to the close documents carry no review opinion.
- **No live provider ran.**
- **Time bounds were measured on one machine.**

## Boundary

- **Merging.** The milestone is closed locally on its branches. Both pull
  requests are open and unmerged: #241 (reading pair) and #245 (admission
  pair, stacked on #241). Merging them is the owner's decision, and this
  record does not authorize it.
- **Not authorized:** no release, publication, issue reply or posting.
- **The panel is advisory.** Its quorum is a count of successful reviewers,
  not an acceptance verdict.
