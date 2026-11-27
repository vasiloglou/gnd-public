# Exact numeric aggregates

Draft r1, 2026-11-27 · awaiting plan review and owner decisions · auto=false. The owner requested planning. No panel was selected or run. Completion requires the phase results below and a separate milestone-close ruling.

## 0. Binding design rules

Bound cardinality and numeric bit growth separately. Never parse exact decimals through binary64 or turn uncovered input into a zero. Use existing loaders, ModelIndex for model queries and the defining component for policy. State validation order at each public boundary and test both sides of every refusal.

## 1. Scope, sources and authority

Issue requirements come from [#336](https://github.com/vasiloglou/gnd-public/issues/336), including their proposed changes and reproduction examples. Implementation baseline 83cd4170. The [predecessor close](../../aggregate-count-certificates/006-milestone-close.md) records the inherited capability and the limits of its evidence. These are framework features; a domain experiment census cannot establish API or evaluator behavior.

## 2. Proposed behavior

Evaluate count over a declared finite catalog of groups including members with zero contributions.

Introduce opt-in decimal and rational encodings with lossless parsing, equality, canonical grouping and output. Pin legacy Number identity independently.

Implement non-integer sums and specified conversions to binary64. Compare exact results across validation, checking and serialization and enforce operand/result work and size bounds.

## 3. Dependencies and artifact homes

NA1 can ship with integer counts. NA2 fixes identity before NA3 arithmetic. Coordinate changes to value parsing with MA4 without making new codegen a prerequisite. Start with [src/gnd/extensions.py](../../../../src/gnd/extensions.py). The component index identifies `checker.evaluate`, `model.validation`. Its November 27 review flagged 105 descriptions older than their source; resolve contract details against code and tests.

## 4. Obligations and completion criteria

| Phase | Issue and deliverable | Observable exit criterion |
|---|---|---|
| NA1 | [#336](https://github.com/vasiloglou/gnd-public/issues/336) Explicit count domains | Evaluate count over a declared finite catalog of groups including members with zero contributions. |
| NA2 | [#336](https://github.com/vasiloglou/gnd-public/issues/336) Exact scalar identity | Introduce opt-in decimal and rational encodings with lossless parsing, equality, canonical grouping and output. Pin legacy Number identity independently. |
| NA3 | [#336](https://github.com/vasiloglou/gnd-public/issues/336) Non-integer aggregates | Implement non-integer sums and specified conversions to binary64. Compare exact results across validation, checking and serialization and enforce operand/result work and size bounds. |

The [first draft spec](phase-NA1-spec.md) expands NA1. Later specs follow the preceding decisions. Carry the predecessor’s documented limits into each new public claim.

## 5. Documentation and compatibility

NA1 owns group-domain grammar. NA2 owns wire identity and conversions. NA3 owns result semantics, examples and legacy parity checks. Start from [docs/reference/formats.md](../../../../docs/reference/formats.md). Run existing examples and compare the observable result for a caller using the previous interface.

## 6. Risks and controls

Bound cardinality and numeric bit growth separately. Never parse exact decimals through binary64 or turn uncovered input into a zero. Vary identifiers, declaration order and input cardinality in the acceptance fixtures. Record work counters and the first refusal where limits apply.

## 7. Outside this milestone

Changing legacy Number arithmetic or existing certificate scope. Release scheduling belongs to the owner.

## 8. Execution and review

Each phase needs its own spec and owner ruling, implementation, focused tests, independent diff review, refactoring review and numbered record. Plan and close require the project’s four-reviewer bar, recorded against the reviewed bytes. The owner selects the panel. Merge and release have separate authority.

## 9. Verification and baseline

Observed at intake: An explicit zero count fails on a catalog member with no readings. Float sum is refused, and two distinct decimal tokens in the issue fixture collapse under Number identity.

Run the first spec’s focused selection and retain its verbatim pytest summary. For each later phase, use the issue reproduction and the criterion in §4 as an acceptance pair, pin the old behavior on unextended inputs and record the public entry point and result. Milestone closure requires a replay across phases, a disposition for each issue and an inventory of unverified claims. Native backend claims require native execution.

NA2: load 9007199254740992.01 and 9007199254740992.02 as distinct exact values and round-trip them through the public writer. Pin decimal/rational equality and coercion with mixed legacy values before arithmetic. NA3: exercise 0.1 + 0.2, a rational third, native Float sum under its documented precision, bit-limit exhaustion and explicit conversion to binary64. Keep legacy Number fixtures and existing aggregate certificate checks as regressions.

## 10. Open decisions

Approve domain syntax and treatment of contributing keys absent from the catalog (proposed exclusion). Before NA2 choose exact wire encodings and conversion/rounding rules. These are proposals for the owner. Resolve the first-phase decision before implementation; later choices may remain open through earlier phases.
