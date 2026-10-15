# Phase PL2 spec: the rules written in PyRel

## 1. Status

owner-decided (2026-10-14): delegated approval under
[`001-plan-gate.md`](../001-plan-gate.md). Implementable; PL1 landed.

## 2. Provenance

Plan r1 §2 (rules in PyRel), §4 PL2 row, §9 PL2 row, PL-R4, PL-R8. Measured
before writing: PyRel 1.30.1 accepts a direct literal comparison (`a > 100`),
`not_` over a fresh `.ref()`, `not_` over an undefined relation, and value
filters (`c != 'EUR'`), so no literal relation is needed. No review round yet.

## 3. Obligations

| Source | Obligation | Discharge |
|---|---|---|
| Owner review: "rules and constraints written in pyrel as well" | each rule as a plain PyRel query | §6.1–6.2 |
| Completion predicate 3 | hand-written queries print the same witness GND prints; agreement test | §8 rows 1–2 |
| PL-R4 | labelled as equivalents, never as emitted text | module docstrings; page wording at PL5 |
| PL-R5 | pinned witnesses printed | §8 row 2 |
| PL-R8 | RF7 allowlist; doc twins byte-pinned | §6.3, §8 rows 4–5 |
| Standing rule 1 | bounded read of the population; `json.loads` on bounded bytes | `LIMIT = 1 << 20` |
| Standing rule 2 | work proportional to facts only; no input-controlled quadratic step beyond DuckDB joins over tutorial-sized inputs | §6 |

## 4. Standing rules, bound

1. Totality: the scripts read at most one MiB and refuse larger input with a
   message; malformed JSON raises in the script, which is a tutorial tool, not a
   gate. 2. Bounds: argued above. 3. Validation order: usage error before any
   read. 4. One walk: caps and limits are table-driven loops, not one block per
   category. 5. One home: the rule text lives in the model; the scripts say they
   are equivalents. 6. Measurement: the agreement test is the instrument.

## 5. Goal

`"$GND_PYREL_PYTHON" bookrec-native/rules_in_pyrel.py bookrec-native/adult-for-minor.population.json`
prints `age_appropriate  violated  {"$b": "night", "$u": "ada"}` and exits 1;
the Expense twin prints `approval_limit_team_lead  violated  {"$a": 800, "$e": 102}`
on `invalid-chain.population.json`; `tests/test_rules_in_pyrel.py` exits 0
under `-m pyrel_oracle` over eleven corpus cases.

## 6. Design

### 6.1 `src/gnd/examples/bookrec/rules_in_pyrel.py` (~100 lines)

`load_facts(path) -> dict`, `check(facts) -> list[tuple[rule, status, witness]]`,
`main(argv) -> int`. One `Relationship` per fact type (`String` fields), loaded
with `m.define`. Rules: `unread_only` = `where(recommendation(u,b), user_rated_book(u,b))`;
`age_appropriate` = `where(recommendation(u,b), user_is_minor(u), book_rated_adult(b))`;
`preferred_genre` = `where(recommendation(u,b), book_has_genre(b,g), not_(user_prefers_genre(u,g)))`
reported as `warning`. Output line: `f'{rule}  {status}  {json.dumps(witness, sort_keys=True)}'`
or `f'{rule}  OK'`. Exit 1 on any `violated`.

### 6.2 `src/gnd/examples/expense/rules_in_pyrel.py` (~140 lines)

Same shape, `Integer` and `String` fields. Guarded comparisons from the tables
`CATEGORY_CAPS` and `CHAIN_LIMITS` plus `positive_amount`; subset rules with
`not_` over a fresh ref; value rules with `*[c != v for v in allowed]`; when the
population covers `expense_has_currency`, the mandatory rule over a closed-world
`expense` relation (every id in any fact list) and `supported_currency`.
Witness shapes follow GND: dict for guarded, `[id]` for subset and mandatory,
bare value for value rules.

### 6.3 Twins and pins

`docs/assets/applications/{bookrec,expense}-rules-in-pyrel.txt` byte-identical;
RF7 allowlist entries for both scripts.

## 7. Decisions

| # | Question | Readings | Ruling |
|---|---|---|---|
| D1 | Script reads the model file | (a) yes, for caps; (b) no, caps are hand-written literals | (b): the point is that a person wrote the rule in PyRel; the agreement test catches drift |
| D2 | Mandatory witness shape | GND reports `[101, 102]` once; app text shows `[101]`, `[102]` | one line per value, `[id]`, matching the app's text output |

## 8. Tests

| File | Case | Expected |
|---|---|---|
| `tests/test_rules_in_pyrel.py::test_hand_written_rules_agree_with_gnd` | 11 corpus cases, witness sets equal, exits equal | pass |
| `::test_bad_candidates_print_the_pinned_witnesses` | three pinned witnesses present | pass |
| `::test_usage_error_without_a_population` | no argument → exit 2 | pass |
| `::test_doc_twins_match_the_shipped_rules` | byte identity | pass |
| `tests/test_rf7_structure.py` | allowlist | pass |

## 9. Out of scope

Page prose (PL5), derived fact types of `complete.orm.yaml` (the hand-written
rules cover the baseline and strict models; `strict` differs only in modality).

## 10. Size

~240 source lines, ~90 test lines.

## 11. Approval instrument

This prose plus the §8 corpus cases (expected exits authored first).

## Owner gate

Delegated approval (auto=true), 2026-10-14, under the owner's default plan
approval. No spec panel.
