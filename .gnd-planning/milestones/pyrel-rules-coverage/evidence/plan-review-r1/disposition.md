# Plan review r1: disposition

Reviewed bytes: `notes/pyrel-rules-coverage-plan.md` r2, sha256
`f2296905bd493c8ee60056994e8f67cc88191f09a2648fb4cf2a66c63dc33dbf`, commit
`a2a69608`. Instrument: the full GND panel, `reviewer_effort` xhigh,
owner-selected on 2026-11-21. It ran from a disposable worktree at
`a2a69608`, and its `gnd` import resolved inside that worktree. The panel
code (`src/gnd/review`, both panel skills) was equal to HEAD.

    uv run python tools/run_gnd_review_panel.py .gnd-planning/milestones/pyrel-rules-coverage/review-request.json --out panel-run --reviewer-timeout 1500 --overall-timeout 1800
    exit 0, run_sha256 1016d3e1f30dd7f4fe2395bac765da8127522f06f7e61f0d52439f972cb76dad
    uv run gnd review finalize panel-run synthesis.json --out PANEL-REVIEW.md
    exit 0, synthesis_sha256 a06616a2f765a1052d1fa9a5fb236f4b4d63d1f7df671b0997d2b6c90d74bfc6

Four of six seats returned schema-valid responses: Claude, Codex, Kimi and
GLM. Qwen and Gemini returned malformed output. All four asked for revision.
Claude and GLM run the same CLI. This folder keeps the request, `run.json`,
the four `response.json` files (copied unedited; none names a local path),
the synthesis and the finalized report. The rest of `panel-run/` stayed in
the disposable worktree; its digest is `run_sha256`. The panel is advisory
and approves nothing.

Each concern was checked against the code at `8c909013` before it was
believed. Class is this disposition's MVP triage, not the reviewer's
severity. Every repair is in plan r3, tagged `(p1)`; r3 carries no review
opinion.

| Reviewer | Concern | Reproduced | Class | Disposition |
|---|---|---|---|---|
| claude, codex, kimi, glm | ambiguous anchor join | yes: `semantic_spec.py:2665-2672` returns `join-anchor-ambiguous`; `gnd check` renders it unchecked (`checker/_core.py:573-577`) | blocking | fixed: §1, §2 RP1, RP1-C7, RP1 spec T14 |
| claude | disconnected join misdescribed | yes: `semantic_spec.py:2696-2700`, `_core.py:569-572`; `_require_joinable` is reached only from message and witness helpers | blocking (same root as the above) | fixed: §1, RP1-C6, RP1 spec T4 |
| claude, codex | comparator blind to not-checked | yes: `tests/test_pyrel_rules.py:62-73` json-decodes the reason; `:83-102` drops an unchecked verdict with no offending facts | blocking | fixed: Goal, §2 RP2, RP2-C6 with a negative control |
| claude, glm | textual line contradiction | yes: r2 §2 and §5 against RP2-C4 | blocking (an unsatisfiable criterion) | fixed: textual reason is `textual rule: <expression>`; RP2-C4 pins the line byte-identical |
| codex | D4 contradicts same-verdict | yes: r2 §0 forbade enforcing more, §2 refused input GND accepts | blocking | fixed: §0 scopes same-verdict to accepted inputs; unrepresentable inputs are by-name exit-3 refusals with both exits pinned, as repeated facts already are |
| codex | Float cannot hold every Number | yes: GND keeps exact integer ratios (`values.py:392-399`); 2**53+1 is not a float | blocking | fixed: D6, RP3-C4; also closes the same pre-existing gap for `Float` |
| claude | anchored decided by `gnd check --anchors` | yes: `commands/checking.py:890-891`; the quantity fixture README runs it | hardening | fixed: §1, the anchored reason, agreement defined without a sidecar |
| claude | shared lowering feeds Ossie | partly: Ossie's `_supported_shape` excludes value rules with `role_ref` (`ossie_formulas.py:258-261`), but a fact-scoped value without `role_ref` and D4's `String` reach it through `constraint_requirements` (`:293-295`) | hardening | fixed: §0 "Ossie export unchanged", Ossie tests in every lane, §3 affected consumer |
| claude | D5 untested | yes: `_LQP_MAIN` reports only after `--connection` | hardening | fixed: RP2-C7 runs the report function with the engine stubbed |
| claude | RP5 populations unenumerated | yes | hardening | fixed: §1 population table, measured exits |
| glm | identity-equal anchors | not reproduced: anchors in the packaged models are strings, where equality is identity; numeric anchors are unmeasured | hardening | fixed as a measurement: RP1 spec T15 |
| claude, glm | change surface incomplete | yes | completeness | fixed: §2 intro |
| glm | representation-format path | yes | completeness | fixed: repository-rooted path |

Measured while dispositioning: a loop over the twelve gold populations of
the flat literature model first printed exit 0 for each. That was a shell
error (`$?` read after a command substitution). `gnd check` and `api.check`
both exit 4 on them, as r2 said; no plan change.

## Convergence ledger

| Round | Seats | Per-seat counts | Self-inflicted / total | Blocking / total | Severity ceiling | Verdicts |
|---|---|---|---|---|---|---|
| r1 (over r2) | 4 / 6 | claude 9, codex 4, kimi 1, glm 5; qwen and gemini malformed | 0 / 19 (first round) | 6 / 19 (by this triage) | high | 4 revise |

Budget declared in plan §8 before round 2: at most two rounds; round 2 over
r3 is the last, and the stop rule applies after it.
