# Growth round outcomes

Outline r1, 2026-11-22, from [issue #227](https://github.com/vasiloglou/gnd-public/issues/227)
and [issue #228](https://github.com/vasiloglou/gnd-public/issues/228).
Not reviewed and not approved.

| Phase | Deliverable |
|---|---|
| GO1 | `gnd evolve` parses each model text once per invocation, so a round's cost stops being about 22 parses of the whole model (#228) |
| GO2 | `gnd evolve preview` reports an outcome for every operation of a proposal, not only the first refusal (#227) |
| GO3 | A supported way to keep the admitted part of a proposal and drop the rest, as a new proposal (#227) |
| GO4 | `unattended-growth.md` says what a reply carries for a fact type it reuses: its id, and no restated rows (#227) |
| GO5 | A per-round growth summary: proposed, mapped onto existing elements, dropped, added (#227) |

[Plan outline](notes/growth-round-outcomes-plan.md). Listed in the
[roadmap update of 2026-11-22](../../PROJECT.md#open-issues-on-2026-11-22--roadmap-update).
GO1 needs no ruling and can run first. GO2 to GO5 wait for the owner's
decisions D1 to D4 in the plan's §5.
