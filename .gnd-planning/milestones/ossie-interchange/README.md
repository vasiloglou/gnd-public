# ossie-interchange

Planning opened 2026-11-10 at the owner's request: is GND compliant with
Apache Ossie (formerly Open Semantic Interchange), and what would it take?

GND is not Ossie-compliant today: it neither reads nor writes Ossie documents.
The plan targets Ossie's ontology layer (layer 4, `0.3.0.dev0`), which is
ORM-shaped. It exports and imports ontology documents validated by Ossie's own
tools at pinned commits, with a loss report for everything Ossie cannot state.
Ossie's RelationalAI converter (Ossie → PyRel) serves as an independent
consumer check.

**Status: plan r3, approved 2026-11-10** ([plan gate](001-plan-gate.md)). The light panel reviewed r2 on 2026-11-10 (5 of 6
seats succeeded; all asked for revision; [report](evidence/plan-review-r2/PANEL-REVIEW.md)).
r3 applies all 19 fixes and has not itself been reviewed. The owner ruled OD0–OD8 on
2026-11-10: light panel for review; ontology layer only; extension as
proposed; reorder roles; keep `Duration` as a deliberate divergence; a lossy
export exits 0 with a loss report; contribute `requires` → `require`
upstream (new phase OS6); and OS0 also tries relationalai 2.0. `auto=false`.

- [Plan r3](notes/ossie-interchange-plan.md)
- [OS0 spec r4](notes/phase-OS0-spec.md)
- [Light-panel review of r2](evidence/plan-review-r2/PANEL-REVIEW.md)

Phases: OS0 (pin, measure, decide; no code), OS1 (export core), OS2
(constraints and derivations as formulas), OS3 (import), OS4 (PyRel consumer
cross-check), OS5 (docs and skill), OS6 (upstream converter contribution);
then close.

The owner approved r3 without a second panel round. PR #159 merged the plan.
The [OS0 spec gate](002-OS0-spec-gate.md) records delegated approval. The
[independent review](notes/phase-OS0-claude-review.md) found the first census
too narrow. The [OS0 phase record](006-phase-OS0.md) closes that phase after
replaying the expanded 41-model census and parser controls. The
[refunds checkpoint](evidence/OS0/CHECKPOINT.md) shows the hand translation.

The [owner confirmed OD6](004-owner-OD6.md). The
[OS1 phase record](009-phase-OS1.md) closes the exporter after independent
review, focused regressions and the pinned validator/parser lane. Draft PR
[#160](https://github.com/vasiloglou/gnd-public/pull/160) carries the work.

Next: prepare the OS2 formula corpus before implementing the renderer. The
early OS5 documentation checkpoint can use the closed OS1 output.
