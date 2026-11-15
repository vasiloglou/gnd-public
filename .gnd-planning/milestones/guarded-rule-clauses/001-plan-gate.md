---
milestone: guarded-rule-clauses
station: plan-gate
skill: "n/a -- repository development under process-milestone auto=true"
scope: plan-gate
date: 2026-11-15
gates:
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/guarded-rule-clauses/notes/guarded-rule-clauses-plan.md sha256 d2f7f3c74e1605f78a06d8e022f213abe2b4235c6fad47bb0dcd94f510f1a513"
    exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/milestones/guarded-rule-clauses/notes/guarded-rule-clauses-plan.md
    sha256: d2f7f3c74e1605f78a06d8e022f213abe2b4235c6fad47bb0dcd94f510f1a513
---

# Plan gate

**Delegated approval (auto=true), 2026-11-15.** Approve the named milestone
plan r3 at the SHA-256 above in response to the owner's explicit
`gnd:process-milestone guarded-rule-clauses auto` invocation. Execute GC1
through GC4 in order and use the owner-selected Standard GND panel for close.
The two-round plan review budget is exhausted.

## Decisions

Accept D1's shared derivation and guarded term comparison sites and D2's
`not in` spelling. Accept D3's v16 count for definite surviving bindings and
the positive-prefix index rule. Accept D4's conditional v17 diagnostics when
the model uses `any_of`. Accept D5's proposed PyRel translations for
membership and antecedent filters, plus named refusals for other unsupported
profiles. D6 records the owner-selected review instrument and delegated
scope. Each phase spec will pin its own expected exporter matrix.

## Review and implementability

The [review disposition](notes/plan-review-disposition.md) cites both
successful Standard advisory runs and the amendments after confirmation.
Five seats returned valid responses on r1, and four on r2. The reviewed
plan digests are recorded there. The ruling covers r3 with the targeted
amendments in the disposition.

The PR checkout baseline gate exited 0 with
`967 passed, 2 deselected in 182.60s (0:03:02)`. An initial GC1 control
also validated the three planned representative sites with ordinary
equality at exit 0, and the draft membership counterpart produced exit 3.
The existing effective constraint view and guarded existential evaluator
supply the semantics recorded in r3. GC1 will collect its own red and
green test evidence after the separate spec ruling.

## Boundary

This ruling authorizes phased implementation under the named milestone.
Phase acceptance requires its own tests and review. Merge, publication and
certification each require separate authorization.

## Open questions

GC2 and GC3 must instantiate the specified unknown, coverage, work-limit
and legacy-report controls in their phase specs. GC4 must pin and run the
installed-example acceptance fixtures.
