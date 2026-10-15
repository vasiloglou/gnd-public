---
milestone: pyrel-agent-loop
station: phase-PL18
skill: "n/a -- repository development, not a gnd-solve station"
scope: phase-PL18
date: 2026-10-15
source_base: 05eedd7
gate:
  command: "uv run python tools/run_tutorials.py --group plan-apps"
  exit: 0
  output: "19 tutorial blocks passed"
docs_gate:
  command: "uv run pytest -q -p no:cacheprovider tests/test_documentation_tutorials.py tests/test_pyrel_learning_path.py tests/test_pyrel_tutorial_experience.py tests/test_tutorial_output_blocks.py tests/test_figures.py tests/test_figures_render.py tests/test_plan_app_docs.py tests/test_replays.py tests/test_plan_app_recordings.py tests/test_plan_app_recording_tools.py tests/test_marketplace_plugins.py tests/test_release_docs.py tests/test_pyrel_applications_install.py tests/test_public_readme_fallback_limits.py"
  exit: 0
  output: "292 passed in 88.89s (0:01:28)"
build:
  - {command: "uv run --group docs zensical build --strict", exit: 0, output: "Build finished"}
  - {command: "uv run python tools/check_docs.py site", exit: 0, output: "10091 local links/assets/anchors checked"}
acceptance:
  command: "uv run python tools/accept_pyrel_applications_install.py --out <scratch>/pl18/accept"
  exit: 0
  output: "fresh wheel target-only application acceptance complete (before the review fixes, which touched pages and tools, not the packaged examples' code)"
recording:
  command: "tools/record_skill_sessions.py --authorized-by .gnd-planning/milestones/pyrel-agent-loop/019-recording-gate-PL18-skills.md --out <scratch>/pl18/skill-rec2; then --finish on a copy"
  exit: "1, then 0: the leak search refused the first result (a /tmp listing, Claude Code paths); --finish applied the keep filter and the second leak search passed"
evidence:
  - {path: "docs/tutorials/course-planner.md", sha256: "eca70a965415a6214576c761439d053b85cfc18de094da5de826e086d29d757c"}
  - {path: "docs/tutorials/clinic-refills.md", sha256: "21ea8f1930841865a53001d1a6acae53fd18e392197be656177060b602523c0b"}
  - {path: "tools/render_replay.py", sha256: "89c86c99514c9ab566602861464a3b2bf5fb99cb356d3af2c2ef63f426bca560"}
  - {path: "tools/record_skill_sessions.py", sha256: "c0063877fc24189deb29ae1c84bb37c0c2dd9834fc23849f8244785ebeb14150"}
  - {path: "src/gnd/examples/plan_apps/skill-sessions/manifest.json", sha256: "8c571da3292432d1c43febc419f37eada173865ad19cdf31bfe3c396723b49a5"}
  - {path: "docs/assets/replays/replays.json", sha256: "1633be9077d095c1d4a5fe188b0f19d3e614d53772a3dfe28f843df2b673ef52"}
  - {path: ".gnd-planning/milestones/pyrel-agent-loop/notes/phase-PL18-spec.md", sha256: "bb5486020218e69d25db92835c2af73ae0a917a933237724eb613041b5777e31"}
  - {path: ".gnd-planning/milestones/pyrel-agent-loop/notes/phase-PL18-claude-review.md", sha256: "16bec3ed999e3f306024d29ee831e92f2b150591f649306ad9d9f18305dd7fd1"}
checkpoints:
  - "C8, 2026-10-15: https://claude.ai/artifact/UeP4QfAHbeaGPLVnZtSSCr (the Course tutorial). Owner: \"looks good\""
---
# Phase PL18: GSD-style pages for the plan apps, built from real runs

Spec: [notes/phase-PL18-spec.md](notes/phase-PL18-spec.md), delegated approval
(auto=true) under the owner's approval of the C2 mockup and of checkpoint C8
("looks good"). Gate for the skill recording:
[019-recording-gate-PL18-skills.md](019-recording-gate-PL18-skills.md), with its
amendment. Amendments A1–A8 are in the spec's §11.

## What landed

- **Tutorials:**
  - `docs/tutorials/course-planner.md` in eight steps: rules; a recorded
    Claude Code session running `/gnd:gnd-model-from-text`; the rules in
    PyRel in full; ask; the first course run refused on a rule then accepted;
    the checker's verdict; the published state; a real evolve proposal that
    refuses the accepted plan;
  - `docs/tutorials/clinic-refills.md`.
- **How-to pages:** access, trip and lease, plus the recorded model runs.
- **Explanation:** a rule in its LQP and DuckDB forms, printed by a runnable
  block.
- **Home page and README:** the eight-step loop with slash commands, the
  plugin Quickstart and the new pages.
- **`tools/render_replay.py`.** A recorded session becomes an SVG card in the
  figures' theme tokens, static under reduced motion, followed by its
  transcript. `replays.json` lists each source.
- **`tools/record_skill_sessions.py`** and
  `src/gnd/examples/plan_apps/skill-sessions/`: four sessions (Haiku and the
  default model, 2 each), every model valid.
- **The A1 figures fix**, the `plan-apps` runner group, and acceptance
  copying `plan_apps`.
- **Tests:** `test_plan_app_docs.py` (20), `test_replays.py` (26),
  `test_figures_render.py` (1).

## Review

One reviewer is one reviewer: a single Claude subagent, same model family, with
no paid calls. Its report is retained verbatim in
`notes/phase-PL18-claude-review.md`. Verdict: REVISE.

| # | Finding | Triage | Disposition |
|---|---|---|---|
| B1 | "the bot gets the PyRel line" | blocking | corrected: the bot gets the rule, where and the facts; the line is for the reader |
| B2 | "all ten Claude clinic runs right" | blocking | corrected to nine; `claude-haiku/clinic/run-3` planned for the host's date. That exposed a model gap (no rule ties a refill to the day), and the page now states it (A7). The false "today is a fact" claim was removed |
| B3 | skill-session prose; stop rule misfired | blocking | prose corrected; misfire disclosed; recorder fixed (A8) |
| B4 | engine overclaim | blocking | "compiled and counted, not yet run on an engine"; agreement claimed for the DuckDB program only |
| B5 | test_documentation_tutorials fake wheel | blocking | fixed |
| B6 | "most failures unusable" | blocking | "many" (82 of 180) |
| B7 | "part-time" rule unmodelled | blocking | reworded as a general cap; proposal regenerated (A1) |
| H1 | "recording order" | hardening | "the order of the results table" |
| H2 | replays could drift from their runs | hardening | names bound to sources; folders required on pages; the reviewer's mutation is now caught (`pl18/mutation-h2.out`) |
| H3 | step 8 block could not fail | hardening | `&& echo applied` |
| H4 | replay hid refused calls; transcript not verbatim | hardening | refused calls marked; transcript labelled condensed, with the full session linked |
| H5, H6, H7 | thinking claim; null costs; keep-filter looseness and agent activity | hardening | disclosed in the skill-session README; recorder fixed |
| H8, H9, H10 | wrong note, lease reasons, checker attribution | hardening | corrected; each page names its checker |
| H11 | typed excerpts | hardening | pinned to the generated lines and rules.md by a test |
| H12, H13 | same-input claim; identical replay labels; D2 timing | hardening | corrected; labels from titles; D2 amended (A2) |
| completeness | Quickstart prompt, README loop, published state, clinic table | completeness | the loop, state and table added, the table pinned; the prompt withdrawn (A3) |

Pre-fix evidence:
- the figures test failed on HEAD's pages (`pl18/prefix-figures.out`);
- the replay-id test failed on the first renders, whose `3.2` ids broke their
  CSS (found in the rendered review, before the reviewer);
- H2 is the reviewer's mutation, now caught.

## Refactoring review

Executed:
- The replay renderer is the one home for turning a recording into a page
  figure.
- `replays.json` is the one list of what each page replays.
- `record_plan_apps.readme_table` and the README section markers are the one
  source of the runs table that the How-to page includes.

Deferred: none beyond the open questions below.

## Boundary

- **Recordings from earlier phases are shown as recorded.** The Clinic gap
  (A7) and PL16-Q1's fidelity gaps are stated, not fixed.
- **The skill-session replay is condensed.** The kept transcripts drop most tool
  output, by design.
- **Not done:** per-skill How-to pages, and moving BookRec ch. 7 / Expense ch. 4
  to Reference (D7).

## Open questions

| # | Question | Target |
|---|---|---|
| PL18-Q1 | Per-skill How-to pages; BookRec/Expense chapters to Reference | after PL19 |
| PL18-Q2 | Clinic model: tie a refill to the day (shown by `claude-haiku/clinic/run-3`) | with PL16-Q1 |
| PL18-Q3 | GND: `gnd validate` refuses a model with references through a symlinked path; `gnd check` exited 70 ("derived origin lineage missing") in `claude-default/run-2` | checker issues, outside this milestone |
| PL18-Q4 | `test_development_scaffold` fails on a code-span link in the approved `plan-amendment-a1.md:10` (inherited since PL12) and on an untracked `.claude/worktrees` checkout | PL19 |

## Owner feedback after the commit (2026-10-15)

On the review copy, the owner asked that the Haiku skill replay explain its
failures: why each failed, what the issue was, and how `gnd validate` helped.
The recording holds the answer:

- **Four chained shell commands were refused by Claude Code's permission rules.**
  This includes `gnd validate ...; echo "EXIT=$?"`. They are listed in the
  turn's `permission_denials`.
- **One combined read returned an error.** Its output was not kept.
- **The modelling mistake.** Two readings had their placeholders out of role
  order (`student_course_grade`, `student_credits_in_term`). `gnd validate`
  refused the model with `semantic:reading-placeholders`, naming each fact type
  and position. Haiku fixed both with two edits, and the model validated.

Changes:
- The replay marks each failed call with its reason, and keeps the failing
  command visible.
- Step 2 of the course page gains "What went wrong, and how it was caught", with
  the two readings before and after and the verbatim errors.
- A test pins the quoted errors, edits and denial count to the recorded session.

Gate after the change: 293 docs tests, 19 runnable blocks, 10095 links.

## Owner feedback: PyRel is optional, and what app.py is (2026-10-15)

The owner noted that step 3 read as if PyRel were required, and asked what
`python plan_apps/course/app.py rules` is, since GND's commands start with
`gnd`.

Changes:
- **A new page,** `docs/explanation/what-is-pyrel.md`, says:
  - you don't need PyRel to use GND;
  - PyRel is RelationalAI's Python library, an optional extension for facts
    that live in a data platform;
  - you can prototype locally on DuckDB, or reach Snowflake through
    RelationalAI's Native App;
  - what GND has tested: GND's checker, and the DuckDB program, which agrees on
    every recorded plan;
  - what it has not: the RelationalAI engine path is compiled, not run;
    "Snowflake execution is not yet supported by gnd export".
- **Step 3** is "Optional: read the rules as PyRel". It links that page and
  shows the GND command `gnd export pyrel ... --rules lqp` beside the app's
  printout.
- **"Before you start"** explains that `app.py` is the example's own program
  built on GND, not a GND command, with a table of its four commands. It points
  to `/gnd:gnd-codegen` for a project of your own.
- **Every page that mentions PyRel** marks it optional and links the new page.
  The recorded checks are attributed to "the app's optional PyRel backend".
- **Tests** enforce the link and the "optional" wording on every page that
  mentions PyRel, the `app.py` explanation, and the untested-path statement.

Gate after the change: 303 docs tests, 20 runnable blocks, 10277 links.
