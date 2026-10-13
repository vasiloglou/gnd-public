# PyRel applications

## Execution checkpoint — 2026-10-13

PA0 is complete in [004-phase-PA0.md](004-phase-PA0.md): 61 obligations,
137 controls, 151 corpus/verifier checks and 77 legacy/isolation checks.
The effective plan is r1 plus [A1](notes/plan-amendment-a1.md), approved in
[003](003-plan-amendment.md). Claude Code phase review is selected and completed
for PA0; the final owned hardening/native measurements are recorded separately.
Next: PA1 guarded checking and explicit acceptance. Native application acceptance
remains red; no other phase is complete. Auto delegation persists for this named
milestone; merge, release and certification remain separate owner actions.

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
