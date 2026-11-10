# Model composition

**Status: r2, draft, awaiting the owner's plan gate.** r2 applies the Codex
review of r1 (P1-P18, all reproduced and accepted;
[review](../evidence/plan-review-r1/codex-review.md), triage in §11). **r2
itself has not been reviewed.** MD0 ruled (o, 2026-11-09): one reviewer,
Codex ("Codex review"). `auto=false`. Authoring this plan approves nothing.
Tags: `(r1)` marks a change made for that review.

Phase prefix `MC`. Source: GR-D4, [issue 95](https://github.com/vasiloglou/gnd-public/issues/95),
filed by the owner on 2026-11-06 and excluded from the rule-check-adoption
milestone as "its own milestone" (owner selection relayed 2026-11-06,
[rule-check-adoption plan §1 and §7](../../rule-check-adoption/notes/rule-check-adoption-plan.md);
[close record](../../rule-check-adoption/012-milestone-close.md), open-questions
row "GR-D4"). The owner asked for this plan on 2026-11-09 ("Plan the milestone").
Inspection baseline: main at `459ca8d2`.

One model file declares that it takes the object types, fact types and
constraints of another model file, pinned by that file's raw sha256, the way
`reference_populations` pin a population. The including file adds what the
project owns: constraints, including inline constraints (ring, mandatory,
internal uniqueness) placed on included fact types (r1 P1), and possibly
object types, fact types and operations of its own. One id namespace across
both. A tool that ships a vocabulary to many projects (the case in the issue:
a fact export with nine fact types such as "Component uses Component") then
ships a new vocabulary file without touching the project's rules, and the
project keeps a real model file it can pass to `gnd validate`, `check`,
`verbalize` and `evolve`.

## Completion predicates

The milestone is complete when, on main after merge:

1. A model with `includes:` (MD1, MD2) loads through `load_model(path)`: each
   included file is read beneath the model's parent with no symlink, its raw
   sha256 is checked, and the loaded `Model` is the composition. `gnd validate`
   and `gnd check` on it agree with its committed hand-flattened twin on exit
   code and on every output field outside a published comparison allowlist
   (model path, model digests and identities, version), and the allowlisted
   fields are verified independently (MC1-C1; r1 P9).
2. Project-owned inline constraints on included fact types work: the issue's
   acyclic rule on an included "uses" fact type, and a mandatory constraint,
   check as on the twin (MC1-C8; r1 P1).
3. Every refusal of an include-bearing input is exit 3, carried as a
   `ValidationIssue` with a distinct, value-free `rule_id` in text and JSON
   output (MC1-C2; r1 P5), in one published order with compound-fault cases
   (MC1-C3; r1 P3).
4. No model without `includes` changes: loaded dump, `model_dump_json`, the
   named identities and `gnd validate --identity` are equal over a defined
   tracked-file census of `*.orm.yaml` and `*.orm.json`, and the expected
   refusals in it are unchanged (MC1-C5; r1 P10, P15).
5. From the commit that admits `includes`, no route gets a silent half-model:
   every direct-bytes consumer either supports the include-bearing model or
   refuses it with `include:unsupported-route` (MC1 guards, MD15; MC2
   supports; r1 P16).
6. `gnd evolve` writes only the including file, never a flattened model,
   refuses operations on included elements, and re-pins an include after a
   vocabulary update with a blast-radius review computed over the old and new
   compositions (MC3; r1 P6, P7, P17).
7. The issue's scenario runs end to end on a committed fixture: vocabulary
   v1, project rules, a vocabulary v2 that removes a fact type a rule uses,
   the re-pin preview that names the broken rule, and the combined re-pin plus
   rule edit that publishes (MC3-C4).
8. The normative contract has one home (`representation-format.md`, new
   section "Model includes (version 5)"); skills and docs cite it (MC4).
9. Each phase has an approved spec, a record with verbatim focused-gate output
   and one independent reviewer; the close record disposes every open
   question and closes issue 95.

## 0. Binding design rules

The six standing design rules of
[project.md](../../../../.codex/skills/process-phase/references/project.md)
bind every phase. Milestone rules:

1. **Composition happens once, in the loader.** One module resolves
   includes and builds the composed document and its provenance; every
   consumer receives the composed `Model`. No consumer re-implements
   resolution.
2. **No silent half-models, from the first commit.** A route that cannot
   resolve includes refuses before any work; it never loads the including file
   alone or a tempdir copy without its included files. The guard ships in the
   same phase that admits `includes` (r1 P16).
3. **Frozen variants.** Models without `includes` keep every byte of every
   output and every recorded digest, across every serialization entry point
   (r1 P10). No new report version unless a phase spec proves one is needed
   and the owner rules it in.
4. **The including file is the only file GND writes.** The included file is
   input, never a write target. A written includer keeps its declarations,
   contains only owned elements and recomposes (r1 P17).
5. **Freshness is claimed only after verification.** The includer's raw
   sha256 commits to the included bytes it pins; a positive currency or
   publication claim additionally requires that those bytes were verified in
   the same invocation (r1 P8).
6. **Measure, don't assert** (inherited, rule-check-followups §0.2). Identity
   and compatibility claims are measured over the census before they are
   planned against; every refusal has a case observed red first.
7. **Stop rule (size).** A phase pauses for the owner past 1.5 times its
   estimate.

## 1. Scope, sources and authority

### 1.1 Obligations

| # | Obligation | Source | Kind | Owner |
|---|---|---|---|---|
| O1 | One model takes object types and fact types from another file | issue 95, "Asked for" | request | MC1 |
| O2 | Bound by digest like a reference population | issue 95 | request | MC1 (MD1) |
| O3 | Including file adds constraints, possibly fact types | issue 95 | request | MC1 (MD4, MD10) |
| O4 | `gnd validate` and `gnd check` resolve it | issue 95 | request | MC1 |
| O5 | Ids stay in one namespace | issue 95; `representation-format.md` "One id namespace" | request; existing rule | MC1 |
| O6 | The project owns a real model file usable with `gnd evolve` and `gnd verbalize` | issue 95, "Workaround today" | request | MC2 (verbalize), MC3 (evolve) |
| O7 | A vocabulary update must not overwrite the project's rules and must not leave the next check ill-formed | issue 95, "Why" | request | MC3 (re-pin, MD8, MD12, MD13) |
| O8 | The runner keeps generating the vocabulary file from exported facts | issue 95, last sentence | boundary | out of scope (§7); MC4 documents the vocabulary-file contract |
| O9 | GR-D4 is its own milestone | rule-check-adoption plan §1, §7; close record | owner ruling 2026-11-06 | this plan |
| O10 | Six standing design rules | project.md | standing | every spec §4 |
| O11 | Component index changes in the same commit as code; `components_index.py changed --base main --strict` before a PR | project.md "Component index" | standing | every phase |
| O12 | Dependency homes and import checks in `tools/gnd_layers.json`, allowance count zero | AGENTS.md "Refactoring dependency homes" | standing | MC1 (new home), every phase |
| O13 | Shared model queries through `ModelIndex`; family hooks in `constraint_families.FAMILIES` | AGENTS.md "Model queries" | standing | MC1 |
| O14 | Reference-bearing inputs: synth, codegen and older session contracts refuse them before publishing | `representation-format.md` "Fixed reference populations (version 4)" | precedent | MC1 guards, MC2 |
| O15 | Evolve CAS is single-leaf, "no multi-file atomicity" | `evolve/service.py:2141`, `safefs.py` | constraint | MC3 (rule 0.4 and 0.5) |
| O16 | `ValidationIssue` has `path`, `message`, `rule_id`, `severity`; no file field | `errors.py:13` | constraint | MC1 |
| O17 | Branch and PR per phase; merge only with the owner's authorization | AGENTS.md "Pull requests are required" | standing | §8 |
| O18 | Ring, mandatory and internal uniqueness are inline-only; the issue's rule is an acyclic ring | `orm-meta.schema.json` `$defs.inline_constraint` (`:1102`, `:1136`); `examples/rule_check/model.orm.yaml:14` | constraint (r1 P1) | MC1 (MD10) |
| O19 | `validate_declarations` refuses references unless version 4 | `model/__init__.py:499` | constraint (r1 P4) | MC1 |
| O20 | Evolve validation evidence is `valid: Literal[True]`; preview validates before the radius; `breaking` knows only rename and delete | `evolve/models.py:675`; `evolve/service.py:1360`, `:1473`, `:1520`, `:1527` | constraint (r1 P7) | MC3 (MD13) |
| O21 | Unattended source mode drives document and span validation | `model/_unattended.py:169-204` | constraint (r1 P18) | MC1 (MD16) |

### 1.2 Observed at `459ca8d2` (read, 2026-11-09)

| Fact | Where | Status |
|---|---|---|
| No include/extends/import mechanism exists; the schema's `$ref`s are internal | `schema/orm-meta.schema.json` | read |
| Meta-schema `version` enum is `[1,2,3,4]`; `operations` needs 2-4, `reference_populations` needs exactly 4; `object_types` and `fact_types` are required | `orm-meta.schema.json:7`, `allOf` | read |
| No `maxItems` on `object_types`, `fact_types` or `constraints`; `MAX_ENTRIES = 100_000` bounds reference-population rows, not model declarations | `orm-meta.schema.json:29`; `model/__init__.py:396` | read (r1 P14) |
| `Model` is `frozen`, `extra="forbid"`: an older gnd refuses an unknown top-level key at load; `model_dump` is overridden, `model_dump_json` is not | `documents.py:24`, `:63` | read (r1 P10) |
| `load_model(path)` reads under a retained parent descriptor (`retained_root`, `O_NOFOLLOW`) and binds references after loading with `_bind_at`; reference-free models keep a historical symlink route | `model/__init__.py:338-380` | read |
| `load_model_bytes` has 40 call sites in 16 modules; `load_model` 28 | grep | read |
| The bounded reader raises one `ArtifactError` class for non-regular, oversized and grown files | `artifacts.py:583-594` | read (r1 P13) |
| Validate and check map only `ModelValidationError` to issues; other exceptions become `error: {type, message}` | `api.py:313`, `checking_service.py:306`, `payloads.py:121` | read (r1 P5) |
| `src/gnd/composition.py` is population composition (`gnd compose`); its API route loads with `load_model_bytes` and collapses refusals to "invalid model" | `composition.py:1`, `api.py:980` | read (r1 P16) |
| PyRel runtime admits a model document by its own parse | `export/pyrel_runtime.py:990` | read (r1 P16) |
| `values._model_digest` is still `repr` of the dump; ROF4 accepts either it or canonical identity v2 via `model_identity_matches`; both cover `version` | `values.py:179-196`, `:253`, `:289`, `:304` | read |
| Conformance computes raw-file currency before retrying a structural load | `conformance/service.py:76`, `:196`, `:206`; `conformance/currency.py:94` | read (r1 P8) |
| Evolve publishes the proposal's candidate text over the live file with `LeafIdentity(sha256=before)`, and reloads the live model at apply and finalization | `evolve/service.py:1456`, `:1984`, `:2141`, `:2310` | read (r1 P6) |
| Discover and ILP render candidate models as JSON (comments lost) | `discover/output.py:99`, `:140` | read |

### 1.3 Direct-bytes consumers (MC1 guards them, MC2 re-reads and supports)

Routes that read or hash the model file themselves rather than receive a
loaded `Model`: evolve (`_load_model_document`, `_parse_model_text`, CAS),
recovery verify (tempdir copy), `gnd import rai-orm` (tempdir copy, rt
writer), export `render_pyrel` (embeds raw text as `MODEL_TEXT`),
`pyrel_runtime` admission, `pyrel_rules`, export applications (tempdir
copies), Lean and Souffle export (`model_raw_sha256`), witness service and
io, discover, ILP, batch, checking-service composition verify, the population
compose API route (`api.py:980`, r1 P16), codegen manifest and emit,
conformance currency, extract, fidelity and doccheck, measure, the exp session
family (`session.py` tempfile, `session_contract`, `session_replay`,
`session_judgments`), judgments, `api.py:1123`, two skill scripts
(`validate_model.py`, `verify_migration.py`), and examples. The MC1 spec turns
this into an activation inventory with one row per admission point (r1 P16).

### 1.4 Authority

The owner's request (2026-11-09); issue 95; the owner's 2026-11-06 selection
that put GR-D4 in its own milestone; MD0 (o, 2026-11-09). Approves no bytes.

## 2. Contract proposal and product behavior

All of this is proposed; the owner rules on MD1-MD16 (§10).

### 2.1 Declaration (MD1, MD2, MD11)

```yaml
version: 5
includes:
  - id: components-vocabulary
    path: vocab/components.orm.yaml
    sha256: <64 lowercase hex digits of the exact file bytes>
fact_type_constraints:            # MD10: inline constraints on included fact types
  - fact_type: component_uses_component
    constraints:
      - { id: no_use_loops, type: ring, variant: acyclic, modality: alethic, ... }
constraints:                      # ordinary top-level constraints
  - ...
```

Exactly three fields per include entry; at most 8 entries. An include-bearing
file may omit `object_types` and `fact_types` (MD11; r1 P2). Paths follow the
reference-population rules (confined POSIX relative, beneath the explicit
model parent, no symlink in root, ancestors or leaf, ≤32 components, ≤4096
chars). One included file is at most 10 MiB, the set at most 32 MiB. The
checks reuse `_relative`, `retained_root` and `read_regular_bounded_at`; the
reader gains a typed size refusal (a subclass of `ArtifactError`, so every
predecessor catch is unchanged; r1 P13).

### 2.2 What an included file is (MD3, MD16)

A complete, standalone-valid model file (`gnd validate` exits 0 on it alone)
with `object_types`, `fact_types` and optionally `constraints` and
`deontic_notes`. It declares no `includes`, `reference_populations`,
`operations`, `rejected_proposals` or `fact_type_constraints`, and its
`source`, if any, is not in unattended mode (MD16; r1 P18). Depth is one.

### 2.3 Composition (MD4, MD5, MD10)

The composed document is: the including file's own elements first, in their
authored positions, so every own-element path is unchanged; then each
included file's object types, fact types, constraints and deontic notes, in
`includes` order; then each `fact_type_constraints` entry's constraints
appended to its target included fact type's inline `constraints` (r1 P1, P11).
`version`, `model_id` and `includes` come from the including file; `source`
per MD16. Any id that appears twice anywhere in the composition is refused
with `include:collision`, naming both origins, never a value. The composed
document is then validated by the unchanged two-layer validation.

Provenance is a private side table on `Model` keyed by **structural address**
(section, index; and for inline constraints the host fact type and index),
not only by id, because constraint ids are optional (r1 P11). Each entry
records the origin (`model` or `includes[<id>]`), the original address in the
origin file, and the id when there is one. Included-file metadata (its
`source`, `model_id`, `version`) is recorded per include, separately from
element ownership. No section a digest covers is written into.

### 2.4 Identity (MD6) and its scope (r1 P8, P9)

No new identity function. The existing ones run over the composed loaded
content, which carries `version: 5` and the `includes` declarations, so an
includer's identities differ from its flattened twin's, by design.

The raw-byte sha256 of the including file is a commitment to the exact
included bytes it pins. It does not show that those bytes are present or
valid. Under rule 0.5, a positive freshness claim (conformance currency,
codegen manifest currency, evolve publication) is made only after the
included bytes were read and verified in the same invocation; MC2 and MC3 fix
the routes where today a raw-file hash is compared before any load
(conformance) or where the last dependency load precedes the CAS (evolve).

For every model without `includes`, every identity is byte-identical
(predicate 4).

### 2.5 Refusals (MD7, MD15)

Exit 3, input band. Each refusal is a `ModelValidationError` carrying one
`ValidationIssue` whose `rule_id` is the reason and whose `path` is the
declaration (`$.includes[<i>]`) or the element, so text and JSON output carry
it through the existing issue route (r1 P5). Proposed reasons (MC1 spec fixes
them literally): `include:declaration`, `include:path`, `include:unreadable`,
`include:size`, `include:hash-mismatch`, `include:parse`,
`include:invalid-included-model`, `include:forbidden-section`,
`include:collision`, `include:unknown-target` (a `fact_type_constraints`
entry naming no included fact type), `include:unresolved` (bytes-only route
with no root), `include:unsupported-route` (MC1's guards).

### 2.6 Diagnostics

An issue inside an included element is reported with the included file's
own path, prefixed with the origin: `includes[components-vocabulary]:$.fact_types[3]...`,
recovered from the provenance table, whether the semantic rule addressed the
element by index or by an id selector such as `fact_types[id=...]` (r1 P11).
Only include-bearing models change spelling; `ValidationIssue` gains no field.

### 2.7 Evolve and re-pin (MD8, MD12, MD13)

Operations whose target element originates in an include are refused
(`evolve:included-element`). `fact_type_constraints` entries are own
elements and evolve like any constraint. A new operation `repin-include`
changes one `includes[]` entry's `sha256` and optionally `path`.

The old composition needs the old vocabulary bytes (r1 P6). MD12 proposes:
the vocabulary-file contract (MC4) has tools write each version to a new
path, so the old file is still present at re-pin; when it is not, the caller
supplies it with `--previous-include ID=PATH`, verified against the pinned
sha256. Evolve retains both included files' bytes in the proposal evidence,
so preview, apply, publication and recovery work from authenticated
snapshots and re-verify the live included file before the CAS (rule 0.5).

A re-pin whose new composition is invalid is not staged (r1 P7). MD13
proposes: the preview still runs, over the composed old and new documents,
and returns an analysis-only result (exit nonzero, no staged candidate, no
`ValidationEvidence`) listing the elements the new vocabulary removed or
changed and every own constraint, operation, reference ownership and linked
project they break. The project then submits one proposal combining the
re-pin with its rule edits; that candidate must be valid. A re-pin that
removes or changes an included element anything references is classified
breaking and needs breaking-change acceptance.

### 2.8 Verbalization (MD9)

`gnd verbalize` verbalizes the composition. Include-bearing models get one
header line per include (`Includes <id> (<path>, sha256 <first 12>)`) and
otherwise unchanged text; models without includes are byte-identical.

## 3. Dependencies and artifact homes

```
MC1 ──┬──> MC2 ──┐
      └──> MC3 ──┴──> MC4 ──> close
```

MC2 and MC3 both need MC1's loader, provenance table and guards, and touch
disjoint files: discover and ILP candidate rendering belong to MC3 (they are
proposal writers), every other §1.3 route to MC2.

| Artifact | Home |
|---|---|
| `includes`, `fact_type_constraints`, version 5 | `src/gnd/schema/orm-meta.schema.json` and its sync-pinned skill copy |
| Resolution, composition, provenance, the guard predicate | new private module `src/gnd/model/_includes.py`, called from `load_model` / `_load_model_no_follow` and a new `load_model_bytes_composed(data, *, source, root)`; assigned in `tools/gnd_layers.json` and the component index (`model.loading`) |
| Typed size refusal | `src/gnd/artifacts.py` (subclass of `ArtifactError`) |
| Provenance side table, `includes` field, JSON serialization omission | `src/gnd/documents.py` `Model` |
| Reference version guard | `src/gnd/model/__init__.py` `validate_declarations` |
| Identities | `src/gnd/values.py` (unchanged functions; MC1 measures) |
| Normative prose | `src/gnd/skills/gnd-orm-core/references/representation-format.md`, new section "Model includes (version 5)" |
| Route guards (MC1), route support (MC2) | each admission point in the MC1 activation inventory |
| `repin-include`, included-element refusal, analysis-only preview, snapshots | `src/gnd/evolve/` (MC3) |
| Candidate rendering of the including file only | `src/gnd/discover/output.py`, ILP service (MC3) |
| End-to-end fixture | `tests/fixtures/mc-vocabulary/` (MC3) |

## 4. Phases, deliverables, named criteria

### MC1: contract, loader, guards, validate and check (about 450 source, 800 test lines)
- MC1-C1: `load_model(path)` composes; `gnd validate` and `gnd check` (text
  and JSON) on an include-bearing model agree with its flattened twin on exit
  code and on every field outside the published allowlist; allowlisted fields
  (path, digests, identities, version) are asserted separately (r1 P9).
- MC1-C2: one hostile-input case per §2.5 reason through `load_model`,
  `gnd validate` and `gnd check`, text and JSON, each exit 3 with its
  `rule_id`; direct hostile-shape tests of each new function (declarations
  parser, composer) over arbitrary JSON, including non-UTF-8 bytes, missing
  fields, malformed hashes and empty declarations (r1 P5, P12).
- MC1-C3: one published resolution order, phase by phase across all includes
  (all declarations, then all paths, then all reads, ...); compound-fault
  cases assert the winning reason and that later work was not called (r1 P3).
- MC1-C4: a scaling test over increasing composition workloads with a
  predeclared ratio criterion and a quadratic mutant control over the merge
  and collision layer (r1 P14). Any new aggregate input limit is MD14.
- MC1-C5: the census (r1 P15): every tracked `*.orm.yaml` and `*.orm.json`
  (`git ls-files`, counts published), split into models that load and expected
  refusals; for loaders, `model_dump`, `model_dump_json`, `_model_digest`,
  `model_identity`, `reference_model_digest` and `gnd validate --identity`
  equal to values recorded at main `459ca8d2`; for refusals, the same rule ids
  (r1 P10).
- MC1-C6: `load_model_bytes` on an include-bearing document refuses
  `include:unresolved`; `load_model_bytes_composed` with a root composes and
  binds references.
- MC1-C7: version-5 reference populations, including ownership of included
  base fact types, bind and check through both the path and composed-bytes
  routes; operation effects on reference-owned included fact types refuse as
  today (r1 P4).
- MC1-C8: `fact_type_constraints` places an acyclic ring and a mandatory
  constraint on included fact types; check matches the twin; an entry naming
  an own or unknown fact type refuses (r1 P1).
- MC1-C9: a branch-to-test matrix over every admitted section: own
  operations, derivations and subtypes that cross the include boundary,
  `rejected_proposals`, deontic-note order, `model_id` and `source`
  precedence (r1 P12, P18).
- MC1-C10: the activation inventory (r1 P16): one row per direct-bytes
  admission point in §1.3 plus any the spec finds; each refuses an
  include-bearing input with `include:unsupported-route`, exit 3, before
  output, through one shared predicate in `_includes.py`, with a case per row.
  PyRel runtime admission and the compose API route are rows.

### MC2: consumer support (about 250 source, 400 test lines)
- MC2-C1: the spec re-reads every MC1 guard row and decides `supports` (guard
  removed, behaviour case) or `refuses` (guard kept). No row is blank.
- MC2-C2: tempdir-copy routes never run on a copy without its included files.
- MC2-C3: `gnd verbalize` per MD9; byte-identical for include-free models.
- MC2-C4: codegen and conformance: currency is claimed only after the
  included bytes are verified in the same run (rule 0.5), shown by a case where
  the vocabulary changes under an unchanged includer; or the route stays
  refused (spec decides, owner rules) (r1 P8).

### MC3: evolve, re-pin and proposal writers (about 400 source, 600 test lines)
- MC3-C1: add/modify/rename/delete on an included element refuses
  `evolve:included-element`; on an own element (including a
  `fact_type_constraints` entry) works as before.
- MC3-C2: `repin-include` per MD12 and MD13: snapshots retained in proposal
  evidence; analysis-only preview for an invalid new composition; breaking
  classification; staging, CAS publication and recovery for a valid one;
  the live included file re-verified immediately before the CAS; a vocabulary
  change between preview, apply, publication and finalization refuses (r1 P6,
  P7, P8).
- MC3-C3: every written includer, from evolve, discover, ILP and interrupted
  operation recovery, keeps its `includes` declarations, contains only owned
  elements, contains no copied vocabulary definition and recomposes; a
  deliberately flattened candidate is refused (r1 P17).
- MC3-C4: the issue's scenario end to end on `tests/fixtures/mc-vocabulary/`:
  vocabulary v1 + rules validate and check; vocabulary v2 at a new path
  removes a fact type a rule uses; the includer still loads against v1; the
  re-pin preview is analysis-only and names the broken rule; the combined
  re-pin plus rule edit publishes and checks.

### MC4: documentation and skills (about 0 source, 40 test lines)
- MC4-C1: `representation-format.md` section is the one home; `gnd-orm-core`,
  `gnd-model-evolve`, `gnd-model-from-text` (vocabulary-file authoring) and
  the CLI reference cite it, with no second normative copy.
- MC4-C2: the vocabulary-file contract a shipping tool follows (what to
  generate, versioned paths per MD12, how a project pins and re-pins), with
  the MC3 fixture as its example.
- MC4-C3: doc-sync and skill-structure tests pass.

### Close
Close record; open-question sweep; full suite against the merge-base run;
closes issue 95.

## 5. Documentation, skill and compatibility surfaces

- Meta-schema and its sync-pinned copy (MC1).
- `representation-format.md` (MC1 writes the normative section; MC4 the rest).
- Skills: `gnd-orm-core`, `gnd-model-evolve`, `gnd-model-from-text`; any skill
  whose script parses models itself (`validate_model.py`,
  `verify_migration.py`) is an MC1 guard row and an MC2 decision.
- Compatibility: models without `includes` are unchanged (predicate 4); an
  older gnd refuses a version-5 file at load (version enum and
  `extra="forbid"`), so no silent misreading by old readers.

## 6. Risks and required controls

| Risk | Control |
|---|---|
| A consumer treats the including file alone as the model | rule 0.2; MC1-C10 guards from the first commit; MC2-C1 no blank row; MC2-C2 |
| A recorded digest or serialization moves for an include-free model | rule 0.3; MC1-C5 census over YAML and JSON, `model_dump_json` included |
| Two resolvers drift | rule 0.1; one module, imported by name; layer map |
| A freshness claim made over unverified included bytes | rule 0.5; MC2-C4; MC3-C2 re-verification before the CAS |
| Evolve or a proposal writer flattens the includer | rule 0.4; MC3-C3 asserts on the written includer, with a flattened negative control |
| The old vocabulary is gone at re-pin | MD12 versioned paths or supplied snapshot; retained evidence snapshots |
| Project rules cannot attach to included fact types | MD10 `fact_type_constraints`; MC1-C8 |
| Included source metadata silently changes validation | MD16; MC1-C9 both mode directions |
| A symlinked or escaping include path | reuse of the reference binder's confinement; MC1-C2 cases |
| Quadratic collision or merge work | MC1-C4 scaling test with a quadratic mutant |
| Scope creep into nested includes or overrides | MD3, MD5; §7 |

## 7. Out of scope

- The dev-tools runner (`rules_check.py`) and generating the vocabulary file
  from exported facts: another repository. MC4 documents the contract it
  follows.
- Nested includes, overriding or removing an included element, partial
  includes (taking a subset of a file), and remote or package-resolved
  includes.
- A new report version, unless a spec proves one is needed and the owner
  rules it in.
- Changing the legacy `repr` model digest (issue 111's successor work).
- Multi-file atomic writes.

## 8. Execution, approval and review protocol

`auto=false`. Each phase: spec, owner gate, implement, focused gate, one
independent reviewer in a different tool (Codex), refactoring review, record,
commit on a topic branch, PR. Merge is the owner's. The plan-review bar is the
maintained panel (project.md); MD0 ruled one Codex reviewer for this plan.

## 9. Per-phase verification story

| Phase | Focused gate (exact files in each spec) | Affected consumers |
|---|---|---|
| MC1 | new MC1 tests + `tests/test_schema_sync.py`, model validation, identity, reference-population and evolve-loading tests, and each guarded route's suite | every loader caller; recorded identities |
| MC2 | new MC2 tests + the consumer suites of each row | export, codegen, conformance, recovery, exp, witness, batch |
| MC3 | new MC3 tests + evolve, discover and ILP suites | evolve evidence readers, linked-project conformance |
| MC4 | doc-sync and skill-structure tests | packaged skills |
| close | full suite vs the merge-base run (main `459ca8d2`) | — |

The merge-base full suite and the MC1-C5 census baseline are recorded on
beast-3 at main `459ca8d2` before MC1 changes code. Exact test file names are
left to each spec, which reads them at its own baseline.

## 10. Owner decisions and open questions

| ID | Question | Readings and cost | Proposal |
|---|---|---|---|
| MD0 | Review this plan before the gate? | (a) one reviewer (Codex); (b) the maintained panel | **Ruled (o, 2026-11-09): (a)** ("Codex review", answering "How should plan r1 be reviewed before the gate (MD0)?") |
| MD1 | Field and shape | (a) `includes:` list of `{id, path, sha256}`, at most 8; (b) a single `extends:` entry. A later widening of (b) is a schema change | (a) |
| MD2 | Version | (a) new version 5 for `includes`, as version 4 was for references; (b) an optional field on version 4. Old readers refuse both at load | (a) |
| MD3 | What an included file may contain | (a) standalone-valid model with object types, fact types, constraints, deontic notes only, depth one; (b) also operations and references; (c) also nested includes | (a) |
| MD4 | Do the included file's constraints apply? | (a) yes, read-only; (b) no. Under (b) a shipped mandatory or uniqueness constraint silently stops being checked | (a) |
| MD5 | Override | (a) none: any duplicate id refuses; (b) the includer may restate an included element, which needs merge semantics per kind | (a) |
| MD6 | Identity | (a) no new identity function, per §2.4, measured in MC1; (b) a new composed identity field in reports, which is a new report version | (a) |
| MD7 | Routes that cannot resolve | (a) refuse with `include:unsupported-route`, exit 3, as references do; (b) support every route in this milestone, roughly doubling MC2 | (a), with MC2 supporting the routes its spec shows are cheap |
| MD8 | Vocabulary updates | (a) an evolve operation `repin-include` with blast radius; (b) hand-edit the hash and rerun `validate`, with no impact review | (a) |
| MD9 | Verbalization | (a) composition text plus one header line per include; (b) composition text only; (c) own elements only, which is not a model verbalization | (a) |
| MD10 (r1 P1) | How the includer places inline-only constraints (ring, mandatory, internal uniqueness) on included fact types | (a) a new top-level section `fact_type_constraints: [{fact_type, constraints}]`, valid only with `includes`, merged inline at composition, owned by the includer; (b) admit those constraint kinds at top level with a `fact_type` field in every model, a wider schema change touching every constraint family's placement; (c) let the includer restate the fact type, which contradicts MD5 | (a) |
| MD11 (r1 P2) | May an include-bearing file omit `object_types` and `fact_types`? | (a) yes, both optional when `includes` is present; (b) required but may be empty lists | (a) |
| MD12 (r1 P6) | Where the old vocabulary bytes come from at re-pin | (a) versioned paths by contract, plus a supplied, digest-verified `--previous-include` when the old file is gone, plus snapshots retained in evolve evidence; (b) evolve keeps a snapshot of every included file at every publication, so the old bytes are always in evidence, at the cost of a new standing evidence artifact; (c) re-pin without an old composition, reporting only what the new composition breaks | (a) |
| MD13 (r1 P7) | An invalid re-pin candidate | (a) analysis-only preview, nothing staged, then a combined valid proposal; (b) a new evidence kind for staged invalid candidates, refused at publication, which changes every evidence reader | (a) |
| MD14 (r1 P14) | A new aggregate cap on composed declarations? | (a) none; rely on the 32 MiB set cap and the scaling test; (b) a cap such as 100,000 composed declarations, a new input limit | (a), unless MC1's scaling test shows superlinear cost |
| MD15 (r1 P16) | When routes become safe | (a) MC1 ships the guards for every admission point; (b) MC1 and MC2 merge to main together, so `includes` is never admitted with unguarded routes | (a) |
| MD16 (r1 P18) | Effective `source` across includes | (a) the includer's `source` governs; an included file may not be in unattended mode; included `source` is kept per include in provenance; (b) unattended included files allowed, with their documents and spans validated against their own `source`, a second validation context; (c) refuse any included `source` | (a) |

Open question: the project hook says both "There is no component index in
this repository" (§"What these skills are here") and that the index lives in
`dev/components/` (§"Component index"). The index exists; this plan follows
the later section. The hook is the owner's file; the conflict is reported,
not edited. The index review reports 31 descriptions older than their code,
including `model.loading` and the `evolve.*` entries this milestone touches;
an index review (components skill, Review mode) is offered before MC1 relies
on it.

## 11. Review of r1: triage

All eighteen findings were checked against the source before acceptance:
P1 (`$defs.inline_constraint`, `examples/rule_check/model.orm.yaml:14`), P4
(`model/__init__.py:499`), P5 (`payloads.py:121`), P7 (`evolve/models.py:675`),
P10 (`model_dump_json` not overridden, probe), P13 (`artifacts.py:583-594`),
P14 (no `maxItems`), P16 (`api.py:980`, `pyrel_runtime.py:990`) and P18
(`_unattended.py:169`) were re-read or re-probed here; the others were
accepted on the reviewer's cited lines after reading them.

| ID | Accurate? | Disposition in r2 |
|---|---|---|
| P1 | yes | MD10, O18, §2.1, §2.3, MC1-C8, predicate 2 |
| P2 | yes | MD11; spec order validates declarations before layer 1 |
| P3 | yes | MC1-C3; one order, phase by phase, compound-fault cases |
| P4 | yes | O19; MC1-C7 |
| P5 | yes | §2.5 refusals are `ModelValidationError` issues; MC1-C2 |
| P6 | yes | MD12; MC3-C2, MC3-C4 |
| P7 | yes | MD13; O20; MC3-C2 |
| P8 | yes | rule 0.5; §2.4 scope; MC2-C4; MC3-C2 |
| P9 | yes | predicate 1 allowlist; MC1-C1 |
| P10 | yes | rule 0.3; MC1-C5 includes `model_dump_json` |
| P11 | yes | §2.3 structural-address provenance; §2.6 |
| P12 | yes | MC1-C2 direct tests; MC1-C9 matrix |
| P13 | yes | §2.1 typed size refusal |
| P14 | yes | MC1-C4; MD14 |
| P15 | yes | MC1-C5 census definition |
| P16 | yes | rule 0.2; MD15; MC1-C10 |
| P17 | yes | rule 0.4; MC3-C3 |
| P18 | yes | MD16; O21; MC1-C9 |
