# Close reading four — honesty, rules and merge readiness

Date: 2026-10-13. Instrument: owner-selected independent local reader (read-only), one of four close readers; condensed by the orchestrator with findings, verdicts and cited lines preserved. Subject: HEAD cd80edd.

Findings:
1. Blocking: tools/gnd_layers.json conflicts with origin/main (branch adds gnd.export.applications; main adds gnd.semantic_origins, gnd.extension_preparation, gnd.population_shape). Keep all; rerun layer/rf6/rf7/rf9 and the full suite on the merged tree.
2. Blocking: no full-suite record on the final tree (only 50eba83, 6 failed). Run the local CI mirror on the merged commit and bind it.
3. Residual: 012:32 native "1 failed, 94 passed" lacks a transcript; all other cited hashes match.
4. Residual: documented setup (index install of 0.1.0, base 3.13) is not the measured path (local wheel, base 3.11.15); runtime-environment path and lock pins confirmed.
5. Note: Snowflake wording honest and code-backed (pyrel_runtime.py:1863-1865, :1881-1886; applications.py:35); "not yet" and commands/export.py:55 help text acceptable as boundary.
6. Note: agentic framing honest.
7. Note: layer map and skill twins conform; do not commit .agents/skills, .claude/launch.json.
8. Residual: commit grammar drift (missing bodies/record lines in b4bbf4f, 211a23f, 04ebec9, 50eba83, 00efef2, cbccf13, e4357ab; scope-token drift). Note in close; do not rewrite history.
9. Residual: 013 does not bind notes/phase-PA6-claude-review.md; empty regate stderr untracked.
10. Open questions for the close: successor split, B3, Expense candidate identity, rel_reflexive, source identity.

Merge checklist: resolve conflict via merge into the branch; local checks on merged tree retained; transcript and bindings; close record; PR out of draft, conversations resolved; explicit owner merge authorization on final bytes; check branch protection before claiming enforcement; do not commit machine-local files.
