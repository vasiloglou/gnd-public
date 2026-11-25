---
milestone: seeded-routes-and-identifiers
station: phase-SI3
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-SI3
date: 2026-11-25
gates:
  - command: ".venv/bin/pytest -q tests/test_si3_ossie_identifiers.py tests/test_ossie_export.py tests/test_ossie_import.py tests/test_ossie_relational.py tests/test_ossie_docs.py tests/test_physical_binding.py --tb=short"
    exit: 0
    output: "745 passed, 34 deselected in 165.86s (0:02:45)"
  - command: "GND_OSSIE_ORACLE_ROOT=<oracle> .venv/bin/pytest -q -m ossie_oracle tests/test_si3_ossie_identifiers.py --tb=short"
    exit: 0
    output: "34 passed, 42 deselected in 14.73s"
  - command: ".venv/bin/pytest -q tests/test_rf6_query_policy.py tests/test_rf8_structure.py::test_graph_and_each_dirty_direction tests/test_release_text.py --tb=short"
    exit: 0
    output: "64 passed in 26.11s"
  - command: ".venv/bin/pytest -q tests/test_rmap.py -k 'identification or role_placement' --tb=short"
    exit: 0
    output: "10 passed, 88 deselected in 2.91s"
  - command: ".venv/bin/ruff check src tests tools"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base origin/main --strict"
    exit: 0
    output: "changed against origin/main (99cf3df): 79 file(s) differ; 0 to fix, 0 warning(s), 23 to reread"
  - command: "python3 .codex/skills/process-phase/scripts/review_tool.py run .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI3-r1 --reviewer claude --wait"
    exit: 0
    output: "VERDICT: CHANGES_REQUESTED"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "The focused gate and the owner-selected pinned Ossie lane were run. The milestone close has a separate full default lane."
evidence:
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/phase-SI3-spec.md
    commit: 70f7c69668060d7ae8ccd02998a865db8b47b856
    sha256: 75e88250f773ec8374710492315daa5f6f9061cebdd231e01b27c2bab2c3a468
  - path: src/gnd/export/ossie.py
    commit: 70f7c69668060d7ae8ccd02998a865db8b47b856
    sha256: 374cefc39c3a614f013daff172470a621086290260dab1882a12e4d87da10ea2
  - path: src/gnd/export/ossie_relational.py
    commit: 70f7c69668060d7ae8ccd02998a865db8b47b856
    sha256: 7da79a1dda0f2585dd1012f590ac23d9669cc0ae6fe5dc8b1298fb0ed7d841a8
  - path: src/gnd/rmap.py
    commit: 70f7c69668060d7ae8ccd02998a865db8b47b856
    sha256: b52457214768b7aeb815270af782dfce7e50ae90c583a6bc847a33d572537ba1
  - path: tests/test_si3_ossie_identifiers.py
    commit: 70f7c69668060d7ae8ccd02998a865db8b47b856
    sha256: 982d9dab3c9f8aafad463f99c141a66b1d3bf74114991dfaf955c4202d93a5ca
  - path: tests/test_physical_binding.py
    commit: 70f7c69668060d7ae8ccd02998a865db8b47b856
    sha256: 467d405a7381245c98557c04deacaf9a48e4d92dc0555816672822726bf52db0
  - path: tests/test_ossie_relational.py
    commit: 70f7c69668060d7ae8ccd02998a865db8b47b856
    sha256: f63db073d6d1f4ac45e385b9a0b0dd0acb3381a307104e7a5f77f5037d9a5bec
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI3/ontology-corpus.json
    commit: 70f7c69668060d7ae8ccd02998a865db8b47b856
    sha256: ba2964bb757ad645340cd870b4e848cd1d17af92fc7af97b14b373de7541bb62
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI3/observed-ontology-digests.json
    commit: 70f7c69668060d7ae8ccd02998a865db8b47b856
    sha256: c45327dd9434a48adca912f7469a52ae909ae8495f9b54ebae0be9333db6ff33
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI3/mapping-census.txt
    commit: 70f7c69668060d7ae8ccd02998a865db8b47b856
    sha256: 6a22c1c255a947fec93e752989d8c10bbf5655c805d53daa09593fa6e4155899
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI3/oracle-preimplementation.json
    commit: 70f7c69668060d7ae8ccd02998a865db8b47b856
    sha256: deedd1c5d2a2751e83183cd3726390593cff91cd11b9a9bff4a47a5fb0a5ab22
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI3-r1/BRIEF.md
    sha256: 792ef1f900071b93fd4fa0955136ca3e8859578f53f337c7487ac182ecb542ae
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI3-r1/brief.json
    sha256: 3de79b7d0319ff20d1c492c03aff72d0a52e6af8da109953ae062f1c3195e86f
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI3-r1/diff.patch
    sha256: c93c78fa7b5635575d906598ed1ef7efc073f54cd5ed47f0e0c3f776b3e31e54
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI3-r1/review.md
    sha256: 7a4e5ff32f4bad46d4194a8f8c4dddd7a9dab0e7710bb1f7ce0ad82dbca63d70
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI3-r1/run.json
    sha256: ec8cea208a2567fd087350d8dc3b24b792e95a28e015bd4dcbbc514d08aa34e5
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI3-r1/FINDINGS.md
    sha256: 8b026b4635f65b108ecd0bde3b41f2e61e5eaa4a5d31bdeb8afc9c11a1944c49
---

# Claim

SI3 projects a unit-based reference as a Decimal identifier and uses the
first declared supertype's exported identifier for inheriting multi-parent
subtypes. The bound sidecar restores all approved source models in both
formats. Exactly 17 of 414 admitted tracked model exports changed their
ontology bytes, matching the approved canonical JSON corpus.

## What shipped

- Unit-based entities share the existing OneToOne identifier relationship
  projection. Their mapped key column supplies the numeric expression.
- Multi-parent subtypes resolve the first declared parent's identifier. A
  same-named authored relationship cannot take the place of a generated key.
  A composite parent supplies its ordered component identifiers.
- Old bound packages remain importable. The current import CLI restored all
  34 JSON and YAML bundles exported from the baseline source.
- The representation format and explanation describe the native projection,
  and the release notes record the wire change.

## Mapping census

| Reason | Before | After |
|---|---:|---:|
| Unit-based unmapped links | 8 | 0 |
| Multi-supertype unmapped links | 5 | 0 |
| Objectification unmapped links | 4 | 4 |
| Objectification concepts without object mapping | 2 | 2 |

## Gate output (verbatim)

    745 passed, 34 deselected in 165.86s (0:02:45)
    34 passed, 42 deselected in 14.73s
    64 passed in 26.11s
    10 passed, 88 deselected in 2.91s
    All checks passed!
    changed against origin/main (99cf3df): 79 file(s) differ; 0 to fix, 0 warning(s), 23 to reread

The additional three physical-binding acceptance and refusal assertions
passed together. The repaired source's exact digest and mapping censuses
matched the initial candidate's results. The GND CLI restored the complete
source from each of 34 predecessor-format bundles. The pinned converter
also resolved all seven multi-supertype fixtures to the declared first parent.

## Independent review

The retained Claude Code Opus review checked all 17 approved outputs and
the bound round trips. It reported a false mapping under mixed inheritance,
missing coverage for a composite-parent mapping mismatch, and a lack of
simple unit inheritance from a single parent. The ledger binds the repairs
to the source commit. The focused controls include the wrong-key red
control with only the target comparison removed. The reviewer did not run
the external oracle. The owner-selected local oracle supplies separate
validator and parser evidence for both formats. The review opinion applies
to the pre-repair bytes.

## Refactoring review

The projection reuses the existing native relationship generator and the
mapping's single-expression path. Only identifier selection gains the
multi-parent name reservation. The importer, Rmap key definition and
pinned external tools retain their existing homes. The predecessor's
T13(b) asserted the earlier unit mapping gap. The successor asserts real
link mapping through the same fixture and independent cross-check.

## Boundary

The external oracle checks the pinned upstream validator and parser against
the changed ontology documents. It does not establish support by every
third-party consumer. The retained objectification cases are outside the
approved change. Sidecar-free imports retain their published foreign
import contract.

## Open questions

The product phases await the owner-controlled merge before SI4 begins.
The close will record the full default lane and the owner's separate
tag act.
