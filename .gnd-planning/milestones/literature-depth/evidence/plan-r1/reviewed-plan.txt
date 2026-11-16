# Literature depth and revision · plan r2

Draft for plan review. The canonical plan covers parts 6–8 of
[issue #193](https://github.com/vasiloglou/gnd-public/issues/193). The
[partition](../../literature-identity/notes/literature-identity-plan.md#11-partition-of-issue-193)
and phase IDs come from the r1 outline, retained in Git at `e3431ba1`.
The owner invoked `process-milestone literature-depth auto` and explicitly
kept part 10 deferred. The delegated plan ruling follows the required review.

## Goal and completion predicates

A reader can run three small literature models with source-backed answers,
replay a targeted reading workflow with coverage, and check which results and
reviews become stale after a semantic revision. Each example must exercise
its ordinary entry point from a fresh output directory with committed inputs.
The fixture record and outcomes carry digests. The milestone closes after
LD1, LD3, LD4 and LD5 are verified, and LD2 either has its own completion
record or a dated trigger disposition citing LD1's findings.

## 0. Design rules

- **Identity and meaning.** Stable identifiers survive a label change.
  Source occurrences, entity identity, scientific assertions, experiments,
  and derived conclusions have distinct identifiers. Scientific taxonomy can
  be an evidenced assertion. ORM subtypes need an actual role or reference
  distinction. Preserve specialization, component, evaluation and influence
  as different relationships.
- **Evidence.** Use authored versioned source notes with section-level primary
  citations and local span anchors. Clearly identify any synthetic negative
  controls and comparisons. Record unknowns and omissions. Checking verifies
  structure and declared rules. Scientific validity and source support have
  their own evidence.
- **Reuse.** Carry LI2 resolution, LI4 judgment receipt and LI5 lineage policy
  contracts forward. Use the rooted LX1 extraction bundle over a reviewed
  standalone included vocabulary and local refinements. Retain extraction
  and checking route boundaries, including current include refusals.
- **Reproducibility.** Use saved, openly shareable inputs for the offline
  acceptance run. Load bounded, digest-bound artifacts under the declared
  root. Reject malformed manifests and stale or missing dependencies before
  reporting current results. Keep previous snapshots independently replayable.
- **Compatibility.** Prefer worked-example and host workflow boundaries.
  Extend shared runtime only with a phase control demonstrating a need and
  tests over both the new and current contract. Retain judgments on supplied
  occurrences and keep rule-edition comparison within the same-vocabulary
  contract.

## 1. Sources, scope and authority

| Source | Obligation | Owner |
|---|---|---|
| #193 part 6 proposal and criteria 1–7 | Three competency-question examples, guarded comparison, justified model constraints and faithful unknowns | LD1 |
| #193 part 6 quantities follow-up | Dimension-aware anchored quantities, percent distinction and exact decimal proof when the examples establish the need | LD2 |
| #193 part 7 proposal, criteria 1–7 and absence follow-up | Six recorded passes, replay, scoped absence, revisit rules, budget and cost denominators | LD3 |
| #193 part 8 proposal, criteria 1–7 | Complete dependencies, reproducible migration with reviewed non-additive changes, and prior snapshot replay | LD4 |
| #193 part 8 derived verdicts follow-up | Support-scoped verdicts and rule/resolution invalidation | LD5 |

LD1 source candidates are the [Clawpack dam-break example](https://www.clawpack.org/gallery/pyclaw/gallery/dam_break.html)
and [solver derivation](https://www.clawpack.org/riemann_book/html/Shallow_water_approximate.html),
the [OPES-eABF sampling paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC12243082/),
and [Halko, Martinsson and Tropp on randomized matrix decompositions](https://arxiv.org/abs/0909.4061).
The LD1 spec will freeze the locator and version for each source and determine
which statements each source supports. Use original summaries for the bounded
fixture and cite the controlling source sections. The larger host-scale
evaluation remains assigned to D1 in the identity plan.

## 2. Dependency and replay model

Inputs carry local relative names, versions and raw digests. Each workflow
stage declares its semantic inputs, outputs and freshness conditions.
Operational replay verifies the complete expected stage inputs and outputs
without a producer callback on a completed unchanged stage. An incomplete
or changed stage is reported explicitly and routed through the affected
worklist when a producer is available. Closure, scope, coverage and
fidelity evidence are explicit inputs to the optional stronger absence
claim. Ordinary zero-row queries keep their normal population semantics.

## 3. Readiness

| Phase | Hard prerequisites | Current state |
|---|---|---|
| LD1 | LI2, LI4, LX1 and the plan ruling | Predecessors merged. Spec follows the ruling. |
| LD2 | LD1 finding demonstrating a declared quantity gap | Conditional. LD1 measures the trigger and names the evidence. |
| LD3 | LD1 and LI4 | Waiting for LD1. Its methods control uses the existing extraction representation. |
| LD4 | LD1, LD3, LI2, LI4 and LI5 | Waiting for LD3. The integration control exercises its coverage artifact. |
| LD5 | LD4 and LI5 | Waiting for LD4. |

LI2, LI4 and LI5 are recorded in the
[literature-identity close](../../literature-identity/035-milestone-close.md).
LX1's rooted extraction work is recorded in the
[literature-interop close](../../literature-interop/014-milestone-close.md)
and merged to main by PR #202 at `e3431ba1`. No mandatory
phase may require output from conditional LD2. Any LD1 evidence that needs
a missing quantity capability may be a discovery control with that
limitation explicitly recorded.

## 4. Phases and acceptance

### LD1 · Three competency-question examples

- Publish three runnable models with four predeclared question rows each.
  For dynamics ask about equation/regime, boundaries, discretization and
  conservation. For molecular/statistical physics ask about system, energy
  model, ensemble/sampling objective and approximation/validity conditions.
  For algorithms ask about operator/objective, components, result and
  assumptions/cost model. Each area must have a source-backed positive
  and a deliberately unanswerable question. Every positive cites a span.
- Model scores through experiments. Dataset version, split, metric, units,
  baseline, configuration and uncertainty are distinct and optional where
  the source is silent. A directly comparable positive has a matching
  evidence context. Changed split, metric or relevant conditions independently
  prevent direct comparison. Unknown comparability inputs stay unresolved.
- Renaming a label preserves identity. A complexity answer with a missing
  assumption or cost model reports a limitation. Distinguish provenance for
  taxonomy-as-data, subtype roles, components and influence. Mark an encoded
  equation as a reported equation and test the output classification.
- Each enforced constraint has a named purpose, positive fixture and
  independent violating control. Run real rooted extraction verification and
  check for all three examples. Record whether existing anchors and replay
  suffice for the quantity observations, with any trigger reproduced.

### LD2 · Conditional quantity support

The LD1 record opens only the capability with a reproduced need in its
examples. Exercise supported unit/quantity anchors against dimension
mismatch, distinguish percentage points from percent without conversion
by label, and, if required, establish exact-decimal witness/replay with
named unsupported Float and non-integral Number boundaries. State the
disposition of each capability and regress existing numeric encodings and
input refusal paths. Preserve optional measurement fields as separate facts.

### LD3 · Multipass reading and coverage

- Freeze an inventory of versions, sections, equations and tables. Replay
  the ordered inventory, broad extraction, targeted selection, targeted
  extraction/vocabulary proposals, review, and affected recheck stages.
  Record each pass's purpose, input/output digests, inspected ranges,
  omissions, producer outcome and carried questions.
- A methods-only fact is absent from the opening pass and recovered by a
  real targeted verify/check over saved responses. Missing methods reports
  unavailable. Exercise distinct inspected-but-unfound, unavailable,
  not-applicable and explicit denial evidence. Reproduce a reported violation
  through extraction and checking.
- Account for every original and newly introduced question through resolved,
  retained with reason, or superseded with a valid link. A vocabulary change
  identifies relevant older source spans for revisit and leaves unrelated
  documents off the worklist. Replay a complete run with zero producer calls.
- Exercise stopping by fulfilled coverage, exhausted evidence or budget.
  Report supported facts and newly answered questions per declared reading
  cost, with attempted/refused/empty/omitted/exhausted rows retained.
  Independently remove closure, the linked coverage or measured fidelity
  recall and verify that the stronger absence claim becomes unavailable.

### LD4 · Semantic revision and current-release evidence

- Bind source excerpts, authored model bytes and semantic definition/policy
  inputs, extraction bundles, decisions, assertion reviews, composition
  manifests, queries, witnesses, and published claims. Integrate the LD3
  coverage dependency. Inventory required kinds and links; a self-consistent
  edited manifest missing a required input cannot claim current status.
- Preview affected occurrences and transitive dependents. Migrate to a
  separately identified snapshot with explicit old-to-new coordinates,
  preserving an ambiguous occurrence as a rereading item. Recheck and
  re-review the affected subset with existing public routes.
- A whale sense split removes the declared false paths and preserves the
  unrelated claim set. A predicate definition change stales its dependent
  reviews even with identical source and role values. Wrong/missing
  dependencies, ambiguous mappings and a disallowed additive edit each
  have distinct controls. Replay the prior snapshot from retained evidence.
- Exercise a reviewed non-additive transition and the additive refusal.
  Use rule-edition comparison only for an unchanged vocabulary case.

### LD5 · Support-scoped derived verdicts

Bind a verdict to the claim, assertion occurrence supports, sense-resolution
decisions, rule bytes and resolution edition. Independently mutate each
binding and require revalidation. Reject one of two supports and preserve
the claim through the other, then remove the last valid support and
show the claim loses that backing. Reuse the example-level binding if it
can enforce these predicates; record the choice at the LD5 spec gate.

## 5. Surfaces and change ownership

Extend the literature worked example, with reader instructions linking to
the documents and evolution guides where the handoffs are relevant. Put
provider-neutral stage and semantic migration format rules in their owning
workflow. Keep core schema, judgment, witness or anchor changes scoped to
demonstrated needs. Record component reuse decisions in phase specs and
update any affected registry and package inventory with implementation.

## 6. Risks and controls

| Risk | Control |
|---|---|
| Textbook facts silently answer source questions | Explicit unavailable answers, span checking and separate synthetic controls |
| Equal score shape implies comparable science | Independent mutations for metric, split and conditions |
| Reading counts imply complete coverage | Typed coverage, omission denominator and absence prerequisites |
| Self-consistent stale snapshot passes | Required artifact roster, per-input mutation and prior-snapshot replay |
| Rejecting one witness removes a multiply supported claim | Two supports, one removal, then last removal |

## 7. Deferred and out of scope

Part 10, aggregate certificates with membership completeness, remains
deferred by the owner's current instruction. Carry omitted and duplicate
members, empty group, stale input and size-limit controls to a future
owner-selected scope. The public worked examples use bounded fixture
inputs. The host-scale corpus and live extraction spend require their own
scope. The issue excludes universal physics ontologies and constraint quotas.

## 8. Review and delivery protocol

Use the GND four-valid-response bar for the plan and milestone close.
The first standard panel is a separate instrument authorization. Assess
convergence and further authorization before any follow-up round. Each
executed phase uses its own approved spec, focused verification, one
independent diff review and a committed phase record. Review the
required roster before closing. Work on the topic branch and use a PR
for integration.

## 9. Verification gate selection

| Gate | Observable result |
|---|---|
| LD1 | Real packaged example per area. Each of the 12 question rows matches its frozen expected disposition. Mutations fail their named control. |
| LD2 | Every opened axis passes its positive and negative controls plus the selected existing anchor or witness consumer tests. An unopened axis has cited trigger evidence. |
| LD3 | A fresh end-to-end run and independently verified replay exercise public GND routes. Source/coverage, question, stop and input mutations each change or refuse their declared result. |
| LD4 | Prior and revised release replay, targeted stale inventory and deliberate broken-dependency cases. Use the affected evolution, judgment, composition and witness tests. |
| LD5 | Supported, stale, one-valid-support and no-valid-support outcomes are verified against the released revision fixture. |
| Cross-phase | Focused affected public tests, project structural guards for changes outside planning, lint with any baseline evidence, component check and fresh installed example run. Reserved evidence and census follow their existing cadence. |

Phase specs record exact commands, input fixtures, expected exits and
verification selection before implementation.

## 10. Decisions ledger

| ID | Disposition |
|---|---|
| P1 | LD2 depends on a reproduced LD1 finding. LD1 records the disposition of each possible quantity gap. |
| P2 | Decide LD5's binding at its spec gate after observing actual LD4 artifact types. |
| P3 | Owner decision. Keep issue #193 part 10 deferred. |
