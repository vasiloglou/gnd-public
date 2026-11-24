---
milestone: literature-reading-reference
station: plan-gate
scope: plan-gate
date: 2026-11-23
skill: "process-milestone (auto=true); the gate ruled under the owner's delegation"
gates:
  - command: "uv run python tools/run_gnd_review_panel.py review-request.json --out panel-run --reviewer-timeout 600 --overall-timeout 900"
    exit: 0
  - command: "uv run gnd review finalize panel-run synthesis.json --out PANEL-REVIEW.md"
    exit: 0
  - command: "uv run python tools/run_gnd_review_panel.py review-request.json --out panel-run --reviewer-timeout 600 --overall-timeout 900"
    exit: 0
  - command: "uv run gnd review finalize panel-run synthesis.json --out PANEL-REVIEW.md"
    exit: 0
  - command: "ruling: delegated approval (auto=true) of .gnd-planning/milestones/literature-reading-reference/notes/literature-reading-reference-plan.md sha256 b07cf6895adac043d8de451c95c49a44ff0e7aac29eb5c4ab9e3b2ed076aa772"
    exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/reviews/literature-reading-reference-r2-panel/PANEL-REVIEW.md
    sha256: 3e39b57d57d2a3ee744535dd97e2b0005f0ca3093a631b8e5ba0b67860d686c8
  - path: .gnd-planning/reviews/literature-reading-reference-r3-panel/PANEL-REVIEW.md
    sha256: 557adc924bcd5a6bee6995a69c3f4a26a41ce92977011f5521ceb360e5c71c60
---

# Plan gate: literature-reading-reference r4

Date: 2026-11-23. `auto=true`.

## Authorization

- **Delegation.** The owner asked that this milestone start with
  `/process-milestone literature-reading-reference auto` ("they should both
  start with /process-milestone auto"), relayed by the coordinating session
  on 2026-11-23. That delegates plan, spec and close rulings within this
  milestone only. It does not authorize a paid producer call, a credential,
  publication, a certification or a merge.
- **Owner rulings, not delegated.** D6, plan and close review: "Full panel,
  both" (2026-11-23). Phase-diff review: "Review helper, both" (2026-11-23),
  one independent reviewer in a different tool per phase diff. Both were
  relayed by the coordinating session in the owner's words.

## Delegated approval (auto=true)

This is a delegated ruling under the authorization above. It is not the
owner's personal reading of the plan.

| Field | Value |
|---|---|
| Artifact | `notes/literature-reading-reference-plan.md`, plan r4 |
| SHA-256 | `b07cf6895adac043d8de451c95c49a44ff0e7aac29eb5c4ab9e3b2ed076aa772` |
| Scope | the whole plan; LR1 and LR2 may proceed to their spec gates; LR3 may not start before LH1 and LH2 are on `main` and D3 is ruled by the owner |
| Review instrument | the full GND panel, two rounds (r2, r3), the budget the plan declared |
| Budget | no paid producer call; panel calls only, two rounds, spent |

**How the review was used.** Round one (r2) blocked on two findings, both
reproduced and fixed in r3. Round two (r3) raised no blocking concern; its
five fixes are applied in r4 under the stop rule r3 §8 declared before round
two, so r4's own bytes were not read by a panel. The r3→r4 diff changes
wording, homes and one lane, and adds no new phase, criterion kind or
decision; that is why no third round is run.

**Implementability sweep.** At `11a7ebf7` the driving agent re-ran H2–H4
(exit 1, one failing `uniqueness` verdict with two rows; text without rows;
`--rule-ids` refused), confirmed the include resolves beside the model,
whole-repository `uv run ruff check` exits 0, derivation failures exit 1,
`assurance_report.py` reports precision and recall against an answer key,
the disclosure default (`docs/reference/disclosure.md:20`), and that every
§9 lane file exists. LR1's spec r2 is written against r4.

## Rulings

| Decision | Ruling | By |
|---|---|---|
| D1 labelled set | (d) reuse the regression corpus with an overlay that changes none of its bytes, if LR3's spec shows the reading stages can read its documents as sectioned sources; else (a) | delegated |
| D2 quote rule | (b): a quote may lie anywhere in the document the sidecar names; the pages recommend the whole source version | delegated |
| D3 LR3 producer and budget | **not ruled.** It spends paid producer calls and needs credentials, which the delegation does not cover. It goes to the owner at LR3's spec gate | owner, pending |
| D4 scoring rule | participant names plus section overlap with the gold passage, predicate agreement beside it, counted by `assurance_report.py`'s precision and recall; section grain stated on the page | delegated |
| D5 LR1 and LR2 ahead of LR3 | yes, each phase its own pull request; interim #226 reply drafted in LR2 | delegated |
| D6 review instrument | the full GND panel for plan and close review | owner, "Full panel, both" |
| D7 does `gnd verify` change | (a) no; LR1 is a page, a runnable example and a test | delegated |
| D8 home of the steps | (a) `docs/guides/documents.md`; the skill cites it by absolute URL | delegated |
| D9 stage settings | as r4 states: producer, budget, roster split, and stage prompts if LH2 records them | delegated |
| Phase-diff review | one independent reviewer in a different tool per phase | owner, "Review helper, both" |

The plan's status line is set to approved under delegation in r4, and its
§10 rows keep their "Proposed" wording; this record is what rules them.

## Sequencing (coordination, not approval)

The coordinating session owns the order across the four milestone sessions.
LR1 needs no clearance. LR2 and LR3 start only after this session sends
"READY <phase>" and receives "GO". LR3 also needs LH1 and LH2 merged on
`main`, checked by fetching `origin/main`.

## Residuals

- `project.md` line 25 says "There is no component index in this
  repository", which its later "Component index" section contradicts. The
  plan keeps the component-index check. Editing `project.md` is outside this
  milestone; reported as a follow-up.
- D3 is the owner's (above).
