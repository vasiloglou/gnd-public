# Induction skill

Planning opened 2026-10-27 for IK6-Q1, which the
[induced-knowledge close](../induced-knowledge/012-milestone-close.md) carried as
its own milestone: a packaged skill for the induction loop (measure against
labels, discover, export to and import from a learner, re-check, then review).

**Status: plan r3 and IS1 spec r3. Plan review closed by its stop rule after
round 2; r3 applies the round-2 repairs with no further round and carries no
review opinion. Not approved.** `auto=false`. Baseline `45c8603` (main after PR
#48), merged into this branch.

- [Canonical plan (r3)](notes/induction-skill-plan.md)
- [IS1 draft spec (r3)](notes/phase-IS1-spec.md)
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
  accepts the round-2 disposition at `a23cd34`.

Plan review:
- round 1: four readers, all request-changes; 45 findings, 14 blocking (13
  distinct), none refuted;
- round 2 (confirmation): four approve-with-fixes; 33 findings, 1 blocking (a
  single routing regex), 28 self-inflicted. The stop rule holds, so no third
  round runs.

Pending owner decisions: plan approval over r3. D1..D12 and D14..D16 remain
proposed (plan §10).

Next action: the owner decides plan approval over r3. After that, an explicit
`process-phase IS1 induction-skill` selection.
