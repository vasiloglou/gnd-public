# Reviewed-vocabulary growth

Plan r4, 2026-11-23, for three open issues that no milestone owned (r1 was
written by `start-milestone` on 2026-11-22):
[#221](https://github.com/vasiloglou/gnd-public/issues/221),
[#222](https://github.com/vasiloglou/gnd-public/issues/222) and
[#218](https://github.com/vasiloglou/gnd-public/issues/218).
**Approved by the owner on 2026-11-23** ([plan gate](001-plan-gate.md)),
with decisions D1–D14 ruled as proposed. A panel reviewed it once, at r1; no
reviewer has read r4. The owner selected the GND panel
light on 2026-11-23; it reviewed plan r1 (sha256 `3d4a06b8…`) and four of six
seats returned `revise`
([report](evidence/plan-review-r1/PANEL-REVIEW.md),
[disposition](evidence/plan-review-r1/disposition.md)). Plan r2 applies the
repairs, tagged `(p1)`, at the owner's request of the same day. A second
round over r2 on 2026-11-23 ended below quorum, two of six seats, so **there
is no panel result for r2**
([record](evidence/plan-review-r2/disposition.md)). Plan r3 repairs the four
points the two returned reviews raised, tagged `(s2)`. A new run over r3 the
same day also ended below quorum, two of six seats, so **there is no panel
result for r3** either ([record](evidence/plan-review-r3/disposition.md)).
Plan r4 repairs the eight points its two returned reviews raised, tagged
`(s3)`, at the owner's request. `auto=false`.

| Phase | Deliverable | State |
|---|---|---|
| VG1 | `gnd check` cost about linear in the number of object types (#221) | done 2026-11-23: [record](002-phase-VG1.md), [spec](notes/phase-VG1-spec.md) (delegated approval, `auto=true`) |
| VG2 | `gnd evolve` and the growth document agree on the sources of a new constraint (#218) | outline; D2 ruled (a), widen rule D-12 |
| VG3 | an unattended root may include a reviewed vocabulary (#222) | outline; D3, D13 and D14 ruled (a) |
| VG4 | growth rounds on that root, and its first source document (#222) | outline; needs VG3 |
| VG5 | one packaged example, the pages and the three issue replies | outline; needs VG1–VG4 |

[Plan](notes/reviewed-vocabulary-growth-plan.md). Listed in the
[roadmap after 0.4.0](../../PROJECT.md#roadmap-after-040--planned-2026-11-21).

Decisions D1–D14 are ruled, each as the plan proposes; the
[plan-gate record](001-plan-gate.md) lists them. In short: one milestone
(D1); rule D-12 is widened (D2); an unattended root may include a reviewed
model, on the strength of its pin (D3, D13); an included span that names one
of the root's documents is still checked and counted (D14); a root with an
include and nothing else may start without a document (D4); the per-include
lines are in the text output of `gnd validate` (D5); a growth round cannot
re-pin an include (D6).

The roadmap of 2026-11-22 puts VG1 first, then GO1 of
[growth-round-outcomes](../growth-round-outcomes/README.md), then VG2–VG5:
that milestone edits `evolve/service.py` and `unattended-growth.md` too, one
writer at a time (plan §3).

`process-milestone reviewed-vocabulary-growth auto` runs this milestone
since 2026-11-23: spec rulings are delegated (`auto=true`); merge is not.
VG2, VG4 and VG5 change `evolve/service.py` or `unattended-growth.md`, so by
the plan's order (§3) they wait for GO1 of growth-round-outcomes, whose plan
is not approved yet. VG3 changes neither file and runs next.
