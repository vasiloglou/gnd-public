# Incremental evaluation

Plan approved, 2026-10-19. Owner subsequently delegated milestone execution
with `auto=true` ([delegation](002-execution-delegation.md)).

- [Canonical plan](notes/incremental-evaluation-plan.md)
- [Owner plan approval and decision rulings](001-plan-gate.md)
- [IE0 spec and amendments](notes/phase-IE0-spec.md)
- [IE0 completed record](003-phase-IE0.md)
- [IE1 completed record](004-phase-IE1.md)
- [IE2 completed record](005-phase-IE2.md)
- [IE3 completed record](006-phase-IE3.md)
- [IE4 completed record](007-phase-IE4.md)
- [IE5 completed record](008-phase-IE5.md)
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
IE1 completed: 1,419 focused tests and lint; eight reproduced review findings repaired.
IE2 completed: 245 focused tests and lint; component envelope reuse and twelve review controls.
IE3 completed:1,079 affected checks plus68 final repair checks; opt-in sessions and private receipts.
IE4 completed:614 affected checks; validated host observations, closed feedback and atomic progress.
IE5 completed: frozen replay body work4878→179 with full parity; installed smoke and focused gates pass.
Measured session wall time is slower on the small public fixtures. Four-reader close is next.
The old public workload is available; the newly offered workload is not supplied.
It blocks claims about the 547-program census, not drafting or the local baseline.
No delivery date or downstream performance result is promised.

Execution continues through IE1–IE5 under the named `auto=true` delegation.
No merge, publication or certification is authorized. IE0–IE5 have been accepted; milestone close remains.
