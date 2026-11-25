# Ossie interchange in GND

Apache Ossie is an open source project that defines a file format for
ontologies, meaning the business concepts in a domain and the relationships
between them. If an Ossie ontology already exists for your domain, you can
import it and use its concepts and relationships as the starting point for a
GND model. If your model lives in GND, as the refunds example does, you can
export its vocabulary and relationships so that another tool or team works
from the same names and connections.

GND supports Ossie ontology version `0.3.0.dev0`. The export schema and
validation tool come from Apache Ossie
`ee89dbdc2844d8b7d293ed42c8613928bb99505f`. The parser used for the
export check comes from Apache Ossie Converters
`83ddc294c8840f5f497a2bdbec2348a128fc2254`.

An export covers three Ossie layers. The **ontology** holds concepts, their
relationships and a documented subset of constraint formulas. The **semantic
model** describes tables that hold the model's facts. The **mapping** says
which table and column holds each concept and relationship. Import reads
the ontology only. Ossie's metrics, dimensions and query interfaces are
outside this scope.

!!! info "Files on GitHub"

    [Normative mapping and file format](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/representation-format.md#ossie-interchange) ·
    [Relational mapping rules](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/representation-format.md#relational-mapping-rmap)

This page explains what the export does and why. The rules themselves have
one home, the two sections linked above.

## Share an ontology and keep the original details

Use `gnd export ossie MODEL --out ONTOLOGY.yaml` to share the ontology.
The sidecar preserves GND details, and the loss report shows how each
source field was handled. Keep the sidecar beside the ontology for a
GND round trip. `gnd import ossie ONTOLOGY.yaml --out MODEL.json` restores
those details when the sidecar is present. What the export omitted stays
omitted: a model with example populations comes back without them. A foreign
ontology imports through the supported projection and gets its own loss report.

An export is the model's own text. A fact type or role marked `redact` keeps
its reading, constraints and provenance text in the export, in every
[disclosure mode](../reference/disclosure.md): `redact` withholds population
values from reports, and an export carries no population. The command prints a
note with the number of fact types that declare `redact`, so you can decide
before you share the files.

GND keeps its `Duration` type, which counts whole days. Ossie receives an
integer value type and the sidecar preserves its original GND meaning.
The export report also records omissions, such as example populations.
Use `--strict` when any refusal should stop the export.

## The tables an export describes

A GND model states facts: a refund is requested by a customer, a refund is
for an amount. A database stores facts in tables. The export works out a set
of tables for the model and writes them as the semantic model.

The method is the standard one for this kind of model:

- A business object that has facts of its own gets a table. Its key is the
  way the business identifies it, such as a refund number.
- A fact that can hold only once per object becomes a column of that
  object's table. If each refund has at most one requesting customer, the
  customer is a column of the refund table.
- A fact that can hold many times gets a table of its own, linked back by a
  foreign key.
- A uniqueness rule that fits inside one table becomes a key of that table.

The result depends only on the model, so two exports of the same model give
the same bytes.

These tables are GND's reading of the model, not tables anyone has built.
Each one carries the marker `"source_kind":"logical"`, so that a reader does
not take its name for a real table in a warehouse. The semantic model and
the mapping are written beside the ontology, as `OUT.semantic_model.<fmt>`
and `OUT.mapping.<fmt>`. Add `--ontology-only` to write the ontology, sidecar
and loss report without them.

GND checks the semantic model and the mapping against the pinned Ossie
schemas before it writes them.

## What is listed instead of mapped

Tables carry facts, keys and links. They do not carry every rule, and a few
shapes do not fit Ossie's mapping format. Nothing is dropped silently. The
mapping file holds a list, under its `GND` extension, of every fact type and
every constraint in the model. Each entry says where it is carried, or gives
a reason it is not. The reasons you are most likely to meet:

| Reason | What it means |
|---|---|
| `not-relational` | A rule over values or across facts, such as a spending limit. A table definition cannot state it. It stays in the sidecar. |
| `uniqueness-not-confirmed` | A uniqueness rule that is not both confirmed and a hard rule of the domain (alethic), so it is not written as a key. A confirmed rule that people are only expected to follow (deontic) is listed this way too. |
| `spans-tables` | A rule whose facts ended up in more than one table. |
| `derived-computed` | A fact that is worked out from others and not stored. |
| `identification-differs` | The ontology and the tables identify an object in different ways, so the link between them is not written. |
| `arity-over-limit` | A fact type with more than 32 roles. It keeps its table, and the mapping does not link it. |

Three limits follow from the same principle of listing and not guessing:

- A model that yields no table at all writes the ontology's three files and
  prints a note, because an Ossie semantic model needs at least one table.
- An object identified through a chain of more than 8 other objects is
  treated as one the ontology does not identify.
- A fact type with more than 32 roles is listed, as the table shows.

## Describe the tables you delivered

The tables above are a proposal. If you have already built your schema, with
your own table and column names, give the export a **binding file** with
`--physical-binding FILE`. The binding lists your tables and says which
columns hold which roles of the model. The semantic model then describes
your tables, marked `"source_kind":"physical"`, and the mapping points at
your columns.

A binding does not need to cover the whole model. Fact types it does not
mention are listed with the reason `unbound`. A binding that contradicts the
model, for example by naming a role the fact type does not have, is refused
with a rule id that starts with `binding:`, and nothing is written.

One limit matters when you plan a binding: a role has to be bound to
columns that hold the model's own identifier for the object. A fact that a
table holds only through a generated surrogate key cannot be bound. It is
left out and listed as `unbound`, while the table and its foreign key are
still described.

Without the option, an export is exactly what it was.

- [Describe your delivered tables](../how-to/describe-delivered-tables-for-ossie.md)

## Large models

Each written file may be at most 10 MiB by default. A large model, such as
one composed from many shared vocabularies, can exceed that. The export then
stops with `ossie:output-size` and writes nothing. Raise the bound for that
run with `--max-output-bytes N`, a number of bytes up to 256 MiB.

Import has the matching option. `gnd import ossie` reads documents up to
10 MiB unless `--max-input-bytes N` sets another bound.

Neither option changes the limit on the model file itself, which stays at
10 MiB.

## Where PyRel fits

PyRel is optional. You can export and import using GND alone. The offline
check used the same Ossie Converters commit with RelationalAI 1.39.0.
It generated PyRel source for 36 of the 38 eligible exports. Concept
names, parent links, relationship names and identifier links matched the
exported declarations. The converter refused one inherited identifier,
and the SDK could not generate source for one derivation chain. The
emitted source contained no `require` calls.

GND can generate its own PyRel rules for supported models. The formula
test corpus compares GND checker results with hand-authored verdicts,
and the Ossie parser checks the corresponding formula syntax. Executing
Ossie formulas is outside the scope of those checks.

- [Share the refunds example](../how-to/share-an-ossie-ontology.md)
- [What PyRel is, and when you need it](what-is-pyrel.md)
