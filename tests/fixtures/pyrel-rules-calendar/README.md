# PyRel rules: calendar and reference corpus (PL14)

`expected.json` holds GND's own verdicts for these populations. It was produced
by `gnd.api.check(model, population, unredacted=True)`, not written by hand.

| Model | What it exercises |
|---|---|
| `clinic` (version 3) | Date and Duration roles. `date_add` with a Duration variable and `date_sub` with a literal, both in guarded comparisons. A tagged date literal in a deontic rule. A Date range and a Duration range. A Date-vs-Date comparison in a derivation's `where` |
| `workload` (version 3) | GND's limit of 10,000 date calculations per rule: 5,000 bindings with two calculations each is at the limit, and 5,001 is over it |
| `refonly/` (version 4) | The shipped dispatch model with its date parts removed, plus its reference catalogue. Before PL14, the generated program ignored references and reported violations GND does not |

## GND behaviour these cases pin

1. Dates compare as dates. A Date's identity is its `YYYY-MM-DD` string, so
   witnesses print dates as strings.
2. `date_add` and `date_sub` move by whole days, leap days included
   (`clinic-on-time-leap-day`: 2024-01-31 + 30 days = 2024-03-01).
3. If any binding computes a date outside 0001-01-01..9999-12-31, the whole
   rule is unchecked (`term:date-out-of-range`), with no witness. This holds
   even when other bindings fail (`clinic-out-of-range-and-failing`).
4. More than 10,000 date calculations in one rule leaves it unchecked
   (`term:temporal-work-limit`).
5. A malformed date or an out-of-range duration in the input is refused
   (exit 3).
6. Reference facts, instances and covers are merged into the candidate's. A
   candidate that names a reference-owned fact type is refused (exit 3).

The shipped `dispatch` and `release` examples, with dates and references
together, are compared live in `tests/test_pyrel_rules_calendar.py`.

## review/

These are the PL14 independent review's reproductions, compared live:
- an empty Date side (`N2`, `N3`, `Z2`);
- date rules left unchecked as the only finding (`E2`, `E3`);
- malformed dates in allowed lists (`J3`, `J4`) and in rosters (`K*`);
- every family over Date roles (`F1`);
- malformed date literals (`D7`, `G*`, `H2`), refused by name;
- a reference owning a derived fact type (`R7`), refused like GND.
