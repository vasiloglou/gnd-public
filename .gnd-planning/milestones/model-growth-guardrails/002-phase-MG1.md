---
milestone: model-growth-guardrails
station: "phase-MG1"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-MG1
date: 2026-11-03
gate:
  command: "uv run pytest -q tests/test_rule_verbalization.py tests/test_public_api.py tests/test_v61_phase2_api.py tests/test_public_runtime.py tests/test_why_not_near_misses_public.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py tests/test_model_evolution.py tests/test_evolution_conformance.py tests/test_evolve_loading.py tests/test_evolve_references.py tests/test_public_evolution_drift_readers.py tests/test_public_evolution_legacy_readers.py tests/test_public_evolution_version_graph.py tests/test_public_legacy_evolution.py tests/test_conformance_payload.py tests/test_public_built_inventory.py tests/test_recovery_adversarial.py tests/test_recovery_inventory.py tests/test_recovery_report.py"
  exit: 0
  output: "701 passed, 30 deselected in 93.69s (0:01:33)"
  note: >-
    The spec's verification selection, plus tests/test_disclosure_docs.py (the
    generated disclosure table) and the recovery files named at
    implementation. Docs commands and the parity capture are listed in the body.
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "the broad historical lanes are outside MG1's impact closure: one new API function, one renderer module, pins and docs"
evidence:
  - path: .gnd-planning/milestones/model-growth-guardrails/notes/phase-MG1-spec.md
    sha256: 2ba0a7460ee7e91295354f08f85020d718d1521db8631fa7548a01f72cd0491e
  - path: .gnd-planning/milestones/model-growth-guardrails/notes/phase-MG1-claude-review.md
    sha256: b56fef101a4c99b312f447ad350395807c4638b29832a128e7a3e4a63f7fe635
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/MG1/capture_parity.py
    sha256: cd013a826330c02444de0b58a04daeed49846746571236565be1ffc9f82fb3c8
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/MG1/parity-before.json
    sha256: 14e6af03b6b3c63eb196d04ab411c20dccb88a247903d21fa78cdf5e8989899a
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/MG1/parity-after.json
    sha256: bcdce6c4eb03f00c3b9f4f0a427c03b187589da8e328d36faeba3baf3636224e
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/MG1/dynamic-query-successor.json
    sha256: 61211da9ba78ac7ecc696674e3a942a4c37df2efa045926eeaf85d4778b0dd62
  - path: src/gnd/model_verbalization.py
    sha256: 78d28cd7d0ddf70c77233d6d80afca27818069fb03d07dbac0992c0b94bff1d8
  - path: src/gnd/api.py
    sha256: cc95b1f79c9ff46ae1e584b721eaac42fc9a704cecb5a7e26c765a28887c91b5
  - path: src/gnd/rule-verbalization.schema.json
    sha256: bc16d32e4d7bb1b8653ec723785d204e67c7d315f73de30136f5734e060857ba
  - path: tests/test_rule_verbalization.py
    sha256: d9949ff7ba8c624e381c81cce49b4a6bbfe59b9bb318cc778b6cf0383edcf83f
---

# Phase MG1: public rendering of derivation rules

**Claim.** `gnd.api.verbalize_rules(model, *, fact_types=None)` returns
`exit_code` 0 and one entry per derived fact type in id order. Over every
corpus model, each rendered `text` appears in the full model verbalization
right after `This fact type is derived: ` and is followed by one of its three
known continuations (282 rendered rules, 19 prose rules reported as
`unsupported`). An in-memory `Model` that no longer validates returns
`exit_code` 3, and `render_rule_verbalizations` raises `VerbalizationError`
for it. No partial text is returned. `render_model_verbalization` no
longer crashes on a model given by path: all 282 loaded renders are
byte-identical to `1446f90`, and the 23 path inputs that raised
`AttributeError` now equal their loaded renders. The focused gate exits 0.

**Authority.** Plan r3 approved `(a1)` ([001-plan-gate.md](001-plan-gate.md));
spec r3 approved `(s1)` 2026-11-03, quoted in the spec header, bytes
`4cddaa525a9da4d237fa863f6c3af45dd162cddb286be87e46c299cc60fce87c` before
its tag. `auto=false`. The owner selected `process-phase MG1` ("Start MG1").

## What shipped

- `src/gnd/model_verbalization.py`:
  - `RuleVerbalization`, `render_rule_verbalizations` and
    `check_fact_type_selection`.
  - An optional fallback collector threaded through `_derivation_cnl`,
    `_guarded_atom` and `_guarded_term`. With the default `None`, behavior
    is identical to `1446f90`, as the reviewer's differential fuzz showed.
  - The path-input fix: the fact-type line passes the loaded model.
- `src/gnd/api.py`: `verbalize_rules`, appended to `__all__`.
- `src/gnd/rule-verbalization.schema.json`: the closed payload schema, in
  both schema inventories.
- `src/gnd/disclosure.py`: the `api:verbalize_rules` `value-free` row. The
  generated table in `docs/reference/disclosure.md` is re-pasted.
- Pins: the four test `__all__` pins, `tools/run_public_acceptance.py` (stale
  at baseline, F5), and the signature pin in `tests/test_public_api.py`.
- RF6 syntax census: a counted successor of 13 occurrences (F6).
- Docs: a runnable `verbalize_rules` section and the ten-function count in
  `docs/reference/python-api.md`; the new `docs/reference/rule-verbalization.md`
  with its nav entry; an Unreleased release note.

## Gate and other commands

| Command | Result |
|---|---|
| focused gate (front matter) | `701 passed, 30 deselected in 93.69s (0:01:33)`; pytest exit 0 |
| `uv run python tools/run_tutorials.py --group api` | `11 tutorial blocks passed` |
| `uv run --group docs zensical build --strict` | `No issues found`; `Build finished in 0.52s` |
| `uv run python tools/check_docs.py site` | `12975 local links/assets/anchors checked`, exit 0 |
| `uv run python .gnd-planning/milestones/model-growth-guardrails/evidence/MG1/capture_parity.py …/parity-after.json` | `models=282 path_errors=0`; against `parity-before.json` (`models=282 path_errors=23`): loaded changed 0, path changed 23, path equals loaded 282 |
| `uv run ruff check src tests/test_rule_verbalization.py` | one finding, I001 in `src/gnd/examples/expense/project/cli/expense_cli.py`: the known red carried by the induced-knowledge close ("IK1 known red"), a file this phase did not touch |

An earlier gate run printed exit 0 through a `tail` pipe while pytest
reported 2 failures (F7). The exit above is pytest's own.

## Coverage against the branch table

Every row of the spec's fallback table has a falsifiable case:

| Row | Case |
|---|---|
| `prose-rule` | T4 |
| each refused mutation | T4b, against its own control, which loads |
| each mutation in memory | T4c (`VerbalizationError` and exit 3) |
| each collector branch, called directly | review-F2, which kills mutant H |
| the dead `binds` branch | no case, by design: `atom_bind` is total |
| root aggregate with clauses | T13 |
| the three line continuations | T3 and T3d |
| `line_text` escaping | T3c, through a variable |
| argument order | T5 |
| linearity | T11 counts renders and index builds; review-F5 counts walks |

## Adversarial review

One reviewer is one reviewer:
[phase-MG1-claude-review.md](notes/phase-MG1-claude-review.md), a local agent
reading the diff with the repository read-only. It ran a differential fuzz,
16 mutants and the parity capture, but not the evolve suites or the docs
runner. Verdict approve-with-fixes; six findings, none blocking. Each finding
was reproduced, and the dispositions are in the spec (F8):

- **Fixed with regressions shown red before the fix:** R-F1 and R-F6.
- **Fixed with new or strengthened cases:** R-F2, R-F3 and R-F5. R-F2's
  case was shown to fail under mutant H.
- **Recorded:** R-F4.

## Refactoring review

**Refactor executed:** the `fact_types` argument check was written twice
during the phase, once in `api.verbalize_rules` and once in
`render_rule_verbalizations`. It now lives in one function,
`model_verbalization.check_fact_type_selection`, called by both. It is
behavior-preserving: the same `TypeError`, still raised before the model is
loaded (T5's order case). It landed behind the final gate above.

**Seen and deferred:**

- `api._run_verbalize` keeps a local `failure` closure that builds the same
  refusal shape as the new module-level `_rule_verbalization_refusal`.
  Merging them would change `_run_verbalize`, which is outside MG1's scope and
  under RF1 handler pins. Open question MG1-Q3 below.

## Refuted premises

- The spec's `date_add` row assumed a valid two-argument control. Validation
  refuses every temporal term in a derivation rule (F1).
- T7 asked for a separate evolve-preview digest table. Evolve renders only
  loaded models, which the loaded-render table already covers (F2).
- T9 assumed no RF6 row change. The syntax census needs a counted successor,
  though the model-query allow-list is unchanged (F6).
- Rule 4 claimed the collector alone prevents partial rendering. Review
  R-F1 refuted it; re-validation now does.

## Open questions

| ID | Question | Target |
|---|---|---|
| MG1-Q3 | Merge `_run_verbalize`'s local `failure` closure with the module-level refusal helper | a later refactoring pass touching `api.py` handlers (RF1 pins) |
| MG1-Q4 | Re-validating every loaded `Model` in `render_rule_verbalizations` roughly doubles direct-call time over the corpus (T2/T3 took 19 s before R-F1, 48 s after) | accepted residual unless a caller reports cost; the public API loads and validates paths once |

## Boundary

- One reviewer is one reviewer. The plan's four-reader bar applies to the
  milestone close, not this phase.
- The broad historical lanes did not run (slow cadence above).
- `render_model_verbalization` still behaves as at `1446f90` on an invalid
  in-memory `Model` (out of scope).
- No merge, release, publication or certification is claimed.
