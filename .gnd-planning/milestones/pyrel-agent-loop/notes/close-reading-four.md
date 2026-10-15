# Close reading four: newcomer following the docs (HEAD 1c30525)

Scope: README.md, docs/index.md, tutorials/course-planner.md, tutorials/clinic-refills.md, how-to/*.md (4), explanation/*.md (2), zensical.toml nav. Every typed command was run in reader4-work/ with the repo .venv on PATH. No model calls.

## What reproduces exactly
Each output block matched byte for byte (diffed): the copy step and `ls`, `gnd validate` (course, clinic, access, trip, lease), `gnd export pyrel --rules lqp`, `app.py rules` (course 214-244, clinic 92-113), all five `app.py ask` stand-in transcripts, the course `next.pop.json` read-back with `pass=7 ...`, the evolve preview/apply returning `applied`, the post-evolve `check` (exit 1, credit_cap at states 2 and 3), the clinic late-refill warning, and the rules-as-pyrel grep pair. The date arithmetic is right (statin due 21 Mar, aspirin 65 days late). The clinic table (clinic-refills.md:233-239) and the course/access run claims agree with recordings/README.md:16-24. A 31 July lease payment does warn `not_in_last_week` (lease-schedule.md:100). All relative links and the `#2-model-them` anchor resolve. Every blob/main GitHub target exists locally. These will 404 until merge, which is noted here but does not block.

## Blocking
1. **The documented install cannot run the tutorials.** course-planner.md:38 says to install the plugin. The plugin page (marketplace-plugins.md:9-12), README.md:42 and index.md:144 install `get-nick-done==0.1.0` with `uv tool install`. That breaks the tutorials in two ways. (a) The tag v0.1.0 has no `examples/plan_apps` and no `--rules` flag (`git grep` finds `--rules` only at HEAD, in src/gnd/commands/export.py:85). (b) A uv tool install is isolated, so the bare `python -c "import gnd, ..."` at course-planner.md:43 fails with `ModuleNotFoundError` (I reproduced this with /usr/bin/python3). The same copy line opens clinic-refills.md:32, access-requests.md:25, trip-budget.md:22, lease-schedule.md:22 and rules-as-pyrel.md:31. pyrel-apps.md:40-48 already admits that the content is newer than 0.1.0 and installs from a checkout. These pages say neither. Fix: add the same "install from a checkout until the next release, into a venv where `python` sees gnd" note, or make the copy step not depend on `python` importing gnd.
2. **Step 8 leaves the reader in the wrong directory.** course-planner.md:441 runs `cd plan_apps/course`, and the next block (:454) runs `python plan_apps/course/app.py check plan_apps/course/plans/attempt-3.steps.json` from the original folder. Typed in one shell, it fails with `can't open file .../plan_apps/course/plan_apps/course/app.py` (exit 2, reproduced). The doc runner hides this because it starts each block fresh. Fix: wrap the block in a subshell, or add `cd ../..`.

## Confusing for a newcomer (non-blocking)
- **LQP is never expanded** in any doc. It appears at course-planner.md:196, 200 and 215, clinic-refills.md:94, what-is-pyrel.md:31 and rules-as-pyrel.md:43-48. A newcomer cannot tell the "lqp version" from the "DuckDB program".
- **DuckDB** is first mentioned at README.md:18 and course-planner.md:187 with no gloss. The gloss arrives in what-is-pyrel.md:23.
- **Populations and `.pop.json`** are never defined on the path (README.md:12; course-planner.md:334 writes `next.pop.json`).
- **"state N" / "states 1-3"** are explained only in passing (course-planner.md:301).
- **"witness"** is defined at course-planner.md:307 but used earlier in output. The access witness `[["bob","carol"]]` (access-requests.md:72, 114) is a bare list, so the reader cannot tell which value is the approver. Other rules print named `$var` objects.
- **The trip `no_overlap` witness uses unprefixed keys** (`"trip"`) at trip-budget.md:105. Every other witness uses `$t`-style keys, and nothing explains the difference.
- **README.md:16-18 overstates where the programs run.** It says "These programs run locally on DuckDB", but only the `--rules duckdb` program does. The LQP program is "compiled and counted, not yet run" (what-is-pyrel.md:40).
- **The Snowflake path reads as available.** course-planner.md:186-188 says "point the same rules at your data in Snowflake through RelationalAI's Native App" before the caveat, which comes only on the linked page.
- **what-is-pyrel.md:48-51 sends the reader to the wrong setup.** It says GND finds PyRel through `GND_PYREL_PYTHON` and points to runtimes/pyrel.md and runtimes/scenario.md. scenario.md:41 sets a different variable, `GND_TUTORIAL_PYREL_PYTHON`, and assumes a repo clone. The setup that actually exports `GND_PYREL_PYTHON` is pyrel-apps.md:53-55. Following the link as written leaves `--backend pyrel` unconfigured.
- **lease-schedule.md:36-38 overstates `gnd extract`.** It says pulling terms "out of the signed PDF ... is `gnd extract`". The `gnd extract` command only emits per-model extraction artifacts (`gnd extract --help`). The reading is done by the gnd-extract skill.
- **Some files are not in the reader's copy.** model-runs.md:62 points to `src/gnd/examples/plan_apps/recordings/`, a repository path that the reader's copy deliberately excludes (`ignore=...'recordings'`). course-planner.md:375 uses `tools/plan_app_bot.py`, which is repo-only. It says so, but gives no clone step.

## Claims a reader cannot verify from the page
- course-planner.md:261-265 and what-is-pyrel.md:39 say the DuckDB program "checked every recorded plan ... same verdict". The evidence is in tests, not linked.
- The verdicts in recorded replays (course-planner.md:301-304; clinic-refills.md:161-166; trip "880 euros" at trip-budget.md:66) need the replay SVG or a repo checkout.

## Navigation (zensical.toml:15-23)
PyRel is never presented as required (index.md:88, course-planner.md:180-183, what-is-pyrel.md:3-5).
The new pages are placed well. Tutorials leads with the course planner and clinic (lines 16-17). There are dedicated "How-to guides" (22) and "Explanation" (23) sections, and index.md:95-99 tables all eight pages. Minor issues:
- "Read the recorded model runs" is reference material rather than a how-to.
- README.md links only the course planner, not the how-to or explanation pages.
- pyrel-apps.md (18) sits between the new tutorials and BookRec. It holds the checkout-install instruction the new tutorials need, so a newcomer reaching it later is confused.

## Verdict
Two blocking items: the 0.1.0 install route cannot run the copy step or the examples, and the `cd` in step 8 breaks the next command. Everything else is clarity work.
