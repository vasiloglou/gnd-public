---
milestone: induction-skill
station: milestone-close
skill: "n/a -- repository development"
scope: milestone-close
date: 2026-11-26
source_base: 6bbbee81d7f47c8fd7d3f02bedbc6acb648765c4
source_subject: c59dc769
gates:
  - command: "ssh beast-3 'bash -s -- <commit> base' < .gnd-planning/milestones/release-0.5.0/evidence/RW1/e1-shards.sh (the six-shard default lane; beast-3, uv 0.13.7, Python 3.13.18)"
    exit: "1 at 4e1ae32c; 1 at c59dc769"
    output: "at c59dc769: 22416 passed, 13 skipped, 8 failed, 2 errors; the 8 failures fail at main on beast-3 too, the 2 errors are the known test_public_optional pair. At 4e1ae32c, 11 more failures in test_pyrel_applications_install (the 12 MiB cap), fixed in bfc2495e"
    note: "evidence/close/default-lane.txt"
  - command: "uv run --no-sync pytest -q -m 'evidence or census' (beast-3, fresh clone)"
    exit: 1
    output: "8 failed, 145 passed, 27 errors at c59dc769; the same node ids at main 6bbbee81"
    note: "evidence/close/broad-lane.txt"
  - command: "uv run python tools/check_installed_docs.py --out <scratch>"
    exit: "0 at 4e1ae32c (one pass, extras installed); 1 at c59dc769 (two passes)"
    output: "at c59dc769 the release origin's bare pass stops at docs/how-to/share-an-ossie-ontology.md block 6 (gnd diff needs the synth extra; unchanged from main); run group by group, the other 26 extra-free groups pass on the bare wheel and bookrec passes 100 blocks with synth"
    note: "evidence/close/installed.txt"
  - command: "uv run pytest -q <the structure guards, project.md> --tb=short (clean clone of c59dc769)"
    exit: 0
    output: "872 passed, 2 deselected in 127.90s (0:02:07)"
  - command: "uv run ruff check (clean clone of c59dc769)"
    exit: 0
    output: "All checks passed!"
  - command: "uv run pytest -q -p no:randomly tests/test_ik6_walk.py tests/test_replays.py tests/test_record_induce_sessions.py tests/test_packaged_skills.py tests/test_pyrel_applications_install.py tests/test_plan_app_docs.py tests/test_documentation_tutorials.py"
    exit: 0
    output: "443 passed in 122.92s (0:02:02)"
  - command: "uv run --group docs zensical build --strict && uv run python tools/check_docs.py site"
    exit: 0
    output: "Build finished in 1.06s; 19949 local links/assets/anchors checked"
  - command: "python3 .claude/skills/process-phase/scripts/review_tool.py status .gnd-planning/milestones/induction-skill/notes/reviews/phase-IS* (clean clone of 9b69ca5f)"
    exit: 1
    output: "13 files unreviewed since their last round; format problems in the four ledgers; the retained review.md files differ from run.json by their retention edits"
    note: "evidence/close/phase-review-status.txt"
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/induction-skill/notes/induction-skill-plan.md sha256 5920218f2969d0004a38a1238f19e4b685e0f63c1feb16f69efd200ecaba8093"
    exit: "n/a -- ruling"
    output: "close ruling below; owner acceptance is separate and pending"
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\"; the full default lane"
  trigger: "the milestone close"
  reason: "run above"
evidence:
  - path: .gnd-planning/milestones/induction-skill/notes/induction-skill-plan.md
    sha256: 5920218f2969d0004a38a1238f19e4b685e0f63c1feb16f69efd200ecaba8093
  - path: .gnd-planning/milestones/induction-skill/notes/close-sweep.md
    sha256: 1142594b675692810603aee0bed9ddd4e51762ca7780d3c0d2ba256232ef2698
  - path: .gnd-planning/milestones/induction-skill/notes/close-review-disposition.md
    sha256: 996be305234985b263c2566e4bfb454039fafe8b578c662b070b013c4395cfed
  - path: .gnd-planning/milestones/induction-skill/notes/close-review-brief.md.snapshot
    sha256: 3dc1c8db79afe0c17290810884b7b4d3d2f9152cae831b2b34f5f7752b0dda69
  - path: .gnd-planning/milestones/induction-skill/notes/close-review-reader-1.md
    sha256: 445742f3dca8efdfdaf1da6dc62167a65cbd1fc386d8a6d7361067653791d7fe
  - path: .gnd-planning/milestones/induction-skill/notes/close-review-reader-2.md
    sha256: 9048e71ca3e8b2c48dba48dd63d9e782c86627d47940414638f69f62c8618f08
  - path: .gnd-planning/milestones/induction-skill/notes/close-review-reader-3.md
    sha256: e193bb16771e9c378ca91e582d9723c3cbab75a4ce2de93cf4d163d77de5fb7d
  - path: .gnd-planning/milestones/induction-skill/notes/close-review-reader-4.md
    sha256: 29cfae7ddbfb73e33cf1e29a6e2f7215aed887677d3fef95409e1300f55db9c5
  - path: .gnd-planning/milestones/induction-skill/002-phase-IS1.md
    sha256: 81b010ef6c8ca389676cc706c9706f1d764e488478070feaaa19f7531772ed5e
  - path: .gnd-planning/milestones/induction-skill/005-phase-IS2.md
    sha256: 70b885fe082086ba0ef01b912581b8c72538ae6abc4520ba178fb5274f74bb3a
  - path: .gnd-planning/milestones/induction-skill/evidence/close/owner-statements.txt
    sha256: df0b67869bcaefe0c64f6b50e7115ce3c14dbfe88de5ba456ac955e853c4fa89
  - path: .gnd-planning/milestones/induction-skill/evidence/close/installed.txt
    sha256: 0efad723d277ec90240f838e63db75bfcfbc464584ba9dbbf6d4526f71c31c69
  - path: .gnd-planning/milestones/induction-skill/evidence/close/default-lane.txt
    sha256: a5fb8b0663a904f4682230841b22b13cb06a87a3f265a2067ccc07a20ea36786
  - path: .gnd-planning/milestones/induction-skill/evidence/close/broad-lane.txt
    sha256: 67426596a2a4f143e1c18209bbaeae30b233bb2315104b07b997cfd0a569028b
  - path: .gnd-planning/milestones/induction-skill/evidence/close/phase-review-status.txt
    sha256: d7fae373ce04209d8e45e49c1427b02e72c56b8b9a3bf7fe3f343dd22f935e54
---

# Claim

The induction-skill milestone's two phases are recorded ([IS1](002-phase-IS1.md),
merged as PR 315; [IS2](005-phase-IS2.md), PR 317, not merged). The close found
and fixed three defects the phases left: the installed docs check never
installed the extra a tutorial names; two copies of the wheel cap missed the
13 MiB budget; and the learn-rules page misstated why commands were refused.
Completion predicates 1 and 3 hold with the amendments of plan §11 and with
owner acceptance still pending. Predicate 2 holds except its last clause: the
installed docs check exits 1 at a defect on main outside this milestone
(`gnd diff` needs the `synth` extra without saying so).

## Completion predicates

| Predicate | Status | Evidence |
|---|---|---|
| 1, IS1: the skill ships, routes and pins move, controls red then green, install and doctor exit 0 | holds, as amended: the IK census half of the red control never existed (plan §11 A4) | record 002; close reader 1 reproduced the red controls at `a7b2f24b` and `86961531` |
| 2, IS2: a skill prompt at every step, every recorded prompt a real recording, failures explained, claims in their recordings, the commands page the runnable walk | holds: reader 1 re-rendered all 15 replays byte for byte and found all 8 claim strings in their conversations' tool output; the page was corrected against the recordings (reader 4) and the three unshown runs are explained in `src/gnd/examples/refunds/skill-sessions/README.md` | record 005; readers 1 and 4; `c59dc769` |
| 2, last clause: "the installed-candidate docs check passes in both wheel origins" | **not met**: exit 1 in the bare pass at the Ossie how-to page. Every IS2 page passes on the bare wheel (the two origins' wheels are byte-identical); `bookrec` passes with `synth`. The failing command and page are unchanged from main | [installed.txt](evidence/close/installed.txt); plan §11 A2 |
| 3, protocol: per phase an approval, focused checks, a diff review, a refactoring review and a record; at the close the selected review, a sweep, a PR and owner acceptance | holds up to the PR; owner acceptance pending | this record; [disposition](notes/close-review-disposition.md); [sweep](notes/close-sweep.md) |

## What the close changed

- `4e1ae32c`, `1c4bc454`: the installed docs check runs each origin's
  extra-free tutorial groups on the bare wheel, and the groups whose pages
  name an extra (`run_tutorials.GROUP_EXTRAS`: `bookrec`) with exactly those
  extras; `results.json` records both passes.
- `bfc2495e`: `tools/accept_pyrel_applications_install.py` and
  `tests/test_release_preparation.py` take the 13 MiB wheel budget the owner set
  at C2. The default lane at `4e1ae32c` failed eleven cases on the old 12 MiB
  copy.
- `c59dc769`: Fable corrected the learn-rules page against the recordings;
  a README lists all nine recordings; the email scan covers them.
- `9b69ca5f` and this commit: plan §11 (amendments A1 to A4), the
  [question sweep](notes/close-sweep.md), the four
  [reader reports](notes/close-review-disposition.md) and their dispositions.

## Default and broad lanes

The six-shard default lane ran twice on beast-3 ([default-lane.txt](evidence/close/default-lane.txt)).
At `4e1ae32c` it failed eleven cases of `tests/test_pyrel_applications_install.py`
on the missed 12 MiB cap. At `c59dc769`, after `bfc2495e`, it gives 22,416
passed, 13 skipped, 8 failed and 2 errors. The 8 failures
(`test_object_type_description` 6, `test_rf2_helpers` 1, `test_v71_phase1_dates`
1) fail at main on the same machine; the 2 errors are the known
`test_public_optional` setup pair. None is this milestone's. beast-3 runs uv
0.13.7, not the 0.10.10 `release.yml` pins.

The broad lane (`-m "evidence or census"`) fails 8 and errors 27 at both the
close head and main, with the same node ids ([broad-lane.txt](evidence/close/broad-lane.txt));
none is this milestone's.

## Close review

Four local reviewer agents (plan D13 (o)), each with a different lens, over
candidate `9b69ca5f`; all four returned APPROVE_WITH_FIXES with 31 findings.
Twenty-six were fixed (one of them also carried in part), four were carried
to #318 by a comment, and one (the local paths in commit `1cbbc18d`) was
carried to the owner. The
[disposition](notes/close-review-disposition.md) lists each. **The repairs carry
no review opinion**: no second round ran. The review helper's status reports 13
files unreviewed since their last phase round ([status](evidence/close/phase-review-status.txt));
the close readers read all of them but are not the helper's instrument.

## Open questions

| Id | Question | Target |
|---|---|---|
| close-Q1 | `gnd diff` synthesizes populations by default and, without the `synth` extra, ends with an internal error; `docs/how-to/share-an-ossie-ontology.md` names no extra. A fix (a named refusal or a not-derivable row, or the page naming the extra) is outside this milestone | the owner: a proposed issue |
| close-Q2 | The distribution lane holds three edits this milestone made and never ran: `tests/test_public_distribution.py` (the wheel budget and skill count), `tests/test_release_acceptance.py` and `tests/test_release_preparation.py` (the 13 MiB budget). The lane is opt-in, and `auto=true` does not select it | the owner's selection |
| IS2-Q4 | Commit `1cbbc18d`'s local paths are on GitHub through PR 317 and the close branch | the owner |
| the rest | carried, closed or retired in the [sweep](notes/close-sweep.md) | as listed there |

## Boundary -- what this close does NOT establish

- That predicate 2's installed check passes: it exits 1 (close-Q1).
- A review opinion over the repairs made after the four reader reports.
- The distribution lane (close-Q2), Linux, or Python versions other than 3.13
  (beast-3) and 3.14 (local).
- Owner acceptance; the merge of PR 317, the close PR or the issue branches;
  any publication.
- That the skill holds on any model: six of nine conversations followed it, one
  run each (record 005).

## Delegated close ruling

Approved the milestone close under `auto=true` on 2026-11-26, from the owner's
invocation `/process-milestone induction-skill auto=true`. The ruling binds
the amended plan (SHA-256 `5920218f2969d0004a38a1238f19e4b685e0f63c1feb16f69efd200ecaba8093`), the
[sweep](notes/close-sweep.md) and the
[disposition](notes/close-review-disposition.md), whose digests are recorded
above. It accepts predicate 2's last clause as not met, at a defect outside
this milestone (close-Q1), and the pending items above. It is a delegated
ruling, not the owner's reading. The plan requires owner acceptance recorded
separately; it is pending.
