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

- .gnd-planning/milestones/compiled-snapshot-obligations/notes/phase-CS0-spec.md: ef0a16ae838103e4b6f0b22cbe406142ea57d934b888558bb2877dee0a32fcef
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CS0/baseline.json: 76edf5cd9b0dd4dc6f58995223454f77ce8bf3dd1ba116e1b2bad62bbfdb7c72
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CS0/corpus-red.txt: f37fe3b5bed88e47a8f791574fc9e15b4e34438ec9b1f66b3624e293dc07fee8
- tests/test_compiled_snapshot_obligations.py: 5dd8a0270074d5e310db15a8cb6048efe71255ea681cf39bab39cb3bac409efa
- tests/fixtures/compiled-snapshot/README.md: 031b1865a423b98765e3ea13517c138b2c57d5ba5489603b218b46cd439e0b29
- tests/fixtures/compiled-snapshot/expected.json: 4fdfcd186bf459f11360fee4fb1f91d6d4e6e805d7137fc131c885e82c53122f
- tests/fixtures/compiled-snapshot/model.orm.json: 2aafee2d38aed67ea5954eb4c08c632bcba61cc801ea703bd3e9b5a9d68dc44e
- tests/fixtures/compiled-snapshot/nonnumeric.pop.json: 68926ae461d209cb6c56e48337860becdbd4c4c71f9b74c0713b1a4b146436b3
- tests/fixtures/compiled-snapshot/nonnumeric.steps.json: d898f3fb7fe7d80afe0d8e046901418575a4ea925846495157f2c788c3f7b579
- tests/fixtures/compiled-snapshot/numeric.pop.json: 80e55944d1c465869702b32bfa91951f2363a48a4ce33bfd6a86e33c3b6b736e
- tests/fixtures/compiled-snapshot/numeric.steps.json: 57f4dcc0b000e22056ca1cfd46aee6d34631358cf66957e0c3ca950047071f06
- tests/fixtures/compiled-snapshot/pre.pop.json: d5eec6b121e61f8a9d3973f20b69ffa1273af3faf54a415f01057dc3d0d4a9ea
