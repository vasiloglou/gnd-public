---
milestone: guarded-rule-workflows
station: phase-GW2-spec-gate
skill: "n/a -- repository development under process-milestone auto=true"
scope: phase-GW2-spec-gate
date: 2026-11-11
gate:
  command: "delegated approval (auto=true)"
  exit: 0
evidence:
  - path: .gnd-planning/milestones/guarded-rule-workflows/notes/phase-GW2-spec.md
    sha256: 72be70e4fb08f694ce8369927e424bf8e7e1efbecc8ef5094bf5fd9f97d89965
  - path: .gnd-planning/milestones/guarded-rule-workflows/corpus/GW2/README.md
    sha256: 2a94b134ae9c3314c5b244e0a086b05a6337b2ceeba5733de60fdb868e99b5ef
  - path: .gnd-planning/milestones/guarded-rule-workflows/corpus/GW2/expected.json
    sha256: 3f302aa42cce0696467abb08c8137b4d5ac9ac888061ddbd987fcd8756dc1c18
---

# GW2 spec gate

The owner's scoped auto delegation approves the GW2 spec, corpus answers,
informational exit contract, comparison budget and fail-closed alignment.
The reproduction used the same admitted population on both editions and
observed check exits 1 with 43 and 1 witnesses. The retained binding has
the same two subject values plus a new guard variable in the narrower
edition, making raw whole-witness equality insufficient.
