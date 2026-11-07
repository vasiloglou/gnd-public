# report-output-fidelity

Planning opened 2026-11-07 for the two issues that `rule-check-followups`
split out by owner ruling (FD1, FD2): 111 (the model digest is a Python
`repr`, not reproducible by a caller) and 112 (text output prints projected
JSON for redaction and temporal models).

**Status: plan r3 approved (2026-11-07, [plan-gate record](001-plan.md)). ROF1
implemented (spec approved with "Approve, implement"; [record](002-phase-ROF1.md)),
on PR 124, awaiting merge.** ROF2 onward are outlines. `auto=false`.

- [Plan-gate record](001-plan.md)
- [ROF1 record](002-phase-ROF1.md)
- [Plan (r3, approved)](notes/report-output-fidelity-plan.md)
- [ROF1 spec (approved, implemented)](notes/phase-ROF1-spec.md)
- ROF1 approval corpus: `tests/fixtures/rof1-projected-text/` (README = stories, `expected/` = answers), runner `tests/test_rof1_projected_text.py`
- [Codex review of r2](evidence/plan-review-r2/codex-review.md) and [triage](evidence/plan-review-r2/triage.md)
- [Digest census](evidence/census-r2/README.md)

Phases: ROF1 (112: check, validate), ROF2 (112: transition, admission, export
verification), ROF3 (111: canonical identity and producer), ROF4 (111: accept
both identities at every matching site), ROF5 (111: report emission,
blocked on D3), close.

Next action: merge PR 124 (owner), rule ROF1-O1, then the ROF2 spec (process-phase).
