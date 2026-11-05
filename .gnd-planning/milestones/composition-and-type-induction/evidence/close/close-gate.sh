# composition-and-type-induction close gate: the union of the CT1 to CT4 gates
# (CT3's witness-test selection is recomputed), the CT5 docs gates and ruff.
set -o pipefail
cd "$(git rev-parse --show-toplevel)"
T="tests/test_anchor_sidecar_v2.py tests/test_composition.py tests/test_conformance_payload.py tests/test_disclosure_docs.py tests/test_disclosure_mode.py tests/test_discover.py tests/test_discover_fact_type_family.py tests/test_evolve_additive_policy.py tests/test_evolve_shape_matches.py tests/test_gnd_arch.py tests/test_ike_q3.py tests/test_incremental_sessions.py tests/test_packaged_skills.py tests/test_public_api.py tests/test_public_built_inventory.py tests/test_public_extraction_prose_policy.py tests/test_public_optional_value_witness.py tests/test_public_replay_admission.py tests/test_public_replay_driver_support.py tests/test_public_runtime.py tests/test_public_v71_witness_corpus.py tests/test_rf1_cli_pins.py tests/test_rf1_layering.py tests/test_rf1_pin_harness.py tests/test_rf1_semantic_pins.py tests/test_rf6_query_policy.py tests/test_schema_sync.py tests/test_skill_prose_sync.py tests/test_v61_phase2_api.py tests/test_v70_phase1_adversarial.py tests/test_v70_phase1_surfaces.py tests/test_v70_phase5_adversarial.py tests/test_v70_phase5_corpus.py tests/test_why_not_near_misses_public.py  tests/test_composition_example.py tests/test_witness_composition.py tests/test_development_scaffold.py $(grep -rl 'gnd.witness\|api.witness\|api.replay' tests/*.py)"
T=$(printf '%s\n' $T | sort -u | tr '\n' ' ')
ls $T >/dev/null || exit 9
uv run pytest -q $T 2>&1 | grep -E "^FAILED|passed|failed"
uv run pytest -q -m distribution tests/test_public_built_inventory.py 2>&1 | tail -1
uv run python tools/run_tutorials.py 2>&1 | tail -1
uv run --group docs zensical build --strict 2>&1 | tail -1
uv run python tools/check_docs.py site 2>&1 | tail -1
uv run ruff check src/gnd/anchors.py src/gnd/composition.py src/gnd/checking_service.py src/gnd/api.py src/gnd/commands/checking.py src/gnd/witness src/gnd/discover tools/build_composition_example.py tests/test_composition.py tests/test_composition_example.py tests/test_witness_composition.py tests/test_anchor_sidecar_v2.py tests/test_discover_fact_type_family.py 2>&1 | tail -1
