---
milestone: literature-reading-reference
station: phase-LR2
skill: "n/a -- repository development via process-phase auto=true, not a gnd-solve station over a domain model"
scope: phase-LR2
date: 2026-11-23
gates:
  - command: "uv run pytest -q tests/test_lr2_quote_scope.py tests/test_anchor_sidecar_v2.py tests/test_ld3_reading_workflow.py tests/test_documentation_tutorials.py --tb=short"
    exit: 0
    output: "158 passed in 143.03s (0:02:23)"
  - command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
    output: "679 passed, 2 deselected in 97.55s (0:01:37)"
  - command: "uv run pytest -q tests/test_lr2_quote_scope.py --tb=short"
    exit: 0
    output: "5 passed in 0.91s"
  - command: "uv run ruff check"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base origin/main --strict"
    exit: 0
    output: "changed against origin/main (11a7ebf): 119 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "LR2 changes pages and adds one test; no package code changes"
evidence:
  - path: .gnd-planning/milestones/literature-reading-reference/notes/phase-LR2-spec.md
    sha256: a40492d71fdb3d7d236f399f133b773835d5ae6d4ee0141516565ccd6674197b
  - path: .gnd-planning/milestones/literature-reading-reference/notes/issue-reply.md
    sha256: 6fe6dabaa8bf53f4b9d529e8edcd228778fd4b599af52ed41e696db89e1fcfef
  - path: .gnd-planning/milestones/literature-reading-reference/evidence/LR2/final-gate.txt
    sha256: 3dc68c393c5bbbfafc13bffdb109854d5322de02cb709515ecfb2f5c3f5ec15b
  - path: .gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR2-r1/review.md
    sha256: facc6e749aa04bfb8504f824dc2634087b067d75cad3936b426f92fc677357fc
  - path: .gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR2-r1/FINDINGS.md
    sha256: 31148ac6aa674939597dd392ab1b304ec767b60763fa298f2ea1b99d894a6e78
  - path: docs/reference/anchors.md
    sha256: adc5acc80c4f339789f5d6440d2c413b2bcb9f924b5ef84635cc0086b155467f
  - path: docs/literature/index.md
    sha256: 29fb040bbb723af20a679096f355ad61c97a669eefb6180aa4008d737616ef38
  - path: docs/literature/commands.md
    sha256: 65c59143405af0148fd8effc404203344a5ca09d5c26b81097f75b1986f7b735
  - path: src/gnd/examples/literature/README.md
    sha256: 45f205c57720ee122717a08d8d2ae30c1a2e566e07a6fa6ae42cde0ce52f120c
  - path: tests/test_lr2_quote_scope.py
    sha256: beefa09ac5f8abe8001f008187151014dc504f865760c07fa2290efcaa578e7e
---

# Phase LR2: where a quote may lie

Phase base `c17ae2d6` (the LR1 branch head, PR 243). Implementation commit
`45551cf1`. Started on the coordinator's "GO LR2" of 2026-11-23, which
sequences the work and approves nothing.

## Spec gate

Delegated approval (`auto=true`), 2026-11-23, under the milestone delegation
in [001-plan-gate.md](001-plan-gate.md). Gated bytes: `notes/phase-LR2-spec.md`
r1 with §12, SHA-256
`3ea42e6a3fa2bbf72000701ab5dbc0f3a4d31c1cb09a24945dfe6c5e363e63a2`; §13 was
appended after the gate. Rulings: LR2-D1 (`block_id` records the shown
section; no new convention) and LR2-D2 (the host guidance goes in
`docs/literature/commands.md` after the Act 2 anchor check). D2 (b), the
plan gate's ruling, is the rule. No paid call. No format change. A delegated
ruling, not the owner's reading.

## What shipped

- `docs/reference/anchors.md`, "Where a span may lie": the rule's one home.
- `docs/literature/index.md`: the "tied to its passage" sentence cites the
  rule.
- `docs/literature/commands.md`: one paragraph after the Act 2 anchor check,
  the host guidance. It is far from PR 241's Act 3 passage, as the
  coordinator asked.
- `src/gnd/examples/literature/README.md`, "Replayable reading": what the
  reading example verifies, outside the admission section.
- `tests/test_lr2_quote_scope.py`, T1–T5.
- `notes/issue-reply.md`: the interim reply draft for requests 3 and 2. The
  owner posts it; nothing was posted.
- A release-notes bullet.

## Criteria

| Criterion | Evidence |
|---|---|
| LR2-C1 | T4 |
| LR2-C2 | T1 (with `block_id` naming the other section) |
| LR2-C3 | T2, told apart from the digest check by T3 |
| LR2-C4 | no reading-example code or fixture changed; `tests/test_ld3_reading_workflow.py` in the lane |
| LR2-C5 | T4, T5 |

## Review

One round, one reviewer: Codex through the review helper, the owner's
"Review helper, both". **One reviewer is one reviewer.** It probed the binder
in memory and confirmed the three binding outcomes and the README's
accuracy. It ran no file-writing test. One finding (hardening, reproduced):
T5 missed two of the README's four claims. Fixed in `45551cf1`, with the
reviewer's mutation now failing T5. The fix is unreviewed bytes; it is a
test-only change, and no second round was run.

## Refactoring review

None needed. The phase adds a page section, three citing passages and a
test; it touches no code, and no helper was duplicated.

## Boundary: what this phase does NOT establish

- That any host's quotes are correct. A bound span shows where a value
  occurs, not that the text supports the fact; the page keeps that limit.
- Anything about the 38 claims #226 dropped for a participant or predicate
  not in the quote: that is the reporter's host rule.
- Pages are checked for fixed sentences and links, not parsed.
- The interim reply is a draft; its merge-status wording must be updated
  before the owner posts it.

## Open questions

None new. LR3 waits for PR 241 (LH1 and LH2) to merge and for the owner's
D3.
