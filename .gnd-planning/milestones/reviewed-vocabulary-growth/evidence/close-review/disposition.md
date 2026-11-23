# Close review: disposition

Reviewed bytes: plan r5 (`notes/reviewed-vocabulary-growth-plan.md`, sha256
`362557f3ea689ae326171b1b4dbf6a4704cf21146a68ca91b3a7d31f57b4ba7c`),
`notes/close-results.md` and `notes/close-delta.md` at `d95dc418`.
Instrument: GND panel light, the close review the plan gate selected (D8),
run at the owner's request ("Run the close", 2026-11-23). `reviewer_effort`
high, bound per run for Claude and Codex only. The tree was clean at
`d95dc418`, the panel implementation equal to `HEAD`, and the reviewed
artifacts unchanged before and after.

    uv run python tools/run_gnd_review_panel.py --light .gnd-planning/milestones/reviewed-vocabulary-growth/evidence/close-review/review-request.json --out panel-run --effort high --reviewer-timeout 600 --overall-timeout 900
    exit 0, quorum-established, run_sha256 c2e9ff49866979e6e7b8147e5d211fb6ac89aca24f96f7f1be4f3263d31d007b
    uv run gnd review finalize panel-run .gnd-planning/milestones/reviewed-vocabulary-growth/evidence/close-review/synthesis.json --out .gnd-planning/milestones/reviewed-vocabulary-growth/evidence/close-review/PANEL-REVIEW.md
    exit 0, synthesis_sha256 7ffe0ffcf08b238954a88029fdb9f497407bc1924d6418571e4efcda8923ea15

Four of six seats succeeded: Codex approved with no concern; Claude, Kimi
and GLM asked for revision. Qwen timed out at the 600-second reviewer
deadline and Gemini returned no JSON; neither is an opinion. No concern has
two supporters, so all four are divergent views. The panel is advisory and
is not an approval.

This folder keeps the request, `run.json`, the four `response.json` files
(copied unedited; none names a local path), the synthesis and the finalized
report. The rest of the run is outside history; its digest is above.

## Findings

Each was checked against the bytes before it was believed. Class is this
disposition's MVP triage.

| Reviewer | Concern | Reproduced | Class | Disposition |
|---|---|---|---|---|
| claude | vg4-u1-composed-reading-unrecorded | yes: plan §2 says the first-document test "cannot be read on the composed document"; `_owns_nothing` (`model/_unattended.py`) reads exactly that, with VG3's origin set; §3 names a `model/__init__.py` home that VG4 did not change; the §10 question "how the root's own document reaches U1" was missing from the results | completeness | repaired: plan §11 amendment 6, the delta's VG4 bullet and item 6, a results row |
| claude | cache-key-residual-understated | yes: `model_index.py` falls back to the cached rows past the routed reader's caps, which the VG1 record states and amendment 5 did not | completeness | repaired: amendment 5, the delta's item 5, the results row |
| kimi | rvg-close-1 | yes: §7 still called the whole-repository ruff red | completeness | repaired: §7 bullet annotated `(c2)` |
| glm | vg3-c7-remap-scope-unmodeled-include-roots | in part. The span-walk case cannot occur: a root without the mode declares no document, so every `--document` is refused as undeclared before a span is re-hashed (VG3 T7's base outputs hold that). The object-type remapping does apply to every include root, but only to an error on an included object type, which a standalone-valid include cannot carry; the exit is 3 either way and the prefix is what "Model includes" promised | hardening | repaired as a statement: plan §11 amendment 7 (§5, Compatibility); no fixture case, since no input reaches it |

No concern was rejected. All four repairs are text in the close bundle; no
code changed. The repaired bytes (plan r6, the results and the delta) carry
no review opinion.
