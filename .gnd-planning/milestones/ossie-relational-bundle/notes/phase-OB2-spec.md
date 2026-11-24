# Phase OB2: the Halpin relational mapping (`gnd.rmap`)

## 1. Status

**Implemented, 2026-11-24.** The owner approved r1 with S1–S11 as proposed
([spec gate](../005-OB2-spec-gate.md)), the corpus and amendment r1.1
([corpus gate](../006-OB2-corpus-gate.md)), and D5 = HALPIN together with
deviations IF5 and RR1 ([D5 gate](../007-OB2-D5-gate.md)). §13 and §14
record what implementation and review changed. The text below §1 is kept as
written at each gate.

## 2. Provenance

- **Plan:** [ossie-relational-bundle plan r2](ossie-relational-bundle-plan.md)
  (sha256 `52d946a4…6e1d`), approved at the [plan gate](../002-plan-gate.md)
  with D1–D11 ruled as proposed. This spec reads §0, §2.3, §3, §4 OB2, §6, §7,
  §9 and §10 D1, D4, D5 and D11.
- **Prior phase:** the OB1 record, `004-phase-OB1.md`, which is on branch
  `claude/ossie-ob1-size-bounds` and PR #266, unmerged, so it is not linked from
  this branch. OB2 depends on no
  OB1 code: this branch is cut from the planning branch at `a7847f2b`.
- **Census survey, run 2026-11-24 while writing this spec.** It covers the
  41-model export census, of which 38 are standalone:

  | What | Count |
  |---|---|
  | Fact types, by arity | 24 unary, 170 binary, 31 ternary, 1 quaternary |
  | Fact types that declare **no** uniqueness constraint | 119 (100 binary, 19 ternary) |
  | Fact types whose uniqueness is proposed or deontic | 6 |
  | Derived fact types | 32 |
  | Entity reference modes | 57 popular, 4 general, 2 external, 0 unit-based, 2 subtypes with none |
  | Popular references that also have an explicit entity–value-type fact type | 3 |
  | Symmetric 1:1 binaries | 3 |
  | Fact types with both a single-role and a compound uniqueness | 0 |
  | Objectified fact types | 1 |
  | Subtypes | 2, both `inherits_reference: true` |

  These counts are why S1–S4 exist. The plan's §2.3 does not address the
  majority case: a fact type with no uniqueness.
- No review has run over these bytes.

## 3. Obligations

| # | Source | Obligation | Discharged in |
|---|---|---|---|
| O1 | Plan §4 OB2 deliverable | `gnd.rmap`: a deterministic Halpin Rmap from a loaded model to an internal relational schema. That schema holds tables, columns, PK, unique keys, ordered composite FKs, and the unmapped list with reasons. It implements both D5 variants behind an internal switch, with no CLI change. | §6.1–§6.4 |
| O2 | Plan OB2-C1, predicate 3 | Every census model yields a schema with no model-level refusal. | §6.5 totality; T1 |
| O3 | Plan OB2-C2 | Hand-derived expected schemas for a fixture corpus, committed before the code, with one fixture per rule and tie-break, including those the plan names. | §8 corpus; §11 |
| O4 | Plan OB2-C3 | Determinism across source paths and declaration order. | T3 |
| O5 | Plan OB2-C4 | A time bound at 1,400 tables and 4,500 fact types. | T4 |
| O6 | Plan OB2-C5, D5 | Both variants measured over the census and the corpus. Recorded per variant: tables, unmapped fact types, FKs, and agreement with the C2 key. The owner rules D5 at a gate inside OB2. | §6.6; T5; §10 gate |
| O7 | Plan §2.3 | Placement precedence; identification and keys; subtypes; objectification; relationships; required core-spec members; determinism and totality; populations; unrepresentable constructs. | §6.2–§6.4, corrected by S1–S9 where the census or Halpin disagrees |
| O8 | Plan D4 | Non-primary confirmed alethic uniqueness within one table becomes `unique_keys`. One spanning several tables is listed. | §6.3 |
| O9 | Plan §0 rule 5 | The normative Rmap rules have one home. | §6.7: a new section in `representation-format.md` |
| O10 | Plan §0 rule 4 | One walk over all fact types and all constraints, so that each is carried or listed. The Rmap supplies it; OB3 reuses it. | §6.5 `dispositions`; T2 |
| O11 | Plan §3 | Homes: `src/gnd/rmap.py`, `tools/gnd_layers.json`, `dev/components/`. | §6 |
| O12 | Plan §9 OB2 row | `uv run pytest -q tests/test_rmap.py --tb=short`. Affected consumers: `tools/gnd_layers.json` and the component index. | §8 gate |
| O13 | Plan §6 | Risk: the Rmap's choices differ from a delivered DDL. | D5 measurement; OB4 owns the remedy (§9) |
| O14 | Plan §7 | No DDL generation and no Ossie files in OB2. | §9 |
| O15 | OB1 record, OB1-Q1 | `guard_yaml` default capture. | Not OB2's: OB2 reads no YAML itself (§9) |

## 4. Standing rules bound to this phase

1. **Totality.** `map_model` consumes a **loaded `Model`**, which passed both
   validation layers, not raw JSON. The rule still binds: for every model the
   loader admits, `map_model` returns a schema and never raises. The function
   holds this, not its callers. Anything it cannot place becomes an
   `Unmapped` row with a closed reason. T1 runs it over every standalone
   model file in the repository, not only the census. T1b feeds it
   adversarial but valid models: reference cycles, a subtype of a subtype
   with no identifier, and an external uniqueness that names its own entity.
2. **Cap bounds the document, not the algorithm.** The work is proportional
   to the number of fact types, roles and constraints, using `ModelIndex`
   maps and per-object-type buckets. There is no scan over all fact types
   per object type, and no pairwise comparison of tables. T4 bounds the time
   at 1,400 entity tables and 4,500 fact types, and T4b at 10× that, to show
   the growth is not quadratic.
3. **Validation order.** The placement precedence in §6.2 is a **normative
   order**. A fact type is placed by the first rule that applies. T6 pins it
   with one fixture per adjacent pair of rules that both apply (S5 is the
   clearest case).
4. **One walk.** `dispositions(model, schema)` returns exactly one row for
   every fact type and every constraint: carried (where) or unmapped (why).
   OB3 renders the GND extension from this walk and does not re-derive it.
   T2 asserts the partition (none missing, none doubled) on every model.
5. **One home.** The rules in §6.2–§6.4 move, in OB2, into a new section
   "Relational mapping (Rmap)" of `representation-format.md`. That section
   becomes their only home; this spec and the code cite it. Plan §2.3 yields
   to it where S1–S9 change it.
6. **Measure.** D5 is decided from T5's measurement, not argued. S1–S4 were
   raised by the census survey in §2.

## 5. Goal

`gnd.rmap.map_model(model, variant=...)` returns a `RelationalSchema` for every
model the loader admits. The same model content gives an equal value,
whatever its path or declaration order.

- **Corpus:** for every fixture, the schema equals the committed
  hand-derived answer (T6).
- **Census:** for every census model, `dispositions` partitions all fact
  types and constraints (T2).
- **Time:** at the reporter's scale, mapping completes within the measured
  bound (T4).
- **D5:** T5 publishes the variant comparison table that the D5 gate reads.

There is no CLI, so there are no exit codes in this phase.

## 6. Design

### Reuse

| Capability | Searches run | Found | Decision |
|---|---|---|---|
| Entity identification (direct or composite) | `components_index.py search "reference scheme"` and `"preferred identifier"` | `model.reference_schemes`: `gnd.refscheme.reference_identity` returns direct, composite or unmatchable | **reuse**, never re-implemented |
| Model queries | `"uniqueness constraint"`; `ModelIndex` | `gnd.model_index.ModelIndex` (`for_model`, `object_types_by_id`, `fact_types`, `supertype_closure`, `subtype_children`, `iter_constraints`) | **reuse** (AGENTS.md: model queries go through ModelIndex) |
| Identifying primitive of a value type | `"reference resolution"` | `model.reference_resolution`: `gnd.model_queries.primitive_for` | **reuse** for column datatypes |
| Relational schema or table mapping | `"relational table"`, `"primary key"`; `git grep -i rmap` | nothing | **new**: GND has no Rmap (plan §1.2) |
| "Confirmed alethic" test | `git grep "modality\") == \"alethic\""` | inline in `export/ossie.py:123,187`, with no shared helper | **new** private predicate in `rmap`. The Ossie copy is a deferred refactor (§9), not touched here. |

### 6.1 Module and surface: `src/gnd/rmap.py`

About 450 lines. Layer `model`, because it depends only on `model`,
`model_index`, `refscheme` and `model_queries`.

```python
class RmapVariant(enum.Enum):
    HALPIN = "halpin"            # subtypes absorbed; symmetric 1:1 toward the first object-type id
    ALTERNATE = "alternate"      # subtypes separate; symmetric 1:1 toward the player with more functional roles

@dataclass(frozen=True)
class Column:
    name: str
    datatype: str | None         # a GND value primitive (String, Integer, ...) or None
    nullable: bool               # False when a confirmed alethic mandatory covers the role, or the column is a key column
    origin: tuple[str, str]      # (fact_type_id, role_name), or ("reference", object_type_id) for a reference column

@dataclass(frozen=True)
class ForeignKey:
    name: str                    # <from_table>__<to_table>, then __2, __3 ... in column order
    columns: tuple[str, ...]     # ordered
    target_table: str
    target_columns: tuple[str, ...]   # the target's primary key, in its order

@dataclass(frozen=True)
class Table:
    name: str
    subject: tuple[str, str]     # ("object_type", id) or ("fact_type", id)
    columns: tuple[Column, ...]
    primary_key: tuple[str, ...]
    unique_keys: tuple[tuple[str, ...], ...]
    foreign_keys: tuple[ForeignKey, ...]

UnmappedReason = Literal[
    "derived-computed",              # S3
    "uniqueness-not-confirmed",      # S2: a proposed, rejected or deontic uniqueness
    "identification-unmatchable",    # refscheme returned "unmatchable"
    "spans-tables",                  # D4: a uniqueness over columns of more than one table
    "not-relational",                # a constraint type the relational form does not carry (§6.4)
]

@dataclass(frozen=True)
class Unmapped:
    kind: Literal["fact_type", "constraint", "object_type"]
    id: str                          # fact type id, object type id, or constraint address (§6.5)
    reason: UnmappedReason
    detail: str = ""                 # the constraint type for not-relational; else empty

@dataclass(frozen=True)
class RelationalSchema:
    variant: RmapVariant
    tables: tuple[Table, ...]        # sorted by name
    unmapped: tuple[Unmapped, ...]   # sorted by (kind, id)

def map_model(model: Model, *, variant: RmapVariant = RmapVariant.HALPIN) -> RelationalSchema: ...

@dataclass(frozen=True)
class Disposition:
    kind: Literal["fact_type", "constraint"]
    id: str
    carried_as: tuple[str, ...]      # e.g. ("table", "order"), ("column", "order", "placed_on"), ("primary_key", "order"); empty when unmapped
    reason: UnmappedReason | None

def dispositions(model: Model, schema: RelationalSchema) -> tuple[Disposition, ...]: ...
```

`variant` is internal. No CLI flag selects it (plan §4 OB2). OB3 calls
`map_model` with the variant D5 selects.

### 6.2 Placement: the normative order

Only **confirmed alethic** uniqueness constraints (`status: confirmed`,
`modality: alethic`) drive placement and keys (S2). Others are listed as
`uniqueness-not-confirmed`, and the fact type is placed as if they were
absent.

The **effective uniqueness set** of a fact type is computed as follows:
1. Take its confirmed alethic internal uniqueness constraints.
2. If there are none, use one implied spanning uniqueness over all roles
   (S1).
3. Drop any uniqueness that is a superset of another in the set: it is
   implied (plan F9).

Each fact type is placed by the **first** rule below that applies:

0. **Not stored.** `derivation` is `derived` with `storage` absent or
   `computed`: unmapped, `derived-computed` (S3). A `semiderived` fact type,
   or one with `storage: stored`, continues to rule 1.
1. **Reference fact type.** It is a binary between an entity E and E's
   reference value type V (popular or general), with a single-role
   uniqueness on V's role. It is carried as E's key column and adds no
   column of its own (S4).
2. **Identification component.** It is named by a preferred external
   uniqueness that identifies an entity E (`refscheme` composite). It is
   carried as E's key column or columns.
3. **Objectified.** It has `objectified_as: O`. Table `O`, keyed by the
   effective uniqueness of the fact type (S8), with one column or FK group
   per role.
4. **Unary.** A non-nullable Boolean column `<fact_type id>` in the table of
   its player (S6). Playing a unary gives the player a table.
5. **Functional.** The effective set contains a single-role uniqueness on a
   role r. Grouped into the table of r's player P (S5, which corrects plan
   rule 2). The other role becomes a column, or an FK group when its player
   has a table. If more than one role carries a single-role uniqueness (1:1):
   - **One role's player is mandatory there:** that role is r.
   - **Otherwise, the variant decides (D5).** Under HALPIN, r is the role
     whose player's id sorts first. Under ALTERNATE, r is the role whose
     player has more functional roles, with ties broken by id. The other
     single-role uniqueness becomes a `unique_keys` entry on that column.
6. **Own table.** Otherwise, the fact type gets table `<fact_type id>`,
   keyed by the primary choice among its effective set (§6.3), with one
   column or FK group per role.

**Which object types get a table** (S7):
- **An entity E:** when some fact type is placed in E (rules 4 and 5),
  when E is `independent: true`, or when E is the target of an
  objectification (rule 3).
- **A value type V:** when V is the determining player of a rule-5
  placement.
- **Otherwise:** the object type has no table. Roles it plays are plain
  value columns (its identifying value or values) with no FK.

**Subtypes** (D5 variant):
- **HALPIN:** a subtype with `inherits_reference: true` is absorbed. Its
  rule 4 and 5 placements go into its root supertype's table as nullable
  columns.
- **ALTERNATE:** such a subtype gets its own table. It is keyed by the
  inherited key, which is also an FK to the supertype's table.
- **`inherits_reference: false`:** always its own table, keyed by its own
  identification.

### 6.3 Identification, keys and columns

**Key columns of an entity table** are its identification, from
`refscheme.reference_identity`:

| Identification | Key columns |
|---|---|
| `direct` (popular or general) | one column named after the value type's id, typed by its primitive |
| `direct`, unit-based | one column `<object type id>_value`, typed `Number` (S9) |
| `composite` | one column per component role, in `role_refs` order. A component whose player has a table becomes an FK group. |
| `unmatchable` | the entity is unmapped (`identification-unmatchable`), and so is every fact type placed in it. `refscheme` returns this for a composite whose component is itself composite-identified ("nested composite joins are not supported"); the Rmap inherits that limit and lists it rather than re-implementing identification. |

**A value-type table**'s key is its single value column, named after the
value type's id.

**The primary key of an own table** (rule 6) is the preferred uniqueness,
when one is marked `preferred: true`. Otherwise it is the smallest-arity
effective uniqueness. Ties are broken by the sorted tuple of the
uniqueness's role positions in the fact type: role order is semantic, and
constraint declaration order is not. Key columns follow role order. Two
uniqueness constraints over the same roles are one key.

**Unique keys** (D4): every other effective uniqueness whose columns all lie
in one table becomes a `unique_keys` entry, in the same order. So does the
second single-role uniqueness of a 1:1 (rule 5). A confirmed alethic
uniqueness whose roles map to columns of more than one table is unmapped,
with `spans-tables`. This includes external uniqueness that is not an
identification.

**Columns:**
- **Names.** A column playing value type V is named `<role_name>`. An FK
  group to a table with key columns k1…kn is named `<role_name>_<ki>`. On a
  name collision inside a table, later columns, in (fact type id, role
  position) order, get `_2`, `_3`, and so on.
- **Datatype.** `primitive_for(value_type, object_types, variant="strict")`,
  or None when unresolved.
- **Nullable.** True unless the column is part of the primary key, or a
  confirmed alethic `mandatory` covers its role on the table's subject.
  Subtype-absorbed columns are always nullable.

**Foreign keys:** one per FK group, from the group's columns to the target's
primary key, named `<from_table>__<to_table>` and then `__2`, `__3` in column
order.

### 6.4 Constraints the relational schema does not carry

`dispositions` lists each of these by constraint address with
`not-relational` and the constraint type as `detail`:

- frequency, ring, subset, equality, exclusion, exclusive-or,
  mandatory-disjunctive, value, value-comparison, cardinality,
  subtype-partition, textual, guarded and anchored;
- a mandatory on a role whose column is not in the role's subject table.

Two kinds of constraint are **carried**:
- a confirmed alethic `mandatory` becomes `nullable: false`;
- a confirmed alethic uniqueness becomes a placement, a PK or a unique key.

### 6.5 Totality and the one walk

- **Constraint address.** `fact_types/<fact_type id>/constraints/<index>`
  for an inline constraint; `constraints/<index>` for a top-level one.
  Indexes are the declaration indexes. Determinism (T3) compares schemas, and
  addresses appear only in `dispositions`.
- **`dispositions`** iterates `ModelIndex` once over fact types and once over
  constraints. For each it emits the carried location recorded during
  placement, or the unmapped reason. It never re-derives placement.
- **Never raises.** `map_model` never raises for an admitted model. A
  `refscheme` result of `unmatchable` and every other unplaceable case
  become rows. An internal invariant violation is a programming error and
  is allowed to raise. T1 is the guard.

### 6.6 The D5 measurement (OB2-C5)

T5 maps every census model and every corpus model under both variants. It
writes `notes/OB2-variant-measurement.md` with one row per model and a total
row. The columns are:
- table count;
- unmapped fact types;
- FK count;
- nullable column count;
- for corpus models, agreement with the answer key for that variant.

The corpus key gives expected answers per variant only for the fixtures
where the variants differ (§8, cases C15–C17). The D5 gate reads this table
before OB2 is recorded.

### 6.7 Normative home

OB2 adds a section "Relational mapping (Rmap)" to
`src/gnd/skills/gnd-orm-core/references/representation-format.md`. It sits
after "Model includes" and before "Ossie interchange", and holds §6.2–§6.4
in prose. The module docstring cites it. Plan §2.3 is superseded where S1–S9
differ. The plan is not edited (process-phase never edits the plan); the
phase record lists the differences as refuted premises for the close
amendment.

## 7. Decisions

| ID | Question | Proposal | What the other reading costs |
|---|---|---|---|
| S1 | A fact type with **no** declared uniqueness: 119 of 226 census fact types. | Treat it as having the implied spanning uniqueness (sets semantics, as in Ossie relationships), so it gets its own table (rule 6), or a column if it is unary. | Listing these as unmapped would leave more than half of every model out of the schema. |
| S2 | Which uniqueness drives placement? | Only confirmed alethic uniqueness. Proposed and deontic ones are listed as `uniqueness-not-confirmed` (6 census fact types). | Using a deontic uniqueness as a key builds a table whose key real data may violate. |
| S3 | Derived fact types (32 in the census). | `derived` and computed: unmapped, `derived-computed`. Stored or semiderived: placed. | Mapping computed derivations writes columns no producer fills. |
| S4 | A popular reference with an explicit fact type between E and its reference value type (3 in the census). | The fact type **is** the reference. It is carried as E's key column, with no duplicate column (rule 1). | A duplicate column holding the key twice. |
| S5 | **Plan §2.3 rule 2 is not Halpin.** It groups n−1 uniqueness of n-aries into an entity table. | Group only on a **single-role** uniqueness. A compound uniqueness always means its own table (Halpin's Rmap). | Rule 2 as written has no table to group a role combination into, so it is not implementable. |
| S6 | A unary fact type. | A non-nullable Boolean column named after the fact type, in its player's table; false means absent. | Halpin's alternative, a separate table keyed by the player, is selectable later; it doubles the number of tables. |
| S7 | Which object types get a table. | §6.2: entities with placements, independent entities, objectifications, and value types that determine a rule-5 placement. Otherwise there is no table, and references are plain value columns. | Giving every object type a table adds empty tables and FKs to them. |
| S8 | Objectification key. | The objectified fact type's own effective uniqueness, through §6.3's primary choice. | — |
| S9 | Unit-based reference (none in the census). | Column `<id>_value`, typed `Number`. The unit and measure type are listed in OB3's extension. | — |
| S10 | Column naming and collisions. | §6.3: role names, `_<key>` for FK groups, and `_2`… suffixes in (fact type id, role position) order. | Names from readings would be unstable under reading edits. |
| S11 | Approval instrument (§11). | Corpus first: the owner gates on the fixture stories, and the spec is the design record. | Prose only: plan OB2-C2 still requires the corpus before code, so the gate comes later and reads less. |

The D5 variants are defined in §6.2. D5 itself is ruled at the internal gate
after T5, not here.

## 8. Tests and corpus

### The corpus (authored first; plan OB2-C2)

Each case lives at `tests/fixtures/rmap/cases/<NN>-<slug>/`:
- `model.orm.yaml` (valid and minimal);
- `STORY.md`: what the model says and, in words, what tables a Halpin
  reader expects. Stories do not show the answer schema.

Answer keys live apart, at `tests/fixtures/rmap/answers/<NN>.json`. They are
canonical JSON of the expected `RelationalSchema` and `dispositions`, with
`answers/<NN>.alternate.json` only where the variants differ. The entry
README (`tests/fixtures/rmap/README.md`) links the stories, not the
answers.

| Case | Exercises |
|---|---|
| C01 | functional binary, entity and value type |
| C02 | popular reference with an explicit reference fact type (S4) |
| C03 | general reference |
| C04 | m:n binary with spanning uniqueness |
| C05 | binary with **no** uniqueness (S1) |
| C06 | 1:1, one role mandatory |
| C07 | 1:1, both roles mandatory (D5) |
| C08 | 1:1, neither role mandatory (D5) |
| C09 | unary (S6) |
| C10 | ternary with an n−1 uniqueness: own table (S5) |
| C11 | quaternary with spanning uniqueness |
| C12 | single-role and compound uniqueness on one fact type: the compound is implied (F9) |
| C13 | own table with two candidate compound keys, one `preferred` |
| C14 | external compound identification, referenced from another entity: composite FK |
| C15 | subtype with `inherits_reference: true` (D5) |
| C16 | subtype with `inherits_reference: false` |
| C17 | objectification |
| C18 | derived computed, derived stored, semiderived (S3) |
| C19 | proposed and deontic uniqueness (S2) |
| C20 | value type as the determining player: value-type table (S7) |
| C21 | self-referential entity binary: FK to its own table, plus column-name collision (S10) |
| C22 | entity with no placements, played only in an m:n: no table, no FK (S7) |
| C23 | unit-based reference (S9) |
| C24 | each `not-relational` constraint type once (§6.4) |
| C25 | unmatchable identification (a composite cycle) |

### Tests (`tests/test_rmap.py`)

| ID | Case | Expected |
|---|---|---|
| T1 | `map_model` over every standalone `*.orm.yaml` and `*.orm.json` model the loader admits under `src/gnd` and `tests/fixtures`, under both variants | returns, never raises |
| T1b | adversarial valid models (reference cycle, an unidentified subtype of a subtype, a self-anchored external uniqueness) | returns; the expected `identification-unmatchable` rows |
| T2 | `dispositions` over the census and corpus | every fact type id and constraint address appears exactly once |
| T3 | each corpus and census model, re-serialized with object types, fact types, inline and top-level constraints in reversed order (role order kept: it is semantic), and loaded from another path | equal `RelationalSchema`; `dispositions` equal after mapping addresses through the permutation |
| T3b | C13 with its two candidate keys declared in both orders | the same primary key (the tie-break never reads declaration order) |
| T4 | generated model: 1,400 entities with popular references and 4,500 fact types (a mix of functional, m:n, unary and ternary) | under a bound set from measurement and recorded |
| T4b | the same generator at 10× | time ratio under 20, which rules out quadratic growth |
| T5 | both variants over census and corpus | writes the measurement table (§6.6); asserts its row count |
| T6 | each corpus case under HALPIN, and ALTERNATE where an alternate answer exists | equals the answer key |
| T7 | precedence pins: C02 (rule 1 over 5), C12 (5 over 6), C17 (3 over 6), C18 (0 over everything) | rules 0 and 1 come first, as written |
| T8 | public surface: dataclasses frozen; `RmapVariant` members exactly `HALPIN`, `ALTERNATE`; `UnmappedReason` members exactly as §6.1 | literal assertions |

**Branch walk.** Each placement rule 0–6 has a case where it fires, and a
case where it would also apply but an earlier rule wins (T7). Each
identification row of §6.3 has a case: C01, C03, C14, C23, C25. Each
`UnmappedReason` has a case: C18, C19, C25, C14 extended, C24.

**Gate:**
1. `uv run pytest -q tests/test_rmap.py --tb=short`
2. the issue-171 guard list from `project.md`
3. `uv run ruff check`
4. `python3 scripts/components_index.py changed --base <phase base> --strict`

## 9. Out of scope for this phase

- No Ossie files, no CLI, no `--ontology-only` (OB3).
- No binding (OB4).
- No DDL text.
- No change to `export/ossie.py`. The duplicated "confirmed alethic"
  predicate there is a deferred refactor: an open-questions row targets
  OB3, which edits that module anyway.
- No YAML reading of its own, so OB1-Q1 (`guard_yaml`) stays open
  elsewhere.
- No population data in any table.

## 10. Size

Estimate:
- `rmap.py`: about 450 lines;
- the normative section: about 120 lines;
- `test_rmap.py`: about 350 lines;
- the corpus: 25 cases of about 20–60 YAML lines each, plus stories and
  answers.

**Inside the phase:** after T5, OB2 stops at an owner gate for D5. That
ruling is recorded before the phase record.

## 11. Approval instrument

**Proposed: corpus first (S11).**

1. The 25 cases and their stories are authored and committed **before any
   `rmap.py` code**.
2. The owner gates on the stories in `tests/fixtures/rmap/README.md`.
3. The answer keys are split into `answers/`, so a later independence pass
   can be run blind.
4. The harness lands red: T6 fails on every case because `gnd.rmap` does
   not exist yet.
5. Each implementation commit names the cases it turns green.

If the owner prefers prose approval, the corpus is still committed before
the code (plan OB2-C2). Only the gate moves.

## 12. Amendment r1.1: rules settled while authoring the corpus (2026-11-24)

The owner approved r1 (sha256 `6bcca4ed…2cb972`; [gate](../005-OB2-spec-gate.md)).
Under S11, authoring the corpus and its hand-derived answers came next.
Doing that forced the rules below, which r1 left open or got wrong. **They
are unapproved**: the owner sees them at the corpus gate, together with the
stories. §1–§11 above are unchanged, except where a row here says it
supersedes them.

| # | Rule | Why | Case |
|---|---|---|---|
| A1 | `carried_as` uses a closed vocabulary: `table`, `columns`, `key`, `placement`, `primary_key`, `unique_key`, `implied` and `not_null`. Its definition is in `tests/fixtures/rmap/answers/README.md`, and it moves into the normative section in OB2. | r1 §6.1 gave examples only, so no answer key could be written. | all |
| A2 | **Column order:** key columns first, in identification order; then placed columns by (fact type id, role position). In an own table, columns follow role order. | r1 did not order columns, but the answer keys compare them in order. | 01–24 |
| A3 | A **unit-based** reference is recognized from `reference.mode` **before** `refscheme` is consulted. | `refscheme.reference_identity` returns `unmatchable` for unit-based references (measured on case 23). Without this rule, S9 could never fire. | 23 |
| A4 | Rule-2 placements (identification components) **give the entity a table**. This refines S7. | Halpin places those functional fact types in the entity's table. Without this, a composite-identified entity with no other facts has no table that its identification facts could live in. | 14, 25 |
| A5 | **Objectification (supersedes rule 3 and S8 where they differ).** Table O is keyed by O's identification from `refscheme`, because GND requires an external uniqueness for an objectified entity (measured on case 17). The objectified fact type's roles are matched to O's composite components **by player object type**. Matched roles are O's key, and the fact type is carried as `key`; unmatched roles become columns. If O's identification is unmatchable, O is keyed by the fact type's effective uniqueness (S8), not unmapped. | The validator refused case 17 as first written: "reference mode 'external' but no top-level external uniqueness constraint identifies it". Matching by player rather than by name keeps names out of it. | 17 |
| A6 | A constraint of an unmapped fact type, and the external uniqueness of an unmapped entity, are unmapped **with the same reason**. | Otherwise the one walk would have to invent a second reason for one cause. | 18, 25 |
| A7 | **Nullability.** Every column of an own table (rule 6), and every objectification column, is non-null: a fact instance fills all its roles. A `mandatory` is carried as `not_null` only when it is on the subject role of a rule-5 placement. Any other mandatory is `not-relational` with detail `mandatory`. This supersedes the second bullet of §6.4. | r1 said "nullable unless PK or mandatory", which would make own-table role columns nullable. | 05, 07, 10, 19 |
| A8 | **ALTERNATE's count of functional roles** is the number of roles the object type plays that carry a confirmed alethic single-role uniqueness, in fact types not unmapped by rule 0. | r1 named the count but did not define it. | 07, 08 |
| A9 | Under HALPIN, a symmetric 1:1 where **both roles have the same player** goes toward the first role position. | The tie-break by id is otherwise undefined. | — (no census case) |
| A10 | The primary key of a **value-type table** is its value column, named after the value type id, with origin `("reference", <value type id>)`. | r1 named the column but not its origin. | 20 |
| A11 | **Foreign-key name suffixes** count per (from table, to table) pair: `T__U`, then `T__U__2`. | A self-referencing junction table gets two foreign keys to one table. | 24 |
| A12 | `unmapped` and `dispositions` are sorted by (`kind`, `id`), comparing ids as strings, so `constraints/10` sorts before `constraints/2`. | r1 said "sorted" without saying by what. | 24 |
| A13 | Corpus models are named `cases/NN-slug/model.yaml`, not `model.orm.yaml`. | `tests/test_li0_witness_wire.py` pins the identity of every `*.orm.yaml` under `tests/fixtures` against a golden file frozen in phase LI0, and extending that historical pin is out of scope. Measured: naming them `.orm.yaml` turned that test red. | all |
| A14 | T1's model scan covers `*.orm.yaml`, `*.orm.json` **and** the corpus `model.yaml` files. | Follows from A13. | — |

**Authoring checks run (no Rmap code exists):**
- All 25 models load through `gnd.model.load_model`.
- `refscheme` classifies the cases as intended: 14 and 17 composite; 23
  and 25 (district) unmatchable.
- The 28 answer files pass a structural check: every fact type and
  constraint appears exactly once; lists are sorted; keys name existing
  columns; foreign keys target an existing primary key.
- `tests/test_li0_witness_wire.py` passes after A13.

## 13. Implementation findings (recorded during OB2)

| # | Finding | Effect |
|---|---|---|
| IF1 | **A guard that went quiet.** Derived fact types got no unmapped row. `dispositions()` hid the gap by defaulting a missing row to `not-relational`, and case 18's answer key caught it. | Derived rows are written. A missing row now raises as an internal invariant violation, so T2 can no longer pass by default. |
| IF2 | **Totality defect.** An identifiable objectification with a role played by an unmatchable entity raised `AttributeError`, because the guard covered only rules 5 and 6. | The guard covers rules 3, 5 and 6. T1b keeps the model as a regression case. |
| IF3 | **Quadratic time.** At 5× the reporter's scale, the time ratio was 27.2 (quadratic predicts 25). `refscheme.reference_identity` → `universe.resolve_reference_value_type` rebuilds a map of every object type on each call, and the Rmap called it once per entity. `build()` also scanned every fact type once per table. | Direct identification now uses `ModelIndex.reference_value_types()`, which is documented as a cache of the same resolver; `refscheme` is called only for composites. The per-table scan is precomputed. Measured after the fix: 0.067 s at 1×, ratio 5.47. |
| IF4 | T4b at 10× cannot load: the generated model exceeds `MAX_MODEL_BYTES`. | T4b runs at 5× and asserts a ratio under 12 (linear is about 5, quadratic about 25). |
| IF5 | **Rule 1 also gives the entity a table.** S7 and A4 list rules 2, 4 and 5. Under that wording, an entity whose only fact type is its explicit reference would have no table for its `key` disposition to point at. | Implemented with rules 1–5 giving a table. No corpus answer changes (case 02 has a table anyway). **The owner sees this at the D5 gate.** |
| IF6 | **RF6 query policy.** The first `rmap.py` read `.fact_types`, `fact.get("roles")` and `constraint.get("roles")` directly, which turned 7 guard tests red. | All model reads go through `ModelIndex`: `iter_fact_types_shared`, `role_object_types` and `constraint_roles`. The 129 syntax-level dynamic-subscript candidates of the new module are recorded as a counted delta in `evidence/OB2/dynamic-query-successor.json`, chained after GO3-GO5. That is a census only; no query exception is widened. |
| IF7 | A uniqueness that repeats another's roles, and a uniqueness on a unary, are recorded as `implied`. | Stated in the normative section. |
| IF8 | **The D5 measurement** ([OB2-variant-measurement.md](OB2-variant-measurement.md)): 4 of 66 models differ between the variants. Three are the D5 corpus cases (07, 08, 15). In the census, only `library_with_subtypes` differs: 1 table and 4 nullable columns under HALPIN, against 3 tables and 1 nullable column under ALTERNATE. | Input to the D5 gate. |
| IF9 | T3's reordered copy of a census model with version-4 reference populations cannot load away from its `references/` folder. | T3 copies the model's folder, so it skips no census model. |
| IF10 | `tests/test_li0_witness_wire.py` scans fixture models. | It joins the focused gate. |

## 14. Review round 1 (Codex, read-only) and its repairs

[review.md](reviews/phase-OB2-r1/review.md) requested changes, with nine
findings. Each was reproduced as a regression test (R1–R9) and shown
failing on the pre-repair code (15 of 15 red) before any fix. The ledger is
[FINDINGS.md](reviews/phase-OB2-r1/FINDINGS.md). No approved corpus answer
changed. The rules the repairs change are now in the normative section.

| # | Change | Departs from |
|---|---|---|
| RR1 | Composite identification is the Rmap's own selection: the external uniqueness that is confirmed, alethic and `preferred`, anchored on the entity, with the smallest sorted role references winning a tie. `refscheme.reference_identity` is no longer used. It takes the first external uniqueness anchored on the entity whatever its status (F1), and calling it per entity was quadratic (F9). | Spec §6 reuse table ("reuse refscheme, never re-implemented"). **The owner sees this at the D5 gate.** |
| RR2 | Duplicate uniqueness constraints form one key, preferred if any is, and share one disposition. | A1's `implied` for duplicates (IF7) |
| RR3 | Unique keys are sorted by column position. | — |
| RR4 | An external uniqueness within one table is a unique key; one over an unmapped fact type takes that fact type's reason. | §6.3 |
| RR5 | An objectified uniqueness narrower than the key is a unique key. | A5 |
| RR6 | Under ALTERNATE, an inheriting subtype's supertype always gets a table. | S7 |
| RR7 | A role played by a value type that has a table is a foreign key. | §6.3 |
| RR8 | An absorbed unary column is nullable. | rule 4 |
| RR9 | The role-to-column map is a real dictionary, not text split back apart. The constraint index is passed in rather than parsed out of the address. | — (AGENTS.md, "General solutions") |

**The repaired bytes are not re-reviewed.**

## 15. Review round 2 (Codex, read-only) and its repairs

The owner asked for a second round over the round-1 repairs ("Re-review,
then PR"). [review.md](reviews/phase-OB2-r2/review.md) requested changes,
with eight findings, from base `af34a54e`. Each was reproduced as a
regression test (14 tests) and shown failing on the pre-repair code before
any fix. The ledger is [FINDINGS.md](reviews/phase-OB2-r2/FINDINGS.md). No
approved corpus answer changed, and the variant measurement is unchanged
(4 of 66 models differ; same totals).

| # | Change | Departs from |
|---|---|---|
| RR10 | An objectification's fallback key (A5) is its key wherever it is referenced; its identification fact types are then placed by later rules (F1). | A5 |
| RR11 | Identifier ties break on the `role_refs` sequence after the sorted references; any confirmed external uniqueness over the identifier's roles is the `primary_key` (F2). | RR1 |
| RR12 | External unique-key columns are in table order, each once, and uniqueness constraints over one column set share one key and one disposition (F3, F8). The R4 pin moved from (`phone`, `email`) to (`email`, `phone`). | RR4 |
| RR13 | An inheriting subtype is identified as its first supertype, composite included (F4). | §6.3 |
| RR14 | A value component of a composite key is a foreign key when its value type has a table (F5). | RR7 |
| RR15 | An external uniqueness that references a rule-0 fact type identifies nothing and takes that fact type's reason (F6). | RR1 |
| RR16 | A unary role is held by its table's key columns, not the Boolean column (F7). | RR4 |

**The round-2 repaired bytes are not reviewed.**
