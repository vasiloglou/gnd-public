---
milestone: reviewed-vocabulary-growth
station: "plan gate"
skill: "n/a -- repository development; plan written by start-milestone"
scope: plan-gate
date: 2026-11-23
gate:
  command: "ruling: owner approved .gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviewed-vocabulary-growth-plan.md sha256 72710267b2dcdacc82b46014037ba0df74c345439e96f62b4ba5db52617f7ec7"
  exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviewed-vocabulary-growth-plan.md
    sha256: 72710267b2dcdacc82b46014037ba0df74c345439e96f62b4ba5db52617f7ec7
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/evidence/plan-review-r1/PANEL-REVIEW.md
    sha256: b270490ae9de6b7c0d43a0dd152378aa33ab1bf4eecbc6ddab827b48cedb8049
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/evidence/plan-review-r1/disposition.md
    sha256: 669b1837fae3d336e39674a90f1106d56271d29d228bf366e00c4ba42eaeb536
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/evidence/plan-review-r2/disposition.md
    sha256: ce5ec6d571f8107795f55f99e9320560f2b1688d140e8a92123386a1f68519ea
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/evidence/plan-review-r3/disposition.md
    sha256: e21a8ac5939f0b3632d8d9adb9a9cd2931b6ffe53e5cd3e9084cdce35144ed9e
---

# Claim

The owner approved plan r4 on 2026-11-23, with decisions D1–D14 each ruled
as the plan proposes. `auto=false`. The ruling approves the plan only: each
phase spec has its own owner gate, and the VG1 draft spec
(`notes/phase-VG1-spec.md`, sha256
`f96702b49b2d6c039a1965acdc73991fc1ee117bd5703e8db10b441ccba3c5d0`) is not
approved here.

## Gate output (verbatim)

Authorization source: the owner's reply in the planning session, 2026-11-23.
This session asked:

    Do you confirm that approval here, and should the plan gate be recorded
    over r4 with every decision as proposed (including D5 text-only), or
    over r3 only with r4 left as a proposed amendment?

with the short form "Record the plan gate over r4, with every decision as
proposed?". The owner answered:

    Yes, gate on r4

Ruling, owner, 2026-11-23:

    approved notes/reviewed-vocabulary-growth-plan.md r4,
    sha256 72710267b2dcdacc82b46014037ba0df74c345439e96f62b4ba5db52617f7ec7

Earlier the same day another session relayed that the owner had typed there
"approve all as proposed, no further review", about plan r3. This session
did not see that message and this record does not rest on it. It rests on
the direct answer above, which names r4.

Before that, asked whether to repair the eight points of the third run "to
r4 and stop reviewing, or rerun the panel with a longer timeout", the owner
answered "Repair to r4".

## Rulings recorded

Each row is the plan's "Proposed" column of §10, ruled by the owner as
proposed.

| ID | Ruling (owner, 2026-11-23) |
|---|---|
| D1 | one milestone for #221, #218 and #222 |
| D2 | (a): rule D-12 also admits a new `sample` and a new `common-sense` constraint when it is `proposed` and `deontic` |
| D3 | (a): an unattended root may include a reviewed model. Included elements are exempt from U2–U6, from U7 as D14 rules, and from U8 as D13 rules |
| D4 | (a): U1 admits no documents while the root declares at least one include and nothing else but its header. The test is read on the root's own document. A model with no include keeps U1 as today |
| D5 | one line per include in the text output of `gnd validate`, with the counts the plan lists, and the `includes[ID]:` prefix on every diagnostic, the span walk's included. Carrier (a): text output only; the JSON payload is unchanged. No line on `gnd check` or `gnd judgments check` |
| D6 | `gnd evolve` refuses `repin-include` on an unattended root, with or without the additive policy |
| D7 | phase diffs are reviewed with the review helper, one reviewer in a different tool |
| D8 | plan review: the GND panel light, already selected by the owner. Close review: the same instrument |
| D9 | VG1 measures `gnd verify` at 1,000 extra types; the witness oracle's walk gets its own table only if that is over the bound |
| D10 | `gnd judgments check` keeps its two checker runs; bounded at twice the check bound; a successor question |
| D11 | the stale lines of `project.md` are the owner's to correct outside a phase; every record names `uv run ruff check src tests tools` as the lint gate. The index review stays an offer and is not accepted by this ruling |
| D12 | a subtype chain hundreds of types deep is out of scope; a successor question with its numbers |
| D13 | (a): the root's pin is the statement of review; U8 is kept for an included element that is not `confirmed` |
| D14 | (a): an included span that names a root-declared document keeps U7's shape check and is re-hashed and counted; one that names another document is read by no rule |

Order: VG1, VG2, VG3, VG4, VG5, with GO1 of growth-round-outcomes between
VG1 and VG2 if the roadmap's order is followed (plan §3).

## Plan review

The instrument was the GND panel light at high effort, selected by the
owner. Three runs were made and one produced a panel result. All are
advisory.

- Round 1 read r1 (`a04e5624`, sha256 `3d4a06b8…eb7f`): four of six seats
  succeeded, each with `revise`. The report retains 22 concerns, 3 of them
  blocking by its triage. All 22 reproduced and none was rejected. r2
  applies them, tagged `(p1)`.
- Round 2 read r2 (`a4db0773`, sha256 `7a2c6bf7…0b9b`): exit 16, two of six
  seats. **No panel result.** The two reviews raised four points, all
  reproduced. r3 applies them, tagged `(s2)`.
- A third run read r3 (`28f94c58`, sha256 `96acc9bf…f7ff`): exit 16, two of
  six seats. **No panel result.** The two reviews raised eight points, none
  above medium, all reproduced. r4 applies them, tagged `(s3)`.

The stop rule declared in r2 (more than half of a round's findings attack
text a repair created) was met in round 2 and in the third run, counted over
two seats each time.

**No reviewer has read r4.** Its `(s3)` repairs carry no review opinion.
Three of them are more than a wording change: U7's shape check is kept for
an included span that names a root-declared document, the first-document
rule is limited to a root that declares an include, and the per-include
lines are carried in text output only.

## Boundary -- what this result did NOT establish

- It is a ruling, not a review opinion. A panel result exists for r1 only.
  r2 and r3 were each read by two single reviewers, and r4 by none.
- It approves no spec. VG1's draft waits for its own owner gate, and VG2–VG5
  have no spec yet.
- It grants no `auto` delegation, no merge, no release and no publication.
- It rules nothing in growth-round-outcomes, literature-host-interfaces or
  literature-reading-reference.
- Every measurement the plan calls "observed" was run once, on one laptop.
  The ruling does not re-measure any of them.

## Open questions

- Those the plan carries into the specs (§10, last paragraph).
- A D3 (b) ruling would have needed a plan amendment; D3 is ruled (a), so
  none is owed.
- The roadmap's "Proposed order" places GO1 between VG1 and VG2. Whether it
  runs there is decided when VG1 closes.
