# Induction skill

Planning opened 2026-10-27 for IK6-Q1, which the
[induced-knowledge close](../induced-knowledge/012-milestone-close.md) carried as
its own milestone: a packaged skill for the induction loop (measure against
labels, discover, export to and import from a learner, re-check, then review).

**Status: plan r3 and IS1 spec r3 were approved by the owner on 2026-10-27
([plan gate](001-plan-gate.md)).** Plan review closed by its stop rule after
round 2; r3 applies the round-2 repairs with no further round and carries no
review opinion. No phase is selected and nothing is implemented. `auto=false`. Baseline `45c8603` (main after PR
#48), merged into this branch.

- [Canonical plan (r3, approved)](notes/induction-skill-plan.md)
- [IS1 spec](notes/phase-IS1-spec.md): **r4 draft (2026-11-25)**, a refresh of the approved r3
  against main `4f2945a9`, with three new decisions D21 to D23; no review and
  no ruling. r3 (approved) is in git history at `e74d882`
- [Plan gate record](001-plan-gate.md)
- [Plan review round 1 disposition](notes/plan-review-r1-disposition.md), with reader notes 1-4
- [Plan review round 2 disposition](notes/plan-review-r2-disposition.md), with reader notes 1-4

Phases:
- IS1: the skill `gnd-induce`, its routes and its pins;
- IS2: recorded skill runs and the tutorial rewrite (outline; blocked on IS1,
  `ilp-learners` IL1, #50, D11 and D12);
- close.

Owner rulings, 2026-10-27:
- D13, quoted: "use four local reviewer agents for the plan and close review,
  as in the induced-knowledge milestone" (instrument only);
- after round 1, quoted: "I accept the round-1 disposition's repairs A-L and
  its proposed answers for D17-D20. Apply them as r2 and run the one
  confirmation round." This accepts the round-1 disposition at `db374d7` and
  rules D17..D20;
- after round 2, quoted: "Apply the round-2 disposition's themes M-S as r3 with
  no further review round. Then I will decide on plan approval over r3." This
  accepts the round-2 disposition at `a23cd34`;
- approval, quoted: "I approve plan r3 (SHA-256 46e8e6c8...b0e7) and IS1 spec
  r3 (SHA-256 a3c29dca...443e)."

Plan review:
- round 1: four readers, all request-changes; 45 findings, 14 blocking (13
  distinct), none refuted;
- round 2 (confirmation): four approve-with-fixes; 33 findings, 1 blocking (a
  single routing regex), 28 self-inflicted. The stop rule holds, so no third
  round runs.

Open at gates: the IS1 base commit (also the D8 pin) and checkpoint C0 at the
IS1 gate; D11 (recordings) at the IS2 gate.

**IS1 done, 2026-11-25** ([record 002](002-phase-IS1.md)): `gnd-induce` ships
with its routes and pins, under `process-milestone induction-skill auto=true`.
The IS1 spec r4 was approved by delegated ruling; checkpoint C0 was shown to
the owner ("Keep them apart"). One reviewer (Codex), two rounds; eight
test-strength residuals carried (IS1-Q2).

**IS2:** the owner approved D11, the paid recordings, on 2026-11-25
([receipt](evidence/IS2/owner-statements.txt)). Next action: the IS2 spec, its
recording gate record with a run bound and cost ceiling, then the recordings
and Fable's tutorial rewrite.

**IS2 done, 2026-11-26** ([record 005](005-phase-IS2.md)): nine recorded
Haiku conversations over the refunds example under gate records
[003](003-IS2-recording-gate.md) and [004](004-IS2-recording-gate.md)
(USD 1.79 of USD 10); `gnd-induce` amended after checkpoint C1; the
learn-rules tutorial rewritten by Fable around six replays, approved at C2;
the wheel budget raised to 13 MiB at C2. Two review rounds, the second ended
by the stop rule; residuals IS2-Q1 to IS2-Q4. Next action: the milestone
close (plan D13: four local reviewer agents), with its plan repairs and
question sweep.
