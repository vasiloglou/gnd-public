---
milestone: literature-identity
station: main-integration
skill: "n/a -- repository development under process-milestone"
scope: main-integration
date: 2026-11-15
gates:
  - command: "uv run --no-sync pytest -q -p no:cacheprovider tests/test_li0_witness_wire.py tests/test_li1_literature_corpus.py tests/test_li1_assurance_report.py tests/test_li2_resolution.py tests/test_li3_diagnostics.py tests/test_li4_assertions.py tests/test_li5_lineage.py --tb=short"
    exit: 0
  - command: "uv run --no-sync pytest -q -p no:cacheprovider tests/test_rf6_query_policy.py tests/test_gnd_arch.py tests/test_development_scaffold.py tests/test_guarded_antecedent_filters.py tests/test_guarded_membership.py tests/test_guarded_disjunction.py tests/test_guarded_clause_exports.py tests/test_witness_composition.py --tb=short"
    exit: 0
  - command: "python3 scripts/components_index.py --check --strict"
    exit: 0
  - command: "uv run --no-sync ruff check --no-cache src tests tools"
    exit: 0
  - command: "uv run --isolated --offline --locked --group docs zensical build --strict"
    exit: 0
  - command: "uv run --no-sync ruff check --no-cache --output-format concise (entire integration tree)"
    exit: 1
evidence:
  - path: .gnd-planning/milestones/literature-identity/evidence/main-integration/query-successor.json
    sha256: 8ecdf9575ee946d9e276fc8c96d68d403148b57c4880bbb9ef46747523577737
  - path: .gnd-planning/milestones/literature-identity/evidence/main-integration/dynamic-query-successor.json
    sha256: 49a355fa0718c5ee66d7be235f69bb2f58a7bc558929686371ddde1af0070b52
---

# Claim

The integration tree combines the LI2–LI5 PR head `b2e2fdc9` with
the merged LI1 and guarded-rule-clauses main head `70a6959b`.
Both sets of authored component entries were retained and the
generated catalog and graph were rebuilt.

## Gate output

    204 passed in 410.32s (0:06:50)
    276 passed, 13 skipped, 1 deselected in 292.09s (0:04:52)
    All checks passed!
    No issues found

The full-tree Ruff invocation exited 1 with `Found 188 errors.`.
Its concise output matched the archived `70a6959b` main snapshot
byte-for-byte. The scoped source, test and tool lint exited 0.

## Query successor chain

The original LI2 and GC4 evidence remains in history. A new successor
extends GC4 with exactly the existing LI2 changes. The query policy
adds one recorded row. The dynamic policy adds 75 and removes six
recorded rows. The guarded-clause predecessor digests, resulting
row counts, and scanner observations agree.

## Boundary

The integration checks establish the merged source and query inventory
behavior over the affected suite. The fresh reserve measurement is
bound in [031](031-phase-LI5-independent-reserve.md). A renewed milestone
close has its own review and ruling.

## Open questions

- The renewed close review and ruling remain pending.
