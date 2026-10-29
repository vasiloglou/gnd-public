# ILP learners

r3 (p2), 2026-10-27. Plan review closed by its stop rule.
**Close notes (c), 2026-10-29.** The owner approved r3 (SHA-256 `329449d8…6281`) on 2026-10-27;
the approval is recorded in `001-plan-gate.md`, not in these bytes. These bytes are r3 plus the
(c) notes, added at the owner's direction without review (plan §8, p2; close plan Part B) and
revised after the close panel. A (c) note records what happened, including each deviation from an
approved criterion and the owner ruling that allowed it; it leaves the approved text as approved.
Milestone: `ilp-learners`. `auto=false`.
Inspection baseline: `63f7f1f` (main, after PR #45, the induced-knowledge close).

**Review status (p1):**
- **Round 1.** r1 (SHA-256 `6cb10d97…e463`) received four reader opinions:
  all four request-changes, 47 findings, 14 blocking, all reproduced. See the
  [round-1 disposition](plan-review-r1-disposition.md).
- **The owner's rulings,** on 2026-10-27 (o): the owner approved the
  disposition's repairs and its proposed answers for D2 and D8–D12.
- **r2** applied them.
- **Round 2 (confirmation).** r2 (SHA-256 `e0668e30…3bb9`) received four
  approve-with-fixes opinions. 13 of the 14 round-1 blockers were resolved and
  R4-F7 partially; there were 18 new non-blocking findings (12 distinct), all
  introduced by r2. The self-inflicted ratio was 1.0, so review stopped. See
  the [round-2 disposition](plan-review-r2-disposition.md) (p2).
- **r3 (p2).** The owner directed, 2026-10-27 (o): "Apply themes A–I as r3
  with no further review round, D13 yes." r3 records those repairs and D13 and
  nothing else. **r3 bytes carry no review opinion.**
- **No approval.** No plan or spec approval exists. *(c) Since: the owner approved r3
  and the IL1 spec r3 on 2026-10-27, recorded in `001-plan-gate.md`.*

**Change tags:**
- `(p1)` marks text added or changed in r2 in response to round 1.
- `(p2)` marks text added or changed in r3 in response to round 2.
- `(o)` marks an owner answer or ruling, quoted where the owner's words exist.
- `(c)` marks a close note, 2026-10-29 (close plan Part B), in italics after the approved text
  it annotates; it carries no review opinion.
- Untagged text is the author's r1 proposal.
- Planning authorship is not approval.
- The retained snapshot under `evidence/plan-review-r1/` is the authoritative
  record of r1's bytes.

## Goal, status and completion predicates

The induced-knowledge milestone (IK) built a tool-neutral ILP bridge (its D4).
It connected one learner, Popper, without ever running it (IK5-D13 (a)), and it
surveyed five other learner families for later adapters. This milestone:
- connects four of those families to the same bridge;
- runs every learner, Popper included, once for real, recorded as evidence.

The four families:
- **ILASP / FastLAS** (answer set programming);
- **Boolean rule sets** (integer-programming or certifiable rule-set learners);
  *(c) Deviation: IL3-D1 (a), owner-ruled at the IL3 gate, integrated RIPPER, a
  sequential-covering learner; no integer-programming or certifiable learner was integrated.*
- **an AMIE-style exact rule miner** (unlabelled Horn-rule mining);
- **an LLM proposer** (a language model writes clauses).

**What does not change: the bridge's trust model.**
- A learner proposes.
- GND re-checks every learned rule over the same inputs, computes its own
  coverage and support, and refuses any disagreement.
- Survivors are admitted only as `induced`/`proposed`/`deontic` constraints,
  through `gnd evolve` (IK-R1, IK-R2).
- Round 1 confirmed this admission gate holds (reader 1).

Planning only. The first phase's [draft spec](phase-IL1-spec.md) awaits plan
approval and its own owner gate. No implementation, measurement, install or
approval is claimed here. *(c) Since: every phase is recorded, `002` to `007`,
and the close in `008` and `009`; this plan claims none of their results.*

Completion requires:

1. **IL1:**
   - **One learner registry** that every adapter enters. Popper and `neutral`
     are its first entries, in that declared order.
   - **Compatibility:** every IK5, IK6 and RF1 golden stays byte-identical,
     except where D12's join check refuses a clause (p1). *(c) Deviation: the
     owner-recorded IL1 amendments moved named IK5 goldens (`002`), and the
     IL1-F1 ruling dropped the neutral `learner-mismatch` refusal below.*
   - **The type-confused join check** refuses, for every target, a clause
     that joins values of different object types (D12 (o)) (p1), or whose
     comparison's declared type differs from its operand's (D13 (o)) (p2).
   - **SWI octal escapes** are read (IK5-Q2).
   - **One real Popper run** over the IK6 refunds export records one
     termination value and one import value, from lists closed before the run
     (p2). A default-gate replay test re-imports its committed output and
     asserts the recorded exit (p1).
2. **IL2:**
   - `--target ilasp` (and `fastlas`, if IL2-D1 keeps it) renders an ASP
     learning task from the neutral form. The task is golden across two
     `PYTHONHASHSEED` values.
   - Learned ASP rules are parsed into the existing clause form, where the
     shared fragment checker accepts them or refuses them by name.
   - One real run is recorded and replayed (p1).
3. **IL3:**
   - **The export:** a propositional feature export of **thresholded**
     features only (p1), golden across two hash seeds.
   - **The import:** a learned rule set's positive single-feature conjuncts map
     to clauses. Every other shape is refused by name: multi-feature
     conjuncts, negated features (p1) and ordered lists. Admission stays
     all-or-nothing (D10 (o)) (p1).
   - One real run is recorded and replayed.
4. **IL4:**
   - **The export:** an unlabelled export of a population as typed binary
     relations (p1).
   - **The import:** mined Horn rules become `guarded` constraints.
     - GND counts support and confidence over distinct head pairs (p1).
     - A rule whose GND support differs from the miner-reported count refuses
       `support-mismatch`.
     - Only rules that hold on the population are admitted (D11 (o)) (p1).
   - One real run is recorded and replayed.
5. **IL5:**
   - An LLM proposer with its own registry entry, `llm` (p1). Its answer is
     accepted only as `gnd-ilp-clauses/1` JSON, through the shared re-check.
   - One real run with a named agent and model is recorded, **only after D8 is
     ruled** at the IL5 gate (p1). If D8 declines the run, IL5 completes with
     fixture-only evidence and records the outcome `not run (D8)` (p2).
6. **IL6:** one public anonymized walk runs the IK6 refunds example through
   every adapter and exits as recorded at every step. *(c) Deviation: IL4-D4
   (o) ran `amie` on the committed staffing fixture, which has the relations a
   miner needs; the labelled adapters run on refunds.* An adapter whose run is
   `not run (D8)` shows that outcome (p2).
   - **The comparison table** is committed, with the columns fixed in §4
     (p1). AMIE has its own unlabelled row (p1).
   - **Docs, skill surfaces and entry points** are updated, and each census row
     has a check.
7. **Every phase has:**
   - approval;
   - focused checks;
   - independent diff review;
   - refactoring review;
   - a record.

   **Close has:**
   - four-reviewer evidence;
   - a question sweep;
   - a PR;
   - separately recorded owner acceptance.

No delivery date is committed.

## 0. Binding design rules

IK-R1 to IK-R12 of the induced-knowledge plan
(`../induced-knowledge/notes/induced-knowledge-plan.md` §0) bind every phase
unchanged. This milestone adds:

| ID | Rule |
|---|---|
| IL-R1 | **No learner is a dependency.** No learner, solver, JVM, Prolog, ASP system, Python rule-learning package or model SDK enters `pyproject.toml`, the built wheel's `Requires-Dist` (p1), or a required lane. GND never imports one. |
| IL-R2 | **Live runs are scratch evidence.** A learner runs only in a scratch environment outside the repository, through `gnd.process.run_bounded_process`, from an evidence script under `evidence/IL<n>/`. A live test carries the existing `live` marker and is never selected by the default gate. **Installs are confined to a scratch prefix: no system package manager, no `sudo`, no global PATH or shell-profile edits; a prebuilt binary or jar is a download, approved at its phase gate with URL, filename, size and SHA-256 (D2 (o)) (p1).** |
| IL-R3 | **One registry, one fragment, one re-check.** Every adapter is one registry entry. Every labelled adapter's output reaches the one clause form and the one fragment checker (`gnd.export.ilp_rewrite`). IL4's sibling contract is fixed in §2. No adapter copies the re-check or the proposal builder. |
| IL-R4 | **A learner's numbers are claims.** Coverage, support, confidence and scores reported by a learner are compared with GND's own and never written into provenance (IK-R2). A disagreement refuses with a named reason. **A run record's coverage comes from the learner or from an evaluator that is not GND (for example SWI or clingo over the rendered files, or the learner's own `predict`), named in the record; the script never derives it with GND. The learner's own printed figures are kept verbatim and compared where they exist (p1).** |
| IL-R5 | **Licences before downloads (p1).** Each phase records the learner's licence from a cited upstream URL, with its date, before any download. A licence that is not a permissive OSI licence, a repository without a licence, or a registration or click-through step stops for an owner ruling. No learner binary or source is committed. |
| IL-R6 | **Untrusted output, never executed.** Learner and LLM output is parsed by a closed, capped, total reader (standing rule 1). Nothing a learner writes is evaluated as code. Prompt text built from host values is neutralized (IK-R5). |
| IL-R7 | **IK5 compatibility.** The `gnd-ilp/1`, `gnd-ilp-clauses/1`, `gnd-ilp-run/1`, `gnd-ilp-import/1` and `gnd-ilp-export/1` wires, the Popper rendering and every IK5 and IK6 golden stay byte-identical unless a phase spec names the change. **Adding a target widens the closed `target` enums of `ilp.schema.json` and `ilp-import.schema.json` within `/1` (D9 (o)); every existing document stays valid. A test asserts both enums equal the registry's targets (p1): `ilp.schema.json` equals `EXPORT_TARGETS` and `ilp-import.schema.json` equals `IMPORT_TARGETS`, the targets `gnd import ilp-rules` accepts (p2).** |
| IL-R8 (p1) | **Synthetic inputs only.** Every live run reads only the IK6 refunds example or a committed synthetic fixture under `tests/fixtures/ilp_learners/`, named in its phase spec, with the export digest recorded. No host data reaches a learner or a provider. |
| IL-R9 (p1) | **Outcomes before runs.** Before each live run its spec fixes the closed outcome as two fields (p2): `termination` ∈ {`rendering-rejected`, `completed`, `learner-timeout`, `wall-clock-kill`, `output-limit`} and `import` ∈ {`none`, `refused:<name>`, `admitted`}, where an unparsable program is `refused:unparsable`. It also fixes the program-extraction rule as one function shared by the script and the replay test (p2), the learner settings with the full argv, all six `ProcessLimits` fields, and the learner's own timeout below the wall clock. *(c) Where the learner has one: ILASP 4.4.1, wittgenstein's RIPPER, AMIE 4.0.0 and the agent CLIs have none, so `learner-timeout` was unreachable for them and the wall clock was the bound (IL2-F5).* Every invocation is numbered and retained; the first after the gate is the run of record. A second run needs an owner ruling and is reported beside the first. A rendering or settings fix after a run is an owner-recorded amendment naming the changed goldens and the `adapter_version` bump; a parser-only fix that changes no golden stays in scope. Each record states, for every number, whether it came from the learner or the script, plus seeds, threads, and "single run, reproducibility not measured". The import is run with fixed `--requested-at`, `--actor` and `--format json`, from a fixed working directory with relative paths, so the replay can reproduce it (p2). |
| IL-R10 (p1) | **Evidence is private-clean.** A test scans this milestone directory for home paths, usernames and the downstream-name digests, with a negative control. Evidence scripts pass `HOME`, `USER` and `TMPDIR` into the bounded environment so redaction applies where it can, and write install commands with a `<scratch>` placeholder. Because `run_bounded_process` redacts only values of 4 or more bytes and only the child's output, each script also substitutes `<scratch>` and `<home>` itself in every file it writes; the scan is the backstop and matches the username as a whole path component, whatever its length (p2). |
| IL-R11 (p1) | **All-or-nothing admission** (IK5-D9) holds for every adapter (D10 (o)). |

## 1. Scope, sources and authority

**The request.** The owner, in session on 2026-10-27 (o): "In the inductive
logic addition we found several ilp packages but we integrated only one. I want
a new milestone that addss more".

**Adapter selection (o), 2026-10-27.**
- **The question:** "Which learner adapters should the new milestone add to
  the ILP bridge?"
- **The owner's selection:** "ILASP / FastLAS (ASP),Boolean rule sets,AMIE-style
  miner,LLM proposer".
- **Not offered (p1):** neural rule learners, the fifth surveyed family. Leaving
  them out is this plan's proposal.

**Live runs (o), 2026-10-27.**
- **The question:** "Should this milestone run real learners, which means
  installing them (e.g. SWI-Prolog, clingo, Popper) in a scratch environment?"
- **The answer:** "Yes, one recorded run each".
- **The confirmation (p1):** after round 1, the owner confirmed its reach:
  "D2 yes (scratch prefix, downloads approved per gate)" (o). It covers one
  recorded run per adapter, Popper included, and the JVM, AMIE, ILASP/FastLAS
  and rule-set installs, within IL-R2's limits.
- **What it supersedes (p1):** the earlier decline, IK5-D13 (a) (2026-10-26),
  and the carried row in `../induced-knowledge/012-milestone-close.md` that
  says "installing Popper was declined".
- **What it does not cover (p1):** the IL5 LLM run. That run uses provider
  credentials and sends data to a provider, so it needs its own selection
  (D8).

**The plan review (o), 2026-10-27.** The owner selected four local reviewer
agents (D5).

**Inherited from the induced-knowledge milestone:**
- IK plan D4: the bridge, and "other families surveyed for later adapters";
- IK5 spec §6 and §9;
- record 007;
- record 012's carried rows;
- IK plan §7: no learner in CI or a required lane.

### Harvested obligations

| Obligation | Source | Owner |
|---|---|---|
| Further adapters "are later work on the same bridge" | IK plan §2 request 5; IK5 spec §9 | IL2–IL5 |
| IK5-Q5: a real Popper run; whether its output fits the IK2 block | 007; 012 carried rows | IL1 |
| IK5-Q2: SWI octal escapes in Popper text | 007; 012 | IL1 |
| IK6 join space: the stand-in learner's join branch has no case (p1: restated) | 010:164–166; 012 | IL1 (C5) |
| IK4Q2-D3: the reference-bearing ILP export | 012 | D7 (proposed out) |
| `--target` names the adapter; `ilp-<target>` method token | IK5 spec §6; IK2-D11 | IL1 registry |
| No GND command runs a learner | IK5-D12 (o) | D3 |
| Recorded fixtures bind the export digest and learner name and version | IK5-C4 | every phase |
| ILP learners never in CI or a required lane | IK plan §7; IK-R8 | IL-R2 |
| The neutral form and import contract stated learner-independently | IK5-C1 | IL-R3 |
| A packaged skill for the induction loop | IK6-Q1 → "its own milestone" | out of scope (§7) |
| (p1) The type-confused join gap in the shipped `neutral` import | round 1, R1-F2 | IL1 (D12) |

## 2. Contract proposal and product behaviour

### The learner registry (IL1)

One table in a new module, `gnd.export.ilp_learners`, with one entry per
adapter, **in declaration order: `popper`, then `neutral`, then each later
adapter appended (p1).**

| Field | Meaning |
|---|---|
| `target` | the `--target` spelling |
| `learner` | the run record's required `learner.name`; for `neutral`, any name that is **not** another registered learner's (p1) |
| `method` | the IK2 `method` token, `ilp-<target>` |
| `exports` | whether `gnd export ilp` accepts this target (`neutral` does, writing `neutral.json` only) (p1) |
| `render` | export input → files; its input type is set by `contract` (p1) |
| `parse` | learner output bytes → `gnd-ilp-clauses/1`, or `None` for JSON input |
| `contract` | `labelled-clauses` (IK5's), or `unlabelled-horn` (IL4's) (p1) |

**Derived tuples (p2):**
- `EXPORT_TARGETS`: the entries with `exports=True`.
- `IMPORT_TARGETS`: the entries with `contract == "labelled-clauses"`, which
  is exactly what `gnd import ilp-rules` accepts.
- **Values:** `popper` and `neutral` are in both. `llm` is import-only
  (`exports=False`). `amie` (`unlabelled-horn`) is export-only for `gnd export
  ilp` and is imported by `gnd import mined-rules`.

**What changes in `ilp_service.py`:**
- `LEARNER = {"popper": "popper"}` and the `if target == "popper"` branches
  become registry lookups.
- The command modules keep literal `choices=` tuples. A test asserts by parser
  introspection that they equal the registry. This adds no entry-point edge and
  no import at parser-construction time (RF5) (p1).
- Every IK5 golden stays byte-identical (IL-R7).

### The type-confused join check (IL1, D12 (o)) (p1)

- **Where:** a new fragment check, `type-confused-join`, as one shared function
  in `gnd.export.ilp_rewrite`. Both the `wrong/1` rewriter and IL4's Horn-rule
  mapping call it (p2).
- **What it refuses:** a variable whose join sites resolve to object types
  that are not compatible under the same ancestor-closure predicate that
  `semantic:op-term-type-compat` uses (`model/_validation.py`
  `_ancestor_closure`).
- **Join sites (p2):**
  - every atom argument position the variable occupies;
  - a comparison predicate's declared type, which counts as a site of its
    variable operand (D13 (o));
  - **not** anonymous `_`: each `_` occurrence is its own fresh variable, so it
    is excluded.
- **Type source (p2):** a closure map computed once from ModelIndex, carried on
  the import's prepared state, never on the `gnd-ilp/1` wire.
- **Scope:** it runs for every target, `neutral` included.
- **What it closes:** today a clause joining a refund id with an amount
  validates with exit 0.
- **Effect on the shipped bridge:** this narrows `gnd import ilp-rules`. An IK5
  corpus case that changes exit is listed in the IL1 record as an intended
  behaviour change.

### ILASP / FastLAS (IL2)

**Export: `--target ilasp` writes `ilasp/task.las`.**
- **Background:** only the comparison definitions (p1).
- **Examples:** one context-dependent example per population (`#pos`/`#neg`).
  Its context holds **that population's facts only, without the example
  argument** (p1).
- **Mode bias:**
  - `#modeh(wrong)`;
  - one `#modeb` per exported predicate, with arity equal to the predicate's
    arity minus 1 and typed placeholders;
  - one `#modeb` per exported comparison (p1).

**Import: a closed ASP rule reader.**
- **Mapping:** a learned `wrong :- body.` becomes `wrong(X) :- body'`, with X
  threaded as the example argument. This step exactly inverts the rendering.
- **Refused by construct name (p1):**
  - constraints (`:- body.`);
  - choice rules;
  - weak constraints;
  - classical negation (`-p`);
  - arithmetic terms;
  - intervals and pools;
  - directives.
- **Reaching the fragment checker:** `not`, aggregates and disjunction get
  there and are refused by name.
- **Constants:** a fragment-table row fixes how the reader maps symbolic
  constants, quoted strings and integers (p1).

**Expected finding:** ASP learners often use negation as failure. The refusal
rate is a recorded result, not a defect.

### Boolean rule sets (IL3)

**Export: `gnd export ilp --target rules` writes a propositional feature table,
`gnd-ilp-features/1`.**
- One row per population, one column per feature.
- **A feature** is one exported predicate with one integer threshold, for
  example `exists f_order_amount(_,A) with A > t`.
- **Unthresholded features are not exported:** as a single-atom clause they
  could only refuse `non-ground-absence` (p1).
- **Thresholds** are the role's observed values, up to a bound fixed in the
  IL3 spec.
- **The schema** declares each column's literal meaning (predicate, role,
  operator, threshold), so a reader cannot reinterpret it (p1).

**Import: polarity table (p1).**

| Learner literal | Maps to |
|---|---|
| feature true (`= 1`, `> 0.5` on a binary column) | its clause |
| feature false or negated (`= 0`, `<= 0.5`) | refused `negation-as-failure` |
| conjunct of two or more features | refused `propositional-conjunction` |
| ordered rule list (`else`) | refused `ordered-rule-list` |

Admission is all-or-nothing (IL-R11). Each learner output spelling has a
test.

### AMIE-style miner (IL4)

**Command shape (p1).**
- **Export:** `gnd export ilp --target amie MODEL --population POP --out DIR`.
  `--labels` and `--population` are mutually exclusive, and the target decides
  which one is required.
  - **Post-parse check (p2):** argparse cannot express the target deciding
    which one is required, so a post-parse check enforces it, with exit 64.
  - **Unchanged (p2):** the missing-`--labels` exit for `popper` and `neutral`.
  - **Moved goldens (p2):** making `--labels` non-required moves two existing
    RF1 goldens, the `gnd export ilp` help usage line and the `unknown_flag`
    exit stderr ("required: …"). IL4 lists both.
- **Import:** `gnd import mined-rules MODEL RULES --population POP
  --reported FILE --target amie --out PROPOSAL`, a new subcommand.
  - **Home (p2):** it lives in `gnd.commands.checking`, which is already bound
    to `gnd.export.ilp_service`, so there is no new `gnd_entrypoints.json`
    binding.
  - **Goldens:** its RF1 goldens are new files.
  - **Report:** it has its own report, with `command` value `import
    mined-rules` and a schema named in the IL4 spec (p2).

**Export contents.**
- **Relations:** each binary asserted fact type is one relation.
- **Typing:** each entity is spelled with its object-type prefix, so joins stay
  typed (p1).
- **Other arities** are skipped and listed.
- **No labels:** the miner looks for regularities, not for a `wrong` target.

**Import mapping.**
- `B1, …, Bn ⇒ r(x, y)` becomes `guarded`: the body is the antecedent and an
  `atom` consequent is the head.
- This is a sibling of IK5's contract, not its `wrong/1` rewriting.
- The shared type-check function and validation apply. IL4 calls it directly
  and has its own test (p2).

**Counting (p1).**
- **Numerator:** |{(x,y) : ∃z body ∧ head}|.
- **Denominator:** |{(x,y) : ∃z body}|.
- **Confidence:** `confidence.value` = numerator / denominator, with formula
  `std-confidence-head-pairs`.
- **The comparison:** the miner's positive-example count must equal GND's
  numerator; otherwise the rule refuses `support-mismatch`.
  *(c) Deviation (IL4-F4): AMIE prints no positive examples; the count
  compared is its Support, its count of distinct head pairs.*
- **Not compared:** PCA confidence. It is kept verbatim as the miner's claim.
- **Weaker than IK5:** only counts are compared, because the miner emits no
  sets.
- **Zero body pairs:** the rule is refused `covers-nothing`.

**Admission (D11 (o)) (p1).**
- A rule is admitted only if it holds on the population: numerator equals
  denominator, the same bar as `gnd discover` (IK4-C1).
- A rule whose head fact type is not in the population's `covers` is refused
  `open-world-head`.
- `examples` are opaque fact ids, never raw values (IK-R11). The provenance
  `manifest_sha256` is the population digest, as `gnd discover` writes it.

### LLM proposer (IL5)

- **Registry entry (p1):** `target: llm`, `parse: None` (JSON input),
  `method: ilp-llm`, `exports: False` (p2). The learner name must be the agent adapter id, and the
  model id is recorded as the agent reports it.
- **The prompt builder** gets a source home in the `export` lane,
  `gnd.export.ilp_prompt` (p1). It is built from the neutral export, the
  model's verbalization and object-type descriptions (IK1), neutralized.
  Host strings are untrusted text (IL-R6).
- **The runner** is an evidence script that selects an agent through
  `gnd.agents`, not a GND command (D3).
- **The run record's coverage** comes from SWI evaluating the clauses over the
  Popper rendering of the same export, not from GND (IL-R4) (p1).
- **Not repeatable:** an LLM run cannot be repeated. The recorded output is
  bound by digest, and the record says so.
- **Blocked until D8 (p1):** the live run is blocked until the IL5 gate rules
  the agent, model, credential source, call or cost ceiling, and provider
  terms.
- **If D8 declines the run (p2):** IL5 keeps fixture-only evidence, records the
  outcome `not run (D8)`, and the IL6 row shows it.

## 3. Dependencies and artifact homes

DAG (p1): **IL1 → IL2 → IL5 → IL3 → IL4 → IL6 → close**. The chain follows D4.
IL2–IL5 are independent in content, but they share the registry, the CLI
choices, the schema enums, `ilp-bridge.md` and the RF1 goldens, so they run
one at a time.

| Artifact | Proposed home |
|---|---|
| Plan, specs, records, evidence, live-run scripts | this milestone directory |
| Registry | `src/gnd/export/ilp_learners.py` (new, `export` lane) |
| Type-confused join check | `src/gnd/export/ilp_rewrite.py` (p1) |
| ASP adapter | `src/gnd/export/ilp_asp.py` |
| Feature export and rule-set import | `src/gnd/export/ilp_rules.py`; schema `src/gnd/ilp-features.schema.json` |
| Triple export and Horn-rule import | `src/gnd/export/ilp_amie.py`; `gnd import mined-rules` (p1) |
| LLM prompt builder | `src/gnd/export/ilp_prompt.py` (p1); runner in `evidence/IL5/` |
| Fixtures | `tests/fixtures/ilp_learners/` (synthetic, anonymized) |
| Docs | `docs/reference/ilp-bridge.md` (normative home), `cli.md`, `capabilities.md`, release notes |

Each new module is assigned in `tools/gnd_layers.json` before use, and the
allowance count stays zero (IK-R7). A command in a new command module would be
bound in `tools/gnd_entrypoints.json` (p1). None is planned:
`gnd import mined-rules` joins `gnd.commands.checking`, which is already bound
(p2).

## 4. Phases, criteria and residuals

### IL1 — Learner registry, join check and a real Popper run

Draft spec r3: [phase-IL1-spec.md](phase-IL1-spec.md) (p1, p2).

- **IL1-C1 (p1):** one registry, in declaration order. `ilp_service.py` has no
  learner-name branch. A fake registry entry, monkeypatched in, reaches
  `render`, the `method` token and the learner check. The export `choices=`
  and `ilp.schema.json` enum equal `EXPORT_TARGETS`; the import `choices=` and
  `ilp-import.schema.json` enum equal `IMPORT_TARGETS` (p2). Every IK5, IK6
  and RF1 golden is byte-identical, except corpus cases that C2 refuses, which
  are listed.
- **IL1-C2 (p1):**
  - A clause that joins incompatible object types exits 3
    `type-confused-join`, for `popper` and `neutral`.
  - A comparison whose declared type is incompatible with its operand's role
    type exits 3 `type-confused-join` (D13 (o)) (p2).
  - A clause that joins compatible types is unchanged, and so is a clause with
    `_` at two incompatible types (p2).
  - A neutral run record that names a registered learner exits 3
    `learner-mismatch`. *(c) Dropped by the owner's IL1-F1 ruling (`002`).*
- **IL1-C3 (p1):**
  - **Where the fix goes:** both the tokenizer and `_unquote`.
  - **What it reads:** every escape form that the pinned SWI version writes,
    listed at the gate.
  - **Boundaries:** U+10FFFF (`\4177777\`) is accepted. `\4200000\`, the
    surrogate `\154000\` and an escape of more than 7 digits refuse with an
    octal-specific message (p2).
  - **A token-boundary case** yields two constants.
- **IL1-C4 (p1):**
  - **The run of record:** one live Popper run over the IK6 refunds export,
    under IL-R9.
  - **Its outcome:** one `termination` value and one `import` value (p2).
  - **What is retained:** raw stdout, the extracted program, an
    independent-evaluation run record (IL-R4), the import report or the
    refusal line, and the versions.
  - **Replay (p2):** a default-gate test checks four things:
    - the shared extractor reproduces `program.pl` (or nothing) from the
      committed raw stdout;
    - with a program, it re-runs `gnd import ilp-rules` with the recorded
      fixed arguments and asserts the exit, the path-normalized report and
      the proposal's SHA-256;
    - for a refusal, it asserts the refusal line instead;
    - with no program, it asserts `import: none`.
- **IL1-C5 (p1):** the importer half of the join space is already closed (IK5
  case I2). A synthetic fixture on which the stand-in learner yields at least
  one join candidate gets a case. If no such fixture exists within the stand-in
  learner's rules, the row stays carried with that reason.

### IL2 — ILASP / FastLAS adapter

- **IL2-C1:** the ASP task equals a committed golden across two hash seeds. The
  golden pins the background as comparisons only, per-example contexts and the
  `#modeb` arities.
- **IL2-C2 (p1):** the ASP reader maps a fixture hypothesis to the clause form.
  Every refused construct in §2 has one test with its name. The constants table
  has one test per kind.
- **IL2-C3:** the run-record binding and the coverage re-check use IK5's code,
  with `method: ilp-ilasp`.
- **IL2-C4 (p1):** one live run under IL-R9, with its licence recorded first
  (IL-R5), and a replay test.

### IL3 — Boolean rule sets

- **IL3-C1:** the feature table equals a committed golden across two hash
  seeds. The threshold and feature bounds are fixed in the spec before results
  (IK-R12), and the work counter stays under its ceiling.
- **IL3-C2 (p1):** each row of the polarity table has a test per learner output
  spelling. A positive single-feature conjunct maps to a clause that re-checks.
- **IL3-C3:** the coverage re-check compares the learner's per-conjunct covered
  populations with GND's, set-wise. Those populations come from the learner's
  own `predict` (IL-R4).
- **IL3-C4:** one live run of a named rule-set learner in a scratch Python
  environment, under IL-R9, with a replay test.

### IL4 — AMIE-style miner

- **IL4-C1:** the typed triple export equals a committed golden across two hash
  seeds, and skipped fact types are listed.
- **IL4-C2:** a mined rule maps to a schema-valid `guarded` constraint with an
  `atom` consequent. Constants, recursion and non-binary atoms are handled as
  the IL4 spec's table says, each with a test.
- **IL4-C3 (p1):** GND's numerator, denominator and confidence match a
  brute-force oracle over distinct head pairs on small fixtures.
  `support-mismatch`, `covers-nothing`, `open-world-head`, `type-confused-join`
  (through the shared function) (p2) and the refusal of a rule that does not
  hold each have a test.
- **IL4-C5 (p2):** the post-parse `--labels`/`--population` check exits 64.
  The missing-`--labels` exit for `popper` and `neutral` is unchanged. The two
  moved RF1 goldens are listed in the IL4 record.
- **IL4-C4:** one live run under IL-R9, with JVM and miner versions recorded,
  and a replay test.

### IL5 — LLM proposer

- **IL5-C1 (p1):** `gnd.export.ilp_prompt` is deterministic for fixed inputs (a
  golden digest) and neutralizes host strings. A hostile description or value
  fixture cannot change the prompt's instruction section.
- **IL5-C2:** a malformed agent answer exits 3 at the clauses reader. A
  well-formed answer whose claimed coverage is wrong exits 3
  `coverage-mismatch`.
- **IL5-C3 (p1):** **blocked until D8.** One live run with the agent adapter
  and model id as ruled, under IL-R9, with a replay test. If D8 declines the
  run, the outcome is `not run (D8)` with fixture-only evidence (p2).

### IL6 — Comparison walk, docs, integration

- **IL6-C1 (p1):** the walk replays every adapter's committed run of record
  over the IK6 refunds example and exits as recorded at every step. The
  comparison table is a golden. *(c) Deviation: `amie` replays over the
  staffing fixture (IL4-D4 (o)).*
  - **Labelled adapters' columns:**
    - the outcome;
    - clauses proposed;
    - the import exit;
    - the first refusal name and its clause index;
    - clauses not evaluated;
    - clauses admitted.
  - **AMIE's columns:**
    - rules mined;
    - rules admitted;
    - the first refusal.
  - **An adapter with no output** shows its outcome and empty counts. That
    includes `not run (D8)` (p2).
- **IL6-C2:** `ilp-bridge.md` has one section per adapter, with its fragment
  table and refusal names. `cli.md`, `capabilities.md` and the release notes
  are updated. The skill census is extended, with a check per row.
- **IL6-C3:** these controls pass:
  - the API and CLI pins;
  - the RF5 entry points;
  - the closed-lane and layer checks;
  - the RF6 query ceiling;
  - the installed-candidate check.

### Carried limitations

| Item | Disposition |
|---|---|
| IK4Q2-D3: reference-bearing ILP export | D7 |
| IK6-Q1: a packaged induction skill | its own milestone |
| Neural rule learners | not offered; out of scope (§7) |
| Coverage agreement is necessary, not sufficient | unchanged; stated per adapter; IL4 compares counts only (p1) |

## 5. Documentation, skill and compatibility surfaces

- **IL1:**
  - The import adds the `type-confused-join` refusal, including the
    comparison-type case (D13 (o)) (p2), and neutral run records gain the
    `learner-mismatch` refusal (p1). *(c) That refusal was dropped by IL1-F1.*
  - `ilp-bridge.md` gains the registry, the new refusals and a "live runs"
    note.
- **Each of IL2–IL5 (p1):**
  - adds a `--target` value (moving the RF1 CLI goldens);
  - widens the `target` enum or enums it belongs to within `/1` (D9 (o)):
    `ilp.schema.json` for an exportable target, `ilp-import.schema.json` for a
    `labelled-clauses` target (p2);
  - adds a section of `ilp-bridge.md`.
- **Further changes:**
  - IL3 and IL4 add schemas to the schema inventories.
  - IL4 adds `gnd import mined-rules` in `gnd.commands.checking`, with no new
    entry-point binding, and its own report schema. It moves two existing
    `gnd export ilp` RF1 goldens (the help usage line and the `unknown_flag`
    exit stderr) (p2).
  - IL5 adds `gnd.export.ilp_prompt`.
- **Skills:** the two pin sites that name `gnd export ilp` are inspected per
  phase, and edited only where behaviour changed. *(c) A third pin site,
  gnd-solve's Station 6, was found by the IL6 review (R3).* No new packaged skill.
- **Public Python names:** none are planned, and `api.__all__` is unchanged.

## 6. Risks and required controls

| Risk | Control |
|---|---|
| A learner enters the dependency set | IL-R1; a test over `pyproject.toml` and the built wheel's `Requires-Dist` (p1) |
| A live run leaks host data or user paths into evidence | IL-R8, IL-R10 (p1) |
| A learner's numbers are trusted, or the "claim" is GND's own | IL-R4 (p1); mismatch refusals tested per adapter |
| ASP, rule-set or miner semantics differ silently from GND's | a fragment table per adapter; the IL3 polarity table; IL4 counting definitions (p1) |
| A learner joins values of different types | D12 type check in the shared rewriter (p1); comparison types too (D13) (p2) |
| A non-OSI or click-through licence | IL-R5 (p1); nothing bundled |
| LLM prompt injection through host values | IL-R6; IL5-C1 hostile fixture |
| An LLM run spends money or credentials without a ruling | D8; IL5-C3 blocked (p1) |
| A live run "passes" by any outcome | IL-R9 closed outcomes and replay tests (p1) |
| A fix after a run silently moves goldens | IL-R9 amendment path (p1) |
| Adapters copy the re-check | IL-R3; refactoring review per phase |

## 7. Out of scope

- neural rule learners (not offered at selection);
- running any learner in CI or a required lane, or bundling one;
- a GND command that runs a learner (unless D3 rules otherwise);
- partial admission (D10 (o));
- new constraint families, `derivation_rule` output, negation, aggregates,
  disjunction or recursion in admitted rules;
- automatic admission or confirmation;
- a packaged skill for the induction loop (IK6-Q1);
- publication, release or certification.

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

**Plan review (p1).**
- **Instrument:** four local reviewer agents (D5 (o)).
- **Round 1:** complete.
- **Budget:** declared in the
  [round-1 disposition](plan-review-r1-disposition.md) §Convergence budget:
  r2 plus at most one confirmation round, restricted to the reproduced
  blocking findings, under the review-convergence stop rule.
- **Round 2:** complete. The stop rule was met (self-inflicted ratio 1.0,
  0 blocking), so no further plan review round runs. r3 applied the round-2
  repairs at the owner's direction, without review (p2).

**Plan approval (p1).** Recorded in `001-plan-gate.md`, which binds the
approved plan's and IL1 spec's SHA-256. The plan is not edited to record its
own approval.

**Close review:** four reviewers.

**Contribution:** a topic branch and PR per AGENTS.md. Merge, release and
certification are separate owner acts.

## 9. Verification story and affected consumers

Every phase's gate also runs these controls (p1):
- `test_rf1_cli_pins.py`;
- `test_rf5_commands.py`;
- `test_rf1_layering.py`;
- `test_gnd_arch.py`;
- `test_rf6_query_policy.py`;
- `test_public_built_inventory.py`;
- the schema inventory.

| Phase | Falsifiable result | Consumers |
|---|---|---|
| IL1 | registry equality and fake-entry tests; goldens unchanged except listed C2 cases; *(c) and the IK5 goldens named by the owner-recorded amendments (`002`)*; type-check refusals; octal cases; one recorded outcome with replay | `test_ilp_bridge.py` (its source-order tokens kept), `test_ik6_walk.py`, `test_ik_close.py` (imports `parse_program`, patches `_load_candidate`) (p1), RF1 CLI goldens, layer map |
| IL2 | ASP golden; per-construct refusals; replayed live record | new adapter tests; RF1 CLI goldens; schema enums |
| IL3 | feature golden; polarity table; work ceiling; replayed live record | new tests; schema inventories |
| IL4 | typed triple golden; oracle counts; five named refusals; post-parse exit 64; replayed live record | new tests; schema inventories; RF5 entry points; the two moved `export ilp` RF1 goldens (p2) |
| IL5 | prompt golden; hostile fixture; IK5 refusals reused; replayed live record (after D8) | new tests; layer map |
| IL6 | walk exits and comparison golden; docs; census; entry points | docs/link tests, API pins, RF layering, RF5 |

Exact commands are fixed in each spec as literal file lists (p1).

### Implementability sweep (author inspection, not review)

| Dependency / conflict | Proposed resolution |
|---|---|
| `LEARNER` dict and `if target == "popper"` branches | IL1 registry |
| CLI choices are pinned in RF1 goldens, in the order `popper, neutral` (p1) | declaration order; literal tuples with an equality test |
| Commands may import only their bound `*_service` modules (RF5) (p1) | no new edge in IL1; IL4's new subcommand lives in `gnd.commands.checking`, already bound to `ilp_service` (p2) |
| `rewrite()` receives no model or index (p2) | a closure map on the prepared state, passed as a keyword-only argument |
| `target` is a closed enum in two schemas (p1) | widen within `/1` (D9 (o)), with an equality test |
| The octal fix fails in the tokenizer first (p1) | change `_TOKEN` and `_unquote` |
| Guarded validation has no join-type rule (p1) | D12 check in the shared rewriter |
| A single-atom clause cannot be designated (p1) | IL3 exports thresholded features only |
| IK5-D12 (o): no GND command runs a learner | kept by default (D3) |
| The IK2 block requires `manifest_sha256`; AMIE has no labels | the population digest, as `gnd discover` writes it |
| `gnd export ilp` requires `--labels` (p1) | `--labels` / `--population` mutually exclusive by target; a new `gnd import mined-rules` |
| `gnd.agents` argv carries no model flag (p1) | record the model id as the agent reports it; anything else is decided under D8 |
| `ProcessLimits` has six required fields (p1) | each spec fixes all six (IL-R9) |
| Popper's console output wraps the program (p1) | the script extracts the program block and keeps raw stdout separately |
| A `live` pytest marker exists, deselected by default | live tests use it (IL-R2) |

## 10. Owner decisions and open questions

| ID | Decision | Status |
|---|---|---|
| D1 | Adapters: ILASP / FastLAS, Boolean rule sets, AMIE-style miner, LLM proposer | **owner-selected 2026-10-27 (o)**: "ILASP / FastLAS (ASP),Boolean rule sets,AMIE-style miner,LLM proposer". Leaving neural learners out is proposed (p1) |
| D2 | Live runs: one recorded run per adapter, Popper included, under IL-R2's scratch-prefix and per-gate download rules | **owner-answered 2026-10-27 (o)**: "Yes, one recorded run each"; scope confirmed: "D2 yes (scratch prefix, downloads approved per gate)" (p1) |
| D3 | Who runs a learner? (a) keep IK5-D12: evidence scripts only, no GND command; (b) add `gnd learn --target T`. (a) costs nothing; (b) makes GND a learner launcher | proposed (a) |
| D4 | Adapter order: IL2, IL5, IL3, IL4, run serially. Cost: only sequencing | proposed |
| D5 | Plan review instrument | **owner-selected 2026-10-27 (o)**: four local reviewer agents (p1) |
| D6 | Milestone name `ilp-learners`, phase prefix `IL` | proposed |
| D7 | IK4Q2-D3, the reference-bearing ILP export: in IL1, or kept out | proposed out |
| D8 (p1) | The IL5 live run: agent adapter and model id; credential source, imported by name from the documented trusted environment and never printed; call or cost ceiling; prompt input limited to the synthetic IK6 export; the provider's terms on output | **owner-ruled 2026-10-27 (o)**: "D8 at the IL5 gate"; open until then, and IL5-C3 is blocked |
| D9 (p1) | New targets widen the two closed `target` enums | **owner-ruled 2026-10-27 (o)**: "widen within /1" |
| D10 (p1) | Admission granularity for the new adapters | **owner-ruled 2026-10-27 (o)**: "all-or-nothing" |
| D11 (p1) | IL4: which mined rules are admitted | **owner-ruled 2026-10-27 (o)**: "holds only" |
| D12 (p1) | A `type-confused-join` check in the shared rewriter, for every target | **owner-ruled 2026-10-27 (o)**: "add the join check in IL1" |
| D13 (p2) | The D12 check also covers a comparison's declared type against its operand's role type | **owner-ruled 2026-10-27 (o)**: "D13 yes" |

**Next action (p2):**
1. The owner's decision on plan approval over r3, recorded in
   `001-plan-gate.md`.
2. Then the owner explicitly selects `process-phase IL1 ilp-learners`.
