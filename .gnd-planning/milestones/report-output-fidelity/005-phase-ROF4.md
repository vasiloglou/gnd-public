---
milestone: report-output-fidelity
station: phase-ROF4
skill: "n/a -- repository development via process-phase auto=false, not a gnd-solve station over a domain model"
scope: phase-ROF4
date: 2026-11-08
gate:
  command: "the full default lane at d83e972c in six round-robin shards of tests/test_*.py (one `python -m pytest -q --tb=line -p no:cacheprovider -rf <files>` per shard, PYTHONPATH=src), compared id by id with the same run at base 6058c674; the focused gate below ran at d44ba67a: .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rof4_accept_identities.py tests/test_public_transition_contract.py tests/test_coverage_payload.py tests/test_witness_composition.py tests/test_public_v71_witness_corpus.py tests/test_public_measure_corpus.py tests/test_measure_offline.py tests/test_pyrel_rules_plans.py tests/test_public_binding_reports.py tests/test_schema_sync.py tests/test_packaged_skills.py tests/test_rof3_model_identity.py tests/test_rof2_projected_text.py tests/test_rof1_projected_text.py tests/test_public_v72_semantic_owners.py tests/test_v71_phase4_successors.py tests/test_public_v72_status.py tests/test_gnd_arch.py tests/test_rf1_layering.py tests/test_rf1_cli_pins.py tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py tests/test_rf3_core.py tests/test_rf4_peripheral.py tests/test_rf5_commands.py tests/test_rf5_handler_pins.py tests/test_rf5_review_regressions.py tests/test_rf6_index.py tests/test_rf6_moves.py tests/test_rf6_query_policy.py tests/test_rf6_registry.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_doccheck.py tests/test_plan_app_docs.py tests/test_documentation_tutorials.py tests/test_v70_phase3_successors.py"
  exit: 1
  output: "123 failed, 18101 passed, 3 skipped, 7 errors (summed over six shards); the 123 failed or errored ids are exactly the base set at 6058c674"
  note: >-
    Exit 1 is the base's own failures (77 in test_public_tests_mode_corpus.py
    and 46 others), none examined; the run at d83e972c has no failure the
    base lacks and the base none the head lacks. The run at 770cf54d had one
    failure outside the base, repaired in d83e972c (Review).
evidence:
  - path: src/gnd/values.py
    sha256: 738d3ca4f390eb2652c4361ca55d643eaab0cf37f91a4705dfd5a27b17c0e833
  - path: src/gnd/transition.py
    sha256: 0faae6b25b691ba7efbdc9cf3cf89396a80963bd6cf824e09a9344dcfafd2212
  - path: src/gnd/admission_validation.py
    sha256: 596666c982e2a6ca93210a7a1dab8e256e84eb3dde3aeb6ae06ffc4a533b29fb
  - path: src/gnd/coverage.py
    sha256: 5fb7f62bf4b02e03fbfc21721713baac51a9fe6993aceb1ce9013882829fbb28
  - path: src/gnd/measure/service.py
    sha256: bc431e7e61cb01fdcaccbbac6d57544eb4298976e0106ddab87ac4d1c5cf025f
  - path: src/gnd/measure/report.py
    sha256: 2510537101f030ea2bc5773c03bbaa386a596c35e6a5da8934b109232dea54af
  - path: src/gnd/witness/kernel.py
    sha256: af3d307e886000bf4f385fe17f2bfa216c7115f7c09b22f65e830b53bf938e51
  - path: src/gnd/skills/gnd-orm-core/references/representation-format.md
    sha256: 4f2c15158f59306a289f863688c2723cd7096895516bf00b4b7c523b0b5f6760
  - path: src/gnd/examples/approvals/plan-draft-2.canonical.steps.json
    sha256: 3c2433ac6e0745cf3b9508353c9f9d98dc105c0df7c384943df88287f3e18b6b
  - path: tests/test_rof4_accept_identities.py
    sha256: 8625621f6bae93959f19f761e354606b234f77295b54d396096d08f67e3a77a4
  - path: tests/fixtures/rof4-accept-identities/README.md
    sha256: 22beae42b3045991f78cd2225e91d32313cd5510d6f6c738325cfedbcfa51698
  - path: tests/fixtures/rof4-accept-identities/expected/cases.json
    sha256: 9ccf5d0cf58bb2ebc3eeb2db3b39d89529fe2beac767ebbe27957e82017a2c2c
  - path: tests/fixtures/rof4-accept-identities/expected/identities.json
    sha256: ab0c943c01232901676330b06cf7d794b04d6256426674db56bddbb6065f6f05
  - path: .gnd-planning/milestones/report-output-fidelity/notes/phase-ROF4-spec.md
    sha256: 6b77f642fde485f299efc66118bd29f1df876e76a1b8a8a5f34a966f687ff030
  - path: .gnd-planning/milestones/report-output-fidelity/evidence/ROF4/codex-review.md
    sha256: b4f326f78d87565a5220c28459dfa14c535a89df1a7c6cce134c4211f1f8a7ed
  - path: .gnd-planning/milestones/report-output-fidelity/evidence/ROF4/dynamic-query-successor.json
    sha256: 55c5b62875bbbea60eafb7f57611c724ec6e49bbe7d1137efdf30b45d1fd189e
  - path: .gnd-planning/milestones/report-output-fidelity/evidence/ROF4/full-suite-base-6058c674.txt
    sha256: 11d11a8301d4e1fac26e40786394692f043b3acbd4dbc01098b169bc73fa70f1
  - path: .gnd-planning/milestones/report-output-fidelity/evidence/ROF4/full-suite-rof4-770cf54d.txt
    sha256: 008b644a242695534f89ccb11c1d989017a6aae4f9db18d21e397cf365464d6b
  - path: .gnd-planning/milestones/report-output-fidelity/evidence/ROF4/full-suite-rof4-d83e972c.txt
    sha256: f97da572101769c5d879f9e3fd4dbd79cd979822eacb244c381f19524f9afdf9
---

# Claim

At d83e972c, wherever GND matches a model identity someone supplied, it
accepts either the model's legacy `model_digest` or its canonical identity
(ROF3), and refuses any other value exactly as before (same rule id, same
message bytes, same exit). One function decides:
`gnd.values.model_identity_matches`, which compares the legacy digest first
(a legacy pin never computes the canonical identity) and answers which
identity matched (`legacy-repr`, `canonical-v1`, `canonical-v2`) or `None`,
never raising for a model without a canonical identity. Seven sites call it:
the walk's `model_digest`, the reference wrapper and the admission report
read back by session replay, a coverage check/verify source, the measure
sidecar (bare hex) and the measure corpus count (normalized, emitted as the
legacy digest), and a witness certificate's `binding.model_digest` (every
other binding field and the key set stay exact). The exact-coherence, copy,
in-process marker and generated-plan sites are unchanged. Every report keeps
the legacy value as its own `model_digest`; a walk report's
`transition.model_digest` echoes the pin as supplied, as its schema states.
A reference-bearing model has one identity. The full default suite at
d83e972c has no failure that the base lacks.

## What shipped

- `src/gnd/values.py`: `IdentityMatch`, `model_identity_matches`,
  `accepted_model_identities`.
- The sites: `transition.verify_digests` (S1), `admission_validation`
  `validate_reference_transport` (S2) and `_validate` (S3),
  `coverage._report_binding` with a `census_model` keyword threaded from
  `build_coverage` (S4), `measure.service._cmd_measure` with a per-digest
  verdict memo (S5), `measure.report.build_measurement_report` (S7),
  `witness.kernel.replay_witness` (S6).
- Shipped example `src/gnd/examples/approvals/plan-draft-2.canonical.steps.json`
  (exit 0) and its README row.
- The acceptance rule's one home: the "Three digests, three bases" table and
  the paragraph after it in the gnd-orm-core `representation-format.md`;
  the ROF3 subsection's item 6 corrected; cited from `docs/reference/formats.md`,
  `docs/guides/data-and-transitions.md` (with `gnd validate --identity`),
  `docs/agents/plans.md` (the generated-plan limitation, D7) and the
  `steps.schema.json` description (both copies).
- Corpus `tests/fixtures/rof4-accept-identities/` (20cc7654, approved with
  "Approve, implement") and runner `tests/test_rof4_accept_identities.py`.
- RF5 row for `_cmd_measure`; dynamic-query successor
  [evidence/ROF4/dynamic-query-successor.json](evidence/ROF4/dynamic-query-successor.json);
  component index (`model.scalar_identity` entry; generated pages).

## Gate output (verbatim)

Corpus and ROF4 tests (`tests/test_rof4_accept_identities.py`):

    20cc7654 (corpus, base code):     22 failed, 55 passed, 1 deselected
    d44ba67a (implementation):        77 passed, 1 deselected
    770cf54d (review repairs):        79 passed, 1 deselected
    d83e972c (provenance lookup):     79 passed, 1 deselected

The deselected test is T8 (`pyrel_oracle`: it needs the DuckDB runtime,
absent on this machine). It did not run.

Focused gate at d44ba67a before the guard successors:

    3 failed, 2973 passed, 1 skipped, 47 deselected in 522.48s (0:08:42)

The three were the guards the spec listed: `test_rf5_commands` for
`_cmd_measure` and two `test_rf6_query_policy` dynamic-inventory tests. After
the RF5 row and the successor: `431 passed, 1 deselected` over
`test_rf5_commands.py test_rf6_query_policy.py test_rf9_ci_repairs.py
test_rf6_moves.py test_rof4_accept_identities.py`. After the review repairs,
the affected suites (`test_rof4_accept_identities.py
test_public_transition_contract.py test_measure_offline.py
test_public_measure_corpus.py test_rf6_query_policy.py test_rf5_commands.py
test_rof3_model_identity.py test_witness_composition.py`):
`522 passed, 1 deselected in 187.03s`.

Full suite (V5): see below.

Lint: `ruff check` over the touched source and test files: `All checks passed!`

Layers and structure: in the focused gate (`test_gnd_arch`,
`test_rf1_layering`, `test_rf8_structure`, `test_rf7_structure`,
`test_rf3_core`, `test_rf4_peripheral`); `gnd.measure.report`,
`gnd.measure.service`, `gnd.witness.kernel`, `gnd.coverage` and
`gnd.admission_validation` now import `gnd.values`, which the layer map
allows.

V6: `python3 scripts/components_index.py changed --base 6058c674 --strict`:
`changed against 6058c674 (6058c67): 50 file(s) differ; 0 to fix, 0 warning(s), 9 to reread`.
The rereads (`subsystem.check`, `subsystem.measure`, `subsystem.witness`,
`measure.report`, `measure.service`, `check.admission`,
`check.element_coverage`, `semantics.transitions`, `witness.replay`) are
still accurate: each member now asks the helper; none gains a capability.

V5, default lane, six round-robin shards run locally:

    base 6058c674:      123 failed or errored ids
    rof4 770cf54d:      124; head minus base = test_rf2_review_regressions::test_cli_uses_new_provenance_lookup[measure]
    rof4 d83e972c:      123; head minus base = none; base minus head = none

Files: [base](evidence/ROF4/full-suite-base-6058c674.txt),
[770cf54d](evidence/ROF4/full-suite-rof4-770cf54d.txt),
[d83e972c](evidence/ROF4/full-suite-rof4-d83e972c.txt). The base and head
runs shared the machine with other worktrees' suites. A run at d44ba67a was
stopped when the review repairs superseded it.

V7: `git diff --stat 6058c674 d83e972c -- .gnd-planning/milestones/*/evidence`
shows only `compiled-snapshot-obligations/evidence/CI/source-successors.json`
(one added RF5 row, 15 lines) and this milestone's new `evidence/ROF4/`
files. No historical record or evidence file is edited.

## Criteria

| Criterion | Result |
|---|---|
| ROF4-C1 | one helper; T1 pins by AST that exactly the seven site functions call it, that only `resolve_context` and `matches_validation_marker` still compare a computed digest, that the exact, copy and plan sites keep their comparison text, and that no consumer calls the canonical identity directly |
| ROF4-C2 | per site, legacy and canonical accepted, wrong refused with today's message (S1-S6, 30 cases); witness: only `model_digest` widened (corpus cases plus a direct test of the comparison); measure: mixed corpus accepted, report emits the legacy digest; reference-bearing model: one value; generated plan refuses the canonical pin (T8, not run here; T12 pins the constant) |
| ROF4-C3 | the 14 shipped approvals pins exit as at the base and none is refused for its digest; the new example exits 0; `recordings/TASK.md` byte-preserved; fixtures and generated-plan fixtures: V5 |
| ROF4-C4 | the docs say "either identity" (T11), with the rule in one home |
| plan rule 1 | refusal messages and the frozen fixtures unchanged (T12); see I1 for the walk echo |

## Review

One reviewer is one reviewer: Codex (gpt-6-sol, xhigh, read-only) over
`git diff 20cc7654 d44ba67a`, disposition `block`, 7 findings:
[codex-review.md](evidence/ROF4/codex-review.md). Each was reproduced before
it was acted on:

- **P1** (blocking): a `str` subclass with its own `__eq__` was accepted as
  `legacy-repr` for a wrong digest, and one whose `__eq__` raises made the
  helper raise. Reproduced (`Liar` accepted, `Boom` raised `RuntimeError`).
  Fixed: only a plain `str` is compared; regression test added.
- **P2** (blocking): the rewrite of `transition.model_digest` to the legacy
  value contradicted the report schema ("As SUPPLIED by the steps
  document"). Reproduced by reading the schema at both definitions. Fixed by
  removing both rewrites; this changes the approved S1 answer (spec I1,
  ROF4-O1).
- **P3** (hardening): the measure count recomputed the legacy digest twice
  per run. Reproduced by reading. Reduced to one helper call per distinct
  digest, reusing the legacy string when a sidecar carries it. With the
  provenance lookup restored (below), a uniform legacy corpus costs two more
  legacy digests per measure run than before, a constant (spec I4).
- **P4** (completeness): dropping `sidecar_sha256` from the comparison could
  hide a wrong published hash. Fixed: each published value is checked
  against its file.
- **P5** (completeness): S2 has no case that tells the widened check from
  the old one (reference-bearing models have one identity). Accepted as a
  limit; stated in the corpus README; T1 pins that S2 asks the helper.
- **P6** (completeness): the extra/missing-key cases stop at the certificate
  shape. Fixed: a test calls the comparison with the shape check removed; it
  showed the key-set clause matters only for a binding without
  `model_digest`, and that case fails when the clause is deleted (checked).
- **P7** (hardening): the ROF3 subsection still said steps files carry the
  legacy identity. Fixed.

The full suite at 770cf54d then found one failure the base lacks:
`test_rf2_review_regressions::test_cli_uses_new_provenance_lookup[measure]`
pins that `gnd measure` looks the legacy digest up through
`synth.provenance`; the S5 change had dropped that lookup from the accepting
path. d83e972c restores it as the run's one lookup (it words the unchanged
refusal; acceptance is still the helper's) and updates the RF5 row.

The reviewer could not run the suite. The repairs were not re-reviewed.

## Refactoring review

Executed: none beyond the helper; each site changed only its predicate.
Seen and not done: `coverage.read_evidence_document` now takes both
`census_model_digest` and `census_model`; the digest could be derived from
the model, but the function is public and tests call it with the digest
only. `transition.transition_model_identity`, `values.reference_model_digest`
and `synth.provenance.validated_model_sha256` remain three names for the
legacy value (two spellings); unifying them is not this milestone's work.

## Size

Estimate: about 90 source lines (stop at 135), 15 doc lines, one example,
about 300 test lines. Measured (`git diff --numstat 20cc7654 d83e972c`):
source +119 / -20 (`values.py` 51, `coverage.py` 29, `witness/kernel.py` 17,
`measure/report.py` 13, `measure/service.py` 12, `transition.py` 9,
`admission_validation.py` 8), under the stop; `api.py` is back to its base
bytes; docs and schema +33 / -6;
example 32 lines; tests +82 / -3 on top of the corpus commit's runner.

## Boundary: what this phase does NOT establish

- Reports still carry the legacy identity as their own `model_digest`; a
  caller comparing a report's digest to its own computed canonical value
  still sees the legacy one (D3; R1 below).
- A generated Pyrel plan refuses a canonical pin (D7); T8, which shows it,
  did not run here (no DuckDB runtime).
- S2 cannot observe the widening (one identity for reference-bearing
  models).
- The legacy identity is not retired.

## Open questions

| Row | Question | Owner / target |
|---|---|---|
| ROF4-O1 | The approved S1 answer said a canonical walk's payload is byte-identical to the legacy one. It differs in `transition.model_digest`, which echoes the supplied pin, as the report schema defines it (I1, review P2). Accept the corrected answer (echo the pin), or report the legacy value there instead and change the schema's description? | owner |
| R1 (D3 re-ask) | Emit the canonical identity in reports? Measured cost: the report schema has live versions 7, 9, 11 and 15 and the wrapped 12/14 forms; emission means a new version per live ladder (D3 (b)) or one additive successor shape (c), each with its own spec. 154 tracked fixture files carry a `model_digest` field (83 report-shaped, 68 under expected or golden directories) and pin today's value. Keep (a), no emission: issue 111 closes at the milestone close on "a caller can recompute the identity and GND accepts it", with the report-side gap recorded; or schedule ROF5. | owner |
