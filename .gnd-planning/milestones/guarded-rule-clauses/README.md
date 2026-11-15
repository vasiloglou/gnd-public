# Guarded rule clauses

Plan r2 review candidate, 2026-11-15. Fixes [#195](https://github.com/vasiloglou/gnd-public/issues/195):
guarded rules gain the clause language derivations already have.

| Order | Phase | Deliverable |
|---|---|---|
| 1 | GC1 | `in` / `not in` with a literal list in guarded and term comparisons |
| 2 | GC2 | `negate` and `where` beside a guarded antecedent |
| 3 | GC3 | Disjunctive `any_of` consequent with per-alternative violation detail |
| 4 | GC4 | Exporter translation or refusal, docs and an installed-candidate smoke |

[Milestone plan](notes/guarded-rule-clauses-plan.md) ·
[GC1 draft spec](notes/phase-GC1-spec.md)

**Readiness.** The owner selected the Standard panel for plan and close and
delegated milestone approval rulings. See the
[round 1 disposition](notes/plan-review-disposition.md). The plan gate follows
confirmation of r2, then GC1's corpus and spec gate.
