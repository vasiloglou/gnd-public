# Phase 3 regression selection — approved r3 policy

Status: acceptance incomplete; owner-approved repairs ready for attempt 3. The source-owned resumption spec
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

## Results and retained findings

Final attempt 2 at d7f3acb completed. Installed acceptance exited 0 on both
profiles: 1,780 behavior cases and 85 contributor cases per wheel; three historic
registration cases were deselected. The macOS outer gate passed 10 in 942.28s;
Ubuntu passed 10 in 1738.27s. Exact candidate wheel and sdist identities are held
in run 37142968600 and the retained local candidate directory.

Full macOS: 3 failed, 11301 passed, 400 deselected, 1 warning in 1609.04s.
Full Ubuntu: 1 failed, 11302 passed, 1 skipped, 400 deselected, 1 warning in
3380.65s. The Linux skip is the case-alias identity case on a case-sensitive
filesystem; the corresponding macOS case executes. The serializer warning is
from the deliberately malformed-feedback control. These are not blanket skips.

The owner approved A1/A2 in phase-3-acceptance-amendment.md on 2026-10-03:
accept either legitimate orphan-pipe failure label while retaining cleanup,
termination and no-late-write checks, and allow four total final attempts.
The controlled delayed-spawn case failed the prior timed-out-only expectation.
All 86 lifecycle, fake-tool and guarded neighbors pass under Python 3.13 with a
clean PATH. Runtime code and performance thresholds remain unchanged.

The offline proof-depth test had mocked output while relying on an ambient
executable. Its existing fake tool now supplies that prerequisite explicitly;
all ten neighboring cases pass without Souffle on PATH. The guarded benchmark
failed twice in full hosted macOS runs, while isolated local measurements pass.
The repaired instrument puts the original workload, normal GC, three samples,
and exact bounds in a fresh process, removing retained pytest heap state. This
is a diagnosis-backed isolation change, not yet a hosted performance pass.
Its failure-propagation control failed pre-fix and passes with the new wrapper.

Earlier failures remain in ordinary Git history and source evidence: the first
local diagnostic stopped at two document/profile failures; the next completed
with six omitted README limitations. The seven related reference/README failures
were repaired without weakening assertions. The approved R3 amendment was
committed unchanged after a Git-snapshot check exposed its missing reference.
An introduced candidate ignore rule was narrowed to /candidate/ after its control
failed; the exact omitted nested fixture was tracked. Imported fixture whitespace
was retained. A mistaken source-root command refused collection; no source suite
ran. First local artifact identity checks refused uv's generated .gitignore files;
only that metadata was removed and the three artifact hashes were recomputed.

Family review restored the 258-story reference runtime driver and ten fixtures,
with source expected answers intact: 261 passed, three historical registration
cases deselected. Twenty of 23 source function ASTs are unchanged; changes route
legacy fixtures locally and mark historical registration controls as evidence.
Installed selection covers actual reference, judgment, session, generated-example
and solve behavior. Prior mapping files remain discovery aids, not a denominator.

One reviewer and one follow-up found three acceptance-instrument gaps, each with
reproduced controls and repaired neighbor checks; see phase-3-review-disposition.md.
That review budget is exhausted. Artifact comparison refuted an initial README
metadata assumption: all three candidate artifacts are byte-identical across the
first two attempts. Final attempt 3 will validate the repaired test instruments;
no completion claim or additional reviewer follows from these local passes.
