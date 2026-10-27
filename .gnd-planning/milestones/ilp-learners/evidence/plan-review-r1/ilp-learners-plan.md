# ILP learners

r1, 2026-10-27. **Draft; awaiting owner approval. No review round has run.**
Milestone: `ilp-learners`. `auto=false`.
Inspection baseline: `63f7f1f` (main, after PR #45, the induced-knowledge close).

Change tags: `(o)` marks an owner answer or ruling. Untagged text is the
author's proposal. Planning authorship is not approval.

## Goal, status and completion predicates

The induced-knowledge milestone (IK) built a tool-neutral ILP bridge (its D4)
and connected one learner, Popper, without ever running it (IK5-D13 (a)). It
surveyed five other learner families for later adapters. This milestone
connects four of them to the same bridge, and runs every learner for real
once, recorded as evidence:

- **ILASP / FastLAS** (answer set programming);
- **Boolean rule sets** (integer-programming or certifiable rule-set learners);
- **an AMIE-style exact rule miner** (unlabelled Horn-rule mining);
- **an LLM proposer** (a language model writes clauses).

Neural rule learners, the fifth surveyed family, are out of scope (§7).

The bridge's trust model does not change. A learner proposes; GND re-checks
every learned rule over the same inputs, computes its own coverage and support,
refuses any disagreement, and admits survivors only as
`induced`/`proposed`/`deontic` constraints through `gnd evolve` (IK-R1, IK-R2).

Planning only. The first phase's [draft spec](phase-IL1-spec.md) awaits plan
approval and its own owner gate. No implementation, measurement, install or
approval is claimed here.

Completion requires:

1. **IL1:** the bridge has one learner registry that every adapter enters, and
   the Popper adapter is its first entry with byte-identical IK5 goldens. One
   real Popper run over the IK6 refunds example is recorded, and its output
   either imports with exit 0 or refuses with a named reason that the record
   explains. IK5-Q2 (SWI octal escapes) is fixed.
2. **IL2:** `--target ilasp` (and `fastlas`, if IL2-D1 keeps it) renders an
   ASP learning task from the neutral form, golden across two `PYTHONHASHSEED`
   values, and parses learned ASP rules into the existing clause form, where
   the existing fragment checker accepts or refuses them by name. One real run
   is recorded.
3. **IL3:** a propositional feature export, golden across two hash seeds, and
   an import of learned rule sets that maps each admissible conjunct to a
   clause and refuses every other shape by name. One real run is recorded.
4. **IL4:** an unlabelled export of a population as binary relations, and an
   import of mined Horn rules as `guarded` constraints. GND recomputes support
   and confidence; a rule whose GND support differs from the miner-reported
   support refuses with a named reason. One real run is recorded.
5. **IL5:** an LLM-proposer path that gives an agent the neutral export and
   accepts its answer only as `gnd-ilp-clauses/1` JSON through the existing
   `--target neutral` import. One real run with a named agent and model is
   recorded.
6. **IL6:** one public anonymized walk runs the same labelled example through
   every labelled adapter and exits as recorded at every step. A committed
   comparison table lists per adapter the clauses proposed, admitted and
   refused, with refusal names. Docs, skill surfaces and entry points are
   updated, and each census row has a check.
7. Every phase has approval, focused checks, independent diff review,
   refactoring review and a record. Close has four-reviewer evidence, a
   question sweep, a PR and separately recorded owner acceptance.

No delivery date is committed.

## 0. Binding design rules

IK-R1 to IK-R12 of the induced-knowledge plan
(`../induced-knowledge/notes/induced-knowledge-plan.md` §0) bind every phase
unchanged. This milestone adds:

| ID | Rule |
|---|---|
| IL-R1 | **No learner is a dependency.** No learner, solver, JVM, Prolog, ASP system, Python rule-learning package or model SDK enters `pyproject.toml`, the wheel or a required lane. GND never imports one. |
| IL-R2 | **Live runs are scratch evidence.** A learner runs only in a scratch environment outside the repository, through `gnd.process.run_bounded_process`, from an evidence script under `evidence/IL<n>/`. The record names the tool, its exact version and its install command. A live test carries the existing `live` marker and is never selected by the default gate. |
| IL-R3 | **One registry, one fragment, one re-check.** Every adapter is one registry entry (render, parse, method token, learner name). Every adapter's output reaches the one clause form and the one fragment checker (`gnd.export.ilp_rewrite`), or a named sibling contract stated in its phase spec (IL3, IL4). No adapter copies the re-check or the proposal builder. |
| IL-R4 | **A learner's numbers are claims.** Coverage, support, confidence and scores reported by any learner are compared with GND's own and never written into provenance (IK-R2). A disagreement refuses with a named reason. |
| IL-R5 | **Licences are recorded, not assumed.** Each phase records the learner's licence from its upstream source at the phase gate. A licence that forbids the recorded evidence use stops the phase for an owner ruling. |
| IL-R6 | **Untrusted output, never executed.** Learner and LLM output is parsed by a closed, capped, total reader (standing rule 1). Nothing a learner writes is evaluated as code. Prompt text built from host values is neutralized by the existing rules (IK-R5). |
| IL-R7 | **IK5 compatibility.** The `gnd-ilp/1`, `gnd-ilp-clauses/1`, `gnd-ilp-run/1`, `gnd-ilp-import/1` and `gnd-ilp-export/1` wires, the Popper rendering and every IK5 and IK6 golden stay byte-identical unless a phase spec names the change and its version bump (IK-R3). |

## 1. Scope, sources and authority

- **Source of the request:** the owner, in session, 2026-10-27 (o): "In the
  inductive logic addition we found several ilp packages but we integrated only
  one. I want a new milestone that adds more."
- **Adapter selection (o), 2026-10-27:** the owner selected all four offered
  families: ILASP / FastLAS, Boolean rule sets, AMIE-style miner, LLM proposer.
- **Live runs (o), 2026-10-27:** to the question "Should this milestone run real
  learners, which means installing them (e.g. SWI-Prolog, clingo, Popper) in a
  scratch environment?", the owner answered "Yes, one recorded run each". This
  plan reads that as authorizing, within this milestone, one recorded run per
  adapter (Popper included, closing IK5-Q5) in a scratch environment. Each
  phase gate still names the exact install commands before anything is
  installed (D2).
- **Inherited:** IK plan D4 (the bridge, "other families surveyed for later
  adapters"), IK5 spec §6 and §9, record 007, record 012's carried rows.

### Harvested obligations

| Obligation | Source | Owner |
|---|---|---|
| Further adapters "are later work on the same bridge" | IK plan §2 request 5; IK5 spec §9 | IL2–IL5 |
| IK5-Q5: a real Popper run; whether its output fits the IK2 block | 007; 012 carried rows | IL1 |
| IK5-Q2: SWI octal escapes in Popper text | 007; 012 | IL1 |
| IK6 join space: the learner's join candidates have no case | 012 | IL1 |
| IK4Q2-D3: the reference-bearing ILP export | 012 | D7 (proposed out of scope) |
| `--target` names the adapter; `ilp-<target>` method token | IK5 spec §6; IK2-D11 | IL1 registry |
| No GND command runs a learner | IK5-D12 (o) | D3 |
| Recorded fixtures bind the export digest and learner name and version | IK5-C4 | every phase |
| ILP learners never in CI or a required lane | IK plan §7; IK-R8 | IL-R2 |
| The neutral form and import contract stated learner-independently | IK5-C1 | IL-R3 |
| A packaged skill for the induction loop | IK6-Q1 → "its own milestone" | out of scope (§7) |

## 2. Contract proposal and product behaviour

### The learner registry (IL1)

One table in a new module `gnd.export.ilp_learners`, one entry per adapter:

| Field | Meaning |
|---|---|
| `target` | the `--target` spelling |
| `learner` | the run record's required `learner.name` |
| `method` | the IK2 `method` token, `ilp-<target>` |
| `render` | neutral form → files, or `None` |
| `parse` | learner output bytes → `gnd-ilp-clauses/1`, or `None` for JSON input |
| `contract` | `labelled-clauses` (IK5's) or a sibling contract named by IL3/IL4 |

`LEARNER = {"popper": "popper"}` and the `if target == "popper"` branches in
`ilp_service.py` become lookups. IK5 goldens stay byte-identical (IL-R7).

### ILASP / FastLAS (IL2)

- **Export:** `--target ilasp` writes `ilasp/task.las`: background from the
  neutral facts, one context-dependent example per population
  (`#pos`/`#neg` with the population's facts as its context), a mode bias with
  `#modeh(wrong)` and one `#modeb` per exported predicate and comparison.
- **Import:** a closed ASP rule reader. A learned `wrong :- body.` becomes
  `wrong(X) :- body'` in the clause form, X threaded as the example argument.
  ASP negation (`not`) reaches the fragment checker as `not` and is refused
  there by name; constraints (`:- body.`), choice rules and weak constraints
  are refused by construct name at parse.
- **Expected finding:** ASP learners often use negation as failure. Its refusal
  rate is a recorded result, not a defect.

### Boolean rule sets (IL3)

- **Export:** `gnd export ilp --target rules` writes a propositional feature
  table, `gnd-ilp-features/1`: one row per population, one column per feature.
  A feature is one exported predicate optionally with one integer threshold
  (`exists f_order_amount(_,A) with A > t`); thresholds are the observed values
  of the role, at most a bound fixed in IL3's spec.
- **Import:** a learned rule set is a disjunction of conjunctions of features.
  Each conjunct of **one** feature maps to one clause and goes through the
  fragment checker. A conjunct of two or more features is two independent
  existentials, which the clause form cannot join, and is refused as
  `propositional-conjunction` (IL3-D1 decides whether joined features are
  added instead). Ordered rule lists (with `else`) are refused as
  `ordered-rule-list`.

### AMIE-style miner (IL4)

- **Export:** `gnd export ilp --target amie MODEL --population POP` writes the
  population as triples. A binary asserted fact type is one relation; other
  arities are skipped and listed. No labels: the miner looks for regularities,
  not a `wrong` target.
- **Import:** `B1, …, Bn ⇒ r(x, y)` becomes `guarded` with the body as
  antecedent and an `atom` consequent. This is a sibling of IK5's contract,
  not its `wrong/1` rewriting: the rule states what the data does, not what is
  wrong. GND evaluates each rule over the population and writes its own
  support and standard confidence into `provenance.induction` (the `confidence`
  block already exists in the schema). A rule whose GND support differs from
  the miner-reported support refuses as `support-mismatch`. The provenance
  `manifest_sha256` is the population digest, as `gnd discover` does.
- **Admission:** a rule with counterexamples is still admissible as
  `proposed`/`deontic`, with counterexamples listed; `gnd discover` admits only
  rules that hold (IK4-C1). IL4-D1 decides whether IL4 keeps that difference.

### LLM proposer (IL5)

- **No new import path.** The agent's answer must be `gnd-ilp-clauses/1` JSON
  with a `gnd-ilp-run/1` run record, imported with the existing
  `--target neutral`. The re-check is the whole trust boundary.
- **The prompt** is built from the neutral export, the model's verbalization
  and object-type descriptions (IK1), neutralized. A host value reaching the
  prompt is untrusted text (IL-R6).
- **The runner** is an evidence script that selects an agent through
  `gnd.agents` (trusted adapter selection), not a GND command (D3).
- **Reproducibility:** an LLM run is not repeatable; the recorded output is
  bound by digest, and the record says so.

## 3. Dependencies and artifact homes

DAG: **IL1 → {IL2, IL3, IL4, IL5} → IL6 → close**.

- IL1 owns the registry every later adapter enters, and the live-run harness.
- IL2–IL5 are independent in content but all touch the registry, the CLI
  `--target` choices, `docs/reference/ilp-bridge.md` and the RF1 CLI goldens.
  They run one at a time, in the order IL2, IL5, IL3, IL4 (D4), merged in
  sequence.
- IL6 needs every adapter.

| Artifact | Proposed home |
|---|---|
| Plan, specs, records, evidence, live-run scripts | this milestone directory |
| Registry | `src/gnd/export/ilp_learners.py` (new, `export` lane) |
| ASP adapter | `src/gnd/export/ilp_asp.py` |
| Feature export and rule-set import | `src/gnd/export/ilp_rules.py`; schema `src/gnd/ilp-features.schema.json` |
| Triple export and Horn-rule import | `src/gnd/export/ilp_amie.py`; contract fixed in IL4 spec |
| LLM proposer | no source module; `evidence/IL5/` script over `gnd.agents` |
| Fixtures | `tests/fixtures/ilp_learners/` (synthetic, anonymized) |
| Docs | `docs/reference/ilp-bridge.md` (normative home), `cli.md`, `capabilities.md`, release notes |

Each new module is assigned in `tools/gnd_layers.json` before use; the
allowance count stays zero (IK-R7).

## 4. Phases, criteria and residuals

### IL1 — Learner registry and a real Popper run

Draft spec r1: [phase-IL1-spec.md](phase-IL1-spec.md).

- **IL1-C1:** one registry; `ilp_service.py` has no learner-name branch. Every
  IK5 and IK6 golden, and the RF1 CLI goldens, are byte-identical.
- **IL1-C2:** an unknown `--target` exits 64 (argparse choices come from the
  registry); a run record whose learner disagrees with the registry entry exits
  3 `learner-mismatch`, as today.
- **IL1-C3:** the Popper parser reads SWI's octal escapes (`\001\`); one test
  per escape form, and a malformed escape exits 3 `unparsable` with line and
  column (IK5-Q2).
- **IL1-C4:** one recorded live Popper run over the IK6 refunds export. The
  record states Popper's, SWI-Prolog's and clingo's versions and install
  commands, the export digest, the raw program, and the import exit with its
  report. If the rendering is rejected or the output does not import, the
  record names why, and fixing that is in IL1's scope when the fix lies in the
  adapter.
- **IL1-C5:** a case where the learned clause joins two fact types through a
  shared variable imports and re-checks (IK6 join space).

### IL2 — ILASP / FastLAS adapter

- **IL2-C1:** the ASP task equals a committed golden across two hash seeds.
- **IL2-C2:** the ASP reader maps a fixture hypothesis to the clause form; each
  refused construct (constraint, choice rule, weak constraint, `not`,
  aggregate, disjunction) has one test with its name.
- **IL2-C3:** run-record binding and the coverage re-check use IK5's code, with
  `method: ilp-ilasp`.
- **IL2-C4:** one recorded live run, licence and version recorded (IL-R5).

### IL3 — Boolean rule sets

- **IL3-C1:** the feature table equals a committed golden across two hash
  seeds; the threshold bound and the feature bound are fixed in the spec before
  results (IK-R12), and the work counter stays under its ceiling.
- **IL3-C2:** a single-feature conjunct maps to a clause that re-checks; a
  multi-feature conjunct refuses as `propositional-conjunction`; an ordered list
  as `ordered-rule-list`.
- **IL3-C3:** the coverage re-check compares the learner's per-conjunct covered
  populations with GND's, set-wise.
- **IL3-C4:** one recorded live run of a named rule-set learner in a scratch
  Python environment.

### IL4 — AMIE-style miner

- **IL4-C1:** the triple export equals a committed golden across two hash seeds;
  skipped fact types are listed.
- **IL4-C2:** a mined rule maps to a schema-valid `guarded` constraint with an
  `atom` consequent; constants, recursion and non-binary atoms are handled as the
  IL4 spec's table says, each with a test.
- **IL4-C3:** GND's support and confidence match a brute-force oracle on small
  fixtures; a miner-reported support that differs refuses as `support-mismatch`.
- **IL4-C4:** one recorded live run, JVM and miner versions recorded.

### IL5 — LLM proposer

- **IL5-C1:** the prompt builder is deterministic for fixed inputs (golden
  digest) and neutralizes host strings; a hostile description or value fixture
  cannot change the prompt's instruction section.
- **IL5-C2:** a malformed agent answer exits 3 at the clauses reader; a
  well-formed answer whose claimed coverage is wrong exits 3
  `coverage-mismatch`. Both reuse IK5's code paths.
- **IL5-C3:** one recorded live run with a named agent adapter and model id;
  its proposed, admitted and refused clauses are listed.

### IL6 — Comparison walk, docs, integration

- **IL6-C1:** the walk exits as recorded at every step over the IK6 refunds
  example for every labelled adapter, from committed learner outputs (the live
  outputs from IL1–IL5). Its comparison table is a golden.
- **IL6-C2:** `ilp-bridge.md` has one section per adapter with its fragment
  table and refusal names; `cli.md`, `capabilities.md` and release notes are
  updated; the skill census is extended, with a check per row.
- **IL6-C3:** API and CLI pins, RF5 entry points, closed-lane and layer checks,
  the RF6 query ceiling, and the installed-candidate check pass.

### Carried limitations

| Item | Disposition |
|---|---|
| IK4Q2-D3: reference-bearing ILP export | D7 |
| IK6-Q1: a packaged induction skill | its own milestone |
| Neural rule learners | out of scope (§7) |
| Coverage agreement is necessary, not sufficient | unchanged; stated per adapter |

## 5. Documentation, skill and compatibility surfaces

- **IL1:** no wire change; `ilp-bridge.md` gains a "live runs" note and the
  registry description.
- **IL2–IL5:** each adds a `--target` value (CLI goldens), a section of
  `ilp-bridge.md`, and IL3/IL4 add schemas to the schema inventories.
- **Skills:** the two pin sites that name `gnd export ilp` are inspected per
  phase; edits only where behaviour changed. No new packaged skill.
- **Public Python names:** none planned; `api.__all__` unchanged.

## 6. Risks and required controls

| Risk | Control |
|---|---|
| A learner enters the dependency set | IL-R1; a test that `pyproject.toml` and the wheel metadata name none |
| A live run leaks host data or user paths into evidence | IK-R10, IK-R11; evidence scripts write relative paths; the IK close's downstream-name and username checks extend to this directory |
| A learner's numbers are trusted | IL-R4; mismatch refusals tested per adapter |
| ASP and rule-set semantics differ silently from GND's | a fragment table per adapter, as IK5's |
| A non-OSI licence | IL-R5; nothing bundled |
| LLM prompt injection through host values | IL-R6; IL5-C1 hostile fixture |
| Live runs are slow or flaky | bounded process limits fixed per spec; live runs are evidence, never a gate |
| Adapters copy the re-check | IL-R3; refactoring review per phase |

## 7. Out of scope

- neural rule learners;
- running any learner in CI or a required lane, or bundling one;
- a GND command that runs a learner (unless D3 rules otherwise);
- new constraint families, `derivation_rule` output, negation, aggregates,
  disjunction or recursion in admitted rules;
- automatic admission or confirmation;
- a packaged skill for the induction loop (IK6-Q1);
- publication, release or certification.

## 8. Execution, approval and review protocol

`auto=false`. Each phase follows process-phase: harvest; spec; owner gate;
approved-spec commit; implementation and focused verification; independent
diff review; refactoring review; record.

- **Plan review:** instrument unselected (D5). No review has run over r1.
- **Close review:** four reviewers, as the repository's close bar requires.
- **Contribution:** topic branch and PR per AGENTS.md; merge, release and
  certification are separate owner acts.

## 9. Verification story and affected consumers

| Phase | Falsifiable result | Consumers |
|---|---|---|
| IL1 | IK5/IK6 goldens unchanged; registry lookups; octal escapes; one live Popper record | `test_ilp_bridge.py`, IK6 walk tests, RF1 CLI goldens, layer map |
| IL2 | ASP golden; per-construct refusals; live record | new adapter tests; RF1 CLI goldens |
| IL3 | feature golden; conjunct mapping and refusals; work ceiling; live record | new tests; schema inventories |
| IL4 | triple golden; oracle support and confidence; `support-mismatch`; live record | new tests; schema inventories |
| IL5 | prompt golden; hostile fixture; reuse of IK5 refusals; live record | new tests |
| IL6 | walk exits and comparison golden; docs; census; entry points | docs/link tests, API pins, RF layering, RF5 |

Exact commands are unresolved until each spec inventories changed definitions.

### Implementability sweep (author inspection, not review)

| Dependency / conflict | Proposed resolution |
|---|---|
| `LEARNER` dict and `if target == "popper"` branches in `ilp_service.py` | IL1 registry |
| IK5-D12 (o): no GND command runs a learner | kept by default; D3 |
| The IK2 block requires `manifest_sha256`; AMIE has no labels | the population digest, as `gnd discover` writes |
| AMIE rules are positive implications, not `wrong/1` clauses | a sibling contract (`atom` consequent), fixed in IL4 |
| Rule-set conjuncts are independent existentials | single-feature conjuncts only by default (IL3-D1) |
| ILASP examples are populations | context-dependent examples carry each population's facts |
| `confidence` already exists in the induction block | AMIE uses it; others leave it absent |
| A `live` pytest marker exists, deselected by default | live tests use it (IL-R2) |
| No Prolog, ASP system or JVM was on the machine at IK5 (IK5-D13) | installs in a scratch environment, named at each gate (D2) |

## 10. Owner decisions and open questions

| ID | Decision | Status |
|---|---|---|
| D1 | Adapters: ILASP / FastLAS, Boolean rule sets, AMIE-style miner, LLM proposer; neural learners out | **owner-selected 2026-10-27 (o)** |
| D2 | Live runs: one recorded run per adapter, Popper included, in a scratch environment; never CI. Each gate names the install commands | **owner-answered 2026-10-27 (o)**: "Yes, one recorded run each"; per-gate install commands pending |
| D3 | Who runs a learner? (a) keep IK5-D12: evidence scripts only, no GND command; (b) add `gnd learn --target T` running a registered learner through the bounded process. (a) costs nothing; (b) gives hosts one command but makes GND a learner launcher | proposed (a) |
| D4 | Adapter order after IL1: IL2 (closest to IK5), IL5 (no new import), IL3, IL4 (sibling contract). Cost: only sequencing | proposed |
| D5 | Plan review instrument: four local reviewer agents (as IK D7), or the maintained panel, or none before IL1 | open |
| D6 | Milestone name `ilp-learners`, phase prefix `IL` | proposed |
| D7 | IK4Q2-D3, the reference-bearing ILP export: in IL1, or kept out | proposed out |

Next action: owner review of this plan and D3–D7; then the owner explicitly
selects `process-phase IL1 ilp-learners`.
