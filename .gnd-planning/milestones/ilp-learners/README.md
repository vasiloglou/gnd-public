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
- **IL1 is complete:** [phase record](002-phase-IL1.md), merged in PR #56.
- **IL2 is complete:** [phase record](003-phase-IL2.md).
  [Spec r1](notes/phase-IL2-spec.md) was approved
  on 2026-10-27, with ILASP 4.4.1 under its non-commercial terms. The adapter
  is implemented. Invocation 1, the run of record, completed and was refused
  `empty-antecedent` (IL2-F7, recorded as is by the owner's ruling). The
  [adversarial review](notes/phase-IL2-agent-review.md) found 11 issues;
  IL2-D13 and IL2-D14 were ruled (a), and three refactors were executed.
  Merged in PR #57.
- **IL5 is complete:** [phase record](004-phase-IL5.md). Invocation 1 with
  `claude` completed and was admitted. IL5-Q1 and IL5-Q2 were ruled on
  2026-10-28: a cut-off run and a stray code fence each give no answer.
  Merged in PR #58.
- **IL3 is complete:** [phase record](005-phase-IL3.md). Merged in PR #60. Invocation 1 with wittgenstein's RIPPER completed and was
  admitted at support 4/5. The [adversarial review](notes/phase-IL3-agent-review.md)
  found 8 issues; 7 were fixed and IL3-Q1 is open for the owner. RIPPER is not
  deterministic under its seed (IL3-F5, IL3-Q3).
- **IL4 is complete:** [phase record](006-phase-IL4.md). Merged in PR #61. Invocation 1 with AMIE 4.0.0 on the synthetic staffing
  fixture completed; AMIE printed 8 rules, two hold, so the all-or-nothing
  import refused the set (`does-not-hold`), as predicted. The
  [adversarial review](notes/phase-IL4-agent-review.md) found 7 issues; 4
  were fixed, one accepted, and IL4-Q1 and IL4-Q2 are open for the owner.
- **The close is under way** ([close plan](notes/close-plan.md), approved
  2026-10-29). **Part A, the close repairs, is recorded:**
  [record](008-close-repairs.md), [spec r1 (approved)](notes/phase-IL-close-spec.md),
  [adversarial review](notes/phase-IL-close-agent-review.md). Every ruled
  "fix" question is fixed corpus-first; the review's 7 findings are fixed.
  ILC-F5 and ILC-F6 (goldens that moved beyond the spec's list) were
  accepted by the owner on 2026-10-29.

**Documents:**
- [Canonical plan (r3, approved)](notes/ilp-learners-plan.md)
- [IL1 spec (r3, approved)](notes/phase-IL1-spec.md)
- [IL1 phase record](002-phase-IL1.md)
- [IL2 spec (r1, approved)](notes/phase-IL2-spec.md)
- [IL2 phase record](003-phase-IL2.md)
- [IL5 phase record](004-phase-IL5.md)
- [IL2 adversarial review](notes/phase-IL2-agent-review.md)
- [IL5 spec (r1, approved)](notes/phase-IL5-spec.md)
- [IL3 spec (r1, approved)](notes/phase-IL3-spec.md)
- [IL3 phase record](005-phase-IL3.md)
- [IL4 spec (r1, approved)](notes/phase-IL4-spec.md)
- [IL4 phase record](006-phase-IL4.md)
- [IL6 spec (r1, approved)](notes/phase-IL6-spec.md)
- [IL6 phase record](007-phase-IL6.md)
- [Close plan (r1, approved)](notes/close-plan.md)
- [IL-close spec (r1, approved)](notes/phase-IL-close-spec.md)
- [IL-close part A record](008-close-repairs.md)
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
- none for part A; parts B to E are in progress.

**Next action:** close parts B to E: the plan repairs, the open-questions sweep, the four-reviewer close review and the close record.
