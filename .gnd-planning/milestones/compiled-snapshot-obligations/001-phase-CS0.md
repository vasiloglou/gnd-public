---
milestone: compiled-snapshot-obligations
station: phase-CS0
skill: process-phase
scope: phase-CS0
date: 2026-10-13
gate:
  command: uv run pytest -q tests/test_compiled_snapshot_obligations.py --tb=short
  exit: 1
  output: "3 failed, 4 passed in 3.37s"
slow_cadence:
  command: uv run pytest -q -ra --tb=short
  trigger: explicit owner request or separately selected CI
  reason: corpus-first baseline, not full regression acceptance
---

# Claim

The portable baseline cases pass and the activated successors are red because
the public keyword is absent. The read-only exact issue diagnosis reproduced
walk band 1 and snapshot/batch band 2 with zero failed derivations.

## Owner gate

The owner explicitly delegated auto=true and four local readers in place of
the pending plan panel, commits and a fix PR. CS0 spec records the authorization
and submitted artifact identity. Four local readers found no blockers and
identified CS1 integration obligations. No provider panel was invoked.

## Evidence

The corpus model and paired populations are committed with this record. Baseline
JSON declares its temporary input/driver bytes outside history. The red log is
retained under evidence/CS0/corpus-red.txt. Digests are added below from disk.

## Refactoring review

None needed in CS0: fixture and spec work only; shared evaluation is CS1 work.

## Boundary

This red corpus does not establish a runtime fix, full-walk equivalence,
certification, external app acceptance or broad CI success. CLI refusal cases
need discriminating error-message controls in CS1; their pre-fix 64 is not yet
evidence of the new option's conflict handling.

## Open questions

CS1 owns work limits, dynamic-derived eligibility, uncertainty, witness redaction
and admission refusal. Existing RF9 carryover questions retain their owners.

## Artifact identities

- .gnd-planning/milestones/compiled-snapshot-obligations/notes/phase-CS0-spec.md: 7e6ef66f23e113df69b3ba48d7995b08a667b096e6f5e8e2693e7a4e28d9d9da
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CS0/baseline.json: 2470a2fcb256bf2cec481c2fd8382b847658dee789eedcbde95ecf2317526112
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CS0/corpus-red.txt: f37fe3b5bed88e47a8f791574fc9e15b4e34438ec9b1f66b3624e293dc07fee8
- tests/test_compiled_snapshot_obligations.py: 5dd8a0270074d5e310db15a8cb6048efe71255ea681cf39bab39cb3bac409efa
- tests/fixtures/compiled-snapshot/README.md: 830603031bd7d6b514eb40fa6d03de3a896da5f6b81bdc9fd8e823e06f019b0d
- tests/fixtures/compiled-snapshot/expected.json: 4fdfcd186bf459f11360fee4fb1f91d6d4e6e805d7137fc131c885e82c53122f
- tests/fixtures/compiled-snapshot/model.orm.json: 4fe9ddcac0530cf5b988ae3220371968ec280979fa10ec94868439f5f159a1e4
- tests/fixtures/compiled-snapshot/nonnumeric.pop.json: 783e9bc033e66ddc3f1bda53d13e0c272c7c04260b52bd4fe4a296e7ebbbe27f
- tests/fixtures/compiled-snapshot/nonnumeric.steps.json: 11b4f73b6cbbb6d9d36158850c2a7df8429bbbff3153a21d77b44c4819e8243f
- tests/fixtures/compiled-snapshot/numeric.pop.json: fb2acc03e0e94531edd33d5ac454432251f0876104bc9773e667c094224c21b5
- tests/fixtures/compiled-snapshot/numeric.steps.json: 2144a7440654be1c1d36a5efbc683d1a116f9aea49655b5595aba9cb451502b3
- tests/fixtures/compiled-snapshot/pre.pop.json: e92175e8a7b2cea764416603b1da840ab3e9b28af6f3d29e3f3bee350a109d9a
