---
milestone: aggregate-count-certificates
station: phase-AC1-spec-gate
scope: phase-AC1-spec-gate
date: 2026-11-16
gates:
  - command: "uv run --no-sync pytest -q tests/test_count_certificates.py --tb=short"
    exit: 1
    output: "22 failed, 2 passed in 46.31s"
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/aggregate-count-certificates/notes/phase-AC1-spec.md sha256 ffde3900151bdc6bc6a87ce5d7f0cfc9f972d965cb7d13e2bf4b28b9160c85e0"
    exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/milestones/aggregate-count-certificates/001-plan-gate.md
    sha256: 39ba2cdc1ed8f541e190dcb207bec0e2a7b9b751cade4b3b7e9c0a7a108fc99d
  - path: .gnd-planning/milestones/aggregate-count-certificates/notes/phase-AC1-spec.md
    sha256: ffde3900151bdc6bc6a87ce5d7f0cfc9f972d965cb7d13e2bf4b28b9160c85e0
  - path: tests/test_count_certificates.py
    sha256: 32924a33d3f9584c7e0c1e54d091747e66faa2ca5bd04bed0c8d1f4368d90734
  - path: tests/fixtures/count-certificates/README.md
    sha256: 0429e491d62f2d56ca76af1f0f3e9cd218224f8b5e2c466b6d8fe8aa4ba2ebd4
  - path: tests/fixtures/count-certificates/empty-group.json
    sha256: 98460aa95a1e03526a5182563286084b56f1674652544154e5dc0f257c96045e
  - path: tests/fixtures/count-certificates/expected.json
    sha256: 8bc8a16dd19500c81fd55109920549e3ecbedcf3c544b94781839baa7b855a55
  - path: tests/fixtures/count-certificates/group.json
    sha256: ff174c391221d8f4320b40750e5039121e8a75819e57a19a36989a1daed4c807
  - path: tests/fixtures/count-certificates/member-targets.json
    sha256: 3915303cdd0817c4f7adeca98e9f7706423bee040637723e58cd634e7b5cd6d8
  - path: tests/fixtures/count-certificates/model.orm.yaml
    sha256: abf5eaa487a2eafb379a30ba7a04278a9bbf9ba85e904aeddf07ad190bb569bb
  - path: tests/fixtures/count-certificates/population.json
    sha256: aeb688b5b147ceeebfca60672995ca51bddd09b5ae5547c5bc984228ddc3bf72
---

# AC1 corpus and spec gate

ruling: delegated (auto=true) approved .gnd-planning/milestones/aggregate-count-certificates/notes/phase-AC1-spec.md sha256 ffde3900151bdc6bc6a87ce5d7f0cfc9f972d965cb7d13e2bf4b28b9160c85e0

The owner authorized aggregate-count-certificates in auto mode. The planned
test corpus went red on the absent public routes. Its legacy checker and
individual member witness controls passed. The spec includes independent
expected request binding and a covered empty-membership result. The phase
proceeds with focused verification and one separately authorized diff review.
