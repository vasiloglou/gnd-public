# Recorded sessions: Claude Code runs gnd-model-evolve on the course model

Recorded under the gate record
`.gnd-planning/milestones/pyrel-agent-loop/019-recording-gate-PL18-skills.md`
(amendments 2 and 3). Each run starts in an empty folder holding only the
course `model.orm.json` and `rules.md`. The plugin is loaded from a copy that
holds only the skills (`--plugin-dir`), so the skill is `/gnd:gnd-model-evolve`
as a reader types it. The user's side is declared in advance:

1. `/gnd:gnd-model-evolve Lower the credit cap from 18 to 6 credits a term, for every student.`
2. `Yes, apply it.` (repeated if needed, at most 6 turns)

The user stops answering once the model validates and its credit cap is 6.

| Run | Turns | Model validates | Claude Code's reported cost (USD) | Refused by the permission rules |
|---|---|---|---|---|
| 1 | 1 | yes | 0.24 | 3 |
| 2 | 1 | yes | 0.22 | 7 |

Both runs wrote the proposal themselves, previewed it, and applied it in the first
turn. The change is modify-only and the preview reported it as not breaking, so
the skill applied it without an acceptance step, as its contract allows. A
breaking change (a rename or a delete) stops until the owner accepts the
preview's exact report digest.

## What was kept

The same keep filter as `../skill-sessions/`: tool output only for plain `gnd`
commands and files in the workspace, no Claude Code start-event paths, and
thinking blocks without signatures. Paths are shortened to `<workspace>`,
`<plugin>`, `<repo>`, `<home>` and `<tmp>`.

## Caveats

- **An earlier launch is not kept here.** It had two runs, recorded with the
  whole repository as the plugin folder and without `shasum` allowed. Run 1
  found the course example's shipped proposal and used it as a template. Run 2
  stopped after five refusals with the model unchanged. Gate amendment 3
  describes both.
- **The skill's pages do not give the proposal format in full.** Both runs read
  GND's installed source (`src/gnd/evolve/models.py`) to find it; run 1 also read
  the approvals example's model.
- **The plugin copy did not fence the repository off.** Read and Grep could still
  reach `<repo>`, including the course example's shipped proposal; neither run
  opened it. Run 1 also searched `<home>/.claude/`, and both runs wrote scripts
  to `<tmp>`, outside the workspace. Those outputs are not kept.
- **Redacted after review.** Claude Code filled the proposal's audit fields with
  the git user's email address and handle. They are replaced by `<user-email>`
  and `<user>` (`manifest.json`, `rebound`), and both recorders now search for
  them.
- **Hashing was done by hand.** Python was not allowed, so each run wrote the
  canonical JSON itself and hashed it with `shasum`. `gnd evolve preview`
  checks every digest, so a wrong one would have been refused.
