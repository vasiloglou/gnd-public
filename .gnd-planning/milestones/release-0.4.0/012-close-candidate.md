---
milestone: release-0.4.0
station: close-candidate
scope: close-candidate
date: 2026-11-17
source_base: 9371d8e39e661d4953a228670a36411063f2aa74
evidence:
  - path: .gnd-planning/milestones/release-0.4.0/001-plan-gate.md
    sha256: 5ff5b7b8c06bf458391a05d9777b8c3ab3106cfd1cfce1e595a4a4aeaa1a64c3
  - path: .gnd-planning/milestones/release-0.4.0/003-RV1-implementation-gate.md
    sha256: cf2ceff6a69ea830b6f510ff3c0a6be73a895fd519fd3c5220d66b61ba6f0463
  - path: .gnd-planning/milestones/release-0.4.0/005-phase-RV1.md
    sha256: 8847be0c29f8c0cc0511b813592ad0fecdccb134c305fabbc84b42243e792bf3
  - path: .gnd-planning/milestones/release-0.4.0/006-RV2-spec-gate.md
    sha256: 21e70701f808f3ef3860e1115d117a32ddd35cda4164d0d177bb1bb8139629f2
  - path: .gnd-planning/milestones/release-0.4.0/008-phase-RV2.md
    sha256: 361ccfce855668c338f667dcf6206a8b9a73b879bf3c1514b77c25ae12a6cc04
  - path: .gnd-planning/milestones/release-0.4.0/009-RV3-spec-gate.md
    sha256: c1282b73e76b1eecefc5df0d70b79235cecf9f0c4462eb1480c4568561cc1f44
  - path: .gnd-planning/milestones/release-0.4.0/010-phase-RV3.md
    sha256: bc31d884b90eb00da31b3682fdb0989eb8ae0605e7b0e2b045d8bf6ffaf7d3d2
  - path: .gnd-planning/milestones/release-0.4.0/011-publication.md
    sha256: 22b3b27c6d870fc82a0eb22a752aeb1fff0b9e94e23c991dadef3c5a44d6eacd
  - path: .gnd-planning/milestones/release-0.4.0/notes/release-0.4.0-plan.md
    sha256: 23bf5d7551cb924e1e5b843453824a62f9dee4472e8f3df326f4a24061518fb2
  - path: .gnd-planning/milestones/release-0.4.0/notes/close-question-sweep.md
    sha256: f7f2b098cc5754cfe26fc4042427ac899e7729dd32c73ae90741d59c8e9d17c9
  - path: .gnd-planning/milestones/release-0.4.0/evidence/close/audit-comparison.txt
    sha256: 7b02823e77f20b6cdf81641acd1af246d2ec16c085d270908d12e92b933b2b02
  - path: .gnd-planning/milestones/release-0.4.0/evidence/close/focused.txt
    sha256: e7d5a03b76fe77ee1ca98e4d93a655b9c4a6a4c09103ba5657a73fe8e4f5f94d
  - path: .gnd-planning/milestones/release-0.4.0/evidence/close/phase-review-status.txt
    sha256: 965ef38a7063143c6b3d5baf2c18e12a21157f70f65692dcfc35389497907000
  - path: .gnd-planning/milestones/release-0.4.0/evidence/close/remote-state.txt
    sha256: 29bc87774878dbd96130b29a385ceaf9f17663dc09bd7b671fb678c4fb6754ec
  - path: .gnd-planning/milestones/release-0.4.0/evidence/close/run-shards.sh
    sha256: 6c22132442e024879f9070e956a6efa5f8aad5b74a3eab56f314eece6828cec4
  - path: .gnd-planning/milestones/release-0.4.0/evidence/close/default-lane.txt
    sha256: 4256f83a7d9410b96ed0acc328d249ae903804b8f085a2099cf6b8e8bdefd78c
---

# Release 0.4.0 close candidate

This is the review subject. The final milestone close record follows the
standard GND panel and delegated ruling. The owner requested “merge. and
close” on 2026-11-17. PR 211 merged into main at
`9371d8e39e661d4953a228670a36411063f2aa74`.

## Phase and publication result

Three mandatory phases are complete with committed specs, delegated approval
rulings, focused checks and an independent Claude Code review per phase.
The standard six-seat panel reviewed the initial plan, and its advisory
report and the delegated amended-plan ruling are separate artifacts.

| Phase | Record | Observed result |
|---|---|---|
| RV1 | [005](005-phase-RV1.md) | Candidate metadata and notes prepared, measured E1 effects repaired, 19,699 passes and two baseline setup errors in the full lane. |
| RV2 | [008](008-phase-RV2.md) | Accepted source `648cc6e0`, two byte-identical builds, 23 installed cases passed on both wheel origins. |
| RV3 | [010](010-phase-RV3.md) | Reviewed dossier and scratch-only post-publication documentation patch. |
| Publication | [011](011-publication.md) | Separately authorized PyPI upload, annotated tag, GitHub release, served-file and attachment equality, fresh index smoke and docs PR. |

All RV1 changes and acceptance probes are on main. Publication uploaded
exactly the retained files. The wheel SHA-256 is
`36288e7a918b17d14ea307b6492acfbad741755e1e83818641836452cee9ea5c`.
The sdist SHA-256 is
`2c171ccccc891333a580c3fe01c4b79ac5d3e5098af20827977a6ce455a229b6`.
Tag `v0.4.0` peels to
`648cc6e07fc6ea0e4d8791a2a33a0d005f4e106a`.
The current main product inputs match that source. The docs and release
state changed through the separately authorized PR 211.

## Exit predicates

| Predicate | Evidence and disposition |
|---|---|
| 1 Version and metadata | Published source, lock and three manifests agree at 0.4.0. Release and version tests pass. |
| 2 Inventory and E1 | All literal 0.3.0/0.3.1 files classified, affected test IDs measured before implementation and twelve generated changed outputs identified. Original fixture bytes remain in history. Excluded lanes stay explicit. |
| 3 Complete notes | Two tag-range reconciliations, LI3–LI5 and LD4–LD5 included, 0.3.1 carryover labelled and published 0.4.0 section present. |
| 4 Installed artifacts and old control | Both retained wheel origins installed outside the checkout. All five new probes and their behavior and hash-pinned public 0.3.0 availability controls passed. |
| 5 Acceptance | 23 passed in 920.19s on beast-3. |
| 6 Hand-over | Dossier bound exact identity, measured limits and owner actions. Helper invocation was first tested only in scratch. |
| 7 Preparation boundary | Baseline and hand-over snapshots agree. The closing delta matches the dated owner-authorized publication actions. Workflow diff is empty, environments remain github-pages only, and release workflow has no runs. |
| 8 Publication | Served PyPI bytes and downloaded release assets match the candidate. Fresh PyPI smoke passes. The documentation PR merged as `9371d8e3`. |
| 9 Records and review | Specs and evidence digests verify. Three phase reviews completed with fully dispositioned ledgers. Final close panel and delegated ruling follow this candidate. |

## Questions, plan repair and refactoring

The [question sweep](notes/close-question-sweep.md) lists dispositions for
every open question across records 001–011, each phase review finding, the
plan decisions and relevant predecessor carryovers. Plan §12 repairs the
refuted E1 prediction and the incomplete literature outline with provenance.
The revised plan has an exact digest in this candidate.

The three phases needed no runtime refactor. Test consumers reuse the
existing version and artifact helpers. The shared-tool lint findings and the
release helper's receipts wording coverage are assigned to their owners.

## Evidence boundaries for the close ruling

- Formal acceptance observed macOS 27.0.1 arm64/Python 3.11.18/uv 0.10.10.
  Fresh-index smoke observed macOS 26.6.2 arm64/Python 3.11.15/uv 0.10.10.
- The default lane uses its default exclusions and uv 0.13.7. Its two
  optional wheel setup errors are measured baseline errors. Repo-wide Ruff
  retains exactly 188 pre-existing shared-tool findings.
- Reviewer opinions bind their original bytes. The changed-file review
  status lists later repairs and publication edits outside those opinions.
  Current tests, the close audit and the standard close panel supply
  separate evidence.
- Account ownership and a separate human content/history audit remain
  unrecorded. The owner authorized each publication act and PyPI accepted
  the token upload. The delegated close treats this as an explicit bounded
  residual and assigns future account-level checks to the owner.
- The plan-panel raw audit archive is local and digest-bound outside Git.
  The finalized report and synthesis remain in the repository.
- Certification, external/native/provider historical lanes, announcements,
  Trusted Publishing, TestPyPI and additional platforms were outside this
  milestone's selected work.

## Closing commands and observed exits

The full [closing default lane](evidence/close/default-lane.txt) at
`9371d8e39e661d4953a228670a36411063f2aa74` completed with 19,699 passes,
13 skips, and the two baseline optional-wheel setup errors. The six shard
exits were 1, 0, 0, 0, 0, 0. It ran before this close review.

The close-focused command selected release-version, release-text and
development-scaffold tests under the default filter. It exited 0 with
159 passed and 1 deselected. The current publication text check exited 0.
The remote audit and digest-comparison script exited 0. Full Ruff exited 1
with the exact 188 baseline diagnostics. This milestone's close changes
planning and evidence only.
