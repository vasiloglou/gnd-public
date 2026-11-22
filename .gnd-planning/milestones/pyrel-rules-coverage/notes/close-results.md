# pyrel-rules-coverage — close results

Measured at `bba37de8` plus the close amendments of plan §11. Every number
below is a gate output quoted in the named phase record.

## Goal predicates (plan, "Goal and completion predicates")

| Predicate | Result | Evidence |
|---|---|---|
| RP1: external uniqueness in `--rules duckdb\|lqp`; `assertions/` and `lineage/` export | holds | `003-phase-RP1.md`: C1–C9; agreement on raw (0), duplicate (1), empty join (2), disconnected (4/4/2), renamed, numeric, three-way |
| RP2: anchored constraints listed as not checked, never compiled | holds | `002-phase-RP2.md`: C1–C8; twelve gold populations agree, exit 4 |
| RP3: `Number` typed like `Float`; integers beyond 2**53 refused by name, cells and constants | holds | `004-phase-RP3.md`: C1–C5, the extended bound (plan §11 A4) |
| RP4: role-scoped value constraints, top level and fact-scoped | holds | `005-phase-RP4.md`: C1–C3; 573 accepted programs byte-identical |
| RP5: every packaged literature model of §1 exports; agreement on the §1 populations; the page states every message | holds | `006-phase-RP5.md`: 12 models × 2 targets; 56 populations agree |

## Last gates (from `006-phase-RP5.md`, cumulative)

- Focused lane: 304 passed, 309 deselected.
- `pyrel_oracle` lane, the five phase files plus the shared suites and plans:
  338 passed, 151 deselected.
- Structure and inventory guard block: 679 passed.
- `uv run ruff check src tests tools`: clean. Whole-tree `ruff check`: 198
  errors, the known red in dev-tools-delivered skill scripts, unchanged
  since the base.

## Review

Phase reviews were one reviewer each (Codex, through the review helper),
with every finding reproduced, fixed or deferred, and regression-tested:

- RP2: 1 round, approved.
- RP1: 3 rounds; r2-F1 was deferred to RP3 and closed there.
- RP3: 5 rounds, plus 2 attempts with no verdict (provider flag). The last
  repair has no second reader.
- RP4: 5 rounds, the last approving.
- RP5: 3 rounds, stopped by the convergence rule. The last sentence has no
  second reader.

## Boundaries

- No RelationalAI engine ran; the LQP programs' enforcement is unverified.
- The programs are stricter than GND by stated design:
  - D4: non-string external ids;
  - D6 and A4: integers beyond 2**53, arithmetic or sums next to Float or
    Number values;
  - repeated facts, including numerically equal rows.
- The LQP version lists a disconnected join as not checked even when GND
  calls it vacuous (exit 4 where GND gives 2).
- Agreement is with `gnd check` without an anchor sidecar.

## Questions

All of plan §10's open questions are resolved (plan §11). No phase record
carries an open question.
