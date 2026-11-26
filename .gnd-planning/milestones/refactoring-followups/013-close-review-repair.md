---
milestone: refactoring-followups
station: milestone close repair
skill: process-milestone
scope: close-review-repair
date: 2026-11-26
---

# Repairs after independent PR review

This record supplements [012-milestone-close.md](012-milestone-close.md) (SHA-256 `62f64962142037918f0868fc74867e9199516fe1376ba0ecf60113ac0b6db05b`). It addresses the [Claude Code review of PR #310 at 63abe5ca](https://github.com/vasiloglou/gnd-public/pull/310#issuecomment-7187733274) and the RF5 source pins found in the repair checks.

- PR review F1. The compatibility guard accepts the versioned JSON method defined on the dispatcher itself or the resolved method from the shared `SessionEvidenceJson` class. The guard still flags a version dispatcher that inherits only Pydantic's JSON method. The original test passed at the PR base and failed at 63abe5ca. At the repaired tree it passes, and injecting a version dispatcher that inherits Pydantic's method makes it fail with the injected class named.
- PR review F2. The F6 table row in 012 names the empty patch hash `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`. The original brief separately pinned the full `tests/test_refactoring_pyrel_parity.py` presented to Claude at SHA-256 `c1229cc177a704e0d044a55925c5528198fbff23040d46306194cece3c1c8365`. The reviewer confirmed both hashes and read the full file. It was untracked at brief creation, which is why it was absent from the patch. [F6 review](notes/F6-Claude-review.md)
- The wider structure selection caught two stale RF5 pins. The exact historical and current hashes for `_canonical_payload` and `_cmd_exp_run` now pass through the existing successor registry. The two recorded changes are F4's finite JSON requirement and F5's digest from the validated read and opt-in portable prompt. [Source successors](evidence/close-repair/rf5-source-successors.json)

The four partial issue dispositions in 012 still apply. Merge authorization remains with the owner.

## Verification

The commands below ran in the clean review checkout with the repair applied. Earlier direct invocations used the host CLI or lacked process-inspection permission. The activated project environment and OS process access resolved those failures.

- `uv run --offline pytest -q tests/test_exp_session_evidence_compat.py tests/test_exp_session_eval.py tests/test_exp_session_contract.py tests/test_refactoring_session_contracts.py tests/test_refactoring_pyrel_parity.py tests/test_rf1_session_pins.py tests/test_rf1_pin_harness.py --tb=short` exited 0.

      251 passed in 265.23s (0:04:25)

- `uv run --offline pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py tests/test_install.py tests/test_doctor_uninstall.py tests/test_verification_fixes.py tests/test_inventory_pin_home.py --tb=short` exited 0.

      866 passed, 2 deselected in 464.09s (0:07:44)

- `.venv/bin/ruff check` exited 0.

      All checks passed!
