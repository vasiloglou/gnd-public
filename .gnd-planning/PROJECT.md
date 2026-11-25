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

## code-refactoring — closed, 2026-11-25

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

**Closed 2026-11-25** ([019](milestones/code-refactoring/019-milestone-close.md)): RF0 to RF9
recorded; closed by the owner on candidate
[018](milestones/code-refactoring/018-close-candidate.md) r2, with predicate 3 not met for five
helper groups accepted as residuals. The text above is the status of 2026-10-05.

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
| any time | [Maintenance: evolve and the unattended-growth sources](maintenance/2026-11-21-evolve-constraint-sources/README.md) | [#218](https://github.com/vasiloglou/gnd-public/issues/218) | Superseded on 2026-11-23: the owner ruled that reviewed-vocabulary-growth carries #218 as VG2, and ruled (a), widen rule D-12 ([its home](../src/gnd/skills/gnd-orm-core/references/provenance-and-modality.md#evolve-admission-d-12)) |
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

Outside this roadmap, [aggregate-count-certificates](milestones/aggregate-count-certificates/README.md)
delivered [#193](https://github.com/vasiloglou/gnd-public/issues/193) part 10,
which the literature-depth outline had deferred. It closed by delegated ruling
on 2026-11-16 ([close](milestones/aggregate-count-certificates/006-milestone-close.md))
and merged on 2026-11-22 as
[PR #204](https://github.com/vasiloglou/gnd-public/pull/204), after its branch
integrated `main` ([record](milestones/aggregate-count-certificates/007-main-integration.md)).
It is not released.

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
plans both, and carries #218 with them in place of the maintenance pass
above (its decision D1, ruled by the owner on 2026-11-23). Plan r1 and the
VG1 draft spec were written on 2026-11-22. The owner approved plan r4 on
2026-11-23 ([plan gate](milestones/reviewed-vocabulary-growth/001-plan-gate.md)); the
[status of 2026-11-23](#open-issues-on-2026-11-22--roadmap-update) says what
reviewed it.

| Order | Work | Issues | Phases |
|---|---|---|---|
| 4 | [reviewed-vocabulary-growth](milestones/reviewed-vocabulary-growth/README.md) | #221, #222, #218 | VG1 checker cost in object types, VG2 evolve sources, VG3 an unattended root that includes a reviewed model, VG4 growth rounds on it, VG5 example, pages and replies |

It is independent of literature-host-interfaces: the two share no source
file. VG1 has no workaround for the reporter (265.74 s at 1,000 extra object
types) and needs no ruling beyond its plan gate, so it can run first.

## Open issues on 2026-11-22 — roadmap update

Ten issues are open. Five were filed after the roadmap above was written:
#221 and #222 on 2026-11-21, and #226, #227 and #228 on 2026-11-22. This
section gives every open issue a home and an order. It replaces nothing above:
the milestones the 0.4.0 roadmap planned keep their outlines. The two new
milestones were outlines r1 on 2026-11-22; since 2026-11-23 each has a full
plan r2 and a first draft spec, not reviewed and not approved.

| Issue | What it asks | State | Home |
|---|---|---|---|
| [#214](https://github.com/vasiloglou/gnd-public/issues/214) | PyRel rules programs for literature-style models | Closed 2026-11-23: on `main` (PRs 220 and 223), not released | Ships in the 0.5.0 release |
| [#217](https://github.com/vasiloglou/gnd-public/issues/217) | Judging a temporal include root | Closed 2026-11-23: on `main` (PR 220), not released | Ships in the 0.5.0 release |
| [#221](https://github.com/vasiloglou/gnd-public/issues/221) | `gnd check` cost in the number of object types | Delivered on `main` 2026-11-23 (PR 239), not released; milestone closed ([close](milestones/reviewed-vocabulary-growth/007-milestone-close.md)) | [reviewed-vocabulary-growth](milestones/reviewed-vocabulary-growth/README.md) VG1 |
| [#218](https://github.com/vasiloglou/gnd-public/issues/218) | `evolve` and the growth document disagree on constraint sources | Delivered on `main` 2026-11-23 (PR 240), not released; milestone closed ([close](milestones/reviewed-vocabulary-growth/007-milestone-close.md)) | [reviewed-vocabulary-growth](milestones/reviewed-vocabulary-growth/README.md) VG2, in place of the [maintenance pass](maintenance/2026-11-21-evolve-constraint-sources/README.md) |
| [#222](https://github.com/vasiloglou/gnd-public/issues/222) | Unattended growth from a reviewed vocabulary | Delivered on `main` 2026-11-23 (PR 240), not released; milestone closed ([close](milestones/reviewed-vocabulary-growth/007-milestone-close.md)) | [reviewed-vocabulary-growth](milestones/reviewed-vocabulary-growth/README.md) VG3–VG5 |
| [#228](https://github.com/vasiloglou/gnd-public/issues/228) | A growth round costs time in proportion to the whole model | Plan r2 and GO1 draft spec, not reviewed, not approved | [growth-round-outcomes](milestones/growth-round-outcomes/README.md) GO1 |
| [#227](https://github.com/vasiloglou/gnd-public/issues/227) | Growth rounds add almost nothing: whole-proposal outcomes, restated replies, no diagnostic | Plan r2, not reviewed, not approved; waits for rulings | [growth-round-outcomes](milestones/growth-round-outcomes/README.md) GO2–GO5 |
| [#216](https://github.com/vasiloglou/gnd-public/issues/216) | A public producer protocol for the reading example | Plan r6 approved 2026-11-23; the LH1 spec waits for its owner gate | [literature-host-interfaces](milestones/literature-host-interfaces/README.md) LH1, LH2 |
| [#215](https://github.com/vasiloglou/gnd-public/issues/215) | Model-generic assertion admission | Plan r6 approved 2026-11-23; LH3 and LH4 are outlines in the plan | [literature-host-interfaces](milestones/literature-host-interfaces/README.md) LH3, LH4 |
| [#226](https://github.com/vasiloglou/gnd-public/issues/226) | A reference recall for literature reading, quote scope, why `verify` fails | Closed locally 2026-11-23 (auto); PRs 243, 244, 252 open, not merged | [literature-reading-reference](milestones/literature-reading-reference/README.md) LR1–LR3 |

Status, 2026-11-23: eight issues are open. #214 and #217 were closed as
delivered on `main`; 0.4.0 still behaves as they describe until 0.5.0 is
released. The reviewed-vocabulary-growth plan r1 and VG1 draft spec merged as
[PR #230](https://github.com/vasiloglou/gnd-public/pull/230). Plan r3 and its
review records merged as
[PR #232](https://github.com/vasiloglou/gnd-public/pull/232). A light panel
read r1 and four of six seats returned `revise`
([disposition](milestones/reviewed-vocabulary-growth/evidence/plan-review-r1/disposition.md));
r2 repaired its 22 concerns. A second round over r2 ended below quorum, two
of six seats, so r2 has no panel result
([record](milestones/reviewed-vocabulary-growth/evidence/plan-review-r2/disposition.md));
r3 repairs the four points those two reviews raised. A third run over r3
also ended below quorum, two of six seats
([record](milestones/reviewed-vocabulary-growth/evidence/plan-review-r3/disposition.md));
r4 repairs the eight points its two reviews raised. No reviewer has read r4.
The owner approved r4 on 2026-11-23 with decisions D1–D14 ruled as proposed
([plan gate](milestones/reviewed-vocabulary-growth/001-plan-gate.md)); each phase spec still has its own gate. The literature-host-interfaces plan
r6 and its LH1 draft spec merged as
[PR #237](https://github.com/vasiloglou/gnd-public/pull/237); the owner
approved r6 on 2026-11-23
([plan gate](milestones/literature-host-interfaces/001-plan-gate.md)).

### Proposed order

| Order | Work | Issues | Why here |
|---|---|---|---|
| any time | Release 0.5.0: include-root-routes, pyrel-rules-coverage and aggregate-count-certificates, all merged and unreleased | #214, #217 (closed) | Owner trigger. Nothing else waits for it, and it puts both fixes in a release |
| 1 | reviewed-vocabulary-growth VG1 | #221 | Done 2026-11-23 (PR 239) |
| 2 | growth-round-outcomes GO1 | #228 | Small, internal, no ruling. Every growth round pays it: 42.6 s at 2,404 object types for one added fact type |
| 3 | reviewed-vocabulary-growth VG2–VG5 | #218, #222 | Done 2026-11-23 (PR 240); milestone closed |
| 4 | growth-round-outcomes GO2–GO5 | #227 | The reporter measured 2 elements added in 20 rounds. Waits for rulings D1–D5 of its plan |
| 5 | literature-host-interfaces LH1–LH4 | #216, #215 | Working host-side workarounds for both |
| 6 | literature-reading-reference LR1–LR3 | #226 | LR1 and LR2 can run at any time; LR3 needs LH1 and LH2 and an owner-selected producer and budget |

Dependencies, by shared file:

- `evolve/service.py`: VG2 (rule D-12), VG4 and GO1–GO3. One writer at a
  time. GO1 goes before VG2 starts or after it merges.
- `unattended-growth.md`: VG2, VG5 and GO4. GO4 follows VG2's change.
- `examples/literature/reading.py`: LH1, LH2, LR2 and LR3. The LR phases
  follow LH2.
- Orders 1 and 2 share no file, so they can run on two branches at once. So
  can order 5 beside orders 1 to 4.

Three growth issues meet in the same round: the seed it starts from (#222),
what a round keeps (#227) and what a round costs (#228). #222 and #227 come
from one reporter's unattended run; #228 was measured here on a synthetic
model. A 0.6.0 release that carries reviewed-vocabulary-growth
and growth-round-outcomes together answers all three.

Status, 2026-11-23, later: the owner asked for the 0.5.0 release, selected
the standard GND panel for its plan and close, and delegated the milestone's
approval rulings. The owner also ruled that the release depends on
literature-host-interfaces and reviewed-vocabulary-growth, so it is cut after
both are merged; this replaces the "any time" row of the order above and the
0.6.0 pairing for reviewed-vocabulary-growth.
[release-0.5.0](milestones/release-0.5.0/README.md) has plan r2, reviewed at
r1 and approved by delegated ruling, and a blocked RW1 draft spec; nothing is
bumped or built. Merges and each publication act stay with the owner.

Status, 2026-11-23, later still: both of those milestones are merged and
closed on `main` (`c227c004`). The owner then ruled that the release also
waits for pins-and-review-check (plan on pull request 248, PF1 on pull
request 250, neither merged), so RW1 is still held. The
[release plan](milestones/release-0.5.0/notes/release-0.5.0-plan.md) §12
records the ruling and a default-lane baseline of `main`.

Status, 2026-11-24: pins-and-review-check is merged and closed, and RW1 of
release-0.5.0 started: its spec is revised against `c62a32b8` and the
version bump's effect was measured once (E1). The owner then ruled that the
release also waits for ossie-relational-bundle (pull requests 264 and 266,
not merged), so RW1 is held before its second ruling and nothing is bumped.
The release plan's §13 records it.

Status, 2026-11-25: ossie-relational-bundle is merged to main with its close
record (pull requests 266 and 270 to 274), so every milestone the release
waited for is on main. RW1 of release-0.5.0 is resumed: its spec is revised
against `e8359685` and E1 runs again. Nothing is bumped. The release plan's
§14 records it, with how it reads that milestone's unrecorded close ruling.

Status, 2026-11-25, later: RW1 is implemented on its branch and recorded
([002-phase-RW1.md](milestones/release-0.5.0/002-phase-RW1.md)): version
0.5.0, one 0.5.0 notes section, prepared and not published. Its pull request
waits for the owner's merge. Pull request 275 recorded the Ossie milestone's
close ruling and is merged. Nothing is built, uploaded, tagged or released.

Status, 2026-11-25, RW2: the owner merged RW1 (pull request 282), so main
says 0.5.0, prepared and not published. RW2's spec is ruled and its six
installed probes are written and rehearsed
([003-RW2-pre-freeze.md](milestones/release-0.5.0/003-RW2-pre-freeze.md));
their pull request waits for the owner's merge. No candidate is built.

Status, 2026-11-25, RW2 done: the owner merged the probes pull request
(283). A 0.5.0 candidate was built from main `85d076ba`, rebuilt
independently on beast-3 with the same hashes, and passed installed
acceptance there (33 passed)
([004-phase-RW2.md](milestones/release-0.5.0/004-phase-RW2.md)). Nothing is
uploaded, tagged or released; RW3 is next.

Status, 2026-11-25, RW3 done: the publication hand-over for 0.5.0 is written
([005-phase-RW3.md](milestones/release-0.5.0/005-phase-RW3.md)): the dossier
with each owner act, the rehearsed publication edits and a remote snapshot.
Nothing is uploaded, tagged or released; each act waits for the owner.

Status, 2026-11-25, published: GND 0.5.0 is on PyPI (uploaded 17:53 UTC), the
served files match the accepted candidate, `v0.5.0` is tagged on `85d076ba`
and the GitHub release exists, each on the owner's request
([006-publication.md](milestones/release-0.5.0/006-publication.md)). The
milestone close is next.

Status, 2026-11-25, closed: release-0.5.0 is closed
([008-milestone-close.md](milestones/release-0.5.0/008-milestone-close.md))
after a full default lane at main (22,057 passed, 0 failed) and the standard
GND panel over the close candidate. 0.5.1 was cut as a GitHub tag only the same
day, outside the milestone, fixing issue 286.

Decisions waiting for the owner: the VG1 spec
of reviewed-vocabulary-growth; D1–D9 of
[growth-round-outcomes](milestones/growth-round-outcomes/notes/growth-round-outcomes-plan.md);
D1–D9 of
[literature-reading-reference](milestones/literature-reading-reference/notes/literature-reading-reference-plan.md);
and whether this order stands. Each of the three has its full plan and first
spec; no plan review has read the last two. The owner approves a plan before
any code.

### Added 2026-11-23: pins-and-review-check

[pins-and-review-check](milestones/pins-and-review-check/README.md) takes
the work that pull requests
[235](https://github.com/vasiloglou/gnd-public/pull/235),
[246](https://github.com/vasiloglou/gnd-public/pull/246) and
[247](https://github.com/vasiloglou/gnd-public/pull/247) left undone. No
issue was filed for it. The owner approved plan r1 on 2026-11-23 with D1–D5
as proposed ([plan gate](milestones/pins-and-review-check/001-plan.md)); no
review has read it.

| Order | Work | Source | Why here |
|---|---|---|---|
| any time | PF1: the packaged-skill inventory defined once; the install, uninstall and verification-fix tests import it and join the guard block | PR 247 | `tests/test_verification_fixes.py` fails 5 of 13 tests on `main`. Tests only; shares no file with the milestones above |
| after PF1 | PF2: a recorded calibration of the standing "code fitted to its examples" review check | PRs 235, 246 | About eight paid `codex` reviews; nothing waits for it |

Status, 2026-11-23, later: closed locally by delegated ruling
([close](milestones/pins-and-review-check/004-close.md)). PF1 is
[PR 250](https://github.com/vasiloglou/gnd-public/pull/250) and PF2 is
[PR 253](https://github.com/vasiloglou/gnd-public/pull/253), stacked on the
plan's [PR 248](https://github.com/vasiloglou/gnd-public/pull/248); none is
merged. PF2 found a defect on `main` in `gnd.exp.frontmatter` (fixed in a
separate pull request). PF1's baseline found 14 more tests red on `main`;
PR 254 repaired them.

### Added 2026-11-25: seeded-routes-and-identifiers

[seeded-routes-and-identifiers](milestones/seeded-routes-and-identifiers/README.md)
plans issues 292 (a seeded unattended root through `gnd flatten`, `gnd extract`
and `gnd export pyrel`), 279 (`refscheme.reference_identity`'s selection) and
280 (Ossie identifiers for unit-based references and multi-supertype subtypes),
and a tag-only 0.5.2. The owner chose the light panel for the plan and close and
delegated approval of the plan and specs. Planning only; no phase has started.

