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

## Amendment 2, 2026-10-15: the gnd-model-evolve session (owner request)

The owner asked why step 8 of the course tutorial shows a shipped proposal
instead of `/gnd:gnd-model-evolve` taking the change in natural language. This
amendment authorizes recording that skill, with the same tool and the same
rules as above, except:

| Item | Authorized |
|---|---|
| Skill | `/gnd:gnd-model-evolve`, through `tools/record_skill_sessions.py --skill model-evolve` |
| Workspace | a new temporary folder holding only the course `model.orm.json` and `rules.md` |
| The user's side | declared before any run: turn 1 `/gnd:gnd-model-evolve Lower the credit cap from 18 to 6 credits a term, for every student.`; later turns `Yes, apply it.`. At most 6 turns, 900 s per turn. The user stops answering once the model validates with the new cap |
| Model and runs | Claude Code `--model haiku`, 2 runs |
| Output | `src/gnd/examples/plan_apps/skill-sessions-evolve/`, with the same keep filter, redaction, leak search and manifest |

## Amendment 3, 2026-10-15: the evolve recording's environment

The first evolve launch (2 Haiku runs, kept in the session scratchpad
`pl18/evolve-rec1`, reported in the phase record) measured the recording setup,
not the skill:

- Loading the plugin from the repository root put the course example's shipped
  `credit-cap-proposal.json` within reach. Run 1 found it and used it as a
  template.
- The permission list refused `shasum`. Run 1 learned the candidate digest from
  `gnd evolve preview`'s own refusal. Run 2 stopped after five refusals, with
  the model unchanged.

The relaunch differs in two ways only:
- **Plugin copy.** The plugin is loaded from a temporary copy holding only
  `.claude-plugin/` and `src/gnd/skills/`.
- **Permissions.** The permission list adds `Bash(shasum *)`, read-only hashing,
  which a user would approve in a normal session.

All else in amendment 2 stands: Haiku, 2 runs, the same user turns.
