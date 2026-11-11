GND — Get Nick Done is a framework for building agentic data apps grounded in ORM conceptual models. Agents produce structured facts and plans; GND checks them against modeled rules with its deterministic Python engine.

0.3.0 is the third package release. Its main addition is Apache Ossie interchange:

- **`gnd export ossie MODEL --out ONTOLOGY.yaml`** shares a model as an Apache Ossie ontology, with a sidecar that keeps the GND details and a loss report that lists how each source field was handled. See [Ossie interchange in GND](https://github.com/vasiloglou/gnd-public/blob/v0.3.0/docs/explanation/ossie.md).
- **`gnd import ossie ONTOLOGY.yaml --out MODEL.json`** starts a model from an ontology, or restores what an export kept when its sidecar is present. See [Share a refund model as an Ossie ontology](https://github.com/vasiloglou/gnd-public/blob/v0.3.0/docs/how-to/share-an-ossie-ontology.md).
- An export writes the model's constraint literals and description text in every disclosure mode, also for a fact type marked `redact`. Read the loss report before you share an export.

The release also includes the other changes made since 0.2.0: shared vocabularies with project-owned policies (model format version 5), a model identity a caller can recompute (`gnd validate --identity`), plain text for redaction and temporal models, constraints admitted on clean data (`--check-population`), counted unchecked source spans (`--require-documents`), and source documents declared inside a growth round.

Some entries change behavior or are not readable by 0.2.0: a version 5 model, a proposal that declares a source document or re-pins an include, a preview with a population check, and a stricter additive rule for constraints written inside a fact type. The [release notes](https://github.com/vasiloglou/gnd-public/blob/v0.3.0/docs/release-notes.md) list each one.

Install with `uv tool install get-nick-done==0.3.0`. The wheel, the sdist and their checksums are attached.
