# DuckDB rule checking

Draft r1, 2026-11-27 · awaiting plan review and owner decisions · auto=false. The owner requested planning. No panel was selected or run. Completion requires the phase results below and a separate milestone-close ruling.

## 0. Binding design rules

Use a read-only engine transaction. Validate relation identifiers and projection types before executing a rule. Bound counterexample rows independently of scan size. Use existing loaders, ModelIndex for model queries and the defining component for policy. State validation order at each public boundary and test both sides of every refusal.

## 1. Scope, sources and authority

Issue requirements come from [#327](https://github.com/vasiloglou/gnd-public/issues/327), [#330](https://github.com/vasiloglou/gnd-public/issues/330), including their proposed changes and reproduction examples. Implementation baseline 83cd4170. The [predecessor close](../../pyrel-rules-coverage/007-milestone-close.md) records the inherited capability and the limits of its evidence. These are framework features; a domain experiment census cannot establish API or evaluator behavior.

## 2. Proposed behavior

Compile a guarded existential over a joint assignment and expose violating antecedent bindings.

Bind named fact roles to a read-only DuckDB snapshot and check uniqueness, inclusion and mandatory participation. Specify duplicate, NULL and type handling; include snapshot and projection identity.

Compare native and database verdicts over the same records, including missing tables, uncovered roles and bounded source keys. Exercise a real read-only database and the generated rules program before claiming backend parity.

## 3. Dependencies and artifact homes

DB1 and DB2 can be developed independently after their respective gates; DB3 needs both. Native execution requires the supported optional backend in a suitable environment. Start with [src/gnd/export/pyrel_rules.py](../../../../src/gnd/export/pyrel_rules.py). The component index identifies `export.pyrel_rules`, `check.service`, `check.constraint_families`. Its November 27 review flagged 105 descriptions older than their source; resolve contract details against code and tests.

## 4. Obligations and completion criteria

| Phase | Issue and deliverable | Observable exit criterion |
|---|---|---|
| DB1 | [#330](https://github.com/vasiloglou/gnd-public/issues/330) Correlated guarded existence | Compile a guarded existential over a joint assignment and expose violating antecedent bindings. |
| DB2 | [#327](https://github.com/vasiloglou/gnd-public/issues/327) Read-only relation bindings | Bind named fact roles to a read-only DuckDB snapshot and check uniqueness, inclusion and mandatory participation. Specify duplicate, NULL and type handling; include snapshot and projection identity. |
| DB3 | [#327](https://github.com/vasiloglou/gnd-public/issues/327) [#330](https://github.com/vasiloglou/gnd-public/issues/330) Backend parity | Compare native and database verdicts over the same records, including missing tables, uncovered roles and bounded source keys. Exercise a real read-only database and the generated rules program before claiming backend parity. |

The [first draft spec](phase-DB1-spec.md) expands DB1. Later specs follow the preceding decisions. Carry the predecessor’s documented limits into each new public claim.

## 5. Documentation and compatibility

DB1 owns the support matrix and generated-program example. DB2 owns relation-binding docs. DB3 records engine and adapter versions and end-to-end parity. Start from [docs/reference/capabilities.md](../../../../docs/reference/capabilities.md). Run existing examples and compare the observable result for a caller using the previous interface.

## 6. Risks and controls

Use a read-only engine transaction. Validate relation identifiers and projection types before executing a rule. Bound counterexample rows independently of scan size. Vary identifiers, declaration order and input cardinality in the acceptance fixtures. Record work counters and the first refusal where limits apply.

## 7. Outside this milestone

Other SQL engines and general SQL compilation. Release scheduling belongs to the owner.

## 8. Execution and review

Each phase needs its own spec and owner ruling, implementation, focused tests, independent diff review, refactoring review and numbered record. Plan and close require the project’s four-reviewer bar, recorded against the reviewed bytes. The owner selects the panel. Merge and release have separate authority.

## 9. Verification and baseline

Observed at intake: The guarded rule fixture passes native checking with an approved outcome and fails with an unrelated one. PyRel export currently refuses an existential consequent. A SQLite cursor is rejected by api.check.

Run the first spec’s focused selection and retain its verbatim pytest summary. For each later phase, use the issue reproduction and the criterion in §4 as an acceptance pair, pin the old behavior on unextended inputs and record the public entry point and result. Milestone closure requires a replay across phases, a disposition for each issue and an inventory of unverified claims. Native backend claims require native execution.

DB2: introduce a duplicate in a read-only database snapshot and compare against a checked materialized population from the same rows; also test missing projection, NULL, duplicate input and incompatible type. DB3: run the #330 good and bad populations against native GND and the generated DuckDB program. Compare verdict, affected binding and coverage; compilation alone cannot discharge this gate.

## 10. Open decisions

Approve the guarded fragment and native execution environment. DB2 must choose an explicit NULL mapping and transaction identity before accepting relation bindings. These are proposals for the owner. Resolve the first-phase decision before implementation; later choices may remain open through earlier phases.
