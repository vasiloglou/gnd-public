---
milestone: literature-depth
station: phase-LD3-spec-gate
skill: "n/a -- repository development under process-phase"
scope: phase-LD3-spec-gate
date: 2026-11-16
gates:
  - command: "uv run --no-sync pytest -q tests/test_ld3_reading_workflow.py --tb=short"
    exit: 1
    output: "2 failed, 3 errors in 0.56s; the public reading module is absent"
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/literature-depth/notes/phase-LD3-spec.md sha256 4445e9f72c8b5632c7819aa21d944bd6621a92a0de59fc85ba12f975794bce64"
    exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/milestones/literature-depth/006-phase-LD2.md
    sha256: 58004fd9ba0a6f4f1d220cb67f48f49e694c5cb6a58d5eb2fede3a7b092b1308
  - path: .gnd-planning/milestones/literature-depth/notes/phase-LD3-spec.md
    sha256: 4445e9f72c8b5632c7819aa21d944bd6621a92a0de59fc85ba12f975794bce64
  - path: tests/test_ld3_reading_workflow.py
    sha256: 74891314c9aaa09280c86b59ba193c1d67e4b5b4f68ee8897650682648e52da1
  - path: tests/fixtures/ld3-reading/expected.json
    sha256: 7b12e90234e2c364f900c10ebfa50b454095b8ede4149498ddf26235fb234964
---

# LD3 spec and corpus gate

ruling: delegated (auto=true) approved .gnd-planning/milestones/literature-depth/notes/phase-LD3-spec.md sha256 4445e9f72c8b5632c7819aa21d944bd6621a92a0de59fc85ba12f975794bce64

Delegated approval under the owner's `process-milestone literature-depth
auto` invocation. Corpus-first applies. The answer key fixes the
six stages, per-stage call counts, coverage outcomes, stop reasons,
worklist and exact fidelity counts independently of implementation.
The expected red run stopped at the absent public module. Optional spec
review was omitted.

## Implementability sweep

The rooted molecular vocabulary can contain both the broad and
methods-only assertions. An additional controlled negative assertion
can use a local fact type. A saved extractor adapter supports an actual
call count, and the output verifier can rederive each stage from retained
bytes without that callback. The GND fidelity case shape accepts a
separate gold population and two extraction variants. Two source-backed
gold facts make the qualifying and below-floor cases discriminating.
LI1's coverage scoring can reuse its exact-fraction report format, with
separate expected rows. Source availability and budget exhaustion affect
the same declared workload and can be tested independently.

Part 10 remains deferred.
