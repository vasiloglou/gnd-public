---
milestone: literature-host-interfaces
station: panel
scope: plan r4
date: 2026-11-23
gates:
  - command: "uv run python tools/run_gnd_review_panel.py review-request.json --out panel-run --reviewer-timeout 600 --overall-timeout 900"
    exit: 0
  - command: "uv run gnd review finalize panel-run synthesis.json --out PANEL-REVIEW.md"
    exit: 0
evidence:
  - path: .gnd-planning/reviews/literature-host-interfaces-r4-panel/PANEL-REVIEW.md
    sha256: 9e761cbc0f7650917f08a17d90b07e7901a06434d2a3e80f700dc27c4ae772ac
  - path: .gnd-planning/reviews/literature-host-interfaces-r4-panel/review-request.json
    sha256: 8b1e222aad78fe0e655e4dddc9af4513720fa172c49160789a8c73b157c39004
  - path: .gnd-planning/reviews/literature-host-interfaces-r4-panel/synthesis.json
    sha256: 2287826b96e0b1ccabf9857c0a27e0d8abe47815d0e3ba115b18987342969926
---

# GND panel on the literature-host-interfaces plan, r4

The owner selected the full GND review panel for plan r4 on 2026-11-23
("full"). The reviewed artifact was
`.gnd-planning/milestones/literature-host-interfaces/notes/literature-host-interfaces-plan.md`
at SHA-256 `6cadaa9134585b348d53ef50ef5c35638a3b0bb20c7c36726ac53039ac357cb6`.
The LH1 spec and the milestone README were offered as context only.

The run used a disposable clone at commit
`4ad0d2168f7fd59be0b76ac97216768ea1277b90` with the three uncommitted planning
files copied in; the panel implementation matched that HEAD and `gnd`
imported from the clone. The two panel credentials came from the trusted
launcher, by name; the OpenRouter preflight passed. After the run the clone's
`git status` showed only the copied planning files and the panel outputs.
Run digest `1e9f693f2f3fe4a226536d5cc0f0f87e6fd0dd2ccfacd94b8834e5e4250f4522`.

Six fixed IDs were attempted and four succeeded: Claude, Codex, Kimi and GLM,
all `revise`. Qwen timed out; Gemini returned malformed output. Kimi's
response is retained as incomplete (one preamble line, nothing dropped).
Claude and GLM share one CLI codebase.

Two concerns are marked blocking, each by one reviewer: R0.4 promises one
admission projection, but the D10 ruling keeps the packaged admission on its
own path (Claude); the plan's narrowed lint gate conflicts with the project's
whole-repository rule (Codex). Two concerns reached agreement: the 64 KiB
response-cap default is not today's constant (Claude, Kimi, GLM), and two H10
line citations are off (Claude, GLM). Twelve fixes are ranked in
[PANEL-REVIEW.md](PANEL-REVIEW.md).

The driving agent re-checked the cited facts at `4ad0d216`; each held:
whole-repository `uv run ruff check` exits 1 with 198 findings, all in the
dev-tools-delivered skill scripts (`review_tool.py`, `rules_check.py`,
`handoff.py`), while `project.md` says it exits 0;
`assurance_report.py:760` and `:725`; `reading.py:38` has two scenario values;
`test_ld3_reading_workflow.py:160` calls `_inspect` directly; `reading.py:300`,
`:320`, `:323` and `:335` carry calibration literals; `reading.py:270`
refuses any exit outside the allowed set, and the checker can exit 4
(`checker/_core.py:423`). The panel is advisory. No fix has been applied.
