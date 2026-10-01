---
name: gnd-review-panel-light
description: "Runs the same bounded six-reviewer advisory workflow as gnd-review-panel, but uses a lighter supported per-run effort: high by default or medium when the user explicitly selects it. Use for faster or lower-cost multi-model review evidence over one plan, one experiment outcome, or one spec/results/delta bundle. The same six reviewer seats, quorum, immutable evidence, synthesis validation, failure retention, no-sandbox disclosure, and advisory-only boundary apply. Not for the quality-first xhigh profile (gnd-review-panel), updating reviewer policy (gnd-update-review-panel), or applying fixes."
---

# GND Review Panel Light

## Inherit the full panel contract

Read [`../gnd-review-panel/SKILL.md`](../gnd-review-panel/SKILL.md) and its required [`review-contract.md`](../gnd-review-panel/references/review-contract.md) completely before a run. Apply every request shape, clean-or-disposable-tree precondition, six-reviewer roster, three-success quorum, timeout and output bound, evidence rule, exit band, synthesis rule, reporting obligation, advisory boundary, and refusal unchanged.

This skill changes exactly two things:

1. Run `gnd review panel-light` instead of `gnd review panel`.
2. Use `high` effort by default, or `medium` only when the user asks for medium.

It never applies a fix. It does not turn reviewer execution into a sandbox, weaken quorum, omit a failure or divergent view, retry a failed seat, change a model, or edit persistent reviewer configuration. It inherits the full panel's fixed customization-isolation flags and focused-pass prompt unchanged; “light” changes only supported per-run effort.

## Effort profile

The selected value is recorded as `reviewer_effort` in `run.json` and in the command's JSON summary.

| Selection | Invocation |
|---|---|
| default | `--effort high` |
| user explicitly requests medium | `--effort medium` |

Claude and Codex receive the selected supported per-run effort. Qwen, Gemini, Kimi, and the GLM seat (whose Z.AI endpoint documents no effort control) expose no supported per-run effort flag; their model and invocation policies therefore remain identical to the quality-first panel. Do not edit Qwen's persistent user settings or invent flags for Qwen, Gemini, Kimi, or the GLM seat in order to make the word “light” appear to cover all six seats.

The original `gnd review panel` command remains the `xhigh` quality-first profile.

## Run and finalize

From the clean or disposable tree required by the full panel contract, run:

```
gnd review panel-light review-request.json --out panel-run/ --effort high --reviewer-timeout 600 --overall-timeout 900
```

Substitute `--effort medium` only on the user's instruction. Read the exit band and perform the semantic grouping exactly as the full panel skill requires. At exit 16, stop: no panel result exists.

Finalization is unchanged:

```
gnd review finalize panel-run/ synthesis.json --out PANEL-REVIEW.md
```

In the final report to the user, state the selected effort and disclose that it was bound per run only for Claude and Codex. Then provide every command, exit code, success/failure, agreed concern, divergent view, and cited fix required by the full panel skill.

## Record and commit

After finalization exits 0, follow the full panel skill's explicit-go-ahead rule and the one normative [`milestone-record-format.md`](../gnd-orm-core/references/milestone-record-format.md). The record and commit are the driving agent's acts; `gnd` itself never touches git.
