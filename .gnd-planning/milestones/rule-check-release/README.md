# rule-check-release

Planning opened 2026-11-07 for GitHub issue 118 (GR-D7): a release of
`get-nick-done` on PyPI that carries the rule-check flags, which are on main
and in no release. The published version is still 0.1.0.

**Status: plan r2 approved by the owner on 2026-11-07 ([plan-gate record](001-plan.md)); no phase spec is approved. r1 was reviewed by one
reviewer (Codex, `revise`, 11 findings, all accepted and applied in r2); r2 carries
no review opinion. RR1's spec is a blocked draft.** This milestone prepares a
release and does not publish one: no upload, tag, GitHub release, `pypi`
environment or publisher registration, and issue 118 stays open until a
published release is verified. `auto=false`.

- [Plan (r2, approved)](notes/rule-check-release-plan.md)
- [Plan-gate record](001-plan.md)
- [Codex review of r1](evidence/plan-review-r1/codex-review.md)
- [RR1 spec (draft, blocked on experiment E1 and its own owner gate)](notes/phase-RR1-spec.md)

Phases: RR1 candidate content (version, lock, manifests, release notes);
RR2 candidate build and installed acceptance; RR3 publication hand-over
dossier; close.

Ruled (owner, 2026-11-07): RL-D1, version 0.2.0; RL-D2, the release waits for rule-check-followups FU2 and FU3 (FU4 and FU5 do not gate).

RL-D0 and RL-D3 to RL-D9 ruled as proposed (owner, 2026-11-07, relayed); RL-D9 stays deferred to after E1.

Next action: experiment E1 (the version bump over the full default lane on beast-3,
plus the grep inventory), then the RR1 spec's owner gate (process-phase). RR2 waits for
FU2 and FU3 on main.
