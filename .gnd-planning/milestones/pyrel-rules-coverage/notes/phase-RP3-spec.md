# Phase RP3 — `Number` typed like `Float` · spec

## 1. Status

owner-decided (2026-11-22) by **delegated approval (auto=true)**: see §7 and
§12. Base commit `1350db9a` (RP1 recorded).

## 2. Provenance

Derived from plan r4 (sha256 `9a93f4c2…9434`, approved in
`001-plan-gate.md`), §2 RP3, §4 RP3-C1…C5, §9 row RP3, §10 D2 and D6. No
review has run over this spec. Citations read at `1350db9a`. Measurements in §6.3 were
run on 2026-11-22 with `gnd.api.check` and `gnd check`.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| RP3-C1 | #214's six-line model and `depth_fixture/decimal.orm.json` render under both targets | T1 |
| RP3-C2 | (oracle) agreement on `depth_fixture/decimal.population.json`; a boolean in a `Number` role refused, exit 3, as `gnd check` does | T2, T3 |
| RP3-C3 | arithmetic on a `Number` value in a derivation refused by name, as on `Float` | T4 |
| RP3-C4 | (oracle) 9007199254740993 in a `Number` role and in a `Float` role refused, exit 3, by name; `gnd check` decides it (both pinned) | T5 |
| RP3-C5 | a model whose `allowed` list holds 9007199254740993 for a `Number` object type refused at export, exit 3, by name | T6 |
| plan §2 RP3 | range bounds and comparison literals in a `Number`/`Float` context take the same bound | T7, T8 |
| plan §0 "Same verdict on accepted inputs" | the six-line model agrees with GND on pass and duplicate populations | T2 |
| plan §0 "Ossie export unchanged" | Ossie bytes of both `Number` models equal their `6e04fe7f` digests | T9 |
| plan §0 "Say what each test proves" | 2**53 itself is admitted (the bound is exclusive) | T5 |
| plan §5 | `docs/runtimes/pyrel.md` states `Number` as `Float` and D6's bound | T10 |
| RP1 review r2-F1 (deferred here) | two Float anchors 9007199254740992 and 9007199254740993 must not merge into a pass: `rp1/numeric-anchor.orm.json` with `rp3/anchor-beyond.population.json` is refused, exit 3, where GND exits 1 | T11 |
| plan §9 RP3 | cumulative focused and oracle lanes | §8 ledger |

## 4. Standing rules, bound to this phase

1. **One home for the bound.** `_EXACT_FLOAT = 2**53` is defined once in
   `pyrel_rules.py`; the program's `check_cell` reads the same constant
   (rendered from it), and `_literal` and the comparison guard read it.
2. **Validation order.** Model refusals at export (constants) before any
   population is read; cell refusals in `read_population`, before PyRel.
3. **Totality.** Only Python `int` (not `bool`) values are bounded; floats are
   already binary in both GND's input and the program.
4. **One walk.** No new walk; the changes are type-table entries and the
   two guards.

## 5. Goal

`Number` exports as PyRel `Float` in both programs, with GND's admission
rule (a finite integer or float, not a boolean). Integers beyond 2**53 in a
`Number` or `Float` role, or as a model constant in such a context, are
refused by name with exit 3.

## 6. Design

### 6.1 `src/gnd/export/pyrel_rules.py`

- `_TYPES["Number"] = "Float"`. `raw_primitive` keeps the model's name
  `Number`, so messages name it.
- Every place that recognises `Float` by its raw name treats `Number` the same:
  `_refuse_inexact` (arithmetic and mixed comparisons in derivations). The
  guarded paths that admit only `Integer`, `String`, `Boolean` (`_typed_term`
  arithmetic, `_guarded_filter`, `_membership_check`) already refuse
  `Float` and so refuse `Number` with the same message naming the type.
- `_EXACT_FLOAT = 2**53`. `_literal(value, "Float")` refuses a Python `int`
  with `abs(value) > _EXACT_FLOAT`: `the integer N is beyond 2**53, which a
  Float or Number value here (a binary float) cannot hold exactly; GND keeps
  it exact`. This covers `allowed`, range bounds and literal arguments of
  atoms, all rendered through `_literal`.
- `_guarded` comparison: a literal integer beyond the bound facing a
  `Float`/`Number` variable is refused with the same message. Derivation
  `where` comparisons get the same check in `_refuse_inexact`.
- Program `check_cell`: `'Number'` admits what `'Float'` admits; for both, an
  `int` beyond `EXACT_FLOAT` raises `<fact>.<role> is N, an integer beyond
  2**53, which a <type> here (a binary float) cannot hold exactly; GND keeps
  it exact`.

### 6.2 Typing

PyRel has no exact decimal that GND's `Number` would map to without being
stricter than GND (plan D2): GND checks no precision or scale.

### 6.3 Measured GND behaviour (2026-11-22)

Six-line model (`run_has_score`, uniqueness on `run`, `score: Number`):

| Population | `gnd check` exit | verdict |
|---|---|---|
| `a: 1`, `b: 0.5` | 0 | pass |
| `a: 1`, `a: 0.5` | 1 | fail, both facts |
| `a: true` | 3 | `population:type-mismatch` |
| `a: 9007199254740993`, `b: 9007199254740992` | 0 | pass |
| `a: 9007199254740993`, `a: 9007199254740992` | 1 | fail (GND keeps them distinct) |
| the same with `score: Float` | 1 | fail |
| `allowed: [9007199254740993, 1]`, `a: 9007199254740992` | 1 | fail |
| `range: {min: 0, max: 9007199254740993}`, `a: 1` | 0 | pass |

`depth_fixture/decimal.population.json` (one fact, `0.002`): exit 0.

## 7. Decisions

| ID | Question | Ruling (delegated, 2026-11-22) |
|---|---|---|
| RP3-D1 | Where the bound applies | every Python `int` in a `Number`/`Float` cell or constant context; floats are not bounded (they are binary on both sides) |
| RP3-D2 | Inclusive or exclusive | exclusive: `abs(value) > 2**53` refused; 2**53 and its neighbours below are exact |
| RP3-D3 | Message type name | the model's own (`Number` or `Float`) |

## 8. Tests

`tests/test_rp3_number.py`; fixtures in `tests/fixtures/pyrel-rules-coverage/rp3/`.

| # | Case | Lane | Expected |
|---|---|---|---|
| T1 | export six-line and `decimal`, both targets | default | exit 0 |
| T2 | six-line pass (0) and duplicate (1); `decimal` population (0) | oracle | agree, literal |
| T3 | boolean in `score` | oracle | program 3, GND 3 |
| T4 | derivation with `add` over a `Number` role | default | `ExportInputError` naming Float or Number |
| T5 | 9007199254740993 in `Number` and in `Float` roles: program 3 by name, GND 1 (pinned); 2**53 admitted and agreeing | oracle | as stated |
| T6 | `allowed` with 9007199254740993 on `Number` | default | export exit 3, message |
| T7 | `range` max 9007199254740993 on `Number` | default | export exit 3 |
| T8 | guarded comparison `score > 9007199254740993` | default | `ExportInputError` |
| T9 | Ossie digests of six-line and `decimal` unchanged | default | equal |
| T10 | runtime page names `Number` and 2**53 | default | pass |
| T11 | RP1's deferred regression: `rp1/numeric-anchor` with `rp3/anchor-beyond` | oracle | program 3 by name; GND 1 (pinned) |

Verification ledger:

- Focused: `uv run pytest -q tests/test_rp3_number.py tests/test_rp1_external_uniqueness.py tests/test_rp2_anchored.py tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py tests/test_pyrel_rules_derivations.py tests/test_rules_in_pyrel.py tests/test_pyrel_export.py tests/test_pyrel_export_boundaries.py tests/test_ossie_formulas.py tests/test_ossie_export.py --tb=short`, exit 0.
- Oracle (opted in): `uv run pytest -q -m pyrel_oracle tests/test_rp3_number.py tests/test_rp1_external_uniqueness.py tests/test_rp2_anchored.py tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py`, exit 0.
- Guards: the `project.md` guard block; `uv run ruff check src tests tools`.

## 9. Out of scope

An exact decimal type; precision or scale; arithmetic on `Float`/`Number`.

## 10. Size

Estimate: ~25 source lines, ~150 test lines, 4 fixture files.

## 11. Approval instrument

Prose plus fixtures whose answer key is `gnd check`, run in the oracle lane,
expected exits written literally.

## 12. Gate

Delegated approval (auto=true), 2026-11-22, under the owner's
`/process-milestone pyrel-rules-coverage auto` (2026-11-21), scope phase RP3.
Decisions RP3-D1…D3 as ruled in §7. Budget: no paid call; phase review by
Codex through the review helper (plan gate D7). Sweep: every §3 row maps to
a test; every expected value in §8 was measured (§6.3). The spec's SHA-256
is recorded in the RP3 phase record.
