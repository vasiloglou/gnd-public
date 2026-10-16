---
milestone: analytics-m3-repairs
station: phase-6
skill: n/a -- repository development, not a gnd-solve station
scope: phase-6
date: 2026-10-13
gate:
  command: "UV_CACHE_DIR=/private/tmp/downstream-uv-cache uv run --offline pytest -q tests/test_m3_generated_json.py tests/test_population_load.py tests/test_public_transition_api_guards.py tests/test_public_transition_ir_immutability.py tests/test_public_transition_contract.py tests/test_public_transition_trace.py tests/test_transition_report.py tests/test_v70_phase4_transition.py tests/test_rf1_layering.py"
  exit: 0
  output: 148 passed in 4.44s
slow_cadence:
  command: uv run pytest -q
  trigger: explicitly selected owner or CI run
  reason: broad historical and certification lanes outside this focused repair
---

## What shipped and measured

Five generated canonical-JSON source labels gain .json; public loader signature,
strict guards and validation remain unchanged. Tests committed RED36703a0 first,
legacy and opaque controls fail for YAML dispatch; both pass with implementation.
Native full-state start baseline52.381s, candidate runs
[32.12781208398519, 32.285824250022415, 32.1113757500425], median32.128s. All exit2 and complete, input
identities unchanged; full normalized reports byte-identical. Only generated label
suffix normalized. This single start is not a completed question/held-out gate.

## Gate output and commands

UV_CACHE_DIR=/private/tmp/downstream-uv-cache uv run --offline pytest -q tests/test_m3_generated_json.py tests/test_population_load.py tests/test_public_transition_api_guards.py tests/test_public_transition_ir_immutability.py tests/test_public_transition_contract.py tests/test_public_transition_trace.py tests/test_transition_report.py tests/test_v70_phase4_transition.py tests/test_rf1_layering.py
Exit0, 148 passed in 4.44s; retained phase-6-focused.txt.
UV_CACHE_DIR=/private/tmp/downstream-uv-cache uv run --offline ruff check src/gnd/transition.py tests/test_m3_generated_json.py
Exit0, All checks passed!; phase-6-lint.txt.
App overlay: UV_CACHE_DIR=/private/tmp/downstream-uv-cache uv run --offline --package downstream-app --with-editable <GND_WORKTREE> --with rpds-py==2026.9.1 pytest -q apps/downstream-app/tests/test_fast_check.py apps/downstream-app/tests/test_source_workspace.py apps/downstream-app/tests/test_execution_budget.py apps/downstream-app/tests/test_parallel_answer.py apps/downstream-app/tests/test_checker_audit.py apps/downstream-app/tests/test_cli.py
Exit0,90 cases100%; retained app output.
Native baseline: M3_REPORT_PATH=<temporary report> UV_CACHE_DIR=/private/tmp/downstream-uv-cache uv run --offline --package downstream-app python <phase-06-native-driver.py> root --seconds 60
Candidate: same command with --with-editable <GND_WORKTREE> --with rpds-py==2026.9.1, repetitions1/2/3, exit0each. App-owned driver and receipts in M3 evidence; copied summary here.

## Review and disposition

Separate read-only Codex CLI gpt-5.5 xhigh, prompt stdin, found no blockers.
Retained sanitized output in notes/phase-6-codex-review.md. It verified all5 call
sites and nonvacuous dispatch coverage; read148 passing controls, did not run them.
Completeness observation reproduced with rg generated_decoder and ANSWERS: answer
metadata decoder field unused while hard-coded .json asserts exactdispatch.
Deferred to phase05 evidence cleanup; no semantic repair or weakened test.

## Refactoring review

None needed: this is5 format metadata corrections through the unchanged central
validating loader. A new public argument would break the pinned signature;
consistent existing suffix dispatch avoids that broader API refactor.

## Boundary and open questions

One reviewer is one reviewer. No certification, broad historical replay, paid
provider or source merge. App production pin unchanged. Phase07 indexed subset
work remains required; phase05 accepted adoption/all-development agreement/15s
question median remain pending. Completeness metadata alignment belongs phase05.
Exact native report equality is for tuning dw_5162 single start, not all candidates.

## Evidence hashes

[
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/notes/phase-6-spec.md",
    "sha256": "2adc61acbe1c45b32f760b91a059bd85e8fb62240c3fa89c5e9d1b47fc6e652c"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/notes/phase-6-approval.json",
    "sha256": "bbc76bc867397d41ed6275aebfc6cab8e6bf6238f42d5fb97ea09277ea82c432"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/notes/phase-6-answers.json",
    "sha256": "23ab28ec38c9f134097c312aea41b01e1ec93eaf30e465064a983809c91f931a"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/notes/phase-6-codex-review.md",
    "sha256": "8b7530b21c38355fd8a5805cabfe67e3db6e9a8a2d099b375d49cd70d50a07d6"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-6-focused.txt",
    "sha256": "aa53d3abb4f796c0055039d14f36bebb4c383bc8584583c3a3e5e8b601b4c61f"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-6-lint.txt",
    "sha256": "82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-6-red.txt",
    "sha256": "c2b3f234ca3500c81d31b6c8906a93a3552ce97b64d0f20ebc4e3822c4bbcd88"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-06-native-summary.json",
    "sha256": "5b49de2a6dc59892ddc97f967856c90135f5109f5cc3aee734ee1bce3485fd48"
  },
  {
    "path": ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-06-app-preview.txt",
    "sha256": "6997ffb705c1c5fa984efec27d8164c9d96401110464c8e386ecce809f88569c"
  },
  {
    "path": "tests/test_m3_generated_json.py",
    "sha256": "de93313caa39d307baed3c71214fb1941a4d6e17bdaa3b248bdc54e1f09af664"
  },
  {
    "path": "src/gnd/transition.py",
    "sha256": "03303cd71b3cdaf18ce8718a85178ebd553846b557b6e50798343a83deb8271d"
  }
]
