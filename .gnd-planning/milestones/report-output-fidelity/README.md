# report-output-fidelity

Planning opened 2026-11-07 for the two issues that `rule-check-followups`
split out by owner ruling (FD1, FD2): 111 (the model digest is a Python
`repr`, not reproducible by a caller) and 112 (text output prints projected
JSON for redaction and temporal models).

**Status: plan r3 approved (2026-11-07, [plan-gate record](001-plan.md)). ROF1
([record](002-phase-ROF1.md)) and ROF2 ([record](003-phase-ROF2.md)) merged to
main (PR 124, PR 127). ROF3 ([record](004-phase-ROF3.md)) merged (PR 132).
ROF4 spec approved, corpus authored, awaiting the go-ahead to implement.**
ROF5 onward are outlines. `auto=false`.

- [Plan-gate record](001-plan.md)
- [ROF1 record](002-phase-ROF1.md)
- [ROF2 record](003-phase-ROF2.md)
- [ROF3 record](004-phase-ROF3.md)
- [Plan (r3, approved)](notes/report-output-fidelity-plan.md)
- [ROF1 spec (approved, implemented)](notes/phase-ROF1-spec.md)
- [ROF2 spec (approved, implemented)](notes/phase-ROF2-spec.md)
- [ROF3 spec (approved, implemented)](notes/phase-ROF3-spec.md)
- [ROF4 spec (approved)](notes/phase-ROF4-spec.md)
- ROF4 approval corpus: `tests/fixtures/rof4-accept-identities/`, runner `tests/test_rof4_accept_identities.py`
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

ROF2-O1 ruled 2026-11-08: the error type stays in `--format json` only.

ROF3 implemented: canonical model identity and `gnd validate --identity`
([spec](notes/phase-ROF3-spec.md), [record](004-phase-ROF3.md)); corpus
`tests/fixtures/rof3-model-identity/`. Issue 111 stays open (ROF4 accepts the
identity at matching sites; reports keep the legacy digest per D3).

ROF3-O1 ruled 2026-11-08: accept the refusal of a mutated non-string
declaration key in `reference_model_digest`.

ROF3 merged (PR 132, 6058c674).

ROF4 spec r1 approved 2026-11-08 ([phase-ROF4-spec.md](notes/phase-ROF4-spec.md),
D1-D6 as proposed), on branch `claude/rof4-accept-identities`. Corpus
`tests/fixtures/rof4-accept-identities/` (README = stories, `expected/` =
answers), runner `tests/test_rof4_accept_identities.py`, red: 22 failed, 55
passed. Next action: the owner's go-ahead to implement.
