# Incremental evaluation

Plan approved, 2026-10-19; `auto=false`. No implementation started.

- [Canonical plan](notes/incremental-evaluation-plan.md)
- [Owner plan approval and decision rulings](001-plan-gate.md)
- [First draft phase spec: IE0](notes/phase-IE0-spec.md)
- [Four-reader plan review and disposition](notes/plan-review-r1-disposition.md)
- [Issue #24](https://github.com/vasiloglou/gnd-public/issues/24)
- [Prior milestone close](../transition-check-performance/006-milestone-close.md)

Six phases: IE0 baseline → IE1 invalidation → IE2 extension reuse → IE3 selective
checks and session API → IE4 observations/feedback → IE5 integration/docs.
Milestone close is separate. The prior milestone's deferred TP4 is carried here;
its closed records and phase IDs are preserved.

Review instrument: four local reviewer agents, selected by the owner.
Plan review complete: three approve, one approve-with-fixes, no blockers.
The timing-schedule repair and status correction are recorded in the disposition;
amended bytes have no new review opinion.
The owner approved amended plan r2 and its proposed milestone decisions.
Pending: IE0's concrete spec gate and explicit phase workflow selection.
The old public workload is available; the newly offered workload is not supplied.
It blocks claims about the 547-program census, not drafting or the local baseline.
No delivery date or downstream performance result is promised.

Next: explicitly select `process-phase IE0 incremental-evaluation` for its
concrete spec gate. The plan gate records the owner decisions and boundaries.
