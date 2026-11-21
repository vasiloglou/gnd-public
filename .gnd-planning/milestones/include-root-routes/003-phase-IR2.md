---
milestone: include-root-routes
station: "phase-IR2"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-IR2
date: 2026-11-21
gates:
  - command: "uv run pytest -q tests/test_ir2_flatten.py tests/test_lx1_flattening.py tests/test_lx2_witness_flattening.py tests/test_extract_cli.py tests/test_public_extract_boundary.py tests/test_rf1_semantic_pins.py tests/test_rf1_cli_pins.py tests/test_mc1_guards.py tests/test_ir1_judgments_includes.py --tb=short"
    exit: 0
  - command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py tests/test_release_text.py --tb=short"
    exit: 0
  - command: "uv run ruff check src tests tools"
    exit: 0
  - command: "uv run pytest -q tests/test_codegen_manifest.py tests/test_exp_bands.py tests/test_exp_spec.py tests/test_install.py tests/test_public_payload_alias_sites.py tests/test_recovery_adversarial.py tests/test_rf1_session_pins.py tests/test_rf1_helper_pins.py tests/test_object_type_description.py tests/test_rf4_premove.py --tb=line"
    exit: 0
evidence:
  - path: src/gnd/extract/flatten_service.py
    commit: 1311ae6d
    sha256: fcba028c35b09c521bbc64614486baa2206df35e4813989a5cdaedf3b4ce97db
  - path: src/gnd/commands/flatten.py
    commit: 1311ae6d
    sha256: 2001fc46743f6f288a023c254c8e463b30686c3805455c37340fbdb0525a8f45
  - path: src/gnd/terms.py
    commit: 1311ae6d
    sha256: 1c4030334c412bd7a7b9b14df241247c8ac6b6c33d0cfcbdc4d246f8fb117944
  - path: src/gnd/cli.py
    commit: 1311ae6d
    sha256: 9f5e190daef5d07361073ed2e1bc25c3ec33846f75ba7f78dc2ca7840cfad751
  - path: tools/gnd_arch.py
    commit: 1311ae6d
    sha256: 324efc879a64e5c93f64bcdadf3c7cee935f5c4740dca2e042d8dc3d83af43dd
  - path: tests/test_ir2_flatten.py
    commit: 1311ae6d
    sha256: a8eb91ddcca3d0b9ec8f436d9f542b1cb9f2d478cab93535352c64525ae3f055
  - path: tests/test_rf1_cli_pins.py
    commit: 1311ae6d
    sha256: da90bcd9fb4c9289d13b3d96595fdc791512c7eb9e4818e6a14fda56531580f0
  - path: .gnd-planning/milestones/include-root-routes/notes/phase-IR2-spec.md
    commit: 1311ae6d
    sha256: dbbebda3fe0480b48b5b37dcc0c2ce9e40a210fb13ecd197140af75c98559079
  - path: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/review.md
    sha256: 62ca1c90818dbfc04b9ed4f05d4ec40afea260c93a380e3826b980eac1173d9a
  - path: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/FINDINGS.md
    sha256: 03a5bf826c3149c9955b75fcdc3c8ff0ad0bc2ce119f3fb540e5bb6e6d8e7555
---

# Claim

`gnd flatten` writes an include root's flat model and its
`gnd-flattening/1` record, temporal roots included: the IR2 focused lane
exited 0 (382 passed) and the guard block exited 0 (712 passed).

## Gate output (verbatim)

Focused lane (plan §9 IR2, plus `tests/test_rf1_cli_pins.py` and the IR1
file):

    382 passed in 34.76s
    exit=0

Guard block, plus `tests/test_release_text.py`:

    712 passed, 2 deselected in 94.90s (0:01:34)
    exit=0

Lint over `src tests tools`:

    All checks passed!
    exit=0

Consumers of `tests/support/rf5_sources.py` (the CLI source set), on the
final bytes:

    452 passed in 123.82s (0:02:03)
    exit=0

Whole-repository ruff is not re-run here: its known red (dev-tools scripts,
`002-phase-IR1.md`) is unchanged by this phase, which edits nothing under
`.claude/` or `.codex/`.

Corpus, committed red before code (`68e426ca`): 15 cases failed (no
command, exit 64); all pass now, with five cases added after the review.

## What the cases establish

| Criterion | Case | Result |
|---|---|---|
| IR2-C1 | T1 | exit 0; bytes equal `flatten_model`'s; origins and `publication_not_before_submission` kept |
| IR2-C2 | T2 | equal exit and verdicts, root and flat in the root's folder |
| IR2-C3 | T3, T4, T5, T12 | exit 3 with `flatten needs a model that declares includes`, `include:hash-mismatch`, `include:forbidden-section`, `include:declaration` |
| IR2-C4 | T6 (both files), race and rollback cases | exit 11, nothing written; a failed second link leaves the folder empty, exit 74 |
| IR2-C5 | T8, F2, `tests/test_rf1_semantic_pins.py` | extract names `gnd flatten` for a temporal include root; synth and include-free models keep the historical message |
| output bands | T7, T11, F1, F3 | 66 missing model; 0 with a stderr note elsewhere; 74 for a file or NUL path |
| rule 2 | T13 | 1,000 extra types under 5 s |
| registration | T15, guard block, CLI successor and its negative control | exit 0; guards green; a changed help turned three pins red |

## Review

One reviewer is one reviewer: Codex, read-only, through the review helper
(`notes/reviews/phase-IR2-r1/`, brief sha256 `b6d08591…a5b0`), over the diff
from `68e426ca`. Verdict `CHANGES_REQUESTED`, three findings (F1 blocking,
F2 and F3 hardening), each reproduced as a failing test on the reviewed
bytes and fixed in `1311ae6d`. The fixes were not re-reviewed. The
reviewer ran no suite (read-only); it confirmed the other claims by probe.

## Refuted premises

- Plan §9's IR2 lane named no CLI pin file. A new top-level command changes
  `tests/test_rf1_cli_pins.py` and six other inventories (spec i1). The
  lane was widened in this phase; the plan's row is repaired at the close.

## Boundary -- what this result did NOT establish

- The cases run over the interop fixture and `write_case`. They establish
  nothing about other include shapes beyond what `compose` and
  `flatten_model` already test.
- A flat model written outside the root's folder cannot bind its reference
  populations; `gnd flatten` says so and `gnd check` then exits 3 (T11).
- The CLI successor is declared in the test, so it pins the declared shape
  of `gnd flatten`, not its correctness.
- The review fixes carry no review opinion. No merge or publication is
  authorized by this record.

## Open questions

- None new. The checker scaling and the lint red from IR1 remain open for
  the close.

## Refactoring review

None needed, argued from what the phase touched: one new service module
and one command module in the shape of their neighbours (`commands/judgments.py`,
`extract/service.py`), a two-line change to `require_non_temporal`, and
inventory rows. `flatten_to` reuses `_flattening_names`, `bundle_stem`,
`safe_output_path`, `flatten_model` and `_print_issues` rather than
restating any of them. Its no-replace publication is a second
implementation beside extract's staging-and-rename; extract's replaces
files by design and `gnd flatten` must not, so they are not one helper.
