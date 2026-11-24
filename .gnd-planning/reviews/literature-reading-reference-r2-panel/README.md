---
milestone: literature-reading-reference
station: panel
scope: plan r2 (first round)
date: 2026-11-23
gates:
  - command: "uv run python tools/run_gnd_review_panel.py review-request.json --out panel-run --reviewer-timeout 600 --overall-timeout 900"
    exit: 0
  - command: "uv run gnd review finalize panel-run synthesis.json --out PANEL-REVIEW.md"
    exit: 0
evidence:
  - path: .gnd-planning/reviews/literature-reading-reference-r2-panel/PANEL-REVIEW.md
    sha256: 3e39b57d57d2a3ee744535dd97e2b0005f0ca3093a631b8e5ba0b67860d686c8
  - path: .gnd-planning/reviews/literature-reading-reference-r2-panel/review-request.json
    sha256: 161ff11d0d46b50219e22fdde6b5a9e442dcc28ca5d241b982ff6d87d1ab8c94
  - path: .gnd-planning/reviews/literature-reading-reference-r2-panel/synthesis.json
    sha256: 768b7cd91da6b509580c5433c8c4ffc0964fcec8179a0ec031e0af69772db8f3
---

# GND panel on the literature-reading-reference plan, r2 (first round)

The owner selected the full GND panel for this milestone's plan and close
review on 2026-11-23 ("Full panel, both", relayed by the coordinating
session). The reviewed artifact was
`.gnd-planning/milestones/literature-reading-reference/notes/literature-reading-reference-plan.md`
at SHA-256 `4960c18dfcf59c7b15b0ca0da1964ae5a4bf6c5034d43455dfb21c8cac97dee2`
(plan r2). The LR1 draft spec and the milestone README were context only.

The run used a disposable local clone at commit `11a7ebf7` with no
uncommitted files. The panel implementation matched HEAD and `gnd` imported
from the clone. The trusted launcher loaded the two panel credentials by name
and the OpenRouter preflight passed. After the run, `git status` in the clone
showed only the request and the panel outputs. Run digest
`24c570d4a176390b4eec57b55f95d1844d5e057642e87011f096990d8e7c6ada`. The raw
reviewer streams were copied unedited; the panel had already masked the
operator's user name in the scratch paths they contain.

## Reviewer outcomes

Six fixed IDs were attempted and five succeeded:

- **Codex:** `block`.
- **Claude, Qwen, Kimi and GLM:** `revise`.
- **Gemini:** `malformed` (no schema-valid response).

Kimi's response is retained as incomplete (nothing dropped). Claude and GLM
share one CLI codebase. Qwen reviewed the inline plan bytes only and ran no
probe.

## Agreed concerns

1. LR2 says the packaged example verifies against one shown section; it
   verifies the attempted sections of a pass joined, with no sidecar
   (Claude, Codex, Qwen; high).
2. The lint gate and H22 are stale against `project.md` (Codex, Kimi; high).
3. D7 (b) changes the default text output (Codex, GLM; medium).
4. Section 1 paths lack the `src/gnd/` prefix (Claude, Kimi, GLM; low).

Sixteen divergent concerns are listed in [PANEL-REVIEW.md](PANEL-REVIEW.md).

## What the driving agent reproduced

- Qwen's high concern that a verdict has no `verdict` field: **refuted**. The
  live report carries `"verdict": "fail"`.
- Kimi's concern that an include resolves against the working directory:
  **refuted** (a run from the parent folder exits 1). What holds is that the
  vocabulary lives in `depth_fixture/` and must be staged beside the model.
- Whole-repository `uv run ruff check` exits 0 at `11a7ebf7`: **confirmed**.
- Derivation failures set exit 1 (`_reports.py:113-116`): **confirmed**.
- `assurance_report.py` reports precision and recall against an answer key:
  **confirmed**.

## Disposition

All seven prioritized fixes are applied in plan r3; its §11 maps each fix to
its sites. A second round reads r3, under the budget and the stop criterion
declared in r3 §8.

The panel is advisory. This record is not an approval.
