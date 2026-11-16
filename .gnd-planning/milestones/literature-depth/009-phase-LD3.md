---
milestone: literature-depth
station: phase-LD3
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-LD3
date: 2026-11-16
gates:
  - command: "uv run --no-sync pytest -q tests/test_ld3_reading_workflow.py tests/test_li1_assurance_report.py::test_harness_reads_gnd_only_through_the_cli tests/test_li1_assurance_report.py::test_dormant_stages tests/test_li1_assurance_report.py::test_opt_in_coverage_checks_bound_rows_without_changing_legacy tests/test_li1_assurance_report.py::test_report_golden tests/test_ld1_competency_examples.py tests/test_ld2_quantities.py tests/test_lx1_flattening.py tests/test_lx4_literature_interop.py tests/test_fidelity_payload.py tests/test_public_fidelity_scope.py --tb=short"
    exit: 0
    output: "196 passed in 362.73s (0:06:02)"
  - command: "uv run --no-sync pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
    output: "679 passed, 2 deselected in 365.87s (0:06:05)"
  - command: ".venv/bin/ruff check --output-format=json"
    exit: 1
    output: "188 identical inherited diagnostics; changed Python files pass"
  - command: "python3 scripts/components_index.py changed --base a8e84ad4 --strict"
    exit: 0
    output: "0 to fix, 0 warning(s), 0 to reread"
  - command: "uv build --offline --wheel --out-dir <scratch>/dist"
    exit: 0
    output: "standalone virtualenv with locked dependencies"
  - command: "python -m gnd.examples.literature.reading run --out run"
    exit: 0
    output: "5 producer calls, 6 scheduled reads with 1 unavailable, qualifying recall 2/2"
  - command: "python -m gnd.examples.literature.reading replay run"
    exit: 0
    output: "0 producer calls, exact retained evidence identity, below-floor control at 1/2"
  - command: "claude -p --model opus --permission-mode plan --add-dir <review-dir> -- '<brief-path prompt>'"
    exit: 0
    output: "one independent review at 92086a00; VERDICT: CHANGES_REQUESTED"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: explicit owner or CI selection
  reason: affected public routes run in the focused and installed gates
evidence:
  - path: .gnd-planning/milestones/literature-depth/007-phase-LD3-spec-gate.md
    sha256: 30fbe5dfc0391a3c07375c53f7ce56dfc7b217d0b87ba67f773b5364ec52a3db
  - path: .gnd-planning/milestones/literature-depth/008-phase-LD3-amendment.md
    sha256: bc8e5de8ea6a156f17813b0c979a9628bd9b3421188f74bd3d904aa137818653
  - path: .gnd-planning/milestones/literature-depth/notes/phase-LD3-spec.md
    sha256: b8cc9faac8b28cc2b6bea9c63696e1261685cb7200ff36001c775a603ee3f8d2
  - path: .gnd-planning/milestones/literature-depth/evidence/LD3/installed-observation.json
    sha256: e6998306a9a5e8640b49bd5ea27615a3eaea6ec0a567f0286eab43429c10db41
  - path: .gnd-planning/milestones/literature-depth/evidence/LD3/review-scope.json
    sha256: b916bf69c00713ff6f42348ab68d96a11aea87e6941c418dcdb42e9be571389e
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD3-r1/BRIEF.md
    sha256: 60ce4022bffabaa818769738d69454d70dfd33f74a4d33da22fa549ca3132dce
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD3-r1/FINDINGS.md
    sha256: 9dd079745603f2cc9a252bef76cbd0c290ea565bd9aec5951f4f9903cbae5e72
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD3-r1/brief.json
    sha256: 2fbbde04424f0e6d707b60d68e11322f50eb5640c8bf6ced5bf5001ead3754f7
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD3-r1/diff.patch
    sha256: 5dcd6f56c777a49506985b53c208e2ed6d1a7711ff7ff5d7e354ebc36cce492c
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD3-r1/review.log
    sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD3-r1/review.md
    sha256: 99716e7ddb21081936ad5fcc56edcc0f2b4fe32f6240c183b22d778dd975c327
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD3-r1/run.json
    sha256: 16a1f5b9a7c6e286a4802973912248dd04fc3cd1fde5052123815fd28ade385e
  - path: src/gnd/examples/literature/reading.py
    sha256: bbe5b3318dba5f57743b90fdf238a6764b3dc10b221613ddd20f8ceb933c8b44
  - path: src/gnd/examples/literature/assurance_report.py
    sha256: a850ca5a369ae90b04cf6fd4cf94a9f5b46d51e02920a4a5e6859517c81735ee
  - path: tests/test_ld3_reading_workflow.py
    sha256: ab85094cf5db56f2edfddddc546c427cc06af9f1d9ac6a53814559a8e083d417
---

# LD3 completion

The installed multipass reader records six stages, five producer calls
and a digest-bound report. Replay rederives the original evidence without
a producer call. The broad pass leaves the method unresolved. The targeted
pass resolves it and the review distinguishes source-qualified support,
explicit denial, an inspected range without a matching assertion, an
unavailable annex and an inapplicable equation. The [installed observation](evidence/LD3/installed-observation.json) binds wheel, reports and retained
evidence.

| Criterion | Observed result |
|---|---|
| Authenticity and replay | Exact artifact roster, ordered stage authentication, bounded source reads and semantic recomputation. Rehashed coverage edits fail replay. The retained response table supports replay after deleting its fixture copy. |
| Worklist and accounting | The vocabulary edit revisits the earlier study opening only. The full run inspects 234 bytes across five attempted reads. The annex occupies one unavailable entry. Budget and unavailable-scenario controls separately exercise both stop reasons. |
| Reported conflict | The saved extraction binds both labels to an independently authored excerpt. Public verify and check each exit 1 on the resulting population. |
| Scoped absence | Public fidelity measures the actual methods extraction and an independent held-back case against gold. At 2/2 the exact scope qualifies. The 1/2 control and the changed-method regression withhold qualification. Each of the four absence bindings has an independent negative control. |
| Assurance | The shared scorer accepts real replayed coverage against independent expected rows. Legacy LI1 goldens preserve their existing scoring output. |

## Independent review

The owner authorized one Claude Code Opus review at
`92086a00f0a25fd9e467e6cd737cf2715fb64379`. The reviewer verified all
27 brief hashes and ran 89 direct and LI1 tests. Its verdict was changes
requested. The [findings ledger](notes/reviews/phase-LD3-r1/FINDINGS.md)
records all eight dispositions at `a589b5b3`. The review helper identifies
the original reviewed files and the changed repair files separately. The
author ran the focused, structural and installed verification against the
repair. The [amendment](008-phase-LD3-amendment.md) preserves the original
answer and binds the corrected revisit.

The regression against the reviewed source showed 2/2 after replacing
the targeted method. The repaired control returns 1/2. Four further
controls fail on the reviewed source at the missing retained producer
path, the unresolved supersession, the missing conflict excerpt and the
missing real-run scorer. The reviewed diff supplied the worklist and
denominator reproductions. Review verification covered the direct and
LI1 tests. Installed, structure and lint evidence come from the repair
verification.

## Refactoring review

Refactors EXECUTED. Both coverage entry points share the exact tuple
scorer. Fresh and replay use the same reading evaluator, with the retained
producer evidence supplied at the input boundary. The example retains its
public command boundaries for extract, verify, check and fidelity.

## Boundary

One independent reviewer read the original candidate. The example
establishes offline replay and exact fidelity over the declared two-case
roster. The absence observation applies to the pinned methods range and
closure. Legacy and structural verification use the default lane filter.

## Open questions

- LD4 consumes LD3's retained coverage, qualified absence inputs and
  earlier-section dependency worklist.
- The Claude prompt separator stays with the dev-tools maintainer's next
  review helper sync. This review used the locally supported separator.
- Part 10 remains deferred under the owner's scope.
