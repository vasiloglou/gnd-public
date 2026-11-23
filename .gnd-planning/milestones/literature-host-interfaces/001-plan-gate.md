---
milestone: literature-host-interfaces
station: plan-gate
scope: plan-gate
date: 2026-11-23
skill: "start-milestone (planning); the gate ruled by the owner, auto=false"
gates:
  - command: "uv run python tools/run_gnd_review_panel.py review-request.json --out panel-run --reviewer-timeout 600 --overall-timeout 900"
    exit: 0
  - command: "uv run gnd review finalize panel-run synthesis.json --out PANEL-REVIEW.md"
    exit: 0
  - command: "uv run python tools/run_gnd_review_panel.py review-request.json --out panel-run --reviewer-timeout 600 --overall-timeout 900"
    exit: 0
  - command: "uv run gnd review finalize panel-run synthesis.json --out PANEL-REVIEW.md"
    exit: 0
  - command: "ruling: owner approved .gnd-planning/milestones/literature-host-interfaces/notes/literature-host-interfaces-plan.md sha256 2dc760e58dbd1b95396695b1c9690443dc62af91bae52b1c3b4ee0dfa3e01528"
    exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/reviews/literature-host-interfaces-r4-panel/PANEL-REVIEW.md
    sha256: 9e761cbc0f7650917f08a17d90b07e7901a06434d2a3e80f700dc27c4ae772ac
  - path: .gnd-planning/reviews/literature-host-interfaces-r5-panel/PANEL-REVIEW.md
    sha256: 73e3c873b36f9e8593c28495625889c31c60510b4c2e253443a89d7dd01866f6
---

# Plan gate: literature-host-interfaces r6

Date: 2026-11-23. `auto=false`.

## Gate output (verbatim)

The gate is the owner's ruling, given in the planning session on 2026-11-23.
The driving agent listed the thirteen open decisions and asked whether to
rule all thirteen as proposed, with D15 phase by phase, or to change some.
The owner answered:

> All as proposed

The full digest of the approved bytes was computed from the working file
before this record was written:

| Artifact | SHA-256 |
|---|---|
| `notes/literature-host-interfaces-plan.md` (r6) | `2dc760e58dbd1b95396695b1c9690443dc62af91bae52b1c3b4ee0dfa3e01528` |

**The plan is not edited to record its own approval.** Its status line still
reads "not approved", and its §10 rows still read "Proposed". This record is
what changes that.

## Rulings

Five decisions were ruled before the gate and are tagged `(o)` in the plan:

- D6: as proposed (2026-11-22).
- D9: the other reading, follow entities outward (2026-11-22).
- D10: the other reading, own handle only (2026-11-22).
- D14: the full GND panel (2026-11-23).
- D17: as proposed (2026-11-23).

The gate rules the other thirteen as the plan's §10 proposes them:

| Decision | Ruling |
|---|---|
| D1 producer protocol home | in `reading.py`, until a second example uses it |
| D2 LH4 disposition | `policy-refused`, in the `/2` record only; `/1` keeps `fail` |
| D3 fixture-only steps | calibration, the conflict check and the absence scope are optional and declared in the profile; an undeclared step is `skipped`; the label is profile data; a reviewer is optional, and any decision other than `supported` refuses the run |
| D4 limits | seven limits with the defaults and ceilings in §10. The retained-file cap of a `/2` run is derived from the run's bounds and is never less than 128 KiB. `document_budget`'s ceiling is the largest-budget limit |
| D5 reading manifest | `literature-reading-run/2` for any run that uses a new argument; `/1` is unchanged otherwise |
| D7 malformed response or raising producer | refuse the run with nothing written |
| D8 judged unit | targets are attached rows; supported means at least one target and every target admitted |
| D11 `max_targets` ceiling | 1,024, the stable command's cap |
| D12 admission record | `literature-assertion-admission/2`; the packaged call keeps `/1` |
| D13 phase diff reviewer | the review helper, subject `phase`, one reviewer in a different tool |
| D15 how the milestone runs | phase by phase, with an owner gate on each spec (`auto=false`) |
| D16 caller-run route exits | 0, 1, 2 and 4 are recorded and the run completes; any other exit refuses |
| D18 generic row bound | `max_rows`, default 16,384, ceiling 65,536; `max_rows` without a shape refuses |

D15's proposal was "the owner selects". The owner's "All as proposed"
answered a question that offered phase by phase as the proposal, so D15 is
recorded as phase by phase. No delegation (`auto=true`) is given for this
milestone.

## Plan review

The instrument was the full GND review panel (D14). It ran twice, each time
from a disposable clone at `4ad0d216` with the uncommitted planning files
copied in. The run records hold the provenance checks, the reviewer outcomes
and the verified facts.

**Round 1, over r4** (sha256 `6cadaa9134585b348d53ef50ef5c35638a3b0bb20c7c36726ac53039ac357cb6`;
[record](../../reviews/literature-host-interfaces-r4-panel/README.md)):

- Outcome: four of six reviewers succeeded, all `revise`. Qwen timed out, and Gemini returned malformed output.
- Findings: two blocking concerns and twelve ranked fixes.
- Disposition: r5 applied all twelve, tagged `(p1)`. For fix 2 (the lint gate), the owner had the dev-tools scripts fixed upstream (dev-tools PR 34, `a29562a`), and the re-sync is part of this milestone's planning change.

**Round 2, over r5** (sha256 `c1a832378a2f303cdf1be8884ea61e745eca7f22e4fab19a449761d62b082c9b`;
[record](../../reviews/literature-host-interfaces-r5-panel/README.md)):

- Outcome: five of six reviewers succeeded. Gemini was `approve`; Claude, Codex, Kimi and GLM were `revise`. Qwen timed out.
- Findings: three agreed concerns, one single-reviewer blocking concern on the retained-file bound, and seven ranked fixes.
- Disposition: r6 applied all seven, tagged `(p2)`. Plan §11 maps every fix of both rounds to its sites.

**No opinion on r6.** The convergence rules allow two rounds, so no panel read
r6. Its new sentences carry no review opinion, and this approval adds none.

## What the approval leaves open

- **The LH1 spec is not approved.** The draft
  `notes/phase-LH1-spec.md` (sha256
  `b3270ded71564d02d8aa0dc806872a53b02c6a4b3b3272c6538348a31f38e416`) has
  its own owner gate, including its decisions LH1-D1 to LH1-D5. No code may be
  written before that gate.
- **The LH1 start commit.** Plan §3 sets it as the merge that lands this plan
  with the dev-tools re-sync. That commit does not exist yet, and the LH1 spec
  records it.
- **LH2 to LH4** each need their own spec and gate.

## Selection

No phase has been selected. Execution starts only when the owner explicitly
selects `process-phase LH1 literature-host-interfaces`.

## Boundary

- **Later phases.** Approving the plan does not approve any phase spec.
- **Planning record only.** This record authorizes no implementation, push,
  PR, merge, release or publication.
- **Uncommitted bytes.** The digests above are of working-tree files. They
  become citations only once the files are committed together with this
  record.
