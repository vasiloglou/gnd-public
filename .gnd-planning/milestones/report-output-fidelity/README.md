# report-output-fidelity

Planning opened 2026-11-07 for the two issues that `rule-check-followups`
split out by owner ruling (FD1, FD2): 111 (the model digest is a Python
`repr`, not reproducible by a caller) and 112 (text output prints projected
JSON for redaction and temporal models).

History (status as of 2026-11-08; superseded by the 2026-11-09 status below): **plan r3 approved (2026-11-07, [plan-gate record](001-plan.md)). ROF1
([record](002-phase-ROF1.md)) and ROF2 ([record](003-phase-ROF2.md)) merged to
main (PR 124, PR 127). ROF3 ([record](004-phase-ROF3.md)) merged (PR 132).
ROF4 implemented ([record](005-phase-ROF4.md)), on branch
`claude/rof4-accept-identities`, awaiting its PR and merge.**
ROF5 onward are outlines. `auto=false`.

**Status, 2026-11-09: closed.** The owner gave the close ruling ("Approve
and merge") over the [close record](006-milestone-close.md) and the seven
plan [section 11](notes/report-output-fidelity-plan.md) amendments, which are
approved and in effect. ROF1-ROF4 are merged (PRs 124, 127, 132, 138). ROF5
is withdrawn by the owner's ruling R1 (no emission in this milestone).
Issues 111 and 112 are closed. The close review ran (one Codex reviewer,
`block`, 10 findings, all fixed), and the full-suite close runs are in
(every failure passed on rerun). The close lands with the owner's merge of
PR 145.

History (status as of 2026-11-09, before the close ruling): the close was
drafted and reviewed, the full-suite runs were in, and it awaited the
owner's close ruling.

- [Plan-gate record](001-plan.md)
- [ROF1 record](002-phase-ROF1.md)
- [ROF2 record](003-phase-ROF2.md)
- [ROF3 record](004-phase-ROF3.md)
- [ROF4 record](005-phase-ROF4.md)
- [Milestone close record (close ruling given 2026-11-09)](006-milestone-close.md)
- [Plan (r3, approved)](notes/report-output-fidelity-plan.md)
- [ROF1 spec (approved, implemented)](notes/phase-ROF1-spec.md)
- [ROF2 spec (approved, implemented)](notes/phase-ROF2-spec.md)
- [ROF3 spec (approved, implemented)](notes/phase-ROF3-spec.md)
- [ROF4 spec (approved, implemented)](notes/phase-ROF4-spec.md)
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
passed. Implemented (record [005-phase-ROF4.md](005-phase-ROF4.md)): 79 passed;
full suite equal to the base. Next actions: the owner's ruling on ROF4-O1
(the walk report echoes the supplied pin) and R1 (the D3 re-ask), then the
PR's merge. Issue 111 stays open until the milestone close.
