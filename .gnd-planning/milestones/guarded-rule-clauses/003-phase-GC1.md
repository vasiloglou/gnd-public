---
milestone: guarded-rule-clauses
station: phase-GC1
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-GC1
date: 2026-11-15
gates:
  - command: "uv run pytest -q tests/test_guarded_membership.py tests/test_model_guarded.py tests/test_public_guarded_consequent_matrix.py tests/test_public_semantic_guarded.py tests/test_derivation_rule.py tests/test_synth_guarded_cases.py tests/test_rule_verbalization.py tests/test_schema_sync.py --tb=short"
    exit: 0
    output: "332 passed in 95.26s (0:01:35)"
  - command: "uv run pytest -q tests/test_pyrel_rules.py tests/test_pyrel_rules_derivations.py tests/test_public_pyrel_export_runtime_support.py tests/test_public_lean_export_successors.py tests/test_ossie_export.py tests/test_public_souffle_successors.py --tb=short"
    exit: 0
    output: "159 passed, 93 deselected in 8.98s"
  - command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
    output: "679 passed, 2 deselected in 115.16s (0:01:55)"
  - command: "ruff check"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base main --strict"
    exit: 0
    output: "changed against main (ecd1298): 82 file(s) differ; 0 to fix, 0 warning(s), 11 to reread"
  - command: "git diff --check"
    exit: 0
    output: ""
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: explicit owner request or separately scoped CI selection
  reason: focused public tests cover affected behavior
evidence:
  - path: .gnd-planning/milestones/guarded-rule-clauses/notes/phase-GC1-spec.md
    sha256: f8e9a7505b0bad2c64c64428c274ce827da834758b0c08ffbc4932819e413888
  - path: .gnd-planning/milestones/guarded-rule-clauses/notes/phase-GC1-claude-review.md
    sha256: 35974cf251c42290f984c5fcdfb5692a5bc8e1d3de2983cf038afef134363107
  - path: .gnd-planning/milestones/guarded-rule-clauses/notes/GC1-review-disposition.md
    sha256: b784bddc3c4a03545da827fe4392eb2db38cfe475202549b3ddc7376724275a0
  - path: .gnd-planning/milestones/guarded-rule-clauses/evidence/GC1/dynamic-query-successor.json
    sha256: 65d0c4294dc5972a50cdcda7b66115423ff1c405b34a2064d962ad51cfb31cc0
  - path: tests/test_guarded_membership.py
    sha256: 6e66f9acf9b16cd0a860defbe227cd61d87b72f44e012276a9fb672ef3ce4b76
  - path: src/gnd/terms.py
    sha256: 0d1b03541f33593c4d696b0a3676bac86a4469dae8f439ce653c66fb9f8d771d
  - path: src/gnd/extensions.py
    sha256: 14e5f5e3f4d6a9bdfd5c648c3faeab66841517bcdf88c6f9c403dddf9d445be5
  - path: src/gnd/schema/orm-meta.schema.json
    sha256: da86267d3b5f41d5794c96ddb361a3a14d704eb8565c986050dfbf83f8d9b659
---

# GC1 phase record

**Delegated acceptance (auto=true), 2026-11-15.** The milestone invocation
delegates acceptance of the GC1 implementation and evidence in this commit.
The owner selected Claude Code for independent phase review.

## What shipped

- I1. The two membership operators use a dedicated bounded schema arm in
  guarded and term comparisons. Model validation rejects incompatible lists
  and locates duplicate and value-domain diagnostics.
- I2. Guarded reference and production evaluation, exact and temporal term
  filters, and derivation checks implement the declared typed identity.
  Comparable numeric spellings share an identity. Cross-domain runtime inputs
  preserve undecidability.
- I3. The seeded independent helper encoding matches verdicts and projected
  offending subjects across 200 covered, decided populations per operator.
  Both satisfied and violated outcomes occur in each run.
- I4. Guarded syntax and CNL describe membership directly. Synthesis emits
  both verdicts when reached and uses the existing finite Boolean refusal
  codes for one-sided domains.
- I5. Export profiles preserve explicit unsupported boundaries. PyRel
  reference admission precedes its capability refusal; Lean and Soufflé
  return a named membership refusal.

## Gate output

    uv run pytest -q tests/test_guarded_membership.py tests/test_model_guarded.py tests/test_public_guarded_consequent_matrix.py tests/test_public_semantic_guarded.py tests/test_derivation_rule.py tests/test_synth_guarded_cases.py tests/test_rule_verbalization.py tests/test_schema_sync.py --tb=short
    332 passed in 95.26s (0:01:35)
    exit 0

    uv run pytest -q tests/test_pyrel_rules.py tests/test_pyrel_rules_derivations.py tests/test_public_pyrel_export_runtime_support.py tests/test_public_lean_export_successors.py tests/test_ossie_export.py tests/test_public_souffle_successors.py --tb=short
    159 passed, 93 deselected in 8.98s
    exit 0

    uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short
    679 passed, 2 deselected in 115.16s (0:01:55)
    exit 0

    ruff check
    All checks passed!
    exit 0

    python3 scripts/components_index.py changed --base main --strict
    changed against main (ecd1298): 82 file(s) differ; 0 to fix, 0 warning(s), 11 to reread
    exit 0

    git diff --check

    exit 0

The exporter gate ran in the local runner that preserves the mode expected
by the pre-existing fake-tool test. The two timed-out review attempts
have no response. The successful review and reproductions are recorded
in the [review disposition](notes/GC1-review-disposition.md).

## Refactoring review

Consolidated membership list and operand preparation in one derivation
preparer. The same declared primitive analysis now feeds validation and
runtime, and each clause's compiled set is retained during fixpoint
iterations. Membership refusal and diagnostics reuse the existing schema,
guarded comparison, extension and exporter boundaries.

## Boundary

One reviewer is one reviewer. The independent Claude review covered the
supplied candidate diff. Current tests and negative controls cover the
subsequent fixes. The fixed-seed differential covers the declared comparable
population domain. Runtime exporter support is deferred to GC4.

## Open questions

GC2 must preserve GC1 membership behavior in antecedent filters. GC4 owns
the final installed-candidate and exporter translation matrix.
