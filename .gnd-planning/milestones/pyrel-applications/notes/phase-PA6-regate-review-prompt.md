# PA6 bounded repair reading after the re-gate

This is PA6's one remaining repair reading (the initial PA6 Claude review is
notes/phase-PA6-claude-review.md). No third pass. One reviewer is one reviewer.
Read/search only; read-only git diff/show/status/log are allowed. Do not run
Python, tests, native tools, providers or agents. Do not open .env files,
credentials or .agents/skills. Make no file edits.

Read notes/phase-PA6-spec.md (including the re-gate paragraph at its end),
012-ci-repair.md and 011-phase-PA5R.md, then git show c0039e4 and 3783051, and the
run-E evidence: evidence/PA6/install-regate-e.txt and evidence/PA6/e-*.json
(receipt, corpora, learning-path receipts, isolation proofs).

Decide: (1) whether the initial PA6 review's findings that the spec says were
repaired are actually reflected in the committed harness and run E; (2) whether
the new constants (7,59,8)/(4,45,10) match the actual receipts' records;
(3) whether run E's receipt binds the committed harness (source identity commit,
harness SHA, sources, tools, site config) and the PA6-C1..C4 claims; (4) whether
the CI repair (012) weakened any guard rather than fixing its cause.

Report: verdict; numbered findings with severity (blocking / hardening /
completeness) and file:line; reading bounds.
