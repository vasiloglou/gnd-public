---
milestone: release-0.4.0
station: phase-RV1
scope: phase-RV1
date: 2026-11-17
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
implementation_commit: ac4b96afc4a5ba269b395b9eb5434f0c489966a9
gates:
  - command: "claude --print --safe-mode --model opus --permission-mode plan --output-format text --no-session-persistence (brief on stdin)"
    exit: 0
  - command: "python3 .codex/skills/process-phase/scripts/review_tool.py status .gnd-planning/milestones/release-0.4.0/notes/reviews/phase-RV1-r1 --format json"
    exit: 1
  - command: "uv run --no-sync pytest -q tests/test_release_version.py tests/test_release_docs.py tests/test_release_text.py --tb=short"
    exit: 0
  - command: "uv run --no-sync --group docs zensical build --strict"
    exit: 0
  - command: "uv run --no-sync python tools/check_docs.py site"
    exit: 0
  - command: "uv run --no-sync python tools/release_text.py check"
    exit: 0
  - command: "uv run --no-sync ruff check --output-format concise"
    exit: 1
  - command: "six post-review default-lane shards on beast-3 using evidence/RV1/verify-shards.sh"
    exit: "1, 0, 0, 0, 0, 0"
evidence:
  - path: .gnd-planning/milestones/release-0.4.0/003-RV1-implementation-gate.md
    sha256: cf2ceff6a69ea830b6f510ff3c0a6be73a895fd519fd3c5220d66b61ba6f0463
  - path: .gnd-planning/milestones/release-0.4.0/004-RV1-verification.md
    sha256: a2ed98501a186a920907ec93a5be632fe2d5f390ac8b4d1a318d62e4ed56d9b3
  - path: .gnd-planning/milestones/release-0.4.0/evidence/RV1/post-review-verification.txt
    sha256: 6eefee3be77811c935c092fd8ec927b8a7f8f342ceb6eb89cd046feae2ba7004
  - path: .gnd-planning/milestones/release-0.4.0/notes/reviews/phase-RV1-r1/diff.patch
    sha256: 9ededa2ee6266b8439a02eb444ce134015199932493c18633d6cf6733680ceab
  - path: .gnd-planning/milestones/release-0.4.0/notes/reviews/phase-RV1-r1/run.json
    sha256: 1812e184955059b77ccb51496c7dcc63fa485f76499658051b6cef76b9ae23bd
  - path: .gnd-planning/milestones/release-0.4.0/notes/reviews/phase-RV1-r1/review.md
    sha256: 0cd3aec9bb3acbcf5a7e6f70d1e2db8802e7c7f913b89223fb6f84b5f593c02a
  - path: .gnd-planning/milestones/release-0.4.0/notes/reviews/phase-RV1-r1/FINDINGS.md
    sha256: 81784923c5ef569fcbb53cc69e972c8f44627a559a431cf2682efbfbb903510f
---

# Claim

RV1 prepared GND 0.4.0 on the release branch. The declared version, editable
lock entry, three marketplace manifests and prepared release pages agree.
The four install pins still point to published 0.3.0. E1 established the
version-only impact before candidate implementation and the repaired
comparisons preserved the twelve committed example artifacts.

The [verification checkpoint](004-RV1-verification.md) records the initial
focused, structure, lint and full-lane gates. The
[post-review rerun](evidence/RV1/post-review-verification.txt) binds the revised
candidate tree `3b6ccce4603f0967999622172792f3367667ba98`. It matches the
baseline with 19,699 passes, 13 skips, and the two known optional-wheel setup
errors. Every failure from E1 resolved. Ruff reported the same 188 baseline
findings from the vendored tools. Changed-test lint exited 0.

## Independent review

The owner authorized the repository's default Claude Code Opus review for the
RV1–RV3 diffs on 2026-11-17. The [RV1 review](notes/reviews/phase-RV1-r1/review.md)
confirmed the reviewed digests, version sync, recorded output checks, and
publication-test controls. It ran 168 selected tests on CPython 3.14.3.
It did not run the separate beast-3, structure, lint, or strict-docs gates.

The [findings ledger](notes/reviews/phase-RV1-r1/FINDINGS.md) records three
dispositions. The review led to an explicit 0.3.1 carryover in the upgrade
paragraph for 0.3.0 users. The placement control failed before that edit and
passed afterward. A scratch publication reproduced the receipts wording
escaping the stale check. The corrected inventory assigns that page and the
two BookRec pages to RV3. RV3 also regenerates the release opening paragraphs.

The review helper exited 1 for the release notes and reconciliation bytes
changed by disposition. It reported a completed round with no ledger problems.
The recorded opinion covers the original diff. Verification covers the
revised bytes.

## Gate output (verbatim)

    72 passed in 0.30s
    No issues found
    18344 local links/assets/anchors checked
    0.4.0 is not in RELEASED: nothing to check before publication
    Found 188 errors.

    2489 passed, 118 deselected, 2 errors in 440.79s (0:07:20)
    3941 passed, 102 deselected in 393.08s (0:06:33)
    2796 passed, 13 skipped, 184 deselected in 491.83s (0:08:11)
    3538 passed, 123 deselected in 624.61s (0:10:24)
    3888 passed, 71 deselected in 707.33s (0:11:47)
    3047 passed, 255 deselected, 1 warning in 755.36s (0:12:35)

## Refactoring review

The publication-tool tests now use a fixed synthetic site for historical
mutation cases and retain a live checkout check. The example tests use the
existing version-comparison helpers. The changes needed no production
refactor.

## Boundary

One reviewer is one reviewer. This phase exercised the default test lane and
strict docs verification. Wheel and sdist acceptance belong to RV2, which
requires the owner-merged RV1 PR. The phase neither updates publication pins nor
creates any release artifacts for upload.

## Open questions

- RV3 must verify the publication-time checkout guidance in
  `docs/expense/05-receipts.md`, `docs/bookrec/08-guarded-rules.md` and
  `docs/bookrec/09-suggested-rules.md` against the actual scratch patch. The
  existing tool does not flag the receipts wording.
- RV3 regenerates the opening paragraphs named in F3.
- The milestone close sweep should carry the inherited dev-tools lint findings
  to their owning repository and record the two baseline setup errors.
