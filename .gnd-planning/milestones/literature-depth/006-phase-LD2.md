---
milestone: literature-depth
station: phase-LD2
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-LD2
date: 2026-11-16
gates:
  - command: "uv run --no-sync pytest -q tests/test_ld2_quantities.py tests/test_ld1_competency_examples.py tests/test_anchor_sidecar_v2.py tests/test_public_semantic_boundaries.py tests/test_schema_sync.py tests/test_li0_witness_wire.py tests/test_li4_assertions.py tests/test_li5_lineage.py tests/test_lx1_flattening.py tests/test_lx2_witness_flattening.py tests/test_lx3_catalog_composition.py tests/test_lx4_literature_interop.py tests/test_witness_composition.py --tb=short"
    exit: 0
    output: "300 passed in 348.26s (0:05:48)"
  - command: "uv run --no-sync pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
    output: "679 passed, 2 deselected in 329.03s (0:05:29)"
  - command: "ruff check --output-format=json"
    exit: 1
    output: "188 exact inherited Ruff diagnostics"
  - command: "python3 scripts/components_index.py changed --base 4fba2ca3 --strict"
    exit: 0
    output: "0 to fix, 0 warning(s), 1 to reread"
  - command: "uv build --offline --wheel --out-dir <scratch>/dist"
    exit: 0
    output: "fresh local wheel used with locked dependencies"
  - command: "gnd check time.orm.yaml time.population.json --document source.txt --anchors time.anchors.json --format json"
    exit: 0
    output: "installed accepted"
  - command: "gnd witness time.orm.yaml time.population.json --targets time.targets.json --raw --out time.witness.json"
    exit: 0
    output: "installed proved exact coefficient, scale and unit"
  - command: "gnd replay time.orm.yaml time.population.json time.witness.json --raw"
    exit: 0
    output: "installed replayed exact 0.002 ps"
  - command: "claude -p --model opus --permission-mode plan --add-dir <review-dir> -- '<brief-path prompt>'"
    exit: 0
    output: "VERDICT: CHANGES_REQUESTED"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: explicitly scoped owner or CI selection
  reason: affected public modes are covered by the selected tests and installed route
evidence:
  - path: .gnd-planning/milestones/literature-depth/005-phase-LD2-spec-gate.md
    sha256: 031defa17d15d6cf45aa1a442ea1127af13e90d3d9fbbfa85f607ccfb5cbc55e
  - path: .gnd-planning/milestones/literature-depth/notes/phase-LD2-spec.md
    sha256: 2f2e8e9679dd1c0db9c1952e6fa0cf540fa74d24255501649837630d5f22cadf
  - path: .gnd-planning/milestones/literature-depth/evidence/LD2/dynamic-query-successor.json
    sha256: 37c0ef7f89e70b889484d59cf95e0d28d93454119663bd158a1f2c9e5ebe495d
  - path: .gnd-planning/milestones/literature-depth/evidence/LD2/installed-observation.json
    sha256: 237d3d023b11614e7cea57c0aec47fcf0240fa6432218bca8b7b33da67281c5d
  - path: .gnd-planning/milestones/literature-depth/evidence/LD2/review-dynamic-query-successor.json
    sha256: dc2b82af5e0adc8c4a5731f07f445274f5f4ef4567aca005963d078df9292d2d
  - path: .gnd-planning/milestones/literature-depth/evidence/LD2/review-scope.json
    sha256: 16670c5b29ac325412a5fec4012e9e960750bbdf258fb7443c7b83fa29d6bfe7
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD2-r1/BRIEF.md
    sha256: bd3e239ba665c03cf0e12b9eecec707b4980fc2aa0654a917d3d4611dbc248e7
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD2-r1/FINDINGS.md
    sha256: abf7e338c9bc38e0c71e8bdb87086e6a0710e0ef593b1c45b5306fa4fc6601d9
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD2-r1/brief.json
    sha256: e65ab9b6f7d02c237135876b65a549d597f819a0d83a842ef06fb486932180fc
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD2-r1/diff.patch
    sha256: 0e4af7f96ea448a68404c31b9c180a1d78917d5d9752a21fb228c9561131e827
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD2-r1/review.md
    sha256: d32f289500cb2715ab280a6e857e55dbfd5fd50868927e96d5a6f42b6ddbdaf2
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD2-r1/review.log
    sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD2-r1/run.json
    sha256: 4a52a8b9bce67f127aa0651bdfb3119f2bc0951c3e7dd72a55f36561da740e87
  - path: src/gnd/anchors.py
    sha256: add36fba98dfc94870e8249be5ef75f198a8657c94017dc6f96855bb5f282866
  - path: tests/test_ld2_quantities.py
    sha256: e8884d6d2c10db490c42ddb994503724a171eee362a55a74ea9bb70f3d584af4
---

# LD2 completion

The opt-in time anchor matches whole-femtosecond values declared in
compatible fs, ps and ns quantities. Concrete public checker controls
reject partial tokens, incompatible dimensions, rates, partial expressions
and sub-femtosecond values. The worked model binds an exact coefficient,
scale and unit to the source evidence. Public witness and independent
replay establish the tuple that represents 0.002 ps.

## Verified observations

| Criterion | Evidence |
|---|---|
| Time dimensions and model admission | Each compatible source span checks at exit 0. Inverse-rate and partial-expression witnesses fail at exit 1. The selector refuses a non-Integer target at model validation. |
| Exact decimal handoff | The checked coefficient, places and unit produce an ordinary witness. Changing each proof cell independently returns exit 1 and proof-invalid. A wrong scale or unit in the population fails the checked model. |
| Existing numerical routes | Native Float and non-integral Number check, then witness exits 2 with fragment-unsupported. The integral Number and LD1 percentage-point controls remain covered by the affected tests. |
| Installed smoke | Check, witness and replay each exited 0 in both tested wheels. The [installed observation](evidence/LD2/installed-observation.json) binds the exact input files, outputs and candidate wheel hashes. |

## Independent review

The owner authorized one Claude Code Opus review of `e0bf8feb`.
The reviewer verified 24 hashes and ran the 27 direct tests and a broader
affected selection. It confirmed time conversions, occurrence order,
model admission and witness/refusal behavior. It reproduced a historical
measure-size discrepancy at the phase base, where that reserved test
also failed. The author ran the installed and whole-tree gates. The
[findings ledger](notes/reviews/phase-LD2-r1/FINDINGS.md) retains all
four dispositions.

The local gates above bind the repairs at `55ffa8ea`. The
[scope comparison](evidence/LD2/review-scope.json) lists the 18 entries
whose original bytes remain and the six amended after review.
The structural guard uses the exact
[review inventory successor](evidence/LD2/review-dynamic-query-successor.json).
The catalog's model validation description still applies to the new
anchor selector check.

## Refactoring review

Refactors EXECUTED. Recognition reuses the existing per-value occurrence
index. Exact decimal handoff uses established Integer and String proof
cells, and the installed example uses the existing three public commands.

## Boundary

One reviewer is one reviewer. The independent review applies to the
recorded original diff. The fixed-scale worked example covers measured
time quantities at whole-femtosecond resolution. Part 10 remains deferred.

## Open questions

- LD3 now owns replayable reading and typed coverage.
- The Claude prompt separator is carried to the dev-tools maintainer's
  next review-helper sync.
