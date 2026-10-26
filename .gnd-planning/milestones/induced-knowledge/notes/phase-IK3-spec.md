# IK3 — Measure over host-labelled populations

## 1. Status

**r1, awaiting owner review.** No code exists. Nothing in this file is approved.
Implementation starts only after the owner rules on §7 and approves these bytes.

## 2. Provenance

- **Plan:** r4, approved 2026-10-24 (SHA-256 `8afbdcbd…cd51a`). This spec expands:
  - §2 "Request 3";
  - §4 IK3;
  - the §9 IK3 row;
  - D5 (o), id-keyed refs;
  - D10 (o), the class agreement scorer.
- **Source request:** [issue #34](https://github.com/vasiloglou/gnd-public/issues/34),
  request 3.
- **Dependencies:** IK3 depends only on the measure package (plan §3). It
  follows IK1, IK2 and IK4, which are all merged. IK5 needs IK3's label
  manifest.
- **Base commit B:** `e8e7158` (`main`, after PR #39).
- **Harvest:** done by the author from the plan and the code
  (`src/gnd/measure/`, `src/gnd/synth/provenance.py`,
  `src/gnd/measurement.schema.json`, `src/gnd/commands/measure.py`).
- **Review:** none has run over these bytes.

## 3. Obligations — inline harvest

| Obligation | Source | Discharge here |
|---|---|---|
| IK3-C1: a capped, digest-bound label manifest loader, total over arbitrary JSON; refs id-keyed or positional; unknown refs refused; cap fixed here | plan §4; IK-R6, IK-R12; D5 (o) | §6 manifest; T1, T2 |
| IK3-C2: `expected-state` mode equals the synth-sidecar measurement of the same populations and expectations | plan §4 | §6 equality definition (IK3-D2); T3 |
| IK3-C3: `class` cells exact on a control; a wrong rule moves the counts; denominators are decided populations; vacuous and unchecked are separate | plan §4; D10 (o) | §6 agreement scorer; T4, T5 |
| IK3-C4: synth-sidecar reports byte-identical to committed goldens; a work counter over manifest size within the ceiling | plan §4; IK-R3, IK-R6 | T6, T7 |
| §9 row: expected-state parity with the synth path; class cells exact; synth goldens unchanged | plan §9 | T3–T6 |
| §5 row: a manifest schema and a class-mode report version | plan §5 | §6 schemas |
| Labels name constraints by `id`; positional refs only for id-less constraints; an unknown `id` is refused by name | D5 (o), r4 | §6 refs; T2 |
| "The host never supplies GND's own `no-subjects` evidence" (class mode) | plan §2 | §6 class mode: vacuity comes from the checker only |
| Learner and host numbers are claims to check | IK-R2 | §6: GND recomputes every verdict; the manifest supplies only labels |
| Host data never persists in induction evidence | IK-R11 | §6: the manifest carries opaque population ids and digests; the report repeats only them |
| Lane homes, RF5/RF6 | IK-R7 | §6 registration; T9 |
| Standing rules 1–6 | IK-R9 | §4 |
| Privacy of fixtures | IK-R10 | synthetic only |

## 4. Standing rules bound to IK3

| Rule | Application |
|---|---|
| 1 Totality | **New loader:** `gnd.measure.labels.read_label_manifest` is total over arbitrary JSON. It reads at most cap + 1 bytes through `gnd.input_policy`, which refuses depth over 64, duplicate keys and non-finite numbers. The schema is validated before any field is read. **Populations** go through the existing capped loader one at a time, after their digest is checked. T2 feeds hostile manifests. |
| 2 Input cap vs algorithm | **Work counter:** one unit per population checked, plus one per label row scored. **Ceiling:** `W ≤ P × (1 + C)`, where P is the manifest's populations and C the model's constraints. T7 pins it on a near-cap manifest. The checker runs once per population, as today. |
| 3 Validation order | Arguments, then the manifest read and schema, then model load, then manifest-to-model binding (model digest, refs resolved), then per population: path, digest, load, check, score. Source-order pin, T8. |
| 4 One walk | Expected-state mode feeds the existing `classify` and `score_constraint` unchanged. Class mode has its one scorer, `gnd.measure.agreement`. One ref resolver serves both modes. |
| 5 One home | **Manifest format:** `src/gnd/labels.schema.json` plus `docs/reference/measure-labels.md`. **Report wire:** `measurement.schema.json`, extended with new variants. **Cell definitions:** the agreement module's docstring, cited by the docs. |
| 6 Measurement | Synth-path byte identity is decided by the committed goldens (T6), not argued. |

## 5. Goal

`gnd measure MODEL --labels MANIFEST [--format json] [--out PATH]` exits 0 and
emits a labelled-measurement report. `--labels` and `--populations` are mutually
exclusive, and naming both or neither is exit 64.
- **Expected-state mode:** every `per_constraint` row equals the row a synth
  measurement of the same populations and expectations produces. Exit 6 on a
  checker defect, as today.
- **Class mode:** per declared rule, six agreement counts with numerators and
  denominators. Exit 0 whatever the counts; the cells are evidence, not a gate.

It exits 3 when:
- the manifest is malformed, over its cap, or names another model;
- a ref is unknown;
- a population is missing from the manifest's directory, escapes it, or fails
  its digest.

A population that fails to load is exit 5, as today. Every report built from
synth sidecars is byte-identical to B.

## 6. Design

### Label manifest (`gnd-labels/1`, `src/gnd/labels.schema.json`, closed)

```json
{"schema_version": "gnd-labels/1",
 "model_sha256": "<sha256 of the model file bytes>",
 "mode": "expected-state" | "class",
 "populations": [
   {"id": "<opaque token>", "path": "<manifest-relative ref>", "sha256": "<hex>",
    "expectations": {"<ref>": {"ground_truth": "satisfied|violated|no-subjects",
                               "expected_verdict": "pass|fail|warning|unchecked|vacuous",
                               "reason": "<string, optional>"}}}
     or, in class mode,
    "class": "positive" | "negative"}],
 "rules": {"<ref>": {"fires_on": "negative" | "positive"}}}
```

- **`rules`** is present exactly in class mode.
- **`expectations`** is present exactly in expected-state mode, with an entry
  for every model constraint in every population (IK3-D4). The census rule
  `n == population_count` is unchanged.
- **Grammars:**
  - `id` uses the IK2 example-id grammar;
  - `path` uses the IK2 ref grammar (relative, no `..` segment, no leading `/`);
  - `sha256` is 64 lowercase hex.
- **Refs (D5 (o)):**
  - `id:<constraint id>` names a constraint by its `id`;
  - the positional forms `fact_types[<ft>].constraints[<i>]` and
    `constraints[<i>]` are accepted only for a constraint with no `id`;
  - an unknown `id`, a positional ref to a constraint that has an `id`, or a
    positional ref past the end is exit 3, with the ref named.
- **Model binding:** `model_sha256` must equal the model file's digest (exit 3
  otherwise), so a manifest cannot be scored against a different model.

**Bounds (IK3-D5, fixed before results):**

| Item | Bound |
|---|---|
| manifest bytes | ≤ 1 MiB |
| populations | 1 … 10,000 |
| rules (class mode) | 1 … 1,024 |
| ref string | ≤ 256 characters |
| `reason` | ≤ 256 characters |
| each population | the existing 10 MiB cap, loaded one at a time |

### Expected-state mode

- **Per population, in manifest order:**
  - resolve `path` under the manifest's directory, refusing symbolic links and
    escapes;
  - verify the digest, then load the population and check it;
  - build an `Observation` per constraint from the manifest's `ExpectedState`
    and the checker's verdict.
- **Scoring:** `score_constraint` and `classify` run unchanged.
- **Report (IK3-D2):** `schema_version` 4, a labelled variant. Its
  `per_constraint` rows and `checker_defects` use exactly the existing row and
  defect shapes. The synth-only header fields are replaced by a `labels` block:
  manifest path and sha256, mode, population count, and one corpus row per
  population (id, path, sha256). There are no seeds, pools, generator version or
  sidecar paths.
- **Equality (IK3-C2):** for a synth corpus converted to a manifest with the same
  populations and expectations, the v4 report's `per_constraint` and
  `checker_defects` equal the synth report's byte for byte, after canonical JSON.
  T3 builds that conversion from a committed synth corpus.

### Class mode (agreement scorer, `gnd.measure.agreement`)

For each rule ref R with `fires_on: F` (and the other class written ¬F), over
the populations:
- **Fired:** the checker's verdict for R is `warning` or `fail`.
- **Silent:** the verdict is `pass`.
- **Vacuous and unchecked** are counted on their own. They are never folded into
  a cell or a denominator, and the host never supplies them.
- **Cells, each `{numerator, denominator}`:**
  - `fired_on_negative`: populations of class `negative` where R fired / the
    negative populations whose verdict for R is decided (`pass`, `warning` or
    `fail`);
  - `fired_on_positive`, `silent_on_negative` and `silent_on_positive`
    likewise;
  - `vacuous`: populations where R is vacuous / all populations;
  - `unchecked`: the same for `unchecked`.
- **Expectation:** the row also carries `fires_on`, so a reader can see what
  agreement means for this rule: `fired_on_F` and `silent_on_¬F` are the
  agreeing cells. No aggregate, accuracy or F1 is computed (D-01 style).
- **Report:** `schema_version` 5, a class variant. It carries the `labels`
  block, plus `rules[]` rows of `{ref, constraint_type, modality, source,
  status, fires_on, cells}`.

### Exits

| Exit | Meaning |
|---|---|
| 0 | done |
| 3 | invalid manifest, binding or ref; a population digest mismatch, escape or missing file |
| 5 | a population failed to load (existing) |
| 6 | expected-state mode found a checker defect (existing C9) |
| 64 | `--labels` with `--populations`, or neither |
| 66 | the manifest or model is missing |
| 70 | internal invariant (partition or census) |
| 74 | a refused path |

### Registration

- **New modules** in the existing `measure` lane: `gnd.measure.labels` and
  `gnd.measure.agreement`.
- **No new command group.** `gnd measure` gains `--labels`, so the RF1 CLI
  goldens for `gnd measure` change: help, exit probe and tree.
- **Model reads** go only through `ModelIndex`; a chained census delta.
- **Docs:** `docs/reference/measure-labels.md`, plus a row in
  `docs/reference/cli.md`.

## 7. Decisions

| ID | Question | Readings and cost | Proposed |
|---|---|---|---|
| IK3-D1 | Approval instrument | **Corpus-first** (default for formats, exits and predicates): small labelled manifests for both modes, with hand-written cells and exits, committed red. **Prose** relies on this spec's tables. | corpus-first |
| IK3-D2 | **Refuted premise:** plan §2 says only class mode adds a report version, but every v1–3 report requires synth-only fields (generator version, pool source, seeds, pools, sidecar paths). A label manifest has none of them. | **(a) New v4 for expected-state:** rows identical to the synth path, with a manifest header; honest provenance. **(b) Fill v1–3 with placeholders** (`pool_source: "host-labels"`, empty seeds and pools): no new version, but fields with misleading meanings. | (a) v4 expected-state, v5 class |
| IK3-D3 | Command shape | **`--labels` on `gnd measure`**, exclusive with `--populations`: one command, and RF1 measure goldens change. **A new `gnd measure-labels`:** a new command group. | `--labels` |
| IK3-D4 | Must expected-state label every constraint? | **Yes** (as sidecars must): the census rule stays exact, at some cost to hosts. **No:** a per-row census over labelled populations only; the score of an unlabelled constraint is undefined. | yes |
| IK3-D5 | Bounds | the §6 table | as stated |
| IK3-D6 | Class mode exit on disagreement | **Exit 0**, cells are evidence. **Exit 6** when an agreeing cell is under 100%: turns host labels into a gate on noisy data. | exit 0 |
| IK3-D7 | Base and branch | `claude/ik3-measure` from B = `e8e7158` | as stated |

## 8. Tests

New file `tests/test_measure_labels.py`, with the corpus under
`tests/fixtures/induced_knowledge/ik3-corpus/` (IK3-D1).

| ID | Case | Expected |
|---|---|---|
| T1 | the schema accepts minimal and maximal manifests for both modes, and refuses a mode/field mismatch | 0 / 3 |
| T2 | hostile manifests: over 1 MiB, depth over 64, duplicate keys, NaN, unknown field, bad path (`/abs`, `../x`), bad digest, unknown `id`, a positional ref to an id-bearing constraint, a ref past the end, a wrong `model_sha256`, an over-bound count | exit 3 with the named cause; nothing scored |
| T3 | a committed synth corpus converted to an expected-state manifest: `per_constraint` and `checker_defects` equal the synth report's byte for byte | equal |
| T4 | a class-mode control: a deontic rule fires on every negative and no positive population, so `fired_on_negative` and `silent_on_positive` have numerator equal to denominator | as stated |
| T5 | a deliberately wrong rule moves those counts; a vacuous and an unchecked population are reported separately and excluded from the denominators | exact cells per the key |
| T6 | the existing synth measure goldens and tests pass unchanged | byte-identical |
| T7 | work counter on a near-cap manifest (10,000 populations, C constraints) is at or under `P × (1 + C)` | at or under |
| T8 | validation-order source pin; exits 64 (both or neither flag), 66 (missing manifest), 5 (a population that fails to load), 74 (a symlinked population) | as listed |
| T9 | RF1 (measure goldens), RF5, RF6, layering, docs | pass |
| T10 | determinism: two runs give byte-identical reports | equal |

**Criteria to tests:**

| Criterion | Tests |
|---|---|
| C1 | T1, T2 |
| C2 | T3 |
| C3 | T4, T5 |
| C4 | T6, T7 |

**Verification selection:**
- **Direct:** `tests/test_measure_labels.py`.
- **Impact closure:**
  - every `tests/test_measure*.py` and `test_public_measure*.py`;
  - `test_v62_phase3_synth_measure.py` and `test_v62_phase4_synth_measure.py`;
  - `test_incremental_session_measurement.py`;
  - every `tests/test_rf*.py` and `test_gnd_arch.py`;
  - the docs and packaged-invocation guards.
- **Selection rule:** the reduced v6.3 selection.

## 9. Out of scope for this phase

- learning or discovering rules (IK4, IK5);
- ILP export of labels (IK5 consumes this manifest);
- any aggregate score;
- YAML manifests;
- multi-model corpora;
- live data sources.

## 10. Size

Estimate: about 450 source lines, 600 test lines plus the corpus, and 120 doc
and registration lines.

## 11. Approval instrument

Proposed in IK3-D1: corpus-first, under
`tests/fixtures/induced_knowledge/ik3-corpus/`.
- The README tells each case's story; `expected.json` holds the answers.
- Committed red, and approved by reading.

## 12. Implementability sweep (author inspection, not review)

| Requirement | Finding |
|---|---|
| "expected-state reports identical to synth" | Only `per_constraint` and `checker_defects` can be identical; the header is synth-only. This is IK3-D2's refuted premise. |
| census `n == population_count` | Holds only if every constraint is labelled in every population (IK3-D4). |
| positional refs | The checker emits positional refs; `id:` refs map through `ModelIndex.iter_constraints`. |
| expected-state reuses `classify` | `ExpectedState{ground_truth, expected_verdict, reason}` is the existing sidecar type, reused unchanged. |
