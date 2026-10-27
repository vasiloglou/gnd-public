---
name: gnd-codegen
description: Turns an ORM model into a runnable plain-Python agent project with `gnd codegen MODEL --out DIR`, then writes the EXTENSION half — the architecture declaration, domain notes, and dependency list — that regeneration is guaranteed never to overwrite. Use when asked to "generate an agent from a model", "run gnd codegen", "scaffold a GND project", "model to code", or to regenerate a project after the model changed. Regeneration is idempotent and refuses rather than overwrites — a hand-edited derived file and an unmanaged file at a derived path both exit 11 with nothing destroyed. Not for checking whether a generated project has drifted from its model (that is the conformance command, and a green result says nothing about your extension code), not for authoring the model itself (gnd-model-from-text), and not for extracting a population from a document (gnd-extract).
---

# GND Codegen

## Summary

**What:** one `model.orm.yaml` becomes a project you can run. `gnd codegen` emits the deterministic half — one constructor tool per asserted or legacy-opaque fact type, no constructor for a structured-derived fact type, the four-file artifact bundle, and a `SKILL.md` for the agent that will run the generated project. **You write the extension half**: the architecture declaration, domain notes, and dependency list. Nothing you write is ever regenerated over.

| You write | A validator discharges it |
|---|---|
| `references/gnd-<model>-notes.md` (domain guidance) | nothing — it is prose, and prose is not digest-gated (see [Limits](#limits)) |
| `pyproject.toml` (your dependencies) | your own build tooling |
| `architecture.contract.yaml` (declared structure and runnable surface) | the loader defined by [`references/architecture-contract.md`](references/architecture-contract.md); static checks and execution remain separate claims |
| the population your generated agent produces | `gnd verify MODEL population.json` |
| nothing at all — the derived surface | `gnd codegen` itself; every derived file is digest-recorded |

Skill prose explains; validators discharge. If you find yourself reasoning about whether the generated tree is still correct, re-run the command and read its exit code instead.

**When to use:**
- A validated model needs to become a runnable agent project
- The model changed and the generated code has to catch up
- You are writing the domain notes or the dependency list for a generated project

**When NOT to use:**
- Checking whether an already-generated project has drifted from its model — [`../gnd-conformance/SKILL.md`](../gnd-conformance/SKILL.md)
- Building the conceptual model in the first place — [`../gnd-model-from-text/SKILL.md`](../gnd-model-from-text/SKILL.md)
- Changing the model this project was generated from — [`../gnd-model-evolve/SKILL.md`](../gnd-model-evolve/SKILL.md)
- Extracting a population from a document — [`../gnd-extract/SKILL.md`](../gnd-extract/SKILL.md)
- Rendering a document from a population — [`../gnd-render-doc/SKILL.md`](../gnd-render-doc/SKILL.md)
- Looking up the ORM YAML spec, the population interchange format, or the exit bands — [`../gnd-orm-core/SKILL.md`](../gnd-orm-core/SKILL.md) and [`../gnd-orm-core/references/population-format.md`](../gnd-orm-core/references/population-format.md)

**Required reading before your first run:** [`references/codegen-contract.md`](references/codegen-contract.md) — the emitted layout with per-file ownership, the six file states, the `--force` rule, and the exit-band table. When you author the architecture declaration, use its one format home: [`references/architecture-contract.md`](references/architecture-contract.md).

## Workflow

### 1. Validate the model first

```
gnd validate model.orm.yaml
```

Codegen refuses a model that does not load, and it refuses one more thing a validated model can still contain: two ids that sanitize to the same Python symbol (`import` and `import_`). Both exit **3**, because the remedy is in the model — rename one id.

Python keywords are legal ORM identifiers. `id: class`, `id: import`, `role_name: from` all pass `gnd validate` at exit 0, and codegen maps them to `class_`, `import_`, `from_` so the emitted code parses. You do not need to avoid them.

### 2. Generate

```
gnd codegen model.orm.yaml --out my-project/
```

The layout, and who owns each file:

| Path | Ownership | What it is |
|---|---|---|
| `<package>/__init__.py` | derived | re-exports every emitted constructor tool |
| `<package>/tools.py` | derived | one constructor per asserted or legacy-opaque fact type; none for a structured-derived fact type. Each role line of a docstring carries its object type's description `summary`, when the model gives one |
| `artifacts/<stem>.projection.schema.json` | derived | the shape-only schema a population must satisfy |
| `artifacts/<stem>.verbalization.txt` | derived | the constraint-blind model rendering |
| `artifacts/<stem>.applicable.json` | derived | which fact types are measurable |
| `artifacts/<stem>.artifacts.json` | derived | digests and the header template |
| `SKILL.md` | derived | the generated agent's own skill document |
| `architecture.contract.yaml` | **extension** | **yours.** Declared project structure; see the [format reference](references/architecture-contract.md) |
| `test_architecture_smoke_<package>.py` | **extension** | **yours.** Three lines that hand every smoke row in your contract to `gnd.archsmoke`; see the [format reference](references/architecture-contract.md) |
| `references/<skill>-notes.md` | **extension** | **yours.** Domain guidance |
| `pyproject.toml` | **extension** | **yours.** Dependencies |
| `.gnd-codegen.json` | the record | model digest + per-file digest + ownership |

**Derived means CODE-EMITTED.** That is not a style rule, it falls out of the digest: an LLM-authored file is not byte-reproducible, so it cannot be digest-gated. Anything you or any agent writes is an extension by definition, and it lands in an extension file.

**The constructor boundary is deliberate.** A structured `derivation_rule`
computes a fact extension, so codegen does not emit a function that lets an
agent construct those facts as though they were asserted inputs. The population
claims the derived rows and `gnd check`/`gnd verify` verifies that claim. A
legacy string `derivation_rule` keeps its constructor for backward-compatible
pre-v5 behavior; the string remains opaque and unchecked. Codegen and
conformance share the same structured-rule predicate so their expected surfaces
cannot disagree.

### 3. Write the extension half

Open `references/<skill>-notes.md` and write what the generated agent needs and the model cannot say: domain vocabulary, worked examples, the traps a reader of this model falls into. Add your dependencies to `pyproject.toml`. Fill in `architecture.contract.yaml` using the [architecture-contract reference](references/architecture-contract.md); its `smoke` rows run under pytest through the emitted `test_architecture_smoke_<package>.py`.

None of these four extension files is ever rewritten. `gnd codegen` creates them once and then leaves them alone, permanently, with or without `--force`.

**Then implement — one thin, user-visible slice at a time.** Extension work is ordinary software work in files you own: implement the slice, run the consuming repository's dependency and build checks, write and run focused tests proportionate to the surface you changed, smoke-test the runnable path once, and ship through that repository's ordinary release process. `gnd verify` enters when there is a population to check; it does not replace those checks (see [Limits](#limits)).

### 4. Regenerate when the model changes

```
gnd codegen model.orm.yaml --out my-project/
```

Re-running is **idempotent**: over an unchanged model it performs zero writes and every hash stays identical. Over a changed model it rewrites the derived files and leaves your extension files untouched.

Re-running **refuses rather than overwrites** where the two rules conflict:

| What it found | Exit | What happened |
|---|---|---|
| everything current | 0 | zero writes |
| derived files stale, or deleted | 0 | rewritten / restored |
| a derived file you hand-edited | **11** | refused; your bytes are untouched |
| a file GND never placed at a derived path | **11** | refused; nothing destroyed |
| an occupied directory with no `.gnd-codegen.json` | **11** | refused; nothing destroyed |

`--force` overwrites the derived files in the 11 rows. It never touches an extension file and never touches a path outside the generated layout, so unrelated work sitting in the same directory is safe either way.

**If you meant to keep an edit to a derived file, move it into an extension file.** A derived file is regenerated from the model by definition; the durable place for a change is either the model or your extension half.

### 5. Optional next steps — each emits its own separate claim

Neither step below runs because codegen ran, and neither is required to consider generation finished. You choose one, invoke it yourself, and read its evidence on its own terms.

| Next step | Command | The claim it emits, and what it is not |
|---|---|---|
| **Standalone conformance check** — does this tree still agree with the model? | `gnd conformance model.orm.yaml my-project/` — [`../gnd-conformance/SKILL.md`](../gnd-conformance/SKILL.md) | a drift finding over the **derived surface only**. It is invocable without codegen and says nothing about your extension code. It is not a verifier verdict |
| **Data-driven session** — does the generated agent's output satisfy the model? | `gnd exp` over a synthetic input/output contract | a session run/attempt record carrying `gnd verify` verdicts over real output. It is not a conformance result: conformance reads bytes and `ast`, a verdict reads a population |

**Do not merge the two.** A green conformance result and a passing session are unlike claims over unlike evidence, and no payload in GND presents them as one score (D-24). They may cite one another by digest; they never combine. A tree can be perfectly conformant and produce populations that fail every constraint, and a tree can pass a session while a derived file has silently drifted.

**And neither one changes the model.** If the session or the conformance run tells you the *model* is wrong, that is an owner-authorized evolution — [`../gnd-model-evolve/SKILL.md`](../gnd-model-evolve/SKILL.md) — and you come back here to regenerate afterwards, deliberately. Nothing regenerates automatically, in either direction.

## The rule about provider clients (G-02)

**The no-provider-client rule binds GND's own package, not your generated project.**

`gnd` itself never imports `anthropic`, `openai`, `httpx` or any other client, and a test scan enforces that. The template `gnd codegen` emits ships none either — so a fresh generated project runs in CI with zero network and no API key, and the agent reading the generated `SKILL.md` is the only place a model is ever called.

**Your project is yours.** If you want a provider client in it, add one. It goes in `pyproject.toml`, which is an extension file, and it is your code from that moment. Nothing in GND forbids it and nothing in GND will remove it.

## Limits

**A conformance pass says nothing about your extension code.** When the conformance check reports green, it has established exactly two things: every derived file matches its recorded digest, and the recorded model digest matches the model on disk. That is "the derived surface is current and unedited". It is **not** "the code is correct", and it is not any statement at all about `references/`, `pyproject.toml`, or anything else you wrote — extension code is unexamined by construction, because prose and hand-written code are not byte-reproducible and cannot be digest-gated.

The GND claim that exercises extension behavior is the runtime verifier over the agent's actual output: `gnd verify MODEL population.json`. That claim is deliberately narrow — it checks population behavior against the model, and it does not replace dependency and build checks, focused unit or integration tests, or a smoke run over the extension code you wrote. Conventional software verification stays yours, proportionate to the extension surface that changed; GND neither generates nor gates it.

**The record cannot record itself.** `.gnd-codegen.json` holds a digest for every file it manages and cannot hold one for itself. So a digest comparison detects a unilateral edit to a derived file, and does not detect an edit to a derived file that is made *together with* an edit to its manifest entry. That is an integrity bound, not tamper evidence. `gnd doctor` carries the identical limit, and the bound is published as data rather than left in prose.

**The generated banner deters; the digest detects.** Every derived file opens with `# Code generated by gnd codegen …; DO NOT EDIT.` A banner can always be forged and nothing checks it as a gate. The digest is the detection.

## Report

State, in your reply: the command you ran and its exit code verbatim, the derived files written and the ones skipped with their state, the extension files you authored, and — if you saw exit 11 — which file was refused and what you did about it. Do not translate an exit band into an adjective of your own.

## Record and commit

Routine fast-lane generation needs no station record. When this run is evidence-lane work -- a generation worth milestone evidence, or an exit-11 refusal that taught something -- append the record `NNN-codegen.md` and commit `feat(codegen): ...` (a recorded refusal is `docs`, not a silent retry) with the exit verbatim, staging by explicit path the generated project including `.gnd-codegen.json`, the extension files you authored, and the record, only on the user's explicit go-ahead. A shipped slice worth milestone evidence records `NNN-slice.md` and commits `feat(slice): ...`, staging by explicit path the changed extension files and the record, only on the user's explicit go-ahead. The lane rule, record shape, staging discipline, and commit grammar have one home: [`../gnd-orm-core/references/milestone-record-format.md`](../gnd-orm-core/references/milestone-record-format.md). If `.gnd-planning/` is absent, offer [`../gnd-new-project/SKILL.md`](../gnd-new-project/SKILL.md) first. The record and the commit are the driving agent's acts; `gnd` itself never reads or writes `.gnd-planning/` and never touches git.


## Calendar-day fragment (v7.1)

Follow [calendar-day terms](../gnd-orm-core/references/representation-format.md#calendar-day-terms-v71) for model version 3, Duration roles, tagged literals and guarded date functions.
This workflow currently refuses temporal models at exit 3 before publishing output. Use the reference above to identify the supported ordinary check/transition route; a route is an explicit user-selected handoff.


## Fixed reference populations

Codegen currently refuses models carrying `reference_populations` at exit 3 before publishing output. Generated catalog copying is outside this contract.

The shared format is [version-4 reference populations](../gnd-orm-core/references/representation-format.md#fixed-reference-populations-version-4).
