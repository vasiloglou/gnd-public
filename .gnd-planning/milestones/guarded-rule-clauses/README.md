# Guarded rule clauses

Draft r1, 2026-11-15. Fixes [#195](https://github.com/vasiloglou/gnd-public/issues/195):
guarded rules gain the clause language derivations already have.

| Order | Phase | Deliverable |
|---|---|---|
| 1 | GC1 | `in` / `not in` with a literal list in guarded and term comparisons |
| 2 | GC2 | `negate` and `where` beside a guarded antecedent |
| 3 | GC3 | Disjunctive `any_of` consequent with per-alternative violation detail |
| 4 | GC4 | Exporter translation or refusal, docs and an installed-candidate smoke |

[Milestone plan](notes/guarded-rule-clauses-plan.md) ·
[GC1 draft spec](notes/phase-GC1-spec.md)

**Readiness.** Not reviewed, not approved. Next: the owner selects a plan
review instrument (project bar: the maintained GND review panel), rules on
plan decisions D1–D6, then the plan gate; GC1 follows with `process-phase GC1
guarded-rule-clauses`.
