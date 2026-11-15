# Guarded rule clauses

Plan r3, 2026-11-15. Fixes [#195](https://github.com/vasiloglou/gnd-public/issues/195):
guarded rules gain the clause language derivations already have.

| Order | Phase | Deliverable |
|---|---|---|
| 1 | GC1 | `in` / `not in` with a literal list in guarded and term comparisons |
| 2 | GC2 | `negate` and `where` beside a guarded antecedent |
| 3 | GC3 | Disjunctive `any_of` consequent with per-alternative violation detail |
| 4 | GC4 | Exporter translation or refusal, docs and an installed-candidate smoke |

[Milestone plan](notes/guarded-rule-clauses-plan.md) ·
[GC1 draft spec](notes/phase-GC1-spec.md)

**Readiness.** See the [review disposition](notes/plan-review-disposition.md)
and the [delegated plan gate](001-plan-gate.md). GC1 proceeds through the
corpus and spec gate.

GC1 is recorded in the [phase record](003-phase-GC1.md). GC2 follows.
