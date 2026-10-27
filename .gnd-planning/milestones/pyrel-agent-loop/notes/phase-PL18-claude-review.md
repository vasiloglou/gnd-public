# Phase PL18 adversarial review (one Claude subagent), retained verbatim

Reviewer: one general-purpose Claude subagent, read-only outside its scratch folder, no paid calls. One reviewer is one reviewer. The report below is unedited.

---

## Verdict: REVISE

The PL18 pages render, run and pass their own tests. But several sentences a reader will take as fact are not supported by the recordings, one existing test now fails because of PL18, and the new tests would not catch a replay that swapped its source.

Scratch work is in `<scratch>/pl18-review/`. Running the docs build also rewrote the gitignored `site/`; that was the only write outside scratch. No recorder was run and no model was called.

## Blocking

**B1. False claim about the bot's feedback.** `docs/tutorials/course-planner.md:207-208` says "That is the feedback the bot gets, with the rule's PyRel line."
- The bot never gets the PyRel line. `core.py:384` adds only `{"plan", "failures"}` to the history.
- `tools/plan_app_bot.py:53-67` (`said()`) turns each failure into `where: check status; the facts …`.
- The PyRel line is printed for the human only (`core.py:375`).
- Fix: "The bot gets the rule's name and the facts; the PyRel line is printed for you."

**B2. "All ten runs right" is false (Clinic).** `docs/tutorials/clinic-refills.md:153` says "The Claude models got the plan right at the first attempt in all ten runs."
- `recordings/claude-haiku/clinic/run-3/session.txt`: Haiku used the host date 2026-10-14 instead of the state's "today" (2024-03-10).
- It refilled the statin and warfarin, and was accepted with two `not_too_late` warnings. That contradicts the page's own step 4 (the statin isn't due).
- Fix: say 9 of 10, and name run-3 as the plan made for the host's date.

**B3. The skill-session prose is false, and the recorder's stop rule misfired.**
- `course-planner.md:80-82` says the other three sessions "asked questions first, such as 'Should a term carry a year?'".
- `claude-default/run-2/turn-01.jsonl` instead ran in one-shot mode, wrote the model and ran `gnd validate` (OK at events 209 and 305). The quoted question comes from that same run.
- `results.json` still records `model_valid_after_turn: false` for that turn, so the scripted user kept answering for 4 more turns ($17.41). The model changed (the reference population was removed in turn 5).
- Root cause: `tools/record_skill_sessions.py:105,133-135` validates the unresolved `/var/folders/...` path, and `gnd validate` refuses a model with references when reached through a symlink.
- Repro (in scratch): copy `tests/fixtures/reference-corpus/dispatch` to `real/` and `ln -s real link`. `gnd validate real/model.orm.yaml` exits 0; `gnd validate link/model.orm.yaml` exits 3 ("safe reference descriptor traversal is unavailable or refused the model path").
- The skill-sessions README sentence "The user stops answering as soon as the model … passes gnd validate" is therefore untrue for that run.
- Fix: resolve the workspace path, correct the prose, and disclose the misfire in the README caveats.

**B4. Overclaim about the RelationalAI engine.** `course-planner.md:165-168` says "a RelationalAI engine, where each requirement runs as written … Either way, the verdicts match GND's own checker."
- The LQP program has never run on an engine. Your own `docs/explanation/rules-as-pyrel.md:40` says "not yet run on an engine", and `docs/runtimes/pyrel.md:106` agrees.
- Engine behaviour is also described two ways: `rules-as-pyrel.md:39` "the engine refuses data" against `runtimes/pyrel.md:64` "reports every violation". Neither is evidenced.
- Fix: say "would run on an engine; it is compiled, not run, here". Restrict the agreement claim to the DuckDB program, where GND re-checks the recorded exits.

**B5. A PL18 change breaks an existing test.**
- `tests/test_documentation_tutorials.py::test_installed_validator_requires_matching_wheels[True]` and `[False]` now fail.
- Cause: `tools/check_installed_docs.py:58` now requires `plan_apps` in the wheel, but the test's fake wheel (`test_documentation_tutorials.py:60`) has no `plan_apps`.
- Repro: `uv run pytest tests/test_documentation_tutorials.py -k matching_wheels`.
- Fix: add `plan_apps` to the fixture's domain list.

**B6. False summary on the runs page.** `docs/how-to/model-runs.md:42-44` says "Most of their failures were answers that were not a plan at all."
- Over the small models' failed attempts in `results.json`: 82 unusable, 79 rule refusals (exit 1), 17 malformed (exit 3), 2 declined. So 82 of 180 is not most.
- By final attempt of the 55 refused runs: 26 rule, 20 unusable, 7 malformed, 2 declined.
- Fix: "Many were not a plan at all."

**B7. Step 8's "part-time" rule is not what the model says.**
- `course-planner.md:263` and `course/credit-cap-proposal.json` claim "part-time students take at most 6 credits".
- The candidate model caps every student at 6; there is no part-time fact, and Maya isn't marked part-time. The rule's words (`user_note`) contradict its logic, which undercuts the page's "every rule keeps the registrar's words".
- It also departs from spec §6.2 (term load 6 → 4) with no recorded ruling.
- Fix: word it as a general cap, or model part-time, or do the specified term-load change.

## Hardening

- **H1. "In recording order" is wrong.** Used at `course-planner.md:219` and `trip-budget.md:54-55`. The recordings README says `results.json` order is table order, "not the order in which runs happened". Say "in results.json order".
- **H2. Tests let a replay drift from its run.**
  - Mutation in scratch: point `replays.json` "course-llama-3.2-3b-run-2" at `run-4/session.txt` and re-render. All 34 tests in `test_plan_app_docs.py` and `test_replays.py` still pass, while the page and title say run 2.
  - `REPLAYED` sets the claim to `None` for access and trip, so neither page has to name its run folder in prose. Clinic and lease never name theirs either.
  - Fix: assert each `replays.json` source matches its name and the A1-chosen folder, and require the folder string on each page.
- **H3. The step 8 block can't fail.** `course-planner.md:270-273` ends with `echo "applied"`, so it prints "applied" even when apply is refused.
  - Repro: copy the example and run the block twice in one folder. The second apply prints `EVOLUTION APPLY REFUSED (11): immutable evidence conflict`, yet "applied" still prints. `app.py check …attempt-3` then exits 0, not the documented 1.
  - Fix: use `&& echo applied`, or show the RECORDED line.
- **H4. The skill-session replay hides some facts.**
  - `render_replay.py:81` drops tool results marked "output not kept", including `is_error: true` permission denials. For example, Haiku's `cd <repo>… && which gnd; …; git status` was blocked but reads as if it ran.
  - `condensed()` (`:107`) folds `Glob **/rules.md` into "reads the skill's reference pages".
  - The transcript cuts each assistant message to 300 characters and keeps only the first line of each result, yet the page calls it the "Transcript" (the spec says verbatim).
  - Fix: mark blocked or errored calls, label the transcript as condensed, and link the jsonl.
- **H5. Thinking blocks are empty.** The skill-sessions README says "Thinking blocks keep their text, so the reasoning shows", but 82 of 85 are empty.
- **H6. `results.json` and the manifest don't match the files.**
  - In skill-sessions `results.json`, every turn has `cost_usd: null` and `assistant_last: ""`. The kept `result` events carry `total_cost_usd`, and their sums equal the README table (0.19 / 0.15 / 2.46 / 17.41).
  - The manifest's source digest for `tools/record_skill_sessions.py` no longer matches the file.
  - Fix: add a "sources changed" note as PL17 did, or regenerate.
- **H7. The keep filter is loose, and some agent behaviour is undisclosed.**
  - `kept_stream` (`:76`) keeps output for any command whose first token ends in `gnd`, so compound commands like `gnd x; cat …` are kept. Tool inputs and `result` events (session ids, `permission_denials`) are always kept. The leak search does not check the hostname, though none was found.
  - Undisclosed: the agent read repository test fixtures (`<repo>/tests/fixtures/reference-corpus/dispatch`), and Claude Code allowed read-only shell commands beyond `Bash(gnd *)` (e.g. `ls`, `cat`, `wc`).
  - It also wrote files and ran a trial `gnd codegen` in its scratchpad, outside the workspace. That goes beyond the gate's "folder holding only rules.md".
  - A path `<home>/.claude/projects/<tmp>/f248082d-…/tool-results/…` is kept.
- **H8. The Llama note is wrong.** `clinic-refills.md:136-137` says "Its note even explains why it left warfarin out", but the note blames the refill interval, which applies to the statin, not warfarin. Say the note is wrong.
- **H9. Lease reasons are misstated.** `lease-schedule.md:39` says "two reasons, and only one is a rule". No lease run was refused on a declared rule. The refusals were malformed plans, unusable answers and failed retract effects (`llama-3.1-8b/lease/run-2`).
- **H10. The checker is misattributed.** Every recorded check is `pyrel check`, but the pages say "GND says / GND refuses" (`course-planner.md:204`, `access-requests.md:57`, `trip-budget.md:48`, `clinic-refills.md:141`). `rules-as-pyrel.md:40` says DuckDB "runs in … tutorials", but the runnable blocks use the gnd backend. The spec requires each page to say which checker checked.
- **H11. Some excerpts are typed, not included.** The PyRel lines at `access-requests.md:33`, `trip-budget.md:22-23` and `lease-schedule.md:22`, and the access rules quote, are typed by hand. They match the files today but no test pins them (PL-R3 says quotes are never typed).
- **H12. Contradiction on the runs page.** `model-runs.md:19` says "the same question, rules, … feedback", which the same page's caveats contradict (Claude Code's extra context and date; the access rules text).
- **H13. Replay accessibility and timing.** Every replay figure has the same `aria-label`, so screen-reader region lists show identical "Replay" entries. Animation starts on page load, not "when shown" as decision D2 says.

## Completeness

- **Home and README.** The Quickstart lacks the one prompt from spec §6.1 ("Open the GND course planner example and plan Maya's spring semester."). The README got a tutorial link but not the "How it works" loop.
- **Course page.** Step 2 shows a YAML excerpt, not the verbalizer's sentences, and step 7 doesn't show the published state.
- **Clinic page.** There is no table of the real runs (§6.3).
- **Unrelated failure.** `test_development_scaffold` also fails, but not because of PL18: the broken link `...svg` is in `plan-amendment-a1.md:10`, unchanged since PL12. Locally it also trips first on a stray `/private/tmp` link in an untracked `.claude/worktrees/` checkout.
- **GND bugs seen in the recordings (worth an issue):**
  - `gnd check` exits 70 with "INTERNAL ERROR: derived origin lineage missing for 'student_carries_credit_load_in_term'" (`claude-default/run-2/turn-01.jsonl`);
  - `gnd validate` refuses a model that has reference populations when reached through a symlinked path (B3).

## Checked and held

- **Runner group:** `uv run python tools/run_tutorials.py --group plan-apps` exits 0, 18 blocks in about 8 s.
- **Docs build:** `zensical build --strict` and `tools/check_docs.py site` both exit 0 (10084 links checked).
- **Tests:** `test_plan_app_docs`, `test_replays`, `test_figures_render`, `test_pyrel_learning_path`, `test_pyrel_tutorial_experience`, `test_tutorial_output_blocks`, `test_figures`, `test_plan_app_recordings` and `test_plan_app_recording_tools` all pass. The only failures are B5 and the unrelated scaffold failure above.
- **Figures fix:** HEAD has 3 bad image sites in each of the two pages (6 in all), so the new test would have failed before the fix; it passes now.
- **Replays:**
  - every replay passes `--check`;
  - each `session.txt` transcript is byte-equal to its recording;
  - each SVG has `role="img"`, title, desc and the reduced-motion rule, and is under 9 KB.
- **Replay choice:** it matches the A1 rule in `results.json` order: Course `llama-3.2-3b/run-2`, Access `llama-3.1-8b/run-1`, Trip `llama-3.1-8b/run-2`. Clinic and lease have no rule-refused-then-accepted run, and their pages say so.
- **Re-derived facts that hold:**
  - Course: the run-2 plan and its refusal at state 1 on MATH220 and STAT210; the repair to MATH220 only; all 10 Claude course runs planned MATH220 and STAT210 with a note.
  - Trip: 880 € total; refused from state 4; the Llama 3.2 3B one-night repair (run-5).
  - Access: refused at states 1-2 with witness `["bob","carol"]`, Erin accepted; all 10 Claude runs declined.
  - Lease: Claude's default model wrote rent as text in all 5 runs; the 31 July warning reproduces.
  - Clinic: the statin is due 21 March; 15 Jan to 20 Mar is 65 days; refused at state 2 with the quoted witness.
  - Skill sessions: Haiku run-1's validate error and fix; the model excerpt (lines 323-340) is the prerequisite rule; all four committed models validate.
- **Quickstart commands** match `.claude-plugin/marketplace.json`.
- **Privacy:** no `/Users`, `/private`, username, hostname or `sk-` key in `skill-sessions/` or `docs/assets/replays/`.
- **Mobile, dark theme:** no horizontal page scroll; each replay scrolls inside its own card (343 px wide showing 760 px); the site's dark tokens apply.