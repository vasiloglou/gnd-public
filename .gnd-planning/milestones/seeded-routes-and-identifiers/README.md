# seeded-routes-and-identifiers

Opened on 2026-11-25 at the owner's request ("can we actually reopen and plan
them", then "can you also include 292?"). **SI1–SI4 recorded. Milestone close gates pending.**

It plans three open issues and a tag-only release:

- [#292](https://github.com/vasiloglou/gnd-public/issues/292): an unattended
  root that includes a reviewed model validates, but `gnd flatten` ends in a
  traceback and `gnd extract` and `gnd export pyrel` refuse it (SI1);
- [#279](https://github.com/vasiloglou/gnd-public/issues/279): which external
  uniqueness `refscheme.reference_identity` selects (SI2);
- [#280](https://github.com/vasiloglou/gnd-public/issues/280): Ossie
  identifiers for unit-based references and multi-supertype subtypes (SI3);
- 0.5.2 as a GitHub tag only (SI4).

The owner chose on 2026-11-25: the light GND panel for the plan and the
close; delegated approval of the plan and the specs, with the owner deciding
merges and the decisions the specs name; a tag-only 0.5.2 at the end.

- [Plan r2](notes/seeded-routes-and-identifiers-plan.md): the measurements of
  all three issues on main `f7ee3720`, four phases, decisions D0 to D5, and
  in §11 the eleven fixes from the light panel over r1.
- [001 plan gate](001-plan-gate.md): light panel over r1 (four of six seats,
  all "revise"), r2 approved by delegated ruling; no review has read r2.
- [SI1 spec](notes/phase-SI1-spec.md): D1 approved by the owner.
- [SI1 record](002-phase-SI1.md): route verification, review and repairs.

- [SI2 record](003-phase-SI2.md): identity selection, compatibility census, and review.
- [SI3 spec](notes/phase-SI3-spec.md): owner-approved corpus and oracle.

- [SI3 record](004-phase-SI3.md): ontology and mapping census, pinned tools, and review.

- [SI4 spec](notes/phase-SI4-spec.md) and [record](005-phase-SI4.md) cover the
  tag-only release preparation.

[PR #294](https://github.com/vasiloglou/gnd-public/pull/294) merged SI1–SI3.
The close record will bind the separate SI4 merge, remote tag, full default
test lane and light panel.
