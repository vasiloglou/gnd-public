# rule-check-adoption

Planning opened 2026-11-06 for five requests from a development tool that
runs `gnd check` as a CI gate over a project's component facts: GR-D1
(issue 92), GR-D2 (93), GR-D3 (94), GR-D5 (96) and GR-D6 (97). GR-D4
(issue 95, model composition) is left for its own milestone.

**Status: plan r6 drafted 2026-11-06. r2 was reviewed by the full panel
([record](001-panel.md)); r3 by one reviewer, Codex (RC-D0;
[record](002-review.md)); Codex re-checked r4 (RC-D14;
[record](003-review.md)) and r5 (RC-D15; [record](004-review.md)).
`--baseline` refuses models with derivations (RC-D11, owner's selection).
r6 repairs the r5 findings and has not been reviewed (RC-D16). A
pre-existing version-7 schema defect found on the way is proposed as its
own issue (RC-D17). The plan is unapproved; no code is written.**

- [Canonical plan (r6, draft)](notes/rule-check-adoption-plan.md)
- [Panel record over r2](001-panel.md)
- [Single-reviewer record over r3](002-review.md)
- [Re-check record over r4](003-review.md)
- [Re-check record over r5](004-review.md)
- [RC1 spec (r6, draft, blocked on the plan gate)](notes/phase-RC1-spec.md)

Phases:
- RC1: declared constraint id and `remedy` in each verdict, report version 15;
- RC2: full extent of an `acyclic` violation (version 15 only);
- RC3: `--baseline`, new vs standing violations;
- RC4: `--allow-vacuous` (after RC3);
- RC5: a population source value for deterministic tool output;
- RC6: documentation and a how-to;
- close.

Next action: the owner's RC-D16 ruling (review r6 or not), then the plan
gate (§10 rulings).
