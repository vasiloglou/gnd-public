# Recorded sessions: Claude Code runs gnd-model-from-text on the course rules

Recorded 2026-10-15 under the gate record `.gnd-planning/milestones/pyrel-agent-loop/019-recording-gate-PL18-skills.md`. Each run starts in an
empty folder holding only the course `rules.md`, with the repository's plugin
loaded (`--plugin-dir`), so the skill is `/gnd:gnd-model-from-text` as a reader
types it. The user's side is declared in advance and never changes:

1. `/gnd:gnd-model-from-text rules.md`
2. `MVP-fast. The rules file is complete: model what it states, including what the registrar does, and ask me only about what it leaves open.`
3. `Yes, as you propose.` (repeated, at most 6 turns)

The user was meant to stop answering as soon as the model in the folder passed
`gnd validate`; see the first caveat for the run where that check misfired.
Every run is listed; none was dropped.

| Model | Run | Turns | Model written | `gnd validate` exit | Claude Code's reported cost, summed over the turns (USD) |
|---|---|---|---|---|---|
| claude-haiku | 1 | 1 | `model.orm.yaml` | 0 | 0.19 |
| claude-haiku | 2 | 2 | `model.orm.yaml` | 0 | 0.15 |
| claude-default | 1 | 2 | `model.orm.yaml` | 0 | 2.46 |
| claude-default | 2 | 5 | `model.orm.json` | 0 | 17.41 |

The cost is the sum of what Claude Code reported at the end of each turn. Each turn resumes the session and re-reads its context, so long sessions cost more per turn. On a subscription the cost is notional.

## What a run folder holds

- `turn-NN.jsonl`: Claude Code's stream-json for each turn, as kept (below);
- the model the skill wrote, and `validate.txt` (GND's verdict on it).

## What was kept, and what was not

- **Tool output is kept only where the replay needs it:** commands whose first
  word is `gnd` and files in the workspace. Later recordings keep it only when
  nothing follows the `gnd` command on the same line. Every other tool output is replaced by its size. In one
  run the assistant listed the machine's temporary folder; that listing is not
  kept.
- **Claude Code's start event keeps no paths,** and paths are shortened to
  `<workspace>`, `<repo>`, `<home>` and `<tmp>`.
- **Thinking blocks are kept, without their opaque signatures.** Most arrive
  empty in Claude Code's stream output, so little reasoning text shows.

## Caveats

- **The stop rule misfired on `claude-default/run-2`.** The default model wrote
  a valid model in turn 1, and its own `gnd validate` printed OK. The recorder's
  check ran through a symlinked temporary path, and `gnd validate` refuses a
  model with reference populations reached that way. So the recorder judged the
  model invalid, and the scripted user answered four more turns. That accounts
  for most of that run's cost. The model changed in turn 5, when the reference
  population was removed. The recorder now resolves the path first.
- **`results.json` lacks costs and closing messages.** Its turns record
  `cost_usd: null` and `assistant_last: ""`, because the recorder missed Claude
  Code's result line. The costs above are read from the result events kept in
  each `turn-NN.jsonl`. The recorder has been fixed.
- **The assistant went beyond the workspace and beyond `Bash(gnd *)`.** Claude
  Code allowed read-only shell commands (`ls`, `cat`, `wc`). The agent read the
  skill's files and some repository test fixtures, and wrote trial files and ran
  a trial `gnd codegen` in its own scratch folder. Those outputs are not kept.
- **Kept beyond the replay:** each turn's closing `result` event (session id,
  cost, the list of commands Claude Code refused) and the inputs of every tool
  call.
- **Finished after recording.** The keep filter above was added after this
  recording. It was applied with `tools/record_skill_sessions.py --finish`
  (`manifest.json`, `finished_later`). It removes content; it adds none.
- **An earlier launch was discarded.** The permission rule `Bash(gnd *)` did not
  match the skill calling GND by its absolute path, so validation was blocked.
  That launch is not kept here; the gate record's amendment describes it.

## Sources changed since the recording

- `tools/record_skill_sessions.py`: the keep filter and `--finish`; after review,
  the workspace path is resolved, result events are parsed reliably, and the
  keep filter needs a plain `gnd` command. The manifest's `sources` digest is the
  recorded one.
