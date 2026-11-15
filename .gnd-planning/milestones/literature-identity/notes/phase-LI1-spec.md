# Phase LI1 · literature regression corpus and staged assurance report · spec r1

## 1. Status

**Awaiting owner review (2026-11-15).** Nothing is implemented. No corpus
byte, harness file or test exists. The owner gate must rule D1–D10 (§7) and
choose the approval instrument (§11) before any file outside
`.gnd-planning/` is created. `auto=false`.

## 2. Provenance

- **Source.** Plan r3 ([plan](literature-identity-plan.md)), approved by the
  owner at SHA-256
  `5ad5b74485a442a8e9fa09ed59c28a4463b812a4119ea6f2959c56cdda7c90de`
  ([001](../001-plan-gate.md)), with plan rulings D1–D9 as proposed. This spec
  uses plan §0, §1.1, §2 LI1, §3, §4 (C1–C7), §4.1, §5, §6, §7 and §9. It also
  reads [#193 part 1](https://github.com/vasiloglou/gnd-public/issues/193)
  directly. The issue text was re-read for this spec, because the plan
  summarizes it.
- **Prior phase.** [LI0](../003-phase-LI0.md) (recorded 2026-11-15). LI1
  inherits none of its boundary items: they concern witness intake, which
  LI1 does not touch. One LI0 test constrains where LI1's model may live
  (§4, rule 5).
- **Review.** No review has run over this spec. The two plan-panel rounds
  reviewed plan r1 and r2 only. These bytes carry no review opinion.
- **Baseline.** Branch head `547acaf1` (LI0 recorded). The code baseline is
  unchanged from `ecd12986` outside `src/gnd/witness/` and LI0's tests.
- **Measurements.** Six probes against 0.3.1 behavior were run on
  2026-11-15 while writing this spec. They are listed in §12 and settle
  several design questions by measurement (standing rule 6).
- **Tags.** `(o)` will mark owner rulings once given.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| Plan C1 | Corpus and split answer key hold at least: 3 supported chains (1 cross-domain), 5 named false chains, 8 reuse cases (4 real, 2 generic words, 2 homonyms), 12 support-labelled assertions, 6 identity pairs (3 `same`, 3 `different`), 4 N1 name pairs (2 homonym, 1 synonym, 1 family). Every gold label cites a passage. Below any floor fails C1 | §6.2 counts, T1, T2, T3 |
| Plan C2 | Six 0.3.1-detectable mutations each fail their named stage: drop all outputs → `semantic-support` and `derivation`; drop one supported fact → `semantic-support`; stale evidence → `freshness`; falsified derived row → `derivation`; invalid source population → `model-population-validity`; shifted anchor span → `source-binding` | §6.6, T10–T15 |
| Plan C3 | No empty premise counts as success. No mutually exclusive flags combined. Routes read over their own commands. Withheld route output → `not-measured`, never a pass | §6.4 route table, §6.5 status rules, T16, T17, T18, D6 |
| Plan C4 | Report states sample sizes, exclusions, disagreements, and that labels are not independent expert ground truth | §6.3 report schema, T7 |
| Plan C5 | P/R/abstention per stage. Abstain on 6 of 12, rest correct → P 1.0, R 0.5, abstention 0.5, exit 1 on `semantic-support` | §6.5 arithmetic, T19 |
| Plan C6 | Held-out subset (1 supported, 2 false chains) committed by digest before LI5; held-out answer key off the LI5 dev branch; whale scored in dev | §6.7, T4, D4 |
| Plan C7 | Dormant stage → `not-measured` with owner, excluded from exit 0. At LI1: `identity-decisions` and `coverage` dormant | §6.5, T8 |
| Plan §2 LI1 | Seven named stages, each with unit, gold, floor, failing mutation. Exit 0/1/3. Floors fixed at this gate before any measurement. Zero denominator never a pass. Metrics computed against the answer key, not taken from `gnd measure --labels` | §6.5, D3, T9 |
| Plan §3 LI1 row | Gold labels passage-level (participants, predicate in plain words, support label), independent of any LI4/LI5 model. Only 0.3.1-detectable mutations | §6.2 answer key schema |
| Plan §3 homes | Report harness is a new example harness (plan D5, ruled). It reads `gnd check`, `gnd fidelity` and `gnd judgments` outputs over their routes | §6.1, §6.4, D1, D6 |
| Plan §3 fixture rule | Every fixture model declares `model_id` and version ≥ 2 | §6.1 model |
| Plan §0 totality | Report harness input is total over arbitrary JSON, with the cap on the read | §4 rule 1, T20 |
| Plan §0 / project rule 2 | Time-bound test over the layer LI1 adds | §4 rule 2, T21 |
| Plan §0 / project rule 3 | Refusal order pinned per boundary | §6.3 order, T22 |
| Plan §1.1, plan D1 (ruled) | Public reconstruction only. The 16/50/24/180 host-scale sets stay host-owned and run with this harness | §9, §6.3 (harness takes any answer key) |
| Plan D2 (ruled) | Paraphrased documents with public work identifiers | §6.2 authoring rules, T3 |
| Plan §5 | Literature example section carries LI1's harness. Business pages show skill prompts and visual results, not Python | §6.1, D7 |
| Plan §6 risks | Copyright (paraphrase), overfitting (held-out before LI5) | §6.2, §6.7 |
| Plan §7 | Not proposed items and host-scale runs out of scope | §9 |
| Plan §8 | Rulings D1, D2, D5 already ruled at the plan gate; spec gate; focused gate + guard list + ruff; diff review; refactoring review; record | §8 ledger, §11 |
| Plan §9 LI1 row | Corpus and harness tests, plus `test_composition_example.py` and the fidelity consumers the harness reads | §8 ledger |
| Plan-gate open question | "LI1: the stage floors" | D3 |
| #193 part 1 criterion 1 | Report reproduces the baseline denominators and records its snapshot identity | §6.3 `inputs` block, T6 |
| #193 part 1 criterion 3 | An omitted supported fact reduces recall; an unresolved case stays visible | T11, §6.3 `unresolved` |
| #193 part 1 "Proposal" | Gold recall from reading the source, not only from what the extractor produced. Micro totals and per-domain results. Related versions of one work grouped to avoid leakage | §6.2 (passages), §6.3 `per_domain`, §6.7 split-by-work rule, T4 |
| Project hook | Guard list, `ruff`, component index `changed --strict` | §8 ledger |
| LI0 test `test_model_identities_match_baseline_golden` | Walks every `tests/fixtures/**/*.orm.yaml`. A new model there would break LI0's golden | §4 rule 5: LI1's model lives under `src/gnd/examples/` |
| `tests/test_mc1_guards.py::test_R30_examples_do_not_declare_includes` | Walks every example model and pins the include-bearing set | LI1's model declares no includes; consumer node in §8 |

## 4. Standing rules bound to this phase

1. **Totality.** The new consumer of untrusted input is
   `assurance_report.score(corpus_dir, answers_path, run_dir)`. It reads three
   JSON documents (`corpus.json`, the answer key, `run.json`) and every route
   payload. Every read is capped before parsing: 4 MiB per document, 64 MiB
   per route payload. The parser refuses NaN and infinities, depth above 64
   and integer literals above 128 digits. T20 feeds each hostile form to each
   reader and expects exit 3 with a reason code and no traceback.
2. **Input-bounded work.** The harness's own work is linear in units plus
   route payload size: anchors are matched to passages through a per-document
   index, never a cross product. T21 scores a synthetic answer key of 5,000
   passages against a run of 5,000 anchors, with routes stubbed, under a
   10-second bound.
3. **Validation order.** One order at the harness boundary (§6.3). T22 gives
   an input that fails two steps and asserts the earlier reason.
4. **One walk per policy.** One function, `stage_status`, applies the status
   rules (§6.5) to all seven stages. No stage computes its own pass/fail.
   T9 drives every stage through each status branch by table.
5. **One home per contract.**
   - **Report and answer-key formats.** One home: the example's
     `README.md`, section "Formats". The harness docstring cites it.
   - **Extractor matching.** It stays in `gnd.fidelity.match` under D1's
     proposal. The harness does not re-implement it.
   - **Where the model lives.** Under `src/gnd/examples/literature/`, not
     `tests/fixtures/`, so LI0's identity golden (which walks
     `tests/fixtures/**/*.orm.yaml`) stays valid.
6. **Measurement.** The route behaviors the design relies on were measured
   (§12), not assumed. The stage floors are fixed here, before any score is
   seen (D3).

**Repository conventions.** The example lives under `src/gnd/examples/`,
which `tools/gnd_layers.json` excludes by glob (`src/gnd/examples/**`). It
needs no layer entry, and the allowance count stays zero. It calls `gnd`
through the CLI (`sys.executable -m gnd`), so ModelIndex and family dispatch
are not touched.

## 5. Goal

`python -m gnd.examples.literature.assurance_report CORPUS ANSWERS RUN --out R`
writes a `literature-assurance-report/1` payload.

- **Reference run:** exits 0. Every active stage is `pass`; `identity-decisions`
  and `coverage` are `not-measured`, with owners LI2 and literature-depth LD3.
- **Each C2 mutation:** exits 1 and names at least its required failing stage.
  Each mutation's exact failing set is pinned by a committed golden.
- **The C5 abstaining run:** exits 1 on `semantic-support`, with precision
  1.0, recall 0.5 and abstention 0.5.
- **Invalid input:** exits 3 with a reason code and no traceback.

The committed corpus meets every C1 floor (T1 exits 0). The held-out answer
key's digest is committed and its bytes are not on the branch (T4).

## 6. Design

### 6.0 Reuse table

The component index (`dev/components/`) was searched before writing.

| Capability | Searches | Found | Decision |
|---|---|---|---|
| Extractor precision/recall with honest denominators | `search fidelity extractor precision recall`, `search assurance report` | `fidelity.match` (multiset match by reference identity, explicit `unresolved`/`ambiguous`), `fidelity.report`, `cli.fidelity_command` | **Reuse** through `gnd fidelity` (D1) |
| Population validity, anchor binding, derivation recomputation, vacuity | same searches; `check.service` | `gnd check` snapshot arm, `--anchors/--document`, `--composition/--sources` | **Reuse** through `gnd check` |
| Composing per-document sources | composition example, `docs/reference/composition.md` | `gnd compose`, `tools/build_composition_example.py` | **Reuse** `gnd compose`. **Adapt** the builder pattern for a new `tools/build_literature_example.py` |
| Saved-judgment verdicts | `semantics.saved_judgments` | `gnd judgments check` | **Not read in LI1** (D6). No LI1 stage consumes review opinions |
| Label-based measurement | `gnd measure --labels` | measures against host labels | **Rejected** by plan §2: metrics are computed against the answer key |
| Report harness and staged status | — | nothing existing | **New** example module |

### 6.1 Files

| Path | Kind | Estimate |
|---|---|---|
| `src/gnd/examples/literature/README.md` | entry point. Lists the corpus and run, and holds the one home for formats. Contains no labels | 140 lines |
| `src/gnd/examples/literature/model.orm.yaml` | the LI1 corpus model: version 2, `model_id: urn:gnd-example:literature-flat@1`, no includes | 70 lines |
| `src/gnd/examples/literature/corpus/corpus.json` | `literature-corpus/1` manifest: documents, passages, artifacts digest | data |
| `src/gnd/examples/literature/corpus/documents/*.md` | about 17 paraphrased documents, one per work (§6.2) | data |
| `src/gnd/examples/literature/corpus/artifacts/` | `gnd extract MODEL --out` bundle (projection, applicable set, digests) | generated |
| `src/gnd/examples/literature/answers/answer-key.json` | `literature-answer-key/1` (split from the entry point) | data |
| `src/gnd/examples/literature/answers/README.md` | narrated case stories with expected outcomes (the corpus-first instrument, §11) | 160 lines |
| `src/gnd/examples/literature/answers/render/<doc>.manifest.json` | `gnd fidelity` renderer manifests, one per document (D1) | generated |
| `src/gnd/examples/literature/answers/heldout.sha256` | digest of the held-out answer key (§6.7) | 1 line |
| `src/gnd/examples/literature/runs/reference/` | the faithful reference run (§6.6) | generated |
| `src/gnd/examples/literature/expected/*.report.json` | golden reports: the reference run, 6 C2 mutations, the C5 run, the consistent-shift case | generated |
| `src/gnd/examples/literature/assurance_report.py` | the harness | ≈ 480 lines |
| `tools/build_literature_example.py` | rebuilds sidecars, the composition, renderer manifests, artifacts and goldens byte-identically | ≈ 280 lines |
| `tests/test_li1_literature_corpus.py` | C1, C6, split and authoring rules, rebuild identity | ≈ 200 lines |
| `tests/test_li1_assurance_report.py` | C2–C5, C7, routes, status rules, totality, time bound, order | ≈ 380 lines |
| `dev/components/COMPONENTS.md` | new entry `examples.literature_assurance` and regenerated module pages | edit |

**The corpus model.** It is deliberately flat, as the host's model was:
methods are identified by name. LI2–LI5 add structure, and LI1 keeps this
model so the corpus can measure that change later.

| Fact type | Roles | Kind |
|---|---|---|
| `work_introduces_method` | work (identifier), method (name, anchored) | asserted |
| `method_builds_on_method` | method (anchored), base method (anchored) | asserted |
| `method_is_used_in_field` | method (anchored), field | asserted |
| `method_has_ancestor_method` | method, ancestor | derived: the transitive closure of `method_builds_on_method` (structured recursion) |

The implementation may add fact types only where a supported assertion
cannot be expressed. Each addition is an implementation finding.

### 6.2 Corpus and answer key

**Documents.** There is one short document per work (D2, ruled). Each is a
paraphrase of that work's abstract-level claims, under its public identifier.
The dev stories need about 14 works, six of them for the whale alone, and
at least 3 more are held out (§6.7). The exact number is fixed at the corpus gate.

The dev set covers these stories:
- **The whale:** dynamic mode decomposition → VAMPnet; VampNet → WhAM; WHAM
  and OpenCap Monocular.
- **`$PINN`:** a paper's `$PINN`, and PINNs.
- **Boltz-1:** Boltz-1 evaluated as a force field.
- **Contrast:** "unlike existing simulation-based inference approaches".
- **Normalizing flows:** "normalizing flow" and "normalizing flows".
- **Cross-domain supported chain:** one supported chain that crosses domains.

The exact passages are authored in the corpus step (§11). The spec fixes their
counts and authoring rules.

**Authoring rules** (T3 checks the mechanical ones):
1. **Paraphrase, no quotation.** No passage contains a run of 12 or more words
   copied from the source work. The check is manual at authoring; a test pins
   that every document declares `paraphrase: true` and names its identifier.
2. **Verified identifiers.** Every work identifier (DOI or arXiv id) is checked
   against its public landing page while authoring. An identifier that cannot
   be verified is replaced by title and year, with `identifier: null`. No
   identifier is guessed.
3. **Synthetic text.** Each document's header says it is a synthetic
   paraphrase for regression testing, not the work itself.

**`corpus.json`** (`literature-corpus/1`, entry point, no labels):

```json
{
  "schema": "literature-corpus/1",
  "model": "model.orm.yaml",
  "model_sha256": "<hex>",
  "artifacts": {"path": "corpus/artifacts", "applicable_sha256": "<hex>", "projection_sha256": "<hex>"},
  "documents": [
    {"id": "d01", "path": "corpus/documents/d01.md", "sha256": "<hex>",
     "domain": "dynamical-systems", "split": "dev",
     "work": {"identifier": "doi:…", "title": "…", "year": 2010}, "paraphrase": true}
  ],
  "passages": [{"id": "p01", "document": "d01", "span": {"start": 0, "end": 212}}]
}
```

Passages are public. A run may abstain on a passage by its id. Listing
passages publicly is what makes source-level recall possible: the gold set
includes passages an extractor never used (#193 part 1, "Proposal").

**`answer-key.json`** (`literature-answer-key/1`, kept apart from the entry point):

```json
{
  "schema": "literature-answer-key/1",
  "corpus_sha256": "<sha256 of corpus.json bytes>",
  "labeller": {"kind": "single-author", "independent": false,
               "note": "Labels were written by the corpus author from the public works; they are not independent expert ground truth."},
  "assertions": [
    {"id": "a01", "passage": "p01", "participants": ["VAMPnet", "dynamic mode decomposition"],
     "predicate": "is a Koopman-operator method related to", "support": "supported",
     "fact": {"fact_type": "method_builds_on_method", "roles": {"method": "VAMPnet", "base_method": "dynamic mode decomposition"}},
     "label_disagreement": null}
  ],
  "anchored_facts": [{"id": "f01", "source": "d02", "fact": {"fact_type": "…", "roles": {}}, "role": "method", "passage": "p03", "span": {"start": 10, "end": 17}}],
  "populations": [{"source": "d01", "expected_check_exit": 0}],
  "chains": [{"id": "c01", "label": "false", "story": "whale", "domains": "cross", "edges": ["a01", "a04", "a06"], "passages": ["p01", "p05", "p07"], "reason": "…"}],
  "reuse_cases": [{"id": "u01", "name": "…", "kind": "real", "passages": ["p02", "p09"]}],
  "identity_pairs": [{"id": "i01", "left": {"source": "d02", "object_type": "method", "value": "VAMPnet"}, "right": {"source": "d03", "object_type": "method", "value": "VampNet"}, "label": "different", "passages": ["p03", "p05"]}],
  "name_pairs": [{"id": "n01", "left": "VAMPnet", "right": "VampNet", "kind": "homonym", "passages": ["p03", "p05"]}],
  "heldout": {"sha256": "<hex>", "chains": {"supported": 1, "false": 2}}
}
```

Enum spellings are given literally, and the schema and implementation must
match them (project trap):
- `support`: `supported`, `stretched`, `contradicted`, `insufficient-evidence`;
- `chains[].label`: `supported`, `false`;
- `reuse_cases[].kind`: `real`, `generic-word`, `homonym`;
- `identity_pairs[].label`: `same`, `different`;
- `name_pairs[].kind`: `homonym`, `synonym`, `family`.

**Counts.** The planned counts meet the C1 floors and add the held-out set.
They are fixed by the arithmetic below, not by preference:

| Category | C1 floor | Planned (dev) | Held out |
|---|---|---|---|
| Supported chains | 3, 1 cross-domain | 3, 1 cross-domain | 1 |
| False chains | 5, the named five | 5, the named five | 2, new stories |
| Reuse cases | 8 (4 real, 2 generic, 2 homonym) | 8 (4/2/2) | 0 |
| Support-labelled assertions | 12 | 12: **8 supported**, 2 stretched, 1 contradicted, 1 insufficient-evidence | 0 |
| Identity pairs | 6 (3/3) | 6 (3/3) | 0 |
| N1 name pairs | 4 (2/1/1) | 4: VAMPnet/VampNet, WhAM/WHAM homonym; normalizing flow/flows synonym; `$PINN`/PINNs family | 0 |

**Why 8 supported.** With S supported assertions, a recall floor of 0.9 fails
on one dropped fact only when (S−1)/S < 0.9, that is S < 10. With 8 tp, one
false positive gives precision 8/9 = 0.889 < 0.9. With 8 supported, C5's
numbers are reachable: abstain on 4 supported and 2 non-supported passages,
then answer the other 6 correctly. That gives precision 4/4, recall 4/8 and
abstention 6/12. A larger S would make C2's one-drop mutation unable to fail
the stage, which is the project's "unfalsifiable by fixtures" class.

**Gold source populations.** For each document, the supported assertions'
`fact` entries, plus the entity facts they need, form that document's gold
source population. That population is what `gnd fidelity` compares the run's
extraction against. Non-supported assertions become `absent-fact`
distractors in the document's renderer manifest.

### 6.3 Harness surface

```python
def score(corpus_dir: Path, answers: Path, run_dir: Path, *,
          gnd: Sequence[str] = (sys.executable, "-m", "gnd"),
          limits: Limits = DEFAULT_LIMITS) -> dict: ...

def main(argv: Sequence[str] | None = None) -> int:
    """CLI: CORPUS ANSWERS RUN [--out PATH]; prints canonical JSON; returns exit_code."""
```

`score` never raises for input it was given. An internal invariant breach
returns exit 3 with reason `internal`, and T20 asserts no traceback on
stderr.

**Run layout** (`literature-run/1`):

```
run/
  run.json        {"schema": "literature-run/1", "corpus_sha256": "<hex>",
                   "sources": ["d01", …], "abstentions": ["p07", …]}
  composition/    a gnd compose directory: manifest.json and, per source,
                  document.txt, population.json, population.json.anchors.json,
                  population.json.extraction.json
  composed/       population.json and record.json, written by gnd compose
```

A run may omit `composed/`, sidecars or `abstentions`. The stage that needed
the missing piece then reports `not-measured` (C3), which exits 1 for an
active stage.

**Validation order at the harness boundary** (refusals exit 3):

1. **Read:** read and parse `corpus.json`, the answer key and `run.json`, in
   that order, with caps (`input:unreadable`, `input:too-large`,
   `input:not-json`);
2. **Shape:** check each document's shape (`input:schema`, with the JSON path
   and no values);
3. **Digests:** check that the answer key's `corpus_sha256` and the run's
   `corpus_sha256` equal the corpus bytes (`corpus:digest-mismatch`,
   `run:corpus-mismatch`);
4. **Run consistency:**
   - every source names a corpus document (`run:unknown-source`);
   - each `document.txt` equals the corpus document's bytes
     (`run:document-mismatch`);
   - every abstention names a passage (`run:unknown-passage`);
   - no anchored fact lies inside an abstained passage
     (`run:abstained-passage-asserted`);
5. **Routes:** invoke the routes (§6.4);
6. **Score:** score the stages (§6.5).

A route's own refusal is **not** a harness refusal. It is an outcome of the
measured run, and step 6 scores it.

**Report** (`literature-assurance-report/1`):

```json
{
  "schema": "literature-assurance-report/1",
  "exit_code": 1,
  "reason": null,
  "inputs": {"corpus_sha256": "…", "answers_sha256": "…", "run_sha256": "…",
             "gnd_version": "0.3.1", "harness_sha256": "…"},
  "labels": {"kind": "single-author", "independent": false, "note": "…"},
  "stages": [
    {"stage": "semantic-support", "active": true, "owner": null,
     "status": "fail", "failed_floors": ["recall", "abstention"],
     "unit": "assertion with a support label", "sample_size": 12,
     "exclusions": [], "unresolved": 0,
     "disagreements": {"count": 4, "units": ["…"]}, "label_disagreements": 0,
     "precision": {"numerator": 4, "denominator": 4, "rate": 1.0},
     "recall": {"numerator": 4, "denominator": 8, "rate": 0.5},
     "abstention": {"numerator": 6, "denominator": 12, "rate": 0.5},
     "floor": {"precision": 0.9, "recall": 0.9, "abstention_max": 0.2},
     "per_domain": [{"domain": "…", "precision": {}, "recall": {}, "abstention": {}}],
     "routes": [{"argv": ["fidelity", "…"], "exit": 0}]}
  ],
  "failed_stages": ["semantic-support"],
  "not_measured": [{"stage": "identity-decisions", "owner": "LI2"}, {"stage": "coverage", "owner": "literature-depth LD3"}],
  "unscored_labels": [{"kind": "chains", "count": 8, "owner": "LI5"}, {"kind": "reuse_cases", "count": 8, "owner": "LI2, LI3"},
                      {"kind": "identity_pairs", "count": 6, "owner": "LI2"}, {"kind": "name_pairs", "count": 4, "owner": "LI3"}]
}
```

**Report rules:**
- A refused input has `stages: []` and `reason` set.
- A rate with denominator 0 is `null`.
- Argv paths are recorded relative to the inputs, so goldens are portable.
- **Snapshot identity.** The `inputs` block and the sample sizes discharge
  #193 part 1 criterion 1. T6 checks that sample sizes equal the answer-key
  counts.

### 6.4 Route table

The harness holds this table as one literal. It never builds argv any other
way.

| Id | Argv (after `gnd`) | Feeds | Per |
|---|---|---|---|
| R1 | `check MODEL POP --format json` | `model-population-validity` | source |
| R2 | `check MODEL POP --anchors SIDECAR --document DOC --format json` | `source-binding`, `freshness` (anchor binding) | source |
| R3 | `fidelity MODEL --cases CASES --artifacts ART --format json` | `semantic-support`, `freshness` (extraction binding) | run (once) |
| R4 | `check MODEL COMPOSED --composition RECORD --sources DIR --format json` | `derivation`, `freshness` (composition binding) | run (once) |

**Forbidden in every argv:** `--allow-vacuous`, `--baseline`,
`--baseline-model`, and `--composition` together with any of `--anchors`,
`--document` or `--populations`. The last combination was measured:
`gnd check` refuses it with exit 64 and the message `--composition checks one
composed snapshot; it excludes --anchors, --document, …` (§12, probe 5). T16
asserts the literal table contains none of these, and runs the forbidden
combination once to pin its exit 64.

**R3 case assembly.** For each source, the harness writes a temporary
fidelity case:
- `source.population.json`: the gold source population, from the answer key;
- `document.md`: the corpus document bytes;
- `document.manifest.json`: from `answers/render/`;
- `extracted.population.json` and its extraction sidecar: the run's.

The case directory exists only inside the harness's temporary directory.

### 6.5 Stages, scoring and status

Every stage defines, per unit, a **run-positive** (what the run claims) and a
**gold-positive** (what the answer key or route recomputation says):

- precision = both positive / run-positive;
- recall = both positive / gold-positive;
- abstention = units the run explicitly declined (or the route reported
  vacuous or unchecked) / sample size.

| Stage | Active | Unit | Run-positive | Gold-positive | Floors (D3) |
|---|---|---|---|---|---|
| `model-population-validity` | LI1 | run source population | R1 exit 0 | answer key `expected_check_exit` is 0 | P 1.0, R 1.0, and every unit's R1 exit equals its expected exit |
| `source-binding` | LI1 | anchored fact in the answer key | the run anchors that fact, and R2 accepted the source's binding | the run's anchor span equals the gold span | P 1.0, R 1.0 |
| `semantic-support` | LI1 | support-labelled assertion (12) | the run extracted a fact of an assertion fact type (R3 `extracted_total`) | label `supported` (R3 `source_total`) | P ≥ 0.9, R ≥ 0.9, abstention ≤ 0.2 |
| `identity-decisions` | LI2 | identity pair | — | — | dormant, `not-measured` |
| `derivation` | LI1 | claimed derived row in the composed population, plus each row R4 recomputes and the run omits | the run claims the row | R4 does not report it unsound, and it is in the recomputed extension | P 1.0, R 1.0, abstention 0 (no vacuous or unchecked derivation verdict) |
| `coverage` | LD3 | inspected section | — | — | dormant, `not-measured` |
| `freshness` | LI1 | evidence binding: per source, anchor and extraction sidecars; per run, the composition record | the binding is present | its route did not refuse it with a binding-digest reason, and every raw-byte digest it names equals the current bytes | P 1.0, R 1.0 |

**Semantic-support detail.**
- **Precision** = Σtp / Σextracted over the assertion fact types, using R3's
  per-fact-type `matched` counts.
- **Recall** = Σtp / Σsource_total.
- **Abstention** = abstained labelled passages / 12.
- An abstained supported passage is not extracted, so it shows up as
  `missed` and lowers recall. That matches C5.
- `unresolved` is R3's `matched.unresolved`. It is listed, never hidden
  (#193 part 1 criterion 3).
- Fact types are micro-totalled here, labelled as the harness's own
  aggregate. R3's per-fact-type rows are copied verbatim beside it.
- **Why the counts equal the labelled set.** In the gold population, every
  fact of an assertion fact type is exactly one `supported` assertion's
  `fact`, and the reverse holds too. T1 checks this both ways. So R3's
  `source_total` over those types is 8.
- **Disagreements.** R3 reports counts, not which fact matched. So this
  stage's `disagreements.count` is `missed + unmatched`, and
  `disagreements.units` lists only abstained passages. A per-assertion list
  is not available from the route, and the report says so in a `note`
  field. This is a cost of D1's proposal.

**Status rules** (one function, `stage_status`). They are applied in this
order:
1. **Dormant.** An inactive stage is `not-measured` with its owner, and is
   excluded from the exit (C7).
2. **Route missing.** An active stage whose route input is missing from the
   run is `not-measured` with owner `run`, and **counts as a failure** for
   the exit. A run cannot pass by withholding output (C3).
3. **Floors.**
   - A zero denominator in any floored metric fails that floor.
   - Every floor is compared inclusively against exact rationals: a recall
     floor of 0.9 is met by 9/10, not by 0.8999.
   - A stage with any failed floor is `fail`, and its failed floors are named.
4. **Pass.** A stage with none of the above is `pass`.

**Refusals never shrink a denominator.** A route that refuses (for example R2
exit 3 on a shifted span) leaves every unit of that source in the
denominator, as `refused` disagreements. **A vacuous derivation is never a
success:** a vacuous or unchecked derivation verdict in R4's JSON counts as
abstention in `derivation`, whose floor is 0. The harness reads this from the
JSON verdicts, not from the exit, because the exit precedence `1 > 4 > 2 > 0`
lets a failure hide a vacuous rule (§12, probe 6).

**Exit:**
- 0 when every active stage is `pass`;
- 1 when any active stage is `fail` or route-missing `not-measured`;
- 3 for a harness refusal (§6.3).

### 6.6 The reference run, mutations and goldens

**The reference run** is the faithful control. It extracts exactly the gold
facts, anchors each at its gold span, claims every derived row R4 recomputes,
and abstains on nothing. It must exit 0, which proves that the instrument
can pass.

`tools/build_literature_example.py` builds the reference run. The test module
derives each mutation from it with one literal transform table. The builder
regenerates every binding after a transform, except where the transform is
about stale bindings, so each mutation changes only what its row says:

| Id | Transform | Required failing stage (C2) | Detected by |
|---|---|---|---|
| M1 `drop-all` | Every source population's facts become `{}` and its anchors `[]`, and the composition is rebuilt | `semantic-support`, `derivation` | R3 recall 0, R4 empty extension (zero denominator) |
| M2 `drop-one` | Remove one supported assertion fact that no claimed derived row depends on, with its anchors | `semantic-support` | R3 recall 7/8 |
| M3 `stale` | Rewrite one source population with different whitespace and do not regenerate its sidecars | `freshness` | R2 `anchor:binding-mismatch: digest differs`; R3 exit 3 on that case |
| M4 `false-derived` | Add one unsound claimed row to `method_has_ancestor_method` in one source, then recompose | `derivation` | R4 `derived-extension-unsound` |
| M5 `invalid-population` | Add an unknown top-level key to one source population | `model-population-validity` | R1 exit 3 against expected 0 |
| M6 `shifted-span` | Move one anchor's span by one character and keep its excerpt hash | `source-binding` | R2 `anchor:binding-mismatch: source span or excerpt differs` |
| X1 `abstain-6` (C5) | Abstain on 4 supported and 2 non-supported passages, and drop their facts | `semantic-support` (P 1.0, R 0.5, abstention 0.5) | R3 plus abstentions |
| X2 `consistent-shift` | As M6, but recompute the excerpt hash for the new span | `source-binding` | gold span comparison only; R2 accepts. This shows what the answer key adds over the route |

A mutation may fail more stages than its required one. M3, for example, also
leaves the source's R2 units `refused` in `source-binding`. Each mutation's
exact failing set is pinned by `expected/<id>.report.json`, and the owner
approves those sets with the corpus (§11). The spec's claim is only the
required stage.

### 6.7 Held-out set

- **Contents.** At least three held-out documents (`split: "heldout"`) carry 1 supported
  and 2 false chains, with stories not used in dev. The whale is in dev
  (C6).
- **No leakage.** No held-out document is a version of a work that a dev
  document covers. T4 checks that work identifiers and titles are disjoint
  across splits (#193 part 1, "group related versions").
- **Committed now.** The held-out documents are committed in the corpus, so
  they are inputs, not answers. Their labels live in a held-out answer key
  in the same format. Only its digest is committed, in
  `answers/heldout.sha256` and `answer-key.json` `heldout.sha256`.
- **Where the held-out bytes live.** Under D4's proposal they sit on a
  separate local branch, `literature-heldout`, which holds that one file and
  is never merged into an LI5 development branch. T4 asserts the file is
  absent from the working tree and that the committed digest is 64 hex
  characters. Verifying the digest against the bytes is an LI5 step.
- **Limit, stated now.** The same author writes the dev and held-out labels
  and may later develop LI5. The separation is procedural, not blind, and
  three chains are a smoke test, as plan C6 says.

## 7. Decisions

All rows are **proposed**. None is ruled.

| ID | Question | Proposal | The other reading and its cost |
|---|---|---|---|
| D1 | Route for `semantic-support` | **`gnd fidelity` (R3)**, with case directories assembled by the harness. Each corpus document gets a renderer manifest, because the manifest type requires `renderer_skill: "gnd-render-doc"` (`src/gnd/extract/manifest.py:145`). Documents are authored under the gnd-render-doc contract from their gold population, with `executing_model` naming the author, the same precedent as `tests/fixtures/roundtrip/`. This reuses `fidelity.match` as the one home of extractor matching, and follows plan §3 | The harness matches facts itself by exact canonical equality, with no renderer manifests or extract artifacts. That is simpler (≈ 120 fewer lines and no manifests), but it is a second matching home beside `fidelity.match` and drops plan §3's fidelity route. Both readings give the same exits on every C2/C5 case, because the fixtures use exact spellings |
| D2 | Approval instrument | **Corpus-first** (§11). The phase ships a serialized format and an exit-code contract, where the default is corpus-first. The owner gates once on this spec's design and once on the authored corpus and goldens, before harness code | Prose only: one gate, but the expected failing set of each mutation and every route payload's shape are unseen until implementation |
| D3 | Stage floors (the plan-gate open question) | As in §6.5: validity, source binding, derivation and freshness need P = R = 1.0; semantic-support needs P ≥ 0.9, R ≥ 0.9, abstention ≤ 0.2; derivation abstention = 0. Comparisons are inclusive, over exact rationals | Lower floors (say R ≥ 0.85) would let M2 pass with S = 8 (7/8 = 0.875), which breaks C2. Higher semantic floors (1.0) make every single stretched extraction fatal, so precision can no longer be reported as graded |
| D4 | Where the held-out answer key lives | **A local branch `literature-heldout`** holding only the held-out answer key, with its digest committed on the LI1 branch. It is pushed only with a later explicit authorization | (a) An owner-held file outside the repository: blinder, but the owner has to keep it. (b) Committed on the LI1 branch: auditable, but plan C6's "off the LI5 development branch" fails |
| D5 | Held-out set composition | **3 additional documents and chains** beyond the C1 floors, so the five named false chains all stay in dev (L2 and L6 need Boltz-1 and the contrast case in dev) | Hold out 2 of the named five: then L2/L6 lose development fixtures |
| D6 | Reading of C3's route list | **Routes are read where a stage consumes them.** LI1 reads `gnd check` (R1, R2, R4) and `gnd fidelity` (R3). `gnd judgments` is first consumed when LI4 feeds review verdicts into `semantic-support`. LI1 records it as unread and has no stub for it | Wire `gnd judgments` now, with an LI1 review fixture: that needs the LI4 rubric (plan D7) before LI4's spec exists |
| D7 | Business-facing docs page | **Deferred to LI5**, where the literature story is complete. LI1 ships the example README (developer-facing formats) only | A `docs/` page now would show a report with two dormant stages and no lineage result, and it would be rewritten in LI2, LI4 and LI5 |
| D8 | Report and corpus schema ids | `literature-corpus/1`, `literature-answer-key/1`, `literature-run/1`, `literature-assurance-report/1`. They are example-level, not `gnd-…` ids, because plan D5 keeps this off the `gnd` contract | `gnd-…` ids would read as public CLI contracts |
| D9 | A route refusal versus a harness refusal | A route's refusal is a measured outcome (scored, exit 1). Only the harness's own inputs exit 3 (§6.3) | Treating route refusals as exit 3 would make M3/M5/M6 report "invalid input" instead of failing their stages, which breaks C2 |
| D10 | Spec review | **None.** The corpus gate (D2) is the second look | A panel round over these bytes |

## 8. Tests and verification

### 8.1 Test list

| # | File :: case | Criterion | Expected |
|---|---|---|---|
| T1 | `test_li1_literature_corpus.py::test_counts_meet_c1_floors` | C1 | each count ≥ its floor, and the 8/2/1/1 support split exactly; the gold populations' assertion-type facts and the `supported` assertions' facts are equal sets; a copy of the key with one category below its floor makes the checker return a failure (both branches) |
| T2 | `…::test_every_label_cites_an_existing_passage` | C1 | every passage id resolves, and every span lies within its document; a mutated span past the end fails |
| T3 | `…::test_documents_declare_paraphrase_and_identifier` | D2 | `paraphrase: true`, plus an identifier or `null` with title and year; a synthetic-text header in every document |
| T4 | `…::test_heldout_split` | C6 | at least 3 held-out documents; work identifiers and titles disjoint across splits; `heldout.sha256` is 64 hex characters and equals the key's `heldout.sha256`; no held-out answer key in the tree |
| T5 | `…::test_rebuild_is_byte_identical` | — | the builder in a temporary directory reproduces every generated file |
| T6 | `test_li1_assurance_report.py::test_reference_run_exits_0` | §5 | exit 0; the report equals `expected/reference.report.json`; sample sizes equal the answer-key counts |
| T7 | `…::test_report_states_labels_and_counts` | C4 | `labels.independent is false`, note present; every stage has `sample_size`, `exclusions`, `unresolved` and `disagreements` |
| T8 | `…::test_dormant_stages` | C7 | `identity-decisions` owner LI2 and `coverage` owner LD3 are `not-measured` and absent from `failed_stages`; the reference run still exits 0 |
| T9 | `…::test_stage_status_branch_table` | §6.5 | a table drives `stage_status` through dormant, route-missing, zero denominator, each failed floor, the inclusive boundary (9/10 at 0.9 passes) and pass |
| T10 | `…::test_mutation[M1]` | C2 | exit 1; `semantic-support` and `derivation` in `failed_stages`; report equals golden |
| T11 | `…::test_mutation[M2]` | C2, #193 crit. 3 | exit 1; `semantic-support` fails on recall 7/8; golden |
| T12 | `…::test_mutation[M3]` | C2 | exit 1; `freshness` fails; golden |
| T13 | `…::test_mutation[M4]` | C2 | exit 1; `derivation` fails on precision; golden |
| T14 | `…::test_mutation[M5]` | C2 | exit 1; `model-population-validity` fails; golden |
| T15 | `…::test_mutation[M6]` and `[X2]` | C2 | both exit 1 with `source-binding` failing; in X2, R2 exited 0 |
| T16 | `…::test_route_table_never_combines_excluded_flags` | C3 | no forbidden flag or combination in the literal table; the forbidden combination run once exits 64 |
| T17 | `…::test_withheld_route_is_not_measured_and_fails` | C3 | removing `composed/` gives `derivation` `not-measured` owner `run`, exit 1; likewise for missing anchor sidecars → `source-binding` |
| T18 | `…::test_vacuous_derivation_is_not_success` | C3 | a run whose composed population covers the derived type but holds no base facts: R4 reports vacuous or unchecked, `derivation` fails on abstention, exit 1 |
| T19 | `…::test_abstaining_run_c5` | C5 | X1: exit 1, P 4/4, R 4/8, abstention 6/12 exactly; golden |
| T20 | `…::test_hostile_inputs[...]` | totality | for each of `corpus.json`, the answer key and `run.json`: NaN, depth 65, a 200-digit integer, a non-object, oversize (cap+1 bytes, read refused before parse), invalid UTF-8 → exit 3 with the named reason, empty stderr traceback |
| T21 | `…::test_time_bound` | rule 2 | 5,000 passages × 5,000 anchors, routes stubbed, under 10 s |
| T22 | `…::test_validation_order` | rule 3 | a malformed answer key together with a run whose `corpus_sha256` mismatches reports `input:schema`; a key mismatch together with an unknown source reports `corpus:digest-mismatch` |
| T23 | `…::test_harness_refusals[...]` | §6.3 | each of `run:unknown-source`, `run:document-mismatch`, `run:unknown-passage`, `run:abstained-passage-asserted` → exit 3 with that reason |

**Branch walk.** Each §6.5 status branch has a failing case: T9 by table,
and T17/T18 end to end. Each §6.3 refusal has a case (T20, T22, T23). Each
route has a case where its output changes the verdict: R1 T14, R2 T15, R3
T11/T19, R4 T13/T18. Each mutation's required stage has a case (T10–T15).
X2 is the case that tells apart "the route accepts" from "the gold span
agrees", so the gold comparison is not decorative.

### 8.2 Verification-selection ledger

| Obligation | Disposition | Command or evidence | Input boundary | Justification | Invalidation |
|---|---|---|---|---|---|
| LI1 direct tests | run | `uv run pytest -q tests/test_li1_literature_corpus.py tests/test_li1_assurance_report.py --tb=short`, exit 0 | `src/gnd/examples/literature/**`, `tools/build_literature_example.py`, both test files | Every criterion maps here (§8.1) | any change to those paths, or to `gnd check`/`gnd fidelity`/`gnd compose` |
| Affected consumers (plan §9 row) | run | `uv run pytest -q tests/test_composition_example.py tests/test_fidelity_payload.py tests/test_fidelity_match.py tests/test_public_fidelity_scope.py tests/test_mc1_guards.py tests/test_gnd_arch.py --tb=short`, exit 0 | composition example and builder pattern, fidelity lane, example-model walks, layer exclusion | LI1 changes no `src/gnd` module outside `examples/`. These are the tests that walk examples or own the routes the harness reads | a change under `src/gnd/` outside `examples/literature/` |
| LI0 identity golden | run | `uv run pytest -q tests/test_li0_witness_wire.py --tb=short`, exit 0 | `tests/fixtures/**/*.orm.yaml` | Shows that LI1 added no fixture model there | a new fixture model under `tests/fixtures/` |
| Structure guard list | run | the project-hook block, verbatim, exit 0 | the guard files' inputs | files outside `.gnd-planning/` change | always run |
| Lint | run | `uv run ruff check`, exit 0 | whole repository | project hook | always run |
| Component index | run | `python3 scripts/components_index.py changed --base 547acaf1 --strict`, exit 0 | `dev/components/` | new example module | always run |
| Broad lanes | cadence | `uv run pytest -q -m "evidence or census"`, explicit request only | — | no historical bytes or census inputs change | owner request |

## 9. Out of scope for this phase

- **Host-scale sets.** Running the 16/50/24/180 sets and importing them stay
  host-owned (plan D1, ruled). The harness accepts any answer key in the
  format, so the host can run it.
- **Later stages.** Scoring chains, identity pairs, reuse cases and name pairs
  belongs to LI2, LI3 and LI5. LI1 only commits them and checks their counts
  and citations.
- **Later mutations.** False merge (R6), missing condition (A1) and reversed
  relation (L5).
- **No new `gnd` command or schema change.** Plan D5 rules this out, and no
  change to `gnd check`, `gnd fidelity`, `gnd compose` or `gnd judgments` is
  made.
- **The judgments route** (D6) and the business-facing docs page (D7).
- **Everything in #193 "Not proposed".**

## 10. Size

Estimate at write time:
- **Source:** harness ≈ 480 lines, builder ≈ 280 lines, README + answers
  README ≈ 300 lines.
- **Tests:** ≈ 580 lines.
- **Data:** about 17 documents, the answer key, renderer manifests, the reference
  run, 9 goldens.

The record will report measured figures, and a landing above 2× is recorded
as a finding about this estimate.

## 11. Approval instrument

Proposed: **corpus-first** (D2), in two gates.

1. **This spec.** The owner rules D1–D10 and approves the design, counts,
   floors and formats.
2. **The corpus gate.** The corpus, the answer key, the reference run, the
   mutation table's outputs and the golden reports are authored and
   committed **red**: the harness does not exist yet, so T6–T23 fail on
   import. Three things are offered for the owner's reading:
   - the narrated stories in `answers/README.md`, one per chain, assertion
     group and mutation, each with its expected outcome;
   - the C1 counts table;
   - each golden's failing set.

   The entry point `README.md` holds no labels. The answer key and stories
   live only under `answers/`, so a later blind reader can be given the
   corpus without the answers.
3. **Then the harness.** Implementation turns the red cases green. Each
   commit names the cases it turns green. Changing an approved golden's
   failing set sends that golden back to the owner.

## 12. Measurements and implementability sweep

**Probes run on 2026-11-15** against the 0.3.1 code at `547acaf1`:

| # | Probe | Result |
|---|---|---|
| 1 | `gnd check --anchors --document` on the composition example's contract-a | exit 0 |
| 2 | Same, with one anchor's span shifted by one character | exit 3, `anchor:binding-mismatch: source span or excerpt differs` |
| 3 | Same, with one byte appended to the document | exit 3, `anchor:binding-mismatch: digest differs` |
| 4 | `gnd check` on the LI0 grandparent model with `covers` declared and one unsound derived row | exit 1, `derived-extension-unsound`, naming the offending fact. Without `covers` the derived row is refused at exit 3 (`population:uncovered-structured-derived-facts`), and without any derived claim the result is exit 4 (`derivation-not-covered`) |
| 5 | `gnd check … --anchors … --composition …` | exit 64, `--composition checks one composed snapshot; it excludes --anchors, --document, …` |
| 6 | `gnd fidelity` on `tests/fixtures/roundtrip/faithful` | exit 0; per-fact-type `matched` {tp, missed, unmatched, unresolved, ambiguous}, with rates whose denominators are explicit and `null` at 0. The renderer manifest requires `renderer_skill: "gnd-render-doc"` (`extract/manifest.py:145`) |

The docs give the exit-band precedence `1 > 4 > 2 > 0`
(`docs/reference/rule-check-report.md`), which is why §6.5 reads verdicts
from JSON.

**Sweep: can some implementation satisfy each requirement as written?**
- **C1 counts.** Yes. The categories are independent, and the 8/2/1/1 split
  meets the floor of 12.
- **C2 for every mutation.** Yes, by probes 2–4 and 6. M1's derivation
  failure relies on the zero-denominator rule (§6.5), not on a route exit,
  so it holds whatever exit R4 gives on an empty composition.
- **C5 arithmetic.** Yes, with S = 8 (§6.2).
- **M2 against floor 0.9.** Yes: S = 8 < 10.
- **C3 withheld routes.** Yes. The status rules make route-missing a failure,
  so withholding cannot pass.
- **C6.** Yes procedurally (D4). Blind separation is not claimed.
- **C7.** Yes.
- **Reference run exits 0.** Not yet proven. It needs `gnd check` exit 0 on
  every per-source population and on the composed population, with the
  derived type covered (probe 4 shows `covers` is required). If a single
  source's population can only exit 2 or 4, then that exit is its
  `expected_check_exit`, and validity still agrees. Validity floors compare
  exits, not 0. This is the one place where corpus authoring may refute a
  detail. It would be recorded as an implementation finding at the corpus
  gate.
- **Fidelity case assembly (D1).** It needs a renderer manifest per
  document, which binds the gold population's digest, and `gnd extract`
  artifacts. Both are generated by the builder, so the requirement is
  satisfiable. The cost is the reason D1 exists.
- **Totality T20 "read refused before parse".** Satisfiable by reading at most
  cap+1 bytes from the opened file.

No requirement was found that no implementation can meet.
