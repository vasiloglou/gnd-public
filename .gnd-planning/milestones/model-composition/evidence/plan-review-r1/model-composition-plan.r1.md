# Model composition

**Status: r1, draft, awaiting the owner's plan gate. Not reviewed:** no plan
review has run over these bytes (MD0 asks which instrument reviews it).
`auto=false`. Authoring this plan approves nothing.

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
project owns: constraints, and possibly object types, fact types and
operations of its own. One id namespace across both. A tool that ships a
vocabulary to many projects (the case in the issue: a fact export with nine
fact types such as "Component uses Component") then updates the vocabulary
file without touching the project's rules, and the project keeps a real model
file it can pass to `gnd validate`, `check`, `verbalize` and `evolve`.

## Completion predicates

The milestone is complete when, on main after merge:

1. A model with `includes:` (MD1, MD2) loads through `load_model(path)`: the
   included file is read beneath the model's parent with no symlink, its raw
   sha256 is checked, and the loaded `Model` is the composition. `gnd validate`
   and `gnd check` exit exactly as they do on the hand-flattened equivalent
   (MC1-C1).
2. Every refusal of an include-bearing input is exit 3 with a distinct,
   value-free reason, in a pinned order (MC1-C2, MC1-C3).
3. No existing model's loaded content, digest, identity, report bytes or
   recorded fixture value moves (MC1-C5, measured over the whole suite).
4. Each of the direct-bytes consumers inventoried in §1.3 either supports an
   include-bearing model or refuses it before work with exit 3 and a named
   reason; none silently treats the including file alone as the model (MC2).
5. `gnd evolve` edits only the including file, refuses an operation on an
   included element, and re-pins an include after a vocabulary update with
   a full blast-radius review of what the new vocabulary breaks (MC3).
6. The issue's scenario runs end to end on a committed fixture: a shipped
   vocabulary, a project rules file, a vocabulary update that removes a fact
   type a rule uses, and the re-pin that reports it (MC3-C4).
7. The normative contract has one home (`representation-format.md`, new
   section "Model includes (version 5)"); skills and docs cite it (MC4).
8. Each phase has an approved spec, a record with verbatim focused-gate output
   and one independent reviewer; the close record disposes every open
   question and closes issue 95.

## 0. Binding design rules

The six standing design rules of
[project.md](../../../../.codex/skills/process-phase/references/project.md)
bind every phase. Milestone rules:

1. **Composition happens once, in the loader.** One function resolves
   includes and builds the composed document; every consumer receives the
   composed `Model`. No consumer re-implements resolution (rule 4 of
   project.md, rule 5 for prose).
2. **No silent half-models.** A route that cannot resolve includes refuses;
   it never loads the including file alone or a tempdir copy without its
   included file.
3. **Frozen variants.** Models without `includes` keep every byte of every
   output and every recorded digest. No new report version unless a phase
   spec proves one is needed and the owner rules it in.
4. **The including file is the only file GND writes.** The included file is
   input, never a write target, for evolve, discover, ILP or any repair.
5. **Measure, don't assert** (inherited, rule-check-followups §0.2). The
   identity claims of §2.4 are measured over the committed fixtures before
   they are planned against, and every refusal has a case observed red first.
6. **Stop rule (size).** A phase pauses for the owner past 1.5 times its
   estimate.

## 1. Scope, sources and authority

### 1.1 Obligations

| # | Obligation | Source | Kind | Owner |
|---|---|---|---|---|
| O1 | One model takes object types and fact types from another file | issue 95, "Asked for" | request | MC1 |
| O2 | Bound by digest like a reference population | issue 95 | request | MC1 (MD1) |
| O3 | Including file adds constraints, possibly fact types | issue 95 | request | MC1 (MD4) |
| O4 | `gnd validate` and `gnd check` resolve it | issue 95 | request | MC1 |
| O5 | Ids stay in one namespace | issue 95; `representation-format.md` "One id namespace" | request; existing rule | MC1 |
| O6 | The project owns a real model file usable with `gnd evolve` and `gnd verbalize` | issue 95, "Workaround today" | request | MC2 (verbalize), MC3 (evolve) |
| O7 | A vocabulary update must not overwrite the project's rules and must not leave the next check ill-formed | issue 95, "Why" | request | MC3 (re-pin, MD8) |
| O8 | The runner keeps generating the vocabulary file from exported facts | issue 95, last sentence | boundary | out of scope (§7); MC4 documents the vocabulary-file contract |
| O9 | GR-D4 is its own milestone | rule-check-adoption plan §1, §7; close record | owner ruling 2026-11-06 | this plan |
| O10 | Six standing design rules | project.md | standing | every spec §4 |
| O11 | Component index changes in the same commit as code; `components_index.py changed --base main --strict` before a PR | project.md "Component index" | standing | every phase |
| O12 | Dependency homes and import checks in `tools/gnd_layers.json`, allowance count zero | AGENTS.md "Refactoring dependency homes" | standing | MC1 (new home), every phase |
| O13 | Shared model queries through `ModelIndex`; family hooks in `constraint_families.FAMILIES` | AGENTS.md "Model queries" | standing | MC1 |
| O14 | Reference-bearing inputs: synth, codegen and older session contracts refuse them before publishing | `representation-format.md` "Fixed reference populations (version 4)" | precedent | MC2 (same pattern) |
| O15 | Evolve CAS is single-leaf, "no multi-file atomicity" | `evolve/service.py:2141`, `safefs.py` | constraint | MC3 (rule 0.4 makes it sufficient) |
| O16 | `ValidationIssue` has `path`, `message`, `rule_id`, `severity`; no file field | `errors.py:13` | constraint | MC1 (MC1-D3) |
| O17 | Branch and PR per phase; merge only with the owner's authorization | AGENTS.md "Pull requests are required" | standing | §8 |

### 1.2 Observed at `459ca8d2` (read, 2026-11-09)

| Fact | Where | Status |
|---|---|---|
| No include/extends/import mechanism exists; the 162 schema `$ref`s are internal | `schema/orm-meta.schema.json` | read |
| Meta-schema `version` enum is `[1,2,3,4]`; `operations` needs 2-4, `reference_populations` needs exactly 4 | `orm-meta.schema.json` `allOf` | read |
| Committed models: version 1 ×190, 2 ×69, 3 ×7, 4 ×10 | survey | read (survey) |
| `Model` is `frozen`, `extra="forbid"`: an older gnd refuses an unknown top-level key at load | `documents.py:24` | read |
| `load_model(path)` reads under a retained parent descriptor (`retained_root`, `O_NOFOLLOW`) and binds references with `_bind_at`; reference-free models keep a historical symlink route | `model/__init__.py:338-380` | read |
| Reference declaration validation, confined relative paths, raw-hash check, caps (32 files, 32 MiB, 10 MiB each) | `model/__init__.py:450-585` | read |
| `load_model_bytes` has 40 call sites in 16 modules; `load_model` 28 | grep | read |
| `src/gnd/composition.py` is population composition (`gnd compose`), not model composition | `composition.py:1` | read |
| `values._model_digest` is still `repr` of the dump; ROF4 accepts either it or canonical identity v2 via `model_identity_matches` | `values.py:179-196`, `:289`, `:304` | read |
| Evolve publishes the proposal's candidate text over the live file with `LeafIdentity(sha256=before)` | `evolve/service.py:2123-2148` | read |
| Discover and ILP render candidate models as JSON (comments lost) | `discover/output.py:99` | read (survey) |

### 1.3 Direct-bytes consumers (MC2's inventory; survey, to be re-read in the MC2 spec)

Routes that read or hash the model file themselves rather than receive a
loaded `Model`: evolve (`_load_model_document`, `_parse_model_text`, CAS),
recovery verify (tempdir copy), `gnd import rai-orm` (tempdir copy, rt
writer), export `render_pyrel` (embeds raw text as `MODEL_TEXT`),
`pyrel_runtime`, `pyrel_rules`, export applications (tempdir copies), Lean and
Souffle export (`model_raw_sha256`), witness service and io, discover, ILP,
batch, checking-service composition verify, codegen manifest and emit,
conformance currency, extract, fidelity and doccheck, measure, the exp session
family (`session.py` tempfile, `session_contract`, `session_replay`,
`session_judgments`), judgments, `api.py:1123`, two skill scripts
(`validate_model.py`, `verify_migration.py`), and examples. Counts of recorded
identities: raw-byte `model_sha256` in 32 src / 56 test / ~100 fixture files;
`model_digest` 27 / 67 / 223.

### 1.4 Authority

The owner's request (2026-11-09); issue 95; the owner's 2026-11-06 selection
that put GR-D4 in its own milestone. Approves no bytes.

## 2. Contract proposal and product behavior

All of this is proposed; the owner rules on MD1-MD9 (§10).

### 2.1 Declaration (MD1, MD2)

```yaml
version: 5
includes:
  - id: components-vocabulary
    path: vocab/components.orm.yaml
    sha256: <64 lowercase hex digits of the exact file bytes>
constraints:
  - id: no-cycle-in-uses
    ...
```

Exactly three fields per entry. At most 8 entries. Paths follow the reference
population rules exactly (confined POSIX relative, beneath the explicit model
parent, no symlink in root, ancestors or leaf, ≤32 components, ≤4096 chars).
One included file is at most 10 MiB, the set at most 32 MiB. The checks reuse
`_relative`, `retained_root` and `read_regular_bounded_at`; they are not copied.

### 2.2 What an included file is (MD3)

A complete, standalone-valid model file (`gnd validate` exits 0 on it alone)
with `object_types`, `fact_types` and optionally `constraints` and
`deontic_notes`. It declares no `includes`, `reference_populations`,
`operations` or `rejected_proposals`. Depth is one.

### 2.3 Composition (MD4, MD5)

The composed document is: the included files' object types, fact types,
inline and top-level constraints and deontic notes, in declaration order of
`includes`, followed by the including file's own entries. The including file
may add object types, fact types, constraints, operations,
`reference_populations` (reference ownership may name included base fact
types), `rejected_proposals` and deontic notes. It may not redeclare,
override or remove an included element: any id that appears twice anywhere
in the composition is refused (the existing `semantic:id-unique` rule, run
over the composed document, plus a distinct include-collision reason that
names both origins by include id). The composed document is then validated
by the unchanged two-layer validation.

Each composed element's origin (`includes[<id>]` or the including file) is a
private side table on `Model`, like `_compiled` (`documents.py:47-58`), so no
section a digest covers is written into.

### 2.4 Identity (MD6)

No new identity. Proposal, to be measured in MC1 before it is relied on:

- The raw-byte sha256 of the including file is already a complete content
  identity of the composition, because it embeds each included file's raw
  sha256. Codegen manifests, conformance currency and the evolve CAS keep
  hashing the including file alone, and a changed vocabulary is caught at
  load as an include hash mismatch before any of them run.
- `_model_digest`, canonical identity v2 and `reference_model_digest` are
  taken over the composed loaded content plus the `includes` declarations.
- For every model without `includes`, every identity is byte-identical
  (predicate 3).

### 2.5 Refusals (MD7)

Exit 3, input band, each with a distinct value-free reason. Proposed reason
spellings (MC1 spec fixes them literally): `include:declaration`,
`include:path`, `include:unreadable`, `include:size`, `include:hash-mismatch`,
`include:invalid-included-model`, `include:forbidden-section`,
`include:collision`, `include:unresolved` (bytes-only route with no root),
`include:unsupported-route` (MC2's refusing consumers).

### 2.6 Diagnostics (MC1-D3)

A validation issue inside an included element keeps its JSON path and is
prefixed with the origin: `includes[components-vocabulary]:$.fact_types[3]...`.
Only include-bearing models change spelling; `ValidationIssue` gains no field.

### 2.7 Evolve and re-pin (MD8)

Operations whose target element originates in an include are refused
(`evolve:included-element`). A new operation `repin-include` changes one
`includes[].sha256` (and optionally `path`). Its preview loads before and
after compositions and reports the blast radius the same way any evolution
does: elements the new vocabulary added, removed or changed, and every
constraint, operation, reference ownership or linked project the change
breaks. A re-pin that leaves the composition invalid is staged for review but
refused at publication, like any invalid candidate.

### 2.8 Verbalization (MD9)

`gnd verbalize` verbalizes the composition. Proposal: include-bearing models
get one header line per include (`Includes <id> (<path>, sha256 <first 12>)`)
and otherwise unchanged text; models without includes are byte-identical.

## 3. Dependencies and artifact homes

```
MC1 ──┬──> MC2 ──┐
      └──> MC3 ──┴──> MC4 ──> close
```

MC2 and MC3 both need MC1's loader and origin table and touch disjoint
files: discover and ILP candidate rendering belong to MC3 (they are proposal
writers), everything else in §1.3 to MC2.

| Artifact | Home |
|---|---|
| `includes` schema, version 5 | `src/gnd/schema/orm-meta.schema.json` (and its sync-pinned copies) |
| Resolution and composition | new private module `src/gnd/model/_includes.py`, called from `load_model` / `_load_model_no_follow` and a new `load_model_bytes_composed(data, *, source, root)`; assigned in `tools/gnd_layers.json` and the component index (`model.loading`) |
| Origin side table | `src/gnd/documents.py` `Model` private attribute |
| Identities | `src/gnd/values.py` (unchanged functions over composed content; MC1 measures) |
| Normative prose | `src/gnd/skills/gnd-orm-core/references/representation-format.md`, new section "Model includes (version 5)" |
| Route refusals and support | each consumer in §1.3 (MC2) |
| `repin-include`, included-element refusal | `src/gnd/evolve/` (MC3) |
| Candidate rendering of the including file only | `src/gnd/discover/output.py`, ILP service (MC3) |
| End-to-end fixture | `tests/fixtures/mc-vocabulary/` (MC3) |

## 4. Phases, deliverables, named criteria

### MC1: contract, loader, validate and check (about 300 source, 500 test lines)
- MC1-C1: `load_model(path)` composes; `gnd validate` and `gnd check` (text
  and JSON) on an include-bearing model exit and print as on its committed
  hand-flattened twin, except where §2.6 and §2.8 spell differently.
- MC1-C2: one hostile-input case per §2.5 reason through `load_model` and
  `gnd validate`, each exit 3, each observed red first.
- MC1-C3: the resolution order (declaration → path → read → size → hash →
  parse → included-model validation → forbidden sections → collision →
  composed validation → reference declarations) pinned by a source-order
  assertion where two refusals cannot otherwise be told apart.
- MC1-C4: a time-bound test over composition at the caps (8 includes, the
  entry maximum) proving it linear.
- MC1-C5: every committed model without includes: loaded dump, all four
  identities and `gnd validate --identity` output unchanged (whole-suite run
  plus a census over committed `*.orm.yaml`).
- MC1-C6: `load_model_bytes` on an include-bearing document refuses
  `include:unresolved`; `load_model_bytes_composed` with a root composes.
- MC1-C7: reference populations whose ownership names included base fact
  types bind and check.

### MC2: consumer sweep (about 250 source, 350 test lines)
- MC2-C1: the spec re-reads every §1.3 site and gives each a row:
  `supports` (with a case) or `refuses` (`include:unsupported-route`, exit 3,
  before any output is written, with a case). No row is blank.
- MC2-C2: tempdir-copy routes never run on a copy without its included file.
- MC2-C3: `gnd verbalize` per MD9; byte-identical for include-free models.
- MC2-C4: codegen and conformance on an include-bearing model: either
  supported with the currency claim of §2.4 shown by a case where the
  vocabulary changes, or refused (spec decides, owner rules).

### MC3: evolve, re-pin and proposal writers (about 300 source, 450 test lines)
- MC3-C1: add/modify/rename/delete on an included element refuses
  `evolve:included-element`; on an own element works as before.
- MC3-C2: `repin-include` preview, staging and CAS publication, writing only
  the including file; an interrupted re-pin resumes like any evolution.
- MC3-C3: discover and ILP proposals over an include-bearing model render
  the including file only; a proposal that would touch an included element
  is not emitted (or is emitted as rejected; spec decides).
- MC3-C4: the issue's scenario end to end on `tests/fixtures/mc-vocabulary/`:
  vocabulary v1 + rules validate and check; vocabulary v2 removes a fact type
  a rule uses; load refuses `include:hash-mismatch`; `repin-include` preview
  names the broken rule; after the rule is edited the re-pin publishes.

### MC4: documentation and skills (about 0 source, 40 test lines)
- MC4-C1: `representation-format.md` section is the one home; `gnd-orm-core`,
  `gnd-model-evolve`, `gnd-model-from-text` (vocabulary-file authoring) and
  the CLI reference cite it, no second normative copy.
- MC4-C2: the vocabulary-file contract a shipping tool follows (what to
  generate, how a project pins it), with the MC3 fixture as its example.
- MC4-C3: doc-sync and skill-structure tests pass.

### Close
Close record; open-question sweep; full suite against the merge-base run;
closes issue 95.

## 5. Documentation, skill and compatibility surfaces

- Meta-schema and its sync-pinned copies (MC1).
- `representation-format.md` (MC1 writes the normative section; MC4 the rest).
- Skills: `gnd-orm-core`, `gnd-model-evolve`, `gnd-model-from-text`; any skill
  whose script parses models itself (`validate_model.py`,
  `verify_migration.py`) is an MC2 row.
- Compatibility: models without `includes` are unchanged (predicate 3); an
  older gnd refuses a version-5 file at load (version enum and
  `extra="forbid"`), so no silent misreading by old readers.

## 6. Risks and required controls

| Risk | Control |
|---|---|
| A consumer treats the including file alone as the model | rule 0.2; MC2-C1 has no blank row; tempdir routes refuse (MC2-C2) |
| A recorded digest moves for an include-free model | rule 0.3; MC1-C5 census and whole suite |
| Two resolvers drift | rule 0.1; one module, imported by name; layer map |
| The raw-sha transitive-identity claim is wrong somewhere (a consumer hashes a different file) | measured in MC1, re-checked per row in MC2 |
| Evolve writes a flattened model, destroying the split | rule 0.4; MC3-C3 and a case that the included file's bytes are unchanged after every evolve |
| A symlinked or escaping include path | reuse of the reference binder's confinement; MC1-C2 cases |
| Quadratic collision or merge work under the cap | MC1-C4 time bound |
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
maintained panel (project.md); MD0 asks which instrument reviews this plan.

## 9. Per-phase verification story

| Phase | Focused gate (exact files in each spec) | Affected consumers |
|---|---|---|
| MC1 | new MC1 tests + `tests/test_schema_sync.py`, model loading, reference-population and identity tests | every loader caller; recorded identities |
| MC2 | new MC2 tests + the consumer suites of each row | export, codegen, conformance, recovery, exp, witness, batch |
| MC3 | new MC3 tests + evolve, discover and ILP suites | evolve evidence, linked-project conformance |
| MC4 | doc-sync and skill-structure tests | packaged skills |
| close | full suite vs the merge-base run (main `459ca8d2`) | — |

The merge-base full suite is run on beast-3 before MC1 changes code. Exact
test file names are left to each spec, which reads them at its own baseline.

## 10. Owner decisions and open questions

| ID | Question | Readings and cost | Proposal |
|---|---|---|---|
| MD0 | Review this plan before the gate? | (a) one reviewer (Codex), as the last two milestones did; (b) the maintained panel, the project's bar, paid | (a) |
| MD1 | Field and shape | (a) `includes:` list of `{id, path, sha256}`, at most 8; (b) a single `extends:` entry. (b) is enough for issue 95's case but a project combining two shipped vocabularies would need (a) later, and a later widening is a schema change | (a) |
| MD2 | Version | (a) new version 5 required for `includes`, as version 4 was for references; (b) an optional field on version 4. Old readers refuse both at load (`extra="forbid"`), so the exit is the same; (a) keeps feature detection by version consistent with the precedent | (a) |
| MD3 | What an included file may contain | (a) standalone-valid model with object types, fact types, constraints, deontic notes only, depth one; (b) also operations and references; (c) also nested includes. (b) and (c) multiply the resolution and evolve cases | (a) |
| MD4 | Do the included file's constraints apply? | (a) yes, read-only; (b) no, vocabulary only. Under (b) a shipped mandatory or uniqueness constraint silently stops being checked | (a) |
| MD5 | Override | (a) none: any duplicate id refuses; (b) the including file may restate an included element. (b) needs a merge semantics per element kind | (a) |
| MD6 | Identity | (a) no new identity, per §2.4, measured in MC1; (b) a new composed identity field in reports. (b) is a new report version | (a) |
| MD7 | Routes that cannot resolve | (a) refuse with `include:unsupported-route`, exit 3, as references do; (b) support every route in this milestone. (b) roughly doubles MC2 | (a), with MC2 supporting the routes the spec shows are cheap |
| MD8 | Vocabulary updates | (a) an evolve operation `repin-include` with blast radius; (b) the project edits the hash by hand and reruns `validate`. (b) has no impact review, which is what issue 95 asks to avoid | (a) |
| MD9 | Verbalization | (a) composition text plus one header line per include; (b) composition text only; (c) own elements only. (c) is not a model verbalization | (a) |

Open question: the project hook says both "There is no component index in
this repository" (§"What these skills are here") and that the index lives in
`dev/components/` (§"Component index"). The index exists; this plan follows
the later section. The hook is the owner's file; the conflict is reported,
not edited. The index review reports 31 descriptions older than their code,
including `model.loading` and the `evolve.*` entries this milestone touches;
an index review (components skill, Review mode) is offered before MC1 relies
on it.
