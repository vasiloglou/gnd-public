---
milestone: pyrel-agent-loop
station: phase-PL17
skill: "n/a -- repository development, not a gnd-solve station"
scope: phase-PL17
date: 2026-10-15
source_base: 7f27561
gate:
  command: "uv run pytest -q -p no:cacheprovider -m \"pyrel_oracle or not pyrel_oracle\" tests/test_plan_apps.py tests/test_plan_app_recordings.py tests/test_plan_app_recording_tools.py"
  exit: 0
  output: "90 passed in 108.64s (0:01:48)"
tamper_gate:
  command: "python3 <scratch>/pl17/mut2/mutate.py (the reviewer's 15 edits to a copy of the recording, manifest recomputed)"
  exit: 0
  output: "15 of 15 caught (before the fixes: 2 of 15)"
structure_gate:
  command: "uv run pytest -q -p no:cacheprovider tests/test_rf7_structure.py tests/test_development_scaffold.py tests/test_rf6_query_policy.py tests/test_rf1_layering.py tests/test_gnd_arch.py"
  exit: 1
  output: "4 failed, 106 passed: three inherited (rf7 routing, rf6 dynamic inventory x2) and the reference closure, which fails on an untracked .claude/worktrees/rf1-code-refactoring-225109 checkout outside this branch"
recording:
  command: "tools/record_plan_apps.py --authorized-by .gnd-planning/milestones/pyrel-agent-loop/018-recording-gate-PL17.md --out <scratch> --pyrel-python tutorials/runtimes/.venv/bin/python"
  exit: 0
  output: "125 runs (5 models x 5 apps x 5 runs), 260 attempts; then --rebind (temporary paths) and --reindex (the index, drift) on the copy committed here"
evidence:
  - {path: "src/gnd/examples/plan_apps/recordings/results.json", sha256: "1dce761366463544323171e839660fb376580f28206c0d3dfdc0530c5e9f731d"}
  - {path: "src/gnd/examples/plan_apps/recordings/manifest.json", sha256: "dfec2a18944fde45a65347d70e0c3a17215d62f3a429558adb9c50cde05ad08b"}
  - {path: "tools/record_plan_apps.py", sha256: "c41cb3af09dc9cb33bd10ce32ac24d14067e26a6251ec72a2e8450e3346b8313"}
  - {path: "tools/plan_app_bot.py", sha256: "6af5b28b0b783c5206f479955f72fb133603e817da59363ac43523c6d08e2351"}
  - {path: "tests/test_plan_app_recordings.py", sha256: "d78cb2e36b1c74aeea76259a8b973a44b9806b83bbdffa969ce3d30132c0b23f"}
  - {path: ".gnd-planning/milestones/pyrel-agent-loop/notes/phase-PL17-spec.md", sha256: "fc1ee550ab34e33517d49053d35971086cd9f8fa6021fa9627b19b7764cf1509"}
  - {path: ".gnd-planning/milestones/pyrel-agent-loop/notes/phase-PL17-claude-review.md", sha256: "ff540cfe352b385c4d0b522a34e23ff8055641db3af62486879b346a79e98bd2"}
checkpoints:
  - "C7, 2026-10-15: https://claude.ai/artifact/XJJ5searFHytKmeESwtegh (the course rules in English and PyRel; the five models' runs)"
---
# Phase PL17: real models behind the five plan apps, every run reported

Spec: [notes/phase-PL17-spec.md](notes/phase-PL17-spec.md), delegated approval
(auto=true) under the owner's rulings "try a smaller model where you can show
the retry", "Claude is authenticated", "you can use the openrouter from .env"
and "you should finish P16 and P17". Gate:
[018-recording-gate-PL17.md](018-recording-gate-PL17.md). Amendments A1–A8 are
in the spec's §11.

## What landed

- **`tools/plan_app_bot.py`.** It puts Claude Code (with no tools) or an
  OpenRouter model behind the apps' bot interface. Feedback is passed in words
  with the witnesses verbatim, and nothing in the answer is repaired except a
  single code fence.
- **`tools/record_plan_apps.py`.** It records every run. It refuses to start
  without the gate record, runs a preflight, redacts, searches for leaks, and
  writes a SHA-256 manifest. `--rebind` and `--reindex` verify the manifest
  before they change anything.
- **`src/gnd/examples/plan_apps/recordings/`.** 125 runs (589 KB):
  - `results.json`;
  - `manifest.json`;
  - a README written from the results, with CAVEATS;
  - each run's `session.txt` and raw replies.
- **Tests:**
  - `tests/test_plan_app_recordings.py` (16): every index field follows from
    the recorded files, GND re-checks every recorded plan, and the README table
    is rebuilt;
  - `tests/test_plan_app_recording_tools.py` (5).

## Measured

| Model (served) | course | access | lease | clinic | trip |
|---|---|---|---|---|---|
| Claude Haiku (claude-haiku-5-5) | 5 first | 5 declined | 3 first, 2 repaired-format | 5 first | 4 first, 1 repaired-format |
| Claude default (claude-opus-5-5) | 5 first | 5 declined | 5 repaired-format | 5 first | 5 first |
| Llama 3.1 8B | 5 refused | 3 repaired-rule, 2 refused | 3 first, 1 repaired-format, 1 refused | 1 repaired-format, 1 declined, 3 refused | 2 first, 3 repaired-rule |
| Gemma 3 4B | 5 refused | 5 refused | 5 refused | 1 declined, 4 refused | 1 first, 1 repaired-rule, 3 refused |
| Llama 3.2 3B | 1 repaired-rule, 4 refused | 5 refused | 5 refused | 2 first, 3 refused | 1 repaired-rule, 1 repaired-format, 3 refused |

- **Attempts:** 260 in all: 60 accepted, 79 refused on a rule, 25 refused as
  malformed, 84 unusable answers, 12 declines.
- **Agreement:** GND gives every recorded plan the exit the PyRel program gave
  it.
- **Cost:** Claude Code reported $0.62 and OpenRouter $0.0135.
- **The A1 replay:** `llama-3.1-8b/access/run-1` (results.json order).
- **Rule repairs come only from the small models.** Every Claude "repair" was a
  format repair (a string amount, or a decline written as a note).

## Review

One reviewer is one reviewer: a single Claude subagent, same model family, with
no paid calls. Its report is retained verbatim in
`notes/phase-PL17-claude-review.md`. Verdict: REVISE. The reviewer
re-derived all 125 rows independently, and they matched.

| # | Finding | Triage | Disposition |
|---|---|---|---|
| B1 | tests could not tell an edited recording from an honest one (2 of 15 edits caught) | blocking | 7 cross-checks added; 15 of 15 caught (`pl17/mut2/result-final.out`) |
| B2.1 | source drift undisclosed | blocking | declared in the manifest and README; tested (A5) |
| B2.2 | Claude Code's extra context | blocking | disclosed (A6). It cannot be removed without an API key; project-only settings for later runs |
| B2.3 | "repaired" mixed rule and format repairs | blocking | split (A4); every Claude repair is a format repair |
| B2.4 | "recording order" ambiguous | blocking | defined as results.json order, in results.json and the README |
| H1 | `--rebind` re-signed any edit | hardening | verifies first; tested |
| H2 | notes could forge a checker line | hardening | printed on one line (A8); the test fails on the pre-fix core (`pl17/prefix-h2.out`) |
| H3 | `failed_checks` mislabelled | hardening | (check, status) pairs and refusal codes; tested |
| H4 | crash misnumbered replies | hardening | named by attempt, failures logged; tested |
| H5, H6 | timeout orphans, one failure aborting all | hardening | process groups, per-run error rows |
| H7 | leak-search gaps | hardening | `/tmp/` and `/var/folders/`; removal on a hit; tested |
| H8 | requested model overwritten; upstream mix | hardening | kept apart for later runs; the mix is disclosed |
| H9 | an API key could reach Claude Code | hardening | removed from its environment |
| C1-C4 | served model, OpenRouter cost, key-reading wording, discarded-run counts | completeness | README and CAVEATS state each |

The tools were not committed before the review, so the pre-fix failures of the
tool tests are the reviewer's reproductions (its scratch `pl17-review/`).
They were not reproduced by running the new tests on the old bytes.

## Refactoring review

Executed:
- `summary`, `outcome`, `replay_choice` and `readme_table` in the recorder
  are the one home for what a run means. The tests and the README both use
  them.
- `parse_answer` (PL16) is the one reader of a reply, in the app and in the
  tests.

Deferred: the app prints text that the recorder parses back. A structured event
log from the app would remove that parse (PL17-Q1).

## Boundary

- **The recorded runs were printed by an earlier `core.py`** (its digest is in
  the manifest's `sources`). Those bytes are not in git; the drift is declared.
- **The OpenRouter reply files** hold the upstream host in `provider`.
- **The Claude lanes ran with Claude Code's own context.** That includes the
  host date, which shows in 4 Haiku clinic runs.
- **5 runs per model and app** at default temperature do not measure a rate.

## Open questions

| # | Question | Target |
|---|---|---|
| PL17-Q1 | A structured event log from the app instead of parsed text | after PL19 |
| PL17-Q2 | Re-record with the type-neutral template, project-only settings and a pinned OpenRouter upstream | owner, if the docs need it |
