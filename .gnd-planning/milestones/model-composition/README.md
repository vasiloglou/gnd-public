# model-composition

Planning opened 2026-11-09 for GR-D4, [issue 95](https://github.com/vasiloglou/gnd-public/issues/95):
one model file takes its object types, fact types and constraints from
another, pinned by sha256, and adds the project's own rules.

**Status: plan r3 approved by the owner on 2026-11-09, MD1-MD16 as proposed
([plan-gate record](001-plan.md)).** Two Codex rounds ran (r1 revise, 18
findings; r2 revise, 13), every finding reproduced and applied; r3 was not
reviewed, because the convergence stop rule fired (plan §11). Execution uses the owner's explicit auto delegation. MC1 is complete ([record 008](008-phase-MC1.md)) and merged through PR #154 at d5ca5d9a. MC2 is complete ([record 013](013-phase-MC2.md)) and merged through PR #156 at 720053ff. MC3 is locally complete ([record 023](023-phase-MC3.md)); [PR #157](https://github.com/vasiloglou/gnd-public/pull/157) at c6dad88d awaits the owner's separate merge authorization.

MC1's corrected default comparison retains exactly six frozen failures; its marked census passes 400 originals plus three additions. Current MC3 focused gates and bounded review are recorded separately. Lint retains 13 baseline findings. The owner rejected the scanner framing and selected Claude Fable's familiar expense example; records 019/020 retain its authorship and checkpoint-binding correction.

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

MC1's D1-D8 were ruled under the named milestone auto delegation; records002–005 retain the exact gates and amendments. MD17 received the actual positive owner reaction to Fable’s expense story: “Yes, this explains it” ([record021](021-MC3-apply-order-amendment.md)). Final MC4 incorporates that direction ([record025](025-phase-MC4.md)); this feedback is not byte or merge approval.

MC4 is locally complete and independently reviewed at6de7189a; PR #155 carries the accepted Fable story and measured update. MC3 merge authorization remains pending. The final beast-3 census passed400originals plus23 separately inventoried additions; the full default comparison is running. Main-branch predicates and independent close still remain.

- [MC4 final spec gate](024-MC4-gate.md)
- [MC4 completion](025-phase-MC4.md)

- [Close preparation and final census](026-close-preparation.md)
- [Inherited question sweep (preparation)](notes/close-question-sweep.md)
- [Completion predicate and final admission map](notes/close-predicate-map.md)
