---
milestone: literature-interop
station: phase-LX1
skill: "n/a -- repository development under process-phase"
scope: phase-LX1
date: 2026-11-15
gates:
  - command: "uv run pytest -q tests/test_lx1_flattening.py tests/test_mc1_model_includes.py tests/test_mc1_guards.py tests/test_extract_cli.py tests/test_extract_manifest.py tests/test_extract_projection.py tests/test_extract_guidelines.py tests/test_verify_cli.py tests/test_li0_witness_wire.py --tb=short"
    exit: 0
  - command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
  - command: "uv run ruff check"
    exit: 1
  - command: "uv run ruff check src/gnd/extract/service.py src/gnd/export/verification_service.py src/gnd/model/_documents.py src/gnd/model/_includes.py src/gnd/model/flattening.py src/gnd/witness/io.py tests/test_li0_witness_wire.py tests/test_lx1_flattening.py tests/test_mc1_guards.py tests/support/rf9_ci_sources.py tests/support/pyrel_application_successors.py"
    exit: 0
  - command: "python3 scripts/components_index.py changed --base 183972ea --strict"
    exit: 0
  - command: "python3 .codex/skills/process-phase/scripts/review_tool.py run .gnd-planning/milestones/literature-interop/notes/reviews/phase-LX1-r1 --reviewer claude --wait"
    exit: 1
  - command: "claude -p --model opus --permission-mode plan --add-dir <review-dir> -- 'Read <review-dir>/BRIEF.md and follow it.'"
    exit: 0
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: explicitly scoped owner or CI selection
  reason: current wire and source controls cover the direct impact
evidence:
  - path: .gnd-planning/milestones/literature-interop/004-phase-LX1-spec-gate.md
    sha256: e479b236e02eac2ae2f487855d47a296cd51a62e09756f5d70a64fdab0af5999
  - path: .gnd-planning/milestones/literature-interop/notes/phase-LX1-spec.md
    sha256: b631be3d5a227dca151363036feb3a3db9d9818a7a58e2045983556111a71da8
  - path: src/gnd/model/flattening.py
    sha256: 75d50046b53d284ff49e8fb19b8e24178e8e24988bfa14eeac7ad774fa00dfed
  - path: src/gnd/extract/service.py
    sha256: d0b6849c02db97521330bddd65ffa4e8a308e751599f3ebf5200df8f4996d57e
  - path: src/gnd/export/verification_service.py
    sha256: 7e1c39a696d25337955e4955c6cce4cd4baad41cb75c91fbf0a27ed9e7ef2908
  - path: src/gnd/skills/gnd-orm-core/references/representation-format.md
    sha256: 7feb364cab8421af06bccfd356384a191482c5c48ab08a7dbef3c9deecbde852
  - path: tests/test_lx1_flattening.py
    sha256: 27e0e865e2303b1138c3472c602f40860a6428b3c2d7a30c4a4f8e4011d4cf51
  - path: .gnd-planning/milestones/literature-interop/evidence/LX1/source-successors.json
    sha256: 9af4e2fee29626a7e28d1b71afa5450a72d17d29c968d320a7e499c4762fb6a9
  - path: .gnd-planning/milestones/literature-interop/evidence/LX1/dynamic-query-successor.json
    sha256: 6309a0664fb9dc6411e2c8a71881e717cf26dba63c5d795baa70d1515e316d94
  - path: .gnd-planning/milestones/literature-interop/notes/reviews/phase-LX1-r1/BRIEF.md
    sha256: 44872ed192d0c4c0eed5af71606f6e0cbb01586a4eb997b6dd7e153f3946bd84
  - path: .gnd-planning/milestones/literature-interop/notes/reviews/phase-LX1-r1/brief.json
    sha256: 908a767b8df4deeaca1d06ac30b4db70034a47b255f2a35252dfb8962ccb6b24
  - path: .gnd-planning/milestones/literature-interop/notes/reviews/phase-LX1-r1/diff.patch
    sha256: f8ac558485e8e249947079d4f96ebb90c7e9878bf1fa47d3a6400687b796b459
  - path: .gnd-planning/milestones/literature-interop/notes/reviews/phase-LX1-r1/run.json
    sha256: 6a273e719e2a84eed9d84f624168bb58f8f39dc6847899f3b00b6a9cdad43c0b
  - path: .gnd-planning/milestones/literature-interop/notes/reviews/phase-LX1-r1/review.md
    sha256: 91398d7ed34b3f662707509aa76be5eb0e009abab076c41f95a67b2a83ce8c76
  - path: .gnd-planning/milestones/literature-interop/notes/reviews/phase-LX1-r1/FINDINGS.md
    sha256: 5de67ce28567c5aa2af49ecde1afe1da7d5e2914de4eb127cf68de0f6c87f578
  - path: .gnd-planning/milestones/literature-interop/notes/reviews/phase-LX1-r1/client-refusal.json
    sha256: 359a0f4f5c5fe8dcdff80f1a39f814ddb0a17129408050e6fc05b61013a25972
  - path: .gnd-planning/milestones/literature-interop/notes/reviews/phase-LX1-r1/client-refusal.txt
    sha256: 2122456c9827a04aff9792c1149505097ac016d61c330a0df0dd73976358987c
---

# Claim

LX1's two-include extraction and authenticated verification meet all
three plan criteria. The direct and structure gates exited 0.

## Gate output

    290 passed in 64.23s (0:01:04)
    679 passed, 2 deselected in 109.73s (0:01:49)
    Found 188 errors.
    All checks passed!
    changed against 183972ea (183972e): 39 file(s) differ; 0 to fix, 0 warning(s), 9 to reread

The full lint diagnostics equal the untouched corpus commit's 188 findings
by file, line, code and message. The amended scope and affected-component
rereads are in the spec. The package checks ran in the locked CPython 3.11
worktree install of GND 0.3.1. The omitted cases follow the default lane filter.

| Plan claim | Criterion evidence |
|---|---|
| LX1.a | Both includes resolve and the public extract and verify calls exit 0. Nine origins resolve, including the anonymous constraint and both root attachments. The flat model re-enters the loader with matching extraction projection, applicability and verbalization. |
| LX1.b | Independent root, include, flat and record changes and coordinated forgery refuse. The separate schema forgery detects repinning of both index and sidecar. Path and standalone errors, nested and unattended sources, and reference declarations within includes retain their named input refusals. |
| LX1.c | Compare complete include-free artifact bytes against the phase-base checksums. LI0's legacy serializer behavior and alias identity pass. |

## Independent review

The owner authorized one Claude Code Opus review of `e2ce2ade`. The initial
client invocation exited 1 before reviewing because the installed client's
variadic `--add-dir` consumed the trailing prompt. The retry kept the
review brief and model and used the argument separator. The
[client refusal](notes/reviews/phase-LX1-r1/client-refusal.txt),
[run](notes/reviews/phase-LX1-r1/run.json) and
[verbatim review](notes/reviews/phase-LX1-r1/review.md) are retained.

The reviewer returned APPROVE, reported 210 tests and a separate 208-case
legacy comparison, and identified no behavioral refutation. Its two
completeness findings are dispositioned in the
[ledger](notes/reviews/phase-LX1-r1/FINDINGS.md).
The reviewer did not run the project structure or lint gates or simulate
interrupted publication. The driver ran those selected gates, including
the extraction interruption test.

The separate driver schema-repin regression exited 1 against the reviewed
implementation because verify returned 0. It passed after re-derivation
was added. The review helper identifies the changed service, test and
representation wording as unreviewed against that round. The local
post-review gates bind the repaired candidate. The retained unified patch
has blank-line context markers, preserved byte for byte for its review digest. One reviewer is one reviewer.

## Refactoring review

Refactors EXECUTED. Reuse the LI0 serializer through a single model-layer
definition, retaining the historical witness identity alias. Share the
bundle verifier between the historical diagnostic helper and the verify
consumer so digest checking and snapshot selection have one implementation.
The historical CLI aliases and source-scan guards remain live.

## Boundary

LX1 verifies extraction over a resolved include-backed model. Witness and
replay provenance are LX2. Reference-catalog composition and checking-model
rebinding have later phase gates.

## Open questions

- The dev-tools review-helper maintainer owns the variadic Claude argument
  transport follow-up. LX1 used the documented client separator without
  editing the synchronized skill.
