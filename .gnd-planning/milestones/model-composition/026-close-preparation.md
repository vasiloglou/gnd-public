---
milestone: model-composition
station: "Milestone close preparation"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: milestone-close-preparation
date: 2026-11-10
gates:
  - command: 'uv tool run --from uv==0.10.10 uv run python tools/mc1_model_census.py --out /private/tmp/gnd-model-composition-final-9f3d22f7/final-census.json'
    exit: 0
    result: 'models=423 loaded=356 load_refused=67 loaded_identity_refused=1'
  - command: 'uv tool run --from uv==0.10.10 uv run pytest -q -s -m "evidence or census" tests/test_mc1_census.py --tb=short'
    exit: 0
    result: 'baseline_members=400 added_members=23; 2 passed in 15.70s'
  - command: 'verify eight phase source/evidence manifests against their declared Git snapshots'
    exit: 0
    result: '81/1117/62/23/73/49/39/37 bound entries; zero mismatches'
  - command: 'ruling: delegated (auto=true) approve append-only plan repairs sha256 0174fd9d4953cbd322abdbd094ca25f93fa99d5bf357872bcd6ef158e5b07e20'
    exit: 'n/a -- amendment ruling, not close acceptance'
evidence:
  - path: .gnd-planning/milestones/model-composition/evidence/close/preparation-manifest.json
    sha256: 919067f39986ff80dc246f709cf8b444d3cb2ae7c5e5a50d63f2cc0bdf110bc9
  - path: .gnd-planning/milestones/model-composition/notes/model-composition-plan.md
    sha256: 0174fd9d4953cbd322abdbd094ca25f93fa99d5bf357872bcd6ef158e5b07e20
---

# Claim

All four mandatory phases have their own local completion records008/013/023/025 and bounded independent reviews. The final named beast-3 census at6de7189a passes and preserves all400 original observations, with23 additions individually dispositioned (22load, one deliberate invalid re-pin-only refusal). The full default suite is running; no final outcome is claimed. MC3/MC4 merge authorization and actual main predicates remain pending. This is preparation, not a milestone-close record.

## Delegated plan amendment

Delegated approval (auto=true),2026-11-10, authority owner's named milestone delegation, adopts exact appended §13 at the hash above after implementability/obligation sweep. All original plan bytes remain as a prefix. This records observed phase premises, existing source-contract rulings and actual owner directions; it does not invent permission or retroactively claim review over changed bytes. Independent close review is still required; no close opinion exists yet.

Repairs cover original400 versus new census members, authentic intake/refusal hashes versus positive freshness, actual serial phase overlap, added model verbalization CLI, minimum same-phase normative updates, all re-pins conservatively breaking, authenticated historical/current dependency ordering and exclusions, exact corpus digest/comparison corrections, component-index premise, measured stops/exceptions, accepted Fable expense story and actual reactions, R30 successor, and historical evidence corrections. Prior wording and raising record paths are retained in the amendment table. Question register groups every harvested explicit question/premise into resolved, accepted residual or pending; no pending row is called complete.

## Measurements and audit limits

The original per-observable baseline JSON is never regenerated. The current producer and marked census ran on beast-3 with locked dev dependencies, uv0.10.10, Python3.11.18 and a clean isolated detached candidate. Raw source/runtime, actual exits, producer output and full per-model rows are retained under evidence/close, sanitized only for declared home/repository prefixes. After sanitization all original400 observations were compared again and remain equal. New members are not counted as backward-compatibility witnesses; their source hashes, originating phases and expected load/refusal dispositions are explicit.

Manifest audit hashes each bound file from the declared Git snapshot, not today's evolved source. It verifies historical byte attribution, not runtime correctness or current certificates. MC1 corrected runtime1117entries, phase evidence and later source/evidence manifests all match; source64a42f12/07986c53/ebec0980/6de7189a remain distinct. MC2 gross106source/563test-support calibration uses final phase diff and stays within375/600. No historical evidence, gate or installer golden changed.

The candidate run occurs before the still-pending merges. It can establish a source-snapshot comparison, not main-branch satisfaction. At close verify actual main relevant-tree equality with measured source and account for metadata-only completion records. Any relevant merge change invalidates affected observations; do not call a premerge candidate an achieved main predicate. The existing phase015 carryover's after-merge sequence remains a close dependency, not claimed fulfilled by this preparatory observation.

## Review budget and boundaries

The owner explicitly selected one Codex CLI close reviewer overriding the maintained panel. Declare a separate close budget now: one first close opinion plus at most one narrowly scoped repair confirmation, max2invocations, existing authenticated environment only; no env-file reads, panel, reviewer subagent or additional vendor call. No invocation runs until the close bundle has the required results and actual main evidence. Phase reviews do not consume or substitute for this budget.

MC1/MC4 historical log trailing-space residuals, six baseline default failure identities and13lint findings remain explicit. The final suite must contain exactly the frozen six failures and no new ones before comparison acceptance. Excluded/native/certification/publication lanes are not selected. Dependency currency remains captured-read verification with single-model CAS, not multi-file atomicity. Include-bearing linked-project evolution/codegen/conformance and other refused routes remain unsupported.

## Pending actions

- Owner: fixed-head PR157 c6dad88d merge question and conditional PR155396f86f3 merge question remain unanswered; verify heads/reviews/threads before SHA-guarded merges.
- Coordinator: retain full default result/exit, compare exact failure names and source invariance to baseline; no outcome from progress dots.
- Coordinator: verify all main predicates after required merges, run one selected independent close review, disposition findings within the declared bound, update question sweep and exact amended-plan ruling.
- Coordinator: write the actual next-numbered milestone-close record and submit its PR only when required work is complete; issue95 closes only after achieved completion. No successor milestone starts.
