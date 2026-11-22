# Phase RP1 — external uniqueness in the rules programs · spec

## 1. Status

owner-decided (2026-11-22) by **delegated approval (auto=true)**: see §7 and
§12. Base commit `6e04fe7f` (RP2 recorded).

History: draft 2026-11-21 by `start-milestone`; `(p1)` amended for plan r3;
`(p2)` amended for plan r4 (join cases measured, T16–T17 added, ledger to
plan §9); `(p3)` 2026-11-22, finalized against RP2's bytes and further
measurement (§6.3): one fact type is a projection, so its anchors are its
roles; a disconnected join is vacuous only when every list is empty;
duplicate role references are refused; the witness order is the comparator's.

## 2. Provenance

Derived from plan r4 (sha256 `9a93f4c2…9434`, approved in
`001-plan-gate.md`), §2 RP1, §4 RP1-C1…C9, §9 row RP1 and §10 D4. No review
has run over this spec. Citations read at `6e04fe7f`; GND's normative join
is `semantic_spec.role_sequence_rows` (`:560-700`), its checker twin
`checker/_core.py` `_join_rows` (`:1099-1153`). Measurements in §6.3 were run
on 2026-11-21 and 2026-11-22 with `gnd.api.check` over the committed fixtures.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| plan §4 RP1-C1 | `assertions/` and `lineage/` render under both targets, exit 0 | T1 |
| plan §4 RP1-C2 | both programs state the (work, passage) requirement from one `Requirement` | T2 |
| plan §4 RP1-C3 | oracle agreement: packaged population (0), duplicate pair (1), empty join (2) | T5, T6, T7 |
| plan §4 RP1-C4 | a non-string `assertion` value refused, exit 3, by name | T8 |
| plan §4 RP1-C5 | `refuse-external-uniqueness.orm.json` renders; external frequency still refused | T3 |
| plan §4 RP1-C6 `(p2)` | a disconnected join: not checked with facts (exit 4), vacuous when every referenced list is empty (exit 2), agreeing with GND | T4 |
| plan §4 RP1-C7 `(p2)` | an ambiguous join refused at export, exit 3, as `gnd check` refuses the model | T14 |
| plan §4 RP1-C8 `(p2)` | numeric anchor agrees, or is refused by name | T15 |
| plan §4 RP1-C9 `(p2)` | a three-fact-type join | T16 |
| plan §3 `(p2)` | Ossie pin for external uniqueness and the `String` entity | T17 |
| plan §2 RP1 | anchors matched by object type, not role name | T9 |
| plan §10 D4 | `String` for an `external` entity, decided from the model | §6.2, T8 |
| plan §0 "Same verdict as GND" | vacuity is the join's emptiness | T7 |
| plan §0 "Families stay registered" | no new family; lowering under `constraint_requirements` | §6.1, T10 |
| plan §0 "Say what each test proves" | a negative control fails | T18 |
| plan §5 | `docs/runtimes/pyrel.md` stops listing external uniqueness as refused and states D4's difference | §6.4, T11 |
| plan §6 | wrong-join risk | T6, T9, T18 |
| plan §9 RP1 | focused lane and oracle lane, exit 0 | §8 ledger |
| plan §1 open question | the join listing's part name and witness shape | §6.1 |

## 4. Standing rules, bound to this phase

1. **Totality.** `_external_uniqueness` is total over `role_refs`: not a
   non-empty list of `{fact_type, role}` mappings, an unknown fact type or
   role, or one role named twice raises `ExportInputError` naming the
   constraint (T12).
2. **Cap bounds the algorithm.** Linear in `len(role_refs)` plus the
   referenced fact types' roles; the connectivity walk visits each anchor key
   once. T13 lowers a 200-fact-type chain under 5 seconds.
3. **Validation order.** Model validation first (an ambiguous join is an
   invalid model, exit 3, before lowering); then `_refuse_unsupported_model`;
   then constraints in model order. Within one external uniqueness: shape
   (T12), ambiguity guard, connectivity (T4), then lowering; T4 asserts the
   classification precedes the atom construction in the source.
4. **One walk.** Reached only through `constraint_requirements`; T10 asserts
   `requirements` and `render` keep one read of the model's rule list.
5. **One home.** `docs/runtimes/pyrel.md` is the home of the refusal list
   (T11).
6. **Measurement.** Every expected exit and witness was measured with GND
   (§6.3) and is written literally in the tests as well as compared.

## 5. Goal

`gnd export pyrel MODEL --rules duckdb|lqp` exits 0 for
`assertions/model.orm.yaml` and `lineage/model.orm.yaml`. On §8's
populations the DuckDB program's exit and findings equal `gnd check`'s, and
a non-string `assertion` value is refused (exit 3) where GND exits 0, D4's
stated difference.

## 6. Design

### 6.1 `src/gnd/export/pyrel_rules.py`

`_external_uniqueness(model, c) -> list[Requirement]`, called from the
top-level branch of `constraint_requirements` in place of the refusal for
`uniqueness`; `frequency` keeps its refusal, and a fact-scoped
`scope: external` keeps its own.

- Group `role_refs` by fact type in first-seen order, as GND does.
  Referenced roles bind `_sequence_names(role_refs)` (`$<role>`, numbered on
  repeats). `(p3)` Anchor keys: with two or more fact types, the object type
  of each non-referenced role (GND merges anchors by object type); with one
  fact type, the role name, because GND projects one fact type and its rows
  differ when any other role differs (`role_sequence_rows`, `:589-607`). Each
  key binds `$<key>_1` in copy one and `$<key>_2` in copy two, suffixed with
  `_` while it collides with a referenced name.
- Ambiguity `(p2)`: GND refuses the model at load (exit 3); the function also
  refuses it by name, as a guard for callers that skip validation.
- Connectivity: fact types linked by a shared anchor key; when not one
  component, append `{"id", "modality", "vacuous_if_empty": [fact types],
  "reason": "join-disconnected: F, G share no anchor object type"}` to
  `model.unchecked` and return no requirement. `(p3)` The DuckDB report
  prints it vacuous when every listed fact list is empty and not checked
  otherwise, as measured; the LQP program, which reads no population, always
  lists it as not checked.
- Listing part `"join"`: copy one's atoms, `Check("none")`, selecting the
  referenced variables; it compiles to no `require`.
- Part `""`: copy one's plus copy two's atoms, `Check("same")` over the
  anchor pairs, witness the referenced variables in `role_refs` order. With
  no anchor key at all (one fact type, every role referenced) this part is
  omitted: rows of a set are distinct, so only vacuity remains.
- Both parts carry `info` `("external", True)` and `("refs", …)` and
  `vacuous_when = ("any", fact types)` (an empty list empties the join).
- DuckDB report: a rule with `info['external']` is judged with the grouped
  families. `judge` returns `vacuous` when the `join` rows are empty, else
  `fail` with the distinct offending referenced tuples, else `pass`. `(p3)`
  Witness order is by JSON text, the order the shared comparator puts GND's
  witness in (as for inline uniqueness).

### 6.2 Typing the external entity (D4)

`_Model.external(object_id)`: an entity with `reference.mode == "external"`,
no primitive and no reference value type. `raw_primitive` returns `String`
for it. `(p3)` `_Model.cell_type` gives `External` for such an entity, else
the raw primitive; `ROLES` and `ROSTERS` carry it, and `check_cell` refuses a
non-string `External` cell with `<fact>.<role> is <value>: GND accepts any
scalar for an externally identified entity; the rules programs need strings`.

### 6.3 Measured GND behaviour

| Model / population | `gnd check` exit | verdict |
|---|---|---|
| assertions / `raw` | 0 | pass |
| assertions / `rp1/assertions-duplicate` | 1 | fail `[["p01", "working-notes"]]` |
| assertions / `rp1/assertions-empty-join` | 2 | vacuous |
| assertions / `rp1/assertions-integer-id` | 0 | pass (GND accepts the integer) |
| `rp1/disconnected` / facts | 4 | unchecked, `join-disconnected` |
| `rp1/disconnected` / partial (one list empty) `(p3)` | 4 | unchecked, `join-disconnected` |
| `rp1/disconnected` / empty | 2 | vacuous |
| `rp1/ambiguous` | 3 | invalid model at load |
| `rp1/renamed-anchor` / duplicate | 1 | fail `[["fr", "fr"]]` |
| `rp1/numeric-anchor` (anchors `1` and `1.0`) / duplicate | 1 | fail `[["fr", "paris"]]` |
| `rp1/three-way` / duplicate | 1 | fail `[["acme", "paris", "fr"]]` |
| `rp1/three-way` / pass | 0 | pass |
| three-way, one list not in covers `(p3)` | 1 | fail (covers not read) |
| three-way, one list empty `(p3)` | 2 | vacuous |

### 6.4 `docs/runtimes/pyrel.md`

External uniqueness leaves the refused list; a paragraph states the join,
the disconnected case and D4's difference. External frequency stays refused.

## 7. Decisions

| ID | Question | Ruling (delegated, 2026-11-22) |
|---|---|---|
| RP1-D1 | Vacuity source | (a) the `join` listing, GND's rule; `("any", fact types)` kept as a shortcut that agrees with it |
| RP1-D2 | Witness shape | (a) referenced tuples in `role_refs` order, one line, as measured |
| RP1-D3 | Non-string external ids | (a) exit 3 by name (D4); coercion would merge `1` and `"1"`, which GND keeps distinct |
| RP1-D4 `(p3)` | One role named twice in `role_refs` | refused by name; GND reads it as one reference, and the programs' variable naming has no meaning for it |

## 8. Tests

`tests/test_rp1_external_uniqueness.py`; fixtures in
`tests/fixtures/pyrel-rules-coverage/rp1/`.

| # | Case | Lane | Expected |
|---|---|---|---|
| T1 | export `assertions/` and `lineage/`, both targets | default | exit 0 |
| T2 | one checked `Requirement`; its statement once in each program; `#   rule:` count equals checked requirements | default | pass |
| T3 | the review fixture renders; external frequency still refuses; its `test_pyrel_rules_families` row removed | default | pass |
| T4 | disconnected: listed, not lowered, source order; oracle facts 4, partial 4, empty 2, agreeing with GND | default + oracle | pass |
| T5–T7 | assertions raw 0, duplicate 1, empty join 2 | oracle | agree, literal |
| T8 | integer id: program exit 3 with the D4 message; GND exit 0 | oracle | pass |
| T9 | renamed anchor roles, duplicate | oracle | exit 1 both |
| T10 | one walk (source scan) | default | pass |
| T11 | runtime page | default | pass |
| T12 | malformed `role_refs` (8 shapes) | default | `ExportInputError` by name |
| T13 | 200-fact-type chain under 5 s | default | pass |
| T14 | ambiguous: export exit 3 `invalid model`; `gnd check` exit 3; guard without validation | default | pass |
| T15 | numeric anchors `1`/`1.0`, duplicate | oracle | exit 1 both |
| T16 | three-way duplicate (1) and pass (0) | oracle | agree |
| T17 | Ossie export of assertions and three-way keeps its digests from `6e04fe7f` | default | equal |
| T18 `(p3)` | negative control: the program with the anchor check removed disagrees with GND on the raw population | oracle | disagree |
| T19 `(p3)` | the LQP program compiles (assertions, three-way) and `--compile` lists the disconnected rule | oracle | exit 0 |

Verification ledger:

- Focused: `uv run pytest -q tests/test_rp1_external_uniqueness.py tests/test_rp2_anchored.py tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py tests/test_pyrel_rules_derivations.py tests/test_rules_in_pyrel.py tests/test_pyrel_export.py tests/test_pyrel_export_boundaries.py tests/test_ossie_formulas.py tests/test_ossie_export.py --tb=short`, exit 0.
- Oracle (opted in): `uv run pytest -q -m pyrel_oracle tests/test_rp1_external_uniqueness.py tests/test_rp2_anchored.py tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py`, exit 0; RP2's count was 128.
- Guards: the `project.md` guard block; `uv run ruff check src tests tools` (whole-tree ruff is the known red of RP2's record).
- Broad lanes: not selected.

## 9. Out of scope for this phase

External frequency; `Number` (RP3); role-scoped value (RP4); a live engine
run; typing an external entity from its identifying tuple; the LQP program
deciding a disconnected join's vacuity.

## 10. Size

Estimate: ~90 source lines, ~260 test lines, 15 fixture files.

## 11. Approval instrument

Prose plus a fixture corpus whose answer key is `gnd check`, run in the
oracle lane, with expected exits written literally.

## 12. Gate

Delegated approval (auto=true), 2026-11-22, under the owner's
`/process-milestone pyrel-rules-coverage auto` (2026-11-21), scope phase RP1
of this milestone. Decisions RP1-D1…D4 as ruled in §7. Budget: no paid call;
the phase review is Codex through the review helper (plan gate D7). The
sweep: every obligation of §3 maps to a test or a design section; every
expected value in §8 was measured (§6.3). The spec's SHA-256 is recorded in
`003-phase-RP1.md`. Disclosure: the implementation was drafted in the
working tree before this gate was written, against the `(p2)` draft; the
gate was ruled over this text, and the record says so.
