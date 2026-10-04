# Phase 3 regression selection — approved r3 policy

Acceptance passed for candidate c63b90c in run 37158889273.
Attempts 1–5 remain retained failures/cancellations. The owner-approved benchmark
amendment and occurrence-identity restoration are qualified. Changes continue
through PR 1; this record does not merge or publish the candidate.
Keep current product assertions, fixtures, helpers and default marker exclusions.
Prior migration maps and source filenames are discovery aids, not coverage counts.

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

Names omit test_ and .py. Run ordinary `uv run pytest -q -ra --tb=short`.
Nine historical-only modules carry evidence: public_acceptance_runner,
public_coverage_progress, public_migration, public_original_projection_archive,
public_content_review_archive and public_review_storage{,_pack02,_pack03,_pack04}.
Their accounting/storage assertions remain intact. Frozen scaffold/collection
snapshots are historical; live origin, duplicates, resources and links remain default.
No archive cleanup or product protection retirement is selected.

## Results and findings

Attempt 2: macOS 3 failed/11301 passed; Ubuntu 1 failed/11302 passed/1 skipped;
400 deselected and one malformed-feedback warning each. Linux's case-alias control
skips on a case-sensitive filesystem and executes on macOS. Installed checks
passed both profiles: 1780 behavior and 85 contributor cases per wheel, with three
historical registration cases deselected. Outer gates: macOS 10 passed/942.28s;
Ubuntu 10 passed/1738.27s. Original candidate identities remain retained.

The fake-tool repair removes an ambient Souffle dependency. A1 accepts both
legitimate orphan-pipe failure labels, retaining termination, cleanup and no late
write. Scheduling controls failed the old expectation. Benchmark isolation keeps
normal GC, three samples, original workloads and exact timing/verdict/count bounds;
its failure-propagation control was red before repair. Attempt 3 still failed
scaling on both profiles (86 other checks passed), so isolation was insufficient.
The A2 runtime repair reduces duplicate scalar construction and join allocation.
375 focused neighbors pass on Python 3.13; 272 pass on local Python 3.11, including
reference-evaluator parity and exact work limits. Hosted acceptance is still due.

Earlier missing README/reference inputs, ignored nested fixture and untracked R3
amendment were repaired without weakening assertions; failed runs stay retained.
The reference driver preserves 258 stories: 261 passed, three historical cases
deselected; 20/23 source function ASTs unchanged. Installed selection includes it.
No source suite ran: a mistaken source-root command refused collection.
One reviewer plus one follow-up found three reproduced instrument gaps; see
phase-3-review-disposition.md. The two-call budget is exhausted; subsequent
repairs carry focused evidence, not another independent opinion. Artifact checks
refuted the initial README-metadata assumption: prior candidate bytes matched.
The runtime repair changes package bytes; attempt 4 must rebuild and qualify them.

Benchmark amendment controls: 137 focused cases passed on local Python 3.13;
101 guarded cases passed on Python 3.11. The 13 new controls failed before the
new instrument existed. No runtime code changes in this amendment; older results
and their then-current contracts remain historical evidence above.

Attempt 5: benchmark preflight passed both profiles; full macOS returned two
provenance/admission failures and 11354 passes. Scalar sharing was the cause,
reproduced locally. The adapter is restored to its pre-optimization bytes; the
existing end-to-end assertions remain, and distinct scalar occurrence identity
has a pre-fix failing control. This corrects the earlier equality-only reasoning.
The relevant admission module now joins preflight; no further runtime tuning.

Attempt 6 passed all required jobs. Full default: macOS 11356 passed; Ubuntu
result and skip reason are retained in 004-phase-3.md and the qualified logs.
Both installed profiles passed 1803 behavior and 85 contributor cases per origin.
The adapter matches source; only correspondence join allocation remains changed.
