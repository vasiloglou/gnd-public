---
milestone: ossie-relational-bundle
station: "milestone close"
skill: process-milestone
scope: milestone-close
date: 2026-11-25
gates:
  - command: "uv run pytest -q tests/test_ossie_export.py tests/test_ossie_import.py tests/test_rmap.py tests/test_ossie_relational.py tests/test_physical_binding.py tests/test_ossie_docs.py tests/test_ossie_formulas.py tests/test_rf1_cli_pins.py tests/test_documentation_tutorials.py::test_documented_learning_path[ossie] tests/test_release_docs.py tests/test_skill_prose_sync.py --tb=line"
    exit: 0
    output: "979 passed in 209.29s (0:03:29)"
    note: "on the close branch after the close-review repairs; on main at f5462783 before them the five phases' files gave 954 passed"
  - command: "the project.md structure and inventory guard block (16 files)"
    exit: 1
    output: "1 failed, 865 passed, 2 deselected in 160.64s (0:02:40)"
    note: "the one failure, tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap, is the known red; the milestone touched neither the test nor the files it reads"
  - command: "uv run ruff check"
    exit: 0
    output: "All checks passed!"
  - command: "uv run --group docs zensical build --strict"
    exit: 0
  - command: "uv run python tools/check_docs.py site"
    exit: 0
    output: "19530 local links/assets/anchors checked"
  - command: "python3 scripts/components_index.py changed --base origin/main --strict"
    exit: 0
    output: "changed against origin/main (f546278): 53 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
  - command: "uv run python tools/run_gnd_review_panel.py --light .gnd-planning/milestones/ossie-relational-bundle/evidence/close-review/review-request.json --out .gnd-planning/milestones/ossie-relational-bundle/evidence/close-review/panel-run --effort high --reviewer-timeout 600 --overall-timeout 900"
    exit: 0
    output: "quorum-established: 5 of 6 seats (kimi nonzero)"
  - command: "uv run gnd review finalize .gnd-planning/milestones/ossie-relational-bundle/evidence/close-review/panel-run .gnd-planning/milestones/ossie-relational-bundle/evidence/close-review/synthesis.json --out .gnd-planning/milestones/ossie-relational-bundle/evidence/close-review/PANEL-REVIEW.md"
    exit: 0
  - command: "ruling: owner selected the light panel at effort high and accepted OB5-Q1 as a stated limit (go with your recs, 2026-11-25)"
    exit: "n/a -- ruling"
  - command: "ruling: owner requested the oracle lane on the final code (yes, 2026-11-25); GND_OSSIE_ORACLE_ROOT=<scratch> uv run pytest -q -m ossie_oracle tests/test_ossie_external_oracle.py -k 'not consumer'"
    exit: 0
    output: "91 passed, 1 deselected in 64.80s (0:01:04)"
  - command: "ruling: the owner's close ruling"
    exit: "n/a -- ruling"
    note: "NOT YET GIVEN. This record is complete except for it."
slow_cadence:
  command: "GND_OSSIE_ORACLE_ROOT=<scratch> uv run pytest -q -m ossie_oracle tests/test_ossie_external_oracle.py -k 'not consumer'"
  trigger: "explicit owner request"
  reason: "run on request at 7a6ccfe9 (90 passed) and again on the final code at 98344052 (91 passed, 1 deselected in 64.80s). The consumer test needs the RelationalAI environments and was not run."
evidence:
  - path: .gnd-planning/milestones/ossie-relational-bundle/notes/ossie-relational-bundle-plan.md
    sha256: a751d3e6a60a40ae3162b0633b6c65a55f964b9d64d763ad1d2495f3efd6220f
    note: "r3 with (c2) rows; the panel read 28c52ece...b924"
  - path: .gnd-planning/milestones/ossie-relational-bundle/notes/close-results.md
    sha256: d79da714b27d2720912a3a3fe8cbccf38de82c9c63c86831ef15eb817533aa4c
    note: "the panel read a1bde138...0aea"
  - path: .gnd-planning/milestones/ossie-relational-bundle/notes/close-delta.md
    sha256: 0945a5793de802d3e10074238e7981262c9ca4a86f4f226e10289468b4d24fa4
    note: "the panel read 22fd0fdb...9c09"
  - path: .gnd-planning/milestones/ossie-relational-bundle/evidence/close-review/review-request.json
    sha256: be5bc7fd11afa9a9d0f2a3788de6128a762425a405eb731068a4f9144cb49e51
  - path: .gnd-planning/milestones/ossie-relational-bundle/evidence/close-review/panel-run/run.json
    sha256: 11fdf71260e1313d53f6c40c43c594ce5a853db2574a7db9ed8b6573019afc93
  - path: .gnd-planning/milestones/ossie-relational-bundle/evidence/close-review/synthesis.json
    sha256: 79cd6ca05dc24bbb7d2164dd7b497145912c0f2a183db54a91e853449ab6dd03
  - path: .gnd-planning/milestones/ossie-relational-bundle/evidence/close-review/PANEL-REVIEW.md
    sha256: 09731adf64096afb28cf547e821f6e37995491c87fddaab167001468988e2934
  - path: .gnd-planning/milestones/ossie-relational-bundle/evidence/close-review/disposition.md
    sha256: abdd4a350c76fd08cde436e0ed277a7b6fda89fa80e83433c049fce02152b5cf
  - path: .gnd-planning/milestones/ossie-relational-bundle/004-phase-OB1.md
    sha256: 82b327a4ac52cf427e2a6fdb47fbd68f31c256a8a21a60e8fa936138095e02bf
  - path: .gnd-planning/milestones/ossie-relational-bundle/008-phase-OB2.md
    sha256: bce1c108c359b56db6749fe91d88a66deb914b41a9afa8723b2c75d25ecb76c0
  - path: .gnd-planning/milestones/ossie-relational-bundle/011-phase-OB3.md
    sha256: 61c9ebed389d7b476ee9cfb58f02a2e8dd303300f158c55ac1519d1c1303c44a
  - path: .gnd-planning/milestones/ossie-relational-bundle/015-phase-OB4.md
    sha256: 25ebff9e9bac3ca27b9d876b9e5b8ef69f1cd9ccf107f0756976dfab63e1166e
  - path: .gnd-planning/milestones/ossie-relational-bundle/020-phase-OB5.md
    sha256: e3eeed1b235e0a440a77221df90a9127c12b8370c20e04619ddd5701c508717d
  - path: src/gnd/export/physical_binding.py
    sha256: 4740b27defa78d26bd07b2a4b85afd3391884f9c1dbe3bce4657c968494fef0e
  - path: src/gnd/export/ossie_relational.py
    sha256: f2b1c9966edca1c504f1f55c9bb090bac65788ce1d685015b82693ff2b8f305b
  - path: src/gnd/skills/gnd-orm-core/references/representation-format.md
    sha256: 594ec58970647df4abeca920579f2088b671fdd65f0ee473354c1ebd204ca92a
---

# Milestone close: ossie-relational-bundle

## Close ruling

**Not yet given.** The owner selected the close review instrument and
accepted OB5-Q1 ("go with your recs", 2026-11-25). The owner has not yet
ruled the close itself. Everything below is what that ruling would be over.

## Phases

Five of five, each with its own gates and record, all merged to main:

| Phase | Record | Pull request |
|---|---|---|
| OB1 size bounds | [004](004-phase-OB1.md) | 266 |
| OB2 Halpin Rmap | [008](008-phase-OB2.md) | 270 |
| OB3 relational files | [011](011-phase-OB3.md) | 271 |
| OB4 physical binding | [015](015-phase-OB4.md) | 272 |
| OB5 docs and skill | [020](020-phase-OB5.md) | 273 |

## Completion predicates

The six predicates of the plan, as amended by its §11, each with the
evidence that would fail if it were false, are in
[close-results.md](notes/close-results.md). All six hold on the tested
bytes, with these limits:

- Predicate 1 holds for model files within the 10 MiB cap.
- Predicate 2 as first written was false in one clause: a default run has a
  second new failure, the size bound on the two new files (A17).
- Predicate 4's upstream validation is evidenced on the final code, at
  `98344052`, for everything but the consumer test.

**External acceptance is missing.** The reporter's own checks need their
model. They have not been asked. No reporter run is cited.

## Close review

The light panel at effort high, selected by the owner
([report](evidence/close-review/PANEL-REVIEW.md),
[dispositions](evidence/close-review/disposition.md)). Six seats were
attempted and five succeeded; the Kimi seat failed on its provider's quota.
All five asked for revision. Effort high was bound per run for Claude and
Codex only.

- **Two blocking concerns, both reproduced and repaired.** The binding's
  name-collision rule refused two tables that Ossie reads as distinct. And
  predicate 2 denied a failure a default run can have.
- **One high concern rejected** after checking: that names are unquoted in
  the semantic model. A declared name is written as given, and the pinned
  validator accepts such files.
- **The rest** were corrections to the plan amendments, the results and the
  delta. All were made.

**The repaired bytes carry no review opinion.** No second panel round ran.

## Plan repair

Plan r3 appends §11, eighteen amendments (A1–A18), each naming the record
that raised it; r2's approved text is kept above it. A17 and A18 came from
the close review.

## Refuted premises

The plan's premises that the phases refuted are §11's rows. The ones with
user-visible effect: a model with no table (A8), the second default failure
(A17), the quoting rule (A14), and the binding rules the plan left open
(A10–A13).

## Open-questions sweep

Every question of records 004–020 and plan §10 is dispositioned in
[close-results.md](notes/close-results.md): closed, carried with an owner,
or an accepted residual. Carried to the owner: three maintenance items
(OB1-Q1, OB2-Q1, OB4-Q4), `refscheme`'s selection (OB2-Q2), identifiers the
ontology does not declare (OB3-Q5), and D10. The D10 texts are drafted in
[D10-drafts.md](notes/D10-drafts.md) and nothing has been sent.

## Residuals

- External acceptance by the reporter: missing.
- A model file above 10 MiB cannot be exported.
- A fact held only through a surrogate key cannot be bound.
- A non-ASCII name can miss a reader on other Unicode tables (accepted by
  the owner as a stated limit).
- Import reads the ontology only.

## Boundary -- what this close does NOT establish

- That the reporter's model exports, binds or matches their schema.
- That the close-review repairs are free of defects. They are unreviewed.
- That the oracle lane's consumer test passes. It was not run.
- Publication. The 0.5.0 release is a separate milestone and is notified
  only after this record merges.
