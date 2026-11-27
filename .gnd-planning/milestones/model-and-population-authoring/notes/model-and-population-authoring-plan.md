# Model and population authoring

Draft r1, 2026-11-27 · awaiting plan review and owner decisions · auto=false. The owner requested planning. No panel was selected or run. Completion requires the phase results below and a separate milestone-close ruling.

## 0. Binding design rules

Route every affected declaration through the same expansion before validation. Preserve file and rule identity across includes and keep regeneration safe for authored extensions. Use existing loaders, ModelIndex for model queries and the defining component for policy. State validation order at each public boundary and test both sides of every refusal.

## 1. Scope, sources and authority

Issue requirements come from [#332](https://github.com/vasiloglou/gnd-public/issues/332), [#334](https://github.com/vasiloglou/gnd-public/issues/334), including their proposed changes and reproduction examples. Implementation baseline 83cd4170. The [predecessor close](../../composition-and-type-induction/007-milestone-close.md) records the inherited capability and the limits of its evidence. These are framework features; a domain experiment census cannot establish API or evaluator behavior.

## 2. Proposed behavior

Expand opt-in file-level defaults with local precedence and field-origin diagnostics before ordinary model validation.

Specify an unambiguous shorthand for multi-clause rules and explicitly requested generated readings. Compare expanded structure and checker results against a fully written model.

Generate typed row readers and builders with role validation and explicit coverage. Round-trip a checked population and preserve existing generated callers across regeneration.

Admit declared composite roles with component access, structural identity and error paths. Preserve multi-role keys and entity reference schemes; exercise generated readers and rules together.

## 3. Dependencies and artifact homes

MA2 uses MA1 expansion. MA3 can start with existing scalars; MA4 needs the typed interfaces and a model-schema ruling. Coordinate scalar and compound encoding changes with exact-numeric-aggregates. Start with [src/gnd/model/_parsing.py](../../../../src/gnd/model/_parsing.py). The component index identifies `model.loading`, `model.validation`, `codegen.emit`, `codegen.manifest`. Its November 27 review flagged 105 descriptions older than their source; resolve contract details against code and tests.

## 4. Obligations and completion criteria

| Phase | Issue and deliverable | Observable exit criterion |
|---|---|---|
| MA1 | [#332](https://github.com/vasiloglou/gnd-public/issues/332) Constraint defaults | Expand opt-in file-level defaults with local precedence and field-origin diagnostics before ordinary model validation. |
| MA2 | [#332](https://github.com/vasiloglou/gnd-public/issues/332) Compact readings and clauses | Specify an unambiguous shorthand for multi-clause rules and explicitly requested generated readings. Compare expanded structure and checker results against a fully written model. |
| MA3 | [#334](https://github.com/vasiloglou/gnd-public/issues/334) Typed populations | Generate typed row readers and builders with role validation and explicit coverage. Round-trip a checked population and preserve existing generated callers across regeneration. |
| MA4 | [#334](https://github.com/vasiloglou/gnd-public/issues/334) Structured role values | Admit declared composite roles with component access, structural identity and error paths. Preserve multi-role keys and entity reference schemes; exercise generated readers and rules together. |

The [first draft spec](phase-MA1-spec.md) expands MA1. Later specs follow the preceding decisions. Carry the predecessor’s documented limits into each new public claim.

## 5. Documentation and compatibility

MA1 and MA2 own the input grammar and diagnostics. MA3 and MA4 own generated interfaces, regeneration checks and examples of compound keys. Start from [docs/reference/formats.md](../../../../docs/reference/formats.md). Run existing examples and compare the observable result for a caller using the previous interface.

## 6. Risks and controls

Route every affected declaration through the same expansion before validation. Preserve file and rule identity across includes and keep regeneration safe for authored extensions. Vary identifiers, declaration order and input cardinality in the acceptance fixtures. Record work counters and the first refusal where limits apply.

## 7. Outside this milestone

General YAML alias support and migration of all existing models. Release scheduling belongs to the owner.

## 8. Execution and review

Each phase needs its own spec and owner ruling, implementation, focused tests, independent diff review, refactoring review and numbered record. Plan and close require the project’s four-reviewer bar, recorded against the reviewed bytes. The owner selects the panel. Merge and release have separate authority.

## 9. Verification and baseline

Observed at intake: The model loader rejects file defaults and omitted readings. Generated constructors accept dictionaries in scalar roles that the checker subsequently rejects.

Run the first spec’s focused selection and retain its verbatim pytest summary. For each later phase, use the issue reproduction and the criterion in §4 as an acceptance pair, pin the old behavior on unextended inputs and record the public entry point and result. Milestone closure requires a replay across phases, a disposition for each issue and an inventory of unverified claims. Native backend claims require native execution.

MA2: validate two multi-clause spellings with nested terms and a generated reading, compare expanded roles, output and diagnostics against explicit declarations. MA3: generate, import, type-check and round-trip rows with an explicitly covered empty relation; rerun codegen over an authored extension. MA4: access a component in a rule, reject a wrong field type, and compare composite identity after field reordering. Keep existing entity and multi-role-key fixtures as controls.

## 10. Open decisions

Approve allowed defaults, provenance inheritance and include boundaries. Choose the structured-value wire shape before MA4. These are proposals for the owner. Resolve the first-phase decision before implementation; later choices may remain open through earlier phases.
