---
milestone: pyrel-rules-coverage
station: "phase-RP5"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-RP5
date: 2026-11-22
gates:
  - command: "uv run pytest -q tests/test_rp5_literature_rules.py tests/test_rp4_role_value.py tests/test_rp3_number.py tests/test_rp1_external_uniqueness.py tests/test_rp2_anchored.py tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py tests/test_pyrel_rules_derivations.py tests/test_rules_in_pyrel.py tests/test_pyrel_export.py tests/test_pyrel_export_boundaries.py tests/test_ossie_formulas.py tests/test_ossie_export.py --tb=short"
    exit: 0
    output: "304 passed, 309 deselected in 33.40s"
    note: "run after round 1's repairs; rounds 2 and 3 changed only docs/runtimes/pyrel.md, after which tests/test_rp5_literature_rules.py tests/test_rp2_anchored.py tests/test_disclosure_docs.py gave 47 passed, 74 deselected"
  - command: "uv run pytest -q -m pyrel_oracle tests/test_rp5_literature_rules.py tests/test_rp4_role_value.py tests/test_rp3_number.py tests/test_rp1_external_uniqueness.py tests/test_rp2_anchored.py tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py tests/test_pyrel_rules_derivations.py tests/test_pyrel_rules_plans.py --tb=short"
    exit: 0
    output: "338 passed, 151 deselected in 418.64s (0:06:58)"
    note: "opted in by the owner for this milestone (plan §8); RP5 changed no product code after this run"
  - command: "the project.md structure and inventory guard block (12 files)"
    exit: 0
    output: "679 passed, 2 deselected in 100.99s (0:01:40)"
  - command: "uv run ruff check src tests tools"
    exit: 0
    output: "All checks passed!"
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "the unchanged broad controls are outside this phase's impact closure"
evidence:
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/phase-RP5-spec.md
    sha256: 8b76982f771ea12643cac8b82c6bb3042392e9dd6efb63c9964a7b49af907a1a
  - path: docs/runtimes/pyrel.md
    sha256: b7d2d59d73ba12a2012509a8b359b75eef138e265c2982d0a06ab6f58a33b8b1
  - path: tests/test_rp5_literature_rules.py
    sha256: fe35106e4b4f63eb619f99d6bd1be52a1e854bda070aee44950539b33b9bb9aa
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r1/BRIEF.md
    sha256: f533847d5d242c4868027fd0cffae1f8afa2099591c08a3eea044d946841fc09
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r1/review.md
    sha256: 3c42fd50e34605961cf0e694752aa2dec130f99d16cbbf8d92f5c27b5fe37a32
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r1/FINDINGS.md
    sha256: 64b7019ca1ede73216cfa0890491cae982ead11e71b36d92eb621d9d819c715c
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r2/BRIEF.md
    sha256: 29d402d025351b0322f7abc42293f73ae08fb42a9a52d63e99fb0cf4024f8931
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r2/review.md
    sha256: 9f7d64949162b56591dc832310358de74701c261ae55fa5b65b57e96066811c8
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r2/FINDINGS.md
    sha256: 19204364da4850a6b2288adc339d24c4a18be8f6f69243ee790b3bbc882888fe
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r3/BRIEF.md
    sha256: 107429a2249c63eda3c5936ca648af6b8ebac2f4b363b517d6992505985fbb40
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r3/review.md
    sha256: fdf66dbd2074151373e8215c917de7afad6aea852b27fd808cf34c3379719e99
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r3/FINDINGS.md
    sha256: eae7503c5c7299e0fe716d6318ae24db0f4f0eb8c59634ef9aecc5ab8bb51c9e
---

# Claim

RP5's criteria C1–C3 hold at these bytes.
- **C1:** the eleven packaged literature models of plan §1, plus
  `depth_fixture/decimal`, export under both targets.
- **C2:** on all 56 populations of plan §1's table, the DuckDB program's
  exit and findings equal `gnd check`'s:
  - twelve flat gold populations, exit 4;
  - `assertions/raw`, exit 0;
  - the 41 resolution cases, exit 4 each, as measured by the test;
  - `quantity_fixture/time`, exit 4;
  - `depth_fixture/decimal`, exit 0.
- **C3:** `docs/runtimes/pyrel.md` states what the programs check, list as
  not checked and refuse, target by target. A test pins every message the
  milestone added.

## What shipped

- `tests/test_rp5_literature_rules.py`: T1 exports 12 models × 2 targets;
  T2 checks agreement on 56 populations; T3 checks that the page states
  each message. A further test pins the RP3 head refusal the page names.
- `docs/runtimes/pyrel.md`: a section listing the not-checked reasons and
  the refusal messages verbatim. Review rounds also corrected older
  statements on that page:
  - DuckDB-only reporting is now attributed to the DuckDB version;
  - plans are checked by the DuckDB version only;
  - the exclusive-or refusal covers multi-role sequences only;
  - the disconnected-body refusal covers guarded antecedents only;
  - exit 4 applies when checking a population and no rule is violated.
- No product code changed in this phase.

## Gate output (verbatim)

    304 passed, 309 deselected in 33.40s
    338 passed, 151 deselected in 418.64s (0:06:58)
    679 passed, 2 deselected in 100.99s (0:01:40)
    All checks passed!

## Review

One reviewer is one reviewer: Codex, read-only, through the review helper.

- r1: five page findings, fixed.
  - F1: a missing RP3 message;
  - F2: an incomplete reason list;
  - F3: DuckDB-only behaviour stated for both targets;
  - F4: the plan command not limited to DuckDB;
  - F5: the exclusive-or refusal stated too broadly.
- r2: two findings, fixed:
  - disconnected derivations are accepted;
  - `--compile` does not exit 4.
- r3: one finding, fixed (exit 4 yields to a violation). It concerned this
  phase's own round-2 sentence, a self-inflicted ratio of 1/1, so rounds
  stop. That final sentence has not been reread by an independent reviewer.

Codex could not run the oracle lane (sandbox); C2 rests on the oracle run
above. `review.log` files are not retained.

## Refactoring review

Nothing to restructure: the phase added tests and documentation. The page's
message list is the one home for the messages; the phase tests assert each
against real output.

## Process note

The test file was drafted before the spec's gate was written. The gate was
ruled and committed (`30643055`) before this phase commit.

## Boundary — what this phase does NOT establish

- No RelationalAI engine ran; the LQP program's enforcement is unverified.
- `reading_fixture/reading.orm.json` stays out of scope (plan §1).
- Agreement is with `gnd check` without an anchor sidecar.

## Open questions

None new.
