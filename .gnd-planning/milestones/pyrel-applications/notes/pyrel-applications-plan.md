# Working BookRec and expense applications with PyRel

Draft r1, 2026-10-13. Milestone: `pyrel-applications`.
Owner request: “create a milestone where we create functioning bookrec and
expenses examples with nice tutorials and build everything we need”.
Planning only. Plan review, owner acceptance and phase implementation are pending.

## Problem and completion predicates

The public package ships BookRec and expense applications implemented in Python
with GND checks, plus a standalone PyRel policy exporter and native release
approval queries. Readers cannot yet run either application with PyRel checking
all of its declared business rules. Successful export alone does not close this
gap: the runtime retains unsupported constraints and reports them explicitly.

Inspection on the opening checkout found:

- `src/gnd/export/pyrel_runtime.py:PyrelOracle.evaluate` has no `guarded` handler.
  BookRec's unread, age and preferred-genre policies are all guarded. Expense
  positive amounts, four category caps and two approval limits are guarded.
- BookRec `complete.orm.yaml` adds derived blocked/eligible facts and the
  `all_eligible` guarded completeness obligation. Checking supplied derived
  claims requires independent calculation, not trusting those claims as inputs.
- The exported audit's process exit zero means report completion. Its verdicts
  are not an application acceptance contract, and currently carry no modality.
- Existing tutorial runtime isolation is intentional: the PyRel 1.30.1 and GND
  Pydantic requirements conflict. `tutorials/runtimes` has a separate lock;
  `tools/run_tutorials.py` selects native lanes explicitly.
- Both baseline models rendered successfully into temporary standalone Python
  programs during this chat. No native PyRel execution was performed. The local
  tutorial runtime was absent. This is inspection evidence, not a passed gate.

**Outcome:** retain GND ORM models as the declared policies; translate the bounded
features these examples need into independently executed PyRel checks; provide
native recommendation/report queries and application publication gates; teach
the complete propose, check, explain, repair and evolve workflow.

The milestone closes only when:

1. BookRec recommendations and expense reports/approval candidates run locally
   using public PyRel APIs on DuckDB without provider credentials or a source
   checkout. Python may orchestrate the application and presentation.
2. PyRel checks every applicable rule in the shipped baseline, strict/complete
   BookRec and currency expense paths. Each rule has a named satisfied and
   discriminating failing/warning control; no omitted rule becomes acceptance.
3. The applications publish only after the selected PyRel acceptance gate. Bad,
   incomplete, unsupported, errored or forged-derived inputs withhold output;
   BookRec's original advisory genre mismatch remains a warning.
4. A finite, declared corpus agrees with GND on normalized business outcomes,
   coverage, warning/failure distinction and derivation mismatches. Report shapes
   and process exits are compared only where their contracts actually agree.
5. A reader can execute both tutorials as written: install, copy resources,
   propose, audit, inspect witnesses, repair, and rerun after rule evolution.
   Each tutorial includes the three required graphics specified in PA5, grounded
   in its actual synthetic facts and checked outcomes. Native steps are actually
   executed for milestone acceptance; rendered graphics receive visual review.
6. The wheel includes all example/runtime inputs; fresh target-only execution,
   focused regressions, docs rendering and independent review are recorded.
   A PR and the owner's acceptance remain separate from local success.

## 0. Binding design rules

| Rule | Requirement |
|---|---|
| PA-R1 — Independent policy execution | Native checks execute PyRel queries; never call GND's evaluator or Python policy predicates and relabel the result PyRel. GND supplies comparison evidence in development only. |
| PA-R2 — Complete declared checking | Inventory constraints and derivations for every shipped model. Missing coverage, unsupported constructs, runtime errors and work refusals cannot produce acceptance. Explicitly covered empty relations differ from unknown relations. |
| PA-R3 — Preserve policy meaning | Preserve typed identity, shared/repeated variables, literals, absence, comparison, vacuity and modality. A deontic violation warns; its strict alethic successor blocks. Derived claims are checked against independently computed facts. |
| PA-R4 — Separate audit and acceptance | Keep legacy audit completion exits compatible. Define a versioned or explicit acceptance interface with stable identities and honest reasons; never infer acceptance from audit exit zero. |
| PA-R5 — Safe publication | Check exact staged candidate bytes, bind reports to exact model/population bytes, preserve inputs and existing output on refusal, and test refusal after candidate generation. A query that already filters bad recommendations does not establish the checker catches them. |
| PA-R6 — Local, bounded, optional runtime | Explicit DuckDB configuration; isolated pinned environment; no ambient remote discovery or credentials. Set input/query/time limits and fail honestly when exceeded. Base GND installation and offline export remain credential-free and PyRel-optional. |
| PA-R7 — One semantic home | Reuse the export/runtime translation for application checking. Keep developer-owned queries separate from generated policy programs. Map new runtime modules in `tools/gnd_layers.json`, keep allowance count zero and preserve actual public lookup/shim identities. |
| PA-R8 — Evidence and scope | Native completion requires native execution; skipped lanes are not passes. No universal ORM equivalence, source-truth, transition-authorization, proof or certification claim follows from these examples. |

Every phase also discharges or argues inapplicable the process-phase standing
rules: totality, algorithmic bounds, validation order, complete policy traversal,
one normative home and measurement of contested representations.

## 1. Scope and authority

This is a new semantic/application milestone, not a rewrite of public launch,
code-refactoring or compiled-snapshot-obligations records. Existing resource
models are starting points, not automatically approved new semantics. No domain
model recovery is needed. `gnd coverage MODEL` reports experiment claims, not
whether the exporter supports a constraint, so it would not settle this plan.

Phase harvesting reads the whole effective plan, public launch runtime record
`007-phase-4.1-runtimes.md`, affected RF6/RF7/RF9 records and the shim inventory.
Changes touching compiled operations also read the compiled-snapshot milestone's
current close/amendments. Its standing-operation opt-in is not a substitute for
guarded constraints, and its delegated approval does not transfer here.

Preserve `.gnd-planning/PROJECT.md`, other milestone/question homes and existing
untracked user files. Use a topic branch and PR. No automatic skill handoff,
paid provider panel, package release, remote deployment or merge is authorized.

## 2. Product and semantic contract

The planned reader-facing applications are:

- **BookRec:** a small synthetic catalogue, reader preferences and ratings;
  native PyRel eligible/recommended-pair queries; deterministic limit/order;
  independent policy audit before publication; reasons for blocked pairs;
  advisory genre fit, strict genre evolution, and complete eligible-set checking.
- **Expenses:** synthetic submissions, amounts, categories and approval chains;
  native PyRel report with counts and totals; candidate approval followed by an
  independent policy gate; cap/chain witnesses; additive currency evolution with
  explicit EUR support. Totals are per currency, never an unlabeled mixed sum.

Checking and calculation are distinct. Correct report totals do not establish
policy validity; approved policy facts do not establish arithmetic correctness.
Neither application claims authentication, reimbursement, durable multi-user
storage or transaction authorization. Static snapshots remain static snapshots.

PA0 pins interfaces and a finite translation grammar before implementation.
The anticipated fragment includes conjunctive fact atoms with variables and
typed literals, consequent presence/absence/comparison, and the supplied
BookRec blocked/eligible derivations including their negation. Traverse exact
models first; do not silently narrow the shipped complete/currency paths to
make the tests pass. Unsupported syntax outside the admitted fragment is named
and refused. No generic recursive/aggregate/temporal ORM compiler is promised.

The acceptance result must expose enough to distinguish accepted, accepted with
warnings, rejected, incomplete/unsupported and runtime failure, with constraint
identity, modality, witnesses/reasons and input binding. PA0 determines exact
schema/version and exit mapping, including uncovered antecedents/consequents,
vacuous rules and malformed bindings. Existing report clients retain their
declared behavior unless the owner approves a versioned migration.

## 3. Dependencies and artifact homes

Hard sequence: `PA0 -> PA1 -> PA2 -> PA3 -> PA4 -> PA5 -> PA6`.
Both applications, evolution paths, executed docs and installed acceptance are
mandatory, not optional stretch goals. Application specs may share contracts,
but every separately landed phase has its own evidence and record.

Expected homes, finalized at the phase gates:

- Framework translation/acceptance: `src/gnd/export/` and its public command
  boundaries; independent exported programs remain executable without GND.
- Example queries, adapters, models, fixtures and checkpoints:
  `src/gnd/examples/bookrec/` and `src/gnd/examples/expense/`.
- Isolated runtime/lock: reuse `tutorials/runtimes/` and the packaged runtime
  resource pattern; exact maintained/packaged copies are byte gated.
- Tutorials: `docs/bookrec/`, `docs/expense/`, relevant runtime/API guides,
  `docs/applications.md` and `zensical.toml` navigation.
- Gates: focused additions beside existing PyRel and tutorial tests;
  `tools/run_tutorials.py` group/lane support as needed.
- Specs/reviews in this milestone's `notes/`; material records at its root;
  final close includes the open-question sweep and artifact digests.

No new generic executor/service abstraction is required merely to run two demos.
Keep orchestration small and use the existing bounded process/filesystem seams.

## 4. Phases

### PA0 — Baseline corpus and approved checking contract

Prepare the owner-gated spec before adding fixtures or code. Inventory all rules,
derivations and resource consumers for baseline/strict/complete BookRec and
baseline/currency expenses. Specify the bounded grammar, coverage semantics,
warning/acceptance schema, compatibility and limits. Measure current behavior
with real local PyRel and GND on the same frozen inputs.

Criteria:

- PA0-C1: a model-addressed matrix maps every rule and derivation to its expected
  supported branch and positive/negative controls, including warning reachability.
- PA0-C2: retain native baseline unsupported guarded verdicts and current derived
  behavior; proposed checking expectations fail for the actual omission.
- PA0-C3: resolve PA-D1 through PA-D5, exact schema/interfaces and ceilings;
  distinguish legacy report completion, policy acceptance and query correctness.
- PA0-C4: baseline driver uses public interfaces, pins exact inputs/runtime,
  and preserves existing exporter/report controls without remote configuration.

### PA1 — Guarded checks, coverage and acceptance

Implement the approved guarded fragment using native PyRel queries, with complete
model traversal and the agreed warning/acceptance contract. Integrate only
through the approved public export/application boundary.

Criteria:

- PA1-C1: BookRec's three and expense's seven baseline guarded rules have native
  satisfied and violated controls with exact normalized witnesses.
- PA1-C2: test presence, absence, comparisons, literals, repeated/shared variables,
  duplicate facts, typed scalars, malformed bindings, empty/vacuous and uncovered
  relations, unsupported shape, runtime error and budget refusal branches.
- PA1-C3: deontic mismatch warns and strict mismatch blocks; unknown/error cannot
  accept; model/population binding and legacy report exits are pinned.
- PA1-C4: rendered program runs in a GND-free interpreter; no runtime GND import,
  hidden fallback evaluator, new mandatory dependency or layer allowance.

### PA2 — Independently checked BookRec derivations

Support the precise complete BookRec derivation fragment required by the corpus.
Compute blocked/eligible relations from asserted facts; compare supplied derived
claims with the result; evaluate `all_eligible` against computed eligibility.
Do not let supplied claims or the recommendation query stand in for checking.

Criteria:

- PA2-C1: valid complete population passes; omitted recommendation fails
  `all_eligible`; fabricated/missing blocked or eligible claims are detected.
- PA2-C2: pin dependency order, negative-premise coverage, empty results, typed
  pair identity and exact missing/extra derived tuples.
- PA2-C3: unsupported derivation/cycle/coverage/work-limit cases refuse honestly;
  no universal derivation claim is emitted for the bounded implementation.
- PA2-C4: GND/native normalized agreement covers every admitted complete-model
  rule and derivation outcome, with the denominator explicitly recorded.

### PA3 — Working native BookRec application

Ship native PyRel queries for eligibility, recommendations and explanations,
plus a small CLI/library flow using the independent PyRel acceptance gate.
Reuse the existing synthetic catalogue and preserve the Python/GND path.

Criteria:

- PA3-C1: deterministic proposals, unknown-reader/limit controls, advisory and
  strict-genre modes, and complete-mode output work through documented commands.
- PA3-C2: injected already-read/adult-for-minor candidates are rejected after
  proposal; the original genre mismatch publishes with a visible warning.
- PA3-C3: omitted eligible recommendations and forged derived claims are rejected;
  repair and recheck work under the exact strict/complete model bytes.
- PA3-C4: exact staged bytes are checked; rejected/error cases preserve input
  and existing output. Native query tests independently assert eligible pairs
  and deterministic order/limit, rather than relying on policy pass alone.
- PA3-C5: retain the exact catalogue rows, blocked/eligible pairs and
  advisory/strict/complete results needed by PA5's BookRec graphics; provide
  source-to-figure mappings so visual explanations can be checked against them.

### PA4 — Working native expense application

Ship native report queries and approval-candidate orchestration gated by PyRel.
Demonstrate category/chain failures and the currency evolution path using the
existing GND model evolution machinery where explicitly selected by the reader.

Criteria:

- PA4-C1: report submission/approval counts and totals match narrated expected
  values; zero approvals and empty datasets are discriminating controls.
- PA4-C2: legitimate team-lead/finance candidates publish; excessive amount,
  invalid category/chain, missing submitter and duplicate/unknown approval
  cases block through the appropriate declared policy or application guard.
- PA4-C3: missing/disallowed currency blocks after evolution; supported EUR
  facts and labeled reports pass; unsupported currency cannot enter mixed totals.
- PA4-C4: exact staged-byte checks and refusal preservation mirror BookRec;
  snapshots make no actor, payment or full-transition permission claim.
- PA4-C5: retain example submissions, cap/chain witnesses and pre/post currency
  results needed by PA5's expense graphics, with source-to-figure mappings and
  units explicit in every amount and total.

### PA5 — Tutorials that readers can execute

Author cohesive learning paths extending the current examples. Each starts with
a concrete business failure, introduces only the facts/rules needed to explain
it, then demonstrates proposal, native queries, audit witnesses, repair and
evolution. Include readable expected tables/output, the required graphics below,
and troubleshooting for interpreter/dependency/coverage errors.

Required graphics are deliverables, not optional decoration:

| Tutorial | Graphic | What it must explain |
|---|---|---|
| BookRec | Recommendation and checking flow | Catalogue/preferences/ratings feed native queries; proposed recommendations enter a separate policy audit; warnings, refusals and published output follow the measured outcomes. |
| BookRec | Eligibility relationships | Show a small actual reader/book/genre example, rated and adult/minor exclusions, and the surviving eligible pairs. Include a named rejected pair and its rule witness. |
| BookRec | Before/after rule evolution | Show the same candidate under advisory versus strict genre fit, and distinguish legal recommendations from the complete eligible set. Display actual warning/failure/missing-pair outcomes. |
| Expenses | Reporting and approval flow | Submission facts feed native reporting; an approval candidate is checked before publication. Separate report arithmetic from policy verdicts. |
| Expenses | Category caps and approval-chain limits | Compare actual example amounts with the applicable category and chain ceilings; show a valid approval and a rejected one with the exact violated rule and EUR units. |
| Expenses | Currency evolution | Show the old implicit-EUR facts, the new explicit currency requirement, a missing-currency failure and the repaired labeled report. Do not imply unimplemented currency conversion. |

Use a consistent visual language across both tutorials: clear hierarchy, readable
labels, restrained colors, generous spacing and a compact legend where needed.
Prefer maintainable SVG or Mermaid for these mechanism/relationship diagrams;
select the format according to actual site rendering. Do not substitute generic
bullet boxes or decorative images for the required explanations. Keep editable
sources in the repository and make assets available in both source and installed
tutorial paths. Captions identify the question answered and relevant checkpoint;
alt text or adjacent prose supplies an accessible equivalent. Meaning cannot
depend on color alone.

Criteria:

- PA5-C1: marked tutorial blocks run sequentially in clean directories with the
  selected PyRel lane, asserting semantic outcomes as well as process exits.
- PA5-C2: both existing offline paths still run; native omission is labeled
  skipped and cannot satisfy native acceptance. Runner groups cover both paths.
- PA5-C3: readers see where policy resides, which queries compute results, and
  why report completion/warnings differ from acceptance. Show deliberate bad
  candidates so filtering cannot hide missing checking behavior.
- PA5-C4: strict site build and link checks pass; inspect rendered desktop and
  mobile pages for navigation, readable tables/code/diagrams and visible warnings.
  Source snippets come from shipped code, not separately drifting examples.
- PA5-C5: all six graphics exist and each has a source mapping to shipped facts,
  model rule identities and executed results. Verify depicted pairs, limits,
  units and outcomes against those inputs; no invented successful check appears.
- PA5-C6: retain rendered desktop/mobile evidence and visual review of every
  graphic in the site's supported themes. Labels, arrows and captions remain
  readable without clipping or overlap; mobile layouts remain usable. Verify
  accessible equivalents, contrast and non-color outcome cues. Repair visual
  defects before acceptance; a successful site build alone is insufficient.

### PA6 — Fresh-install acceptance and milestone close preparation

Build the candidate wheel and execute the selected applications/tutorials from
a target-only tree with separate GND/PyRel interpreters. Bind retained evidence
to exact wheel, models, programs, populations, locks and output artifacts.

Criteria:

- PA6-C1: both complete learning paths and their deliberate rejection controls
  run against the installed wheel, without editable checkout imports.
- PA6-C2: native corpus has 100% agreement within the explicit denominator;
  every shipped applicable rule/derivation is evaluated, with no unsupported/error
  entry in an accepted path. Query arithmetic is checked separately.
- PA6-C3: affected offline/export/application/package/docs/layer gates pass;
  runtime and generated-source isolation are demonstrated on candidate bytes.
  Installed tutorial resources include the graphic assets/sources required by
  PA5, and rendered installed-path pages have no missing visual assets.
- PA6-C4: independent review findings are reproduced/disposed; residuals and
  questions have named owners/targets. Prepare the close review and PR; only
  current owner acceptance closes the milestone or permits merge.

## 5. Documentation and compatibility surfaces

PA0 inventories report-schema clients, exporter goldens, runtime isolation
receipts and tutorial runner markers. Record intentional new profile/version
expectations separately from legacy pins. Do not refresh historical evidence
or goldens merely to hide a semantic change.

Canonical ORM semantics remain in the packaged ORM references. PyRel profile
documentation states its exact supported subset and acceptance interpretation.
Installer-owned discovery links are never hand maintained. If real development
skill twins change, preserve byte equality and executable modes in both roots;
no skill rewrite is required just to add these applications.

## 6. Risk register

| Risk | Required control |
|---|---|
| Export success mistaken for policy enforcement | A deliberately invalid candidate must fail native acceptance; inspect all rule dispositions. |
| Empty relation mistaken for unknown data | Coverage controls for each antecedent, consequent and negative premise. |
| PyRel builder accidentally uses Python boolean logic | Use public query operators; native true/false witness controls per branch. |
| Shared Python business predicates make agreement circular | GND comparison and PyRel evaluation remain separate; hand-narrated expectations and adversarial controls supplement agreement. |
| Deontic warnings block or vanish | Original/strict genre corpus and visible application warning tests. |
| Forged derived claims bypass completeness | Recompute from asserted inputs and compare missing/extra tuples before acceptance. |
| Plausible report has wrong grouping or totals | Independent expected counts/totals, empty/duplicate cases, per-currency labels. |
| Isolated runtime accidentally imports editable GND | GND-free exported-program run and fresh installed target-only tests. |
| Docs report skips as green | Required native lane and explicit executed/skipped receipts. |
| Attractive graphics contradict the tutorial or fail on mobile | Six mandatory source-grounded graphics, result/units checks, accessible equivalents and rendered desktop/mobile/theme review. |
| Broad compiler work delays working examples | Exact bounded grammar approved in PA0; outside-fragment refusal tests. |
| Query/resource exhaustion | Approved deterministic limits and bounded subprocess controls; no silent acceptance on timeout. |

## 7. Out of scope

Snowflake/Cortex deployment, hosted web UI, production authentication/storage,
payments, recommendation-quality claims, universal ORM translation, arbitrary
recursive/aggregate derivations, full operation/transition equivalence, automatic
GND backend replacement, performance marketing, certification, package release
and changes to GitHub protection/CI requirements.

## 8. Execution and review protocol

Default `auto=false`. This draft is not implementation approval. The plan and
milestone close need the development protocol's four-reviewer review bar.
The review instrument must be explicitly selected; neither the maintained
provider panel nor local reviewer delegation has been invoked by this plan.
Use bounded review convergence and retain honest residual dispositions.

After plan acceptance, run `process-phase PA0 pyrel-applications`: harvest all
obligations/carryovers; write the spec; obtain its owner gate; implement and run
focused gates; perform independent adversarial diff review and refactoring
review; write the digest-bound record and explicit-path commit on authorization.
Every declared branch needs a case capable of failing it. Reproduced fixes need
regressions demonstrated red on pre-fix bytes. Planning authorship, inherited
delegation from another milestone and old certificates confer no authority here.

## 9. Verification selection

Future obligations only; exact new filenames/nodes/commands are set in specs.
Preserve default pytest exclusions for ordinary development. This milestone
explicitly requires a separately selected, narrowly scoped native PyRel lane
for its named models/corpus/tutorials, not an exhaustive historical oracle replay.

| Phase | Required gate (expected exit 0 at completion) | Existing starting points |
|---|---|---|
| PA0 | Complete model matrix, real baseline, deliberately red successor cases | `tests/test_pyrel_export.py`, `tests/test_pyrel_constraint_oracle.py`, tutorial resources |
| PA1 | Guarded/coverage/modality/refusal branches, schema compatibility and standalone execution | `tests/test_pyrel_export_boundaries.py`, `tests/test_public_pyrel_export_runtime_optional.py`, `tests/test_public_pyrel_export_runtime_support.py` |
| PA2 | Native derived-claim/completeness cases and bounded agreement | `tests/test_pyrel_derivation_contract.py`, `tests/test_bookrec_tutorial.py`; new focused native cases |
| PA3 | BookRec commands, query answers, adversarial candidates and preserved outputs | `tests/test_bookrec_tutorial.py`; new native application cases |
| PA4 | Expense commands, numeric/currency reports, adversarial candidates and preserved outputs | `tests/test_expense_tutorial.py`; new native application cases |
| PA5 | Executed offline/native Markdown, six source-grounded graphics, strict site/links and recorded desktop/mobile/theme/accessibility inspection | `tests/test_documentation_tutorials.py`, `tests/test_external_runtime_tutorials.py`, `tools/run_tutorials.py`; graphic source/result and render controls |
| PA6 | Installed-wheel native paths, explicit corpus denominator, focused consumer/package/layer checks | Existing package resource controls, `tests/test_rf1_layering.py`, PA1–PA5 selected controls |

Acceptance records exact commands, exits, executed lane, Python/package/backend
versions and artifact digests. Historical native receipts are context only.
Planning-only verification checks files, links and whitespace; it runs no native
or product acceptance suite and makes no corresponding claim.

## 10. Owner decisions and open questions

Proposed defaults below are not owner rulings. PA0 must resolve its contract
questions before implementation; later phases cannot quietly weaken them.

| ID | Proposed default | Resolve by |
|---|---|---|
| PA-D1 — Product boundary | Local CLI/library examples with native PyRel queries and checking, preserving existing Python/GND paths; no hosted service. | Plan gate |
| PA-D2 — Model boundary | Baseline, strict and complete BookRec plus baseline/currency expenses are mandatory. Exact derivation grammar follows those files. | PA0 |
| PA-D3 — Acceptance/report compatibility | Preserve audit completion behavior; add explicit versioned/opt-in acceptance with modality, coverage, reasons and exact input binding. Pin names and exit mapping. | PA0 |
| PA-D4 — Runtime and limits | Start from existing isolated PyRel 1.30.1/DuckDB 1.5.5 lock and explicit local config. Validate actual compatibility; propose any upgrade with evidence and consumer impact. Pin ceilings. | PA0 |
| PA-D5 — Agreement normalization | Compare exact obligation identities and semantic dispositions/witnesses within the declared corpus; preserve warnings/vacuity/unknown distinctions. No arbitrary model equivalence. | PA0 |
| PA-D6 — Review selection | Required plan/close review instrument selected explicitly; no paid or delegated review inferred. | Before plan acceptance |
| PA-D7 — Tutorial experience | Extend the existing docs with clear native paths, six required explanatory graphics, expected outputs, repair/evolution and troubleshooting. The owner requested nice graphics and authorized making these requirements explicit on 2026-10-13; format/style details remain for the PA5 spec. | PA5 spec |

Next actionable step: select the plan review instrument and accept/amend the
reviewed plan; then author the PA0 spec. No phase is currently complete.
