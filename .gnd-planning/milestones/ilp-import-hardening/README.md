# ILP import hardening

Planning opened 2026-10-29 at the owner's request, as the successor to
[ILP learners](../ilp-learners/README.md) for the debt its close carried
into the mined-rule import.

**Status:** planning only. No plan or spec approval exists. `auto=false`.

- [Plan r1](notes/ilp-import-hardening-plan.md): four steps, IH0 → IH1 → IH2 → close. No learner runs.
  - **IH0:** a review of the ilp-learners source diff, `07f4d45^..fb03739`.
  - **IH1:** one public counting entry and one rendering pass for the mined import.
  - **IH2:** joins through an own-reference subtype, counted or refused by name.
  - **Close:** runs the full local CI on both Pythons before the PR merges.
- [IH0 spec (r1, draft)](notes/phase-IH0-spec.md)

**Open decisions:** IH-D1 to IH-D5 in the plan's §10; IH0-D1 to IH0-D4 in
the spec.

**Next action:** the owner rules on the plan's review instrument (IH-D5),
then on the plan and IH-D1 to IH-D4.
