---
milestone: pyrel-agent-loop
station: owner-gate
skill: process-phase
scope: phase-PL18-skill-recording
date: 2026-10-15
---
# Owner authorization for recording a GND skill session (PL18)

These owner rulings authorize the recording:
- A1's model table: "Claude Code, small model | `claude --model haiku` | a real
  coding-assistant transcript with skills and tool calls";
- the C2 tutorial shape ("it looks great"), whose step 2 shows the
  `gnd-model-from-text` skill at work;
- "1. Claude is authenticated" (record 012);
- "you should finish P16 and P17" and the milestone delegation.

This record binds the recording to a named scope, so
`tools/record_skill_sessions.py --authorized-by` can refuse anything outside it.

## Scope

| Item | Authorized |
|---|---|
| Tool | `tools/record_skill_sessions.py` |
| Claude Code | the owner's logged-in `claude` CLI with `--plugin-dir <repo>` (the repository's own plugin, so the skill is `/gnd:gnd-model-from-text`), `--permission-mode acceptEdits`, `--allowedTools "Bash(gnd *),Read,Write,Edit,Glob,Grep"`, `--output-format stream-json --verbose`; `--model haiku` and the account default. No API key is read |
| Workspace | a new temporary folder holding only the Course `rules.md`; `gnd` from the repository's environment on `PATH` |
| The user's side | declared before any run: turn 1 `/gnd:gnd-model-from-text rules.md`; turn 2 `MVP-fast. The rules file is complete: model what it states, including what the registrar does, and ask me only about what it leaves open.`; later turns `Yes, as you propose.`. At most 6 turns, 900 s per turn |
| Runs | 2 per model |
| Redaction | workspace → `<workspace>`, repository → `<repo>`, home → `<home>`, temporary paths → `<tmp>`. Every file is searched for local paths and key prefixes before it is kept |

Every run is listed in `results.json`; none is discarded for its outcome.

## Amendment, 2026-10-15 (delegated, auto=true)

The first launch was stopped after one run. The skill called GND by its absolute
path (`<repo>/.venv/bin/gnd validate`, found with `which gnd`), which
`Bash(gnd *)` does not match. Validation was blocked, and the run ended with a
model that fails `gnd validate`. The run is kept in the session scratchpad
(`pl18/skill-rec1-aborted-permission`) and reported in the phase record, not
in the recording.

The permission list adds `Bash(<repo>/.venv/bin/gnd *)`, the same command by its
absolute path. The stop rule is now: the user stops answering once the model
validates, or after 6 turns. The recorder checks this after each turn.
