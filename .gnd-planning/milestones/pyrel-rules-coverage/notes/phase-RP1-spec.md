# Phase RP1 — external uniqueness in the rules programs · spec (draft)

## 1. Status

Draft, 2026-11-21, written by `start-milestone`. Awaiting the plan gate,
then this spec's own delegated gate. No implementation file exists.

## 2. Provenance

Derived from plan r2 (`notes/pyrel-rules-coverage-plan.md`), §2 RP1, §4
RP1-C1…C6, §9 row RP1 and §10 D4. No review has run over this spec. Every
citation was read at `8c909013`. The measurements in §6 were run on
2026-11-21 against scratch copies of the packaged populations.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| plan §4 RP1-C1 | `assertions/` and `lineage/` render under both targets, exit 0 | T1 |
| plan §4 RP1-C2 | both programs state the (work, passage) requirement from one `Requirement` | T2 |
| plan §4 RP1-C3 | oracle agreement: packaged population (0), duplicate pair (1), empty join (2) | T5, T6, T7 |
| plan §4 RP1-C4 | a non-string `assertion` value refused, exit 3, by name | T8 |
| plan §4 RP1-C5 | `refuse-external-uniqueness.orm.json` renders; external frequency still refused | T3 |
| plan §4 RP1-C6 | a disconnected external join refused by name | T4 |
| plan §2 RP1 | anchors matched by object type, not role name | T9 |
| plan §10 D4 | `String` for an `external` entity, decided from the model | §6.2, T8 |
| plan §0 "Same verdict as GND" | vacuity is the join's emptiness | T7 |
| plan §0 "Families stay registered" | no new family; lowering under `constraint_requirements` | §6.1, T10 |
| plan §5 | `docs/runtimes/pyrel.md:156-161` stops listing external uniqueness as refused and states D4's difference | §6.4, T11 |
| plan §6 | wrong-join risk | T6, T9 |
| plan §9 RP1 | focused lane and oracle lane, exit 0 | §8 ledger |
| plan §1 open question | the join listing's part name and witness shape | §6.1 |

## 4. Standing rules, bound to this phase

1. **Totality.** `_external_uniqueness` reads model JSON that passed
   `gnd validate`, but is total anyway: a `role_refs` that is not a list of
   mappings, an unknown fact type or role, or an empty list raises
   `ExportInputError` naming the constraint, never a traceback. T12 feeds
   each to `requirements()`.
2. **Cap bounds the algorithm.** The lowering is linear in `len(role_refs)`
   plus the referenced fact types' roles. T13 renders a 200-fact-type chain
   join under a 5-second bound.
3. **Validation order.** Model-wide refusals (`_refuse_unsupported_model`)
   run first, then constraints in model order: fact-scoped, then top-level.
   Within one external uniqueness: shape (T12), then connectivity (T4), then
   lowering. Pinned by T4's source-order assertion that the connectivity
   check precedes the atom construction.
4. **One walk.** The external branch is reached only through
   `constraint_requirements`, which `requirements()` already walks once over
   every family (`pyrel_rules.py:845-908`). T10 asserts no second loop over
   top-level constraints is added (a source scan of `render` and
   `requirements`).
5. **One home.** `docs/runtimes/pyrel.md` is the home of the refusal list;
   it yields in this phase (T11). The plan's §1 measurement table is history.
6. **Measurement.** The witness shape and the vacuous verdict were measured
   with `gnd check` before this spec (§6.3), not argued.

## 5. Goal

`gnd export pyrel MODEL --rules duckdb|lqp` exits 0 for
`assertions/model.orm.yaml` and `lineage/model.orm.yaml`. On the
populations of §8, the DuckDB program's exit code and finding set equal
`gnd check`'s: 0, 1 and 2 as measured, and 3 for a non-string `assertion`
value (GND exits 0 there; D4's stated difference).

## 6. Design

### 6.1 `src/gnd/export/pyrel_rules.py` (~70 lines)

```python
def _external_uniqueness(model: _Model, c: dict[str, Any]) -> list[Requirement]:
    """GND's shared-entity join (checker/_core.py:1099-1150), twice; equal referenced values need equal anchors."""
```

- Called from `constraint_requirements` in the top-level branch, in place of
  the `:882` refusal for `uniqueness`; `frequency` keeps the refusal.
- Join shape. Group `role_refs` by fact type in first-seen order, as
  `_join_rows` does. For each fact type, each referenced role binds
  `$<role>` (numbered by `_sequence_names` on repeats). Each non-referenced
  role binds `$<object type>_1` in copy one and `$<object type>_2` in copy
  two, so two roles of the same object type in different fact types share a
  variable, which is GND's merge by object type.
- Connectivity. Refuse with `ExportInputError(f"{cid}: the external
  uniqueness join is disconnected; GND refuses it")` when the referenced fact
  types do not form one component under shared anchor object types (the
  rule of `_require_joinable`, `_core.py:1156`).
- Requirement `"uniqueness"`, part `""`: domain = copy one's atoms plus copy
  two's atoms; check `same` over the anchor pairs; witness = the referenced
  variables in `role_refs` order; `vacuous_when = ("any", ())` with the
  listing below deciding; `info` carries `("external", True)` and
  `("refs", [[fact_type, role], ...])`.
- Listing part `"join"`: one `Requirement` with `listing=True`, domain =
  copy one's atoms, selecting the referenced variables. It compiles to no
  `require` (`_require_count` returns 0 for a listing, `:1399-1403`).
- `uniqueness` with `info['external']` joins `GROUPED` in the DuckDB
  program; `judge` returns `vacuous` when the `join` rows are empty, else
  `fail` with the distinct offending referenced tuples, else `pass`.
  `witnesses` is not used for it.

### 6.2 Typing the external entity (D4)

`raw_primitive(object_id)` returns `"String"` when the object type is an
entity with `reference.mode == "external"` and no `value_type`. Nothing else
changes there. `check_cell` already refuses a non-string in a `String` role;
the message for this case names the entity and says
`GND accepts any scalar for an externally identified entity; the rules
programs need strings`. Exact text fixed in T8.

### 6.3 Measured GND behaviour (2026-11-21)

| Population | `gnd check` exit | verdict for `constraints[0]` |
|---|---|---|
| `assertions/raw.population.json` | 0 | pass |
| one second assertion given the first one's passage and work | 1 | fail, `offending_facts [["p01", "working-notes"]]` |
| every `assertion_names_work` row renamed to another assertion | 2 | vacuous, `offending_facts []` |

The witness is the list of offending referenced-value tuples in
`role_refs` order (passage, work), one per tuple. The program prints it as
one line, as GND reports one verdict per rule.

### 6.4 `docs/runtimes/pyrel.md`

Line 156: external uniqueness moves from the refused list to the checked
list; external frequency stays refused. One sentence states D4: values of
an externally identified entity must be strings in the programs, though GND
accepts any scalar.

## 7. Decisions

| ID | Question | Readings and cost | Ruling |
|---|---|---|---|
| RP1-D1 | Vacuity source | (a) the `join` listing, GND's rule; (b) `("any", fact types)`, which calls a non-empty pair of lists with an empty join "decided", exit 0 vs GND's 2 | open; proposed (a) |
| RP1-D2 | Witness shape | (a) referenced tuples in `role_refs` order, as measured; (b) GND-internal facts, as inline uniqueness prints | open; proposed (a) |
| RP1-D3 | Non-string external ids | (a) exit 3 by name (D4); (b) coerce to string, which merges `1` and `"1"`, which GND keeps distinct | open; proposed (a) |

## 8. Tests

New file `tests/test_rp1_external_uniqueness.py`; fixtures under
`tests/fixtures/pyrel-rules-coverage/rp1/`, committed red before the code.

| # | Case | Lane | Expected |
|---|---|---|---|
| T1 | render `assertions/` and `lineage/`, both targets | default | no exception |
| T2 | both programs carry `require_text` of the one `Requirement`; `#   rule:` count equals requirements | default | pass |
| T3 | `refuse-external-uniqueness.orm.json` renders; `refuse-external-frequency.orm.json` still refuses `external frequency` | default | pass; the `:98` parametrize row moves |
| T4 | `rp1/disconnected.orm.json` refuses `disconnected`; source order: connectivity before atoms | default | `ExportInputError` |
| T5 | DuckDB program on `assertions/raw.population.json` agrees with GND | oracle | exit 0 both |
| T6 | `rp1/duplicate.population.json` | oracle | exit 1 both; `[["p01", "working-notes"]]` |
| T7 | `rp1/empty-join.population.json` | oracle | exit 2 both; vacuous |
| T8 | `rp1/integer-id.population.json` | oracle | program exit 3 with the D4 message; GND exit 0 (asserted, the difference is pinned) |
| T9 | `rp1/renamed-anchor.orm.json` (anchor roles of one object type with different role names) with a duplicate | oracle | exit 1 both |
| T10 | source scan: no new loop over `doc['constraints']` | default | pass |
| T11 | runtime page no longer lists external uniqueness as refused, still lists external frequency | default | pass |
| T12 | malformed `role_refs` shapes | default | `ExportInputError`, no traceback |
| T13 | 200-fact-type chain render under 5 s | default | pass |

Verification ledger:

- Focused: `uv run pytest -q tests/test_rp1_external_uniqueness.py tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py tests/test_pyrel_export.py tests/test_pyrel_export_boundaries.py --tb=short`, exit 0.
- Oracle (opted in): `uv run pytest -q -m pyrel_oracle tests/test_rp1_external_uniqueness.py tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py`, exit 0; baseline 110 passed.
- Guards: the `project.md` guard block; `uv run ruff check`.
- Broad lanes: not selected.

## 9. Out of scope for this phase

External frequency; anchored (RP2); `Number` (RP3); role-scoped value
(RP4); a live engine run; typing an external entity from its identifying
tuple.

## 10. Size

Estimate: ~70 source lines, ~220 test lines, 5 fixture files.

## 11. Approval instrument

Prose plus a fixture corpus whose answer key is `gnd check` itself, run in
the oracle lane: the populations are committed first and T5–T9 are red
until the lowering exists. Expected exits are written literally in the
tests as well as compared with GND, so a change in GND cannot silently move
them.
