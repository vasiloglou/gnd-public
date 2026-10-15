# Phase PL3 spec: the deterministic agent loop

## 1. Status

owner-decided (2026-10-14): delegated approval under
[`001-plan-gate.md`](../001-plan-gate.md). Implementable; PL1 landed.

## 2. Provenance

Plan r1 §2 (agent loop), §4 PL3 row, §9 PL3 row, PL-R2, PL-R5, PL-R8.
Pattern: `src/gnd/examples/approvals/stand_in_agent.py` and
`docs/agents/dev-session.md`. Measured before writing (scratch sessions on
2026-10-14): a schema-6 contract with `constraint-satisfaction` acceptance and
`verify.command: check` runs the stand-in from the `candidate/` directory, so
`../input/seed.population.json` is the seed; attempt feedback is
`attempts/NNNN/feedback.json` with `required[0].acceptance.violations[*].offending_facts`
and `payload_exit [[case, 1]]` (there is no `band` key); candidates are
retained at `attempts/NNNN/candidate/<subject>`; `agent.stdout` is retained.

## 3. Obligations

| Source | Obligation | Discharge |
|---|---|---|
| Owner review: "what the LLM outputs, how this is checked, what it feeds back" | a runnable loop with a refused first attempt and a repaired second | §6, §8 row 1 |
| Completion predicate 4 | `gnd exp run` exits 0 after two attempts; attempt-1 feedback equals the pinned witness; accepted candidate passes the PyRel app | §8 rows 1, 3 |
| PL-R2 | no model call | stand-ins are deterministic scripts |
| PL-R5 | pinned witnesses | §8 row 1 |
| PL-R8 | RF7 allowlist; wheel inventory | §6.3 |
| Standing rule 1 | stand-ins read only the seed they are handed; feedback parsed defensively (`.get`) | §6.1–6.2 |

## 4. Standing rules, bound

1. Totality: the stand-ins are tutorial scripts, not gates; they tolerate a
   missing or empty feedback. 2. Bounds: inputs are the shipped seeds. 3.
   Validation order: n/a. 4. One walk: one `offending_pairs`/`named_expenses`
   reader each. 5. One home: the loop is described on the chapter page; the
   agents page links to it. 6. Measurement: the scratch sessions above.

## 5. Goal

`gnd exp run EXP-003-recommend-ada --adapter-policy agent.policy.json` exits 0
with `attempt_count 2`; attempt 1 is `retry` with
`offending_facts == [{"$b": "night", "$u": "ada"}]`; the attempt-2 candidate
is `ada/map, ben/night, ada/cosmos` and `check_proposal` accepts it with one
warning. Expense: `offending_facts == [{"$a": 800, "$e": 102}]`, repaired
chain `finance`, `report` on the candidate prints `2 approved`.

## 6. Design

### 6.1 `src/gnd/examples/bookrec/stand_in_agent.py` (~60 lines)

`offending_pairs(feedback) -> set[tuple]`, `main() -> int`. Rows = seed
recommendations plus `ada/night` (what the user asked). If the feedback names
pairs, drop them and add `ada/cosmos`. Writes `recommendation.population.json`
with every other field of the seed verbatim, so `check_proposal` sees only
`recommendation` changed.

### 6.2 `src/gnd/examples/expense/stand_in_agent.py` (~50 lines)

`named_expenses(feedback) -> set[int]`, `main()`. Appends
`expense_is_approved {102}` and `expense_approved_by_chain {102, chain}` with
`chain = 'finance' if 102 in named else 'team-lead'`. Writes
`approvals.population.json`.

### 6.3 Contract, policy, pins

Written by page blocks at PL5 exactly as in §2 of this spec (schema 6, one
required case, coverage floor 2 on `recommendation` /
`expense_approved_by_chain`, `verify.command check`, subject as above). RF7
allowlist gains both scripts. Wheel inventory picks them up by rglob.

## 7. Decisions

| # | Question | Readings | Ruling |
|---|---|---|---|
| D1 | Seed location for the stand-in | (a) copy from its own folder; (b) read `../input/seed.population.json` | (b): the repair is visible as a change to the handed facts |
| D2 | Coverage floor | 1 or 2 | 2: proves the repair kept the other recommendation/approval |

## 8. Tests

| File | Case | Expected |
|---|---|---|
| `tests/test_pyrel_stand_in_sessions.py::test_stand_in_is_refused_then_accepted[bookrec,expense]` | exit 0, two attempts, pinned witness, accepted rows, feedback carries no repaired value | pass |
| `::test_stand_in_version_probe_and_missing_feedback` | `--version` exits 0 | pass |
| `::test_accepted_candidate_passes_the_pyrel_app` (`pyrel_oracle`) | attempt 2 accepted by the PyRel app; attempt 1 refused with the pinned witness | pass |
| `tests/test_rf7_structure.py` | allowlist | pass |

## 9. Out of scope

Real agent recordings (PL4); page prose (PL5).

## 10. Size

~110 source lines, ~110 test lines.

## 11. Approval instrument

This prose plus the §8 cases.

## Owner gate

Delegated approval (auto=true), 2026-10-14, under the owner's default plan
approval. No spec panel.
