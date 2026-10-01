# The conformance contract

Everything `gnd conformance` claims, everything it refuses to claim, and the exact shape of what it prints. Read [`../SKILL.md`](../SKILL.md) first; this file is the detail behind it.

The single most important sentence in this document also appears in `SKILL.md`, deliberately, because progressive disclosure loads `SKILL.md` on every trigger and loads this file only on demand — a correction that lands here and not there is worse than a correction that never lands, since the stale claim then sits in the file agents always read:

> **A green conformance result establishes that the derived surface is unedited, current, has the model-required constructor surface (including structured-derived constructor absences), and that declared architecture agrees with bounded static observations. Extension bytes are not integrity-digest-gated, and nothing here establishes what any tool function or derivation computes.**

---

## 1. The four assertions, and why one of them is the gate

### Assertion 1 — integrity

Every file the codegen manifest records as `derived` still hashes to the recorded `sha256`. Files recorded as `extension` are not digest-gated by integrity; they land in the payload's `unexamined` array with a reason. Another assertion may separately inspect explicit extension declarations.

Findings: `derived-file-modified`, `derived-file-missing`. Each carries the recorded digest and the actual one, so you can reproduce the detection with `shasum -a 256` instead of believing it.

### Assertion 2 — currency

The model's bytes right now hash to the digest recorded in the manifest at generation time. **This one is literally model-code drift**: the model moved and the code did not.

Finding: `model-digest-mismatch`, carrying both digests as a pair.

The digest is over BYTES. A comment-only edit to the model changes the bytes and is reported. That is the honest answer for a digest-bound record, and the repair is one command; hashing a canonicalized parse instead would introduce a second notion of model identity that the manifest writer does not share, and two identities that disagree is worse than one that is occasionally conservative.

### Assertion 3 — structural

**This is the anti-tautology gate.** Assertions 1 and 2 are exact and cheap and both compare the generator's output against a digest the generator wrote — so both are satisfied completely by a generator that produced well-formed nothing.

Assertion 3 computes what the emitted surface must contain **from the model**, then reads the filesystem to see whether it is there. It reads no manifest and no previous generation. Three stages:

1. **Expected surface, from the model only.** For each asserted fact type and each legacy string-rule fact type, the tool symbol is the model id mapped through the one published sanitizer the emitter also calls, and the parameters are the role names in declared order through the same mapping. A structured-rule derived fact type expects no constructor. A constructor-bearing fact type named `import` is therefore expected as `import_(from_, return_)` — a Python keyword is a legal ORM identifier, and the sanitization is shared rather than reimplemented, so this assertion agrees with the emitter instead of red-flagging correct output.
2. **Observed surface, by AST.** Every `.py` under the project root is parsed with `ast.parse`. Discovery is a **whole-tree scan and not the manifest's file list** — otherwise a generator could hide a missing tool simply by leaving its file out of the manifest, which is the same tautology in different clothes. Collection is **module level only**: a `def` nested inside a function, or inside a dead branch, is not the public surface.
3. **The assertion.** A constructor-bearing fact type with no tool anywhere, a tool whose parameters do not match the role names, a constructor anywhere for a structured-derived fact type, a symbol in the derived tool module that no constructor-bearing fact type names, a model that cannot be mapped to a distinct Python surface at all, and a source file that will not parse.

Findings: `fact-type-unimplemented`, `tool-signature-mismatch`, `derived-fact-type-constructed`, `orphan-tool-symbol`, `fact-type-satisfied-by-non-derived`, `identifier-hazard`, `unparseable-source`.

**The project under inspection is never imported.** Importing a generated module to inspect it would execute arbitrary user code on every CI run. `ast.parse` is the whole mechanism, a syntax error is a finding rather than a crash, a symlink at a `.py` path is skipped rather than followed, and an oversized file is reported from its stat and never read.

Constructor presence or absence is only emitted-surface structure. A green
structural assertion does not establish that a structured derivation computes
the semantically right extension.

### Assertion 4 — architecture

The authored `architecture.contract.yaml` declares modules, module-level function names and positional parameters, artifacts, artifact consumers, entry points, flags/subcommands, model fact types, exits, and later smoke rows. Assertion 4 compares only the static subset: safe declared paths, module-level positional shape, fact-type membership, recognized literal artifact-path expressions, and whole-AST flag/subcommand string presence. It never imports or executes project code, binds only what the contract declares, and publishes `architecture-static-only` as a required limit.

### Why the split matters when you report

The two digest assertions **corroborate**. The structural assertion is the **primary gate**. State them apart when you report; a summary that averages them into "conformance passed" loses the only distinction that makes the result worth having.

---

## 2. The satisfied-by partition, and the co-edit blind spot

Whole-tree discovery has a consequence worth stating plainly: a **hand-written** file can satisfy a fact type. That is not forbidden, and it is not silent.

Every fact type whose tool was found appears in the payload's `satisfied` array with the file that satisfied it and that file's `ownership` — `derived`, `extension`, or `unmanaged` (a file GND has no record of placing). Only `derived` is a clean satisfaction; the other two also raise a `fact-type-satisfied-by-non-derived` finding, because a derived surface that no longer covers the model is repaired by regeneration and a hand-written one is not.

`len(satisfied)` plus the number of `fact-type-unimplemented` findings equals
`model.fact_types`, where that payload field is the number of
**constructor-bearing** fact types expected after structured-derived fact types
are removed. Structured-derived fact types are instead checked for constructor
absence and produce `derived-fact-type-constructed` when violated. You can
check both directions from the printed findings; neither kind of fact type may
silently disappear from the structural claim.

**The co-edit blind spot.** A manifest cannot record its own digest. So assertion 1 detects a *unilateral* edit to a derived file, and does **not** detect an edit to a derived file made together with an edit to its manifest entry. `gnd doctor` carries the identical limit. Assertion 3 partly backstops it — a co-edit that deletes a tool is still caught, because assertion 3 never consults the manifest to decide what should exist — but a co-edit that changes a body while preserving the signature passes all four assertions. That bound is published in the payload's `limits.unchecked` array under `manifest-co-edit`, not left in prose.

---

## 3. The payload

One JSON object with a fixed key set, printed under `--format json`. No timestamp anywhere: two runs over one unchanged project are byte-identical, which is what makes a recorded conformance result something a reviewer reproduces rather than trusts.

```
schema_version, tool, command, gnd_version, model, project, architecture,
assertions, examined, unexamined, satisfied, findings, limits, error
```

| Key | What it carries |
|---|---|
| `model` | the model file NAME, the recorded and actual digests, and `fact_types` — assertion 3's constructor-bearing denominator |
| `project` | the manifest version and `recorded_files`, the partition's audit trail |
| `architecture` | the current contract digest binding, six declaration counts, and sorted files whose bytes assertion 4 obtained |
| `assertions` | one entry per assertion with `ran` and a finding count |
| `examined` | every file that was digest-gated, with both digests |
| `unexamined` | every recorded file integrity deliberately did NOT digest-gate, with the reason |
| `satisfied` | every model fact type whose tool was found, with the file and its ownership |
| `findings` | what was found, each naming its subject |
| `limits.unchecked` | what a green result does not say |
| `error` | why a check could not run, or null |

**Four properties are structural rather than conventional**, which is to say a payload that violated them would be schema-invalid rather than merely impolite:

- `unexamined` and `satisfied` are required with `minItems: 0` — present-and-empty, never absent. A reader must be able to tell "nothing was skipped" from "the skipping was not reported".
- Five limits are unremovable: `manifest-co-edit`, `extension-unexamined`, `green-is-not-correctness`, `structural-surface-only`, `architecture-static-only`. Limits may be added; a limit may only be removed when the check that closes it actually ships.
- Every assertion carries `ran`, so a check that could not run can never look like one that passed. Its finding count is zero for the same reason a clean run's is.
- No verdict field and no rate field exists at any depth, and every object is closed so none can be added by accident. This payload family carries **files, digests and drift**. Verdicts about a population live in `gnd check` and `gnd verify`; rates live in `gnd fidelity` and `gnd measure`. No output carries two.

---

## 4. Exit bands

| Band | Name | When | Why not its neighbour |
|---|---|---|---|
| 0 | — | every assertion ran and found nothing | bounded by `unexamined` and `limits` |
| 3 | ill-formed | the manifest will not parse, or the MODEL will not load | the remedy is in the document; 13 would claim the code drifted from a model that does not load |
| 13 | model-code drift | any finding | the only outcome that reports a fact about the project |
| 66 | no input | no `.gnd-codegen.json`, or no model at that path | reporting 13 would say the code drifted from a model that is not there |
| 74 | IO | the tree could not be read | says nothing about what is in it |

Precedence is **74 > 66 > 3 > 13 > 0**.

**One band covers the whole command.** There is deliberately no band per assertion: the payload names which assertion found what, and a CI job branching on one code and reading `findings[].kind` is strictly better than one branching on three drift codes.

**A model that will not load is 3, not 13.** This case is worth naming because it is the shape most likely to be mistaken for a catch. Rename a fact type on only its declaration line and the constraints referencing it dangle — the model is now invalid, the structural assertion never runs, and the command exits 3 with `ran: false` and an `error`. Nothing was established about the project in either direction. A rename made consistently at every site keeps the model valid, and *that* is the edit that exits 13 with two findings: the missing fact type and the orphaned symbol.

---

## 5. The close gate (`gnd exp close`)

A `kind: codegen` experiment must record `conformance.json` beside its documents. The rule the gate applies:

> conformance **passed** iff the schema-valid payload's `findings` array is empty **and** every assertion in it reports `ran: true`.

The second clause is not an extra condition; it is what makes the first one mean anything. An empty findings array is produced by a clean run and by a run that could not happen, and the count cannot carry that distinction — which is exactly why `ran` exists.

Refused at band **14**, naming conformance as the unmet obligation, when the file is absent, unreadable, not a valid conformance payload, reports any assertion as not having run, or carries any finding. **An absent measurement is not a passing one.**

The gate reads no verdict field and no recorded exit code. There is no verdict field, and there will not be one. An exit code is a property of a past process invocation rather than of the artifact — a payload copied out of a different run would carry a stale one, and the payload is what the experiment commits.

This obligation is about the **integrity of the artifact**, never about whether the experiment succeeded. An experiment whose every question honestly resolves to `unanswered` with a reason closes at exit 0, codegen kind or not. What it may not do is close on top of a generated tree that has drifted from its own model, because every conclusion it recorded was measured against something the record no longer describes.

---

## 6. What to write when you report

- the command and its exit code, verbatim
- per assertion: the finding count **and** whether it `ran`
- every finding by `kind` and `target`
- for a green result: which of the five published limits bound it
- for band 3 or 66: that **no comparison was performed**, in those words

Do not write "the project is correct" or "the derivation is semantically
right". Nothing in this contract licenses either sentence.
