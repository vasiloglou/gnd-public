---
milestone: literature-interop
station: phase-LX2
skill: "n/a -- repository development under process-phase"
scope: phase-LX2
date: 2026-11-15
gates:
  - command: "uv run pytest -q tests/test_lx2_witness_flattening.py tests/test_witness_composition.py tests/test_public_replay_admission.py tests/test_mc1_model_includes.py tests/test_mc1_guards.py tests/test_li0_witness_wire.py tests/test_lx1_flattening.py tests/test_public_v72_ownership_direct.py tests/test_v71_phase3_successors.py tests/test_mc2_consumers.py::test_composed_witness_validation_refusal_compatibility tests/test_mc1_review_regressions.py::test_full_followup_raw_view_pin_rejects_unrecorded_body --tb=short"
    exit: 0
    output: "288 passed in 50.33s"
  - command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
    output: "679 passed, 2 deselected in 106.55s (0:01:46)"
  - command: "uv run ruff check --output-format=json"
    exit: 1
    output: "188 diagnostics equal the predecessor by file, line, code and message."
  - command: "uv run ruff check src/gnd/witness/flattening.py src/gnd/witness/service.py tests/test_lx2_witness_flattening.py"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base ac157120 --strict"
    exit: 0
    output: "0 to fix, 0 warning(s), 3 to reread"
  - command: "claude -p --model opus --permission-mode plan --add-dir <review-dir> -- '<brief-path prompt>'"
    exit: 0
    output: "VERDICT: CHANGES_REQUESTED"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: explicitly scoped owner or CI selection
  reason: the direct and structural gates exercise the changed path and wire contracts
evidence:
  - path: .gnd-planning/milestones/literature-interop/006-phase-LX2-spec-gate.md
    sha256: 7eb5b012125d8020fa510079611c4429baca0d4e3c90f2e350bc9b6d0c991dde
  - path: .gnd-planning/milestones/literature-interop/notes/phase-LX2-spec.md
    sha256: a221efdedd240abafa0291a9e2bab2cbca837f74e3b869431c9968ccdbbeb6f2
  - path: .gnd-planning/milestones/literature-interop/evidence/LX2/dynamic-query-successor.json
    sha256: e14ff83d7e3f527dd5a390b5e871720457d0775c146328bcba2e13d40d8e48e7
  - path: .gnd-planning/milestones/literature-interop/notes/reviews/phase-LX2-r1/BRIEF.md
    sha256: 82770755c241edb61725b02af076e3b830e260bacb6ecd4347144b06e5433c50
  - path: .gnd-planning/milestones/literature-interop/notes/reviews/phase-LX2-r1/FINDINGS.md
    sha256: 11f200ccae0a90f05cbec7f9aca5f24473db1bc24daef139194c8b7d98dafd20
  - path: .gnd-planning/milestones/literature-interop/notes/reviews/phase-LX2-r1/brief.json
    sha256: ef785123b6ff7148b9dce94d80c0bb47153665ca9446525a235563ffbbb3ec02
  - path: .gnd-planning/milestones/literature-interop/notes/reviews/phase-LX2-r1/diff.patch
    sha256: d216fd96948411015f7ae935cb1f391275fd3cef8d63706c05d3d9a4baa1afbc
  - path: .gnd-planning/milestones/literature-interop/notes/reviews/phase-LX2-r1/review.log
    sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
  - path: .gnd-planning/milestones/literature-interop/notes/reviews/phase-LX2-r1/review.md
    sha256: 95e76b8276bb4ae45250935f0fdcb798e4f6220f170cb31b0e40d264027b19b3
  - path: .gnd-planning/milestones/literature-interop/notes/reviews/phase-LX2-r1/run.json
    sha256: 9bf42700ae1b087bd51f39b22b244f5411e52a17df460582ffe7279f9a465345
  - path: src/gnd/witness/service.py
    sha256: 593f81c9e6cf0956ff57720f8d49d5eda598480ac48bbc533d2d691d74280944
  - path: src/gnd/witness/flattening.py
    sha256: 4fda541d57493485aa678447464571c1ed4d7f5b628b6a118e639afc4a5f2338
  - path: src/gnd/witness/io.py
    sha256: bd4833cdac2ecd1632dec1a5807dc85254e3d76640ceb2132043a4b2495701fc
  - path: src/gnd/witness/kernel.py
    sha256: 7911387d2a79cea38c707f7168e1fb5d7bdd9de1cb2bfcf69cf0d9042c0bd674
  - path: src/gnd/schema/witness-result.schema.json
    sha256: 68dcfc71c8089fbd09e7f2e3593d773f90de0ce30792adeeb35984804f7f824b
  - path: src/gnd/schema/witness.schema.json
    sha256: b0a08258abf500929e53026ce2322bfea083ef1b8763fa0bd1c4c79eb7e3304d
  - path: src/gnd/skills/gnd-export/references/witness.schema.json
    sha256: b0a08258abf500929e53026ce2322bfea083ef1b8763fa0bd1c4c79eb7e3304d
  - path: tests/test_lx2_witness_flattening.py
    sha256: 031db704709d077e6111aaa672f1231c4c81c4ddec2bb4edbc7f4f0261c2328b
---

# Claim

LX2 produces and independently replays witnesses over the authenticated LX1
projection, including a reference-free composition. The code binds the
flattening record and checks model origins separately from occurrence origins
and composition lineage. The include-free v1 and v2 producer bytes, replay
controls and public API signatures match the phase-base contract.

| Criterion | Evidence |
|---|---|
| LX2.a | Public extraction, witness and replay exit 0. The root and include origins are present in the proof. Separate mutations of model origin, occurrence origin and composition lineage give proof-invalid. Substituting flat bytes with the pins fixed gives binding-stale. |
| LX2.b | Changing a pinned include gives exit 3 and binding-stale. The v1 and v2 compatibility controls and the stream regression pass. |
| Intake and bounds | Unrooted include bytes retain their refusal. Closed schemas agree on v3. The existing budget is rechecked after the origin stamps. |

## Gate output

    288 passed in 50.33s
    679 passed, 2 deselected in 106.55s (0:01:46)
    All checks passed!
    changed against ac157120 (ac15712): 31 file(s) differ; 0 to fix, 0 warning(s), 3 to reread

The selected checks ran in the locked CPython 3.11 GND 0.3.1 environment
under the default test filters. Whole-tree Ruff exits 1 with the same 188
diagnostics as the untouched baseline, compared by file, line, code and
message. Changed-code lint passed before review and after the repair.

## Independent review

On the owner's scoped authorization, Claude Code Opus reviewed
`12747764` and reported 316 passing tests before returning CHANGES_REQUESTED.
It verified the independent model-origin derivation, replay refusal
precedence and v3 schema controls. It did not rerun the structure, lint,
component, full or historical lanes or independently recalculate the
legacy producer goldens.

All four findings reproduced before repair. The streamed-model assertion
previously returned 3. The other controls returned three generic stale
diagnostics, an input refusal on a symlinked parent, and an include
refusal ahead of invalid targets. Repair commit `706b9345` passes these
controls and both selected gates. The [ledger](notes/reviews/phase-LX2-r1/FINDINGS.md)
names each regression. Opus read the original candidate. Local tests
cover the repaired files. The retained unified patch preserves its context
bytes for the review digest.

## Refactoring review

Refactors EXECUTED. Legacy and rooted input paths now share the bounded
stream reader. The rooted path reuses the already read model bytes when
there are no includes. Explicit projected artifacts share the bounded
regular-file reader after resolving the caller path. Include dependencies
continue through the resolver.

## Boundary

One reviewer is one reviewer. This phase covers model origins with
standalone and reference-free composed inputs. LX3 owns the composed
catalog and mixed fact provenance. LX4 owns checking-model rebinding.

## Open questions

- The synchronized review-helper prompt separator follow-up recorded under
  LX1 remains with the dev-tools maintainer.
