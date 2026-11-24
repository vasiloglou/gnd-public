# Close review: disposition

The full GND panel (D7, the owner's "Full panel, both") over the close bundle
at `e111e59a`: plan r4, `notes/close-results.md`, `notes/close-delta.md`.
Quorum established with four of six seats (codex, qwen, kimi, glm), each
`revise`; claude and gemini returned malformed output and contribute no
opinion. [PANEL-REVIEW.md](PANEL-REVIEW.md) is the rendered synthesis. A
concern is believed only once it is reproduced; each fixed one has a test
that fails at `e111e59a` and passes at `32a50ed7`.

| Reviewer | Concern | Class (ours) | Reproduced | Disposition |
|---|---|---|---|---|
| codex | `go4-orphaned-subtype`: the reply example links `insurer` as a subtype but does not add it | blocking | yes: translating the example raises `KeyError` | fixed: the example adds `insurer`; `test_go4_close_the_example_links_only_a_subtype_it_adds` |
| codex | `go5-empty-counts`: an empty round reports `null` outcomes and shape matches | blocking | yes | fixed: `{}` and `0` without a proposal; the contract says so; `test_close_an_empty_round_is_zero_in_every_count` |
| codex, qwen (agreed) | `go4-multiline-code-span`, `markdown-sections-unreviewed-new-reader` | hardening | yes: `<!--` inside a code span continued onto the next line was read as a comment | fixed: the open span is carried across the paragraph's lines; `test_go4_close_a_code_span_may_continue_onto_the_next_line`. This panel is the reader's review |
| qwen | `close-results-green-evidence-predates-head` | completeness | yes: the whole lane ran at `a30b6192` | fixed: the whole lane ran again at `32a50ed7` (`evidence/GO2-GO5/full-lane.md`), and the close record cites it |
| qwen | `d4-refutation-contradicts-go2-preview-verdicts` | n/a | no | rejected: in `src/gnd/evolve/policy.py` an element `add` is admitted (`if kind is _ADD: ... continue`), so a written preview's only refusals are the policy's and none removes an element another operation needs; every other refusal (validation, D-12) writes no preview. The verdict list allows `dropped-with` in an outcome report, which is where the test counts it. Recorded as plan amendment A2 |
| qwen | `d7-substitutes-ruled-diff-review` | hardening | yes: the budget's second single-reviewer rounds for GO4 and GO3–GO5 were not run | accepted as a residual: D8 sets the phase instrument and a ceiling of two rounds, not an obligation to spend the second; this close panel read those repairs and its findings are fixed. Named in the close record |
| qwen, glm (agreed) | `close-results-omit-non-pytest-gates`, `close-record-missing-gate-citations` | completeness | yes | fixed: the close record cites every gate command with exit and output at the close head |
| qwen | `d8-omits-conftest-autouse-fixture` | completeness | yes | fixed in the close record's file list (`tests/conftest.py` is GO1's, merged with GO1) |
| qwen | `go1-c5-ratio-indistinguishable-from-prototype` | completeness | partly: `evidence/GO1/t8-ratio.json` holds the four timings (on 2.04 s and 2.05 s, off 8.27 s and 6.59 s), so the figure is measured; it equals the prototype's 0.31 by coincidence of rounding | no change; the close record quotes the timings |
| kimi | `gr-out-close-go4c2-count`: one of the eleven cases is a no-op control | completeness | yes | fixed in the close record's wording: ten edits fail the guard, one control does not |
| glm | `go3-narrow-before-model-json-escape`: a before model JSON cannot spell escaped as `ModelValueError` | hardening | yes | fixed: a named `ValueError` ("cannot be replayed"); `test_close_a_before_model_json_cannot_spell_is_refused_by_name` |
| glm | `go5-summary-row-reference-unchecked` | hardening | yes | fixed: the reference is checked too, as in narrowing; `test_close_a_row_with_another_operations_reference_is_refused` |

The close repairs (`32a50ed7`) are read by no reviewer. No second panel
round runs: the budget is one close review, and no concern was left open.
