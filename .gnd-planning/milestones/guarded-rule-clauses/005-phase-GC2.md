---
milestone: guarded-rule-clauses
station: phase-GC2
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-GC2
date: 2026-11-15
gates:
  - command: "uv run pytest -q tests/test_guarded_antecedent_filters.py tests/test_guarded_membership.py tests/test_model_guarded.py tests/test_public_semantic_guarded.py tests/test_guarded_diagnostics.py tests/test_v71_phase1_dates.py tests/test_derivation_rule.py tests/test_synth_guarded_cases.py tests/test_rule_verbalization.py tests/test_schema_sync.py --tb=short"
    exit: 0
    output: "462 passed in 195.52s (0:03:15)"
  - command: "uv run pytest -q tests/test_pyrel_rules.py tests/test_pyrel_rules_derivations.py tests/test_public_pyrel_export_runtime_support.py tests/test_public_lean_export_successors.py tests/test_ossie_export.py tests/test_public_souffle_successors.py --tb=short"
    exit: 0
    output: "159 passed, 93 deselected in 26.81s"
  - command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
    output: "679 passed, 2 deselected in 154.17s (0:02:34)"
  - command: "ruff check"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base main --strict"
    exit: 0
    output: "changed against main (ecd1298): 94 file(s) differ; 0 to fix, 0 warning(s), 15 to reread"
  - command: "git diff --check"
    exit: 0
    output: ""
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: explicit owner request or separately scoped CI selection
  reason: focused public tests cover the affected guarded, extension and reporting behavior
evidence:
  - path: .gnd-planning/milestones/guarded-rule-clauses/notes/phase-GC2-spec.md
    sha256: a580b9d778507471df36223230ee32225e63428145177fbeb6435085fe0a5513
  - path: .gnd-planning/milestones/guarded-rule-clauses/notes/phase-GC2-claude-review.md
    sha256: c68eb0e8f250a67e25d04f6669c31101b4f52991a84d42e8e7122e6faec79145
  - path: .gnd-planning/milestones/guarded-rule-clauses/notes/GC2-review-disposition.md
    sha256: e087af3f5daa5fda2f3610a2fa88d1070121ae59329a8a7a01b84e3169ee06cc
  - path: .gnd-planning/milestones/guarded-rule-clauses/evidence/GC2/dynamic-query-successor.json
    sha256: 432e4850a5e55b8b12c77a243f7dc0d42fde4fea0c7ae31fc98b7a126877e964
  - path: .gnd-planning/milestones/guarded-rule-clauses/evidence/GC2/query-successor.json
    sha256: 318031033e09e219eb45899076a1fa50e538478e812aabca853119afb95d3c11
  - path: src/gnd/semantic_spec.py
    sha256: 49eeffae297d193bad847a83cc03c1e5b7806bea0f64792c932cc4abc71f3730
  - path: src/gnd/semantic_adapter.py
    sha256: 07214ff0146726764329aa981e5b366ef60a5f325839454e768d0e850f4eecea
  - path: src/gnd/correspondence.py
    sha256: c89428ae3dff4ca701ffbbb6529666bfb12daa5326825211245a2b0380ee5cd9
  - path: tests/test_guarded_antecedent_filters.py
    sha256: 5f09fa36c6bd130d5b5f0efb4c5e4a414410c451a66fe45f5aa89b3923678209
---

# GC2 phase record

**Delegated acceptance (auto=true), 2026-11-15.** The owner's named
milestone invocation delegates GC2 acceptance. Claude Code supplied the
independent phase-diff review on candidate `b4e84af4`. The retained
[review and disposition](notes/GC2-review-disposition.md) identify later
fixes and measured compatibility.

## What shipped

- N1. The schema and shared guard walks cover top-level negative atoms and
  where comparisons. Positive antecedent variables bound their scopes.
  Fully grounded negative atoms apply to every binding.
- N2. Negative relations use covered claims or available calculated rows.
  The fixture distinguishes a covered consistent claim, a covered
  inconsistent claim, and an uncovered derived relation. A separate test
  exercises unavailable semiderived rows and confirms a public unchecked
  verdict. A guard adds no derivation definition or graph edge.
- N3. Indexed negative lookup distinguishes absence, a known match, and
  an unavailable absence test. Definite exclusion beats an outstanding
  unknown. The fixed-seed helper differential and reference evaluator
  agree on 200 covered populations with fail, pass and vacuous outcomes.
  The 10,000-binding control exercises indexed filtering and a separate
  threshold failure. Legacy report bytes remain pinned.
- N4. CNL renders the filters in one sentence. Guarded-cases generates two
  active outcomes for representative where and negate forms. The passing
  example with a negative exception fails when that filter is removed.

## Gate output

    uv run pytest -q tests/test_guarded_antecedent_filters.py tests/test_guarded_membership.py tests/test_model_guarded.py tests/test_public_semantic_guarded.py tests/test_guarded_diagnostics.py tests/test_v71_phase1_dates.py tests/test_derivation_rule.py tests/test_synth_guarded_cases.py tests/test_rule_verbalization.py tests/test_schema_sync.py --tb=short
    462 passed in 195.52s (0:03:15)
    exit 0

    uv run pytest -q tests/test_pyrel_rules.py tests/test_pyrel_rules_derivations.py tests/test_public_pyrel_export_runtime_support.py tests/test_public_lean_export_successors.py tests/test_ossie_export.py tests/test_public_souffle_successors.py --tb=short
    159 passed, 93 deselected in 26.81s
    exit 0

    uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short
    679 passed, 2 deselected in 154.17s (0:02:34)
    exit 0

    ruff check
    All checks passed!
    exit 0

    python3 scripts/components_index.py changed --base main --strict
    changed against main (ecd1298): 94 file(s) differ; 0 to fix, 0 warning(s), 15 to reread
    exit 0

    git diff --check
    exit 0

The component reread entries still describe their modules' behavior. The
new coverage proof uses one counted IR read and no layer allowance.

## Refactoring review

The filtered temporal route reuses temporal evaluation over surviving
bindings. Negative filtering uses the same typed row and operand
representation as the guard. Existing extension admission represents
unavailable-only calculated relations without projecting raw claims.

## Boundary

One reviewer is one reviewer. The review supplied opinions on the candidate
diff and did not execute the tests. Targeted regressions verify the subsequent
repairs. Exporter translation and the installed retail examples remain GC4
responsibilities.

## Open questions

GC3 must preserve filtering, coverage, and v16 behavior when composing
disjunctions. GC4 still owns the final profile coverage matrix.
