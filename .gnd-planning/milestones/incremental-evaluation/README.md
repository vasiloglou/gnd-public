# Incremental evaluation

Plan approved, 2026-10-19. Owner subsequently delegated milestone execution
with `auto=true` ([delegation](002-execution-delegation.md)).

- [Canonical plan](notes/incremental-evaluation-plan.md)
- [Owner plan approval and decision rulings](001-plan-gate.md)
- [IE0 spec and amendments](notes/phase-IE0-spec.md)
- [IE0 completed record](003-phase-IE0.md)
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
IE0 completed: 49 focused tests, lint and strict serial baseline passed.
IE1 is next; its spec/corpus gate follows the existing scoped delegation.
The old public workload is available; the newly offered workload is not supplied.
It blocks claims about the 547-program census, not drafting or the local baseline.
No delivery date or downstream performance result is promised.

Execution continues through IE1–IE5 under the named `auto=true` delegation.
No merge, publication or certification is authorized. No implementation beyond
IE0 has been accepted yet.
