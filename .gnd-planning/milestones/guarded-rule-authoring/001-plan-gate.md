---
milestone: guarded-rule-authoring
station: plan-gate
skill: "n/a -- repository development under process-milestone auto=true"
scope: plan-gate
date: 2026-11-11
gates:
  - command: "uv run python tools/run_gnd_review_panel.py ga-plan-review-request.json --out ga-plan-panel-r2 --reviewer-timeout 600 --overall-timeout 900"
    exit: 0
  - command: "gnd review finalize ga-plan-panel-r2 ga-plan-synthesis.json --out GA-PLAN-REVIEW-R2.md"
    exit: 0
  - command: "delegated approval (auto=true)"
    exit: 0
evidence:
  - path: .gnd-planning/milestones/guarded-rule-authoring/notes/guarded-rule-authoring-plan.md
    sha256: 577d5ae0eca1dd88f1a6ea7f3bceb609e1994ade439af56cd9082eb7511277b7
---

# Plan gate

**Delegated approval (auto=true).** The owner invoked
`process-milestone guarded-rule-authoring auto` and selected the standard
GND plan and close panel. Approve the reviewed r2 bytes for GA1, GA2 and
GA3 in order, with the [review dispositions](notes/plan-review-disposition.md).
Five valid responses met the four-reviewer project bar. The two-round
plan budget is exhausted.

The implementability sweep confirmed the shipped mixed model exits 5
because the independent oracle cannot label its guards. Removing the
guards in an explicit scratch scoped model gave exit 0 and 15 ordinary
cases, including mandatory and ring targets. Existing focused checks
exited 0 with 308 passed and one deselected.

For fact-changing consequents, both cases use a shared antecedent
assignment. A comparison consequent can require changing one operand's
value to switch outcomes. In that case, pair two populations with the
same antecedent structure and an active binding in each. This resolves
the literal shared-binding wording in §2 where its operands determine
the consequent. The author asks for an active pass and a targeted
failure. The phase gate will require both directly.

The phase records own implementation verification. Merge, certification
and publication remain outside this delegation.
