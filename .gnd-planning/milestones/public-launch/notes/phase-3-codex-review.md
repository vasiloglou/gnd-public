# Phase 3 — independent Codex CLI review

2026-10-03, gpt-6-astra/xhigh, ephemeral read-only CLI with prompt on stdin.
One reviewer is one reviewer. The response below is retained verbatim except
absolute target file links are converted to plain repository citations and
absolute target paths normalized to <TARGET>. No panel or repaired-byte approval
is implied. The exact reviewed range is retained in the response.

Two findings survived review of `cf4c1d7..bb14d18`.

1. **Blocking — severity: medium. Retained-wheel checks can miss broken packaged skill references.** `tests/test_release_acceptance.py:65` checks the number of `SKILL.md` files but not their resource closure. The contributor checks selected at `tests/test_release_acceptance.py:197` validate links under the archived checkout’s `src/gnd/skills`, rather than the installed package (`tests/test_contributor_preparation.py:36`). An in-memory probe removed `gnd/skills/gnd-review-panel/references/review-contract.md` from both wheel archives; the retained identity test still passed. Installer lifecycle checks copy the available resources without establishing completeness. Run the existing resource-inventory and link-resolution protections against both retained installations.

2. **Hardening — severity: medium. Collection-time skips escape the installed acceptance gate.** The plugin at `tests/test_release_acceptance.py:180` observes only `pytest_runtest_logreport`. Module-level `pytest.importorskip()` or `pytest.skip(..., allow_module_level=True)` produces a collection report instead. If another test passes, the acceptance predicate permits success. A read-only hook probe reproduced `passed=1, skips=[]` after a skipped collection report. Capture collection skips and add a negative control. I did not identify an existing collection-time skip in the selected modules.

The inspected workflow requires all upstream job groups to succeed, checks candidate/head agreement, and enables no publication. The root-anchored ignore fix is appropriate. All ten imported reference-corpus files match their source bytes; the runner differences are the documented paths and historical registration exclusions. I found no weakened product predicate in the sampled modified tests.

Coverage was architectural and sampled across the 996-file diff, not exhaustive historical-test review. I ran read-only comparisons and in-memory probes; I did **not** run pytest, installation/build tests, the full suite, or hosted profiles. The reported earlier passes and ignore-test red/green result were not independently rerun. Remote protection remains separately observed evidence; this review establishes neither phase completion nor assurance.
