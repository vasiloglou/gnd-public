# rule-check-release

Planning opened 2026-11-07 for GitHub issue 118 (GR-D7): a release of
`get-nick-done` on PyPI that carries the rule-check flags, which are on main
and in no release. The published version is still 0.1.0.

**Status: plan r2 approved by the owner on 2026-11-07 ([plan-gate record](001-plan.md)). RR1 is implemented, reviewed and recorded ([record](002-phase-RR1.md)); its spec was approved by the owner on 2026-11-07 ("approved all", relayed). RR2 and RR3 have no spec.** r1 was reviewed by one
reviewer (Codex, `revise`, 11 findings, all accepted and applied in r2); the RR1 diff by one reviewer (Codex, `revise`, 3 findings, fixed). This milestone prepares a
release and does not publish one: no upload, tag, GitHub release, `pypi`
environment or publisher registration, and issue 118 stays open until a
published release is verified. `auto=false`.

- [Plan (r2, approved)](notes/rule-check-release-plan.md)
- [Plan-gate record](001-plan.md)
- [E1 results: the version bump moves 47 default-lane tests](evidence/e1/README.md)
- [Codex review of r1](evidence/plan-review-r1/codex-review.md)
- [RR1 record](002-phase-RR1.md); [RR1 spec (approved 2026-11-07)](notes/phase-RR1-spec.md); [per-file classification and moved digests (§13)](notes/phase-RR1-spec.md#13-classification-of-the-47-and-the-moved-digests-2026-11-07-appended-before-any-code)

Phases: RR1 candidate content (version, lock, manifests, release notes);
RR2 candidate build and installed acceptance; RR3 publication hand-over
dossier; close.

Ruled (owner, 2026-11-07): RL-D1, version 0.2.0; RL-D2, the release waits for rule-check-followups FU2 and FU3 (FU4 and FU5 do not gate).

RL-D0 and RL-D3 to RL-D9 ruled as proposed (owner, 2026-11-07, relayed). RL-D9, after E1 (owner, 2026-11-07, relayed): "Split (a)+(b) (Recommended)" (normalize the version in the one RF1 pin helper; regenerate the committed outputs whose purpose is to equal the current command's output, every moved digest listed first; no fix of the version in the test environment). Opt-in lanes (`evidence`, `census`): "Record as excluded (Recommended)".

Next action: RR2's spec and its owner gate (build and installed acceptance of a candidate). RR2 waits for
FU3 on main (FU2 is on main).
