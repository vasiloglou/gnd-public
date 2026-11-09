# rule-check-release

Planning opened 2026-11-07 for GitHub issue 118 (GR-D7): a release of
`get-nick-done` on PyPI that carries the rule-check flags, which are on main
and in no release before 0.2.0. **0.2.0 is published on PyPI (2026-11-08T17:24:56Z): the owner uploaded the retained `7c0f4d0e` files by hand with their own token (route (a)), and the served files are byte-identical to them ([step E](evidence/publication/step-E-served-files.txt)).**

**Status: plan r2 approved by the owner on 2026-11-07 ([plan-gate record](001-plan.md)). RR1 is implemented, reviewed and recorded ([record](002-phase-RR1.md)); its spec was approved by the owner on 2026-11-07 ("approved all", relayed). RR2's spec was approved by the owner on 2026-11-08 ("Approve as recommended"); RR2 is implemented and recorded ([record](003-phase-RR2.md)): candidate built from main `7c0f4d0e`, wheel sha256 `e323c19e…69e4`, sdist `f85818ea…5104`, release acceptance 14 passed on beast-3. RR3's spec was approved by the owner on 2026-11-08 ("Approve as recommended"); RR3 is implemented and recorded ([record](004-phase-RR3.md)): the hand-over dossier, three unapplied post-publication patches with a route-aware stale-text check, and `docs/releasing.md` stating both publication routes; implementation review by one reviewer (Codex, `revise`, J1 to J8, all fixed).** r1 was reviewed by one
reviewer (Codex, `revise`, 11 findings, all accepted and applied in r2); the RR1 diff by one reviewer (Codex, `revise`, 3 findings, fixed). The three phases prepared a
release and published nothing: no phase made an upload, tag, GitHub release,
`pypi` environment or publisher registration. The publication that followed was
the owner's (RL-D10, in the draft close): 0.2.0 is on PyPI, and issue 118 is
closed as completed. `auto=false`.

- [Plan (r2, approved)](notes/rule-check-release-plan.md)
- [Plan-gate record](001-plan.md)
- [E1 results: the version bump moves 47 default-lane tests](evidence/e1/README.md)
- [Codex review of r1](evidence/plan-review-r1/codex-review.md)
- [RR3 record](004-phase-RR3.md); [publication hand-over dossier](evidence/RR3/dossier.md); [RR3 spec (approved 2026-11-08)](notes/phase-RR3-spec.md); [Codex review of r1](notes/phase-RR3-codex-review.md); [implementation review](notes/phase-RR3-codex-review-impl.md)
- [RR2 spec (approved 2026-11-08)](notes/phase-RR2-spec.md); [Codex review of r1](notes/phase-RR2-codex-review.md)
- [RR1 record](002-phase-RR1.md); [RR1 spec (approved 2026-11-07)](notes/phase-RR1-spec.md); [per-file classification and moved digests (§13)](notes/phase-RR1-spec.md#13-classification-of-the-47-and-the-moved-digests-2026-11-07-appended-before-any-code)

Phases: RR1 candidate content (version, lock, manifests, release notes);
RR2 candidate build and installed acceptance; RR3 publication hand-over
dossier; close.

Ruled (owner, 2026-11-07): RL-D1, version 0.2.0; RL-D2, the release waits for rule-check-followups FU2 and FU3 (FU4 and FU5 do not gate).

RL-D5 route (owner, 2026-11-08, relayed): "Upload saved candidate", route (a), a token upload of the retained `7c0f4d0e` files, done by the owner by hand ([plan row](notes/rule-check-release-plan.md)).

RL-D0 and RL-D3 to RL-D9 ruled as proposed (owner, 2026-11-07, relayed). RL-D9, after E1 (owner, 2026-11-07, relayed): "Split (a)+(b) (Recommended)" (normalize the version in the one RF1 pin helper; regenerate the committed outputs whose purpose is to equal the current command's output, every moved digest listed first; no fix of the version in the test environment). Opt-in lanes (`evidence`, `census`): "Record as excluded (Recommended)".

Dossier actions 4 to 7 are done (RL-D10, recorded in the draft close).
- The owner pushed tag `v0.2.0` (`d84ad6d5` → `7c0f4d0e`) and created the
  [GitHub release](https://github.com/vasiloglou/gnd-public/releases/tag/v0.2.0).
- [PR 140](https://github.com/vasiloglou/gnd-public/pull/140) applies the
  post-publication patches; the owner merged it as `c239ad8e` (2026-11-09),
  and PR 133 (the draft close) as `8a3ae7aa`.
- Issue 118 is closed as completed (2026-11-09).

**Closed: the owner approved the close as proposed ("Accept as proposed", 2026-11-09; [close record](005-milestone-close.md), plan §12 approved).** Close review: one Codex reviewer, the owner's choice ("One Codex reviewer", 2026-11-09); [retained review](notes/close-codex-review.md): `revise`, L1 to L8, all reproduced and applied. The closing full lane on beast-3 at main `25e432e4`: 18251 passed, 0 failed, the 2 known `test_public_optional.py` errors only. The same ruling:
- accepted two residuals: the 0.1.0 control's PyPI download, and no Ubuntu profile for 0.2.0;
- carried the deferred fixtures refactor to the milestone that prepares the release after 0.2.0;
- accepted the dossier's owner checks 1, 1.1, 1.2 and 1.3 as residuals.

Merging the close record is the owner's.

Done: route (a) upload (owner, by hand) and the step E served-file check (served wheel and sdist equal `e323c19e…69e4` and `f85818ea…5104`; a fresh index install gives `gnd 0.2.0`). PR 131 (RR3) merged as `36e47981`; main's `src` has since moved past the candidate (ROF1 to ROF3), which does not affect the published files.
