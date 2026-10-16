---
milestone: analytics-m3-repairs
station: phase-8
skill: n/a -- repository development, not a gnd-solve station
scope: phase-8
date: 2026-10-13
gate:
  command: "uv run pytest -q tests/test_m3_population_schema.py tests/test_population_load.py tests/test_m3_generated_json.py tests/test_m3_indexed_subset.py tests/test_public_transition_api_guards.py tests/test_public_transition_ir_immutability.py tests/test_public_transition_contract.py tests/test_public_transition_trace.py tests/test_transition_report.py tests/test_v70_phase4_transition.py tests/test_rf1_layering.py tests/test_schema_sync.py tests/test_rf7_consumers.py"
  exit: 0
  output: 227 passed in 5.22s
slow_cadence:
  command: uv run pytest -q
  trigger: explicit source owner or separately selected CI run
  reason: broad historical/proof/certification lanes outside this focused source repair
---

## What shipped

Bounded in-memory expansion of sole local refs in the bundled acyclic population
schema. Same Draft202012Validator and loaded-schema lookup seam; no schema artifact,
parser, layer2, marker or model edits. Unsupported reference/resource/keyword shapes
retain original validator semantics. Depth48/work4096 bound; literals/annotations
are not schema positions. No persistent cache or validation bypass. RED6f0665b:
14 missing-preparation failures,15 preexisting exact error-parity controls pass.

## Gate commands and output

uv run pytest -q tests/test_m3_population_schema.py tests/test_population_load.py tests/test_m3_generated_json.py tests/test_m3_indexed_subset.py tests/test_public_transition_api_guards.py tests/test_public_transition_ir_immutability.py tests/test_public_transition_contract.py tests/test_public_transition_trace.py tests/test_transition_report.py tests/test_v70_phase4_transition.py tests/test_rf1_layering.py tests/test_schema_sync.py tests/test_rf7_consumers.py
UV_CACHE_DIR=/private/tmp/downstream-uv-cache wrapper used, exit0,227 passed in5.22s;
phase-8-focused.txt. New successor work-bound test catches removed-node-cap mutant,
phase-8-bound-mutant-red.txt:1 failed in0.06s. Unchanged implementation/direct:
UV_CACHE_DIR=/private/tmp/downstream-uv-cache uv run --offline pytest -q tests/test_m3_population_schema.py
Exit0,30 passed in0.07s, phase-8-bound-green.txt. Additional test after review did
not alter production bytes or existing answers; ruleretained separately.
UV_CACHE_DIR=/private/tmp/downstream-uv-cache uv run --offline ruff check src/gnd/population.py tests/test_m3_population_schema.py
Exit0,All checks passed!, phase-8-lint.txt.
App affected90 selection repeats exact phase06 overlay command,exit0,100%.
Full app: UV_CACHE_DIR=/private/tmp/downstream-uv-cache uv run --offline --package downstream-app --with-editable <GND_WORKTREE> --with rpds-py==2026.9.1 pytest -q apps/downstream-app
Exit0,274cases100%, phase-08-full-app.txt. This is candidate overlay, not adoption.

## Native measurement

App-owned phase-08-native-driver.py: uv offline --package downstream-app,
json-load --seconds60 originalpinfa population code(equal7f40population code) vs
--with-editable <GND_WORKTREE> --with rpds-py==2026.9.1 candidate, each3serialruns
with no warmup. JSON loads1.866828s median→0.832687s; identical bytes/facts/types/
instances/covers/warnings. Full native root3 repeats8.306632/8.300915/8.301700s,
median8.301700s vs phase07 12.325069s. APIexit2; complete normalized full report
byte-identical to originalfa, only phase06 generated.json labels normalized.
Native question: same prior app-owned tuning probe, cap8/top3/workers1/wall120,
exit0 process but parent statuswall_budget, no completed answer, peakRSSnull.
One tiny0.04s unitcontrol overlapped this censored diagnostic; it is no finalgate
or speedratio. No heavy-test concurrency in component timing runs. Full app test
started after this question probe ended. No held-out/test access or paidcost.

## Independent review and refactoring

Own Codex CLI gpt-5.5 xhigh read-only, prompt stdin; no blocking/hardening findings.
Retained notes/phase-8-codex-review.md, edited only pathsanitization. It verified
schema byteidentity, bounded schema-position expansion/fallback, errorprojection,
patchseams and unchanged validation order. It read29/227/lint evidence, did not
run tests. Pending native/app acceptance evidence completed and retained here.
One reviewer is one reviewer. Postreview addedworkbound control not independently
reviewed; production bytes remain exactly those reviewed and measured.
Refactors EXECUTED: one shared bounded schema preparation helper at current loader
home; no second validator/schema, dependency, import home or global caching layer.

## Boundary and open questions

M3 still open. This is source delivery, not owner merge/adoption or final all109
agreement/29held-out15s successful median. App pinfa retained. Question120s remains
censored, not a successful completion. Source PR20 receives these tested bytes;
explicit owner merge required. Further scoped performance work before gate needed.
Native compiled candidate diagnostic also exposes unrelated empty-operation work
limit refusals; investigate under a new required phase before edits, never bump or
waive the budget. No broad historical replay, proof/certification or releaseclaim.

## Evidence hashes

[
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/notes/phase-8-approval.json",
    "sha256": "ed8e3848a66b113d0d5287db553ac722b3b86cc923cafd9c8579527363135415"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/notes/phase-8-bound-ruling.json",
    "sha256": "40fae735f05444a699ac44b64b944ac814b8178170c9b4f72a9a14cec494dff6"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/notes/phase-8-codex-review.md",
    "sha256": "2fb87cb6f68237f29e8cf67ec5923354510e3ffac9eb146442d01d3c1d80d7ae"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/notes/phase-8-spec.md",
    "sha256": "c8b5007ec7e493236c7b573a343ced1c2a68a2624ac662b3f7892befbaab36d8"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-8-bound-green.txt",
    "sha256": "19cd19134c7de50bfd71adc9152e2416667ce7505e7968c5a04ad0225c7e375f"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-8-bound-mutant-red.txt",
    "sha256": "2439903fc706c4a935d4b48e485ad8ad50be1da46c152c93f2311ec2952547d1"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-8-direct.txt",
    "sha256": "c7830d2f13f8e0f9b8ec8e0c14b457d7634c13c96f3c88b5841197d54704f008"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-8-focused.txt",
    "sha256": "f5ab2e9ab89155ccb801f4e0d4fde9f05e9e2dae69262c0f34b6a5a68a856d02"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-8-lint.txt",
    "sha256": "82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-8-red.txt",
    "sha256": "c2e6be3eda6e459ae061c89598ccc753526ca2f399186d28c4c6ee123c917424"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-08-app-preview.txt",
    "sha256": "6997ffb705c1c5fa984efec27d8164c9d96401110464c8e386ecce809f88569c"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-08-full-app.txt",
    "sha256": "97be6ba130d443c43a143d9e22ac09c3d39fdb15a6044f2eccc1474bc2e33302"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-08-native-summary.json",
    "sha256": "82622e6adc2d445f91d841acc2e9f2938e261429d509f7e9e50db274e022f596"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-08-question-probe.json",
    "sha256": "e5df345d9f9e62372aa658f6e7510e76f013e3047b00de6ccf39f111a99963c1"
  },
  {
    "path": "src/gnd/population.py",
    "sha256": "a7eca16d78fe76452dfd26629e03bc459accd8e4da8b6bb2897a3f2dd8743eef"
  },
  {
    "path": "tests/test_m3_population_schema.py",
    "sha256": "f63a3ed8c7b306b19d279003550b0bc9289dbc296be457e3e54a9075d7c4c6f8"
  }
]
