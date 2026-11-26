---
subject: issue-318
station: discovery-gate
scope: issue-318-hook-discovery
date: 2026-11-26
source_base: a6cf76e197d84acced25b41d2a3643fdf80bbb61
evidence:
  - path: .gnd-planning/maintenance/2026-11-26-issue-318-command-log/evidence/discover.py
    sha256: b9511b09dc6b3206d9affb30b6344e48afde345c01f2e9c4d6608deeb43115a1
  - path: .gnd-planning/maintenance/2026-11-26-issue-318-command-log/evidence/hook.py
    sha256: 0fddd80e57a2d095e752b001d6a13b142e6cb3d0f255fba22d8195d8faaf2e4d
  - path: tools/record_skill_sessions.py
    sha256: 0c8b9e437ea72ec0b830be85ea7ebae36cf5f9dd8479225f586de92fb3373068
  - path: .gnd-planning/maintenance/2026-11-26-issue-318-command-log/evidence/owner-statements.txt
    sha256: b376ebae1acb9b0d052dc8d645f16ad13edb9dbbd47a55081f2e4ce76550e067
---

# Issue 318 discovery gate

One paid run to learn what Claude Code's Bash hooks receive, so the
per-command log that issue 318 item 2 proposes can read the exit code from a
documented place, or from the place this run shows.

| Item | Declared |
|---|---|
| authority | the owner's words, quoted whole in [owner-statements.txt](evidence/owner-statements.txt): "appeoved", then "Yes, higher ceiling" |
| model | Claude Code `--model haiku`, Claude Code's own login, no `ANTHROPIC_*` or `OPENROUTER_*` variables, no repository `.env` |
| conversation | the two turns of `TURNS` in [discover.py](evidence/discover.py) at the SHA-256 above, in a new temporary folder; Bash allowed for `true`, `false` and `sh -c *` only, so `date` is refused |
| hooks | PreToolUse, PostToolUse and PostToolUseFailure on Bash, each running [hook.py](evidence/hook.py), attached with `--settings` on both calls; user and local settings not loaded |
| run bound | one run of the script; two turns at most, 300 seconds a turn; no re-run under this record |
| cost ceiling | USD 3.00 in total; USD 1.40 a turn through `--max-budget-usd`, and a turn starts only while the total stays under the ceiling |
| keeping | the raw stream and hook log stay outside the repository; only `schema.json` (key paths and types, a few named values, host paths redacted, refused on any leak needle) may be committed beside this record |
| not authorized | any recording into an example, any other model, a second run, a merge or a publication |
