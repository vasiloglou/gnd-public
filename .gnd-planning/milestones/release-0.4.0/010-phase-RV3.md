---
milestone: release-0.4.0
station: phase-RV3
scope: phase-RV3
date: 2026-11-17
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
implementation_commit: ee3173eb342621f7452c326f97a2650f6b5402ca
gates:
  - command: "Read-only GitHub and PyPI hand-over snapshot; shasum -a 256 -c SHA256SUMS in the retained directory"
    exit: 0
  - command: "uv run --no-sync python tools/release_text.py check (prepared tree)"
    exit: 0
  - command: "uv run --no-sync pytest -q tests/test_release_docs.py tests/test_release_preparation.py tests/test_release_version.py tests/test_release_text.py --tb=short (prepared tree)"
    exit: 0
  - command: "Publication helper on the frozen scratch tree before the supplement"
    exit: 1
  - command: "rehearse-publication.sh <scratch> <supplement> (apply check, release tests, text check, strict docs, site links)"
    exit: 0
  - command: "uv run --no-sync ruff check --output-format json"
    exit: 1
  - command: "claude --print --safe-mode --model opus --permission-mode plan --output-format text --no-session-persistence (brief on stdin)"
    exit: 0
  - command: "review_tool.py status <RV3 round> --format json"
    exit: 1
  - command: "Validate five dossier shell blocks with bash -n; scratch attachment checksums and corrupted-sdist negative control"
    exit: 0
evidence:
  - path: .gnd-planning/milestones/release-0.4.0/008-phase-RV2.md
    sha256: 361ccfce855668c338f667dcf6206a8b9a73b879bf3c1514b77c25ae12a6cc04
  - path: .gnd-planning/milestones/release-0.4.0/009-RV3-spec-gate.md
    sha256: c1282b73e76b1eecefc5df0d70b79235cecf9f0c4462eb1480c4568561cc1f44
  - path: .gnd-planning/milestones/release-0.4.0/evidence/RV3/contributor-realpaths.txt
    sha256: b08c3140bfc6316a5666864697c95e33c6744ee5b7b2b3bd17ceca046136f5c3
  - path: .gnd-planning/milestones/release-0.4.0/evidence/RV3/dossier.md
    sha256: fc7707c88253612c1d6c8f0a76419de07dfce1d4b41dec57180186d4825b400c
  - path: .gnd-planning/milestones/release-0.4.0/evidence/RV3/github-release-notes.md
    sha256: a3d5267c1fcc9b6eca9d09c33d288cf4145696307432b619d668eb0f9f7124ac
  - path: .gnd-planning/milestones/release-0.4.0/evidence/RV3/post-publication-supplement.patch
    sha256: e9b4f82ff62d6b3f1ee0a072d9be3cb16ce341fd8148bc60ba664f8cc4b8ae1d
  - path: .gnd-planning/milestones/release-0.4.0/evidence/RV3/pre-publication-state.txt
    sha256: 2a6f2e7c7ebf326172948146d7ee4a0625333ccc11afc5de99beddf568b83aae
  - path: .gnd-planning/milestones/release-0.4.0/evidence/RV3/rehearse-publication.sh
    sha256: 21ae6775aaf90a48c34659aac50e43bfaed5e190565efc8cbd55218b3c201755
  - path: .gnd-planning/milestones/release-0.4.0/evidence/RV3/scratch-verification.txt
    sha256: 02350aec0f3f30f3b1b28bb878e9cdb2f1eaf125a99efe59614063040a946875
  - path: .gnd-planning/milestones/release-0.4.0/evidence/RV3/tool-only-preview.txt
    sha256: 5f5d1a36c57df1ab2f20619230b8a35e78e9f5b407b5cbf5a06af72a3cdf0596
  - path: .gnd-planning/milestones/release-0.4.0/notes/reviews/phase-RV3-r1/review.md
    sha256: cedbaed83f4aaf5bb0eb43978a1f0b11a82a659adba491e6a6de77e152c78bb9
  - path: .gnd-planning/milestones/release-0.4.0/notes/reviews/phase-RV3-r1/run.json
    sha256: d54128e5ae47a4076bc549bb6eb6250cd1afa2ddc8b1902751cd87fe1b89e800
  - path: .gnd-planning/milestones/release-0.4.0/notes/reviews/phase-RV3-r1/FINDINGS.md
    sha256: 2d992f99789c44afc1e452d9a51c1bfaf984cd69e5354fdc78a65c94df99cabe
---

# Claim

RV3 prepared the [handover dossier](evidence/RV3/dossier.md) for the accepted
wheel and sdist at source `648cc6e07fc6ea0e4d8791a2a33a0d005f4e106a`.
The retained bundle rehashed successfully. The read-only snapshot shows
0.4.0 is absent from PyPI, zero release workflow runs and no new publisher
environment. The release-specific workflow diff was empty.

The [scratch rehearsal](evidence/RV3/scratch-verification.txt) used the frozen
source and a stand-in date. The automatic helper exited 1 with residual
messages. The supplemental patch applied and removed the prepared installation
guidance from the two BookRec pages, the receipts page and the marketplace
page. The final scratch text, release checks, strict docs, and links passed.
The publication branch still uses the prepared release pages.

## Review

One Claude Code Opus reviewer verified the original hand-over digests and
reproduced the scratch text result in memory. It could not verify live
remote state or the test and site build runs. The
[findings ledger](notes/reviews/phase-RV3-r1/FINDINGS.md) records the seven
dispositions, including explicit command inputs, attachment verification,
both build profiles and the full scratch gate transcript. The review status
tool flags the revised evidence as changed from the original opinion.
The scripted rehearsal, shell syntax checks and attachment controls cover
the revised hand-over.

## Gate output (verbatim selected lines)

    Tool-only publish exit: 1
    git apply --check <supplement>: exit 0
    no page describes the state before 0.4.0 was published
    85 passed, 1 deselected in 0.49s
    uv run --no-sync --group docs zensical build --strict: exit 0
    18347 local links/assets/anchors checked
    uv run --no-sync python tools/check_docs.py site: exit 0
    Scratch publication diff SHA-256: 3f0b4e33bce19b7db039d53387c62143c56081e6c46b765f4b88c0562eb837cf
    Five owner command blocks parse in bash; no publication commands executed.
    Attachment rehearsal accepts retained bytes and rejects a changed sdist.
    188 Ruff diagnostics, identical to RV1.

## Refactoring review

The hand-over reuses the canonical release helper and receipt formats.
The supplemental patch changes scratch documentation only. No production
refactor was needed.

## Boundary

One reviewer is one reviewer. All publication actions remain pending:
ownership and authority, final availability, upload, annotated tag,
GitHub release, verification against served files, and the publication-page
PR. The evidence records preparation and one verified candidate. Milestone
close follows the authorized publication stage and the standard close panel.

## Open questions

- The owner must authorize the hand-over PR merge separately.
- The publication stage requires explicit current authorization for each
  act. The close must compare remote state with both pre-publication
  snapshots and with dated execution receipts.
