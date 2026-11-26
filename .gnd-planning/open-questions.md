# Public question home

No source question is closed or transferred merely by this scaffold. The
[carryover register](milestones/public-launch/migration/obligations.md) preserves
original IDs and states at launch. The dated transfers below supersede its Authority column for the four named questions. All other source questions retain their prior ownership.
New authoritative development questions belong here once their unit has a recorded
public handoff. Cross-unit questions have one canonical owner and cross-references.

## Four question transfers accepted 2026-11-25

The source repository has restricted access. Source paths, line numbers and the relevant wording are reproduced here.

The repository owner authorized the transfer of these four questions and publication of their wording and provenance in PR #310. The [owner handoff record](milestones/refactoring-followups/notes/F8-approval.md) records the authorization. This public register now owns their future disposition. The original records retain their historical status and release targets. [Transfer issue](https://github.com/vasiloglou/gnd-public/issues/308).

### OQ-V52-P1-IMPORTWALK-1

Decision for #308 is transfer to gnd-public. Transferred as **open**. Public owner is codegen/conformance maintenance.

> Consolidate the AST import walk re-implemented in 16 files behind one published helper. Codegen/conformance maintenance.

[Source `.gnd-planning/milestones/v5.2/001-phase-1.md:264` at 65b73ee9](https://github.com/vasiloglou/gnd/blob/65b73ee9d687365dfabb15cc1412a4ee9b4a4111/.gnd-planning/milestones/v5.2/001-phase-1.md#L264).

The later v6.0 close carried import-walk consolidation unscheduled. [Source `v6.0/notes/v6.0-close-amendments.md:114–117`](https://github.com/vasiloglou/gnd/blob/65b73ee9d687365dfabb15cc1412a4ee9b4a4111/.gnd-planning/milestones/v6.0/notes/v6.0-close-amendments.md#L114).

### OQ-V52-CLOSE-CANONJSON-1

Decision for #308 is transfer to gnd-public. Transferred as **open**. Public owner is artifacts maintenance.

> Decide whether and how the report, evolution,
>   and derivation-parity canonical JSON conventions should converge without
>   changing historical evidence bytes. Target: v5.3 artifacts maintenance.

[Source `.gnd-planning/milestones/v5.2/notes/v5.2-close-amendments.md:54` at 65b73ee9](https://github.com/vasiloglou/gnd/blob/65b73ee9d687365dfabb15cc1412a4ee9b4a4111/.gnd-planning/milestones/v5.2/notes/v5.2-close-amendments.md#L54).

The v6.0 close proposed carrying canonical JSON consolidation unscheduled. [Source `v6.0/notes/v6.0-close-amendments.md:110`](https://github.com/vasiloglou/gnd/blob/65b73ee9d687365dfabb15cc1412a4ee9b4a4111/.gnd-planning/milestones/v6.0/notes/v6.0-close-amendments.md#L110).

### OQ-V63-CLOSE-HELPER-TAIL-1

Decision for #308 is transfer to gnd-public. Transferred as **carried**. Public owner is test-hygiene milestone owner.

> carried to an unscheduled test-hygiene
>   milestone. Phase 4's remaining CLI/digest/writer adapters and separate
>   global import-path cleanup need their own bounded inventory and import
>   resolution controls. The trigger is a later explicit helper-consolidation
>   request, not this milestone close.

[Source `.gnd-planning/milestones/v6.3/009-milestone-close.md:116` at 65b73ee9](https://github.com/vasiloglou/gnd/blob/65b73ee9d687365dfabb15cc1412a4ee9b4a4111/.gnd-planning/milestones/v6.3/009-milestone-close.md#L116).

### OQ-V72-P1-ARTIFACT-COPIES

Decision for #308 is transfer to gnd-public. Transferred as **carried**. Public owner is artifact-routing investigation.

> Owner: future v7.3 artifact-routing investigation. v7.2 P1 measured three newly
> recorded copies: diff.py::_digest, export/souffle.py::digest and cli.py::_cmd_diff.
> The first two wrap sha256 hexdigest; the third performs canonical JSON display.
> P1 adds drift detection and does not route production code. A future bounded
> change must preserve exported bytes/CLI newline behavior with focused controls.
> This is new debt outside the seven named v7.2 investigations; see v7.2/006-phase-1.md.

[Source `.gnd-planning/open-questions.md:660` at 65b73ee9](https://github.com/vasiloglou/gnd/blob/65b73ee9d687365dfabb15cc1412a4ee9b4a4111/.gnd-planning/open-questions.md#L660).

The artifact-copy question was minted in [v7.2 phase 1](https://github.com/vasiloglou/gnd/blob/65b73ee9d687365dfabb15cc1412a4ee9b4a4111/.gnd-planning/milestones/v7.2/006-phase-1.md#L247). The v7.3 artifact-routing trigger was recorded as follows.

> before changing any named digest/display caller or at that planning gate, whichever occurs first, characterize exported-byte and CLI newline compatibility.

Source paths are `.gnd-planning/milestones/v7.2/006-phase-1.md:247` and `.gnd-planning/open-questions.md:667–671`. [Source ruling](https://github.com/vasiloglou/gnd/blob/65b73ee9d687365dfabb15cc1412a4ee9b4a4111/.gnd-planning/open-questions.md#L667).
