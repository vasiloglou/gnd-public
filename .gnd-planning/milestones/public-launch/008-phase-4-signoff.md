---
milestone: gnd-public-migration
station: phase-4-signoff
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-4-signoff
date: 2026-10-04
gate:
  command: "uv run pytest -q tests/test_documentation_tutorials.py tests/test_external_runtime_tutorials.py tests/test_bookrec_tutorial.py tests/test_expense_tutorial.py tests/test_release_docs.py tests/test_release_examples.py tests/test_public_generated_examples.py tests/test_contributor_preparation.py tests/test_development_scaffold.py tests/test_public_agent_failure_transition.py tests/test_artifacts.py --tb=short"
  exit: 0
  output: "232 passed, 1 deselected in 92.74s"
  note: "Local focused gate on 91f12e2 (P4.1 gate plus the P4.2 and PR #5 surfaces); not a cloud CI run"
slow_cadence:
  command: "existing configured repository CI"
  trigger: "GitHub runner billing restored"
  reason: "Owner deferred paid CI; the last cloud success is c63b90cc3 (Phase 3 acceptance)"
evidence:
  - path: evidence/phase-4-signoff/gate.txt
    sha256: 416473fc2918228f55f664d5f44a9893ac4f24b3b159de1097cd2666b4ad2ca6
  - path: evidence/phase-4-signoff/candidate.json
    sha256: a92af59b513469e19b700765655de70ec3a708dac29129d86ad5d7283f65bad6
---
# Phase 4 sign-off — owner accepted candidate 91f12e2

The owner closed Phase 4 on 2026-10-04 by direct instruction ("just close
phase 4"), accepting the CI already run on gnd-public as sufficient. This is
an owner decision, not a new cloud acceptance.

## What is signed off

Candidate `main` at `91f12e207ba4040cd308862c6f91b2191584c3c4`, version 0.1.0
(still provisional). It contains Phase 3 acceptance ([004](004-phase-3.md)),
Phase 4 preparation ([003](003-phase-4-preparation.md)), Phase 4.1
([005](005-phase-4.1-preparation.md), [006](006-phase-4.1-review.md),
[007](007-phase-4.1-runtimes.md)), the P4.2 documentation revision (PR #3,
merged without a separate record) and the agent-failure transition fix (PR #5).

Built once from that commit: wheel `aedd1a4b…a5a36` (1,698,690 bytes) and sdist
`2e02db5f…bfe019` (1,498,826 bytes); full hashes in
[candidate.json](evidence/phase-4-signoff/candidate.json). The wheel installed
into a fresh Python 3.11 venv outside the checkout and `gnd --help` exited 0.
The artifacts were not retained; a publication build must rebuild and re-hash.

## Boundary

- Last cloud CI success: `c63b90cc3`, 2026-10-03. Every later run on `main`
  (P4.1, P4.2, PR #5) was refused by GitHub billing before any job started.
  Those changes are covered only by the local focused gate above, on macOS
  arm64. The Ubuntu 3.11 / macOS 3.13 matrix was not re-run on this commit.
- No independent review of P4.2 or of this sign-off.
- Five-user trial, five-minute timing, TestPyPI and publisher configuration
  remain unmeasured, as recorded in 003 and 007.
- No upload, release, announcement or visibility change happened here.

## Refactoring review

None. This record changes no product code.
