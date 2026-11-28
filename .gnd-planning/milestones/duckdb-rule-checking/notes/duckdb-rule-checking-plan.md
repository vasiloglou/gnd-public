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

## Delegated revision 2

DB1 accepts snapshot-only, asserted positive conjunctive consequent atoms with a connected join to the antecedent. Reject existential where, disconnected variables, plan operations, LQP lowering and unsupported inputs explicitly. Test the #330 model with matching, unrelated, covered-empty and absent approved values against the native GND checker; only project antecedent bindings. Preserve emitted bytes for an existing simple rule. Pin local PyRel 1.30.1 with Python 3.13 and DuckDB 2.0.1 for native program execution. A missing backend blocks the native exit gate.

DB2 introduces a separate Python entry point for an existing on-disk DuckDB database, a model and a declarative mapping from fact IDs to named base tables and role IDs to columns. Open the database read-only with external access disabled. Never accept caller SQL. Bind within one read transaction; only complete mappings of supported primitive-typed roles participate. Inventory coverage for mandatory participation must be explicit. Reject NULL in a bound role. Count distinct fact tuples under ordinary GND set semantics. Preserve duplicate physical input as data provenance where relevant. Identify the snapshot and normalized projection separately. Use typed, deterministic ordering with a caller-visible truncation flag and a default sample of 20, maximum 100; zero still computes the verdict. Set engine memory and wall time budgets; return a non-successful explicit refusal on exhaustion. Attempt a write using the same connection factory in a test, require refusal, and verify original data. Missing tables, partial projections, invalid types, unusual valid identifiers and NULL each require a test. DB2 will freeze the exact call and supported constraint shapes before implementation.

DB3 compares the GND Python checker, generated DuckDB PyRel program and direct database bindings on their advertised fragments. Compare per-constraint verdict, coverage status and normalized witness set on deliberately small complete fixtures. Compare deterministic sample and truncation separately for larger failures. Include pass/fail for each database rule family and include missing table, role, NULL, duplicates, coverage and witness limit. Retain exact tool versions, input and projection identities, exit codes and commands. Store reproductions under this milestone's evidence/DB1 to DB3, phase specs under notes/phase-ID-spec.md, and phase records at its root. Each phase checks real code against the component index and runs the strict changed-component check. Capture the public issue's relevant model as a fixture. Phase order is DB1, DB2 then DB3. The intake's stale-count estimate is historical and carries no verification weight.

DB2 correction after DB1. The native checker preserves physical copies of identical asserted facts for uniqueness. For example, the shipped basics_fail population returns two identical student/nickname facts as a full-key violation. Replace the earlier assumption of set semantics for uniqueness with physical-row multiplicity. Inclusion and mandatory remain membership checks. This evidence-based amendment has no separate panel opinion.
