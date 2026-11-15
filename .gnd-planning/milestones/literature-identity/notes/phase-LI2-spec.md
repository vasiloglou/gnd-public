# Phase LI2 · sense-resolution decisions bound to composition · spec r1

## 1. Status

**Awaiting owner review (2026-11-15).** Nothing is implemented. The owner gate
must rule D1–D11 (§7) and choose the approval instrument (§11) before any
file outside `.gnd-planning/` is created. `auto=false`.

## 2. Provenance

- **Source.** Plan r3 ([plan](literature-identity-plan.md)), approved at
  SHA-256 `5ad5b74485a442a8e9fa09ed59c28a4463b812a4119ea6f2959c56cdda7c90de`
  ([001](../001-plan-gate.md)), with plan ruling D3 (runtime binds and
  verifies decisions; meaning stays host-side). This spec uses plan §0
  (validation order, one walk, totality, input-bounded work), §2 LI2, §3,
  §4 (R1–R7), §5, §6, §9 and §10. It also reads
  [#193 part 2](https://github.com/vasiloglou/gnd-public/issues/193)
  directly.
- **Prior phases.**
  - [LI1](../006-phase-LI1.md) supplies the corpus, its six identity pairs,
    and the assurance harness whose `identity-decisions` stage LI2
    activates.
  - LI1's open question on the two evidence layouts is assigned to
    literature-interop, not here.
  - [LI0](../003-phase-LI0.md) leaves nothing that binds LI2.
- **Review.** No review has run over this spec. These bytes carry no review
  opinion.
- **Baseline.** Branch head `d09189ca` (LI1 recorded). The composition code
  is unchanged since `ecd12986`.
- **Tags.** `(o)` will mark owner rulings once given.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| Plan R1, #193 p2 crit 1 | In a two-document whale fixture with identically spelled homonyms, four senses stay distinct, the three legitimate direct edges survive, and the false combined chain disappears | §6.6 fixture W, T1 |
| Plan R2, #193 p2 crit 2 and 4 | Two senses with one spelling in one document are representable through `Mention` entities without rewriting text; an `anchored` constraint still passes. A method key and a version key stay distinct; merging them without `same` refuses with exit 3 | §6.6 fixture M, T2, T3 |
| Plan R3, #193 p2 crit 3 | An evidenced alias joins across documents. A same-domain homonym with no decision refuses at exit 3. Under `different` or `unresolved` it composes, at exit 0, into two values | T4, T5, T6 |
| Plan R4, #193 p2 crit 5 | Exit 3, naming keys and mentions but never values, for: an uncovered pair, a partially covered renaming, a transitive merge across `different`. A mutated evidence coordinate refuses. A bad digest together with an uncovered pair reports the digest first | T7–T12 |
| Plan R5, #193 p2 crit 6 | A changed decision makes `check --composition` and replay stale (exit 3, reason asserted). The prior snapshot replays to its original result. A manifest without `resolution` matches golden outputs from the baseline | T13–T16 |
| Plan R6 | A false-merge mutation fails the LI1 `identity-decisions` stage | §6.7, T19 |
| Plan R7 | Two identically spelled keys under `unresolved` compose, at exit 0, into two distinct placeholder values | T6 |
| Plan §2 LI2 | The `resolution` entry, the `gnd-resolution/1` record, the decision key grain, evidence coordinates, the coverage set, the rules, value-free refusals, unresolved semantics, the record fields, and senses inside one document | §6.1–§6.5 |
| Plan §0 validation order | 1 manifest; 2 resolution digest; 3 resolution parse and evidence binding; 4 existing composition refusals; 5 coverage and `different` closure | §6.4, T12 |
| Plan §0 one walk | One walk enforces the policy over every identity-changing outcome: a merging renaming, a separating renaming, an equal value joined unchanged, and an `unresolved` separation | §6.4 step 5, §4 rule 4, T17 |
| Plan §0 totality | The resolution record reader is total over arbitrary JSON, with the cap on the read | §4 rule 1, T18 |
| Plan §0 input-bounded | A time-bound test over values × sources × decisions | §4 rule 2, T20 |
| Plan §0 one home | The composition reference stays the home of the composition contract, and LI2 extends it there | §6.8 |
| Plan §0 strictness | Composition's one-value-one-entity rule and its refusal of contradictory partial renamings stay as they are | §6.4 step 4, T15 |
| Plan §3 homes | Adapt `model.composition`, its manifest and record schemas, and `checker._composed` re-verification (through `verify_composition`) | §6.0, §6.1 |
| Plan §5 | The composition reference gains the resolution entry, the coverage set and the record fields; the CLI reference points to it | §6.8 |
| Plan §9 LI2 row | New resolution tests, plus `test_composition.py`, `test_composition_example.py`, `test_witness_composition.py`; a time-bound test | §8.2 |
| Plan-gate open question | "LI2: the record schema ids" | D1 |
| Plan D3 (ruled) | Runtime binds and verifies decisions and the coverage set only; meaning stays host-side | §6.3 rule list, D3 |
| Plan §6 risk "silent coercion" | Keys use composition's exact value-and-type match; evidence uses mention coordinates | §6.2 |
| LI1 harness, stage table | `identity-decisions`: unit, cross-source key pair; gold, `same`/`different`; precision 1.0, recall ≥ 0.9 | §6.7 |
| LI1 approved expectations | Activating a dormant stage changes every approved LI1 outcome, which must go back to the owner | D8, §11 |
| LI0 test `test_model_identities_match_baseline_golden` | It walks `tests/fixtures/**/*.orm.yaml`, so no new model may go there | §6.6: fixtures under `src/gnd/examples/literature/resolution/` |
| Project hook | Guard list, `ruff`, component index `changed --strict`, a new module recorded in `tools/gnd_layers.json` | §8.2, §6.0 |

## 4. Standing rules bound to this phase

1. **Totality.**
   - *The new reader.* `parse_resolution(raw: bytes)` reads a
     `gnd-resolution/1` record. It goes through `gnd.anchors.strict_json`,
     the reader composition already uses, with a 4 MiB cap applied to the
     read (`read_regular_path(..., max_bytes=)`).
   - *Its failures.* Every malformed shape raises `CompositionError`, which
     is exit 3 with a value-free message.
   - *The test.* T18 feeds NaN, depth 65, a 200-digit integer, a non-object,
     wrong types in every field, and an oversize file.
2. **Input-bounded work.**
   - *The layer.* The coverage walk: union-find over decisions, plus one
     pass that groups keys by composed value and by original value.
   - *Its cost.* O((keys + decisions) · α), with no pairwise product. Groups
     are compared through their union-find roots, not pair by pair.
   - *The test.* T20 composes 200 sources × 200 keys with 20,000 decisions
     under a 10-second bound.
3. **Validation order.**
   - *The order.* The plan's five steps, in §6.4.
   - *The test.* T12 gives a bad resolution digest together with an
     uncovered pair, and asserts the digest refusal. A second case gives a
     mutated evidence coordinate together with an uncovered pair, and
     asserts the evidence refusal.
4. **One walk per policy.**
   - *The function.* `check_coverage(keys, outcome, decisions)`, the only
     place the decision policy is enforced.
   - *What it covers.* It walks every key group, whichever outcome produced
     it:
     - a merging renaming;
     - a separating renaming;
     - equal values joined unchanged;
     - an `unresolved` placeholder separation.
   - *What it rules out.* No outcome has its own check.
   - *The test.* T17 drives the four outcomes through the one function by
     table, and a source-scan assertion pins that `same`, `different` and
     `unresolved` are compared only inside it.
5. **One home per contract.**
   - *The composition contract.* It stays in `docs/reference/composition.md`,
     which gains a "Resolution" section. The CLI reference links to it. The
     schemas stay descriptive; the parser is the authority, as now.
   - *The decision format.* It has one home, the same section. The fixture
     README cites it.
   - *The harness stage.* Its semantics go in the literature example README,
     the home of the formats.
6. **Measurement.** Before the corpus gate, three questions are measured:
   - whether identity-preserving composition outputs change at all (the R5
     golden);
   - whether the existing renaming refusals still fire with a resolution
     present (T15);
   - whether `check --composition` re-derives the resolution through
     `verify_composition` unchanged (T13).

**Repository conventions.**
- **Layer.** The new module `gnd.composition_resolution` goes in
  `tools/gnd_layers.json` at layer `model`, beside `gnd.composition`, and
  the allowance count stays zero.
- **Model queries.** Role-to-object-type lookups use
  `ModelIndex.role_object_type`, as composition does.
- **Family dispatch** is not touched.

## 5. Goal

With `resolution` in the manifest, `gnd compose` and `gnd check --composition
--sources` work as follows:
- **Exit 0** when every key pair that composition joins, or that shares a
  spelling across sources, is covered by decisions consistent with the
  composed result.
- **Exit 3** otherwise, with a value-free refusal naming the decision index,
  the keys by source and object type, and the mention coordinates.

Without `resolution`, every output equals the baseline bytes. A changed
decision makes the composition and its witnesses stale (exit 3). In the
literature harness, `identity-decisions` becomes active: the reference run
passes it, and a false-merge run fails it at exit 1.

## 6. Design

### 6.0 Reuse table

The component index was searched (`components_index.py search compose
renaming lineage`, `search resolution identity decision`, `search
union find`).

| Capability | Found | Decision |
|---|---|---|
| Manifest, record, compose, re-verify | `model.composition` (`parse_manifest`, `compose`, `verify_composition`, `parse_record`) | **Adapt.** It gains an optional `resolution` entry, a `decision` field on each renaming, and optional record fields |
| Strict JSON reading, safe file reads | `model.anchors` (`strict_json`, `read_regular_path`) | **Reuse** |
| Anchors to resolve evidence spans | `model.anchors` (`AnchorSidecar`, `bind_anchors`), already bound per source in `_load_source` | **Reuse** the bound sidecar |
| Role object types | `model.query_index` (`ModelIndex.role_object_type`) | **Reuse** |
| Re-verification in `check --composition` | `check.service` calls `verify_composition` | **Reuse** unchanged. It calls `compose`, which now reads the resolution |
| Witness binding of the record | `witness.service` (binds the record's bytes) | **Reuse** unchanged. A changed record is already `binding-stale` |
| Decision policy | nothing existing | **New** module `gnd/composition_resolution.py` |

### 6.1 Files

| Path | Change | Estimate |
|---|---|---|
| `src/gnd/composition_resolution.py` | new: `parse_resolution`, `bind_evidence`, `check_coverage`, `decisions_for_fact` | ≈ 280 lines |
| `src/gnd/composition.py` | the manifest gains an optional `resolution`; a renaming gains an optional `decision`; `compose` runs the five steps; the record gains optional `resolution_sha256` and per-fact `decisions`; `parse_record` accepts them | ≈ +70 lines |
| `src/gnd/composition-manifest.schema.json`, `src/gnd/composition.schema.json` | optional properties added | ≈ +40 lines |
| `src/gnd/resolution.schema.json` | new, descriptive schema of `gnd-resolution/1` | ≈ 90 lines |
| `docs/reference/composition.md` | a "Resolution" section; the record section adds the fields | ≈ +90 lines |
| `docs/reference/cli.md` | one row pointing to the section | +1 line |
| `tools/gnd_layers.json` | `gnd.composition_resolution` at layer `model` | +1 line |
| `src/gnd/examples/literature/resolution/` | fixtures W (whale), M (mentions and method/version), A (alias), and the refusal set (§6.6) | data |
| `tools/build_literature_example.py` | builds the fixtures, and adds `resolution.json` to the LI1 reference run (D8) | ≈ +150 lines |
| `src/gnd/examples/literature/assurance_report.py` | the `identity-decisions` stage becomes active (§6.7) | ≈ +80 lines |
| `tests/test_li2_resolution.py` | T1–T18, T20 | ≈ 420 lines |
| `tests/test_li1_assurance_report.py` | T19 (R6), plus amended expectations (D8) | ≈ +40 lines |
| `dev/components/COMPONENTS.md` | a new entry `model.composition_resolution`; edits to `model.composition` and `examples.literature_assurance` | edit |

### 6.2 The manifest entry and the resolution record

**Manifest** (`gnd-composition-manifest/1`, D1). There are two optional
additions.

```json
{
  "schema": "gnd-composition-manifest/1",
  "sources": ["whale-a", "whale-b"],
  "renamings": [{"source": "whale-b", "fact_type": "method_builds_on_method", "role": "base_method",
                  "from": "VampNet", "to": "VampNet#music", "decision": 0}],
  "deduplications": "identical-rows",
  "scope_tags": [],
  "resolution": {"path": "resolution.json", "sha256": "<hex>"}
}
```

- **The path.** `resolution.path` is relative to the composition directory,
  one segment matching `^[A-Za-z0-9][A-Za-z0-9._-]{0,63}\.json$`. It is read
  with the same safe-read rules as every other composition input.
- **Citing a decision.** `decision` is an index into the resolution record.
  - With `resolution` present, **every renaming must cite one**.
  - Without it, a renaming carrying `decision` is refused.

**Resolution record** (`gnd-resolution/1`):

```json
{
  "schema": "gnd-resolution/1",
  "object_types": ["method"],
  "decisions": [
    {"decision": "different",
     "keys": [{"source": "whale-a", "object_type": "method", "value": "VampNet"},
              {"source": "whale-b", "object_type": "method", "value": "VampNet"}],
     "evidence": [
       {"key": 0, "source": "whale-a", "fact_type": "method_builds_on_method", "fact_index": 0,
        "role": "method", "span": {"start": 0, "end": 74}},
       {"key": 1, "source": "whale-b", "fact_type": "method_builds_on_method", "fact_index": 0,
        "role": "base_method", "span": {"start": 0, "end": 91}}],
     "producer": {"kind": "reviewer", "id": "corpus-author"},
     "input_sha256": {"whale-a": "<population sha>", "whale-b": "<population sha>"},
     "placeholders": null}
  ]
}
```

**Field rules:**
- **`object_types`.** These are the object types the coverage set covers
  (D2). Each must be declared by the model.
- **`decision`.** One of `same`, `different`, `unresolved`. This spelling is
  the schema's and the implementation's alike.
- **`keys`.** Exactly two keys (D10), each at composition's grain:
  - `source` must be a manifest source;
  - `object_type` must be listed in `object_types`;
  - `value` is a JSON scalar, matched by exact value and JSON type, as
    renamings are.

  The two keys must differ in source.
- **`evidence`.** At least one coordinate per key (D10).
  - `key` is the key's index in `keys`.
  - The coordinate names a fact of that source (`fact_type`, `fact_index`)
    whose `role` holds the key's value.
  - The role's object type must be the key's.
  - When the role is `anchored`, `span` is required, and the source's bound
    sidecar must hold an anchor for that fact and role with exactly that
    span. Otherwise `span` must be absent.
- **`producer`.** `kind` is `reviewer` or `tool`, with an `id` of 1 to 128
  characters.
- **`input_sha256`.** For each key's source, the SHA-256 of its
  `population.json` raw bytes. It must equal the current bytes, so a
  decision made over other inputs is stale.
- **`placeholders`.** `null` unless `decision` is `unresolved`. For an
  `unresolved` decision it lists one scalar per key, of the key's JSON
  type. The placeholders must be distinct, and distinct from every composed
  value of that object type.

### 6.3 What a decision means

GND verifies decisions; it never makes one (plan D3). Renaming stays the only
way composition changes a value. An `unresolved` separation is a pair of
renamings in the manifest, which the host writes and composition applies
(D3).

**The key graph.**
- *Keys.* A key is `(source, object_type, value)` for every value of a role
  whose object type is in `object_types`, taken from the source population
  before renaming.
- *Outcome.* `outcome(k)` is the key's value after the manifest's renamings.
- *Two groupings.* A **joined group** is the set of keys of one object type
  with equal outcomes, drawn from two or more sources. A **spelling group**
  is the set of keys of one object type with equal original values, drawn
  from two or more sources.

**Rules** (one walk, §6.4 step 5):

1. **Joined keys need `same`.** Every pair of keys in a joined group must be
   connected through `same` decisions. The `same` edges form a union-find
   over keys, and the group must sit in one component. This covers
   - merging renamings,
   - equal values joined unchanged (#193 crit 3),
   - a method key renamed onto a version key (R2).
2. **Shared spellings that end apart need `different` or `unresolved`.**
   Every pair of keys from a spelling group whose outcomes differ must be
   covered by a `different` or an `unresolved` decision on that exact pair.
   This covers separating renamings and `unresolved` separations.
3. **`different` is closed.** For a `different` pair, the two keys must not
   share a `same` component, and their outcomes must differ. This catches a
   direct merge and a transitive one (a `same` b, b `same` c, a `different`
   c).
4. **`unresolved` never joins.** For an `unresolved` pair, each key's
   outcome must equal its placeholder (R7), and the keys must not share a
   `same` component.
5. **`same` is applied (D4).** For a `same` pair, the two keys' outcomes must
   be equal. A recorded `same` that the manifest did not apply is refused.
6. **A renaming cites a decision about its own key (D3).** The cited
   decision must name the renaming's `(source, object type of
   fact_type.role, from)` key.

A pair that rules 1–2 do not require may still be decided (for example, a
`different` between differently spelled keys). Rules 3–5 then apply to it.

### 6.4 Validation order and refusals

`compose` runs these steps in order. Each refusal is a `CompositionError`
(`composition:invalid: …`, exit 3). It names decision indexes, key indexes,
sources, object types and coordinates, **never a value**.

1. **The manifest.** The existing parse, plus the shape of `resolution` and
   of `decision`.
2. **The resolution digest.** Read the file safely; its SHA-256 must equal
   `resolution.sha256` (`resolution digest differs from the manifest`).
3. **Resolution parse and evidence binding.**
   - *Parse.* §6.2 shapes, `object_types` declared by the model, key sources
     in the manifest. Each renaming's `decision` exists and passes rule 6.
   - *Load.* Then load each source (`_load_source`, unchanged).
   - *Bind.* Check every `input_sha256`, and bind every evidence coordinate:
     `decision 2 evidence 1 (source whale-b, method_builds_on_method#0.base_method) does not hold key 1`.
4. **Existing composition refusals, unchanged.** These are the renamings,
   the one-value-one-entity rule, a renaming that matches no row, and the
   validation of the composed population.
5. **Coverage and closure** over the key graph (`check_coverage`):
   - `keys 0 and 1 of object type method (sources whale-a, whale-b) are joined without a same decision`;
   - `decision 4 (different) is joined through same decisions`;
   - and so on.

A manifest without `resolution` skips steps 2, 3 and 5. Its behavior and
bytes are those of the baseline (R5, T16).

**The record.** It gains two fields, both present together or both absent
(D1):
- `resolution_sha256`: the raw SHA-256 of the resolution file;
- `facts[].decisions`: the sorted indexes of the decisions whose keys
  include a key of any of that composed fact's source facts. It mirrors
  `renamings`.

`parse_record` accepts records with or without the pair. `verify_composition`
compares both fields with the re-derived ones.

### 6.5 Senses inside one document (R2)

The source text is not rewritten. A reviewed replacement population models
occurrences as `Mention` entities:
- **Identity.** A mention id is `<document>@<start>-<end>`, a string value.
- **Surface text.** The `anchored` role `mention_has_surface_text.surface` is
  anchored at the mention's span, so anchors still match the document.
- **Sense.** A separate fact type, `mention_denotes_sense`.

Fixture M carries two mentions of one spelling with two senses in one
document. Its population passes `gnd check --anchors --document` with every
anchored rule `pass`. Coverage does not apply within one source: composition
keys are per source, and one source value is one entity there.

### 6.6 Fixtures (`src/gnd/examples/literature/resolution/`)

| Fixture | What it holds | Cases |
|---|---|---|
| **W** whale | Two documents, both spelling `VampNet` and `WHAM` identically, with four senses: Koopman VampNet and human-pose WHAM in `whale-a`; music VampNet and whale WHAM in `whale-b`. Three direct edges: `VampNet ← DMD` (a), `WHAM ← VampNet` (b), `OpenCap ← WHAM` (a). The model adds the derived recursive `method_has_ancestor_method` | flat (no resolution): the false chain `OpenCap … DMD` is witnessed, exit 0. Resolved (`different` decisions with separating renamings): the four senses stay distinct, the three edges survive, and a witness for the false chain reports `missing` (exit 2) (R1) |
| **M** mentions | One document with two `VampNet` mentions of two senses (§6.5). A second source holds a method key `Boltz-1` and a version key `Boltz-1x` | R2 anchors pass. Renaming `Boltz-1x` to `Boltz-1` without `same` refuses at exit 3 |
| **A** alias | `AlphaFold3` in one source and `AF3` in another, with a `same` decision and evidence | joins, exit 0 (R3). A same-domain homonym with no decision refuses at exit 3. Under `different` or `unresolved` it gives two values at exit 0 (R3, R7) |
| **R** refusals | Variants of W | an uncovered pair; a partially covered renaming (a renaming that cites a decision about another key); a transitive merge across `different`; a mutated evidence coordinate; a stale `input_sha256`; a bad digest together with an uncovered pair (R4) |

The fixture models declare `model_id` and version 2 (plan §3), and live
outside `tests/fixtures/` (§3, last row).

### 6.7 The LI1 harness: `identity-decisions` becomes active

- **Unit.** An answer-key `identity_pairs` entry (6 in LI1). The label is
  `same` or `different`.
- **Run-positive.** The run's resolution connects the pair's two keys
  through `same` decisions. R4 (`gnd check --composition`) verifies that the
  resolution is the one the composition used. A key named by the answer key
  but absent from the run is not run-positive.
- **Gold-positive.** The label is `same`.
- **Abstention.** Pairs covered by an `unresolved` decision, over the pair
  count.
- **Floors** (the LI1 plan table). Precision 1.0, recall ≥ 9/10,
  abstention ≤ 1/5.
- **Route.** R4 must accept the composition and the manifest must name a
  resolution. Otherwise:
  - no resolution, or no composed output: `not-measured` with owner `run`,
    which counts as a failure;
  - R4 refused: `route_refused`.
- **The LI1 reference run** gains `composition/resolution.json` (D8):
  - `same` for i04–i06, the equal spellings that composition joins
    unchanged;
  - `different` for i01–i03, with evidence;
  - no renamings.

  It scores precision 3/3, recall 3/3 and abstention 0/6.
- **R6 mutation** (`M7-false-merge`). Rename vampnets' `VAMPnet` to
  `VampNet` in every role of that source, citing a new `same` decision
  between `(vampnets, VAMPnet)` and `(wham-whale, VampNet)`. R4 accepts it,
  because the decision exists, and precision falls to 3/4 (exit 1). This is
  #193 crit 4's "false identity merge fails its gate".

### 6.8 Documentation

- **The composition reference.** It gains a "Resolution" section, the one
  home of the format and rules of §6.2–§6.4 and of the record fields. The
  sentence "Renaming is the only way composition changes a value" stays
  true and is kept.
- **The CLI reference.** One row: `gnd compose` with a `resolution` entry →
  the Resolution section.
- **The literature README** documents the `identity-decisions` stage.

## 7. Decisions

All rows are **proposed**. None is ruled.

| ID | Question | Proposal | The other reading and its cost |
|---|---|---|---|
| D1 | Schema ids (the plan-gate open question) | **Keep** `gnd-composition-manifest/1` and `gnd-composition/1`, with the new fields optional and paired. Without `resolution`, the bytes equal the baseline (R5) | Bump to `/2`: a clearer message from 0.3.1 readers, which refuse a new document at exit 3 either way, but every reader must then accept two ids and every existing record keeps `/1` |
| D2 | Which object types the coverage set covers | **Those the resolution record lists** in `object_types`, each declared by the model | All object types: dates and numbers would then need decisions whenever they repeat. Entity kind only: LI1's flat model uses value types for methods, so nothing would be covered |
| D3 | How a decision takes effect | **The manifest's renamings cite decisions, and GND verifies them.** Renaming stays the only way a value changes, and `unresolved` placeholders are renamings the host writes | GND applies `unresolved` placeholders itself, as plan §2's wording ("composition applies those as separating renamings") could also be read: a second way to change values, contrary to plan D3's "binds and verifies only" |
| D4 | A `same` decision whose keys are not joined | **Refuse** (rule 5). The decision record and the composition must agree | Allow it: a recorded `same` could silently not hold, which #193 crit 5 forbids |
| D5 | Approval instrument | **Corpus-first** (§11): serialized formats and exit codes again | Prose only: the refusal messages and the amended LI1 outcomes go unseen until implementation |
| D6 | Home of the decision policy | **A new module** `gnd.composition_resolution` at layer `model`, called by `compose` | Extending `composition.py`: one file, but ≈ 650 lines mixing two contracts |
| D7 | How the harness reads the run's identity outcome | **The `same`-connectivity of the run's resolution**, valid because R4 verified it against the composition | Recomputing joins from composed values: the harness would need role-to-object-type lookups from the model, against LI1's CLI-only rule |
| D8 | The LI1 approved expectations | **Amend them:** the reference run gains a resolution; every case gains `identity-decisions` values; M5 and M6 also fail it (no composed output); M7 is added. These go back to the owner at the corpus gate | Keep the stage dormant in LI1's corpus: then R6 has no case and plan C7's "active from LI2" is not met |
| D9 | The `Mention` id form | **`<document>@<start>-<end>`**, a string value of a `Mention` value type | A composite reference scheme (document, start, end): more structure, but it changes the anchoring pattern LI4 will build on before LI4's spec exists |
| D10 | Decision arity and evidence | **Exactly two keys, with at least one coordinate per key** | Groups of keys: fewer decisions, but a partial group is ambiguous about which pair is evidenced |
| D11 | Spec review | **None.** The corpus gate is the second look | A panel round over these bytes |

## 8. Tests and verification

### 8.1 Test list (`tests/test_li2_resolution.py` unless noted)

| # | Case | Criterion | Expected |
|---|---|---|---|
| T1 | Fixture W, flat vs resolved | R1 | flat: witness for (OpenCap Monocular, DMD) exit 0. Resolved: compose exit 0, four distinct `VampNet`/`WHAM` outcomes, the three edges present, and the same witness exit 2 (`missing`) |
| T2 | Fixture M, two mentions | R2 | `gnd check --anchors --document` exit 0. Two mention rows with one surface spelling, two senses |
| T3 | Fixture M, method/version merge without `same` | R2 | compose exit 3, `joined without a same decision`, and no value in the message |
| T4 | Fixture A, alias with `same` and evidence | R3 | compose exit 0. One composed value. Record `decisions` lists the decision on both facts |
| T5 | Fixture A, same-domain homonym with no decision | R3 | exit 3, an uncovered spelling pair |
| T6 | The same pair under `different` with separating renamings, and under `unresolved` with placeholders | R3, R7 | both exit 0 with two distinct outcomes. `unresolved` outcomes equal the placeholders |
| T7 | Uncovered joined pair | R4 | exit 3, keys and sources named, the value absent from the message |
| T8 | A renaming citing a decision about another key | R4 | exit 3 (rule 6) |
| T9 | Transitive merge across `different` | R4 | exit 3 (rule 3) |
| T10 | A mutated evidence coordinate (fact index, role, or span) | R4 | exit 3, the evidence named |
| T11 | Stale `input_sha256` | §6.2 | exit 3 |
| T12 | Bad digest with an uncovered pair; bad evidence with an uncovered pair | order | the earlier reason in each |
| T13 | A changed decision: `gnd check --composition --sources` over the old composed bytes and record | R5 | exit 3, `resolution digest differs` or `differs from the record at manifest_sha256` |
| T14 | A changed decision: `gnd replay --composition` with the new record, and the old snapshot with the old record | R5 | exit 3 `binding-stale`; exit 0 for the old snapshot |
| T15 | The existing renaming refusals with a resolution present | §0 strictness | split and contradictory renamings still refused, with the existing messages |
| T16 | No `resolution`: composition example and LI1 reference run | R5 | record and composed bytes equal goldens taken at `d09189ca` before any edit |
| T17 | One walk: four outcomes by table through `check_coverage`; source scan | rule 4 | each outcome's rule fires there; no other module compares the decision kinds |
| T18 | Hostile resolution records | totality | exit 3, no traceback, for each form in §4 |
| T19 | `tests/test_li1_assurance_report.py`: M7 false merge | R6 | exit 1, `identity-decisions` precision 3/4 |
| T20 | Time bound, 200 × 200 × 20,000 | rule 2 | under 10 s |
| T21 | `tests/test_li1_assurance_report.py`: the amended expectations of all ten cases | D8 | each report agrees with its amended expectation |

**Branch walk.**
- Every rule in §6.3 has a failing case: rule 1 T3, T5, T7; rule 2 T5;
  rule 3 T9; rule 4 T6 (an equal-to-placeholder variant); rule 5 T17 table;
  rule 6 T8.
- Every §6.4 step has a refusal case: step 1 T18, step 2 T12, step 3 T10
  and T11, step 4 T15, step 5 T7.
- Each harness branch has a case: route missing (M5, M6), route refused
  (M3), a false merge (M7), and pass (the reference run).

### 8.2 Verification-selection ledger

| Obligation | Disposition | Command | Input boundary | Invalidation |
|---|---|---|---|---|
| LI2 direct | run | `uv run pytest -q tests/test_li2_resolution.py --tb=short` | `composition*.py`, schemas, fixtures | any of those |
| LI1 harness and corpus | run | `uv run pytest -q tests/test_li1_literature_corpus.py tests/test_li1_assurance_report.py --tb=short` | harness, builder, LI1 data | harness or builder change |
| Composition consumers (plan §9 row) | run | `uv run pytest -q tests/test_composition.py tests/test_composition_example.py tests/test_witness_composition.py tests/test_public_composition_digest_1.py tests/test_public_composition_digest_3.py tests/test_public_semantic_composition.py tests/test_v62_phase3_composition.py tests/test_v62_phase4_composition.py --tb=short` | composition module, schemas, check and witness services | composition change |
| Layer map | run | `uv run pytest -q tests/test_gnd_arch.py --tb=short` | `tools/gnd_layers.json` | new module |
| Structure guard list | run | the project-hook block | as listed | always |
| Lint | run | `uv run ruff check` | repository | always |
| Component index | run | `python3 scripts/components_index.py changed --base d09189ca --strict` | `dev/components/` | always |
| Broad lanes | cadence | `uv run pytest -q -m "evidence or census"`, explicit request only | — | owner request |

## 9. Out of scope for this phase

- **Deciding meaning.** GND verifies decisions and never proposes them (plan
  D3). Name diagnostics are LI3.
- **Witness format changes.** The record names decisions per fact; naming
  them in witness nodes is LI5 (L5).
- **Assertion patterns, review on saved judgments, lineage policy.** These
  are LI4 and LI5.
- **Composition with reference populations, and includes.** They stay
  refused (literature-interop).
- **The LI1 open questions.** The evidence layouts and the symlink refusal.
- **Everything in #193 "Not proposed"**, notably fuzzy identity joins.

## 10. Size

Estimate at write time:
- **Source:** ≈ 430 lines (the new module 280, composition +70, the harness
  +80).
- **Schemas and docs:** ≈ 220 lines.
- **Builder:** ≈ 150 lines.
- **Tests:** ≈ 460 lines.

The LI1 builder came in at 2.4× its estimate, because its authored data
lived inside it. This estimate counts that data inside the builder.

## 11. Approval instrument

Proposed: **corpus-first** (D5), as in LI1.

1. **This spec.** D1–D11.
2. **The corpus gate.**
   - *Authored.* Fixtures W, M, A and R, the LI1 reference run's resolution,
     the M7 mutation, and the amended LI1 expectations (D8).
   - *Committed red.* T1–T20 fail because `resolution` is not yet
     understood. The manifest parser refuses the unknown key, and that
     refusal is the red.
   - *For your reading.* The fixture README narrates each case with its
     expected exit and refusal message.
   - *Measured first.* The R5 goldens are measured at `d09189ca` before any
     source edit.
3. **Then the implementation.** Changing an approved expected outcome
   returns it to the owner.

## 12. Implementability sweep

- **R1.** Satisfiable.
  - *The false chain needs recursion across documents.* The derived
    `method_has_ancestor_method` is recursive. Its rows across the two
    documents are not claimed by any source, which LI1 found composition
    cannot hold.
  - *So T1 uses `gnd witness`, not `gnd check`.* The witness computes the
    extension from the base facts and needs no claimed derived rows.
  - *Measured already.* The witness route over a composed population works:
    the composition example's witness test passes today.
- **R2.**
  - *Anchors per mention.* An anchor is per fact row and role, with an
    occurrence index, so two rows with one surface spelling anchor to two
    occurrences. LI1's anchor builder already computes occurrences per span.
  - *The method/version clause.* Satisfiable by rule 1, because a renaming
    `Boltz-1x → Boltz-1` makes a joined group.
- **R3 and R7.** Satisfiable by rules 1, 2 and 4, with host-written
  renamings.
- **R4.** Every listed refusal maps to one rule or step (branch walk, §8.1).
  The double-fault order follows from §6.4: steps 2 and 3 run before step 5.
- **R5.**
  - *A changed resolution file.* It changes its digest, so with the
    manifest unchanged step 2 refuses.
  - *A changed resolution with an updated manifest.* It changes
    `manifest_sha256`, so `verify_composition` refuses at "differs from the
    record".
  - *Witnesses.* They bind the record bytes, so replay with a new record is
    `binding-stale`, which is existing behavior.
  - *Without `resolution`.* No new step runs, so the bytes are unchanged.
- **R6.** Satisfiable. A `same` decision with evidence passes R4, and the
  harness compares it with the gold label `different`.
- **D8 and the existing LI1 cases.** M5 and M6 have no composed output, so
  `identity-decisions` is route-missing there and joins their failing sets.
  M3's R4 refuses, so the stage is `route_refused`. M4 and X2 keep every
  key, and pass the stage.

  **Three cases lose decision keys.** The mutation table regenerates every
  binding after its transform (LI1 §6.6), and `input_sha256` moves with
  any population change. So the builder regenerates the resolution as
  well, and keeps only the decisions whose keys and evidence still exist:
  - **M1** empties every population, so every decision is dropped and
    recall is 0/3;
  - **M2 and X1** remove `XPINN builds on PINNs` from `apinn`, the only
    `apinn` fact that holds `PINNs`, so i06 is dropped and recall is 2/3.

  M1, M2 and X1 therefore add `identity-decisions` to their failing sets.
  Each amended failing set is measured and shown at the corpus gate (D8).
- **T16 goldens.** They are measured before any edit. No requirement was
  found that no implementation can meet.
