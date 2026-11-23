---
milestone: aggregate-count-certificates
station: close-candidate
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: close-candidate
date: 2026-11-16
evidence:
  - path: .gnd-planning/milestones/aggregate-count-certificates/001-plan-gate.md
    sha256: 39ba2cdc1ed8f541e190dcb207bec0e2a7b9b751cade4b3b7e9c0a7a108fc99d
  - path: .gnd-planning/milestones/aggregate-count-certificates/002-phase-AC1-spec-gate.md
    sha256: 38db868c385b0b7e1a2be39278d3292f9fb2da1000518aaaf59c5da0a4e9c3d5
  - path: .gnd-planning/milestones/aggregate-count-certificates/notes/aggregate-count-certificates-plan.md
    sha256: cd4f3b24b3c1427ce4b214fee08b81111bc832da0ca51f9c94189c905cd74a0c
  - path: .gnd-planning/milestones/aggregate-count-certificates/003-phase-AC1.md
    sha256: 132d1ece214de4de0033cce197aea732ae23ec46e9e9f0a5839b86b9daf6b710
  - path: .gnd-planning/milestones/aggregate-count-certificates/evidence/AC1/installed-observation.json
    sha256: 6d010b9c6b332ffccfbf1275d36a975d300a8889165fe7fc58dc9a106d86adbc
---

# Aggregate COUNT certificates close candidate

[Issue #193 part 10](https://github.com/vasiloglou/gnd-public/issues/193#part-10-aggregate-certificates-with-membership-completeness)
calls for a replayable proof of the exact members of a count. The
[approved plan](notes/aggregate-count-certificates-plan.md) applies that
goal to one explicitly named group in the bounded single-relation COUNT
fragment. [Draft PR #204](https://github.com/vasiloglou/gnd-public/pull/204)
carries the runtime, wire contract, tests and installed example.

## Exit predicates

| Issue criterion | Evidence |
|---|---|
| Omitted member | Replay refuses an omission with a correspondingly reduced count at exit 1. |
| Duplicate member | Replay refuses a repeated member with an adjusted count at exit 1. |
| Empty group | A named group with no contributions replays successfully over a declared covered relation. The checker still derives rows only for groups with contributing bindings. The installed checker reports before and after are byte-identical. |
| Changed inputs | Model, candidate population and independently selected request are exact digest bindings. Changes stale the certificate before membership comparison. |
| Size limits | Intake, row visits, cells, distinct members and generated certificate bytes have explicit ceilings. Work refusal yields no certificate. |
| Individual member evidence | The installed example exercises a separate ordinary witness for the source row named by the COUNT member. |

[AC1](003-phase-AC1.md) records the independent review, the verification
selection and the exact observations. The packaged example produced
two contributions for `flow` and zero for `empty`. It replayed both
COUNT certificates and the individual member witness.

## Questions and residuals

| Question | Disposition |
|---|---|
| Issue #193 part 10 | All five scoped criteria have executable controls. Close is pending the standard panel and delegated ruling. The issue remains open. |
| Wider aggregate rules | Other aggregate functions, joins, recursion, references, includes and composition lineage have separate evaluation requirements. Any successor needs its own scope and review. |
| Coverage outside the snapshot | The claim covers the supplied, authenticated relation under its explicit coverage declaration. The plan treats external or corpus-wide completeness as a separate question. |
| Host-scale literature evidence | The inherited host-scale follow-up remains with the literature identity work. |
| Review helper prompt separator | Carry to the dev-tools maintainer, as recorded by the preceding milestones. |
| Whole-tree lint | Carry the inherited diagnostics to repository maintenance. This milestone adds none. |

## Boundary

The requested ruling is the close of the aggregate-count-certificates
milestone over this packet. Draft PR state and issue disposition retain
their separately authorized workflow.
