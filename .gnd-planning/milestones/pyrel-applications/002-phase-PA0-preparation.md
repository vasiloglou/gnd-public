---
milestone: pyrel-applications
station: phase-PA0-preparation
skill: process-phase
scope: phase-PA0-preparation
date: 2026-10-13
gate:
  command: ".venv/bin/python -m pytest -q tests/test_pyrel_application_corpus.py --tb=short"
  exit: 0
  output: "128 passed in 4.42s"
slow_cadence:
  command: uv run pytest -q
  trigger: explicit owner selection or separately scoped CI
  reason: PA0 adds a bounded corpus/driver; no production change or broad replay
evidence:
  - {path: .gnd-planning/milestones/pyrel-applications/notes/phase-PA0-spec.md, sha256: 25fd4d509d18009073d0eac63f71dc63c1a38345a6e29d1a27c0a430bd7f953a}
  - {path: .gnd-planning/milestones/pyrel-applications/notes/phase-PA0-review-prompt.md, sha256: 2222e55e43aacba858ec0886b08bfcc4de3b27f07ccc7bbaa022a47deafafbbd}
  - {path: tests/fixtures/pyrel_applications/matrix.json, sha256: c9c2ef19fa6ec46cf7224b616ea538c7fe70dd860e2cbc4a24f36e93752b3472}
  - {path: tests/fixtures/pyrel_applications/answers.json, sha256: 7bed9d8569ee8aec801dd816adb62d7658500c54b3c73473204db57517c1a9e4}
  - {path: tests/test_pyrel_application_corpus.py, sha256: 743dfd58fe90e77bdfa584f12c4dcae52448e735b30b8607dbcfdc8d56dd58a6}
  - {path: tools/measure_pyrel_applications.py, sha256: afa7cca33e1b6d1ee6318b639f2518164146df5fe703cdb172c0ccab73bd42fa}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/baseline-current.json, sha256: 8f7361dd9706919425289a530d73de48cd65117a3b1bdb900c2a803707a3545a}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/baseline-current.txt, sha256: b57d491fed7cd638c59e7d7d14dd24a538d6ed1efa6bbcc095533b2b9aba7ba4}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/baseline.json, sha256: 30db3e4b1ad546eb8821978c509953c0e3b531fc8656110de0d6ed4d214d65d2}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/corpus-final.txt, sha256: 9efeca6427873987dba3485ba3cd30ecdb4aaa0a004c24d0bd2c77dada76d2e3}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/corpus-green.txt, sha256: af21b79d7c7835f30eae514e441f5b20a1552c94b27fb252b1e465dc6eb3b7b9}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/legacy-green.txt, sha256: f19ef5a3c071f9357ee0457bb85664abb11362754c27bb0c48c6b8a594d06928}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/lint.txt, sha256: 82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/successor-red.json, sha256: 51b9e2ba6882ae3aebd1e3fd7f997b49c3d795c653cbafc2074940c3b71799b0}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/successor-red.txt, sha256: ec22428035ce9220b8fbf60e412eeb9fefcff8eaa2ca1b24c2e49f6a6db69cf9}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/reference-isolated.txt, sha256: 30c0a18111db6dc7738e04991bc22c2360a36fe0125861094d989cc0e3d51e97}
---
# Claim

PA0 preparation records the approved specification and frozen executable corpus:
61 addressed obligations across five models, 124 narrated positive/negative
controls, 128 corpus checks and 72 selected legacy checks. It does not complete
PA0: independent adversarial diff review is pending instrument selection.

## Gate output (verbatim)

.venv/bin/python -m pytest -q tests/test_pyrel_application_corpus.py --tb=short

    128 passed in 4.42s
    Exit: 0

.venv/bin/python -m pytest -q tests/test_pyrel_export.py tests/test_pyrel_export_boundaries.py tests/test_public_pyrel_export_runtime_optional.py tests/test_external_runtime_tutorials.py --tb=short

    72 passed, 13 deselected in 6.06s
    Exit: 0

.venv/bin/ruff check tools/measure_pyrel_applications.py tests/test_pyrel_application_corpus.py --output-format concise

    All checks passed!
    Exit: 0

.venv/bin/python tools/measure_pyrel_applications.py --mode baseline --out .gnd-planning/milestones/pyrel-applications/evidence/PA0/baseline-current.json

    Exit: 0

.venv/bin/python tools/measure_pyrel_applications.py --mode successor --out .gnd-planning/milestones/pyrel-applications/evidence/PA0/successor-red.json

    Exit: 1

The native command streams are retained separately. All 124 legacy audit
processes exit 0. Target dispositions match 70/124 controls; 48 guarded controls
are unsupported and six supplied-derived controls have no derivation verdict.
The RED result identifies the actual runtime omissions, not a simulated absence.
Runtime is Python 3.13.12, relationalai 1.30.1, DuckDB 1.5.5; maintained lock
and exact model/population/program hashes are included in each receipt.
The generated programs lived outside history in isolated temporary directories
and were removed after execution. Their hashes are run provenance, not retained
program artifacts. Exporter/runtime source is unchanged from base 00efef2; model
and population bytes and full native reports are committed with this record.

## Supplementary reference check

The optional whole-tree development scaffold check exited 1 (1 failed, 17 passed,
1 deselected) because it traversed an existing ignored nested checkout under
.claude/worktrees and checked that checkout's historical external evidence link.
No nested checkout or user file was modified. The focused reference-closure check
on archive ac3ad34 with the current milestone Markdown overlaid excludes ignored
nested worktrees; its exact result is retained in evidence/PA0/reference-isolated.txt.
This is an environmental traversal boundary, not a passing whole-tree check.

## What shipped and approval

The spec pins opt-in applications-v1 grammar, coverage, modality, acceptance
schema/exits, raw input bindings, conservative work and process ceilings.
Existing audit completion/report interfaces are the legacy compatibility surface.
The corpus gives each rule a narrated satisfied and discriminating failure or
warning target. Both complete derived heads have positive/missing/extra controls.
GND report rows are retained comparison measurements; stories are the authored
expected controls. The default test lane runs no native PyRel process.

The owner explicitly delegated auto approval of pyrel-applications and selected
four local plan/close reviewers. 001 binds reviewed plan bytes; the spec records
its original approved prefix and later exact corpus ruling separately. No corpus
meaning was changed after successor runtime implementation: production is unchanged.
Fixture data is 5,735 lines, 317,489 bytes within the 15,000-line planning budget.
128 checks include liveness controls proving omitted obligations/changed model
hashes fail the matrix validator. Native programs are public offline exports
running in a separate interpreter with explicit DuckDB config and scratch state.

## Refactoring review

None needed in this preparation: production modules and application queries are
unchanged. A single development driver generates standalone programs per model
and collects isolated receipts; tests enumerate obligations from exact models.
The future runtime translation remains PA1/PA2, not a duplicated Python checker.

## Boundary -- what this result did NOT establish

No completed PA0 independent phase review or phase completion. No guarded or
derivation fix, native acceptance, application publication, tutorial/graphics,
installed-wheel acceptance, universal equivalence, certificate, package release
or PR merge. One reviewer is one reviewer; plan/close subagents cannot satisfy
the distinct-harness phase review contract. Local same-model plan readings are
advisory, not proof. Historical source-owned/RF/compiled-operation authority and
shim-retirement questions retain their original owners.

## Open questions and readiness

- PA0 distinct-harness reviewer -> owner selects Codex CLI or Claude Code for
  phase diffs; request pending. The concrete review prompt is retained.
- PA0 completion -> reproduce/dispose review, then completion record and commit.
- PA1 -> PA0 completion; PA2 -> PA1; PA3 -> PA2; PA4 -> PA3;
  PA5 -> PA4; PA6 -> PA5. None bypasses its dependency.
- PA-D7 graphic format/theme/source mapping -> PA5 spec.
- Source-owned questions, RF-D5 retirement and historical budget/architecture
  reconciliation -> original code-refactoring owners; no discharge claimed here.
- Publication/merge/current human acceptance -> owner, separately from auto gates.

## Refuted premises

Completion exit zero does not mean all business rules were checked: retained
native successor runs demonstrate 48 unsupported guarded targets and six absent
derivation verdicts. The malformed dangling-chain draft and mistyped consumer
path were rejected by public admission/inventory checks and corrected before
freezing the corpus. Initial baseline.json binds the pre-path-repair inventory;
baseline-current.json is the corrected current receipt, without deleting history.
