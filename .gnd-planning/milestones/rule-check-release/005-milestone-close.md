---
milestone: rule-check-release
station: milestone-close
skill: "n/a -- repository development under process-milestone auto=false, not a gnd-solve station over a domain model"
scope: milestone-close
date: 2026-11-09
status: "DRAFT -- not ruled. Close review and closing full lane done; waiting on the owner's rulings listed at the end"
source_base: 12daa5b7
gates:
  - command: "~/rr-close/close-shards.sh closetree 25e432e43119a771a7e68d1537baa3e9c71e311b on beast-3: the full default lane, six round-robin shards"
    exit: "1 (the 2 known tests/test_public_optional.py errors only)"
    output: "18251 passed, 0 failed, 2 errors; failing-id list sha256 8261732b…9c20a"
  - command: "git diff --stat 12daa5b7 HEAD -- .github (HEAD afc5bd8f, 2026-11-09T03:27:33Z)"
    exit: 0
    output: "0 lines"
  - command: "gh api repos/vasiloglou/gnd-public/environments -q \"[.environments[].name]\""
    exit: 0
    output: "[\"github-pages\"]"
  - command: "gh run list --repo vasiloglou/gnd-public --workflow release.yml --json databaseId -q length"
    exit: 0
    output: "0"
  - command: "gh release list --repo vasiloglou/gnd-public; gh release view v0.2.0 --json isDraft,isPrerelease,assets"
    exit: 0
    output: "GND v0.2.0 (Latest) and GND v0.1.0; draft=false prerelease=false; wheel 2857045 sha256:e323c19e…69e4, sdist 2220814 sha256:f85818ea…5104, SHA256SUMS.txt 196 sha256:de14131e…72f"
  - command: "git ls-remote --tags origin"
    exit: 0
    output: "refs/tags/v0.1.0 75eda93f; refs/tags/v0.2.0 d84ad6d5, peeled 7c0f4d0e"
  - command: "GET https://pypi.org/pypi/get-nick-done/0.2.0/json"
    exit: 0
    output: "info.version 0.2.0; wheel e323c19e…69e4 2857045 17:24:56Z yanked=False; sdist f85818ea…5104 2220814 17:24:58Z yanked=False"
  - command: "GET https://pypi.org/simple/get-nick-done/ (JSON)"
    exit: 0
    output: "both 0.1.0 files and both 0.2.0 files"
  - command: "GET https://pypi.org/pypi/get-nick-done/json (releases)"
    exit: 0
    output: "['0.1.0', '0.2.0']"
  - command: "gh issue view 118 --json state,stateReason,closedAt"
    exit: 0
    output: "CLOSED COMPLETED 2026-11-09T03:21:19Z"
  - command: "git diff --stat 7c0f4d0e origin/main -- src pyproject.toml LICENSE NOTICE | tail -1 (origin/main db762f29)"
    exit: 0
    output: "18 files changed, 809 insertions(+), 214 deletions(-)"
  - command: "local CI at 7c0f4d0e (RELAYED by the session that started this one; this session has the numbers, not the logs): development.yml's regression and installed jobs, macOS, Python 3.11 (beast-3) and 3.13"
    exit: 1
    output: "each leg 17872 passed, 1 failed (tests/test_development_scaffold.py reference check: three broken planning links); release acceptance over the published files 14 passed; Ubuntu not reproduced"
  - command: "PR 140 at ac34737e: sh stale-text-check.sh token; uv run pytest -q tests/test_release_version.py tests/test_release_docs.py tests/test_marketplace_plugins.py tests/test_release_preparation.py tests/test_development_scaffold.py"
    exit: 0
    output: "no stale release-state text (15 allowlisted hits, route token, build 7c0f4d0e); 99 passed, 2 deselected"
  - command: "main 54554bf0, after the merges (RELAYED, not run by this session): sh stale-text-check.sh token; the release, docs, scaffold, RF1 pin and coverage tests and the merged PRs' own tests"
    exit: 0
    output: "stale-text check exit 0; 267 passed"
  - command: "this branch: sh .gnd-planning/milestones/rule-check-release/evidence/RR3/stale-text-check.sh token"
    exit: 0
    output: "no stale release-state text (15 allowlisted hits, route token, build 7c0f4d0e)"
  - command: "this branch: uv run pytest -q tests/test_development_scaffold.py tests/test_release_docs.py tests/test_release_version.py"
    exit: 0
    output: "82 passed, 1 deselected"
  - command: "python3 scripts/components_index.py changed --base 12daa5b7 --strict"
    exit: 0
    output: "457 file(s) differ; 0 to fix, 0 warning(s), 20 to reread -- none from this milestone (its merges change no src/)"
  - command: "codex exec --ephemeral --model gpt-6-sol --config model_reasoning_effort=\"xhigh\" --sandbox read-only --color never --skip-git-repo-check - (close review, prompt on stdin, over 71df1b99)"
    exit: 0
    output: "DISPOSITION: revise; L1-L8, all reproduced and applied (see Close review)"
  - command: "ruling: owner, close review instrument"
    exit: "n/a -- ruling"
    output: "\"One Codex reviewer\" (2026-11-09, relayed)"
  - command: "ruling: owner <approved | amended | refused> .gnd-planning/milestones/rule-check-release/005-milestone-close.md"
    exit: "n/a -- ruling, PENDING"
    output: "not given"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request"
  reason: "excluded for this milestone by the owner (RR1 spec D6, 2026-11-07); not selected at this close"
evidence:
  - path: .gnd-planning/milestones/rule-check-release/notes/rule-check-release-plan.md
    sha256: dcdab3174655038385b44fc730c663ee96f7608a961386c9780d7e8a18b56283
    note: "r2 plus the draft §12 close amendment (narrowed after review L3); the approved r2 bytes are 97a94db5…aad at c09dcbcc"
  - path: .gnd-planning/milestones/rule-check-release/001-plan.md
    sha256: 355d004fb12f5fe1550bd7becef8fc7489cee420b61f46d032c3ddeb16a4a8b7
  - path: .gnd-planning/milestones/rule-check-release/002-phase-RR1.md
    sha256: 13a0e235efc14198858cfb436969cf6e79ff1c0346837e8a7b0778d70ee22945
  - path: .gnd-planning/milestones/rule-check-release/003-phase-RR2.md
    sha256: 7ceb30324e499de754a9c8cb77898b82a4d8bdcc08d01867c089743fbf9c521b
  - path: .gnd-planning/milestones/rule-check-release/004-phase-RR3.md
    sha256: 8b0f0e867f84766a237941feb1a40d1b2d2a643bb6245131bbf6323a307842c8
  - path: .gnd-planning/milestones/rule-check-release/evidence/RR3/dossier.md
    sha256: 64035c5565d1ab0fb483f465626bb168ee14bbcf2fa2df4c6af09771830ce7cc
  - path: .gnd-planning/milestones/rule-check-release/evidence/publication/step-E-served-files.txt
    sha256: 46f0e89bd154068122deaa015572fc0ac925c473231d141f30c66d0d3118de88
  - path: .gnd-planning/milestones/rule-check-release/evidence/close/remote-state-2026-11-09.txt
    sha256: a3f844eaf0222067571a3eae06825c25bf544a8900d3ee69ec34d779d99d1047
  - path: .gnd-planning/milestones/rule-check-release/evidence/close/full-lane-closetree-25e432e4.txt
    sha256: 6c8c959f205240c6f8c09db7653d284f6db4b9ec4105234c29ac9005ed4fdfd5
  - path: .gnd-planning/milestones/rule-check-release/notes/close-codex-review.md
    sha256: b69da10c15d8028a6ee7b0ec9d2f0cd9d3d5606af82d3226235d6a5c8a47fed3
  - path: docs/release-notes.md
    sha256: 4d073050bf528803299f0eebc3c0b1d2ac6e56cd649a0f7f81cd3722dcd58a2c
  - path: docs/support.md
    sha256: 94400e63aeeb59c6818705e393a7d2ae7850f350d7bce85e2e3cb30dccf0b22b
  - path: docs/installation.md
    sha256: cbd579f4d4a4d9820407f17b865d09f37876a54169d9dcb95e27f99620295014
  - path: docs/compatibility.md
    sha256: e0eff465ef6b225cadac25648ca5550c193ecd8a43e687bfcf5680500beee688
  - path: README.md
    sha256: d84e42a258c95dfee0c994856f68d183fd2f2034241e3995604354d47b6e86d1
---

# Claim (draft)

**This record is a draft and is not ruled.** The close review (one Codex
reviewer, the owner's choice) and the closing full lane are done. The close is
final only after the owner's rulings listed at the end.

The closing full lane at main `25e432e4` exited 1 on the two known
`tests/test_public_optional.py` errors only: 18251 passed, 0 failed. That
failing-id list equals RR1's closing list (`15ea4265`), and its sha256 equals
the rule-check-adoption close's. The record is on main after `8eb4fe60`. That
commit differs from `25e432e4` only in two planning Markdown files (the PR 143
merge).

The owner merged PR 140 (the post-publication docs) as `c239ad8e`, PR 133
(this draft, the route ruling and step E) as `8a3ae7aa`, and PR 143 (the merge
facts) as `8eb4fe60`, all on 2026-11-09, relayed.

All three phases (RR1 to RR3) are on main. Each has an owner-approved spec, a
record with verbatim focused-gate output, one independent reviewer (Codex) and
an owner-merged PR (125, 130, 131). The milestone was planned to stop before
publication. The owner then asked for publication (RL-D10, below): **0.2.0 is
published.**
- PyPI received the retained `7c0f4d0e` candidate at 2026-11-08T17:24:56Z.
  The served files are byte-identical to it.
- The owner pushed tag `v0.2.0` (`d84ad6d5`, pointing to `7c0f4d0e`) and
  created the GitHub release.
- Issue 118 is closed as completed.

## Phases

| Phase | Record | Focused gate | Review (one reviewer, Codex) | PR |
|---|---|---|---|---|
| RR1 | [002](002-phase-RR1.md) | 228 passed, 1 deselected; full lane at 15ea4265: 17851 passed, 2 known errors | `revise`, 3 findings, all fixed | 125 |
| RR2 | [003](003-phase-RR2.md) | release acceptance over the retained candidate: 14 passed | spec `revise` 9; part one `revise` I1-I4; record `revise` R1-R7; all disposed | 125 (part one), 130 |
| RR3 | [004](004-phase-RR3.md) | 35 passed; stale-text check exit 0 on the patched tree | spec `revise` Q1-Q8; implementation `revise` J1-J8; all fixed | 131 |

## RL-D10: the owner's publication requests (a new decision, not phase work)

Plan §4's close row records a publication request as a new decision. Every
quote below was relayed to this session by the session that started it.

| Date | Request (quoted) | Done by | Result |
|---|---|---|---|
| 2026-11-08 | Route: "Upload saved candidate" (RL-D5, route (a)) | the owner, by hand with their own token | 0.2.0 on PyPI at 17:24:56Z (wheel) and 17:24:58Z (sdist); step E: served files byte-identical, fresh index install gives `gnd 0.2.0` ([step E](evidence/publication/step-E-served-files.txt)) |
| 2026-11-08 | "Yes, all four": tag, GitHub release, docs PR, issue 118 | as below | -- |
| 2026-11-08 | HOLD for local CI, then "Yes, resume" | the session that started this one | local CI at 7c0f4d0e (relayed gate above); its one failure was fixed in PR 137 (`c104644d`) |
| 2026-11-09 | tag `v0.2.0` | the owner (this session's push was refused by a permission check) | `d84ad6d5` → `7c0f4d0e` |
| 2026-11-09 | GitHub release | the owner ran the command this session prepared (this session's attempt was refused) | [GND v0.2.0](https://github.com/vasiloglou/gnd-public/releases/tag/v0.2.0), Latest; wheel, sdist and `SHA256SUMS.txt` attached, as for v0.1.0 |
| 2026-11-09 | docs PR | this session | [PR 140](https://github.com/vasiloglou/gnd-public/pull/140): the three RR3 patches (date 2026-11-08), then the `Unreleased:` section and the "private" fix; merged by the owner as `c239ad8e` (2026-11-09T03:47:18Z) |
| 2026-11-09 | issue 118 comment and close | the session that started this one posted this session's text | [comment](https://github.com/vasiloglou/gnd-public/issues/118#issuecomment-6731442881); closed as completed 03:21:19Z |

No announcement was made; that is a separate decision.

## Completion predicates

| # | Predicate (plan) | Evidence | Holds |
|---|---|---|---|
| 1 | Version written once; lock, manifests and notes agree; a drift test | RR1 (`tests/test_release_version.py`) | yes |
| 2 | Version-bearing files and moved tests inventoried, classified and handled by a ruled method; opt-in lanes listed as exclusions | RR1, E1, RL-D9 | yes |
| 3 | Candidate installs outside the checkout and carries every issue-118 item; 0.1.0 lacks them | RR2 (T1-T3, 0.1.0 controls) | yes |
| 4 | Release acceptance passes over the retained files, output recorded | RR2 V4: 14 passed | yes; also 14 passed over the published files (relayed) |
| 5 | Dossier written; post-publication patch prepared and not applied | RR3 | yes at RR3; the patches are now on main by PR 140 (`c239ad8e`) under RL-D10 |
| 6 | No workflow, environment, setting or PyPI configuration changed to enable publication; nothing uploaded | the read-only gates: `.github` diff empty since 12daa5b7; environments `["github-pages"]`; 0 `release.yml` runs | **proposed reading, pending the owner's §12 and close rulings**: no phase uploaded anything; the observed `.github` diff, environments and workflow runs are unchanged; repository settings and the PyPI publisher configuration are not audited; the upload, tag and release are the owner's under RL-D10 |
| 7 | Spec, verbatim gate and one reviewer per phase; every open question disposed; issue 118 left open | the three records; the close review; the sweep below | **pending**: the per-phase part holds and the close review ran. Two residuals, the fixtures-refactor target and three dossier owner checks are still the owner's (sweep). Issue 118 is closed as completed, which is the proposed §12 reading, pending ruling |

## Gate output (verbatim)

Full default lane, six shards on beast-3, at main `25e432e4`
([full-lane-closetree-25e432e4.txt](evidence/close/full-lane-closetree-25e432e4.txt)):

    closetree shard0: 4253 passed, 85 deselected in 815.99s (0:13:35)(shard exit=0)
    closetree shard1: 2296 passed, 278 deselected in 726.60s (0:12:06)(shard exit=0)
    closetree shard2: 2259 passed, 123 deselected, 2 errors in 432.54s (0:07:12)(shard exit=1)
    closetree shard3: 3574 passed, 58 deselected, 1 warning in 600.96s (0:10:00)(shard exit=0)
    closetree shard4: 2871 passed, 122 deselected in 622.32s (0:10:22)(shard exit=0)
    closetree shard5: 2998 passed, 133 deselected in 639.93s (0:10:39)(shard exit=0)
    ERROR tests/test_public_optional.py::test_base_wheel_refuses_missing_synth_extra_and_still_checks
    ERROR tests/test_public_optional.py::test_declared_synth_extra_is_seeded_and_loader_valid
    sha256 of that list: 8261732b98e252d1e17e491a8480080bafd2434fbd17f8a503aad8390ea9c20a

Compared with RR1's records ([full-lane-main-and-final.txt](evidence/RR1/full-lane-main-and-final.txt)):
- **RR1's main record (`1e63aeb5`):** the same two errors, plus the two
  timing failures that FU4 (issue 117) addressed. Neither timing test failed
  here.
- **RR1's closing record (`15ea4265`):** the same two errors only.

The range from `12daa5b7` to `25e432e4` also holds other milestones'
merges, so this compares observed failing sets, not this milestone's commits
alone. Two setup attempts failed before any test ran: the first bundle carried
no branch ref, and the second launch died when its SSH session closed. The run
above is the third, from a fresh directory.

The read-only remote gates are retained verbatim in
[remote-state-2026-11-09.txt](evidence/close/remote-state-2026-11-09.txt).

## Close review

The owner chose the instrument: "One Codex reviewer" (2026-11-09, relayed).
This replaces the plan's panel bar (§8) for the close, as at the
rule-check-adoption close.

One reviewer is one reviewer. Codex (gpt-6-sol, xhigh, read-only) reviewed the
draft at `71df1b99`, with the plan, the README, the four earlier records and
their evidence. Disposition `revise`, 8 findings, retained verbatim in
[close-codex-review.md](notes/close-codex-review.md). Each finding was
reproduced against the cited lines before it was applied. The corrected record
was not re-reviewed.

| Finding | Reproduced | Applied |
|---|---|---|
| L1 predicates 6 and 7 marked "as amended" while §12 is a draft | yes: plan §12 heading says "draft"; the record's plan-repair section says "applies only under the close ruling" | both rows now say "proposed reading, pending the owner's §12 and close rulings" |
| L2 predicate 7 said "the rest holds once the close review runs" | yes: two residuals and the fixtures target were still proposed | predicate 7 is "pending", naming what is outstanding |
| L3 "no phase ... changed anything" exceeds what was audited | yes: the gates read `.github`, environments and runs only; the dossier calls release authority "not auditable here" | predicate 6 and plan §12 now state only the observed checks and name settings and publisher configuration as not audited |
| L4 sweep omits the dossier's owner checks (action 1) | yes: dossier action 1 (ownership; 1.1 to 1.4) has no sweep row | five rows added below, each with its evidenced status |
| L5 README still said the milestone "does not publish" and issue 118 "stays open" | yes: README line 8 | rewritten as the history of the three phases, then the present state |
| L6 the close-review instrument still "PENDING" | yes | the owner's ruling is recorded here, in the gates, and in the README |
| L7 one `gate` and one `gates`; shorthand multi-check gate; no verbatim section | yes: front matter used both keys; the format requires `gates` with one entry per gate | one `gates` list, one entry per check; "Gate output (verbatim)" added; relayed results are labelled as relayed |
| L8 the close relies on current docs that it does not bind | yes: no docs in the evidence list | `docs/release-notes.md`, `docs/support.md`, `docs/installation.md`, `docs/compatibility.md` and `README.md` are bound by sha256 |

## Open-questions sweep

| Item | Raised | Disposition |
|---|---|---|
| Should `docs/support.md` name the candidate's observed profile? | plan §10 | closed: yes, one row (RR3 patch), on main by PR 140 (`c239ad8e`) |
| Should the GitHub release attach the wheel and sdist? | plan §10, RR3 | closed: the owner's release attaches the wheel, the sdist and `SHA256SUMS.txt` (RL-D10) |
| Publication route | plan RL-D5, RR3 | closed: route (a), "Upload saved candidate" |
| Tag, release, announcements | RR3 | closed: tag and release made by the owner (RL-D10). Announcements retired as outside this milestone (plan §7); none made |
| Dossier 1: does the account that uploaded 0.1.0 own `get-nick-done`? | dossier §D | **carried to the owner**: account-side, not readable by any agent. The owner's own token upload of 0.2.0 was accepted, which shows upload rights, not ownership |
| Dossier 1.1: repository review (visibility, content, history) | dossier §D | partly observed: visibility `public`, default branch `main`. A content and history review is not recorded; **carried to the owner** |
| Dossier 1.2: only the owner can publish `get-nick-done` | dossier §D | **carried to the owner**: not auditable here (dossier); no `pypi` environment or `release.yml` run exists (gates) |
| Dossier 1.3: the 0.2.0 notes record every breaking change with its migration | dossier §D | **carried to the owner**: the dossier gave starting points, not a confirmation. No record confirms completeness. A missed note can still be added to the notes on `main` |
| Dossier 1.4: never overwrite released files | dossier §D | closed as observed: the simple index still lists both 0.1.0 files (2026-11-09). They were not re-hashed |
| Dossier 2: version availability before the upload | dossier §D | closed: PyPI accepted the 0.2.0 upload |
| RR2 spec gate and FU3 on main (RL-D2) | 002 | closed: [003](003-phase-RR2.md) |
| Reconcile the notes before the build (RR2-C0) | 002 | closed: 003 V1, 0 `Unreleased` headings at `7c0f4d0e` |
| Publication-day patch (pins, `RELEASED`, compatibility) | 002, 003 | closed: on main by PR 140 (`c239ad8e`) |
| RR3 spec, dossier and patches | 003 | closed: [004](004-phase-RR3.md) |
| Deferred refactor: record version-bearing fixtures independently of the version (31 files, 7 gzip containers) | 002, carried by 003 and 004 | **carried; target pending the owner**: proposed, the milestone that prepares the release after 0.2.0, or an issue |
| Two load-sensitive timing tests | 002, carried by 003 and 004 | closed: FU4 (PR 129, issue 117 closed). Neither failed in the closing full lane |
| The 0.1.0 control downloads from PyPI on every prepare run | 003, carried by 004 | **accepted residual, proposed, pending the owner**: 0.1.0 is not yanked; if it were removed, the test fails with its hash or lookup message, which is the intended signal |
| Three pages say the repository is private | 004 | closed: on main by PR 140 (`c239ad8e`); `README.md` and the two docs are bound above |
| Dossier 3(b): "none changed since `7c0f4d0e`", observed at `25f58b5e` | close input | retired: the observation is stale (18 package-input files differ at `db762f29`), but route (a) published the retained files, so 3(b) was never used. Recorded here; the RR3 evidence is not edited |
| ROF changes on main after the candidate have no `Unreleased:` entry | close input | closed: on main by PR 140 (`c239ad8e`), "Unreleased: model identity and plain text for projected reports"; `docs/release-notes.md` is bound above |
| Patches checked only against the RR3 tree | 004 | closed: they applied cleanly on `6058c674` and rebased cleanly onto `db762f29`; the stale-text check gives exit 0 on this branch |
| Local CI's scaffold failure | RL-D10 HOLD | closed: PR 137 |
| Ubuntu profile not observed (RL-D6; local CI) | 003, local CI | **accepted residual, proposed, pending the owner**: `docs/support.md` names only observed profiles; the prepare job (`publish=false`) on GitHub would add Ubuntu, on the owner's request |
| Issue 118 | plan predicate 7 | closed as completed (RL-D10); the plan reading is §12, pending ruling |
| Close review instrument | plan §8, RL-D0 | closed: "One Codex reviewer" (owner, 2026-11-09) |

## Plan repair

Plan §12 (draft, appended 2026-11-09, narrowed after review L3) reads
predicates 6 and 7, and §4's close row, against RL-D10. The r2 wording is
kept. It applies only under the close ruling. The amended plan's sha256 is
bound above.

## Refactoring review

- No phase executed a refactor.
- One deferred refactor was raised (version-independent fixtures, RR1). It
  has a sweep row above; its target is pending the owner.
- The component index check over `12daa5b7..HEAD` lists 20 entries to
  reread. None comes from this milestone: its merges (PRs 125, 130, 131, 133,
  140 and 143) change nothing under `src/`.

## Refuted premises

- The dossier's 3(b) observation is stale; see the sweep row.
- Predicate 6 names "the public PyPI JSON listing of versions" as the remote
  check, which assumes that listing is current. On publication day it lagged:
  at 17:26Z it still listed `['0.1.0']` (cached), while the version endpoint
  and the simple index already showed 0.2.0. By 2026-11-09T03:27Z it listed
  both versions. A publication check should read the version endpoint or the
  simple index.

## Boundary: what this close does NOT establish

- One reviewer is one reviewer, and the corrected record was not re-reviewed.
- The full lane ran once, on one machine (beast-3, macOS), at `25e432e4`.
  The broad lanes (`slow_cadence`) did not run.
- The local CI and the post-merge check were run by another session; this
  record has their numbers, not their logs.
- Ubuntu, Windows and other Python versions were not observed for 0.2.0.
- PyPI ownership, publisher registration and repository settings are not
  auditable here.
- Any announcement is the owner's.

## Owner rulings at the close

Given:
- Close review instrument: "One Codex reviewer" (2026-11-09, relayed).

Still needed:
- the two proposed residuals: the 0.1.0 control's PyPI download, and no
  Ubuntu profile;
- the target of the deferred fixtures refactor;
- dossier owner checks 1, 1.1 (content and history) and 1.2, and 1.3
  (breaking changes and migrations): confirm each, or accept it as a residual;
- plan §12;
- the close ruling itself.
