# release-0.3.0

Planning opened 2026-11-10 on the owner's request to cut a new version now
that Ossie interchange is on main. 0.2.0 is the latest published version;
nothing here is published.

**Status: plan r2 approved by the owner on 2026-11-10 ([plan-gate
record](001-plan-gate.md)). r1 was reviewed by one
reviewer (Codex, `revise`, 9 findings, all accepted and applied in r2); r2 was
not re-reviewed. No phase spec is approved. `auto=false`.**

- [Plan (r2, approved; §12 amendment proposed, not ruled)](notes/release-0.3.0-plan.md)
- [RN1 spec (blocked draft r2)](notes/phase-RN1-spec.md)
- [Codex review of r1](evidence/plan-review-r1/codex-review.md)
- [E1 results: the bump moves 35 tests; main's lane is red by 26](evidence/e1/README.md)

Phases: RN1 candidate content (version, lock, manifests, release notes with
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

Next action: the owner rules RN-D12 (plan §12): repair main's lane in a new
phase RN0 before RN1, or not.
