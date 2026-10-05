---
milestone: gnd-public-migration
station: milestone-close
skill: "n/a -- repository milestone close"
scope: gnd-public-migration-close
date: 2026-10-04
status: closed
gate:
  command: "see 008-phase-4-signoff.md"
  exit: 0
  output: "232 passed, 1 deselected"
  note: "No new gate; the close rests on the P0-P4 records"
evidence:
  - path: 008-phase-4-signoff.md
    sha256: 58fd9b6389c9cb9f7abf71538715e675027d36c69724b461f49c19ca383a5dfb
---
# gnd-public-migration — milestone close

Closed on 2026-10-04 by owner instruction: rename the milestone, close Phase 4,
defer Phase 5, close the milestone.

## Rename

The milestone formerly called `public-launch` is now **gnd-public-migration**.
What it delivered was the migration (a fresh repository, a working runtime,
transferred coverage and a release candidate), not the launch. The directory
stays at `.gnd-planning/milestones/public-launch/`: about 145 digest-bound
manifest entries, seven test/tool files and the source-side records
cite that path, and moving it would break those citations without changing
any content. Records 001–007 keep `milestone: public-launch` in their
frontmatter as historical bytes.

## Phase disposition

| Phase | State | Record |
|---|---|---|
| P0 freeze scope | complete | [summary](notes/phase-0-summary.md); full record in the source repository |
| P1 scaffold | complete | [001](001-phase-1.md) |
| P2 runtime and package | complete | [002](002-phase-2.md) |
| P3 coverage transfer | complete | [004](004-phase-3.md) |
| P4 release candidate | complete, owner sign-off | [003](003-phase-4-preparation.md), [005](005-phase-4.1-preparation.md)–[007](007-phase-4.1-runtimes.md), [008](008-phase-4-signoff.md) |
| P5 publish and launch | **deferred** | — |
| P6–P7 transition/retirement | not part of this milestone; see below | — |

## Phase 5 deferral

Owner: the repository owner. Trigger: owner chooses to publish. The owner will
handle the visibility change manually. Before doing so, the plan's Phase 5 still
calls for:

- a scan of the full reachable history for private material;
- a candidate rebuilt from the then-current commit, since 008's artifacts were
  not retained;
- optionally, the PyPI trusted-publisher upload, a fresh install from the index
  with the intro example, a GitHub release and announcements
  ([release dossier](notes/release-dossier.md)).

Cloud CI is deferred with it until GitHub billing is restored (owner decision:
no budget now).

## Source repository

The owner intends to archive the source repository (`vasiloglou/gnd`) and
develop only in gnd-public from now on. Before closing, its unmerged branches
were checked: `claude/gracious-brattain-01b7eb` is superseded by PR #5 here;
`backup-pre-amend-6853211` is an older copy of commits already on its main
under amended hashes; `codex/public-p3-records` holds source-side copies of the
P3/P4.1 records and is pushed to its remote, so archiving preserves it. Formal
P6/P7 records (final source reconciliation, recovery check) were not produced.
The owner's decision to archive stands in for them.

## Carried

- [Carryover register](migration/obligations.md) states are unchanged.
- Version 0.1.0 remains provisional until publication.
- Cloud CI on everything after `c63b90cc3` remains unrun.
