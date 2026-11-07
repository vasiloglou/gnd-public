# report-output-fidelity

Planning opened 2026-11-07 for the two issues that `rule-check-followups`
split out by owner ruling (FD1, FD2): 111 (the model digest is a Python
`repr`, not reproducible by a caller) and 112 (text output prints projected
JSON for redaction and temporal models).

**Status: plan r3 proposed. The owner ruled RF-D0 and D1-D6 as proposed
(2026-11-07). The one Codex review RF-D0 selects ran over r2 (`block`, 10
findings, all applied in r3; r3 was not re-reviewed). The plan gate is still
open, and new decision D7 (generated Pyrel plans) is open. Phase ROF1 spec
(r2) is a draft, blocked on the plan gate.** `auto=false`. No code has changed.

- [Plan (r3, proposed)](notes/report-output-fidelity-plan.md)
- [ROF1 spec (draft r2)](notes/phase-ROF1-spec.md)
- [Codex review of r2](evidence/plan-review-r2/codex-review.md) and [triage](evidence/plan-review-r2/triage.md)
- [Digest census](evidence/census-r2/README.md)

Phases: ROF1 (112: check, validate), ROF2 (112: transition, admission, export
verification), ROF3 (111: canonical identity and producer), ROF4 (111: accept
both identities at every matching site), ROF5 (111: report emission,
blocked on D3), close.

Next action: the owner's plan gate on r3 (and a ruling on D7);
then ROF1's corpus is authored and its spec goes to its own owner gate.
