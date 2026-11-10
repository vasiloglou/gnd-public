# model-composition

Planning opened 2026-11-09 for GR-D4, [issue 95](https://github.com/vasiloglou/gnd-public/issues/95):
one model file takes its object types, fact types and constraints from
another, pinned by sha256, and adds the project's own rules.

**Status: plan r3 approved by the owner on 2026-11-09, MD1-MD16 as proposed
([plan-gate record](001-plan.md)).** Two Codex rounds ran (r1 revise, 18
findings; r2 revise, 13), every finding reproduced and applied; r3 was not
reviewed, because the convergence stop rule fired (plan §11). Execution uses the owner's explicit auto delegation. MC1 is locally complete ([phase record](008-phase-MC1.md)): the corrected default comparison retains exactly the six frozen failures and no additional failure; marked census passes400 original members plus3 additions. Lint retains13 frozen findings. Independent production and test-inventory reviews retain their actual byte scopes. PR154 remains unmerged.

- [Plan (r3, approved)](notes/model-composition-plan.md)
- [Plan-gate record](001-plan.md)
- [MC1 spec (r5, delegated approval and review repairs)](notes/phase-MC1-spec.md)
- [Codex review of r1](evidence/plan-review-r1/codex-review.md), with the
  reviewed r1 bytes and the prompt beside it
- [Codex review of r2](evidence/plan-review-r2/codex-review.md), likewise

Phases: MC1 (contract, loader, route guards, validate and check), MC2
(consumer support), MC3 (evolve, re-pin, proposal writers, end-to-end
scenario), MC4 (docs, skills and a runnable how-to on the shipped component
example); close. Owner amendment a1 (2026-11-09, plan §12) adds the how-to
and a review copy of it shown to the owner right after MC1 (MC4-draft).

MC1's D1-D8 were ruled under the named milestone auto delegation; records002–005 retain the exact gates and amendments. MD17, the business-level tutorial page (plan §10), remains before MC4.

Next: obtain explicit merge authorization for the fixed MC1 PR head and execute MC2 under its own spec/corpus gate. The after-merge owner docs reaction remains a separate checkpoint.
