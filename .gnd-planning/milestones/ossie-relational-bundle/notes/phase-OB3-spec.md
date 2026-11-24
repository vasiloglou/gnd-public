# Phase OB3: the relational files (semantic model and mapping)

## 1. Status

**Implemented, 2026-11-24.** The owner approved r1 with E1–E16 as proposed
([spec gate](../009-OB3-spec-gate.md)) and the corpus with amendment r1.1
([corpus gate](../010-OB3-corpus-gate.md)). §12 records what implementation
found, including two departures for the owner (IF1, IF2). The text below §1
is kept as written at each gate.

## 2. Provenance

- **Plan:** [ossie-relational-bundle plan r2](ossie-relational-bundle-plan.md)
  (sha256 `52d946a4…6e1d`), approved at the [plan gate](../002-plan-gate.md)
  with D1–D11 as proposed. Read for this spec: §0, §1.2, §2.1–§2.3, §3, §4
  OB3, §5, §6, §7, §9 and §10 D2, D4, D6.
- **Prior phases:**
  - OB1, record `004-phase-OB1.md` on branch `claude/ossie-ob1-size-bounds`
    (PR #266, unmerged): `--max-output-bytes`, the census baseline
    `tests/fixtures/ossie_ob1_baseline.json`, open questions OB1-Q1 and
    OB1-Q2.
  - OB2, record [008-phase-OB2.md](../008-phase-OB2.md) (PR #270,
    unmerged): `gnd.rmap`, D5 = HALPIN, IF5 and RR1 accepted, open
    questions OB2-Q1 to OB2-Q3.
- **OB2-Q3 ruled.** Asked "Run a third review round before OB3?", the owner
  answered: "Move on to OB3". No third round runs over the OB2 round-2
  repairs (`171665e8`); OB3's tests are the next instrument over that code.
- **Upstream format, read 2026-11-24 at the pinned commit `ee89dbd`:**
  `ontology/mapping.json` (sha256 `936118ca…04f3`, 2,550 bytes, not yet
  vendored), the `ConceptMapping`, `ObjectMapping`, `ReferentMapping` and
  `LinkMapping` definitions in the vendored `ontology.json`, `ontology.md`
  § "Ontology mappings", `core-spec/expression_language.md` § "Namespacing
  and Identifier Resolution", the `examples/flights.*` trio and
  `validation/validate.py` (`validate_mapping`,
  `mapping_relationship_errors`).
- **Measured while writing this spec** (§13 has the detail):
  - H1: over 425 admitted models, the ontology export and the Rmap disagree
    on the composite identifier of 3 entities. In each, the Rmap accepts an
    identification over a non-functional binary.
  - H2: adding a `sample_population` changes `model_identity` (case 01:
    `a7ba3beb…` against `cfdd9f72…`).

## 3. Obligations

| # | Source | Obligation | Discharged in |
|---|---|---|---|
| O1 | Plan §4 OB3 deliverable | Semantic-model and mapping renderers, the vendored `mapping.json`, the `GND` extension, and the default per D2 (a): five files, with `--ontology-only` | §6 |
| O2 | OB3-C1 | 0 schema errors in-process against the pinned schemas | T2 |
| O3 | OB3-C2 | The upstream validator accepts all three files in the opt-in oracle lane | T11 |
| O4 | OB3-C3, plan §0 rule 4 | One walk: every fact type and every constraint is carried or listed with a closed reason | §6.5; T4 |
| O5 | OB3-C4 | Byte reproducibility | T5 |
| O6 | OB3-C5, predicate 2, D2 (a) | The three legacy files are byte-identical to the baseline, and a collision on a new path exits 11 | T6, T7 |
| O7 | OB3-C6 | `--max-output-bytes` covers the new files | T8 |
| O8 | OB3-C7, D6 | The semantic model, and the mapping minus its identity and binding fields, are byte-identical with and without a `sample_population`; the expected differences are asserted | T9 |
| O9 | Plan §0 rule 2 | A time bound for the mapping walk at the reporter's scale | T10 |
| O10 | Plan §0 rule 5 | Normative prose has one home: `representation-format.md` § "Ossie interchange" | §6.8 |
| O11 | Plan §2.2 | File names, schemas, and the mapping's `GND` extension bound to the ontology sha256, the semantic-model sha256 and the model identity | §6.1, §6.6 |
| O12 | Plan §2.3 "Required core-spec members" (p1 F11) | `Dataset.source` is the table name, marked `source_kind: logical`; `Field.expression` names the column; `Field.datatype` through a closed map | §6.3; E5, E6 |
| O13 | Plan §2.3 "Populations", D6 | No population rows in any relational file | §6.3, T9 |
| O14 | Plan §2.3 "Unrepresentable constructs" (p1 F14) | Listed by id with a closed reason; nothing dropped silently | §6.5 |
| O15 | Plan §5 | `PINNED.json` gains `mapping.json`; the pin test is extended, not duplicated; the disclosure tables class the new files like the existing Ossie surfaces | §6.7; T12 |
| O16 | Plan §9 OB3 row | `uv run pytest -q tests/test_ossie_export.py tests/test_ossie_relational.py --tb=short`; affected consumers: the Ossie docs, the disclosure tables, the `PINNED.json` test | §8 gate |
| O17 | OB2-Q1 | `export/ossie.py` and `gnd.rmap` each decide "confirmed alethic" | E15 |
| O18 | H1 (this spec) | The Rmap and the ontology must agree on each entity's identifier, or the mapping is wrong | E3 |
| O19 | OB1-Q2, D11 | Whether the source cap becomes a parameter | not OB3's (§9) |
| O20 | OB1-Q1 | `guard_yaml` default capture | not OB3's (§9) |

## 4. Standing rules bound to this phase

| Rule | How it binds OB3 |
|---|---|
| 1 Totality | The renderer reads only an admitted model and the Rmap's schema; it never refuses on its own. The only new refusals are the existing ones: `ossie:output-size` (exit 3) and a collision (exit 11). |
| 2 Cap bounds the document, not the algorithm | T10 times the whole five-file render at 1,400 entities and 4,500 fact types, and checks the growth ratio at 5×. Every lookup in the mapping walk is a dictionary lookup. |
| 3 Validation order | Unchanged: usage (64), read, the existing refusals, the Rmap (never refuses), schema validation of all files (an internal error if it fails), then output size, then publication. |
| 4 One walk | `gnd.rmap.dispositions` is the one walk. The mapping's `GND` extension is rendered from it, and T4 checks it against the model, not against the walk's own output. |
| 5 One home | The normative text for both files lives in § "Ossie interchange". The vendored `mapping.json` is a pinned copy held identical by a digest test. |
| 6 Measure | H1 and H2 were measured before this spec. E3's effect is measured on the census in implementation and recorded. |
| General solutions (AGENTS.md) | Identifiers are quoted by one rule over their whole grammar (E5). Names come from the Rmap and the ontology as data, never re-parsed from rendered text. |

## 5. Goal

`gnd export ossie MODEL --out OUT` writes five files by default:

| File | Content |
|---|---|
| `OUT` | the ontology, unchanged |
| `OUT.gnd.json` | the sidecar, unchanged |
| `OUT.loss.json` | the loss report, unchanged |
| `OUT.semantic_model.<fmt>` | an Ossie core-spec semantic model: one dataset per Rmap table, one field per column, keys, unique keys, one relationship per foreign key |
| `OUT.mapping.<fmt>` | an Ossie mapping document from the ontology's concepts and relationships to the semantic model's datasets and fields, plus a `GND` extension that lists every fact type and constraint with its disposition |

`--ontology-only` writes the first three, byte-identical to today.

## 6. Design

### Reuse

Searched with `scripts/components_index.py search` for "ossie export",
"publish new files", "canonical json", "json schema validation" and
"ossie names".

| Capability | Found | Decision |
|---|---|---|
| Relational schema and the one walk | `model.relational_mapping` (`gnd.rmap`) | **reuse**, with one public addition (E4) |
| Concept names, relationship owners and role order | `export.ossie`: `_names`, `_role_order`, `ProjectedRelation` | **reuse**: the renderer reads the ontology `_ontology` already builds, never recomputes it (E12) |
| Create-once publication with a commit marker | `infra.safe_filesystem` (`publish_new_files`) | **reuse**: two more files in the same group |
| Canonical JSON | `infra.artifacts` (`canonical_json_bytes`) | **reuse** |
| YAML output | the ontology's dumper settings in `render_ossie` | **reuse** by moving them into one helper both files call |
| Schema validation | `jsonschema` `Draft202012Validator`, as `export.ossie._schema` uses | **reuse**, with a reference registry for the pinned cross-document `$ref`s (§6.7) |
| A relational renderer | none | **new**: `src/gnd/export/ossie_relational.py` (plan §3) |

### 6.1 Command and files

- **Flags.** `--ontology-only` is added (D2 a). With it, the run is the
  pre-OB3 run in every respect. `--relational` is not added.
- **Names.** `OUT + ".semantic_model." + fmt` and `OUT + ".mapping." + fmt`,
  where `fmt` is the run's `--format` (`yaml` or `json`), like the sidecar's
  `OUT + ".gnd.json"`.
- **Publication.** One `publish_new_files` group in this order: loss
  report, sidecar, semantic model, mapping, then the ontology last as the
  commit marker. A collision on any path exits 11 and publishes nothing.
- **Size.** `--max-output-bytes` (OB1) bounds each of the five files.
- **Strictness.** `--strict` keeps its meaning (the loss report's refusals).
  An unmapped fact type or constraint is never a refusal (E11).

### 6.2 Library surface

```python
# src/gnd/export/ossie_relational.py
@dataclass(frozen=True)
class RelationalArtifacts:
    semantic_model: bytes
    mapping: bytes

def render_relational(
    model, ontology: dict, projected: Mapping[str, ProjectedRelation],
    names: Mapping[str, str], *, ontology_bytes: bytes, output_format: str,
) -> RelationalArtifacts
```

`render_ossie` gains `relational: bool = True`. `OssieArtifacts` gains
`semantic_model: bytes | None` and `mapping: bytes | None`, which are `None`
when `relational` is false. The size check covers every non-`None` artifact.

### 6.3 The semantic model

| Member | Value |
|---|---|
| `version` | `0.3.0.dev0` |
| `name` | the ontology's `name` + `_relational` |
| `datasets` | one per Rmap table, in the Rmap's table order |
| `Dataset.name`, `Dataset.source` | the table name. `custom_extensions`: `GND`, data `{"source_kind":"logical"}` (p1 F11) |
| `Dataset.primary_key` | the table's primary key; omitted when empty |
| `Dataset.unique_keys` | the table's unique keys (D4); omitted when empty |
| `Dataset.fields` | one per column, in column order |
| `Field.name` | the column name |
| `Field.expression` | `{"sql": <quoted column>}` (E5) |
| `Field.datatype` | the column's primitive through the closed map (E6); omitted for a column with no primitive |
| `relationships` | one per foreign key, in table order and then foreign-key order: `name`, `from` (the referencing table), `to`, `from_columns`, `to_columns` |

It carries no model identity, no digest, and no population (D6).

### 6.4 The mapping

| Member | Value |
|---|---|
| `version` | `0.3.0.dev0` |
| `name` | the ontology's `name` + `_mapping` |
| `ontology_ref` | `name`: the ontology's `name`; `iri`: `./` + the basename of `OUT` |
| `semantic_model_ref` | `name`: the semantic model's `name`; `iri`: `./` + the basename of its file |
| `concept_mappings` | one per concept that has at least one object or link mapping, in the ontology's component order |
| `custom_extensions` | one `GND` entry (§6.6) |

**Object mappings** (how a concept's objects come from a table). A concept
gets one when its object type has its own table (not absorbed):
- **Value type or simple identifier:** `expression` over the table's single
  key column.
- **Composite identifier:** `referent_mappings`, one per relationship of the
  ontology's `identify_by`, in that order. A value component is an
  `expression`; an entity component is nested `referent_mappings` over
  that entity's own `identify_by`, recursively, as in `ontology.md`'s
  `OrderLineItem` example.
- **Absorbed subtype (HALPIN):** no object mapping (E9).

**Link mappings** (how a relationship's links come from a table). Each
carried fact type F gets one tree, under the concept that owns F's
relationship in the ontology:
- The levels follow the relationship's role order (`ProjectedRelation.order`):
  the root maps the owner role, and each child the next role.
- The node at level *n* = F's arity names F. Unary F is a root node that
  names F.
- Each node's `object_mapping` maps the objects of its role from the role's
  columns in F's table (E4), with an explicit `concept` below the root.
- A nullable column contributes a link only where it is not NULL, and a
  unary flag through `CASE WHEN <flag> THEN <key> END` (E8).

Trees are not merged across fact types (§9).

### 6.5 Totality: the one walk

The mapping's `GND` extension carries every row of `gnd.rmap.dispositions`,
carried and unmapped alike, in its order. T4 then checks, from the model
alone:
- every fact type id and every constraint address appears exactly once;
- every fact type carried by the Rmap names exactly one link mapping tree;
- every unmapped fact type names none.

Constructs the relational layer does not carry (mandatory constraints
outside rule 5, value, frequency, ring, subset, exclusion, derivations,
deontic rules, uniqueness spanning tables) are the Rmap's `not-relational`,
`spans-tables` and other closed reasons. OB3 adds no reason of its own
except the two of E3 and E9 (`identification-differs`, `subtype-absorbed`),
which are listed per concept.

### 6.6 The `GND` extension

One `CustomExtension` on the mapping: `vendor_name: GND`, `data`: the
canonical JSON of:

```json
{
  "schema": "gnd-ossie-relational/1",
  "model_identity": "sha256:…",
  "ontology_sha256": "…",
  "semantic_model_sha256": "…",
  "rmap_variant": "halpin",
  "dispositions": [{"kind": "…", "id": "…", "carried_as": […], "reason": null}],
  "concepts": [{"concept": "…", "reason": "subtype-absorbed"}]
}
```

`data` is an opaque string in core-spec, so its schema id is GND's. OB4
adds `binding_sha256` and `unbound`. The mapping is not bound into the
sidecar or the loss report, so those stay byte-identical (O6).

### 6.7 Pins and validation

- `src/gnd/schema/ossie/mapping.json` is vendored byte-for-byte from
  `ee89dbd`. `PINNED.json` gains a `mapping` entry with its upstream path
  and sha256, and the existing pin test is extended to check it.
- `mapping.json` and `ontology.json` `$ref` each other and core-spec through
  `raw.githubusercontent.com/apache/ossie/main/…` URLs. In-process
  validation resolves exactly those URLs to the vendored files through a
  `referencing` registry, offline. An unknown `$ref` is an internal error,
  never a network read.
- `render_ossie` validates both new files before it returns, like the
  ontology today. A failure is an internal error (exit 70): it means a
  renderer defect, not bad input.

### 6.8 Normative home

§ "Ossie interchange" in `representation-format.md` gains a subsection
"Semantic model and mapping" holding §6.1, §6.3–§6.6 and E5–E9 in prose. The
module docstring cites it. OB5 writes the explanation and how-to; OB3 writes
only the normative subsection and the export command's help text.

## 7. Decisions

| ID | Question | Proposal | What the other reading costs |
|---|---|---|---|
| E1 | **Branch base.** OB3 needs OB1's `--max-output-bytes` and census baseline, and OB2's Rmap. Neither is on main. | Draft and gate the spec now. Implement on a branch cut from main **after** #264, #266 and #270 merge. | Merging the OB1 branch into this one now gives a PR that carries two phases' diffs, and a rebase whenever either changes. |
| E2 | **Approval instrument** (§11). | Corpus first: hand-derived expected semantic models and mappings for seven OB2 corpus cases, committed before code. | Prose only: the shapes of two new serialized formats are approved without seeing one. |
| E3 | **H1: the identifier the mapping uses.** The Rmap takes a preferred external uniqueness over binaries whose component role need not be functional. The ontology export requires each component binary to be functional on the entity (a confirmed alethic single-role uniqueness there). They disagree on 3 census entities. | (a) **Fix the Rmap**: a composite identifier qualifies only when every component binary is functional on the entity, as Halpin requires and the ontology already checks. The 3 entities become `identification-unmatchable` (measured and recorded). (b) Where the two still differ (the export also admits a non-preferred external uniqueness), the concept's object mapping and every link through it are listed as `identification-differs`. The ontology export is not changed. | Leaving the Rmap as it is writes key columns that can hold several values per entity, and mappings whose referents the ontology does not declare. This amends an OB2 rule, so it is the owner's. |
| E4 | **Role-to-column access.** The mapping needs, for every role of every carried fact type, its table and columns. The Rmap keeps this internally (`role_cols`, plus rule-specific cases). | Add one public field `RelationalSchema.roles: tuple[((fact_type, role), (table, columns)), …]`, sorted, covering every role of every carried fact type. T8 is extended to pin it. | Recomputing it in the renderer from `Column.origin` misses rule-5 subject roles and key roles, which have no origin of their own: a second placement engine. |
| E5 | **Identifier spelling in SQL expressions.** Rmap names match `^[a-z][a-z0-9_]*$` but can be SQL reserved words (`order`, `date`, `year`). Ossie compares a regular identifier by its uppercased form, and a quoted one exactly. | Write every identifier in an expression quoted and uppercased: `"ORDER"`, `"STATE"."CODE"`. By `expression_language.md`, `"ID"` matches the regular `id`, so this names the declared field and never collides with a keyword. One rule over the whole grammar; no keyword list. `Field.name` and dataset names stay as the Rmap writes them. | Unquoted names need a reserved-word list, which is a pattern fitted to a vendor. Quoting the lowercase spelling (`"order"`) does not match the regular field name `order`. |
| E6 | **Datatype map.** | String, Integer, Float, Boolean, Date and DateTime map to themselves. Number goes to Decimal. Binary and Duration go to `Opaque`, with a field extension `{"gnd_primitive": …}`. A column with no primitive has no `datatype`. | Mapping Duration to Integer (as the ontology's `extends` does) claims a unit the model does not state. |
| E7 | **Dataset source.** | `source` is the table name, with `source_kind: logical` in a dataset extension (plan §2.3, p1 F11). | — |
| E8 | **Nullable columns and unary flags in link mappings.** Ossie does not say what a NULL in a mapping expression means. | GND's reading, stated in the normative text: a NULL yields no object and so no link. A unary maps through `CASE WHEN "T"."FLAG" THEN <key> END`. The oracle lane checks the expressions parse; it cannot check the semantics, so this is a recorded residual. | Listing every nullable and unary mapping as unmapped would leave most functional fact types out of the mapping. |
| E9 | **Absorbed subtypes (HALPIN).** The supertype's table has no column saying which rows are the subtype's. | No object mapping for the subtype, listed as `subtype-absorbed`. Its own fact types are still link-mapped at the subtype's concept: by E8, a link exists only where the subtype's column is not NULL. | A discriminator column would be a new Rmap rule, which OB2 did not approve. |
| E10 | **What the `GND` extension lists.** | Every disposition, carried and unmapped, so a reader can check totality from the file alone (§6.6). | Listing only the unmapped rows makes the file smaller, but then "carried" can only be read off the mapping trees. |
| E11 | **`--strict` and unmapped constructs.** | `--strict` is unchanged. The Rmap never refuses, and an unmapped construct is listed, not refused. | Making `--strict` refuse any unmapped construct would refuse most census models (35 unmapped fact types). |
| E12 | **Where the renderer gets concept names and role order.** | From the ontology `_ontology` builds (its `names`, `ProjectedRelation.order`, `identify_by`), passed in, never recomputed. `_ontology` also returns `names` and `projected`. | Recomputing would let the mapping name a relationship or role order the ontology does not have. |
| E13 | **Document names and references.** | `<name>_relational` and `<name>_mapping`. Each `iri` is `./` plus the referenced file's basename, so the upstream validator resolves the trio from one directory. | Absolute IRIs would put the caller's paths in the output. |
| E14 | **Format.** | The run's `--format` applies to all five files. YAML uses the ontology's dumper settings; JSON uses `canonical_json_bytes`. | — |
| E15 | **OB2-Q1:** should `export/ossie.py` take its "confirmed alethic" decisions from `gnd.rmap`? | Not in OB3. Changing the ontology export risks the byte-identity of predicate 2. The question goes to the close sweep. | — |
| E16 | **Identifiers longer than 128 characters.** Composite column names can exceed Ossie's portable limit. | No rename in OB3. Count them in the measurement, and record them as a residual. | Truncation needs a collision rule and changes OB2's approved names. |

## 8. Tests and corpus

### The corpus (authored first; E2)

Seven OB2 corpus cases, each with a hand-derived
`expected.semantic_model.yaml` and `expected.mapping.yaml` under
`tests/fixtures/ossie_relational/NN/`, plus a `STORY.md` saying what each
file must show:

| Case | Shows |
|---|---|
| 01 functional binary | one dataset; simple-identifier object mapping; a level-2 link mapping |
| 04 many-to-many | own table; two foreign keys; two relationships |
| 09 unary | a Boolean field; the `CASE WHEN` link (E8) |
| 14 external identification | composite key; nested referent mappings; a composite foreign key |
| 15 subtype | HALPIN absorption; `subtype-absorbed` (E9) |
| 17 objectification | objectified table; matched key roles |
| 18 derived | `derived-computed` in the extension; no link mapping |

### Tests (`tests/test_ossie_relational.py`, plus `tests/test_ossie_export.py`)

| ID | Case | Expected |
|---|---|---|
| T1 | the seven corpus cases | equal to their expected files, byte for byte in YAML; the JSON run equal in structure |
| T2 | every census and corpus model, both formats | the semantic model has 0 errors against core-spec, and the mapping 0 against `mapping.json`, offline |
| T3 | the same models | in-process cross-checks: unique dataset, field and relationship names; every relationship names existing datasets and fields with equal arity; every mapping expression names a declared `dataset.field`; every link node's relationship is declared on its concept at the level its arity calls for; every referent relationship is in the concept's `identify_by` |
| T4 | the same models | the one-walk checks of §6.5, computed from the model |
| T5 | two runs, and runs from two paths | identical bytes for all five files |
| T6 | the OB1 census baseline (82 entries) | `--ontology-only` and the default run both give the three legacy files byte-identical, with the same exits |
| T7 | an existing file at each new path in turn | exit 11, nothing published |
| T8 | the large model with the mapping the largest file; `--max-output-bytes` at its size − 1 and at its size | refused with `ossie:output-size` (exit 3), then published |
| T9 | case 01 with and without a `sample_population` | semantic model byte-identical; mapping equal except `model_identity` in the extension; the loss report's `population:out-of-scope` row present |
| T10 | the `rmap_large` generator at 1× and 5× | the five-file render within a recorded bound; time ratio under 12 |
| T11 | oracle lane (opt-in, named, not run by default) | `validation/validate.py` accepts the ontology, semantic model and mapping of every census model, the mapping cross-checked against the other two |
| T12 | `PINNED.json` and the vendored file | the mapping digest matches; the pin test covers it |
| T13 | E3 (a): case 14 with a non-functional component binary | the entity is `identification-unmatchable`; the census measurement records the 3 entities |
| T14 | E5: a role named `order` and one named `select` | expressions `"T"."ORDER"`; T2 and T3 pass; T11 parses them |
| T15 | E6 | the map covers every value of the model schema's `primitive` enum (a literal table) |
| T16 | E4 | `RelationalSchema.roles` has exactly one row per role of every carried fact type; T8 of OB2 extended |

**Gate:**
1. `uv run pytest -q tests/test_ossie_export.py tests/test_ossie_relational.py tests/test_rmap.py --tb=short`
2. the issue-171 guard list from `project.md`, including the disclosure tests
3. `uv run ruff check`
4. `python3 scripts/components_index.py changed --base <phase base> --strict`

## 9. Out of scope for this phase

- The physical binding (OB4) and the explanation, how-to and skill (OB5).
- Merging link-mapping trees across fact types (ontology.md's shared
  prefixes). Each fact type has its own tree.
- Rows of any population.
- Changing the ontology export (E15), the sidecar or the loss report.
- DDL; importing a semantic model or mapping.
- OB1-Q1 (`guard_yaml`) and D11 (the source cap).
- Upstream questions about NULL semantics in mappings (E8).

## 10. Size

Estimate:
- `ossie_relational.py`: about 350 lines;
- `ossie.py` and `commands/export.py`: about 60 lines changed;
- `rmap.py`: about 40 lines (E3, E4);
- the normative subsection: about 90 lines;
- tests: about 450 lines;
- the corpus: 7 cases with two expected files and a story each.

## 11. Approval instrument

**Proposed: corpus first (E2).** The two files are new serialized formats,
the shape `review-convergence.md` defaults to corpus first.

1. The seven cases' stories and expected files are committed before any
   renderer code.
2. The owner gates on the stories and the expected files.
3. The harness lands red: T1 fails on every case because the renderer does
   not exist.
4. Each implementation commit names the cases it turns green.

## 12. Implementation findings (recorded during OB3)

Rows marked **owner** depart from an approved rule and are put to the owner
with the phase record.

| # | Finding | Effect |
|---|---|---|
| IF1 | **A model that maps to no table cannot have a semantic model.** The pinned core-spec requires at least one dataset. Two scanned models map to none (their fact types are all derived or unmapped). The first render failed schema validation on them. | Such a run writes the ontology's three files, prints a note on standard error and exits 0. **Owner:** this departs from predicate 2 ("a run with no new flag writes ... plus the two files") for these models. |
| IF2 | **`unmapped_links`.** A carried fact type whose roles cannot be object-mapped (E3 b) has to be listed somewhere, and §6.6 had only `concepts`. | The extension gains `unmapped_links`, present only when not empty, so no approved corpus byte changes. **Owner:** a member §6.6 did not name. |
| IF3 | **`identification-differs` in practice.** Over the 422 scanned models the export maps, it lists 16 fact types in 14 models and 2 concepts. Three causes: a unit-based reference (the ontology declares no identifier for it), an objectification keyed by its own fact type, and a subtype inheriting through several supertypes (the ontology inherits only through one). | Stated in the normative text. No guess is written for any of them. |
| IF4 | **E3 (a) on the census.** One census model changes, equally under both variants: `reference_scheme_elicitation` loses the `task` table (4 to 3 tables; 3 fact types become `identification-unmatchable`). The two literature examples keep their `assertion` table, because it is an objectification and falls back to its fact type's key. Totals move from 195 / 196 tables and 35 / 35 unmapped to 194 / 195 and 38 / 38. | [OB3-rmap-measurement-after-E3.md](OB3-rmap-measurement-after-E3.md). The models that differ between the variants are the same four, so the D5 ruling stands on the same comparison. OB2's own measurement file is history and is not rewritten. |
| IF5 | **The Rmap needed a second public record.** E4 named `roles`. Building referent mappings by fact type (B8) and comparing identifications with the ontology (E3 b) also need each object type's key structure and owning table. | `RelationalSchema.identifications` (`Identification`: kind, key columns, the component fact type and role per column, the owning table), beside `roles` (`RolePlacement`). T16 pins both. |
| IF6 | **§6.2's signature changed.** `render_relational` would have needed the YAML encoder, which lives in `ossie.py`, which imports the renderer. | `ossie_relational` builds documents only (`build_semantic_model`, `build_mapping`, `validate_relational`); `ossie.py` encodes all five files through one `_encode` and computes the digests. |
| IF7 | **Entities without a table** (S7: only ever a role player) get no object mapping and are not listed in `concepts`, which holds only entities that have a table. A **value-type owner** of a relationship gets link mappings and no object mapping (B1). | Stated in the normative text. |
| IF8 | **One existing test changed.** OB1's per-artifact bound test asserted three published files. | It now passes `--ontology-only`: it is about the three legacy artifacts. T8 covers the relational files, with a model where the mapping is the largest file and one where the semantic model is. |
| IF9 | **E16 measured.** Of 3,157 fields over the scanned models, none has a name over 128 characters. | The residual stays recorded; no rename. |
| IF10 | **T10 measured.** At 1,400 entities and 4,500 fact types the five files render in 3.3 s, against 2.6 s for the ontology's three; the ratio to one fifth of that scale is 5.1 (linear). | T10's bound is 60 s and a ratio under 12. |
| IF11 | **T11 is written and not run.** `OssieOracle.validate` gains a `schema` argument, and `test_external_relational_census` validates the semantic model and the mapping of every census model with the pinned validator. | The opt-in oracle lane needs the owner's request. Until it runs, upstream acceptance of quoted identifiers and of `CASE WHEN` is unconfirmed. |
| IF12 | **RF6.** The new module and the wiring add 70 dynamic-subscript rows and remove 11. | `evidence/OB3/dynamic-query-successor.json`, chained after OB2's. A census only; no query exception is widened, and the renderer reads the model only through `gnd.rmap` and the ontology view. |
| IF13 | **The disclosure table** already classes `gnd export ossie` as every-mode. | Its row now names the ids the two new files carry, and a test holds the two files equal in customer mode. |

## 13. Harvest findings (measured while writing this spec)

| # | Finding | Effect |
|---|---|---|
| H1 | Over the 425 scanned models the export admits (85 more it does not), 13 entities use external identification. For 3 of them, the ontology has no `identify_by` but the Rmap has a composite: `reference_scheme_elicitation` (`task`, through `task_in_project`, which has no uniqueness on `task`), and two literature examples (`assertion`, through `assertion_names_passage` and `assertion_names_work`, which have none). The Rmap does not check that a component is functional; the export does. | E3 |
| H2 | `model_identity` changes when a `sample_population` is added (case 01). | D6's "expected differences" include the mapping's `model_identity`; T9 asserts it. |
| H3 | The upstream mapping schema `$ref`s the ontology and core-spec through `main` branch URLs, not the pinned commit. | §6.7: an offline registry maps exactly those URLs to the vendored files. |
| H4 | Upstream says parser and converter support for standalone mapping documents "is not yet available"; the validator does cross-check them. | T11 uses the validator only. |

## 14. Amendment r1.1: rules settled while authoring the corpus (2026-11-24)

The owner approved r1 (sha256 `fa034f27…9484`; [gate](../009-OB3-spec-gate.md))
with E1–E16 as proposed. Under E2, authoring the corpus came next. Writing
the expected files by hand forced the rules below, which r1 left open or got
wrong. **They are unapproved**: the owner sees them at the corpus gate,
together with the stories in
[tests/fixtures/ossie_relational](../../../../tests/fixtures/ossie_relational/README.md).
§1–§13 are unchanged, except where a row says it supersedes them.

| # | Rule | Why | Case |
|---|---|---|---|
| B1 | **A value-type concept never gets an object mapping**, even when the Rmap gives it a table. This supersedes §6.4's "value type or simple identifier". | The pinned `ontology.json` says of `object_mappings`: "Valid only when the concept is an entity type". | all |
| B2 | **`render_ossie` needs OUT's basename.** It gains `document_name: str`, which the two `iri` values are built from. The corpus assumes `ontology.yaml`. This amends §6.2. | E13 makes each `iri` the referenced file's basename, which the library could not know. | all |
| B3 | An extension's `data` is the canonical JSON of its payload **without the trailing newline**, for the mapping's extension and for each dataset's `{"source_kind":"logical"}`. | A trailing newline inside a YAML string forces an escaped, double-quoted scalar. | all |
| B4 | **Member order.** Semantic model: `version`, `name`, `datasets`, `relationships`. Dataset: `name`, `source`, `primary_key`, `unique_keys`, `fields`, `custom_extensions`. Field: `name`, `expression`, `datatype`, `custom_extensions`. Relationship: `name`, `from`, `to`, `from_columns`, `to_columns`. Mapping: `version`, `name`, `ontology_ref`, `semantic_model_ref`, `concept_mappings`, `custom_extensions`. Concept mapping: `concept`, `object_mappings`, `link_mappings`. Link mapping: `object_mapping`, `relationship`, `children`. Object mapping: `concept`, then `expression` or `referent_mappings`. Referent mapping: `relationship`, then `expression` or `referent_mappings`. | YAML output keeps insertion order, and T1 compares bytes. | all |
| B5 | **Empty lists are omitted**: `relationships`, `primary_key`, `unique_keys`, `children`, `object_mappings`. The extension's `dispositions` and `concepts` are always present. | Several of these have `minItems: 1` in the pinned schemas. | 01, 09 |
| B6 | **Order.** Concept mappings follow the ontology's component order. A concept's link mappings follow the order of its relationships in the ontology. | r1 ordered concept mappings only. | 04, 18 |
| B7 | **`gnd_reference` gets no link mapping.** It is the ontology's spelling of a simple identifier and has no fact type. A nested referent mapping names it to reach an entity component's identifier. | Otherwise totality (§6.5) would count a relationship no fact type stands behind. | 01, 14 |
| B8 | **Referent mappings follow the ontology's `identify_by` order.** Each component's columns are found by its fact type id, never by position. | The Rmap orders key columns by `role_refs`; `identify_by` has its own order. They agree in the corpus but need not. | 14, 17 |
| B9 | **A root object mapping never names `concept`; every node below it does.** | Upstream resolves the root to the concept being mapped, and a lower node to the role's concept; naming it below the root is what its examples do. | all |
| B10 | **Identification fact types are link-mapped like any carried fact type** (the Rmap's `key` dispositions). | They are carried, so §6.5 requires a tree for each. | 14, 17 |
| B11 | **An absorbed subtype's link trees root at the supertype table's key.** | The subtype has no table; its columns are in its owner's. | 15 |
| B12 | **A third file per case**, `expected.extension.json`: the mapping's extension, pretty-printed. T1 also asserts that the string in the mapping parses to it. | The canonical JSON string is folded by the YAML dumper and is not readable at a gate. | all |
| B13 | **The corpus checker** `tests/support/ossie_relational_corpus.py` is authoring tooling. It renders nothing: it writes the extension string from `expected.extension.json` and checks the cases. T1 reuses its YAML helper. | The checks of §8 T2–T4 have to exist before the renderer, to check the hand-derived files. | — |
| B14 | **Long strings are folded** by the ontology's YAML dumper, which leaves a trailing space on the folded line. OB3 keeps the dumper's settings (E14). | Changing the width would change the ontology's bytes for models with long readings. | 09 |

**Authoring checks run (no renderer exists):**
- The hand-written semantic models and mapping bodies were already in the
  dumper's form, except case 09's long `CASE WHEN` line (B14).
- The pinned core-spec accepts all seven semantic models, and the upstream
  `ontology/mapping.json` (sha256 `936118ca7753676c069d1fa615c8dced7e9a9499ab185cc2ddbe8d1c2d4404f3`,
  read at the pinned commit, not yet vendored) accepts all seven mappings,
  with its cross-document `$ref`s resolved offline to the vendored files.
- Each semantic model equals the owner-approved OB2 answer for its case:
  tables, columns, datatypes, keys and foreign keys.
- Each mapping passes the cross-checks of T3 and the totality check of T4
  against today's real ontology export.
- **The checker can fail.** Thirteen deliberate breakages of copied files
  were each caught: an undeclared field, reversed referents, a missing link,
  a link for a derived fact type, a binary named at level 1, a wrong child
  concept, a dropped foreign key, a changed datatype, a reversed key, a
  stale digest, an unlisted absorbed subtype, an unknown schema member, and
  a file not in dumper form.
- **Not run:** the upstream validator (T11's opt-in oracle lane). Whether it
  accepts quoted, uppercased identifiers and the `CASE WHEN` expression is
  therefore unconfirmed.

## 15. Review round 1 (Codex, read-only) and its repairs

[review.md](reviews/phase-OB3-r1/review.md) requested changes, with five
findings, over base `39e3d4c3`. Four were reproduced as regression tests
(8 tests red on the pre-repair code; two more are passing controls) and
fixed. The fifth is IF1, which is the owner's. The ledger is
[FINDINGS.md](reviews/phase-OB3-r1/FINDINGS.md). No approved corpus file
changed.

| # | Change | Departs from |
|---|---|---|
| RR1 | `Identification.columns` are the owning table's own key columns, so a key column renamed on a name collision is read under its real name (F1). | IF5 |
| RR2 | **A link mapping nests at most 32 levels.** A fact type with more roles keeps its table and is listed in `unmapped_links` as `arity-over-limit` (F2). The bound keeps the document shallow enough for any recursive reader, whatever arity the model admits. | §6.5 ("no reason of its own except the two of E3 and E9"). **Owner.** |
| RR3 | **Foreign-key names are unique in the whole schema**, not only per table pair: tables are named in sorted order, and a name already taken takes the next number (F3). No corpus answer has such a collision. | OB2 A11. **Owner.** |
| RR4 | Each `iri` percent-encodes the file name, every character outside the unreserved set (F4). | E13 |

**Open for the owner (F5 / IF1).** A model that maps to no table writes
three files and no relational listing. The alternatives are to accept that,
or to refuse such an export unless `--ontology-only` is given.

**The repaired bytes are not re-reviewed.**

