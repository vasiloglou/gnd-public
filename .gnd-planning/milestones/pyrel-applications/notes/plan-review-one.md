# Plan review one — policy semantics and bounded compiler feasibility

Reviewed: 2026-10-13. Instrument: independently delegated local reviewer.

Subject: `.gnd-planning/milestones/pyrel-applications/notes/pyrel-applications-plan.md`

Exact reviewed SHA-256: `a001e5b87eaf55d4bc6763b918a5ec8f90a9a34d2c6655905cd420ea9f6ea735`.

Verdict: **pass for planning within this review scope**. No actionable plan
findings. This is advisory review, not owner acceptance or implementation/native
execution evidence.

## Evidence and assessment

- The stated omission is real: `src/gnd/export/pyrel_runtime.py:321` dispatches
  supported constraint families without guarded checking. The plan's PA1
  controls at `pyrel-applications-plan.md:183` require the three BookRec and seven
  expense guarded branches to produce native satisfied and violated witnesses.
  `src/gnd/examples/expense/model.orm.json:260`, `:352`, `:385`, `:418`, `:451`,
  `:484`, and `:517` contain those seven guarded rules. Observable consequence:
  merely rendering these policies cannot satisfy the planned acceptance gate.
- The complete BookRec model has a bounded acyclic derivation chain: blocked
  pairs use adult/minor asserted facts, then eligible pairs join preference and
  genre and exclude blocked/rated pairs
  (`src/gnd/examples/bookrec/complete.orm.yaml:155`, `:199`, `:216`). The existing
  independent fixture oracle orders acyclic heads and executes joins/projection/
  negation in native PyRel (`tests/oracles/pyrel_derivation_oracle.py:89`, `:156`,
  `:185`). This is credible static feasibility evidence for the restricted
  fragment. It is not native validation of the new application implementation.
  PA2 explicitly requires independent computation, negative-premise coverage,
  missing/extra claim comparisons and honest cycle/work refusals
  (`pyrel-applications-plan.md:195`).
- The legacy runtime admits relation rows without interpreting coverage
  (`src/gnd/export/pyrel_runtime.py:1082`) and reports constraint status without
  modality (`:1152`). The plan addresses both deficiencies: known empty versus
  unknown relations, warning versus blocking modality, uncovered antecedents/
  consequents and versioned acceptance are explicit obligations
  (`pyrel-applications-plan.md:62`, `:122`, `:160`, `:185`). Observable consequence:
  an unsupported, unknown or errored check cannot be promoted to acceptance,
  while the original advisory genre violation can publish visibly as a warning.
- PA0 defers exact grammar, schema, normalization and numerical/work ceilings
  to an owner-gated contract (`pyrel-applications-plan.md:158`, `:170`, `:410`).
  This is appropriate staging rather than an omitted implementation requirement.
  Implementation must still settle repeated/shared variable typing, duplicate
  semantics, numeric precision and boundary comparisons before claiming corpus
  agreement; the plan's typed-scalar, malformed-binding and bounded-corpus
  criteria already require that work (`:185`, `:208`, `:319`).
- Complete-set checking and limited recommendation proposals are separate
  product modes (`pyrel-applications-plan.md:219`), with omitted eligible output
  required to reject (`:223`). Existing application proposals illustrate the
  distinction (`src/gnd/examples/bookrec/extension/bookrec/library.py:28`, `:41`).
  The phase spec must preserve that distinction when fixing interfaces; no
  contradictory requirement to accept a truncated complete set is present.
- Policy acceptance and report arithmetic remain independent obligations
  (`pyrel-applications-plan.md:109`, `:240`). EUR-only evolution matches the
  shipped currency model's allowed value
  (`src/gnd/examples/expense/currency.orm.json:598`). The plan requires explicit
  currency labels and forbids implicit conversion or mixed totals.

## Findings

None. No suggested plan correction is required by this review. The remaining
exact interface and ceiling choices are named PA0 obligations, not inferred
approval for implementation.

## Scope limits

Read the entire plan and inspected all five named model variants, the shared
standalone runtime's admission/evaluation/report boundaries, BookRec and expense
application helpers, and the independent derivation fixture oracle and its
contract tests. This was static inspection only: no PyRel installation/execution,
provider call, product acceptance test, implementation edit or plan edit occurred.
No conclusion is made about rendered tutorial quality, package completeness,
security enforcement, runtime compatibility or performance. Other reviewer seats
must cover their assigned subjects; all phase and close gates remain outstanding.
