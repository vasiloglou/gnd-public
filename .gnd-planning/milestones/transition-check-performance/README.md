# transition-check-performance

Source: [issue #24](https://github.com/vasiloglou/gnd-public/issues/24), which
reports per-step transition/check cost dominating imperative plan execution.

- Plan: [notes/transition-check-performance-plan.md](notes/transition-check-performance-plan.md)
  (draft r5, 2026-10-16, reviewed: two rounds, stopped by rule; not approved)
- First phase spec: [notes/phase-TP0-spec.md](notes/phase-TP0-spec.md)
  (awaiting owner review)

Phases: TP0 baseline → TP1 ModelIndex hits → TP2 deep copies → TP3 opt-in,
receipt-bound pre-state reuse → close. TP4 (incremental evaluation) is
deferred to a successor milestone.

**Decisions:** TP-D1 through TP-D7 are ruled by the owner (2026-10-16). The
reporter's workload bundle is available.

**Done:** plan approved ([001](001-plan-gate.md)); TP0 baseline recorded ([002](002-phase-TP0.md)); TP1 one index key per call ([003](003-phase-TP1.md)); TP2 shared fact-type rows ([004](004-phase-TP2.md)); TP3 check receipts ([005](005-phase-TP3.md)).

**Next action:** milestone close: four local readers, open-questions sweep, carryovers.
