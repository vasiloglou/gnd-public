# Bounded graph paths

Draft r1, 2026-11-27 · awaiting plan review and owner decisions · auto=false. The owner requested planning. No panel was selected or run. Completion requires the phase results below and a separate milestone-close ruling.

## 0. Binding design rules

Cap the number of edge examinations, retain prefix-local visited state, and order edges without relying on Python object ordering across unlike types. Use existing loaders, ModelIndex for model queries and the defining component for policy. State validation order at each public boundary and test both sides of every refusal.

## 1. Scope, sources and authority

Issue requirements come from [#335](https://github.com/vasiloglou/gnd-public/issues/335), including their proposed changes and reproduction examples. Implementation baseline 83cd4170. The [predecessor close](../../aggregate-count-certificates/006-milestone-close.md) records the inherited capability and the limits of its evidence. These are framework features; a domain experiment census cannot establish API or evaluator behavior.

## 2. Proposed behavior

Implement a bounded simple-path counter over finite directed edges. Return a shortest example with a deterministic tie-break and explicit work consumption.

Bind edge and optional terminal relations to a snapshot. Return coverage, count and example or an indeterminate result. Exercise cycles, parallel edges and a terminal return or self-loop.

## 3. Dependencies and artifact homes

GP1 is independent of numeric aggregates. GP2 consumes its result and the existing coverage/disclosure conventions. A standalone path example carries no derivation certificate. Start with [src/gnd/graphs.py](../../../../src/gnd/graphs.py). The component index identifies `checker.evaluate`, `cli.api`. Its November 27 review flagged 105 descriptions older than their source; resolve contract details against code and tests.

## 4. Obligations and completion criteria

| Phase | Issue and deliverable | Observable exit criterion |
|---|---|---|
| GP1 | [#335](https://github.com/vasiloglou/gnd-public/issues/335) Finite path enumeration | Implement a bounded simple-path counter over finite directed edges. Return a shortest example with a deterministic tie-break and explicit work consumption. |
| GP2 | [#335](https://github.com/vasiloglou/gnd-public/issues/335) Snapshot operation and evidence | Bind edge and optional terminal relations to a snapshot. Return coverage, count and example or an indeterminate result. Exercise cycles, parallel edges and a terminal return or self-loop. |

The [first draft spec](phase-GP1-spec.md) expands GP1. Later specs follow the preceding decisions. Carry the predecessor’s documented limits into each new public claim.

## 5. Documentation and compatibility

GP1 owns edge identity and counting semantics. GP2 owns the public API, disclosure of example edges, work limits and a runnable diamond example. Start from [docs/reference/python-api.md](../../../../docs/reference/python-api.md). Run existing examples and compare the observable result for a caller using the previous interface.

## 6. Risks and controls

Cap the number of edge examinations, retain prefix-local visited state, and order edges without relying on Python object ordering across unlike types. Vary identifiers, declaration order and input cardinality in the acceptance fixtures. Record work counters and the first refusal where limits apply.

## 7. Outside this milestone

Unbounded recursion and general recursive aggregation. Release scheduling belongs to the owner.

## 8. Execution and review

Each phase needs its own spec and owner ruling, implementation, focused tests, independent diff review, refactoring review and numbered record. Plan and close require the project’s four-reviewer bar, recorded against the reviewed bytes. The owner selects the panel. Merge and release have separate authority.

## 9. Verification and baseline

Observed at intake: A diamond produces one reachability tuple for its two paths. Validation rejects an aggregate within the recursive dependency component.

Run the first spec’s focused selection and retain its verbatim pytest summary. For each later phase, use the issue reproduction and the criterion in §4 as an acceptance pair, pin the old behavior on unextended inputs and record the public entry point and result. Milestone closure requires a replay across phases, a disposition for each issue and an inventory of unverified claims. Native backend claims require native execution.

GP2: project a model-bound directed edge relation and exercise disconnected, covered-empty and uncovered cases. Reverse input order and retain the same shortest edge sequence. Test the maximum-hop and work cutoffs separately. Check that disclosure policy governs every node and edge identifier in the example.

## 10. Open decisions

Approve edge-distinct multiplicity, whether an empty path counts, and whether max_hops includes the terminal edge. Proposed defaults exclude empty paths and include the terminal edge. These are proposals for the owner. Resolve the first-phase decision before implementation; later choices may remain open through earlier phases.
