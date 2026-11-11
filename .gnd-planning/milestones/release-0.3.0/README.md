# release-0.3.0

Planning opened 2026-11-10 on the owner's request to cut a new version now
that Ossie interchange is on main. 0.2.0 is the latest published version;
nothing here is published.

**Status: plan r2 approved by the owner on 2026-11-10 ([plan-gate
record](001-plan-gate.md)). r1 was reviewed by one
reviewer (Codex, `revise`, 9 findings, all accepted and applied in r2); r2 was
not re-reviewed. No phase spec is approved. `auto=false`.**

- [Plan (r2, approved; §12 amendment approved 2026-11-10)](notes/release-0.3.0-plan.md)
- [RN2 spec (awaiting owner review)](notes/phase-RN2-spec.md)
- [RN0 record](002-phase-RN0.md); [RN0 spec (approved 2026-11-10)](notes/phase-RN0-spec.md); [diff review](notes/phase-RN0-codex-review.md)
- [RN1 record](003-phase-RN1.md); [RN1 spec (approved 2026-11-11)](notes/phase-RN1-spec.md); [diff review](notes/phase-RN1-codex-review.md); [moved digests](evidence/e1/moved-digests.md)
- [Codex review of r1](evidence/plan-review-r1/codex-review.md)
- [E1 results: the bump moves 35 tests; main's lane is red by 26](evidence/e1/README.md)

Phases: RN0 repair of main's default lane (added by the §12 amendment); RN1
candidate content (version, lock, manifests, release notes with
the Ossie block); RN2 candidate build and installed acceptance; RN3
publication hand-over; then a publication stage of owner acts (RN-D5, ruled),
each on the owner's request at that time; close.

Ruled (owner, 2026-11-10): RN-D1, version 0.3.0; RN-D2 in part, the release
includes PR 161 (merged, main `2490dd77`).

RN-D0 and RN-D3 to RN-D11 ruled as proposed (owner, 2026-11-10, "Approve as
proposed"). RN1 is blocked on experiment E1, which runs only after the plan
gate, and on the per-file handling ruled after it.

E1 ran on 2026-11-11 (UTC). The bump moves the same 31 recorded outputs as
the 0.2.0 bump, plus 4 release-version cases the notes edit settles. It also
showed main's default lane red by 26 tests: 6 since model composition, 20
more since the Ossie merge.

RN-D12 ruled (owner, 2026-11-10): "Yes, add RN0". RN0's spec classifies the
24 red guards: 11 are stale counts, pins or inventories and one is a missing
guard entry; 12 report real findings in the Ossie modules (entry-point
imports without a policy row, two query budgets exceeded, JSON read outside
the shared reader, identity sites outside the exact lists).

RN0's spec was approved by the owner on 2026-11-10 ("Approve as recommended").
RN0 is implemented, reviewed and recorded ([record](002-phase-RN0.md)): the
24 guards exit 0, the Ossie outputs are byte-identical over the census, and
the default lane at `326a1900` lists only the 2 known errors and RN1's two
tests. Review: one reviewer (Codex, `revise`, K1 and K2, both fixed). The
opt-in Ossie oracle lane did not run.

PR 162 is merged (main `d7317d25`, 2026-11-11). RN1's spec is draft r3 with
its measured inputs ([moved digests](evidence/e1/moved-digests.md)).

RN1's spec was approved by the owner on 2026-11-11 ("Approve, start RN1").
RN1 is implemented, reviewed and recorded ([record](003-phase-RN1.md)):
version 0.3.0 declared, 30 pins re-recorded, the 0.3.0 notes written as
prepared and not published, and the default lane at `d78e576c` clean
(19,016 passed, the 2 known errors). Review: one reviewer (Codex, `revise`,
F1 to F7, all fixed).

PR 163 is merged (main `f9f502d9`, 2026-11-11); main declares 0.3.0. RN2's
spec is drafted with its five probes measured on the 0.3.0 tree and on the
published 0.2.0 wheel.

Next action: the owner rules the RN2 spec gate and its decisions D1 to D6
(D5 is the Ossie oracle lane).
