# Python snapshot evaluation

Draft r1, 2026-11-27 · awaiting plan review and owner decisions · auto=false. The owner requested planning. No panel was selected or run. Completion requires the phase results below and a separate milestone-close ruling.

## 0. Binding design rules

Preserve redaction and per-target limits across envelopes, including malformed input. A failure before evaluation must never look like an empty successful check. Use existing loaders, ModelIndex for model queries and the defining component for policy. State validation order at each public boundary and test both sides of every refusal.

## 1. Scope, sources and authority

Issue requirements come from [#326](https://github.com/vasiloglou/gnd-public/issues/326), [#328](https://github.com/vasiloglou/gnd-public/issues/328), [#329](https://github.com/vasiloglou/gnd-public/issues/329), [#331](https://github.com/vasiloglou/gnd-public/issues/331), [#333](https://github.com/vasiloglou/gnd-public/issues/333), including their proposed changes and reproduction examples. Implementation baseline 83cd4170. The [predecessor close](../../incremental-evaluation/012-milestone-close.md) records the inherited capability and the limits of its evidence. These are framework features; a domain experiment census cannot establish API or evaluator behavior.

## 2. Proposed behavior

Normalize the supported snapshot envelopes and expose the CLI vacuity acceptance option to Python. Document inventory-grounded participation with empty and missing coverage.

Return requested derived rows, availability and findings from a single evaluation, with disclosure and size limits. Distinguish a complete empty extension from one that could not be computed.

Reuse loaded snapshot indexes across ordered why-not targets. Replay a fully grounded negative premise only with covered relations. Report per-target work and exhaustion.

Test shared dependency ranges against pinned builds and an independent host. Specify and exercise a versioned persistent local worker with repeated requests, structured errors and model invalidation.

## 3. Dependencies and artifact homes

PS2 and PS3 consume PS1 statuses. PS4 may measure dependency compatibility independently; the worker protocol freezes after the result and explanation contracts. Start with [src/gnd/api.py](../../../../src/gnd/api.py). The component index identifies `cli.api`, `check.service`, `checker.reports`, `witness.service`. Its November 27 review flagged 105 descriptions older than their source; resolve contract details against code and tests.

## 4. Obligations and completion criteria

| Phase | Issue and deliverable | Observable exit criterion |
|---|---|---|
| PS1 | [#333](https://github.com/vasiloglou/gnd-public/issues/333) [#331](https://github.com/vasiloglou/gnd-public/issues/331) Interpret snapshot reports | Normalize the supported snapshot envelopes and expose the CLI vacuity acceptance option to Python. Document inventory-grounded participation with empty and missing coverage. |
| PS2 | [#326](https://github.com/vasiloglou/gnd-public/issues/326) Return computed extensions | Return requested derived rows, availability and findings from a single evaluation, with disclosure and size limits. Distinguish a complete empty extension from one that could not be computed. |
| PS3 | [#328](https://github.com/vasiloglou/gnd-public/issues/328) Explain a batch | Reuse loaded snapshot indexes across ordered why-not targets. Replay a fully grounded negative premise only with covered relations. Report per-target work and exhaustion. |
| PS4 | [#329](https://github.com/vasiloglou/gnd-public/issues/329) Embed or isolate the evaluator | Test shared dependency ranges against pinned builds and an independent host. Specify and exercise a versioned persistent local worker with repeated requests, structured errors and model invalidation. |

The [first draft spec](phase-PS1-spec.md) expands PS1. Later specs follow the preceding decisions. Carry the predecessor’s documented limits into each new public claim.

## 5. Documentation and compatibility

PS1 owns the Python API reference and paired CLI example. PS2 and PS3 own disclosure tests and PS4 owns installation and worker lifecycle documentation. Start from [docs/reference/python-api.md](../../../../docs/reference/python-api.md). Run existing examples and compare the observable result for a caller using the previous interface.

## 6. Risks and controls

Preserve redaction and per-target limits across envelopes, including malformed input. A failure before evaluation must never look like an empty successful check. Vary identifiers, declaration order and input cardinality in the acceptance fixtures. Record work counters and the first refusal where limits apply.

## 7. Outside this milestone

Hosted network service and broad dependency upgrades. Release scheduling belongs to the owner.

## 8. Execution and review

Each phase needs its own spec and owner ruling, implementation, focused tests, independent diff review, refactoring review and numbered record. Plan and close require the project’s four-reviewer bar, recorded against the reviewed bytes. The owner selects the panel. Merge and release have separate authority.

## 9. Verification and baseline

Observed at intake: The issue fixtures exercise raw schemas 7, 12 and 14. A missing population exits 3 with zero failed constraints. A two-target why-not request is refused. The dependency metadata pins Pydantic 2.13.4.

Run the first spec’s focused selection and retain its verbatim pytest summary. For each later phase, use the issue reproduction and the criterion in §4 as an acceptance pair, pin the old behavior on unextended inputs and record the public entry point and result. Milestone closure requires a replay across phases, a disposition for each issue and an inventory of unverified claims. Native backend claims require native execution.

PS2: compare requested inferred rows to a hand-built extension from the #326 fixture; count evaluations, expecting one. Exercise a redacted role and a capped extension. PS3: replay two targets against one loaded snapshot and invalidate a negative witness when the blocked relation changes. PS4: execute two requests in one isolated process, force one invalid input, then evaluate a valid request; log request IDs, model identities and restart behavior. Lockfile reproducibility and shared-host installation are separate gates.

## 10. Open decisions

Approve the accessor name, response fields and unsupported-schema status. Decide the supported worker transport and dependency test matrix before PS4. These are proposals for the owner. Resolve the first-phase decision before implementation; later choices may remain open through earlier phases.
