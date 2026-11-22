---
milestone: pyrel-rules-coverage
station: "plan gate"
skill: process-milestone (plan written by start-milestone)
scope: plan-gate
date: 2026-11-21
gate:
  command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/pyrel-rules-coverage/notes/pyrel-rules-coverage-plan.md sha256 9a93f4c2aee127cb0608c4f502740c9e123010df70d6fd1963a4737954ae9434"
  exit: n/a -- ruling
evidence:
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/pyrel-rules-coverage-plan.md
    sha256: 9a93f4c2aee127cb0608c4f502740c9e123010df70d6fd1963a4737954ae9434
  - path: .gnd-planning/milestones/pyrel-rules-coverage/evidence/plan-review-r1/disposition.md
    sha256: 7c27a76e3baf9af048d56c6cfbbb0c99304a93f7ea77138f3af933181e0d8dc3
  - path: .gnd-planning/milestones/pyrel-rules-coverage/evidence/plan-review-r1/PANEL-REVIEW.md
    sha256: d415e95c016083821cf23c3bb93beb3a20d494223fe72cc91379014af12850c3
  - path: .gnd-planning/milestones/pyrel-rules-coverage/evidence/plan-review-r2/disposition.md
    sha256: 4158b74913f8cd8833a95a864f9c23ba038f2d964fba0c82ba6432ea98aafe6b
  - path: .gnd-planning/milestones/pyrel-rules-coverage/evidence/plan-review-r2/PANEL-REVIEW.md
    sha256: cdb650d2e4977a4d7fd9caf22b58c4b4223f103d53c7a32c8be8f99a0cd82846
---

# Claim

Plan r4 is approved by **delegated approval (auto=true)** on 2026-11-21. This
is the driving agent's ruling under the owner's delegation, not the owner's
reading of the plan. It approves the plan only; each phase spec has its own
gate. The RP1 draft spec (`notes/phase-RP1-spec.md`) is not approved here.

## Gate output (verbatim)

Authorization source: the owner invoked
`/process-milestone pyrel-rules-coverage auto` in this session on
2026-11-21, which delegates plan, spec and close rulings within this
milestone. Answering questions the same day, the owner chose "Run
start-milestone (Recommended)" for the plan, "GND panel (full xhigh)" as
the review instrument for the plan review and the milestone close, and
"Opt in pyrel_oracle (Recommended)" for this milestone's phase and close
gates.

Ruling, delegated (auto=true), 2026-11-21:

    approved notes/pyrel-rules-coverage-plan.md r4,
    sha256 9a93f4c2aee127cb0608c4f502740c9e123010df70d6fd1963a4737954ae9434

The implementability sweep ran before this ruling. Every GND behaviour the
criteria compare against was measured on 2026-11-21, not read: anchored
(unchecked, exit 4, also over an empty subject), external uniqueness on the
packaged population (0), a repeated pair (1, witness `[["p01",
"working-notes"]]`), an empty join (2), a disconnected join (2 empty, 4 with
facts), an ambiguous join (refused, exit 3, by `gnd check` and by the
export), a boolean in a `Number` role (3), and the 41 resolution
populations' count. Each criterion was walked for "can some implementation
satisfy this": RP2-C7 needs the report function separable from the engine
call, which the LQP main allows; RP1-C8 has a stated fallback; RP3-C5 needs
only a walk of the model's numeric constants. The oracle-lane baseline at
`8c909013` is `110 passed, 21 deselected`.

## Rulings recorded

| ID | Ruling (delegated, 2026-11-21) |
|---|---|
| D1 | anchored constraints are listed in the program as not checked, with a reason and counted in the success line, as r2–r4 propose |
| D2 | `Number` is typed as `Float`, as proposed |
| D3 | role-scoped value constraints are taken in, as proposed |
| D4 | an externally identified entity is `String`; a non-string value is a by-name input refusal (exit 3), as proposed |
| D5 | the LQP program exits 4 when it lists a must-rule as not checked and the engine reports no violation; a deontic one keeps the band, as proposed |
| D6 | integers beyond 2**53 are refused by name in `Number` and `Float` roles and in the model's constants of those types, as proposed |
| D7 | phase diffs are reviewed by the review helper with Codex, read-only; one reviewer is one reviewer (`project.md`, plan §8) |

Budget: two plan-review rounds (spent); one full-panel round at close. Per
phase: one Codex review round through the review helper. Order: RP2, RP1,
RP3, RP4, RP5.

## Plan review

Two rounds of the full GND panel (xhigh), both advisory:

- Round 1 over r2 (`a2a69608`, sha256 `f2296905…3dbf`): four of six seats
  (Qwen and Gemini malformed), all four revise; 19 concerns, 18
  reproduced, one turned into a measurement; 6 blocking. Repairs in r3
  `(p1)`.
- Round 2 over r3 (`5b1df6fb`, sha256 `077871ed…4179`): four of six seats
  (Claude and Gemini malformed); Kimi approved, three revise; 19 concerns,
  18 reproduced, one rejected by measurement; 12 self-inflicted. Repairs in
  r4 `(p2)`.

The stop rule fired after round 2 (self-inflicted 12/19), and the declared
budget was two rounds. **r4 has not been reviewed**; its `(p2)` repairs
carry no review opinion.

## Boundary

- This ruling is not a review opinion and not the owner's reading.
- Neither round had all six seats. No seat ran on r4.
- The oracle lane runs DuckDB locally; no RelationalAI engine run is
  planned or authorized.

## Open questions

Carried in plan §10 to the phase specs.

## Refuted premises

- Round 1's disposition accepted that GND reports an ambiguous external join
  as unchecked. Measurement showed GND refuses the model (exit 3). Recorded
  in `evidence/plan-review-r2/disposition.md`; r4 corrects §1 and RP1-C7.
