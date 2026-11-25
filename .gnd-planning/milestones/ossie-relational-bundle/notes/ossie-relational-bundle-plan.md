# Ossie relational bundle

**Status: r3, 2026-11-25: r2 with the close amendments of §11.** r2 (sha256
`52d946a48c7acd82562afbbd6a8057fe7da8a58bac328218c0a483eab13c6e1d`) was approved at the
[plan gate](../002-plan-gate.md) and is unchanged above §11, this status
paragraph apart. The r2 status text follows as written.

*r2, draft, 2026-11-24. Not approved.* r1 (sha256
`cdc1576f1f1d5f1b6a040b7eebed4f6e14b0d1c02097b73ad3680076fc40f44d`) was
reviewed by the maintained light panel at effort high on 2026-11-24:

- 4 of 6 seats succeeded (qwen and glm timed out).
- claude, codex and kimi asked for revision; gemini blocked.
- Finalization exited 0 ([report](../evidence/plan-review-r1/PANEL-REVIEW.md);
  run sha256 `c4276ed9…d0e5`).

The owner directed "Apply fixes as r2". r2 applies all 16 prioritized fixes,
each tagged `(p1 Fn)` with the fix's rank in the report. **r2 itself is not
reviewed.** No phase spec is approved and no code is written. `auto=false`. The
decisions in §10 are open. D1 reopens two rulings of the closed
ossie-interchange milestone and is the owner's to make before OB2 can be
specified.

Phase prefix `OB`. Inspection baseline: gnd-public main at `1926e895`
(2026-11-24). Vendored Ossie pins are as in `src/gnd/schema/ossie/PINNED.json`
(apache/ossie `ee89dbdc2844d8b7d293ed42c8613928bb99505f`, `0.3.0.dev0`).

`gnd export ossie` writes an Ossie ontology (layer 4) and two GND files: the
`.gnd.json` sidecar and the `.loss.json` report. This milestone does three
things:

1. It makes the output size bound a parameter, so large models can export.
2. It adds Ossie's relational layer next to the ontology: a **semantic model**
   (datasets, fields, keys, relationships), produced by a new Halpin Rmap, and
   a **mapping** document from concepts and roles to datasets and fields.
3. It lets a caller bind that relational layer to a physical schema they
   deliver, through a binding file. The built-in Rmap is then not used.

## Completion predicates

The milestone is complete when, on main after merge:

1. **Size bound.** `gnd export ossie MODEL --out OUT --ontology-only` writes
   the same three files, byte for byte, as `1926e895` for every model in the
   export census, and exits with the same code. With `--max-output-bytes N`,
   an export whose largest artifact is above 10 MiB and at most N publishes
   all of its files. An export whose largest artifact is above N is refused
   with `ossie:output-size`, exit 3, and nothing is published (OB1-C1..C3).
   This holds for sources within the export's source cap. Whether that cap
   also becomes a parameter is D11 `(p1 F8)`.
2. **Default run, by D2 `(p1 F2)`.**
   - Under D2 (a), a run with no new flag writes the same three files
     byte-identically, plus `OUT.semantic_model.<fmt>` and
     `OUT.mapping.<fmt>`. Its only new failure is a collision on those two
     paths, exit 11.
   - Under D2 (b), a run with no new flag is identical to today in every
     respect, and `--relational` writes the five files (OB3-C5).
3. **Rmap.** A deterministic Halpin Rmap (`gnd.rmap`) returns a relational
   schema for **every model the ontology export admits**. A fact type or
   constraint the rules cannot place is listed as unmapped with a closed
   reason, so the Rmap itself never refuses a model `(p1 F12)`. Its normative
   rules, including every tie-break in §2.3, have one home (OB2-C1..C5).
4. **Relational files.**
   - The semantic model and mapping validate with 0 errors against the
     pinned core-spec and the pinned `ontology/mapping.json`. The ontology
     still passes too, and all three pass the upstream validator in the
     opt-in oracle lane.
   - Every fact type and every constraint is carried (as a dataset, field,
     key or relationship) or listed under the mapping's `GND` custom
     extension `(p1 F14)`.
   - Two runs give identical bytes (OB3-C1..C6).
5. **Physical binding.** `--physical-binding FILE` replaces the Rmap with a
   caller's column map under a GND-owned JSON schema.
   - Every member the issue names is consumed under a stated rule:
     `tables`, `columns`, `sql_type`, `targets`, `references`,
     `primary_key`, `roles` and `extension_roles` `(p1 F7)`.
   - Each foreign key gives exactly one relationship, composite keys
     included `(p1 F10)`.
   - A binding that names an unknown fact type, role, object type, table or
     column is refused before anything is published.
   - Unbound fact types are listed in the `GND` extension with the binding's
     sha256.
   - Without the flag the output does not change (OB4-C1..C7).
6. **Docs.** The normative section "Ossie interchange" in
   `gnd-orm-core/references/representation-format.md`, the export skill, the
   Ossie explanation and the how-to describe all of the above. No second
   home states a rule (OB5).

## 0. Binding design rules

The six paid-for rules of `.codex/skills/process-phase/references/project.md`
bind every phase. Where each one bites in this milestone:

| Rule | Where it applies here |
|---|---|
| 1 Totality | The binding-file reader (OB4) is a new consumer of untrusted JSON. It is total over arbitrary JSON: the cap applies to the read, `NaN`, deep nesting and long integers are refused with a named reason, and it has a hostile-input test. The `--max-output-bytes` and `--max-input-bytes` arguments (OB1) are validated as bounded positive integers at the CLI boundary. A bad value exits 64 (`EXIT_USAGE`) `(p1 F1)`. |
| 2 Cap bounds the document, not the algorithm | Raising the output bound admits larger outputs. The Rmap (OB2), the mapping walk (OB3) and the binding resolution (OB4) each get a time-bound test on a generated model at the reporter's scale (about 1,400 tables and 4,500 fact types). Role-name matching (OB4) is a hash lookup, not quadratic in roles per table. |
| 3 Validation order | OB4 pins one refusal order by source-order assertion: binding syntax, schema, unknown names, contradictions, then output size. Usage errors (exit 64) come before any read. Each spec states whether the binding is checked before or after the ontology projection. |
| 4 One walk over N kinds | One walk over all fact types **and all constraints** enforces "carried or listed in the GND extension". The Rmap path (OB3) and the binding path (OB4) share it `(p1 F14)`. |
| 5 One home | Normative prose for the Rmap, the semantic model, the mapping and the binding lives in `representation-format.md` § "Ossie interchange". The binding's JSON schema is a packaged artifact that section cites. The vendored `mapping.json` is a pinned copy held identical by a digest test, which counts as one artifact under the rule's scope note. |
| 6 Measure | OB2 implements both Rmap variants behind an internal switch. It measures them over the census and the OB2 fixture corpus with named metrics, and D5 is ruled from that result inside OB2 `(p1 F4)`. OB1 measures the output-to-source size ratio `(p1 F8)`. |

## 1. Scope, sources and authority

### 1.1 Sources

| ID | Source | Requests |
|---|---|---|
| I1 | Owner's issue file, 2026-11-24, issue 1 (not filed on GitHub at r2) | Parameterize the 10 MiB output bound (`--max-output-bytes N`). 10 MiB stays the default, with no change. Apply it equally to the ontology and both sidecars. Test both cases. |
| I2 | Same file, issue 2 | Write `OUT.semantic_model.<fmt>` (Rmap) and `OUT.mapping.<fmt>`, validated against pinned core-spec and `ontology/mapping.json` at `ee89dbd`. List unrepresentable constructs in a `GND` custom extension. `--ontology-only` keeps today's three files. Output must be reproducible. Decide the UNIQUE gap and the `sample_population` behaviour. |
| I3 | Same file, issue 3 | `--physical-binding FILE`: a column-map document under a JSON schema shipped in GND, carrying tables, columns (`sql_type`, `targets`, `references`), `primary_key`, `roles` and `extension_roles`. Role names match ignoring case and punctuation. Unknown names are refused. Unbound fact types are listed with the binding's sha256. Output is unchanged without the flag. Depends on I2. |
| P1 | ossie-interchange plan r3 §10, OD1 and OD3; [close](../../ossie-interchange/034-milestone-close.md) | OD1 ruled "ontology layer only". OD3 (physical bindings) ruled "not now", noting that a binding concept in the model would be a model-format change and its own milestone. |
| P2 | `representation-format.md` § "Ossie interchange" (line 2032 at baseline) | The current normative export contract: three artifacts; loss report `gnd-ossie-loss/1`; sidecar `gnd-ossie-sidecar/1`; populations refused as `population:out-of-scope`; include-bearing models refused with `include:unsupported-route`. |
| R1 | [Panel report on r1](../evidence/plan-review-r1/PANEL-REVIEW.md) | 7 agreed concerns, 9 divergent views, 16 prioritized fixes. All 16 are applied here. |

The reporter's three local commits (`03e690c2`, `1fea51f5`, `d7fe319c`) are
not in any repository on this machine. If the owner supplies their diffs,
they are reference material for a spec, not evidence and not reviewed code
(D10).

Public text in this repository names no downstream project or customer. The
reporter's case is described here as "a large composed model": 1,410 tables,
4,466 fact types, about 32 MiB of output, 2,269 relationships and about 260
UNIQUE constraints.

### 1.2 Observed at baseline (not inherited claims)

All four successful panel seats confirmed the claims in this section against
the code (R1).

- **Issue 1 is a refusal, not a truncation.** `render_ossie`
  (`src/gnd/export/ossie.py`, end of file) builds all three artifacts in
  memory. If any one exceeds `gnd.input_policy.MAX_BYTES` (10 MiB), it raises
  `OssieInputError("ossie:output-size")`. The command maps that to exit 3 and
  publishes nothing. No test covers this branch.
- `MAX_BYTES` is the shared **input** cap of `gnd.input_policy`. The export
  reuses it as an output bound. Changing the constant would change every
  input boundary in GND, so OB1 adds a separate parameter.
- **`gnd import ossie` has five 10 MiB-scale caps, not one** `(p1 F5)`:
  1. `_read` reads at most `MAX_BYTES` and refuses `<rule>-size`
     (`src/gnd/ossie_import.py:66`, `:78`).
  2. `_parse` calls `guard_yaml(data)` with its default `max_bytes=MAX_BYTES`.
  3. JSON input goes through `input_policy.loads`, whose `_text` checks
     `MAX_BYTES` with no parameter.
  4. `_bounded_model` refuses `model-size` at `MAX_BYTES` (line 329).
  5. The import loss report is capped at `2 * MAX_BYTES` (`loss-size`, line
     642).

  After those, the restored model is parsed under `MAX_MODEL_BYTES`. A
  document exported above 10 MiB therefore cannot be imported back today.
- **The export source cap** `(p1 F8)`. The source must be a standalone model
  of at most `MAX_MODEL_BYTES` (10 MiB, `ossie.py:73`), and an
  include-bearing model is refused. So OB1 fixes issue 1 only for sources
  within that cap. Whether the reporter's flattened model is within it is
  not known (D10), and D11 decides whether to raise it.
- **GND has no relational mapping today.** The component index
  (`scripts/components_index.py search relational`) and `src/gnd` contain no
  Rmap, no DDL writer and no table concept. OB2 is new code.
- **What the vendored `core-spec.json` requires:**
  - `Dataset` requires `name` and `source` (a physical table, view or query)
    and carries `primary_key` and `unique_keys` (an array of field lists)
    `(p1 F11)`.
  - `Relationship` requires `name`, `from`, `to`, `from_columns` and
    `to_columns`.
  - `Field` requires `name` and `expression`; `datatype` is optional.
  - Every level carries `custom_extensions`.
  - **The UNIQUE gap that I2 names is therefore representable** (D4).
- `ontology/mapping.json` is not vendored. `PINNED.json` names only
  `ontology.json` and the core reference.
- Exit bands (`src/gnd/exits.py`) `(p1 F1, F3)`: usage errors exit 64
  (`EXIT_USAGE`; argparse's 2 is remapped because 2 means "vacuous");
  collisions exit 11 (`EXIT_COLLISION`); refusals exit 3.
- The model identity (`gnd.values.model_identity`) is computed over the
  loaded model. Whether a `sample_population` changes it is to be measured
  in OB3. D6's equality claim is scoped so as not to depend on the answer
  `(p1 F13)`.

### 1.3 Authority

Writing this plan is not approval. The owner approves the plan at a plan
gate (record `001-plan-gate.md`) and each phase spec at its own gate before
any code. Merge, publication and any upstream contribution keep their
separate authorization.

## 2. Contract proposal and product behaviour

### 2.1 Command surface (proposal)

```text
gnd export ossie MODEL --out OUT
    [--format yaml|json] [--loss-report PATH] [--strict]        # existing
    [--max-output-bytes N]                                       # OB1
    [--ontology-only]          # OB3; under D2 (a)
    [--relational]             # OB3; under D2 (b) instead of --ontology-only  (p1 F2)
    [--physical-binding FILE]                                    # OB4
gnd import ossie DOC --out MODEL [--max-input-bytes N]           # OB1, D3
```

- `--max-output-bytes N` is a positive integer, default `10485760`, with an
  upper limit set by D3 (proposed 268435456, i.e. 256 MiB). It applies to
  **each** artifact the run writes: the ontology, sidecar and loss report,
  and from OB3 the semantic model and mapping. If any artifact is above N,
  the whole run is refused with `ossie:output-size`, exit 3, and nothing is
  published. This keeps today's all-or-nothing behaviour. It never
  truncates.
- `--max-input-bytes N` on import uses the same bounds and validator.
  Section 6.3 of the OB1 spec says which of the five import caps it moves
  `(p1 F5)`.
- An invalid N is a usage error: **exit 64**, before any read `(p1 F1)`.
- D2 selects exactly one of `--ontology-only` and `--relational`; the other
  is not added.
- `--physical-binding` is a usage error (exit 64) when no relational files
  are written: with `--ontology-only` under (a), or without `--relational`
  under (b).

### 2.2 Output files (OB3/OB4 proposal)

| File | Schema | Bound to |
|---|---|---|
| `OUT` | Ossie `ontology/ontology.json` (pinned) | (unchanged) |
| `OUT.gnd.json` | `gnd-ossie-sidecar/1` | ontology sha256 (unchanged) |
| `OUT.loss.json` | `gnd-ossie-loss/1` | ontology sha256 (unchanged) |
| `OUT.semantic_model.<fmt>` | core-spec `SemanticModel` (pinned) | nothing model-dependent beyond its structure: no identity, no digest `(p1 F13)` |
| `OUT.mapping.<fmt>` | `ontology/mapping.json` (pinned, newly vendored) | In its `GND` custom extension: ontology sha256, semantic-model sha256, model identity, and the binding sha256 when present |

Publication stays one create-once group through `safefs.publish_new_files`,
with the ontology written last as the commit marker, as today. A collision
on any path exits 11 and publishes nothing `(p1 F3)`.

### 2.3 Rmap semantics (proposal; OB2 fixes them, D5 rules the variants)

**Placement**, applied to each fact type in a fixed precedence `(p1 F9)`:

1. **Unary** fact type: a Boolean field in its player's table `(p1 F6)`.
2. **Functional** (some uniqueness spans exactly one role of a binary, or
   n−1 roles of an n-ary whose remaining role's player is an entity): grouped
   into the table of the entity playing the determining role(s). A spanning
   uniqueness implied by a shorter one never triggers rule 4.
3. **1:1 binary** (a single-role uniqueness on each role) `(p1 F6)`:
   - One role mandatory: absorbed into the table of that role's player.
   - Both roles mandatory, or neither: absorbed into the table of the player
     whose object-type id sorts first (the variant D5 measures). The other
     role's column becomes a `unique_keys` entry.
4. **Otherwise**: its own table, keyed on its shortest uniqueness (ties by
   constraint id).

**Identification and keys** `(p1 F6)`:
- Reference modes become key columns. A compound preferred reference scheme
  becomes a composite key, and every reference to that entity becomes a
  composite foreign key.
- **Primary key**: the entity's preferred identifier when the table belongs
  to an entity. Otherwise the shortest confirmed alethic uniqueness, with
  ties broken by constraint id.
- Every other confirmed alethic uniqueness whose roles all map to columns of
  one table becomes a `unique_keys` entry (D4). One spanning several tables
  is listed in the `GND` extension.

**Subtypes**: absorbed into the supertype table unless the subtype has its
own preferred identification. D5 measures the separate-table variant.

**Objectification**: an objectified fact type becomes a table keyed by its
uniqueness.

**Relationships**: one per foreign key, named
`<from_table>__<to_table>[__<n>]` deterministically, with ordered composite
columns.

**Required core-spec members** `(p1 F11)`:
- `Dataset.source` is the table name. The GND extension marks it
  `"source_kind": "logical"`, so no physical location is claimed.
- `Field.expression` is an ANSI SQL expression naming the column.
- `Field.datatype` follows a closed map from GND value primitives to core-spec
  data types. A primitive outside the map leaves `datatype` absent, and the
  extension carries the source type.

**Determinism and totality** `(p1 F12)`: the output depends only on the
model's content, never on declaration order or path. A fact type or
constraint that no rule places is listed as unmapped with a closed reason.
There is no model-level refusal.

**Populations** (D6): `sample_population` and `reference_populations` stay out
of every relational file and keep their `population:out-of-scope` refusal in
the loss report.

**Unrepresentable constructs** are listed in the mapping's `GND` extension
by fact-type or constraint id with a closed reason. These are mandatory
(NOT NULL), value constraints, frequency, ring, subset, exclusion,
derivations, deontic rules, and uniqueness spanning tables. Nothing is
dropped silently `(p1 F14)`.

### 2.4 Binding semantics (proposal; OB4 fixes them) `(p1 F7, F10)`

| Binding member | Use |
|---|---|
| `tables.<t>` | One dataset, `name = source = t` as written, which may be schema-qualified. |
| `columns.<c>` | One field, with `expression` set to the column name. |
| `columns.<c>.sql_type` | `Field.datatype` through a closed SQL-type map (D7). The raw `sql_type` is kept in the field's `GND` extension. A type outside the map leaves `datatype` absent. |
| `columns.<c>.targets[]` | Mapping entries: `kind` selects a fact-type role, an object-type identifier, or a reference. `fact_type` and `object_type` must resolve. |
| `columns.<c>.references {table, columns}` | Foreign key. **The columns of one table whose `references` blocks are equal form one foreign key**, ordered by each column's position in `references.columns`. The group's size must equal `len(references.columns)`; otherwise the binding is refused. |
| `primary_key` | `Dataset.primary_key`; each name must be a column of the table. |
| `unique_keys` (optional) | `Dataset.unique_keys`. When absent, it is derived from the model's uniqueness constraints whose roles all bind to one table's columns. |
| `roles` | `fact_type → role → [table.column]`, the authoritative role-to-column mapping. |
| `extension_roles` (optional) | Same shape and the same resolution rules as `roles`. Its entries are kept apart in the mapping's `GND` extension. Its intended meaning is confirmed with the reporter (D10). |

**Role-name matching** (D8) `(p1 F15)`: names are compared after NFKC
normalization, then `casefold()`, then dropping every character outside
Unicode general categories L* and N*. A role name that normalizes to the
empty string is refused. A fact type whose role names collide after
normalization is refused.

## 3. Dependencies and artifact homes

```text
OB1 (needs D3) ─────────────────────────────┐
OB2 (needs D1; rules D5 inside) → OB3 → OB4 → OB5 → close
```

OB1 and OB2 are independent and can run in parallel. OB5 also documents OB1.
D5 no longer blocks OB2: OB2 produces its evidence `(p1 F4)`.

| Artifact | Home |
|---|---|
| Output and input bounds | `src/gnd/export/ossie.py` (`render_ossie(..., max_output_bytes=)`), `src/gnd/commands/export.py`, `src/gnd/ossie_import.py`, `src/gnd/commands/checking.py`, `src/gnd/input_policy.py` (`loads(..., max_bytes=)` with the current default) |
| Rmap | new `src/gnd/rmap.py`, assigned in `tools/gnd_layers.json` and `dev/components/` |
| Semantic model and mapping renderers | new `src/gnd/export/ossie_relational.py` |
| Vendored mapping schema | `src/gnd/schema/ossie/mapping.json`; `PINNED.json` gains its path and sha256 |
| Binding schema | new `src/gnd/schema/physical-binding.schema.json` (schema id `gnd-physical-binding/1`, D7) |
| Binding reader | new `src/gnd/export/physical_binding.py` |
| Normative text | `src/gnd/skills/gnd-orm-core/references/representation-format.md` § "Ossie interchange" |
| User docs | `docs/explanation/ossie.md`, `docs/how-to/share-an-ossie-ontology.md`, `src/gnd/skills/gnd-export/SKILL.md` |
| Tests | `tests/test_ossie_export.py` and `tests/test_ossie_import.py` (OB1); new `tests/test_rmap.py`, `tests/test_ossie_relational.py`, `tests/test_physical_binding.py`; oracle-lane additions in `tests/test_ossie_external_oracle.py` |

## 4. Phases

### OB1: size bounds

**State:** draft [spec](phase-OB1-spec.md). Blocked on the plan gate and D3
`(p1 F16)`.

**Deliverable:**
- `--max-output-bytes N` on `gnd export ossie`, applied to each artifact.
- Under D3 (b), `--max-input-bytes N` on `gnd import ossie`, threaded through
  the caps it moves.

**Criteria:**
- **C1** `--ontology-only`-equivalent output (today's command) is
  byte-identical on the census.
- **C2** A generated model whose largest artifact is above 10 MiB exports
  completely with `--max-output-bytes 33554432` (exit 0). The output-to-source
  ratio is recorded `(p1 F8)`.
- **C3** Output above N is refused with `ossie:output-size`, exit 3, and
  nothing is published, including when each artifact in turn is the largest.
- **C4** Invalid N exits 64 `(p1 F1)`.
- **C5** A time bound for the large export.
- **C6** (D3 b) The C2 document imports with `--max-input-bytes`. A document
  above 10 MiB is tested at each moved cap (read, YAML guard, JSON
  `loads`, loss-size), and the kept `model-size`/`MAX_MODEL_BYTES` cap is
  tested too `(p1 F5)`.

### OB2: Rmap library

**State:** blocked on D1 only `(p1 F4)`.

**Deliverable:** `gnd.rmap`, a deterministic Halpin Rmap from a loaded model
to an internal relational schema: tables, columns, PK, unique keys, ordered
composite FKs, and the unmapped list with reasons. It implements both D5
variants behind an internal switch. There is no CLI change. Its normative
rules have one home.

**Criteria:**
- **C1** Every census model yields a schema with no model-level refusal
  `(p1 F12)`.
- **C2** Hand-derived expected schemas for a fixture corpus are committed
  before the code. It holds one fixture per rule and tie-break:
  - compound uniqueness; functional grouping; a fact type with both a
    single-role and a compound uniqueness `(p1 F9)`;
  - 1:1 with one, both and neither role mandatory `(p1 F6)`;
  - unary;
  - several candidate keys `(p1 F6)`;
  - compound preferred reference with a composite FK;
  - subtype absorbed and separate; objectification; n-ary.
- **C3** Determinism across source paths and declaration order.
- **C4** A time bound at 1,400 tables and 4,500 fact types.
- **C5** D5 measurement `(p1 F4)`. Both variants run over the census and
  the corpus. Recorded per variant: tables, unmapped fact types, FKs, and
  agreement with the C2 answer key. The owner rules D5 at a gate inside OB2
  before OB2 is recorded.

### OB3: relational files

**State:** blocked on OB2, D2, D4 and D6.

**Deliverable:** semantic-model and mapping renderers, the vendored
`mapping.json`, the `GND` extension, and the default per D2: either
`--ontology-only`, or `--relational`.

**Criteria:**
- **C1** 0 schema errors in-process against the pinned schemas.
- **C2** The upstream validator accepts all three files in the opt-in
  oracle lane.
- **C3** One walk confirms that every fact type **and every constraint** is
  carried or listed with a closed reason `(p1 F14)`.
- **C4** Byte reproducibility.
- **C5** Predicate 2 for the D2 ruling `(p1 F2)`: under (a), the three legacy
  files are byte-identical to baseline and a collision exits 11; under (b),
  no flag is byte-identical in every respect.
- **C6** `--max-output-bytes` covers the new files.
- **C7** D6 `(p1 F13)`: the semantic model, and the mapping minus its `GND`
  extension binding fields, are byte-identical with and without a
  `sample_population`. The expected differences in the loss report and the
  mapping's identity field are asserted, not ignored.

### OB4: physical binding

**State:** blocked on OB3, D7 and D8.

**Deliverable:** `--physical-binding FILE`: the schema, a total reader, name
resolution, normalized role matching, the refusal order, and the
unbound-fact-type listing with the binding's sha256.

**Criteria:**
- **C1** A valid binding replaces datasets, fields, PKs, unique keys and
  relationships. Every §2.4 member has a case: `sql_type` to `datatype`,
  `targets`, `roles`, `extension_roles`, and `unique_keys` present and absent
  `(p1 F7)`.
- **C2** Each unknown-name class (fact type, role, object type, table,
  column) is refused with exit 3 and a named rule id, in the pinned order.
- **C3** Contradictions are refused, as D8 defines them.
- **C4** Unbound fact types are listed with the binding's sha256.
- **C5** Without the flag, the output is unchanged.
- **C6** Hostile-input and time-bound tests, plus hostile Unicode role names:
  compatibility forms, punctuation-only names, collisions `(p1 F15)`.
- **C7** A two-column FK gives one relationship with ordered columns. A
  mismatched group is refused `(p1 F10)`.

### OB5: docs and skill

**State:** after OB4.

**Deliverable:** the normative section, the explanation, the how-to (a
worked relational export and a binding), the export skill guidance, and a
changelog entry. The changelog states exit 11 and exit 64 by their
constants.

**Criteria:** the docs build and the link check passes, and the normative
section is the only home (the reviewer checks every cited rule).

### close

**State:** after OB5.

**Deliverable:** the close record `NNN-milestone-close.md`, on merged main.

**Criteria:** every predicate is re-run on main, and the panel runs at the
project's close bar.

### Residuals and external acceptance

Inherited residuals: ossie-interchange predicate 5 (round trip) holds for
documents within the import caps. OB1 under D3 (b) extends it to large
documents. ossie-interchange OD1 and OD3 are superseded only if the owner
rules D1.

**External acceptance.** The reporter's checks need their model and DDL,
which are not in this repository. Those checks are: datasets equal the
delivered DDL, relationships equal the DDL foreign keys, and the 1,410/2,269
counts. In-repo tests use a generated large model and a fixture binding
shaped like DDL, composite FKs included. The close record cites the
reporter's own run as external evidence only if the owner supplies it, and
labels it as such.

## 5. Documentation, skill and compatibility surfaces

- **Compatibility.** The existing three files keep their schemas
  (`gnd-ossie-sidecar/1`, `gnd-ossie-loss/1`).
  - Under D2 (a), a default run writes five files. A caller whose
    `OUT.semantic_model.*` or `OUT.mapping.*` already exists gets **exit 11**
    (`EXIT_COLLISION`) where today's run succeeded `(p1 F3)`. This goes in
    the changelog, and it is why D2 is an owner ruling.
  - Under D2 (b), nothing changes without `--relational`.
  - The Rmap never refuses a model `(p1 F12)`, so collision is the only new
    default-path failure.
- **Disclosure table.** The new files carry model literals (names,
  descriptions), so they are classed like the existing Ossie surfaces
  (`every-mode`, RN0-K1). `tests/test_disclosure_mode.py` and
  `tests/test_disclosure_docs.py` are in each phase's guard gate.
- **Pins.** `PINNED.json` gains the `mapping.json` entry. The pin test is
  extended, not duplicated.

## 6. Risks and required controls

| Risk | Control |
|---|---|
| Rmap choices differ from the reporter's DDL, so their bundle changes when they move to upstream | D5 is measured over the census and fixtures. OB4 exists so that a delivered schema wins over the Rmap. |
| A 256 MiB ceiling lets one run use several hundred MiB of memory, because artifacts are built in memory | The D3 ceiling. OB1's large-model test measures and records time and memory. Streaming is out of scope. |
| The source cap still blocks the reporter after OB1 `(p1 F8)` | OB1 records the output-to-source ratio. D10 asks the reporter's source size. D11 decides on a parameter. |
| The default change (D2 a) breaks scripts that rely on three files | The changelog, the opt-out flag, and an explicit collision exit 11. |
| Normalized role matching merges two distinct roles | D8 pins NFKC, casefold and the L*/N* class, and refuses empty names and collisions `(p1 F15)`. |
| A consumer reads the logical `Dataset.source` as a real table | The `source_kind: logical` marker, and the docs `(p1 F11)`. |
| The binding schema hard-codes one producer's format | D7: a GND-owned schema id. The issue's member names are kept, so the reporter's documents need only a schema tag. |

## 7. Out of scope

- DDL generation (`CREATE TABLE`) from the Rmap. The semantic model is the
  deliverable; a DDL writer is a separate request.
- Importing a semantic model or mapping. `gnd import ossie` stays
  ontology-only.
- A binding concept inside the model format (the OD3 alternative).
- Streaming or chunked output.
- Exporting include-bearing models directly. They remain refused, as today.
- Ossie metrics, dimensions and AI context.
- Upstream contributions to apache/ossie.

## 8. Execution, approval and review protocol

- `auto=false`. Each phase follows process-phase in this order:
  1. spec, then the owner gate;
  2. implementation;
  3. focused tests, plus the issue-171 guard list, plus `uv run ruff check`;
  4. independent review (one reviewer in a different tool);
  5. refactoring review;
  6. record `NNN-phase-OB<n>.md` and a commit with scope `phase-OB<n>`.

  OB2 has one internal owner gate, for D5.
- Plan review: the light panel reviewed r1 (R1). r2 is not reviewed. The
  owner decides whether r2 needs a second round or goes to the plan gate as
  is (D9).
- Branch and PR per AGENTS.md. Before each PR, run
  `python3 scripts/components_index.py changed --base main --strict`.

## 9. Per-phase verification story and affected consumers

| Phase | Focused gate (plus the guard list and ruff) | Affected consumers |
|---|---|---|
| OB1 | `uv run pytest -q tests/test_ossie_export.py tests/test_ossie_import.py --tb=short` | `commands/export.py`; `commands/checking.py` (the import CLI); `input_policy.loads` callers (default unchanged); disclosure tables |
| OB2 | `uv run pytest -q tests/test_rmap.py --tb=short` | `tools/gnd_layers.json`, the component index |
| OB3 | `uv run pytest -q tests/test_ossie_export.py tests/test_ossie_relational.py --tb=short`. The opt-in oracle lane is named, not run by default. | Ossie docs, disclosure tables, the `PINNED.json` test |
| OB4 | `uv run pytest -q tests/test_physical_binding.py tests/test_ossie_relational.py --tb=short` | as OB3 |
| OB5 | the docs link check named in the OB5 spec | the site |

Baseline expectations: today's census export is the byte reference for
OB1-C1 and OB3-C5. It is captured at OB1 start from `1926e895` and committed
as digests only.

## 10. Owner decisions and open questions

All open at r2.

| ID | Question | Proposal | Cost of the alternative |
|---|---|---|---|
| D1 | Reopen ossie-interchange OD1 ("ontology only") and OD3 ("physical bindings not now") to take issues 2 and 3? | Yes: OD1 (b), and OD3 through an **external** binding file, which needs no model-format change. | Not reopening leaves only OB1 in this milestone. |
| D2 | Default output: (a) five files by default with `--ontology-only` to opt out, as the issue requests; or (b) three files by default with `--relational` to opt in `(p1 F2)`. | (a). With a total Rmap `(p1 F12)`, the only new default failure is a collision (exit 11). | (a) Scripts that expect three files, or that already own those two paths, change behaviour. (b) The reporter must add a flag. Predicate 2 and OB3-C5 follow the ruling. |
| D3 | The ceiling for `--max-output-bytes`, and the import side: (a) the export flag only, or (b) the export flag plus `--max-input-bytes` on `gnd import ossie` in OB1. | Ceiling 256 MiB, and (b). It moves the read, YAML guard, JSON `loads` and loss-size caps, and keeps the restored model under `MAX_MODEL_BYTES` `(p1 F5)`. | Without the import flag, large documents export but cannot round-trip. |
| D4 | UNIQUE constraints in the semantic model. | Write non-primary confirmed alethic uniqueness within one table as `Dataset.unique_keys`. Uniqueness spanning tables goes in the `GND` extension. | Leaving them out keeps the ~260-constraint gap the issue reports. |
| D5 | Rmap variants: the subtype mapping (absorb or separate) and the symmetric 1:1 direction. | Ruled inside OB2 from the OB2-C5 measurement `(p1 F4)`. Proposed defaults are Halpin's (absorb; first id). | A per-run policy flag adds a test matrix. |
| D6 | Behaviour with `sample_population`. | No rows in any relational file, and the existing loss-report refusal stays. The semantic model, and the mapping without its binding fields, are byte-identical with and without a population. The loss report and the mapping's identity may differ, and OB3-C7 asserts how `(p1 F13)`. | Emitting rows belongs to a different Ossie layer and is out of scope. |
| D7 | Binding schema identity and the SQL type map. | A GND-owned `gnd-physical-binding/1`, with the issue's member names (§2.4), and a closed SQL-type map to core-spec data types. | A producer-named schema id ties GND's public schema to one caller. |
| D8 | Role-name normalization and contradictions. | NFKC, then casefold, then keep only Unicode L* and N*. Refuse empty results and collisions `(p1 F15)`. Contradictions are: a column targeting two fact types with incompatible keys; a `references` group to a column list that is not a key of the target; a PK column bound to a non-identifying role; an FK group whose size differs from its `references.columns` `(p1 F10)`. | A looser match silently binds the wrong role. |
| D9 | Review before the plan gate. | The light panel reviewed r1. Proposed: go to the plan gate with r2, recorded as unreviewed, or run a second light round on r2 at the owner's choice. | A second round costs one more panel run. |
| D10 | Reporter inputs. | Ask for: the three local diffs (reference only); the size of their flattened model; the intended meaning of `extension_roles`; and whether they can run the external acceptance. File the three issues on GitHub so the records can link them. | Without these, external acceptance stays missing evidence, and D11 is decided blind. |
| D11 | Raise the export's source cap (`MAX_MODEL_BYTES`, 10 MiB) for `gnd export ossie` `(p1 F8)`. | Decide after D10 and OB1-C2's measured ratio. If needed, add a phase OB1b, because this threads a cap through the model loader. | Without it, issue 1 is fixed only for sources of 10 MiB or less. |

## 11. Close amendments (r3)

Phases deferred plan repairs to the close. Each row amends the text named,
which stays above as written. Where a row and the older text disagree, the
row governs. The normative rules are in `representation-format.md`; this
section only records what the plan got wrong or left open.

| # | Plan text (r2) | Amendment | Raised in |
|---|---|---|---|
| A1 | §1.2: no test covered `ossie:output-size`. | One did, in `tests/test_ossie_import.py`. | [004](../004-phase-OB1.md) IF1 |
| A2 | §2.1, D3: five import caps. | Six: the JSON decoder re-checks the cap after the load. | 004 IF2 |
| A3 | §9, OB1 affected consumers. | Add the CLI pin tests and the RF7 input-policy tests. | 004 IF7 |
| A4 | §2.3 rule 2: an n-1 uniqueness of an n-ary groups into an entity table. | Not Halpin, and there is no table to group into. Such a fact type has its own table. | [008](../008-phase-OB2.md), S5 |
| A5 | §2.3: silent on a fact type with no uniqueness. | Its key is all its roles (119 of 226 census fact types). | 008, S1 |
| A6 | OB2-C4: a 10x scale model. | It cannot load under the 10 MiB model cap. The scale test runs at 5x. | 008 IF4 |
| A7 | §2.3: any preferred external uniqueness is a composite key. | Every component must also be functional on the entity, as the ontology export requires. | [011](../011-phase-OB3.md), E3 (a) |
| A8 | Predicate 2 and §5: a default run always adds the two relational files. | A model that maps to no table writes the ontology's three files and a note, because the pinned core-spec requires a dataset. | 011 IF1; [012](../012-OB3-departures-gate.md) |
| A9 | Predicate 4: every fact type and constraint is carried or listed. | Also: a link the mapping cannot write is listed in `unmapped_links` (`identification-differs`, `arity-over-limit` above 32 roles). Foreign-key names are unique in the whole schema. | 011 IF2, RR2, RR3; 012 |
| A10 | §2.4: a foreign key's columns are ordered by position in `references.columns`. | Every column of a group carries the same block. They pair by the table's column order. | [015](../015-phase-OB4.md), K1 |
| A11 | D8: four contradiction classes, undefined. | Defined as rule ids in the normative section. For `binding:incompatible-keys`, an entity and a part of its own identifier are compatible. | 015 K4, K5, IF1; [016](../016-OB4-departures-gate.md) |
| A12 | §2.4: `targets` give a column its meaning. | `roles` alone binds a role. An `identifier` target marks a home table; the other two kinds are only checked. | 015 K12 |
| A13 | §2.4: silent on nesting depth and surrogate keys. | An identifier nested more than 8 entities deep is not followed. A fact held only through a surrogate key cannot be bound. | 015 RR2, K13; 016 |
| A14 | OB3 E5 (spec), plan §2.2: identifiers are quoted and upper-cased. | Only a regular identifier is upper-cased. Any other name is quoted as written. Found by the oracle lane. | [020](../020-phase-OB5.md); [019](../019-OB5-quoting-gate.md) |
| A15 | §4 OB5: "a changelog entry". | The repository has no changelog file. The entry is a section of `docs/release-notes.md` under `Unreleased:`. | 020, O14 |
| A16 | D11: decide the source cap after D10. | Measured: output is about 6 times the source, and a model at the reporter's scale is 1.5 MB of source. No source-cap parameter is added. D10's answer can reopen it. | 004 IF9; 011 |
