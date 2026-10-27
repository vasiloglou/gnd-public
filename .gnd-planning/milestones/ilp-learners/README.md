# ILP learners

Planning opened 2026-10-27 at the owner's request, as the successor to
[induced knowledge](../induced-knowledge/README.md). The aim is to connect more
learners to the ILP bridge, which shipped with Popper only and never ran it.

**Status:** plan r3 and IL1 spec r3 were **approved by the owner on 2026-10-27**
([plan gate](001-plan-gate.md)). Plan review is closed by its stop rule.
- **Round 1:** r1 was reviewed by four local readers. All four asked for
  changes: 47 findings, 14 blocking, all reproduced.
- **Round 2 (confirmation):** r2 got four approve-with-fixes. 13 of the 14
  blockers were resolved and one partially; there were 18 new non-blocking
  findings, all introduced by r2.
- **r3** applies the round-2 repairs and D13 at the owner's direction, with no
  further review round. **r3 bytes carry no review opinion.**
- **Nothing else exists:** no phase selection, install or implementation.

**Documents:**
- [Canonical plan (r3, approved)](notes/ilp-learners-plan.md)
- [IL1 spec (r3, approved)](notes/phase-IL1-spec.md)
- [Plan gate record](001-plan-gate.md)
- [Plan review round 1 disposition](notes/plan-review-r1-disposition.md), with
  reader notes 1–4 and the [r1 snapshot](evidence/plan-review-r1/)
- [Plan review round 2 disposition](notes/plan-review-r2-disposition.md), with
  reader notes 1–4 and the [r2 snapshot](evidence/plan-review-r2/)

**Owner answers and rulings, 2026-10-27:**
- **Adapters,** quoted: "ILASP / FastLAS (ASP),Boolean rule sets,AMIE-style
  miner,LLM proposer".
- **Live runs,** quoted: "Yes, one recorded run each".
- **Review instrument** (the option chosen): four local reviewer agents.
- **After round 1,** quoted: "I approve the round-1 disposition's repairs and
  its proposed answers: D2 yes (scratch prefix, downloads approved per gate),
  D8 at the IL5 gate, D9 widen within /1, D10 all-or-nothing, D11 holds only,
  D12 add the join check in IL1."
- **After round 2,** quoted: "Apply themes A–I as r3 with no further review
  round, D13 yes. Then I will decide on plan approval over r3."
- **Approval,** quoted: "I approve plan r3 (SHA-256 329449d8…6281) and IL1
  spec r3 (SHA-256 83138d48…0f30)."

**Six phases, run serially:** IL1 registry, join check and a real Popper run →
IL2 ILASP → IL5 LLM proposer → IL3 rule sets → IL4 AMIE-style miner → IL6
comparison walk and docs. Close is separate.

**Open at gates:**
- IL1-D3 (installs and downloads) and IL1-D8 (licences);
- plan D8 (the LLM run), at the IL5 gate.

**Next action:** an explicit `process-phase IL1 ilp-learners`, whose gate rules
IL1-D3, IL1-D5 and IL1-D8.
