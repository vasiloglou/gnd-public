---
milestone: analytics-m3-repairs
station: phase-7
skill: n/a -- repository development, not a gnd-solve station
scope: phase-7
date: 2026-10-13
gate:
  command: "UV_CACHE_DIR=/private/tmp/downstream-uv-cache uv run --offline pytest -q tests/test_m3_indexed_subset.py tests/test_m3_generated_json.py tests/test_public_branch_runtime.py tests/test_public_correspondence_projection.py tests/test_public_semantic_adapter.py tests/test_public_semantic_composition.py tests/test_rf6_registry.py tests/test_rf1_layering.py tests/test_public_transition_contract.py tests/test_transition_report.py tests/test_v70_phase4_transition.py"
  exit: 0
  output: 1172 passed in 24.37s
slow_cadence:
  command: uv run pytest -q
  trigger: explicitly selected owner or CI run
  reason: broad historical/proof/certification lanes outside selected impact closure
---

## What shipped

Optional Family.production hook defaultsNone; only subset registers indexed
production verdict. Common applicability/refusal, opaque override, public origin
projection and branch recording remain unchanged. Each sequence projected once,
right identity membership indexed, canonical left-only witnesses computed once.
Uses existing typed scalar identity and canonical ordering; pure semantic_spec
unchanged, equality/exclusion remain sibling controls. Both source mirror rules
retained. Corpus-first RED2086e61,16 intended failures/3 existing scalar controls.

## Gates and evidence

UV_CACHE_DIR=/private/tmp/downstream-uv-cache uv run --offline pytest -q tests/test_m3_indexed_subset.py tests/test_m3_generated_json.py tests/test_public_branch_runtime.py tests/test_public_correspondence_projection.py tests/test_public_semantic_adapter.py tests/test_public_semantic_composition.py tests/test_rf6_registry.py tests/test_rf1_layering.py tests/test_public_transition_contract.py tests/test_transition_report.py tests/test_v70_phase4_transition.py
Exit0,1172 passed in 24.37s, phase-7-focused.txt.
UV_CACHE_DIR=/private/tmp/downstream-uv-cache uv run --offline pytest -q tests/test_m3_indexed_subset.py
After review instrument regression, exit0,20 passed in 1.71s (actual output retained
in phase-7-review-green.txt; includes original19 and added work-counter control).
UV_CACHE_DIR=/private/tmp/downstream-uv-cache uv run --offline ruff check src/gnd/semantic_rows.py src/gnd/constraint_families.py src/gnd/correspondence.py tests/test_m3_indexed_subset.py .gnd-planning/milestones/analytics-m3-repairs/evidence/phase-7-native-layer.py
Exit0,All checks passed!; phase-7-final-lint.txt.
App phase06 overlay command repeated with both fixes:90 cases100%,exit0,
phase-07-app-preview.txt. Pin unchanged.

Native exact commands use app-owned phase-06-native-driver.py: baseline check
--with-editable <PARSER_BASELINE> at9993750 and candidate --with-editable
<GND_WORKTREE>, --with rpds-py==2026.9.1, root/check --seconds60, same app
uv workspace/Python3.13. Each exit0, APIexit2, reports byte-identical (onlyphase06
.json diagnostic normalization). Check7.864→1.315s;
root repeats[12.325068709033076, 12.288108207983896, 12.41559883399168], median12.325s,
parser-only median32.128s. All native input hashes match.
UV_CACHE_DIR=/private/tmp/downstream-uv-cache uv run --offline python .gnd-planning/milestones/analytics-m3-repairs/evidence/phase-7-native-layer.py <APP_WORKSPACE>/.downstream-app/local/beast-2/m3-full-state
Exit0. Both mirrors2119rows on each side, exact pure oracle pass;8476 actual
identity calls vs16952 bound each, indexed layer~0.0017s,15s alarm percall.
No generated large domain data. No report-row/data contents committed.

## Independent review and dispositions

Separate Codex CLI gpt-5.5 xhigh read-only, stdinprompt; one reviewer is one reviewer.
Review found no production semantic defect. Initial blocking missing retained
native results reflected measurement still inprogress: now outputs/hashes retained.
Hardening counter missed private canonical alias: reproduced0vs2 in reviewerRED
f0a9348; counter patches/restores bothaliases,20-casegreen; retained follow-up
review confirmsclosed. Completeness red whitespace corrected, diffcheckclean.
Native script initially selected IDs instead of IR locatorrefs and failed its
len2 guard; mapped unchanged top-level constraints indices to actual IDs, both
results confirmed. No expected semantic answerchanged. Reviewer could not recompute
external raw-data hashes or rerun tests; parent commands did. All referenced files
included in this record/commit, resolving prior untracked-evidence boundary.

## Refactoring review

Refactors EXECUTED: registered optional production optimization through existing
family registry, reusing existing shared row/identity helper home. No parallel
app evaluator, no private source copy, no new module/layer exceptions or shim
retirement. Common semantics remain outside the family-specific membership lane.

## Boundary and open questions

No broad historical replay, certification, release or upstream merge. App pin
stillfa926ae, adoption pending owner acceptance. Phase05 exhaustive109question cap8
agreement and29held-out15s successful median remain unmet. Native single start
12.325s is not an entire8-candidate answer. Fresh tuning-only complete-answer
probe hit120s parent wall cap, no completed result; further scoped M3 performance
work required before finalgate. No held-out tuning or sealed438test access, cost0.

## Evidence hashes

[
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/notes/phase-7-approval.json",
    "sha256": "9c699b2c9c27ba3a50fa1012fd8e9b2a0339c68cdba8f82138680295f6f8c659"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/notes/phase-7-codex-followup-review.md",
    "sha256": "e99148cd3b887d59529adc896fef6de7d35bf83132abb0ce7bd3156cf034e4cd"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/notes/phase-7-codex-review.md",
    "sha256": "4192b81d5eb877defce126d2dad0e662b2ea4098ea81575a8f7c9d74abc8da33"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/notes/phase-7-review-ruling.json",
    "sha256": "2c0b6791be5979dd2ee28ade8ad44b0e9c895b46d5857650a7013f20aedef49b"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/notes/phase-7-spec.md",
    "sha256": "3e82264fd02c24508ac6923d1596532597f8f9daed47b6f9208bb559bc48616e"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-7-direct.txt",
    "sha256": "fae0f120c0eb0586be551d5a26f426ce69d516ccf497eff8cec792f3116c3019"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-7-final-lint.txt",
    "sha256": "82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-7-focused.txt",
    "sha256": "47b0d66c14e3547d07bbb6421a507104748c4e3ca49b5db2607c2d439a082077"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-7-lint.txt",
    "sha256": "82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-7-native-layer.json",
    "sha256": "b7ac6cc6c64bb511c3195848d6707a58bece7a49ea681f4b8fc82ad1a71ef65b"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-7-native-layer.py",
    "sha256": "0551113ff11c9695209664be506188722e3a73def6cab8c68009e7a9ddb9b3a3"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-7-red.txt",
    "sha256": "404ca6a7061f9eaf06c86946240ed7595981dcadce94ba1fd92813b5bc15a810"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-7-review-green.txt",
    "sha256": "f0519417877edcda966f57485e25bd5de6f7e5081393f347ce2ee60c28a3fa6a"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-7-review-red.txt",
    "sha256": "31e7d68f09dbb0bf480da0fd496d7592f83a32a9979a5c5f5d8ded0bd6613fa3"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-07-native-summary.json",
    "sha256": "e8588c47e6a9f637e2f33b922f56b0eafbf08007c791845f672de58213283e68"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-07-app-preview.txt",
    "sha256": "6997ffb705c1c5fa984efec27d8164c9d96401110464c8e386ecce809f88569c"
  },
  {
    "path": "tests/test_m3_indexed_subset.py",
    "sha256": "bd3109b97d953508c5fa808458ce8ee813c85fae9f61f479e36ae1744415e729"
  },
  {
    "path": "src/gnd/semantic_rows.py",
    "sha256": "1257f0399a6e65d4a605497229bc66b57c4d40aeaa8d9d8db9edfb8c376af9f5"
  },
  {
    "path": "src/gnd/correspondence.py",
    "sha256": "e8558de8178f734bf628d9caeb5e4e00a95b2215c99ed441d1c66cd854c538e9"
  },
  {
    "path": "src/gnd/constraint_families.py",
    "sha256": "13bd449715a2e226ac9df62ad66fa867a9888d620e2687fa372a0f4e4dcc6b5b"
  }
]
