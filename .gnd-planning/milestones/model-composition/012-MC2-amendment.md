---
milestone: model-composition
station: "MC2 measured comparison amendment"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: MC2-amendment
date: 2026-11-10
gate:
  command: "ruling: delegated (auto=true) amended MC2 replay comparison .gnd-planning/milestones/model-composition/evidence/MC2/corpus/answers.json sha256 94e93dce968908f5923c0c303555494b071bebd1a7c35da7259b16b9b63c40a0"
  exit: n/a -- ruling
evidence:
  - path: .gnd-planning/milestones/model-composition/evidence/MC2/corpus/answers.json
    sha256: 94e93dce968908f5923c0c303555494b071bebd1a7c35da7259b16b9b63c40a0
  - path: .gnd-planning/milestones/model-composition/evidence/MC2/010-approved-answers.json
    sha256: 087a3cb6f7933c96b148ecea14a32ebf6a7601a99eeb3abf38e780a0cd5c145e
  - path: .gnd-planning/milestones/model-composition/evidence/MC2/012-approved-spec.md
    sha256: 031fe06dd0da43442a87963bf34aafbce975a9dc6588b1c3bc99febf88fcec77
  - path: .gnd-planning/milestones/model-composition/evidence/MC2/red-corpus-comparison.json
    sha256: 8f843d12353b92bea14dd1976e678a9f98ac622302b72820f47f338e49bc389c
---

# Claim

Delegated approval corrects only C03's comparison allowlist and requires independent digest checks before its successor harness is accepted.

## Gate output (verbatim)

Delegated ruling,2026-11-10. Authority: current owner request, process-milestone model-composition auto. Approve the exact C03 successor: model/population coordinates, model_digest and composition.record_sha256 are the only admitted differences; independently verify each from retained model/record inputs, and compare all other fields and full lineage. Preserve the original answer and gate. No report, identity algorithm, schema or production behavior changes; the one-review/one-confirmation budget and375/600 stop remain.

## Finding and boundary

The new public composition/replay reaches exit0; the full corpus run has22 passes and one comparison failure. The output identifies model_digest and composition.record_sha256. The original frozen record contains the authored model SHA, so its changed record SHA is required by the unchanged record format. This is a measured harness correction, not a waiver of a product criterion or a claim that the corrected checks passed. The prior gate's C03 comparison claim is superseded by these exact bytes; all other answers retain their meaning. No owner personal reading, new review round, merge, docs acceptance or milestone close is established.

## Open questions

- Run the corrected C03 harness, independent digest checks and the full focused impact selection.
- Address the owner's higher-level real-example documentation feedback on the separate checkpoint branch and record the actual reply in the final MC4 spec.
