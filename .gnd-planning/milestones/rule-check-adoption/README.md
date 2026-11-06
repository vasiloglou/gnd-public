# rule-check-adoption

Planning opened 2026-11-06 for five requests from a development tool that
runs `gnd check` as a CI gate over a project's component facts: GR-D1
(issue 92), GR-D2 (93), GR-D3 (94), GR-D5 (96) and GR-D6 (97). GR-D4
(issue 95, model composition) is left for its own milestone.

**Status: plan r3 drafted 2026-11-06, repairing r2 from the full panel's
22 fixes (r2 panel: six of six, exit 0, three `block`, three `revise`;
[record](001-panel.md)). r3 has not been reviewed; whether it is, and how,
is RC-D0. The plan is unapproved; no code is written.**

- [Canonical plan (r3, draft)](notes/rule-check-adoption-plan.md)
- [Panel record over r2](001-panel.md)
- [RC1 spec (r3, draft, blocked on the plan gate)](notes/phase-RC1-spec.md)

Phases:
- RC1: declared constraint id and `remedy` in each verdict, report version 15;
- RC2: full extent of an `acyclic` violation (version 15 only);
- RC3: `--baseline`, new vs standing violations;
- RC4: `--allow-vacuous` (after RC3);
- RC5: a population source value for deterministic tool output;
- RC6: documentation and a how-to;
- close.

Next action: the owner's ruling on RC-D0 (review r3 or not), then the plan
gate (§10 rulings, RC-D0 to RC-D13).
