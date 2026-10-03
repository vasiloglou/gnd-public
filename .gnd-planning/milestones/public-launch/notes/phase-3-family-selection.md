# Phase 3 regression selection — approved r3 policy

Status: execution selection, results pending. The source-owned resumption spec
and owner approval govern this target copy. All changes land through a PR.

Keep the current target behavioral suite and its exact fixtures/helpers. Existing
adaptations include public coordinates, current temporal rejecting cases and
loader-valid opaque/recursive controls; no acceptance assertion is relaxed here.
The source family inventory and prior migration maps are discovery aids, not a
completion denominator. All earlier retained-private labels require inspection
by claim: historical proof/certificate producers and planning/accounting records
stay historical; current acceptance, refusal, redaction and lifecycle protections
remain in the corresponding public successor tests.

| Family | Kept protections / target modules | Decision |
|---|---|---|
| Model/population/checker/API | model_*, population_load, popvalidate, checker_families, public_api, v61_phase2_api, schema_sync, report_json | Keep positive/refusal branches and schema identity |
| Derivation/transition/temporal/aggregate/opaque | derivation_*, guarded_*, transition_*, v62_*, v70_*, public_adapter_*, public_transition_*, public_v72_* | Keep current semantics, synthetic parity/mutation and input boundaries; optional native/oracle markers unchanged |
| Synth/measurement | synth_*, measure_*, poolfile, public_measurement_publication | Keep prediction independence, concrete populations, sidecar/digest/refusal behavior |
| Extraction/rendering | extract_*, fidelity_*, doccheck, v51_* | Keep projection, identity, refusal and deterministic artifact guards |
| Generated code/conformance | codegen_*, conformance_*, architecture_*, archsmoke, public_generated_examples, generated_project_isolation | Keep real generation, drift and both small application workflows |
| Evolution/recovery/adoption | model_evolution, evolution_conformance, recovery_*, adopt_migration | Keep staged/CAS/provenance and bounded static recovery behavior |
| Sessions/feedback/solve | exp_*, agent_cli, junit_reader, solve*, public_v71_phase4_*, v72_phase5_session_mechanics | Keep subprocess limits, refusals, ranks and real local workflows |
| References/judgments/witness/export | public_v71_*, v71_*successors, public_lean_*, public_souffle_*, pyrel_export* | Keep offline emit/replay/input protection; real engines/providers remain separately selected |
| Assurance readers | public_assurance_*, v6_phase6_*, v62_*assurance | Keep stale/missing/tampered-evidence refusals; no positive recertification claim |
| Review/installer/skills | review_*, install, doctor_uninstall, packaged_skills, skill_prose_sync, public_installer, development_scaffold | Keep offline transport/security and both discovery roots |
| Release/contributor | release_*, contributor_preparation, runtime_preparation, public_optional, yaml_comment_neighbor, transition_mapping_totality | Keep examples, dependency refusals, resources and later retained-candidate installed tests |

Names above omit test_ prefix and .py suffix; stars identify module families.
The command is ordinary `uv run pytest -q --tb=short`, retaining pyproject default
exclusions. Actual selected node counts/results will be recorded after execution.
No default case is removed for age, runtime, confidentiality labeling or size.

## Historical-only controls retained outside ordinary acceptance

Nine modules receive the existing evidence marker: public_acceptance_runner,
public_coverage_progress, public_migration, public_original_projection_archive,
public_content_review_archive and public_review_storage{,_pack02,_pack03,_pack04}.
These test the superseded original-definition ledger, migration packet format and
lossless storage, not GND product verdicts. Their original assertions stay intact.
The scaffold's manifest_bytes_modes_and_sizes and collection's frozen snapshot
comparison also become evidence controls because current Git changes legitimately
invalidate those historical snapshots. Real skill/link/reference/owner checks and
fresh target module/hook origin checks remain default. Old wheel reconstruction
is not a release-candidate test. Current installed origin/dependency checks remain
in public_optional and are extended by retained candidate acceptance.

No archive cleanup is selected. Historical source originals remain where they
are; pending target archival work is not a release prerequisite. New collection
checks retain origin/duplicate checks without requiring frozen node-count equality.
No consolidated product assertion or retired product test is proposed this pass.

## Source coverage review limits

Source test modules missing by identical filename include historical phase/corpus,
proof and certification producers as well as mixed modules. Their current runtime
portions appear in public_* and versioned successors; filenames alone are not
coverage evidence. Review the advertised CLI/API/skill branches against these
families and investigate concrete uncovered branches before final acceptance.
Old per-definition mappings remain navigational evidence, not percentage completion.

## Results

Initial discovery: 11,187 selected / 221 excluded, collection only. Following
historical policy separation, focused collection/origin/skill/credential controls:
37 passed, 1 deselected in 9.26s. Full current execution and clean candidate checks
remain pending. No source suite, native/provider matrix or certification selected.


## Implementation findings

The initial default diagnostic run was interrupted after its first two failures:
2 failed, 2,134 passed, 387 deselected in 254.45s (exit 2). One was the old CI
job-location assumption; the profile guard now checks all three real job types.
The other was the target adaptation of this source-owned spec linking to two
source-only record names; links are replaced by a source-origin explanation and
the actual public preparation successor. Product expectations were unchanged.
A mistaken source-root invocation was refused by its lane collector (exit 4,
no tests ran); it supplies no source-suite result.

Candidate preparation initially included uv's generated .gitignore files in the
local artifact roster. The identity control refused before installation. Removed
only that generated build-directory metadata and recomputed the three-file list;
wheel/sdist bytes were neither changed nor rebuilt. These are development checks,
not reviewed final candidate attempts. Final CI freezes its own build-once files.

The staged inheritance includes 186 whitespace findings in 93 pre-existing
fixture/example files. Their bytes are retained; no evidence fixture is reformatted
for cosmetic consistency. Authored current changes pass scoped diff/ruff checks.
The indexed tree measures 16,365,652 bytes, largest ordinary blob 584,130 bytes.


## Coverage gap found by family review

Reference-population corpus integrity was carried, but its runtime case runner
was absent. Import the source's 258-story reference corpus and runner as
`tests/test_reference_population_corpus.py`, with original expected answers.
The only function adaptations are the source-independent legacy fixture path,
parameter marking of B24's old whole-repository census registration as evidence,
and its corresponding registration-dirty control's evidence marker. Model and
reference refusal/check/transition/diff behavior keeps the source predicates.
Source schema identity and keyword signatures retain current standalone guards.
This is imported regression code, measured separately from newly authored helpers;
it adds no product feature or preservation machinery. Its execution is pending.

Mixed source families were also spot-checked against target successors: v7.2
semantic-owner calculator/lineage/mutant/import-boundary controls remain current;
v7.1 judgments retain the full branch driver, and witness tests execute their
case/answer corpus. Installed selection now includes actual reference runtime,
judgment/session branches and generated/solve workflows, not only corpus integrity.

Reference corpus gate: `uv run pytest -q tests/test_reference_population_corpus.py --tb=short` exits 0: 261 passed, 3 deselected in 42.41s. The three excluded cases are explicitly historical registration checks. Twenty of 23 source function ASTs are unchanged; the three adaptations are enumerated above.
