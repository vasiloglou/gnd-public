---
milestone: aggregate-count-certificates
station: phase-AC1
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-AC1
date: 2026-11-16
gates:
  - command: "uv run --no-sync pytest -q tests/test_count_certificates.py tests/test_v62_phase4_aggregate.py tests/test_li0_witness_wire.py tests/test_witness_composition.py tests/test_artifacts.py tests/test_rf1_cli_pins.py --tb=short"
    exit: 0
    output: "295 passed in 166.71s (0:02:46)"
  - command: "uv run --no-sync pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
    output: "679 passed, 2 deselected in 313.40s (0:05:13)"
  - command: "uv run --no-sync pytest -q tests/test_count_certificates.py -k deep_yaml --tb=short"
    exit: 1
    output: "2 failed, 41 deselected in 1.99s on the original candidate with the added regression tests"
  - command: "uv run --no-sync pytest -q tests/test_count_certificates.py -k deep_yaml --tb=short"
    exit: 0
    output: "2 passed, 41 deselected in 4.92s on the repaired candidate"
  - command: "uv run --no-sync ruff check --output-format=json"
    exit: 1
    output: "188 exact inherited diagnostics, 0 new"
  - command: "python3 scripts/components_index.py changed --base a7785ffb --strict"
    exit: 0
    output: "0 to fix, 0 warning(s), 0 to reread"
  - command: "uv build --offline --wheel --out-dir <scratch>/dist; install into scratch virtualenv and run the COUNT fixture README commands"
    exit: 0
    output: "Installed wheel: both COUNT groups and the member replayed. Checker output was byte-identical."
  - command: "claude -p --model opus --permission-mode plan --add-dir <review-dir> -- '<brief-path prompt>'"
    exit: 0
    output: "VERDICT: CHANGES_REQUESTED"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: explicit owner or CI selection
  reason: current COUNT and affected public routes are exercised by the focused and installed gates
evidence:
  - path: .gnd-planning/milestones/aggregate-count-certificates/001-plan-gate.md
    sha256: 39ba2cdc1ed8f541e190dcb207bec0e2a7b9b751cade4b3b7e9c0a7a108fc99d
  - path: .gnd-planning/milestones/aggregate-count-certificates/002-phase-AC1-spec-gate.md
    sha256: 38db868c385b0b7e1a2be39278d3292f9fb2da1000518aaaf59c5da0a4e9c3d5
  - path: .gnd-planning/milestones/aggregate-count-certificates/notes/phase-AC1-spec.md
    sha256: ffde3900151bdc6bc6a87ce5d7f0cfc9f972d965cb7d13e2bf4b28b9160c85e0
  - path: .gnd-planning/milestones/aggregate-count-certificates/evidence/AC1/installed-observation.json
    sha256: 6d010b9c6b332ffccfbf1275d36a975d300a8889165fe7fc58dc9a106d86adbc
  - path: .gnd-planning/milestones/aggregate-count-certificates/evidence/AC1/independent-review-status.txt
    sha256: 6cf8ec8dd07bdb5d2346aede87ed85d2549d739a9efa2085365270b637edad8e
  - path: .gnd-planning/milestones/aggregate-count-certificates/notes/reviews/phase-AC1-r1/BRIEF.md
    sha256: fb243ea00dad3377e3fbf63f5ea59b8149631083d1f9c399583a35f4f44e4df3
  - path: .gnd-planning/milestones/aggregate-count-certificates/notes/reviews/phase-AC1-r1/brief.json
    sha256: b6c7aa086ae5293feeed1de45ea19527edcc4db7d963a45cbdaecdd8d2e62249
  - path: .gnd-planning/milestones/aggregate-count-certificates/notes/reviews/phase-AC1-r1/diff.patch
    sha256: 15446f3df7bc8f5e30e858d5f9beba524de37ff2454c5fe129a3cfb850d06b7b
  - path: .gnd-planning/milestones/aggregate-count-certificates/notes/reviews/phase-AC1-r1/FINDINGS.md
    sha256: 288ddc54e9c8d8b3e4f5cda11ef7e530d3ad3ef09727379ae619dc3f3bfc1373
  - path: .gnd-planning/milestones/aggregate-count-certificates/notes/reviews/phase-AC1-r1/review.md
    sha256: 53fbb37316b69af1d1e70913f728bd3b603fa4c56d13a6efedd0060b60a32dcd
  - path: .gnd-planning/milestones/aggregate-count-certificates/notes/reviews/phase-AC1-r1/review.log
    sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
  - path: .gnd-planning/milestones/aggregate-count-certificates/notes/reviews/phase-AC1-r1/run.json
    sha256: ca8dfa26ac6bad878d700de995a47dfef6c39f8124caa68ffb9ebd049cd024f8
  - path: src/gnd/witness/count_membership.py
    sha256: 7777ad746315e7de375142a2b1d1fd8a394407cb04a075076c69c419fa649e46
  - path: src/gnd/witness/count_producer.py
    sha256: 2bc4c0cfac1ab375db2df0d50427e00cdbe1d37db82101a1bae8c47f1d0f2ac1
  - path: src/gnd/witness/count_replay.py
    sha256: f7f06c1b7ab41ff21937e04b94add56b0740e64bb080dcfead92a0ea0d9f18db
  - path: tests/test_count_certificates.py
    sha256: 097032f0ede02fcccc5fb97bdf0d6b421ad155b4cc67c1f4385932dab72f41ce
  - path: src/gnd/skills/gnd-export/references/count-witness-contract.md
    sha256: 7b8e3f374cdc7659d0fd215ca32d97dc73edfd40e2760de99c52ddaf5e3b4b98
---

# AC1 completion

AC1 produces and independently replays a complete contribution roster for a
caller-selected COUNT group over one declared covered asserted relation.
The ordinary checker continues to derive aggregate rows for groups with
contributing bindings.

| Criterion | Evidence |
|---|---|
| Distinct roster | The frozen answer roster and checker comparison exercise both present groups. Equal values with different ordered keys count separately. Repeated contributions select their lowest source position. |
| Semantic forgery | Omission with an adjusted count, duplication, wrong count, false empty, substitution, wrong type and noncanonical representative positions refuse at exit 1. |
| Input authority | Exact model, population and caller request bytes bind the result. Changes stale replay at exit 3 before membership checking. |
| Empty and uncovered groups | A named absent group certifies zero over a populated covered relation and over an empty covered relation. Undeclared coverage and opaque values refuse. An invented ordinary zero aggregate row fails the checker. |
| Work limits | Raw snapshot, wire, row visit, binding cell, node and generated-byte controls distinguish malformed input from work refusal. |
| Ordinary member evidence | The installed positive witness points to the COUNT certificate's first representative position and independently replays. Checker reports before and after are byte-identical. |
| Replay independence | Replay succeeds while imports of the new producer, the ordinary witness producer and the aggregate evaluator are blocked. |

## Independent review

The owner authorized one independent Claude Code Opus review of
`c56ce751`. The reviewer matched all 37 brief files, passed 555 selected
tests, and confirmed exact replay, covered empty groups, typed identity,
resource refusals outside the YAML nesting gap, and disclosure. The
reviewer exercised a Unicode identity case. The reviewer ran from the
source tree, and the installed observation records the separate wheel
verification.

The [findings ledger](notes/reviews/phase-AC1-r1/FINDINGS.md) records both
dispositions. The review reproduced a slow shared YAML loader on deeply
nested models. The author reproduced it for YAML models and populations
and applied the existing streaming guard before node construction at
`2f906af0`. Both regression cases went red before the repair. The
[review status](evidence/AC1/independent-review-status.txt) identifies
the original reviewed files and the six changed files. Local verification
and the installed wheel cover the repaired bytes.

## Refactoring review

Refactors EXECUTED. The producer and replay use one bounded snapshot
scan, with separate invocation paths and caller-controlled request
authentication in replay. Model role lookup goes through ModelIndex, and
raw certificate creation uses the existing atomic publication helper
with a private file mode.

## Boundary

One independent Claude Code Opus reviewer reviewed the named candidate.
The implementation proves membership in the declared covered candidate
relation within the admitted COUNT rule fragment. The worked example
uses synthetic records.

## Open questions

- The milestone close panel owns the question sweep over the part 10
  criteria and the scope of the delegated close ruling.
- Carry the review helper's Claude prompt separator to dev-tools
  maintenance.
