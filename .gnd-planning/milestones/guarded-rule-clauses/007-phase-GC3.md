---
milestone: guarded-rule-clauses
station: phase-GC3
skill: gnd:process-phase
scope: phase-GC3
date: 2026-11-15
gates:
  - command: "uv run pytest -q tests/test_guarded_disjunction.py tests/test_guarded_corpus.py tests/test_v62_phase6_limits.py tests/test_public_guarded_consequent_matrix.py tests/test_rc1_rule_ids.py tests/test_guarded_antecedent_filters.py tests/test_guarded_membership.py tests/test_model_guarded.py tests/test_public_semantic_guarded.py tests/test_guarded_diagnostics.py tests/test_v71_phase1_dates.py tests/test_derivation_rule.py tests/test_synth_guarded_cases.py tests/test_rule_verbalization.py tests/test_schema_sync.py --tb=short"
    exit: 0
    output: "629 passed in 197.45s (0:03:17)"
  - command: "uv run pytest -q tests/test_pyrel_rules.py tests/test_pyrel_rules_derivations.py tests/test_public_pyrel_export_runtime_support.py tests/test_public_lean_export_successors.py tests/test_ossie_export.py tests/test_public_souffle_successors.py --tb=short"
    exit: 0
    output: "159 passed, 93 deselected in 10.76s"
  - command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
    output: "679 passed, 2 deselected in 94.65s (0:01:34)"
  - command: "ruff check"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base main --strict"
    exit: 0
    output: "113 file(s) differ; 0 to fix, 0 warning(s), 19 to reread"
  - command: "git diff --check"
    exit: 0
evidence:
  - path: .gnd-planning/milestones/guarded-rule-clauses/notes/phase-GC3-spec.md
    sha256: 15975815f6882d8c42796d6fd2d935ef0caf300f34267073aa66636e45eb122c
  - path: .gnd-planning/milestones/guarded-rule-clauses/notes/phase-GC3-claude-review.md
    sha256: 22a189ced0e39317de5d35adfefcb555c3c3b1d8ffa4892ac693a607bced3f6e
  - path: .gnd-planning/milestones/guarded-rule-clauses/notes/GC3-review-disposition.md
    sha256: 179161d1c94be6b2c48b55709d65a3996d8367eda0c169a54668f6ca6dea1f93
  - path: .gnd-planning/milestones/guarded-rule-clauses/evidence/GC3/dynamic-query-successor.json
    sha256: 23349bc5a2030a1d42085b7fe9f975c7da889af7aa41010d633b85216d9f329c
  - path: .gnd-planning/milestones/guarded-rule-clauses/evidence/GC3/query-successor.json
    sha256: cfde10e1cd3019ce36eb91355103418b8dc6a762595f57c974216864b4db7cbc
  - path: .gnd-planning/milestones/guarded-rule-clauses/evidence/GC3/source-successors.json
    sha256: f7c5ba8f3960986d4ef468bbf20d59d891462ba86c96ea4030d1410b779dbdd4
  - path: tests/test_guarded_disjunction.py
    sha256: 3c248c3d412a619234c4f86c93b11c85f08ec49dc7d08c81f6c86953bf261adb
  - path: src/gnd/semantic_spec.py
    sha256: d1fd3086acd0ae0c8c551d12da132734c5b6f3ae5b26a096b8e4526913f02658
  - path: src/gnd/correspondence.py
    sha256: 32acec9fa007411f4d7ff3d21880037b8ce180576d7c6975df5606c13fae1b5d
  - path: src/gnd/report.schema.json
    sha256: ea7de08b57d9a0742e0d56524d00c35411d12e543e74454d97e159c892aaca62
---

# GC3 phase record

**Delegated acceptance (auto=true), 2026-11-15.** The named milestone
invocation delegates acceptance. Claude Code reviewed candidate
`20172ace`; the [review disposition](notes/GC3-review-disposition.md)
binds the repairs covered by these gates at `b89a1f00`.

- A1. The schema accepts two or more single-form alternatives and refuses
  nesting. Shared walks validate reference and role claims before local
  grounding and compatible terms. A duration conflict in shared variables
  appears once at the shared rule path.
- A2. A true sibling prevails while an existential alternative retains
  undefined candidate precedence. Indexed and reference paths match a
  semiderived union across 200 covered samples. Both paths agree at the
  exact comparison and joint-witness ceilings and on 6,000 bindings.
- A3. Opt-in diagnostics select v17 for an admitted disjunction model.
  Failed bindings pair with ordered reason records. Missing existential atoms
  carry relation names and zero-based atom indexes. Older report versions
  and existing wire fields are preserved.
- A4. CNL expresses the policy in one sentence. Synthesis generates and checks
  active fail and pass cases for a disjunction using all four forms.

The source and query successors identify two typed snapshot reads, one
wire-field read, and the opt-in text rendering delta. No new layer allowance.
Component reread entries still describe current ownership. Evidence and
census lanes remain outside the focused gate. The existing plain-report
restrictions on rule-ID and diagnostic flags apply.

GC4 owns the final exporter matrix, published explanations and installed
retail smoke. The Standard panel remains due at milestone close.
