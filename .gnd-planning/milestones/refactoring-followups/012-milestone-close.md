---
milestone: refactoring-followups
station: milestone close
skill: process-milestone
scope: milestone-close
date: 2026-11-25
gates:
  - command: uv run pytest -q tests/test_si1_seeded_routes.py tests/test_si2_reference_identity.py tests/test_si3_ossie_identifiers.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_rf6_index.py tests/test_refactoring_pyrel_parity.py tests/test_refactoring_input_boundaries.py tests/test_refactoring_session_contracts.py tests/test_rf8_structure.py tests/test_rf1_pin_harness.py --tb=short
    exit: 0
  - command: uv run pytest -q tests/test_development_scaffold.py tests/test_poolfile.py tests/test_refactoring_pyrel_parity.py tests/test_refactoring_input_boundaries.py tests/test_rf7_input_policy.py --tb=short
    exit: 0
  - command: python -m pytest -q tests/test_rf4_peripheral.py tests/test_rf6_packages.py tests/test_fu5_retired_helpers.py tests/test_rf8_structure.py tests/test_rf6_moves.py .gnd-planning/milestones/refactoring-followups/evidence/F7/test_audit.py --tb=short
    exit: 0
  - command: zensical build --strict && cmp docs/assets/refactoring-import-migration.tsv site/assets/refactoring-import-migration.tsv
    exit: 0
  - command: python -m pytest -q tests/test_refactoring_session_contracts.py::test_portable_v6_terminal_evidence tests/test_poolfile.py::test_pool_file_errors --tb=short
    exit: 0
evidence:
  - path: .gnd-planning/milestones/refactoring-followups/notes/refactoring-followups-plan.md
    sha256: 8b8aa057d6dbd940adf567008871bdf4b16c800aec8f2f8ec728005630dfc7a2
  - path: .gnd-planning/milestones/refactoring-followups/011-panel.md
    sha256: e70de480bdc061a9fb605e10d2f1110acf30de3fc044e677a7869430bfa0c28e
  - path: docs/assets/refactoring-import-migration.tsv
    sha256: 0c6f06f1a76a2e52f1ba145f684d6a153dbc09e114801112c0ff68c02652879e
---

# Delegated close ruling

Accepted for the named eight-phase milestone under the owner's auto=true instruction and delegated architectural judgment. Eight issue dispositions are accepted (#298–301, #303, #306–308). Four have delivered changes and open criteria (#297, #302, #304, #305). The fourth partial supersedes the three-partial proposal in the reviewed packet. GitHub tracker state, PR merge and release are separate owner decisions. The owner explicitly authorized the four transfers in #308.

The phases executed approved r2 (e41991fce641c1a2c5539b75014c57b17c0f99aa31bb07c61179b09d4c27cdfa). The five successful close reviewers saw r3 (07d736cf14c9590b7748cb99e79cf98dff7cfc85020fab07dc15f068aabee258). This ruling accepts amended r4 at the digest above. The [review report](evidence/close-panel/PANEL-REVIEW.md) retains disagreement and the pre-repair evidence. The owner delegated the decision. The advisory panel did not issue a consensus approval.

## Phase and issue reconciliation

- [003-phase-F1](003-phase-F1.md) · c852cb96d537c2ac4c16996b7d821306b9eed402df5c8928b54cf0486d029bc0
- [004-phase-F2](004-phase-F2.md) · ca5ca31dfe739381f9e770eb37838753bcdf4d6e8c4017f23a3a77dca6ed3bbc
- [005-phase-F3](005-phase-F3.md) · 73f2a0c684aa458301ec410035dcdab650a4b8f0acc72a5ba75009b359b25d27
- [006-phase-F4](006-phase-F4.md) · 58016d92c47cc4e2364db3cd92bf2095a0483c3fa699cda79ead2671071c216d
- [007-phase-F5](007-phase-F5.md) · 2e48f90cb5021dae7be8a12d2940afefd52322c7f5768acfa8a9b14a2695dddb
- [008-phase-F6](008-phase-F6.md) · de55c11689a773d6e59e370525638117d8a6bd81d24ae0ace09246f27e183f0f
- [009-phase-F7](009-phase-F7.md) · b72b84e1a7e58da8293a2ee4bee9541671a43b01f2aa524d0e4b0e99cc6e28b0
- [010-phase-F8](010-phase-F8.md) · a70e67c9d91340806e9c5411e5ac4565775d9d76e1596f363c2cf43d116bdbf6

- F1, #300. The physical read is capped before decoding. The close regression now checks that an under-budget malformed JSON object preserves the decoder exception and position. The physical-cap and Unicode cases remain in the same test file.
- F2, #306. The four historically owed inventory rows are RF2 measure/report.py:488, RF5 without byte pins, RF6 package split and RF4 directory_identity. The [phase spec](notes/phase-F2-spec.md) corrects the two hex validators and the file-byte hasher. F2's refactoring review retained one guard and the shared substitution loop.
- F3, #298 and #305. The three pinned core groups are assurance, checker and model. The four lane groups are evolve, recovery, review and synth.oracle. The [initial inventory](notes/F3-readiness.md) and [phase record](005-phase-F3.md) bind layer direction, cold imports and group membership. Thirteen equivalent occurrences moved. Distinct exemptions count expressions with multiplicities, so removing thirteen occurrences removed nine distinct rows (294 to 285), with 349 remaining occurrences. When any listed consumer changes, the query owner must compare its individual semantics before migrating it. The independently approved version had twelve sites. The thirteenth site and four observations were checked after review.
- F4, #301 and #302. The 314 and 127 counts refer to different selections of seven and three files as recorded in F4. Both include the boundary module. The JSON helper refuses NaN and both infinities, including nested floats. Its three typed service producers expose no float field. Direct Python callers must provide finite values. The two-host-table MIME control shows that historical classification can vary. The [intake inventory](notes/F4-intake-inventory.md) describes preserved parser and error variants. The component maintainer takes up other reader limits, validator-by-validator error contracts and deterministic MIME policy at the next change to the relevant intake contract.
- F5, #299, #303 and #304. Four helper groups received individual share/retain decisions. Refusal to reuse incomplete terminal evidence and recovery through a fresh run are accepted policy for #303. The session maintainer revisits the contract on any proposal for resumable terminal runs. For #304 the same contract bytes produce matching base, controller and effective prompt digests across roots, and a one-byte change alters all three. The old wire fixtures pass. The close regression also exercises reuse of an already completed portable-v6 run and checks exit 74 and unchanged files. Full cross-root evidence parity has a separate open criterion under #304 for the session maintainer when portable evidence or replay next changes.
- F6, #307. The delegated decision accepts positional address parity in the domain both programs admit. The offline fixed export stayed byte-identical. The export maintainer must revisit the different malformed-declaration policies at the next change to the generated reader, where any change to generated bytes needs its own release ruling. No native database gate was run.
- F7, #297. All 1,373 rows and 1,252 spellings were recounted on the integrated table. The compatibility suite plus four audit controls passed on b12be6a2. The strict site build served exactly the tracked TSV bytes. The two class-body guard changes repaired in F7 were caused by the F5 validator extraction and were detected by the F7 compatibility suite. The release owner reassesses removals at the first public API release review following the release that carries the notice.
- F8, #308. The [public question register](../../open-questions.md) preserves the four source questions, original wording, provenance, states and triggers. Two are open and two carried. Their transfer is complete.

## Review and measurement boundaries

The named Claude diff outputs below are the independent opinions. F1–F6 used direct review. Helper bookkeeping failures have no evidentiary weight. F7 and F8 used completed helper rounds. The separate maintainer refactoring assessment accepts the existing bounded reader in F1, shared test guards in F2, snapshot query home in F3, distinct parser policies in F4, scoped helper sharing in F5, fixed generator boundary in F6, existing compatibility aliases in F7 and register-only transfer in F8. The delegated ruling accepts the measured repairs and integration mapping at c0fe7b0e. Only the submitted phase diffs received independent phase opinions. Gemini's request for subsequent independent approvals goes beyond the selected single-round protocol.

| Submitted phase diff | SHA-256 of review input | Retained opinion |
|---|---|---|
| F1 | 8b894b5bde35b5c81a0178b12c2c30bdcb92d41886b80eb154391a7ff16a01b7 | [Claude review](notes/F1-Claude-review.md) |
| F2 | 654d3d6f36af9bf19b085e4849c97ded0d94a7d692ae08c42d747a418b47ab76 | [Claude review](notes/F2-Claude-review.md) |
| F3 | 2c26142c16ab6314a9667de85bf2727163d8b7e1bae6833f680d66f11c770e14 | [Claude review](notes/F3-Claude-review.md) |
| F4 | ff28e17f9c1b8085df391635542f55f0dd38e77ee4974ee1f8c3b474202a6372 | [Claude review](notes/F4-Claude-review.md) |
| F5 | cf3c11592e637c65e34902ed0d9d343bb9b38aeef86275daf99aa1b672ad0182 | [Claude review](notes/F5-Claude-review.md) |
| F6 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | [Claude review](notes/F6-Claude-review.md) |
| F7 | e56211ca2c525dfe0aa4129e1098ed5359608ce296c2bd7760dec4facf054d4a | [Claude review](notes/F7-Claude-review.md) |
| F8 | b3ee1ee303efffbe31effc82a5279dfbdaa096cf7885f8b5cd12f806354778c2 | [Claude review](notes/F8-Claude-review.md) |

Selected gate output, in command order:

    250 passed, 34 deselected in 167.46s (0:02:47)
    176 passed, 1 deselected in 85.68s (0:01:25)
    1186 passed in 86.97s (0:01:26)
    No issues found
    2 passed in 3.40s

The integrated selections ran on b12be6a2. The final two new assertions ran on the close repair. A duplicate scaffold run in the development checkout included a separate nested worktree with a broken relative skill link (1 failed, 175 passed, 1 deselected). The clean checkout of the same committed source passed all 176 selected checks. The 1,186 includes the F7 compatibility suite and its four audit controls. These overlapping selections are reported separately. Full default and evidence/census suites, live services, native PyRel, release and formal certification were outside the exit gates.

The subsequent combined repair regression command `python -m pytest -q tests/test_refactoring_session_contracts.py tests/test_poolfile.py tests/test_rf1_pin_harness.py --tb=short` exited 0.

    122 passed in 53.90s
