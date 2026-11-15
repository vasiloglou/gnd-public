---
milestone: literature-identity
station: plan-gate
skill: "n/a -- repository development under start-milestone, not a gnd-solve station over a domain model"
scope: plan-gate
date: 2026-11-15
gates:
  - command: "uv run python tools/run_gnd_review_panel.py li-plan-review-request.json --out li-plan-panel-r1 --reviewer-timeout 600 --overall-timeout 900"
    exit: 0
  - command: "gnd review finalize li-plan-panel-r1 li-plan-synthesis-r1.json --out LI-PLAN-PANEL-REVIEW-r1.md"
    exit: 0
  - command: "uv run python tools/run_gnd_review_panel.py li-plan-review-request-r2.json --out li-plan-panel-r2 --reviewer-timeout 600 --overall-timeout 900"
    exit: 0
  - command: "gnd review finalize li-plan-panel-r2 li-plan-synthesis-r2.json --out LI-PLAN-PANEL-REVIEW-r2.md"
    exit: 0
  - command: "ruling: owner approved .gnd-planning/milestones/literature-identity/notes/literature-identity-plan.md sha256 5ad5b74485a442a8e9fa09ed59c28a4463b812a4119ea6f2959c56cdda7c90de"
    exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/milestones/literature-identity/notes/literature-identity-plan.md
    sha256: 5ad5b74485a442a8e9fa09ed59c28a4463b812a4119ea6f2959c56cdda7c90de
  - path: .gnd-planning/milestones/literature-identity/notes/plan-review-disposition.md
    sha256: ca7c3aa0a08fbd0d8d755643bef33503732324c6f816e1c3d0536b11086728df
---

# Claim

The owner approved literature-identity plan r3 at the SHA-256 above, and
ruled D1–D9 as proposed. Review stopped after round 2 under its declared rule.
Round 2 did not meet the project's four-reviewer bar, and r3 carries no review
opinion.

## Gate output (verbatim)

    Owner ruling, 2026-11-15, in chat, answering the plan-gate question for
    plan r3 (SHA-256 5ad5b744…7c90de, commit 3aaa1e6d):
      Plan gate: "Approve r3 (Recommended)"
      D1–D9:     "Accept all proposals"

    Panel round 1 over r1 (f27c10dc…53bfe3): exit 0, 5 of 6 seats valid,
      run b65da370…0538653, finalize exit 0, synthesis f34dc7b7…055.
    Panel round 2 over r2 (5badf3ef…f95143): exit 0, 3 of 6 seats valid,
      run 052eae84…f7f86, finalize exit 0, synthesis cfbe8e0e…8d7.

## Rulings `(o)`, 2026-11-15

Each row is ruled as its proposal in plan r3 §10. The plan bytes are not
edited, so the approved digest stays valid.

| ID | Ruling |
|---|---|
| D1 | Ship the public reconstruction, held to the C1 floors. The 16/50/24/180 host-scale sets stay host-owned, and the host runs them with the LI1 report |
| D2 | Paraphrased documents with public work identifiers |
| D3 | Runtime binds and verifies decisions and the coverage set only. Meaning stays host-side |
| D4 | An example-level diagnostics report first. Promote it to a `gnd discover` family only after the N3 measurement |
| D5 | The assurance report and the admission step are an example harness and an example step, with no new `gnd` command |
| D6 | Three milestones as in §1.1. literature-interop starts after LI0 and may run alongside LI1–LI5 |
| D7 | `stretched` maps to reject, and the disposition is kept in the review record |
| D8 | LI0 is a phase of this milestone |
| D9 | The maintained standard panel, with two rounds at most. The successor plans are reviewed when they start |

Some r3 text says a later spec gate will fix something, for example the
stage floors, the path policy, and the record schema ids. Those remain
proposals for the named spec gate. They are not ruled here.

## Review

The [review disposition](notes/plan-review-disposition.md) records both rounds,
every concern and its disposition, and the stop-rule arithmetic.

| Round | Result |
|---|---|
| 1 | 5 of 6 seats valid, so the four-reviewer bar was met |
| 2 | 3 of 6 seats valid: Gemini and Kimi malformed, GLM timed out. The bar was **not met** |

**Stop rule.** It fired after round 2: 32 of the 36 findings attacked r2
text, which is above one half. The two-round budget is exhausted.

The r3 repairs are marked `(p3)` and have not been reviewed. This approval
adds no review opinion.

## Boundary -- what this result did NOT establish

- **Specs.** Approving the plan is not approving any phase spec. LI0's draft
  spec still needs its own owner gate before implementation. `auto=false`.
- **Successor plans.** The literature-interop and literature-depth outline
  plans are not approved by this ruling. D9 holds their review until each
  starts.
- **Reviewer status.** Neither the panel opinion nor this ruling is a
  conformance result, a certification or an acceptance of any behavior.
- **Further authority.** No merge, publication, release or certification is
  authorized.

## Open questions

- The open items carried from r3 to named spec gates:
  - LI1: the stage floors;
  - LI2: the record schema ids;
  - LI3: the threshold `T`, `k` and the false-positive budget;
  - LI5: the path-policy table and L3's witness exit code.
