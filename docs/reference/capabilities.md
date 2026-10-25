# What GND supports

GND combines a conceptual model, deterministic checks, and agent workflows
for building applications around explicit domain rules. Choose a capability
by the question you need to answer. The supported fragment differs between
checking, generation, measurement, and external exports.

The tutorials exercise local Python/CLI paths with synthetic public inputs.
An available command is not by itself a measured support claim for every
operating system, Python version, provider, or native toolchain. See the
[compatibility policy](../compatibility.md) for release support.

## Capabilities by task

| Task | Supported surface | Principal boundary | Start here |
|---|---|---|---|
| Describe a domain and its rules | ORM YAML/JSON; guided text-to-model skill; readable verbalization | A person reviews requirements and inferred constraints | [Modeling](../guides/modeling.md) |
| Validate a model | CLI `validate`; `api.validate` | Valid syntax/semantics do not establish complete requirements | [Python API](python-api.md) |
| Check candidate facts | `check`; `api.check`; admission projection | Checks supplied facts and declared coverage; no automatic repair | [Quickstart](../quickstart.md) |
| Explain supplied facts | `verbalize population`; `api.verbalize` | Deterministic sentences are not a truth judgment | [Python API](python-api.md) |
| Compute derived relations | Structured clauses, joins, supported exact terms, stratified negation, recursion and aggregates | Resource bounds and construct-specific validation apply | [Data and transitions](../guides/data-and-transitions.md) |
| Check calendar deadlines | Date/Duration guarded comparisons | Calendar days only; no live clock, timezones, or business calendar | [Data and transitions](../guides/data-and-transitions.md) |
| Use a fixed catalog | Version-4 reference populations with path and byte-hash binding | Candidate/reference fact ownership is disjoint | [Data and transitions](../guides/data-and-transitions.md) |
| Audit an operation walk | `check --pre --steps --post`; `api.transition` | Frame checks cover the walk's touched fact types | [Python API](python-api.md) |
| Reuse a checked pre-state | `api.check_with_receipt`; `api.transition(pre_receipt=...)` | In-process, default options; only the pre-state check is skipped | [Python API](python-api.md#reusing-a-checked-pre-state) |
| Recheck related snapshots | `api.EvaluationSession` | Explicit loaded-input session; conservative fresh fallback, one bounded generation, full snapshot validation | [Python API](python-api.md#reusing-evaluation-work-across-snapshots) |
| Incorporate host observations | `EvaluationSession.observe`, `check_with_feedback` | Validated relation replacement; counts are diagnostic, not external truth; separate in-process feedback wire | [Host loop](../agents/dev-session.md#a-host-loop-in-one-python-process) |
| Generate a Python project | `codegen` plus explicitly selected skill | Developer writes extension behavior; temporal models refused | [Generated projects](../guides/generated-projects.md) |
| Detect model/project drift | `conformance`; static architecture checks | Does not execute the app or verify all extension behavior | [Generated projects](../guides/generated-projects.md) |
| Change an existing model | Staged `evolve preview/apply/finalize` | Explicit reviewed changes; no automatic regeneration | [Evolution](../guides/evolution-and-recovery.md) |
| Discover rules in data | `discover` over one population | Proposes induced, advisory rules only; admission is a reviewed evolve step; single-role families, stated bounds | [Discovery](discover.md) |
| Recover a model from code | Bounded `recovery inventory/verify` and authoring skill | One-time static selected roots; no continuous synchronization | [Recovery](../guides/evolution-and-recovery.md) |
| Compare compatible models | `diff`; `api.diff` | Same vocabulary; bounded entailment catalogue and concrete populations; no temporal models | [Python API](python-api.md) |
| Exercise rule behavior | `synth`, `measure` | Optional synth dependency; generation is narrower than checking | [Synthetic data](../guides/synthetic-data.md) |
| Extract and check document facts | Offline extraction bundle, agent skill, `verify`, source anchors | Agent performs extraction; checking is distinct from fidelity | [Documents](../guides/documents.md) |
| Render evaluation documents | Agent rendering skill, `doccheck`, `fidelity` | Bound manifests and distractors; fidelity remains a separate measured claim | [Documents](../guides/documents.md) |
| Run a bounded agent experiment | `exp` commands and selected adapter/policy | Requires authored contract; live adapter prerequisites are separate | [Experiments](../guides/experiments.md) |
| Evaluate saved external opinions | `judgments check`; explicit session judgment gate | Consumes receipts; does not obtain opinions or calibrate providers | [Experiments](../guides/experiments.md) |
| Explain a finite derived tuple | `witness`, `replay`, `witness-view`; API witness/replay | Selected positive proof fragment, not extension completeness | [Exports](../guides/exports.md) |
| Export to external runtimes | Bounded Souffle/Lean/PyRel profiles | Export, native execution, compilation and proof are distinct | [Exports](../guides/exports.md), [worked native guides](../runtimes/scenario.md) |
| Review a plan or result | Explicit advisory review-panel skill and CLI | Live tools/credentials; reviewer findings do not apply fixes | [Exports and a second opinion](../agents/export-and-review.md) |

## Constraint coverage

| Family | What checking supports |
|---|---|
| Uniqueness | Internal role combinations and external identifiers |
| Mandatory | Individual roles and inclusive-or participation over the declared instance set |
| Values | Enumerations, ranges, multiple ranges and supported role-scoped forms |
| Frequency | Internal and external occurrence bounds |
| Relational inclusion | Subset and equality over declared role sequences |
| Exclusion and partitions | Exclusion; exclusive-or, with only the exclusion component for multi-role sequences |
| Ring properties | Thirteen variants; each has its own local relation semantics |
| Comparison | Supported typed comparisons; current-time operands remain unchecked |
| Cardinality | Object and role counts |
| Subtype partition | Checks when required membership is observable; otherwise unchecked |
| Guarded rules | Bound antecedents with supported relation, comparison or absence consequences |
| Source anchoring | Bound document spans and supported lexical/numeric/date matching |
| Textual requirements | Preserved, but reported unchecked by the deterministic checker |

The [constraint reference](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/constraint-reference.md)
is the detailed authority for syntax and semantics. “Supported” does not mean
every downstream tool accepts every combination of these constructs.

## Compatibility between feature families

Temporal models currently work in validation and documented check/transition
surfaces, including the packaged dispatch admission example. They are refused
by synth, measure, codegen, conformance, diff, extraction, document checking,
and the existing PyRel exporter. Date values alone do not necessarily select
temporal arithmetic; `Duration` and temporal terms do.

Native proof/export profiles have separate restrictions. The witness lane
does not admit negation or aggregates; Souffle exports exclude constraints
and operations; Lean uses a selected finite acyclic fragment. Unsupported
input is not silently converted to a successful partial export.

## What an application still provides

GND does not supply a hosted application, database, UI, deployment service,
universal optimizer, or recommender ranking-quality guarantee. Your code
decides how to obtain facts, propose outputs, persist state, and present
findings. The model states what those outputs must satisfy.

Mechanical verdicts, model/project conformance, experiment acceptance,
extraction fidelity, advisory review, and formal assurance are different
results. A pass in one does not automatically confer the others. Missing or
stale assurance evidence remains unavailable; the documentation tutorials
do not perform certification or recertification.
