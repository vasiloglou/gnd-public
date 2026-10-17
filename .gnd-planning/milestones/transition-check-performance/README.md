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

**Next action:** the owner approves the plan and the TP0 spec, and rules on
D-p1-1, D-p1-2 and spec D7/D8. After that, run `process-phase TP0 transition-check-performance`.
