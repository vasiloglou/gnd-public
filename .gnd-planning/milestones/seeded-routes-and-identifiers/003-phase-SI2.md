---
milestone: seeded-routes-and-identifiers
station: phase-SI2
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-SI2
date: 2026-11-25
gates:
  - command: ".venv/bin/pytest -q tests/test_si2_reference_identity.py tests/test_model_verbalization.py tests/test_extract_vocabulary.py tests/test_extract_applicable.py tests/test_extract_guidelines.py tests/test_evolve_shape_matches.py tests/test_rmap.py -k 'not test_r2_f8_external_unique_keys_are_not_quadratic' --tb=short"
    exit: 0
    output: "183 passed, 1 deselected in 47.12s"
  - command: ".venv/bin/pytest -q tests/test_si2_reference_identity.py tests/test_rf6_query_policy.py tests/test_rf8_structure.py::test_graph_and_each_dirty_direction tests/test_release_text.py --tb=short"
    exit: 0
    output: "72 passed in 16.26s"
  - command: "cmp .gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI2/baseline.json .gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI2/candidate.json"
    exit: 0
    output: "No output. The two files are byte-identical."
  - command: ".venv/bin/ruff check src tests tools"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base origin/main --strict"
    exit: 0
    output: "changed against origin/main (99cf3df): 64 file(s) differ; 0 to fix, 0 warning(s), 21 to reread"
  - command: "python3 .codex/skills/process-phase/scripts/review_tool.py run .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI2-r1 --reviewer claude --wait"
    exit: 0
    output: "VERDICT: APPROVE"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "The phase uses its focused lane. The milestone close has a separate full default lane."
evidence:
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/phase-SI2-spec.md
    commit: 9e42b37cc311e783983a5e34e33e478b78a1eb0d
    sha256: 114aeec34736de3fe4162bbf4b72d4fb28db156e5c31ae8e10bde67bd0bfffb7
  - path: src/gnd/refscheme.py
    commit: 9e42b37cc311e783983a5e34e33e478b78a1eb0d
    sha256: a0c94fa2b29bce6d47948276f40fb53e829b51adda62c5afa207ff8147d90833
  - path: src/gnd/rmap.py
    commit: 9e42b37cc311e783983a5e34e33e478b78a1eb0d
    sha256: 8b4292c72fc86394a6f230cb370c0003df3b8efdccc1f307a463ffdf98578065
  - path: tests/test_si2_reference_identity.py
    commit: 9e42b37cc311e783983a5e34e33e478b78a1eb0d
    sha256: afad5d78fd0d1d36c17a6881cf3166793761ca6492ac15af9f5e1ebaa052f2af
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI2/census.py
    commit: 9e42b37cc311e783983a5e34e33e478b78a1eb0d
    sha256: e59eace90c54c0d8570c446ab06eab060cff90511ebea7e8be7e5c017381e99b
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI2/baseline.json
    commit: 9e42b37cc311e783983a5e34e33e478b78a1eb0d
    sha256: 5f48cdaaabd59515ebad79d1739588c986fb61bac646bc106101b0a34c1e4d6d
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI2/candidate.json
    commit: 9e42b37cc311e783983a5e34e33e478b78a1eb0d
    sha256: 5f48cdaaabd59515ebad79d1739588c986fb61bac646bc106101b0a34c1e4d6d
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI2-r1/BRIEF.md
    sha256: 536e0d5b87d0c7082a2c8400f2cce377d14e8dd0eb7382344ebc00620820719c
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI2-r1/brief.json
    sha256: f96d86f4c5cf17180cbe33006fd715b968dd08e57a8121943735032c848b39ca
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI2-r1/diff.patch
    sha256: 0326614e061698831102fa229b8dbf4cb4120b587334f1f1cad2df7e82439681
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI2-r1/review.md
    sha256: 0afa51a8fdb546df21a48d45983441000d2ecb45ebb2b29a7de7d2b38b9e613d
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI2-r1/run.json
    sha256: b9d2e9ee019dd43f1702774388af14263fb1435b610af0c34d9424784816102f
  - path: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI2-r1/FINDINGS.md
    sha256: 2312eeca8d2ddd6a169d939f8619324918d8631813de59608540fcea0fdb6eb8
---

# Claim

SI2 selects a preferred confirmed alethic anchored external uniqueness for
composite reference identity. The first matching declaration is the
fallback. Ties compare sorted role pairs and then the original declaration
sequence. Direct resolution, ordered components, and unresolved-component
handling retain their existing paths.

The preimplementation fixture observed five red cases and two passing
controls. The SHA-256 of all 436 tracked admitted model results was
`58f0ebce91661bb0c66912633234951ccfa53f3a32af11b01b50e7d6a828535a`
before and after. The complete machine outputs compare byte-for-byte.

## What shipped

- The shared reference identity implementation chooses one anchor and then
  resolves it for the vocabulary, model verbalization, applicability,
  evolve shapes and extraction guidelines.
- Anchor lookup reuses the current compatibility map within a selection.
  The tie order and confirmed/alethic predicate are shared with Rmap.
- New cases distinguish nonpreferred, proposed, and deontic leading
  declarations, both branches of the tie, direct reference, and fallback.

## Gate output (verbatim)

    183 passed, 1 deselected in 47.12s
    72 passed in 16.26s
    All checks passed!
    changed against origin/main (99cf3df): 64 file(s) differ; 0 to fix, 0 warning(s), 21 to reread

The Rmap timing node exceeded its ratio threshold on the broader candidate
run and the matched archived baseline at `5699c76a`:

    candidate: 1 failed, 181 passed in 54.09s
    baseline: 1 failed, 173 passed in 54.70s

The assertion's ratios were approximately 6.73 and 7.01 against a strict
limit of 6, respectively. The node passes in isolation on both versions.
It was deselected from the final focused selection. Its fixture builds
nonpreferred keys, so it does not execute the shared tie comparator.

## Independent review

Claude Code with Opus approved the implementation and found two evidence
and documentation gaps. The retained review confirms preference, tie,
fallback, compatibility and query-budget behavior. It also compared 27
model fixtures outside the filename census and found zero identity changes.
The review did not directly run all secondary caller outputs on the built
fixture. The unmatchable-key behavior and amended test ledger are pinned by
the subsequent repair and its focused controls. The review opinion applies
to the pre-repair bytes.

## Refactoring review

The order comparison was already implicit in the Rmap loop. The helper now
gives both code paths the same ordering while leaving Rmap's eligibility
checks and output unchanged. The in-process compatibility maps and identity
lookups keep their existing source seams. Their broader replacement remains
outside SI2.

## Boundary

The census reflects the 436 tracked models admitted at the phase baseline.
There were 67 load refusals. The machine measurement compares the resolved
identities, and the fixtures exercise callers that render those identities.
The phase does not establish a new Rmap placement rule or change an Ossie
ontology.

## Open questions

- Plan §1's Rmap alternative deletes three existing composites and adds ten
  other composites across the checked models. Carry this correction to the
  milestone plan sweep. The approved reading changes none of these callers.
- The broad local Rmap timing test intermittently exceeds its ratio threshold.
  Carry it to the close gate on beast-3 and report its observed result there.
