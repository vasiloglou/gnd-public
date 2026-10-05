# Documents in, documents out

Much enterprise data arrives as prose: reports, forms, emails, contracts. GND treats a
document as **quoted data**. An agent extracts facts from it into a population that the
model checks, and the agent never follows instructions written inside the document.
The reverse direction, rendering a document from known facts, gives you test material
whose ground truth you control.

## Read a document into facts

```text
Use gnd-extract with model.orm.yaml and artifacts/ to extract report.md into
extracted.population.json. Preserve the document's facts, including facts that
violate the model. Write the digest-bound extraction sidecar, then run the verifier
and explain its findings.
```

1. `gnd extract model.orm.yaml --out artifacts` writes the extraction vocabulary: a
   shape-only JSON Schema, a constraint-blind verbalization and a header template. It
   runs offline and never reads the document.
2. The agent writes `extracted.population.json` and a sidecar that binds the model,
   the document and the vocabulary by digest.
3. `gnd verify model.orm.yaml extracted.population.json --artifacts artifacts` checks
   the handoff first (a missing or stale sidecar is refused at band 3), then the facts.

The vocabulary is deliberately *constraint-blind*. If the document describes an invalid
state, the extraction must preserve it so that the checker can reveal it. The agent is
not told how to make the facts pass.

To pin important values to the text, an `anchored` constraint checks that each value
has a witness span in the bound source document
(`gnd check … --anchors … --document report.md`).

## Write a document from facts

```text
Use gnd-render-doc to render a status report from seed.population.json for
model.orm.yaml. Plant all three distractor kinds, write the manifest, and run doccheck
until it passes.
```

The skill reads the population and its verbalization (never the model file), writes
`document.md`, and plants three kinds of **distractors** so that an extractor which
grabs everything in sight is caught:

| Kind | Example |
|---|---|
| out-of-model | "The offsite was rained out, so the review moved to Thursday." |
| near-miss entity | a second "Ada Lovelacé" who plays no role in any fact |
| absent fact | "There was talk of putting Grace on the glass project, but it never happened." |

`gnd doccheck model.orm.yaml document.manifest.json --artifacts artifacts` verifies
the rendering obligations: every applicable fact is mentioned, and every recorded
distractor really appears in the text and is really absent from the source facts.

## Measure the round trip

Render, extract and compare: `gnd fidelity` measures, per fact type, how faithfully
extraction recovered the source population across committed round-trip cases. It keeps
three questions separate: whether the rendering was complete, whether the extracted
facts satisfy the model, and whether the extraction was faithful.

The [documents guide](../guides/documents.md), the
[extraction contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-extract/references/extraction-contract.md)
and the
[rendering contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-render-doc/references/rendering-contract.md)
define the exact sidecars, manifests and failure semantics.
