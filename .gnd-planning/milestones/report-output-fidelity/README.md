# report-output-fidelity

Planning opened 2026-11-07 for the two issues that `rule-check-followups`
split out by owner ruling (FD1, FD2): 111 (the model digest is a Python
`repr`, not reproducible by a caller) and 112 (text output prints projected
JSON for redaction and temporal models).

**Status: plan r2 proposed. The owner ruled RF-D0 and D1-D6 as proposed
(2026-11-07); the plan gate is still open, and the one Codex review RF-D0
selects is pending. Phase ROF1 spec is a draft, blocked on the plan gate.**
`auto=false`. No code has changed.

- [Plan (r2, proposed)](notes/report-output-fidelity-plan.md)
- [ROF1 spec (draft)](notes/phase-ROF1-spec.md)

Phases: ROF1 (112: check, validate), ROF2 (112: transition, admission, export
verification), ROF3 (111: canonical identity and producer), ROF4 (111: accept
both identities at every comparison site), ROF5 (111: report emission,
blocked on D3), close.

Next action: Codex review of the plan, triage, then the owner's plan gate;
then ROF1's corpus is authored and its spec goes to its own owner gate.
