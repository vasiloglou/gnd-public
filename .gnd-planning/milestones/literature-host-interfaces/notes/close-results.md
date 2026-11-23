# literature-host-interfaces — close results

Measured at the close, on the tree of the close commit (the commit that
adds `006-milestone-close.md`, whose parent is `19a53466` plus the review and
index files it stages), gnd 0.4.0. Phase numbers are gate outputs quoted in
the phase records.

## Close gates

| Command | Result |
|---|---|
| `uv run pytest -q` over the eleven focused files of LH1 to LH4 and their consumers (`test_lh1_reading_host`, `test_lh2_reading_replay`, `test_lh3_admission_shape`, `test_lh4_admission_rules`, `test_ld3_reading_workflow`, `test_ld4_revision`, `test_ld5_verdict`, `test_li1_assurance_report`, `test_ld1_competency_examples`, `test_li4_assertions`, `test_li5_lineage`) | exit 0, `381 passed in 376.71s` |
| `uv run python tools/run_tutorials.py --group literature` | exit 0, `15 tutorial blocks passed` |
| the `project.md` guard block (12 files) | exit 0, `679 passed, 2 deselected in 128.70s` |
| `uv run ruff check` | exit 0, `All checks passed!` |
| `python3 scripts/components_index.py changed --base origin/main --strict` | exit 0, `0 to fix, 0 warning(s), 1 to reread` (`examples.literature_depth`, still accurate) |

The three packaged runs equal the trees recorded at `78934ee3` before any
edit, file for file through `tests/support/recorded_version.py` at
`RECORDED_AT = "0.4.0"`; their `run.json` digests are `ee67e13c…fd1c`,
`d4010f94…6ddf` and `7dcf43ec…a071` (H11, LH1 T11). The packaged admission's
four outputs keep their H18 digests (LH3 T8).

## Goal predicates (plan, "Goal and completion predicates")

| Predicate | Result | Evidence |
|---|---|---|
| LH1: a public producer protocol; `run()` drives the six stages with a caller's producer over a caller's root; fixture-only steps run on caller data or are recorded skipped; a budget per document; caps as parameters; responses and receipts retained | holds | `002-phase-LH1.md`: LH1-C1 to C14 (T1 to T20, R1 to R9); the three packaged runs equal trees recorded before any edit |
| LH2: `replay()` re-derives a live run with zero producer and reviewer calls, settings from the run, refusing a changed response, receipt or input | holds | `003-phase-LH2.md`: LH2-C1 to C7 (T1 to T9, R1 to R3) |
| LH3: admission of a caller-named assertion entity by its own handle; every attached row kept, with the facts of followed entities; optional facts absent; include roots | holds | `004-phase-LH3.md`: LH3-C1 to C10 (T1 to T10, R1 to R5); the packaged call's four H18 digests. Handles compare as the checker compares values (`test_r1_a_boolean_handle_is_not_a_number`, `test_r1_one_and_one_point_zero_are_one_number`) |
| LH4: admission rules as caller data, a status of their own, the target cap a parameter | holds | `005-phase-LH4.md`: LH4-C1 to C7 (T1 to T8, R1, R2) |
| the close cites green focused lanes for LH1 to LH4, the guards, the whole-repository lint | holds | "Close gates" above, and `006-milestone-close.md` |
| replies drafted for #216 and #215 | holds | `notes/issue-replies.md` (not posted; the owner posts) |
| the close review | ran | full GND panel, `evidence/close-review/PANEL-REVIEW.md`; dispositions in `006-milestone-close.md` |

## Review

Each phase diff had one reviewer (Codex, in the other harness, through the
review helper). Every finding was reproduced, then fixed with a regression
test that failed before its fix.

| Phase | Rounds | Findings | Blocking | Last verdict | Unread repair |
|---|---|---|---|---|---|
| LH1 | 2 | 8 | 6 | CHANGES_REQUESTED | `59fd62f0` (round 2 declared last) |
| LH2 | 1 | 3 | 1 | CHANGES_REQUESTED | `9df661c8` |
| LH3 | 2 | 5 | 2 | CHANGES_REQUESTED | `f718b572` (round 2 declared last) |
| LH4 | 1 | 2 | 1 | CHANGES_REQUESTED | `4428a24d` |

The close panel (full GND panel, the owner's word "full") ran at
`9abb436a`, every phase repair included. Of its four successful seats,
Codex, Gemini and Kimi read the code; Qwen was given the three close
artifacts inline, as its seat always is, and read no code. Claude and GLM
timed out. The close panel's own repair (empty fact lists, `19a53466`) had
one Codex read (`notes/reviews/close-repairs-r1/`), which found no runtime
counterexample.

## Boundaries

- No live provider ran; producers and reviewers in the tests are local
  objects. The corpus and provider-budget run stays with the
  literature-identity follow-up (H20).
- Time bounds are measured on one machine (Apple silicon).
- No stable command changed; `gnd judgments check`'s 1,024-target cap stands.
- The pull requests are open: #241 (reading pair) and #245 (admission pair,
  stacked on #241). Neither is merged.
