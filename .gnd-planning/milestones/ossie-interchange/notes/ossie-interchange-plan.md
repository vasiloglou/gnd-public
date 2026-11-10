# Ossie interchange

**Status: r3, approved at the plan gate on 2026-11-10 `(a1)`
([record](../001-plan-gate.md)). The owner ruled OD0–OD8 on 2026-11-10 (OD3 follows
from OD1); the rulings are in §10, and changes made for them are tagged `(o)`.
r2 (sha256 `fb6fc6fe07faa4c9d4237424c806eea87b836042e40271320441cc989d822d68`)
was reviewed by the maintained light panel at effort high on 2026-11-10: 5 of 6
seats succeeded (Qwen timed out), all asked for revision, and finalization
exited 0 ([report](../evidence/plan-review-r2/PANEL-REVIEW.md)). The owner
directed "Apply fixes as r3". r3 applies all 19 prioritized fixes, tagged
`(p2 Fn)` with the fix's rank. **r3 itself is not reviewed.** The owner approved r3 knowing
that ("Approve r3", `(a1)`). `auto=false`. The plan approves no phase spec: OS0 needs its own owner
gate before any work, and no code is written before an OS1 spec is approved.

Phase prefix `OS`. The owner asked on 2026-11-10 whether GND is compliant with
Apache Ossie (incubating; formerly Open Semantic Interchange, OSI), what
compliance would take, and to plan it. The owner added that PyRel is
Ossie-compatible; §1.3 records what that turned out to mean.
Inspection baseline: gnd-public main at `720053ff`; apache/ossie at
`ee89dbdc2844d8b7d293ed42c8613928bb99505f` and apache/ossie-converters at
`83ddc294c8840f5f497a2bdbec2348a128fc2254`, both read on 2026-11-10.

GND writes its ORM 2 model as an Ossie **ontology document** (Ossie layer 4,
spec `ontology/ontology.md`, version `0.3.0.dev0`). That document passes
Ossie's own validator and parser at a pinned commit. GND also reads such
documents back. Every GND construct that the Ossie ontology cannot express is
exported losslessly in a GND vendor extension, or refused with a named
reason. Nothing is dropped silently. Ossie's own PyRel converter is used as an
independent consumer, to show that what GND writes is what a third party
reads.

## Completion predicates

The milestone is complete when, on main after merge:

1. `gnd export ossie MODEL --out FILE` writes one Ossie ontology document for
   every packaged example model and every `gnd-model-from-text` example model
   (the "export census", fixed in OS0). Each document validates against the
   vendored `ontology/ontology.json` in-process (OS1-C1). It also passes
   upstream `validation/validate.py --schema ontology/ontology.json` and
   `OssieParser` at the pinned commits, in the opt-in `ossie_oracle` lane
   (OS1-C2).
2. Export is deterministic. The same model bytes give the same document bytes
   and the same loss-report bytes. The model's identity digest is carried in
   the `gnd` extension when E1 admits `custom_extensions`. On the sidecar
   route (OD2), it is carried in the sidecar, which is itself bound to the
   document's sha256 (OS1-C3; p2 F9).
3. Every model element has exactly one disposition in a published,
   machine-readable loss report: `native` (a core Ossie construct), `requires`
   (an Ossie formula), `extension` (the `gnd` vendor extension) or `refused`
   (a closed reason code). **The unit of disposition is a JSON pointer into
   the source model document**, down to scalar fields (p2 F3). An object type
   whose `kind` and `subtype_of` are `native` and whose `storage` is
   `extension` therefore has three pointers with one disposition each, not one
   element with two. A census test shows that every pointer of every census
   model has exactly one disposition, none missing and none doubled (OS1-C4,
   OS2-C4).
4. Constraints and derivations that the Ossie formula grammar can state are
   exported as `requires` and `derived_by` formulas that `OssieParser` accepts
   (OS2-C1). For each exported constraint kind, a committed case corpus holds
   a violating and a satisfying population, and the **expected verdict under
   the formula's meaning according to `ontology.md`**. The verdicts are hand
   derived and reviewed, and committed before the formula renderer exists.
   GND's checker must reach that verdict on every case (OS2-C2). No evaluator
   of Ossie formulas exists at the pins, so this is the second engine. Its
   limit is stated in the OS2 spec: it checks that GND's rendering agrees with
   a human reading of the Ossie semantics, not with an independent Ossie
   implementation (p2 F2).
5. `gnd import ossie FILE --out MODEL` is total over arbitrary input. It
   refuses with exit 3 and a value-free `rule_id`, in one published order
   (OS3-C1, OS3-C2). For a GND-exported document whose loss report has no
   `refused` rows, import restores a model that `gnd diff` reports as equal to
   the source. For one with `refused` rows (populations always are, §2.1),
   import restores the source with exactly the refused pointers removed. The
   OS3 spec lists those models and pointers (round trip, OS3-C3; p2 F11). A foreign
   document, such as Ossie's `examples/flights.ontology.yaml`, imports with
   `imported` provenance, or is refused element by element in the loss report
   (OS3-C4).
6. Ossie's RelationalAI converter (`ossie_relationalai`, pinned) converts
   every exported document of the census offline, with `declared_table` or
   with no mappings, in the opt-in lane. The concepts, properties, supertypes
   and identifiers in its PyRel output match the export's own declaration
   list (OS4-C1). Where the converter skips a construct, the skip is recorded
   as a consumer limitation, not as GND's defect, in a separate OS4 lane
   artifact, `consumer-limitations.json`. It is keyed by converter commit and
   `relationalai` version, so the runtime loss report of `gnd export ossie`
   never depends on the converter (OS4-C2; p2 F8).
7. An include-bearing model (model-composition MC1) is either exported as its
   composition or refused with `include:unsupported-route`. A test pins which
   (OS1-C5).
8. A docs page states exactly what is claimed ("GND exports and imports Ossie
   0.3.0.dev0 ontology documents, validated at commit …") and what is not
   (layers 1–3, semantic models, mappings, the query interfaces). It presents
   PyRel as optional and links `what-is-pyrel.md`. It names the deliberate
   divergences, such as `Duration` (o, OD5). The `gnd-export` skill cites the
   one normative home (OS5).
9. OS6 has reached one of two recorded end states (p2 F5). Either the
   contribution that makes `ossie_relationalai` emit `require` for Ossie
   `requires` formulas has been opened upstream, with the owner's approval of
   the fork push and of its text, and its URL and state are recorded. Or the
   owner declined to publish it, and that decision is recorded with the
   prepared local branch. An upstream merge is never required (OS6; o,
   OD7).

## 0. Binding design rules

The six standing rules in `.codex/skills/process-phase/references/project.md`
bind every phase. They bind here as follows:

| Rule | Where it bites in this milestone |
|---|---|
| 1 Totality | `gnd import ossie` reads foreign YAML/JSON. The reader, the formula parser GND adds and the extension decoder are each total over arbitrary input, with hostile-input tests (OS3). Export reads only validated models, but its loss-report reader is total too. |
| 2 Cap bounds the algorithm | Import resolves relationship names (`Concept.rel`), `extends` chains, `identify_by` paths and formula ASTs, which can be quadratic or deep. OS3 ships time-bound tests over each layer it adds. |
| 3 Validation order | Import order: byte cap, then YAML events, then the vendored JSON schema, then Ossie name rules (unique concepts, declared references), then **verification of the extension's (or sidecar's) binding digest**, then GND admission over the native projection merged with the verified extension. No extension content reaches admission unverified. The order is pinned by a source-order assertion (OS3-C2; p2 F7; r2 placed the digest after admission). |
| 4 One walk | One disposition walk over every JSON pointer of the model document decides `native`/`requires`/`extension`/`refused` (p2 F3). There are no per-kind copies. The census test (predicate 3) is its witness. |
| 5 One home | The GND↔Ossie mapping is normative in one new section of `gnd-orm-core/references/representation-format.md` ("Ossie interchange"). Docs and skills cite it. The vendored Ossie schemas are sync-pinned copies of upstream (one artifact under the rule's scope note), held identical by a digest test against the pinned commit. |
| 6 Measure | OS0 measures the export census, the converter's offline behaviour and the formula grammar's reach before OS1–OS4 are specified. Contested mapping questions (role order, OneToOne, modality) are settled by experiments on the fixtures: E4 for role order, E6 for OneToOne and modality (p2 F19). |

Milestone-specific rules (proposed):

- **R7 Never claim more than the pinned bytes.** Every compliance sentence
  names the Ossie spec version and the two pinned commits. A re-pin is its own
  owner-gated change.
- **R8 Lossless or loud.** The loss report is part of the output contract. An
  element without a disposition is an internal error (exit 70), not a quiet
  omission.
- **R9 Credential-free by default.** Ordinary gates use only the vendored
  schemas and GND's own code. Upstream `validate.py`, `OssieParser` and
  `ossie_relationalai` run only in the opt-in `ossie_oracle` lane, in their
  own environments. They are never GND runtime dependencies (CONTRIBUTING; the
  `relationalai` package is proprietary and its converter extra is opt-in
  upstream).

## 1. Scope, sources and authority

### 1.1 What Ossie is, as read on 2026-11-10

- Four layers (`core-spec/spec_layers.md`, informational): 1 Model
  Definition (`core-spec/spec.md`: datasets, fields, relationships, metrics,
  SQL expressions), 2 Relational Query Interface, 3 Wide Table Query
  Interface, 4 Ontology (`ontology/ontology.md`). Each layer "can be adopted
  independently".
- Version: 0.1.1 (2025-12-11) is the only release, and it has no ontology.
  Sources: `core-spec/spec.md` §Version History and `ontology/ontology.md`
  §Version History at the pin (p2 F18).
  0.3.0.dev0 is unreleased and its schema is mutable ("do not depend on this
  version in production"). The ontology layer exists only in 0.3.0.dev0.
- Ossie defines no single "compliant" certification. What exists is
  `validation/validate.py`, with `ossie-schema.json`, `ontology/ontology.json`
  and `ontology/mapping.json`; `compliance/portability` (an M0–M3
  converter-fidelity ladder over layer 1); and `compliance/query` (layer 2
  query cases).
- The ontology layer is ORM-shaped: `EntityType` and `ValueType` concepts,
  built-in value types, `extends` (subtypes), `identify_by` (preferred
  reference), n-ary relationships grouped under the concept that plays the
  first role, `verbalizes` reading patterns, `multiplicity` (`ManyToOne`,
  `OneToOne` only), `requires` (constraint formulas) and `derived_by`
  (derivation formulas, including recursion), plus optional IRIs.

### 1.2 Why layer 4 and not layer 1

GND models are conceptual. They carry no tables, columns or SQL. Layer 1
requires `datasets[].source` (a physical table) and SQL expressions. It could
only be produced by inventing bindings or adding a physical-binding concept to
GND, and that is a new modelling feature (OD3). Layers 2 and 3 are query
engines, outside GND's purpose. Layer 4 maps onto GND's metaschema element for
element (§2).

### 1.3 What "PyRel is Ossie-compatible" means here (measured, not assumed)

- apache/ossie-converters ships `relationalai/` (`ossie_relationalai`,
  authored by RelationalAI). It converts **Ossie → PyRel** only. There is no
  PyRel → Ossie converter. It emits ontology-style PyRel (`m.Concept`,
  `m.Property("{A} has {B}")`, `identify_by`, `define` rules from mappings).
- In the pinned snapshot (`tests/snapshots/.../flights/flights.py`), the
  converter emits **no `require`**. The Ossie `requires` constraints of
  `flights.ontology.yaml` do not reach PyRel. `derived_by` with `OR` or
  `EXISTS` raises `NotImplementedError` (`formula.py`). It pins
  `relationalai==1.39.0`, while GND's PyRel export pins `1.30.1`.
- GND's own `gnd export pyrel` writes rule-checking programs
  (`m.Relationship(fields=…)` plus `require` per constraint), not
  ontology-style declarations.

Therefore GND → PyRel plus PyRel ⇄ Ossie does **not** make GND
Ossie-compliant transitively. PyRel helps in three ways, and each is used:

1. **An independent consumer (OS4).** The converter is a third-party reader
   of GND's Ossie output: if it builds the same concepts and properties, the
   export means what GND says.
2. **A user path.** GND model → Ossie document → `ossie_relationalai` → a
   RelationalAI model on Snowflake, alongside GND's existing PyRel rule
   export. GND's rule export stays the path for constraints, because the
   converter drops them.
3. **A shared idiom.** The converter's PyRel mirrors ORM (concepts, readings,
   identify_by), which confirms the §2 mapping direction. GND's requirement IR
   in `src/gnd/export/pyrel_rules.py` (`requirements(doc)`, one `Requirement`
   per constraint, domain and check) is the reuse seam for rendering Ossie
   `requires` formulas in OS2.

### 1.4 Sources

| Source | Section | Used for |
|---|---|---|
| owner request, 2026-11-10 | this conversation | goal; rulings OD0–OD8 (§10) |
| `ontology/ontology.md` @ee89dbdc | Concepts, Relationships, Identifying relationships, Derivation expressions, Requires, Global identifiers, Mapping documents | the target contract |
| `ontology/ontology.json`, `validation/validate.py` @ee89dbdc | — | oracle and vendored schema |
| `core-spec/spec_layers.md` @ee89dbdc | Layers | layer choice |
| ossie-converters `ontology/` @83ddc294 | `ossie_ontology.parser.OssieParser` (`ontology/src/ossie_ontology/parser/`), `expr/formula/` (lexer, parser, validator), README | the formula grammar and parser named "OssieParser" throughout this plan (p2 F14) |
| ossie-converters `relationalai/` @83ddc294 | README, `formula.py`, `converter.py`, snapshots | consumer oracle |
| `src/gnd/schema/orm-meta.schema.json` @720053ff | `$defs` object_type, fact_type, role, constraint kinds, derivation_rule | source contract |
| `src/gnd/export/pyrel_rules.py` @720053ff | `requirements`, `_refuse_unsupported_model` | reuse seam, refusal precedent |
| `src/gnd/rai_import.py` @720053ff | bounded `rai-orm-from-schema` import | import precedent (caps, provenance) |
| model-composition plan r3 | predicate 5 | include route guard |
| AGENTS.md, CONTRIBUTING.md | PRs, credential-free development | protocol |
| owner memory: PyRel optional, checkpoints | — | docs wording, checkpoints |

## 2. Contract proposal and product behaviour

### 2.1 Element mapping (proposal; OS0 measures it, OS1 fixes it)

| GND metaschema | Ossie ontology | Disposition |
|---|---|---|
| object type `kind: entity` | `concept`, `type: EntityType` | native |
| object type `kind: value`, `primitive` | `type: ValueType`, `extends: [<built-in>]` | native; `Duration` has no built-in, so it is kept as a GND value type: `extends: [Integer]`, with its meaning in the extension (o, OD5, a deliberate divergence) |
| `subtype_of` | `extends` | native |
| subtype derivation rule | concept `derived_by` | requires/extension (OS2) |
| `reference` (preferred identifier) | `identify_by` and an identifying relationship | native |
| `independent`, `storage`, `description`, `provenance` | `description`; the rest in the extension | native + extension |
| fact type, roles, `role_name` | relationship under its first-role concept; `roles[].concept`, `roles[].name` | native; roles reordered so the uniqueness fits `ManyToOne` (o, OD4), with the original GND order kept in the extension for a lossless import |
| `reading`, `inverse_reading` | `verbalizes` patterns `{Concept}` / `{Concept:role}` | native |
| simple internal uniqueness on n−1 roles | `multiplicity: ManyToOne` (last role determined), with role reordering | native if reorderable, else requires/extension |
| uniqueness on both roles of a binary | `OneToOne` | native |
| spanning, external uniqueness; mandatory; frequency; ring; subset; equality; exclusion; exclusive-or; value range; value comparison; cardinality; subtype partition; guarded | `requires` formulas where the grammar can state them | requires, else extension |
| alethic/deontic `modality`, `source`, `status`, `rationale`, `remedy` | none | extension |
| derivation rules and aggregates | `derived_by`; `COUNT[...]`-style aggregates | requires/extension (OS2) |
| objectification | none native (Ossie has no nesting) | extension, or refused (OS0 measures) |
| operations, dynamic rules, frames | none | extension (opaque) |
| `includes` | none (no cross-model references) | compose or refuse (predicate 7) |
| `reference_populations`, `sample_population` | none in the ontology; mappings are layer 1 | `refused`, reason `population:out-of-scope`, one row per pointer; covered by the census test; removed in the round trip (predicate 5) (p2 F1; r2 said "out of scope", which is not a disposition) |

### 2.2 The `gnd` vendor extension

`custom_extensions` exists in the layer-1 spec. Whether it is admitted on
ontology concepts and relationships at the pinned commit is unverified until
OS0 checks `ontology.json`. If it is not admitted, the fallback is a sidecar
`FILE.gnd.json` bound by digest to the document (OD2). Content: canonical JSON
of the source elements that are not native, keyed by element id, plus the
model identity digest. Import verifies the digest before using any of it
(rule 3).

### 2.3 CLI and exits (proposal)

- `gnd export ossie MODEL --out FILE [--loss-report FILE] [--format yaml|json]`
  exits 0 on success. The loss report is always written: by default to
  `FILE.loss.json` beside the document, or to `--loss-report` when given. The
  document and its report are published together or not at all. If the
  report cannot be written, nothing is published and the exit is 74 (`EXIT_IO`)
  (p2 F4). It exits 3 for an invalid model or a refused construct
  under `--strict` (OD6), 66 for missing input, 11 for an existing output (`EXIT_COLLISION`, the
  code `write_new` collisions already use) and 70 for an internal error.
- `gnd import ossie FILE --out MODEL [--loss-report FILE]` exits 0 or 3, with
  `rule_id`s in one order, and 11 if the output already exists.
- No network, no upstream package import, at runtime.

## 3. Dependencies and artifact homes

| Artifact | Home |
|---|---|
| exporter | `src/gnd/export/ossie.py` (new; layer map entry in `tools/gnd_layers.json`) |
| importer | `src/gnd/ossie_import.py` (new; same pattern as `rai_import.py`) |
| vendored schemas | `src/gnd/schema/ossie/ontology.json` (+ `mapping.json` only if OD3), with `PINNED.json` naming commit and sha256 |
| loss-report schema | `src/gnd/ossie-loss-report.schema.json` |
| normative mapping | `src/gnd/skills/gnd-orm-core/references/representation-format.md`, new section "Ossie interchange" |
| CLI | `src/gnd/commands/export.py`, the import command group; CLI goldens under `tests/fixtures/rf1-pins/goldens/` regenerate |
| oracle lane | `tests/test_ossie_external_oracle.py`, marker `ossie_oracle` (new; registered beside `pyrel_oracle` in `pyproject.toml`); `tools/ossie_oracle.py` builds pinned upstream environments outside the repository |
| docs | `docs/explanation/ossie.md` and a how-to |
| planning | `.gnd-planning/milestones/ossie-interchange/` |

Upstream prerequisites: neither package is on PyPI (`apache-ossie-ontology`
and `apache-ossie-relationalai` return 404 on 2026-11-10), so the oracle lane
installs from git at the pinned commits. `ossie_relationalai` needs the
proprietary `relationalai==1.39.0` and a `raiconfig.yaml`. Its offline mode
(`declared_table`) is claimed upstream, and OS0 measures it.

Phase dependencies (p2 F13; r2's single arrow contradicted this prose):

- OS1 needs OS0.
- OS2, OS3 and OS4 each need OS1 only. OS4 uses OS2's output when it exists,
  but that is a soft input, not a prerequisite.
- OS5-draft (the owner checkpoint) needs OS1. Final OS5 needs OS1–OS4.
- OS6 needs OS2 (formula shapes) and OS4 (the lane that measures the effect)
  (o, OD7).
- The close needs OS5 and OS6's recorded end state (predicate 9).

## 4. Phases

### OS0 — Pin, measure and decide (no product code)

Deliverables: pinned upstream commits and digests; an isolated oracle
environment (scratch, outside the repository); the export census, listed;
for every census model, a hand-run element inventory against §2.1; the
experiments below; the mapping table promoted to measured; and a checkpoint
page for the owner.

Experiments, recorded before they run:

- E1: does `ontology.json` admit `custom_extensions` on concepts and
  relationships? (decides OD2)
- E2: does the `OssieParser` formula grammar express each GND constraint kind?
  This uses one hand-written formula per kind, from a census model.
- E3: does `ossie_relationalai` convert `flights.ontology.yaml` and one
  hand-translated GND example offline on relationalai 1.39.0? On a separate
  Python environment from GND's 1.30.1 PyRel environment.
- E3b (o, OD8): the same on relationalai 2.0.1 (released 2026-11-06; 2.0.0 on
  2026-11-03), overriding the converter's `==1.39.0` pin. The result tells OS4
  and OS6 which version to target. It is an observation only: GND's own PyRel
  pin (1.30.1) does not change in this milestone.
- E4: role order — how many census fact types need reordering to state their
  uniqueness as `ManyToOne`, and does reordering change readings? (OD4 is
  ruled "reorder"; E4 counts the exceptions)
- E5: upstream validator and parser run over Ossie's own examples, as a
  liveness proof that the oracle scores both ends: one valid document and one
  deliberately broken one.
- E6 (p2 F19): inventory checks for the two other contested questions. First,
  OneToOne: count the census binaries with a uniqueness on each role, and
  check that `OneToOne` states both. Second, modality: count the census
  constraints by `modality`, and confirm that the extension carries every
  alethic/deontic mark at its pointer.

Criteria: OS0-C1, every JSON pointer of every census model has a measured
disposition (p2 F3); OS0-C2,
each of E1–E6 (and E3b) has a recorded result with its limits; OS0-C3, the
rulings that depend on a measurement are settled: OD2 by E1, OD4's exceptions
by E4, OneToOne and modality handling by E6, and the target `relationalai`
version by E3/E3b (o; p2 F17, F19; the r1 wording is kept in §11). Spec: [phase-OS0-spec.md](phase-OS0-spec.md).

### OS1 — Export core: types, fact types, readings, identifiers

Covers the `native` rows of §2.1, the extension for everything else, the loss
report, determinism, the include guard, vendored schema validation and the
oracle lane. Criteria: OS1-C1 to C5 (predicates 1, 2, 3, 7).

### OS2 — Constraints and derivations as formulas

A formula renderer over `pyrel_rules.requirements` (reuse, not a second
constraint walk; rule 4). Each formula is checked by `OssieParser` in the
oracle lane, and by GND's own grammar check for the subset it emits in
ordinary gates. The expected-verdict corpus (predicate 4) is the phase's
approval instrument and is committed before the renderer (p2 F2). Criteria:
OS2-C1 to C4 (predicates 3, 4).

### OS3 — Import

A total reader, caps, validation order, `imported` provenance, an extension
round trip, and foreign documents (the Ossie flights ontology). Criteria:
OS3-C1 to C4 (predicate 5).

### OS4 — PyRel consumer cross-check

In the oracle lane: export → `ossie_relationalai` → PyRel source, then a
structural comparison with the export's declaration list. Converter skips
(`requires`, `OR` or `EXISTS` derivations) go into the lane artifact
`consumer-limitations.json`, keyed by converter commit and `relationalai`
version, not into the runtime loss report (p2 F8). The lane shows, beside the converter's output, what
GND's `gnd export pyrel --rules` adds for the same model. Criteria: OS4-C1,
C2 (predicate 6). The converter's dropped `requires` are the input to OS6
(o, OD7).

### OS6 — Upstream contribution: `requires` → `require` in `ossie_relationalai` (o, OD7)

The converter emits no `require` for Ossie `requires` formulas, so the
constraints GND exports (OS2) are lost on the way to PyRel. OS6 prepares a
contribution to apache/ossie-converters `relationalai/` that renders each
parsed `requires` formula as `m.where(...).require(...)`. It is modelled on
GND's own rendering in `pyrel_rules.py`, re-derived under Apache-2.0 for that
repository, not copied wholesale. Upstream tests and snapshots are extended,
starting with `flights`.

- Deliverable: a **local** branch with upstream tests passing locally at the
  pin and the target `relationalai` version chosen from E3/E3b. Nothing is
  pushed to a public remote, and no fork is created, until the owner approves
  both the fork push and the PR's exact title and body (p2 F6). Then the
  upstream PR is opened.
- Criteria: OS6-C1, upstream `relationalai/` tests pass, with new snapshot
  cases that contain `require`. OS6-C2, for every OS2 constraint kind the
  converter now renders, GND's OS4 lane, run against the recorded OS6 branch
  commit, observes a `require`, and the matching row of
  `consumer-limitations.json` goes away for that commit. That commit is
  recorded separately from the R7 pins. Published compliance claims stay on
  the pinned converter `83ddc294` unless an owner-gated re-pin happens (p2
  F10). OS6-C3, one of predicate 9's two end states is recorded. Merge upstream is
  not a criterion: the Ossie maintainers decide it.
- Follows the upstream repository's CONTRIBUTING and licence-header rules
  (`dev/check-license`). No GND private detail and no downstream application
  names go in the upstream text.
- Depends on OS2 (formula shapes) and OS4 (the lane that measures the effect).
  The close needs one of predicate 9's end states, not an upstream decision.
  A PR still open at close is recorded with its state as a carryover (p2 F5).

### OS5 — Docs, skill, claim wording

The explanation page, a how-to with a business-level telling (`/gnd` skill
prompts and visual results, no Python on the tutorial page), the
`gnd-export` skill section, and the README one-liner. The review copy goes to
the owner early: a checkpoint after OS1 (OS5-draft), not only at the end.
Criteria: OS5-C1 (predicate 8).

### Close

Milestone close record. Review instrument: the maintained light panel (o,
OD0).

### Obligation-to-phase map

| Obligation | Source | Phase / gate |
|---|---|---|
| answer "what would compliance take" with a falsifiable claim | owner 2026-11-10 | predicates 1–8 |
| use PyRel where it helps | owner 2026-11-10 | §1.3, OS4 |
| totality, caps, order, one walk, one home, measure | project.md | §0, every spec |
| include-bearing models refused or supported | model-composition predicate 5 | OS1-C5 |
| credential-free ordinary gates | AGENTS.md, CONTRIBUTING | R9, oracle lane |
| PyRel optional in docs | owner feedback 2026-10-15 | OS5-C1 |
| checkpoints before completion | owner feedback 2026-10-14 | OS0 page, OS5-draft |
| CLI goldens updated for new subcommands | rf1-pins | OS1, OS3 |
| try relationalai 2.0 | owner 2026-11-10 (OD8) | OS0 E3b |
| contribute `requires` → `require` upstream | owner 2026-11-10 (OD7) | OS6 |
| keep `Duration`, documented divergence | owner 2026-11-10 (OD5) | OS1, OS5 |

## 5. Documentation, skill and compatibility surfaces

- New subcommands change `gnd export --help` and `gnd import --help` goldens
  (`tests/fixtures/rf1-pins/goldens/cli-help/*`, `cli/tree.json`). OS1 and OS3
  regenerate them deliberately.
- No change to existing exports, the model format or populations.
- The `gnd-export` skill gains an Ossie section. `gnd-orm-core` holds the
  normative mapping.

## 6. Risks and controls

| Risk | Control |
|---|---|
| The 0.3.0.dev0 ontology schema changes under us | R7 pins; a digest test on the vendored copy; re-pin as an owner-gated amendment |
| A "compliant" claim read as certification | OS5 claim wording names layer, version and commits; no certification is run (project.md opt-in gates) |
| Formula grammar too weak for ORM constraints | E2 measures it; extension fallback; the loss report makes loss visible |
| Proprietary `relationalai` enters GND dependencies | R9; oracle lane in its own environment; never imported by `src/gnd` |
| Converter's offline mode does not work | E3 and E3b; OS4 then records the converter as unrunnable and predicate 6 is amended (owner) |
| relationalai 2.0.x is days old and the converter pins 1.39.0 | E3b is an observation only; OS4 and OS6 target the version E3/E3b show working, recorded with its digest |
| Upstream PR (OS6) is rejected, stalls or is not approved for posting | the close needs only a recorded end state (predicate 9); an open PR is a carryover; GND's own rule export still covers constraints (p2 F5) |
| Role reordering silently changes readings | E4; the mapping keeps the GND reading text verbatim in the extension |

## 7. Out of scope

- Layer 1 semantic models, mapping documents and SQL expressions, unless OD3
  selects them (then a successor milestone or an amendment).
- Layers 2 and 3, and the `compliance/query` and `compliance/portability`
  suites (layer 1 and 2 instruments).
- Running anything on Snowflake or a RelationalAI engine.
- Upstream contributions other than OS6 (in particular, to the Ossie spec
  itself, for example a `Duration` built-in). r1 excluded all upstream
  contributions; OD7 (o) moved the converter contribution in scope.
- Re-pinning GND's own PyRel export (1.30.1) to relationalai 2.x.
- Certification or recertification.

## 8. Execution, approval and review protocol

`auto=false`. Each phase: spec, owner gate, implementation, focused tests
(`uv run pytest -q tests/<phase-tests>.py …`), one independent reviewer in a
different tool for the diff, refactoring review, record
(`NNN-phase-OS<n>.md`). Work goes on a topic branch with a PR; merge only on
the owner's explicit authorization. Plan review and close review use the
maintained light panel (o, OD0), via
`uv run python tools/run_gnd_review_panel.py --light REQUEST --out DIR`.
Each run needs the owner's go-ahead.

## 9. Per-phase verification and affected consumers

| Phase | Ordinary gate | Opt-in lane | Affected consumers |
|---|---|---|---|
| OS0 | none (no code); evidence under `evidence/OS0/` | E1–E5 | none |
| OS1 | `tests/test_ossie_export.py`, CLI golden tests | upstream validator and parser | `gnd export` help |
| OS2 | `tests/test_ossie_formulas.py`, `tests/test_pyrel_rules.py` | parser | PyRel rule export (shared IR; must not change) |
| OS3 | `tests/test_ossie_import.py`, `tests/test_diff*.py` | — | `gnd import` help |
| OS4 | — | `tests/test_ossie_external_oracle.py` | none |
| OS5 | docs tests (`tests/test_plan_app_docs.py` pattern for PyRel wording) | — | site |
| OS6 | none in this repository | upstream `relationalai/` suite on the local branch, in its own environment with the proprietary `relationalai` (outside this repository, never an ordinary gate; p2 F15); OS4 lane re-run | `consumer-limitations.json` |

Exact test file names are proposals until each spec fixes them.

## 10. Owner decisions and open questions

Rulings were given by the owner in the conversation on 2026-11-10 (`(o)`),
quoted. The prior question and readings are kept in each row.

| ID | Question | Readings and cost | Ruling |
|---|---|---|---|
| OD0 | Plan-review instrument | maintained panel (the bar), or one Codex reviewer as in model-composition (MD0) | (o) "the light": the maintained **light** panel (`gnd-review-panel-light`, default effort high) reviews the plan and the close. Selecting it does not run it. A run needs its own go-ahead, because it spends provider budget |
| OD1 | Target layer | (a) ontology only (proposed); (b) ontology plus layer 1, which needs physical bindings (OD3) | (o) "ontology layer only": (a) |
| OD2 | Where non-native elements go | `custom_extensions` in the document if E1 admits it; otherwise a digest-bound sidecar. The difference is whether a third party sees GND detail | (o) "ok": as proposed. E1 decides between the two |
| OD3 | Physical bindings for layer 1 and mappings | not now (proposed); or a new binding concept in the model (a model-format change, its own milestone) | Follows from OD1, not ruled separately: not now |
| OD4 | Role order | reorder roles to state uniqueness natively (more native, readings rewritten) or keep GND order and put uniqueness in `requires` (fewer native multiplicities) | (o) "if it is not too difficult do it": reorder. This is expected to be cheap: `verbalizes` patterns can name roles in any order (`'{Person:child} is a child of {Person}'`, ontology.md §Derivation expressions), so a reading need not change when roles are reordered. E4 confirms this. If E4 finds a fact type that cannot be reordered without changing its reading, OS1 keeps GND order for that fact type, puts its uniqueness in `requires`, and the record counts them |
| OD5 | `Duration` and other primitives with no Ossie built-in | `extends: Integer` plus extension (proposed), or refuse | (o) "keep it, we will have to be different to Ossie here": keep `Duration` as a GND value type (`ValueType`, `extends: [Integer]`, whole days) with its GND meaning in the extension. This is a deliberate, documented divergence from Ossie's built-ins (OS5 states it), not a refusal |
| OD6 | Default on a refused construct | write the document with a loss report and exit 0 (proposed), or exit 3 unless `--allow-loss` | (o) "why not": read as accepting the proposal. Exit 0 with the loss report; `--strict` turns any `refused` disposition into exit 3. If the owner meant the other reading, this row is re-ruled before OS1's spec. **An explicit owner confirmation of this reading is a listed precondition of the OS1 spec gate** (p2 F12) |
| OD7 | Contribute `requires` → `require` to `ossie_relationalai` upstream | outside (proposed); or a follow-up after OS4 | (o) "yes": in scope as phase OS6 (§4). Opening the upstream PR is outward-facing, so its exact text gets a separate owner go-ahead before it is posted |
| OD8 | Which `relationalai` versions OS0 tries | 1.39.0 only (the converter's pin) | (o) "you can also try relationalai 2.0": E3 runs on 1.39.0 and on 2.0.1 (E3b). OS0 may install both, proprietary, in scratch environments only. This also answers OS0's D1 |

## 11. Change log

- r1 (2026-11-10): first draft, not reviewed.
- r2 (2026-11-10): applied owner rulings OD0–OD8 (`(o)`). Prior wording that
  the rulings replaced: OS0-C3 read "OD1–OD7 can be ruled on measured cost";
  §7 excluded every upstream contribution.
- r3 (2026-11-10): applied the light panel's 19 prioritized fixes over r2
  (`(p2 F1)`–`(p2 F19)`; [PANEL-REVIEW.md](../evidence/plan-review-r2/PANEL-REVIEW.md),
  synthesis sha256 `3c55be06dd7a5470e9760909067a1ef79ffe898d2ae0b1c83fc8aa7f3db38e64`).
  The agreed groups were G1 populations (5 seats), G2 semantic oracle (3), G3
  disposition unit (2), G4 OS6 close (2), G5 phase graph (2) and G6 OD range
  (3); 13 views came from a single seat. Every fix was applied as the
  synthesis proposed. The repaired bytes carry no review opinion.
