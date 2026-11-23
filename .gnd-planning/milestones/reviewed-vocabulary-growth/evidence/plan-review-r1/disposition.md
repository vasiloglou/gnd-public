# Plan review r1: disposition

Reviewed bytes: `notes/reviewed-vocabulary-growth-plan.md` r1, sha256
`3d4a06b864a339f55c82a83c2e9dad6cc704d45bf156aeaeb1aaa086fbd4eb7f`, commit
`a04e5624`. Instrument: GND panel light, selected by the owner on 2026-11-23
("Light panel"). `reviewer_effort` high, bound per run for Claude and Codex
only. Panel implementation equal to HEAD; the `gnd` import resolved inside
the tree.

The run used the session's worktree, not a disposable one. Its tracked files
were clean at `a04e5624`; the request file was the one untracked path before
the run. After the run `git status --short` listed that folder and
`panel-run/` and nothing else, and the reviewed artifact digest was equal
before and after.

    uv run python tools/run_gnd_review_panel.py --light .gnd-planning/milestones/reviewed-vocabulary-growth/evidence/plan-review-r1/review-request.json --out panel-run --effort high --reviewer-timeout 600 --overall-timeout 900
    exit 0, run_sha256 b5124eb719517ccd3b2393a52fbe5c16338edb4ecec13cd81247421755acd5a5
    uv run gnd review finalize panel-run .gnd-planning/milestones/reviewed-vocabulary-growth/evidence/plan-review-r1/synthesis.json --out .gnd-planning/milestones/reviewed-vocabulary-growth/evidence/plan-review-r1/PANEL-REVIEW.md
    exit 0, synthesis_sha256 ffcd2dbd66c4b1f06c2ef99528f0ad9a992fd78ec014667096b0164914b5055d

Four of six seats succeeded: Claude, Codex, Kimi and GLM, each with
`revise`. Two did not, and neither is an opinion:

| Seat | Status | Reason retained in the envelope |
|---|---|---|
| qwen | `nonzero` | the CLI aborted: "tool-call budget of 0 exceeded (--max-tool-calls); observed 1" |
| gemini | `malformed` | "output contains no JSON object", after 8 s |

Claude and GLM share one CLI codebase. Kimi's response is marked incomplete
because one line of prose came before its head; no concern was dropped. One
Claude concern (`u7-status-ambiguous`) carries no verbatim quotation of the
plan; it was checked against the code like the others.

This folder keeps the request, `run.json`, the four `response.json` files
(copied unedited from `panel-run/reviewers/<id>/`; none names a local path),
the synthesis and the finalized report. The rest of `panel-run/` (raw
streams, envelopes, capability probes) is outside history; its digest is
`run_sha256` above. The panel is advisory and is not an approval.

## Findings

Every concern was checked against the code at `a04e5624` before it was
believed. Class is this disposition's MVP triage, not the reviewer's
severity. The disposition was written with no repair applied; the last
column is what it proposed for plan r2. The owner asked for the repair on
2026-11-23 ("Repair to r2"); what r2 carries is under "Repair" below.

| Reviewer | Concern | Reproduced | Class | Proposed for r2 |
|---|---|---|---|---|
| claude, codex | d3-include-launders-unreviewed-content, reviewed-include-trust | yes: the #222 seed, `explicit`, `confirmed`, `alethic`, with no reviewer named, validates standalone; `_includes.py:234` keeps only errors, so a D-03 warning does not stop an include | blocking for D3's ruling | a new decision D13: what makes an include exempt (the root's owner-authored pin, a reviewer the included file must declare, or U3 and U8 kept for included constraints that are not `confirmed`); attribution counts widened; one VG3 criterion; the remaining trust named as a limit in §6 |
| claude, codex | d4-owned-element-definition, first-document-owned-operations | yes: U2 and U8 walk `_iter_provenance_bearing`, which covers operations and obligations (`_unattended.py:193`, `:229`); D4 names three kinds only | hardening, in VG4's own deliverable | D4 (a) defined over every root-owned provenance-bearing element, attachments included, with `reviewer: none` still required; VG4-C3 gains one case per boundary |
| claude, codex | vg1-absolute-time-bounds, vg1-machine-dependent-gate | yes, as worded; the VG1 spec already has a call-count test (T9) the plan does not name | hardening | VG1-C4 (ratio) and a call-count criterion become the required gates; the absolute bounds stay, with their margin and lane stated |
| kimi, glm | rvg-r1-001, d2b-branch-vg5-round2 | yes | completeness | §3 and §4 gain the D2 (b) branch for VG2 and for VG5's round 2 |
| kimi, glm | rvg-r1-002, h13-u8-line-range | yes: the constant is at `_unattended.py:58`, the check at `:229-234` | completeness | H13 corrected |
| claude | r04-criteria-miss-u6-u7-u8 | yes: an attached constraint has origin `model` inside an included fact type (`_includes.py:162-167`) | hardening | VG3-C2 and C3 gain one root-owned case each for U6, U7 and U8, the U8 case on an attached constraint |
| claude | u7-status-ambiguous | yes: U7 is raised only inside the U4, U5 and U6 walks (`_unattended.py:204-226`) | hardening | U7 listed with the exemption for a span an included element carries; decided in the plan, not the spec |
| claude | compat-claim-false-unattended-include-roots | yes, by running it: an unattended root whose included elements are `proposed`, `deontic` and cite a root-declared document validates today, exit 0, with `--document` and `--require-documents` | hardening; the plan's sentence is false | §5 corrected; a new decision D14: an included span that names a root-declared document is still hashed and counted; one criterion pins such a root's output |
| claude | vg3-c8-no-producer | yes: the three remaining `$.object_types[id=…]` issues are errors a standalone-valid include cannot raise | completeness | VG3-C8 restated as a test of `remap_issues`, with a VG3-C7 case on an include root without the mode |
| claude | vg4-lane-omits-u1-tests | yes: `tests/test_unattended_mode.py:120-121` | completeness | added to VG4's homes and lane |
| claude | vg1-c1-base-commit-oracle | yes; the VG1 spec (T1) uses frozen copies of the base bodies | completeness | VG1-C1 and §6 name that reference |
| claude | d9-no-criterion-or-home | yes | completeness | a VG1 criterion for the `gnd verify` measurement and its conditional home |
| codex | include-attribution-per-element | yes | completeness | the VG3 predicate reworded to what D5 gives: one line per include and the prefix on diagnostics |
| kimi | rvg-r1-003 | yes | completeness | R0.4 rewritten |
| glm | lint-gate-conflicts-project-guard | yes: `uv run ruff check` exits 1 at this commit, 198 errors, all under `.codex/skills` and `.claude/skills`; `uv run ruff check src tests tools` passes. The stale statement is `project.md`'s | completeness | H27 becomes observed; D11 names the line |
| glm | vg1-c1-examples-path | yes: top-level `examples/` holds one script and no model | completeness | VG1-C1 names `src/gnd/examples/` |
| glm | include-attribution-validate-only | yes, as a design choice | hardening | answered with D13 in §6: why `gnd validate` is the route that reports it, or extend it |

No concern was rejected. Two need the owner: D13 (the trust boundary of an
exempt include) and D14 (included spans that name a root's document).

## Repair

Plan r2, sha256
`7a2c6bf7e69287aba9b6fcd6472138900e2c80dd14fc0ff2a163540a63e90b9b`, applies
every row above at its site, tagged `(p1)`. The VG1 spec follows it as r2,
sha256 `177abe38649593b44c9d19a7fc959ef09ee5a52553ab99e18d3d58896c459205`.
No review has read either. Where r2 differs from the last column:

- **D13 is written as two options, not three.** (a) the root's pin is the
  statement of review, with U8 kept for an included element that is not
  `confirmed`; (b) the same, and the included file must also declare a
  reviewer. Keeping U3 for unconfirmed included constraints was dropped: the
  source and status rule already makes every `explicit` and `user-supplied`
  constraint `confirmed`, so it would refuse nothing. The plan proposes (a);
  the owner rules.
- **D14 is written with its alternative.** (a) an included span that names a
  root-declared document is still hashed and counted; (b) root-owned spans
  only, as r1 said. The plan proposes (a).
- **`include-attribution-validate-only`** is answered in §6 and D5 as a
  design choice, with its reason; the lines are not extended to `gnd check`
  or `gnd judgments check`.
- **VG1's absolute bounds** keep their numbers. Plan §4 and §6 now say which
  gates read no clock (VG1-C1, C6, C7) and that those are the required
  regression gates.

r2 also carries changes no reviewer raised, tagged `(m)`: `main` moved to
`c47dc126` after r1 (PR 229, PR 230, PR 231), no cited file differs there,
#214 and #217 are closed, and the growth-round-outcomes outline shares
`evolve/service.py` and `unattended-growth.md` with VG2, VG4 and VG5 (plan
H36, §3). Three small corrections by the author: VG1's homes name
`semantic_adapter.py`, as its spec does; the ratio test takes the minimum of
three runs, as its spec says, not a median; and the spec's T1 also compares
`_universe_types`, which plan VG1-C1 names.

Round budget, from plan §8: two. A second round, if the owner asks for one,
reads r2 and is the last.
