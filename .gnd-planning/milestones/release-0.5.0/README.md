# release-0.5.0

Opened on 2026-11-23 at the owner's request ("Release 0.5.0"). **RW1 is on
main. RW2's installed probes are written and wait for the owner's merge; no
candidate is built.** The four milestones the owner made the release wait for are
merged to main:
[literature-host-interfaces](../literature-host-interfaces/README.md),
[reviewed-vocabulary-growth](../reviewed-vocabulary-growth/README.md),
[pins-and-review-check](../pins-and-review-check/README.md) and
[ossie-relational-bundle](../ossie-relational-bundle/README.md), each with
its close record; the plan's §14 has the last one's history. Nothing is
built or published.

RW2 began on 2026-11-25 after the owner merged RW1 (pull request 282). Its
[pre-freeze record](003-RW2-pre-freeze.md) has the probes, their rehearsal
and two review rounds. The freeze, the two builds and the acceptance run on
beast-3 follow the merge of the probes pull request.

RW1 started on 2026-11-24, was held for ossie-relational-bundle, and resumed
on 2026-11-25. Its [record](002-phase-RW1.md) has the result: the version is
0.5.0 on the RW1 branch, the notes have one 0.5.0 section headed by the
Ossie relational files (the owner's choice), and the default lane has no
failure at `4a73af2e`.

The plan's §11 and the gate record describe the first two milestones as they
stood when the plan was approved. The plan's §12 to §14 and the milestones'
own READMEs give their current state.

It will carry what merged after 0.4.0: include roots on more routes, the
PyRel rules programs for literature-style models, aggregate COUNT
certificates, the Ossie relational files, and what the other milestones
ship.

- [Plan r5](notes/release-0.5.0-plan.md): r1 reviewed by the standard GND
  panel, amended in §11, approved at r2 by delegated ruling. §12 to §14
  record the owner's later dependency rulings, a default-lane baseline of
  main and the dependencies' arrival.
- [Plan gate](001-plan-gate.md): the review, its disposition and the ruling.
- [RW1 record](002-phase-RW1.md) and [RW1 spec r7](notes/phase-RW1-spec.md):
  candidate content, with both rulings and the owner's headline ruling.
- [E1 summary](evidence/RW1/e1-summary.md),
  [the lanes on the RW1 tree](evidence/RW1/t7-lanes.md),
  [notes reconciliation](evidence/RW1/notes-reconciliation.md) and
  [the 0.4.0 comparisons](evidence/RW1/old-version-probes.md).
- Review rounds [1](notes/reviews/phase-RW1-r1/FINDINGS.md) and
  [2](notes/reviews/phase-RW1-r2/FINDINGS.md) over the RW1 diff.
- [RW2 spec](notes/phase-RW2-spec.md), its
  [pre-freeze record](003-RW2-pre-freeze.md), the
  [0.4.0 controls](evidence/RW2/controls-0.4.0.md) and the
  [probe rehearsal](evidence/RW2/probes-rehearsal.md).

Three phases prepare the release and publish nothing: RW1 candidate content,
RW2 candidate build and installed acceptance, RW3 publication hand-over.
Publication is a separate stage in which each act runs on the owner's
request.

Next action: the owner's merge decision on the RW2 probes pull request. The
main commit it makes is the freeze commit: the freeze checks, the two builds,
the acceptance run and the two oracle lanes run at it.
