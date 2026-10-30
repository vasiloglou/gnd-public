# IH2: own-reference subtype joins

**Status:** r1. The gate is recorded in the IH2 phase record, under the
owner's milestone delegation (`process-milestone ilp-import-hardening auto`,
2026-10-30). The plan's IH-D1 is ruled (b) (o): refuse by a new name.

## Provenance

- Plan r2: the IH2 predicate, §0, §2 "Own-reference subtype joins (IH2)", §4
  "IH2", §5, §9 IH2 row, §10 IH-D1 (ruled (b), 2026-10-29 (o)).
- Plan review r1, reader 1, findings 5 and 11: the reproduction of the false
  `support-mismatch` and R1's name change under (b).
- IL's close: IL4-Q1 (own-reference remainder), and the IL-close review's
  finding 1, which R1 pins.
- IH0's triage, "Suspected, not reproduced": the own-reference exit-70 and
  `spell` suspicions are assigned to IH2.

## Obligations

| Obligation | Source | Discharged in |
|---|---|---|
| A fixture reproduces today's false `support-mismatch`, red at IH1's head | plan §4 IH2 | T1 |
| The import refuses an own-reference join by a new name before any count (IH-D1 (b)) | plan §4 IH2; IH-D1 (o) | Design 1; T1, T2 |
| The name enters `MAPPING_REFUSALS` after `type-confused-join`, with the docs table in the same commit | IH-R4; IH-D1 (o) | Design 2; T3 and IH1's T5 |
| R1 still refuses with exit 3, never 70; its asserted name moves to the new name, as IH-D1 (b) (o) records | plan §4 IH2 | T2 |
| No fixture golden moves; the AMIE `adapter_version` stays 2 | plan §4 IH2 under (b) | T4 |
| Release notes: one bullet | plan §5 | Design 2 |
| IH0's suspicions: an own-reference exit 70; `spell` writing `1` and `"1"` alike | IH0 triage | Design 3; T5 |

## Standing rules, bound to this phase

- **IK-R1 to IK-R12, IL-R1 to IL-R11:** bind unchanged. IL-R7: no wire,
  golden or adapter version moves under (b).
- **IH-R1:** no learner, solver or model runs.
- **IH-R2:** binds IH1 only. IH2 changes behaviour on purpose, by the
  ruling.
- **IH-R4:** the new name goes in the tuple and the docs table together.
- **RF6:** an IH2 dynamic-query successor, chained after IH1's.

## Goal

A mined rule that joins an own-reference subtype with its supertype is
refused `own-reference-join` before any count, so GND never reports a false
`support-mismatch` for it.

## Design

1. **The check,** in `ilp_amie.mapped`, after `check_join_types`:
   - a variable is checked if it occupies role positions spelled by more than
     one AMIE family (`Relation.families`), counting the head too;
   - such a variable is refused `rule K: own-reference-join`;
   - the message names the variable and the families.

   After `type-confused-join` passes, the types a variable joins are related
   by subtyping. Two related types fall in different families only when one
   of them has its own reference scheme (`family`, IL4-Q1). So this check
   catches exactly the joins the count cannot meet as the checker does.
2. **The name and the docs:**
   - `MAPPING_REFUSALS` gains `own-reference-join` as its last entry;
   - `docs/reference/ilp-bridge.md` gains the mapping-table row after
     `type-confused-join`, and changes the sentence on own-reference families;
   - `docs/release-notes.md` gains one bullet.
3. **IH0's suspicions.** A cross-family join is now refused before the
   count, so the count and the checker cannot disagree on it, and exit 70 is
   unreachable through such a join. `spell` writing `1` and `"1"` alike
   within one family is unchanged. Within one family the checker also
   compares raw values of one primitive, because a family is built only from
   reference-inheriting subtypes that share their supertype's reference type.
   T5 pins a mixed-primitive own-reference join (R1's model) as refused by
   name.

## Decisions

| ID | Question | Readings | Proposed |
|---|---|---|---|
| IH2-D1 | What counts as an own-reference join | **(a)** a variable spanning more than one family, as Design 1. **(b)** a variable whose role types include an own-reference subtype; this refuses joins wholly inside that subtype's own family, which count correctly today | (a) |

## Tests

New fixture `tests/fixtures/ilp_import_hardening/ih2/`: `ownref-string.orm.yaml`
and `ownref-string.population.yaml`. It is IL-close's own-reference fixture
with `manager_no` String and the manager values `"1"` and `"2"`. New file
`tests/test_ih2_ownref.py`.

| Test | Expected |
|---|---|
| T1 the String own-reference fixture with R1's rule is refused `rule 0: own-reference-join`, exit 3, no proposal | red at IH1's head (`support-mismatch`), then exit 0 |
| T2 R1 (`tests/test_il_close.py`, Integer against String) is refused `rule 0: own-reference-join`, exit 3 | the test's assertion changes per IH-D1 (b) (o); exit 0 |
| T3 `MAPPING_REFUSALS[-1] == "own-reference-join"`; IH1's T5 pins the docs order | red, then exit 0 |
| T4 a rule wholly inside one family (IL-close's `family`/`subtype` fixtures, C1) is admitted as before; `ADAPTER_VERSION == "2"`; `tools/ilp_comparison.py` exits 0 | exit 0 at both heads |
| T5 the mapping refuses before the count: with `ilp_amie.count` replaced by one that raises, T1 still gives `own-reference-join` | exit 0 |

**Gate:**
- IH1's gate list plus `tests/test_ih2_ownref.py` and `tests/test_ih1_counting.py`;
- the RF6 tests;
- ruff on the changed files;
- one full default suite run.

## Out of scope for this phase

- IH-D1 (a), counting the join (adapter version 3).
- Any learner, solver or model run.

## Size

About 15 changed lines of code, one fixture pair and the tests.

## Approval instrument

This prose plus the fixture: T1's case is the plan's reproduction.
