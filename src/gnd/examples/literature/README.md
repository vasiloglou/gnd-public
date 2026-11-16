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

The report written by `python -m gnd.examples.literature.assurance_report
CORPUS ANSWERS RUN [--out PATH]`, where CORPUS is this directory.

**Exit codes.** The process exits with the report's `exit_code`:
- 0 when every active stage is `pass`;
- 1 when any active stage is `fail`, or `not-measured` because the run left
  out a route's input;
- 3 when the harness refuses an input.

**A refused input** gets `stages: []` and a `reason`. The reasons, in
validation order:
1. `input:unreadable`, `input:too-large` (every document is capped at 4 MiB
   on read), `input:not-json` (no NaN, depth at most 64, integers at most 128
   digits);
2. `input:schema`;
3. `corpus:digest-mismatch`, `run:corpus-mismatch`;
4. `run:unknown-source`, `run:document-mismatch`, `run:unknown-passage`,
   `run:abstained-passage-asserted`;
5. `internal`, for anything unforeseen.

**Top-level fields:**
- `schema`, `exit_code` and `reason` (`null` when scored);
- `inputs`: `corpus_sha256`, `answers_sha256`, `run_sha256` (a digest over
  every file of the run), `gnd_version` and `harness_sha256`;
- `labels`: the answer key's labeller `kind`, `independent` and `note`;
- `stages`: the seven stages, in order;
- `failed_stages`, in stage order;
- `not_measured`: each stage not measured, with its owner;
- `unscored_labels`: the label groups this report does not score, with their
  counts and owners.

**Fields of each active stage:**
- `status`: `pass`, `fail` or `not-measured`;
- `owner`: `null`, or `run` when the run left out the stage's route input;
- `failed_floors`: names from `agreement`, `precision`, `recall`,
  `abstention`, `refused` and `route-refused`;
- `unit`, `sample_size`, `exclusions` and `unresolved`;
- `disagreements`: `count` and `units`;
- `label_disagreements` and `refused_units`;
- `floor`: each floor as an exact fraction, where a `_max` key is an upper
  bound;
- `routes`: each route's `argv`, shown relative to the inputs, and its
  `exit`;
- `route_refused`, set when the stage's whole route refused;
- the metrics `agreement`, `precision`, `recall` and `abstention`, each with
  its `numerator`, `denominator` and `rate` (`null` when the denominator is
  0).

`semantic-support` adds `per_domain` and an `aggregate` note.

**Status rules.** One function, `stage_status`, applies them to every stage:
- A floor with a zero denominator fails.
- Floors compare exact fractions, inclusively.
- A stage with any refused unit fails.
- A route refusal never shrinks a denominator.

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

`identity-decisions` scores cross-source pairs against the answer key after
the composition route verifies the run's resolution. A pair connected by
`same` decisions counts as a join. A pair with an `unresolved` decision
counts toward abstention. The precision floor is 1, the recall floor is
9/10 and the abstention ceiling is 1/5. A run without a verified composition
and resolution cannot pass this stage.

`coverage` remains dormant, owned by the reading-coverage milestone.

## Name diagnostics

The [name diagnostics example](diagnostics/README.md) scores candidate
spelling relationships for review and supplies unresolved proposals
with source evidence. Its synthetic measurement reports an observed
false-discovery fraction for each sampled kind.


```sh
python -m gnd.examples.literature.name_diagnostics src/gnd/examples/literature/diagnostics/cases.json
```

The input schema is `literature-name-occurrences/1`. Each row has an ID,
work ID, contexts, introducing works, original source key, one evidence
coordinate and the raw population SHA-256. The example accepts up to
500 occurrences and 8,000 candidates. Candidate generation uses the
original spellings. Folded equality in disjoint contexts provides the
homonym signal. In overlapping contexts, a casing variant needs a compact
spelling with at least two adjacent capitals. A shared introducing work
suppresses that signal. A family signal needs a shared name token in at
least four distinct works and no introducing work. The generic tokens
`family`, `method` and `variant` supply no family signal. Synonyms have
one edit between folded names and share a context. The ordered kinds
are homonym, family and synonym, with scores 1.0, 0.9 and 0.85. The
threshold is 0.8.

The output schema is `literature-name-diagnostics/1`. Each candidate
includes the occurrences, kind, score and an unresolved decision
proposal with distinct placeholders and evidence coordinates. The example
writes only to stdout. The composition reference governs use of
resolution records. Malformed or over-limit input exits 3.

Run the frozen synthetic measurement with the separate ledger.

```sh
python -m gnd.examples.literature.diagnostic_measurement \
  src/gnd/examples/literature/diagnostics/measurement.json \
  src/gnd/examples/literature/diagnostics/labels.json
```

## Contextual assertions and saved reviews

The [contextual assertions corpus](assertions/README.md) represents each
statement with a work version, predicate, participants, source passage
and experiment. Conditions and regimes qualify individual statements.
Opposing results under different experiments remain separate. A mention
can identify a document occurrence while its participant sense remains
unresolved.

The example preserves an assertion's polarity and attribution. Reviewers
can approve an accurate extraction of a negation, comparison, speculation
or citation. The positive projection selects statements that pass the
saved-judgment and condition checks and assert an own finding. The
[saved judgment contract](../../skills/gnd-dev-session/references/judgment-contract.md)
defines the underlying receipt and policy shapes. The corpus rubric records
`stretched` as rejection and `insufficient-evidence` as abstention.

```sh
cd src/gnd/examples/literature/assertions
python -m gnd.examples.literature.assertion_admission \
  model.orm.yaml raw.population.json policy.json receipts.json evidence \
  --out trial-admission
```

The producer runs `gnd judgments check` over captured consumer-pinned inputs
and retains its ordinary JSON report. A conditional statement needs a
concrete condition. The words unspecified, none and n/a denote absence
for that check, regardless of case or surrounding space. Each statement
has its own work and passage identity. Separate excerpts can represent
several statements reported in the same passage. The producer writes
`raw.population.json`, `judgment-report.json`, `admitted.population.json`
and `admission.json` in the new output directory. The admission marker
binds the exact input and output digests and lists per-statement decisions
under `semantic-support` and `positive-own-findings`. A completed
projection exits 0, including one with declined rows. Invalid,
unavailable or stale inputs refuse at exit 3.

## Context-qualified lineage

The [lineage fixtures](lineage/README.md) use saved-opinion admission
and compose its admitted rows with the original source evidence.
The path-policy file names the relations that can supply lineage.
A derived step also names its assertion's passage. A transfer step
requires reviewed assumption and interface conditions in that
assertion. Evaluation, comparison, inspiration and taxonomic
membership remain available as statements.

Run the public development score from the repository root with a
fresh output directory.

```sh
example=src/gnd/examples/literature
python -m gnd.examples.literature.lineage_run assemble "$example" \
  "$example/lineage/model.orm.yaml" "$example/lineage/development-input.json" lineage-run
python -m gnd.examples.literature.lineage_run score \
  "$example/lineage/model.orm.yaml" lineage-run "$example/answers/answer-key.json"
```

The scorer checks the retained admission bundles and composition binding,
then requests both the
directed steps and the ancestry query for each path. It reports the
supported and excluded counts separately. The original flat whale
fixture is in the [resolution example](resolution/README.md).

The committed rule model is generated from the path-policy table
and the contextual assertion model by
`python tools/build_literature_lineage_model.py`.

## Extraction-to-checking interop

```sh
python -m gnd.examples.literature.interop run --out literature-run --dates
python -m gnd.examples.literature.interop verify literature-run
```

The packaged fixture uses two saved document extractions and two shared
vocabulary files. The example runs GND's extraction projection and validates
the saved populations against the original evidence. It verifies the source
rebinds, applies a candidate identity decision onto a fixed catalog method,
then runs composition, temporal checking, witness, replay and fidelity. The
manifest verifies the input and output bytes and the stage links. See the
[documents guide](../../../../docs/guides/documents.md#separate-extraction-and-checking-models)
for the model split and rebind contract.

The two source directories each contain evidence for both readers. Fidelity
reads `document.md`, while composition reads the same bytes at
`document.txt`. This layout materializes one extra document file per source.
The original extraction population and its extraction sidecar have one
materialization each. The rebound populations and anchors carry the checking
model's coordinates.

### Publication-year advice

Omit `--dates` to run the checking and proof stages on their own. Generate
the same report later with:

```sh
python -m gnd.examples.literature.interop dates literature-run --out advice.json
```

The advisory input lists proposed work pairs and uses the public LI5
[chainability policy](lineage/path-policy.json). The separate date table
names the work, date role, declared precision and value. An edge passes when
the descendant's publication year is at least the ancestor's year at the
same precision. Unknown works, missing or conflicting publication dates and
mixed precision remain unresolved. Alternative date roles supply no
publication comparison. The report binds the edge, date and policy bytes.

The fixture's incorrect PINN edge is a proposed edge from the 2019 PINNs paper
to Bayesian PINNs, published in 2021. It produces one advisory. Its work IDs
come from the two publications. The 2026 and equal-year edges are synthetic
comparison controls. [Issue #193](https://github.com/vasiloglou/gnd-public/issues/193),
[PINNs](https://doi.org/10.1016/j.jcp.2018.10.045),
[Bayesian PINNs](https://doi.org/10.1016/j.jcp.2020.109913)
