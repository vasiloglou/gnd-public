# Plan review r1: disposition

Reviewed bytes: `notes/include-root-routes-plan.md` r2, sha256
`4079c650ad046dcec1087c7cb95b58a71f471743ec511ff670a7426d3027c39b`, commit
`185ccaca`. Instrument: GND panel light, `reviewer_effort` high (bound per
run for Claude and Codex only), run from a disposable worktree at `185ccaca`
whose `gnd` import resolved inside it; panel implementation equal to HEAD.

    uv run python tools/run_gnd_review_panel.py --light .gnd-planning/milestones/include-root-routes/review-request.json --out panel-run --effort high --reviewer-timeout 600 --overall-timeout 900
    exit 0, run_sha256 5e84e32170a44f7e413396828e4ab467ee017b9b1a8b4a54020fe9443df45f40
    uv run gnd review finalize panel-run synthesis.json --out PANEL-REVIEW.md
    exit 0, synthesis_sha256 1bc90c8c7f4a0524a71ae29f2e27b38db94a24ff78f962b3d52e2bc22b114abd

Six of six seats succeeded. Gemini approved with no concern; Claude, Codex,
Qwen, Kimi and GLM requested revision. Claude and GLM share one CLI
codebase. This folder keeps the request, `run.json`, the six
`response.json` files (copied unedited from `panel-run/reviewers/<id>/`;
none names a local path), the synthesis and the finalized report. The rest
of `panel-run/` (raw streams, envelopes, capability probes) stayed in the
disposable worktree and is outside history; its digest is `run_sha256`
above. The panel is advisory and is not an approval.

Every concern was checked against the code at `260c4337` before it was
believed. Class is this disposition's MVP triage, not the reviewer's
severity. All repairs are in plan r3, tagged `(p1)`; r3 carries no review
opinion.

| Reviewer | Concern | Reproduced | Class | Disposition |
|---|---|---|---|---|
| claude | ir1-composed-loader-ignores-reference-root | yes: `_composed_view` binds references under the composition root (`model/__init__.py:362-376`) | hardening, in IR1's own deliverable | fixed: §2 IR1 composes only include roots and binds references at `--reference-root`; IR1-C8 |
| claude | ir1-guard-drop-contradicts-test-r4 | yes | completeness | fixed: §2 IR1 second bullet |
| claude | h6-line-range-off-by-one | yes: `api.py:1195-1198` | completeness | fixed: H6 |
| claude | homes-omit-release-notes-and-route-list | yes | completeness | fixed: §3 homes |
| codex | ir2-cli-registration | yes: commands are registered in `src/gnd/cli.py:650-676` | blocking | fixed: §2 IR2, §3 |
| codex | ir3-include-error-band | yes: `commands/export.py:15-25`, `:45-55` map only `ExportInputError` to 3 | blocking | fixed: §2 IR3, IR3-C7 |
| qwen | r06-contradicts-ir2c5 | yes: rf1 extract goldens pin the include-free temporal message | blocking | fixed: §2 IR2, IR2-C5, R0.6 |
| qwen | ir1-two-model-digests | yes, as an unstated distinction | completeness | fixed: §2 IR1 "Two digests" |
| qwen | ir1c7-model-digest-baseline | yes: r2's §2 wording applied the composed load to every model | hardening | fixed: §2 IR1, IR1-C7 |
| qwen | ir3c3-disjunctive-expectation | yes | hardening | fixed: IR3-C3 fixed at IR3's spec gate |
| qwen | ir1c2-flat-fixture-before-ir2 | no: `flatten_model` shipped in LX1 and IR1 calls it in process; IR1 needs no IR2 code | — | rejected; §3 now says where each input comes from |
| qwen | ir2c2-temporal-parity-scope | yes: the row named no root | completeness | fixed: IR2-C2 |
| qwen | ir3-no-include-refusal-criterion | yes | blocking | fixed: IR3-C7 |
| qwen | criteria-consume-unproduced-fixtures | yes: policies and receipts had no stated author | completeness | fixed: §3 fixture paragraph |
| qwen | test-r4-stays-versus-d6 | partly: D6 governs the API report, `test_R4_judgments` pins the exception of `evaluate_judgments`; the guard wording did contradict | completeness | fixed: §2 IR1 second bullet |
| qwen | guard-tests-absent-from-lanes | no: §9's "all" row runs the guard block, which lists both files | — | rejected; §9 now names them |
| qwen | ir2-homes-omit-extract-tests | yes | hardening | fixed: IR2 lane adds `tests/test_rf1_semantic_pins.py` |
| qwen | ir2-existing-output-undecided | yes | hardening | fixed: exit 11, IR2-C4 |
| qwen | d4-mandatory-pin-premise | no: `parse_declarations` refuses an entry without a 64-hex `sha256` (`model/_includes.py:61-77`) | — | rejected; the goal now cites it |
| qwen | release-notes-absent-from-homes | yes | completeness | fixed: §3 homes |
| kimi | irr2-path-h11-examples-prefix | yes | completeness | fixed: H11 |
| glm | plan-ir1-composed-load-breaks-r06-for-reference-root | yes | hardening | fixed with claude's |
| glm | ir2-c5-extract-message-scope | yes | blocking | fixed with qwen's |
| glm | h11-example-path-mismatch | yes | completeness | fixed: H11 |

## Convergence ledger

| Round | Seats | Per-seat counts | Self-inflicted / total | Blocking / total | Severity ceiling | Verdicts |
|---|---|---|---|---|---|---|
| r1 (over r2) | 6 / 6 | claude 4, codex 2, qwen 14, gemini 0, kimi 1, glm 3 | 0 / 24 (first round) | 5 / 24 | high | 1 approve, 5 revise |

Round budget, declared here before round two: plan §8 planned one round and
a second only if the first blocks. It blocked (5 blocking), so one second
round runs over r3. There is no third round: after r2 the findings are
dispositioned and the plan is gated without another review.
