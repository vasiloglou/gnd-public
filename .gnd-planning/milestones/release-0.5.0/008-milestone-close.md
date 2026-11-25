---
milestone: release-0.5.0
station: "milestone close"
skill: process-milestone
scope: milestone-close
date: 2026-11-25
source_base: 75c9ef52630f980746d994f9a72348ce84d223ad
gates:
  - command: "bash e1-shards.sh 75c9ef52630f980746d994f9a72348ce84d223ad base (beast-3, six default-lane shards, clean clone)"
    exit: "1, 0, 0, 0, 0, 0"
    output: "22,057 passed, 0 failed, 2 errors, 13 skipped"
    note: "shard 0's exit is the two RC-02 setup errors of tests/test_public_optional.py; the 13 skips are tests/test_guarded_clause_exports.py without GND_PYREL_PYTHON"
  - command: "read-only audit: git diff v0.4.0 origin/main -- .github; git ls-remote origin; gh release list; gh api .../environments; gh run list --workflow release.yml; the PyPI JSON API"
    exit: 0
    output: ".github unchanged; new tags v0.5.0 and v0.5.1 only; new release v0.5.0 only; environments github-pages only; no release.yml run; PyPI latest 0.5.0 with the accepted digests, no 0.5.1"
  - command: "uv run python tools/run_gnd_review_panel.py .gnd-planning/milestones/release-0.5.0/evidence/close-panel/review-request.json --out <scratch>/panel-run --reviewer-timeout 1500 --overall-timeout 1800 (disposable clone at d1da80bf)"
    exit: 0
    output: "quorum-established: 5 of 6 seats (claude, codex, qwen, gemini, glm); kimi nonzero; effort xhigh"
  - command: "uv run gnd review finalize <scratch>/panel-run <scratch>/synthesis.json --out <scratch>/PANEL-REVIEW.md"
    exit: 0
    output: "3 agreed groups, 7 divergent concerns, 6 prioritized fixes"
  - command: "ruling: owner answered 'Review done' to the close's question on the content and history review (RC-07), 2026-11-25"
    exit: "n/a -- ruling"
    output: "settles the close panel's one blocking concern; the answer carries no date"
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/release-0.5.0/notes/release-0.5.0-plan.md sha256 59abdb8fc2f51e7c4ac375c1ebf26efeb398512dcc56ebe18ab44410c31f349d"
    exit: "n/a -- ruling"
    output: "plan r6: the close's plan repairs R1 to R6 in section 15"
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/release-0.5.0/007-close-candidate.md sha256 8c6b0e2ceb6eff3c53b798734ef0d58d69af7bc0f5e2c734ac16e321985f7647"
    exit: "n/a -- ruling"
    output: "the milestone is closed; see Close ruling"
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "not run"
  reason: "not selected by the plan for the close; pyrel_oracle and ossie_oracle ran at the freeze commit (004)"
evidence:
  - path: .gnd-planning/milestones/release-0.5.0/007-close-candidate.md
    sha256: 8c6b0e2ceb6eff3c53b798734ef0d58d69af7bc0f5e2c734ac16e321985f7647
    note: "after the panel's repairs; the panel read 039e7ab5...6376 at d1da80bf"
  - path: .gnd-planning/milestones/release-0.5.0/notes/release-0.5.0-plan.md
    sha256: 59abdb8fc2f51e7c4ac375c1ebf26efeb398512dcc56ebe18ab44410c31f349d
  - path: .gnd-planning/milestones/release-0.5.0/notes/close-results.md
    sha256: d2f35b4ad91a22a3fba40b5c94f926f6694f0382cc274ea164828554cdc1ee96
  - path: .gnd-planning/milestones/release-0.5.0/notes/close-question-sweep.md
    sha256: 5369519a04b281211ae7ff301d024402f75d0e08ceec7491452902bc6346a1ff
  - path: .gnd-planning/milestones/release-0.5.0/evidence/close-panel/review-request.json
    sha256: 9b396b9460a832856b940d159957f6f573f387591f69fbd1e9ef47694704bfb4
  - path: .gnd-planning/milestones/release-0.5.0/evidence/close-panel/synthesis.json
    sha256: 4d5bb330f1a451c7338ac33d55f6ed326d1e42e7ca5384366b51bc82c984c171
    note: "binds the panel run.json by sha256 ee6f217a...ce6b; the run directory is retained outside the repository. The finalize output's synthesis_sha256 (1db652f2...b9b1) is its digest of the parsed document, not of these bytes"
  - path: .gnd-planning/milestones/release-0.5.0/evidence/close-panel/PANEL-REVIEW.md
    sha256: a2caf2bddb85a1e13878174394efdaa97182f9a67aea9fe105b0bb6a5259c3b6
  - path: .gnd-planning/milestones/release-0.5.0/evidence/close-panel/disposition.md
    sha256: c8da22a034f415f5d0e0d715ce36ed2a8bd7c52ad1cbd39c27833c6b5a2336ac
  - path: .gnd-planning/milestones/release-0.5.0/evidence/close/owner-statements.txt
    sha256: c115bb8c9e85a9995cefebf95129ddaaf7b8b7fb6e3460cadb7d608e066384e9
  - path: .gnd-planning/milestones/release-0.5.0/evidence/publication/owner-statements.txt
    sha256: 5549dce1bddf818038bfbe41ce6ca4c81973545cf669cb23909063547a62ab78
  - path: .gnd-planning/milestones/release-0.5.0/evidence/close/default-lane.txt
    sha256: 1f5d48131b140fac70553127a60cb446c1937a002f209f9140aa1d30687cd952
  - path: .gnd-planning/milestones/release-0.5.0/evidence/close/remote-state.txt
    sha256: 87c15ded19f2d22174937e9d7fe5c4fe08deda6ad632caf44916ed157f071651
  - path: .gnd-planning/milestones/release-0.5.0/evidence/close/audit.txt
    sha256: 5539e99a30330bb382c129e696401c4675edd70ebdd586dccf8a6f3a2ec02a20
  - path: .gnd-planning/milestones/release-0.5.0/evidence/close/phase-review-status.txt
    sha256: af14eef43314b6ce430dba87ca8e7b84f42d7c1c4576148f4fef748eb628a721
---

# Milestone close: release-0.5.0

## Close ruling

> **Delegated approval (auto=true), 2026-11-25.** Authority: the owner's
> "Release 0.5.0" request and selection of delegated approval for this
> milestone on 2026-11-23, and the owner's "close it" of 2026-11-25
> ([receipt](evidence/close/owner-statements.txt)). Approves the close
> candidate at SHA-256 `8c6b0e2c…7647` and plan r6 at SHA-256
> `59abdb8f…349d`, whose §15 repairs fall under this ruling. Accepts the
> three phases, the publication (006) and the sweep's dispositions, subject
> to the close panel's dispositions. Review: the standard GND panel the owner
> selected for the close, one round, five of six seats. **The milestone is
> closed.** This ruling is separate from the lanes and the advisory panel,
> and it is not the owner's reading of the candidate. The owner's own words
> in the close are the request and the answer on RC-07, both quoted in the
> receipt.

## What the milestone delivered

GND 0.5.0 is on PyPI (wheel `c843909e…0d49`, sdist `9576a57d…a8c0`, the
files accepted on beast-3), tagged `v0.5.0` on `85d076ba`, with a GitHub
release and published pages. Three phases (RW1, RW2, RW3) and the
publication stage, each with its record: 002 to 006. The
[close candidate](007-close-candidate.md) has the phase table and the
predicate map.

## Completion predicates

[close-results.md](notes/close-results.md) judges all nine against the
evidence. All nine hold, with these limits:

- **Predicate 1** at the milestone's commits; main now declares 0.5.1, a
  tag-only version cut after the publication, outside the milestone
  (plan §15, R6).
- **Predicate 2** with a refuted premise: E1 cannot see the tests that read
  the notes (R1).
- **Predicate 3** by a reconciliation table and review rounds, not a test.
- **Predicate 9**: fifteen paths changed after the last review round that
  read them; close-results lists each with the instrument in its place.

## Close review

The standard GND panel, run from a disposable clone of `d1da80bf` with the
panel sources equal to that commit. Five of six seats returned schema-valid
responses at effort xhigh; Kimi's seat exited nonzero. Codex blocked; Claude,
Qwen, Gemini and GLM asked for revision. Fourteen concerns: three agreed
groups and seven single-seat concerns
([report](evidence/close-panel/PANEL-REVIEW.md),
[dispositions](evidence/close-panel/disposition.md)).

- **The blocking concern** (codex): the plan put the owner's review of
  repository content and history before the upload, and it was not stated.
  Asked at the close, the owner answered "Review done". RC-07 is closed on
  that answer. The answer carries no date, so this record does not show that
  the review preceded the upload.
- **The rest** were reproduced and fixed in the candidate, close-results, the
  sweep and a new close receipt: act 3's wording, the unreviewed-byte list,
  the pinning of the owner's words, the lanes' errors, skips and profiles,
  the repairs' authority, a predicate map, and RW-D0's wording.
- **No panel round read the repaired bytes.** One round was run, as for the
  0.4.0 close.

## Plan repair

Plan r6 appends §15, six repairs (R1 to R6), each naming the record that
raised it; r5's text stays above. They are approved with the close ruling.

## Refuted premises

Plan §15 lists them: E1 and the notes' readers (R1); the RW2 size estimate
(R5); the publication helper's paragraph pass (R4). The owner's rulings
changed the headline and the probes (R2, R3).

## Open-questions sweep

[close-question-sweep.md](notes/close-question-sweep.md): every open
question of records 002 to 006, every plan decision and the carried register.
Closed: RC-01, RC-03, RC-06 and RC-07. Carried with an owner: RC-02 (the two
optional-wheel setup errors), RC-04, RC-05, the new RC-08 (the publication
check reads lines), the `gnd flatten` file-name wording, the shared Markdown
reader's line separators, the Ossie oracle root's durability, and the
owner's `~/.pypirc` permissions. Accepted: the local scaffold-guard failure,
the Ossie oracle root's origin, act 3 without a separate request, no issue
comments, no RelationalAI engine run, and no Ubuntu profile.

## Gate output (verbatim)

    Shard 0 exit 1
    ERROR tests/test_public_optional.py::test_base_wheel_refuses_missing_synth_extra_and_still_checks
    ERROR tests/test_public_optional.py::test_declared_synth_extra_is_seeded_and_loader_valid
    2973 passed, 183 deselected, 2 errors in 608.68s (0:10:08)
    Shard 1 exit 0
    4350 passed, 77 deselected in 731.72s (0:12:11)
    Shard 2 exit 0
    3282 passed, 214 deselected, 1 warning in 568.90s (0:09:28)
    Shard 3 exit 0
    3991 passed, 13 skipped, 222 deselected in 580.82s (0:09:40)
    Shard 4 exit 0
    4341 passed, 126 deselected in 970.11s (0:16:10)
    Shard 5 exit 0
    3120 passed, 228 deselected in 461.28s (0:07:41)

    {"advisory":true,"agreed_concern_count":3,"command":"review finalize","divergent_concern_count":7,"gnd_version":"0.5.1","outcome":"quorum-established","prioritized_fix_count":6,"quorum_met":true,"required_successes":3,"run_sha256":"ee6f217adcd1e9250f93a80ef314aba41a25a55db495f7e606687fdf3eefce6b","successful_reviewer_ids":["claude","codex","qwen","gemini","glm"],"synthesis_sha256":"1db652f26f275cf66158ffcd50c24db0f1fe8b0831d12ea571a0918602fba9b1"}

## Refactoring review

None in the close: it changed planning records only.

## Boundary -- what this close does NOT establish

- Any profile but those observed: acceptance on macOS 27.0.1 arm64 with
  Python 3.11.18 and uv 0.10.10; the default lanes on the same machine with
  Python 3.13.18 and uv 0.13.7; one fresh index install with Python 3.14.3.
- A RelationalAI engine run, or the Ossie oracle's consumer test.
- When the owner's content and history review was done.
- That the notes describe every user-visible change beyond the
  reconciliation table and the review rounds.
- A review opinion on the bytes changed after the last review that read
  them, among them the close panel's repairs.
- 0.5.1 as a deliverable of this milestone.
