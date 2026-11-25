---
milestone: seeded-routes-and-identifiers
station: phase-SI4
skill: "n/a -- repository development"
scope: phase-SI4
date: 2026-11-25
gates:
  - command: "uv sync --offline --locked --group dev --python 3.11"
    exit: 0
    output: "Installed editable get-nick-done 0.5.2"
  - command: "uv run --no-sync pytest -q tests/test_release_version.py tests/test_release_text.py tests/test_release_docs.py --tb=short"
    exit: 0
    output: "85 passed in 0.60s"
  - command: "uv run --no-sync python tools/release_text.py check"
    exit: 0
    output: "No page describes the state before 0.5.0 was published; 0.5.2 is tag-only"
  - command: ".venv/bin/gnd --version"
    exit: 0
    output: "gnd 0.5.2"
  - command: ".venv/bin/ruff check src tests tools"
    exit: 0
    output: "All checks passed!"
  - command: "python3 .codex/skills/process-phase/scripts/review_tool.py run .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI4-r1 --reviewer claude --wait"
    exit: 0
    output: "VERDICT: APPROVE, no findings"
evidence:
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/phase-SI4-spec.md
    sha256: 4e7fd3b45fc683054817cfb2f9c4c0a532933b00cfa9f34137d33023d2e55111
  - path: pyproject.toml
    sha256: 48ae2383765cec78ff87591f40dbebe8c0b558cebc0394613c2c0292a945d766
  - path: uv.lock
    sha256: a8bf8a6a367ac116f1ac8531ad19349c22c497b6cbfb2c21bbf47d4c25ee23c1
  - path: .claude-plugin/plugin.json
    sha256: 1551fd6e7cfe078ee01b75755eb4b75b90b2a9dd6600de850646800ae1fb503e
  - path: .claude-plugin/marketplace.json
    sha256: 01e00a21f2db5ec81130ea1d32136cc6a94f1e1062e3901008c05cb4055211c8
  - path: .codex-plugin/plugin.json
    sha256: 286e0d3b4a41352797b06340148f5cc43e06627d44631aab1f2f612197138ccb
  - path: tests/test_release_version.py
    sha256: aa7b6ec975ea944806dff16d12f9980fb4343142021312b4a5d396bd4077f90d
  - path: docs/release-notes.md
    sha256: 4cd8cca18d8d4f91f4a5543ab4ea675305d80a271f33ba3dfcbdf050338cacb1
  - path: docs/compatibility.md
    sha256: 7557ce453df44b26a0b9b0ae607946db54a6bc27366f4556b1fb1cccbd12139b
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI4-r1/BRIEF.md
    sha256: ccdaf7a0dda32e40c28a021a818ae00f8e2aef5c5764a59d1d3b743e71295d4e
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI4-r1/brief.json
    sha256: 4f0ca32270a73ef1476bf3eeccc3c652a890a814ff06b8346ae9be4893c93e4f
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI4-r1/diff.patch
    sha256: 706f2ab1e5e4fc8fe7b94db90d48439067c35d3e7382ab662e93a0c15f9eed16
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI4-r1/review.md
    sha256: 18bdaf8a0ff9d5e91cbd0562fb40e7c4210f571c09852b474bab3a9fe742e195
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI4-r1/run.json
    sha256: a36211eb340bb4a862bc08884298cad798316aa8aa2b5ace96dd734676fd3c23
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI4-r1/FINDINGS.md
    sha256: cbda01078636d9fdbe07ea02bcdd7d2aa2c6d46e9b4b36d9bfa90e4b5293a47c
---

# Claim

SI4 prepares 0.5.2 as a GitHub tag. The five version fields agree and the
three pending release notes are under 0.5.2. The package-index release
record and install pins are 0.5.0.

## Review and release gates

Claude Code Opus independently verified the brief and tracked diff, ran
the 85 release tests and the release-text check, and approved the diff.
The reviewer noted an existing single-line input convention for the
`TAGGED` reader. The edited metadata follows that convention.

The owner authorized the separate release-preparation merge and annotated
tag after the implementation merged in
[PR #294](https://github.com/vasiloglou/gnd-public/pull/294).
The close record will contain the remote tag and merge verification and
the full default test lane on the merge commit.
