---
milestone: release-0.4.0
station: phase-RV2
scope: RV2-pre-freeze
date: 2026-11-17
implementation_commit: 9ae859222288c62a9da229442140ba83fd4a771e
gates:
  - command: "uv run --no-sync pytest -q tests/test_guarded_antecedent_filters.py tests/test_li1_assurance_report.py tests/test_li2_resolution.py tests/test_lx3_catalog_composition.py tests/test_lx4_literature_interop.py tests/test_expense_receipts_example.py --tb=short"
    exit: 0
  - command: "uv run --no-sync pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
  - command: "uv run --no-sync ruff check --output-format json"
    exit: 1
  - command: "uv run --no-sync ruff check tests/test_release_acceptance.py"
    exit: 0
  - command: "claude --print --safe-mode --model opus --permission-mode plan --output-format text --no-session-persistence (brief on stdin)"
    exit: 0
  - command: "review_tool.py status <RV2 pre-freeze round> --format json"
    exit: 1
  - command: "GND_CANDIDATE_DIR=<synthetic inventory> uv run --no-sync pytest -q -o addopts='' tests/test_release_acceptance.py::test_candidate_identity_negative_controls --tb=short"
    exit: 0
  - command: "uv run --no-sync pytest -q --collect-only -o addopts='' tests/test_release_acceptance.py"
    exit: 0
  - command: "Editable 0.4.0 and hash-verified installed 0.3.0 rehearsal of the four new probe functions"
    exit: 0
evidence:
  - path: .gnd-planning/milestones/release-0.4.0/006-RV2-spec-gate.md
    sha256: 21e70701f808f3ef3860e1115d117a32ddd35cda4164d0d177bb1bb8139629f2
  - path: .gnd-planning/milestones/release-0.4.0/notes/reviews/phase-RV2-pre-freeze-r1/diff.patch
    sha256: e69d81aae7d052ce4dd99ed153ce99c6767efe0debc9a359e28a25c89521842f
  - path: .gnd-planning/milestones/release-0.4.0/notes/reviews/phase-RV2-pre-freeze-r1/review.md
    sha256: cca9412deaec0ed51c33e6544fa3c9b276a2d3f7121584d8da3fd1748eb4f515
  - path: .gnd-planning/milestones/release-0.4.0/notes/reviews/phase-RV2-pre-freeze-r1/run.json
    sha256: e98d36fcf4a03c231b9450f1808ac6fa76dbfe7ddcd1c521a024d31563e7fac6
  - path: .gnd-planning/milestones/release-0.4.0/notes/reviews/phase-RV2-pre-freeze-r1/FINDINGS.md
    sha256: a0a1560da7ad8f32759d94d2ff9462648d4c47a2580bef86b54a09a1dad4a12b
---

# RV2 pre-freeze checkpoint

The acceptance probes are implemented and ready for the owner-merged PR
required by [the spec](notes/phase-RV2-spec.md). The RV1 merge is
`bcc4a5287d24822c7a7d48048351eb0653d10526`. The probe diff preserves the
prior positive regressions and replaces the 0.2.0 availability comparison
with the hash-pinned 0.3.0 wheel. The new suite exercises guarded membership
and filtering, two-include composition and identity decisions, fixed catalog
witness and replay, the literature assurance report, and expense receipts.

The rehearsal called the four new test functions on the editable 0.4.0
interpreter and the separately installed public 0.3.0 wheel. The checkout
inputs came from a Git archive. CPython was 3.14.3. The rehearsal supplied an
empty sandbox prefix and did not use the retained release/comparison wheel
fixture. The synthetic identity run tested the receipt and hash verifier
using stub bytes. The 23-case collection result measures test selection only.

## Independent review

One Claude Code Opus reviewer read the original diff and approved it with
three findings. The [ledger](notes/reviews/phase-RV2-pre-freeze-r1/FINDINGS.md)
records dispositions. The source-receipt mismatch reproduced before the
fix. The verifier now refuses a wrong commit and archives the checked SHA.
The composition probe also checks the resolved manifest path and digest
directly. The source-side normalization helper supplies report comparison
only. The reviewer performed a code reading without building or running tests.

The review helper returned exit 1 because the repaired test file differs
from the review digest. It reports one completed review and no ledger
problems. Rehearsal and focused controls cover the revised bytes.

## Gate output (verbatim)

    224 passed in 280.25s (0:04:40)
    679 passed, 2 deselected in 256.10s (0:04:16)
    188 repository-wide diagnostics, exact equality to RV1: True
    Full Ruff exit 1
    All checks passed!
    4 passed in 0.24s
    23 tests collected in 0.04s
    Pass: guarded_membership
    Pass: composition_and_catalog
    Pass: literature_assurance
    Pass: expense_receipts

## Boundary

One reviewer is one reviewer. This checkpoint covers the pre-freeze probe
diff. The phase still owes the actual merged source freeze, the full baseline
comparison, both builds, all retained artifact identities, the installed
acceptance run, and a final phase record. The merge requires separate owner
authorization. No release artifact or publication action is part of this PR.

## Open questions

- Freeze only after this PR lands on main, rerun notes reconciliation and
  public index availability, and discharge RV2-C0 before building.
- Preserve the RV3 publication-page findings from the RV1 record.
