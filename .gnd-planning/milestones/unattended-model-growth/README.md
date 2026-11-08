# unattended-model-growth

Planning opened 2026-11-07 for issues
[#104](https://github.com/vasiloglou/gnd-public/issues/104),
[#74](https://github.com/vasiloglou/gnd-public/issues/74),
[#75](https://github.com/vasiloglou/gnd-public/issues/75) and
[#76](https://github.com/vasiloglou/gnd-public/issues/76): growing one
model over many documents with no human reviewer, without overstating evidence
or invalidating admitted facts. A later wave (73, 77, 78, 95) is not in this
milestone.

**Status: plan r1.2 drafted, awaiting the owner's plan gate. The owner ruled the
decisions UG-D0 to UG-D9 on 2026-11-07 (decision rulings only, not gate
approval). Plan review round 1 (four local readers, UG-D1 (a)) ran over r1.1
and its accurate repairs are applied in r1.2; r1.2 has not been re-read. No
phase has an approved spec. Nothing is implemented, no issue is closed.**
`auto=false`.

**Headline.** Most of the four issues is already on main, from the closed
[model-growth-guardrails](../model-growth-guardrails/README.md) milestone (74,
75, 76) and PR 106 (104, items 1 to 4). What is genuinely open: 104 item 5's
second option (admit a clean-population constraint over a populated fact
type), and a gap found while planning: a growth round cannot declare its own
new source document through `gnd evolve`. The plan therefore starts with an
acceptance replay that measures the shipped behavior, then offers the open
items as owner decisions.

- [Canonical plan (r1.2, draft)](notes/unattended-model-growth-plan.md)
- [Plan review round 1: disposition](notes/plan-review-r1-disposition.md)
- [UG1 spec (r1.2, draft)](notes/phase-UG1-spec.md): acceptance replay and issue
  disposition, test-only
- Phases: UG1 acceptance replay (ready once gated); UG2 population-checked
  constraint admission (blocked on UG-D2); UG3 the unattended source header
  across rounds (blocked on UG-D3, UG-D9); UG4 documentation and dispositions;
  then the close.

**Owner rulings, 2026-11-07** (plan §10, "Owner ruling" column): UG-D2 (b)
build the population-checked admission (UG2); UG-D9 (b) an append-only
`source.documents` locator admitted by `--policy additive` (UG3 (i)); UG-D3
(c) counts plus an opt-in strict flag (UG3 (ii)); UG-D0, D1 (four local
readers, the maintained panel stated as the project's bar), D4, D5, D6, D7, D8
as proposed. The owner closes issues 74, 75, 76 and 104 (UG-D0).

**Next action.** The owner reads the disposition, then rules on the plan gate
(r1.2 or a confirmation round), then on UG1's spec gate. Open owner questions:
UG-Q6 (component-index contradiction in `project.md`), UG-Q7 (tracker labels).
