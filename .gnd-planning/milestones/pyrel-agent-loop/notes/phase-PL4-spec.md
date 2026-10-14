# Phase PL4 spec: real recorded sessions

## 1. Status

owner-decided (2026-10-14): delegated approval under
[`001-plan-gate.md`](../001-plan-gate.md); live runs authorized by
[`005-recording-gate.md`](../005-recording-gate.md). Implementable; PL3 landed.

## 2. Provenance

Plan r1 §2 (recordings), §4 PL4 row, §9 PL4 row, PL-R2, PL-R3, PL-R6. Pattern:
`src/gnd/examples/approvals/recordings/` and `tests/test_agent_recordings.py`.
Measured before writing (2026-10-14 smoke runs):

- Claude Code 2.1.281 started under the adapter's minimal environment but
  returned `Not logged in · Please run /login`: the standalone CLI has no login
  of its own on this machine; the "logged in" status seen interactively belongs
  to the desktop app's host session. A wrapper that imports `ANTHROPIC_API_KEY`
  from the owner's `.env` as data was written (`tools/agent_with_env_key.py`),
  but the session's permission classifier refused the first key-bearing call as
  a real-world transaction. Claude Code recordings therefore wait for the owner
  (allow the wrapper, or `claude login` for the standalone CLI).
- Codex CLI 0.156.1 under a ChatGPT login rejects its default model; with
  `--model gpt-5.6-sol` (the model the approvals recordings used) it runs. One
  smoke session on the BookRec conflict task was accepted on attempt 1: the
  agent read the contract, opened the installed `gnd-solve` skill, read the
  task, seed and model, reasoned that Ada is a minor and `night` is adult-rated,
  recommended `map` and `river`, and ran `gnd check` itself before finishing.

## 3. Obligations

| Source | Obligation | Discharge |
|---|---|---|
| Owner review: show what the LLM outputs, how GND checks it, what it feeds back; show skills; show reasoning | committed transcripts with the agent's messages and commands, candidate, feedback | §6.2 layout; §8 rows 1–3 |
| Completion predicate 4 | every quoted excerpt printed from a SHA-256-checked file | PL5 page blocks; §8 row 4 |
| PL-R2 | model calls only in the tool under the gate | `--authorized-by` refusal; §8 row 5 |
| PL-R3 | quotes printed, not typed | PL5 |
| PL-R6 | every run listed; redaction documented; unredacted digests kept | `results.json`, `manifest.json` `source_stdout_sha256`, README |
| 005 gate | tools, scope, runs, redaction as listed | tool defaults |
| Standing rule 1 | stdout capped at 256 KiB; env file capped at 64 KiB and parsed as data | tool constants |

## 4. Standing rules, bound

1. Totality: the recorder treats agent stdout as bytes, decodes with
   replacement, and caps; the key wrapper refuses an oversized env file or a
   missing/empty key. 2. Bounds: fixed run plan; wall clock 900 s per session.
3. Validation order: the gate record is checked before any environment is
   built. 4. One walk: one `harvest()` for every agent. 5. One home: the task
   text lives in the tool and is written to `TASK-<variant>.md`; pages quote
   those files. 6. Measurement: the smoke runs above.

## 5. Goal

`tools/record_pyrel_sessions.py --authorized-by 005-recording-gate.md --agents codex`
exits 0 and writes `src/gnd/examples/{bookrec,expense}/recordings/` with
`README.md`, `TASK-conflict.md`, `TASK-plain.md`, `results.json`,
`manifest.json` and one folder per session holding `result.json` and
`attempt-NNNN/{<subject>, feedback.json, agent.stdout}`;
`tests/test_pyrel_recordings.py` exits 0 (digests, inventory, no needles, replay
bands); the `pyrel_oracle` replay pushes every retained candidate through the
PyRel app and gets the recorded verdict.

## 6. Design

### 6.1 `tools/record_pyrel_sessions.py` (~330 lines) and `tools/agent_with_env_key.py` (~60 lines)

As committed: `clean_install`, `prepare_experiment`, `write_policy`,
`harvest`, `main`. Policies: Claude Code through the key wrapper (not run in
this phase), Codex `exec --json --skip-git-repo-check --sandbox workspace-write --color never --model gpt-5.6-sol`.
Flags: `--agents`, `--domains`, `--variants`, `--runs`, `--max-attempts`,
`--workspace`, `--out`, `--env-file`, `--codex-model`, `--keep-experiments`,
`--dry-run`.

### 6.2 Recording layout per domain

```
recordings/README.md           date, tools, model, scope, redactions, what happened
recordings/TASK-conflict.md    the task as the agent read it
recordings/TASK-plain.md
recordings/results.json        every run: agent, variant, run, disposition, attempts, bands, exit
recordings/manifest.json       per session: files → SHA-256, source_stdout_sha256, tool, model, route
recordings/<agent>-<variant>-<n>/result.json
recordings/<agent>-<variant>-<n>/attempt-NNNN/{recommendation|approvals}.population.json
recordings/<agent>-<variant>-<n>/attempt-NNNN/feedback.json
recordings/<agent>-<variant>-<n>/attempt-NNNN/agent.stdout   (JSON lines, redacted)
```

### 6.3 `tests/test_pyrel_recordings.py`

Mirrors `tests/test_agent_recordings.py`: manifest digests; every committed
file listed (except README, TASK-*, results, manifest); no needles
(`/Users/`, `/private/`, `/home/`, `sk-`, `Bearer`, `API_KEY=`); every
retained candidate replays through `gnd.api.check` to its recorded
`payload_exit`; `results.json` consistent with `manifest.json`; under
`pyrel_oracle`, every candidate through `check_proposal` /
`execute_application` with the same verdict.

## 7. Decisions

| # | Question | Readings | Ruling |
|---|---|---|---|
| D1 | Claude Code credential | (a) wrapper imports the key from `.env`; (b) owner logs the CLI in | (a) built, blocked by the session classifier; needs the owner; recordings proceed with Codex and say so |
| D2 | Codex model | default rejected; `gpt-5.6-sol` accepted | `--codex-model gpt-5.6-sol` |
| D3 | Discarding first-try acceptances | never | every run listed |

## 8. Tests

| File | Case | Expected |
|---|---|---|
| `tests/test_pyrel_recordings.py::test_recorded_bytes_match_the_manifest` | per session | pass |
| `::test_every_committed_file_is_in_the_manifest` | inventory | pass |
| `::test_recordings_contain_no_paths_or_credentials` | needles | pass |
| `::test_every_retained_candidate_replays_to_its_recorded_exit` | `api.check` | pass |
| `::test_results_match_manifest` | consistency | pass |
| `::test_candidates_through_the_pyrel_app` (`pyrel_oracle`) | same verdicts | pass |
| `tests/test_recording_tools.py` | recorder refuses without a gate record; key wrapper refuses a missing/empty key and oversized file; `--version` passes through without the key | pass |

## 9. Out of scope

Hosted models; Claude Code until the owner rules on D1; page prose (PL5).

## 10. Size

~400 tool lines, ~150 test lines, recordings under 1 MiB.

## 11. Approval instrument

This prose plus §8.

## Owner gate

Delegated approval (auto=true), 2026-10-14, under the owner's default plan
approval; live runs under `005-recording-gate.md`. No spec panel.
