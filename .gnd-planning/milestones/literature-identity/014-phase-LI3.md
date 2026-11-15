---
milestone: literature-identity
station: phase-LI3
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-LI3
date: 2026-11-15
base_commit: 4735730da4c0871ff91be48b154ce5c60b4f2f77
gates:
  - command: "uv run pytest -q tests/test_li3_diagnostics.py tests/test_li1_literature_corpus.py tests/test_li2_resolution.py --tb=short"
    exit: 0
    output: "88 passed in 13.70s"
  - command: "uv run pytest -q tests/test_li3_diagnostics.py --tb=short"
    exit: 0
    output: "19 passed in 2.47s"
  - command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
    output: "679 passed, 2 deselected in 195.92s (0:03:15)"
  - command: "uv run ruff check"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base 4735730d --strict"
    exit: 0
    output: "changed against 4735730d (4735730): 35 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
  - command: "uv run python -m gnd.examples.literature.diagnostic_measurement src/gnd/examples/literature/diagnostics/measurement.json src/gnd/examples/literature/diagnostics/labels.json"
    exit: 0
    output: "exit_code: 0; family 3/52, homonym 1/24, synonym 2/24"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request only"
  reason: "The example modules and measured corpus use the direct selection and standard structure guards."
evidence:
  - path: .gnd-planning/milestones/literature-identity/011-phase-LI3-spec-gate.md
    sha256: 554e2af663529cdd23d070295c6228f914776191e21f402da883476389a2ee0d
  - path: .gnd-planning/milestones/literature-identity/012-phase-LI3-corpus-gate.md
    sha256: bee6890a3a224e3f5436ed66cdf190581358315cb1d113dbe55bc5337fc7e555
  - path: .gnd-planning/milestones/literature-identity/013-phase-LI3-family-amendment.md
    sha256: ed8acca875ed1e6185d254d4eeb39a16cd6867b77fa8af382b754e7e4393e177
  - path: .gnd-planning/milestones/literature-identity/notes/phase-LI3-spec.md
    sha256: d236004e3cb5bae04f1c5e99f1af89a5f9168336c7af920559db92d9f5bee449
  - path: .gnd-planning/milestones/literature-identity/notes/phase-LI3-claude-review.md
    sha256: 42ff0ef3f8dbd8f8b0ef9a79b2610f97ae3339d7932821e9a2a2ae62142f13f8
  - path: .gnd-planning/milestones/literature-identity/evidence/LI3/family-token-amendment.md
    sha256: 22c2737c2bf33b3dc6dd86c6d2b2d92c53c6d7e29994aa67699ab96df2d0231b
  - path: .gnd-planning/milestones/literature-identity/evidence/LI3/first-review-transport.txt
    sha256: 06040fabbe22313470c3699f50f69707b8b66a27de7c0efb20c45dfc746a0369
  - path: .gnd-planning/milestones/literature-identity/evidence/LI3/measurement-design.md
    sha256: cbba7d064badfb0aef3f3cf844ebd20bb3d1a19e9ff89b04676c5520f89cdda2
  - path: .gnd-planning/milestones/literature-identity/evidence/LI3/measurement-first.json
    sha256: 6ad5ae7ced877171af0b9313f10ecafb7d5f42994038704060118d97e03d45bb
  - path: .gnd-planning/milestones/literature-identity/evidence/LI3/measurement.json
    sha256: 2e331825a74e37c08be4bb84b0672313591c71c06be855e1db05d41fc17fac3f
  - path: .gnd-planning/milestones/literature-identity/evidence/LI3/review-repair-ruling.md
    sha256: 91edc25c4ec3d2f7668f16f2836079bb8f29cdacbdb2daa3b93650f108e68ee5
  - path: src/gnd/examples/literature/diagnostics/README.md
    sha256: 3d2d003c86486dfd5655a50ec1d015bb1c0d80814937483206a6735dbdb10ebe
  - path: src/gnd/examples/literature/diagnostics/case-outcomes.json
    sha256: d1e243b41cec7ca6f042229428dbb2b088fc456fd97eb4b1ae1cb1346c88fa96
  - path: src/gnd/examples/literature/diagnostics/cases.json
    sha256: f38f07d2e37c91dcc2d0185da30f1a396fb02550f4277bb1ef424b028e7f56c4
  - path: src/gnd/examples/literature/diagnostics/labels.json
    sha256: b95f3c72f2c119b5e31d035634fe8261c0d49e551132016d29d743c7d275418f
  - path: src/gnd/examples/literature/diagnostics/measurement.json
    sha256: 75aa507694c9b005a39009a8468a4f84c5b41a3887398c950ae61aaca6669305
  - path: src/gnd/examples/literature/name_diagnostics.py
    sha256: 415d2022048c65a2a7e98d9474b95d0962fdb1aced2224e6086eb10c3918d5c0
  - path: src/gnd/examples/literature/diagnostic_measurement.py
    sha256: ffa0d016ffa8118f64eb098e71e6e13efbf237b8b0fa78293d859661537da5cf
  - path: tests/test_li3_diagnostics.py
    sha256: 37b72b52705189e72f206060205f0cc413c422ffa8c76a26e94ea7960c242a6a
---

# Claim

LI3 emits unresolved name proposals at example scope. N1's two homonyms,
synonym and family candidate have their required kinds. N2's shared
introducing work suppresses the cross-field flow matching homonym.
Proposal decisions retain the original key, source-population digest
and evidence coordinate. Candidates remain separate from composition.

## Measured results

The input contains 300 synthetic occurrences. The corpus and its labels
were pinned in [012](012-phase-LI3-corpus-gate.md) before this run. The
grader passed the perfect and completely wrong controls and checked
the unmeasured arm. The 100 emissions sampled at seed 193 gave the
following counts.

| Kind | Emitted | Sample | False discoveries | Ceiling |
|---|---:|---:|---:|---:|
| Family | 144 | 52 | 3/52 | 1/5 |
| Homonym | 36 | 24 | 1/24 | 1/5 |
| Synonym | 36 | 24 | 2/24 | 1/5 |

The example reports candidate false discoveries over the authored
synthetic set. Each measured stratum met the predeclared ceiling.
The sample measures emitted candidates and uses the corpus author's labels.

## Criteria

- N1 and N2 use the pinned four spelling relationships, the shared-work
  flow matching suppression and its discriminating control.
- N3 uses the separately pinned label ledger and reports exact counts in
  the measurement artifact. The family-token amendment in
  [013](013-phase-LI3-family-amendment.md) was recorded before measurement.
- N4 tests malformed JSON, duplicate keys, hostile rows, invalid digests,
  the occurrence cap and the candidate cap. The 500-occurrence sparse and
  dense examples each stay below the 10-second bound.

## Independent review and repair

The retained Claude Code review traced the required kinds and the origin
suppression by inspection. It checked the sampling arithmetic, ordered
reader limits and LI2 proposal shape. It could not execute the tests
or the measurement. The first invocation returned tool markup without
a review. The technical retry yielded the sole phase review.

| Finding | Disposition |
|---|---|
| D1, generic plurals | Reproduced six false family pairs from the word families. Treat it as the generic family noun and exercise the plural control |
| D2, CamelCase | Reproduced a false homonym from AlphaFold and Alphafold with overlapping contexts. Require adjacent capitals for the acronym arm. The named acronym variants still qualify in the new shared-context control |
| D3, flow token | Confirmed the specified corpus-wide introduction rule. Clearing the two origins yields a flow matching homonym and changes the separate flow pair to family. The control now asserts both effects |
| D4, weak controls | The occurrence overflow asserts its named reason. The 500-row sparse control exercises one-edit comparisons in a shared context. Proposals parse with LI2's resolution reader. Added a wrong-kind label control at and above 1/5 |
| D5, report and input details | Reproduced the FIFO hang and ASCII output crash. The regular-file reader and ASCII-safe JSON encoding correct both. Output order is lexical and the measured rows report fractions. The revised measure changed only the added fraction fields |

The additional spelling interpretations have a digest-bound delegated
[ruling](evidence/LI3/review-repair-ruling.md). The finite candidate scope
still includes context-sensitive heuristic mistakes. The phrase
“independently authored” in the design means the scenario ledger is
authored separately from the candidate output. One corpus author
prepared both the scenarios and implementation, as the measurement
artifact states. The record makes no statistical generalization.

## Refactoring review

The classifier has one precedence function. The diagnostic and sample
runner both use the shared bounded file reader and strict JSON parser.
The body and grade are example modules. The existing composition
semantics and LI1 report remain in their prior homes.

## Boundary

For the phase diff, one reviewer is one reviewer. A single Claude Code
review provides static evidence. Executed coverage comes from the focused
tests. The measured budget applies to the synthetic sample. Plan D4 keeps the diagnostics surface at example scope.

## Open questions

The report makes no claim for any later project's label stability or
unmeasured category. Carry the D4 example surface into milestone close.
