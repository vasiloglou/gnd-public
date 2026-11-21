---
milestone: include-root-routes
station: "plan gate"
skill: process-milestone (plan written by start-milestone)
scope: plan-gate
date: 2026-11-21
gate:
  command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/include-root-routes/notes/include-root-routes-plan.md sha256 4cd41420effcd19e5d9528a9ad7a16c3ef0badf38c4f1b48103448c744f2194a"
  exit: n/a -- ruling
evidence:
  - path: .gnd-planning/milestones/include-root-routes/notes/include-root-routes-plan.md
    sha256: 4cd41420effcd19e5d9528a9ad7a16c3ef0badf38c4f1b48103448c744f2194a
  - path: .gnd-planning/milestones/include-root-routes/evidence/plan-review-r1/disposition.md
    sha256: 7124a97c5686f509270185ca88840b26723e120fd70a56cb7dc3b0a33ada9a99
  - path: .gnd-planning/milestones/include-root-routes/evidence/plan-review-r1/PANEL-REVIEW.md
    sha256: f98b2077638cd770b77860f1d8fe20693ef7df9f55896f1717ab3011b8b6e405
  - path: .gnd-planning/milestones/include-root-routes/evidence/plan-review-r2/disposition.md
    sha256: ed08dc43f3cfc6a50017ed0ac16528a5908efccce21b5bf4e8ab469a6d3fbb8c
  - path: .gnd-planning/milestones/include-root-routes/evidence/plan-review-r2/PANEL-REVIEW.md
    sha256: 0e0a353216e495c869396de4dd60d5a39ce46ff52bb50cb634ef5fddf4bf6971
---

# Claim

Plan r4 is approved by **delegated approval (auto=true)** on 2026-11-21. This
is the driving agent's ruling under the owner's delegation, not the owner's
reading of the plan. It approves the plan only; each phase spec has its own
gate.

## Gate output (verbatim)

Authorization source: the owner invoked
`/process-milestone include-root-routes auto` in this session on
2026-11-21, which delegates plan, spec and close rulings within this
milestone. Answering two questions the same day, the owner chose "Run
start-milestone (Recommended)" for the plan, and "GND panel light" as the
review instrument for the plan review and the milestone close.

Ruling, delegated (auto=true), 2026-11-21:

    approved notes/include-root-routes-plan.md r4,
    sha256 4cd41420effcd19e5d9528a9ad7a16c3ef0badf38c4f1b48103448c744f2194a

The implementability sweep ran before this ruling. Each IR1 criterion was
shown satisfiable by the scratch measurement in the IR1 spec §2. For IR2,
`flatten_model` already flattens the temporal root in memory and keeps
`publication_not_before_submission`. For IR3, the probes in plan §1 H4 and
H7 measured each export mode's present refusal and the exit its flat model
gives. Every code citation was re-read at `260c4337`.

## Rulings recorded

| ID | Ruling (delegated, 2026-11-21) |
|---|---|
| D1 | `gnd flatten MODEL --out DIR`, a separate top-level command, as proposed |
| D2 | IR2 stays mandatory, as proposed |
| D3 | default export keeps refusing temporal models; `--rules` accepts them and gains no refusal, as proposed |
| D4 | receipts keep binding the root's bytes; pins bind includes; no schema version change, as proposed |
| D5 | the program records `FLATTENING_RECORD_SHA256` and `MODEL_INCLUDES`; exact spelling fixed at the IR3 spec gate |
| D6 | include refusals in the judgments report: `reason` `binding`, include code in `message`, as proposed |
| D7 | phase diffs are reviewed by the review helper with Codex read-only, as `project.md` names; one reviewer is one reviewer |

Budget: two plan-review rounds (spent); the panel light once more at close.
Per phase: one Codex review round through the review helper.

## Plan review

Two rounds of the GND panel light, both advisory:

- Round 1 over r2 (`185ccaca`, sha256 `4079c650…c39b`): six of six seats;
  24 concerns, 21 reproduced, 3 rejected with the text clarified; 5
  blocking. All 13 fixes applied in r3 (`(p1)`).
- Round 2 over r3 (`c1d7219b`, sha256 `bf150b5b…ea45a`): three of six seats
  (quorum exactly; Qwen timeout, Gemini and Kimi malformed); 5 concerns, all
  reproduced, none blocking, 3 self-inflicted. All 4 fixes applied in r4
  (`(p2)`).

The stop rule fired after round 2 and the declared budget was two rounds.
**r4 has not been reviewed**; its `(p2)` repairs carry no review opinion.

## Boundary

- This approves plan r4. It approves no phase spec, no merge, no push to
  `main`, no release, publication or certification, and no posting of the
  issue replies.
- The panel is advisory: its quorum is a count of successes, not of
  quality, and round 2's quorum includes two seats that share one CLI.
- The rest of each `panel-run/` (raw streams, capability probes) is outside
  history; each round is identified by its `run_sha256` in its disposition.

## Open questions

- IR2 spec: whether `gnd flatten` refuses a `--out` other than the root's
  directory for a model that declares references (plan §2 IR2, `(p2)`).
- IR3 spec: the single expected outcome of IR3-C3, read from `main` at that
  gate.
