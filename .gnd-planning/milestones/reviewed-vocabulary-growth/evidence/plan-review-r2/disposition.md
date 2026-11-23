# Plan review r2: no panel result

Reviewed bytes: `notes/reviewed-vocabulary-growth-plan.md` r2, sha256
`7a2c6bf7e69287aba9b6fcd6472138900e2c80dd14fc0ff2a163540a63e90b9b`, commit
`a4db0773`. Instrument: GND panel light, second round, asked for by the owner
on 2026-11-23. `reviewer_effort` high, bound per run for Claude and Codex
only. The tree was clean at `a4db0773` apart from the request file; the panel
implementation was equal to HEAD and the `gnd` import resolved inside the
tree. The reviewed artifact digest was equal before and after.

    uv run python tools/run_gnd_review_panel.py --light .gnd-planning/milestones/reviewed-vocabulary-growth/evidence/plan-review-r2/review-request.json --out panel-run --effort high --reviewer-timeout 600 --overall-timeout 900
    exit 16, run_sha256 890922adb8413921962648019c83d962849856ead7de016aa5813613fcb2df49

**Exit 16: six seats were attempted and two succeeded. Quorum is three. No
panel result exists for r2.** There is no synthesis and no `PANEL-REVIEW.md`,
and `gnd review finalize` was not run. The run was not repeated: a repeat is
a new panel with its own evidence, and it is the owner's to ask for.

| Seat | Status | Reason retained in the envelope |
|---|---|---|
| claude | `nonzero` | "reviewer capability probe exited nonzero". The help process printed its complete help and returned 0, but its process group needed a SIGTERM to clean. The seat was never invoked |
| codex | `success` | `revise`, 3 concerns, all anchored, response complete |
| qwen | `timeout` | "reviewer invocation exceeded its shared deadline", after 600 s |
| gemini | `malformed` | "output contains no JSON object", after 12 s |
| kimi | `success` | `revise`, 1 concern, anchored. Marked incomplete for one line of prose before its head; no concern was dropped |
| glm | `nonzero` | the same probe result as claude; the two seats share one executable |

In round 1 the same two probes exited cleanly on the same executable, which
has not changed since. The cause of the leftover process was not found.

This folder keeps the request, `run.json` and the two `response.json` files,
copied unedited; none names a local path. The rest of `panel-run/` is outside
history; its digest is `run_sha256` above.

## The two reviews that returned

These are two individual reviews. They are not agreed concerns, not a panel
finding, and not an approval of anything they did not mention. Each was
checked against the code at `a4db0773`. The record was written with no
repair applied; the owner then asked for one ("yes repair"), and what r3
carries is under "Repair" below.

| Reviewer | Concern | Reproduced | Class | What a repair would be |
|---|---|---|---|---|
| codex | d4-root-deontic-note | yes: a note is `{text, rationale}` with no source, status or provenance (`orm-meta.schema.json`, `deontic_notes`), and `_unattended.py` never reads the key. Plan §2's first-document rule lists five kinds of element and not notes, so a root that holds only a note and no document would validate | hardening. Notes carry no span under the mode today, with or without documents | D4 (a) says the root declares nothing but its header and its includes; VG4-C3 gains a note case |
| codex | d14-root-operation-spans | yes: `_iter_unattended_spans` (`_unattended.py:321`) walks object types, fact types, constraints and sample rows; the format says spans on an operation or an obligation "are neither checked by U7 nor counted". Plan §2 says the walk covers "every root-owned span" | completeness: wording | §2 and VG3-C5 say "every root-owned span the walk visits today" |
| codex | d5-attribution-overclaim | yes: §6 says each include is printed "by status, modality and source"; D5 lists three counts over constraints | completeness: wording | §6 names the counts D5 lists |
| kimi | rvg-r2-vg4c3-boundaries | yes: §6 says "one case per boundary"; VG4-C3 has no case for a root that owns only a fact type, only a constraint of its own, or only an obligation | hardening | VG4-C3 gains those three cases |

Kimi's summary also says it checked H13, H30–H36, D13 and D14 against the
three source files, the D2 (b) readings, VG1-C7, VG1-C8, the VG3 criteria it
was asked about and `project.md:129-131`, and found them to hold. That is one
seat's statement, recorded as such.

## The convergence numbers

Plan §8 declared them before this round. They are computed over two seats,
not over a panel.

- Self-inflicted ratio: 4 of 4. Every concern attacks text that r2 created.
  That is over one half, which is the stop condition.
- Same-seat trend: codex 4, then 3; kimi 3, then 1. Severity: codex rated one
  concern high and two medium; kimi one medium.

The round budget was two and both are spent. Whether the plan gate proceeds
on round 1's result and these two reviews, or a new panel is run, is the
owner's decision.

## Repair

Plan r3, sha256
`96acc9bf0ad324802f882b863fe75e5c6910bede25f3ac86fa68032f8ae1f7ff`, applies
all four rows, tagged `(s2)` at their site. No review has read r3.

- **d4-root-deontic-note.** The first-document rule is now written on the
  file: every section of the root other than `version`, `model_id`, `source`
  and `includes` is absent or empty. That is wider than the reviewer asked:
  it also covers `rejected_proposals` and `reference_populations`, so one
  sentence decides every section. VG4-C3 gains a case for each.
- **rvg-r2-vg4c3-boundaries.** VG4-C3 gains a root that owns only a fact
  type, only a top-level constraint, and only an operation that carries an
  obligation. There is no case for an obligation alone: an obligation exists
  only inside an operation.
- **d14-root-operation-spans.** §2 and VG3-C5 say the walk covers the
  root-owned spans it visits today, and that a span on an operation or an
  obligation stays unchecked and uncounted, as "Unattended source" says.
  VG3 does not widen the walk.
- **d5-attribution-overclaim.** §6 names the counts D5 prints and says they
  are counts. D5 and §2 add deontic notes to the element counts.

The VG1 spec changes two sentences to name plan r3; its content is the r2
content, sha256 `9fb95ab7a1aff1a316fbc881620af02eb2b1d8a1e8578ba5fe79927110b36090`.
