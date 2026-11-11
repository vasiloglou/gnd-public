---
milestone: guarded-rule-authoring
station: phase-GA1-spec-gate
skill: "n/a -- repository development under process-milestone auto=true"
scope: phase-GA1-spec-gate
date: 2026-11-11
gate:
  command: "delegated approval (auto=true)"
  exit: 0
evidence:
  - path: .gnd-planning/milestones/guarded-rule-authoring/notes/phase-GA1-spec.md
    sha256: 0758b55f0cf564854b3eef1970beb82013f63878a785f49c430b5169e6548891
  - path: .gnd-planning/milestones/guarded-rule-authoring/corpus/GA1/README.md
    sha256: ff52b7c56e87f4f5cb503956a916c73eadfa16eaa30486400d18ca6b806ced1f
  - path: .gnd-planning/milestones/guarded-rule-authoring/corpus/GA1/expected.json
    sha256: f810f3bb3b8d99c73ac9b52d0cb14cada90a99ba1f06b280f24dfce477753f1b
---

# GA1 spec gate

The named delegation approves the exact GA1 spec and corpus answers.
A scratch scoped copy of the shipped rule-check model generated 15
ordinary cases at seed 17, with mandatory and ring targets. The guarded
oracle can be extended to typed literal matching without reading the
checker's output. The first phase owns the scope and case manifests,
bounded construction, paired confirmation and independent labels.
