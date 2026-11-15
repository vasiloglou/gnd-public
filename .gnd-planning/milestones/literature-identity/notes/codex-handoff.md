# Handoff: running the rest of literature-identity from Codex

Written 2026-11-15 by the session that ran LI0–LI2's gates. It records where
the milestone stands, what a delegated run may and may not do, and the traps
already found. It is navigation, not a ruling: the records it cites are the
authority. Nothing here grants approval.

## Where it stands

| Phase | State | Authority | Next action |
|---|---|---|---|
| Plan | approved r3, D1–D9 ruled | [001](../001-plan-gate.md) | none |
| LI0 | done and recorded | [003](../003-phase-LI0.md) | none |
| LI1 | done and recorded | [004](../004-phase-LI1-spec-gate.md), [005](../005-phase-LI1-corpus-gate.md), [006](../006-phase-LI1.md) | none. Its approved outcomes were amended at 008 |
| LI2 | spec approved, corpus approved, **not implemented** | [007](../007-phase-LI2-spec-gate.md), [008](../008-phase-LI2-corpus-gate.md), [spec](phase-LI2-spec.md) §13 (B1–B4) | implement, so that the red tests turn green against the approved outcomes, unchanged |
| LI3 | not started | plan §4 LI3, plan D4 | spec |
| LI4 | not started | plan §4 LI4, plan D5, D7 | spec |
| LI5 | not started | plan §4 LI5, plan C6 (held out) | spec |
| Close | not started | plan §8 (the maintained panel) | close review and record |

## Branches and PRs

- **The branches stack.** `claude/new-request-published-f8692a` (PR 194:
  plans and LI0), then `claude/li1-spec` (PR 197: LI1), then
  `claude/li2-spec` (LI2 so far). Each builds on the one before it.
- **Neither PR is merged.** Only the owner merges. Continue on
  `claude/li2-spec`, or on a new topic branch built on it, and open a PR per
  phase or per branch. Never push to `main`.
- **`literature-heldout` is local only and must stay that way.** It holds
  the held-out answer key, pinned on the LI1 branch by SHA-256
  (`ef7b017a…27b8`, in `src/gnd/examples/literature/answers/heldout.sha256`).
  - *Where it is.* It exists only in this machine's repository. A run on
    this machine sees it; a cloud run does not.
  - *Who needs it.* LI5's held-out scoring (plan C6) needs it. Read it with
    `git show literature-heldout:heldout-answer-key.json` and check the
    digest first.
  - *Keep it off the LI5 branch.* Never merge it into an LI5 development
    branch (plan C6, LI1 D4).

## What `auto=true` covers, and what it does not

The skill text governs this. In short:

- **It covers** plan, spec and close approval rulings, and amendments,
  within literature-identity only, recorded as **delegated approval
  (auto=true)** with the date, the authorization source, the exact SHA-256
  and the scope. The owner's rulings already recorded stay, and a delegated
  ruling is never described as the owner's reading.
- **It does not select or pay for a review instrument.** The owner must
  name them in the prompt:
  - *Phase diffs:* one reviewer in a different tool. From Codex, that is
    Claude Code with its prompt on stdin. The record must say "one reviewer
    is one reviewer".
  - *Milestone close:* the maintained GND panel, which is the four-reviewer
    bar. It is launched with `uv run python tools/run_gnd_review_panel.py
    REQUEST --out DIR --reviewer-timeout 600 --overall-timeout 900`. It needs
    `OPENROUTER_API_KEY` and `ZAI_API_KEY` in the parent environment, or the
    launcher reads them from the owner's trusted `~/.codex/.env`. Never read
    a repository `.env`, and never print a value. The panel is paid, so it
    runs only if the owner's prompt authorizes it.
- **It never authorizes** a merge, a push to `main`, publication,
  certification, broad lanes (`-m "evidence or census"`), or a push of
  `literature-heldout`.
- **Approved outcomes stay fixed.** Changing an approved expected outcome
  (an `expected/*.expected.json` file or a `cases.json` exit or message) is
  an amendment. Under `auto=true` it is a delegated ruling that keeps the
  prior answer and explains the change; it is never a silent edit.

## LI2 implementation notes

The spec is the design, §13's B1–B4 are ruled, and the red tests are the
contract.

- **What to build.**
  - The new module `src/gnd/composition_resolution.py`, at layer `model`,
    added to `tools/gnd_layers.json`.
  - `check_coverage(keys, decisions)`, with the interface of B2.
  - `parse_resolution` and evidence binding.
  - The five steps in `compose`.
  - The optional record fields, and `parse_record` accepting them.
- **The refusal messages** must equal `resolution/cases.json` exactly, in
  the B3 order.
- **Keys come only from asserted fact types** (B1).
- **The literature builder.** `write_reference_run` must now pass
  `resolution=resolution_for(reference_sources(...))` (D8). Then rebuild with
  `uv run python tools/build_literature_example.py src/gnd/examples/literature`
  and regenerate the report goldens with
  `uv run python tests/test_li1_assurance_report.py --write-goldens`.
- **The harness.** `identity-decisions` becomes active in
  `src/gnd/examples/literature/assurance_report.py`, as spec §6.7 describes
  (it reads `same`-connectivity, D7). It still imports no gnd module.
- **The red baseline** at `baf42979`:
  - `tests/test_li2_resolution.py`: 42 failed, 17 passed.
  - `tests/test_li1_*`: 22 failed, 51 passed.
  - Green means everything passes, with `expected/*.expected.json` and
    `resolution/cases.json` unchanged.
- **The gates** (spec §8.2):
  - the LI2 and LI1 direct tests;
  - the composition consumers;
  - `tests/test_gnd_arch.py`;
  - the structure guard list in `.codex/skills/process-phase/references/project.md`;
  - `uv run ruff check`;
  - `python3 scripts/components_index.py changed --base d09189ca --strict`.

## Traps already found

- **Symlinked paths.** gnd's safe readers refuse a path through a symlink.
  macOS `/var` (the system temporary directory) is one. Use resolved paths
  (`Path(...).resolve()`) for any directory handed to `gnd compose`, `gnd
  check --anchors` or `gnd check --composition`. pytest's `tmp_path` is
  already resolved; `tempfile.TemporaryDirectory()` is not.
- **Plain `gnd check` exits 4 on every source** of the literature model,
  because an anchored rule is unchecked without its sidecar (LI1 A1). An
  empty anchored fact type is `vacuous` (exit 2), and an empty derivation
  reports `pass`.
- **Cross-document derived rows.** The composition record binds the
  composed bytes, so a cross-document derived row cannot be claimed after
  composing. The fixtures use `gnd witness` for recursive chains.
- **`gnd fidelity` refusals are text.** On exit 3 it prints plain text, not
  JSON.
- **New fixture models stay out of `tests/fixtures/`.** LI0's identity
  golden walks `tests/fixtures/**/*.orm.yaml`, so new models go under
  `src/gnd/examples/`.
- **Report goldens pin `harness_sha256`.** Regenerate them after any harness
  edit, and check that only that field moved unless an approved outcome was
  meant to change.
- **The guard list runs on everything.** `tests/test_development_scaffold.py`
  checks every link in `.gnd-planning`. Do not link a record before it
  exists.
- **The prompt goes on stdin.** Review instruments take their prompt on
  stdin, never through argv (project hook).
- **Retained reviewer output.** Before committing it, replace the absolute
  home path with `<repo>`.
- **Downstream applications.** Never name them in this repository's text
  (owner rule).

## A prompt to start the run

Paste this into Codex in this repository, on `claude/li2-spec`. Edit the
review lines to the instruments you want.

```text
process-milestone literature-identity auto=true

I delegate approval of the remaining spec, corpus, amendment and close
rulings for the literature-identity milestone only (phases LI2 through LI5
and the milestone close), under the repository's process-phase and
process-milestone rules. Recorded owner rulings stay as they are.

Review instruments:
- Phase diffs: one independent reviewer in a different tool, Claude Code,
  prompt on stdin. Say "one reviewer is one reviewer" in each record.
- Milestone close: the maintained GND panel via
  tools/run_gnd_review_panel.py, at most two rounds. I authorize its cost
  for this close only.

Not authorized: merging, pushing to main, publication, certification,
broad lanes, or pushing the literature-heldout branch.

Start from .gnd-planning/milestones/literature-identity/notes/codex-handoff.md.
Continue on claude/li2-spec (or a topic branch built on it) and open a PR
for the work. Stop when the milestone close record is written.
```
