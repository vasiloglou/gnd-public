# Phase OB4: the physical binding (`--physical-binding FILE`)

## 1. Status

**r1 approved 2026-11-24 with G1–G18 as proposed**
([spec gate](../013-OB4-spec-gate.md)). The corpus, the schema file and
amendment r1.1 (§13) are authored and **await the corpus gate**. No reader
code is written. Not reviewed.

## 2. Provenance

- **Plan:** [ossie-relational-bundle plan r2](ossie-relational-bundle-plan.md)
  (sha256 `52d946a4…6e1d`), approved at the [plan gate](../002-plan-gate.md)
  with D1–D11 as proposed. Read for this spec: §0, §1.1 (I3), §2.1, §2.2,
  §2.4, §3, §4 OB4, §5, §6, §7, §9 and §10 D7, D8, D10.
- **The issue** (I3, the owner's issue file, issue 3). Its text is the only
  description of the caller's document. It names `tables`, `columns`,
  `sql_type`, `targets` (`kind`, `fact_type`, `object_type`,
  `references {table, columns}`), `primary_key`, `roles` and
  `extension_roles`, and the rules "role names match ignoring case and
  punctuation", "refuse unknown names", "an unbound fact type is listed with
  the binding's sha256" and "output unchanged without the flag".
- **Prior phases:**
  - OB3, record [011-phase-OB3.md](../011-phase-OB3.md) (PR #271, unmerged):
    the semantic-model and mapping builders, `OntologyView`, the `GND`
    extension, the rules B1–B14, and the owner-accepted departures
    ([gate](../012-OB3-departures-gate.md)). Open: OB3-Q3 (oracle lane),
    OB3-Q4 (second review round), OB3-Q5, OB3-Q6.
  - OB2, record [008-phase-OB2.md](../008-phase-OB2.md): `gnd.rmap`, whose
    `RelationalSchema`, `RolePlacement`, `Identification` and `dispositions`
    this phase fills from a binding instead.
- **D10 is not done.** The reporter has not been asked for their diffs,
  their document's exact shape, or the meaning of `extension_roles`. This
  spec therefore defines a GND-owned document from the issue's words alone
  (D7). G1 puts that to the owner.
- No review has run over these bytes.

## 3. Obligations

| # | Source | Obligation | Discharged in |
|---|---|---|---|
| O1 | Plan §4 OB4 deliverable | `--physical-binding FILE`: the schema, a total reader, name resolution, normalized role matching, the refusal order, and the unbound listing with the binding's sha256 | §6 |
| O2 | OB4-C1 (p1 F7) | A valid binding replaces datasets, fields, PKs, unique keys and relationships. Every §2.4 member has a case: `sql_type` to `datatype`, `targets`, `roles`, `extension_roles`, and `unique_keys` present and absent. | §6.3–§6.6; T1, T2 |
| O3 | OB4-C2 | Each unknown-name class (fact type, role, object type, table, column) is refused with exit 3 and a named rule id, in the pinned order | §6.7; T4, T5 |
| O4 | OB4-C3, D8 | Contradictions are refused, as D8 defines them | §6.7; T4 |
| O5 | OB4-C4 | Unbound fact types are listed with the binding's sha256 | §6.6; T6 |
| O6 | OB4-C5 | Without the flag, the output is unchanged | T7 |
| O7 | OB4-C6 (p1 F15) | Hostile-input and time-bound tests, plus hostile Unicode role names: compatibility forms, punctuation-only names, collisions | T8, T9, T10 |
| O8 | OB4-C7 (p1 F10) | A two-column FK gives one relationship with ordered columns. A mismatched group is refused. | §6.3; T3 |
| O9 | Plan §0 rule 1 | The reader is total over arbitrary JSON: the cap applies to the read; `NaN`, deep nesting and long integers are refused with a named reason | §6.2; T8 |
| O10 | Plan §0 rule 2 | A time bound at the reporter's scale; role-name matching is a hash lookup | T10 |
| O11 | Plan §0 rule 3 | One refusal order, pinned by a source-order assertion; the spec states where the binding is checked relative to the ontology projection | §6.7; T5 |
| O12 | Plan §0 rule 4 | The one walk over all fact types and all constraints is shared by the Rmap path and the binding path | §6.6; T6 |
| O13 | Plan §0 rule 5 | Normative prose in `representation-format.md` § "Ossie interchange"; the binding's JSON schema is a packaged artifact that section cites | §6.9 |
| O14 | Plan §2.1 | `--physical-binding` with `--ontology-only` is a usage error, exit 64 | §6.1; T5 |
| O15 | Plan §2.2 | The mapping's `GND` extension carries the binding sha256 | §6.6 |
| O16 | Plan §2.4 | The member table: tables, columns, `sql_type`, `targets`, `references`, `primary_key`, `unique_keys`, `roles`, `extension_roles`; role-name matching | §6.2–§6.5 |
| O17 | Plan §3 | Homes: `src/gnd/schema/physical-binding.schema.json`, `src/gnd/export/physical_binding.py`, `tests/test_physical_binding.py` | §6 |
| O18 | Plan §9 OB4 row | `uv run pytest -q tests/test_physical_binding.py tests/test_ossie_relational.py --tb=short`; affected consumers as OB3 | §8 gate |
| O19 | Plan §6 | Risks: normalized matching merges two roles; the schema hard-codes one producer's format | G8; G1, G2 |
| O20 | Plan "External acceptance" | The reporter's checks need their model and DDL. In-repo tests use a generated large model and a fixture binding shaped like DDL, composite FKs included. | T3, T10; §9 |
| O21 | OB3-Q6 | One fixture-model scan shared by the test files | G17 |
| O22 | OB3 residual E5 | Identifier spelling in expressions, now for names the caller chose | G11 |

## 4. Standing rules bound to this phase

| Rule | How it binds OB4 |
|---|---|
| 1 Totality | The binding is untrusted JSON. It is read through `input_policy.loads` with a byte cap, so non-finite numbers, nesting past 64 and oversized input are refused by name. Schema validation precedes every lookup, so later code never meets a wrong type. |
| 2 Cap bounds the document, not the algorithm | Every name is resolved through a dictionary built once. Role-name matching normalizes each name once and looks it up. T10 measures the growth ratio. |
| 3 Validation order | §6.7 pins one order. Each step's rule ids are listed there, and a test asserts the order from the source. |
| 4 One walk | The binding path fills the same `RelationalSchema` records the Rmap fills. `gnd.rmap.dispositions` then performs the walk for both paths and fails on a missing row. |
| 5 One home | The rules go in § "Ossie interchange", "Physical binding". The schema file is the packaged artifact the section cites; the section restates no member list. |
| 6 Measure | The size of a binding at the reporter's scale is measured and recorded, to check the 10 MiB cap (G6). |
| General solutions (AGENTS.md) | A `table.column` string is never split on a dot (G4). An SQL type is lexed by a stated grammar, not by a pattern over examples (G9). Names are quoted by OB3's one rule (G11). |

## 5. Goal

`gnd export ossie MODEL --out OUT --physical-binding FILE` writes the same
five files, but the semantic model describes the tables the caller actually
delivers, and the mapping maps the ontology onto those tables. The built-in
Rmap is not run. The ontology, sidecar and loss report are byte-identical to
a run without the flag.

## 6. Design

### Reuse

Searched with `scripts/components_index.py search` for "physical binding",
"bounded json read", "role name normalization" and "sql type".

| Capability | Found | Decision |
|---|---|---|
| Semantic-model and mapping documents, validation, encoding, the extension | `export.ossie_relational`, `export.ossie` | **reuse** unchanged: the binding path hands them a `RelationalSchema` |
| The relational records and the one walk | `model.relational_mapping`: `RelationalSchema`, `Table`, `RolePlacement`, `Identification`, `dispositions` | **reuse**; one field and three reasons are added (G12, G13) |
| Bounded, hostile-safe JSON read | `infra.input_policy` (`loads`), `infra.safe_filesystem` (`open_regular`) | **reuse** |
| How the ontology identifies each object type, and role order | `OntologyView` (OB3) | **reuse** |
| Role-name normalization | none (the model validator compares role names exactly) | **new**, in the binding module |
| SQL type lexing | none | **new**, in the binding module |
| A binding reader | none | **new**: `src/gnd/export/physical_binding.py` |

### 6.1 Command

- `--physical-binding FILE` is added to `gnd export ossie`.
- With `--ontology-only` it is a usage error, exit 64, before any read.
- A missing `FILE` exits 66, like a missing model.
- The five output names, the publication group, `--max-output-bytes` and
  the collision exit are OB3's, unchanged.

### 6.2 The document (`gnd-physical-binding/1`)

JSON only, read with a 10 MiB cap (G6). The packaged schema
`src/gnd/schema/physical-binding.schema.json` is closed
(`additionalProperties: false`) at every level.

```json
{
  "schema": "gnd-physical-binding/1",
  "tables": {
    "sales.state": {
      "columns": {
        "country_cd": {
          "sql_type": "CHAR(2)",
          "targets": [{"kind": "identifier", "object_type": "state"}],
          "references": {"table": "sales.country", "columns": ["cd"]}
        },
        "state_cd": {"sql_type": "VARCHAR(8)"}
      },
      "primary_key": ["country_cd", "state_cd"],
      "unique_keys": [["state_cd", "country_cd"]]
    }
  },
  "roles": {
    "state_in_country": {
      "state": [{"table": "sales.state", "column": "country_cd"},
                {"table": "sales.state", "column": "state_cd"}],
      "country": ["sales.state.country_cd"]
    }
  },
  "extension_roles": {}
}
```

| Member | Required | Rule |
|---|---|---|
| `schema` | yes | the constant `gnd-physical-binding/1` |
| `tables` | yes, at least one | keyed by table name, which may be schema-qualified |
| `tables.<t>.columns` | yes, at least one | keyed by column name; the document's member order is the field order (G3) |
| `columns.<c>.sql_type` | no | §6.4 |
| `columns.<c>.targets` | no | a list of `{kind: identifier, object_type}`, `{kind: reference, object_type}` or `{kind: role, fact_type, role}` (§6.5) |
| `columns.<c>.references` | no | `{table, columns}`: the foreign key this column belongs to (§6.3) |
| `tables.<t>.primary_key` | no | column names of the table, distinct |
| `tables.<t>.unique_keys` | no | lists of column names of the table |
| `roles` | yes (may be empty) | fact type id → role name → an ordered list of columns |
| `extension_roles` | no | the same shape as `roles` |

**A column reference** in `roles` is an object `{table, column}`, or the
string `table.column`. The string form is resolved by lookup, never by
splitting: the reader builds one dictionary from every declared
(table, column) pair to its `table.column` spelling, and a string names the
pair it equals. If two pairs spell the same string, the binding is refused
(`binding:ambiguous-column`), because a qualified table name can contain a
dot (G4).

### 6.3 From `tables` to the semantic model (OB4-C1, C7)

This step reads only the binding. It does not need the model.

| Binding | Semantic model |
|---|---|
| Table | One dataset, in sorted table-name order: `name` and `source` are the table name as written. Its `GND` extension is `{"source_kind":"physical"}`. |
| Column | One field in document order: `name` is the column name, `expression.sql` the quoted name (G11). |
| `sql_type` | `datatype` through §6.4, and the raw text in the field's `GND` extension as `{"sql_type": …}` |
| `primary_key`, `unique_keys` | `primary_key`, `unique_keys`. With no `unique_keys` member, they are derived (§6.6). |
| `references` | **The columns of one table whose `references` name the same table and the same column list form one foreign key**, ordered by each column's position in that list. Each gives one relationship, named by the Rmap's rule (`<from>__<to>`, numbered, unique in the schema). |

A `references` block is refused when:
- its group's size differs from the length of its column list, or two
  columns of the group claim the same position (`binding:reference-group`);
- its column list is neither the target table's `primary_key` nor one of its
  declared `unique_keys`, as a sequence (`binding:reference-not-a-key`).

### 6.4 SQL types (D7)

The closed map is over a **normalized type name**. A type is lexed as:
words of letters, digits and underscores, separated by spaces; at most one
parenthesized list of unsigned integers after any word. The name is the
words, casefolded and joined by one space. Anything else (an array suffix, a
quoted type, a second list) is not a known type.

| Ossie data type | Normalized names |
|---|---|
| `String` | `char`, `character`, `varchar`, `character varying`, `nchar`, `nvarchar`, `text`, `string`, `uuid` |
| `Integer` | `smallint`, `integer`, `int`, `bigint`, `tinyint`, `int2`, `int4`, `int8`, `serial`, `bigserial`, `long`, `short`, `byte` |
| `Decimal` | `numeric`, `decimal`, `dec`, `number` |
| `Float` | `real`, `float`, `float4`, `float8`, `double`, `double precision` |
| `Boolean` | `boolean`, `bool` |
| `Date` | `date` |
| `Time` | `time`, `time without time zone` |
| `DateTime` | `timestamp`, `timestamp without time zone`, `timestamp_ntz`, `datetime` |
| `DateTimeTz` | `timestamp with time zone`, `timestamptz`, `timestamp_ltz` |
| `Opaque` | `bytea`, `binary`, `varbinary`, `blob`, `json`, `jsonb` |

A type outside the map leaves `datatype` absent; it is never a refusal. The
raw `sql_type` is always kept in the field's extension.

### 6.5 From `roles` and `targets` to the mapping

This step needs the model and the ontology view.

- **Names.** Fact type ids, object type ids, table names and column names
  match exactly. **Role names** match after normalization (D8): NFKC, then
  `casefold()`, then every character outside Unicode general categories L*
  and N* is dropped. A role name that normalizes to nothing is refused, in
  the model's fact type or in the binding. Two role names of one fact type
  that normalize alike are refused, on either side.
- **A bound fact type** is one that `roles` names. Each of its roles must
  be bound (`binding:partial-fact-type` otherwise). Its roles' columns must
  lie in one table; if they do not, the fact type keeps no link mapping and
  is listed as `spans-tables` (G14).
- **The columns of a role.** A role played by a value type has one column. A
  role played by an entity type has one column per column of that entity's
  identification, **in the entity's identification order**: the ontology's
  `identify_by` order, an entity component expanded in turn. A wrong count
  is refused (`binding:role-arity`).
- **Home tables.** `targets` of kind `identifier` say whose rows a table
  holds. A table is the home of object type X when every column of its
  primary key carries `{kind: identifier, object_type: X}`. X then gets an
  object mapping over that primary key, built as in OB3 from the ontology's
  identifier. An object type with no home table gets none.
- **Checked targets.** A target of kind `role` must agree with `roles` or
  `extension_roles`: the column must be among that role's columns. A target
  of kind `reference` must sit on a column of some role that the named
  object type plays. A disagreement is a contradiction (§6.7). These two
  kinds add nothing beyond the check; `roles` is the authority (plan §2.4).
- **`extension_roles`** are resolved and checked exactly like `roles`. They
  produce no link mapping. They are listed, resolved, in the mapping's `GND`
  extension. A fact type bound only there is listed with the reason
  `extension-role` (G7).
- **Link mappings** are OB3's: one tree per bound fact type, under the
  concept that owns the relationship, a node per role in the relationship's
  order. `identification-differs`, `arity-over-limit` and the NULL reading
  apply unchanged. A unary fact type is bound to its player's key columns
  and has no flag, so every row is a link.

### 6.6 Dispositions and the extension (OB4-C4)

The binding path fills `RelationalSchema` and its carried and unmapped rows,
and `gnd.rmap.dispositions` walks them. A missing row fails the run.

| Element | Disposition |
|---|---|
| Fact type bound in `roles` within one table | carried: `columns`, the table, its role columns |
| Fact type bound in `roles` across tables | `spans-tables` |
| Fact type bound only in `extension_roles` | `extension-role` |
| Any other fact type | `unbound` |
| Confirmed alethic uniqueness (internal or external) whose roles are all bound in one table | `primary_key` when its columns are that table's primary key; `unique_key` when they are a unique key of the table; otherwise `not-in-binding` |
| Uniqueness that is not confirmed or not alethic | `uniqueness-not-confirmed` |
| A constraint of a fact type that is not carried | that fact type's reason |
| Every other constraint | `not-relational`, as under the Rmap |

**Derived unique keys.** When a table has no `unique_keys` member, each
confirmed alethic uniqueness whose roles are all bound to that table, and
whose columns are not its primary key, becomes a unique key, one per column
set, in table column order. When the member is present, nothing is derived.

**The extension.** `gnd-ossie-relational/1` gains, on a binding run only:

| Member | Value |
|---|---|
| `binding_sha256` | the bare hexadecimal SHA-256 of the binding file's bytes |
| `extension_roles` | the resolved entries: fact type, role, table and columns |

`rmap_variant` is absent on a binding run (G15). A run without the flag
writes exactly OB3's bytes.

### 6.7 Refusals and their order (OB4-C2, C3; plan §0 rule 3)

Every binding refusal exits 3 with its rule id on standard error, and
publishes nothing.

| Step | Rule ids |
|---|---|
| 1 Usage (exit 64) | `--physical-binding` with `--ontology-only`; an invalid `--max-output-bytes` |
| 2 Binding syntax | `binding:not-a-file`, `binding:size`, `binding:syntax` (malformed JSON, a non-finite number, nesting past the limit, a duplicate member name) |
| 3 Binding schema | `binding:schema`, with the JSON pointer of the first violation in sorted order |
| 4 Model | the existing model and include refusals, unchanged |
| 5 Names, in this order | `binding:name-collision`, `binding:unknown-table`, `binding:unknown-column`, `binding:ambiguous-column`, `binding:unknown-fact-type`, `binding:unknown-role`, `binding:unknown-object-type` |
| 6 Contradictions, in this order | `binding:role-name` (empty or colliding after normalization), `binding:reference-group`, `binding:reference-not-a-key`, `binding:partial-fact-type`, `binding:role-arity`, `binding:target-mismatch`, `binding:key-role`, `binding:incompatible-keys` |
| 7 Strict | the existing `--strict` refusals |
| 8 Size, then collision | `ossie:output-size` (exit 3); exit 11 |

- Steps 2 and 3 need no model, so they come before the model is read. Steps
  5 and 6 need the model and the ontology view, so the ontology is projected
  between steps 4 and 5; its own strict refusals still come after the
  binding's (step 7).
- Within a step, the first violation in sorted order of (table, column) or
  (fact type, role) is reported, so the message does not depend on the
  document's member order.
- **D8's four classes** map to: `binding:incompatible-keys` (a column bound
  to roles of two fact types that are each functional on different roles of
  the same table), `binding:reference-not-a-key`, `binding:key-role` (a
  primary-key column bound to a role that is not part of what identifies the
  table's home object type, when the table has one), and
  `binding:reference-group`.

### 6.8 Library surface

```python
# src/gnd/export/physical_binding.py
class BindingError(ValueError):       # .rule: the rule id
def read_binding(path: Path) -> Binding           # steps 2-3; total over arbitrary bytes
def bind(model, view: OntologyView, binding: Binding) -> RelationalSchema   # steps 5-6
```

`render_ossie` gains `physical_binding: Path | None = None`. With it,
`_relational` calls `bind` instead of `map_model`; the rest is shared.

### 6.9 Normative home

§ "Ossie interchange" gains "Physical binding": §6.2's semantics (citing the
schema file for the member list), §6.3–§6.7. OB5 writes the how-to with a
worked binding.

## 7. Decisions

| ID | Question | Proposal | What the other reading costs |
|---|---|---|---|
| G1 | **D10 first, or define the format now?** The reporter's document shape is known only from the issue's prose. | Define the GND-owned format now (D7 already rules it GND-owned). Ask the reporter in parallel; if their shape differs, a later revision adds what is needed. | Waiting blocks OB4 on an outside party. Proceeding risks a format the reporter must adapt to: a `schema` tag for certain, possibly more. |
| G2 | **Where `references` lives.** The issue lists it inside `targets`; plan §2.4 puts it on the column. | On the column (plan §2.4). A foreign key is a fact about the column, whatever it targets. | Inside `targets`, one column with two targets could carry two different foreign keys. |
| G3 | **`tables` and `columns` as objects keyed by name, or as lists.** | Objects keyed by name, as the issue's wording suggests. Field order is the document's member order; dataset order is sorted. A duplicate member name is refused. | Lists make order explicit but move every name into a `name` member, further from the issue's shape. |
| G4 | **Column references in `roles`.** | Accept `{table, column}` and the string `table.column`, resolved by lookup against the declared pairs; an ambiguous string is refused. | Splitting on the last dot mis-reads any column name that contains a dot. |
| G5 | **Format.** | JSON only. | YAML too adds a second hostile-input surface for no stated need. |
| G6 | **Size cap of the binding file.** | 10 MiB, fixed. T10 records the size of a binding at the reporter's scale; if it is close, a parameter goes to the owner. | A parameter now is a fifth flag with no measured need. |
| G7 | **`extension_roles`.** Its meaning is unknown (D10). | Resolve and check them like `roles`, write no link mapping for them, list them in the extension, and give a fact type bound only there the reason `extension-role`. | Treating them as `roles` would publish mappings whose meaning nobody has confirmed. |
| G8 | **Role-name matching** (D8, ruled). | As ruled: NFKC, casefold, keep L* and N*. Applied to role names only; every other name is exact. | — |
| G9 | **The SQL type map** (D7). | §6.4: PostgreSQL, Databricks and ANSI names; unknown types leave `datatype` absent. | Refusing an unknown type would refuse a schema for a column the mapping may not even use. |
| G10 | **`uuid`, `json`, `jsonb`.** | `uuid` is `String`; `json` and `jsonb` are `Opaque`. | Leaving them absent loses a type a consumer can use. |
| G11 | **Identifiers the caller chose** (O22). | Names are written as given in `name` and `source`, and quoted and uppercased in expressions, as in OB3. Two tables, or two columns of one table, that are equal after uppercasing are refused (`binding:name-collision`, first in step 5). A database that folds unquoted names to lowercase is a recorded residual. | Quoting names exactly as written would not match the regular identifiers in `name`, by Ossie's comparison rule. |
| G12 | **`source_kind`.** | `physical` on a binding run, `logical` otherwise. | — |
| G13 | **New reasons.** | Three, used only on a binding run: `unbound`, `extension-role`, `not-in-binding`. `UnmappedReason` gains them, and OB2's T8 is extended. | Reusing `not-relational` for an unbound fact type would hide the difference the issue asks to see. |
| G14 | **A fact type bound across tables.** | Listed as `spans-tables`, not refused: the data exists, but one row does not hold the link. | Refusing would reject a legitimate physical design. |
| G15 | **`rmap_variant` on a binding run.** | Absent; `binding_sha256` is present instead. | Writing `halpin` would claim a mapping that did not run. |
| G16 | **Branch base.** OB4 needs OB3, which is PR #271. | Draft and gate the spec and corpus now; implement on a branch cut from main after #271 merges. | As OB3's E1. |
| G17 | **OB3-Q6.** | Move the fixture-model scan into `tests/support/` and use it from the three test files. | — |
| G18 | **Approval instrument** (§11). | Corpus first: valid bindings with hand-derived expected files, and a refusal table with the expected rule id of each bad binding. | Prose only approves a serialized format, an exit-code contract and a set of validation predicates unseen, the three shapes `review-convergence.md` defaults to corpus first. |

## 8. Tests and corpus

### The corpus (authored first; G18)

Under `tests/fixtures/physical_binding/`.

**Valid cases**, each with `binding.json`, a hand-derived
`expected.semantic_model.yaml`, `expected.mapping.yaml`,
`expected.extension.json` and a `STORY.md`, over OB2 corpus models:

| Case | Model | Shows |
|---|---|---|
| V1 | 01 functional binary | renamed table and columns; `sql_type` to `datatype`; a home table; one link |
| V2 | 04 many-to-many | three tables; two single-column foreign keys; a schema-qualified table name |
| V3 | 14 external identification | a composite key; a **two-column** foreign key as one relationship (OB4-C7); nested referents over the caller's columns |
| V4 | 14 again | one fact type unbound, one in `extension_roles` only; `unique_keys` absent, so one is derived |
| V5 | 13 candidate keys | `unique_keys` present; a uniqueness the binding does not declare (`not-in-binding`) |
| V6 | 01 | role names matched through normalization (case, punctuation, a compatibility form); the string form of a column reference |

**Refusals**: `refusals.json`, a hand-written table. Each row is a small
edit of a valid binding, its expected rule id and its exit. One row at least
per rule id of §6.7 steps 2, 3, 5 and 6 (19 rule ids), and the hostile role names of
OB4-C6 (a compatibility form that collides, a punctuation-only name).

### Tests (`tests/test_physical_binding.py`)

| ID | Case | Expected |
|---|---|---|
| T1 | the valid corpus cases | equal to the expected files, byte for byte in YAML; the extension parses to its readable copy |
| T2 | every valid case | the pinned schemas accept both files; OB3's cross-checks and totality check hold; the three legacy files equal the run without the flag |
| T3 | V3, and V3 with one column of the group removed, and with the two positions swapped | one relationship with ordered columns; `binding:reference-group`; `binding:reference-not-a-key` |
| T4 | every row of `refusals.json` | its rule id on standard error, its exit, nothing published |
| T5 | pairs of defects from adjacent steps of §6.7 | the earlier step's rule id; plus a source-order assertion over the step functions; plus the two usage errors (exit 64) |
| T6 | V4; and a generated model with half its fact types bound | every fact type and constraint appears once; unbound ones carry `unbound`; `binding_sha256` equals the file's digest; `gnd.rmap.map_model` is not called |
| T7 | the OB3 corpus (T1 of OB3) and a digest baseline of the census, captured from OB3's code before any OB4 edit | byte-identical without the flag |
| T8 | hostile bindings: empty file, a directory, 10 MiB + 1, `NaN`, nesting past the limit, a 5,000-digit integer, a duplicate member, wrong types at every schema level (generated from the schema) | a `binding:` rule id each; never a traceback; never exit 70 |
| T9 | hostile role names: NFKC compatibility forms, punctuation-only, a collision created by normalization | matched, or refused with `binding:role-name` |
| T10 | a generated model and binding at 1,400 tables and 4,500 fact types, and at one fifth of that | a recorded time bound; ratio under 12; the binding's size recorded against the cap |
| T11 | §6.4 | every row of the type table; parameters and case ignored; an array type, a quoted type and an unknown word leave `datatype` absent; a literal copy of the table |
| T12 | the packaged schema | it is a valid Draft 2020-12 schema; it is closed at every level; its member names are exactly §6.2's |
| T13 | oracle lane (opt-in, named, not run by default) | the pinned validator accepts the valid cases' files |

**Gate:**
1. `uv run pytest -q tests/test_physical_binding.py tests/test_ossie_relational.py tests/test_ossie_export.py tests/test_rmap.py --tb=short`
2. the issue-171 guard list from `project.md`
3. `uv run ruff check`
4. `python3 scripts/components_index.py changed --base <phase base> --strict`

## 9. Out of scope for this phase

- Generating a binding from DDL, or DDL from a binding.
- A binding concept inside the model format (plan §7).
- YAML bindings; a size parameter for the binding (G5, G6).
- Nullability: the binding carries none, so `mandatory` stays
  `not-relational`.
- The reporter's external acceptance (their model and DDL are not here).
- The explanation, how-to, skill and release note (OB5).

## 10. Size

Estimate:
- `physical_binding.py`: about 450 lines;
- the schema file: about 120 lines;
- `ossie.py`, `commands/export.py`, `rmap.py`: about 60 lines;
- the normative subsection: about 110 lines;
- tests: about 500 lines;
- the corpus: 6 valid cases and a refusal table of about 30 rows.

## 11. Approval instrument

**Proposed: corpus first (G18).**

1. The valid cases, their stories and `refusals.json` are committed before
   any reader code.
2. The owner gates on the stories, the bindings and the refusal table.
3. The harness lands red.
4. Each implementation commit names the cases it turns green.

## 12. Implementation findings

None yet.

## 13. Amendment r1.1: rules settled while authoring the corpus (2026-11-24)

The owner approved r1 (sha256 `f79b3979…7b8a`; [gate](../013-OB4-spec-gate.md)) with
G1–G18 as proposed. Under G18, authoring the corpus came next. Writing the
bindings, their expected files and the refusal table by hand forced the
rules below, which r1 left open or got wrong. **They are unapproved**: the
owner sees them at the corpus gate, together with the stories in
[tests/fixtures/physical_binding](../../../../tests/fixtures/physical_binding/README.md)
and the format in
[physical-binding.schema.json](../../../../src/gnd/schema/physical-binding.schema.json).
§1–§12 are unchanged, except where a row says it supersedes them.

| # | Rule | Why | Case |
|---|---|---|---|
| K1 | **Foreign-key columns pair with `references.columns` in the table's column order.** This supersedes §6.3 and plan §2.4 ("each column's position in `references.columns`"). `binding:reference-group` is then a size mismatch only. | Every column of a group carries the same `references` block, so nothing in it says which referenced column a given column matches. | V3 |
| K2 | **`binding:role-name` moves into step 5, before `binding:unknown-role`.** This supersedes §6.7's step 6. | A role name that normalizes to nothing, or like another, cannot be looked up, so it has to be judged before the lookup. | refusals |
| K3 | **A home table's key columns match the identifier by role, not by position.** For a composite identifier, the column of each identifying relationship is the one its component role is bound to in the home table. | The primary key's column order need not be the ontology's `identify_by` order. | V3 |
| K4 | **`binding:key-role`, defined.** A primary-key column of a home table is bound to a role that is neither played by the home object type (or a subtype or supertype of it) nor a component of its identifier. | r1's wording, "a role that is not part of what identifies the home object type", would refuse the subject role of every ordinary fact type. | refusals |
| K5 | **`binding:incompatible-keys`, defined.** One column is bound, in `roles`, to roles played by two object types that are neither the same nor related by subtyping. | r1's wording could not be tested. A column holds objects of one type. | refusals |
| K6 | **Dispositions on a binding run.** A bound fact type is `columns`, its table, then the columns of its roles in role order, each once. A uniqueness is compared with the keys as a set of columns. A `unique_key` row lists its columns in table column order. | r1 named the outcomes, not their spelling. | all |
| K7 | **The extension on a binding run** always carries `extension_roles` and `concepts`, empty or not. `extension_roles` rows are `{fact_type, role, table, columns}`, with the model's role name, sorted by fact type and role. | A reader can tell a binding run by the members alone. | V4 |
| K8 | **A table's foreign keys are ordered by their first column's position.** Relationship names use the table names as written, dots included. | r1 left the order open. | V2 |
| K9 | **Seven valid cases, not six.** V4 shows the unbound and extension-only fact types. The derived unique key moved to a new V7, over model 13. This supersedes §8's table. | Model 14 has no uniqueness beyond its keys, so nothing could be derived in V4. | V4, V7 |
| K10 | **The refusal table's format**: 50 rows, each a `base` with an RFC 6902 `patch`, or `raw` text, or a `generate` kind. A 5,000-digit integer is `binding:syntax`, not `binding:schema`. | Measured: the existing reader refuses it while parsing. | refusals |
| K11 | **The schema file is written now**, at its packaged home, and is part of the corpus gate. It is the format, and the corpus is checked against it. | A valid binding cannot be told from an invalid one without it. | all |
| K12 | **Targets are optional everywhere.** A role is bound by `roles` alone; a `role` or `reference` target only has to agree when present. | V2 and V5 bind roles with no `role` target. | V2, V5 |
| K13 | **Known limit: surrogate keys.** A role played by an entity needs columns that hold the entity's identifying values. A table that points at another only through a generated id has none. That fact type then cannot be bound: left out, it is listed as `unbound`; bound to the id column, it is refused with `binding:role-arity`. Likewise a table whose primary key is a generated id is no object type's home, so that object type gets no object mapping. The foreign key itself still becomes a relationship. | Mapping through a join would need Ossie to define how an expression reaches a second dataset, which the pinned spec does not. Delivered schemas often use surrogate keys, so **this may matter to the reporter**: D10 should ask. | — |

**Authoring checks run (no reader exists):**
- The packaged schema is a valid Draft 2020-12 schema, and accepts the seven
  valid bindings.
- The pinned Ossie schemas accept all fourteen expected files, which were
  already in the exporter's YAML form as written.
- Each expected semantic model equals its binding's tables: names, sorted
  order, field order, keys, raw SQL types and foreign-key groups.
- Each expected mapping passes OB3's cross-checks against today's real
  ontology export, and lists every fact type and constraint of its model
  exactly once, with the carried fact types exactly the link-mapped ones.
- All 50 refusal rows are classified by step: the syntax rows do not parse
  with the existing bounded reader, the schema rows parse and fail the
  schema, and the other rows pass the schema.
- **The checker can fail.** Sixteen deliberate breakages of copied files
  were each caught.
- **Not checked, because it needs the reader:** the datatype each SQL type
  maps to, and which rule id each row of steps 5 and 6 actually produces.
