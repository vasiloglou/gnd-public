# Guarded rule workflows

Draft r3, 2026-11-11. The issue author's priority update puts guarded-rule
diagnostics first and rule-edition comparison second.

| Order | Phase | Issue | Deliverable |
|---|---|---|---|
| 1 | GW0 | [GR-D12](https://github.com/vasiloglou/gnd-public/issues/183) | Report when a guarded rule matched nothing and flag out-of-domain literals during validation |
| 2 | GW2 | [GR-D9](https://github.com/vasiloglou/gnd-public/issues/180) | Compare findings under two rule editions on the same population |

[Milestone plan](notes/guarded-rule-workflows-plan.md) ·
[GW0 draft spec](notes/phase-GW0-spec.md)

Generated cases (GW3), relational discovery (GW4), and mined-rule constants
(GW1) are [deferred](notes/guarded-rule-workflows-plan.md#7-deferred-and-out-of-scope).
The standard panel reviewed r2. The [review disposition](notes/plan-review-disposition.md)
records the first round and the r3 changes. The [delegated plan gate](001-plan-gate.md) is recorded.
[GW0](003-phase-GW0.md) and [GW2](005-phase-GW2.md) are implemented and
reviewed. The [close outcome](notes/close-outcome.md) awaits the standard panel.
