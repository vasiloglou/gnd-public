---
milestone: compiled-snapshot-obligations
station: milestone-close
skill: n/a -- repository development close
scope: milestone-close
date: 2026-10-13
gate:
  command: "uv run pytest -q tests/test_compiled_snapshot_obligations.py tests/test_compiled_snapshot_boundaries.py tests/test_public_api.py tests/test_schema_sync.py tests/test_model_v2.py tests/test_public_transition_contract.py tests/test_public_transition_trace.py tests/test_v61_phase1_batch.py tests/test_rf1_layering.py tests/test_v6_phase2_registry.py tests/test_public_redaction_reports.py tests/test_public_reference_signatures.py tests/test_rf5_review_regressions.py --tb=short"
  exit: 0
  output: "218 passed in 26.96s; 218 passed in 25.89s"
slow_cadence:
  command: uv run pytest -q -ra --tb=short
  trigger: explicit owner selection or separately scoped CI
  reason: bounded completion gate; broad replay not selected
---

# Claim

CS0, CS1 and CS2 complete the delegated bounded development scope at runtime
commit 6cff353e7bc25a8e5bab3952cfb9d137611ced45 and docs commit 47e9071.
Four local close opinions and their disposition are retained in the notes
listed below. PR submission follows; merge and human acceptance
remain separate owner actions. This is not a provider-panel certificate.

## Gates

001-phase-CS0.md records the reproduced missing keyword: 3 failed, 4 passed.
002-phase-CS1.md and 003-phase-CS2.md record the selected current-byte gates:
215 passed in 26.69s (Python 3.11), 215 passed in 25.80s (Python 3.13).
Ruff: All checks passed! Whitespace gate exited 0.
The bounded agreement artifact records 2/2 populations, 23 compiled entries
each, normalized over exit/count/failing-reference fields only.

The supplementary final gate (frontmatter command) exited 0 on both interpreters:

    218 passed in 26.96s
    218 passed in 25.89s
    All checks passed!

The new boundary tests are included in these retained streams. Their import
ordering was corrected by Ruff; this changed no test semantics.

## Open-questions sweep

| Source / question | Disposition / evidence or next owner |
|---|---|
| Plan CS-D1 meaning | Closed by owner approval recorded in CS0: explicit opt-in standing obligations. |
| Plan CS-D2 activation/provenance | Closed by CS0 spec, CS1 public activation and CS2 docs; no provenance inference. |
| Plan CS-D3 coverage/limits | Closed by CS1: explicit unchecked and 100,000 projected-cell ceiling with refusal cases. |
| Plan CS-D4 report compatibility | Closed by CS1 schema, redaction, assurance and qualified-reference gates; existing schemas retained. |
| Plan CS-D5 agreement boundary | Closed with delegated observable-field amendment at plan close; evidence/CS2/agreement.json. |
| Plan CS-D6 review selection | Closed by explicit owner selection of four local readers; no vendor panel claimed. |
| CS0 work limits | Closed by CS1 counted-work tests and unchecked disposition. |
| CS0 dynamic-derived eligibility/uncertainty | Closed by CS1 effective view and possible-only regression; opaque/possible participation unchecked. |
| CS0 witness redaction | Closed by CS1 source and required-relation redaction controls. |
| CS0 admission refusal | Closed by discriminating API and CLI refusal controls in CS1. |
| CS0/CS1/CS2 RF9 authority and structure carryovers | Carried to their original RF9/RF6/RF7 owners; this semantic fix does not confer new authority or retire shims. |
| CS1/CS2 future occurrence admission support | Carried to a separately scoped occurrence-admission milestone, owned by the framework maintainer. |
| CS1/CS2 external app acceptance | Carried to downstream-apps owner after adoption at exact merged commit; notes/app-regression-recipe.md. |
| CS1/CS2 close question sweep | Closed by this table and four local close reviews. |
| CS2 pending plan/close review history | Closed only for the explicitly selected local instrument; previous vendor-panel history remains historical. |

## Supplementary completion evidence

The close review reproduced a missing demonstration in CS2-C3, an evidence
completion defect rather than a runtime defect. Three new public API tests in
tests/test_compiled_snapshot_boundaries.py directly pair snapshot band 0 with
walk band 1 for a retained literal precondition, an undeclared delta in a touched
relation and an invalid intermediate state between clean endpoints. The frame
fixture uses a touched relation: unrelated untouched deltas remain outside the
walk's established frame policy. Original phase records retain their bounded
claims; this later evidence discharges the outstanding demonstration.

Public validate --trace exited 0 and its complete output is retained in
evidence/CS2/obligation-inventory.txt: 23 compiled entries, one excluded
start.pre_concept_exists entry because var_bound has multiple asserters.

## Local close review disposition

Four local opinions are retained in notes/close-review-one.md through
close-review-four.md. Seats one and three identified missing paired walk
counterexamples; seat one also identified the missing retained inventory.
Those findings are retained verbatim, reproduced against the test/evidence
inventory, and repaired with the supplementary artifacts above. Seats two and
four checked uncertainty, assurance, public recipe and artifact claims; no
runtime blocker was reproduced. Final follow-up opinions bind the repairs.
These readers share one model family; this is the owner's selected local review
instrument, not the maintained vendor panel or a certificate. The bounded close
is accepted as a delegated auto=true ruling after those checks, without labeling
it human review of successor bytes. No second repair round or paid budget used.

## Refuted premises and plan repair

Batch cannot measure all passing/warning obligation identities. The original
CS2-C2 demand is repaired by the dated close amendment and scoped evidence.
Passing derivation consistency does not make its effective relation definite;
CS1 review-two reproductions and regression retain the corrected reasoning.
A loaded operation side table is not current after mutation; CS1 recompiles
current declarations without contaminating the model or changing default digests.

## Refactoring review

Shared typed indexed matching replaces duplicated walk matching behind the
focused walk/snapshot gates. CS0 needed no refactor; CS2 documentation requires
no structural refactor. No new deferred refactor arose. Existing historical
structure/authority questions remain carried to their original owners.

## Boundary

No full repository replay, Ubuntu run, distribution acceptance, external M3
acceptance, provider review, certification, package release or full-walk
correctness. Conservative unknowns may remain unchecked even where a known
subset could suffice. Occurrence admission is refused. Local readers share the
same model family; four readings do not establish independent proof. Closure
is bounded development completion, not merge, publication or human acceptance.

## Artifact identities

- .gnd-planning/milestones/compiled-snapshot-obligations/001-phase-CS0.md: 4a417b1c7b29ffea382778e073c82ac287a6bc75574ba0b7403b68b999fcd871
- .gnd-planning/milestones/compiled-snapshot-obligations/002-phase-CS1.md: a2ed4f92aa3338b2e4a8b3e2922df46b6c2f54a865b69dff3fe3ff0548984435
- .gnd-planning/milestones/compiled-snapshot-obligations/003-phase-CS2.md: b34f4dc48bca18d7fdbeb8b1483de43d34a8adf5d33dfddfeb1d761c80da57ab
- .gnd-planning/milestones/compiled-snapshot-obligations/notes/compiled-snapshot-obligations-plan.md: fba63966205df03f581f01ebd32e0011647028165eb8cf33df6895489870be05
- .gnd-planning/milestones/compiled-snapshot-obligations/notes/app-regression-recipe.md: 91433700a617342601d060590250e154a35718000e5cd3a1b15cc2d0c17cd088
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CS2/agreement.json: eab3dc3c895b8cf2072a6baab7c770e46d0110651663f85a35e7cae526a44270
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CS2/obligation-inventory.txt: 2f6ef3279dc1561f1de23ca7fb72df9efefbfdb4364fa56f85fe5453420aec9e
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CS2/close-focused-311.txt: a97f4af95ee0ce240575afd66ed2949186d92569561271fbfa8c82d446b6a668
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CS2/close-focused-313.txt: d45578ab1be53df4b8b2939e10ba62bf9288a12ef10d3eaad1a886d12e04889f
- tests/test_compiled_snapshot_boundaries.py: 0e2f5972105726afde58cb63a0249af058b85dfcaf938a3d53fd06436fa57acb
- .gnd-planning/milestones/compiled-snapshot-obligations/notes/close-review-one.md: c6f56a98f15ecb8396c70e680fe16469f677c904ea8885c05541829bc8ad81c1
- .gnd-planning/milestones/compiled-snapshot-obligations/notes/close-review-two.md: fddc3c0e39093952582b0852c6fbd497cad69bf77bdeddf40977d75c55387b2a
- .gnd-planning/milestones/compiled-snapshot-obligations/notes/close-review-three.md: 19b991a4d680b2e8a6661f0e64bea1d5bdbf6afe4e652fecf74b4b74a1d03025
- .gnd-planning/milestones/compiled-snapshot-obligations/notes/close-review-four.md: cb3a02b5943c8353e989f4db7d3b7f18d6c4a7e5074245aa3879db2e9fa0e503
