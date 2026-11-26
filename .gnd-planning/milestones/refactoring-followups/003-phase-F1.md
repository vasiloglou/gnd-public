---
milestone: refactoring-followups
station: phase-F1
scope: phase-F1
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
date: 2026-11-25
gates:
  - command: uv run pytest -q tests/test_poolfile.py tests/test_rf9_ci_repairs.py tests/test_rf7_input_policy.py tests/test_rf7_consumers.py --tb=short
    exit: 0
  - command: uv run ruff check src/gnd/synth/poolfile.py tests/test_poolfile.py
    exit: 0
evidence:
  - path: .gnd-planning/milestones/refactoring-followups/notes/F1-Claude-review.md
    sha256: 152978de22eacefad347ae76b99aaa06a1f077284c4846e292ffaf51e9373de7
---
F1 complete by delegated approval (auto=true). Commit d217e7a7. At base the oversize case raised plain ValueError. The accepted loader now reads at most MAX_BYTES+1 and supplies the specified finding to callers. The phase added four tests, including strict UTF-8, CRLF at the physical limit, guarded read size and timed large-file refusal.

    183 passed in 5.74s
    All checks passed!

The helper invocation exited 1 before review. Claude Code received the identical brief on stdin in the isolated clone, exited 0 and approved. The derived component page was regenerated after the reviewed diff. Refactoring review retains the explicit physical cap message and newline conversion. Both preserve the measured contract. S1 may be revisited if F4 introduces a shared byte-refusal vocabulary; S2 had no reproducing discrepancy. No broad historical suite ran. Slow cadence: uv run pytest -q -m "evidence or census".
