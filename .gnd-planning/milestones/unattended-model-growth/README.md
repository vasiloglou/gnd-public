# unattended-model-growth

Planning opened 2026-11-07 for issues
[#104](https://github.com/vasiloglou/gnd-public/issues/104),
[#74](https://github.com/vasiloglou/gnd-public/issues/74),
[#75](https://github.com/vasiloglou/gnd-public/issues/75) and
[#76](https://github.com/vasiloglou/gnd-public/issues/76): growing one
model over many documents with no human reviewer, without overstating evidence
or invalidating admitted facts. A later wave (73, 77, 78, 95) is not in this
milestone.

**Status: plan r1.2 approved at the plan gate on 2026-11-07 ([record](001-plan.md); the owner's reply "approved all", relayed). The owner also ruled the
decisions UG-D0 to UG-D9 the same day. Plan review round 1 (four local readers, UG-D1 (a)) ran over r1.1
and its accurate repairs are in r1.2; no confirmation round was run. The UG1 spec (r1.3) was approved at its gate and UG1 is implemented as tests only
([record](002-phase-UG1.md)); UG2 is implemented and merged (PR 147); UG3 is implemented and merged (PR 149; [part A](004-phase-UG3a.md), [part B](005-phase-UG3b.md)); UG4 is implemented and merged (PR 151, `dd3c35a5`; [record](006-phase-UG4.md)). The milestone close is recorded in [007-close.md](007-close.md) on branch `claude/ug-close`, with one blocking close-review fix; owner acceptance and merge of the close are pending. Issues 74, 75 and 76 are closed (2026-11-08); 104 is open.**
`auto=false`.

**Headline.** Most of the four issues is already on main, from the closed
[model-growth-guardrails](../model-growth-guardrails/README.md) milestone (74,
75, 76) and PR 106 (104, items 1 to 4). What is genuinely open: 104 item 5's
second option (admit a clean-population constraint over a populated fact
type), and a gap found while planning: a growth round cannot declare its own
new source document through `gnd evolve`. The plan therefore starts with an
acceptance replay that measures the shipped behavior, then offers the open
items as owner decisions.

- [Plan-gate record](001-plan.md)
- [Canonical plan (r1.2, approved)](notes/unattended-model-growth-plan.md)
- [Plan review round 1: disposition](notes/plan-review-r1-disposition.md)
- [UG1 spec (r1.3, approved)](notes/phase-UG1-spec.md): acceptance replay and issue
  disposition, test-only
- [UG2 spec (r1, approved 2026-11-09, all decisions as proposed)](notes/phase-UG2-spec.md): population-checked
  constraint admission; corpus approved
- [UG2 record](003-phase-UG2.md): implemented, one-reviewer diff review applied; merged in PR 147 (`5c6a0c5f`)
- [UG3a record](004-phase-UG3a.md): span counts and `validate --require-documents` (issue 74); one-reviewer diff review applied; merged in PR 149 (`ad454305`)
- [UG3b record](005-phase-UG3b.md): the `source-document` evolve operation (issues 74 and 104); one-reviewer diff review applied; merged in PR 149 (`ad454305`)
- [UG4 spec (r1, approved 2026-11-09, all decisions as proposed)](notes/phase-UG4-spec.md): documentation, skill pointer and issue follow-ups
- [UG4 record](006-phase-UG4.md): docs and skill prose, one guard test; one-reviewer diff review applied; merged in PR 151 (`dd3c35a5`). [Drafted issue follow-ups](notes/ug4-issue-followups.md) (not posted)
- [Milestone close](007-close.md): union gate, parity table, four close readers, question sweep, plan close note `(c1)`
- [UG3 spec (r1, approved 2026-11-09, all decisions as proposed; corpus approved the same day)](notes/phase-UG3-spec.md): span counts and `--require-documents` (part A), a `source.documents` evolve locator (part B)
- Phases (all done): UG1 acceptance replay (test-only); UG2 population-checked
  constraint admission; UG3 the unattended source header across rounds; UG4 documentation and
  dispositions; then the close.

**Owner rulings, 2026-11-07** (plan §10, "Owner ruling" column): UG-D2 (b)
build the population-checked admission (UG2); UG-D9 (b) an append-only
`source.documents` locator admitted by `--policy additive` (UG3 (i)); UG-D3
(c) counts plus an opt-in strict flag (UG3 (ii)); UG-D0, D1 (four local
readers, the maintained panel stated as the project's bar), D4, D5, D6, D7, D8
as proposed. The owner closes issues 74, 75, 76 and 104 (UG-D0).

**Next action.** The owner accepts or amends the close ([007-close.md](007-close.md)) and decides whether to merge its pull request (branch `claude/ug-close`). Posting the drafted follow-ups ([ug4-issue-followups.md](notes/ug4-issue-followups.md)) and closing issue 104 are the owner's (UG-D0). Open owner questions are in the close record's sweep.
