# M3 phase08: Reuse frozen population schema reference resolution

Status: ready, delegated scope2026-10-13; before additional runtime edits.

## Obligations and measured prerequisite

| Source | Obligation | Acceptance |
|---|---|---|
| M3 plan phase05 follow-up/roadmap6.5 and15s target | address measured remaining population validation cost | native_population_load; native_start; question_probe |
| Phase06/07 records and original source semantics | preserve both fixes, full native model/state and reports | exact_schema_issues; public_transition_parity |
| AGENTS public APIs/GND ownership | change only source-owned validator preparation | source_only; app_overlay; separatepin |
| Source/app development protocols | committed RED, independent review and evidence | validator_ref_path; adversarial_review; hashes |

Phase07 native root12.325s does not meet whole-question gate: first tuning dw_5162
cap8/top3/workers1 hits120s. Follow-up30s cProfile firstcandidate shows3 population
loads, schema validation15.364 cumulative profiled seconds and976662 reference
resolution calls. These are causal profiled spans, not additive normal wall costs.
Inputs/model/mirrors unchanged; held-out/test untouched; paidcost0.

## Exact design, compatibility and implementability

Optimize only population.py schema preparation before the same Draft202012Validator.
A bounded pure helper expands recognized sole-$ref nodes from the loaded frozen
population schema, only local #/$defs refs into that schema's3 acyclic definitions
(scalar/opaque_marker/fact_value). No $ref siblings, recursive refs, external refs,
nested resource IDs/dynamic anchors or unknown formats may be rewritten. If any
precondition is absent, return the original schema and use the existing validator.
Expansion retains annotation/type/anyOf/allOf/if/else/properties/items semantics;
original canonical schema artifacts remain byte-identical. No trusted-population
construction, skipped shape/model checks, data-dependent bypass or new dependency.

Preserve _load_population_schema and _schema_issues patch lookup seams; read the
actual schema before expansion, so source monkeypatch/mutation cannot use stale
compiled bytes. No global schema/model/population cache in this phase. Helper must
be total on arbitrary input with explicit recursion/work bound and fallback. The
ordinary validator remains authority for unknown/cyclic/custom schemas. A fallback
is not a fabricated pass or changed schema error. Layer2/population_validate,
validation markers/model identity/content digests, parser caps/JSON duplicate and
nonfinite/YAML alias guards stay unchanged. No operation/frame/rule/IR changes.

## Corpus-first controls and selected gates

New source tests/test_m3_population_schema.py: spy on actual validator constructor
through public packaged population load and assert selected schema has no active
local ref traversal; fails old source's reference-bearing schema. Exact ordered
ValidationIssue(path,message,rule_id,severity) parity against original Draft202012
validator for existing shipped population fixtures and existing hostile shape/value
unit controls (no new domain corpus). Cover v1/v2 opaque values, wrong root/header,
instances/facts/values, equal-json_path ties. Source helper fallback controls for
unknown/cyclic/sibling/external/nested-id refs and hostile schema input. Retain all
original loader/parser guards. Commit RED tests before implementation.

Focused source gate: uv run pytest -q tests/test_m3_population_schema.py
 tests/test_population_load.py tests/test_public_population_paths.py (if present)
 tests/test_m3_generated_json.py tests/test_m3_indexed_subset.py
 tests/test_public_transition_api_guards.py tests/test_public_transition_contract.py
 tests/test_public_transition_trace.py tests/test_transition_report.py
 tests/test_v70_phase4_transition.py tests/test_rf1_layering.py tests/test_schema_sync.py.
Record actual existing filenames and exact command before running. Default lane
exclusions retained; broad historical/proof/certification/provider lanes not selected,
explicit owner/CI cadence remains. Ruff changed source/tests. Independent Codex CLI
read-only diff review with stdin prompt and reproduction-before-fix triage required.

App affected90 controls repeat with candidateoverlay/pin unchanged. Native public
population load at unchanged state: original/current validator, serial3 repeats,
no warmup, wallcap60 each, record completion/CPU/input/code identity and identical
facts/types/covers/markers. Full native root serial3 repeats same dw_5162/cap8,
normalized report parity with phase07. Fresh complete-question tuning-only probe
cap8/top3/workers1 wall120; no successful median if refused. Algorithm-layer test
must bound preprocessing even for hostile schema. No flaky small-call timing CI.

## Standing rules and approval

Totality: bounded expansion/fallback over arbitrary schema JSON, hostile control.
Input cap versus algorithm: fixed acyclic3-definition work and explicit expansion
cap, measured native validator layer. Validation order: parser→shape→model→marker
unchanged. One policy walk: one shared refexpansion helper, actual validator seam.
Normative prose one home: canonical schema unchanged. Representation by measurement:
exact error parity and real-input timings determine admissibility.

Delegated approval auto=true,2026-10-13: existing M3 auto, make fixes part of M3/go
 ahead; plan explicitly requires scoped further performance work when both fixes
miss target. Corpus-first instrument; budget0; no synthetic domain data/upstream
merge/release/certification authority. Source remains GND topic/PR governed.
App directmain; no pin adoption without accepted tested revision.

Phase08 required before final05; independent source-owned execution supplement
and hash approval precede code. No15s waiver, no source slicing or mirror deletion.
If this does not meet original gate, record findings and scope further required
context/prefix reuse before edits. Final all109 cap8 agreement/29held-out latency
and independent closure remain phase05; no held-out tuning/sealed438test access.
