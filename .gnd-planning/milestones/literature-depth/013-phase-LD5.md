---
milestone: literature-depth
station: phase-LD5
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-LD5
date: 2026-11-16
gates:
  - command: "uv run --no-sync pytest -q tests/test_ld5_verdict.py tests/test_ld4_revision.py tests/test_li4_assertions.py tests/test_li5_lineage.py tests/test_witness_composition.py tests/test_rule_edition_comparison.py --tb=short"
    exit: 0
    output: "106 passed in 413.64s (0:06:53)"
  - command: "uv run --no-sync pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
    output: "679 passed, 2 deselected in 326.04s (0:05:26)"
  - command: ".venv/bin/ruff check --output-format=json"
    exit: 1
    output: "188 exact inherited diagnostics; changed Python files pass"
  - command: "python3 scripts/components_index.py changed --base 4e0b542f --strict"
    exit: 0
    output: "0 to fix, 0 warning(s), 0 to reread"
  - command: "uv build --offline --wheel --out-dir <scratch>/dist"
    exit: 0
    output: "installed in a standalone scratch virtualenv"
  - command: "python -m gnd.examples.literature.verdict run release --out verdict"
    exit: 0
    output: "all five frozen outcomes from a fresh reading and revision release"
  - command: "python -m gnd.examples.literature.verdict replay release verdict"
    exit: 0
    output: "fresh and replay reports match byte for byte"
  - command: "python -m gnd.examples.literature.verdict evaluate release --case reject-both"
    exit: 2
    output: "unsupported"
  - command: "python -m gnd.examples.literature.verdict evaluate release --case both-approved --edition revised"
    exit: 3
    output: "revalidation-required"
  - command: "claude -p --model opus --permission-mode plan --add-dir <review-dir> -- '<brief-path prompt>'"
    exit: 0
    output: "CHANGES_REQUESTED"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: explicit owner or CI selection
  reason: current affected public routes use the focused and installed gates
evidence:
  - path: .gnd-planning/milestones/literature-depth/011-phase-LD4.md
    sha256: e108270204a5e5817e98c14b720f9a9a5aa835816a33e6c365553c6bebe48a75
  - path: .gnd-planning/milestones/literature-depth/012-phase-LD5-spec-gate.md
    sha256: 8e990c62c07b7d31da976b40f06fbcb457070566cd4de5eeb7b9e9df72f9de03
  - path: .gnd-planning/milestones/literature-depth/notes/phase-LD5-spec.md
    sha256: a7d17a5ad2369f796c0261aa29ca9b315c9ac8119ef7ccc8b29326d5de7d6616
  - path: .gnd-planning/milestones/literature-depth/notes/phase-LD5-amendment.md
    sha256: d6fb86e1f3a9843fe18031c53c3e511405958ebeee1630e93eb480e69de90cfb
  - path: .gnd-planning/milestones/literature-depth/evidence/LD5/installed-observation.json
    sha256: 48d9c7735238a9046f637d19d0c8046fcbc59ed7abaffe1e43a7e648a0e2a387
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD5-r1/BRIEF.md
    sha256: 074986cbeb92b355594e7c5d4724cddfa83ec03495d9c6579104fc66f7dea9e5
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD5-r1/FINDINGS.md
    sha256: 4f965ffacdb696df34265d7ed075fce7fdb3b29b48979ea4ca0037237f5a751b
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD5-r1/brief.json
    sha256: 399c5ebdda348072c8b625b36c050c02a53a2fd9bc18b2f6621b9f2c686c0820
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD5-r1/diff.patch
    sha256: baa6606b5d26a9f600f2d5ca597080a417fa020278459258b420672cb63dfa2b
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD5-r1/review.log
    sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD5-r1/review.md
    sha256: 2464655cf062b3294d046d0391c8bab7b78d3c1d7f8f2da31c9fc0082babe90b
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD5-r1/run.json
    sha256: 1ba1e08c9ff48cbd7c4be27360cb1d5d0cab22ef7c55ff9fe4ad0c31e27ee6f6
  - path: src/gnd/examples/literature/verdict.py
    sha256: e315187ec48a3d8c92aca0467f43c863e638f816d06998fb44e3c1c494dc2d96
  - path: src/gnd/examples/literature/revision.py
    sha256: 989aa68f85e51040cd4d18b572b75ae63b4a5262fb64754440f0cc25affec443
  - path: src/gnd/examples/literature/verdict_fixture/opinions.json
    sha256: bf6a73926cbd3bd7ea296522a290308faad0b66399817ba57f7c2a44c6ca2625
  - path: tests/test_ld5_verdict.py
    sha256: f212e847125bd1f4c7fc03b6722f8733daebfab494c6118f3fe8b2d761efbec2
---

# LD5 completion

The installed example evaluates two separately pinned source opinions
for VampNet's ancestry from DMD. A verdict identifies the exact released
claim and semantic edition. Each opinion binds a reviewed source occurrence
and an independently replayable witness. It retains the other effective
support when a single certificate loses its binding.

| Criterion | Observed result |
|---|---|
| Two, one and zero supports | Two live approvals support the claim. Explicit rejection of whale-a leaves corroboration. Rejecting both yields the unsupported outcome at exit 2. |
| Shared semantic changes | Mutating the released claim, identity decisions, rule or definition independently refuses the old opinion. |
| Individual dependencies | Rehashed occurrence, resolution and review changes stale the affected opinion while the independent peer still backs the claim. |
| Revised definition | The old pair requires revalidation. A separate replacement review and a newly replayed witness restore the same whale-a occurrence. The second opinion remains stale. |
| Report replay | The installed run and replay carry identical report bytes and preserve all five declared observations. |

## Independent review

The owner authorized a single Claude Code Opus review at `2e34530a`.
The [findings ledger](notes/reviews/phase-LD5-r1/FINDINGS.md) records the
phase dispositions. The review helper identifies the files at the
original reviewed hashes and the repaired files separately. The local
verification and installed observations cover the repair. The reviewer
matched 20 input hashes and passed ten original direct tests. It reproduced
lost peer support after a consistent support-list update and an unsupported
decision when shared evidence was missing. The review addressed those paths,
the negative control coverage and renewed rule verification. The author
also reproduced a successful demonstration without a release. The repaired
entry point refuses that case without publishing.

## Refactoring review

Refactors EXECUTED. The original and renewed support paths share witness
production and replay. The verdict evaluator consumes the LD4 authored
occurrences and semantic editions without a second assertion judgment
format. Fresh and replay use the same verified scenario evaluator.

## Boundary

One independent reviewer read the original candidate. The packaged
verdicts are synthetic opinions on the selected fixture. General
assertion judgment and published witness surfaces keep their existing
scope. Part 10 remains deferred.

## Open questions

- The milestone close panel reviews the complete question sweep and
  the evidence for the accepted parts 6–8 scope.
- The Claude prompt separator remains a dev-tools review-helper follow-up.
