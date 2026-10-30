# Derivation why-not

Planning opened 2026-10-30 for [issue #66](https://github.com/vasiloglou/gnd-public/issues/66):
when a derivation rule derives nothing, say which body step emptied the join,
with the binding counts before it, so a host can add the missing fact.

**Status: plan r3 and WN1 spec r3 were approved by the owner on 2026-10-30
([plan gate](001-plan-gate.md)).** Plan review closed by its stop rule after
round 2; r3 applies the round-2 repairs with no further round and carries no
review opinion. No phase is selected and nothing is implemented. `auto=false`.
Baseline `fb03739` (main after PR #64).

- [Canonical plan (r3, approved)](notes/derivation-why-not-plan.md)
- [WN1 spec (r3, approved)](notes/phase-WN1-spec.md)
- [Plan gate record](001-plan-gate.md)
- [Plan review round 1 disposition](notes/plan-review-r1-disposition.md), with reader notes 1-4
- [Plan review round 2 disposition](notes/plan-review-r2-disposition.md), with reader notes 1-4

Phases:
- WN1: the explanation kernel (status from GND's own evaluator, declared-order
  prefix counts, blocking step, row mode, ground-only descent, independent
  oracle, two work budgets);
- WN2: `gnd why-not`, `gnd.api.why_not`, output schema, pins, reference doc and
  release note;
- WN3: the two-gap repair loop as a packaged example, and a how-to;
- close.

Owner rulings and directions, 2026-10-30:
- WN-D8, quoted: "use four local reviewer agents for the plan and close review,
  as in recent milestones. Run plan review round 1 over r1." (instrument only);
- after round 1, quoted: "I accept the round-1 disposition's repair themes A-K.
  Apply them as r2, take the proposed answers where a decision is re-argued, and
  run the one confirmation round over the blocking themes.";
- after round 2, quoted: "I accept the round-2 disposition's repair themes L-S.
  Apply them as r3 with no further review round. Then I will decide on plan
  approval over r3."
- approval, quoted: "I approve plan r3 (SHA-256 fb590faa...441d) and WN1 spec
  r3 (SHA-256 78fbfe88...3faa), confirm WN-D3, D4 and D5, and take the proposed
  answers for WN-D1, D2, D6, D7, D9-D14 and spec D6."

Plan review:
- round 1 over r1 (plan `77928fb2…cc70`, spec `cbc99f26…1f03`): two
  request-changes, two approve-with-fixes; 35 findings, 8 distinct blocking,
  none refuted;
- round 2 (confirmation) over r2 (plan `b0308e35…630e`, spec `d1c87cb1…6f69`):
  two request-changes, two approve-with-fixes; 27 new findings, 4 distinct
  blocking, 25 self-inflicted (ratio 0.93). The stop rule holds, so no third
  round runs.

Open at the WN1 gate: the base commit, the forbidden-token list for the
anonymity test (only digests are committed), and any restated T13 counter
values.

Next action: an explicit `process-phase WN1 derivation-why-not` selection.
