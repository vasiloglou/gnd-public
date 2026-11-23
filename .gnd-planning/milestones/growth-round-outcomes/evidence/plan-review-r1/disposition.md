# Plan review r1: disposition

Reviewed bytes: `notes/growth-round-outcomes-plan.md` r2, sha256
`a041b21d544865d73196d2c4f602231be5d7e77fffd44314de1f01837dae17ba`, commit
`11a7ebf7`. Instrument: the full maintained GND panel (`gnd-review-panel`),
ruled by the owner on 2026-11-23 ("Full panel, both", D7). `reviewer_effort`
xhigh. Panel implementation equal to `HEAD` (`git diff --quiet` over
`src/gnd/review` and both panel skills); the `gnd` import resolved inside the
worktree.

The run used the session's worktree. Its tracked files were clean at
`11a7ebf7`; the request file was the one untracked path. The run directory
was written outside the repository (the session scratchpad). The reviewed
artifact digest was equal before and after (`reviewed_artifacts_*_sha256`
`0cab1c18…0f44` in `run.json`).

    uv run python tools/run_gnd_review_panel.py .gnd-planning/milestones/growth-round-outcomes/evidence/plan-review-r1/review-request.json --out <scratchpad>/go-plan-panel-r1 --reviewer-timeout 900 --overall-timeout 1200
    exit 0 (run by the owner in the terminal pane after approving the launch), run_sha256 324832d2f59b00511f90b580a483d71a281c1042030d8b0d4781bd090c715765
    uv run gnd review finalize <scratchpad>/go-plan-panel-r1 .gnd-planning/milestones/growth-round-outcomes/evidence/plan-review-r1/synthesis.json --out .gnd-planning/milestones/growth-round-outcomes/evidence/plan-review-r1/PANEL-REVIEW.md
    exit 0, synthesis_sha256 8af43439e374c52204dcf42d3933f35751293a15b8051ba03cc458b753c4102c

`<scratchpad>` replaces the operator's session directory (edited for the
home-directory guard). A second launch of the same command by this session
was stopped before it published anything, so the run above is the only one.

Five of six seats succeeded: Claude, Codex, Gemini, Kimi and GLM. Gemini
approved with no concern; the other four asked for revision. Qwen did not
succeed and is not an opinion: status `nonzero`, "Run aborted: wall-clock
budget of 600s exceeded (--max-wall-time)". Claude and GLM share one CLI
codebase. Kimi's response is marked incomplete because one line of prose
came before its head; no concern was dropped. One GLM concern
(`h20-wording-contradicts-r03-d2`) carries no verbatim quotation of the
plan; it was checked against the plan text like the others.

This folder keeps the request, `run.json`, the five `response.json` files
(copied unedited from `<run>/reviewers/<id>/`; none names a local path), the
synthesis and the finalized report. The rest of the run directory (raw
streams, envelopes, probes) is outside history; its digest is `run_sha256`.
The panel is advisory and is not an approval.

## Findings

Every concern was reproduced against the code at `11a7ebf7` or the plan
text before it was accepted. None was rejected. r3 applies them, tagged
`(p1)`.

| Group / concern | Supporters | Reproduced by | r3 change |
|---|---|---|---|
| go1-reader-key (high) | claude, codex, kimi | `model/_parsing.py:37-50`: non-`.json` text starting with `{` falls back to YAML; under `.json` it is refused. A key on content alone, or one restating "`.json` or starts with `{`", returns the YAML-built document to a `.json` caller | R0.5, H5, §2 GO1, §6 row: key = (sha256, suffix is `.json`), one helper |
| go2-refused-preview-shape (high) | claude, glm | `evolve/models.py:1035-1055` requires validation, verbalization, blast radius; `service.py:294-295` raises before any preview | §2 GO2: a separate outcome report for a refused candidate; GO2-C1, GO2-C5 |
| go2-whole-refusals (high) | claude, codex | `_enforce_d12` (`service.py:402-477`) raises at the first fault with messages that name no element; `model/__init__.py:302-304` stops before layer 2 | §2 GO2 "One pass"; D1 (a) restated; `unassessed`; two-fault case in GO2-C2 |
| go2-digests-move (high) | claude, codex, glm | `models.py:1096-1097` "preview and proposal versions must match"; `preview_sha256` binds the body; `_OPTIONAL_PREVIEW_FIELDS` (`models.py:874`) is the omit-when-unset precedent | R0.3, D2 (a), GO2-C3, §5: optional field, no version move |
| go5-empty-round (high) | claude, codex, glm | a round with no proposal has no proposal or preview; a reused element adds no operation | §2 GO5: the host's round file; GO5-C2 |
| go3-stale (medium) | claude, codex, glm | narrowing writes no model bytes, so the original preview's CAS still matches | GO3-C3 split before and after applying the narrowed proposal |
| cross-milestone-order (medium) | claude, codex, kimi | §3 said "merged or not started" and "GO4 at any point"; GO5 edits `unattended-growth.md` with no VG5 condition | §3 rows and order paragraph; READY handshake |
| go1-timing-gate (medium) | claude, codex | C5 is a wall-clock ratio inside the required lane | GO1-C5 recorded, marker excluded from the focused lane |
| codex go1-canonical-date | codex | an unquoted YAML date is kept by the parser (`model/_documents.py`) and canonical JSON cannot spell it | §2 GO1: a type-preserving snapshot |
| kimi go2-c1-exit-3-unverified | kimi | H11 says the exit was not re-read, yet GO2-C1 pinned exit 3 | GO2-C1: "the exit today's refusal gives"; the GO2 spec reads it |
| glm go2-lane-omits-preview-consumers | glm | `tests/test_evolve_population_check.py`, `tests/test_evolve_shape_matches.py`, `tests/test_evolve_source_document.py` read preview fields | §9 GO2 lane widened |
| glm h21-d6-shared-file-claim-incomplete | glm | GO1 and VG1 both write `docs/release-notes.md` and `dev/components/`; VG2/VG5 also touch `tests/test_unattended_growth_guidance.py` | H21, §3 "Other writers" |
| glm h20-wording-contradicts-r03-d2 | glm | H20 "no record changes" against R0.3's added fields | H20 glossed to R0.2 |

Also repaired, found by this session while preparing the review (not a
panel finding): H24's claim that whole-repository `uv run ruff check` exits 1
is refuted; it exits 0 at `11a7ebf7`.

Round 1 had blocking concerns, so the plan's budget of two rounds applies
and r3 goes to a second round.
