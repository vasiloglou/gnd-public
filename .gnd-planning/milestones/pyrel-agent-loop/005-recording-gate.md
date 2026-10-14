---
milestone: pyrel-agent-loop
station: owner-gate
skill: process-phase
scope: phase-PL4-recording
date: 2026-10-14
---
# Owner authorization for live recording (PL4)

The owner's rulings in the 2026-10-14 session authorize the live recording step:
"Record real sessions + scripted replay" (PL-D3), "approve the plan by default"
(PL-D5), and "if you need keys for llm runs use .env" (PL-D6). This record
binds that authorization to a named scope so `tools/record_pyrel_sessions.py`
can refuse anything outside it.

## Scope

| Item | Authorized |
|---|---|
| Tools | the owner's installed `claude` (Claude Code 2.1.281) and `codex` (Codex CLI 0.156.1), authenticating from their own configuration; no API key is read |
| Claude Code permissions | `--permission-mode acceptEdits --allowedTools "Bash(gnd *),Read,Write,Edit,Glob,Grep" --add-dir <experiment>`; `--output-format stream-json --verbose` so the transcript shows what the assistant read, ran and wrote |
| Codex | `codex exec --json --skip-git-repo-check --sandbox workspace-write --color never` |
| Tasks | BookRec recommend-for-Ada and Expense approve-102, each in a plain variant and a conflict variant where the request contradicts a rule |
| Runs | up to 2 per agent per task variant, 3 attempts each, 900 s wall per session |
| Environment | a clean install of this checkout from which the example folders are removed, in a scratch workspace; skills installed with `gnd install --project` |
| Redaction | workspace path → `<workspace>`, home path → `<home>`; stdout capped at 256 KiB; unredacted digests recorded |
| Hosted models | not authorized by this record; a later record would name the single key read from `.env` as data |
| Keys | `.env` is never sourced; this run reads no key |

Every run is listed in `results.json`; none is discarded for its outcome.
Paid, nondeterministic calls happen only through this tool under this record.
