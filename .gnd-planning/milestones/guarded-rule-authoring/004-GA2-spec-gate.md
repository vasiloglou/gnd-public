---
milestone: guarded-rule-authoring
station: GA2-spec-gate
skill: "n/a -- repository development under process-milestone auto=true"
scope: GA2
date: 2026-11-11
gate:
  command: "review GA2 spec against approved plan and completed GA1"
  exit: 0
  output: "GA2 delegated implementation approved"
evidence:
  - path: .gnd-planning/milestones/guarded-rule-authoring/notes/phase-GA2-spec.md
    sha256: 5a16e10ad1f1f772522b20c0c2094e0e0323d35755941c721edcc612a463baa9
  - path: .gnd-planning/milestones/guarded-rule-authoring/corpus/GA2/expected.json
    sha256: 2a38942d2c191e6dff33a2aa7999672e1a4ea1ac666eac6a0484bbbb193db8b2
  - path: .gnd-planning/milestones/guarded-rule-authoring/003-phase-GA1.md
    sha256: dd049e0ae2da61e9fbf75c2d2940f96f28b7f290feb633d328abf80b0bd904fe
---

The approved plan and panel dispositions delegate this phase's specification
gate. GA1 is recorded complete at `1aeebd99`. The GA2 scope uses explicit role
coordinates, complete functional classification and separate directed caps.
The pre-implementation corpus pins distinct relation-row support, the
marker filter, counterexample attribution and the pair cap. Code starts
after the red CLI fixture. Phase diff review and milestone close remain
separate gates.
