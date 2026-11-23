# literature-host-interfaces — close results

Measured at the close commit named in `006-milestone-close.md`. Phase
numbers are gate outputs quoted in the phase records; the close gates are
quoted in the close record.

## Goal predicates (plan, "Goal and completion predicates")

| Predicate | Result | Evidence |
|---|---|---|
| LH1: a public producer protocol; `run()` drives the six stages with a caller's producer over a caller's root; fixture-only steps run on caller data or are recorded skipped; a budget per document; caps as parameters; responses and receipts retained | holds | `002-phase-LH1.md`: LH1-C1 to C14 (T1 to T20, R1 to R9); the three packaged runs equal trees recorded before any edit |
| LH2: `replay()` re-derives a live run with zero producer and reviewer calls, settings from the run, refusing a changed response, receipt or input | holds | `003-phase-LH2.md`: LH2-C1 to C7 (T1 to T9, R1 to R3) |
| LH3: admission of a caller-named assertion entity by its own handle; every attached row kept, with the facts of followed entities; optional facts absent; include roots | holds | `004-phase-LH3.md`: LH3-C1 to C10 (T1 to T10, R1 to R5); the packaged call's four H18 digests |
| LH4: admission rules as caller data, a status of their own, the target cap a parameter | holds | `005-phase-LH4.md`: LH4-C1 to C7 (T1 to T8, R1, R2) |
| the close cites green focused lanes for LH1 to LH4, the guards, the whole-repository lint | holds at close | `006-milestone-close.md` gates |
| replies drafted for #216 and #215 | holds | `notes/issue-replies.md` (not posted; the owner posts) |
| the close review | see the close record | `evidence/close-review/` |

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

The close panel reads the code at the close commit, every unread repair
included.

## Boundaries

- No live provider ran; producers and reviewers in the tests are local
  objects. The corpus and provider-budget run stays with the
  literature-identity follow-up (H20).
- Time bounds are measured on one machine (Apple silicon).
- No stable command changed; `gnd judgments check`'s 1,024-target cap stands.
- The pull requests are open: #241 (reading pair) and #245 (admission pair,
  stacked on #241). Neither is merged.
