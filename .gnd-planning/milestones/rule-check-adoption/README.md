# rule-check-adoption

Planning opened 2026-11-06 for five requests from a development tool that
runs `gnd check` as a CI gate over a project's component facts: GR-D1
(issue 92), GR-D2 (93), GR-D3 (94), GR-D5 (96) and GR-D6 (97). GR-D4
(issue 95, model composition) is left for its own milestone.

**Status: plan r2 drafted and reviewed by the full panel (2026-11-06, six
of six, exit 0: 9 agreed groups, 13 divergent, 22 fixes;
[record](001-panel.md)). Three seats `block`, three `revise`. No fix is
applied yet; the plan is unapproved; no code is written.**

- [Canonical plan (r2, draft)](notes/rule-check-adoption-plan.md)
- [Panel record over r2](001-panel.md)
- [RC1 spec (r2, draft, blocked on the plan gate)](notes/phase-RC1-spec.md)

Phases:
- RC1: declared constraint id and `remedy` in each verdict, report version 15;
- RC2: full extent of an `acyclic` violation (version 15 only);
- RC3: `--baseline`, new vs standing violations;
- RC4: `--allow-vacuous`;
- RC5: a population source value for deterministic tool output;
- RC6: documentation and a how-to;
- close.

Next action: repair r2 into r3 from the panel's fixes, then the owner's
plan gate (§10 rulings).
