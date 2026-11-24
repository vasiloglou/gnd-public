# OB3 corpus: expected semantic models and mappings

Seven cases of the OB2 Rmap corpus (`tests/fixtures/rmap/cases`), each with the
files `gnd export ossie` must write next to the ontology. They are
**hand-derived** and were written before any renderer existed (OB3 spec §11,
decision E2). The owner approves them at the OB3 corpus gate.

| Case | Model | Shows |
|---|---|---|
| [01](01/STORY.md) | functional binary | one dataset; a simple-identifier object mapping; one link mapping |
| [04](04/STORY.md) | many-to-many | a table of its own; two foreign keys as two relationships |
| [09](09/STORY.md) | unary | a Boolean field; a unary link through `CASE WHEN` |
| [14](14/STORY.md) | external identification | a composite key; nested referent mappings; a two-column foreign key |
| [15](15/STORY.md) | subtype | an absorbed subtype with no object mapping |
| [17](17/STORY.md) | objectification | an objectified fact type keyed by its two roles |
| [18](18/STORY.md) | derived | a computed fact type listed, not mapped |

## Files in each case

| File | What it is |
|---|---|
| `STORY.md` | what the two files must show, in plain words |
| `expected.semantic_model.yaml` | the expected `OUT.semantic_model.yaml`, byte for byte |
| `expected.mapping.yaml` | the expected `OUT.mapping.yaml`, byte for byte |
| `expected.extension.json` | the mapping's `GND` extension, pretty-printed for reading. The string in the mapping is its canonical JSON. |

## Conventions

- **OUT.** The expected bytes assume the ontology is written to a file named
  `ontology.yaml`, so the mapping's references read `./ontology.yaml` and
  `./ontology.yaml.semantic_model.yaml`.
- **Identifiers in expressions** are quoted and uppercased: `"CUSTOMER"."EMAIL"`
  names field `email` of dataset `customer` (decision E5).
- **A NULL gives no link** (decision E8). A nullable column is mapped like any
  other; a row where it is NULL contributes no link.
- **Trees are not shared.** Each fact type has its own link mapping tree, so a
  concept's key expression repeats once per fact type.
- **Long strings are folded** by the YAML dumper. The extension string and the
  `CASE WHEN` expression are single-line values that the file shows on
  several lines.
- **Digests.** In the extension, `ontology_sha256` is the digest of today's
  ontology export for the model, `model_identity` is `gnd.values.model_identity`,
  and `semantic_model_sha256` is the digest of `expected.semantic_model.yaml`.
  `dispositions` is the owner-approved OB2 answer for the case, unchanged.

## Authoring checks

`tests/support/ossie_relational_corpus.py` checks the corpus without rendering
anything: the pinned schemas accept every file; each semantic model equals
the OB2 answer table for table; every expression names a declared field;
every link names a relationship of its concept at the level its arity calls
for; the carried fact types are exactly the link-mapped ones; and the
extension's digests are right.

```bash
uv run python -m tests.support.ossie_relational_corpus
```

It reads Ossie's `ontology/mapping.json` as vendored at the pinned commit
(`src/gnd/schema/ossie/mapping.json`). `tests/test_ossie_relational.py` holds
the same cases against the renderer.
