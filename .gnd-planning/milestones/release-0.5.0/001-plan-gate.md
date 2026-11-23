---
milestone: release-0.5.0
station: plan-gate
scope: plan-gate
date: 2026-11-23
skill: "n/a -- repository development under process-milestone"
gates:
  - command: "uv run python tools/run_gnd_review_panel.py .gnd-planning/milestones/release-0.5.0/evidence/plan-r1/review-request.json --out <scratch>/panel-run --reviewer-timeout 1500 --overall-timeout 1800"
    exit: 0
    output: "quorum-established: 5 of 6 seats (claude, codex, gemini, kimi, glm); qwen nonzero"
  - command: "uv run gnd review finalize <scratch>/panel-run .gnd-planning/milestones/release-0.5.0/evidence/plan-r1/synthesis.json --out .gnd-planning/milestones/release-0.5.0/evidence/plan-r1/PANEL-REVIEW.md"
    exit: 0
    output: "2 agreed groups, 9 divergent concerns, 11 prioritized fixes"
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/release-0.5.0/notes/release-0.5.0-plan.md sha256 c1c846bd5b8e5b29962d6a611c73862c55ccf069d66e788acc240ee9f4781999"
    exit: "n/a -- ruling"
    output: "plan r2 approved; RW1 held by the owner's RW-D2 ruling"
evidence:
  - path: .gnd-planning/milestones/release-0.5.0/notes/release-0.5.0-plan.md
    sha256: c1c846bd5b8e5b29962d6a611c73862c55ccf069d66e788acc240ee9f4781999
  - path: .gnd-planning/milestones/release-0.5.0/evidence/plan-r1/review-request.json
    sha256: 84efcce6e773a562e24a20eb60136e5c61aaee4112528a396bb905d93ebffb7f
  - path: .gnd-planning/milestones/release-0.5.0/evidence/plan-r1/synthesis.json
    sha256: 553a0bcee6de00d8755bb36912544dc654128ae266129b1771070f7ec52a46dd
  - path: .gnd-planning/milestones/release-0.5.0/evidence/plan-r1/PANEL-REVIEW.md
    sha256: 8e6616c9e6373a1974a98a25deee5da628c0ea56ee518bbca94e2dfe109ceac1
---

# Claim

The standard GND panel reviewed plan r1 from commit `94eb80e0`, SHA-256
`5a34615dd38d5a2076de20933516cae8df41963d2d82fad59265fad9fc823391`. Five of
six seats returned validated responses: one `approve` (kimi), three `revise`
(claude, codex, glm) and one `block` (gemini). The Qwen seat's CLI stopped at
its own 600 second wall-clock budget and returned nothing. Plan r2 applies the fixes in
its §11 and is approved by delegated ruling. **No review has read r2.**

The owner's ruling RW-D2, given while the review ran, makes the release wait
for two other milestones. The plan gate is therefore satisfied and the first
phase is blocked.

## Review disposition

The [panel report](evidence/plan-r1/PANEL-REVIEW.md) retains all fourteen
concerns. Each was checked against the repository before its fix was written.

| Concern | Seats | Checked how | Class | Disposition |
|---|---|---|---|---|
| Role-scoped value rules have no installed probe; no change-to-probe table | claude, gemini, glm | plan §2 probe 3 against W7 | blocking for predicate 4 as written | fixed in §11: probe 3 gains the model; RW2 carries the table |
| Notes reconciliation misses the freeze commit and shipped files outside `src` and `docs` | claude, codex | RW1-C3's diff scope against W5 | blocking for predicate 3 | fixed in §11: one path scope, run at the build commit |
| Freeze, probe-merge and build commits are not bound together | claude | RW2-C0 to C3 as ordered in r1 | hardening | fixed in §11: one commit, freeze void if main moves |
| An exit of 0 does not show the exported program holds the rule; default and `duckdb` modes unprobed | codex | plan §2 against the release notes on main | blocking for predicate 4 | fixed in §11: content assertions, every advertised mode |
| The GitHub release precedes the served-file check | codex | publication stage order against `docs/releasing.md` | hardening | fixed in §11: comparison right after upload |
| RW2 and RW3 gates omit the structure guards | codex | §9 against §0 | hardening | fixed in §11 |
| The releasing sentence is pinned in `tools/release_text.py` and a test fixture | claude | `STANDING` entry at line 81; fixture at line 78 of `tests/test_release_text.py` | hardening | fixed in §11: three files move together; RC-03 lands with them |
| The E1 base commit is not named | glm | W10, RW1-C6 | hardening | fixed in §11 and RW1 spec D5 |
| Replacements for the retired 0.3.0 controls are deferred to a later spec | gemini | the four uses of the 0.3.0 wheel in the acceptance test | hardening | fixed in §11: the table of four, each retired without replacement and why |
| The oracle lane's environment is unchecked | glm | imported `relationalai` and `duckdb` from the tutorials runtime environment, 2026-11-23 | hardening | fixed in §11: recorded; rechecked before the freeze |
| "RW1 D4" reported as a typo for RW-D3 | gemini | the RW1 spec has a D4, the headline block | completeness | rejected as a typo; §11 says which decision is which |

The first row holds three concerns and the second two, so the eleven rows
hold all fourteen.

## Owner rulings recorded with this gate

- 2026-11-23: the standard GND panel for the plan and the close; delegated
  approval rulings for this milestone; the `pyrel_oracle` lane on the build
  commit. Source: the owner's answers to three questions in the planning
  session.
- 2026-11-23, RW-D2: the release depends on literature-host-interfaces and
  reviewed-vocabulary-growth. Source: the owner's message in the same
  session. The plan reads it as "cut after both are merged with their close
  records"; that reading is the plan's and the owner may narrow it.

## Readiness

| Stage | Prerequisite | Current gate | Next action |
|---|---|---|---|
| RW1 | Plan gate; both RW-D2 milestones merged | Blocked draft spec, no ruling | Revise the spec against main once both are merged, then rule on E1 |
| RW2 | RW1 on main | Pending | Write the acceptance spec |
| RW3 | RW2's accepted candidate | Pending | Prepare the hand-over |
| Close | Publication record and phase evidence | Pending | Standard panel and delegated close ruling |

On 2026-11-23 literature-host-interfaces is an outline r1 with four phases,
and reviewed-vocabulary-growth is plan r3 with five phases, not approved.
Neither has started a phase.

## Gate output (verbatim)

    panel: exit 0
    {"advisory":true,"attempted_reviewer_ids":["claude","codex","qwen","gemini","kimi","glm"],"command":"review panel","gnd_version":"0.4.0","outcome":"quorum-established","quorum_met":true,"request_kind":"plan","request_sha256":"e47d9730e70e313ffb92e296783c4b9d4bc3a8d41bc7246c22a5d440f333ac91","required_successes":3,"reviewed_artifacts_unchanged":true,"reviewer_effort":"xhigh","reviewer_statuses":[{"reviewer_id":"claude","status":"success"},{"reviewer_id":"codex","status":"success"},{"reviewer_id":"qwen","status":"nonzero"},{"reviewer_id":"gemini","status":"success"},{"reviewer_id":"kimi","status":"success"},{"reviewer_id":"glm","status":"success"}],"run_directory":"<scratch>/panel-run","run_sha256":"c7edeab17da6f9d14180520d436d384eba75f454b350d30e2bbf096bc2f5d327","schema_version":1,"successful_reviewer_ids":["claude","codex","gemini","kimi","glm"],"tool":"gnd"}
    finalize: exit 0
    {"advisory":true,"agreed_concern_count":2,"command":"review finalize","divergent_concern_count":9,"gnd_version":"0.4.0","outcome":"quorum-established","prioritized_fix_count":11,"quorum_met":true,"report_path":".gnd-planning/milestones/release-0.5.0/evidence/plan-r1/PANEL-REVIEW.md","required_successes":3,"run_sha256":"c7edeab17da6f9d14180520d436d384eba75f454b350d30e2bbf096bc2f5d327","schema_version":1,"successful_reviewer_ids":["claude","codex","gemini","kimi","glm"],"synthesis_sha256":"d6701ef887d82c83756fb599a8dbd4fe1c709116906bdd306618b84a9c3d7a91","tool":"gnd"}

The `run_directory` value was an absolute scratch path; it is written here as
`<scratch>/panel-run`. Nothing else in the two lines was edited.

> Delegated approval (auto=true), 2026-11-23. Approved the release-0.5.0
> plan r2 at SHA-256
> c1c846bd5b8e5b29962d6a611c73862c55ccf069d66e788acc240ee9f4781999.
> Source: the owner's request "Release 0.5.0" and the owner's selection of
> delegated approval and the standard GND panel in the same session. Scope:
> plan decisions RW-D0 to RW-D14 as amended in §11, with RW-D2 recorded as
> the owner's own ruling and not a delegated one; phase and close rulings
> are recorded separately. Review budget: one standard panel round, six
> reviewer attempts, 1,500 seconds per seat and 1,800 overall. The reviewed
> r1 and the approved r2 have distinct digests, and r2 has no review opinion
> of its own. Merge, each publication act and the phase size limits keep
> their separate gates. This ruling is not the owner's reading of the plan.

## Boundary

- The raw panel streams and the run manifest are in the session's scratch
  directory and are not in history. The request, the synthesis and the
  report are.
- The finalize receipt reports the synthesis digest `d6701ef8…7a91`. The tool
  takes it over its canonical form of the synthesis
  (`canonical_panel_synthesis` in `src/gnd/review/report.py`), not over the
  file's bytes; the evidence list above gives the digest of the committed
  file.
- Five seats, not six, reviewed the plan. The Qwen seat was not rerun.
- Nothing in this gate bumped a version, built a file or changed anything
  outside `.gnd-planning/`.
