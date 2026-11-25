# OB4 corpus: physical bindings

A physical binding tells `gnd export ossie --physical-binding FILE` which
tables the caller actually delivers and where they hold the model's roles.
This corpus was **hand-written before any binding reader existed** (OB4 spec
§11, decision G18). The owner approves it at the OB4 corpus gate, together
with the format itself:
[physical-binding.schema.json](../../../src/gnd/schema/physical-binding.schema.json).

## Valid cases

Each has `binding.json`, the files the export must then write
(`expected.semantic_model.yaml`, `expected.mapping.yaml`), a readable copy of
the mapping's `GND` extension (`expected.extension.json`), `case.json` naming
its model in `tests/fixtures/rmap/cases`, and a `STORY.md`.

| Case | Model | Shows |
|---|---|---|
| [V1](V1/STORY.md) | 01 functional binary | renamed table and columns; SQL types; a home table; one link |
| [V2](V2/STORY.md) | 04 many-to-many | three tables with schema-qualified names; two foreign keys |
| [V3](V3/STORY.md) | 14 external identification | a composite key; a two-column foreign key as one relationship |
| [V4](V4/STORY.md) | 14 again | one fact type left unbound; one bound only in `extension_roles` |
| [V5](V5/STORY.md) | 13 candidate keys | a declared unique key; a model uniqueness the binding does not declare |
| [V6](V6/STORY.md) | 01 | role names matched ignoring case and punctuation; SQL types in another spelling |
| [V7](V7/STORY.md) | 13 again | no `unique_keys` member, so one is derived from the model |

## Refusals

[refusals.json](refusals.json) lists 50 bad bindings and the refusal each
must produce. Every row exits 3, names its rule id on standard error and
publishes nothing. A row is one of:
- `base` and `patch`: an RFC 6902 patch of a valid case's `binding.json`;
- `raw`: the literal file text;
- `generate`: a file the test builds (a directory, a file over the size cap,
  65 nested arrays, a 5,000-digit integer, a byte that is not UTF-8).

| Step | Rule ids | Rows |
|---|---|---|
| The file cannot be read as JSON | `binding:not-a-file`, `binding:size`, `binding:syntax` | 9 |
| The JSON is not a binding | `binding:schema` | 12 |
| A name does not resolve | `binding:name-collision`, `binding:unknown-table`, `binding:unknown-column`, `binding:ambiguous-column`, `binding:unknown-fact-type`, `binding:role-name`, `binding:unknown-role`, `binding:unknown-object-type` | 19 |
| The binding contradicts itself or the model | `binding:reference-group`, `binding:reference-not-a-key`, `binding:partial-fact-type`, `binding:role-arity`, `binding:target-mismatch`, `binding:key-role`, `binding:incompatible-keys` | 10 |

## Conventions

- **OUT** is `ontology.yaml`, as in the OB3 corpus.
- **Datasets** are in sorted table-name order. **Fields** are in the
  binding's own column order.
- **A foreign key** is the columns of one table whose `references` are equal.
  They pair with the referenced columns in the table's column order.
- **A role played by an entity** lists one column per part of that entity's
  identifier, in the ontology's `identify_by` order.
- **Identifiers in expressions** are quoted and uppercased, whole:
  `"UNI.STUDENT"."NR"` names field `nr` of dataset `uni.student`.
- **Digests** in each extension: `binding_sha256` is the digest of
  `binding.json`; the others are as in the OB3 corpus.

## Known limit: surrogate keys

A role played by an entity is bound to columns that hold that entity's
identifying values. A table that points at another only through a generated
id (a surrogate key the model does not know) has no such columns, so that
fact type cannot be bound and is listed as `unbound`. Its foreign key still
appears as a relationship. See the spec's amendment, K13.

## Authoring checks

```bash
uv run python -m tests.support.physical_binding_corpus
```

It checks every valid case against the packaged binding schema, the pinned
Ossie schemas, the real ontology export and the model, and every refusal row
against the step its rule belongs to. It reads no binding the way the
product will.
