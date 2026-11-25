---
milestone: seeded-routes-and-identifiers
station: plan-gate
scope: plan-gate
date: 2026-11-25
skill: "n/a -- repository development under start-milestone and process-milestone"
gates:
  - command: "uv run python tools/run_gnd_review_panel.py --light .gnd-planning/milestones/seeded-routes-and-identifiers/evidence/plan-r1/review-request.json --out <scratch>/panel-run --effort high --reviewer-timeout 600 --overall-timeout 900"
    exit: 0
    output: "quorum-established: 4 of 6 seats (claude, codex, qwen, glm); gemini malformed, kimi nonzero"
  - command: "uv run gnd review finalize <scratch>/panel-run .gnd-planning/milestones/seeded-routes-and-identifiers/evidence/plan-r1/synthesis.json --out .gnd-planning/milestones/seeded-routes-and-identifiers/evidence/plan-r1/PANEL-REVIEW.md"
    exit: 0
    output: "6 agreed groups, 5 divergent concerns, 11 prioritized fixes"
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/seeded-routes-and-identifiers/notes/seeded-routes-and-identifiers-plan.md sha256 76ddbb2b93b5ab5716090d69130136ac4a818251a4bf638e1aef42413ee819f1"
    exit: "n/a -- ruling"
    output: "plan r2 approved; SI1 ready for its E1 measurement; D1 waits for the owner"
evidence:
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/seeded-routes-and-identifiers-plan.md
    sha256: 76ddbb2b93b5ab5716090d69130136ac4a818251a4bf638e1aef42413ee819f1
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/evidence/plan-r1/review-request.json
    sha256: ff50610270bfee6a664b2ad2a669ce7c2b941e500f2126ef4f450ee9f8f5aa9f
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/evidence/plan-r1/synthesis.json
    sha256: 0d1e465b882dacd5c0d822ffd47519d546061da08cc0515f980cb895919c8bb3
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/evidence/plan-r1/PANEL-REVIEW.md
    sha256: 5cc105961c06c913fd4970cff2647b8c8d5be71748f916fbee7fac312e32c392
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/evidence/plan-r1/disposition.md
    sha256: 858cf0b9374d5dec7f5779dcdc60893dbd1e16d4aafb9b335a8a25fee8d8f91d
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/evidence/plan-r1/cause280.py
    sha256: beed5bffb02732edd96b2060e628635df7ef12d6e0ad10995d0f0bfaeca9a630
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/evidence/plan-r1/cause280.txt
    sha256: 2fe4a59dcab2a2a06a0bcad51fba5441d89e950de7d95500e88a31f700a06e35
---

# Claim

The light GND panel reviewed plan r1 from commit `98008384`, SHA-256
`3bd8904535d1d5cfbbe387e14c183235112c0edf21cabee2b80618e9c6923f1f`, at high
effort. Four of six seats returned validated responses, all `revise`
(claude, codex, qwen, glm). Gemini's output held no JSON object; Kimi's CLI
stopped on the account's weekly usage limit. Plan r2 applies all eleven
fixes, listed in its §11, and is approved by delegated ruling. **No review
has read r2.**

## Review disposition

All four seats found the same blocking defect: r1 proposed carrying the
seed's exemption as a list in the flat model, and allowed binding it to the
flattening record's digests. An unattended host writes both files and can
compute the digests, so it could exempt its own claims. r2 withdraws the
marker: the exemption is computed only in process, from includes checked
against their pins in the same run, and nothing in input bytes grants it.

The other ten fixes make the predicates checkable. Two of them rest on new
measurements, made for this gate on main `f7ee3720`:

- #280's 17 unmapped links split as 8 unit-based, 5 multi-supertype and 4
  from the out-of-scope objectification cause ([cause280.txt](evidence/plan-r1/cause280.txt)).
- All 7 subtypes with several supertypes have supertypes that disagree, so
  SI3 follows GND's existing first-supertype rule.

One reviewer premise was refuted with its conclusion kept: U1 on the
packaged root is not the root's own rule but also depends on the includes
(`_owns_nothing` reads `includes`), so the in-process re-entry must carry the
root's owns-nothing state as well as its origins.

The [disposition](evidence/plan-r1/disposition.md) gives each of the
twenty-five concerns, how it was checked and where its fix is. None was
rejected.

## Owner rulings recorded with this gate

2026-11-25, from the owner's answers to three questions in the planning
session: the light GND panel for the plan and the close (D0); delegated
approval of the plan and specs, with merges and the decisions the specs name
kept by the owner; 0.5.2 as a tag only (D4).

## Readiness

| Phase | Prerequisite | Current gate | Next action |
|---|---|---|---|
| SI1 | plan gate | draft spec r2, no ruling | E1: list every route that loads an include root or flat bytes; then put D1 to the owner |
| SI2 | plan gate | outline | spec with the per-caller and fixture measurement |
| SI3 | plan gate | outline | corpus-first spec |
| SI4 | SI1 to SI3 merged | outline | tag-only preparation |
| close | SI4 | pending | light panel, full lane on beast-3, sweep |

## Gate output (verbatim)

    panel: exit 0
    {"advisory":true,"attempted_reviewer_ids":["claude","codex","qwen","gemini","kimi","glm"],"command":"review panel-light","gnd_version":"0.5.1","outcome":"quorum-established","quorum_met":true,"request_kind":"plan","request_sha256":"6e4ed28e9be6965c63353bbe309bc62deac000274d9b1f0028c7fcc2fc1b3db3","required_successes":3,"reviewed_artifacts_unchanged":true,"reviewer_effort":"high","reviewer_statuses":[{"reviewer_id":"claude","status":"success"},{"reviewer_id":"codex","status":"success"},{"reviewer_id":"qwen","status":"success"},{"reviewer_id":"gemini","status":"malformed"},{"reviewer_id":"kimi","status":"nonzero"},{"reviewer_id":"glm","status":"success"}],"run_directory":"<scratch>/panel-run","run_sha256":"9d33b12b548700b8bafd864fdcaff02475d6f3e104ec93aa11bb14f548fe6754","schema_version":1,"successful_reviewer_ids":["claude","codex","qwen","glm"],"tool":"gnd"}
    finalize: exit 0
    {"advisory":true,"agreed_concern_count":6,"command":"review finalize","divergent_concern_count":5,"gnd_version":"0.5.1","outcome":"quorum-established","prioritized_fix_count":11,"quorum_met":true,"report_path":"<worktree>/.gnd-planning/milestones/seeded-routes-and-identifiers/evidence/plan-r1/PANEL-REVIEW.md","required_successes":3,"run_sha256":"9d33b12b548700b8bafd864fdcaff02475d6f3e104ec93aa11bb14f548fe6754","schema_version":1,"successful_reviewer_ids":["claude","codex","qwen","glm"],"synthesis_sha256":"7e2c110a89f3e840256f911b7664d27340ad751ec8051671e612a61f6e1d9273","tool":"gnd"}

The `run_directory` and `report_path` values were absolute local paths; they
are written here as `<scratch>/panel-run` and `<worktree>/…`. Nothing else in
the two lines was edited.

> Delegated approval (auto=true), 2026-11-25. Approved the
> seeded-routes-and-identifiers plan r2 at SHA-256
> 76ddbb2b93b5ab5716090d69130136ac4a818251a4bf638e1aef42413ee819f1.
> Source: the owner's request to reopen and plan issues 279 and 280 and to
> include 292, and the owner's selection of delegated approval and the light
> GND panel in the same session. Scope: plan decisions D0 to D5 as amended in
> §11, with D0 and D4 recorded as the owner's own choices; D1 and D3 stay the
> owner's to decide at their specs, and D2 too when its ruled reading changes
> a shipped example. Review budget: one light panel round at high effort, six
> reviewer attempts, 600 seconds per seat and 900 overall. The reviewed r1
> and the approved r2 have distinct digests, and r2 has no review opinion of
> its own. Merge, the tag and the phase size limits keep their separate
> gates. This ruling is not the owner's reading of the plan.

## Boundary

- The raw panel streams and the run manifest are in the session's scratch
  directory and are not in history. The request, the synthesis, the report,
  the disposition and the cause measurement are.
- The finalize receipt's synthesis digest `7e2c110a…9273` is over the tool's
  canonical form of the synthesis, not over the file's bytes; the evidence
  list gives the committed file's digest.
- Four seats, not six, reviewed the plan. Neither failed seat was rerun.
- The SI1 spec draft was revised to r2 alongside the plan; it has no ruling
  and no review.
