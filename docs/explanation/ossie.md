# Ossie interchange in GND

GND exports and imports Apache Ossie ontology documents, version
`0.3.0.dev0`. The validator and schema are pinned to Apache Ossie
`ee89dbdc2844d8b7d293ed42c8613928bb99505f`. The parser and optional
RelationalAI converter are pinned to Apache Ossie Converters
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
those details when the sidecar is present. A foreign ontology imports
through the supported projection and gets its own loss report.

GND keeps its `Duration` type, which counts whole days. Ossie receives an
integer value type and the sidecar preserves its original GND meaning.
The export report also records omissions, such as example populations.
Use `--strict` when any refusal should stop the export.

## Where PyRel fits

PyRel is optional. You can export and import using GND alone. In the
offline check with RelationalAI 1.39.0, the pinned converter matched
the compared declarations for 36 of the 38 eligible exports. The other
two exposed limits involving inherited identifiers and a derivation
chain. The converter also omitted `requires` expressions from its output.

GND can generate its own PyRel rules for supported models. The converter
check compares the emitted declarations, and GND checks formula cases
against hand-authored verdicts. Those checks cover different behavior.

- [Share the refunds example](../how-to/share-an-ossie-ontology.md)
- [What PyRel is, and when you need it](what-is-pyrel.md)
