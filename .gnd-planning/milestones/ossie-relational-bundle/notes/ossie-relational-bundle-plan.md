# Ossie relational bundle

**Status: r1, draft, 2026-11-24. Not reviewed and not approved.** No review
instrument has run over these bytes. No phase spec is approved and no code is
written. `auto=false`. The decisions in §10 are open. D1 reopens two rulings of
the closed ossie-interchange milestone and is the owner's to make before OB2
can be specified.

Phase prefix `OB`. Inspection baseline: gnd-public main at `1926e895`
(2026-11-24); vendored Ossie pins as in `src/gnd/schema/ossie/PINNED.json`
(apache/ossie `ee89dbdc2844d8b7d293ed42c8613928bb99505f`, `0.3.0.dev0`).

`gnd export ossie` writes an Ossie ontology (layer 4) and two GND files: the
`.gnd.json` sidecar and the `.loss.json` report. This milestone does three things.

1. It makes the output size bound a parameter, so large models can export.
2. It adds Ossie's relational layer next to the ontology. That layer is a
   **semantic model** (datasets, fields, keys, relationships), produced by a
   new Halpin Rmap, plus a **mapping** document from concepts and roles to
   datasets and fields.
3. It lets a caller bind that relational layer to a physical schema they
   deliver, through a binding file. The built-in Rmap is then not used.

## Completion predicates

The milestone is complete when, on main after merge:

1. `gnd export ossie MODEL --out OUT` behaves exactly as today when no new flag
   is given and the model's three artifacts each fit in 10 MiB: the three files
   are byte-identical to the baseline for every model in the export census
   (OB1-C1, and OB3-C5 under D2). With `--max-output-bytes N`, an export whose
   largest artifact is above 10 MiB and at most N publishes all of its files.
   An export above N is refused with `ossie:output-size`, exit 3, and nothing
   is published (OB1-C2, OB1-C3).
2. A total, deterministic Rmap (`gnd.rmap`) turns every model of the export
   census into a relational schema, or refuses it with a closed reason. It
   assigns every fact type a table, or lists it as unmapped with a reason.
   The normative rules have one home (OB2-C1..C4).
3. The export writes `OUT.semantic_model.<fmt>` and `OUT.mapping.<fmt>`.
   Each validates against the pinned core-spec and pinned
   `ontology/mapping.json` schemas with 0 errors. The ontology must also still
   pass, and all three pass the upstream validator in the opt-in oracle lane.
   Every fact type is mapped or listed under the mapping's `GND` custom
   extension. Two runs give identical bytes. `--ontology-only` output equals
   today's output (OB3-C1..C5).
4. `--physical-binding FILE` replaces the Rmap with a caller's column map
   under a GND-owned JSON schema. Datasets, fields, primary keys and
   relationships come from the binding. A binding that names an unknown fact
   type, role, object type, table or column is refused before anything is
   published. Unbound fact types are listed in the `GND` extension with the
   binding's sha256. Without the flag the output does not change (OB4-C1..C5).
5. The normative section "Ossie interchange" in
   `gnd-orm-core/references/representation-format.md`, the export skill, the
   Ossie explanation and the how-to describe all of the above. No second home
   states a rule (OB5).

## 0. Binding design rules

The six paid-for rules of `.codex/skills/process-phase/references/project.md`
bind every phase. Here is where each one bites in this milestone:

| Rule | Where it applies here |
|---|---|
| 1 Totality | The binding-file reader (OB4) is a new consumer of untrusted JSON. It is total over arbitrary JSON, with the cap on the read, and refuses `NaN`, deep nesting and long integers with a named reason. It gets a hostile-input test. The `--max-output-bytes` argument (OB1) is validated as a bounded positive integer at the CLI boundary. |
| 2 Cap bounds the document, not the algorithm | Raising the output bound (OB1) lets in models about 3× larger than today. The Rmap (OB2), the mapping walk (OB3) and the binding resolution (OB4) each get a time-bound test on a generated model at the size the reporter measured (about 1,400 tables and 4,500 fact types). Role-name matching (OB4) must not be quadratic in roles per table. |
| 3 Validation order | OB4 states and pins one refusal order: binding syntax, then schema, then unknown names, then contradictions, then output size. Each spec also states whether the binding is checked before or after the ontology projection. |
| 4 One walk over N kinds | The policy "every fact type is mapped or listed in the GND extension" is enforced by one walk over all fact types, shared by the Rmap path (OB3) and the binding path (OB4). They do not get two copies of that check. |
| 5 One home | Normative prose for the Rmap, the semantic model, the mapping and the binding lives in `representation-format.md` § "Ossie interchange". The binding's JSON schema is a packaged artifact that this section cites. The vendored `mapping.json` is a pinned copy held identical by a digest test, which is one artifact under the rule's scope note. |
| 6 Measure | Choices between Rmap variants (subtype absorption, 1:1 absorption, D5) are settled by running both variants over the census and the reporter's case where available, not by argument. |

## 1. Scope, sources and authority

### 1.1 Sources

| ID | Source | Requests |
|---|---|---|
| I1 | Owner's issue file, 2026-11-24, issue 1 (not filed on GitHub at r1) | Parameterize the 10 MiB output bound (`--max-output-bytes N`). 10 MiB stays the default with no change. Apply it equally to the ontology and both sidecars. Test both cases. |
| I2 | Same file, issue 2 | Write `OUT.semantic_model.<fmt>` (Rmap) and `OUT.mapping.<fmt>`. Validate against pinned core-spec and `ontology/mapping.json` at `ee89dbd`. List unrepresentable constructs in a `GND` custom extension. `--ontology-only` keeps today's three files. Output is reproducible. Decide the UNIQUE gap and the `sample_population` behaviour. |
| I3 | Same file, issue 3 | `--physical-binding FILE`, a column-map document under a JSON schema shipped in GND. It supplies tables, columns (`sql_type`, `targets`, `references`), `primary_key`, `roles` and `extension_roles`. Role names match ignoring case and punctuation. Unknown names are refused. Unbound fact types are listed with the binding's sha256. Without the flag, output is unchanged. Depends on I2. |
| P1 | ossie-interchange plan r3 §10, OD1 and OD3; [close](../../ossie-interchange/034-milestone-close.md) | OD1 ruled "ontology layer only". OD3 (physical bindings) ruled "not now", noting that a binding concept in the model would be a model-format change and its own milestone. |
| P2 | `representation-format.md` § "Ossie interchange" (line 2032 at baseline) | Current normative export contract: three artifacts, loss report `gnd-ossie-loss/1`, sidecar `gnd-ossie-sidecar/1`, refusal of populations as `population:out-of-scope`, refusal of include-bearing models with `include:unsupported-route`. |

The reporter's three local commits (`03e690c2`, `1fea51f5`, `d7fe319c`) are not
in any repository on this machine. If the owner supplies their diffs, they are
reference material for a spec, not evidence and not reviewed code (D10).

Public text in this repository names no downstream project or customer. The
reporter's case is described here as "a large composed model". Its figures are
1,410 tables, 4,466 fact types, about 32 MiB of output, 2,269 relationships and
about 260 UNIQUE constraints.

### 1.2 Observed at baseline (not inherited claims)

- **Issue 1 is a refusal, not a truncation.** `render_ossie`
  (`src/gnd/export/ossie.py`, end of file) builds all three artifacts in
  memory. If any one is over `gnd.input_policy.MAX_BYTES` (10 MiB), it raises
  `OssieInputError("ossie:output-size")`. The command maps that to exit 3 and
  publishes nothing. No test covers this branch (`tests/test_ossie_export.py`
  has none).
- `MAX_BYTES` is the shared **input** cap of `gnd.input_policy`. The export
  reuses it as an output bound. Changing the constant would change every
  input boundary in GND, so OB1 adds a separate parameter.
- `gnd import ossie` reads at most `MAX_BYTES` (`src/gnd/ossie_import.py:66`,
  `:78`). A document exported above 10 MiB therefore cannot be imported back.
  This breaks round-trip predicate 5 of ossie-interchange for large models
  (D3).
- The export source must be a standalone model of at most `MAX_MODEL_BYTES` (10
  MiB). An include-bearing model is refused. Whether the reporter's flattened
  model is under that cap is not known (D10).
- **GND has no relational mapping today.** The component index
  (`scripts/components_index.py search relational`) and `src/gnd` contain no
  Rmap, no DDL writer and no table concept. OB2 is new code.
- The vendored `core-spec.json` `Dataset` already has `primary_key` and
  `unique_keys` (array of field lists). `Relationship` requires `name`, `from`,
  `to`, `from_columns`, `to_columns`. `Field` requires `name` and
  `expression`. Every level carries `custom_extensions`. **The UNIQUE gap that
  I2 names is therefore representable** (D4).
- `ontology/mapping.json` is not vendored. `PINNED.json` names only
  `ontology.json` and the core reference.

### 1.3 Authority

Writing this plan is not approval. The owner approves the plan at a plan gate
(record `001-plan-gate.md`) and each phase spec at its own gate before any code.
Merge, publication and any upstream contribution keep their separate
authorization.

## 2. Contract proposal and product behaviour

### 2.1 Command surface (proposal)

```text
gnd export ossie MODEL --out OUT
    [--format yaml|json] [--loss-report PATH] [--strict]        # existing
    [--max-output-bytes N]                                       # OB1
    [--ontology-only]                                            # OB3
    [--physical-binding FILE]                                    # OB4
```

- `--max-output-bytes N`: a positive integer, default `10485760`, upper limit
  set by D3 (proposed 268435456, i.e. 256 MiB). It applies to **each** artifact
  the run writes (ontology, sidecar, loss report, and in OB3 the semantic
  model and mapping). Any artifact above N refuses the whole run with
  `ossie:output-size`, exit 3, and nothing is published. This keeps today's
  all-or-nothing behaviour. It never truncates.
- `--ontology-only`: writes exactly today's three files. With D2 (a), it is
  how a caller keeps today's output.
- `--physical-binding FILE` together with `--ontology-only` is refused as a
  usage error (exit 2), because the binding has nothing to bind.

### 2.2 Output files (OB3/OB4 proposal)

| File | Schema | Bound to |
|---|---|---|
| `OUT` | Ossie `ontology/ontology.json` (pinned) | (unchanged) |
| `OUT.gnd.json` | `gnd-ossie-sidecar/1` | ontology sha256 (unchanged) |
| `OUT.loss.json` | `gnd-ossie-loss/1` | ontology sha256 (unchanged) |
| `OUT.semantic_model.<fmt>` | core-spec `SemanticModel` (pinned) | model identity in a `GND` custom extension |
| `OUT.mapping.<fmt>` | `ontology/mapping.json` (pinned, newly vendored) | ontology and semantic-model sha256, model identity, and the binding sha256 when present, in its `GND` custom extension |

Publication stays one create-once group through `safefs.publish_new_files`,
with the ontology as the last-written commit marker, as today.

### 2.3 Semantics (proposal; OB2 fixes them)

- **Rmap.** Halpin's relational mapping. Each fact type with a compound
  uniqueness constraint gets its own table. Fact types whose role is
  functional on an entity are grouped into that entity's table. Reference
  modes become key columns. 1:1 fact types are absorbed toward the mandatory
  side. Subtypes are absorbed into the supertype unless they have their own
  identification (D5). Objectified fact types become tables keyed by their
  uniqueness. A fact type the rules cannot place is unmapped, with a closed
  reason.
- **Keys.** The primary uniqueness becomes `primary_key`. Every other
  confirmed alethic uniqueness over one table's columns becomes a
  `unique_keys` entry (D4).
- **Relationships.** One per foreign key the Rmap produces, named
  deterministically.
- **Populations.** `sample_population` and `reference_populations` stay out of
  every relational file and keep their `population:out-of-scope` refusal in
  the loss report. A semantic model describes structure, not rows (D6).
- **Unrepresentable constructs** (mandatory and NOT NULL, value constraints,
  frequency, ring, subset, exclusion, derivations, deontic rules) are listed
  in the mapping's `GND` extension by fact type or constraint id with a closed
  reason. Nothing is dropped silently.

## 3. Dependencies and artifact homes

```text
OB1 ──────────────────────────────┐
OB2 → OB3 → OB4 → OB5 → close   ←─┘
```

OB1 and OB2 are independent and can run in parallel. OB5 also documents OB1.

| Artifact | Home |
|---|---|
| Output bound | `src/gnd/export/ossie.py` (`render_ossie(..., max_output_bytes=)`), `src/gnd/commands/export.py` |
| Rmap | new `src/gnd/rmap.py`, assigned in `tools/gnd_layers.json` and `dev/components/` |
| Semantic model and mapping renderers | new `src/gnd/export/ossie_relational.py` |
| Vendored mapping schema | `src/gnd/schema/ossie/mapping.json`; `PINNED.json` gains its path and sha256 |
| Binding schema | new `src/gnd/schema/physical-binding.schema.json` (schema id `gnd-physical-binding/1`, D7) |
| Binding reader | new `src/gnd/export/physical_binding.py` |
| Normative text | `src/gnd/skills/gnd-orm-core/references/representation-format.md` § "Ossie interchange" |
| User docs | `docs/explanation/ossie.md`, `docs/how-to/share-an-ossie-ontology.md`, `src/gnd/skills/gnd-export/SKILL.md` |
| Tests | `tests/test_ossie_export.py` (OB1), new `tests/test_rmap.py`, `tests/test_ossie_relational.py`, `tests/test_physical_binding.py`; oracle-lane additions in `tests/test_ossie_external_oracle.py` |

## 4. Phases

| Phase | Deliverable | Criteria | Ready |
|---|---|---|---|
| **OB1** | `--max-output-bytes N` on `gnd export ossie`, with the bound applied to each artifact. Plus, per D3, `--max-input-bytes N` on `gnd import ossie` so that large exports can be read back. | C1 byte-identical without the flag on the census. C2 a generated model whose largest artifact is above 10 MiB exports completely with `--max-output-bytes 33554432` (exit 0). C3 above N is refused with `ossie:output-size`, exit 3, nothing published; also tested at a small N. C4 the argument is refused at the CLI boundary when 0, negative, non-integer or above the ceiling (exit 2). C5 time bound for the large export. C6 (if D3 a) the large export round-trips through import with the matching input bound. | **Ready**: [draft spec](phase-OB1-spec.md). Needs D3 only. |
| **OB2** | `gnd.rmap`, a total, deterministic Halpin Rmap from a loaded model to an internal relational schema (tables, columns, PK, unique keys, FKs, unmapped list with reasons). No CLI change. Normative rules in the one home. | C1 every census model maps or refuses with a closed reason. C2 hand-derived expected schemas for a fixture corpus covering each rule (compound uniqueness, functional grouping, 1:1, subtype absorbed and separate, objectification, reference modes, n-ary), committed before the code. C3 determinism across source paths and declaration order. C4 time bound at 1,400 tables / 4,500 fact types. | Blocked on D1, D5. |
| **OB3** | Semantic-model and mapping renderers, vendored `mapping.json`, the `GND` extension, `--ontology-only`, and the default per D2. | C1 0 schema errors for all files in-process against pinned schemas. C2 the upstream validator accepts them in the opt-in oracle lane. C3 every fact type is mapped or listed (one walk). C4 byte reproducibility. C5 `--ontology-only` (and the default, under D2 b) equals the baseline. C6 `--max-output-bytes` covers the new files. | Blocked on OB2, D2, D4, D6. |
| **OB4** | `--physical-binding FILE`: schema, total reader, name resolution, normalized role matching, refusal order, unbound listing with sha256. | C1 a valid binding replaces datasets, fields, PKs and relationships, each `references` becomes a relationship. C2 each unknown-name class is refused (fact type, role, object type, table, column) with exit 3 and a named rule id, in the pinned order. C3 a contradicting binding is refused (D8 says what counts as a contradiction). C4 unbound fact types are listed with the binding sha256. C5 without the flag the output is unchanged. C6 hostile-input and time-bound tests. | Blocked on OB3, D7, D8. |
| **OB5** | Docs and skill: the normative section, the explanation, the how-to (a worked relational export and a binding), export skill guidance, changelog entry. | Docs build and link check; the normative section is the only home (the reviewer checks every cited rule). | After OB4. |
| **close** | Close record `NNN-milestone-close.md`, on merged main. | Every predicate re-run on main; panel at the project's close bar. | After OB5. |

Inherited residuals: ossie-interchange predicate 5 (round trip) is stated for
documents within the import cap; OB1/D3 decides whether it extends to large
documents. ossie-interchange OD1 and OD3 are superseded only if the owner rules
D1.

**External acceptance.** The reporter's acceptance checks ("datasets equal the
delivered DDL", "relationships equal the DDL foreign keys", 1,410/2,269) need
their model and DDL, which are not in this repository. In-repo tests use a
generated large model and a fixture DDL-shaped binding. The close record cites
the reporter's own run as external evidence only if the owner supplies it, and
labels it as such.

## 5. Documentation, skill and compatibility surfaces

- Compatibility: the existing three files keep their schemas
  (`gnd-ossie-sidecar/1`, `gnd-ossie-loss/1`). Under D2 (a), a default run now
  writes five files. A caller whose `OUT.semantic_model.*` or `OUT.mapping.*`
  already exists gets exit 10 (collision) where today's run succeeded. This is
  stated in the changelog and is why D2 is an owner ruling.
- The disclosure table: the new files carry model literals (names,
  descriptions), so they are classed like the existing Ossie surfaces
  (`every-mode`, RN0-K1). `tests/test_disclosure_mode.py` and
  `tests/test_disclosure_docs.py` are in each phase's guard gate.
- `PINNED.json` gains the `mapping.json` entry. The pin test is extended, not
  duplicated.

## 6. Risks and required controls

| Risk | Control |
|---|---|
| Rmap choices differ from the reporter's DDL, so their bundle changes when they move to upstream | D5 measured over census plus fixtures. OB4 exists exactly so a delivered schema wins over the Rmap. |
| A 256 MiB ceiling lets a single run use several hundred MiB of memory (artifacts are built in memory) | D3 ceiling. Time and memory are measured in OB1's large-model test and recorded. Streaming is out of scope. |
| Default change (D2 a) breaks scripts that rely on three files | Changelog, `--ontology-only`, collision exit is explicit. |
| Normalized role matching merges two distinct roles | D8: refuse when two roles of one fact type normalize equal. |
| The binding schema hard-codes one producer's format | D7: GND-owned schema id. The issue's member names are kept so the reporter's documents need only a schema tag. |
| Rmap on census models exposes model shapes it cannot place | Closed unmapped reasons. The census result is recorded. |

## 7. Out of scope

- DDL generation (`CREATE TABLE`) from the Rmap. The semantic model is the
  deliverable. A DDL writer is a separate request.
- Importing a semantic model or mapping (`gnd import ossie` stays
  ontology-only).
- A binding concept inside the model format (the OD3 alternative).
- Streaming or chunked output.
- Exporting include-bearing models directly. They remain refused, as today.
- Ossie metrics, dimensions and AI context.
- Upstream contributions to apache/ossie.

## 8. Execution, approval and review protocol

- `auto=false`. Each phase follows process-phase: spec, then owner gate, then
  implementation, focused tests plus the issue-171 guard list plus
  `uv run ruff check`, then independent review (one reviewer in a different
  tool), refactoring review, record `NNN-phase-OB<n>.md`, and commit with scope
  `phase-OB<n>`.
- Plan review: the project bar is the maintained panel. This plan has not been
  reviewed. The owner selects the instrument (D9).
- Branch and PR per AGENTS.md. Before each PR, run
  `python3 scripts/components_index.py changed --base main --strict`.

## 9. Per-phase verification story and affected consumers

| Phase | Focused gate (plus the guard list and ruff) | Affected consumers |
|---|---|---|
| OB1 | `uv run pytest -q tests/test_ossie_export.py tests/test_ossie_import.py --tb=short` | `commands/export.py`, `commands/checking.py` (import CLI), disclosure tables |
| OB2 | `uv run pytest -q tests/test_rmap.py --tb=short` | `tools/gnd_layers.json`, component index |
| OB3 | `uv run pytest -q tests/test_ossie_export.py tests/test_ossie_relational.py --tb=short`; opt-in oracle lane named, not run by default | Ossie docs, disclosure tables, `PINNED.json` test |
| OB4 | `uv run pytest -q tests/test_physical_binding.py tests/test_ossie_relational.py --tb=short` | as OB3 |
| OB5 | docs link check named in the OB5 spec | site |

Baseline expectations: today's census export is the byte reference for OB1-C1
and OB3-C5. It is captured at OB1 start from `1926e895` and committed as
digests only.

## 10. Owner decisions and open questions

All open at r1.

| ID | Question | Proposal | Cost of the alternative |
|---|---|---|---|
| D1 | Reopen ossie-interchange OD1 ("ontology only") and OD3 ("physical bindings not now") to take issues 2 and 3? | Yes. OD1 (b), and OD3 through an **external** binding file, which needs no model-format change. | Not reopening leaves only OB1 in this milestone. |
| D2 | Default output: five files by default with `--ontology-only` to opt out (the issue's request), or three by default with an opt-in flag? | (a) as requested, **provided** OB2's census shows the Rmap is total on every census model. If it is not, (b). | (a) a default run can newly fail (collision, or Rmap refusal) where it succeeded. (b) the reporter must add a flag. |
| D3 | Ceiling for `--max-output-bytes`, and does `gnd import ossie` get a matching `--max-input-bytes` in OB1? | Ceiling 256 MiB. Yes to import, so a large export can be read back. | No import flag: large documents export but cannot round-trip. |
| D4 | UNIQUE constraints in the semantic model | Write non-primary confirmed alethic uniqueness as `Dataset.unique_keys`, which the pinned core-spec supports. Uniqueness spanning tables goes to the `GND` extension. | Leaving them out keeps the ~260-constraint gap the issue reports. |
| D5 | Rmap variants: subtype absorption versus separate tables; 1:1 absorption direction | Halpin defaults (absorb, toward the mandatory side), settled by measurement in OB2. | A per-run policy flag adds a test matrix. |
| D6 | Behaviour with `sample_population` | No rows in any relational file. Keep the existing loss-report refusal. Same output with or without a population. | Emitting rows is a different Ossie layer and out of scope. |
| D7 | Binding schema identity | GND-owned `gnd-physical-binding/1`, with the issue's member names (`tables`, `columns`, `sql_type`, `targets`, `references`, `primary_key`, `roles`, `extension_roles`). | Accepting a producer-named schema id ties GND's public schema to one caller. |
| D8 | Role-name normalization and contradictions | Unicode casefold plus removal of non-alphanumeric characters. Refuse a fact type whose roles collide after normalization. Contradictions: a column targeting two fact types with incompatible keys, a `references` to a non-key column set, a PK column bound to a non-identifying role. | A looser match silently binds the wrong role. |
| D9 | Plan-review instrument | Light maintained panel over this plan and the OB1 spec, like ossie-interchange. | Unreviewed approval is the owner's call and is recorded as such. |
| D10 | Reporter inputs | Ask for the three local diffs (reference only), the size of their flattened model, and whether they can run the external acceptance. File the three issues on GitHub so the records can link them. | Without them, external acceptance stays missing evidence. |
