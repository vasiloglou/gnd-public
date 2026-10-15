# Phase PL14 review (one Claude subagent, same model family)

Retained verbatim as delivered in the session on 2026-10-14. The reviewer was
read-only on `src/`, `tests/` and `docs/` and could not write this file itself.
Reviewed bytes: `src/gnd/export/pyrel_rules.py` sha256
`65057861a9a103d9b621fc7d2f58b8a7cc36e46b0e319fb9b21c37369945028e`, HEAD da71d7b
plus uncommitted changes. Scratch reproductions: `scratchpad/pl14-review/` in
the session.

---

**Verdict: REVISE.** Two blocking defects, both reproduced with exact commands below. The common case agrees: 30 of 30 randomised clinic populations matched GND when every fact type had rows, and so did the date-family and reference scenarios listed at the end.

Reviewed `src/gnd/export/pyrel_rules.py` sha256 `65057861a9a103d9b621fc7d2f58b8a7cc36e46b0e319fb9b21c37369945028e`, checked at start and end, unchanged. I wrote nothing under src/, tests/ or docs/. `git status` now also shows ` M docs/runtimes/pyrel.md`, which I did not touch; something else running concurrently changed it.

Scratch directory: `S=/private/tmp/claude-501/-Users-nikolaosvasiloglou-github-repos-gnd-public/fd814110-b392-4c16-8294-2db75ff438c9/scratchpad/pl14-review`. The harness `$S/h.py` + `$S/common.py` renders with `render()`, runs `tutorials/runtimes/.venv/bin/python -I`, and compares against `api.check(unredacted=True)` using the tests' own `_assert_agrees`. Every case is in `$S/cases/<name>/` (`model.orm.json`, `pop.json`, `rules.py`).

## Findings

**F1 — BLOCKING: crash (exit 70) on a vacuous rule when the relation feeding `date_add`/`date_sub`'s date argument is empty**
- Where: emitted denial/listing queries (`_rule_block`, ~l.1165; operand from `_operand` l.887-889).
- Cause: an empty Date relation (base or computed) reaches DuckDB with a NULL column type, so `NULL + INTERVAL` fails to bind. The query runs even though the report would call the rule vacuous.
- Scope: hit 14 of 30 random populations (`$S/fuzz.py`).
- Repro:
  ```
  python3 -c "import json;p=json.load(open('tests/fixtures/pyrel-rules-calendar/clinic-on-time-leap-day.population.json'));p['facts']['last_refill']=[];p['facts']['recent_request']=[];json.dump(p,open('$S/min/no-last-refill.population.json','w'))"
  uv run gnd export pyrel tests/fixtures/pyrel-rules-calendar/clinic.orm.json --rules duckdb --out $S/min/clinic_rules.py
  tutorials/runtimes/.venv/bin/python -I $S/min/clinic_rules.py $S/min/no-last-refill.population.json
  ```
  - Program: exit 70, `Binder Error: Could not choose a best candidate function for the function call "+("NULL", INTERVAL)"` at the `refill_not_early` line (`req < std_date.add(last, days(n))`).
  - GND: exit 2; `refill_not_early` vacuous, all else pass.
- Same crash in cases N2 (empty `prescribed_until`, `date_sub`; GND exit 2) and N3 (a derived Date relation whose computed extension is empty; GND exit 2, `late_bound` vacuous).
- Not affected: an empty Duration side (N1 agrees) and a non-empty but empty join (N4 agrees).
- Why tests miss it: `clinic-no-requests` only empties the non-date side.
- Fix: skip a temporal rule's queries when any antecedent relation, including computed ones, is empty (GND calls it vacuous anyway), or make the empty relation's column type a real Date. Add a corpus row for each of these three shapes.

**F2 — BLOCKING: loose Date literal parsing gives wrong verdicts and crashes**
- Where: `_literal` l.857-866 (`value.split("-")` → `int`, with no `valid_date` check); `_typed_term` l.267 (turns any untagged string facing a Date into a date).
- GND accepts these models and compares by token or strict ISO:

| Case | Model change | GND | Program |
|---|---|---|---|
| J3 | Date value constraint `allowed` contains `'2024-7-07'` | exit 1, `plausible_birth` fail `["2024-07-07"]` | exit 0, OK — silent wrong verdict |
| H2 | guarded antecedent atom literal `day: '2024-3-01'` | pass, exit 0 | warning with a witness |
| D7 | derivation body literal `day: '2000-2-29'` | `derivation:leapers` pass, exit 0 | exit 1, `missing {"patient":"ben"}` |
| G3 | guarded `$req >= '2020-1-01'` | unchecked `values-not-comparable` | OK |
| G | guarded `$req >= '2024-02-30'` | unchecked `values-not-comparable`, exit 0 | exit 70 at run time: `ValueError: day is out of range for month` |
| G2 | guarded `$req >= 'soon'` | unchecked, exit 0 | export exit 70: `uv run gnd export pyrel $S/cases/G2_nondate_string/model.orm.json --rules duckdb --out $S/cases/G2_nondate_string/cli.py` prints `Export failed: invalid literal for int() with base 10: 'soon'` |
| J4 | `allowed` contains `'tomorrow'` | exit 0 | export raises raw `ValueError` |

- Fix:
  - Convert a string to a Date only when `gnd.terms.valid_date` holds.
  - Otherwise, in atoms and allowed lists, render a literal that never matches (GND's token identity).
  - In guarded comparisons, reproduce `values-not-comparable` as "not checked" (vacuity still first), or refuse by name with `ExportInputError`.

**F3 — BLOCKING (low-cost fix): instance rosters of Date/Duration are never validated**
- Where: l.953 (`datetime.date.fromisoformat(value)`); `read_population` never checks `instances`.
- Python 3.11+ `fromisoformat` accepts basic format such as `'20240229'`. §6.1 promises strict checks on every cell.
- Repro `$S/t8.py`:

| Roster value | GND | Program |
|---|---|---|
| `'20240229'` (K0) | exit 3 `population:type-mismatch` | exit 0 — silent accept |
| days `-1` (K2) | exit 3 | exit 1, `interval_cap violated -1` |
| days `2000000` (K3) | exit 3 | exit 1, `interval_cap violated 2000000` |
| `'2024-1-01'` (K1) | exit 3 | exit 70 |

- The Integer roster gap predates PL14, but there it crashes (K6, exit 70) rather than giving a verdict.
- Fix: run `check_cell` (or the same primitive checks) over `document['instances']` for every roster key.

**F4 — HARDENING: some reference refusals exit 70, not 3**
- Where: `render` l.1575 catches only `ModelLoadError` and `ModelValidationError`. `load_model_bytes` calls `validate_declarations`, which raises `ReferenceInputError`.
- Repro (a reference owning a derived fact type):
  ```
  uv run gnd export pyrel $S/cases/R7_ref_owns_derived/model.orm.json --rules duckdb --out $S/cases/R7_ref_owns_derived/cli.py
  ```
  prints `export failed: references may own only base fact types`, exit 70. `gnd check` exits 3.
- Same path for:
  - bad sha256 format;
  - duplicate or unknown ownership;
  - more than 32 files;
  - operations writing an owned fact type.
- Spec §6.3 says exit 3.
- Fix: also catch `ReferenceInputError` there.

**F5 — HARDENING: Integer arithmetic in guarded comparisons crashes beyond DECIMAL(38)**
- GND computes exactly up to 65,536 bits.
- Repro `$S/t3.py`:
  - O6, `mul(mul($q,$q),$q)` with q=2^50: GND pass/exit 0, program exit 70 `Overflow in multiplication of DECIMAL(38)`.
  - O8, q = c = 2^64+1: same.
- It is a crash, not a wrong verdict. Derivation arithmetic already had this before PL14; guarded comparisons get it new.
- Fix: refuse by name (or treat as not checked) when operands can exceed the decimal range, or document the bound.

**F6 — COMPLETENESS: spec and code differ on order and on derivation literals**
- Order: §4.3 says load, then reference binding, then lowering. Code runs `requirements()` (l.1580) before `_bind_reference` (l.1581). Exit code is the same (3), but the refusal message can differ.
- Derivation `where`: §5 and §4.5 say an untagged ISO literal facing a Date in a derivation `where` is a date. GND actually refuses it at validation (C_deriv_where_iso: "incompatible types 'Date' and 'String'", exit 3). The program refuses it the same way, but the spec text is wrong, and `_expr` does not use the "one home" `_literal`.

**F7 — COMPLETENESS: LQP header does not mention date rules**
- The LQP version will report a requirement violation where GND says unchecked (`term:date-out-of-range` / `term:temporal-work-limit`) or warning (deontic).
- The header covers "vacuous rules and exit bands" but not this case.
- `--compile` counts were correct on every model I built: J, M, F1, O4, R1, T7, V3, E7.

**F8 — COMPLETENESS: test gaps (mutation survivors likely)**
- No corpus row has a deontic temporal rule left unchecked (GND exit 0) or an alethic `date-out-of-range` as the only problem (GND exit 4). Every out-of-range row exits 1 because of another failure, so the mutant `unchecked = True` in `report` survives. My E7 cases agree with GND on both.
- No test covers: the F1 empty-relation crash; invalid or unpadded literals (F2); roster validation (F3); declaration-level reference refusals through the CLI (F4).
- No test re-derives `expected.json` from GND. I checked it myself (`$S/t12.py`): 0 stale rows.
- `test_a_tampered_reference...`: `.replace('"', '"', 1)` does nothing; only the appended `'\n'` tampers the file. It works but reads like a mistake.

## Scenarios that agree with GND (exit and lines)
- **Extreme dates in witnesses:** 0001-01-01, 9999-12-31, years 1500/2300; dates print as ISO.
- **Every constraint family over Date and Duration roles:**
  - ring acyclic/irreflexive/asymmetric/transitive/symmetric, including a cycle 0001↔9999;
  - uniqueness, internal frequency, mandatory, exclusion, equality, subset (same set; one line per witness);
  - cardinality object and role, mandatory-disjunctive;
  - Date range with exclusive max, Duration range, Date and Duration allowed lists;
  - Date instances.
- **Temporal rules:**
  - out of range alone or with failures, deontic and alethic exit bands (E2–E7);
  - `date_add`/`date_sub` on both sides, duration 0 and 1,000,000 at the 9999 edge (T4/T5);
  - work limit at and over 10,000, with two functions;
  - derived and semiderived relations feeding temporal rules (V1–V3);
  - Duration vs Duration, Duration vs tagged duration, untagged valid ISO on either side (G4);
  - a valid date literal in an antecedent atom (H) and in a derivation body (D4).
- **Arithmetic** within range, including 2^63±1 squared.
- **References:**
  - two files, one in a subfolder, with Date/Duration facts, instances and covers;
  - a reference row making a rule fail;
  - reference covers missing, giving mandatory vacuous;
  - a candidate covering an owned fact type without listing it;
  - duplicate reference rows (deduped);
  - candidate and reference instances overlapping;
  - symlinked file, symlinked directory, model symlink, and a bad reference cell all exit 3 like GND.
- **GND refuses at validation as well**, so nothing to match: untagged int durations, a literal date as `date_add` argument, min/max over dates, count into a Duration, tagged literals in derivation bodies, unpadded tagged dates, oversized duration literals, Date-vs-String `where`.
- **Shipped tests:** the calendar tests pass (`-m pyrel_oracle`: 28 passed; default lane: 6 passed).
