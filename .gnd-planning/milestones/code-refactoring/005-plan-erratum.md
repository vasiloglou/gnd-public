---
milestone: code-refactoring
station: "plan-erratum-e1"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: plan-erratum
date: 2026-10-05
gate:
  command: "owner ruling in chat, 2026-10-05: \"ok go ahead\""
  exit: "approved"
  note: "Given in reply to a proposal to correct four stale plan statements, add an RF1 pointer, record this erratum and add a PROJECT.md status section; no new decision."
evidence:
  - path: .gnd-planning/milestones/code-refactoring/notes/code-refactoring-plan.md
    sha256: 1ffe91ddfd22f9e0fc7102fc6eb27e518d05dad996194e9bab584b58806acac8
    supersedes_sha256: ca55aac340d2263429d77bad1a30f3def8a914c88fd71870a7e408bf8e4daebd
  - path: .gnd-planning/milestones/code-refactoring/004-phase-RF0.md
    sha256: 87e3be484b7573aed2313a20086b7cd1b77da13d00b8e160699b5942b3a26154
  - path: .gnd-planning/PROJECT.md
    sha256: 0ac52b3e98b7318953ae12cd2871f21ba0c6751290bf67b18ceb514fd6b6e737
---

# Claim

The owner approved text-only erratum e1 to the code-refactoring plan on
2026-10-05. It brings the plan into line with rulings and measurements
already recorded and adds no new decision.

## Gate output (verbatim)

    ok go ahead

## Changes, each tagged (e1) in the plan

| Site | Was | Now | Authority |
|---|---|---|---|
| Status paragraphs | `src/gnd` gated on future RF-D2 conditions | All three conditions hold; code edits begin at RF2, after RF1 | [003](003-plan-gate.md), [004](004-phase-RF0.md), RF0 spec owner amendment 2 |
| Inspection baseline | `7e08e1e` | Measured base `19b131b`; `rf0-baseline.md` supersedes the audit's numbers | RF0 spec owner amendment 1 |
| Predicate 5 | Close table includes co-change pairs | Co-change removed | RF0 D3; refuted premise in 004 |
| Section 3, sequence | RF2 and later wait for RF-D2 | RF-D2 satisfied; RF2 follows the RF1 record | RF0 spec owner amendment 2 |
| RF1 | — | A pointer to RF0-OQ2 and RF0-OQ3 and the F4 budget routing | 004 open questions; 002 routing |
| RF8 body and RF-D8 | Remove the "dead" first `SESSION_CONTRACT_VERSION` assignment | Withdrawn: the assignment is live | rf0-baseline A13; refuted premise in 004 |
| RF-D2 row | Tag and Phase-5-from-tag conditions | Satisfied; the original text is kept, marked superseded | RF0 spec owner amendment 2 |
| Risk row "Release evidence is invalidated" | Control via the tag | No longer applies | Public-launch `009` close |

Also added: a `code-refactoring` status section in `.gnd-planning/PROJECT.md`.

## Boundary -- what this result did NOT establish

- No panel reviewed the e1 bytes. The r1 and r2 panels cover only their
  own digests.
- This erratum resolves none of the open questions routed to later spec
  gates (RF0-OQ4 to OQ7), apart from the plan-text repairs that OQ7 named,
  which are done here instead of at close.
- It approves no phase spec and no code.

## Open questions

- RF0-OQ7 (plan text repair at close) is discharged by this erratum for
  predicate 5 and RF-D2. The close record still sweeps it.
