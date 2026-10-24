# Induced knowledge

r4 (o), 2026-10-24. **Draft; awaiting owner approval. Plan review closed by its stop rule.**
Milestone: `induced-knowledge`. `auto=false`.
Inspection baseline: `a22ccde` (main, after PR #33). The request-2 fix is
proposed separately in [PR #35](https://github.com/vasiloglou/gnd-public/pull/35),
**open, not merged**, and is not an ancestor of this plan's branch (p1).

Review status (p1): r1 (SHA-256 `26fa9163…1814`) received four reader opinions
— three request-changes, one approve-with-fixes, 12 reproduced blocking findings;
see [round-1 disposition](plan-review-r1-disposition.md). The owner accepted the
disposition's proposed repairs and its proposed answers for D8–D13 on 2026-10-23
(o); the accepted disposition is commit `642cade` (p2). r2 (SHA-256 `d1a40a89…7c85`)
applied them and received the single declared confirmation round: three
approve-with-fixes, one request-changes; 10 of 12 round-1 blockers resolved;
self-inflicted ratio 0.95, so review stopped
([round-2 disposition](plan-review-r2-disposition.md), commit `73a76ad`) (p2).
The owner then confirmed D12's reading and directed repairs P-1..P-9 as r3
with no further review round, 2026-10-23 (o). On 2026-10-24 the owner ruled
D1–D6 and replaced the string description with a JSON object (D14); r4 records
those rulings and nothing else (r4). **r3 and r4 bytes carry no review
opinion.** No plan or spec approval exists.

Change tags: `(p1)` marks text added or changed in r2 in response to round 1;
`(p2)` marks text added or changed in r3 in response to round 2; `(r4)` marks
text changed in r4 to record the 2026-10-24 rulings; `(o)` marks an owner
ruling. The r1→r2 tags were incomplete (C3-F3): r2 also reworded D1–D6,
IK-R8 and IK-O9–O12 without tags; r3 tags those sites `(p2)` and restores the
r1 D1–D6 cost readings. The retained snapshots under `evidence/` are the
authoritative record of each revision's bytes.

## Goal, status and completion predicates

Let a host that holds *real* labelled populations turn them into reviewed model
knowledge inside GND: describe what an object type is, score a candidate rule
against labelled examples, discover candidate constraints from a population,
round-trip rules through an inductive logic programming (ILP) learner, and admit
each result through `gnd evolve` with provenance that says it was induced.
Admission stays a reviewed act. Nothing induced becomes `confirmed` without a
recorded owner review (p1).

Planning only. The first phase's [draft spec](phase-IK1-spec.md) awaits plan
approval and its own owner gate. No implementation, measurement or approval is
claimed here.

Completion requires (p1, rewritten):

1. **IK1:** an optional object-type `description` JSON object (D14) validates.
   Its fixed core keys render in model verbalization, the constraint-blind
   extraction vocabulary and generated tool docstrings; its extra keys are
   carried unchanged and never rendered as prose (r4). `gnd diff` reports description changes and exits as it does today
   for otherwise-identical models. `gnd evolve preview` lists them on an
   `annotation` surface. For every named fixture without descriptions, the
   SHA-256 of each rendered output equals the value captured at IK1's base
   commit, named at the IK1 spec gate after PR #35's disposition (p2). The
   outputs covered are verbalization, vocabulary, extraction projection,
   codegen tree, conformance payload, diff JSON and evolve preview.
2. **IK2:** source kind `induced` with a required `provenance.induction` block
   validates.
   - New induced constraints are admitted only as `proposed`/`deontic`.
   - An induced constraint becomes `confirmed` only by a status change of an
     existing `proposed` induced constraint carrying `reviewed_in`; discover and
     import output never carry `reviewed_in` (p2).
   - `provenance.induction` is refused under any other source.
   - `gnd coverage` lists induced elements.
   - Coverage reports without induced elements equal their committed goldens.
3. **IK3:** `gnd measure --labels` scores real populations in two declared label
   modes.
   - Per-constraint expected states use the existing truth table unchanged.
   - Host class labels use a new agreement scorer with fixed, named cells, each
     with a numerator and denominator.
   - Measurement reports built from synth sidecars stay byte-identical.
4. **IK4:** `gnd discover` emits only candidates that meet two conditions in the
   `gnd check` report over the same population: the constraint's verdict is
   `pass`, and its support (as defined in the IK4 spec) is greater than 0.
   - Candidates already present, or entailed under the IK4 suppression catalogue,
     are not emitted; they are counted instead.
   - The output is an evolve proposal that IK2's gate admits.
   - A deterministic work counter stays at or below the ceiling fixed in the IK4
     spec on the fixed near-cap fixture.
5. **IK5:** a tool-neutral bridge (D4). One GND export format writes background,
   examples and modes, and the first learner adapter (Popper) renders it,
   reproducible as one committed golden digest across two runs with different
   `PYTHONHASHSEED` (r4).
   - Import accepts only clauses in the declared clause-to-`guarded` fragment and
     emits `guarded` constraints, never `derivation_rule` (D8).
   - Import refuses with a named non-zero exit when the set of example ids that
     GND's re-evaluation covers differs from the learner-reported set.
6. **IK6:** one public anonymized walk exits 0 at every step: labels → measure →
   discover and learn → evolve preview. Docs, skill surfaces and entry-point
   registrations are updated, and each listed census row has a check.
7. Every phase has:
   - approval;
   - focused checks;
   - independent diff review;
   - refactoring review;
   - a record.

   Close has four-reviewer evidence, a question sweep, a PR and separately
   recorded owner acceptance.

No delivery date is committed.

## 0. Binding design rules

| ID | Rule |
|---|---|
| IK-R1 | Induction proposes; review admits. No phase adds a path from observed or learned evidence to `status: confirmed` or `modality: alethic` without an explicit, recorded owner review (`reviewed_in`) through evolve. **Every artifact an inducer can emit is gated by D-12; induced rules are emitted as gated constraints only, never as ungated `derivation_rule` (p1, D8).** |
| IK-R2 | Evidence is exact and reproducible. Support, counterexamples and coverage are computed by GND from named inputs whose digests are recorded, using per-family definitions fixed in the phase spec (p1). A learner's or host's own numbers are claims to check, never inputs to trust. |
| IK-R3 | Additive compatibility. Existing models, populations, sidecars, measurement reports, diff output and every rendered output without the new fields stay valid and byte-identical, proven by SHA-256 values captured at each phase's named base commit for named fixtures (p1, p2). A model version bump needs D1. A wire-format version change (diff, measurement, coverage) is a decision in the owning phase spec (p1). |
| IK-R4 | One schema home. Edit `src/gnd/skills/gnd-orm-core/references/*.schema.json` and keep the vendored copy byte-identical (`tests/test_schema_sync.py`). Embedded schema copies without a sync test (e.g. `report.schema.json` `$defs.diff_reference_report`) change in the same phase as their source (p1). Normative prose lives in the gnd-orm-core references; docs cite it. |
| IK-R5 | Free text is untrusted. Descriptions, labels and learned clause text pass through the existing neutralizers (`verbalize._neutralize`, `codegen.docstrings` delimiter rule) and never execute. |
| IK-R6 | Inputs are capped before reading, and loaders are total over arbitrary JSON (standing rule 1). Discovery evaluates the whole closed-world population, never one fact type in isolation (p1). The honest memory bound is one population of at most 10 MiB in memory, plus bounded derived indexes. Each new work path ships a deterministic work-counter test against a ceiling fixed in its spec (standing rule 2). |
| IK-R7 | Layer homes follow `tools/gnd_layers.json`; new modules are assigned before use; allowance count stays zero; ModelIndex is the shared query path; family hooks register in `constraint_families.FAMILIES`. New command groups also update the closed `lanes` list, `RF5_COMMAND_GROUPS` (`tools/gnd_arch.py`) and `gnd_entrypoints.json`, with `*.service` lane modules. New model reads stay within the RF6 query ceiling or amend it explicitly (p1). |
| IK-R8 (p2: reworded in r2) | No external solver is a runtime dependency. ILP tools are optional, invoked only by explicit command with bounded execution through `gnd.process.run_bounded_process`, and absent tools give a named refusal. |
| IK-R9 | All six process-phase standing rules bind every spec by name. |
| IK-R10 | Privacy. Fixtures are synthetic or anonymized; downstream applications are not named in public text, issues, PRs or fixtures. |
| IK-R11 (p1) | Induction evidence never persists host data. `provenance.induction` and discovery counterexamples carry example ids that are opaque or relative to a declared manifest, plus SHA-256 digests of values; they never carry host filesystem paths or raw population values. Each loader enforces this, with a hostile-input test. |
| IK-R12 (p1) | Bounds before results. Every numeric bound is fixed in its phase spec before implementation, and never moved after measurement without an owner-recorded amendment that states its arithmetic. This covers work ceilings, the counterexample cap, the manifest cap, the set-comparison pair cap, the value-domain size and the near-miss rule. |

## 1. Scope, sources and authority

Framework runtime work. A `gnd coverage` census does not establish whether
these capabilities exist, so it does not settle scope.

| Source | Authority / use |
|---|---|
| [Issue #34](https://github.com/vasiloglou/gnd-public/issues/34), requests 1–6 | Requested capabilities; reporter's pin `add0c2b` |
| Request-2 fix proposed in [PR #35](https://github.com/vasiloglou/gnd-public/pull/35) (open) (p1) | Discharges request 2 if merged; IK1 is the fallback owner otherwise |
| [Round-1 review disposition](plan-review-r1-disposition.md) (p1) | Repairs and D8–D13 accepted by owner 2026-10-23 (o) |
| `src/gnd/schema/orm-meta.schema.json` `object_type` (`additionalProperties: false`), `source_kind`, `provenance_policy` | Request 1 and 6 schema homes |
| `src/gnd/evolve/service.py` `_enforce_d12`, `_constraints`, `_surface_index`; `evolve/models.py` `BlastRadiusEntry.surface` (p1) | D-12 refuses any new constraint unless it is `llm-inferred` (proposed/deontic) or `user-supplied` (confirmed); D-12 reads constraints only, not derivation rules; surfaces are a closed `Literal` |
| `src/gnd/checker/_reports.py` `has_alethic_fail`, `band` (p1) | Any derivation `fail` counts as alethic; deontic `warning` leaves the exit code at 0 |
| `src/gnd/measure/` (`truth.py`, `score.py`, `report.py`), `synth/provenance.py` `ExpectedState`, `measurement.schema.json` | `ExpectedState` needs `ground_truth` and `expected_verdict`; reports already publish numerators/denominators (p1) |
| `src/gnd/population.py` `MAX_POPULATION_BYTES` | 10 MiB cap enforced before parsing; whole population parsed in memory |
| `src/gnd/anchors.py` `vocabulary_digest`; `diff.py` `diff:vocabulary-mismatch`; `api.py` diff path (p1) | Vocabulary digest hashes whole object types; diff refuses (exit 3) when digests differ |
| `src/gnd/extract/projection.py` `_ALLOWED_KEYWORDS`; `src/gnd/vocabulary.py` `render_verbalization` (p1) | Projection is shape-only with a fail-closed keyword allowlist; the constraint-blind vocabulary is the extraction text seed |
| `diff.schema.json` (`gnd-diff/1`, `additionalProperties: false`), `report.schema.json` `$defs.diff_reference_report`, `redaction.py` diff branch, `diff.reference.md` (p1) | Diff wire contract and its embedded copy |
| `tools/gnd_layers.json` (closed `lanes`), `tools/gnd_arch.py` `RF5_COMMAND_GROUPS`, `gnd_entrypoints.json`, `tests/test_rf6_query_policy.py` (p1) | Homes, lanes and entry-point policy for new commands |
| `src/gnd/export/` (lean, souffle, pyrel), `src/gnd/rai_import.py` | Existing export targets; only import path is create-once dialect import |
| `src/gnd/model_verbalization.py`, `codegen/docstrings.py`, `coverage.py` | Rendering and reporting consumers |
| gnd-orm-core references: `provenance-and-modality.md`, `representation-format.md`, `verbalization-patterns.md`; gnd-model-evolve `evolution-contract.md` (p1) | Normative prose homes |
| `AGENTS.md`, `CONTRIBUTING.md`, process-phase references incl. `review-convergence.md` | Binding development rules |

### Harvested obligation ownership

| ID | Obligation (source) | Evidence class | Phase / gate |
|---|---|---|---|
| IK-O1 | Object-type description, rendered by verbalization, extract, codegen; carried by diff, evolve (req 1) | requested | IK1-C1..C5 |
| IK-O2 | Role-scoped value verbalization (req 2) | requested; fix proposed in PR #35 (open) (p1) | PR #35; fallback IK1 if #35 is not merged before IK1's spec gate (p1) |
| IK-O3 | Measure over host-labelled real populations, numerators/denominators (req 3) | requested | IK3-C1..C4 |
| IK-O4 | Discovery of seven families with support and counterexamples, as evolve proposal, `status: proposed`, observed source (req 4) | requested | IK4-C1..C5 |
| IK-O5 | 10 MB cap; stream or per fact type (req 4 note) | requested constraint; per-fact-type evaluation rejected as unsound (p1) | IK-R6, IK4-C4 |
| IK-O6 | ILP export of background, examples, modes (req 5) | requested | IK5-C1 |
| IK-O7 | ILP import with faithful re-evaluation (req 5) | requested | IK5-C2..C4 |
| IK-O8 | Induced provenance: source kind, inducer identity, example ids, support, confidence, counterexamples, evidence digests; accepted by evolve preview, shown by coverage (req 6) | requested; "confidence" kept only where defined (p1) | IK2-C1..C4 |
| IK-O9 (p2: reworded in r2) | A `gold` source kind "alongside GR-12" (req 6) | **not found** in this repository | D3 |
| IK-O10 (p2: reworded in r2) | D-12 refuses every new source other than llm-inferred/user-supplied, including `sample` | inspected conflict | D2; IK2-C2 |
| IK-O11 (p2: reworded in r2) | Measure keys labels by positional refs | inspected risk | IK3-C1; D5 |
| IK-O12 (p2: reworded in r2) | Rendered-output digests in committed fixtures | inspected risk | IK1-C4 |
| IK-O13 | Four-reviewer plan/close bar and explicit instrument | inherited protocol | D7 (o); plan and close gates |
| IK-O14 | Anonymity of downstream reporter | owner rule | IK-R10; every diff review; D13 (p1) |
| IK-O15 (p1) | D-12 does not see derivation rules; derivation `fail` is alethic | reviewed defect class (R1-F1) | IK-R1; D8; IK5-C2 |
| IK-O16 (p1) | No path to confirm induced knowledge without losing its marker | reviewed gap (R1-F7) | D9; IK2-C2 |
| IK-O17 (p1) | Induction evidence may leak host paths and values | reviewed gap (R3-F4) | IK-R11; IK2-C1; IK4-C3 |
| IK-O18 (p1) | Host already holds 1,880 uniqueness constraints in its own format (req 4 "without it") | issue note | Disposition: no import obligation. Discovery output is the migration path; the host may compare its set to IK4 output. Not a GND acceptance gate. |
| IK-O19 (p1) | "Without it" fallbacks: description text in `provenance`/`deontic_note`, host sidecars for gold-derived constraints (req 1, 6) | issue note | Disposition: existing models using those fallbacks stay valid (IK-R3); GND does not migrate them. A host may move text into `description` through an ordinary evolve proposal. |
| IK-O20 (p1) | Source issue names a downstream application in public | reviewed (R3-F5) | D13 (o): editing the issue text is an owner act; GND text never repeats the name |

## 2. Contract proposal and product behavior

**Request 1 (IK1)** (p1, revised).
- **Field (D14 (o), r4):** `object_types[].description` is an optional JSON
  object with a fixed core plus extras. The core keys are `summary` (what one
  instance is; required when `description` is present), `row` (what one fact
  or record about it means), `source` (where the knowledge came from) and
  `notes`; each is a non-empty string whose length cap the IK1 spec fixes under
  IK-R12. Any other key is an extra: any JSON value, carried unchanged by the
  model, diff and evolve, and never interpreted or rendered as prose. The r3
  512-character string and its rationale are withdrawn. There is no version
  bump (D1 (o)). Core strings are rendered escaped but **uncapped** (C2-F1, p2).
- **Model verbalization:** appends the neutralized core keys, in fixed order,
  to the object type's sentence. Extras appear only in the existing
  `canonical=` machine field, which already carries every key.
- **Extraction:** the constraint-blind extraction vocabulary
  (`gnd.vocabulary.render_verbalization`) renders the core keys. The shape-only
  projection schema and its keyword allowlist are unchanged.
- **Codegen:** adds `summary` to the docstrings of tools whose roles use the
  type.
- **Vocabulary digest (D11):** `anchors.vocabulary_digest` excludes
  `description`, so a description-only change keeps the vocabulary identity. No
  existing digest changes, because no current model carries the key. As a
  consequence, the vocabulary digest no longer identifies the rendered
  vocabulary text: an extraction sidecar stays bound when only a description
  changes. This is intended and pinned by a test (p2, C1-F5).
- **Diff (D12):** `gnd diff` emits an `annotations` list only when some
  description differs, and then labels its output `schema_version: "gnd-diff/2"`.
  Otherwise the output stays byte-identical `gnd-diff/1`. These change in the same
  phase:
  - `diff.schema.json` and its `report.schema.json` embedded copy;
  - a test pinning that redaction passes `annotations` through unchanged
    (the redaction diff branch itself is not edited);
  - `diff.reference.md`;
  - the RF1 mutation anchor.
- **Evolve:** indexes `object_types[id].description` as surface `annotation`,
  only when present. `BlastRadiusEntry.surface` and `evolution-contract.md` gain
  that member.

**Request 6 (IK2)**.
- **Source kind:** `induced`, with a required `provenance.induction` block. No
  `gold` source kind; a gold-answer origin is recorded as the block's `method`
  (D3 (o), r4).
- **Block shape (p1):**

  ```
  {inducer: {name, version}, method, manifest_sha256,
   examples: [opaque-id…], support: {numerator, denominator},
   counterexamples: [opaque-id…] (≤ cap fixed in the IK2 spec),
   evidence: [{ref, sha256}…]}
  ```

  - `ref` is manifest-relative.
  - There are no raw values and no absolute paths (IK-R11).
  - `confidence` is present only for methods that define it, with its formula
    named.
- **Modality:** D-03 default modality is deontic.
- **Gate (p1, D9):** `_enforce_d12` admits `induced` in exactly two cases, and
  refuses `provenance.induction` under every other source:
  - as `proposed`/`deontic`;
  - as `confirmed` only as a status change of an existing `proposed` induced
    constraint, with `provenance.reviewed_in`; a new constraint arriving already
    `confirmed` is refused, and discover/import output carrying `reviewed_in` is
    refused (p2, C1-F3). (r2's "`imported` precedent" wording is withdrawn: D-12
    refuses `imported` outright.)
- **Coverage:** gains a provenance view of induced elements.

**Request 3 (IK3)** (p1, revised). `gnd measure MODEL --labels MANIFEST`. The
manifest is capped, lists populations by relative path and SHA-256, and declares
exactly one label mode:
- **Mode `expected-state`:** each population gives, per named constraint, an
  `ExpectedState{ground_truth, expected_verdict}`. It feeds the existing
  `classify`/`score_constraint` and report unchanged.
- **Mode `class` (D10):** each population carries a host class `positive` or
  `negative`, plus a declared mapping of which class a named rule should fire on.
  - A new agreement scorer reports these cells, each with its numerator and
    denominator:
    - `fired_on_negative`
    - `fired_on_positive`
    - `silent_on_negative`
    - `silent_on_positive`
    - `vacuous` (separate, never folded)
    - `unchecked` (separate, never folded)
  - "Fired" means verdict `warning` or `fail` for that constraint; "silent" means
    `pass`.
  - The host never supplies GND's own `no-subjects` evidence.

Constraints are named by `id` (D5 (o)); positional refs are accepted only for
constraints without an `id`, and a ref naming an unknown `id` is refused with a
named error (r4). Only class mode adds a report version. Reports built from synth
sidecars stay byte-identical.

**Request 4 (IK4)** (p1, revised). `gnd discover MODEL POPULATION [--families …]`
works as follows:
- **Input:** reads one capped population and builds the same closed-world
  universe as `gnd check`.
- **Candidates:** proposes candidates of the seven families.
- **Bounds (D6 (o), r4):** value candidates only for roles with at most 20
  distinct values; set-comparison pairs only between roles played by the same
  object type, up to a pair cap fixed in the IK4 spec. These are defaults: a
  run may override each by flag, and the report states the bounds used and
  counts every role and pair skipped by a bound.
- **Admission test:** runs `gnd check`'s evaluator on the model plus candidates
  and keeps a candidate only if its verdict is `pass` and its support is
  greater than 0. Vacuous candidates are never emitted.
- **Suppression:** candidates already declared, or entailed by declared
  constraints under a closed, modality-blind catalogue fixed in the IK4 spec, are
  counted per catalogue rule and not emitted. The catalogue covers:
  - equality ⇒ subset;
  - frequency max 1 ≡ uniqueness;
  - unscoped value ⇒ role-scoped value;
  - reference scheme ⇒ uniqueness;
  - spanning uniqueness, which is trivial.
- **Canonical forms:** frequency candidates use the tightest observed
  `[min, max]`, and min 1 alone is never emitted.
- **Support:** the per-family numerator and denominator are defined in the IK4
  spec. Discovery has no "confidence", since emitted candidates always hold.
- **Near-misses:** reported separately with counterexamples, by the rule fixed in
  the IK4 spec, and never as constraints.
- **Output:** an evolve proposal whose constraints are
  `source: induced, status: proposed, modality: deontic` (the r1 `sample` option
  is withdrawn).

**Request 5 (IK5)** (p1, revised; D4 (o), r4).
- **Tool-neutral bridge:** GND owns one learner-independent export format
  (background facts, examples, mode declarations derived from fact-type roles)
  and one import contract (below). Each learner connects through its own small
  adapter that translates to and from that format. The first adapter is
  Popper; further adapters (for example an LLM proposer, a neural rule learner
  or integer-programming rule sets) are later work on the same bridge and are
  not in this milestone.
- **Export:** `gnd export ilp --target <adapter> MODEL --labels MANIFEST`
  writes the neutral form through the named adapter.
- **Import:** `gnd import ilp-rules MODEL CLAUSES --labels MANIFEST
  --reported-coverage FILE`:
  - accepts only the declared clause-to-`guarded` fragment, and refuses anything
    else by construct name;
  - maps each learned clause `wrong(X) :- B1, …, Bn` by **body rewriting**
    (p2, C1-F1): one designated body literal moves into the consequent, negated;
    the remaining literals form the antecedent. A comparison literal becomes a
    `comparison` consequent with the negated operator (`V > 10` → `V <= 10`); a
    positive atom becomes an `absence` consequent, which must be ground per
    representation-format.md. The head `wrong(X)` is a host label and never
    becomes a fact type;
  - the fragment is restricted to clauses whose bodies are conjunctions of
    positive atoms and comparisons over declared fact types; negation as
    failure, aggregates, disjunction and non-ground absence are refused by
    construct name (p2). The fragment table states, per accepted construct, how
    GND's semantics differ from the learner's (closed-world rosters, boolean
    typing, vacuity);
  - re-evaluates the result on the same examples and compares the **set** of
    covered example ids with the learner-reported set; a vacuous verdict counts
    as **not covered** and is reported separately (p2, C1-F2);
  - refuses on any difference.
- **Strength of the check:** coverage agreement is necessary, not sufficient;
  the fragment table carries the semantic argument.
- **Fixtures:** recorded learner fixtures bind the exported-bytes digest and the
  learner name and version.
- **Output:** an evolve proposal under IK2 provenance (D8).

## 3. Dependencies and artifact homes

DAG (p1): **IK1 → IK2 → IK4**, **IK3 → IK5**, **IK2 → IK5**, **{IK4, IK5} → IK6
→ close**.
- IK1 precedes IK2 because both edit the orm-meta twins and
  `evolve/service.py`.
- IK3 depends only on the measure package and may run after IK1, in parallel
  with IK2, under merge sequencing.
- IK4 needs IK2's gate, not IK3.

Six implementation phases; close is a separate gate.

| Artifact | Proposed home |
|---|---|
| Plan, specs, records, evidence | this milestone directory |
| Schema changes | gnd-orm-core `orm-meta.schema.json` (canonical) + vendored twin; diff schema + `report.schema.json` embedded copy (p1); new manifest schema beside `measurement.schema.json` |
| Description rendering | `model_verbalization.py`, `gnd/vocabulary.py` (p1), `codegen/docstrings.py`, `anchors.py` (p1), `diff.py`/`api.py` diff path (p1), `evolve/service.py`, `evolve/models.py` (p1) |
| Induced provenance gate | `evolve/service.py` `_enforce_d12`; `coverage.py` |
| Labelled measurement | `src/gnd/measure/` new label-source and agreement-scorer modules in the existing `measure` lane |
| Discovery (p1) | `src/gnd/discover/` as a new `discover` lane: add to the closed `lanes` list, `RF5_COMMAND_GROUPS`, `gnd_entrypoints.json`, with `discover/service.py` as the service target. Reuses checker family evaluation through ModelIndex. |
| ILP bridge (p1) | export in the existing `export` lane (`src/gnd/export/ilp*.py`); import as a `gnd import` subcommand beside the rai-orm importer, home and lane fixed in the IK5 spec with layer-map updates; bounded process via `gnd.process.run_bounded_process` |
| Fixtures | `tests/fixtures/induced_knowledge/` (synthetic, anonymized) |
| Docs | gnd-orm-core references; gnd-model-evolve evolution contract (p1); `docs/` guide; release notes |

## 4. Phases, criteria and residuals

### IK1 — Object-type descriptions

Draft spec r4: [phase-IK1-spec.md](phase-IK1-spec.md) (p1, r4).

- **IK1-C1 (r4):** the schema accepts an optional `description` object with core keys `summary` (required), `row`, `source`, `notes` and any extra keys, and both copies stay identical. `gnd validate` exits 0 for a minimal and a maximal core plus extras, and exits 3 for a string, an empty object, a missing `summary`, a non-string or empty core value and a core value over its cap.
- **IK1-C2 (r4):** model verbalization, the extraction vocabulary and codegen docstrings render the neutralized core keys with no truncation; extras appear in none of their prose. The projection schema and allowlist are unchanged (p1).
- **IK1-C3:** `anchors.vocabulary_digest` ignores `description` (D11). `gnd diff` of two models differing only in a description exits as for identical models. It emits `annotations` under `gnd-diff/2`, and both diff schemas validate the result (D12) (p1).
- **IK1-C4:** for the named fixtures without descriptions, the SHA-256 of each output equals the value captured at IK1's base commit (named at the IK1 spec gate after PR #35's disposition), using the exact commands listed in the IK1 spec (p2). The outputs are verbalization, vocabulary, extraction projection, codegen tree, conformance payload, diff JSON and evolve preview (p1).
- **IK1-C5 (p1):** evolve preview lists a description-only change on the `annotation` surface, which validates in `BlastRadiusEntry`. `representation-format.md` (field and vocabulary-digest composition, line 272), `constraint-reference.md` (vocabulary-digest composition, line 47), `evolution-contract.md`, `diff.reference.md` and the gnd-extract skill references are updated; reference updates are review-checked, not test-checked (p2).

### IK2 — Induced provenance and admission

- **IK2-C1:** the new source kind and its required induction block validate, with hostile-input cases including absolute paths and raw values, both refused (IK-R11) (p1). The D-03 table is updated in one home.
- **IK2-C2 (p1, p2):** evolve preview admits new induced constraints only as `proposed`/`deontic`, and a `proposed`→`confirmed` status change only with `reviewed_in`; a new constraint already `confirmed`, and any discover/import output carrying `reviewed_in`, is refused. It refuses every other combination, and `provenance.induction` under other sources, each with a named reason. Existing D-12 outcomes are pinned unchanged.
- **IK2-C3 (p1):** coverage lists induced elements with inducer, support and evidence digests. `tests/test_public_coverage_goldens.py` goldens stay byte-identical.
- **IK2-C4 (p1):** the counterexample cap and block size bounds are fixed in the IK2 spec, with a loader test at each boundary.

### IK3 — Measure over host-labelled populations

- **IK3-C1:** a capped, digest-bound label manifest loader, total over arbitrary JSON. Refs are id-keyed or positional, and unknown refs are refused. The manifest cap is fixed in the spec (p1).
- **IK3-C2 (p1):** `expected-state` mode yields reports identical to an equivalent synth-sidecar measurement of the same populations and expectations.
- **IK3-C3 (p1):** `class` mode's agreement cells are exact on a control. A deontic rule fires on every negative-class population and on no positive one, giving numerators equal to denominators in `fired_on_negative`/`silent_on_positive`. A deliberately wrong rule moves those counts. Each cell's denominator is the number of populations of that class whose verdict for the rule is decided (`pass`, `warning` or `fail`); `vacuous` and `unchecked` populations are excluded from those denominators and reported with their own counts (p2).
- **IK3-C4 (p1):** synth-sidecar reports are byte-identical to committed goldens. A deterministic work counter over manifest size stays within the spec's ceiling.

### IK4 — Constraint discovery

- **IK4-C1 (p1):** every family has a positive case and a counterexample case. For every emitted constraint ref, the `gnd check` report verdict is `pass` and support is greater than 0. A seeded wrong discoverer that emits a violated deontic candidate fails this test.
- **IK4-C2:** the output is a valid evolve proposal that IK2's gate admits and `evolve preview` renders.
- **IK4-C3 (p1):** support numerators and denominators per family match an independent brute-force oracle on small fixtures. Counterexamples are opaque ids (IK-R11).
- **IK4-C4 (p1, r4):** whole-population evaluation within the 10 MiB cap. A deterministic work counter stays at or below the spec's ceiling on a fixed near-cap fixture at the default bounds. The value-domain and pair bounds are enforced, overridable per run by flag, and the report states the bounds used and counts every skipped role and pair (D6).
- **IK4-C5 (p1, p2):** suppression counts per catalogue rule equal the expected counts on a fixture exercising every catalogue row, including a declared alethic constraint suppressing its deontic twin. The IK4 spec also fixes, under IK-R12, a candidate-vs-candidate redundancy rule (e.g. equality emitted instead of its two subsets; uniqueness instead of frequency `[1,1]`) and states that "min 1 alone" means a frequency whose only bound is `min: 1` (C1-F4).

### IK5 — ILP bridge

- **IK5-C1 (p1, r4):** the neutral export form and its Popper rendering each equal a committed golden digest across two runs with different `PYTHONHASHSEED`. Modes are derived from fact-type roles; examples come from IK3 manifests. The import contract (C2–C4) is stated against the neutral form, not against Popper.
- **IK5-C2 (p1, p2):** import emits only `guarded` constraints by body rewriting. Every construct outside the fragment (NAF, aggregates, disjunction, non-ground absence) is refused by name, with one test per refused construct; a fixture clause maps to a schema-valid guarded constraint.
- **IK5-C3 (p1, p2):** re-evaluation compares sets of covered example ids, vacuous = not covered. A fixture with equal counts but different sets refuses, a fixture whose only difference is a vacuous example refuses, and a matching fixture is admitted as a proposal.
- **IK5-C4 (p1):** recorded learner fixtures bind the exported-bytes digest and the learner name and version, and a mismatched binding refuses. A live learner run, when installed, is evidence only, never a required lane.

### IK6 — End-to-end example, docs, integration

- **IK6-C1 (p1):** a public anonymized walk exits 0 at every step: labels → measure → discover and learn → evolve preview. Its outputs match committed goldens.
- **IK6-C2 (p1):** docs, gnd-orm-core references and affected packaged skills are updated: gnd-extract, gnd-model-evolve, gnd-codegen, gnd-orm-core. The skill-surface census is a committed table listing each packaged skill file, whether it changed and why; a new test asserts every packaged skill file appears in it exactly once (p2). Twin identity remains checked by the existing skill sync tests.
- **IK6-C3 (p1):** these controls pass:
  - API and CLI pins;
  - the RF5 entry-point test (`test_rf5_commands.py`);
  - the closed-lane and layer checks;
  - the RF6 query ceiling;
  - the RF layering and source-scan controls;
  - the installed-candidate check for new entry points.

### Carried limitations

| Item | Disposition |
|---|---|
| Request 2 | proposed in PR #35 (open); IK1 fallback owner if unmerged at IK1's spec gate (p1) |
| GR-12 / `gold` | not present in this repository; not added (D3 (o), r4) |
| 1,880 host constraints (p1) | IK-O18: no import obligation |
| "Without it" fallbacks (p1) | IK-O19: remain valid, not migrated |
| Model-level thesaurus (issue "Not requested") | out of scope |
| Use of derived fact types inside host plans | host compiler's responsibility (issue "Not requested") |

## 5. Documentation, skill and compatibility surfaces

- **IK1:** changes the model schema (additive), the diff wire (D12, version 2
  only when annotations are present), the extraction vocabulary and the evolve
  surface set. It edits:
  - `representation-format.md`;
  - `evolution-contract.md`;
  - `diff.reference.md`;
  - the gnd-extract references (p1).
- **IK2:** changes `provenance-and-modality.md` and the D-03 table.
- **IK3:** adds a manifest schema and a class-mode report version.
- **IK4/IK5:** add CLI commands, lanes and entry-point registrations, and must
  update `api.__all__` and signature pins if they add public Python names (p1).
- **Per phase:** packaged skills that teach provenance, extraction, codegen or
  evolve are inspected, with edits only where behaviour changed.

## 6. Risks and required controls

| Risk | Control / owner |
|---|---|
| Induced items slip into confirmed knowledge | IK-R1; D9; IK2-C2 refusal pins |
| Learned rule becomes an ungated hard rule (p1) | D8: guarded-only output; IK5-C2 |
| Description text injects into prompts or code | IK-R5; neutralization tests in IK1 |
| Description change breaks extraction or diff (p1) | D11 vocabulary digest; vocabulary not projection; IK1-C2/C3 |
| Discovery explodes on pairwise families | IK-R6, IK-R12; pair cap; IK4-C4 work counter |
| Overfitting: candidates hold by accident on small samples | support numerator/denominator always reported; no admission threshold implied; review decides |
| Violated deontic candidates pass a weak check (p1) | IK4-C1 per-ref `pass` + support > 0, seeded wrong-discoverer test |
| ILP translation changes meaning | fragment table; set-equality coverage; IK5-C2/C3 |
| Host data leaks into public models (p1) | IK-R11; IK2-C1 and IK4-C3 tests |
| Measurement output churn breaks consumers | IK3-C4 byte-identity; new report version only for class mode |
| Positional refs mislabel after model edits | D5 id-keyed refs |
| Thresholds chosen after measurement (p1) | IK-R12 |

## 7. Out of scope

- running ILP learners in CI or as a required lane;
- bundling solvers;
- automatic admission or confirmation;
- induced `derivation_rule` output (D8, p1);
- a model-level thesaurus or NL lexicon;
- host plan compilers;
- changes to the verdict or band semantics of existing families;
- live database profiling (discovery reads populations only);
- editing the source issue (an owner act, D13, p1);
- publication or certification.

## 8. Execution, approval and review protocol

`auto=false`. Each phase follows process-phase:
1. harvest;
2. spec;
3. owner gate;
4. approved-spec commit;
5. implementation and focused verification;
6. independent diff review;
7. refactoring review;
8. record.

**Plan review (p1):**
- **Instrument:** four local reviewer agents (D7 (o)).
- **Round 1:** complete.
- **Declared budget** (one home: the [round-1 disposition](plan-review-r1-disposition.md) §Convergence budget) (p2): r2 plus at most one confirmation round. The round as run also reported r2-introduced defects; that widening is recorded in the round-2 disposition (C3-F4).
- **Round 2:** complete; stop rule met (ratio 0.95). No further plan review round. Remaining questions move into phase specs (p2).

**Close review:** uses the same instrument.

**Contribution:** topic branch and PR per AGENTS.md. Merge, release and
certification are separate owner acts.

## 9. Verification story and affected consumers

| Phase | Falsifiable result | Consumers |
|---|---|---|
| IK1 | boundary validation exits; renders in three surfaces; diff v2 only with annotations; digests captured at IK1's base commit unchanged (p1, p2) | `test_schema_sync.py`, `test_model_verbalization.py`, `test_extract_vocabulary.py`, codegen/conformance tests, diff and report schema tests, evolve tests, RF1 mutation table (p1) |
| IK2 | induced admitted only as specified; old D-12 outcomes pinned; coverage goldens unchanged (p1) | evolve tests, `test_public_coverage_goldens.py`, schema tests |
| IK3 | expected-state parity with synth path; class cells exact; synth goldens unchanged (p1) | measure tests, measurement schema tests |
| IK4 | per-ref pass + support > 0; oracle support; suppression counts; work ceiling (p1) | new discover tests; evolve preview; RF5/lanes/RF6 controls |
| IK5 | guarded-only; set-equality refusal; bound fixtures; golden export digest (p1) | new ILP tests; export tests |
| IK6 | end-to-end exits 0 with goldens; census table; entry-point controls (p1) | docs/link tests, API pins, RF layering, RF5 |

Exact commands are unresolved until each spec inventories changed definitions.

### Implementability sweep (author inspection, not review)

| Dependency / conflict | Proposed resolution |
|---|---|
| `object_type` forbids extra properties | additive optional property, no version bump (D1) |
| D-12 refuses `sample` and any new source | IK2 extends the gate for `induced` only (D2, D9) |
| D-12 does not see derivation rules (p1) | D8: IK5 emits gated `guarded` constraints only |
| Projection allowlist excludes `description` (p1) | render in the constraint-blind vocabulary; projection unchanged |
| Vocabulary digest covers whole object types (p1) | D11: exclude `description`; no existing digest changes |
| Diff schema closed at `gnd-diff/1` (p1) | D12: `gnd-diff/2` only when annotations present; embedded copy, reference and RF1 anchor changed together; redaction pass-through pinned, branch unedited |
| `_neutralize` escapes before its 512 cap (p1, p2, r4) | render core description strings escaped but uncapped; their input cap is fixed in the IK1 spec (D14) |
| Diff schema shape vs existing test indexing `properties` (p2) | closed top-level `properties` with optional `annotations` plus `if`/`then` on `schema_version`; no top-level `oneOf` |
| Closed surface `Literal` (p1) | add `annotation` member and contract row in IK1 |
| Measure truth table needs ground truth (p1) | two label modes; class mode uses a new agreement scorer (D10) |
| Closed lanes and RF5 policy (p1) | IK4 adds `discover` lane and command group; IK5 fixes its import home |
| No profiling code exists | new discover package reusing checker family evaluation |
| No rule import path exists | new importer emitting `guarded` constraints |
| ILP tool availability | optional, explicit, bounded; recorded fixtures bound to export digest and learner version |

## 10. Owner decisions and open questions

| ID | Decision / answer | Status |
|---|---|---|
| D1 | Additive optional fields without a model version bump. Cost: a bump would force migration of every model | **owner-ruled 2026-10-24 (o)**: no bump |
| D2 (p2: D9 clause added in r2) | Extend D-12 to admit `induced` (proposed/deontic; confirmed only per D9); leave `sample` refused. Cost: admitting `sample` too widens the gate | **owner-ruled 2026-10-24 (o)**: induced rules enter as proposed and advisory (deontic) |
| D3 | Spell the source `induced`; do not add `gold` (no GR-12 here). Cost: adding `gold` blind invents semantics | **owner-ruled 2026-10-24 (o)**: `induced` only; a gold-answer origin is recorded in `provenance.induction.method` (r4) |
| D4 (r4) | IK5 is a tool-neutral bridge: one GND export format and one import/re-check contract, with a small adapter per learner. First adapter: Popper (MIT licence, noise-tolerant learning, Datalog-shaped rules). Other families surveyed for later adapters: ILASP, integer-programming Boolean rule sets, AMIE-style exact miners, neural rule learners, LLM proposers. Cost: the neutral format is one extra layer over a single-tool exporter | **owner-ruled 2026-10-24 (o)**: tool-neutral bridge; Popper first |
| D5 | Label manifest keys constraints by `id`, positional refs as fallback for constraints without an `id`; unknown ids refused. Cost: id-less constraints stay positional | **owner-ruled 2026-10-24 (o)** |
| D6 (p2: reworded in r2; r4) | Discovery bounds: value domains ≤ 20 distinct values; set-comparison pairs between roles of the same object type, pair cap fixed in IK4 spec under IK-R12. Defaults are overridable per run; the report states the bounds used and counts every skip. Cost: fewer candidates vs runaway cost | **owner-ruled 2026-10-24 (o)** |
| D7 | Plan and close review instrument: four local reviewer agents | **owner-selected 2026-10-23 (o)**; instrument only, no artifact approval |
| D8 (p1) | IK5 emits `guarded` constraints only, never `derivation_rule` | **owner-accepted 2026-10-23 (o)** |
| D9 (p1, p2) | `induced`+`confirmed` only as a `proposed`→`confirmed` status change with `provenance.reviewed_in`; `provenance.induction` refused under other sources; discover/import output never carries `reviewed_in` | **owner-accepted 2026-10-23 (o)**; P-3 refinement directed by the owner 2026-10-23 (o) |
| D10 (p1) | IK3 class labels use a second, agreement scorer with fixed cells; expected-state labels reuse the truth table | **owner-accepted 2026-10-23 (o)** |
| D11 (p1) | `anchors.vocabulary_digest` excludes `description` | **owner-accepted 2026-10-23 (o)** |
| D12 (p1, p2) | `gnd diff` emits `annotations` and `gnd-diff/2` only when a description differs; otherwise unchanged `gnd-diff/1` | **owner-confirmed 2026-10-23 (o)**: the owner explicitly confirmed this reading after round 2 (C3-F2). r2's earlier "owner-accepted" label recorded a coordinator selection |
| D13 (p1) | The source issue's naming of a downstream application is the owner's to edit; GND text never repeats it | **owner-accepted 2026-10-23 (o)** |
| D14 (r4) | Object-type `description` is a JSON object: fixed core keys `summary` (required), `row`, `source`, `notes` that GND validates and renders, plus extra keys carried unchanged and never rendered as prose. Replaces r3's 512-character string, whose cap had no remaining basis | **owner-ruled 2026-10-24 (o)**: fixed core plus extras |

Next action (r4): plan approval; then the owner explicitly selects
`process-phase IK1 induced-knowledge`, at whose gate IK1's base commit and
PR #35's disposition are named.
