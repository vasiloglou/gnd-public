# Close reading ONE: the plan's original completion predicates

Subject: `codex/pyrel-agent-loop` at 1c30525 (draft PR #22, open against `main`, head 1c30525). Read-only.
Plan: `notes/pyrel-agent-loop-plan.md:49-75`. A1: `notes/plan-amendment-a1.md`. Owner rulings: `012-owner-decisions-a1.md`.

## What I ran (offline, this checkout)
- `pytest -m "pyrel_oracle or not pyrel_oracle" tests/test_rules_in_pyrel.py tests/test_pyrel_stand_in_sessions.py tests/test_pyrel_recordings.py`: 40 passed.
- `run_tutorials.py --group bookrec`/`expense`, offline: 61 / 48 blocks passed. With `--lane pyrel`: 71 / 59 passed.
- `pytest tests/test_pyrel_applications_install.py tests/test_pyrel_learning_path.py tests/test_pyrel_tutorial_experience.py`: 107 passed.

## Verdicts

| # | Predicate | Verdict |
|---|---|---|
| 1 | Readable commands | NOT MET (literal); not superseded |
| 2 | One copy per project | MET WITH RESIDUAL |
| 3 | Rules three ways + agreement test | MET |
| 4 | Agent loop, twice | Stand-in half MET; the "recorded real Claude Code session" half NOT MET on the chapters. A1 moves it to other pages without retiring it |
| 5 | Skills shown in place | MET WITH RESIDUAL |
| 6 | Gates green | MET WITH RESIDUAL. Acceptance and full suite are not on HEAD bytes |

## Blocking findings
B1. **Predicate 1 is false as written, and record 002 says otherwise.**
- `002-phase-PL1.md:46-47` says every command is `python <project>/app.py ...` or `gnd ...`.
- The pages still run the interpreter variable directly:
  - `docs/bookrec/07-native.md:83,181`;
  - `docs/expense/04-native.md:120,213`.
- Bare `python -c` commands remain:
  - `07-native.md:74,445`;
  - `04-native.md:111,446`;
  - `pyrel-apps.md:53`.
- `04-native.md:588` runs `python expense-native-demo/prepare_meal_cap.py`.
- The interpreter is named three times per chapter, not "once, in Set up".
- The cause is in the plan's own specs. `notes/phase-PL1-spec.md:119` kept `"$GND_PYREL_PYTHON" -c`, and `notes/phase-PL2-spec.md:38` designed `"$GND_PYREL_PYTHON" rules_in_pyrel.py`. Neither spec amended the predicate.
- A1 does not supersede predicate 1. A1 "Supersedes the PL5 page design" (`plan-amendment-a1.md:3`) and demotes these chapters to Reference (`:94`). That move was not done (`021-phase-PL18.md`, Boundary, and PL18-Q1).
- Missing: either rewrite these blocks (for example, an `app.py rules` subcommand and a `check-env` command), or record an amendment that relaxes predicate 1. Correct 002's claim either way.

B2. **The Claude Code half of predicate 4 is unresolved, and nothing records an owner disposition.**
- Each chapter shows only Codex recordings, all accepted on attempt 1 (`07-native.md:8,262,320`; `04-native.md:10,269,324`). The pages state this honestly, so it is not a false claim on the pages.
- PL4-Q1 ("Record Claude Code or explicitly accept Codex-only scope", `007:167`, `008:123`, `009:108`) is still open.
- A1 relocates the Claude Code loop to new tutorials (`plan-amendment-a1.md:53-88`). Record 012 then reordered the work, and PL7–PL11, including the BookRec flagship, "never ran" (`notes/phase-PL18-spec.md:20`).
- The Claude Code evidence that does exist is on the Course and Clinic pages:
  - PL17 ran Claude with `--tools ""`, not as a coding assistant (`018:422`). Haiku shows only format repairs (`020` table).
  - PL18 skill sessions (`019`) cover `gnd-model-from-text` and `gnd-model-evolve`, not a refuse-then-repair loop.
- A close that counts predicate 4 as met needs one of two owner rulings: accept Codex-only on these chapters, or accept the A1 relocation to the Course and Clinic pages as discharging predicate 4.

## Hardening
H1. **Acceptance predates HEAD's wheel bytes.**
- `021` says `accept_pyrel_applications_install.py` ran "before the review fixes".
- Since then, `df4de9f..HEAD` added `src/gnd/examples/plan_apps/skill-sessions-evolve/` (about 2,000 lines of wheel resources) and changed `tools/render_replay.py` and `tools/record_skill_sessions.py`.
- The acceptance tool copies `plan_apps` (`tools/accept_pyrel_applications_install.py:112`). Its receipt therefore does not describe HEAD. Rerun it before close.

H2. **The full suite was not rerun on HEAD.**
- `021` (Local CI): 9 failed at a1d9452. The 2 branch failures were fixed in 6dcc4d9, but checked only over "45 passed in those files".
- The inherited count also grew: the plan's residual of seven `main` failures now includes `test_rf4_peripheral` ×2. Classify the full suite again on 1c30525.

H3. **Untracked generated files sit inside a package directory.**
- `src/gnd/examples/bookrec/*.population.rules.py` (five files, untracked) are in a folder that the page copies wholesale (`07-native.md:46-52`, `copytree`).
- A local editable install or wheel build would ship them. Root `rules.py`, `my_rules.py` and `rules_lqp.py` are also untracked. Clean them before the acceptance rerun.

H4. **Predicate 2 residual.**
- Both chapters copy files one by one into the experiment folder: `shutil.copy` ×2 at `07-native.md:~412-413` and `04-native.md:407-408`.
- Expense uses two copytrees: the example at `04-native.md:50` and `project/` at `:89`.
- The project assembly matches the predicate: `gnd codegen` plus one copytree, then conformance exit 0 (`04-native.md:102-106`). The experiment setup breaks "No page block copies files one by one" literally.

## Completeness
C1. **Predicate 3 is MET.**
- Bookrec shows the rule four ways: the quote, the verbalizer sentence (`07-native.md:97-112`), the YAML constraint (`:129-142`), and the hand-written query (`:151-161`). Its runnable block prints `age_appropriate violated {"$b": "night", "$u": "ada"}` (`:181-187`), and GND prints the same witness (`:480,510`).
- Expense has the same shape (`04-native.md:135-147,213`). The query is labelled an equivalent (PL-R4, `07-native.md:~220`).
- `tests/test_rules_in_pyrel.py` is green under `pyrel_oracle`.
- A1 retires the hand-written files "once `--explain` covers them" (`plan-amendment-a1.md:399-400`). `--explain` became `--rules`, and the files were kept. This is consistent, but should be noted.

C2. **Predicate 5 residual.**
- The skill prompts and recap tables cover steps 2, 3, 5 and 7 (`07-native.md:689-692`, `04-native.md:732-735`). `docs/agents/{index,model-from-text,evolve,codegen-conformance,dev-session}.md` cross-reference the chapters.
- The skill steps are paraphrased, not cited from `SKILL.md` by heading as plan §5 requires ("pages cite `SKILL.md` steps by heading").
- BookRec step 2 (`:57-60`) lists no two-to-four skill steps.

C3. **Predicate 4 stand-in half is MET.**
- `gnd exp run` reports accepted after 2 attempts. Attempt-1 witness Ada/night appears at `07-native.md:480`, and expense uses `{"$a": 800, "$e": 102}`.
- The accepted candidate runs through `app.py check` and `report` (`07-native.md:~515-527`; `04-native.md` report on the attempt-2 candidate).
- Recorded excerpts are printed by SHA-256-checked blocks (`07-native.md:274-275,304-307,348-352`).

C4. **Predicate 6 items that are met.**
- Both lanes are green now (measured above).
- Strict build and check_docs were green at 1c30525 per `021`; not re-measured here.
- The PR is open (draft). The PL19 close record does not exist yet.
