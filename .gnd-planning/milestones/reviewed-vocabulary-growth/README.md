# Reviewed-vocabulary growth

Plan r3, 2026-11-23, for three open issues that no milestone owned (r1 was
written by `start-milestone` on 2026-11-22):
[#221](https://github.com/vasiloglou/gnd-public/issues/221),
[#222](https://github.com/vasiloglou/gnd-public/issues/222) and
[#218](https://github.com/vasiloglou/gnd-public/issues/218).
**Reviewed once, at r1; not approved.** The owner selected the GND panel
light on 2026-11-23; it reviewed plan r1 (sha256 `3d4a06b8…`) and four of six
seats returned `revise`
([report](evidence/plan-review-r1/PANEL-REVIEW.md),
[disposition](evidence/plan-review-r1/disposition.md)). Plan r2 applies the
repairs, tagged `(p1)`, at the owner's request of the same day. A second
round over r2 on 2026-11-23 ended below quorum, two of six seats, so **there
is no panel result for r2**
([record](evidence/plan-review-r2/disposition.md)). Plan r3 repairs the four
points the two returned reviews raised, tagged `(s2)`. No review has read
r3. `auto=false`.

| Phase | Deliverable | State |
|---|---|---|
| VG1 | `gnd check` cost about linear in the number of object types (#221) | [draft spec](notes/phase-VG1-spec.md), awaiting the plan gate and the owner's review |
| VG2 | `gnd evolve` and the growth document agree on the sources of a new constraint (#218) | outline; waits for ruling D2 |
| VG3 | an unattended root may include a reviewed vocabulary (#222) | outline; waits for rulings D3, D13 and D14 |
| VG4 | growth rounds on that root, and its first source document (#222) | outline; needs VG3, D4 and D6 |
| VG5 | one packaged example, the pages and the three issue replies | outline; needs VG1–VG4 |

[Plan](notes/reviewed-vocabulary-growth-plan.md). Listed in the
[roadmap after 0.4.0](../../PROJECT.md#roadmap-after-040--planned-2026-11-21).

Decisions waiting for the owner (plan §10): D1 one milestone or two
maintenance passes plus #222; D2 widen rule D-12 or change the growth
document; D3 the include route or the documented packaging; D4 the first
document; D6 re-pinning under the unattended mode; D8 the review instrument.

The review added two, each with a proposal in the plan. D13: what an
include must be for its elements to be exempt from the unattended rules
(proposed: the root's pin is the statement of review, and an unconfirmed
inferred claim in an include still cannot be `alethic`). D14: whether an
included span that names one of the root's documents is still hashed and
counted (proposed: yes, as today).

The roadmap of 2026-11-22 puts VG1 first, then GO1 of
[growth-round-outcomes](../growth-round-outcomes/README.md), then VG2–VG5:
that milestone edits `evolve/service.py` and `unattended-growth.md` too, one
writer at a time (plan §3).

Next action, the owner's: rule D1–D14 or amend them. Both planned review
rounds are spent; a new panel is the owner's to ask for. Then the plan gate.
VG1 can start from its spec gate after that; it needs no other ruling.
