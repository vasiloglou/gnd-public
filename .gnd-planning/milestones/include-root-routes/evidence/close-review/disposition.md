# Close review: disposition

Reviewed bytes, commit `f48659b1`: plan r5 (`notes/include-root-routes-plan.md`,
sha256 `d090387762a75d0c64bfd8c16f16af53776dce46e923753fbd98984021af1a3d`),
`notes/close-results.md` (sha256 `012dad61cab5…`) and `notes/close-delta.md`
(sha256 `fdf2d287d362…`), as one `spec-results-delta` request. Instrument:
GND panel light, `reviewer_effort` high (bound per run for Claude and Codex
only), from a disposable worktree at `f48659b1` whose `gnd` import resolved
inside it.

    uv run python tools/run_gnd_review_panel.py --light .gnd-planning/milestones/include-root-routes/close-review-request.json --out panel-run --effort high --reviewer-timeout 600 --overall-timeout 900
    exit 0, run_sha256 f3218632ec79a4a22da5d9b96f3e61b6ddea79e12228422b93a5dd1ffff9a47b
    uv run gnd review finalize panel-run synthesis.json --out PANEL-REVIEW.md
    exit 0 (outcome quorum-established; 5 agreed, 5 divergent, 7 fixes)

Six of six seats succeeded. Gemini approved; Claude, Codex, Qwen, Kimi and
GLM asked for revision. Claude and GLM share one CLI codebase. The six
responses, `run.json`, the request, the synthesis and the report are kept
here unedited; none names a local path. The rest of `panel-run/` is outside
history. The panel is advisory and is not an approval.

Every concern was checked against the code and records before it was
believed. All repairs are in `0e1b7fb6` and plan r6, tagged `(c2)`; they
carry no review opinion.

| Reviewer | Concern | Reproduced | Class | Disposition |
|---|---|---|---|---|
| claude, codex, qwen, kimi, glm | the plan's close predicate requires a green whole-repository `uv run ruff check`, which exits 1 | yes: exit 1 at `90ac280c`, all in dev-tools scripts, also red on `185ccaca` | blocking for the close as written (Codex, Qwen), hardening in substance: no code of this milestone is involved | fixed by amendment (c2): the gate is `ruff check src tests tools`; the whole-repository exit is recorded and carried with an owner; ruled in the close record |
| qwen, glm | the refusal-naming predicate is marked met while an unencodable include path gives a codec message | yes: `gnd validate`, `gnd flatten`, `gnd judgments check` and all three export modes | blocking: a goal predicate was not met | fixed: `compose` refuses such a path `include:path` (`model/_includes.py`); seven cases in `tests/test_include_root_close.py`, red before the fix |
| qwen | the delta omits that behaviour change | yes | completeness | fixed: `notes/close-delta.md` adds it |
| qwen, kimi | carried questions name no owner or target | yes | completeness | fixed in the close record's sweep: each carried row names its owner |
| claude, qwen | the union lane cites 19 files where §9 unions to 18, and no command | yes: the run added `tests/test_pyrel_learning_path.py`, a widening IR3 recorded | completeness | fixed: the close record gives the exact file list (now 21 with the close-repair file and `tests/test_mc1_census.py`) |
| claude, qwen | §11 paraphrases r4 and says "seven" inventories against six paths | yes | completeness | fixed: §11 quotes r4 verbatim from `1e419a88`; six paths |
| qwen | judgments-versus-`gnd check` parity is asserted, not tested (T2 compares two judgments runs) | yes | hardening | fixed: `test_judgments_mechanical_report_equals_gnd_check` (model digest, verdicts, reference binding); it passes on the reviewed code, so it is a new pin, not a defect fix |
| claude | the delta's orphan-attachment claim has no IR3 case | yes | hardening | fixed: `test_export_refuses_orphan_attachments_as_declaration`, three modes; passes on the reviewed code (new pin) |
| qwen | `src/gnd/extract/flatten_service.py` is in no plan home | yes | completeness | fixed: §3 and §11 (c2) |
| glm | the two plan-gate questions cite phase records that do not contain IR2-D2 and IR3-D5 | yes: the rulings are in the spec files | completeness | fixed in the close record's sweep |
| glm | §11's preamble says every row came from a phase record, but the §8 row came from `project.md` | yes | completeness | fixed: preamble and row |

## Convergence

One close round, as plan §8 provides. Blocking / total: 2 groups of 10
items (the lint predicate as written, the refusal predicate). No second
close round was run: the blocking items were a predicate amendment and a
one-line refusal fix with its regression cases; the repairs are recorded as
unreviewed in the close record.
