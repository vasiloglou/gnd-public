# Literature regression corpus

A small public corpus for measuring how well a literature pipeline reads
scientific papers. A staged assurance report scores a run of that pipeline
against an answer key, and keeps each stage's denominator separate. It is the
public reconstruction of the known-error set in issue 193, part 1. Larger
sets stay with whoever owns them, and can be scored with the same report.

The documents are **synthetic paraphrases** of public works, written for
regression testing. Each names its work's public identifier, and each
identifier was checked against its public record on 2026-11-15. No document
is the text of its work.

This directory is the entry point, and it holds no labels. The answers are in
[`answers/`](answers/), kept apart so the corpus can be handed to a reader
without them.

## What is here

| Path | What it is |
|---|---|
| `model.orm.yaml` | The flat corpus model. A method is identified by the name a document uses, as in the host graph the issue reports |
| `corpus/corpus.json` | The corpus manifest (`literature-corpus/1`): documents, their digests and splits, and every passage |
| `corpus/documents/*.md` | One document per work: a title line, an identifier line, then one passage per line |
| `corpus/artifacts/` | `gnd extract` output for the model, which `gnd fidelity` needs |
| `runs/reference/` | The faithful reference run (`literature-run/1`). It must score exit 0 |
| `expected/` | The approved expected outcome of each scored case (`literature-assurance-expectation/1`) |
| `answers/` | The answer key, gold populations and renderer manifests. Not for blind readers |

Every generated file is rebuilt, byte for byte, by
`tools/build_literature_example.py` in the source repository.

## Formats

This section is the one home of the formats below. Every other mention cites it.

### `literature-corpus/1`

- **`model`, `model_sha256`:** the model file and its digest.
- **`artifacts`:** the `gnd extract` bundle path, plus the digests of its
  applicable set and projection.
- **`documents[]`:** each document's `id`, `path` and `sha256`.
  - `domain`: the document's field.
  - `split`: `dev` or `heldout`.
  - `paraphrase`: always `true`.
  - `work`: the work's `identifier`, `title` and `year`.
- **`passages[]`:** `id` (`<document>.p<n>`), `document` and `span` (`start`
  and `end`, half-open character offsets into the NFC text). Line 1 is the
  title and line 2 the identifier; every later line is one passage.

### `literature-answer-key/1`

- **`corpus_sha256`:** the SHA-256 of the `corpus.json` bytes.
- **`labeller`:** who wrote the labels. `independent` is `false` here.
- **`assertions[]`:** one passage-level claim each.
  - `passage`, `participants`, and `predicate` in plain words.
  - `support`: one of `supported`, `stretched`, `contradicted`,
    `insufficient-evidence`.
  - `fact`: the claim in the flat model.
  - `label_disagreement`: `null` when the labellers agreed.
- **`anchored_facts[]`:** every anchored role of a gold fact, with `source`,
  `fact`, `role`, `passage` and its gold `span`.
- **`populations[]`:** each source's `expected_check_exit` under plain
  `gnd check`.
- **`chains[]`:** labelled lineage paths, kept here for the lineage phase.
  - `label`: `supported` or `false`.
  - `story` and `domains` (`same` or `cross`).
  - `edges`: assertion ids.
  - `merges`: identity pair ids that a false merge needs.
  - `path`, `passages` and `reason`.
- **`reuse_cases[]`:** names reused across works. `kind` is one of `real`,
  `generic-word`, `homonym`.
- **`identity_pairs[]`:** cross-source key pairs, each a `left` and a `right`
  key (`source`, `object_type`, `value`). `label` is `same` or `different`.
- **`name_pairs[]`:** pairs of names. `kind` is one of `homonym`, `synonym`,
  `family`.
- **`heldout`:** the SHA-256 of the held-out answer key, and its chain counts.
  The held-out key itself is not in this branch.

### `literature-run/1`

```
run.json        {"schema": "literature-run/1", "corpus_sha256": "...",
                 "sources": [...], "abstentions": ["<passage id>", ...]}
composition/    a gnd compose directory: manifest.json, and per source
                document.txt, population.json, population.json.anchors.json,
                population.json.extraction.json
composed/       population.json and record.json written by gnd compose
```

A run abstains on a passage by listing its id. A run may not anchor a fact
inside a passage it abstains on.

### `literature-assurance-report/1`

The report written by the harness. Its fields are specified in the phase
spec, §6.3, until the harness lands. This section will then hold them.

### `literature-assurance-expectation/1`

The approved outcome of one scored case:
- `exit_code` and `failed_stages`, in stage order;
- per stage, its `status` and the numerator and denominator of every floored
  metric (`agreement`, `precision`, `recall`, `abstention`);
- `refused_units`, `route_refused` and `counts_as_failure` where they apply.

A report for that case must agree with every value given.

## The stages

The stages are, in order:
1. `model-population-validity`
2. `source-binding`
3. `semantic-support`
4. `identity-decisions`
5. `derivation`
6. `coverage`
7. `freshness`

`identity-decisions` and `coverage` are not measured yet. Their owners are the
sense-resolution phase and the reading-coverage milestone.
