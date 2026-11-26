---
milestone: refactoring-followups
station: phase-F5
scope: phase-F5
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
date: 2026-11-25
gates:
  - command: uv run pytest -q tests/test_refactoring_session_contracts.py tests/test_exp_session_contract.py tests/test_exp_session_eval.py tests/test_rf1_layering.py --tb=short
    exit: 0
  - command: uv run pytest -q tests/test_rf1_session_pins.py tests/test_exp_session_e2e.py tests/test_refactoring_session_contracts.py --tb=short
    exit: 0
  - command: uv run pytest -q tests/test_refactoring_session_contracts.py --tb=short
    exit: 0
evidence:
  - path: .gnd-planning/milestones/refactoring-followups/notes/F5-Claude-review.md
    sha256: f78e6d609bb61a7cf364a3a48112a4d6f1c76e7122091aba3101008ba2bd1612
---
Delegated acceptance for #299, #303 and #304. Two rate expressions stay local to independent scoring domains. Assurance and proof retain their respective sorted identity functions, including the proof boundary. Session entry wrappers retain their names and existing shared implementation. The three identical JSON dispatchers share one implementation and preserve class dispatch, bounded decoding, bytearray and keyword behavior. The stricter contract decoder remains independent. Nine helper tests passed before edits. No public rename.

Versions 2, 3, 7 and 8 returned 74 when reusing a completed run, both with its terminal result and after removal. All experiment files and paths remained unchanged. The v3 directory collision, v2 feedback inconsistency and v7/v8 exhausted budgets explain the removed-file refusals. The documented recovery is a new run. All eight legacy versions retained their pinned evidence. Versions 6–8 allow an explicit portable-v1 prompt. The relative locator is correct for the adapter working directory. Hashes of base, controller and effective prompts agreed across roots and changed with one extra byte in the contract. The bounded descriptor read now supplies the digest for all versions. Path replacement after read leaves the original digest intact. Other evidence fields retain their existing identities.

    192 passed in 14.28s
    86 passed in 82.24s (0:01:22)
    25 passed in 20.75s

Claude requested changes. The repairs sorted imports, fixed the exit band at 74, widened the tree comparison to all paths and files in the experiment, and ran portable launch checks on v6/v7/v8. Final 25-test gate includes selector acceptance/refusal across versions and the read-once regression. The reviewer independently ran local adapter probes. Touched lint passed and component index reported zero fixes. No live adapter or independent rereview of repairs. Slow cadence: uv run pytest -q -m "evidence or census".
