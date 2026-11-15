---
milestone: literature-identity
station: phase-LI2
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-LI2
date: 2026-11-15
base_commit: 457baeb382799108d48e6c1bfe1e6850e17f7143
gates:
  - command: "uv run pytest -q tests/test_li2_resolution.py tests/test_li1_literature_corpus.py tests/test_li1_assurance_report.py tests/test_composition.py tests/test_composition_example.py tests/test_witness_composition.py tests/test_public_composition_digest_1.py tests/test_public_composition_digest_3.py tests/test_public_semantic_composition.py tests/test_v62_phase3_composition.py tests/test_v62_phase4_composition.py tests/test_gnd_arch.py --tb=short"
    exit: 0
    output: "513 passed in 231.37s (0:03:51)"
  - command: "uv run pytest -q tests/test_li2_resolution.py tests/test_li1_assurance_report.py::test_identity_scoring_refuses_resolution_replaced_after_route tests/test_rf6_query_policy.py::test_exact_live_query_policy tests/test_rf6_query_policy.py::test_dynamic_candidate_inventory_is_complete_and_live --tb=short"
    exit: 0
    output: "66 passed in 38.70s"
  - command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
    output: "679 passed, 2 deselected in 139.59s (0:02:19)"
  - command: "uv run ruff check"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base d09189ca --strict"
    exit: 0
    output: "changed against d09189ca (d09189c): 225 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request only"
  reason: "The focused gate and structure guards cover LI2's declared impact closure."
evidence:
  - path: .gnd-planning/milestones/literature-identity/notes/phase-LI2-spec.md
    sha256: fff00be040c67f9546973344a8f906ad58665360fbeb7047cb6c28bc80f79a7f
  - path: .gnd-planning/milestones/literature-identity/007-phase-LI2-spec-gate.md
    sha256: f30b9d2ff2483a218db3bd45586a40fa2013cc9ab2dc43d6f6c0f6755c25e76f
  - path: .gnd-planning/milestones/literature-identity/008-phase-LI2-corpus-gate.md
    sha256: d6ccc89af3c53578147713c92564c01bf19129c7ee652e16bd8b71996e487212
  - path: .gnd-planning/milestones/literature-identity/009-phase-LI2-report-amendment.md
    sha256: ff998ac537a6c33d47c611e9a1a479bd74ade9fcc800e83642cdb570943a236e
  - path: .gnd-planning/milestones/literature-identity/notes/phase-LI2-claude-review.md
    sha256: 4be926c0f61558911a65cfe873c11186d4a3e615a4327e6adda91f356d7a59a6
  - path: .gnd-planning/milestones/literature-identity/evidence/LI2/query-successor.json
    sha256: 3b7f5d1832c26cafb0a64f3a593bf9e95b5e644a626512a73f368f36b0136de2
  - path: .gnd-planning/milestones/literature-identity/evidence/LI2/dynamic-query-successor.json
    sha256: 00f9b60131a39a98584e8474700b766749ffc85da2365fe671629b7683822006
  - path: src/gnd/composition.py
    sha256: 6a8c470082887dd64a64880910a43fcfa09a6ba32c27980ed127fabe8b369936
  - path: src/gnd/composition_resolution.py
    sha256: e4fa5ba9eea5bc24ccc579d0020c20f0b213a12d8d79e7b844f15b8e599d07ed
  - path: src/gnd/composition-manifest.schema.json
    sha256: 8275db65817e80be145aa01d227e4ae460687db52de61fd83475c1625ca43602
  - path: src/gnd/composition.schema.json
    sha256: 15925d9cae6acb2f11795376ab1a0b81fcc6fff82345ffd7b0ccc75d5ef0a8dc
  - path: src/gnd/resolution.schema.json
    sha256: af3f4e3783dd647a8b86b9cd5b7da818c57e846ecec079726d490232387d03c8
  - path: src/gnd/examples/literature/assurance_report.py
    sha256: b3dc219528f3d2131357ce6a4cd5fb55a25dad37a5fbd5b4d1ea43663ac481e4
  - path: src/gnd/examples/literature/resolution/cases.json
    sha256: 97b9c0e88071cb66d5431e2e23f65266ed8be303b734ba9624dc60e0483789bc
  - path: src/gnd/examples/literature/resolution/baseline.json
    sha256: b94ab5f5e615b12f753a84b5c58547c420de760bc13b5e6ca64313ccad17ac31
  - path: src/gnd/examples/literature/runs/reference/composition/resolution.json
    sha256: 62c7847ae1f2097c71fa88aecdf1261847c3c499603b7ce5b958f387d6891ea9
  - path: src/gnd/examples/literature/runs/reference/composed/record.json
    sha256: 636772b3f6a9dcf682a90ef8cbfc8f25bdb1515fd28f920d1bb032574735c791
  - path: src/gnd/examples/literature/expected/reference.report.json
    sha256: 9f2cf6a7f5be06290b6424a42626b1594e36ae5eb34c9dc9fc152695917b6a1b
  - path: src/gnd/examples/literature/expected/M7-false-merge.report.json
    sha256: c83547df5998a113a8bdf71faf7fbcbbf48584a4f1bfb03f21ea0e538e28a138
  - path: tests/test_li2_resolution.py
    sha256: 95f420f45e09976b8691360dadf0e163f30b380796f3143857851ec19b8f0d37
  - path: tests/test_li1_assurance_report.py
    sha256: 43ef4b5fe7d6ebd6ecb054cdc1aa0f68a979cbc7a55e0a99a3232fb082628d71
---

# Claim

LI2 binds explicitly authored resolution decisions to composition. The
manifest, evidence and coverage checks have separate refusal points.
Composition records identify the resolution digest and decision indexes
behind each asserted source fact. Legacy composition and witness bytes
match the approved baseline. The literature reference passes
`identity-decisions` at precision 3/3, recall 3/3 and abstention 0/6. M7
exits 1 with precision 3/4 for identity and recall 7/8 for derivation.

## Criteria and evidence

| Criterion | Evidence |
|---|---|
| R1 | T1 retains three whale edges and four meanings. The flat witness exits 0 and the resolved witness exits 2 |
| R2 | T2 passes its anchors. Both method/version controls match the approved outcomes |
| R3 and R7 | The alias joins with decision lineage. A homonym with no decision refuses. Different and unresolved controls exit 0; a placeholder already used by an instance refuses |
| R4 | The 20 cases match their exact exits and messages. Double-fault cases preserve refusal order, and the all-role anchor and hostile-input regressions check bounded refusals |
| R5 | Check and replay reject changed evidence. The old snapshot replays, and T16 matches the baseline composition and record digests |
| R6 and D8 | The harness uses a digest-confirmed resolution from R4. All ten cases match their approved outcome files |

The owner-approved spec and corpus are recorded in 007 and 008.
Delegated approval in [009](009-phase-LI2-report-amendment.md) corrects
one report census expectation, which had continued to call scored
identity labels unscored. The old expectation remains in the corpus
commit; all approved case messages, stage verdicts and scored denominators
are unchanged. The table test now matches literal refusal text rather
than treating its parentheses as a regular expression.

## Review and disposition

The [Claude Code review](notes/phase-LI2-claude-review.md) read the
first implementation diff and verified R1–R7, the ordered refusals
and legacy branch by inspection. It could neither run the controls
nor confirm the B3 tie-break by executing a two-decision fault.

| Finding | Disposition |
|---|---|
| F1, fact-level anchoring | Reproduced as `KeyError: 'role'`. Expanding an omitted role to every modeled role restores success with an anchor and exit 3 without the required span |
| F2, placeholder collision | Reproduced a composition accepting an instance-only collision at exit 0. Covered instances and nonasserted roles now participate in the collision check without becoming coverage keys |
| F3, unscored census | Reproduced in the reference report. The delegated amendment is recorded in 009. A refused route still exposes the unresolved scoring count |
| F4, time-control scope | The first control measures 40,000 keys and 19,900 decisions at the coverage layer. Added a timed accepting case with 40,000 keys and 20,000 unresolved decisions, covering the decision and spelling-group paths. File-based evidence binding is checked in the CLI cases |
| F5, source scan scope | Confirmed. The source scan is a shallow regression pin. The bounded runtime policy is in one routine. D7 explicitly allows the standalone harness to compute connectivity from verified decisions |
| F6, wrong model role wording | Retained the ruled step 3 citation refusal when a role cannot name a key. Non-resolution manifests still use the existing undeclared-role refusal |
| F7, import identity | Restored explicit aliases for the moved row matcher, strict JSON reader, shape and scalar helpers. The exception retains its historical public import and qualification. The existing instrumented linearity control patches the old row matcher name |

Two additional reproduced controls changed no approved outcome. A malformed
identity label now refuses as input schema before route execution. A
resolution and manifest replaced after R4 can no longer supply scoring
evidence. The stage confirms the reread bytes against the record digest in
the route response.

## Refactoring review

**Refactors executed.** The bounded parser, exact typed value identity and
row identity are shared with composition through explicit compatibility
bindings. The layer map covers the new module at model level. Model role
lookups use ModelIndex. The query-policy delta counts a single literal
sidecar role read, and the dynamic-query successor binds the exact observed
changes. A bounded decision-index stamp avoids retaining expanded
per-source citation lists. The two file layouts from LI1 remain an
interop question.

## Refuted premise

The existing T20 fixture exercises the coverage function, whereas the
spec's design-rule wording said it timed composition. A compact minimum-shape decision already occupies 472 bytes.
20,000 such decisions require 9,440,000 bytes before array framing and
exceed the 4 MiB resolution wire cap. The measured proof is the
coverage-layer control required by plan §9 plus the accepting control above.
The actual file reader, evidence binding and compatibility paths have
direct CLI cases.

## Boundary

For the phase diff, one reviewer is one reviewer. Claude Code ran a read-only review with the
prompt on stdin. Tests and refactoring checks cover the repairs. The
reviewer's observations bind its first snapshot. Coverage uses the
host-selected object types and asserted keys under D2 and B1. Examples
use public-scale labels. This phase does not claim broad-lane results.

## Open questions

- One evidence layout between fidelity and composition remains assigned to
  literature-interop.
- The safe path documentation and witness serializer structure remain with
  the maintenance targets carried by LI1 and LI0.
- The milestone close should cite this record for the corrected interpretation
  of T20 and verify the still-open plan rows.

## Verification sequencing

The 513-test gate covers the first green implementation and its affected consumers. The late anchoring and import-identity repair has its own 66-test targeted rerun. The structure list ran again over the repaired tree. All commands and verbatim summaries are in the front matter.
