---
milestone: rule-check-adoption
station: phase-RC5
skill: "n/a -- repository development via process-phase auto=false, not a gnd-solve station over a domain model"
scope: phase-RC5
date: 2026-11-06
gate:
  command: "uv run pytest -q tests/test_rc5_tool_output.py tests/test_schema_sync.py tests/test_extract_projection.py tests/test_population_load.py --tb=short -p no:cacheprovider"
  exit: 0
  output: "82 passed"
  note: >-
    The plan section 9 RC5 row (V2), at e3e15ca5. The impact closure (V4),
    lint (V5), the component index check (V6) and the sharded full default
    suite against main 14f66ad3 (V1/V3) are in the body.
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "explicit owner selection at milestone close (plan section 9)"
  reason: "RC5 changes no historical artifact; the full default suite covers every dump and digest consumer"
evidence:
  - path: src/gnd/schema/population.schema.json
    sha256: 2f0e2a46109824a5850c458b628e20270c69b9c92d18bef0e2dd83585d4ce0d0
  - path: src/gnd/skills/gnd-orm-core/references/population.schema.json
    sha256: 2f0e2a46109824a5850c458b628e20270c69b9c92d18bef0e2dd83585d4ce0d0
  - path: src/gnd/skills/gnd-orm-core/references/population-format.md
    sha256: 3d94c0e7d56bc15bf4fe757e34d0b888f9d25a695df54abc60657c1a8b480230
  - path: src/gnd/population.py
    sha256: bcad4c41c1b973f7a94681cfe9ddd3f3074fef7cee2263a8d349ed52bf73a314
  - path: src/gnd/population_shape.py
    sha256: 76947860968961973a03e2e942d9b64c2bf8786d2321d1d9c7418d831286cecf
  - path: src/gnd/model/__init__.py
    sha256: c37ac30bcda63cbd753f4d0acf56da2effb159218c2d3e3d18d0a059c2e00b6e
  - path: src/gnd/composition.py
    sha256: 345a845ca494a4ec1a776d1226780159dd6b6cc702ff9596f7cc1bd6d6394a20
  - path: src/gnd/witness/io.py
    sha256: fcd1b4621a4f73154737adbb0ab438640c80f413c42367b6da6aa9665d6cd95c
  - path: docs/reference/composition.md
    sha256: cff58c5c7378829ff21bcee9e3d3a8905896b78349a38d4b024b54c073dbf71c
  - path: tests/test_rc5_tool_output.py
    sha256: bf36dc54a7479240f45cce161700294505e33015b464b0d5a8213ec04714eebc
  - path: tests/fixtures/rc5-tool-output/README.md
    sha256: e5be20d402e335717b6c243193b7fa072ccec564e178fd88ce55e09c2cd3c706
  - path: tests/fixtures/rc5-tool-output/expected/answers.json
    sha256: fc3c0ed8bb2525310c4af82ebcbd1edb80be37b254a554adb7b2c972a205cd28
  - path: .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/source-successors.json
    sha256: dea753b3e6d07db56173363af07b2abc8c9b6f2165ba0cf9cf122eba5daa3789
  - path: .gnd-planning/milestones/rule-check-adoption/evidence/RC5/dynamic-query-successor.json
    sha256: 8159231d9b95e413ce83d967a38e3420327c572e0d1c164185f4d85c86ed972b
  - path: .gnd-planning/milestones/rule-check-adoption/evidence/RC5/full-suite-main-14f66ad3.txt
    sha256: 6209543f0e44016a02a0f5b8081ef4317c955ea89d10a8e0dfc53ea26c6bbad2
  - path: .gnd-planning/milestones/rule-check-adoption/evidence/RC5/full-suite-rc5-e3e15ca5.txt
    sha256: eb01853a1b98ef520c535ebf98dcffcd597108ab3ec06a1026b32109ac8ee9f7
  - path: .gnd-planning/milestones/rule-check-adoption/notes/phase-RC5-spec.md
    sha256: 0505947fd102055cc560d9c69f75a8f8d993305bfb2b3bb28255dfda3105919f
  - path: .gnd-planning/milestones/rule-check-adoption/notes/phase-RC5-codex-review.md
    sha256: 66add7fa48208b203e32b3b0abc4fd89fcc73f6d31e1efe6f536ebedeb5c4593
---

# Claim

At e3e15ca5, a population may declare `source: tool-output` with an
optional `producer` (1-200 characters, only with that source); it loads,
checks, composes and travels on the witness wire exactly like any other
population, and a population without a producer serializes and digests
exactly as before RC5, as the owner-approved corpus specifies. V2 exited 0
(82 passed), V4 exited 0 (11481 passed over 298 files), and the sharded full
default suite's failure list is byte-identical to main 14f66ad3's.

## What shipped

- **M1** `population.schema.json` and its sync-pinned skill copy: `tool-output`
  in the source enum; `producer` (string, 1-200); `dependentSchemas` so a
  producer requires `source: tool-output`; descriptions updated.
- **M2** `Population.source` gains `tool-output` (pinned to the schema, T2);
  `Population.producer`, excluded from every dump when unset; a model
  validator for direct construction; both constructors, the reference
  binder, composition and the witness wire carry a present producer.
- **M3** the loader's positive-only fast path (`population._prepared_population_schema`,
  `population_shape`) compiles `maxLength` and `dependentSchemas`; T6 pins it
  to Draft on every producer case.
- **M4** `population-format.md` (opening paragraph, enum, `source` and
  `producer` entries) and `docs/reference/composition.md` (the composed header).
- The extraction projection keeps its three values, pinned as a subset
  (D2).
- Guards: RF6b `bind_population`; RC5 dynamic query delta.

## Gate output (verbatim)

V1, focused, at the base 14f66ad3 before any source edit:

    uv run pytest -q tests/test_schema_sync.py tests/test_extract_projection.py tests/test_population_load.py --tb=short -p no:cacheprovider
    56 passed in 0.94s
    V1 exit=0

V2, focused gate (plan §9 row), at e3e15ca5:

    uv run pytest -q tests/test_rc5_tool_output.py tests/test_schema_sync.py tests/test_extract_projection.py tests/test_population_load.py --tb=short -p no:cacheprovider
    82 passed in 1.26s

V4, impact closure, at the review-fix tree (committed as e3e15ca5): every test
file naming the population schema, `Population(`, the population reference,
the content digest, `bind_population`, composition, the witness wire,
`model_dump` or assurance, the M3 fast-path tests, the documentation
tutorials and the guard suites (298 files):

    uv run pytest -q <the 298 files> --tb=line -p no:cacheprovider
    11481 passed, 472 deselected, 1 warning in 1521.02s (0:25:21)
    V4 exit=0

V5, lint: `uv run ruff check <the Python files changed since 14f66ad3>` →
`All checks passed!`.

V6, component index: `python3 scripts/components_index.py changed --base
14f66ad3 --strict` → `0 to fix, 0 warning(s), 9 to reread`. Edited with the
code: search verbs on `model.population_loading` and `model.population_shape`;
the reread entries (the subsystems that list `model.loading`, `model.loading`
itself, `model.scalar_identity`) still describe their code.

V1 (main 14f66ad3) and V3 (e3e15ca5), full default lane, sharded on
beast-3 as in the earlier records:

    V1 main 14f66ad3: 17718 passed, 2 errors; shards exit 0,0,0,1,0,0
    V3 rc5 e3e15ca5:  17744 passed, 2 errors; shards exit 0,0,0,1,0,0
    comm -13: empty; comm -23: empty
    sha256 of each sorted failing-id list: 8261732b…9c20a (both)

The 2 errors are the `tests/test_public_optional.py` uv-version pins. The
26 extra passes are RC5's tests. A first full run at a59693d3 failed 32
tests main passes (witness corpus, session pins, certificate replay,
timing instruments), all from `producer: None` in `model_dump()` (review
T1, spec I5); the fix landed in e3e15ca5 and those tests pass. Evidence:
`evidence/RC5/full-suite-*.txt`.

## Criteria

| Criterion | Evidence | Result |
|---|---|---|
| RC5-C1 | corpus (six cases); T1, T3, T4; review T2, T3 | loads, retained everywhere, refused at exit 3 with `const`, `minLength`, `maxLength`; refused on direct construction |
| RC5-C2 | T2 | `Literal` equals the schema enum; the projection is a pinned subset (D2) |
| no report change | corpus control comparison; V3 | accepted cases check byte for byte like the `fixture` control; no new full-suite failure |

## Review

One reviewer is one reviewer: Codex (gpt-6-sol, xhigh, read-only), over
`git diff 14f66ad3 a59693d3 -- src tests tools`, disposition `revise`, 6
findings: T1 blocking (fixed, and confirmed independently by the first full
run), T2, T3, T6 fixed, T4 no defect (claim narrowed), T5 deferred.
Retained verbatim with the triage in
[phase-RC5-codex-review.md](notes/phase-RC5-codex-review.md). The fixes were
not re-reviewed.

## Refactoring review

Refactors EXECUTED: none beyond the field-level dump exclusion, which
replaced a one-site digest special case (values.py back to base bytes) with
one rule every dump consumer inherits.

Seen, deferred: `_combine_validated_populations` drops `label` (pre-existing,
spec F2).

## Boundary: what this phase does NOT establish

- One reviewer read the diff; the fixes were not re-reviewed.
- The loader's fast path accepts only what Draft accepts, not everything
  Draft accepts (T4); refused documents fall back to Draft.
- `Population.model_copy(update=...)` can bypass the producer invariant (T5).
- The source and producer appear in no check report; documentation beyond
  the two references is RC6's.
- The broad lanes did not run (`slow_cadence`).

## Open questions

- **Size (plan rule 8).** Measured at e3e15ca5: Python source +48 lines
  (population 19, population_shape 25, composition 2, model 1, witness 1)
  against the 30-line estimate (pause past 45); tests +188 against 80 (pause
  past 120); plus schema, reference and doc lines. The overrun is the
  loader fast path (finding I1) and the review regressions. **Resolved
  2026-11-06, owner ruling: "Accept overrun".** The plan is not amended.
- **T5**: validate the producer invariant on copies, if a caller ever
  updates `source` or `producer` through `model_copy`. Target: its own issue.
- **`label` dropped by the reference binder** (F2). Target: its own issue.
- Carried: unused cycle helpers, index drift, the session-driver flake.
  Target: milestone close.

## Refuted premises

- RC5-C2 read literally ("a test fails if `extract/projection.py`
  disagrees") would have moved recorded projection digests; the projection
  is an agent-facing subset (spec F1, D2).
