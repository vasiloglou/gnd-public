# Read the recorded model runs

The tutorials replay real sessions. This page shows all of them: five models
answered each plan app's question five times, and every run was kept. Use it
to see how often a model gets a plan right, how often GND refuses one, and
whether the model repairs it from the feedback.

!!! info "Files on GitHub"

    - [`results.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/plan_apps/recordings/results.json): one row per run
    - [the recordings README](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/plan_apps/recordings/README.md): the table and the caveats
    - [`tools/plan_app_bot.py`](https://github.com/vasiloglou/gnd-public/blob/main/tools/plan_app_bot.py): how a model is called
    - [`tools/record_plan_apps.py`](https://github.com/vasiloglou/gnd-public/blob/main/tools/record_plan_apps.py): how the runs were recorded
    - [this page's Markdown source](https://github.com/vasiloglou/gnd-public/blob/main/docs/how-to/model-runs.md): replays and included files show only as include lines there; they render on the docs site

## How the runs were made

Each run is one `app.py ask QUESTION` with a model behind the bot, at most
three attempts. The app's optional PyRel backend, the DuckDB program GND
generates ([What PyRel is, and when you need it](../explanation/what-is-pyrel.md)), checked every plan. In the tests,
GND checks every recorded plan again and gives each the same verdict.

| Model | How it was called |
|---|---|
| Claude Haiku, Claude Code's default model | Claude Code, signed in, with no tools: it can only answer |
| Llama 3.1 8B, Gemma 3 4B, Llama 3.2 3B | OpenRouter, one chat call per attempt |

The app sent every model the same question, rules, operations, state and
feedback. The feedback names the rule, where it broke, and the facts that break
it. It never contains the answer. Claude Code added context of its own, such as
the computer's date; the caveats below say what.

## What happened

--8<-- "src/gnd/examples/plan_apps/recordings/README.md:table"

- **first**: accepted at the first attempt.
- **repaired-rule**: refused on a rule, then accepted after the feedback.
- **repaired-format**: only malformed or unusable answers before it was
  accepted.
- **declined**: the model said no useful plan exists, and why.
- **refused**: nothing accepted in three attempts.

Three things to read from it:

1. **Only the small models repaired a plan after a rule refusal.** The Claude
   models planned within the rules at the first attempt. Their only repairs
   fixed the format, such as rent written as text instead of a number.
2. **Declining is sometimes right.** The access question asks for Carol, who
   manages Bob through Dana, so no allowed plan exists. Both Claude models
   said so every time.
3. **Small models fail more than they repair.** Many of their failures were
   answers that were not a plan at all, which the app reports back like any
   other refusal.

## What to keep in mind

--8<-- "src/gnd/examples/plan_apps/recordings/README.md:caveats"

## Look at a run yourself

Each run folder in `src/gnd/examples/plan_apps/recordings/` of the GND
repository (the example copy in the tutorials leaves it out) holds what the app
printed (`session.txt`) and the model's raw reply to each attempt. The
[course tutorial](../tutorials/course-planner.md) replays
`llama-3.2-3b/course/run-2`, the first course run refused on a rule and then
accepted.
