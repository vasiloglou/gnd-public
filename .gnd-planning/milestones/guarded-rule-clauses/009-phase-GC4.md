---
milestone: guarded-rule-clauses
station: phase-GC4
skill: gnd:process-phase
scope: phase-GC4
date: 2026-11-15
gates:
  - command: "GND_PYREL_PYTHON=<pinned-local-runtime> uv run pytest -q tests/test_guarded_clause_exports.py tests/test_guarded_disjunction.py tests/test_guarded_corpus.py tests/test_v62_phase6_limits.py tests/test_public_guarded_consequent_matrix.py tests/test_rc1_rule_ids.py tests/test_guarded_antecedent_filters.py tests/test_guarded_membership.py tests/test_model_guarded.py tests/test_public_semantic_guarded.py tests/test_guarded_diagnostics.py tests/test_v71_phase1_dates.py tests/test_derivation_rule.py tests/test_synth_guarded_cases.py tests/test_rule_verbalization.py tests/test_schema_sync.py --tb=short"
    exit: 0
    output: "653 passed in 220.59s (0:03:40)"
  - command: "uv run pytest -q tests/test_pyrel_rules.py tests/test_pyrel_rules_derivations.py tests/test_public_pyrel_export_runtime_support.py tests/test_public_lean_export_successors.py tests/test_ossie_export.py tests/test_public_souffle_successors.py --tb=short"
    exit: 0
    output: "159 passed, 93 deselected in 10.46s"
  - command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
    output: "679 passed, 2 deselected in 98.47s (0:01:38)"
  - command: "uv run pytest -q tests/test_documentation_tutorials.py --tb=short"
    exit: 0
    output: "98 passed in 89.35s (0:01:29)"
  - command: "zensical build --strict"
    exit: 0
    output: "Build started\nNo issues found\nBuild finished in 0.56s"
  - command: "python tools/check_docs.py site"
    exit: 0
    output: "17552 local links/assets/anchors checked"
  - command: "python tools/run_tutorials.py --group bookrec --lane offline --python <candidate>/venv/bin/python --receipt <scratch>/bookrec.json"
    exit: 0
    output: "99 tutorial blocks passed"
  - command: "python tools/run_tutorials.py --group rule-check --lane offline --python <candidate>/venv/bin/python --receipt <scratch>/rule-check.json"
    exit: 0
    output: "7 tutorial blocks passed"
  - command: "uv build --wheel --offline; install locked synth extra and run evidence/GC4/installed-smoke.py with isolated Python"
    exit: 0
    output: "Retail smoke completed with exit 0 and wrote installed-smoke.json"
  - command: "ruff check"
    exit: 0
    output: "All checks passed!"
  - command: "python scripts/components_index.py changed --base main --strict"
    exit: 0
    output: "135 file(s) differ; 0 to fix, 0 warning(s), 20 to reread"
  - command: "git diff --check"
    exit: 0
    output: ""
evidence:
  - path: .gnd-planning/milestones/guarded-rule-clauses/notes/phase-GC4-spec.md
    sha256: 5090aeb767d22a67a34c0c7aa41a41fa83a668be3ef79b33bb7dcada4b2fc238
  - path: .gnd-planning/milestones/guarded-rule-clauses/notes/phase-GC4-claude-review.md
    sha256: 856d833fc1734ef61d175eb8cd9731e6641af23a7061246b51fbeab3a43dd22a
  - path: .gnd-planning/milestones/guarded-rule-clauses/notes/GC4-review-disposition.md
    sha256: 5c91671a88237b15ed8ccb9d1693a1f868dd9ebdb1ba056e8c5868cd4da72899
  - path: .gnd-planning/milestones/guarded-rule-clauses/evidence/GC4/dynamic-query-successor.json
    sha256: 371a612771c73cad1bf16d96d26716c483154a2b2582eef76415d93cc1e4c044
  - path: .gnd-planning/milestones/guarded-rule-clauses/evidence/GC4/installed-smoke-replay.md
    sha256: 421ce08b88233cb6e462a9a17b05975d8e5301c7b0f6b3697f9a35219fc45a2e
  - path: .gnd-planning/milestones/guarded-rule-clauses/evidence/GC4/installed-smoke.json
    sha256: 3ff066d6d5160b5e8938a81fac7c7dd8e4cb80d5a09b6070105c887bbe0fa535
  - path: .gnd-planning/milestones/guarded-rule-clauses/evidence/GC4/installed-smoke.py
    sha256: d6b9ce615b3a610edd2a93be33c1e926a743248f79b61822c5e486b84a33d1ce
  - path: .gnd-planning/milestones/guarded-rule-clauses/evidence/GC4/query-successor.json
    sha256: 9ec679ad282648415cd69d3d6296d6ea476596ae38f15a2ca74bf914be4e43c2
  - path: .gnd-planning/milestones/guarded-rule-clauses/evidence/GC4/retail-model.json
    sha256: a0626d5985b89b7bf360d7686fae03fdf9ebf6f30d78a06022f9515decc93f7e
  - path: src/gnd/export/emit.py
    sha256: d0b7dab956b88d2da31d37f5c6bb5476636296a093958fcf9732cc998e6b7e77
  - path: src/gnd/export/pyrel_rules.py
    sha256: 0361808da0ece68fccdcf82298b2f43bd8d6d051edb696e49543e2f97941f62d
  - path: src/gnd/export/ossie.py
    sha256: 5bfe866e4df42237e7e528885c0cf27e4916e6c8051c4a40231b24c4bb0b6c0e
  - path: tests/test_guarded_clause_exports.py
    sha256: 451bd1790133d6d49dc9ef11283ec9e8aa1980898b42c928afcd948bd915c381
  - path: docs/bookrec/08-guarded-rules.md
    sha256: 6218f66981fd9da9449100e3f57e6eba67128a1e479707714b2b10b4f5708cf8
  - path: docs/reference/rule-check-report.md
    sha256: 7ad8a55c15a09de8a46e5accabb1c68eb0c04a71775faca38a61c59e5b8b4b65
---

# GC4 phase record

**Delegated acceptance (auto=true), 2026-11-15.** The named milestone
invocation delegates acceptance. The independent Claude Code review
covered `f446f350`, with the [recorded disposition](notes/GC4-review-disposition.md)
and measured post-review results at `6cd2e5df`. The final gates exited 0.

## What shipped

- E1. Readable PyRel membership uses an emitted typed finite relation.
  Antecedent filters lower to relation absence and bound scalar comparisons.
  Local DuckDB decisions agree on covered and uncovered inputs for the
  measured cases. LQP compilation accounts for each enforceable requirement.
  Embedded PyRel, unsupported readable terms, and finite export profiles
  use named refusals. Ossie has explicit loss metadata and strict refusals.
  The predecessor byte pins and existing exporter tests passed.
- E2. The ORM representation, CLI and rule-check report explain the
  feature and its diagnostics. BookRec uses one rule with an exception and
  alternatives. Packaged authoring guides point to the normative format.
  The packaged link inventory and strict site build passed.
- E3. The wheel smoke runs all retail conditions against the installed
  package. The corpus checks A and S membership, warning for C, both
  delivery branches, missing confirmation, and the two-atom account
  control. The shipped-code exception gives vacuity after binding
  exclusion. Feedback names the original declared rules.

## Gate output

    GND_PYREL_PYTHON=<pinned-local-runtime> uv run pytest -q tests/test_guarded_clause_exports.py tests/test_guarded_disjunction.py tests/test_guarded_corpus.py tests/test_v62_phase6_limits.py tests/test_public_guarded_consequent_matrix.py tests/test_rc1_rule_ids.py tests/test_guarded_antecedent_filters.py tests/test_guarded_membership.py tests/test_model_guarded.py tests/test_public_semantic_guarded.py tests/test_guarded_diagnostics.py tests/test_v71_phase1_dates.py tests/test_derivation_rule.py tests/test_synth_guarded_cases.py tests/test_rule_verbalization.py tests/test_schema_sync.py --tb=short
    653 passed in 220.59s (0:03:40)
    exit 0

    uv run pytest -q tests/test_pyrel_rules.py tests/test_pyrel_rules_derivations.py tests/test_public_pyrel_export_runtime_support.py tests/test_public_lean_export_successors.py tests/test_ossie_export.py tests/test_public_souffle_successors.py --tb=short
    159 passed, 93 deselected in 10.46s
    exit 0

    uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short
    679 passed, 2 deselected in 98.47s (0:01:38)
    exit 0

    uv run pytest -q tests/test_documentation_tutorials.py --tb=short
    98 passed in 89.35s (0:01:29)
    exit 0

    zensical build --strict
    Build started
    No issues found
    Build finished in 0.56s
    exit 0

    python tools/check_docs.py site
    17552 local links/assets/anchors checked
    exit 0

    python tools/run_tutorials.py --group bookrec --lane offline --python <candidate>/venv/bin/python --receipt <scratch>/bookrec.json
    99 tutorial blocks passed
    exit 0

    python tools/run_tutorials.py --group rule-check --lane offline --python <candidate>/venv/bin/python --receipt <scratch>/rule-check.json
    7 tutorial blocks passed
    exit 0

    uv build --wheel --offline; install locked synth extra and run evidence/GC4/installed-smoke.py with isolated Python
    Retail smoke completed with exit 0 and wrote installed-smoke.json
    exit 0

    ruff check
    All checks passed!
    exit 0

    python scripts/components_index.py changed --base main --strict
    135 file(s) differ; 0 to fix, 0 warning(s), 20 to reread
    exit 0

## Refactoring review

Readable rule filtering reuses the requirement, comparison, atom and
literal relation renderers. Each export route uses the canonical derivation
clause walk. The embedded checker template remains byte-stable. The source
and dynamic query deltas identify the admitted export traversal.

## Boundary

The source build and native checks cover the selected local PyRel
1.30.1 and DuckDB 1.5.5 fragments. Local LQP compilation checks the
translation. Remote engine enforcement remains outside the phase gate.
The installed wheel identifies this local candidate by hash.

## Open questions

The milestone close audit records the final issue-to-criterion sweep and
the profile and synthesis decisions. The Standard panel is the independent
close instrument.
