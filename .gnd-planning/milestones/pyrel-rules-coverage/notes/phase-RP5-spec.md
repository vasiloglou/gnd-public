# Phase RP5 — the packaged literature models end to end · spec

## 1. Status

owner-decided (2026-11-22) by **delegated approval (auto=true)**: see §7 and
§12. Base commit `78b9cbb8` (RP4 recorded).

## 2. Provenance

Derived from plan r4 (sha256 `9a93f4c2…9434`, approved in
`001-plan-gate.md`), §2 RP5, §4 RP5-C1…C3, §1's acceptance and population
tables, §9 row RP5. Read at `78b9cbb8`. RP5 is an acceptance phase: RP1–RP4
delivered the constructs; RP5 adds no lowering. No review has run over this
spec.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| RP5-C1 | the eleven packaged models of plan §1 export under both targets, exit 0 (plus `depth_fixture/decimal`, RP3's) | T1 |
| RP5-C2 | (oracle) the DuckDB program agrees with GND on every population of §1's table: the flat model's twelve gold populations (4), `assertions/raw` (0), the 41 `resolution/cases/*/*/population.json` (measured by the test), `quantity_fixture/time` (4), `depth_fixture/decimal` (0) | T2 |
| RP5-C3 | `docs/runtimes/pyrel.md` lists what the programs check, list as not checked, and refuse; a default-lane test asserts every not-checked reason and refusal message this milestone added is on the page; the reviewer reads the rest against the code | T3, §6 |
| plan §9 RP5 | cumulative lanes | §8 |

## 4. Standing rules

1. **No new lowering.** RP5 changes the runtime page and adds a test file;
   a failure it finds in a construct is a finding against that construct's
   phase, repaired there with its own regression.
2. **Measurement.** The resolution cases' exits are measured by the test
   itself (plan §1 measured the first); every other exit is literal.

## 5. Goal

Every packaged literature model in plan §1 exports, the DuckDB program
agrees with `gnd check` on every listed population, and the runtime page
states every message.

## 6. Design

`docs/runtimes/pyrel.md` gains a section, "What the programs print when they
do not check a rule", listing the not-checked reasons and the refusal
messages (input and model) verbatim, with placeholders for names.
`tests/test_rp5_literature_rules.py` holds T1–T3.

## 7. Decisions

| ID | Question | Ruling (delegated, 2026-11-22) |
|---|---|---|
| RP5-D1 | Which messages T3 lists | the ones this milestone's phases added or changed; older refusals keep their place in the page's prose |
| RP5-D2 | Whether T3 also scans the source for each message | no: the phase tests assert each message against what the programs print, and a source scan of wrapped string literals is brittle |

## 8. Tests

| # | Case | Lane | Expected |
|---|---|---|---|
| T1 | 12 models × 2 targets | default | exit 0 |
| T2 | 56 populations | oracle | agree; literal exits where the table has them |
| T3 | the page states each message | default | pass |

Ledger: the cumulative focused lane with `tests/test_rp5_literature_rules.py`
added; the cumulative oracle lane likewise (plans included, as RP4); guards;
`uv run ruff check src tests tools`.

## 9. Out of scope

`reading_fixture/reading.orm.json` (plan §1: its includes are not shipped);
a live engine run.

## 10. Size

~0 source lines, ~90 test lines, ~35 doc lines.

## 11. Approval instrument

The packaged populations, with `gnd check` as the answer key.

## 12. Gate

Delegated approval (auto=true), 2026-11-22, under the owner's
`/process-milestone pyrel-rules-coverage auto` (2026-11-21), scope phase RP5.
Decisions RP5-D1, D2 as in §7. Budget: no paid call; review by Codex through
the review helper. Sweep: every §3 row maps to a test. Disclosure: the test
file was drafted before this gate was written; no product code changes in
this phase.
