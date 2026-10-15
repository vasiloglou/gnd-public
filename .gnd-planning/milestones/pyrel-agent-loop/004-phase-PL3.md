---
milestone: pyrel-agent-loop
station: phase-PL3
skill: "n/a -- repository development, not a gnd-solve station"
scope: phase-PL3
date: 2026-10-14
source_base: ad85288
gate:
  command: "uv run pytest -q -p no:cacheprovider tests/test_pyrel_stand_in_sessions.py tests/test_recording_tools.py"
  exit: 0
  output: "10 passed, 2 deselected in 3.02s"
native_gate:
  command: "uv run pytest -q -p no:cacheprovider -m pyrel_oracle tests/test_pyrel_stand_in_sessions.py"
  exit: 0
  output: "2 passed, 4 deselected in 10.11s"
evidence:
  - {"path": ".gnd-planning/milestones/pyrel-agent-loop/notes/phase-PL3-spec.md"}
  - {"path": ".gnd-planning/milestones/pyrel-agent-loop/notes/phase-PL3-claude-review.md"}
---
# Phase PL3: the deterministic agent loop

Spec: [notes/phase-PL3-spec.md](notes/phase-PL3-spec.md), delegated approval
(auto=true). Implemented and verified on 2026-10-14.

## What landed

- `src/gnd/examples/bookrec/stand_in_agent.py` and
  `src/gnd/examples/expense/stand_in_agent.py`: deterministic stand-ins driven
  by `gnd exp run` through a command policy. Attempt 1 obeys the user's bad
  request; attempt 2 reads `offending_facts` from the closed feedback and
  repairs. Both sessions end `accepted` after two attempts with the pinned
  witnesses in attempt-1 feedback.
- `tests/test_pyrel_stand_in_sessions.py`: end-to-end sessions in both domains,
  feedback shape, retained candidates, no repaired value in the feedback,
  version probe, literal first attempt without feedback, missing-seed message;
  under `pyrel_oracle` the accepted candidates pass the PyRel app (one warning
  for BookRec; two approvals for Expense) and the refused ones fail with the
  pinned witness.

Measured before implementation: the agent runs in `candidate/`, inputs sit at
`../input/`, feedback is `attempts/NNNN/feedback.json` with
`required[0].acceptance.violations[*].offending_facts`, candidates are retained
at `attempts/NNNN/candidate/<subject>`.

## Review

One reviewer is one reviewer: a single Claude subagent, report retained verbatim
in `notes/phase-PL3-claude-review.md`. Verdict: approve, with hardening notes.

| # | Class | Finding | Disposition |
|---|---|---|---|
| H1 | hardening | pair match was rule-blind and role-blind | fixed: matches `$u`/`$b` by name |
| H2 | hardening | `int(fact["$e"])` not total | fixed: integer check |
| H3 | informational | malformed feedback is a traceback | accepted for a tutorial script; GND never emits such bytes |
| H4 | hardening | missing seed gave a bare traceback | fixed: one-line message naming the expected path |
| H5 | informational | uncapped seed read | accepted; inputs are the shipped seeds and GND caps the candidate |
| C1 | completeness | missing-feedback branch not tested directly | fixed: direct stdin case and missing-seed case |
| C2 | completeness | oracle test did not pin the warning count or `approved == 2` | fixed |
| C3 | completeness | leak-check comment overclaimed | reworded |
| C4 | completeness | RF7 pre-existing failure cited as pass | residual cited here |
| C5 | informational | `ruff format` differences | not enforced by the repository |

## Refactoring review

None needed: the two stand-ins mirror the approvals stand-in, each with one
feedback reader; no shared helper is warranted for three forty-line scripts.

## Boundary

The stand-ins are deterministic and call no model. Their repair reads only the
closed feedback. Contract and policy are written by page blocks at PL5. The
pre-existing RF7 failure at `main` is unchanged.

## Open questions

None new.
