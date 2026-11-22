# Plan review r2: disposition

Reviewed bytes: `notes/include-root-routes-plan.md` r3, sha256
`bf150b5b7e40eb92230b5103b012bbb2533e2ce11f0e7b95b3e00b2e832ea45a`, commit
`c1d7219b`. Same instrument as round 1 (GND panel light, `reviewer_effort`
high, bound per run for Claude and Codex only), from a disposable worktree
at `c1d7219b` whose `gnd` import resolved inside it.

    uv run python tools/run_gnd_review_panel.py --light .gnd-planning/milestones/include-root-routes/review-request-r2.json --out panel-run --effort high --reviewer-timeout 600 --overall-timeout 900
    exit 0, run_sha256 2ea9bb2cfd6617615597b8573f97d46a18b89506dee394c7341eb53c9c7fd6f5
    uv run gnd review finalize panel-run synthesis.json --out PANEL-REVIEW.md
    exit 0, synthesis_sha256 92f4b2ed0b36d35b90681a1d9f05394c6731c4528c1875078fd12e098ac7d9f1

Three of six seats succeeded, the quorum exactly: Claude, Codex and GLM,
all `revise`. Claude and GLM share one CLI codebase, so this quorum is
weaker evidence of independence than round 1's. Not counted, and kept as
failures in `envelopes/`: Qwen `timeout` ("reviewer invocation exceeded its
shared deadline"), Gemini `malformed` ("output contains no JSON object"),
Kimi `malformed` ("an approve response cannot carry unread lines"). Kimi's
retained output appears to approve, but a malformed response is not an
opinion and is not counted. The request was saved in the panel worktree as
`review-request-r2.json`; it is kept here as `review-request.json`.

| Reviewer | Concern | Reproduced | Class | Self-inflicted | Disposition |
|---|---|---|---|---|---|
| codex | ir1-draft-spec-reference-root | yes, for the spec bytes at `c1d7219b` (spec r1 line 96); the plan r3 text is correct | hardening | yes: the gap between a `(p1)` plan sentence and the unrepaired spec | fixed in spec r2 (`40d3265b`) by `load_model_bytes_composed(..., bind_references=False)`; T12 pins IR1-C8 |
| glm | ir1-spec-draft-contradicts-r3-composed-route | same | hardening | yes | fixed with codex's |
| claude | ir2-flat-model-reference-paths | yes: `flatten_model` keeps relative `reference_populations` paths (`model/flattening.py:33-35`) | hardening, in IR2's own deliverable | no | fixed in r4 §2 IR2 and IR2-C2; the refusal choice goes to the IR2 spec |
| claude | flat-file-name-inconsistent | yes: `_flattening_names` uses the stem `checking.orm` | completeness | yes: IR2-C2 was a `(p1)` sentence | fixed in r4: H7 marked probe-local, IR3-C1 renamed |
| glm | r06-scope-orphan-fact-type-constraints | yes: `declares_includes` is true for `fact_type_constraints` alone (`model/_includes.py:56-58`), and 0.4.0 refuses it `include:unsupported-route` | hardening | no | fixed in r4 R0.6 and IR1-C9; T13 pins it |

## Convergence ledger

| Round | Seats | Per-seat counts | Self-inflicted / total | Blocking / total | Severity ceiling | Verdicts |
|---|---|---|---|---|---|---|
| r1 (over r2) | 6 / 6 | claude 4, codex 2, qwen 14, gemini 0, kimi 1, glm 3 | 0 / 24 | 5 / 24 | high | 1 approve, 5 revise |
| r2 (over r3) | 3 / 6 | claude 2, codex 1, glm 2 | 3 / 5 | 0 / 5 | high | 3 revise |

The self-inflicted ratio (3/5) is over one half and no round-2 finding is
blocking: the stop rule fires, and the declared budget (two rounds) is spent.
Plan r4 applies the four fixes, tagged `(p2)`, and goes to the plan gate
without a third review. r4 carries no review opinion. The panel is advisory
and is not an approval.
