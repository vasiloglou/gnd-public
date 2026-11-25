---
milestone: refactoring-followups
station: phase-F3
scope: phase-F3
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
date: 2026-11-25
gates:
  - command: python -m pytest -q tests/test_rf1_layering.py tests/test_rf6_index.py tests/test_rf6_query_policy.py --tb=short
    exit: 0
  - command: uv run pytest -q tests/test_v62_phase6_verbalization.py tests/test_public_semantic_adapter.py tests/test_rf6_moves.py tests/test_rf6_packages.py --tb=short
    exit: 0
evidence:
  - path: .gnd-planning/milestones/refactoring-followups/notes/F3-Claude-review.md
    sha256: eb93869d0885bcd85622cf58beb40b5908ec1f8d3311e7678365c43fdac944dd
---
Delegated acceptance with a named residual. The phase pins all thirteen migrated call sites and both id variants. Direct occurrences fell from 362 to 349 across 285 remaining distinct rows. Existing reasons remain attached to every residual through the exact live policy. #305 stays open for consumer-specific routing. #298 receives a ratchet for the three core groups, a measured negative control and three cold first-import checks. Module/runtime graphs retain zero cycles. The diagnostic initializer count remains seven.

    73 passed in 18.24s
    469 passed in 20.68s
    110 passed in 19.87s

The 110-test run also covered admission and transition reports before the final diff-site addition. Claude approved the original twelve sites. All four review items were addressed: each package starts cold, a synthetic tree exercises the graph measurement, diff uses the same strict variant, and the routing test counts each syntactic occurrence. No separate opinion over the repair. Refactoring review preserves strict access, row identity and last-wins duplicates. The successor gate is reproducible from the authenticated prior inventory. Prior panel authorization covers only plan and close. Slow cadence: uv run pytest -q -m "evidence or census".
