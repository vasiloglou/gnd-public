# Models, populations, and evidence formats

GND artifacts answer different questions and have different versioned
contracts. Keep them separate even when they refer to the same model. A model
version, a report schema version, and the package version are independent
identities.

## The two starting artifacts

A **model** declares object types, fact types, constraints, provenance, and
optional operations, derivations, and fixed references. A **population**
provides instances and facts for that vocabulary and declares what it covers.
Both accept the supported YAML/JSON representation; a `.json` suffix does not
turn a file into a different semantic model.

`population.model` is a model reference label; `model_id`, when declared,
checks compatible identity. Neither means “open any path written inside this
data.” Pass the actual model explicitly to the API or command. Coverage says
which fact types the population addresses. An absent relation is not silently
equivalent to a deliberately covered empty relation.

Use complete tutorial checkpoints as starting examples. A schema fragment in
a guide illustrates one construct and is not a complete loadable model.

## Canonical references

| Artifact or concern | Authoritative reference |
|---|---|
| Model YAML/JSON, operations, derivations, temporal terms, references | [Representation format](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/representation-format.md) |
| Constraint families and checkability | [Constraint reference](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/constraint-reference.md) |
| Populations, typing, coverage and verdict bands | [Population format](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/population-format.md) |
| Rule origins, proposal status and modality | [Provenance and modality](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/provenance-and-modality.md) |
| Structural model and population schemas | [Model schema](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/schema/orm-meta.schema.json), [population schema](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/schema/population.schema.json) |
| Operation invocation walk | [Steps schema](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/schema/steps.schema.json) and the representation format's walk contract |
| Check/report variants | [Report schema](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/report.schema.json) |
| Model comparison | [Diff contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/diff.reference.md), [diff schema](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/diff.schema.json) |
| Generated project and ownership | [Codegen contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-codegen/references/codegen-contract.md) |
| Static declarations and runnable smoke rows | [Architecture contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-codegen/references/architecture-contract.md) |
| Project agreement findings | [Conformance contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-conformance/references/conformance-contract.md) |
| Change proposals, previews and records | [Evolution contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-model-evolve/references/evolution-contract.md) |
| Recovered-code evidence | [Recovery contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-model-from-code/references/recovery-contract.md) |
| Extraction sidecars and document manifests | [Extraction contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-extract/references/extraction-contract.md), [rendering contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-render-doc/references/rendering-contract.md) |
| Session contracts and outcomes | [Session skill](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-dev-session/SKILL.md), [v7 contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-dev-session/references/session-v7-contract.md), [v8 judgments](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-dev-session/references/judgment-contract.md) |
| Finite witnesses and bounded native bundles | [Witness contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-export/references/witness-contract.md), [export contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-export/references/export-contract.md) |

These links point into the repository's maintained specification and schema
sources. For a released integration, consult the same paths at the tag/commit
matching your installed package rather than assuming `main` is that version.

## Bind bytes without confusing the identities

Some identities bind normalized model/population representations; others bind
the raw file bytes. The format says which applies. Fixed-reference `sha256`
pins, for example, bind exact raw files; changing whitespace changes the pin.
Transition `model_digest` and `operations_digest` have different bases.
Obtain them from `gnd validate MODEL --trace`, rather than hashing the whole
model file and guessing.

An input refusal after a file change is useful information: the old evidence
described other bytes. Re-author or regenerate the appropriate dependent
artifact deliberately. Do not merely replace a digest to label old evidence
current without rerunning the step that produced it.

## Consume the right report

Check JSON, a session outcome, a conformance report, a witness certificate,
and a review synthesis are not interchangeable success records. Read the
schema version and command family first, then its findings and bindings.
Reference-aware reports can wrap the mechanical report, while the base diff
schema has its own shape. Use the [API examples](python-api.md) for concrete
access patterns rather than reaching into private evaluator internals.
