---
milestone: pyrel-agent-loop
station: owner-gate
skill: start-milestone
scope: plan-amendment-a1
date: 2026-10-14
---
# Owner decisions on amendment A1

The owner reviewed the plan summary in the session on 2026-10-14 and ruled on
the four open decisions of [notes/plan-amendment-a1.md](notes/plan-amendment-a1.md):

| # | Decision | Ruling (owner's words) |
|---|---|---|
| A1-D2 | Claude Code credentials for recordings | "Claude is authenticated" |
| A1-D3 | OpenRouter key for small-model recordings | "you can use the openrouter from .env". Read as data by the gateway's key wrapper only; never sourced or printed |
| A1-D1 | The bot's answer: operation plan or population | "real operation plans" |
| PL12-Q2 | LQP version verified only by compiling until an engine is available | "ok" |

Earlier rulings in the same session:
- implement all five toy examples;
- write the rules as PyRel requirements, in an LQP version and a version without LQP.

Amendment A1 is therefore adopted, with the phase order:

1. PL13a, the remaining families;
2. PL13b, derivations;
3. PL14, calendar and reference populations;
4. PL15, plans;
5. PL16, the five examples;
6. PL17, recordings;
7. PL18, documentation;
8. PL19, close.

These decisions extend `005-recording-gate.md` to OpenRouter models, which the
`.env` key is read as data for. The run plan of five runs per model, every run
reported, is fixed in A1 before any run.

Merge, release and certification stay separate owner decisions.
