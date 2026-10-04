# Recorded agent sessions

Real agent sessions on one task, recorded on 2026-10-04: pay expense 41 by writing
a `steps.json` plan that GND accepts (`TASK.md`). Each session ran
`gnd exp run` with a transition contract and a budget of three attempts.

| File | What it is |
|---|---|
| `TASK.md` | The one task every agent was given, with the digests a plan must carry |
| `results.json` | Every recorded session: agent, route, disposition, attempts and the verifier band of each attempt |
| `<agent>/attempt-NNNN/` | For six illustrative sessions: the candidate `steps.json` and GND's closed `feedback.json` for that attempt |
| `<agent>/result.json` | The session's terminal disposition |
| `manifest.json` | Tool, model and route for each illustrative session, plus SHA-256 of every file |

The bytes are exactly what each agent wrote. Nothing was edited, including plans that
are not valid JSON. `docs/agents/recorded-sessions.md` replays every recorded attempt
through the checker and asserts that it reproduces the recorded band.

## How they were recorded

- **Claude Code 2.1.281 and Codex CLI 0.156.1** ran through GND's own adapters
  (`gnd exp run --adapter claude|codex`) against a clean installed copy of GND from
  which this example had been removed, so the answer was not on disk. (A first Claude
  Code run found the packaged answer in a source checkout. That run was discarded.)
  Codex requires the experiment to sit in a git repository and a model that the login
  supports, which was selected with a scratch `CODEX_HOME`.
- **Nine hosted models** ran through `gnd exp run --adapter-policy` with an
  `openai-compatible` policy that points at `openrouter_gateway.py` on loopback. The
  adapter sends a model only a prompt that names the contract, so the gateway supplies
  the context a tool-using agent would read itself: the task, the model and the state.
  The OpenRouter key lived only in the gateway's environment.
- Each hosted model ran three times, because sampling varies. Claude Code and Codex ran
  once each.

This is not a benchmark. It is one small task, and the numbers describe these runs.
