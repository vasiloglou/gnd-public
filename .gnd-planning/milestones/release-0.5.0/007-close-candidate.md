---
milestone: release-0.5.0
station: close-candidate
scope: close-candidate
date: 2026-11-25
source_base: 75c9ef52630f980746d994f9a72348ce84d223ad
evidence:
  - path: .gnd-planning/milestones/release-0.5.0/001-plan-gate.md
    sha256: ff098b010cf4060df0227238805c7eb3803c993005cd6ddff7a1c92f84bae02a
  - path: .gnd-planning/milestones/release-0.5.0/002-phase-RW1.md
    sha256: 10160b141526c8900c3aa9f553786f6f87eda7e67054472ee31dfef9f0d509c6
  - path: .gnd-planning/milestones/release-0.5.0/003-RW2-pre-freeze.md
    sha256: f9729e4dd9f7ecc975173416d2bf7dd4f17e626ddd7bc02451b6190b6cd74818
  - path: .gnd-planning/milestones/release-0.5.0/004-phase-RW2.md
    sha256: 3b801257361ad1a537ea3003c9da7eab65cf6278e1824ed4d6dbb88cd031e7f5
  - path: .gnd-planning/milestones/release-0.5.0/005-phase-RW3.md
    sha256: 78d9e3a0bf5374a241ad670b9970cdc3eed16221d21287d5169fb66b33f63c54
  - path: .gnd-planning/milestones/release-0.5.0/006-publication.md
    sha256: c2c1b98ce8f1cb4e10c1ecb4f2febc52e4c228e6ef7e2ab33468e1053af1bd57
  - path: .gnd-planning/milestones/release-0.5.0/notes/release-0.5.0-plan.md
    sha256: 59abdb8fc2f51e7c4ac375c1ebf26efeb398512dcc56ebe18ab44410c31f349d
    note: "r6, with §15 the close's plan repairs"
  - path: .gnd-planning/milestones/release-0.5.0/notes/close-results.md
    sha256: d2f35b4ad91a22a3fba40b5c94f926f6694f0382cc274ea164828554cdc1ee96
  - path: .gnd-planning/milestones/release-0.5.0/notes/close-question-sweep.md
    sha256: 5369519a04b281211ae7ff301d024402f75d0e08ceec7491452902bc6346a1ff
  - path: .gnd-planning/milestones/release-0.5.0/evidence/close/default-lane.txt
    sha256: 1f5d48131b140fac70553127a60cb446c1937a002f209f9140aa1d30687cd952
  - path: .gnd-planning/milestones/release-0.5.0/evidence/close/remote-state.txt
    sha256: 87c15ded19f2d22174937e9d7fe5c4fe08deda6ad632caf44916ed157f071651
  - path: .gnd-planning/milestones/release-0.5.0/evidence/close/audit.txt
    sha256: 5539e99a30330bb382c129e696401c4675edd70ebdd586dccf8a6f3a2ec02a20
  - path: .gnd-planning/milestones/release-0.5.0/evidence/close/phase-review-status.txt
    sha256: af14eef43314b6ce430dba87ca8e7b84f42d7c1c4576148f4fef748eb628a721
  - path: .gnd-planning/milestones/release-0.5.0/evidence/publication/owner-statements.txt
    sha256: 5549dce1bddf818038bfbe41ce6ca4c81973545cf669cb23909063547a62ab78
  - path: .gnd-planning/milestones/release-0.5.0/evidence/close/owner-statements.txt
    sha256: c115bb8c9e85a9995cefebf95129ddaaf7b8b7fb6e3460cadb7d608e066384e9
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW2/candidate/SHA256SUMS
    sha256: fefaef011502c8b9e921fe84ba34538c1330dbda2817b4f08b334dfe82d12b64
---

# Release 0.5.0 close candidate

This is the review subject of the close. The milestone close record follows
the standard GND panel the owner selected for the close on 2026-11-23, and a
delegated close ruling. The owner asked for the close on 2026-11-25 ("close
it"). Main is at `75c9ef52`.

## What the milestone delivered

GND 0.5.0 is published. The wheel
(`c843909e6f5f676b19f06522b0e9dffe89b84421e1f7bd5610ee0494b32b0d49`) and the
sdist (`9576a57d735d54aa7cd565b52670f11feb6bf659dd75da40a868942168e8a8c0`),
built from main `85d076ba` and accepted on beast-3, are the files PyPI serves;
tag `v0.5.0` peels to `85d076ba`; the GitHub release carries both files and
their checksums; main's pages say 0.5.0 is published.

| Phase or stage | Record | Result |
|---|---|---|
| plan | [001](001-plan-gate.md) | standard panel over r1 (five of six seats); r2 approved by delegated ruling; the owner's dependency rulings in plan §11 to §14 |
| RW1 candidate content | [002](002-phase-RW1.md) | version 0.5.0 in five places; one 0.5.0 notes section headed by the Ossie relational files (the owner's choice); two E1 measurements; lane 21,998 passed, 0 failed |
| RW2 probes | [003](003-RW2-pre-freeze.md) | six installed probes with 0.4.0 controls, five families files, the 0.3.0 controls retired; two Codex rounds |
| RW2 build and acceptance | [004](004-phase-RW2.md) | freeze at `85d076ba` (lane 22,020 passed, 0 failed, 2 errors, 13 skipped); two builds with equal digests; 33 passed on beast-3; `gnd 0.5.0`; `pyrel_oracle` 345 passed, `ossie_oracle` 91 passed |
| RW3 hand-over | [005](005-phase-RW3.md) | dossier, rehearsal, remote snapshot; publication helper hardened (RC-03), token-route sentence (RC-06); two Codex rounds, one addition withdrawn |
| publication | [006](006-publication.md) | the upload, the tag, the GitHub release and the pages, each on the owner's words; the served-file comparison and fresh install ran right after the upload without a separate request, as `docs/releasing.md` requires, and 006 discloses it |

## The predicates

[close-results.md](notes/close-results.md) judges the nine predicates of the
plan, as amended by its §15, against the evidence. All nine hold, with these
limits:

- **Predicate 1** holds at the milestone's commits. Main now declares 0.5.1,
  a tag-only version the owner had cut after the publication, outside the
  milestone (plan §15, R6).
- **Predicate 2** holds with a refuted premise: E1 cannot see the tests that
  read the notes (plan §15, R1).
- **Predicate 3** is shown by a reconciliation table and review rounds, not
  by a test.
- **Predicate 9**: fifteen paths changed after the last review round that
  read them ([status](evidence/close/phase-review-status.txt)).
  [close-results.md](notes/close-results.md), "Bytes without a review
  opinion", lists each with the predicate it supports and the instrument that
  stands in for review.

| Predicate | Evidence |
|---|---|
| 1 version | 002; the release-version tests in every lane |
| 2 inventory and E1 | the RW1 spec, `evidence/RW1/e1-summary.md` |
| 3 notes | `evidence/RW1/notes-reconciliation.md`, `evidence/RW2/freeze-summary.md` |
| 4 candidate and probes | 003, 004 |
| 5 acceptance | `evidence/RW2/acceptance-summary.txt` |
| 6 dossier and rehearsal | `evidence/RW3/dossier.md`, `evidence/RW3/scratch-verification.txt` |
| 7 no phase published | `evidence/close/audit.txt` and the four snapshots |
| 8 publication | 006 and `evidence/publication/` |
| 9 specs, records, reviews, sweep | 002 to 005, the sweep |

## The close's own evidence

- **Full default lane** at main `75c9ef52`, six shards on beast-3:
  [22,057 passed, 0 failed, 2 errors, 13 skipped](evidence/close/default-lane.txt).
  The two errors are RC-02's.
- **Predicate 7 audit** ([audit.txt](evidence/close/audit.txt)): `.github/`
  is unchanged since `v0.4.0`. The [close snapshot](evidence/close/remote-state.txt)
  against the plan's baseline W4: two new tags, `v0.5.0` (publication act 4)
  and `v0.5.1` (after the milestone); one new GitHub release, v0.5.0;
  environments still `github-pages` only; no `release.yml` run; PyPI lists
  0.5.0 as latest with the accepted digests, and has no 0.5.1.
- **Question sweep** ([sweep](notes/close-question-sweep.md)): every open
  question of records 002 to 006, every plan decision and RC-01 to RC-07 is
  closed, repaired, carried with an owner, or accepted. RC-01, RC-03 and
  RC-06 are closed; RC-07 is closed by the owner's answer; RC-08 is new.
- **Plan repairs** (plan §15, R1 to R6), each naming the record that raised
  it. Repairs found at a close are plan amendments that fall under the close
  ruling (process-milestone, "Close the named milestone"); record 008 cites the
  amended plan's SHA-256 with that ruling.
- **RC-02 beside the lane:** the two errors are carried to the optional-test
  tooling owner (sweep), and the 13 skips are `tests/test_guarded_clause_exports.py`
  without `GND_PYREL_PYTHON` (close-results, "Lanes").

## Separation of authority

The owner's own acts and words are kept apart from tests and reviews:

- The owner's words for each publication act are quoted whole in
  [owner-statements.txt](evidence/publication/owner-statements.txt), and the
  words behind the close and the later 0.5.1 in
  [the close's receipt](evidence/close/owner-statements.txt); both are pinned
  above. Act 3 had no words of its own (see the publication row).
- Spec approvals and amendments are delegated rulings (auto=true), each with
  the digest of the bytes it covers. None is described as the owner's
  reading.
- The decisions the plan left to the owner were put to the owner and
  recorded as owner rulings: the headline, the added probes, `ossie_oracle`
  at the freeze, the issue links, and the literature page's version.

## What the close does not establish

- Any profile but these: installed acceptance on macOS 27.0.1 arm64 with
  Python 3.11.18 and uv 0.10.10; the default lanes on the same machine with
  Python 3.13.18 and uv 0.13.7; one fresh index install on the planning
  machine with Python 3.14.3 and uv 0.10.10.
- A RelationalAI engine run of an exported program, or the Ossie oracle's
  consumer test.
- When the owner's review of repository content and history was done: the
  owner answered "Review done" at the close, which closes RC-07, without a
  date.
- That the notes describe every user-visible change: they were reconciled
  file by file, mostly from pull-request attribution.
- That every byte is reviewed: see predicate 9 above.
- 0.5.1 as a deliverable of this milestone.
