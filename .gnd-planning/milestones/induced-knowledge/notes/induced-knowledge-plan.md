# Induced knowledge

r1, 2026-10-23. **Draft; awaiting plan review and owner approval.**
Milestone: `induced-knowledge`. `auto=false`.
Inspection baseline: `a22ccde` (main, after PR #33), plus the request-2 fix in
[PR #35](https://github.com/vasiloglou/gnd-public/pull/35) (see §1). No review has run; no approval exists.

## Goal, status and completion predicates

Let a host that holds *real* labelled populations turn them into reviewed model
knowledge inside GND: describe what an object type is, score a candidate rule
against labelled examples, discover candidate constraints from a population,
round-trip rules through an inductive logic programming (ILP) learner, and admit
each result through `gnd evolve` with provenance that says it was induced.
Admission stays a reviewed act. Nothing induced becomes `confirmed` automatically.

Planning only. The first phase's [draft spec](phase-IK1-spec.md) awaits plan
approval and its own owner gate. No implementation, measurement or approval is
claimed here.

Completion requires:

1. IK1: an optional object-type `description` validates, renders in model
   verbalization and generated docstrings, is carried by `diff` and `evolve`,
   and is reachable by extraction guidance. Models without it are byte-unchanged
   in every rendered output.
2. IK2: a new provenance source for induced elements, with a required evidence
   block, validates; `gnd evolve preview` admits it only as `proposed`/`deontic`;
   `gnd coverage` reports it. Existing sources keep their behaviour.
3. IK3: `gnd measure` scores a host-labelled manifest of real populations and
   reports the same cells with numerators and denominators. Synth-sidecar
   measurement output is byte-unchanged.
4. IK4: a discovery command proposes uniqueness, mandatory, value, frequency,
   subset, equality and exclusion candidates with exact support and
   counterexamples, as an evolve proposal that IK2's gate admits. Every candidate
   it emits is satisfied by the input population under `gnd check` (exit 0 for
   that constraint), and discovery stays within the existing 10 MB input caps
   with a time-bound test.
5. IK5: export emits background knowledge, examples and mode declarations for one
   owner-selected ILP target; import reads a learned clause set into a structured
   `derivation_rule` or `guarded` constraint and re-evaluates it. Import refuses
   (non-zero exit) when GND's computed coverage differs from the learner-reported
   coverage.
6. IK6: one end-to-end public example walks label → measure → discover/learn →
   evolve preview on anonymized fixtures; docs and skill surfaces updated.
7. Every phase has approval, focused checks, independent diff review,
   refactoring review and a record. Close has four-reviewer evidence, a question
   sweep, a PR and separately recorded owner acceptance.

No delivery date is committed.

## 0. Binding design rules

| ID | Rule |
|---|---|
| IK-R1 | Induction proposes; review admits. No phase adds a path from observed or learned evidence to `status: confirmed` or `modality: alethic` without an explicit owner act through existing evolve review. |
| IK-R2 | Evidence is exact and reproducible. Support, confidence and counterexamples are computed by GND from named inputs whose digests are recorded; a learner's or host's own numbers are claims to check, never inputs to trust. |
| IK-R3 | Additive compatibility. Existing models, populations, sidecars, measurement reports and verbalization outputs without the new fields stay valid and byte-identical. Any version bump needs an owner decision (D1). |
| IK-R4 | One schema home. Edit `src/gnd/skills/gnd-orm-core/references/*.schema.json` and keep the vendored copy byte-identical (`tests/test_schema_sync.py`). Normative prose lives in the gnd-orm-core references; docs cite it. |
| IK-R5 | Free text is untrusted. Descriptions, labels and learned clause text pass through the existing neutralizers (`verbalize._neutralize`, `codegen.docstrings` delimiter rule) and never execute. |
| IK-R6 | Inputs are capped before reading and loaders are total over arbitrary JSON (standing rule 1). New work proportional to input ships a time-bound test (standing rule 2). Discovery works per fact type and never needs more than one population in memory beyond the existing caps. |
| IK-R7 | Layer homes follow `tools/gnd_layers.json`; new modules are assigned before use; the allowance count stays zero; ModelIndex is the shared query path; constraint-family hooks register in `constraint_families.FAMILIES`. |
| IK-R8 | No external solver is a runtime dependency. ILP tools are optional, invoked only by explicit command with bounded process execution through `gnd.process`, and absent tools produce a named refusal, not a failure of unrelated commands. |
| IK-R9 | All six process-phase standing rules bind every spec by name. |
| IK-R10 | Privacy. Fixtures are synthetic or anonymized; downstream applications are not named in public text, issues, PRs or fixtures. |

## 1. Scope, sources and authority

Framework runtime work. A `gnd coverage` census does not establish whether
these capabilities exist, so it does not settle scope.

| Source | Authority / use |
|---|---|
| [Issue #34](https://github.com/vasiloglou/gnd-public/issues/34), requests 1–6 | Requested capabilities; reporter's pin `add0c2b` |
| Request-2 fix, [PR #35](https://github.com/vasiloglou/gnd-public/pull/35) | Request 2 discharged outside this milestone; IK-O2 records it, no phase owns it |
| `src/gnd/schema/orm-meta.schema.json` `object_type` (`additionalProperties: false`), `source_kind`, `provenance_policy` | Request 1 and 6 schema homes |
| `src/gnd/evolve/service.py` `_enforce_d12`, `_surface_index` | Admission gate refusing any new constraint not `llm-inferred`/proposed/deontic or `user-supplied`/confirmed; evolve surfaces |
| `src/gnd/measure/` (`service.py`, `score.py`, `truth.py`, `report.py`), `src/gnd/synth/provenance.py` `Sidecar`, `src/gnd/measurement.schema.json` | Measure's synth-bound inputs and its six cells |
| `src/gnd/population.py` `MAX_POPULATION_BYTES` | 10 MB cap enforced before parsing |
| `src/gnd/export/` (lean, souffle, pyrel), `src/gnd/rai_import.py` | Existing export targets; only import path is create-once dialect import |
| `src/gnd/model_verbalization.py`, `codegen/docstrings.py`, `extract/projection.py`, `diff.py`, `coverage.py` | Rendering and carrying consumers |
| gnd-orm-core references: `provenance-and-modality.md`, `constraint-inference.md`, `verbalization-patterns.md`, `representation-format.md` | Normative prose homes |
| `AGENTS.md`, `CONTRIBUTING.md`, process-phase references | Binding development rules |

### Harvested obligation ownership

| ID | Obligation (source) | Evidence class | Phase / gate |
|---|---|---|---|
| IK-O1 | Object-type description, rendered by verbalization, extract, codegen; carried by diff, evolve (req 1) | requested | IK1-C1..C4 |
| IK-O2 | Role-scoped value verbalization (req 2) | requested; fixed in PR #35 | none; close sweep confirms merge state |
| IK-O3 | Measure over host-labelled real populations, numerators/denominators (req 3) | requested | IK3-C1..C3 |
| IK-O4 | Discovery of seven families with support and counterexamples, as evolve proposal, `status: proposed`, observed source (req 4) | requested | IK4-C1..C4 |
| IK-O5 | 10 MB cap; stream or per fact type (req 4 note) | requested constraint | IK-R6, IK4-C3 |
| IK-O6 | ILP export of background, examples, modes (req 5) | requested | IK5-C1 |
| IK-O7 | ILP import with faithful re-evaluation (req 5) | requested | IK5-C2..C3 |
| IK-O8 | Induced provenance: source kind, inducer identity, example ids, support, confidence, counterexamples, evidence digests; accepted by evolve preview, shown by coverage (req 6) | requested | IK2-C1..C3 |
| IK-O9 | A `gold` source kind "alongside GR-12" (req 6) | **not found** in this repository: no GR-12, no `gold` source | D3 |
| IK-O10 | D-12 gate refuses every new source other than llm-inferred/user-supplied, including `sample` | inspected conflict with IK-O4, IK-O8 | D2; IK2-C2 |
| IK-O11 | Measure keys labels by positional refs (`constraints[i]`), fragile for host labels | inspected risk | IK3-C1; D5 |
| IK-O12 | Verbalization/codegen output digests in committed fixtures may change | inspected risk | IK1-C3 (byte-unchanged when absent) |
| IK-O13 | Four-reviewer plan/close bar and explicit instrument | inherited protocol | D7; plan and close gates |
| IK-O14 | Anonymity of downstream reporter | owner rule | IK-R10; every diff review |

## 2. Contract proposal and product behavior

**Request 1 (IK1).** `object_types[].description`: optional non-empty string,
bounded length (proposed 2,000 characters). No version bump (precedent:
top-level `model_id` is optional and ungated). Model verbalization appends it to
the object type's sentence; codegen adds it to the docstring of tools whose roles
use the type; extraction guidance shows it beside the type. `diff` reports
description changes; evolve indexes `object_types[id].description` as a surface.

**Request 6 (IK2).** New source kind, proposed spelling `induced` (D3 decides
whether `gold` is added too). Required `provenance.induction` block:
`{inducer: {name, version}, method, examples: [id…], support: {numerator, denominator},
confidence, counterexamples: [id…] (bounded), evidence: [{path, sha256}…]}`.
D-03 default modality: deontic. `_enforce_d12` admits `induced` only as
`proposed`/`deontic` (D2). Coverage gains a provenance view listing induced
elements with support. The schema stays the only home of the shape.

**Request 3 (IK3).** `gnd measure MODEL --labels MANIFEST`: a capped manifest
lists populations by path and SHA-256, each with either per-constraint expected
verdicts or a population class mapped to expectations. Constraints are named by
constraint `id` (D5), with positional refs accepted for compatibility. The
labels feed the existing `classify`/`score_constraint` path; the report uses the
existing cells and adds explicit numerator/denominator fields only under a new
report version. Synth-sidecar input keeps its current report bytes.

**Request 4 (IK4).** `gnd discover MODEL POPULATION [--families …] [--max-domain N]`
reads one capped population, evaluates each family per fact type, and writes an
evolve proposal whose new constraints are `source: induced` (or `sample`, per
D2/D3), `status: proposed`, `modality: deontic`, each with exact support and
bounded counterexamples. A candidate is emitted only if it holds on the input;
near-misses are reported separately with counterexamples, never as constraints.
Implied candidates (already declared, or entailed by a declared one) are suppressed
and counted.

**Request 5 (IK5).** Export: `gnd export ilp --target <popper|ilasp> MODEL --labels MANIFEST`
writes background facts, positive/negative examples and mode declarations derived
from fact-type roles. Import: `gnd import ilp-rules MODEL CLAUSES --labels MANIFEST
--reported-coverage FILE` translates the clause subset GND can represent into a
structured `derivation_rule` or `guarded` constraint, re-evaluates it on the
same examples, and refuses on any coverage mismatch or unrepresentable clause.
Output is an evolve proposal under IK2's provenance. D4 selects the first target.

## 3. Dependencies and artifact homes

DAG: **IK1** (independent) · **IK2 → IK3 → IK4 → IK5 → IK6 → close**. IK1 may
run first or in parallel with IK2; IK3's measurement provides the scoring that
IK4 support reports and IK5 coverage checks reuse; IK5 needs IK3 labels. Six
implementation phases; close is a separate gate.

| Artifact | Proposed home |
|---|---|
| Plan, specs, records, evidence | this milestone directory |
| Schema changes | gnd-orm-core `orm-meta.schema.json` (canonical) + vendored twin; new manifest schema beside `measurement.schema.json` |
| Description rendering | `model_verbalization.py`, `codegen/docstrings.py`, `extract/projection.py`, `diff.py`, `evolve/service.py` |
| Induced provenance gate | `evolve/service.py` `_enforce_d12`; `coverage.py` |
| Labelled measurement | `src/gnd/measure/` new label-source module beside `truth.py` |
| Discovery | new `src/gnd/discover/` package, layer-assigned; uses ModelIndex and checker family evaluation |
| ILP bridge | `src/gnd/export/ilp*.py`, new import module beside `rai_import.py`; bounded process via `gnd.process` |
| Fixtures | `tests/fixtures/induced_knowledge/` (synthetic, anonymized) |
| Docs | gnd-orm-core references; `docs/` guide for the induction loop; release notes |

## 4. Phases, criteria and residuals

### IK1 — Object-type descriptions

First draft spec: [phase-IK1-spec.md](phase-IK1-spec.md).

- **IK1-C1:** schema accepts an optional bounded `description`; both copies stay identical; over-long, empty and non-string values fail `gnd validate` (exit 3 per current validation codes).
- **IK1-C2:** model verbalization and codegen docstrings render the neutralized description; extraction projection exposes it.
- **IK1-C3:** models without descriptions produce byte-identical verbalization, codegen and conformance digests.
- **IK1-C4:** `diff` reports description add/change/remove; evolve indexes and previews a description modification.

### IK2 — Induced provenance and admission

- **IK2-C1:** new source kind with required induction block; total validation with hostile-input cases; D-03 table updated in one home.
- **IK2-C2:** evolve preview admits induced constraints only as proposed/deontic, refuses other combinations with a named reason; existing D-12 outcomes unchanged (pinned).
- **IK2-C3:** coverage lists induced elements with inducer, support and evidence digests; reports without induced elements unchanged.

### IK3 — Measure over host-labelled populations

- **IK3-C1:** a capped, digest-bound label manifest loader, total over arbitrary JSON; id-keyed and positional refs; unknown refs refused (no silent default).
- **IK3-C2:** scoring reuses the existing truth table; numerators and denominators reported; a control shows a deontic rule firing on wrong-labelled plans and not on right ones.
- **IK3-C3:** synth-sidecar measurement reports byte-identical; time-bound test over manifest size.

### IK4 — Constraint discovery

- **IK4-C1:** each family's discovery has positive and counterexample cases; every emitted candidate passes `gnd check` on its input.
- **IK4-C2:** output is a valid evolve proposal that IK2's gate admits and `evolve preview` renders.
- **IK4-C3:** per-fact-type evaluation within existing caps; time-bound test at the cap; subset/equality/exclusion pair enumeration bounded (D6).
- **IK4-C4:** suppression of already-declared and entailed candidates is counted and reported.

### IK5 — ILP bridge

- **IK5-C1:** export for the D4 target is deterministic and digest-bound; modes derived from fact-type roles; examples from IK3 labels.
- **IK5-C2:** import translates the representable clause subset into `derivation_rule`/`guarded`; unrepresentable clauses refused by name.
- **IK5-C3:** GND re-evaluates the imported rule on the same examples; any difference from the learner-reported coverage refuses. A learner run, when the optional tool is installed, is evidence only, never a required lane.

### IK6 — End-to-end example, docs, integration

- **IK6-C1:** public anonymized walk: labels → measure → discover and learn → evolve preview.
- **IK6-C2:** docs, gnd-orm-core references, affected packaged skills (gnd-extract, gnd-model-evolve, gnd-codegen) and release notes; skill-surface census.
- **IK6-C3:** API/CLI pins, RF layer and source-scan controls, installed-candidate check for new entry points.

### Carried limitations

| Item | Disposition |
|---|---|
| Request 2 | discharged by PR #35; close records its merge state |
| GR-12 / `gold` | not present in this repository; D3 |
| Model-level thesaurus (issue "Not requested") | out of scope |
| Use of derived fact types inside host plans | host compiler's responsibility (issue "Not requested") |

## 5. Documentation, skill and compatibility surfaces

IK1 changes the model schema (additive) and the gnd-orm-core representation
reference. IK2 changes provenance-and-modality.md and the D-03 table. IK3 adds a
manifest schema and a report version. IK4/IK5 add CLI commands and must update
`api.__all__`/signature pins if they add public Python names. Packaged skills
that teach provenance or evolve (gnd-model-evolve, gnd-orm-core, gnd-extract,
gnd-codegen) are inspected per phase; edits only where behaviour changed.

## 6. Risks and required controls

| Risk | Control / owner |
|---|---|
| Induced items slip into confirmed knowledge | IK-R1; IK2-C2 refusal pins |
| Description text injects into prompts or code | IK-R5; neutralization tests in IK1 |
| Discovery explodes on pairwise families | IK-R6; D6 bounds; IK4-C3 time-bound test |
| Overfitting: candidates hold by accident on small samples | support/denominator always reported; no admission threshold implied; review decides |
| ILP translation changes meaning | IK5-C3 coverage-equality refusal |
| Measurement output churn breaks consumers | IK3-C3 byte-identity; new report version only for new input |
| Positional refs mislabel after model edits | D5 id-keyed refs |

## 7. Out of scope

Running ILP learners in CI or as a required lane; bundling solvers; automatic
admission or confirmation; a model-level thesaurus or NL lexicon; host plan
compilers; changes to verdict/band semantics of existing families; live database
profiling (discovery reads populations only); publication or certification.

## 8. Execution, approval and review protocol

`auto=false`. This start-milestone request authorizes planning artifacts only.
Each phase follows process-phase: harvest → spec → owner gate → approved-spec
commit → implementation and focused verification → independent diff review →
refactoring review → record. Plan and close review instrument: D7. Review
convergence follows `.codex/skills/process-phase/references/review-convergence.md`.
Topic branch and PR per AGENTS.md; merge, release and certification are separate
owner acts.

## 9. Verification story and affected consumers

| Phase | Falsifiable result | Consumers |
|---|---|---|
| IK1 | description validates, renders, diffs; absent ⇒ byte-identical outputs | `test_schema_sync.py`, `test_model_verbalization.py`, codegen/conformance tests, diff and evolve tests |
| IK2 | induced admitted only proposed/deontic; old D-12 outcomes pinned | evolve tests, coverage tests, schema tests |
| IK3 | labelled cells exact; synth reports byte-identical | measure tests, measurement schema tests |
| IK4 | every candidate holds; proposal admitted; time bound at cap | new discover tests; evolve preview |
| IK5 | coverage mismatch refuses; round-trip on fixtures | new ILP tests; export tests |
| IK6 | end-to-end example exits 0; docs links valid | docs/link tests, API pins, RF layering |

Exact commands are unresolved until each spec inventories changed definitions.

### Implementability sweep (author inspection, not review)

| Dependency / conflict | Proposed resolution |
|---|---|
| `object_type` forbids extra properties | additive optional property, no version bump (D1) |
| D-12 refuses `sample` and any new source | IK2 extends the gate for `induced` only, proposed/deontic (D2) |
| Measure bound to synth sidecars and pool digests | parallel label source feeding the same scorer; sidecar path untouched |
| Measure refs positional | add id-keyed refs (D5) |
| No profiling code exists | new discover package; reuse checker family evaluation to verify candidates |
| No rule import path exists | new importer emitting structured clauses already supported by the checker |
| ILP tool availability | optional, explicit, bounded; fixtures carry recorded learner output so tests need no solver |

## 10. Owner decisions and open questions

All rows are **proposed/open**.

| ID | Decision / proposed answer | Cost / blocking point |
|---|---|---|
| D1 | Additive optional fields without a model version bump | A bump would force migration of every model; rule before IK1 |
| D2 | Extend D-12 to admit `induced` as proposed/deontic only; leave `sample` refused | Admitting `sample` too widens the gate; rule before IK2 |
| D3 | Spell the source `induced`; do not add `gold` (no GR-12 here) unless the reporter supplies its definition | Adding `gold` blind invents semantics; rule before IK2 |
| D4 | First ILP target: Popper (Prolog) or ILASP (ASP) — proposed Popper for its plain Prolog modes and Datalog fit; second target is a follow-up | Two targets double IK5; rule before IK5 |
| D5 | Label manifest keys constraints by `id`, positional refs as fallback | Id-less constraints stay positional; rule before IK3 |
| D6 | Discovery bounds: value domains ≤ N=20 distinct values; set-comparison pairs only between roles of the same object type, capped count | Fewer candidates vs runaway cost; rule before IK4 |
| D7 | Review instrument for plan and close (proposed: four local reviewer agents, as in the prior milestone) | Required before plan review starts |

Next action: owner review of this plan and D1–D7, then plan review with the
selected instrument; then explicitly select `process-phase IK1 induced-knowledge`.
