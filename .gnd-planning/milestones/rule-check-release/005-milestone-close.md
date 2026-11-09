---
milestone: rule-check-release
station: milestone-close
skill: "n/a -- repository development under process-milestone auto=false, not a gnd-solve station over a domain model"
scope: milestone-close
date: 2026-11-09
status: "DRAFT -- not ruled. Waiting on the close review, the closing full-lane gate, the owner's close ruling, and the merges of PR 133 and PR 140"
source_base: 12daa5b7
gate:
  command: "PENDING: ~/close-shards/close-shards.sh <run> <sha> on beast-3, the full default lane in six shards, at the closing tree (main after PR 133 and PR 140 merge), compared with RR1's main record 1e63aeb5"
  exit: "not run"
  output: "not run; see 'Exit gates'"
gates:
  - command: "predicate 6, read-only (2026-11-09T03:27:33Z, tree afc5bd8f): git diff 12daa5b7 HEAD -- .github; environments; release.yml runs; gh release list; v0.2.0 assets; remote tags; PyPI version JSON, simple index and project JSON; issue 118 state; package inputs since 7c0f4d0e"
    exit: 0
    output: "0 lines; [\"github-pages\"]; 0; v0.2.0 (Latest) and v0.1.0; wheel e323c19e…69e4 2857045, sdist f85818ea…5104 2220814, SHA256SUMS.txt de14131e…; refs/tags/v0.2.0 d84ad6d5 -> 7c0f4d0e; PyPI 0.2.0 files equal to the candidate, not yanked; simple index lists both 0.2.0 files; ['0.1.0', '0.2.0']; CLOSED COMPLETED 2026-11-09T03:21:19Z; 18 files changed"
  - command: "local CI at 7c0f4d0e (relayed, not run by this session): development.yml's regression and installed jobs, macOS, Python 3.11 (beast-3) and Python 3.13 (this Mac)"
    exit: 1
    output: "each leg 17872 passed, 1 failed (tests/test_development_scaffold.py reference check: three broken planning links); release acceptance over the published files 14 passed; Ubuntu not reproduced"
  - command: "PR 140 at ac34737e: sh stale-text-check.sh token; uv run pytest -q tests/test_release_version.py tests/test_release_docs.py tests/test_marketplace_plugins.py tests/test_release_preparation.py tests/test_development_scaffold.py"
    exit: 0
    output: "no stale release-state text (15 allowlisted hits, route token, build 7c0f4d0e); 99 passed, 2 deselected"
  - command: "close review"
    exit: "PENDING -- instrument not selected"
    output: "not run"
  - command: "ruling: the owner's close ruling"
    exit: "PENDING"
    output: "not given"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request"
  reason: "excluded for this milestone by the owner (RR1 spec D6, 2026-11-07); not selected at this close"
evidence:
  - path: .gnd-planning/milestones/rule-check-release/notes/rule-check-release-plan.md
    sha256: 1e6e461c89d3150179c58f2551681365a72f59fbeb9656319b6d0964c02f0d9e
    note: "r2 plus the draft §12 close amendment; the approved r2 bytes are 97a94db5…aad at c09dcbcc"
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
---

# Claim (draft)

**This record is a draft and is not ruled.** The close is final only after:
the close review; the closing full-lane gate; the owner's close ruling; and
the owner's merges of PR 133 (this record, the route ruling and step E) and
PR 140 (the post-publication docs).

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
| 2026-11-08 | HOLD for local CI, then "Yes, resume" | the session that started this one | local CI at 7c0f4d0e (gates above); its one failure was fixed in PR 137 (`c104644d`) |
| 2026-11-09 | tag `v0.2.0` | the owner (this session's push was refused by a permission check) | `d84ad6d5` → `7c0f4d0e` |
| 2026-11-09 | GitHub release | the owner ran the command this session prepared (this session's attempt was refused) | [GND v0.2.0](https://github.com/vasiloglou/gnd-public/releases/tag/v0.2.0), Latest; wheel, sdist and `SHA256SUMS.txt` attached, as for v0.1.0 |
| 2026-11-09 | docs PR | this session | [PR 140](https://github.com/vasiloglou/gnd-public/pull/140): the three RR3 patches (date 2026-11-08), then the `Unreleased:` section and the "private" fix; open, not merged |
| 2026-11-09 | issue 118 comment and close | the session that started this one posted this session's text | [comment](https://github.com/vasiloglou/gnd-public/issues/118#issuecomment-6731442881); closed as completed 03:21:19Z |

No announcement was made; that is a separate decision.

## Completion predicates

| # | Predicate (plan) | Evidence | Holds |
|---|---|---|---|
| 1 | Version written once; lock, manifests and notes agree; a drift test | RR1 (`tests/test_release_version.py`) | yes |
| 2 | Version-bearing files and moved tests inventoried, classified and handled by a ruled method; opt-in lanes listed as exclusions | RR1, E1, RL-D9 | yes |
| 3 | Candidate installs outside the checkout and carries every issue-118 item; 0.1.0 lacks them | RR2 (T1-T3, 0.1.0 controls) | yes |
| 4 | Release acceptance passes over the retained files, output recorded | RR2 V4: 14 passed | yes; also 14 passed over the published files (relayed) |
| 5 | Dossier written; post-publication patch prepared and not applied | RR3 | yes at RR3; the patches are now applied in PR 140 under RL-D10 (plan §12) |
| 6 | No workflow, environment, setting or PyPI configuration changed to enable publication; nothing uploaded | the read-only checks above: `.github` diff empty since 12daa5b7; environments `["github-pages"]`; 0 `release.yml` runs | **as amended (§12)**: no phase uploaded or changed anything; the upload, tag and release are the owner's under RL-D10; publisher registration on PyPI is not auditable |
| 7 | Spec, verbatim gate and one reviewer per phase; every open question disposed; issue 118 left open | the three records; the sweep below | **as amended (§12)**: issue 118 is closed as completed after publication; the rest holds once the close review runs |

## Exit gates

- **Predicate 6, read-only, 2026-11-09T03:27:33Z.** Every line is in
  [remote-state-2026-11-09.txt](evidence/close/remote-state-2026-11-09.txt).
  The PyPI project JSON now lists `['0.1.0', '0.2.0']`; the earlier stale
  cache has cleared.
- **Local CI at `7c0f4d0e` (relayed).** Each leg: 17872 passed, 1 failed. The
  failure was `tests/test_development_scaffold.py`'s reference check: three
  broken planning links, including `../notes/phase-RR1-codex-review.md` in
  `002-phase-RR1.md`. No package input was involved. Fixed in PR 137
  (`c104644d`), merged into this branch with main. The Ubuntu leg was not
  reproduced; there is no Docker on these machines.
- **PENDING: the full default lane at the closing tree** (plan §9). Run
  `close-shards.sh` on beast-3 at main after PR 133 and PR 140 merge, and
  compare with RR1's main record (`1e63aeb5`: 17830 passed, 2 timing
  failures, 2 errors). Until it runs, this close claims no full-suite result
  for the closing tree. The local CI above was at the candidate, not here.

## Close review

**PENDING.** The plan holds the close to the panel bar (§8). The previous
close (rule-check-adoption) used one reviewer, Codex, selected by the owner
instead of the panel. The instrument is the owner's choice. Until it runs,
this record has no review opinion.

## Open-questions sweep

| Item | Raised | Disposition |
|---|---|---|
| Should `docs/support.md` name the candidate's observed profile? | plan §10 | closed: yes, one row (RR3 patch), applied in PR 140 |
| Should the GitHub release attach the wheel and sdist? | plan §10, RR3 | closed: the owner's release attaches the wheel, the sdist and `SHA256SUMS.txt` (RL-D10) |
| Publication route | plan RL-D5, RR3 | closed: route (a), "Upload saved candidate" |
| Tag, release, announcements | RR3 | closed: tag and release made by the owner (RL-D10). Announcements retired as outside this milestone (plan §7); none made |
| RR2 spec gate and FU3 on main (RL-D2) | 002 | closed: [003](003-phase-RR2.md) |
| Reconcile the notes before the build (RR2-C0) | 002 | closed: 003 V1, 0 `Unreleased` headings at `7c0f4d0e` |
| Publication-day patch (pins, `RELEASED`, compatibility) | 002, 003 | closed by PR 140 once it merges (owner) |
| RR3 spec, dossier and patches | 003 | closed: [004](004-phase-RR3.md) |
| Deferred refactor: record version-bearing fixtures independently of the version (31 files, 7 gzip containers) | 002, carried by 003 and 004 | **carried**: target is the milestone that prepares the release after 0.2.0. The owner should name it or file an issue (proposed) |
| Two load-sensitive timing tests | 002, carried by 003 and 004 | closed: FU4 (PR 129, issue 117 closed). No timing failure in the local CI at `7c0f4d0e`, which predates FU4. The closing full lane will show whether they recur |
| The 0.1.0 control downloads from PyPI on every prepare run | 003, carried by 004 | **accepted residual (proposed)**: 0.1.0 is not yanked; if it were removed, the test fails with its hash or lookup message, which is the intended signal |
| Three pages say the repository is private | 004 | closed by PR 140 (`ac34737e`) once it merges |
| Dossier 3(b): "none changed since `7c0f4d0e`", observed at `25f58b5e` | close input | retired: the observation is stale (18 package-input files differ at `db762f29`), but route (a) published the retained files, so 3(b) was never used. Recorded here; the RR3 evidence is not edited |
| ROF changes on main after the candidate have no `Unreleased:` entry | close input | closed by PR 140 (`ac34737e`), "Unreleased: model identity and plain text for projected reports", once it merges |
| Patches checked only against the RR3 tree | 004 | closed: they applied cleanly on `6058c674`, and the branch rebased cleanly onto `db762f29`; the stale-text check gives exit 0 |
| Local CI's scaffold failure | RL-D10 HOLD | closed: PR 137 |
| Ubuntu profile not observed (RL-D6; local CI) | 003, local CI | **accepted residual (proposed)**: `docs/support.md` names only observed profiles; the prepare job (`publish=false`) on GitHub would add Ubuntu, on the owner's request |
| Issue 118 | plan predicate 7 | closed as completed (RL-D10); plan §12 |

## Plan repair

Plan §12 (draft, appended 2026-11-09) reads predicates 6 and 7, and §4's
close row, against RL-D10. The r2 wording is kept. It applies only under the
close ruling. The amended plan's sha256 is bound above.

## Refactoring review

- No phase executed a refactor.
- One deferred refactor was raised (version-independent fixtures, RR1). It
  has a sweep row above with a named target.

## Refuted premises

- The dossier's 3(b) observation is stale; see the sweep row.
- Predicate 6 names "the public PyPI JSON listing of versions" as the remote
  check, which assumes that listing is current. On publication day it lagged:
  at 17:26Z it still listed `['0.1.0']` (cached), while the version endpoint
  and the simple index already showed 0.2.0. By 2026-11-09T03:27Z it listed
  both versions. A publication check should read the version endpoint or the
  simple index.

## Boundary: what this close does NOT establish

- No close review has run, and the closing full lane has not run.
- The local CI was run by another session; this session has its numbers, not
  its logs.
- Ubuntu, Windows and other Python versions were not observed for 0.2.0.
- PyPI publisher registration and account ownership are not auditable here.
- Merging PR 133 and PR 140, and any announcement, are the owner's.

## Owner rulings at the close

None yet. Needed:
- the close review instrument;
- whether to run the closing full lane after the merges;
- the residuals proposed above (the 0.1.0 control, the Ubuntu profile);
- the target of the deferred fixtures refactor;
- plan §12;
- the close ruling itself.
