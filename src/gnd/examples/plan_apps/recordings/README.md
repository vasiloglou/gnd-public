# Recorded runs: real models behind the plan apps

Recorded 2026-10-14 under the gate record `.gnd-planning/milestones/pyrel-agent-loop/018-recording-gate-PL17.md`. Each run is one
`app.py ask QUESTION --attempts 3 --backend pyrel` with the model behind `tools/plan_app_bot.py`.
Every run is listed in `results.json`; none was dropped. `manifest.json` binds each file by SHA-256.

Outcomes per model and app, over 5 runs (the served model ids are in brackets):

- **first**: accepted at the first attempt;
- **repaired-rule**: refused on a rule (exit 1), then accepted after the feedback;
- **repaired-format**: only malformed plans (exit 3) or unusable answers before acceptance;
- **declined**: the model answered that no useful plan exists, with a reason;
- **refused**: no plan accepted in the attempts allowed;
- **crash**: the run did not finish normally.

| Model | course | access | lease | clinic | trip |
|---|---|---|---|---|---|
| claude-haiku (`claude-haiku-5-5`) | 5 first | 5 declined | 3 first, 2 repaired-format | 5 first | 4 first, 1 repaired-format |
| claude-default (`claude-opus-5-5[1m]`) | 5 first | 5 declined | 5 repaired-format | 5 first | 5 first |
| llama-3.1-8b (`meta-llama/llama-3.1-8b-instruct`) | 5 refused | 3 repaired-rule, 2 refused | 3 first, 1 repaired-format, 1 refused | 1 repaired-format, 1 declined, 3 refused | 2 first, 3 repaired-rule |
| gemma-3-4b (`google/gemma-3-4b-it`) | 5 refused | 5 refused | 5 refused | 1 declined, 4 refused | 1 first, 1 repaired-rule, 3 refused |
| llama-3.2-3b (`meta-llama/llama-3.2-3b-instruct`) | 1 repaired-rule, 4 refused | 5 refused | 5 refused | 2 first, 3 refused | 1 repaired-rule, 1 repaired-format, 3 refused |

## The replayed run

Replayed run: `llama-3.1-8b/access/run-1`, the first run in results.json order (model, example, run) refused on a rule and then accepted (A1 protocol). The model lanes ran side by side, so this is table order, not the order in which runs happened.

## What a run folder holds

- `session.txt`: what the app printed, with paths shortened to `<workspace>` and `<tmp>`;
- `reply-NN.json`: the model's raw reply to attempt NN, with usage.

Claude Code reported $0.62 for its runs; OpenRouter reported $0.0135.

## Sources changed since the recording

- `src/gnd/examples/plan_apps/access/rules.md`: after the recording: Frank's wiki access approved by Dana, as the state says (PL16 review C1)
- `src/gnd/examples/plan_apps/core.py`: after the recording: the PL16 review fixes (malformed-plan reasons, the two-space parser, timeouts, a 100-step bound, temporary paths out of feedback) and PL17 review H2 (the bot's words printed on one line). The recorded runs were printed by the earlier bytes, digest in sources
- `tools/plan_app_bot.py`: after the recording: replies named by attempt, failed calls logged, requested and served model kept apart, API keys kept from Claude Code, project-only settings, a type-neutral template
- `tools/record_plan_apps.py`: after the recording: --rebind, --reindex, the summary and outcome split, timeouts by process group, per-run error rows, the wider leak search

## Caveats

- **Two launches before this one were stopped and discarded.** The cause was a
  recorder defect, not the outcomes: both passed the PyRel interpreter in a way
  that failed inside each run's temporary directory, so every PyRel check
  crashed.
  - The first launch made 132 model calls over 86 runs.
  - The second made 143 calls over 49 runs.
  - Neither recording is kept here. The recorder now refuses to start unless
    each app's documented first plan gets its documented verdict.
- **Rebound once after recording.** A refusal message printed the app's
  temporary plan path, which is now replaced by `<tmp>`. `manifest.json`
  (`rebound`) lists the files changed and their digests. No outcome changed.
- **Reindexed once after recording.** `results.json`'s per-attempt index was
  rebuilt from the recorded `session.txt` and reply files, which were not
  changed:
  - each reported (check, status) pair is kept, including warnings and rules
    reported as not checked;
  - exit-3 refusal codes are kept;
  - "repaired" is split into repaired-rule and repaired-format.
- **Claude Code saw context the OpenRouter models did not.**
  - Claude Code adds its own environment context, about 1.5k tokens, including
    the host's date. Four Claude Haiku clinic runs mention the system date
    2026-10-14; the clinic state's "today" is 2024-03-10.
  - Claude also reasons before it answers (extended thinking); the small models
    do not.
  - Claude Code cannot drop that context without an API key (`--bare`), and the
    owner's login was used.
- **The answer template quoted every value.** The adapter's system prompt showed
  bindings as `"<value>"`. Every Claude lease repair was a repaired-format run:
  `amount` was first written as the string `"1450"`. The template is now
  type-neutral for later recordings.
- **OpenRouter chose the upstream host per call:**
  - Llama 3.1 8B: Novita 26, DeepInfra 34;
  - Gemma 3 4B: Parasail 68, DeepInfra 3;
  - Llama 3.2 3B: Parasail 69.

  The reply files' `provider` field holds that host, not "openrouter".
- **The access rules the models read said Frank's wiki access was "approved by
  Erin"**, while the state says Dana. The text was corrected after the
  recording (PL16 review, C1). No run's verdict depends on Frank's approval.
- **Small models are nondeterministic.** These are 5 runs each, at the
  provider's default temperature; another 5 runs would differ.
