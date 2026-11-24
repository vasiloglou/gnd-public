---
milestone: literature-reading-reference
station: phase-LR1
skill: "n/a -- repository development via process-phase auto=true, not a gnd-solve station over a domain model"
scope: phase-LR1
date: 2026-11-23
gates:
  - command: "uv run pytest -q tests/test_lr1_verify_failure_listing.py tests/test_verify_cli.py tests/test_ld3_reading_workflow.py tests/test_documentation_tutorials.py tests/test_public_extraction_prose_policy.py tests/test_extract_guidelines.py --tb=short"
    exit: 0
    output: "183 passed in 200.90s (0:03:20)"
  - command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
    output: "679 passed, 2 deselected in 108.60s (0:01:48)"
  - command: "uv run ruff check"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base origin/main --strict"
    exit: 0
    output: "changed against origin/main (11a7ebf): 106 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "LR1 changes pages, one runner group and tests; no package code changes, so the broad lanes are outside its impact closure"
evidence:
  - path: .gnd-planning/milestones/literature-reading-reference/notes/phase-LR1-spec.md
    sha256: 0b1bdd6166acf0fd064d0cdea1d2510dc999722c375cbdcd0864f0fb4f732285
  - path: .gnd-planning/milestones/literature-reading-reference/evidence/LR1/final-gate.txt
    sha256: c017f680963083f3e61c15fcfeff6098397a68865e5df422dfebb7fcfccf9bbb
  - path: .gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR1-r1/review.md
    sha256: 91ef1396f7b6429f93f41d2c48b499ce8d9fe26af1887e6769820dad680e16fe
  - path: .gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR1-r1/FINDINGS.md
    sha256: df8e3a0b3004fb87f0ba4b04326256ab5ed7ba23b76652a8c61fad62b9e3a0a7
  - path: .gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR1-r2/review.md
    sha256: 4b13e9cb8edf91f45329099c3c1f426bc7d59e6cb667f0d281e0f2380b5162fb
  - path: .gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR1-r2/FINDINGS.md
    sha256: 373105c209645aef29592ad3fe3cb1e7549b8221640b249c42254edb46e9a3c9
  - path: docs/guides/documents.md
    sha256: f810f3a70f886c46beba0474f68cb42383c15d4ab61ddea7c4e2c3126103d0a3
  - path: tests/test_lr1_verify_failure_listing.py
    sha256: 39f08e5a82f3a5951c30f0edfe4af0ff620bded065dfdc4b7100eee985137156
  - path: src/gnd/skills/gnd-extract/references/extraction-contract.md
    sha256: 3af890ab079323e6f6d4a3d11a8a99bcfa253051196e6fa578313f5a1da4ea08
  - path: docs/literature/commands.md
    sha256: 1b2a12be2af4759d8aecbf8314ccc87e516f51a3cc1ea4c03c20cefef4f0e334
  - path: tools/run_tutorials.py
    sha256: 06ae7f3a7919b30faf6e67f4a02344aa3aed1e8bb7dfd68edf97d0f20ea1b156
  - path: tests/test_documentation_tutorials.py
    sha256: 9dfa5685b9e0e9471b14d9e9cfc8569e2306980db62c9ce04486c5943334257a
---

# Phase LR1: why a source fails verification

Phase base `9a10bda1` (the plan gate). Implementation commits `910b8c2b`
and `60306a5c`.

## Spec gate

Delegated approval (`auto=true`), 2026-11-23, under the milestone
delegation recorded in [001-plan-gate.md](001-plan-gate.md). Gated bytes:
`notes/phase-LR1-spec.md` r2 with §12, SHA-256
`bb14f137aadd734da3bc55e4dc42185ec6f6d83e563626506224f48aba8df706`.
§13 (implementation findings) was appended after the gate; the evidence
digest above is the file with §13. Instrument: the spec prose. No paid
call. Compatibility: `gnd verify` unchanged. The §7 rulings (D7 (a), D8 (a),
the runnable block, the printed fields) are the gate's. This is a delegated
ruling, not the owner's reading of the spec.

## What shipped

- `docs/guides/documents.md`, "Reading a failed verification": the steps
  that list the failing constraints (alethic `fail` verdicts) and failing
  derivations, what `constraint_ref` addresses and how to map it back
  through `gnd flatten`'s `gnd-flattening/1` origins, what a witness is,
  deontic warnings, redaction and the disclosure mode (cited, not restated),
  and a runnable example whose `failed` function the test executes.
- One citing cell in the packaged `gnd-extract` extraction contract
  (absolute URL) and one citing paragraph in `docs/literature/commands.md`.
- `tools/run_tutorials.py`: a `failed-verification` group;
  `tests/test_documentation_tutorials.py` runs it. Outside the plan's LR1
  homes, as the spec said.
- `tests/test_lr1_verify_failure_listing.py`, eleven cases T1–T8, T10, T11
  (T6 four-way): the reported conflict (one uniqueness constraint, two rows,
  mapped to `subject_has_one_label` through the flattening record), the
  broad pass, the field check against the schema and the live report, a
  deontic warning, a redacting vocabulary with its markers and both ways to
  show the rows, the default verify digests, one home, a derivation
  failure, a mandatory bare-instance witness and a ring witness.
- A release-notes entry under the unreleased heading.

## Criteria

| Criterion | Evidence |
|---|---|
| LR1-C1 | T1 |
| LR1-C2 | T2 |
| LR1-C3 | T3: the keys the page's code reads equal the listed set; each listed name is a property of its level in `report.schema.json`, a key of the live report at that level, and named on the page |
| LR1-C4 | T4, T5 |
| LR1-C5 | T6: SHA-256 of default text and JSON for both sources equal the values measured at the base |
| LR1-C6 | T1, T8, T10, T11 |

## Review

Two rounds, one reviewer each: Codex (`codex exec --sandbox read-only`,
effort high) through the review helper, the instrument the owner ruled
("Review helper, both"). **One reviewer is one reviewer.** The reviewer could
not run the pytest lane, which writes files; it ran the verify handlers
in memory.

- Round 1 (`notes/reviews/phase-LR1-r1/`): five findings, all reproduced.
  Two blocking (the guide's witness claim; the runnable output not compared
  and the test reimplementing the filter), three hardening. Four fixed in
  `910b8c2b`; the prose half of codex-3 deferred.
- Round 2 (`notes/reviews/phase-LR1-r2/`), over the repaired bytes: round
  one's codex-2, -4 and -5 repairs hold. Three findings: one blocking
  (`constraint_ref` is a composed address), one hardening (a positional
  witness the guide's list missed), and the deferred half of codex-3. Two
  fixed in `60306a5c`.
- Round 2's repairs carry no review opinion. Under the convergence rules the
  remaining finding classes are documentation-hardening, and the next
  instrument is the tests, not a third round.

Mutation runs, before commit: dropping the page's derivation filter fails
T8; printing no constraints fails the tutorial node; reading a field the
report lacks fails T3.

## Refactoring review

None needed. The phase adds a page section, a test and one runner group. It
showed that `gnd verify`'s report has no field naming a constraint's declared
id; that is plan D7 (c), offered to the owner and not ruled in, not a
refactor. No helper was duplicated: the page block is read by the runner's
existing `parsed_blocks` and `ast`.

## Boundary: what this phase does NOT establish

- The guide's prose is not parsed. A field the prose names and the page's
  code does not read is unchecked (codex-3, deferred): the default
  environment has no Markdown parser, and a new one is outside this phase.
- The guide names three witness shapes as examples, not a closed list. No
  test enumerates every constraint family's witness shape.
- The composed-address mapping is tested on the reading model's included
  fact-type constraint only, not on a top-level constraint from an include.
- Round 2's repairs are unreviewed bytes.
- No change to `gnd verify`; no fidelity rate anywhere (R0.3). A passing
  report still says nothing about faithfulness.

## Open questions

- Prose field check (codex-3): target, a later documentation-tests change
  that brings a Markdown parser into the test environment. Not this
  milestone.
- `project.md` line 25 ("There is no component index in this repository")
  contradicts its own later section; carried from the plan gate.

## Refuted premises

- Spec §6 step 3 / plan §2: "the constraint's own `id` is at that address
  in the file that declares it". Refuted by
  `tests/fixtures/lx1-flattening/expected.json` (a root constraint at
  `fact_type_constraints[0].constraints[0]` is composed at
  `fact_types[0].constraints[1]`). Repair: the guide maps through the
  flattening record. Plan repair at close: §2 LR1's wording.
- Spec r1 LR1-D3 (a): `parsed_blocks` reads a page with no runnable block.
  Refuted before implementation (spec r2 §2).
