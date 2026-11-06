# rule-check-adoption

Planning opened 2026-11-06 for five requests from a development tool that
runs `gnd check` as a CI gate over a project's component facts: GR-D1
(issue 92), GR-D2 (93), GR-D3 (94), GR-D5 (96) and GR-D6 (97). GR-D4
(issue 95, model composition) is left for its own milestone.

**Status: plan r1 drafted, awaiting the owner's plan gate. No plan review
has run (RC-D0). No spec is approved; no code is written.**

- [Canonical plan (r1, draft)](notes/rule-check-adoption-plan.md)
- [RC1 spec (r1, draft, blocked on the plan gate)](notes/phase-RC1-spec.md)

Phases:
- RC1: declared constraint id and `remedy` in each verdict, report version 15;
- RC2: full extent of an `acyclic` violation (version 15 only);
- RC3: `--baseline`, new vs standing violations;
- RC4: `--allow-vacuous`;
- RC5: a population source value for deterministic tool output;
- RC6: documentation and a how-to;
- close.

Next action: the owner rules on the plan (RC-D0 to RC-D8 in §10) and
decides whether the panel reviews r1.
