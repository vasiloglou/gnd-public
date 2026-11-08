# report-output-fidelity

Planning opened 2026-11-07 for the two issues that `rule-check-followups`
split out by owner ruling (FD1, FD2): 111 (the model digest is a Python
`repr`, not reproducible by a caller) and 112 (text output prints projected
JSON for redaction and temporal models).

**Status: plan r3 approved (2026-11-07, [plan-gate record](001-plan.md)). ROF1
implemented ([record](002-phase-ROF1.md), PR 124); ROF2 implemented
([record](003-phase-ROF2.md), PR 127, stacked on 124); both await merge.**
ROF3 onward are outlines. `auto=false`.

- [Plan-gate record](001-plan.md)
- [ROF1 record](002-phase-ROF1.md)
- [ROF2 record](003-phase-ROF2.md)
- [Plan (r3, approved)](notes/report-output-fidelity-plan.md)
- [ROF1 spec (approved, implemented)](notes/phase-ROF1-spec.md)
- [ROF2 spec (approved, implemented)](notes/phase-ROF2-spec.md)
- ROF1 approval corpus: `tests/fixtures/rof1-projected-text/` (README = stories, `expected/` = answers), runner `tests/test_rof1_projected_text.py`
- [Codex review of r2](evidence/plan-review-r2/codex-review.md) and [triage](evidence/plan-review-r2/triage.md)
- [Digest census](evidence/census-r2/README.md)

Phases: ROF1 (112: check, validate), ROF2 (112: transition, admission, export
verification), ROF3 (111: canonical identity and producer), ROF4 (111: accept
both identities at every matching site), ROF5 (111: report emission,
blocked on D3), close.

ROF1-O1 ruled 2026-11-07: keep the `[reason: ...]` suffix.

ROF2 implemented (spec approved with "Approve, implement"; [record](003-phase-ROF2.md)),
on PR 127 (stacked on PR 124), awaiting merge. Corpus
`tests/fixtures/rof2-projected-text/`; changed-bytes census in
[evidence/ROF2-census/](evidence/ROF2-census/). With ROF1 and ROF2, issue 112's
text defect is fixed in code; the issue closes at the milestone close.

Next action: merge PR 124 then PR 127 (owner); rule ROF2-O1; then the ROF3
spec (issue 111) with process-phase.
