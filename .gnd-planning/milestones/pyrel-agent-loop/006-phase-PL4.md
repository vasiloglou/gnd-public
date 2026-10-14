---
milestone: pyrel-agent-loop
station: phase-PL4
skill: "n/a -- repository development, not a gnd-solve station"
scope: phase-PL4
date: 2026-10-14
source_base: 2094f25
gate:
  command: "uv run pytest -q -p no:cacheprovider tests/test_pyrel_recordings.py tests/test_recording_tools.py"
  exit: 0
  output: "22 passed, 2 deselected in 0.79s"
native_gate:
  command: "uv run pytest -q -p no:cacheprovider -m pyrel_oracle tests/test_pyrel_recordings.py"
  exit: 0
  output: "2 passed, 16 deselected in 22.06s"
recording:
  command: "uv run python tools/record_pyrel_sessions.py --authorized-by .gnd-planning/milestones/pyrel-agent-loop/005-recording-gate.md --agents codex --domains bookrec,expense --variants conflict,plain --runs 2 --keep-experiments --out src/gnd/examples"
  exit: 0
  output: "8 sessions, all accepted after 1 attempt; Codex CLI 0.156.1, model gpt-5.6-sol"
evidence:
  - {"path": ".gnd-planning/milestones/pyrel-agent-loop/notes/phase-PL4-spec.md"}
  - {"path": ".gnd-planning/milestones/pyrel-agent-loop/005-recording-gate.md"}
  - {"path": "src/gnd/examples/bookrec/recordings/manifest.json"}
  - {"path": "src/gnd/examples/expense/recordings/manifest.json"}
---
# Phase PL4: real recorded sessions

Spec: [notes/phase-PL4-spec.md](notes/phase-PL4-spec.md), delegated approval
(auto=true); live runs under [005-recording-gate.md](005-recording-gate.md).
Recorded and verified on 2026-10-14.

## What landed

- `tools/record_pyrel_sessions.py`: builds a clean install with the two
  example folders removed, installs the skills, prepares a schema-6
  constraint-satisfaction experiment per domain and task variant, runs
  `gnd exp run` with a declared command policy, harvests candidate, feedback
  and redacted `agent.stdout` per attempt, and writes `results.json`,
  `manifest.json` (with unredacted digests) and the task files. Refuses to
  run without `--authorized-by` naming a gate record.
- `tools/agent_with_env_key.py`: imports exactly one named key from an env
  file as data into a child process; never sources, never prints.
- `src/gnd/examples/{bookrec,expense}/recordings/`: eight Codex CLI sessions
  (two domains, two variants, two runs each), every one accepted on attempt 1,
  plus READMEs stating scope, redaction and what was not recorded.
- `tests/test_pyrel_recordings.py`, `tests/test_recording_tools.py`.

## What happened

Codex CLI 0.156.1 under a ChatGPT login with `--model gpt-5.6-sol`: in every
conflict run the agent opened the installed `gnd-dev-session` skill, read the
task, seed and model, named the conflict in its own words, wrote a candidate
that satisfies the rules, and ran `gnd check` itself. No rule-level refusal
was recorded; the pages say so and show the refusal-and-repair loop with the
PL3 stand-ins.

Claude Code 2.1.281 was not recorded. Under the adapter's minimal environment
the standalone CLI reported `Not logged in`; the interactive "logged in" status
belongs to the desktop app's host session. The key wrapper was written, and
the session's permission classifier refused the first key-bearing call as a
real-world transaction. This needs the owner: allow the wrapper, or log the
standalone CLI in, then rerun the recorder with `--agents claude`.

## Review

No separate reviewer ran over this phase's bytes: the recorder and wrapper are
repository tools outside the wheel, exercised by their tests and by the eight
recorded runs. One reviewer is one reviewer, and here there was none; the PL6
close readers cover these files.

## Refactoring review

None needed: the recorder reuses the approvals recording layout and the
declared-adapter policy shape; no runtime module changed.

## Boundary

Recordings are evidence of eight runs on one day with one tool; they rank
nothing. The pages print committed bytes and never call a model. The Claude
Code recording is open work, not a failure of the loop.

## Open questions

| # | Question | Target |
|---|---|---|
| PL4-Q1 | Record Claude Code once the owner allows the key wrapper or logs the standalone CLI in | owner; rerun `tools/record_pyrel_sessions.py --agents claude` under `005-recording-gate.md` |
