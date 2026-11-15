---
milestone: literature-identity
station: phase-LI5
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-LI5
date: 2026-11-15
base_commit: 0fffbba5875e1535f631224df4b85e57c06aa25b
gates:
  - command: "uv run pytest -q tests/test_li5_lineage.py tests/test_li4_assertions.py tests/test_li2_resolution.py tests/test_witness_composition.py tests/test_public_why_not.py tests/test_checker_families.py tests/test_fu3_derived_ring.py tests/test_public_v71_witness_corpus.py --tb=short"
    exit: 0
    output: "602 passed in 655.66s (0:10:55)"
  - command: "uv run pytest -q tests/test_li5_lineage.py --tb=short"
    exit: 0
    output: "10 passed in 54.54s"
  - command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
    output: "679 passed, 2 deselected in 317.66s (0:05:17)"
  - command: "uv run --isolated --offline --locked --group docs zensical build --strict"
    exit: 0
    output: "No issues found"
  - command: "uv run ruff check"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base 0fffbba5 --strict"
    exit: 0
    output: "changed against 0fffbba5 (0fffbba): 33 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
  - command: "uv run python -m gnd.examples.literature.lineage_run score MODEL DEVELOPMENT-RUN DEVELOPMENT-KEY"
    exit: 0
    output: "supported 3/3; false excluded 5/5"
  - command: "uv run python -m gnd.examples.literature.lineage_run score MODEL FIRST-RESERVED-RUN LOCAL-KEY"
    exit: 1
    output: "supported 0/1; false excluded 2/2"
  - command: "uv run python -m gnd.examples.literature.lineage_run score MODEL CORRECTED-RESERVED-RUN LOCAL-KEY"
    exit: 0
    output: "supported 1/1; false excluded 2/2"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request only"
  reason: "Focused proof and example controls cover the declared LI5 scope."
evidence:
  - path: .gnd-planning/milestones/literature-identity/019-phase-LI5-spec-gate.md
    sha256: 03a9e891ff5152912c1f4ac2faa1b3c9a90bf57b82ec7b77e0e05d1394f7d1f9
  - path: .gnd-planning/milestones/literature-identity/020-phase-LI5-corpus-gate.md
    sha256: 1146a0a77d90c568b39312e26e4acc85e7d99647244a593be3707c1d40ffa010
  - path: .gnd-planning/milestones/literature-identity/021-phase-LI5-rule-freeze.md
    sha256: 7b4d42679496de9026b2acb7300db41c3dc9e66cc5168c1f9dd4ce989e027572
  - path: .gnd-planning/milestones/literature-identity/022-phase-LI5-reserved-input-freeze.md
    sha256: 792bfb417cd3b4ceb36041789677f3104dd4aaeb8981f86325f82cc55d63cbf5
  - path: .gnd-planning/milestones/literature-identity/023-phase-LI5-reserved-input-amendment.md
    sha256: 5b2c11314bb1b5b271be6e2a7d560509841d0efd4b7c639aff43443fe18596c5
  - path: .gnd-planning/milestones/literature-identity/notes/phase-LI5-spec.md
    sha256: 64ecb12ff34f8c7cd68f9e4a26bdb5b3e3f6d10e4035d5fb4508375b92999c6d
  - path: .gnd-planning/milestones/literature-identity/notes/phase-LI5-claude-review.md
    sha256: d0c92b6c4756d58837db4db61ec98310d1ccae20b151d40a8a9bf0c1969a6440
  - path: .gnd-planning/milestones/literature-identity/evidence/LI5/development-composition.json
    sha256: 6e2f2ed89dca890bfe0f4d89af6dd3d0b9ec25f874283e21b5f51671832470f9
  - path: .gnd-planning/milestones/literature-identity/evidence/LI5/development-score.json
    sha256: 0b66ac5b8a19141273b700b57c31bf257215004b3c0e1669971b50e6d6c76dfe
  - path: .gnd-planning/milestones/literature-identity/evidence/LI5/development-witness.json
    sha256: cb7b846b7987adbacf5f828ba0ff685cd4777e2bb23e27a53aa52d740650348b
  - path: .gnd-planning/milestones/literature-identity/evidence/LI5/reserved-corrected.json
    sha256: ff55d9ec11a1257896b347864b96236fdc679dd307b11b37b0342076a3556ebf
  - path: .gnd-planning/milestones/literature-identity/evidence/LI5/reserved-first.json
    sha256: 822e3c3c4a61eaafa698f0579bc54330e4777c574a319a715514285de914c182
  - path: .gnd-planning/milestones/literature-identity/evidence/LI5/reserved-input-correction.md
    sha256: 863a738199c9e3ec13abf580e72d1666ee754a1ad4c9f28c53b3e6404660cba0
  - path: .gnd-planning/milestones/literature-identity/evidence/LI5/reserved-procedure.md
    sha256: 7b2f823eac6b3d482e253aee6f1c444daf6fec1b292e00f25c0744ed8c185fe4
  - path: src/gnd/examples/literature/lineage/README.md
    sha256: 441636cbc30fbb1e43971772ecd9a91bb84d48962b33cc543dcf43927f316135
  - path: src/gnd/examples/literature/lineage/cases.json
    sha256: 0cc4b2764858d0712dbdb2026571cd65ed11bac2213ad67b95282198f4822f2f
  - path: src/gnd/examples/literature/lineage/control-document.txt
    sha256: 87ed667e39088964a7c2d12f01ac88885aa667bf24fa232475b009bf242032b5
  - path: src/gnd/examples/literature/lineage/control-input.json
    sha256: ca0ede0c69e13a8449c0bc9c9b47d5b39d02480a5871aed90bc97579226533a2
  - path: src/gnd/examples/literature/lineage/cycle-document.txt
    sha256: 39644edd5b8c279881087728884784aacb6fa2f57e896d514c3a44d6d15dc131
  - path: src/gnd/examples/literature/lineage/cycle-input.json
    sha256: 66d4a8e2f243cbd8e1a11b4361fca13977cc1ebb12fdd52fadee21b36b9374a5
  - path: src/gnd/examples/literature/lineage/development-input.json
    sha256: cbb2c0eaf19b66afd83a6835f4d878ae734ceb7c9ffa5bbddc317c6405e52b97
  - path: src/gnd/examples/literature/lineage/model.orm.yaml
    sha256: a63b64293edbed71c74d1ded8423c133c328aa4ea02f550bad4fb03c91591279
  - path: src/gnd/examples/literature/lineage/path-policy.json
    sha256: cc27412b17b7cc1ca4f6d5da940b74b80528e45d2aa9d5a78dbee4986274c0b7
  - path: src/gnd/examples/literature/lineage_run.py
    sha256: 15ff3ddc3d483fcdaed71ccfcc059facecb102282a674ce109d967085353706b
  - path: tools/build_literature_lineage_model.py
    sha256: 2a6a2b8ea283bbcac5114167f6ee9ce3c48293ff38c60db64c662a8d39e5eb29
  - path: tests/test_li5_lineage.py
    sha256: 192c8e4a51929a5295440fed0a62bf41ac390e41e50db0087aee012efda6ef7d
  - path: docs/literature/01-lineage.md
    sha256: a71fd1e099f5aa9c0525aa0b03be81e7ab333f89bff5a882ab7e40bb90fb462d
---

# Claim

The example composes saved-opinion contextual assertions, witnesses
documented lineage and qualified transfer, and scores the directed
public path cases. The model and path policy are committed before
reserved scoring. The development cases retained 3/3 supported paths
and excluded 5/5 false paths.

## Criterion evidence

| Criterion | Control |
|---|---|
| L1, C6 | Development 3/3 supported and 5/5 excluded. Reserved first measurement 0/1 supported and 2/2 excluded. Corrected-input smoke measurement 1/1 supported and 2/2 excluded on the same rules, policy and key |
| L2 and L6 | The Boltz-1 evaluation remains an admitted statement. Its exact family query and the four never-chaining predicates have missing witnesses. A supported cross-domain chain and the false same-domain chains are among the development cases |
| L3 | Unreviewed and unresolved edges have missing witnesses (2). The transfer control passes with both inputs and fails with a missing interface on either an individual or a transitive path |
| L4 | The cyclic and acyclic checks exit 0. The first warns and retains both edges. The second has no ring warning. The separate flat whale demonstration remains in the resolution example |
| L5 | The witnessed public path names the contextual assertion sources. Its composition record carries the decision indexes. The original replays, a changed assertion coordinate fails with proof-invalid (1), and a changed record fails with binding-stale (3). A reversed claimed edge fails derivation |

## Reserved scoring

The [rule freeze](021-phase-LI5-rule-freeze.md) and [first-input
freeze](022-phase-LI5-reserved-input-freeze.md) precede scoring. The key
digest matched the existing approved pin before the key was scored.
The first result is retained. It missed the supported path because
the source annotation named the encoder qualifier as the entire method.
The [delegated correction](023-phase-LI5-reserved-input-amendment.md)
preserves that qualifier as the regime, and tests the same architecture
dependency under the frozen rules. The subsequent result is a corrected-input
smoke score. The first miss and the feedback used for correction remain
material limits on the close's reserve evidence.

The reserved artifacts committed here are aggregate results and
hashes. The local key, source annotations and reserved runs stay outside the
worktree. The development score, composition record and one version-2
witness are retained for the public replay demonstration.

## Independent diff review and repairs

Claude Code read the source and approved test cases, reviewed the
scoring boundaries and disclosed reserve results, and returned the
[retained findings](notes/phase-LI5-claude-review.md). It had no
execution evidence and no access to the reserved key or private inputs.

| Finding | Disposition |
|---|---|
| F1, false-path sensitivity | The normal development run excludes all five false paths. A new dirty-input control explicitly gives the two contrast statements the wrong saved approvals and the shared identity. The unchanged scorer witnesses the false path, exits 1, and drops exclusion to 4/5. LI2 retains the separate false merge control. The exact-spelling examples use approved same joins and retain different decisions as evidence |
| F2, witness and decision binding | Both contextual base sources link through their record entries to decision indexes. Existing replay binds the full record digest. A separate rederivation now tests that changing decision lineage also refuses the record against its sources. The scorer performs that rederivation before making a witness. The general witness API's digest-bound record trust remains its existing contract |
| F3, assumptions and qualification | The contextual producer already filters missing assumptions. A model-layer control replaces the condition on a valid statement while carrying its interface. The lineage proof remains and the transfer proof exits 2. The original composed path control independently isolates a missing interface |
| F4 and F5, positive and directional controls | All three additional allowed predicate examples are now witnessed. The reverse of the valid Nimbus edge is missing |
| F6, binding and reserved procedure | Reproduced score accepting a run without its admission marker. The repaired scorer checks each marker against retained raw, receipt, policy, judgment and admitted bytes and the composed source digest. The exact local key procedure and aggregate transform are documented alongside both scores |
| F7, model and policy coherence | The component test regenerates exact model bytes from its declared policy and verifies the chainable and non-chaining sets are disjoint. The recorded freezes preserve the named scorer both before first key access and after the safety repair |
| F8, cycle and reversed claims | Completed cyclic and acyclic checks keep the warning behavior separate. The reversed-arc regression names the exact derived relation and unsound row finding |

The review found that the corrected result does not replace the
original reserved measurement as independent evidence. This phase records
a working example and the corrected public smoke exercise, with the
original reserved exit predicate carried as an open acceptance condition.
The close panel audits that boundary. This phase's one reviewer
assesses the diff and does not supply close authority.

## Refactoring review

The policy file drives both model rule families through one rule builder.
The assembly reuses the saved-judgment projection, strict readers,
composition and manifest-last publication. The proof scorer uses one
directed-path check and queries captured, already verified input
bytes. The format of the ordinary witness and composition record
remains in its existing home.

## Boundary

For the phase diff, one reviewer is one reviewer. The close uses
its separate panel. The public score covers the approved fixture floors and the reserved
rerun is post-correction evidence. The stage checks document-level
lineage assertions and the named transfer prerequisites in this
example.

## Open questions

- Disposition the first reserved failure and the post-correction claim
  at milestone close. An additional fresh reserve is a separate corpus task.
- The safe path and common evidence layout questions remain carried
  to their recorded maintenance and interop targets.

## Verification sequencing

The focused affected-consumer and structure gates cover the first
reviewed implementation. The LI5 direct suite ran again after the
admission-link and control repairs. The fixed-rule corrected score
also replayed byte-for-byte after the admission guard was added.
The exact local reserved command and digest procedure lives in
[reserved-procedure](evidence/LI5/reserved-procedure.md).
