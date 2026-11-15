---
milestone: literature-identity
station: phase-LI4-corpus-gate
skill: "n/a -- repository development under process-phase"
scope: phase-LI4-corpus-gate
date: 2026-11-15
gate:
  command: "ruling: delegated approval (auto=true) of LI4 contextual assertions corpus"
  exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/milestones/literature-identity/notes/phase-LI4-spec.md
    sha256: 30f20e7509b71e5f236fe67897b2af721561f5f84c2a82b7d3f3401b8e2ba90c
  - path: tests/test_li4_assertions.py
    sha256: b313745644e6ce07cdf67415d4383bc70898f1d2667b9f725d641f407a104fe0
  - path: src/gnd/examples/literature/assertions/README.md
    sha256: d99ac2d80eb68da97e6e44456739364392d7507d7e12659b8b67bbeda2a2170e
  - path: src/gnd/examples/literature/assertions/case-outcomes.json
    sha256: 8aa6376f99843952d3cd927985d52a86fd476758abdda54d6f0617d5b866a26c
  - path: src/gnd/examples/literature/assertions/evidence/passages.txt
    sha256: 9b0415e9d4eb6cb8bb3f7111e312f0d28e8db78656008c70e76d85c2e909e0f0
  - path: src/gnd/examples/literature/assertions/model.orm.yaml
    sha256: 3212647b84df439e3304d598275864b0b47cc0ef22fc530c6293b27c7e440f5b
  - path: src/gnd/examples/literature/assertions/policy.json
    sha256: 3b39c12629eff258c038824eaf9acc7a491aa3e976ea2a0446a2a12cb6e60db8
  - path: src/gnd/examples/literature/assertions/raw.population.json
    sha256: 888cc1662abcb7810ea923acd60ff9bb44efce34218d40ba6ecbb28250e435a0
  - path: src/gnd/examples/literature/assertions/receipts.json
    sha256: 3a0934d91e1c9b0b0864715c958a2f0689defb0638e5fe01621c5118e416f862
  - path: src/gnd/examples/literature/assertions/rubric.json
    sha256: 1c98384795afd57033b0416a6e8dbd6cd3f914a33fadc3510f605394079b0178
---

# Claim

**Delegated approval (auto=true), 2026-11-15.** The current milestone
chat delegates this LI4 corpus ruling. The identified passages, raw
extraction, policy, bound receipts, rubric and case outcomes are
approved as the corpus-first instrument. They distinguish extraction
support, declined opinions, abstention and missing review, and
positive eligibility. The expected projection keeps the two
conditional findings and the supported mention as separate statements.

Model validation exited 0. The unredacted saved-judgment command over
this exact fixture exited 1 with admitted targets 0, 1, 3, 4, 5, 6, 7
and the reject, abstain and missing cells at indexes 2, 8 and 9.
The producer's direct suite gave 11 failures in 1.32s with its
entry module absent. These measured controls establish that the
phase can select a sound subset from an overall judgment exit 1.

The selected independent diff review is Claude Code on stdin, with
one reviewer and no spec or corpus review rounds.

## Boundary

The underlying judgment command establishes opinion checks on the
frozen corpus. The producer's behavior is measured after implementation.
