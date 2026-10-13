# PyRel applications

## Execution checkpoint — 2026-10-13

PA0, PA1 and PA2 are complete: [PA0](004-phase-PA0.md) freezes 61 obligations
and 137 controls; [PA1](005-phase-PA1.md) enables guarded native acceptance;
[PA2](006-phase-PA2.md) integrates independent computed derivations and claims.
PA2 current gates: 355 focused checks, 26 native direct tests, 137/137 full native
cases and 2,321 comparable GND/native row matches. The two A1 disagreements are
separately enumerated, and both engines reject those populations.

The effective plan is r1 plus [A1](notes/plan-amendment-a1.md), approved in
[003](003-plan-amendment.md). Next: PA3's native BookRec query/publication flow;
its [specification](notes/phase-PA3-spec.md) is preparation before its own gate.
Four phases remain. Named auto delegation persists; merge, release and
certification require separate owner authorization.

## Initial execution preparation

The owner invoked `process-milestone pyrel-applications auto=true` and selected
four local readers for plan/close review. [001-plan-gate.md](001-plan-gate.md)
records their readings and delegated approval of draft r1.
[PA0 preparation](002-phase-PA0-preparation.md) freezes 61 obligations and 124
controls; its corpus/legacy gates exit 0 and the native successor measurement
exits 1 for the actual guarded/derivation omissions. PA0's independent diff
review still needs a distinct terminal harness selection. No phase is complete;
PA1 remains dependent on PA0 completion. Approval delegation persists within
this milestone; merge, release and certification remain separately authorized.

## Opening history

Opened 2026-10-13 at the owner's request: functioning BookRec and expense
examples, useful tutorials, and the framework support needed to check them
with PyRel.

The [milestone plan](notes/pyrel-applications-plan.md) is draft r1. Opening this
milestone authorizes planning; it does not approve the plan, phase specs,
implementation, certification, publication or merge. Default `auto=false`.
Existing project and milestone records remain unchanged.

The intended result is two runnable local applications with native PyRel
queries and PyRel policy gates, a declared model agreement boundary, and
tutorials executed from a fresh installed package. The existing Python/GND
examples remain working learning paths.

Records belong here, one per material event, under the
[milestone record contract](../../../src/gnd/skills/gnd-orm-core/references/milestone-record-format.md).
Phase specs and review artifacts belong in `notes/`. No phase has run.

Next: review and accept the plan, then invoke
`process-phase PA0 pyrel-applications` to prepare the first owner-gated spec.
