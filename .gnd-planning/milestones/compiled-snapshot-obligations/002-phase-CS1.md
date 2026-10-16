---
milestone: compiled-snapshot-obligations
station: phase-CS1
skill: process-phase
scope: phase-CS1
date: 2026-10-13
gate:
  command: "uv run pytest -q tests/test_compiled_snapshot_obligations.py tests/test_public_api.py tests/test_schema_sync.py tests/test_model_v2.py tests/test_public_transition_contract.py tests/test_public_transition_trace.py tests/test_v61_phase1_batch.py tests/test_rf1_layering.py tests/test_v6_phase2_registry.py tests/test_public_redaction_reports.py tests/test_public_reference_signatures.py tests/test_rf5_review_regressions.py --tb=short"
  exit: 0
  output: "215 passed in 26.69s; 215 passed in 25.80s"
slow_cadence:
  command: uv run pytest -q -ra --tb=short
  trigger: explicit owner selection or separately scoped CI
  reason: focused runtime impact closure; broad replay was not reselected
---

# Claim

The approved opt-in API/single/batch checks report the missing numeric-role failure.
The complete selected gate passes on Python 3.11 and 3.13. Defaults remain outside
operation checking. Every public compiled result carries assurance level none.

## What shipped

Shared typed indexed matching serves compiled snapshots and existing walks.
Snapshot mode retains computed uncertainty and compiler guards, uses a counted
100,000 projected-cell ceiling and qualified source references. Current operation
edits are recompiled without mutating model documents or historical side tables.
API/service/checker/batch/CLI activation preserves default routes. Occurrence
admission and walk combinations refuse explicitly. Witness redaction resolves
fresh compiler locators. All added module homes retain zero layer allowances.

## Owner decisions

Delegated auto=true under the structured approval recorded in CS0. CS1/CS2 specs
were authored before runtime writes. The corpus-first red commit is b57046f.
Current declarations, conservative uncertainty and admission refusal are explicit
agent rulings in the specs, not a claim of human reading of successor bytes.

## Gate output (verbatim summaries)

    215 passed in 26.69s
    215 passed in 25.80s
    All checks passed!

The first two streams are retained in evidence/CS1/focused-311.txt and focused-313.txt.
The logged argv were the gate above via isolated UV_PROJECT_ENVIRONMENT values
under /private/tmp/gnd-issue16-audit/venv and venv313, using uv 0.10.10.
Ruff checked all changed source/test files; git diff --check exited 0.

## Review

Three independent local same-model diff readers contributed bounded observations;
one reviewer is one reviewer. Their retained verbatim notes describe their scopes,
reproductions and repairs; this is not a maintained vendor panel or certificate.
Review one reproduced truthy nonboolean activation; controls now reject it.
Review two reproduced false failures from lost possible patterns; its predicate
probe now yields unchecked while the derivation passes. Review four confirmed
redaction, current locator mutation, anchor routing and unavailable assurance.
The root's stale operation edit also reproduced red before repair.

## Refactoring review

Refactors EXECUTED: replace walk-only nested matching with one shared typed index
without changing walk coverage, scope or grading policies. No unrelated structure
change is justified by this bounded fix. Existing shim-retirement and architecture
carryovers retain their old owners.

## Boundary

No full regression replay, Ubuntu run, distribution acceptance, provider oracle,
certificate, release, external app M3 acceptance or full-walk equivalence. Unknown
participants are conservatively unchecked even where known rows could suffice.
Occurrence admission is explicitly unsupported with the new mode. No production
publisher or merge is authorized by this record.

## Open questions

Occurrence admission with compiled obligations -> a separately scoped successor
milestone. All RF9 historical/frozen-authority carryovers keep their existing
owners. Actual app fast/full acceptance -> downstream-apps owner after adopting the new
keyword/flag at the exact merged commit. Milestone close and its question sweep
remain separate work; this record does not declare the milestone closed.

## Refuted premises

A passing derivation consistency verdict does not imply a definite relation. The
review-two retained empty-claim/predicate reproductions refute that assumption.
A loaded model's operation side table is not current after a valid mutable edit;
its dedicated regression refutes that assumption without changing default digests.

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
