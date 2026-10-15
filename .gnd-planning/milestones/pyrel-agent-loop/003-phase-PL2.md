---
milestone: pyrel-agent-loop
station: phase-PL2
skill: "n/a -- repository development, not a gnd-solve station"
scope: phase-PL2
date: 2026-10-14
source_base: ad85288
gate:
  command: "uv run pytest -q -p no:cacheprovider -m pyrel_oracle tests/test_rules_in_pyrel.py"
  exit: 0
  output: "16 passed in 17.54s"
evidence:
  - {"path": ".gnd-planning/milestones/pyrel-agent-loop/notes/phase-PL2-spec.md"}
  - {"path": ".gnd-planning/milestones/pyrel-agent-loop/notes/phase-PL2-claude-review.md"}
---
# Phase PL2: the rules written in PyRel

Spec: [notes/phase-PL2-spec.md](notes/phase-PL2-spec.md), delegated approval
(auto=true). Implemented and verified on 2026-10-14.

## What landed

- `src/gnd/examples/bookrec/rules_in_pyrel.py` and
  `src/gnd/examples/expense/rules_in_pyrel.py`: the three BookRec rules and
  twelve Expense rules (fourteen under the currency model) written by hand as
  plain PyRel queries over relationships loaded from a population. One line per
  rule or per distinct witness, GND's variable names, exit 1 on an alethic
  violation, exit 2 when a rule is vacuous, exit 3 on an unreadable population.
- Doc twins `docs/assets/applications/{bookrec,expense}-rules-in-pyrel.txt`.
- `tests/test_rules_in_pyrel.py`: witness-for-witness agreement with
  `gnd.api.check` over eleven shipped populations plus an off-corpus
  empty-currency case; pinned witnesses; usage and malformed-input exits; twins.

## Review

One reviewer is one reviewer: a single Claude subagent, report retained verbatim
in `notes/phase-PL2-claude-review.md`. Verdict: revise. It authored 22 extra
populations; the shipped corpus agreed everywhere, and the findings were about
inputs the corpus did not reach.

| # | Class | Finding | Disposition |
|---|---|---|---|
| F1 | blocking (predicate 3) | mandatory currency rule fired where GND is vacuous (empty `expense_has_currency` under the currency model) | fixed: guarded on a non-empty list; off-corpus case added, both sides exit 2 |
| F2 | hardening | closed-world `expense` relation ignored the `instances` roster | fixed: roster ids join the universe |
| F3 | hardening | `OK`/exit 0 where GND reports `vacuous`/exit 2 | fixed: empty antecedents print `vacuous` and exit 2; agreement test maps GND's vacuous verdicts |
| F4 | completeness | docstrings read as the full constraint set | fixed: both docstrings name the constraints left to GND; the page says the same |
| F5 | hardening | value witnesses printed once per distinct value while GND repeats | documented in the test; D2 wording "per distinct value" |
| F6 | completeness | test normalization comment misleading | fixed: mandatory scalars wrapped by constraint type, not rule-name prefix |
| F7 | hardening | error exits collided with exit 1 | fixed: unreadable population exits 3 with a message |
| F8 | notes | plan §2 "one line per rule" wording; RF7 pre-existing failure | plan wording superseded by D2; residual cited |

## Refactoring review

Executed: both scripts share one `report()` shape and table-driven cap and
limit loops; no copied per-rule block remains. Nothing else in the touched
files called for structural change.

## Boundary

The hand-written rules are equivalents for reading and agreement, not the
checker. They cover the top-level rules and the currency model's mandatory and
value rules; uniqueness constraints and the other fact-type mandatory roles are
left to GND, and the files say so. Agreement is proven on the shipped corpus
plus one off-corpus case; the review's 22 scratch populations are not committed.

## Open questions

None new.
