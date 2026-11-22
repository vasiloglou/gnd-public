---
milestone: release-0.4.0
station: phase-RV1
scope: RV1-verification
date: 2026-11-17
gates:
  - command: "uv lock --check"
    exit: 0
  - command: "uv run --no-sync python tools/release_text.py check"
    exit: 0
  - command: "uv run --no-sync pytest -q tests/test_release_version.py tests/test_recorded_version.py tests/test_marketplace_plugins.py tests/test_release_docs.py tests/test_release_preparation.py tests/test_package_description.py tests/test_release_text.py tests/test_li1_assurance_report.py tests/test_li1_literature_corpus.py tests/test_expense_receipts_example.py --tb=short"
    exit: 0
  - command: "uv run --no-sync pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
  - command: "uv run --no-sync --group docs zensical build --strict"
    exit: 0
  - command: "uv run --no-sync python tools/check_docs.py site"
    exit: 0
  - command: "uv run --no-sync ruff check"
    exit: 1
  - command: "uv run --no-sync ruff check tests/test_release_text.py tests/test_li1_assurance_report.py tests/test_li1_literature_corpus.py tests/test_expense_receipts_example.py tests/test_release_version.py"
    exit: 0
  - command: "python3 scripts/components_index.py changed --base dde52ef8 --strict"
    exit: 0
  - command: "RV1 candidate default-lane verification on beast-3"
    exit: "1, 0, 0, 0, 0, 0"
evidence:
  - path: .gnd-planning/milestones/release-0.4.0/evidence/RV1/verification-summary.txt
    sha256: 4107a51beddf4c773812f6accc47e2001ea7fd23f77b7955ace29826dd753dc4
  - path: .gnd-planning/milestones/release-0.4.0/evidence/RV1/verify-shards.sh
    sha256: 9344b5a151761dff67e8c10a0fe5d8450f82ef7fa0deda4a18b41974b108e579
---

# RV1 verification checkpoint

The implementation has passed its focused tests and default-lane comparison
against the plan baseline. RV1 completion awaits an independent diff review,
review disposition and phase record. The product edits are in the local
working tree. The tested patch from `9dc1d99f` has SHA-256
`1fadc97e40329de94bb070987b16d243b1e979a614e574f70b6c39b898f41edf`.
It yielded Git tree `1bd2f7a23429ad532b898276e63f200267fc745e` on beast-3.
The patch bytes are held locally outside Git history.

The phase synchronizes the source, lock and marketplace fields, adds prepared
release pages and retains the 0.3.0 pins. The old notes sections still match
the base bytes. The three example tests compare full outputs after existing
recorded-version normalization. The publication-text tests use an independent
tagged fixture for their mutations and retain a separate live-tree check.
The first fixture omitted a 0.2.0 historical support row. The stale-line
control caught it and the corrected fixture includes that row.

## Gate output (verbatim)

    Resolved 32 packages in 10ms
    0.4.0 is not in RELEASED: nothing to check before publication
    181 passed, 1 deselected in 107.78s (0:01:47)
    679 passed, 2 deselected in 134.75s (0:02:14)
    No issues found
    18344 local links/assets/anchors checked
    All checks passed!
    changed against dde52ef8 (dde52ef): 14 file(s) differ; 0 to fix, 0 warning(s), 0 to reread
    0.4.0 headline removal refused: the 0.4.0 notes do not open with '### Literature: identity, composition and depth'

The [shard results](evidence/RV1/verification-summary.txt) total 19,699 passed
and 13 skipped. The remaining two errors match the baseline IDs in
`test_public_optional.py` on beast-3's uv 0.13.7. All 37 E1 failures resolved.

### Repository-wide lint

The exact lint target exited 1 on both the candidate and the clean
`9458c0a1` baseline clone. That clone differs from the RV1 starting ref only
in planning artifacts. Relative path, rule, message, line and column match for
all 188 diagnostics. There are 88 per copy of the dev-tools review helper and
six per copy of the components rules checker. The supplemental changed-test
lint exits 0. The existing shared-tool findings fall outside RV1's write set.

    Base: 188. Candidate: 188. Candidate only: 0. Base only: 0.

## Refuted premises

E1 refuted the draft prediction that the version bump would leave all recorded
output comparisons green. It exercised three direct consumers of
version-bearing output that had still compared to frozen 0.3.1 bytes.
The [measured ruling](003-RV1-implementation-gate.md) records the repair.

## Boundary

Verification uses the existing default lane exclusions, and the optional wheel
setup errors retain their baseline status. Installed release acceptance
belongs to RV2. This checkpoint does not contain a reviewer opinion or a phase
completion ruling.

## Open questions

- Run the independent RV1 diff review under a separately authorized tool.
- Record the shared dev-tools lint baseline for the milestone close sweep.
