# Phase RP4 — value constraints scoped to a role · spec

## 1. Status

owner-decided (2026-11-22) by **delegated approval (auto=true)**: see §7 and
§12. Base commit `33bd03db` (RP3 recorded).

## 2. Provenance

Derived from plan r4 (sha256 `9a93f4c2…9434`, approved in
`001-plan-gate.md`), §2 RP4, §4 RP4-C1…C3, §9 row RP4, §10 D3. Citations
read at `33bd03db`. Measurements in §6.3 were run on 2026-11-22 with
`gnd.api.check`. No review has run over this spec.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| RP4-C1 | a role-scoped value constraint renders in both branches (top level and fact-scoped), both targets | T1 |
| RP4-C2 | (oracle) a disallowed value in the role is denied (exit 1, GND's witness); the same value only in another role, or only in the roster, is not; an empty role is vacuous | T2 |
| RP4-C3 | `quantity_fixture/time.orm.yaml` renders under both targets | T3 |
| plan §2 RP4 | a fact-scoped value constraint without `role_ref` is lowered like the top-level form, as GND scopes it | T4 |
| plan §0 "Same verdict" | ranges as well as `allowed` lists | T5 |
| plan §0 "Ossie export unchanged" | Ossie digests of `rp4/top`, `rp4/fact` and the quantity fixture equal their `33bd03db` bytes | T6 |
| plan §5 | `docs/runtimes/pyrel.md` names role-scoped value constraints | T7 |
| plan §9 RP4 | cumulative lanes | §8 |

## 4. Standing rules, bound to this phase

1. **One walk.** The fact-scoped branch of `constraint_requirements` admits
   `value` and calls the same `_value`; no new loop.
2. **One home for allowed lists.** `_value` records each list on the model
   (`allowed_lists`, in lowering order); `_allowed` renders from it, so
   top-level and fact-scoped rules use one path. Existing models render the
   same lines in the same order.
3. **Totality.** A `role_ref` that is not a `{fact_type, role}` mapping, or
   names a role of another object type, is refused by name.

## 5. Goal

Value constraints with a `role_ref`, at the top level or on a fact type,
compile in both programs and agree with `gnd check`; the quantity fixture
exports.

## 6. Design

### 6.1 `src/gnd/export/pyrel_rules.py`

- `_value(model, c)`: with `role_ref`, the domain is one atom over the
  role's fact type, the value in that role; vacuity is that fact list being
  empty (`("any", (fact,))`); no roster is read. Without `role_ref`,
  unchanged (the object type's universe).
- `constraint_requirements`, fact-scoped branch: `value` lowers through
  `_value` with the `<fact>#<i>` id.
- `_allowed` renders `model.allowed_lists`.

### 6.2 Measured GND behaviour

`rp4/top` and `rp4/fact` (`grade` in `has_grade` allowed `A`, `B`):

| Population | exit | verdict |
|---|---|---|
| `deny` (`has_grade` holds `C`) | 1 | fail `["C"]` |
| `other-role` (`C` only in `wants_grade`) | 0 | pass |
| `roster` (`C` only in the `grade` roster) | 0 | pass |
| `empty-role` (`has_grade` empty) | 2 | vacuous |

`rp4/fact-plain` (fact-scoped, no `role_ref`): fail `["C"]` on all four,
the object type's universe, as the top-level form without `role_ref`.
`rp4/range` (1..5 on `has_grade.grade`): `range-deny` 1 `[9]` (the `0` in
`wants_grade` does not count), `range-pass` 0.

## 7. Decisions

| ID | Question | Ruling (delegated, 2026-11-22) |
|---|---|---|
| RP4-D1 | Where allowed lists live | on the model, in lowering order, one rendering path |
| RP4-D2 | A `role_ref` whose role is not played by `object_type` | refused by name (GND validation refuses it too; this is a guard) |

## 8. Tests

`tests/test_rp4_role_value.py`; fixtures in `tests/fixtures/pyrel-rules-coverage/rp4/`.

| # | Case | Lane | Expected |
|---|---|---|---|
| T1 | export `top`, `fact`, both targets | default | exit 0 |
| T2 | `top`, `fact` × `deny`, `other-role`, `roster`, `empty-role` | oracle | 1, 0, 0, 2, agreeing |
| T3 | export `quantity_fixture/time.orm.yaml`, both targets | default | exit 0 |
| T4 | `fact-plain` × the four populations | oracle | 1 each, agreeing |
| T5 | `range` × `range-deny`, `range-pass` | oracle | 1, 0, agreeing |
| T6 | Ossie digests | default | equal |
| T7 | runtime page | default | pass |
| T8 | malformed `role_ref` | default | `ExportInputError` |

Ledger: the cumulative focused and oracle lanes with `tests/test_rp4_role_value.py`
added (and the derivations file, as in RP3); guards; `uv run ruff check src tests tools`.

## 9. Out of scope

A live engine run; value constraints on derived roles beyond what the
existing derivation path reads.

## 10. Size

~30 source lines, ~120 test lines, 10 fixture files.

## 11. Approval instrument

Fixtures whose answer key is `gnd check`, oracle lane, literal exits.

## 12. Gate

Delegated approval (auto=true), 2026-11-22, under the owner's
`/process-milestone pyrel-rules-coverage auto` (2026-11-21), scope phase RP4.
Decisions RP4-D1, D2 as in §7. Budget: no paid call; review by Codex
through the review helper (plan gate D7). Sweep: every §3 row maps to a
test; every expected value was measured (§6.2).
