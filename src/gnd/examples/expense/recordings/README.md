# Recorded coding-assistant sessions: Expense

Real sessions on the Expense task, recorded on 2026-10-14 with `tools/record_pyrel_sessions.py`
(in the repository, not the wheel). Each session ran `gnd exp run` with a schema-6
constraint-satisfaction contract (coverage floor: two chain approvals) and a budget of
three attempts, against a clean installed GND from which this example folder had been
removed, so the shipped answers were not on disk. The packaged skills were installed in
the workspace with `gnd install --project`.

| File | What it is |
|---|---|
| `TASK-conflict.md`, `TASK-plain.md` | The two task variants as the agent read them; `conflict` says the team lead approved expense 102 (800 EUR), which the team-lead limit forbids |
| `results.json` | Every run: agent, variant, run number, disposition, attempts, verifier exit per attempt |
| `manifest.json` | Per session: tool, model, route, SHA-256 of every committed file, and the SHA-256 of each unredacted transcript |
| `<agent>-<variant>-<n>/attempt-NNNN/` | The candidate the agent wrote, GND's closed `feedback.json`, and `agent.stdout` (JSON lines: what the agent said, ran and wrote) |
| `<agent>-<variant>-<n>/result.json` | The session's terminal disposition |

## What happened

Codex CLI 0.156.1 with `--model gpt-5.6-sol` under a ChatGPT login ran four sessions
(two per variant). All four were accepted on attempt 1. In every `conflict` run the agent
read the contract, opened the installed `gnd-dev-session` skill, read the task, the seed
facts and the model, named the conflict (expense 102 is 800 EUR; the team-lead limit is
100 EUR) and recorded the approval under the `finance` chain instead, after running
`gnd check` itself. No run was discarded.

Claude Code 2.1.281 was not recorded: the standalone CLI had no login of its own on the
recording machine, and the owner's session did not permit the API-key wrapper
(`tools/agent_with_env_key.py`) to run. The gate record is
`.gnd-planning/milestones/pyrel-agent-loop/005-recording-gate.md`.

## Redaction

Exactly two substitutions were applied to `agent.stdout`: the workspace path became
`<workspace>` and the home directory became `<home>`. Candidates and feedback are
byte-for-byte as recorded; feedback carries no paths by design. Transcripts are capped
at 256 KiB. `manifest.json` records the SHA-256 of the committed bytes and, under
`source_stdout_sha256`, of the unredacted original.

This is not a benchmark: one small task, one tool, four runs. The numbers describe these runs.
