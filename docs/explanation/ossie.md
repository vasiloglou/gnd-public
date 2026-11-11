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

The supported scope is the ontology layer. It covers concepts, their
relationships and a documented subset of constraint formulas. Ossie's
semantic models, mappings and query interfaces are outside this scope.

!!! info "Files on GitHub"

    [Normative mapping and file format](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/representation-format.md#ossie-interchange)

## Share an ontology and keep the original details

Use `gnd export ossie MODEL --out ONTOLOGY.yaml` to share the ontology.
The sidecar preserves GND details, and the loss report shows how each
source field was handled. Keep the sidecar beside the ontology for a
GND round trip. `gnd import ossie ONTOLOGY.yaml --out MODEL.json` restores
those details when the sidecar is present. What the export omitted stays
omitted: a model with example populations comes back without them. A foreign
ontology imports through the supported projection and gets its own loss report.

GND keeps its `Duration` type, which counts whole days. Ossie receives an
integer value type and the sidecar preserves its original GND meaning.
The export report also records omissions, such as example populations.
Use `--strict` when any refusal should stop the export.

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
