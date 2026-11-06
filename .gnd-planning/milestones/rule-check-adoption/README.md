# rule-check-adoption

Planning opened 2026-11-06 for five requests from a development tool that
runs `gnd check` as a CI gate over a project's component facts: GR-D1
(issue 92), GR-D2 (93), GR-D3 (94), GR-D5 (96) and GR-D6 (97). GR-D4
(issue 95, model composition) is left for its own milestone.

**Status: plan r6 approved by the owner on 2026-11-06, as written
([plan-gate record](005-plan.md)). Reviews ran over r2 (full panel) and r3
to r5 (Codex); r6 itself was not reviewed (RC-D16). RC1 is implemented and
recorded ([phase record](006-phase-RC1.md)); not yet pushed or merged.**

- [Canonical plan (r6, approved)](notes/rule-check-adoption-plan.md)
- [Panel record over r2](001-panel.md)
- [Single-reviewer record over r3](002-review.md)
- [Re-check record over r4](003-review.md)
- [Re-check record over r5](004-review.md)
- [Plan-gate record](005-plan.md)
- [RC1 spec (owner-approved)](notes/phase-RC1-spec.md)
- [RC1 phase record](006-phase-RC1.md)
- [RC2 spec (owner-approved)](notes/phase-RC2-spec.md)
- [RC2 phase record](007-phase-RC2.md)
- [RC3 spec (r1, awaiting its owner gate)](notes/phase-RC3-spec.md)

Phases:
- RC1: declared constraint id and `remedy` in each verdict, report version 15;
- RC2: full extent of an `acyclic` violation (version 15 only);
- RC3: `--baseline`, new vs standing violations;
- RC4: `--allow-vacuous` (after RC3);
- RC5: a population source value for deterministic tool output;
- RC6: documentation and a how-to;
- close.

Next action: the RC3 spec owner gate (process-phase). RC2 is merged (PR 103).
