# Phase PL17 spec: real models behind the five plan apps, every run reported

## 1. Status

Delegated approval (auto=true), 2026-10-14. Owner rulings:
- "try a smaller model where you can show the retry" (A1);
- "1. Claude is authenticated 2. you can use the openrouter from .env" (record 012);
- "you should finish P16 and P17" (2026-10-14).

The recording gate is `018-recording-gate-PL17.md`.

## 2. Provenance

- **A1 "Recording a retry with a smaller model":**
  - the model table;
  - the protocol of 5 runs per model with 3 attempts each, every run listed;
  - the replay choice;
  - feedback "in words".
- **PL16:** the bot interface (JSON prompt on stdin, plan on stdout) and the
  five apps.
- **Harvest of 2026-10-14** (session scratchpad `pl17/probe`, `pl17/dry`,
  `pl17/dry2`):
  - Claude Code haiku, with no tools, answers in about 5 s;
  - the three OpenRouter models are listed and cost under $0.0001 per 1k
    tokens;
  - Gemma 3 4B repeated one refused plan five times;
  - Llama 3.1 8B invented grades;
  - Haiku planned four apps at the first attempt and declined the access
    question with a correct reason.

## 3. Obligations

| Source | Obligation | Discharge |
|---|---|---|
| A1 table | Claude Code haiku, Claude Code default (contrast), Llama 3.1 8B, Gemma 3 4B, Llama 3.2 3B | §6.2 |
| A1 protocol | 5 runs per model, 3 attempts each, every run in `results.json` | §6.3, test 2 |
| A1 | feedback a small model can use: the failed rule and the facts, in words | §6.1 `said` |
| A1 credentials | `OPENROUTER_API_KEY` read from `.env` as data, only in the bot's process, under a gate record | §6.2, gate 018 |
| A1 replay rule | the docs replay the first run that is refused and then accepted; if none, say so | PL18, from `results.json` |
| AGENTS.md | never source `.env`, never print a value | §6.2, test 3 |

## 4. Standing rules, bound

1. **Totality.** Any model answer goes through the app's own validation. The
   adapter changes nothing except unwrapping a single fenced JSON object.
2. **Bounds.**
   - 3 attempts per run;
   - 300 s per model call;
   - 1800 s per run;
   - 2000 output tokens per OpenRouter call;
   - 5 runs at most.
3. **Measurement.** Every run is kept and reported, and the recording is bound by
   a SHA-256 manifest. Each recorded plan is re-checked by GND in tests, which
   is also an agreement check, since the recording used the PyRel backend.

## 5. What the reader sees

`src/gnd/examples/plan_apps/recordings/`:
- `results.json`: one row per run, with each attempt's exit, failed checks,
  decline or note;
- `manifest.json`;
- `<model>/<example>/run-N/session.txt`: what the app printed;
- `reply-NN.json`: the raw model replies.

## 6. Design

### 6.1 `tools/plan_app_bot.py`, the adapter
- **Message.** It turns the app's prompt into one message: question, rules,
  operations, state, and each refused attempt's plan with its failures as
  sentences.
- **Claude.** `claude --print --tools "" --no-session-persistence
  --strict-mcp-config --system-prompt ... --output-format json`, run in an
  empty temporary directory.
- **OpenRouter.** One chat call at the provider's default temperature, with two
  retries on 429/502/503.
- **Logging.** `--log DIR` writes each raw reply with its usage (`x` mode).

### 6.2 `tools/record_plan_apps.py`, the recorder
- Refuses without `--authorized-by` naming a record that mentions PL17.
- Writes to a new `--out` directory and never overwrites one.
- **Runs.** For each model and example, it runs `app.py ask QUESTION --attempts
  3 --backend pyrel`, one lane per model, in recording order.
- **Redaction.** Workspace, repository and home paths.
- **Leak search.** Every recorded file is searched for the key and for local
  paths before the manifest is written; a hit refuses the recording.

### 6.3 App changes found by the harvest (PL16 core, owner-visible)
- **A bot may decline:** `{"steps": [], "reason": ...}`. The app prints the
  reason and stops with exit 1. An empty plan without a reason is still a
  failed attempt.
- **A plan may carry a note:** `"note"`. The app prints it.
- **The `rules` command lists dynamic rules.** For example, the course's
  `grade_final` ("Once a grade is recorded, it never changes."). A broken
  dynamic rule shows its PyRel line in the feedback. This answers the owner's
  C6 remark: "I would show the rules expressed in pyrel".
- **`--bot` is split with `shlex`.**

## 7. Decisions

| # | Question | Ruling |
|---|---|---|
| D1 | A new recorder or generalising `record_pyrel_sessions.py` | a new tool. The old one drives `gnd exp run` sessions for BookRec and Expense (PL4) and stays as it is |
| D2 | Gateway or direct call | a direct call from the adapter. The plan apps do not use `gnd exp`, so `openrouter_gateway.py` is not needed |
| D3 | Temperature | the provider's default, so 5 runs can differ, as Claude Code's do |
| D4 | Checker for the recording | PyRel (the milestone's subject). GND re-checks in tests |
| D5 | Whether the adapter may repair answers | no, apart from unwrapping a code fence (disclosed) |

## 8. Tests (`tests/test_plan_app_recordings.py`, offline)

| # | Case | Expected |
|---|---|---|
| 1 | The manifest's SHA-256 values match every recorded file, and no file is unlisted | pass |
| 2 | `results.json` has 5 x 5 x 5 rows in recording order, each with its session and one reply per attempt | pass |
| 3 | No recorded file holds `/Users/`, `/private/`, `/home/` or an OpenRouter key prefix | pass |
| 4 | Each recorded plan, re-checked by GND from the example's state, gives the recorded exit | pass |
| 5 | The A1 replay choice is computable: the first run refused and then accepted, or none | pass |

Plus the PL16 app tests for decline, note and dynamic rules.

## 9. Out of scope

- Docs pages (PL18).
- Re-recording BookRec and Expense (PL4).
- Codex.

## 10. Approval instrument

This prose and gate record 018, as delegated approval (auto=true) within the
milestone scope.

## 11. Amendments during recording and after review (delegated approval, auto=true, 2026-10-15)

| # | Amendment | Why |
|---|---|---|
| A1 | The bot interface gains a note and a decline (PL16 A1) | harvest: Haiku declined the access question correctly |
| A2 | A preflight checks each app's documented first plan before any model call | two launches were lost to an interpreter-path defect (132 and 143 calls); both are disclosed |
| A3 | `--rebind` adds a redaction after recording. It verifies the manifest first, only redactions may change a file, and the changed files are recorded | a refusal message printed the temporary plan path; review H1 |
| A4 | `--reindex` rebuilds results.json's index from the recorded session and reply files. The index keeps (check, status) pairs and refusal codes. "repaired" is split into repaired-rule and repaired-format | review B2.3, H3 |
| A5 | The README is written by the recorder from results.json; caveats live in CAVEATS.md; changed sources are declared as drift | review B1, B2.1 |
| A6 | Disclosed: Claude Code's extra context (the host date, about 1.5k tokens, extended thinking); the quoted-value template; OpenRouter's upstream mix; "recording order" means results.json order | review B2.2-B2.4, H8 |
| A7 | Hardening for later recordings: process-group timeouts, per-run error rows, replies named by attempt with failures logged, the requested and served models kept apart, API keys kept from Claude Code, project-only settings, a type-neutral template, the leak search covering `/tmp/` and `/var/folders/` with removal on a hit | review H4-H9 |
| A8 | The app prints the bot's words on one line | review H2 |
