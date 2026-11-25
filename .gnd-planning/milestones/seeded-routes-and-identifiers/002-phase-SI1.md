---
milestone: seeded-routes-and-identifiers
station: phase-SI1
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-SI1
date: 2026-11-25
gates:
  - command: "UV_CACHE_DIR=<cache> uv run --no-sync pytest -q tests/test_si1_seeded_routes.py tests/test_vg3_unattended_includes.py tests/test_vg4_seeded_growth_rounds.py tests/test_vg5_seeded_growth_example.py tests/test_ir1_judgments_includes.py tests/test_ir2_flatten.py tests/test_ir3_pyrel_includes.py tests/test_lx1_flattening.py tests/test_lx2_witness_flattening.py tests/test_extract_cli.py tests/test_include_root_close.py tests/test_pyrel_export_boundaries.py tests/test_unattended_mode.py tests/test_witness_timing_measurement.py --tb=short"
    exit: 0
    output: "364 passed in 31.63s"
  - command: "UV_CACHE_DIR=<cache> uv run --no-sync pytest -q tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_release_text.py --tb=short"
    exit: 0
    output: "116 passed in 37.62s"
  - command: ".venv/bin/ruff check src tests tools"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base origin/main --strict"
    exit: 0
    output: "changed against origin/main (99cf3df): 29 file(s) differ; 0 to fix, 0 warning(s), 19 to reread"
  - command: "python3 .codex/skills/process-phase/scripts/review_tool.py run .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI1-r1 --reviewer claude --wait"
    exit: 0
    output: "VERDICT: CHANGES_REQUESTED"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "The phase uses the focused default lane. The plan has a separate full default lane at milestone close."
evidence:
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/phase-SI1-spec.md
    commit: 8acc7b29141d1627ca6f51e51cfe31ccd748d722
    sha256: 77d1c284f064402f9738a50012e9d9b969d7a02345795b0d1baf4ea83d5fd154
  - path: tests/test_si1_seeded_routes.py
    commit: 8acc7b29141d1627ca6f51e51cfe31ccd748d722
    sha256: 86522458b65e6ca410ddda8898c3e07be9ba9587888bb76b725f23637d80efc5
  - path: src/gnd/model/flattening.py
    commit: 8acc7b29141d1627ca6f51e51cfe31ccd748d722
    sha256: 2042b1f217d5b0bb2733f060d7f329e2b28a8ab6ae42acc179efdfd436388b05
  - path: src/gnd/model/_unattended.py
    commit: 8acc7b29141d1627ca6f51e51cfe31ccd748d722
    sha256: 04609f3fa423434ca32013403c540e49d8fcc069ea0fabf2aff8eafb2abac2c3
  - path: src/gnd/model/__init__.py
    commit: 8acc7b29141d1627ca6f51e51cfe31ccd748d722
    sha256: d9881751f18708326ec6cab3d9bc4c3e72be6829c8b12ff613991214ee75707d
  - path: src/gnd/witness/io.py
    commit: 8acc7b29141d1627ca6f51e51cfe31ccd748d722
    sha256: d65f2cf95e24ef54fda3d44f7ebb7c4c8bb69e325e451cbb46861f15a079de0e
  - path: src/gnd/export/include_roots.py
    commit: 8acc7b29141d1627ca6f51e51cfe31ccd748d722
    sha256: e57b76c3baf4103595a89e43e785e16f189366ab5d05b1b68771319ed7144585
  - path: src/gnd/export/emit.py
    commit: 8acc7b29141d1627ca6f51e51cfe31ccd748d722
    sha256: 422b2b45b74936948515e96b54dbeed95f849321e0eb7133b18fbef73ccf760f
  - path: src/gnd/export/pyrel_rules.py
    commit: 8acc7b29141d1627ca6f51e51cfe31ccd748d722
    sha256: ab20c148cf89bf03ad18f3e87b1c1f8f79026c2d41ee01952f6c95a48bc049f9
  - path: src/gnd/skills/gnd-orm-core/references/representation-format.md
    commit: 8acc7b29141d1627ca6f51e51cfe31ccd748d722
    sha256: 4f88ce40cb7e0edcd28a05a624ba6b86ea0a703e4709bd0d55689e1e12edd301
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI1-r1/BRIEF.md
    sha256: 5722f06cc177dcb8face5a81c4b3c275fb1e2be9a09e139c1bc8ef6b95d452ef
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI1-r1/brief.json
    sha256: 5b180ae16bb80d72a4e9f23bf4e2149fc49747ecfc23d213953d425c76f065f7
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI1-r1/diff.patch
    sha256: 347b027b10038a95792c88878543538a4e2989d368168dd6991a0518b24cc060
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI1-r1/review.md
    sha256: e2f8d61308ff63cbae643b169cfa4191f49ddc5551dd780f23d49a3e9f286327
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI1-r1/run.json
    sha256: 478c57470f79369cdcb8e7adde4809aa01a6ee018cd04615bdd755f91f98aca0
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI1-r1/FINDINGS.md
    sha256: a3218d4c9f51b8dc193f93298f0a731b0d47ba21d8e60bf2b71846c8f2bdbedb
---

# Claim

The packaged and twice-grown seeded roots are accepted by flatten, extraction
and all three PyRel export modes. Standalone flat bytes that fail an
include-sensitive unattended rule retain the original rule IDs and add
`unattended:flat-without-root`, including after renaming. The injected
flattening re-entry refusal reports `flattening:re-entry` and writes neither
artifact.

## What shipped

- Model loading preserves U1 ownership and element exemptions across flat
  re-entry with origin metadata from a root whose include pins were checked.
- The rules renderers and rooted witness path use the validated projection.
  The witness reader still checks its input bounds and compares the model
  document to the projection. Extraction verification re-derives the pair.
- Default PyRel applies model admission for standalone unattended input
  before its profile check. The other modes retain full-model admission.
- The representation format states the standalone admission contract. The
  unattended growth guide links to it and the release notes record the route
  behavior.

## Gate output (verbatim)

Focused default lane:

    364 passed in 31.63s

Query policy, architecture and release-note control:

    116 passed in 37.62s

Lint:

    All checks passed!

Component index:

    changed against origin/main (99cf3df): 29 file(s) differ; 0 to fix, 0 warning(s), 19 to reread

The 19 existing component and subsystem contracts were reread against the
diff. The generated index now lists the changed model and witness surfaces.

## Independent review

Claude Code with Opus returned three findings over the pre-repair brief.
The retained review confirms the required route behavior, origin binding,
rooted witness verification, program model digests, and its affected test
selection. It did not run the beast-3 close gate. The findings ledger records
the measured red re-entry and documentation controls, the expanded timing
fixture, and the repair commit. The changes after the reviewed brief have
focused test evidence. The review opinion applies to the pre-repair bytes.

## Refactoring review

The flat projection is computed and validated once. The rules export and
rooted witness path reuse that same snapshot and bind their input documents
to its contents. Origin calculation and U1 ownership still use their
existing homes. No separate exemption mechanism or wire representation was
introduced.

## Boundary

The conditional standalone diagnostic keeps the existing rule IDs because
the same bytes can also be authored directly. Its scope is version-5 model
validation. The already admitted flat bytes are still used by the generated
default PyRel program. No native PyRel execution or full suite was part of
this focused gate.

## Open questions

- The packaged starter root can make `discover` exit 70 with U1 when a
  generated candidate adds a constraint before any document exists. This
  is independently reproduced by E1 on the base and patched source. It
  belongs to a separate discovery candidate-admission repair.
- The plan's standalone-flat detection premise is disposed by the conditional
  diagnostic. The E1 renamed-file probes and absence of origin data in the
  bytes show why intake cannot make a categorical origin claim.

## Refuted premises

The standalone reporter's failure was not uniform across PyRel modes:
default PyRel applied its own structural intake and exported the candidate
flat bytes. The falsifying baseline and the corrected route matrix are in
the spec and regression fixture.
