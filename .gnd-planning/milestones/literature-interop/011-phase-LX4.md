---
milestone: literature-interop
station: phase-LX4
skill: "n/a -- repository development under process-phase"
scope: phase-LX4
date: 2026-11-15
gates:
  - command: "uv run pytest -q tests/test_lx1_flattening.py tests/test_lx2_witness_flattening.py tests/test_lx3_catalog_composition.py tests/test_lx4_literature_interop.py tests/test_composition.py tests/test_composition_example.py tests/test_mc1_guards.py tests/test_mc2_consumers.py tests/test_reference_population_corpus.py tests/test_witness_composition.py tests/test_li2_resolution.py tests/test_li5_lineage.py tests/test_public_replay_admission.py tests/test_fidelity_payload.py tests/test_public_fidelity_scope.py tests/test_schema_sync.py --tb=short"
    exit: 0
    output: "669 passed, 3 deselected in 146.75s (0:02:26)"
  - command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
    output: "679 passed, 2 deselected in 105.35s (0:01:45)"
  - command: "uv run ruff check --output-format=json"
    exit: 1
    output: "188 inherited diagnostics, exact match"
  - command: "uv run ruff check <changed Python files>"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base d523c14d --strict"
    exit: 0
    output: "0 to fix, 0 warning(s), 3 to reread"
  - command: "<wheel-venv>/bin/python -m gnd.examples.literature.interop run --out <run> --dates"
    exit: 0
    output: "installed run"
  - command: "<wheel-venv>/bin/python -m gnd.examples.literature.interop verify <run>"
    exit: 0
    output: "both modes verified"
  - command: "claude -p --model opus --permission-mode plan --add-dir <review-dir> -- '<brief-path prompt>'"
    exit: 0
    output: "VERDICT: CHANGES_REQUESTED"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: explicitly scoped owner or CI selection
  reason: the cross-phase affected routes and public example cover the changed contracts
evidence:
  - path: .gnd-planning/milestones/literature-interop/010-phase-LX4-spec-gate.md
    sha256: b7ab838eb21b5588c9f0721c8c0605285b76a2e519031eb3667752e8abddc32a
  - path: .gnd-planning/milestones/literature-interop/notes/phase-LX4-spec.md
    sha256: 7e57eff71351e8ad20e287511e7da86d5fee7518301c653cc5f66c1b1b51fc7b
  - path: .gnd-planning/milestones/literature-interop/evidence/LX4/dynamic-query-successor.json
    sha256: 3c97f142da96fbd1502f1951e342b526f4ff80fc0b93696a30d4c9a1eee4a482
  - path: .gnd-planning/milestones/literature-interop/evidence/LX4/installed-observation.json
    sha256: 5dd61435b73a58f558ed3613fbfbe1ed176671354d74e399e9b6c863142390a5
  - path: .gnd-planning/milestones/literature-interop/evidence/LX4/source-successors.json
    sha256: 479adfa12b2da8f75946361eca68d1db5a975fe2db6afd00e70314fd3ea6eb21
  - path: .gnd-planning/milestones/literature-interop/notes/reviews/phase-LX4-r1/BRIEF.md
    sha256: f0310486fc2a4fea57d113c06153b68c06df0362c3677a18fffc84eec33d9d51
  - path: .gnd-planning/milestones/literature-interop/notes/reviews/phase-LX4-r1/FINDINGS.md
    sha256: 0c1cf42b96e461df7cd31118b6bbc5d032af4417bacd87f00830c6e80547ebd7
  - path: .gnd-planning/milestones/literature-interop/notes/reviews/phase-LX4-r1/brief.json
    sha256: d5de0258681c062639fb728d5f754fdaece178004fa508601140339155e2cf73
  - path: .gnd-planning/milestones/literature-interop/notes/reviews/phase-LX4-r1/diff.patch
    sha256: fbabacf4104966bd75adc0d5c3e2168f94ce69624b1d08c024c782cbd6c8eaa6
  - path: .gnd-planning/milestones/literature-interop/notes/reviews/phase-LX4-r1/review.log
    sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
  - path: .gnd-planning/milestones/literature-interop/notes/reviews/phase-LX4-r1/review.md
    sha256: ca396cab39595aa858c9e4ac71195429ad40b31a28deef71cf13626a64535db7
  - path: .gnd-planning/milestones/literature-interop/notes/reviews/phase-LX4-r1/run.json
    sha256: 671e776791df55543ca6e7bb8edb257dd5babcf37f6fa27ab63f39e093f27163
  - path: src/gnd/examples/literature/interop.py
    sha256: 65fe085f99378f56a8570c4163fc4e2b204346644ff7103ae5a150f937bdef72
  - path: src/gnd/examples/literature/interop_dates.py
    sha256: 71ad08f9e7b57e27fe9c64ea319391d5199e4c5b84d8acf37641aa04d052a141
  - path: src/gnd/fidelity/service.py
    sha256: 4b80a18a24fe9afdfe0f54cc4a8bf9b27b1b9094e1072346d797980afe8f3d6d
  - path: src/gnd/checking_service.py
    sha256: 331516d2bab4b1d1b38797ab12f4265d583c7793cb03a8f92679d5b5ca327da2
  - path: tests/test_lx4_literature_interop.py
    sha256: 626dcb2ad0d8f1cf97c9ed235e474b2bc2e9f9ce6ce112fb8d1b89ef911a18e8
  - path: docs/guides/documents.md
    sha256: c47f5da1016347b8665c48481915741e8ffebf656743ccf8b94261675ce696ee
---

# Claim

The packaged example runs extraction, source rebind, catalog-assisted
identity resolution, composition, temporal check, witness, replay and
fidelity. Its verifier re-derives the model and evidence handoffs. The
optional publication-year advice has a separate input and report binding.

| Criterion | Evidence |
|---|---|
| LX4.a | Distinct authored roots pin the same two includes and catalog. Exact source rebinds carry both roots and the extraction evidence. The larger allowance control generates fresh rebinds and produces a guarded check failure. Pairing it with a stale rebind refuses before check or advice. Temporal extract, valid different pins and valid different catalogs refuse. |
| LX4.b | The LI5 policy admits the chainable candidates to the advisory denominator. Two pass, one PINN edge is advisory and five are unresolved. The direct null-link control is unresolved. The separate comparison proves byte equality of product-stage outputs when advice is omitted. |
| LX4.c | Installed-wheel run and independent verification exit 0 in both modes. The physical layout has two additional document copies and zero additional original extraction population or sidecar copies. Both fidelity cases ran. The rebound populations and anchors have two physical materializations each. |

## Gate output

    669 passed, 3 deselected in 146.75s (0:02:26)
    679 passed, 2 deselected in 105.35s (0:01:45)
    All checks passed!
    0 to fix, 0 warning(s), 3 to reread
    Installed-wheel interop build and verification exited 0 using the locked dependency directory.
    Installed verification with and without advice passed. Product-stage bytes match.

Whole-tree Ruff matches the baseline's exact 188 diagnostics. The test
lanes use the locked CPython 3.11 runtime and default markers. The installed
wheel uses the existing locked dependency directory. The
[installed observation](evidence/LX4/installed-observation.json) binds the
manifest, rebinds, check counts, advisory, proof origins and copy census.

## Independent review

The owner authorized one Claude Code Opus review of `8e98afc1`. The
reviewer confirmed all 36 declared hashes, ran 160 selected tests and
returned CHANGES_REQUESTED. It confirmed the temporal failure, the
candidate and catalog proof binding, the separate advisory and fidelity
census, and the include guard compatibility controls. The review did not
run the structural, component, lint or wheel gates. The exact
[review](notes/reviews/phase-LX4-r1/review.md) and
[findings ledger](notes/reviews/phase-LX4-r1/FINDINGS.md) are retained.

Forged producer metadata, a replaced indexed verbalization, an unbound
dates report and added evidence copies reproduced on the reviewed
candidate. The driver also reproduced refusal of a missing work endpoint.
Six regression cases failed before the repair and passed at `a3463627`.
The temporal order and exact mismatch controls were strengthened on that
candidate. The reviewed status applies to 30 unchanged brief entries.
Six amended files carry their local verification. The retained patch
keeps its context bytes for the review digest.

## Refactoring review

Refactors EXECUTED. The example shares its fixture-source evidence
producer across generation and independent verification. The verifier
reruns the extraction command to establish all expected bundle bytes.
The rooted fidelity path uses LX1's authenticated bundle reader. The
physical copy census uses actual file identities and content digests.

## Boundary

One reviewer is one reviewer. The fixture uses saved source extractions
and actual local product commands. Its advisory compares publication
years at equal precision under the LI5 policy. The milestone-close
panel and delegated close ruling follow the phase record.

## Open questions

- The LI1 shared-layout question closes for the fixture with the measured
  data above. Two filename conventions account for the document copies.
- The review-helper prompt separator remains with the dev-tools maintainer.
