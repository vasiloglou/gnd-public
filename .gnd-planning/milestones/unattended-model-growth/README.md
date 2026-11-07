# unattended-model-growth

Planning opened 2026-11-07 for issues
[#104](https://github.com/vasiloglou/gnd-public/issues/104) (GR-T17),
[#74](https://github.com/vasiloglou/gnd-public/issues/74) (GR-T11),
[#75](https://github.com/vasiloglou/gnd-public/issues/75) (GR-T12) and
[#76](https://github.com/vasiloglou/gnd-public/issues/76) (GR-T13): growing one
model over many documents with no human reviewer, without overstating evidence
or invalidating admitted facts. A later wave (73, 77, 78, 95) is not in this
milestone.

**Status: plan r1 drafted, awaiting the owner's plan gate. No plan review has
run. No phase has an approved spec. Nothing is implemented, no issue is
closed.** `auto=false`.

**Headline.** Most of the four issues is already on main, from the closed
[model-growth-guardrails](../model-growth-guardrails/README.md) milestone (74,
75, 76) and PR 106 (104, items 1 to 4). What is genuinely open: 104 item 5's
second option (admit a clean-population constraint over a populated fact
type), and a gap found while planning: a growth round cannot declare its own
new source document through `gnd evolve`. The plan therefore starts with an
acceptance replay that measures the shipped behavior, then offers the open
items as owner decisions.

- [Canonical plan (r1, draft)](notes/unattended-model-growth-plan.md)
- [UG1 spec (r1, draft)](notes/phase-UG1-spec.md): acceptance replay and issue
  disposition, test-only
- Phases: UG1 acceptance replay (ready once gated); UG2 population-checked
  constraint admission (blocked on UG-D2); UG3 the unattended source header
  across rounds (blocked on UG-D3, UG-D9); UG4 documentation and dispositions;
  then the close.

**Pending owner decisions** (plan §10): UG-D0 who closes the issues; UG-D1
review instrument; UG-D2 build item 5's population check or decline; UG-D3
fail-closed span coverage; UG-D9 how a round declares its document; UG-D4 to
UG-D7 smaller scope rulings.

**Next action.** The owner reads the plan and rules, or approves r1 at the gate
and then UG1's spec.
