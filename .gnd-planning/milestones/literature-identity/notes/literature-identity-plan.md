# Literature identity and assertions · plan r2

**Status: draft r2, 2026-11-15. Not approved.**

- **Review.** Round 1 of the maintained panel reviewed r1 (SHA-256
  `f27c10dc…53bfe3`, commit `b75c910e`). The [review disposition](plan-review-disposition.md)
  records it.
- **Repairs.** The r2 changes are marked `(p2)`. They carry no review opinion.
  Round 2, the last in the declared budget, has not run.
- **Gates.** No owner gate is recorded, and no phase may start implementation
  before its spec gate. `auto=false`.

## Goal and completion predicates

Make the identity of a scientific entity and the meaning of an asserted
relation explicit, reviewable and bound to composition. Then show, on small
public fixtures, that a lineage built from them keeps true chains and drops
false ones. This milestone covers parts 9, 1, 2, 3 and 4 of
[issue #193](https://github.com/vasiloglou/gnd-public/issues/193). The
[partition table](#11-partition-of-issue-193) assigns the other parts to two
successor milestones.

The milestone is complete when all of these hold:

- **LI0.** `gnd witness` and `gnd why-not` accept a valid version-1 model, and
  a model with no `model_id` at any version. `gnd replay` replays the
  resulting witnesses.
- **LI1.** A public regression corpus holds the case counts declared in C1. A
  staged assurance report over it lists each named stage's denominator
  separately, and reports precision, recall and abstention. A run that drops
  every output fails the report. `(p2)`
- **LI2.** When a composition binds a resolution record, every cross-source
  identity join needs a `same` decision. This covers equal values left
  unchanged, not only renamings. A changed decision makes the composition
  record and its witnesses stale. `(p2)`
- **LI3.** A name-diagnostics report proposes homonym, synonym and family
  candidates as `unresolved` decisions, and applies none of them. Its false
  positives are measured on a predeclared sample against a predeclared budget.
- **LI4.** A contextual-assertion example meets the A criteria. A named
  producer builds the admitted population from the raw extraction, and binds
  both to the policy and the receipts. `(p2)`
- **LI5.** On the LI1 corpus, lineage rules keep every chain labelled
  supported and exclude every chain labelled false, on the development set
  and on the held-out set. Each accepted path's witness names the assertions
  and resolution decisions it rests on. `(p2)`
- The milestone close sweeps every row of the [criterion trace](#41-criterion-trace-from-193-p2)
  to a phase result, a carried row, or a recorded owner ruling.

## 0. Binding design rules

Every spec applies the six standing design rules of the
[project hook](../../../../.codex/skills/process-phase/references/project.md)
by name.

- **Totality.** Every new reader is total over arbitrary JSON, with the cap on
  the read. That covers the resolution record (LI2), the diagnostics input
  (LI3), the admission producer's inputs (LI4) and the report harness input
  (LI1).
- **Input-bounded work.** Bound work proportional to the input with a
  time-bound test. In LI2 the input is values × sources × decisions, and in
  LI3 it is occurrences × candidates.
- **Validation order.** Pin the refusal order at each boundary. In LI2 that is
  the manifest, then the resolution record digest, then the decision coverage
  set, then composition.
- **One walk per policy.** One walk enforces the LI2 decision policy over every
  identity-changing outcome: a renaming that merges, a renaming that
  separates, and an equal value joined unchanged. `(p2)`
- **One home per contract.** The composition reference stays the home of the
  composition contract, and LI2 extends it there. The judgment contract stays
  the home of saved opinions. LI4 cites it and does not restate it. LI0's
  default-omission rule gets exactly one home (§2). `(p2)`
- **Measurement over argument.** Representation disputes are settled by
  measurement.

Further rules:

- **Repository conventions.** Use ModelIndex and family dispatch. Keep the
  runtime layer allowance at zero, and add every new module to
  `tools/gnd_layers.json`.
- **Meaning stays with the host.** GND binds and verifies decisions. It never
  decides whether two mentions mean the same thing.
- **Existing checks stay strict.** Composition's one-value-one-entity rule and
  its refusal of contradictory partial renamings stay as they are (#193 part 2).

## 1. Scope, sources and authority

The baseline is `ecd12986` (main after #191 and the 0.3.1 tag at `5fe58524`).
The issue was checked against v0.3.1. This is framework development, so an
experiment-claim census cannot measure the feature coverage these phases add.

| Source and location | Obligation | Phase and gate |
|---|---|---|
| #193 part 9, "Cause" and "Acceptance criteria" | Version-1 model witnesses and replays. Regression test on the serialization path | LI0 W1–W3 |
| Local reproduction, 2026-11-14/15 (§9) | Without `model_id`, witness and why-not fail at versions 1 and 2 | LI0 W1–W2 |
| #193 part 1, "Proposal" and criteria 1–8 | See the [criterion trace](#41-criterion-trace-from-193-p2) | LI1 C1–C6, D1 |
| #193 part 2, "Proposal", criteria 1–6 and "name diagnostics" | See the criterion trace | LI2 R1–R6, LI3 N1–N3 |
| #193 part 3, "Proposal" and criteria 1–6 | See the criterion trace | LI4 A1–A5 |
| #193 part 4, "Proposal", criteria 1–7 and "dates" | See the criterion trace. The dates step goes to literature-interop LX4 | LI5 L1–L5 |
| #193 "Not proposed" | No fuzzy identity joins, no constraint quota, no ILP-first repair, no universal physics ontology. The host's own mistakes are not GND defects | All phases, §7 |
| #193 "Related issues" | Cite #66, #70, #73, #75–#78, #94, #95, #104, #119, #180, #183. Coordinate with open #179, #181, #182. Reopen nothing without a v0.3.1 reproduction | §7, close sweep |
| [Composition reference](../../../../docs/reference/composition.md) | Manifest, renaming, record and witness version-2 contracts are the home LI2 extends | LI2 |
| [Judgment contract](../../../../src/gnd/skills/gnd-dev-session/references/judgment-contract.md) | Saved opinions target supplied occurrences only. Abstention and stale bytes are already defined | LI4 |
| [Project hook](../../../../.codex/skills/process-phase/references/project.md), [CONTRIBUTING](../../../../CONTRIBUTING.md) | Owner gates, guard list, lint, topic PR, separate merge authority | All phases and close |

### 1.1 Partition of issue #193

This table is the single home of the cross-milestone partition. The two
successor plans cite it.

| #193 part | Priority in the issue | Milestone and phases |
|---|---|---|
| 9 · version-1 witness bug | P1 | **literature-identity** LI0 |
| 1 · regression corpus and assurance report | P0 | **literature-identity** LI1. The host-scale sets are D1 |
| 2 · sense-resolution decisions | P0 | **literature-identity** LI2, plus LI3 for name diagnostics |
| 3 · contextual assertions and review | P0 | **literature-identity** LI4 |
| 4 · context-qualified lineage | P0 | **literature-identity** LI5. The dates step goes to **literature-interop** LX4 |
| 5 · includes, reference populations, extraction, composition and witnesses together | P0 | [**literature-interop**](../../literature-interop/notes/literature-interop-plan.md) LX1–LX4 |
| 6 · physics and algorithm examples | P1 | [**literature-depth**](../../literature-depth/notes/literature-depth-plan.md) LD1, plus LD2 for quantities |
| 7 · multipass reading with coverage | P1 | **literature-depth** LD3 |
| 8 · semantic revisions | P1 | **literature-depth** LD4, plus LD5 for verdicts on derived claims |
| 10 · aggregate certificates | P2 | Owned by **literature-depth** as a deferred row, with its criteria carried ([§7](../../literature-depth/notes/literature-depth-plan.md#7-deferred-and-out-of-scope)). The deferral needs owner ruling P3 there `(p2)` |

The issue's order is corpus, then identity and assertions, then lineage, then
depth once the features work together. The partition follows it. Part 5 has
no dependency on parts 2–4, so literature-interop could run alongside this
milestone (D6).

## 2. Contract proposal and product behavior

**LI0.** The witness producer and the why-not path both serialize the loaded
model again before intake. That serialization keeps the loader defaults
`operations: []` and `model_id: null`. The meta-schema's version rule
(`version` 2–5) applies only when `operations` is present. So dropping the
empty list is enough for version 1, as measured in §9. A null `model_id` fails
the string type at any version.

`gnd.documents.Model` already omits some empty defaults, in two places:

- `model_dump` drops `reference_populations`;
- `_omit_empty_include_fields` drops `includes` and `fact_type_constraints`.

The omission of the two further defaults has one home. The spec chooses it by
measurement, either those existing hooks or a single wire projection that
reuses them, and does not create a third. `(p2)` (#193 calls the class
`ModelDocument`. In the source it is `gnd.documents.Model`.)

**LI1.** The fixture corpus has small paraphrased source documents with
public work identifiers. Gold annotations live in an answer key split out
from the entry point. C1 declares the counts. The staged assurance report is
an example harness over existing commands (D5).

The harness emits these named stages separately, each with its sample size,
exclusions, unresolved count and disagreements: `(p2)`

1. `model-population-validity`
2. `source-binding`
3. `semantic-support`
4. `identity-decisions`
5. `derivation`
6. `coverage`
7. `freshness`

It also reports precision, recall and abstention per stage, computed against
the answer key. It does not take them from `gnd measure --labels`. Exit codes:

| Exit | Meaning |
|---|---|
| 0 | every stage meets its declared floor |
| 1 | some stage fails, and that stage is named |
| 3 | invalid input |

`(p2)`

**LI2.** Composition gets an opt-in `resolution` entry in the manifest, with
`path` and `sha256`, and a `gnd-resolution/1` record.

**What a decision is keyed on.** A decision is keyed at composition's own
grain: a source, an object type and a source value. That keeps the
one-value-one-entity rule unchanged. Each decision cites evidence
coordinates, meaning mentions: source, fact type, fact index, role and anchor
span. It also names its producer or reviewer and its input digests. `(p2)`

**Coverage set.** With `resolution` present, consider each composed value of
an entity-typed object type that draws on two or more source keys. This
covers equal spellings that are never renamed. Every pair of those source
keys must be connected by `same` decisions.

**Rules:** `(p2)`

- A renaming that merges two keys must cite `same`.
- A renaming that separates a key to a fresh sense identifier must cite
  `different`.
- `different` is closed over the composed result. Two keys under a
  `different` decision may never end in one composed value, directly or
  through a chain of `same` decisions.
- An uncovered pair refuses with exit 3. The refusal names keys and mentions,
  never values.

**Unresolved mentions.** An `unresolved` decision never joins two keys. Its
mentions stay distinct and carry no sense. LI4 and LI5 can therefore still
represent and query them. `(p2)`

**Record fields.** The composition record gains `resolution_sha256`, and a
per-fact list of the decision indexes applied, which mirrors `renamings`.

**Senses inside one document.** When one document uses one spelling for two
senses, the source is not rewritten. The reviewed replacement population
models occurrences as `Mention` entities identified by document and span.
The anchored role is the mention's surface text, so anchors still match. The
sense is a separate fact type over the mention. `(p2)`

A manifest without `resolution` behaves exactly as in 0.3.1.

**LI3.** A report runs over the original occurrences, before any renaming,
with its own normalization and distance. The `why_not` near-miss key does not
fit, because it cannot pair `$PINN` with `PINNs`. Each candidate carries a
kind (`homonym`, `synonym`, `family`) and a `score` in [0, 1]. The threshold
`T` is declared in the spec before any measurement. `(p2)` The candidate kinds:

- **Homonyms:** one value in contexts that do not overlap, or case variants of
  one acronym. The signal is suppressed when the uses share an introducing
  work. `(p2)`
- **Synonyms:** values within the declared distance whose contexts overlap.
- **Families:** a value used by at least `k` unrelated works, with no
  `introduces` assertion in the input. `k` is declared in the spec. `(p2)`

The report writes `unresolved` entries in the LI2 format and never applies
them. The surface is D4.

**LI4.** A worked example model:

- **The assertion:** an objectified assertion that links a work and its
  version, a specific predicate and its argument roles, and resolved
  participants or unresolved mentions.
- **Its context:** condition, regime and experiment facts.
- **Its passage record:** the passage itself, plus a `polarity` (`asserts`,
  `negates`) and an `attribution` (`own-finding`, `baseline-comparison`,
  `speculation`, `cites-other-work`). `(p2)`
- **Its records:** extraction and review are kept as separate records.

A review rubric maps each disposition onto saved-judgment verdicts:

| Disposition | Saved-judgment verdict |
|---|---|
| supported | approve |
| contradicted | reject |
| stretched | reject. Proposed under D7, not ruled `(p2)` |
| insufficient evidence | abstain |

**Admission producer.** The literature example's admission step builds the
admitted population. `(p2)` Its inputs are:

- the raw extraction population;
- the `gnd judgments` report;
- the policy.

It writes the admitted population and an admission record binding the
SHA-256 of each of those three inputs. It refuses (exit 3) when any input is
missing. The step lives in the example, per D5, and is not a `gnd` command.

**LI5.** The relations are fine-tuning, implementation, extension, component
use, training on another method's outputs, evaluated-as, compared-against,
inspired-by and taxonomic membership. Each has an explicit **path policy**, a
relation-by-query-family table that says whether the relation may chain in:
`(p2)`

- **Documented methodological lineage.**
- **Justified transfer of a result.** It needs assumption and interface
  evidence.

The derived lineage fact types carry assertion identities as roles. Witness
version 2 therefore names every assertion fact on a path. The composition
record names the decisions applied to each base fact. `(p2)`

LI5 queries the composed admitted population. Unresolved mentions appear in
it as distinct, sense-less participants. Cycles are diagnosed with every edge
reported, and no edge is deleted to make a check pass.

## 3. Dependencies and artifact homes

Phase dependencies (all acyclic, LI0 → LI5): `(p2)`

| Phase | Needs |
|---|---|
| LI0 | Nothing |
| LI1 | Nothing. It runs first among the semantic phases because it supplies their fixtures. Its mutations are only the ones that 0.3.1 commands can detect (C2) |
| LI2 | LI1 |
| LI3 | LI2 |
| LI4 | LI2 |
| LI5 | LI1, LI2 and LI4 |

Every fixture model declares `model_id` and version 2 or later, unless its
phase depends on LI0. Nothing in this milestone needs literature-interop. The
L2 cross-domain chain composes ordinary public fixture sources with the
current composition. It uses no includes and no reference populations.
`(p2)`

| Capability | Observed component and decision |
|---|---|
| Default omission | Adapt `gnd.documents.Model` (`model_dump`, `_omit_empty_include_fields`), or a single projection reusing them. The dump sites are `witness/producer.py:197` and `witness/service.py:252` (why-not). Replay through `service.replay_result` passes the raw parsed document `md` to the kernel, and the Soufflé/Lean exports parse raw bytes in their `admit` paths. None of these re-serializes `(p2)` |
| Resolution binding | Adapt `model.composition` (`src/gnd/composition.py`), its manifest schema `composition-manifest.schema.json` and record schema `composition.schema.json`. Adapt `checker._composed` for re-verification and witness version 2 for the record digest |
| Mention spans | Reuse the anchor sidecars bound per source by composition |
| Name diagnostics | A new module whose home is set by D4. Its normalization is its own (`gnd.witness.why_not` near-miss keys do not fit). Coordinate with #181 if the home is `gnd discover` `(p2)` |
| Assertion review | Reuse `src/gnd/judgments.py` and `src/gnd/commands/judgments.py` unchanged. The component id is `semantics.saved_judgments` `(p2)` |
| Admission producer | New example step (LI4), with its home set by D5 `(p2)` |
| Lineage queries | Reuse structured rules, recursion, ring/acyclic reporting (#94, #119) and witness version 2 |
| Report harness | New example harness, with its home set by D5. It reads `gnd check`, `gnd fidelity` and `gnd judgments` outputs over their supported routes |

The component index search covered composition renaming, saved judgments,
include flattening, reference populations and near-miss spelling. The index
review lists 69 descriptions older than their code, so the plan relies on
inspected source. A Review pass over the index can be selected separately.

## 4. Phases, deliverables and named criteria

### LI0 · W1–W3 · #193 part 9

- **W1.** A version-1 fixture witnesses (exit 0) and replays (exit 0). So
  does a model without `model_id`, at versions 1 and 2.
- **W2.** `why-not` on the same inputs exits 0 with its derivation result.
- **W3.** A regression test pins the round trip over the committed fixture
  models. Witness certificates for already-supported inputs match golden
  digests committed from the baseline `ecd12986` before the change. `(p2)`

### LI1 · C1–C6 · part 1

- **C1.** The corpus and its split answer key hold at least these cases.
  Every gold label cites a passage. `(p2)`

  | Category | Cases |
  |---|---|
  | Supported chains | 3, one of them cross-domain |
  | False chains | 5: the whale, a `$PINN` chain, the `$PINN` loop, Boltz-1 as ancestry, contrast as "builds on" |
  | Reuse cases | 8: 4 real, 2 generic words, 2 homonyms |
  | Assertions with support labels | 12 |

  An answer key below any floor fails C1.
- **C2.** These mutations, which 0.3.1 commands can detect, each fail their
  named stage: `(p2)`

  | Mutation | Stage it fails |
  |---|---|
  | Dropping all outputs | `semantic-support` and `derivation` |
  | Dropping one supported fact | `semantic-support` |
  | Stale evidence | `freshness` |
  | A falsified derived row | `derivation` |

  The later phases own the other mutations: false merge (R6), missing
  condition (A1) and reversed relation (L5).
- **C3.** An empty rule premise never counts as a successful test, and
  mutually exclusive flags are never combined.
- **C4.** The report states sample sizes, exclusions and disagreements, and
  that its labels are not independent expert ground truth.
- **C5.** Precision, recall and abstention are reported per stage. A fixture
  run that abstains heavily reaches high precision and must still report low
  recall. `(p2)`
- **C6.** A held-out subset is committed with its digest before LI5 starts:
  1 supported chain and 2 false chains not used in LI5 development. The whale
  is scored in the development set. `(p2)`

### LI2 · R1–R6 · part 2

- **R1.** In a two-document whale fixture where `VampNet`-style homonyms are
  spelled identically, the four senses stay distinct and the three
  legitimate direct edges survive. The false combined chain disappears.
  `(p2)`
- **R2.** Two senses with one spelling in one document are both
  representable through `Mention` entities, without rewriting the text. An
  `anchored` constraint still passes. `(p2)`
- **R3.** An evidenced alias joins across documents. A same-domain homonym
  with no supporting decision does not.
- **R4.** Each of these refuses with exit 3 and names keys and mentions, not
  values: an uncovered pair, a partially covered renaming, and a transitive
  merge across a `different` decision. `(p2)`
- **R5.** A changed decision makes `check --composition` and replay stale
  (exit 3, reason asserted). The prior snapshot replays to its original
  result. A manifest without `resolution` matches golden outputs committed
  from the baseline. `(p2)`
- **R6.** A false-merge mutation fails the LI1 `identity-decisions` stage.
  `(p2)`

### LI3 · N1–N3 · part 2 diagnostics

- **N1.** These pairs appear with these kinds. A wrong kind fails N1. `(p2)`

  | Pair | Kind |
  |---|---|
  | VAMPnet/VampNet | `homonym` |
  | WhAM/WHAM | `homonym` |
  | normalizing flow/flows | `synonym` |
  | `$PINN` within PINNs | `family` |

- **N2.** Flow matching used across fields is never emitted as a `homonym`
  with a score of `T` or more. `T` is declared before the run. `(p2)`
- **N3.** These are declared before the measurement: a sample of at least 100
  emitted candidates drawn uniformly, its labeller, per-kind denominators, and
  the budget. The false-positive rate per kind is within the budget. Nothing
  is ever applied. `(p2)`

### LI4 · A1–A5 · part 3

- **A1.** A supported conditional claim keeps its conditions. A
  missing-condition mutation fails `semantic-support`.
- **A2.** Co-occurring names with the wrong predicate fail admission.
- **A3.** Four passages of a negation, a baseline comparison, a speculation
  and a citation produce four distinct `(polarity, attribution)` pairs. None
  of them is admitted as an `own-finding` positive assertion. Conflicting
  claims under different experiments both remain. `(p2)`
- **A4.** A missing review or an abstention never becomes approval. A changed
  subject or evidence makes the review stale. Batches stay within the
  judgment-contract limits.
- **A5.** Changing one receipt changes the admitted population's digest. A
  missing raw extraction or policy refuses (exit 3), and the raw extraction
  is retained beside the admitted population. `(p2)`

### LI5 · L1–L5 · part 4

- **L1.** Every supported chain is kept and every false chain is excluded.
  Development and held-out counts are reported separately.
- **L2.** The Boltz-1 statement is kept but is not ancestry. One fixture per
  non-ancestral relation is excluded from lineage. A valid cross-domain chain
  is kept, and an invalid same-domain chain is rejected. `(p2)`
- **L3.** A path with an unreviewed edge, or with an edge whose participant
  is an unresolved mention, is not accepted. A transfer missing its required
  conditions fails.
- **L4.** Cyclic and acyclic fixtures exist, and a warning is not read as a
  failure. The original flat-model whale witness is a separate,
  documentation-only fixture outside the scored corpus. It is a
  demonstration of the old model's weakness, not a checker defect. `(p2)`
- **L5.** An accepted path's witness names its assertion facts, and its
  composition record names the decisions behind them. Removing either fails
  replay. A reversed-relation mutation fails `derivation`. `(p2)`

### 4.1 Criterion trace from #193 `(p2)`

| #193 criterion | Owner |
|---|---|
| Part 9, criteria 1–2 | W1, W3 |
| Part 1, criterion 1 (baseline denominators, snapshot) | C1 for the public corpus. The host-scale sets go to D1 |
| Part 1, criterion 2 (removing outputs cannot pass) | C2, C5 |
| Part 1, criterion 3 (omitted fact reduces recall) | C2, C5 |
| Part 1, criterion 4 (each mutation fails its gate) | C2, R6, A1, L5 |
| Part 1, criterion 5 (stages separate) | The LI1 stage list (§2) |
| Part 1, criterion 6 (empty premises) | C3 |
| Part 1, criterion 7 (supported routes) | C3 |
| Part 1, criterion 8 (sample sizes and disagreements) | C4 |
| Part 1, the three evaluation sets | Public analogues in C1 and C6. The host-scale sets go to D1 |
| Part 2, criterion 1 | R1 |
| Part 2, criterion 2 | R2 |
| Part 2, criterion 3 | R3 |
| Part 2, criterion 4 (family, method and version distinct) | R2, N1 (`family`) |
| Part 2, criterion 5 | R4 |
| Part 2, criterion 6 | R5 |
| Part 2, diagnostics | N1–N3 |
| Part 3, criterion 1 | A1 |
| Part 3, criterion 2 | A2 |
| Part 3, criteria 3–4 | A3 |
| Part 3, criterion 5 | A4 |
| Part 3, criterion 6 | A4 |
| Part 3, raw extraction retained | A5 |
| Part 4, criterion 1 (7 kept, 8 excluded) | L1 at public scale. The host-scale sets go to D1 |
| Part 4, criteria 2–3 | L2 |
| Part 4, criteria 4–5 | L3 |
| Part 4, criterion 6 | L4 |
| Part 4, criterion 7 | L4 |
| Part 4, dates | Carried to literature-interop LX4 |

The #193 numbers (16 chains, 50 reuse cases, 7 supported and 8 false chains,
a 24-paper pilot, a 180-assertion audit) are host-scale and host-owned under
D1. The public corpus is bound only by the C1 floors. `(p2)`

## 5. Documentation, skill and compatibility surfaces

- **Home pages.** The composition reference gains the resolution entry,
  coverage set and record fields. The CLI reference points to it. If LI0's
  measurement picks the serializer home, the `gnd-orm-core` representation
  reference states the omission rule. A wire change to the `gnd-export`
  witness contract would be a defect. `(p2)`
- **Worked example.** A new literature section beside the bookrec and expense
  examples carries LI1, LI4 and LI5, including the harness and the admission
  step. Business-facing pages show skill prompts and visual results, not
  Python.
- **Skills.** `gnd-extract` and `gnd-model-from-text` guidance gains pointers
  to the assertion pattern. Packaged skill manifests and installer-managed
  links keep their ownership.
- **Compatibility.** Existing manifests, records and witnesses stay readable.
  Committed golden digests show that the 0.3.1 outputs over them are
  unchanged.

## 6. Risks and required controls

- **A fix moves digests.** LI0 could move committed digests or witness
  bytes. Control: the round-trip test and golden digests.
- **Silent coercion.** Decisions could coerce values. Control: keys use
  composition's exact value-and-type match, and evidence uses mention
  coordinates.
- **An oracle in disguise.** Diagnostics could act as an identity oracle.
  Control: output is `unresolved` only, and no command consumes a diagnostic
  as a decision.
- **Copyright.** Fixtures could reproduce copyrighted text. Control:
  paraphrased documents with work identifiers (D2).
- **Overfitting.** The lineage rules could be tuned to their own corpus.
  Control: C6 commits the held-out subset before LI5.

## 7. Deferred and out of scope

- Everything in #193 "Not proposed" is out of scope.
- Running the host's 15K-document graph and the host-scale 16/50/24/180 sets
  is host work. D1 decides whether any of it is imported.
- The date check goes to literature-interop LX4.
- Parts 5–8 and 10 go to the successor milestones (§1.1).
- Open #179, #181 and #182 keep their own scope.
- Publication, certification and release are outside this milestone.

## 8. Execution, approval and review protocol

Default `auto=false`. Each phase needs, in order: `(p2)`

1. the owner rulings its spec depends on:

   | Phase | Rulings |
   |---|---|
   | LI0 | D8 |
   | LI1 | D1, D2, D5 |
   | LI2 | D3 |
   | LI3 | D4 |
   | LI4 | D7 |
   | Partition | D6 |

2. its spec gate;
3. implementation;
4. the focused gate, plus the structure guard list and `uv run ruff check`;
5. an independent diff review and a refactoring review;
6. its phase record.

Plan review and close use the maintained panel (project hook). The
plan-review budget is two rounds, with the early stop rules of the
[convergence guidance](../../../../.codex/skills/process-phase/references/review-convergence.md).
If the bar is unmet after round 2, record that and stop. Work goes on topic
branches and PRs, and merge needs separate owner authorization.

## 9. Per-phase verification story

The LI0 reproduction, before any change, used a two-fact-type grandparent
fixture on 2026-11-14/15. Every input passed `gnd validate`, and `gnd check`
accepted every population:

| Model | `gnd witness` | `gnd why-not` |
|---|---|---|
| version 1, `model_id` present | exit 3. Meta-schema: `version: 1 is not one of [2, 3, 4, 5]` | exit 3 |
| version 2, `model_id` present | exit 0, and its replay exits 0 | exit 0 |
| version 1 or 2, no `model_id` | exit 3. Meta-schema: `$.model_id: None is not of type 'string'` | exit 3 |

Dropping `operations` and the null `model_id` from the dump makes both
version-1 models load back to an equal `Model` `(p2)`.

| Phase | Focused lane and affected consumers |
|---|---|
| LI0 | New regression tests, plus `test_witness_composition.py`, `test_public_why_not.py`, `test_public_replay_admission.py`, `test_public_optional_value_witness.py` and `test_public_v71_witness_corpus.py` |
| LI1 | Corpus and harness tests, plus `test_composition_example.py` and the fidelity/judgments consumers the harness reads |
| LI2 | New resolution tests, plus `test_composition.py`, `test_composition_example.py` and `test_witness_composition.py`. Time-bound test over values × sources × decisions |
| LI3 | Diagnostics tests and the N3 measurement, recorded before it runs |
| LI4 | Example-model, admission-step and judgment tests |
| LI5 | Lineage fixture tests, plus ring/acyclic, witness and why-not consumers |

Every phase also runs the structure guard list from the project hook. The
evidence, census, native and provider lanes and certification have separate
triggers.

## 10. Owner decisions and open questions

All rows are **proposed**. None is ruled.

| ID | Question | Proposal | Cost of the other reading |
|---|---|---|---|
| D1 | Home of the evaluation corpus | Ship the public reconstruction (C1 floors). The 16/50/24/180 host-scale sets stay host-owned, and the host runs them with the LI1 report | Importing them means public passages, licence checks, anonymizing the talk's repository, and a corpus too large for the focused lane |
| D2 | Source text in fixtures | Paraphrased documents with public work identifiers | Real quotations make anchors more realistic but bring licence and size limits |
| D3 | Depth of LI2 runtime integration | Runtime binds and verifies decisions and the coverage set only. Meaning stays host-side | A pure example adapter cannot make a changed decision stale in `check --composition` |
| D4 | Surface for name diagnostics | An example-level report first. Promote it to a `gnd discover` family only after the N3 measurement | A discover family now couples to #181 and to the discover wire |
| D5 | Surface of the assurance report and admission step | Example harness and example step, with documented shapes and no new command | A `gnd` command makes both public CLI contracts to maintain |
| D6 | Partition and parallelism | Three milestones as in §1.1. literature-interop starts after LI0 and may run alongside LI1–LI5 | One milestone would hold 14+ phases. Strict sequencing delays the part 6 examples |
| D7 | Rubric mapping of `stretched` | Reject, with the disposition kept in the review record | Abstain hides a known misreading. Approve admits it |
| D8 | LI0 as a phase or a maintenance PR | A phase, so its record feeds the close sweep | A maintenance PR is faster but sits outside the milestone's sweep |
| D9 | Plan review | The maintained standard panel, with two rounds at most. The successor plans are reviewed when they start | Reviewing the outlines now produces findings that go stale before they are ready |
