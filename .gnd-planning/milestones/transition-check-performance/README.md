# transition-check-performance

Source: [issue #24](https://github.com/vasiloglou/gnd-public/issues/24), which
reports per-step transition/check cost dominating imperative plan execution.

- Plan: [notes/transition-check-performance-plan.md](notes/transition-check-performance-plan.md)
  (draft r2, 2026-10-16, not reviewed, not approved)
- First phase spec: [notes/phase-TP0-spec.md](notes/phase-TP0-spec.md)
  (awaiting owner review; blocked on the reporter's workload files)

Phases: TP0 baseline → TP1 ModelIndex hits → TP2 deep copies → TP3 opt-in,
receipt-bound pre-state reuse → close. TP4 (incremental evaluation) is
deferred to a successor milestone.

**Ruled 2026-10-16 (owner, after a conference with the reporter):** TP-D1, TP-D2,
TP-D3, TP-D4. **Open:** TP-D5 (receipt details), TP-D6 (targets), TP-D7 (review
instrument). **Input pending:** the reporter's workload files.

**Next action:** the owner reviews the plan and selects a review instrument.
After plan approval, run `process-phase TP0 transition-check-performance`.
