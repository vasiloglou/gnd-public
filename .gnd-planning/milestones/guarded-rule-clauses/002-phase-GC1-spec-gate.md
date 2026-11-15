---
milestone: guarded-rule-clauses
station: phase-GC1-spec-gate
skill: gnd:process-phase
scope: phase-GC1-spec-gate
date: 2026-11-15
gates:
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/guarded-rule-clauses/notes/phase-GC1-spec.md sha256 f8e9a7505b0bad2c64c64428c274ce827da834758b0c08ffbc4932819e413888"
    exit: "n/a -- ruling"
  - command: "python -m pytest -q tests/test_guarded_membership.py --tb=short"
    exit: 1
evidence:
  - path: .gnd-planning/milestones/guarded-rule-clauses/notes/phase-GC1-spec.md
    sha256: f8e9a7505b0bad2c64c64428c274ce827da834758b0c08ffbc4932819e413888
  - path: .gnd-planning/milestones/guarded-rule-clauses/corpus/GC1/expected.json
    sha256: 27cf54b888e3988db24b6d3b68a3f108282923bc8fbd72e7dba82b7336595ca9
  - path: tests/test_guarded_membership.py
    sha256: bbd32521c03550b8046d9f4d694326535d0ee196b6d6a86bbb56f6f1c1b98a2c
---

# GC1 spec and corpus gate

**Delegated approval (auto=true), 2026-11-15.** The owner's named invocation
delegates the GC1 spec and corpus gate. Approve the r4 spec and initial corpus
above for GC1 implementation. Use the approved plan and its two-round
Standard panel evidence. GC1 uses the repository's independent phase-diff
review and the focused gates in the spec.

Allow membership in derivation and guarded term filters, with a 1,024-item
list cap. Use the literal spelling `not in`. Integer, Float and Number share
a membership identity domain. Duplicate members generate a diagnostic.
Retain the existing synthesis reasons for proven one-sided Boolean domains.

The initial corpus failed on all fifteen new positive requirements because
the existing schema rejects the new form. Six refusal controls passed.
The ordinary equality equivalents for the direct, existential and
derived authoring sites separately validated at exit 0 on the baseline.

## Gate output

    15 failed, 6 passed in 0.96s

## Boundary

This record binds the expected public behavior and the initial red corpus.
Implementation, focused compatibility gates, the differential harness,
and the independent phase-diff review remain part of GC1 completion.

## Open questions

The GC1 completion record must cite its green gate, each refusal and each
supported path. GC2 remains dependent on GC1 completion.
