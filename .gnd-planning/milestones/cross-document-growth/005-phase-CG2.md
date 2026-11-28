---
milestone: cross-document-growth
station: phase-CG2
scope: phase-CG2
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
date: 2026-11-28
gates:
  - command: "pytest -q tests/test_consolidation_candidates.py --tb=short"
    exit: 0
  - command: "pytest -q tests/test_consolidation_candidates.py tests/test_rf6_query_policy.py --tb=short"
    exit: 0
  - command: "ruff check ."
    exit: 0
  - command: "python3 scripts/components_index.py --no-cache changed --base 88227f35 --strict"
    exit: 0
evidence:
  - path: tests/test_consolidation_candidates.py
    sha256: 925e2eb2493a680e51b5e6b94dcdeb38128637d6786e62b20d8697986cd2f719
  - path: .gnd-planning/milestones/cross-document-growth/notes/reviews/CG2-r1/independent-review.md
    sha256: 1d5d18b33f8df7797c37eeaf051cd96c37f2b40bd7609f15713a10a1a99d7c55
slow_cadence: 'uv run pytest -q -m "evidence or census"'
---

Delegated acceptance (auto=true), 2026-11-28, for CG2 at 25efdbd3. The command reports all six signals, stable member identity, source locations, charged work and the stopping condition. A value-free public report must omit hashes of raw sample values. The evidence hash binds disclosed observations and shape metadata. CG3 separately binds every decision to the reviewed model digest.

The focused suite reported 13 passed in 8.99s. The final focused and RF6 selection reported 30 passed in 13.69s. The structure, CLI, installation, disclosure and discovery selection on the pre-repair implementation reported 1019 passed, 2 deselected in 130.61s. The independent [review](notes/reviews/CG2-r1/independent-review.md) requested changes; the [ledger](notes/reviews/CG2-r1/FINDINGS.md) links each finding to the repair. Four regressions failed against the pre-repair implementation. One reviewer is one reviewer.

## Refactoring review

The parser now calls its existing discovery service. Role lookup and role-player signatures use the shared ModelIndex and refscheme implementations. The strict component check reported zero failures and zero warnings. Its five reread notices concerned the existing dispatch, discovery and disclosure descriptions, which still describe their public roles.

## Boundary

Source locations are advisory. CG2 performs no model mutation and does not establish whether two names denote the same concept. The reporter's large models were unavailable. The included-fact scenario from review F7 was verified by source inspection; the installed composition test establishes ownership filtering only.
