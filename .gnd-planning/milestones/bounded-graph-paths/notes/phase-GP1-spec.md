# GP1 · Finite path enumeration

Awaiting owner review.

## 2. Provenance

[Plan r1](bounded-graph-paths-plan.md), §§0–10, based on main 83cd4170 and [#335](https://github.com/vasiloglou/gnd-public/issues/335). Draft dated 2026-11-27. Plan and spec have received no independent review.

## 3. Harvested obligations

| Source | Obligation | Discharge |
|---|---|---|
| Plan §4, GP1 | Implement a bounded simple-path counter over finite directed edges. Return a shortest example with a deterministic tie-break and explicit work consumption. | Design §6 and acceptance §8 |
| Plan §§0, 6 | Cap the number of edge examinations, retain prefix-local visited state, and order edges without relying on Python object ordering across unlike types. | Boundary cases in §8 and focused regression suite |
| Plan §§5, 9 | Preserve current caller behavior and document the new contract | Reference and compatibility control in §§6, 8 |

## 4. Standing rules as applied

The boundary under test is [src/gnd/graphs.py](../../../../src/gnd/graphs.py). Validate structural inputs before computing a result. Cap the number of edge examinations, retain prefix-local visited state, and order edges without relying on Python object ordering across unlike types. Use one traversal for all supported declarations or bindings. Compare the issue fixture and a differently named or reordered equivalent. The normative reference is [docs/reference/python-api.md](../../../../docs/reference/python-api.md). Record measured work in the fixture wherever a budget affects results.

## 5. Goal

Implement a bounded simple-path counter over finite directed edges. Return a shortest example with a deterministic tie-break and explicit work consumption. The focused selection exits 0 with every branch below exercised.

## 6. Design proposal

Proposed internal count_simple_paths(edges, source, target, *, max_hops, max_work, terminal_edges=()). Each edge has identity and two endpoints. Count edge sequences with a vertex-simple prefix, then optionally one distinct terminal edge. Order candidates by stable edge identity. Charge each considered edge before extending a prefix. At exhaustion return indeterminate with no exact count.

Reuse the existing components checker.evaluate, cli.api and add the contract to [docs/reference/python-api.md](../../../../docs/reference/python-api.md). Implement the change at the defining layer and retain existing public call paths. Baseline control: A diamond produces one reachability tuple for its two paths. Validation rejects an aggregate within the recursive dependency component.

`src/gnd/graphs.py` supplies existing graph utilities. Introduce a dedicated bounded path routine after confirming the required edge multiplicity and traversal order. Proposed exact results carry `count`, `shortest_edge_ids` and `work_used`; exhausted results carry status `indeterminate` and `work_used`. A disconnected covered graph returns count 0 and no example. Reject duplicate edge IDs before traversal; parallel edges with different IDs are legal.

## 7. Owner decisions

D1 (open). Approve edge-distinct multiplicity, whether an empty path counts, and whether max_hops includes the terminal edge. Proposed defaults exclude empty paths and include the terminal edge.

## 8. Tests and expected results

The diamond counts two and returns the lexicographically first shortest edge sequence regardless of input order. A cycle terminates; parallel IDs are distinct. A terminal self-loop can close the path once. Exactly sufficient budget yields a count, one less yields indeterminate. Cover absent endpoints and source equal to target.

Add the new cases in `tests/test_bounded_graph_paths_phase1.py`. Preserve [tests/test_derivation_rule.py](../../../../tests/test_derivation_rule.py) as an affected-consumer regression. Proposed command after implementation:

```sh
uv run pytest -q tests/test_bounded_graph_paths_phase1.py tests/test_derivation_rule.py --tb=short
```

Expected pytest exit 0. Compare the old public path on the same unchanged input and record its verdict or emitted bytes.

## 9. Phase boundary

Later phases own snapshot operation and evidence. Unbounded recursion and general recursive aggregation remains outside the milestone.

## 10. Size estimate

Estimated 120–240 source lines and 130–220 test lines. Measure the actual diff in the phase record.

## 11. Approval instrument

This draft and its case expectations are the proposed approval instrument. Record an owner decision on the plan and this spec before phase execution.
