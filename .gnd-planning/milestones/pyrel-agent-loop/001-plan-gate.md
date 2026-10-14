---
milestone: pyrel-agent-loop
station: plan-gate
skill: start-milestone
scope: plan-gate
date: 2026-10-14
---
# Owner default approval of plan r1

The owner reviewed the shipped PyRel tutorial pages in a Claude Code session on
2026-10-14, answered four scoping questions (scope, command ergonomics, LLM
evidence, process), then wrote "approve the plan by default" and "if you need
keys for llm runs use .env" before the plan file was final. The approved
session plan was transcribed into
[`notes/pyrel-agent-loop-plan.md`](notes/pyrel-agent-loop-plan.md) with the
repository's plan shape; the owner's rulings are its section 10 (PL-D1–D6).

This is the owner's own approval, given in advance, not a reader panel. No
plan readers ran. The repository's four-reader bar for plan review was not
applied; the owner's explicit approval supersedes it for this plan. Phase
specs within this milestone are approved by delegation under the same ruling
(`auto=true`, scope: `pyrel-agent-loop`). Two steps stay explicit owner
actions: running the owner's `claude`/`codex` CLIs for PL4 recordings, and
merging the pull request.

Plan SHA-256: recorded in the PL1 record once the plan bytes are committed.

## Implementability sweep

- PyRel 1.30.1 runtime project and lock exist (`tutorials/runtimes`,
  `src/gnd/examples/release_governance/runtime-environment`).
- Schema-6 contracts support `constraint-satisfaction` with `coverage` floors
  (`src/gnd/exp/session_contract.py:283-295`); command adapter policies exist
  (`src/gnd/exp/adapter_policy.py`); the approvals stand-in is the pattern.
- Attempts retain agent stdout with a SHA-256 (`src/gnd/exp/session_store.py:1058`).
- `gnd codegen` refuses an unrecorded occupant at a planned path
  (`src/gnd/codegen/plan.py:108`), so the ready folder is copied after codegen.
- Local `claude` and `codex` executables are present; `.env` holds provider key
  names (names only were listed; values never read).
- Every completion predicate has a phase owner (plan §4) and a command (plan §9).

## Boundary

No implementation, review, merge, release or certification has occurred.
`pyrel-applications` records are unchanged. A2 D6 is superseded only for this
milestone (plan PL-R2).
