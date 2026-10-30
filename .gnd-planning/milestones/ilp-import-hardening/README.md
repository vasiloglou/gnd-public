# ILP import hardening

Planning opened 2026-10-29 at the owner's request, as the successor to
[ILP learners](../ilp-learners/README.md) for the debt its close carried
into the mined-rule import.

**Status:** planning only. No plan or spec approval exists. `auto=false`.
Plan r1 had one reader's review (IH-D5, owner-ruled): request-changes, 14
findings, all applied in r2 ([disposition](notes/plan-review-r1-disposition.md)).
r2 bytes carry no review opinion.

- [Plan r2](notes/ilp-import-hardening-plan.md): four steps, IH0 → IH1 → IH2 → close. No learner runs.
  - **IH0:** a review of IL's own source merges (37 files), as one change.
  - **IH1:** one public counting entry for the mined import, building its relation table and pairs once.
  - **IH2:** joins through an own-reference subtype, counted or refused by name.
  - **Close:** runs the full local CI on both Pythons before the PR merges.
- [IH0 spec (r2, draft)](notes/phase-IH0-spec.md)

**Open decisions:** IH-D1 to IH-D4, IH-D6, IH1-D1 and IH1-D2 in the plan's
§10 (IH-D5 is ruled); IH0-D1 to IH0-D4 in the spec.

**Next action:** the owner approves plan r2 or amends it, and rules on the
open decisions.
