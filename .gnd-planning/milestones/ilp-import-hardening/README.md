# ILP import hardening

Planning opened 2026-10-29 at the owner's request, as the successor to
[ILP learners](../ilp-learners/README.md) for the debt its close carried
into the mined-rule import.

**Status:** plan r2 approved by the owner on 2026-10-29, with its proposed
rulings ([plan gate](001-plan-gate.md)). On 2026-10-30 the owner delegated
the rest of this milestone (`process-milestone ilp-import-hardening auto`):
spec, plan and close rulings within it. Merge, publication, paid calls and
certification stay the owner's.
Plan r1 had one reader's review (IH-D5, owner-ruled): request-changes, 14
findings, all applied in r2 ([disposition](notes/plan-review-r1-disposition.md)).
r2 bytes carry no review opinion.

- [Plan r2](notes/ilp-import-hardening-plan.md): four steps, IH0 → IH1 → IH2 → close. No learner runs.
  - **IH0:** a review of IL's own source merges (37 files), as one change.
  - **IH1:** one public counting entry for the mined import, building its relation table and pairs once.
  - **IH2:** joins through an own-reference subtype, counted or refused by name.
  - **Close:** runs the full local CI on both Pythons before the PR merges.
- [IH0 spec (r2, draft)](notes/phase-IH0-spec.md)

**IH0 done** ([record](002-phase-IH0.md)): four readers, 13 finding rows, no
blocking; five fixed with regressions, E, F and J assigned to IH1, three
carried ([triage](notes/phase-IH0-triage.md)).

**IH0-D4, ruled 2026-10-29 (o):** "Keep both held". The LLM threshold check
and Popper's binary and infix spellings stay unapplied.

**IH1 done** ([record](003-phase-IH1.md)): one public counting entry, built
once, with the owner's IH1-D3 to D5 (o). One reviewer: no blocking; two
hardening and three completeness findings, all fixed.

**IH2 done** ([record](004-phase-IH2.md)), under a delegated approval
(auto=true) of its [spec](notes/phase-IH2-spec.md): `own-reference-join`
refuses a variable over two families, or over references of more than one
kind of value, before any count. One reviewer, then the close review, found
and fixed two exit-70 shapes and one false refusal.

**Closed locally** ([close record](005-milestone-close.md)), under a delegated
close ruling (auto=true). The workflow's steps passed on Python 3.13 and 3.11
on clean clones of the PR head ([CI run](evidence/close/ci-run.txt)); four
close readers' findings are dispositioned ([close review](notes/close-review.md)).

**Next action:** owner acceptance, and the owner's merge of vasiloglou/gnd-public#65.
