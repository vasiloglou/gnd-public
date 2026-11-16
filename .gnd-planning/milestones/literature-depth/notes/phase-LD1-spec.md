# LD1 · Scientific competency examples

Status: delegated decision recorded in the LD1 spec gate.

## Provenance

This spec implements the [r3 plan](literature-depth-plan.md), whose
[delegated plan gate](../002-plan-gate.md) follows the panel over r2.
LD1 reuses the LI4 occurrence evidence boundary and the
[LX1 rooted extraction route](../../literature-interop/005-phase-LX1.md).
The [interop close](../../literature-interop/014-milestone-close.md) records
the installed package route. The plan panel reviewed the plan.

## Obligations

| Source | Obligation | Control |
|---|---|---|
| Part 6.1, 6.5 and plan §4 LD1 | Four questions per area, positives grounded in source sections, source omissions retained | Q1 and Q2 |
| Part 6.2–6.4 | Stable identity, limitations on bounds, separate optional experiment context, incompatible comparisons refused | Q3 through Q6 |
| Part 6.6–6.7 | Purpose and negative case for every enforced constraint. Distinguish a reported equation from correctness. | Q1 and Q7 |
| Plan §3, §4 LD1/LD2, §10 P1 | Record three numeric trigger probes and their consequences for the examples | Q8 |
| Plan §0, §§5–7 and §9 | Reuse GND, keep normative rule ownership, add fixture and consumer tests, retain boundaries | Q1–Q10 and gate selection |
| Plan §11 and support dispositions | Local note, primary evidence and review have separate bindings. A stale or substituted citation fails. | Q1 and Q2 |

## Standing rules

- **Identity and meaning:** Subjects have stable reference IDs and a separate
  label fact. Relation facts distinguish scientific taxonomy, components and
  influence. Q4 changes a label while retaining an occurrence reference.
- **Evidence and reproducibility:** Real source assertions and synthetic
  comparisons have explicit origins. Bind every answer to a selected checked
  fact and an exact character span where its meaning was documented. Q2
  exercises invalid span, changed source, and citation substitution.
- **Reuse and compatibility:** The existing extract, verify and check routes
  own ORM admission. The example adds no core model or proof extension.
- **Totality and input cost:** An example loads its finite packaged case
  manifest and bounded local artifacts. A malformed JSON shape refuses
  before product calls. Index each population once by declared fact type and
  the case's unique subject. Avoid comparisons across all row pairs. Q9
  exercises malformed and capped input, including their ordering.
- **Validation order and shared policy:** Verify case/support shape and
  authenticated input before product calls. Then extract and verify, then
  check, then derive answers and comparisons. Use one decision path for all
  three cases. The comparison classifies a known differing context as
  incompatible even when an independent field is missing.
- **One normative home:** The fixture README owns the example's answer,
  comparison and support contracts. GND documentation links to it.
- **Measurement:** Q8 makes all three quantity questions observable before
  deciding the trigger. Q6 distinguishes a missing comparison input from a
  different one.

## Goal

The packaged example exits 0 over three checked populations and emits 12
question rows, with three deliberate scope limitations. It exits 3 on
unusable fixture or support evidence. Expected unknown answers and incompatible
score pairs are represented as report rows and the run can still exit 0.

## Design

| Capability | Component search | Decision |
|---|---|---|
| Rooted extraction | `rooted extraction include projection`, `literature interop example verify provenance` | Reuse extract, verify and check. Adapt the packaged offline runner pattern. The interop catalog and rebind helpers serve the LX4 topology. |
| Evidence and comparison | `published scientific assertion context comparison`, `work passages evidence receipt` | Reuse raw byte and JSON helpers and LI4's distinction between receipt and validity. Add the bounded source-locator and answer binding for this example. General numeric ordering does not enforce evidence context. |

`gnd.examples.literature.depth` provides `main(argv: list[str] | None = None) -> int`.
Invoke `python -m gnd.examples.literature.depth --out DIR` with a fresh
directory. Use `build(out: Path) -> dict` to materialize bundled inputs and
derive the final report. Treat the extracted population as saved producer
output, bind it to the authored root and bundle, and run all three product
commands using the active interpreter. A supplied output directory is never
replaced. Scope the CLI to the committed corpus; independent tests can
substitute an input tree for a mutation control.

Use a shared standalone vocabulary plus local roots. The shared fact
types are:

| Fact | Roles |
|---|---|
| `subject_label` | subject, label |
| `subject_specializes`, `subject_has_component`, `subject_influenced_by` | subject, related |
| `experiment_dataset` | experiment, dataset_version |
| `experiment_split` | experiment, split |
| `experiment_metric` | experiment, metric |
| `experiment_units` | experiment, units |
| `experiment_conditions` | experiment, conditions |
| `experiment_score` | experiment, score |
| `experiment_baseline` | experiment, baseline |
| `experiment_configuration` | experiment, configuration |
| `experiment_uncertainty` | experiment, uncertainty |

The local roots carry separate domain facts. Each local fact selects a
`subject` and a `value`. Use `equation`, `regime`, `boundaries`,
`discretization` and `conservation` for dynamics; `system`, `energy_model`,
`ensemble`, `objective`, `approximation` and `validity` for molecular;
`operator`, `objective`, `result`, `assumptions` and `cost_model` for
algorithms. Optional facts have no fabricated empty values. The supported
complexity answer needs `result`, `assumptions` and `cost_model`.
A fact records the equation statement. The answer has `claim_kind: reported-equation`
where relevant. Each question names required facts; absent required facts
produce an explicit scope limitation. Each asserted label has a
stable subject reference. Enforce one label per subject within a
population so a display-name lookup has one answer. A conflicting pair
must produce the named uniqueness violation. Other constraints are added
only if a positive and named negative case require them.

The source record binds case, question, primary version and locator, the
local document's SHA-256 and span, reviewed support and the selected facts.
Original descriptions preserve legal redistribution. Use a short retained
primary quotation only when permitted and record the source locator
for it. Unanswerable rows retain the inspected primary section and reason.
Do not treat a signed digest or structure check as a semantic support
judgment. Check reviewed data against a separately frozen case evidence
inventory. Extending an inventory needs new reviewed evidence. Synthetic
score controls have their own explicit origin and no scientific claim.

Compare a frozen list of requested experiment pairs. Compare known values
for dataset version, split, metric, units and conditions first. A known
difference yields `incompatible` with its fields. If none differ and a
required value or score is missing, yield `unknown`. Otherwise yield
`comparable`. Baseline, configuration and uncertainty appear only as
source-supplied fields and configuration differences that affect the
comparison are included in conditions. Score cases include a control for
each field recognized by comparison.

Report `format: literature-depth/1`, `cases` with question rows
(`id`, `status`, `claim_kind`, `facts`, `evidence`), a `comparisons`
array, and exact artifact SHA-256 bindings. Question `status` is
`supported` or `unknown`. The question key is kept outside the runner's
inputs. The following case intents freeze the coverage floor:

| Area | Four questions |
|---|---|
| Clawpack dam break | Reported equation and regime. Outer boundary treatment. Solver and configuration. Whether the selected source reports a measured conservation residual. |
| OPES-eABF alanine | System and energy model. Sampling objective. Numerical approximation and run configuration. Whether the selected evidence establishes validity in a different solvent environment. |
| Randomized SVD | Operator and objective. Which two algorithm stages produce the approximation. Dense-input result with assumptions and cost model. Whether the selected evidence reports a runtime for a specified unreported device. |

## Decisions

| ID | Delegated disposition |
|---|---|
| D1 | Use three anchored source notes from the named primary versions and a separate reviewed support roster. |
| D2 | Keep comparison controls synthetic and independent of the source reports. Preserve one known-mismatch plus unknown control. |
| D3 | Probe all three LD2 axes. For dimension compare the reported step unit with a compatible time unit and incompatible energy unit. For percent compare an absolute difference between percentages with a relative change. For exact decimal try a native decimal numeric proof and verify its actual refusal or exact replay. Record the existing route and whether a gap affects a declared handoff. |
| D4 | Corpus-first. The fixtures and exact expected rows precede implementation. Optional spec panel omitted. |

## Tests and gate selection

| Control in `tests/test_ld1_competency_examples.py` | Expected result |
|---|---|
| Q1, packaged run and separate key | Exit 0 with all 12 rows, exact unknowns, intended positive facts and reported-equation classification. |
| Q2, tamper source or support | Exit 3 for a changed document, altered span or substituted source locator. A local note matching a fabricated answer cannot skip review bindings. |
| Q3, guarded bound | Remove assumptions and cost model separately. Each returns a limitation. |
| Q4, identity and relationships | Label change preserves reference ID. The three relation predicates remain distinguishable. |
| Q5, comparability | Same-context supported. Each dataset, split, metric, units or condition change yields incompatible. |
| Q6, missing and mixed | Missing required context yields unknown; a known difference with a missing peer yields incompatible. |
| Q7, model purpose | Conflicting labels for one ID produce the uniqueness violation through the public checker. |
| Q8, quantity trigger measurement | Report a measured dimension, percent distinction and exact decimal observation. Preserve each supported path or named refusal and record which scoped requirement needs it. |
| Q9, admission | Malformed, duplicate-key and capped input refuse before GND execution. Retain deterministic ordering when input and output errors coincide. |
| Q10, package and rebuild | Independent clean build with the installed wheel yields equivalent report and checks. |

Run `uv run pytest -q tests/test_ld1_competency_examples.py tests/test_lx1_flattening.py tests/test_li4_assertions.py tests/test_lx4_literature_interop.py --tb=short`
and the structural guard selection in the project hook for changed source.
Run whole-tree Ruff against pre-phase diagnostics and the strict component
gate. Run the built wheel in a fresh output directory. Retain ordinary
pytest marker filters and the existing reserved-suite cadence.

## Boundary and size

No provider call, proof of scientific truth, host-scale corpus or quantity
runtime change is part of LD1. Part 10 remains deferred. Estimated 250–350
source lines and 150–220 test lines, plus generated or authored fixture data.

## Approval instrument

Corpus-first using `tests/fixtures/ld1-competency/` with its own entry
README and separate expected file. Commit the expected acceptance corpus
red before product implementation. The phase ruling is delegated under the
owner's named milestone invocation and applies to this spec.

## Implementation findings

- The synthetic comparison initially produced a vacuous one-label
  constraint because its population had score facts and zero labels.
  The synthetic control now includes one labeled subject and the documented
  influence relation. The check then exited 0.
- GND's canonical JSON orders keys lexically. The frozen question key
  retains predicate membership and the test compares those members as a set.
- The existing integer anchor recognizer returns both the time and energy
  spans with magnitude 2. The percent recognizer returns 40 and 45 and
  excludes the percentage-point phrase. The example expresses score units
  and percentage-point uncertainty as distinct fields.
- The decimal Float population passes the checker. With the versioned
  target document and model-bound population, witness exits 2 and reports
  `fragment-unsupported`. A producer refusal with a malformed target or
  missing population binding would have measured input plumbing instead.
  These observations support opening dimension-aware anchors and exact
  decimal witness probes in LD2 after the LD1 review. They do not require a
  new percent recognizer for the present example.
- The output runner uses the existing capped process runner and shared JSON
  parser. The malformed comparison case exercises admission before the
  product invocations.

## Independent-review repairs

The one authorized review of `da41bc07` reproduced that the initial
Float control measured a blanket primitive refusal. A checked fractional
Number is the LD2 trigger observation. The integral Number probe produces
and replays a witness on the same route. The report derives the value from
the checked population and checks the target's value against it.

The dimension observation also inspects an equivalent ps span. It
recognizes the decimal token yet does not normalize it on the integer
route. The energy span still matches the integer magnitude. The percentage
observation now exercises an explicit absolute and relative change and
derives its disposition from the recognizer's results. A false point
recognition changes the trigger. The approved quantity scope follows these
corrected observations.

The question inventory's independent primary locators catch a retagged
citation even with a refreshed support digest. The checked population
supplies the subject occurrence coordinate. The added controls trace
the coordinate, move a component out of its predicate, and exercise
missing score independently of missing comparison context.
