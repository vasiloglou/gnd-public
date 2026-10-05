# Check facts extracted from documents

Use GND when a report, form, memo, or article needs to become structured facts
that can be checked against domain rules. Keep two questions visible:
“Do these facts satisfy the model?” and “Did the extraction faithfully capture
the document?” A checker pass answers the first question; extraction fidelity
needs its own evidence.

## Prepare the extraction vocabulary

With an authored, supported non-temporal model, this contextual command emits
the extraction bundle:

```sh
gnd extract model.orm.yaml --out artifacts
```

The bundle includes a shape-only JSON Schema projection, a constraint-blind
verbalization, an applicability description, and an index that binds their
digests and header template. It is produced offline. `gnd extract` does not
read the source document or call a model provider.

The extraction schema describes which facts and values can be represented.
It deliberately does not tell an extractor how to rewrite facts to satisfy
uniqueness, mandatory, or other domain rules. If a document describes an
invalid application state, the extraction should preserve that state so the
checker can reveal it.

## Ask an agent to extract, then verify its output

In an agent session with the GND skills installed, explicitly select the
extraction workflow. Example prompt; replace the named files with your own:

```text
Use gnd-extract with model.orm.yaml and artifacts/ to extract report.md into
extracted.population.json. Preserve the document's facts, including facts
that violate the model. Write the required digest-bound extraction sidecar,
then run the verifier and explain its findings.
```

The skill treats the document as quoted data. Instructions, links, and code
inside it are content to interpret, not commands to follow. The agent writes
the population and its adjacent extraction sidecar. The sidecar records the
model, document, projection, and population binding.

Given those completed artifacts, the contextual verification command is:

```sh
gnd verify model.orm.yaml extracted.population.json --artifacts artifacts --format json
```

Verification validates the handoff before checking the population. Missing,
malformed, or stale sidecars produce input refusal at band `3`. Read the
`extraction` block and the semantic verdicts independently. If your population
was authored directly and never extracted, explicitly use `--no-extraction`;
the report records that the extraction path was skipped.

## Bind important values to source spans

An `anchored` constraint checks whether populated role values have witnesses
in a bound source document. The anchor sidecar names a fact occurrence, role,
source span, and the necessary digests. Contextual snapshot command:

```sh
gnd check model.orm.yaml extracted.population.json --anchors extracted.population.anchors.json --document report.md --format json
```

A malformed binding is refused. An absent or unsuitable witness can be a
failure or an unchecked result depending on the situation and modality. The
matcher uses documented lexical normalization and explicit numeric/date
recognizers; it does not infer arbitrary paraphrase equivalence. Source
anchoring provides specific occurrence evidence, not a blanket truth claim.

## Test a round trip without hiding failures

For an extraction evaluation, explicitly select `gnd-render-doc` to turn a
known population into prose. That workflow preserves all applicable source
facts, plants three kinds of distractors, and writes a document manifest.
`gnd doccheck` checks that rendering contract. Then separately select
`gnd-extract` to read the document back, and measure the retained round-trip
cases with `gnd fidelity`.

These outputs remain different evidence: rendering completeness, extracted
population checking, and measured fidelity. Saved extraction outputs or
synthetic receipts are not evidence that a provider ran now.

See the [extraction contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-extract/references/extraction-contract.md)
and [rendering contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-render-doc/references/rendering-contract.md)
for exact sidecars, manifests, distractors, and failure semantics.
