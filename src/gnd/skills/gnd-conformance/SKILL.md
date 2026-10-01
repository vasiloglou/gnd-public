---
name: gnd-conformance
description: Checks generated-project agreement with `gnd conformance MODEL DIR` and records the evidence a codegen experiment needs before close. Use for model-code drift checks, conformance runs, or committed conformance evidence. Four assertions cover recorded derived-file digests, model currency, the constructor surface (asserted and legacy-opaque fact types present; structured-derived constructors absent), and bounded static architecture observations. Green is structural only; it establishes no extension-file integrity, tool-body behavior, or derivation-semantic correctness. Not for generation (gnd-codegen), population verification (`gnd verify`), or model authoring (gnd-model-from-text).
---

# GND Conformance

## Summary

**What:** `gnd conformance MODEL DIR` answers one question — *does the code in `DIR` still agree with `MODEL`?* It reads bytes and parses source. It never imports the project, never writes anything, and never calls a model.

**Why it is a separate skill from `gnd-codegen`:** conformance is invocable **without** codegen. `gnd exp close` calls this contract to decide whether a codegen experiment may close, and a later phase calls the currency assertion from a third entry point entirely. A check that only the generator's own workflow could reach would be a check nothing else could reuse.

| You do | A validator discharges it |
|---|---|
| run `gnd conformance MODEL DIR` and read the exit band | the command itself |
| record `conformance.json` in a codegen experiment | `gnd exp close`, which refuses at **14** without it |
| decide what a green result licenses you to say | nothing — read [Limits](#limits) before you say it |

Skill prose explains; validators discharge. If you find yourself reasoning about whether a generated tree is still current, run the command and read its exit code.

**When to use:**
- After the model changed, to find out whether the generated project fell behind
- Before closing a `kind: codegen` experiment, to produce the evidence the close gate requires
- In CI, as the check that model-code drift is detected in the same commit it could first appear

**When NOT to use:**
- Generating or regenerating the project — [`../gnd-codegen/SKILL.md`](../gnd-codegen/SKILL.md)
- Checking a population against the model's constraints — that is `gnd verify`, and a green conformance result says nothing about it
- Authoring a model from a natural-language description — [`../gnd-model-from-text/SKILL.md`](../gnd-model-from-text/SKILL.md)
- Changing an existing model — [`../gnd-model-evolve/SKILL.md`](../gnd-model-evolve/SKILL.md)
- Recovering a model from a codebase that never had one — [`../gnd-model-from-code/SKILL.md`](../gnd-model-from-code/SKILL.md)
- Extracting a population from a document — [`../gnd-extract/SKILL.md`](../gnd-extract/SKILL.md)
- Looking up the ORM YAML spec or the population interchange format — [`../gnd-orm-core/SKILL.md`](../gnd-orm-core/SKILL.md)

**Required reading before your first run:** [`references/conformance-contract.md`](references/conformance-contract.md) — the four assertions with their roles, the payload's key set, the exit-band table, and the published limits in full.

## Workflow

### 1. Run it

```
gnd conformance model.orm.yaml my-project/
gnd conformance model.orm.yaml my-project/ --format json > conformance.json
```

Two arguments, both paths you supply. Nothing is read from inside the project to decide where to look.

### 2. Read the band, do not translate it

| Exit | What it means | What to do |
|---|---|---|
| **0** | every assertion ran and found nothing | read [Limits](#limits) before calling the project "fine" |
| **13** | drift — the payload names every affected file or model surface | usually `gnd codegen` again; read the findings first |
| **3** | the manifest or the model will not parse | the remedy is in the document, not in the code |
| **66** | no `.gnd-codegen.json`, or no model at that path | nothing was compared; this is **not** a passing result |
| **74** | the tree could not be read | says nothing about what is in it |

**66 and 3 are not conformance failures and not conformance passes.** No comparison happened. The payload reports `ran: false` on the assertions that could not run and a non-null `error`, precisely so a consumer cannot mistake "did not run" for "found nothing".

### 3. The four assertions, and which one carries the weight

| # | Assertion | What it compares | Role |
|---|---|---|---|
| 1 | **integrity** | each derived file's bytes against the digest the manifest recorded | exact, cheap, **corroborating** |
| 2 | **currency** | the model's bytes now against the digest recorded at generation | exact, cheap, **corroborating** — this one IS model-code drift |
| 3 | **structural** | the MODEL's constructor-bearing fact types, plus structured-derived constructor absences, against module-level functions on disk | **the gate that makes the check mean something** |
| 4 | **architecture** | authored modules, symbols, artifacts and entry points against static filesystem and AST observations | static and execution-free; binds only what the contract declares |

Assertions 1 and 2 are *self-referential*: each compares the generator's output against a digest the generator itself wrote. Both are green on a project that is 100 percent derived and 0 percent useful, because regenerate-and-diff passes whenever generation is deterministic — which it is, by construction.

Assertion 3 compares the model against the filesystem. Nothing it reads was written by the generator. A generator that emitted a syntactically perfect module containing no constructor tools is caught once per asserted or legacy-opaque fact type. Conversely, a constructor present anywhere for a structured-derived fact type is `derived-fact-type-constructed` drift: computed facts are claimed by a population and checked, not constructed by generated code.

Assertion 3 reads the tree with `ast.parse` and looks at **module level only**. A function nested inside another function, or sitting in a dead `if False:` branch, is not the public surface and does not satisfy a fact type.

This is structural agreement only. It establishes neither that a structured
derivation computes the right extension nor that its business rule is
semantically correct; those claims are outside conformance.

### 4. Record it in a codegen experiment

A `kind: codegen` experiment carries one obligation beyond the usual ones: a `conformance.json` beside its `SPEC.md` and `CONCLUSIONS.md`.

```
gnd conformance model.orm.yaml my-project/ --format json > EXP-001-something/conformance.json
gnd exp close EXP-001-something/
```

`gnd exp close` refuses at **14** when that file is absent, is not a valid conformance payload, reports any assertion as `ran: false`, or carries a non-empty `findings` array. **An absent measurement is not a passing one**, and a hand-written file that merely looks like a payload is refused by schema validation before its findings array is read.

The close gate does not read a pass-or-fail field, because the payload has none and never will: conformance publishes files, digests and drift, and a verdict summarizing them would be a second source of truth for a fact already in the data. The reader derives the rule.

## 5. Where a drift result routes — and where it does not

Exit 13 is a **finding**, never an instruction. This command writes nothing, and nothing downstream of it starts because it ran. Choose the destination deliberately:

| What the payload told you | Where it routes | The boundary the handoff keeps |
|---|---|---|
| the code fell behind a model that is right | [`../gnd-codegen/SKILL.md`](../gnd-codegen/SKILL.md) — regenerate | you invoke codegen; conformance never invokes it, and a drift finding is not permission to regenerate |
| the **model** is what has to change | [`../gnd-model-evolve/SKILL.md`](../gnd-model-evolve/SKILL.md) — one owner-authorized evolution | evolution's staged proposal, acceptance, CAS, and change record stay four claims (D-24). Nothing here authorizes a model edit, and evolution does not regenerate code as a side effect |
| this project never had a model to drift from | [`../gnd-model-from-code/SKILL.md`](../gnd-model-from-code/SKILL.md) — one-time recovery | **generated-project drift and brownfield recovery are different questions.** This command compares a tree against the `.gnd-codegen.json` that generated it; a project with no such record was never generated and cannot drift. 66 is that case, and 66 is not a conformance failure |
| you want a second opinion on the finding | [`../gnd-review-panel/SKILL.md`](../gnd-review-panel/SKILL.md) — advisory panel | the panel is advisory: it never edits the reviewed artifact and never applies a fix (D-22). Its synthesis is its own claim and is never folded into this payload |

**Recovery is one-time and there is no synchronization.** No route above installs a watcher, a background index, or a continuous code-to-model link (D-14). Every one of them is a command a human runs next, with its own evidence, on purpose.

## Limits

**Read this before you report a green result.** Everything below also travels in the payload's `limits.unchecked` array, so a machine consumer sees it too — a limitation that lives only in prose is one skim away from not existing.

**Extension bytes are not integrity-digest-gated.** `pyproject.toml`, `references/`, and the authored architecture contract are not byte-reproducible generator output. They appear in integrity's `unexamined` array with the reason; assertion 4 may separately inspect an explicitly declared contract or source without turning that observation into a digest claim. Extension behavior is exercised by `gnd verify MODEL population.json` over the agent's actual output — a population claim only — and by the conventional software verification that stays yours: dependency and build checks, focused tests, a smoke run, each proportionate to the extension surface that changed.

**Assertion 4 is static only.** It never imports or executes project code. It checks declared paths, module-level positional parameter shape, fact-type membership, recognized literal path expressions, and whole-AST flag/subcommand string presence. It does not prove argparse wiring, exit behavior, semantic correctness, or undeclared architecture.

**The record cannot record itself.** `.gnd-codegen.json` holds a digest for every file it manages and cannot hold one for itself, so a digest comparison detects a unilateral edit to a derived file and does not detect an edit made *together with* an edit to its manifest entry. That is an integrity bound, not tamper evidence. `gnd doctor` carries the identical limit. Assertion 3 partly backstops it — a co-edit that removes a tool is still caught, because assertion 3 never reads the manifest to decide what should be there.

**Assertion 3 binds names and signatures, never bodies.** A tool whose name and parameter list agree with the model may still compute the wrong thing. Structural conformance is a claim about the emitted *surface*.

**Derivation semantics are unchecked here.** Constructor absence for a
structured-derived fact type is the correct emitted shape, not evidence that
the derivation rule itself is right.

**A green digest comparison is not correctness.** It says the derived surface is unedited, current, and covers the model. It does not say the generated project does anything useful.

## Report

State, in your reply: the command you ran and its exit code verbatim; the counts each of the four assertions reported and whether each one **ran**; every finding by kind and target; and — when the band was 0 — which limits above bound that result. Do not translate an exit band into an adjective of your own, and do not describe a green result as "the project is correct".

## Record and commit

A conformance run worth citing -- close evidence for an experiment, or a drift finding that changes what happens next -- is evidence-lane work: append the record `NNN-conformance.md` and commit `docs(conformance): ...` with band 0 or 13 verbatim (a drift finding is information, never translated into permission), staging by explicit path the `conformance.json` you redirected and the record, only on the user's explicit go-ahead. A routine fast-lane check needs no station record. The lane rule, record shape, staging discipline, and commit grammar have one home: [`../gnd-orm-core/references/milestone-record-format.md`](../gnd-orm-core/references/milestone-record-format.md). If `.gnd-planning/` is absent, offer [`../gnd-new-project/SKILL.md`](../gnd-new-project/SKILL.md) first. The record and the commit are the driving agent's acts; `gnd` itself never reads or writes `.gnd-planning/` and never touches git.


## Calendar-day fragment (v7.1)

Follow [calendar-day terms](../gnd-orm-core/references/representation-format.md#calendar-day-terms-v71) for model version 3, Duration roles, tagged literals and guarded date functions.
This workflow currently refuses temporal models at exit 3 before publishing output. Use the reference above to identify the supported ordinary check/transition route; a route is an explicit user-selected handoff.


## Fixed reference populations

Reference-bearing model identity includes the declared fixed catalog hashes, paths and ownership. Conformance reports identity drift and never regenerates a project.

The shared format is [version-4 reference populations](../gnd-orm-core/references/representation-format.md#fixed-reference-populations-version-4).
