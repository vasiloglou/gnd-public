---
milestone: cross-document-growth
station: phase-CG3
scope: phase-CG3
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
date: 2026-11-28
gates:
  - command: "pytest -q tests/test_consolidation_loop.py --tb=short"
    exit: 0
  - command: "pytest -q tests/test_consolidation_loop.py tests/test_rf6_query_policy.py --tb=short"
    exit: 0
  - command: "ruff check ."
    exit: 0
  - command: "python3 scripts/components_index.py --no-cache changed --base 1cce6979 --strict"
    exit: 0
evidence:
  - path: tests/test_consolidation_loop.py
    sha256: 8d6b728550efe0679efc7966008e9aaa9899c2cc468642659a4edea3ab3c3580
  - path: .gnd-planning/milestones/cross-document-growth/notes/reviews/CG3-r1/independent-review.md
    sha256: d7e3815c0a475597fe9c37a78d1864255aeef4fe179387cf946c4fa0181a8b16
slow_cadence: 'uv run pytest -q -m "evidence or census"'
---

Delegated acceptance (auto=true) on November 28, 2026. The CG3 terminal workflow supports leave, merge, demote to row and subtype link. The integrated two-document sample replay and the uninterrupted/interrupted equivalence test are described in [closure evidence](notes/close-delta.md). The decision journal records the whole proposal before mutation. Role references, constraint preservation, located sample multisets, source locations and model CAS guard the mutation. A pre-publication stale intent is superseded only before evidence staging.

Focused result: 16 passed in 10.13s. The post-repair focused and RF6 checks returned 32 passed in 17.73s before the directory-alias regression was added. The phase structure, CLI, packaging, install, doctor, disclosure and CG1–3 selection on the earlier implementation returned 1053 passed, 2 deselected in 170.41s. A separately installed offline wheel ran the packaged terminal example and recorded one leave before reporting a different group. The wheel test preceded the final review repairs.

## Independent review and refactoring

The [review](notes/reviews/CG3-r1/independent-review.md) found two group-scope issues, two evidence-loss paths, a stale-intent recovery defect and a path alias defect. The [ledger](notes/reviews/CG3-r1/FINDINGS.md) binds each disposition to a repair. One reviewer is one reviewer. The source constraint loss case separately failed before repair. Shared sample population evaluation now serves both additive admission and the reviewed mutation check. The existing evolution service owns publication, conformance and recovery. The strict component check reported no fixes or warnings; the existing evolution subsystem and population admission descriptions still apply.

## Boundary

The journal and model directory are locally trusted. The workflow needs POSIX directory locking for journal writers. Divergence after staging requires reconciliation. Referenced external populations require separate review. The replay simulates process interruption at publication and finalization boundaries. Real hardware power loss was not tested.
