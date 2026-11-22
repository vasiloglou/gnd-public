# Milestone close review: disposition

Reviewed bytes: the plan with §11 (first form), `notes/close-results.md` and
`notes/close-delta.md` at commit `e99782fe` (digests in `review-request.json`).
Instrument: the full GND panel, `reviewer_effort` xhigh, run from a
disposable worktree at `e99782fe`.

    uv run python tools/run_gnd_review_panel.py close-request.json --out panel-close-run --reviewer-timeout 1500 --overall-timeout 1800
    exit 0, run_sha256 4304fd11dbf30f8b1b2a48aaa335b6f8b0d41e02ef9bc8e027dce1063bd53025
    uv run gnd review finalize panel-close-run synthesis.json --out PANEL-REVIEW.md
    exit 0, synthesis_sha256 c83a1a3bee560f8421cb3e862814b19a31b97fad656c62987e60a54dd10d00e2

All six seats returned schema-valid responses. Dispositions: Codex and
Gemini block; Claude, Qwen, Kimi and GLM revise. The panel is advisory and
approves nothing. Four seats agreed on one blocking concern. Each concern was
checked against the code before its disposition; "Self" marks a concern
that attacks text the close itself wrote.

| Reviewer | Concern | Reproduced | Self | Class | Disposition |
|---|---|---|---|---|---|
| claude, codex, qwen, gemini | LQP verdict on an empty disconnected join (exit 4, GND 2) | yes: `lqp_report` returned 4 on `rp1/disconnected-empty`; GND 2 | no (RP1's stated boundary) | blocking | fixed: the LQP version reads the population; over a derived fact type it refuses at export; `test_lqp_report_bands_a_disconnected_join_as_gnd` (3), `test_lqp_refuses_a_disconnected_join_over_a_derived_fact_type` (plan §11 A10, A2) |
| codex | malformed population escapes exit 3 | yes by reading: `document.get` on a JSON array raises `AttributeError`, uncaught; the regression test confirms exit 3 now | no (predates the milestone) | blocking | fixed: shape checks and `AttributeError` caught in both mains; `test_a_malformed_population_is_refused_with_exit_3` (4) (A11) |
| claude | page messages incomplete; hand-kept list | yes: the role_refs, role_ref, ambiguity refusals were missing | no | hardening | fixed: page and T3 list them; a role named twice is a stated difference, measured (GND exit 1), pinned (A12); "Float or Number" in the older list |
| claude | resolution exits not pinned | yes | no | hardening | fixed: literal exit 4 for the 41 cases |
| claude | goldens disposition cites a comparison after RP3 | yes | yes | completeness | fixed: resolved by RP2's own review evidence |
| claude | counts do not reconcile | yes | yes | completeness | fixed in `close-results.md` |
| claude | delta items 8–10 without §11 rows | yes | yes | completeness | fixed: A8 for the comparator; items 9–10 named as process facts |
| qwen | Ossie byte pins not evidenced | partly: the pins exist (RP1, RP3, RP4 tests) but were not named | yes | hardening | fixed: named in §11 A5 |
| qwen | comparator change unamended, no negative control | yes | no | hardening | fixed: A8 and `test_the_comparator_identifies_1_and_1_0_and_nothing_else` |
| qwen | final edits without a second reader | yes | no | hardening | accepted residual, stated in `close-results.md`; the close panel read both at `e99782fe` |
| qwen | ruff gate narrower than §9 | yes | no | hardening | accepted residual: the known 198 at base `92cd5c9b`, now attributed |
| qwen | eleven vs twelve models | yes | no | completeness | fixed: A9 |
| qwen | §11 quotes not verbatim | yes | yes | completeness | fixed: every quote checked verbatim against r4 |
| kimi | RP3 round count overstated | yes | yes | completeness | fixed: 4 with a verdict, 2 without |
| glm | eleven vs twelve | yes | no | completeness | fixed: A9 |
| glm | RP3 round count | yes | yes | completeness | fixed |
| glm | whole-tree ruff not a gate of 006 | yes | yes | completeness | fixed: attributed to `002-phase-RP2.md` |

Self-inflicted: 7 of 17 concerns attack text the close wrote, below the
convergence rule's 1/2. The repairs were read by one independent reviewer
(Codex through the review helper, `notes/reviews/close-repairs-r1/`)
rather than a second panel round; the close record says so.
