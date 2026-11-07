# rule-check-release

Planning opened 2026-11-07 for GitHub issue 118 (GR-D7): a release of
`get-nick-done` on PyPI that carries the rule-check flags, which are on main
and in no release. The published version is still 0.1.0.

**Status: plan r1 drafted, awaiting the owner's plan gate. The plan review has
not run (RL-D0). RR1's spec is a blocked draft.** This milestone prepares a
release and does not publish one: no upload, tag, GitHub release, `pypi`
environment or publisher registration, and issue 118 stays open until a
published release is verified. `auto=false`.

- [Plan (r1, draft)](notes/rule-check-release-plan.md)
- [RR1 spec (draft, blocked on RL-D1 and experiment E1)](notes/phase-RR1-spec.md)

Phases: RR1 candidate content (version, lock, manifests, release notes);
RR2 candidate build and installed acceptance; RR3 publication hand-over
dossier; close.

Pending owner decisions: RL-D0 (plan review), RL-D1 (version, 0.2.0
proposed), RL-D2 (which main content the release carries, in particular
whether it waits for rule-check-followups FU2 and FU3), RL-D3 to RL-D9.

Next action: the owner rules the plan's decisions and the plan gate; then
experiment E1 (the version bump over the full default lane on beast-3) and
the RR1 owner gate.
