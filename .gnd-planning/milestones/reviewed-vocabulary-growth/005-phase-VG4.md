---
milestone: reviewed-vocabulary-growth
station: "phase-VG4"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-VG4
date: 2026-11-23
gates:
  - command: "uv run pytest -q tests/test_vg4_seeded_growth_rounds.py tests/test_mc3_evolution.py tests/test_evolve_source_document.py tests/test_evolve_additive_policy.py tests/test_evolve_population_check.py tests/test_unattended_model_growth_acceptance.py tests/test_unattended_mode.py tests/test_unattended_span_coverage.py --tb=short"
    exit: 0
    output: "437 passed in 41.74s"
    note: "the plan's section 9 VG4 lane with the new file, at 18411c92"
  - command: "uv run pytest -q tests/test_vg3_unattended_includes.py tests/test_mc1_model_includes.py tests/test_mc1_guards.py tests/test_include_root_close.py tests/test_vg2_evolve_sources.py --tb=short"
    exit: 0
    output: "246 passed in 19.57s"
    note: "VG3's and VG2's direct tests, since U1 changed in _unattended.py; at 002dc86e, three runs; one earlier run failed one test (spec finding 4)"
  - command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=line"
    exit: 0
    output: "679 passed, 2 deselected in 102.72s (0:01:42)"
  - command: "uv run ruff check src tests tools"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base b50593b2 --strict"
    exit: 0
    output: "changed against b50593b2 (b50593b): 17 file(s) differ; 0 to fix, 0 warning(s), 3 to reread"
    note: "exit 1 first ('stale or missing: dev/components/modules/model.md') after 18411c92; regenerated and committed, then exit 0"
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "explicit owner request, or the milestone-close default lane"
  reason: "U1 changes only for a root with includes and nothing of its own; the re-pin refusal only for an unattended root; both lanes that read them ran"
evidence:
  - path: src/gnd/model/_unattended.py
    sha256: 15b76d85cabd8ae9a82365461e1e606669726e371ca689eb2dfc0de9bdd05d91
  - path: src/gnd/evolve/service.py
    sha256: 3e1c4e9923ab8f48deae954098a4d2b0de9058703f5aece2c99ed00313a09531
  - path: src/gnd/evolve/_includes.py
    sha256: b0f939fa57c9927a647ade7aa75c914e700b9cee0da45fb32533c430eb5efb5d
  - path: src/gnd/skills/gnd-orm-core/references/representation-format.md
    sha256: 939e9ef2d429bdde040001bbd301ee8abbb36badf6a89d15fe77531d8f72e02c
  - path: src/gnd/skills/gnd-model-evolve/references/evolution-contract.md
    sha256: f67c07c4084f8874d01030dff7964e78c7918e7f0f2995386af72585b29722be
  - path: tests/test_vg4_seeded_growth_rounds.py
    sha256: d5f1bf7bfddc7ad3dc861fa587e561fb3006077abf0a47cf9c0127aad3aee738
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/notes/phase-VG4-spec.md
    sha256: a54cdea8aace7b060159bcf33b20a48791e61dccf3da284b154bd6adc1e9f847
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviews/phase-VG4-r1/review.md
    sha256: c0d19198b87fdc71e65118072ec7d73860779d25f268188f563cb1bd1761ba93
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviews/phase-VG4-r1/FINDINGS.md
    sha256: b818ed63f51df43c0f2ffd242f4043b1ff15e06fd1b20e71596cc9fcc59d8bda
---

# Claim

At `18411c92`, the VG4 lane exited 0 (437 passed), the guard block exited 0
(679 passed), `uv run ruff check src tests tools` exited 0, and the
component-index check exited 0 after the module page was regenerated. Issue
222's root with no `documents` key validates; its first `gnd evolve` round
declares the document, adds owned elements and attaches a constraint to an
included fact type; preview, apply and finalize exit 0 and the result
validates with its document.

## What shipped

- `src/gnd/model/_unattended.py`: `_owns_nothing(doc, included)`, read with
  VG3's origin set: the composed root declares includes and nothing of its
  own in any section. While it holds, U1 does not require `documents` when
  the key is absent or the list empty (D4 (a); a present `null` keeps U1,
  review r1, F1). `reviewer: none` is still required.
- `src/gnd/evolve/service.py`, `_source_document_target`: on an unattended
  model whose `source` has no `documents` key, the add creates the list
  (VG4-D1; limited to the mode, spec finding 1).
- `src/gnd/evolve/_includes.py`, `enforce_ownership`: `repin-include` on an
  unattended root is refused, `evolve:unattended-repin: <reference>`, under
  every policy, before the policy runs (D6, VG4-D2).
- Pages: the U1 row and the first-document paragraph in "Unattended
  source"; the re-pin sentence in "Shared vocabulary evolution"; one
  release-notes entry.
- `tests/test_vg4_seeded_growth_rounds.py`: T1–T6 and the review regression.
- `dev/components/`: regenerated; `evolve.service`, `model.validation` and
  `subsystem.evolve` re-read and still accurate.

Measured size: 383 lines added and 5 removed under `src` and `tests`
(`git diff --stat b50593b2 18411c92`); source about 50 of them, against an
estimate of 40.

## Gate output (verbatim)

    $ uv run pytest -q tests/test_vg4_seeded_growth_rounds.py tests/test_mc3_evolution.py tests/test_evolve_source_document.py tests/test_evolve_additive_policy.py tests/test_evolve_population_check.py tests/test_unattended_model_growth_acceptance.py tests/test_unattended_mode.py tests/test_unattended_span_coverage.py --tb=short
    437 passed in 41.74s
    $ uv run pytest -q <the VG3 and VG2 direct tests> --tb=short
    246 passed in 19.57s
    $ uv run pytest -q <the project.md guard block> --tb=line
    679 passed, 2 deselected in 102.72s (0:01:42)
    $ uv run ruff check src tests tools
    All checks passed!
    $ python3 scripts/components_index.py changed --base b50593b2 --strict
    changed against b50593b2 (b50593b): 17 file(s) differ; 0 to fix, 0 warning(s), 3 to reread

## The criteria

| Criterion | Test | Result |
|---|---|---|
| VG4-C1 | T1: on the documented #222 root, a round adds a value type, a fact type with spans and a sample row, and an attached constraint; `--policy additive` | no policy issue; apply and finalize; validate with the document exit 0 |
| VG4-C2 | T2: modify and rename an included object type, delete an included fact type and an included constraint | each refused `evolve:included-element` |
| VG4-C3 | T3: the undocumented root validates; its first round declares the document and adds elements; U1 kept for an owned object type, fact type, attached and top-level constraint, deontic note (CLI); an operation, an operation with an obligation, a rejected proposal, a reference population (rule); `reviewer` absent or not `none`; `documents` not a list or `null`; an unattended model without includes | as stated |
| VG4-C4 | T4: `repin-include` with no policy and with `additive`; control without the mode | `evolve:unattended-repin` both times; control not |
| VG4-C5 | T5: `--populated` names the included host of an attached constraint; `--check-population` over the root | the same cell as any model; the check reads the composed root (narrower than the row, spec finding 3) |

## Review

One reviewer is one reviewer: Codex (default model, effort high, read-only)
through the review helper, round `notes/reviews/phase-VG4-r1/`, over the
diff from `b50593b2` to the working tree at `002dc86e`. Verdict
`CHANGES_REQUESTED`, one finding, reproduced and fixed at `18411c92` with a
regression test that failed first:

- F1, hardening: `documents: null` passed the first-document rule but the
  first round could not extend it.

The reviewer checked and found true: first-document previews from an
absent key and from `[]`, with owned elements and an attachment; U1 kept
for owned elements, attachments and the other sections; re-pins refused
before the policy under both settings, controls unchanged; eleven ownership
probes over included objects, facts, roles and constraints; 21 existing
unattended-rule branches. It could not run apply, finalize or any lane
that writes files. It noted the spec had gained implementation notes after
the brief. `review.md` and `review.log` were sanitized by the helper.

## Refactoring review

None needed, argued from what the phase touched: one predicate beside U1
that reuses VG3's origin set, one branch in the source-document target and
one refusal in the existing ownership walk.

## Boundary -- what this phase does NOT establish

- One reviewer is one reviewer. The fix commit `18411c92` carries no review
  opinion; the round read `002dc86e`.
- T5 does not compare `--check-population` on the root against a flattened
  copy of it (spec finding 3).
- Include-bearing linked-project evolution stays refused.
- The first-document add creates a `documents` list only on an unattended
  model.
- The MC1 T22 timing test flaked once in these lanes (spec finding 4); it is
  outside VG4's code.

## Open questions

- None new. VG5 runs the whole path on a packaged example.
