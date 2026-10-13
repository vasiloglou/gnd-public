---
milestone: M3
scope: phase-9
station: phase-9
skill: n/a -- repository development, not a gnd-solve station
gate:
  command: uv run pytest -q tests/test_m3_compiled_work.py tests/test_compiled_snapshot_obligations.py tests/test_m3_population_schema.py tests/test_m3_generated_json.py tests/test_m3_indexed_subset.py tests/test_public_transition_contract.py tests/test_public_transition_trace.py tests/test_transition_report.py tests/test_public_transition_api_guards.py tests/test_public_transition_ir_immutability.py tests/test_v70_phase4_transition.py tests/test_rf1_layering.py
  exit: 0
  output: 193 passed in 8.04s
slow_cadence:
  command: uv run pytest -q
  trigger: explicit source owner request or separately selected CI
  reason: broad historical and certification lanes outside focused repair
date: 2026-10-13
---

## What shipped

Per-compose prepared compiled subset rows: known empty left rows consume no right
projection work; repeated required projections share their typed identity index.
Required fact and ordered roles identify the cache. Standalone matcher signature,
coverage/unavailable/opaque/metadata guard order, offending row order and shared
MAX_COMPILED_WORK=100000 remain intact. No retained cross-call state.
Corpus-first RED commit0867fcb: four failures and one passing active-budget control.

## Verification

UV_CACHE_DIR=/private/tmp/gnd-apps-uv-cache uv run --offline pytest -q tests/test_m3_compiled_work.py
Exit0,5 passed. Direct output evidence/phase-9-direct.txt.
UV_CACHE_DIR=/private/tmp/gnd-apps-uv-cache uv run --offline pytest -q tests/test_m3_compiled_work.py tests/test_compiled_snapshot_obligations.py tests/test_m3_population_schema.py tests/test_m3_generated_json.py tests/test_m3_indexed_subset.py tests/test_public_transition_contract.py tests/test_public_transition_trace.py tests/test_transition_report.py tests/test_public_transition_api_guards.py tests/test_public_transition_ir_immutability.py tests/test_v70_phase4_transition.py tests/test_rf1_layering.py
Exit0,193 passed in8.04s; evidence/phase-9-focused.txt.
UV_CACHE_DIR=/private/tmp/gnd-apps-uv-cache uv run --offline ruff check src/gnd/compiled_obligations.py tests/test_m3_compiled_work.py
Exit0,All checks passed!; evidence/phase-9-lint.txt.
App overlay: UV_CACHE_DIR=/private/tmp/gnd-apps-uv-cache uv run --offline --package gnd-analytics --with-editable /private/tmp/gnd-m3-performance --with rpds-py==2026.9.1 pytest -q apps/gnd-analytics/tests/test_fast_check.py apps/gnd-analytics/tests/test_source_workspace.py apps/gnd-analytics/tests/test_execution_budget.py apps/gnd-analytics/tests/test_parallel_answer.py apps/gnd-analytics/tests/test_checker_audit.py apps/gnd-analytics/tests/test_cli.py
Exit0,90 affected controls, evidence/phase-09-app-preview.txt. No adoption.

## Native evidence and declared output differences

Same42782-row real first candidate, population SHA256
4f14a10db277c26217e8547b9ed0df95f845a0a7dc44b41fa70fc1abed3f5c6f.
Three serial unprofiled public compiled checks against baseline65b6de0 and candidate:
baseline median3.312944s, candidate3.326023s. No speedup claim.
Exit4→2; exactly three unused compiled obligations change unchecked work-limit to
vacuous: filter_pattern.compiled[2], order_result.compiled[0], limit_result.compiled[0].
Only those finding message/reason_code/verdict and corresponding top-level
counts/exit_code/outcome/verdicts change. All other report fields, warnings and
derivations identical in all three repetitions. D9 explicitly approved this
redundant-work correction; budget unchanged. Summary evidence/phase-09-native-summary.json.
Complete tuning question cap8/top3/workers1/wall120 still wall_budget at120.000447s,
no completed answer. Evidence/phase-09-question-probe.json. No successful latency
median, held-out tuning or final agreement gate claim.

## Review and refactoring

Independent own Codex CLI gpt-5.5 xhigh read-only stdin review, retained verbatim
except path sanitation in notes/phase-9-codex-review.md. No blocking/hardening defect.
One reviewer is one reviewer. Reviewer did not rerun tests. Completeness finding:
RED approval hash differs after import-only Ruff formatting; current green lint
and unchanged expected outcomes recorded in notes/phase-9-lint-ruling.json.
Refactors EXECUTED: one typed per-compose prepared view replaces repeated subset
preparation at its existing module home; no public import relocation or shim change.

## Boundary and open questions

M3 open, original all-cap8/109-question agreement and successful29-held-out median
<=15s unchanged. Source PR20/owner merge and standalone app pin remain pending.
Quadratic origin projection is a separately scoped required follow-up before05.
No broad historical replay, provider spending, certification or release authority.

## Evidence hashes

[
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-09-app-preview.txt",
    "sha256": "6997ffb705c1c5fa984efec27d8164c9d96401110464c8e386ecce809f88569c"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-09-native-summary.json",
    "sha256": "611995f6a0234655fd211816a3b7b655d79a50540e238ff7f13e8deb79073a0a"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-09-question-probe.json",
    "sha256": "d71ef1b14470c30f9e411777a39d8d9b39a9eac23d50ded218c29199e15279d4"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-9-direct.txt",
    "sha256": "d9e7f0060f94f8cf8cd79289b21e226ea7368472d94b0aa47ba098b76482b4d5"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-9-focused.txt",
    "sha256": "1ba844229beaa347b84655a6f36589495bc754bf168205441842d003c8c83809"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-9-lint.txt",
    "sha256": "82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-9-red.txt",
    "sha256": "394f8fb2c5a61babcaeba314e733c66bc0075f7195fe52f02075d3df28c4714e"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/notes/phase-9-approval.json",
    "sha256": "ddeed5309de87d9041b77f24892d2cb7c4191f4667fbada074c350587c4364dc"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/notes/phase-9-codex-review.md",
    "sha256": "df9242fc5243581e2dbb54f74bd1fbb1f307b91939e13164262e55c727e8a243"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/notes/phase-9-lint-ruling.json",
    "sha256": "22e9f119c7de9f4a1aa5795a92eca26e2d72e9b6f6d0318415954ed15a87450a"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/notes/phase-9-spec.md",
    "sha256": "a4231f8487afe6c44b6126abb4c7f11b8b3ce5356597dbf583970797929dc5ff"
  },
  {
    "path": "src/gnd/compiled_obligations.py",
    "sha256": "068d95de141ed79ef6f02e9049f75548be4bc3c78eedfff58fa739142002b6fd"
  },
  {
    "path": "tests/test_m3_compiled_work.py",
    "sha256": "edff8310563d52db5a6346b1723215fdfc9647eab339c75512eb0f99c264d27d"
  }
]
