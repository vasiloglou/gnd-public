---
milestone: compiled-snapshot-obligations
station: phase-CS2
skill: process-phase
scope: phase-CS2
date: 2026-10-13
gate:
  command: "uv run pytest -q tests/test_compiled_snapshot_obligations.py tests/test_public_api.py tests/test_schema_sync.py tests/test_model_v2.py tests/test_public_transition_contract.py tests/test_public_transition_trace.py tests/test_v61_phase1_batch.py tests/test_rf1_layering.py tests/test_v6_phase2_registry.py tests/test_public_redaction_reports.py tests/test_public_reference_signatures.py tests/test_rf5_review_regressions.py --tb=short"
  exit: 0
  output: "215 passed in 26.69s; 215 passed in 25.80s"
slow_cadence:
  command: uv run pytest -q -ra --tb=short
  trigger: explicit owner selection or separately scoped CI
  reason: trace/schema/docs and selected consumers are bounded gates
---

# Claim

Trace identifies snapshot activation and walk-only boundaries. The bounded API,
single CLI and batch recipe reports the named issue failure. Public normalized
exit/count/failing-reference fields agree for 2/2 fixture populations.

## What shipped and evidence

Canonical ORM text and synchronized schema descriptions qualify default snapshot
semantics; public API/transition docs show the activation syntax and boundaries.
Trace's required model/operations digests and retained reasons remain intact.
The selected gate and work-limit, identity, redaction, reference, default and
transition-only controls are retained by CS1. evidence/CS2/agreement.json names
its denominator, inventory and public-output limitation.

## Gate output

    215 passed in 26.69s
    215 passed in 25.80s
    2/2 populations agree in exit, counts and failed-constraint identities.

## Refactoring review

None needed: this phase changes explanations and trace activation text, with
canonical semantics in one packaged reference and synchronized schema copies.

## Boundary

No per-passing/per-warning batch identity claim, full-walk equivalence, external
app M3 run, hosted documentation build, publication or certificate. Snapshot
checking cannot establish intermediate states, dynamic step rules or frames.
The explicit occurrence-admission limitation remains. No milestone close claim.

## Open questions

App owner must opt into compiled_operations=True / --compiled-operations and run
its own exact M3 gate after merging this candidate. Occurrence admission support
belongs to a successor. Pending plan/close review history is superseded only for
the owner's selected local plan instrument; milestone close still owns its own
question sweep and review. Existing authority carryovers remain unchanged.

## Artifact identities

- .gnd-planning/milestones/compiled-snapshot-obligations/notes/phase-CS1-spec.md: d13e5342777536fcfa10f4373412a14ab7f2cb634f9091c268be68748d8a6df4
- .gnd-planning/milestones/compiled-snapshot-obligations/notes/phase-CS2-spec.md: 165cf26ab5f6556cfd1f8bbae1980c0909bd0a6922cfd977bb1f0f2d33673455
- .gnd-planning/milestones/compiled-snapshot-obligations/notes/phase-CS1-review-four.md: bd3ad4ff6bad448c9c284c95b0d33f76f69061560fb06780794337badb428995
- .gnd-planning/milestones/compiled-snapshot-obligations/notes/phase-CS1-review-one.md: 62b77ee38e22ec170b206ae6210ef4c990a95a03f8c499c62c180d0c3235bb32
- .gnd-planning/milestones/compiled-snapshot-obligations/notes/phase-CS1-review-two.md: c41947c8173925d406e2a3abe83d9dc759c9061726684fd810567ca8739b297b
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CS1/focused-311.txt: 9bf74db7b25660e3a477fde7bdc01339d364427146569abd4cab79feffa37b25
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CS1/focused-313.txt: e8c11fc60e99038caafa30ca7d8e68fdcd3da5b50b16a6429dd096e5d6be516e
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CS1/review-four-mutation-probe.py: 9778eafd036cbdf03a41e00881c97b702ea87f06a74d22097d3ac27dc345c025
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CS1/review-four-probe.py: 9d08085962edf1fda79a84de7f9ea7d06943962999346e596afcd9d46ecfbfda
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CS2/agreement.json: eab3dc3c895b8cf2072a6baab7c770e46d0110651663f85a35e7cae526a44270
- src/gnd/compiled_obligations.py: 4fd2940c1cb05f94ee9f6e76709fa6e37d7ab0cc4a41506bef9552cb45253a3c
- tests/test_compiled_snapshot_obligations.py: b876ce526c0952e09a3381ab846e67314ee07f9db17e1bd5390b7425312919d5
