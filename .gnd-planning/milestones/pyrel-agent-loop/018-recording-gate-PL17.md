---
milestone: pyrel-agent-loop
station: owner-gate
skill: process-phase
scope: phase-PL17-recording
date: 2026-10-14
---
# Owner authorization for the PL17 recordings

The owner's rulings authorize recording real models behind the five plan apps:
- "try a smaller model where you can show the retry" (A1);
- "1. Claude is authenticated 2. you can use the openrouter from .env" (A1 decisions, record 012);
- "you should finish P16 and P17" (2026-10-14).

This record binds that authorization to a named scope, so
`tools/record_plan_apps.py --authorized-by` can refuse anything outside it.

## Scope

| Item | Authorized |
|---|---|
| Tool | `tools/record_plan_apps.py`, with the bot adapter `tools/plan_app_bot.py` |
| Claude Code | the owner's logged-in `claude` CLI: `--print --tools "" --no-session-persistence --strict-mcp-config`, in an empty temporary directory, with `--model haiku` and with the account default. No API key is read |
| OpenRouter | `meta-llama/llama-3.1-8b-instruct`, `google/gemma-3-4b-it`, `meta-llama/llama-3.2-3b-instruct` (A1 table), at the provider's default temperature, at most 2000 output tokens per call |
| Key | `OPENROUTER_API_KEY` only, read from `.env` as data by `tools/agent_with_env_key.py` into the bot process. `.env` is never sourced; the key is never printed; recorded files are searched for it before they are kept |
| Questions | the five apps' documented questions (course, access, lease, clinic, trip) |
| Runs | 5 per model per example, 3 attempts each (A1 protocol), 1800 s wall per run |
| Checker | the PyRel backend (the generated DuckDB program); GND re-checks the recorded plans in tests |
| Redaction | workspace → `<workspace>`, repository → `<repo>`, home → `<home>` |

Every run is listed in `results.json`; none is discarded for its outcome. Paid,
nondeterministic calls happen only through this tool under this record.
