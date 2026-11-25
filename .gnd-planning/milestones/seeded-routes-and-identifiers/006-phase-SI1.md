---
milestone: seeded-routes-and-identifiers
station: phase-SI1-repair
skill: "n/a -- repository development"
scope: phase-SI1
date: 2026-11-25
gates:
  - command: "beast-3, shard 2, uv run --no-sync pytest -q --tb=line -p no:cacheprovider <shard-2 files>"
    exit: 1
    output: "FAILED tests/test_packaged_skills.py::test_every_relative_skill_link_resolves_inside_the_resource_tree"
  - command: "uv run --no-sync pytest -q tests/test_packaged_skills.py tests/test_development_scaffold.py tests/test_si1_seeded_routes.py --tb=short"
    exit: 0
    output: "176 passed, 1 deselected in 29.25s"
  - command: ".venv/bin/ruff check tests/test_packaged_skills.py"
    exit: 0
    output: "All checks passed!"
  - command: "python3 .codex/skills/process-phase/scripts/review_tool.py run .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI1-r2 --reviewer claude --wait"
    exit: 0
    output: "VERDICT: APPROVE"
evidence:
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/002-phase-SI1.md
    sha256: 98225d7db5cb912ee5a0b16166fd1c45f80339843031ae2d0f34ec9b64d5cef1
  - path: tests/test_packaged_skills.py
    sha256: 962093d37de52031c6c0840e1ba81ef66899a31e305b26ae73d02dda798a6f01
  - path: src/gnd/skills/gnd-model-from-text/references/unattended-growth.md
    sha256: eb004b90f123ac034ca8553306bffdf6532d20554c0273f15f7728c01f48a309
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI1-r2/BRIEF.md
    sha256: 242eef618d1324e776194cb8902934d9850d73c3e9a965cd1376762ad3b7ad3a
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI1-r2/brief.json
    sha256: b3b77e96fbeaf586b0d7d35896117a9dc56400f553e7fa0522d865e5ea441d83
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI1-r2/diff.patch
    sha256: a81518319d1e16e796297441f9278ce0055eabfbf0c4950ca51ece939d6a9392
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI1-r2/review.md
    sha256: 066e7cdb49c4bb8d2a432b70a62786bca1016ceea9374992ac3fe258cab964de
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI1-r2/run.json
    sha256: 31c50d87e156c78277ee3133944c8c3f588675e4b666851def591845f789069d
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI1-r2/FINDINGS.md
    sha256: eb55e2ca5c90e78a2d6cee4a514d7564a3a3014d0921e84da2416ffebb806bd4
---

# Claim

The packaged skill link inventory now includes the intentional SI1
citation from the unattended growth guide to the extraction flattening
record. The guard still compares exact link membership and checks the
total number of mentions.

## Reproduction and repair

Shard 2 on release-preparation merge `4f2945a95fd0e9bd1de0103caa190da7616bb159`
failed on exactly one unexpected edge. The guide's paragraph directs
callers of a named standalone refusal back to their authored root and
links its flattening contract. The target path exists and its
“Extraction flattening record” heading supplies the anchor. The
repair records that edge and increases the expected count from 248
to 249.

## Independent review

Claude Code Opus checked the original red failure and the passing
51-test packaged skill file. Removing, duplicating or retargeting
the new link still failed the guard. The reviewer identified the
existing aggregate-count limit for two offsetting changes in mentions
and an optional provenance comment. The findings ledger records both
dispositions. Product code, package version and release text are
unchanged by this repair.
