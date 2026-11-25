# Phase SI2 — reference identity selection

## 1. Status

Approved by delegated ruling on 2026-11-25.
The [SI1 completion record](../002-phase-SI1.md) precedes implementation.

## 2. Provenance

Issue #279, approved plan r2 §0, §2, §4, §6, §8–10, and Ossie relational
bundle record 022. Measurements use the tracked model set at `99cf3df2`.
Rmap's functional-key rules remain its separate contract.

## 3. Obligations

| Obligation | Discharge |
|---|---|
| SI2-C1 / D2 / R2, per-caller measurements over tracked and built models | Census and fixture outcomes below. |
| SI2-C2, discriminating red fixtures, unchanged callers pinned | Add the proposed/nonpreferred/deontic, tie, fallback, and affected-consumer controls below. |
| SI2-C3 / RC-04, counted query budget and map ruling | Keep the compatibility lookups on the existing budget. Run the exact static and dynamic query guards without changing their allowlists. |
| §5 and §9 | Add the release note and run focused refscheme, verbalization, vocabulary, applicability, shapes, and guidelines checks. |

## 4. Standing rules

Selection reads the loaded constraint records and resolves them with the
existing structured role join. The direct-reference resolver stays first.
Compatibility and tie policy live in `reference_identity` and the reference
scheme section of the representation format. The work adds no raw document
intake, runtime query sites, wire fields, tag action, or claim about Rmap
outputs. A bounded synthetic multi-key control checks the added candidate
scan.

## 5. Goal

Choose the preferred confirmed alethic anchored external uniqueness where
present. The previous first-anchored resolution is the fallback. Both paths
continue to report the same failure if the chosen identifier cannot be
grounded. Tracked model identity output remains byte-equivalent where the
callers emit bytes.

## 6. Design

Reuse the reference lookup component (`reference scheme`, `composite
identity`) and the confirmed-alethic predicate in `gnd.rmap`. Apply the
status preference only after identifying an anchored external uniqueness.
A declaration order distinction exists only in the legacy fallback. Among
qualifying keys compare sorted `(fact_type, role)` pairs lexicographically,
then the original role-ref sequence, preserving component order in output.
This is the Rmap tie ordering; Rmap's functionality, stored-extension and
objectification tests remain specific to relational key placement.

Keep the compatibility maps for this change. Their counted query sites
already exist and the shared API accepts model-like inputs as well as
validated `Model`. Reuse one lookup table for all anchor checks in an
identity selection. Changing those semantics and their query inventory is not
required to select the right constraint. The focus gate pins the remaining
direct resolver and both legacy and preferred caller behavior.

### Tracked model measurement

The census evaluated all object identities on 436 loadable tracked
`*.orm.yaml` and `*.orm.json` files. The current selection produced nine
composites. A stable priority sort of top-level constraints simulated
preferred confirmed alethic with a legacy fallback; every identity and
component sequence stayed equal. Since none of the tracked models has
competing qualifying constraints, the chosen tie rule cannot change a tracked
output. Keeping first-declared also changes zero, and leaves the reported
case unresolved.

For the Rmap alternative, replacing only the composite-selection behavior
removed the three composites the plan names. It also made ten formerly
unmatchable entities composite. The applicability change for every one of
these is measured alongside the actual caller outputs.

| Model | Entities changed by the Rmap alternative | Consumers with changed output |
|---|---|---|
| `src/gnd/examples/literature/assertions/model.orm.yaml` | assertion | Model verbalization, extraction vocabulary, applicability, evolve shape references, extraction guidelines |
| `src/gnd/examples/literature/lineage/model.orm.yaml` | assertion | Same five |
| `src/gnd/skills/gnd-model-from-text/examples/reference_scheme_elicitation.orm.yaml` | task | Same five |
| `src/gnd/skills/gnd-model-from-text/examples/objectification_in_enrollment.orm.yaml` | enrolment | Applicability |
| `tests/fixtures/checker/setfam.orm.yaml` | booking | Applicability |
| `tests/fixtures/coverage/positional/library.orm.yaml` | copy, circulating_copy, reference_copy | Applicability, evolve shape references |
| `tests/fixtures/models/dispatch.orm.yaml` | delivery | Applicability |
| `tests/fixtures/models/full_vocabulary.orm.yaml` | assignment | Applicability |
| `tests/fixtures/models/library.orm.yaml` | copy, circulating_copy, reference_copy | Applicability, evolve shape references |

This extends the plan §1 count, which compared only the nine previously
composite entities. Carry the ten newly selectable composites to the
milestone plan repair ledger. Reading C changes none of the rows.

### Built inputs

Use the task model's existing reference coordinates, a second external
uniqueness over assignment employee and task name, and a task uniqueness
on the project fact so both relational functions can select a key. All
models pass the ordinary loader.

| First matching declaration | Legacy result | Preferred plus fallback |
|---|---|---|
| Nonpreferred assignment key, then preferred project key | Assignment | Project |
| Proposed preferred assignment key, then confirmed project key | Assignment | Project |
| Confirmed deontic preferred assignment key, then confirmed alethic project key | Assignment | Project |
| Both qualify, project first | Project | Assignment by the sorted role pair tie rule |
| Both qualify, assignment first | Assignment | Assignment with the same component order |
| Neither qualifies | First anchored declaration | First anchored declaration |

For the first three cases Rmap selects project, and for the tie it selects
assignment. For the no-eligible control, Rmap has no eligible composite.
The legacy fallback resolves the first matching anchor. Inspect the
same fixture through model verbalization, vocabulary, and applicability and
confirm guidelines and evolve retain composite kind without collapsing the
ordered components returned by reference identity.

## 7. Decisions

D2 selects reading C (preferred confirmed alethic, otherwise first) with
lexical tie order. The per-caller impact of applying Rmap separately is
listed above. Since reading C maintains shipped outputs, the plan authorizes
the delegated ruling. Independent review uses Claude Code Opus per the
owner's selection on SI1.

## 8. Tests

Author `tests/test_si2_reference_identity.py` first and observe all three
preference cases and reverse tie red on the base. Pin the fallback and
unchanged direct path, all downstream output checks, and the existing
model-index query guards. Run the relevant model verbalization, vocabulary,
applicability, extraction guidelines and shape matching tests, alongside lint
and the component index change gate.

## 9. Out of scope

Rmap key selection, Ossie ontology output, lifecycle rewriting and release.

## 10. Size

Approximately 35 production lines and 100 test lines. Stop at twice these
estimates if a larger design is needed.

## 11. Approval instrument

Spec and executable fixture expectations. The issue alters semantic selection
within an existing in-process return shape. The executable cases separate
the choices and record the losing baseline behavior before implementation.

### Preimplementation evidence

The census script and baseline machine output are in
[evidence/SI2](../evidence/SI2/). The query processed 503 tracked paths
with 436 valid models, 67 load refusals, and zero competing qualifying
declarations. Its aggregate digest covers the complete pre-change
reference-identity outputs over the loadable models.

The preimplementation gate ran
`.venv/bin/pytest -q tests/test_si2_reference_identity.py --tb=short`
at `5699c76a` and exited 1 with `5 failed, 2 passed in 0.42s`.
All preference cases and the reverse tie chose the first declaration;
the timing case likewise chose the wrong declaration, and the forward
tie and compatibility fallback controls passed.

Delegated approval (auto=true), 2026-11-25. Approved this SI2 spec through
the preimplementation evidence at SHA-256 `f4b1802ee78787be9c52f7f3f8f7060837638cce0fea7a56acf616bf767cb24f`. Source: the owner renewed
the milestone delegation in the D1 message. Scope: D2 reading C with the
stated tie, the observed compatibility results, and the focused phase gates.
Instrument: spec and executable case expectations. Review budget: one phase
diff review with the owner's selection of Claude Code Opus, and a second
only over repairs if needed. The confirmed tracked outputs remain equal.

### Review clarification, 2026-11-25

F1: the five-red/two-green gate above measured the first seven cases.
The same-role-set tie was added before the diff review. Re-run against the
archived baseline source with the complete eight-case selection: **6 failed,
2 passed, 2 deselected in 0.56s**. The two deselected cases are the review
regressions. The additionally red case is the reversed component sequence
over an identical role set.

F2: a selected but unresolvable preferred key yields `unmatchable`. The
legacy fallback covers only absence of a qualifying key. The normative
paragraph and nested-composite fixture now pin that behavior. The reviewer
reproduced the case on a valid model.

F3: the five-second timing case checks a bound at one input scale. The
record makes no linearity inference from that measurement.

Delegated clarification (auto=true), 2026-11-25. Approved the review
clarification through the preceding paragraph at SHA-256 `fadf80f330392861fd2ee037f9dab3e45047f608d96f0228a9e5e1c0c5bc9b68`.
Source: renewed milestone delegation. Scope: test ledger and normative
clarification, preserving D2. Instrument: the first independent phase
review and the focused red and green controls. One review round.
