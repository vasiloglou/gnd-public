# Plan review r2: disposition

Reviewed bytes: `notes/pyrel-rules-coverage-plan.md` r3, sha256
`077871ed1e7b5e2adad1b47ae5fab84603c24ea54d406794a663aaaefd874179`, commit
`5b1df6fb`. Instrument: the full GND panel, `reviewer_effort` xhigh, run
from a disposable worktree at `5b1df6fb` with the same command as round 1.

    uv run python tools/run_gnd_review_panel.py .gnd-planning/milestones/pyrel-rules-coverage/review-request.json --out panel-run --reviewer-timeout 1500 --overall-timeout 1800
    exit 0, run_sha256 1744b2cbcf2a04f3b76424cf99cd87d8749b8da87d3bc0a7674c11d21e418475
    uv run gnd review finalize panel-run synthesis.json --out PANEL-REVIEW.md
    exit 0, synthesis.json sha256 0021bd14c428880344fdf61994219d9c24fcf0ef963793566053639f90af5cb1

Four of six seats returned schema-valid responses: Codex, Qwen, Kimi and
GLM. Claude and Gemini returned malformed output. Kimi approved after
checking about forty cited locations; Codex, Qwen and GLM asked for
revision. No concern was raised by two seats. Files kept as in round 1.
The panel is advisory and approves nothing.

Each concern was checked against the code at `8c909013`, by measurement
where it turned on GND behaviour. Repairs are in r4, tagged `(p2)`; r4
carries no review opinion. "Self" marks a concern that attacks text the
round-1 repair (`(p1)`) created.

| Reviewer | Concern | Reproduced | Self | Class | Disposition |
|---|---|---|---|---|---|
| codex | rp1-join-refusal-vacuity-order | yes, measured: a disconnected join is vacuous (exit 2) with both lists empty, unchecked (exit 4) with facts | yes | blocking | fixed: §1, §2 RP1, RP1-C6 |
| codex | rp2-anchored-empty-subject | **no**, measured: with `time_step` empty, in `covers` or not, the anchored rule stays unchecked (exit 4); its scope hook returns no subjects, so the vacuity branch at `semantic_spec.py:2922-2925` never applies | no | — | rejected; the measurement is recorded in §1 and pinned by RP2-C8 |
| codex | rp3-model-numeric-literals | yes: `_allowed` writes model constants into a `Float` helper | yes | blocking | fixed: D6 and RP3-C5 |
| qwen | r3-line-882-two-opposite-treatments | yes: one line raises for both families | no | completeness | fixed: §1, §2 RP1 |
| qwen | r3-rp2c4-byte-identity-vs-lqp-textual-line | yes | yes | blocking | fixed: RP2-C4 scoped to the DuckDB program |
| qwen | r3-rp2c7-default-lane-executes-lqp | yes: §0 says the default lane executes no program | yes | blocking | fixed: RP2-C7 runs in the oracle lane |
| qwen | r3-rp3c2-boolean-exit-unmeasured | yes; measured: `gnd check` exits 3 (`population:type-mismatch`) | no | completeness | fixed: §1, RP3-C2 |
| qwen | r3-d6-float-bound-unmeasured-populations | yes; measured: no packaged population holds an integer beyond 2**53 | yes | completeness | fixed: §1 |
| qwen | r3-success-line-scope-vs-frozen-default-export | yes: the rules path has its own function (`commands/export.py:40-65`) | no | hardening | fixed: §2 RP2, RP2-C5 |
| qwen | r3-rp5c1-acceptance-table-undefined | yes | no | hardening | fixed: RP5-C1 lists eleven models |
| qwen | r3-rp5c3-not-falsifiable | yes | no | hardening | fixed: RP5-C3 |
| qwen | r3-rp1-numeric-anchor-no-criterion | yes | yes | hardening | fixed: RP1-C8 |
| qwen | r3-rp1-join-arity | yes, as unstated | no | hardening | fixed: §2 RP1, RP1-C9 |
| qwen | r3-d5-modality-gap | yes, as unstated | no | completeness | fixed: §2 RP2, D5 |
| qwen | r3-round1-blocking-evidence | yes | yes | completeness | fixed: §8 |
| glm | r2-population-count-resolution-41 | yes: 41 files | yes | completeness | fixed: §1 |
| glm | r2-lanes-not-cumulative-rp3-rp5 | yes | yes | hardening | fixed: §9 |
| glm | r2-ossie-backstop-misses-new-shapes | yes: `tests/test_ossie_formulas.py` has no value-family case | yes | hardening | fixed: §3 Ossie pins |
| glm | r2-rp1-spec-diverges-from-plan-homes-lanes | yes | yes | completeness | fixed: §3 homes; RP1 spec ledger |

## Refuted premise (from round 1)

Round 1's disposition accepted that GND reports an **ambiguous** external
join as unchecked, reading `semantic_spec.py:2665-2672`. Measured on
2026-11-21: `gnd validate` and `gnd check` refuse such a model with
`semantic:join-anchor-ambiguous`, exit 3, and the rules export already
refuses it as `invalid model` (exit 3). r3's repair (list it as not
checked) was wrong; r4 replaces it with RP1-C7, which pins the existing
refusal on both sides. The round-1 row stays as written.

## Convergence ledger

| Round | Seats | Per-seat counts | Self-inflicted / total | Blocking / total | Severity ceiling | Verdicts |
|---|---|---|---|---|---|---|
| r1 (over r2) | 4 / 6 | claude 9, codex 4, kimi 1, glm 5 | 0 / 19 | 6 / 19 | high | 4 revise |
| r2 (over r3) | 4 / 6 | codex 3, qwen 12, kimi 0, glm 4 | 12 / 19 | 4 / 19 | high (reviewer); 4 blocking by this triage | 1 approve, 3 revise |

The self-inflicted ratio is 12/19 > 1/2, so the stop rule fires. The
declared budget was two rounds. r4 goes to the delegated plan gate
unreviewed, and implementation is the next instrument.
