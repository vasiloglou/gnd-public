# Plan review r2: disposition

Reviewed bytes: `notes/growth-round-outcomes-plan.md` r3, sha256
`2d9e62f80ff03aa03b71e61bb0befb4f3aa75fbc2757e5567f9e3211abcf8d48`, commit
`89ffeee8`. Instrument: the full maintained GND panel, ruled by the owner
("Full panel, both", D7). `reviewer_effort` xhigh. Panel implementation equal
to `HEAD`; the tracked tree was clean at `89ffeee8` and the request file was
the one untracked path. The reviewed artifact digest was equal before and
after.

    uv run python tools/run_gnd_review_panel.py .gnd-planning/milestones/growth-round-outcomes/evidence/plan-review-r2/review-request.json --out <scratchpad>/go-plan-panel-r2 --reviewer-timeout 900 --overall-timeout 1200
    exit 0, run_sha256 dfdb18d6ff606683c92e173c7b128961d86abacb944060bcb1df8abfc34b9ac0
    uv run gnd review finalize <scratchpad>/go-plan-panel-r2 .gnd-planning/milestones/growth-round-outcomes/evidence/plan-review-r2/synthesis.json --out .gnd-planning/milestones/growth-round-outcomes/evidence/plan-review-r2/PANEL-REVIEW.md
    exit 0

`<scratchpad>` replaces the operator's session directory (edited for the
home-directory guard).

Three of six seats succeeded: Claude, Codex and GLM, each with `revise`.
Three did not, and none is an opinion:

| Seat | Status | Reason retained in the envelope |
|---|---|---|
| gemini | `malformed` | "output contains no JSON object" |
| kimi | `malformed` | "malformed JSON precedes the response head" |
| qwen | `nonzero` | "Run aborted: wall-clock budget of 600s exceeded (--max-wall-time)" |

The quorum is met exactly. Claude and GLM share one CLI codebase, so two of
the three opinions are less independent than three unrelated CLIs.

## Findings

All twelve concerns were reproduced against the code at `89ffeee8` or the r3
text; none was rejected. Nine of twelve attack text that the r3 repairs
created (GO2's outcome report, GO3's input, GO5's round file, GO1's control),
which is the convergence signal the bounded rules name. r4 applies them,
tagged `(p2)`.

| Group / concern | Supporters | Reproduced by | r4 change |
|---|---|---|---|
| go3-c1-input (high) | claude, codex, glm | r3 GO2-C1 "no preview is written"; GO3-C1 "from the GO2-C1 preview" | GO3-C1 starts from the outcome report; the report carries the before model; GO3-C3 uses a second fixture |
| go5-added-evidence (high) | claude, codex | a preview exists whether or not it was applied; `apply` can still refuse (`service.py:1889`, `:2189`) | GO5 reads the evolution record for elements added; GO5-C1b |
| go2-outcomes-apply-replay | claude | `cli_service.py:810` replays `shape_report` from the reviewed preview and `:825` compares the fresh one; nothing said outcomes would be replayed | §2 GO2 "Apply replays the setting"; GO2-C6 |
| go2-admitted-unreached-gates | claude | preview runs validation, equality, D-12, policy in order (`service.py:1621-1636`); a validation refusal stops the rest | `unassessed` with gates named; `admitted` means every gate ran; GO2-C1, GO2-C7 |
| go3-origin-no-home | claude | `EvolutionProposal` is closed (`models.py:102-103`, `:646-655`), no origin field | optional origin field under R0.3; `models.py` in GO3 homes |
| go1-shared-doc-control-coverage | claude | `_finish_model` copies the top level only (`model/__init__.py:315`); `documents.py:40-41` "Nested dictionaries/lists remain mutable" | §2 GO1 verify mode across the whole GO1 lane; GO1-C3 |
| d6-forced-by-order | claude | VG plan §3: "VG2 starts from a `main` that holds GO1" | GO1's own PR binding (§3, D6) |
| go5-c1-not-discriminating | claude | GO5-C1 checks only the total | known-mix round in GO5-C1 |
| go1-c5-failure-consequence | claude | r3 said a failed C5 is reported, with no effect | a failed C5 stops GO1 before its PR |
| go1-goal-json-two-parses | claude | `_parse_model_text` hard-codes `model.orm.yaml` (`service.py:344`) | goal "once per reader"; GO1-C1 adds a `.json` model |
| s7-ruff-red-stale | claude | §7 still said ruff was red | §7 reworded |
| h21-vg2-unattended-growth-claim | glm | VG plan §3 homes under its ruled D2 (a) omit `unattended-growth.md` for VG2, though its §3 prose names VG2 | H21 corrected; start conditions kept as the coordinating session set them |

While preparing r4 this session also found and repaired two contradictions
the (p2) changes introduced: `admitted` defined two ways, and GO2-C1's
"three `admitted`" against the new `unassessed` rule. GO3 now keeps
operations that are `admitted` or `unassessed`.

The plan's budget was two rounds. It is spent. r4 is not reviewed; the next
review of these phases is each phase's spec and diff review, and the close
review.
