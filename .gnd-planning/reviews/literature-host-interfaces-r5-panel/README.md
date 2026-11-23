---
milestone: literature-host-interfaces
station: panel
scope: plan r5 (second round)
date: 2026-11-23
gates:
  - command: "uv run python tools/run_gnd_review_panel.py review-request.json --out panel-run --reviewer-timeout 600 --overall-timeout 900"
    exit: 0
  - command: "uv run gnd review finalize panel-run synthesis.json --out PANEL-REVIEW.md"
    exit: 0
evidence:
  - path: .gnd-planning/reviews/literature-host-interfaces-r5-panel/PANEL-REVIEW.md
    sha256: 73e3c873b36f9e8593c28495625889c31c60510b4c2e253443a89d7dd01866f6
  - path: .gnd-planning/reviews/literature-host-interfaces-r5-panel/review-request.json
    sha256: f887eec1b52289a1c4482678205cb69e1f8aa5eab0de3f0f74ec0474ccd58b4f
  - path: .gnd-planning/reviews/literature-host-interfaces-r5-panel/synthesis.json
    sha256: cba2f2ad715dbf6296686a7493661b05fc8079d4f79c7a3b0be9d73e0cdf03fe
---

# GND panel on the literature-host-interfaces plan, r5 (second round)

The owner asked for a second round over plan r5 on 2026-11-23 ("Run round
two"). The review convergence rules allow two rounds, so this is the last one.
The reviewed artifact was
`.gnd-planning/milestones/literature-host-interfaces/notes/literature-host-interfaces-plan.md`
at SHA-256 `c1a832378a2f303cdf1be8884ea61e745eca7f22e4fab19a449761d62b082c9b`.
The rubric asked each reviewer to check whether r5 resolves the first round's
twelve fixes ([r4 panel](../literature-host-interfaces-r4-panel/README.md)).
The LH1 spec, the milestone README and the first-round report were context
only.

The run used a disposable clone at commit
`4ad0d2168f7fd59be0b76ac97216768ea1277b90`. Every uncommitted file in this
worktree was copied into it, including the dev-tools re-sync from `a29562a`.
In the clone the whole-repository `uv run ruff check` exited 0, the panel
implementation matched HEAD, and `gnd` imported from the clone. The trusted
launcher loaded the two panel credentials by name, and the OpenRouter preflight
passed. After the run, `git status` in the clone showed only the copied files
and the panel outputs. Run digest
`614d4f74ff2d1b2b497dc7dfda6fbe8200574166bdea7fade3ae2d8cf1b99de1`.

## Reviewer outcomes

Six fixed IDs were attempted and five succeeded:

- **Gemini:** `approve`, with no concerns.
- **Claude, Codex, Kimi and GLM:** `revise`.
- **Qwen:** timed out.

Disclosures:

- Kimi's response is retained as incomplete: one preamble line, nothing dropped.
- One of Codex's three concerns (`lh1-combined-ceilings`) is unanchored.
- Claude and GLM share one CLI codebase.

Claude, Codex, Kimi and GLM each found most of the twelve r4 fixes resolved at the sites §11 names. Gemini found all twelve resolved.

## Agreed concerns

Three concerns reached agreement:

- **LH1-C14 cannot be met as written** (Claude, Codex and Kimi). Its completing run at the response and roster ceilings cannot fit the 64 MiB retained-file ceiling: 4,096 sections at 1 MiB each is about 4 GiB.
- **The start commit is wrong** (Claude, Codex and GLM). §3 starts LH1 at `4ad0d216`, which comes before the lint re-sync the plan relies on.
- **LH1-C10 misses two ceilings** (Kimi and GLM). It gives time-bound tests at five of D4's seven ceilings; route output and retained file are missing.

## Blocking concerns

Four concerns are marked blocking:

- **The retained-file bound refuses default runs** (Claude only). Under D4's defaults, the bound refuses the packaged runs and every default live run before the first producer call. A response cap and a retained-file cap of 128 KiB each cannot fit three scheduled sections.
- **LH1-C14** (Codex). This is the agreed concern above.
- **The start commit** (Codex). This is the agreed concern above.
- **LH3's attached-row rule contradicts LH3-C4** (Codex only).

## Hardening and completeness concerns

The other concerns are hardening or completeness, all from Claude:

- Replay of a `/1` run must keep the frozen two-argument `reading._read`.
- The plan does not say which fact type rules name on the packaged shape.
- `max_rows` on a packaged-shape call bounds nothing.

## Fixes and verification

Seven fixes are ranked in [PANEL-REVIEW.md](PANEL-REVIEW.md).

The driving agent re-checked the cited facts in the clone, and each held:

- §3 line 358 names `4ad0d216`.
- §2 LH1 'Retained files' (lines 244-247) has no scope limit.
- D4 (line 481) defaults both the response and retained-file caps to 128 KiB.
- The packaged roster schedules three opening sections.
- `test_ld3_reading_workflow.py:240-244` patches `reading._read` with `restricted_read(folder, name)`.
- `depth.py:55-56` defines `_read(root, name)` with no cap.
- Plan line 280 ("Every attached row of an admitted assertion is kept") and the limit at lines 288-290 are in separate bullets.

The panel is advisory. No fix has been applied.
