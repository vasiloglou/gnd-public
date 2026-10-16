# GND public framework

## Current status — public launch closed, 2026-10-12

The owner accepted and closed the public launch. GND is public on GitHub;
`get-nick-done==0.1.0` is published on PyPI and verified from a fresh install.
The GitHub release/tag, Claude Code and Codex marketplace plugins, installation
docs, CODEOWNERS and owner-controlled PR protections are in place.
See [the launch close](milestones/public-launch/010-public-launch-close.md) for
artifact identities, validation, owner decisions and maintenance boundaries.

Trusted Publishing setup, announcements, a hosted docs site, interaction-limit
renewal and separately activated transition/retirement remain maintenance choices.
Earlier migration/refactoring checkpoints below are historical status; this
section supersedes the earlier publication deferral.

## Historical checkpoints


Create a fresh public repository through private reviewed migration, retain the
phase development workflow, then launch the generic framework. `public-launch`
is a migration milestone, not a semantic v8.0 release. P0–P5 own launch; P6–P7
are separately activated transition/retirement work. This P1 scaffold is not the
public release. Source remains authority for staged units and migration originals.

## Public launch — Phase 4 preparation complete, 2026-10-03

The [preparation record](milestones/public-launch/003-phase-4-preparation.md) supersedes older
next-preparation status. Prepared target commit `5059dba` contains packaged
dispatch/release examples, contributor/release docs, build workflow and focused
runtime adaptations. The selected gate passes 98 tests; both wheel origins and
45 staged package/fixture controls pass. One complete independent reviewer
returned four reproduced/fixed findings; the stopped follow-up has no opinion.

**Phase 3 remains paused; Phase 4 candidate sign-off remains pending.** Resume
Phase 3 separately for final behavior-family/candidate/clean-install/CI acceptance,
then sign off those exact retained artifacts. No publication or certification
occurred; source ownership and unrelated pending work remain in place.

## Current direction — Phase 4.1, 2026-10-03

The owner approved [r4](milestones/public-launch/notes/public-launch-plan-r4-amendments.md)
and its documentation/application implementation. Phase 3 acceptance is recorded
in [004](milestones/public-launch/004-phase-3.md); earlier paused statements
above describe the preparation checkpoint. Current order: Phase 4.1, affected
candidate validation, Phase 4 sign-off, then Phase 5 publication.

## gnd-public-migration — closed, 2026-10-04

The milestone formerly named `public-launch` is renamed **gnd-public-migration**
and closed by owner instruction ([close record](milestones/public-launch/009-milestone-close.md)).
Records stay under `milestones/public-launch/`. Phase 4 is signed off by the owner on
candidate `91f12e2` ([008](milestones/public-launch/008-phase-4-signoff.md)). Its local
focused gate passes 232 tests; cloud CI after `c63b90cc3` has not run because of
GitHub billing. **Phase 5 publication is deferred**: the owner makes the repository
public manually, and PyPI, the release and announcements wait for an owner trigger.
gnd-public is now the only development repository; the source repository is to be
archived. This section supersedes the paused and pending statements above.

## code-refactoring — in progress, 2026-10-05

A behavior-preserving restructuring of `src/gnd`
([plan](milestones/code-refactoring/notes/code-refactoring-plan.md)): pin
current behavior, then break the core import cycle, consolidate copied
helpers, split the CLI into command groups, add a model query layer and
merge the session versions. Tightening that changes accepted inputs is
deferred to a successor milestone. The plan was approved on 2026-10-05
([gate](milestones/code-refactoring/003-plan-gate.md)) and updated by text-only
erratum e1 ([005](milestones/code-refactoring/005-plan-erratum.md)). **RF0** (baseline,
measurement tool, authority handoff) is recorded in
[004](milestones/code-refactoring/004-phase-RF0.md). **RF1** (characterization pins over every
surface RF2–RF8 move; 167 of 167 seeded mutations killed) is recorded in
[006](milestones/code-refactoring/006-phase-RF1.md). **Next:** RF2, consolidating
the identical helpers, run with `process-phase RF2 code-refactoring`.

## pyrel-agent-loop — opened, 2026-10-14

The owner rejected the PyRel tutorial pages shipped by `pyrel-applications`
as unpedagogical and asked for readable commands, rules shown in English, ORM
and PyRel, and a demonstration of GND with a coding assistant: what the LLM
outputs, how GND checks it, what it feeds back, how the skills are used.
[Plan r1](milestones/pyrel-agent-loop/notes/pyrel-agent-loop-plan.md) was
approved by the owner by default
([gate](milestones/pyrel-agent-loop/001-plan-gate.md)); phases PL0–PL6 run
on `codex/pyrel-agent-loop`. Real Claude Code and Codex sessions are recorded
once as evidence (PL4, owner-gated); pages replay deterministic stand-ins.

## transition-check-performance — planning, 2026-10-16

From [issue #24](https://github.com/vasiloglou/gnd-public/issues/24): GND checks
dominate a downstream application's per-step plan execution. [Draft plan r2](milestones/transition-check-performance/notes/transition-check-performance-plan.md)
covers TP0 (baseline on the reporter's exact workload), TP1 (one ModelIndex key per
public call), TP2 (fewer deep copies) and TP3 (opt-in, receipt-bound pre-state
reuse). Incremental evaluation is deferred. Defaults stay byte-identical. The
owner ruled TP-D1 to TP-D4. The plan is not reviewed or approved.
