# GND public framework

## Current status — public launch closed, 2026-10-12

This section records the 0.1.0 launch. The current release and the open
work are in [Roadmap after 0.4.0](#roadmap-after-040--planned-2026-11-21).

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

## transition-check-performance — closed, 2026-10-17

From [issue #24](https://github.com/vasiloglou/gnd-public/issues/24). This milestone
cut GND's per-step check cost on a downstream application's plan workload with
results unchanged. On the reporter's 13-call workload:

- **TP1** computes one ModelIndex key per public call.
- **TP2** shares fact-type rows with internal readers instead of copying them.
- **TP3** adds opt-in, receipt-bound pre-state reuse (25 → 19 checker runs).

GND time fell by about a third on the default path and by about 42% with receipts.
Incremental evaluation is carried to a successor milestone. See the
[close record](milestones/transition-check-performance/006-milestone-close.md).


## incremental-evaluation — locally closed, 2026-10-20

Six phases IE0–IE5 deliver explicit in-process EvaluationSession reuse, validated
host observations, bounded separate feedback and private receipt detachment.
The frozen reporter replay preserves full payload/exit/branch/ordered calculation
parity and reduces derivation bodies4878→179, but median wall time grows5.83→6.79s
against receipts. No elapsed speedup is established. Four independent local close
readers returned close-with-carryovers. [009 close record](milestones/incremental-evaluation/009-milestone-close.md)
and its separate delegated acceptance bind the local result under the owner's
named auto delegation. [PR33](https://github.com/vasiloglou/gnd-public/pull/33)
contains the isolated topic work. Performance bookkeeping and reporter-owned
547-program downstream acceptance remain explicit follow-ups; no date, merge,
publication or certification is inferred. Earlier milestone entries retain their
historical scope.

### Incremental-evaluation IE6 follow-up — locally closed, 2026-10-20

The owner reopened the milestone for a seventh phase. IE6 reuses conservative
immutable policy-footprint summaries and reduces scalar/container accounting
overhead while preserving live signature hashing, clone isolation and caps.
The final balanced pre-IE6/current comparison observes session median reductions
of about 6% / 17% / 6% on reporter/course/localized controls; all session medians
remain slower than full evaluation with receipts. Small shared-host samples
establish no general or 547-program downstream speedup. The 486-test focused
gate, current ordered parity oracle, installed Python3.11 candidate smoke and
Astra review/confirmation are recorded in
[011](milestones/incremental-evaluation/011-phase-IE6.md).
Four renewed local close opinions and a separate delegated exact-byte ruling
support [012](milestones/incremental-evaluation/012-milestone-close.md).
The [successor sweep](milestones/incremental-evaluation/notes/IE6-close-question-sweep.md)
preserves all prior questions and names remaining framework/reporter owners.
[PR33](https://github.com/vasiloglou/gnd-public/pull/33) contains all seven phases;
no merge, publication or certification is authorized by this local close.

## induced-knowledge — closed, 2026-10-27

Planning for [issue #34](https://github.com/vasiloglou/gnd-public/issues/34):
let a host with real labelled populations turn them into reviewed model
knowledge ([plan](milestones/induced-knowledge/notes/induced-knowledge-plan.md)).

Six phases: IK1 object-type descriptions, IK2 induced provenance and admission,
IK3 measure over host-labelled populations, IK4 constraint discovery, IK5 an ILP
bridge, IK6 an end-to-end example and docs.

Request 2 is proposed separately in
[PR35](https://github.com/vasiloglou/gnd-public/pull/35) (open).

Review history:
- The owner selected four local reviewer agents (D7).
- Round 1 reviewed r1.
- The owner accepted its repairs and D8–D13.
- Round 2 confirmed r2, and review stopped by the declared convergence rule.
  See the [round-2 disposition](milestones/induced-knowledge/notes/plan-review-r2-disposition.md).
- The owner confirmed D12 and directed the text repairs as r3, with no further
  review round.
- On 2026-10-24 the owner ruled D1–D6 and D14 (the description becomes a JSON
  object with fixed core keys plus extras); r4 records them, unreviewed.

**Closed and accepted, 2026-10-27.** The owner approved plan r4 on
2026-10-24 ([001](milestones/induced-knowledge/001-plan-gate.md)). Phases IK1–IK6
and IK4-Q2 shipped object-type descriptions, `induced` provenance, `gnd measure
--labels`, `gnd discover`, the ILP bridge, evolve over reference populations
and the refunds walk. Four local readers reviewed the close
([012](milestones/induced-knowledge/012-milestone-close.md)), and the owner
ruled CD1–CD5 ([011](milestones/induced-knowledge/011-owner-decisions-close.md))
and accepted the close ([013](milestones/induced-knowledge/013-owner-acceptance.md),
PR #45). The evolve-loading follow-up merged as PR #47
([014](milestones/induced-knowledge/014-followup-evolve-loading.md)), and the
host-path sanitization of older evidence as PR #46.

The carried rows and their targets are in records 012 and 014.

## model-growth-guardrails and composition-and-type-induction — planned, 2026-11-03

Two milestones from the GR-T9..T15 requests (issues #72–#78). The first,
[model-growth-guardrails](milestones/model-growth-guardrails/README.md),
covers public rule rendering, an additive-only evolve policy, a
duplicate-shape report, extraction guidelines and an unattended
model-from-text mode. The second,
[composition-and-type-induction](milestones/composition-and-type-induction/README.md),
covers several anchors per fact role, composing populations with lineage,
witness lineage and fact-type proposals in discover; its CT4 waits on the
first milestone's MG2 and MG3. Both plans are at r3 after two four-reader
review rounds (the second stopped by the declared stop rule; r3 carries no
review opinion). The owner approved both plans at r3 on 2026-11-03 `(a1)`.
MG1 (public rule rendering, #72) is implemented and recorded in
[002-phase-MG1.md](milestones/model-growth-guardrails/002-phase-MG1.md).

## literature-identity, literature-interop and literature-depth — planned, 2026-11-14

Three milestones from [issue #193](https://github.com/vasiloglou/gnd-public/issues/193),
on sense-aware literature ontologies. The partition has one home:
[literature-identity plan §1.1](milestones/literature-identity/notes/literature-identity-plan.md#11-partition-of-issue-193).

- [literature-identity](milestones/literature-identity/README.md) has the full
  plan r1 and the LI0 draft spec. It covers parts 9 and 1–4.
- [literature-interop](milestones/literature-interop/README.md) is an outline
  covering part 5.
- [literature-depth](milestones/literature-depth/README.md) is an outline
  covering parts 6–8. Part 10 is deferred.

The owner approved literature-identity plan r3 on 2026-11-15 ([plan gate](milestones/literature-identity/001-plan-gate.md)), with D1–D9 as proposed. Review stopped after round 2, and the bar was not met in that round. The two outline plans are not approved. LI0 (#193 part 9) is implemented and recorded ([003](milestones/literature-identity/003-phase-LI0.md)). LI1 (#193 part 1), the literature regression corpus and its staged assurance report, is implemented and recorded ([006](milestones/literature-identity/006-phase-LI1.md)).

LI0–LI5 are implemented and merged. The [fresh independent reserve](milestones/literature-identity/031-phase-LI5-independent-reserve.md)
met the L1 scoring threshold. Literature-identity [closed on 2026-11-15](milestones/literature-identity/035-milestone-close.md)
after six valid responses in its renewed close review. The two successor outlines keep their own gates.

## Roadmap after 0.4.0 — planned, 2026-11-21

GND 0.4.0 is published, and its milestone closed on 2026-11-17
([close record](milestones/release-0.4.0/014-milestone-close.md)). It is the
latest release, which supersedes the 0.1.0 line under "Current status" above.
Every milestone an earlier section calls planned has since closed:
model-growth-guardrails, composition-and-type-induction, literature-interop and
literature-depth each have a milestone-close record in their folders.

Six issues were open on 2026-11-21.
[#179](https://github.com/vasiloglou/gnd-public/issues/179) was already
delivered by guarded-rule-authoring GA1
([phase record](milestones/guarded-rule-authoring/003-phase-GA1.md),
[close](milestones/guarded-rule-authoring/008-milestone-close.md)) and shipped
in 0.4.0; it is closed. The other five are planned below. Each milestone is an
outline r1: not reviewed and not approved. `start-milestone` writes its full
plan and first spec, and the owner approves the plan before any code. Each
outline's §1 maps every issue request to the phase that discharges it.

| Order | Work | Issues | Phases |
|---|---|---|---|
| any time | [Maintenance: evolve and the unattended-growth sources](maintenance/2026-11-21-evolve-constraint-sources/README.md) | [#218](https://github.com/vasiloglou/gnd-public/issues/218) | One fix, after the owner rules (a) widen rule D-12 ([its home](../src/gnd/skills/gnd-orm-core/references/provenance-and-modality.md#evolve-admission-d-12)) or (b) change the growth document |
| 1 | [include-root-routes](milestones/include-root-routes/README.md) | [#217](https://github.com/vasiloglou/gnd-public/issues/217), [#214](https://github.com/vasiloglou/gnd-public/issues/214) item 1 | IR1 judgments on include roots, IR2 flattening outside extract, IR3 PyRel export of include roots |
| 2 | [pyrel-rules-coverage](milestones/pyrel-rules-coverage/README.md) | [#214](https://github.com/vasiloglou/gnd-public/issues/214) items 2–4 and its quantity-fixture case | RP1 external uniqueness, RP2 anchored projection, RP3 `Number`, RP4 role-scoped value constraints, RP5 literature end to end |
| 3 | [literature-host-interfaces](milestones/literature-host-interfaces/README.md) | [#216](https://github.com/vasiloglou/gnd-public/issues/216), [#215](https://github.com/vasiloglou/gnd-public/issues/215) | LH1 producer protocol over caller inputs, LH2 replay of a live run, LH3 generic admission, LH4 admission policy |

#214 lists four items under "What would unblock it": item 1 is IR3, items 2–4
are RP1–RP3.

Status, 2026-11-22: milestones 1 and 2 are closed and merged.
include-root-routes merged as
[PR #220](https://github.com/vasiloglou/gnd-public/pull/220)
([close](milestones/include-root-routes/005-milestone-close.md)), and
pyrel-rules-coverage as
[PR #223](https://github.com/vasiloglou/gnd-public/pull/223)
([close](milestones/pyrel-rules-coverage/007-milestone-close.md)). Neither is
released. Milestone 3 and the maintenance pass remain planned.

Why this order: #217 has no workaround; #214 blocks a downstream query layer
but the default export of a flat model works; #215 and #216 have working host-side
workarounds. The maintenance pass is independent: no milestone waits for its
ruling, and it ships whenever the ruling is made.

Dependencies: milestones 1 and 2 both edit `export/pyrel_rules.py`, so they
never have two writers at once: one works while the other waits, or the second
rebases on the first's merged change. RP1–RP4 may start before
include-root-routes closes; RP5's include-root cases need IR3 merged.
Milestone 3 is independent of both: RP5 exports packaged models and uses none
of its interfaces. Milestones 1 and 2 widen accepted inputs and together suit a
0.5.0 release; the maintenance fix may ship earlier.

Open owner decisions are listed in each plan's §5 and, for the maintenance
pass, in its "Ruling needed" table. Work handed to another assistant or
machine carries a hand-off note in `.gnd-planning/handoffs/`, written with the
dev-handoff skill and read with dev-takeover. The reviews of this roadmap are
in `reviews/pr-219-r2/` and `reviews/pr-219-panel/`.

### Added 2026-11-22: reviewed-vocabulary-growth

Two issues were filed after this roadmap was written:
[#221](https://github.com/vasiloglou/gnd-public/issues/221) (`gnd check` is
superlinear in the number of object types) and
[#222](https://github.com/vasiloglou/gnd-public/issues/222) (unattended
growth cannot start from a reviewed vocabulary).
[reviewed-vocabulary-growth](milestones/reviewed-vocabulary-growth/README.md)
plans both, and proposes to carry #218 with them in place of the maintenance
pass above (its decision D1; the pass stays as written until the owner
rules). Plan r1 and the VG1 draft spec are written; neither is reviewed or
approved.

| Order | Work | Issues | Phases |
|---|---|---|---|
| 4 | [reviewed-vocabulary-growth](milestones/reviewed-vocabulary-growth/README.md) | #221, #222, #218 (proposed) | VG1 checker cost in object types, VG2 evolve sources, VG3 an unattended root that includes a reviewed model, VG4 growth rounds on it, VG5 example, pages and replies |

It is independent of literature-host-interfaces: the two share no source
file. VG1 has no workaround for the reporter (265.74 s at 1,000 extra object
types) and needs no ruling beyond its plan gate, so it can run first.
