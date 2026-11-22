# pyrel-rules-coverage — close results

Measured at the close commit named in `007-milestone-close.md`. Phase
numbers are gate outputs quoted in the named phase records; the close gates
were run after the close panel's repairs and are quoted in the close record.

## Goal predicates (plan, "Goal and completion predicates")

| Predicate | Result | Evidence |
|---|---|---|
| RP1: external uniqueness in `--rules duckdb\|lqp`; `assertions/` and `lineage/` export | holds | `003-phase-RP1.md`: C1–C9. Agreement on raw (0), duplicate (1), empty join (2), disconnected (4/4/2), renamed, numeric, three-way. Since the close (plan §11 A10), the LQP version also gives exit 2 for an empty disconnected join |
| RP2: anchored constraints listed as not checked, never compiled | holds | `002-phase-RP2.md`: C1–C8; twelve gold populations agree, exit 4 |
| RP3: `Number` typed like `Float`; integers beyond 2**53 refused by name, cells and constants | holds | `004-phase-RP3.md`: C1–C5, with the extended bound (A4) |
| RP4: role-scoped value constraints, top level and fact-scoped | holds | `005-phase-RP4.md`: C1–C3; 573 programs accepted at its base are byte-identical |
| RP5: every packaged literature model of §1 exports; agreement on the §1 populations; the page states every message | holds | `006-phase-RP5.md`: twelve models (A9) × 2 targets. 56 populations agree, the 41 resolution cases with a literal exit 4 since the close |

Ossie byte pins for each newly lowerable shape are named in plan §11 A5.

## Review

Phase reviews were one reviewer each (Codex, through the review helper).
Every finding was reproduced, then fixed or deferred, with a regression
test:

| Phase | Rounds with a verdict | Last verdict | Note |
|---|---|---|---|
| RP2 | 1 | APPROVE | — |
| RP1 | 3 | CHANGES_REQUESTED | r2-F1 deferred to RP3, closed there; stopped by the convergence rule (2/2 self-inflicted) |
| RP3 | 4 (r1, r2, r3, r5) | CHANGES_REQUESTED | 2 more attempts (r4, r6) ended without a verdict (provider flag); the r5 repair has no second phase reader |
| RP4 | 5 | APPROVE | — |
| RP5 | 3 | CHANGES_REQUESTED | stopped by the convergence rule (1/1); the last sentence has no second phase reader |

Plan §8 asks for one independent reviewer over each phase's diff. The two
unreread repairs are accepted residuals of that protocol. The close panel
read the code at `e99782fe`, both repairs included; its own repairs had a
Codex read (`007-milestone-close.md`).

## Boundaries

- No RelationalAI engine ran; the LQP programs' enforcement is unverified.
  The LQP version relays engine reports only and does not report a compiled
  rule as vacuous (`docs/runtimes/pyrel.md`).
- The programs are stricter than GND by stated design:
  - D4: non-string external ids;
  - D6 and A4: integers beyond 2**53, arithmetic or sums next to Float or
    Number values;
  - repeated facts, including numerically equal rows (A3);
  - a role named twice in `role_refs` (A12);
  - in the LQP version, a disconnected join over a derived fact type (A2).
- Agreement is with `gnd check` without an anchor sidecar.
- Whole-tree `uv run ruff check` stays red with the 198 errors present at
  the base `92cd5c9b` (proven in `002-phase-RP2.md`), all in
  dev-tools-delivered skill scripts. This is a residual against plan §9's
  whole-tree "exit 0"; `uv run ruff check src tests tools` is clean.

## Questions

All of plan §10's open questions are resolved (plan §11). No phase record
carries an open question.
