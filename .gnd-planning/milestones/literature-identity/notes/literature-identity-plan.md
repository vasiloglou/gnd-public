# Literature identity and assertions · plan r1

**Status: draft, 2026-11-14. Not reviewed and not approved.** This plan is
written from [issue #193](https://github.com/vasiloglou/gnd-public/issues/193)
at the owner's request. No plan review has run over these bytes yet. No owner
gate is recorded. No phase may start implementation before its spec gate.
`auto=false`.

## Goal and completion predicates

Make the identity of a scientific entity and the meaning of an asserted
relation explicit, reviewable and bound to composition. Then show, on small
public fixtures, that a lineage built from them keeps true chains and drops
false ones. This milestone covers parts 9, 1, 2, 3 and 4 of #193. The
[partition table](#11-partition-of-issue-193) assigns the other parts to two
successor milestones.

The milestone is complete when all of these hold:

- **LI0.** `gnd witness` and `gnd why-not` accept a valid version-1 model, and
  a model with no `model_id`. `gnd replay` replays the version-1 witness.
- **LI1.** A public regression corpus reproduces the whale, `$PINN`, Boltz-1
  and contrast cases from #193. A staged assurance report over it lists each
  stage's denominator separately. A run that drops every output fails the report.
- **LI2.** A composition can bind a resolution record of `same`, `different`
  and `unresolved` decisions. A renaming without a `same` decision is refused.
  A changed decision makes the composition record and its witnesses stale.
- **LI3.** A name-diagnostics report proposes homonym, synonym and family
  candidates as `unresolved` decisions and applies none of them. Its false
  positives are measured on a labelled sample against a declared budget.
- **LI4.** A contextual-assertion example model, with a review rubric mapped
  onto saved judgments, meets #193 part 3 criteria 1–6 on fixtures.
- **LI5.** On the LI1 corpus, lineage rules keep every chain the fixture
  labels supported and exclude every chain it labels false. They keep the
  Boltz-1 evaluation statement out of ancestry. Both query families carry
  assertion and decision identities through their explanations.
- The milestone close sweeps every #193 part 1–4 and part 9 criterion to a
  phase result, a carried row, or a recorded owner ruling.

## 0. Binding design rules

Every spec applies the six standing design rules of the
[project hook](../../../../.codex/skills/process-phase/references/project.md)
by name.

- **Totality.** Every new reader is total over arbitrary JSON, with the cap on
  the read. That covers the resolution record (LI2), the diagnostics input
  (LI3) and the report harness input (LI1).
- **Input-bounded work.** Bound work proportional to the input with a
  time-bound test. In LI2 the input is decisions × renamings. In LI3 it is
  occurrences × candidates.
- **Validation order.** Pin the refusal order at each boundary. In LI2 that is
  the manifest, then the resolution record digest, then decision coverage,
  then composition.
- **One walk per policy.** One walk enforces the LI2 decision policy over every
  identity-changing operation, not one copy per renaming kind.
- **One home per contract.** The composition reference stays the home of the
  composition contract, and LI2 extends it there. The judgment contract stays
  the home of saved opinions. LI4 cites it and does not restate it.
- **Measurement over argument.** Representation disputes are settled by
  measurement, for example LI0's global serializer change against a local
  wire projection.

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
| Local reproduction, 2026-11-14 (§9) | A model without `model_id` fails the same way at version 2. `why-not` shares the defect | LI0 W1–W2 |
| #193 part 1, "Proposal" and criteria 1–8 | Separate evaluation sets. Precision, recall and abstention reported separately. Staged report with honest denominators | LI1 C1–C4 (framework half), D1 |
| #193 part 2, "Proposal" and criteria 1–6 | Mention identity apart from surface text. `same`/`different`/`unresolved` decisions bound to composition. Stale on change | LI2 R1–R5 |
| #193 part 2, "Folded in: name diagnostics" | Candidate generation only. Measured false-positive budget. Cross-domain reuse is not flagged as a homonym | LI3 N1–N3 |
| #193 part 3, "Proposal" and criteria 1–6 | Contextual assertion model and review rubric on saved judgments. Raw extraction kept beside the admitted population | LI4 A1–A4 |
| #193 part 4, "Proposal" and criteria 1–7 | Distinct relations, two query families, assertion IDs carried through explanations, cycle diagnosis | LI5 L1–L4 |
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
| 1 · regression corpus and assurance report | P0 | **literature-identity** LI1. The host-scale baseline is D1 |
| 2 · sense-resolution decisions | P0 | **literature-identity** LI2, plus LI3 for name diagnostics |
| 3 · contextual assertions and review | P0 | **literature-identity** LI4 |
| 4 · context-qualified lineage | P0 | **literature-identity** LI5. The dates step goes to **literature-interop** LX4 |
| 5 · includes, reference populations, extraction, composition and witnesses together | P0 | [**literature-interop**](../../literature-interop/notes/literature-interop-plan.md) LX1–LX4 |
| 6 · physics and algorithm examples | P1 | [**literature-depth**](../../literature-depth/notes/literature-depth-plan.md) LD1, plus LD2 for quantities |
| 7 · multipass reading with coverage | P1 | **literature-depth** LD3 |
| 8 · semantic revisions | P1 | **literature-depth** LD4, plus LD5 for verdicts on derived claims |
| 10 · aggregate certificates | P2 | Deferred. See the [literature-depth plan §7](../../literature-depth/notes/literature-depth-plan.md#7-deferred-and-out-of-scope) |

The issue's order is corpus, then identity and assertions, then lineage, then
depth once the features work together. The partition follows it. Part 5 has
no dependency on parts 2–4, so literature-interop could run alongside this
milestone (D6).

## 2. Contract proposal and product behavior

**LI0.** The witness producer and the why-not path both serialize the loaded
model again before intake. That serialization keeps the loader defaults
`operations: []` and `model_id: null`. The meta-schema then rejects
`operations` at version 1, and it rejects a null `model_id` at any version.
Replace those two dump sites with one wire projection beside
`population_wire`. The projection's output must load back to the same model.
The spec measures the alternative, changing `gnd.documents.Model`
serialization globally, before choosing. (#193 calls the class
`ModelDocument`. In the source it is `gnd.documents.Model`.)

**LI1.** The fixture corpus has small paraphrased source documents with
public work identifiers, and gold annotations kept apart from the entry
point. It covers:

- the whale chain and its four senses;
- the `$PINN`/"PINNs" merge and the loop it makes;
- normalizing flow versus flows;
- Boltz-1 evaluated as a potential;
- a contrast passage read as "builds on";
- one valid cross-domain chain.

The staged assurance report is an example harness over existing commands. It
emits the stages of #193 part 1 criterion 5 separately, each with its sample
size, exclusions and unresolved count. It introduces no `gnd` command unless
D5 rules otherwise.

**LI2.** Composition gets an opt-in `resolution` entry in the manifest, with
`path` and `sha256`, and a `gnd-resolution/1` record. The record holds
mention identities (source, fact type, fact index, role, and anchor span where
one exists), candidate mappings, decisions, evidence references, the producer
or reviewer, and input digests. The rules:

- Each renaming must cite a `same` decision.
- A `different` decision refuses any renaming that would merge the two
  mentions.
- An `unresolved` mapping cannot enter the composed population.
- The composition record carries `resolution_sha256`. `gnd check
  --composition` and witness version 2 then make a changed decision stale.
- When one source uses a single identifier for two senses, the source is not
  rewritten. A reviewed replacement population with occurrence-specific
  identities is composed instead.

A manifest without `resolution` behaves exactly as in 0.3.1.

**LI3.** A report runs over the original occurrences, before any renaming. It
proposes three kinds of candidate:

- **Homonyms:** one value used in contexts that do not overlap, or case
  variants of one acronym.
- **Synonyms:** values within a normalization distance whose contexts overlap.
- **Families:** values used by many unrelated works with no introducing work.

It writes `unresolved` entries in the LI2 format and never applies them. The
surface is D4.

**LI4.** A worked example model:

- **The assertion:** an objectified assertion that links a work and its
  version, a specific predicate and its argument roles, and resolved
  participants or unresolved mentions.
- **Its context:** condition, regime and experiment facts, the passage, its
  polarity and its qualification.
- **Its records:** extraction and review are kept as separate records.

A review rubric maps each disposition onto saved-judgment verdicts:

| Disposition | Saved-judgment verdict |
|---|---|
| supported | approve |
| contradicted | reject |
| stretched | reject. Owner ruling D7 |
| insufficient evidence | abstain |

The admitted population is a separately identified population built from the
raw extraction under a policy. A runtime gap found in this phase is recorded
as a finding and is not closed silently.

**LI5.** The relations are fine-tuning, implementation, extension, component
use, training on another method's outputs, evaluated-as, compared-against,
inspired-by and taxonomic membership. Each has its own explicit composition
policy. Two query families:

- **Documented methodological lineage.**
- **Justified transfer of a result.** It needs assumption and interface
  evidence.

Every accepted path names the assertion and resolution decisions it rests on.
Cycles are diagnosed with every edge reported, and no edge is deleted to make
a check pass.

## 3. Dependencies and artifact homes

LI0 depends on nothing. LI1 comes first among the semantic phases because it
supplies their fixtures. LI2 needs LI1. LI3 writes LI2 records. LI4 needs
LI2's mention identities, and unresolved mentions stay representable. LI5
needs LI1, LI2 and LI4, and it needs LI0 only if its fixture models are
version 1. Nothing in this milestone needs literature-interop.

| Capability | Observed component and decision |
|---|---|
| Witness wire projection | Adapt `witness/io.py`, which holds `population_wire` and `intake`. Fix the dump sites `witness/producer.py:197` and `witness/service.py:252` (why-not). Replay and the Soufflé/Lean exports parse raw bytes and are unaffected (§9). |
| Resolution binding | Adapt `model.composition` (`src/gnd/composition.py`), its manifest schema `composition-manifest.schema.json` and record schema `composition.schema.json`. Adapt `checker._composed` for re-verification and witness version 2 for the record digest. |
| Mention spans | Reuse the anchor sidecars bound per source by composition. |
| Name diagnostics | Reuse the `why_not._near_key`/`_near_miss_pair` spelling neighbourhoods if their contract fits. Otherwise a new module whose home is set by D4. Coordinate with #181 if the home is `gnd discover`. |
| Assertion review | Reuse `semantics.saved_judgments` and `gnd judgments` unchanged. |
| Lineage queries | Reuse structured rules, recursion, ring/acyclic reporting (#94, #119) and witness version 2. |
| Report harness | New example harness, with its home set by D5. It reads `gnd check`, `gnd fidelity` and `gnd measure --labels` outputs over their supported routes. |

The component index search covered composition renaming, saved judgments,
include flattening, reference populations and near-miss spelling. The index
review lists 69 descriptions older than their code, so the plan relies on
inspected source. A Review pass over the index can be selected separately.

## 4. Phases, deliverables and named criteria

| Order | Phase | Acceptance criteria |
|---|---|---|
| 0 | **LI0 · W1–W3** · #193 part 9 | W1: a version-1 fixture witnesses (exit 0) and replays (exit 0). So does a model without `model_id`. W2: `why-not` on the same inputs exits 0 with its derivation result. W3: a regression test pins the wire projection's round trip over the committed fixture models. Witness bytes for already-supported inputs are unchanged. |
| 1 | **LI1 · C1–C4** · part 1 | C1: the corpus and its split-out answer key exist, and every gold label cites a passage. C2: dropping all outputs, dropping one supported fact, a false merge, a reversed relation, a missing condition and stale evidence each fail their own stage. C3: an empty rule premise never counts as a successful test. Mutually exclusive flags are never combined. C4: the report states sample sizes, exclusions and disagreements, and that its labels are not independent expert ground truth. |
| 2 | **LI2 · R1–R5** · part 2 | R1: the whale's four senses stay distinct, its three legitimate direct edges survive, and the false combined chain disappears. R2: two senses with one spelling in one document are both representable without rewriting the text. R3: an evidenced alias joins across documents. A same-domain homonym with no supporting decision does not. R4: a missing or conflicting decision refuses (exit 3) and names the mention, not its value. R5: a changed decision makes `check --composition` and replay stale (exit 3). The prior snapshot replays to its original result. A manifest without `resolution` gives byte-identical 0.3.1 output. |
| 3 | **LI3 · N1–N3** · part 2 diagnostics | N1: VAMPnet/VampNet, WhAM/WHAM and `$PINN`/PINNs appear as candidates. N2: flow matching across fields is not reported as a homonym, or only below a stated score. N3: the false-positive rate on a labelled sample is within a budget declared in the spec before the measurement runs. Nothing is ever applied. |
| 4 | **LI4 · A1–A4** · part 3 | A1: a supported conditional claim keeps its conditions. A2: co-occurring names with the wrong predicate fail admission. A3: negation, baseline comparison, speculation and citation are distinguishable from the paper's own finding. Conflicting claims under different experiments both remain. A4: a missing review or an abstention never becomes approval. A changed subject or evidence makes the review stale. Batches stay within the judgment-contract limits. |
| 5 | **LI5 · L1–L4** · part 4 | L1: on the LI1 corpus, every chain labelled supported is kept and every chain labelled false is excluded, with the counts reported. L2: the Boltz-1 statement is kept but is not ancestry. A valid cross-domain chain is kept, and an invalid same-domain chain is rejected. L3: a path with an unreviewed or unresolved edge is not accepted. A transfer missing its required conditions fails. L4: cyclic and acyclic fixtures exist, a warning is not read as a failure, and the original whale witness stays a documented demonstration of the old model's weakness, not a checker defect. |

LI1–LI5 apply the #193 part 1, 2 and 4 numeric criteria (16 chains, 50
reuse cases, 7 supported and 8 false chains, a 24-paper pilot, a 180-assertion
audit) to the public reconstruction. The host-scale numbers belong to the host
(D1).

## 5. Documentation, skill and compatibility surfaces

- **Home pages.** The composition reference gains the resolution entry and
  the record field. The CLI reference points to it. The witness contract in
  `gnd-export` gains nothing unless LI0 changes a wire field, and it should not.
- **Worked example.** A new literature section beside the bookrec and expense
  examples carries LI1, LI4 and LI5. Business-facing pages show skill prompts
  and visual results, not Python.
- **Skills.** `gnd-extract` and `gnd-model-from-text` guidance gains pointers
  to the assertion pattern. Packaged skill manifests and installer-managed
  links keep their ownership.
- **Compatibility.** Existing manifests, records and witnesses stay readable,
  and the 0.3.1 outputs over them stay byte-identical.

## 6. Risks and required controls

- **A fix moves digests.** LI0 could move committed digests or witness
  bytes. Control: the round-trip test and unchanged bytes on supported inputs.
- **Silent coercion.** A resolution record could coerce values. Control: an
  identity is mention coordinates, never a normalized spelling, and the same
  JSON-type rule as renamings applies.
- **An oracle in disguise.** Diagnostics could act as an identity oracle.
  Control: output is `unresolved` only, and no command consumes a diagnostic
  as a decision.
- **Copyright.** Fixtures could reproduce copyrighted text. Control:
  paraphrased documents with work identifiers, and short quotations only
  where the source licence allows them (D2).
- **Overfitting.** The lineage rules could be tuned to their own corpus.
  Control: the answer key is split from the entry point, and some cases are
  held out from LI5 development (#193 part 1, "Keep regression fixtures
  separate").

## 7. Deferred and out of scope

- Everything in #193 "Not proposed" is out of scope.
- Running the host's 15K-document graph, its 16/50 regression set at host
  scale, and the 24-paper pilot and 180-assertion audit on real papers are
  host work. D1 decides whether any of it is imported.
- The date check of part 4 goes to literature-interop LX4, because extraction
  refuses temporal models.
- Parts 5–8 and 10 go to the successor milestones (§1.1).
- Open #179, #181 and #182 keep their own scope. LI3 coordinates with #181
  only if D4 puts it in `gnd discover`.
- Publication, certification and release are outside this milestone.

## 8. Execution, approval and review protocol

Default `auto=false`. Each phase needs a spec gate, implementation, the
focused gate plus the structure guard list, `uv run ruff check`, an
independent diff review and a refactoring review, then a phase record. Plan
review and close use the maintained panel (project hook). The plan-review
budget is two rounds, with the early stop rules of the
[convergence guidance](../../../../.codex/skills/process-phase/references/review-convergence.md).
If the bar is unmet after round 2, record that and stop. Work goes on topic
branches and PRs, and merge needs separate owner authorization.

## 9. Per-phase verification story

The LI0 reproduction on 2026-11-14, before any change, using a two-fact-type
grandparent fixture:

| Model | `gnd witness` | `gnd why-not` |
|---|---|---|
| version 1, `model_id` present | exit 3 `input-invalid`. Meta-schema: `version: 1 is not one of [2, 3, 4, 5]` | exit 3 `input-invalid` |
| version 2, `model_id` present | exit 0, and its replay exits 0 | exit 0 |
| either version, no `model_id` | exit 3. Meta-schema: `$.model_id: None is not of type 'string'` | not run |

`gnd validate` and `gnd check` accept all of these models.

| Phase | Focused lane and affected consumers |
|---|---|
| LI0 | New regression tests, plus `test_witness_composition.py`, `test_public_why_not.py`, `test_public_replay_admission.py`, `test_public_optional_value_witness.py` and `test_public_v71_witness_corpus.py` |
| LI1 | Corpus and harness tests, plus `test_composition_example.py` and the fidelity/measure consumers the harness reads |
| LI2 | New resolution tests, plus `test_composition.py`, `test_composition_example.py` and `test_witness_composition.py`. Time-bound test over decisions × renamings |
| LI3 | Diagnostics tests and the labelled-sample measurement, recorded before it runs. Discover or why-not consumers depend on D4 |
| LI4 | Example-model and judgment tests, plus the existing judgments consumers |
| LI5 | Lineage fixture tests, plus ring/acyclic, witness and why-not consumers |

Every phase also runs the structure guard list from the project hook. The
evidence, census, native and provider lanes and certification have separate
triggers and are not run to fill this plan.

## 10. Owner decisions and open questions

All rows are **proposed**. None is ruled.

| ID | Question | Proposal | Cost of the other reading |
|---|---|---|---|
| D1 | Home of the evaluation corpus | Ship small public reconstructions. The 16/50/24/180 host-scale sets stay host-owned, and the host runs them with the LI1 report | Importing them means public passages, licence checks, anonymizing the talk's repository, and a corpus too large for the focused lane |
| D2 | Source text in fixtures | Paraphrased documents with public work identifiers | Real quotations make anchors more realistic but bring licence and size limits |
| D3 | Depth of LI2 runtime integration | Runtime binds and verifies decisions only. Meaning stays host-side, as #193 part 2 asks | A pure example adapter cannot make a changed decision stale in `check --composition` |
| D4 | Surface for name diagnostics | An example-level report first. Promote it to a `gnd discover` family only after the LI3 measurement | A discover family now couples to #181 and to the discover wire |
| D5 | Assurance report surface | An example harness plus a documented report shape, with no new command | A `gnd` command makes the report contract a public CLI surface to maintain |
| D6 | Partition and parallelism | Three milestones as in §1.1. literature-interop starts after LI0 and may run alongside LI1–LI5 | One milestone would hold 14+ phases. Strict sequencing delays the part 6 examples |
| D7 | Rubric mapping of `stretched` | Reject, with the disposition kept in the review record | Abstain hides a known misreading. Approve admits it |
| D8 | LI0 as a phase or a maintenance PR | A phase, so its record feeds the close sweep | A maintenance PR is faster but sits outside the milestone's sweep |
| D9 | Plan review | The maintained standard panel, with two rounds at most for this plan. The successor plans are reviewed when they start | Reviewing the outlines now produces findings that go stale before they are ready |
