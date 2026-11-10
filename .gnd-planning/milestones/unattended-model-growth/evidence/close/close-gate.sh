#!/usr/bin/env bash
# UG close gate: the union of the UG1 to UG4 phase gates and their impact closures
# (107 test modules), the full tutorial run, the strict site build, the link check, and
# ruff over the milestone's changed Python. Run from the repository root.
set -o pipefail
cd "$(git rev-parse --show-toplevel)"
T=$(cat <<'L'
tests/support/offline_roots.py
tests/support/rf5_sources.py
tests/support/runtime_schema_inventory.py
tests/test_atom_bind.py
tests/test_compiled_snapshot_obligations.py
tests/test_conformance_payload.py
tests/test_coverage_cli.py
tests/test_digest_helpers.py
tests/test_disclosure_mode.py
tests/test_discover.py
tests/test_discover_fact_type_family.py
tests/test_discover_type_judgements.py
tests/test_doctor_uninstall.py
tests/test_documentation_tutorials.py
tests/test_evolution_conformance.py
tests/test_evolve_additive_policy.py
tests/test_evolve_loading.py
tests/test_evolve_population_check.py
tests/test_evolve_references.py
tests/test_evolve_shape_matches.py
tests/test_evolve_source_document.py
tests/test_exp_bands.py
tests/test_exp_session_eval.py
tests/test_fu1_term_reasons.py
tests/test_fu3_derived_ring.py
tests/test_gnd_arch.py
tests/test_growth_example.py
tests/test_ik6_skill_census.py
tests/test_ik_close.py
tests/test_il6_skill_census.py
tests/test_ilp_amie.py
tests/test_ilp_bridge.py
tests/test_induced_provenance.py
tests/test_install.py
tests/test_judge_fact_types_skill.py
tests/test_measure_offline.py
tests/test_model_evolution.py
tests/test_model_multivalued_skill.py
tests/test_model_v2.py
tests/test_object_type_description.py
tests/test_packaged_skills.py
tests/test_public_admission_schema_mutations.py
tests/test_public_binding_graphs.py
tests/test_public_binding_prose.py
tests/test_public_binding_reports.py
tests/test_public_binding_rosters.py
tests/test_public_book_boundaries.py
tests/test_public_book_identity.py
tests/test_public_book_population_publish.py
tests/test_public_book_runtime.py
tests/test_public_built_inventory.py
tests/test_public_corpus_integration_support.py
tests/test_public_derivation_evaluation_complete.py
tests/test_public_distribution_runtime.py
tests/test_public_evolution_drift_readers.py
tests/test_public_evolution_legacy_readers.py
tests/test_public_evolution_version_graph.py
tests/test_public_example_guards.py
tests/test_public_example_projections.py
tests/test_public_expense_guards.py
tests/test_public_guarded_consequent_matrix.py
tests/test_public_installer.py
tests/test_public_plan_contract.py
tests/test_public_report_redaction_metadata.py
tests/test_public_report_v8_preservation.py
tests/test_public_scope_boundary_guards.py
tests/test_public_transition_api_guards.py
tests/test_public_transition_walks.py
tests/test_public_v70_wire_guard.py
tests/test_public_v72_ownership_direct.py
tests/test_pyrel_learning_path.py
tests/test_rc1_rule_ids.py
tests/test_rc2_acyclic_extent.py
tests/test_rc3_baseline.py
tests/test_rc4_allow_vacuous.py
tests/test_recovery_adversarial.py
tests/test_recovery_report.py
tests/test_reference_population_corpus.py
tests/test_report_json.py
tests/test_rf1_cli_pins.py
tests/test_rf1_helper_pins.py
tests/test_rf1_layering.py
tests/test_rf1_pin_harness.py
tests/test_rf2_helpers.py
tests/test_rf6_packages.py
tests/test_rf6_query_policy.py
tests/test_rf7_consumers.py
tests/test_rof4_accept_identities.py
tests/test_schema_sync.py
tests/test_skill_prose_sync.py
tests/test_transition_report.py
tests/test_unattended_growth_guidance.py
tests/test_unattended_mode.py
tests/test_unattended_model_growth_acceptance.py
tests/test_unattended_span_coverage.py
tests/test_v61_phase1_batch.py
tests/test_v61_phase4_projection.py
tests/test_v61_phase4_review_regressions.py
tests/test_v62_phase2_report.py
tests/test_v6_phase6_report.py
tests/test_v70_phase3_opaque.py
tests/test_v70_phase3_successors.py
tests/test_v70_phase4_transition.py
tests/test_v70_phase4_wire.py
tests/test_v71_phase1_successors.py
tests/test_verification_fixes.py
tests/test_verify_cli.py
L
)
ls $T >/dev/null || exit 9
uv run pytest -q -p no:cacheprovider $T 2>&1 | grep -E "^FAILED|^ERROR|passed|failed"
echo "pytest exit ${PIPESTATUS[0]}"
uv run python tools/run_tutorials.py 2>&1 | tail -1
uv run --group docs zensical build --strict 2>&1 | tail -1
uv run python tools/check_docs.py site 2>&1 | tail -1
uv run ruff check src/gnd/api.py src/gnd/commands/checking.py src/gnd/commands/evolve.py src/gnd/model/__init__.py src/gnd/model/_unattended.py src/gnd/evolve tests/test_unattended_model_growth_acceptance.py tests/test_evolve_population_check.py tests/test_unattended_span_coverage.py tests/test_evolve_source_document.py tests/test_unattended_growth_guidance.py tests/test_rf1_cli_pins.py tests/support/pyrel_application_successors.py .gnd-planning/milestones/unattended-model-growth/evidence/close/capture_parity.py 2>&1 | tail -1
