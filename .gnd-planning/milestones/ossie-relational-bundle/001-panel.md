---
milestone: ossie-relational-bundle
station: plan-panel
skill: gnd-review-panel-light
scope: panel
date: 2026-11-24
gates:
  - command: "uv run python tools/run_gnd_review_panel.py --light .gnd-planning/milestones/ossie-relational-bundle/evidence/plan-review-r1/review-request.json --out .gnd-planning/milestones/ossie-relational-bundle/evidence/plan-review-r1/panel-run --effort high --reviewer-timeout 600 --overall-timeout 900"
    exit: 0
  - command: "gnd review finalize panel-run synthesis.json --out PANEL-REVIEW.md"
    exit: 0
evidence:
  - path: .gnd-planning/milestones/ossie-relational-bundle/evidence/plan-review-r1/review-request.json
    sha256: 0ede59af6a50afbf7b62f65c0605bbf00451123eb2b3ee3147cd3a8f5f43c92c
  - path: .gnd-planning/milestones/ossie-relational-bundle/evidence/plan-review-r1/panel-run/run.json
    sha256: c4276ed9b988236047a4aaaa9874906be2451608bfa4b34b5a0b2128d0bcd0e5
  - path: .gnd-planning/milestones/ossie-relational-bundle/evidence/plan-review-r1/synthesis.json
    sha256: bd996771f0c567f5be82f0a276c69a7f8ae6e6af4ffa2830d25a05fdeb5907c0
  - path: .gnd-planning/milestones/ossie-relational-bundle/evidence/plan-review-r1/PANEL-REVIEW.md
    sha256: 40a36b724d5e682185a3c9d9fbaf76af658ac9ffcde9b47a3c0a5a2cb86c8203
---

# Light plan panel over plan r1

On 2026-11-24 the owner selected the light panel for plan r1 ("Run the
light panel"). The run used effort high, which applies per run to Claude
and Codex only. Qwen, Gemini, Kimi and the GLM seat have no per-run
effort flag.

## Subject

| Field | Value |
|---|---|
| Subject | plan r1, `notes/ossie-relational-bundle-plan.md`, sha256 `cdc1576f1f1d5f1b6a040b7eebed4f6e14b0d1c02097b73ad3680076fc40f44d` |
| Reviewed commit | `7890dc6c`. Load the request against that commit; the canonical plan has since moved to r2. |
| Context only | the draft OB1 spec r1. The rubric told reviewers that a concern about it must cite the plan. |
| Not a subject | plan r2 and OB1 spec r2. They carry no panel opinion. |

## Gate output

| Item | Result |
|---|---|
| Panel exit | 0, `quorum-established` |
| `reviewed_artifacts_unchanged` | `true` |
| Request sha256 | `a386842092fe…1fddb` |
| Run sha256 | `c4276ed9…d0e5` |
| Seats that succeeded | 4 of 6: claude, codex, gemini, kimi |
| Seats that timed out | qwen, glm (shared deadline) |
| Verdicts | `revise` from claude, codex and kimi; `block` from gemini |
| Concerns retained | 27, with every response complete and none dropped |
| Concerns anchored by an exact quotation | 23. The four without one: claude `required-source-expression`, codex `d2-no-opt-in` and `one-to-one-direction`, gemini `ob1-specified-before-d3`. |

The working tree showed no change outside the evidence directory after the
run. The retained files contain no home-directory, scratch or temporary
path, so no sanitization was needed.

Finalization exited 0 on the first attempt:

| Item | Result |
|---|---|
| Agreed groups | 7 |
| Divergent views | 9 |
| Prioritized fixes | 16 |
| MVP triage | 16 blocking, 11 hardening, 0 completeness |
| Canonical synthesis sha256 (reported by finalize) | `76f25b91729e21c9d1a7d09581bc47b348483c30ecd006e69fda56e89f2f5bd1` |

The file digest above is over the pretty-printed bytes.

## Findings and disposition

The owner directed "Apply fixes as r2". Plan r2 applies every fix. Each
change is tagged `(p1 Fn)` with its rank in the report.

| Fix | Concern | Support | Disposition in r2 |
|---|---|---|---|
| F1 | Usage errors exit 64, not 2 | claude, kimi | §0, §2.1, OB1-C4; OB1 spec T4 |
| F2 | Predicate 1 against the D2(a) default; no opt-in flag | claude, codex, gemini, kimi | Predicates 1–2 split; `--relational` under D2 (b) |
| F3 | Collision exit is 11 | claude, kimi | §1.2, §2.2, §5 |
| F4 | D5/OB2 cycle | claude, codex | OB2 blocked on D1 only; OB2-C5 measures and rules D5 |
| F5 | Import caps beyond the read | claude, codex | §1.2 lists five caps; OB1 spec §6.3, T6b and T6c |
| F6 | Rmap tie-breaks | claude, codex (2), gemini | §2.3 placement and keys; OB2-C2 fixtures |
| F7 | I3 members not owned | claude, gemini | §2.4; OB4-C1 |
| F8 | Source cap may still block issue 1 | claude | §1.2; new D11; OB1-C2 records the ratio |
| F9 | Overlapping placement rules | codex | §2.3 precedence; OB2-C2 fixture |
| F10 | Composite foreign keys | codex | §2.4 grouping rule; OB4-C7; D8 |
| F11 | Required `Dataset.source` and `Field.expression` | claude | §2.3 required members; `source_kind: logical` |
| F12 | Rmap refusal on the default path | claude | Predicate 3: the Rmap never refuses a model |
| F13 | D6 equality against model identity | codex | D6 scoped; OB3-C7 |
| F14 | Unrepresentable constraints not owned | gemini | Predicate 4; OB3-C3 walk covers constraints |
| F15 | Role-name normalization | claude | D8: NFKC, casefold, L*/N*; OB4-C6 |
| F16 | OB1 shown ready before D3 | gemini | OB1 blocked on the plan gate and D3 |

Two code claims were checked against `src/gnd/exits.py` before r2 was
written: `EXIT_USAGE = 64` and `EXIT_COLLISION = 11`. One error was found
while r2 was being written and was corrected in the OB1 spec r2: the import
read rule is `input-size`, not `ontology-size`.

## Boundary

This panel is advisory. It approves no plan, no spec and no decision. The
plan gate is still open, D1–D11 are unruled, and r2 is unreviewed (D9).
