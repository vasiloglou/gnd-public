---
milestone: model-composition
station: "Final candidate compatibility comparison"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: candidate-comparison
date: 2026-11-10
gates:
  - command: 'uv tool run --from uv==0.10.10 uv run pytest -q --tb=short'
    exit: 1
    result: '6 failed, 18795 passed, 801 deselected, 1 warning in 2550.44s (0:42:30)'
  - command: 'uv tool run --from uv==0.10.10 uv run python tools/mc1_model_census.py --out /private/tmp/gnd-model-composition-candidate-r2-1ca2379f/candidate-r2-census.json'
    exit: 0
    result: '423members;400 original observations unchanged;23 additions separately dispositioned'
  - command: 'uv tool run --from uv==0.10.10 uv run pytest -q -s -m "evidence or census" tests/test_mc1_census.py --tb=short'
    exit: 0
    result: 'baseline_members=400 added_members=23;2 passed in15.82s'
  - command: 'compare exact frozen default failure identities and complete summaries'
    exit: 0
    result: 'no added/removed failures or errors/skips/xfails/xpasses; clean before/after tracked status'
  - command: 'ruling: delegated (auto=true) accept compatibility comparison, amended plan sha256 dab3337b2c9ce26a2459e5040dd040da0bde2eb605f8b441d22d2c6a679c36d8'
    exit: 'n/a -- comparison acceptance only, not milestone close'
evidence:
  - path: .gnd-planning/milestones/model-composition/evidence/close/candidate-r2-result-manifest.json
    sha256: 92a00860db381e869be7a3834c799a400a33f751e7cafdbdd705d774e795b4a8
  - path: .gnd-planning/milestones/model-composition/notes/model-composition-plan.md
    sha256: dab3337b2c9ce26a2459e5040dd040da0bde2eb605f8b441d22d2c6a679c36d8
---

# Claim

Candidate1ca2379f7e0d0834da8e530599f1e9eada7a335d completes the actual named beast-3 default/census comparison. Default exits1 with18795passes and exactly the same six frozen failures as baseline459ca8d2; marked census exits0 with2passes. All400 original per-observable model rows are unchanged, with23 additions individually dispositioned (22load,1deliberate invalid re-pin-only fixture). Delegated acceptance (auto=true),2026-11-10, under the named milestone instruction accepts this unchanged-known-red comparison only. It is not a green full suite, the owner's personal reading, actual main satisfaction or milestone acceptance.

## Frozen failures and outputs

The grow-a-model prose paragraph and five RF5 source-body pins remain exactly the baseline node identities. There are no additional/removed failures, errors, skips, xfails or xpasses. Counts increased from18392baseline passes to18795; configured deselections799→801 reflect the separately selected census tests. No xfail or expected-answer refresh was introduced. Raw complete summaries and both process exits are retained under candidate-r2 names; actual tracked status is empty before and after. Parent SSH also returned1 with producer0/census0/default1, independently retrieved before comparison.

The new producer's423-row bytes exactly equal the already retained final-census.json. candidate-r2-census-binding.json binds this new invocation/source/runtime/exit to those identical retained bytes; no duplicate data file or silent baseline regeneration. census-comparison.json lists all23 additions, original phases, source hashes and the intentional invalid fixture. Earlier6de completed census, its invalidated incomplete full run, and rejected8e5 complete14-failure run stay distinct and are not relabelled.

## Setup and repairs

Fresh isolated tracked checkout on beast-3, uv0.10.10, locked dev group, Python3.11.18; source1ca2379f and documented main reference d2d6309b captured. The earlier local phase interpreter is3.11.15 and is not conflated with this execution. No env file/credential value was read or printed. Optional/excluded native, proof, external or historical lanes remain excluded and are not claimed executed.

Record027 repairs retained-draft reference fidelity;028 reproduces and repairs all eight added failures using one offline prose fix plus exact API/order/instrument successors. All418 affected checks and dirty guard probes pass; no runtime/schema/model/CLI grammar or golden bytes changed in those follow-ups. Phase budget attribution and combined128line accounting are explicit in028. The completed new replay confirms those added failures are absent; its six baseline failures remain nonzero accepted residuals.

## Boundary and pending gates

This record accepts candidate compatibility, not the milestone. Later comparison/provenance bookkeeping changes only planning/evidence and requires focused current-context checks; no new runtime/test change inherits this full result. Actual source/test/skill delta to main must be measured after explicitly authorized merges, with close follow-ups identified separately. Source-snapshot results never manufacture main evidence.

PR157c6dad88d and PR155396f86f3 are still pending explicit owner merge authority. Draft PR158 contains close follow-ups and evidence. One explicitly selected independent Codex CLI close opinion and final question/ruling remain owed; prior phase reviews cannot substitute. Issue95 remains open. No merge, publisher, certification or successor milestone is authorized by this comparison acceptance.

## Current bookkeeping verification

Measured source/test/skill bytes remain1ca2379f. Focused current-context reference checks pass2tests;114milestone citations are well formed. All11 historical manifests match their recorded snapshots (1524 bound entries). The manifest binds these outputs. Original pytest diagnostic trailing whitespace is retained only in the raw artifact at the exact lines enumerated in plan §17; authored metadata must pass whitespace checking. These checks do not substitute for main verification or the independent close opinion.
