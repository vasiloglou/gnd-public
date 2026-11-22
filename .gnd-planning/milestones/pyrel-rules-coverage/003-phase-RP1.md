---
milestone: pyrel-rules-coverage
station: "phase-RP1"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-RP1
date: 2026-11-22
gates:
  - command: "uv run pytest -q tests/test_rp1_external_uniqueness.py tests/test_rp2_anchored.py tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py tests/test_pyrel_rules_derivations.py tests/test_rules_in_pyrel.py tests/test_pyrel_export.py tests/test_pyrel_export_boundaries.py tests/test_ossie_formulas.py tests/test_ossie_export.py --tb=short"
    exit: 0
    output: "240 passed, 224 deselected in 18.18s"
  - command: "uv run pytest -q -m pyrel_oracle tests/test_rp1_external_uniqueness.py tests/test_rp2_anchored.py tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py --tb=short"
    exit: 0
    output: "154 passed, 58 deselected in 153.07s (0:02:33)"
    note: "opted in by the owner for this milestone (plan §8); RP2's count was 128"
  - command: "the project.md structure and inventory guard block (12 files)"
    exit: 0
    output: "679 passed, 2 deselected in 97.49s (0:01:37)"
  - command: "uv run ruff check src tests tools"
    exit: 0
    output: "All checks passed!"
  - command: "uv run ruff check"
    exit: 1
    output: "Found 198 errors."
    note: "known red, the same 198 errors in dev-tools-delivered skill scripts as RP2's record shows at 92cd5c9b"
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "the unchanged broad controls are outside this phase's impact closure"
evidence:
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/phase-RP1-spec.md
    sha256: de95894e6e26c4b78f7d982a0b029f38d0534878d0aea80efd13ad3ed4619818
  - path: src/gnd/export/pyrel_rules.py
    sha256: f61206a0c89e1b7d5a3c3686beeb815e6d84aa6067e162b10a6238b96bd500a7
  - path: docs/runtimes/pyrel.md
    sha256: 38712ee499852a45d9539c82edbbe915f2b8689a10501e670d57e6caa60daefb
  - path: tests/test_rp1_external_uniqueness.py
    sha256: 381048c78f22e3f1223b464f042eba8a3e2cef0fbc46a798c62e93f7e554d5bc
  - path: tests/test_pyrel_rules_families.py
    sha256: 3389b5662e5153c46ef6ee01fa3875e7677dcf98df02770a3d0cfe11d3f01aa1
  - path: tests/support/pyrel_application_successors.py
    sha256: bd6429e6f3fddf231f9dd857c547e1418fbc69c9e0dd993790c25311f5b02006
  - path: .gnd-planning/milestones/pyrel-rules-coverage/evidence/RP1/dynamic-query-successor.json
    sha256: aa180028b0cd2291b8e168aa1a2f82ce1a5a014029a480cb255ca36b0d6a5be6
  - path: tests/fixtures/pyrel-rules-coverage/rp1/ambiguous.orm.json
    sha256: f3f03f1637adf5e8b93bfe45235d038a3917de186b4cd7364b3390353aa01e99
  - path: tests/fixtures/pyrel-rules-coverage/rp1/assertions-duplicate.population.json
    sha256: 8a5d7f5276f673a6ef11a31dcb78b7ec08a5ff1d42295d5b12cc60dae84e6a60
  - path: tests/fixtures/pyrel-rules-coverage/rp1/assertions-empty-join.population.json
    sha256: baa942110dd260f6cbf432d0fa50130c027e66751b7376202bfa36125ef1ff24
  - path: tests/fixtures/pyrel-rules-coverage/rp1/assertions-integer-id.population.json
    sha256: 2a309fb0f0d47e3d6cf13b4a4cec42b138977fe5b33a521d2aac5caba8dc0afe
  - path: tests/fixtures/pyrel-rules-coverage/rp1/disconnected-empty.population.json
    sha256: 4233be1a90c2bc42a5bc0282280dce817af058bfe1190694f8bf6626d21c2bc3
  - path: tests/fixtures/pyrel-rules-coverage/rp1/disconnected-facts.population.json
    sha256: 9e2f8da3eba0920f8a85c02799babda5e3fac0c44684981779ec2f6ceb58323f
  - path: tests/fixtures/pyrel-rules-coverage/rp1/disconnected-partial.population.json
    sha256: 69511dd3fa9360f4a364af91afafa579ca49327fe7f03503d378f022be5ee409
  - path: tests/fixtures/pyrel-rules-coverage/rp1/disconnected-semiderived.orm.json
    sha256: 5bc0193aa73074d9ec5707ed028c64b41ab6ce73a504c43b507be514e078975e
  - path: tests/fixtures/pyrel-rules-coverage/rp1/disconnected-semiderived.population.json
    sha256: 6ada9ab0584b8d3f8f22f1e1d58bcbdc44a5919982f85584433ea17605efff04
  - path: tests/fixtures/pyrel-rules-coverage/rp1/disconnected.orm.json
    sha256: 3d2c1de99b1837846295d5cdd0d62091a62a6d32000e2c0abf5f6679d846273e
  - path: tests/fixtures/pyrel-rules-coverage/rp1/infinite-roster.population.json
    sha256: 7604784c021b81f16ec9d246bdee0743027fe4dfb1f8a9363e1c0eeb75c1922c
  - path: tests/fixtures/pyrel-rules-coverage/rp1/infinite.population.json
    sha256: fb544aca9dae1b6df03b3f268a655eea9e1dde03241843130c926440a62d002a
  - path: tests/fixtures/pyrel-rules-coverage/rp1/numeric-anchor.orm.json
    sha256: b3eddc57affb401533190862e74a6a6149ffb48f5b17e9e596aac81bd30b37da
  - path: tests/fixtures/pyrel-rules-coverage/rp1/numeric-duplicate.population.json
    sha256: 179bf97f2e3a0fe3de23f3c89136d285bc443649f0b9d379af5f9665e315ec4c
  - path: tests/fixtures/pyrel-rules-coverage/rp1/numeric-inline-repeated.population.json
    sha256: 7a801ee030f95b29404b42c95df73a5ebe99cef1c4a2aabfb29d39c6bd87744d
  - path: tests/fixtures/pyrel-rules-coverage/rp1/numeric-inline.orm.json
    sha256: 62b3dd24c1d2f45015e1aa95713960b7fe1331422092643b229b0b38855f5a49
  - path: tests/fixtures/pyrel-rules-coverage/rp1/numeric-repeated-fact.population.json
    sha256: 105fad723955518127610069299439b35344ff544b6de6b084e5b27c7c3e4096
  - path: tests/fixtures/pyrel-rules-coverage/rp1/renamed-anchor.orm.json
    sha256: 6f6d4191965111f29dd891735ae6790183e682bdbe7426ff87a8434ee51639ff
  - path: tests/fixtures/pyrel-rules-coverage/rp1/renamed-duplicate.population.json
    sha256: 21d6b09b43d37ee4700b2b8e729324c59b8e8f02dc66cee7ecfe86ef5180e6db
  - path: tests/fixtures/pyrel-rules-coverage/rp1/three-way-duplicate.population.json
    sha256: 459d7f4c776c7eeafe67028edbcd9e2f00a5bc80fa735957eef98c995ff91935
  - path: tests/fixtures/pyrel-rules-coverage/rp1/three-way-pass.population.json
    sha256: 1a96a6509b3471a71d24e3d1638d806dcdc0e529128e33441fe540068b8eccd0
  - path: tests/fixtures/pyrel-rules-coverage/rp1/three-way.orm.json
    sha256: 2f683881401a274e9a093e94756772eab373706ddaeb9db366fc74925bc015d9
  - path: tests/fixtures/pyrel-rules-coverage/rp3/anchor-beyond.population.json
    sha256: f00a0d53b9f7b4220143065540d33ffaa6c263b8284348504616d6adb2528860
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r1/BRIEF.md
    sha256: db5bd1a54ab5af81b66965312b0cf1b9ad7be62c529f3f066f0217413173b08a
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r1/review.md
    sha256: af90362ec56fc315e9d9f9ea798a19244ea2e7aa7a9136af05d77434ac6aaf7d
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r1/FINDINGS.md
    sha256: 1c74a215688c64a7d153420a6c909e8ba6b2fe4f37ea6a5ee29e9494697e1ee7
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r2/BRIEF.md
    sha256: 7168243f89700aedd3c818ad9baecc34adbc1a95e4ddbcf9a1b4ee382a216f20
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r2/review.md
    sha256: 90ee937652aa1dbee7763097cd61eafde25b39824b3b2a7b623406d9da1f8f9f
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r2/FINDINGS.md
    sha256: 7a072c4cde8c69d199cc2cf2c271d3b032037d9b98da1e783de18aea8a2ced83
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r3/BRIEF.md
    sha256: 9a30d4b39990be18b08bcfeec890b96d7c8e4faf22428514190afdb6b8137302
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r3/review.md
    sha256: bacac81784d716649f62479051867faf4704bb6006675580448688c36afde0f7
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r3/FINDINGS.md
    sha256: 4b2c5ff1a751adf82d31844f323d58ee1758c366e39f7f556b64009c0130470f
---

# Claim

RP1's criteria C1–C9 hold at these bytes. `gnd export pyrel --rules
duckdb|lqp` lowers external uniqueness over GND's shared-entity join, and
`assertions/` and `lineage/` export. On every RP1 population the DuckDB
program's exit and findings equal `gnd check`'s, through the shared
comparator, whose negative control fails as it must. A non-string value of
an externally identified entity is refused with exit 3, where GND exits 0
(D4's stated difference).

## What shipped

- `export/pyrel_rules.py`:
  - `_external_uniqueness` lowers the rule from the shared IR: a `join`
    listing (vacuity) and a requirement over two copies of the join, `same`
    over the anchor pairs. Across fact types the anchors are object types;
    within one fact type they are its roles, because GND projects one fact
    type (measured in `semantic_spec.role_sequence_rows`).
  - A disconnected join is listed as not checked. The DuckDB report prints
    it vacuous when every referenced relation is empty, reading the
    computed view of semiderived types. An ambiguous join stays an invalid
    model at load (exit 3); the function also guards it.
  - `_Model.external` and `cell_type`: an externally identified entity is
    `String` in the programs. `check_cell` refuses a non-string with the D4
    message.
  - The population reader keys repeated rows by GND's numeric identity, and
    `check_cell` refuses a non-finite number in any cell, roster or plan
    binding.
  - The LQP `main` returns 3 for a population it cannot read.
- `docs/runtimes/pyrel.md`: external uniqueness leaves the refused list; a
  paragraph states the join, the disconnected case and D4.
- `tests/test_pyrel_rules_families.py`: the external-uniqueness refusal row
  is removed (T3 now asserts it renders).
- RF6 inventory: `evidence/RP1/dynamic-query-successor.json`, chained in
  `tests/support/pyrel_application_successors.py`. It adds the new counted
  reads (15 rows), all local lookups in `_external_uniqueness` plus one
  object-type read in `_Model.external`, and removes none.

## Gate output (verbatim)

    240 passed, 224 deselected in 18.18s
    154 passed, 58 deselected in 153.07s (0:02:33)
    679 passed, 2 deselected in 97.49s (0:01:37)
    All checks passed!
    Found 198 errors.            (uv run ruff check; known red, see gates)

## Criteria, measured

| Criterion | Test | Result |
|---|---|---|
| C1 | `test_literature_models_with_external_uniqueness_render` (4) | pass |
| C2 | `test_both_programs_state_the_one_requirement` | pass |
| C3 | `test_duckdb_program_agrees_with_gnd[assertions-raw, -duplicate, -empty-join]` (oracle) | 0, 1, 2 both |
| C4 | `test_a_non_string_external_id_is_refused_where_gnd_accepts_it`, `test_lqp_refuses_a_non_string_external_id_with_exit_3` (oracle) | 3; GND 0 |
| C5 | `test_the_review_fixture_renders_and_external_frequency_still_refuses` | pass |
| C6 | `test_a_disconnected_join_is_listed_not_lowered`; agreement `disconnected-facts` 4, `-partial` 4, `-empty` 2; `test_disconnected_vacuity_reads_computed_semiderived_relations` 2 (oracle) | pass |
| C7 | `test_an_ambiguous_join_is_refused_as_gnd_refuses_the_model`, `test_the_ambiguity_guard_also_holds_without_model_validation` | 3 both |
| C8 | agreement `numeric-anchor` 1 (anchors `1` and `1.0`); `test_numerically_repeated_facts_are_refused_not_merged` (oracle) | pass |
| C9 | agreement `three-way-duplicate` 1, `three-way-pass` 0 (oracle) | pass |
| plan §3 Ossie | `test_ossie_export_is_unchanged` (2) | digests from `6e04fe7f` |
| negative control | `test_negative_control_a_join_without_the_anchor_check_disagrees` (oracle) | disagrees |
| T10, T11, T12, T13 | one walk, runtime page, 8 malformed shapes, 200-fact-type chain | pass |
| LQP | `test_lqp_program_compiles_the_requirement` (2), `test_lqp_compile_lists_the_disconnected_rule` (oracle) | exit 0 |

## Implementation findings

1. Measured beyond the draft: GND projects a single fact type (anchors are
   its roles), and a disconnected join with one empty list is still
   unchecked (exit 4). Spec `(p3)` records both.
2. The RF6 dynamic-query guard failed on the first guard run: the new
   function's reads were not inventoried. Repaired by the authenticated
   successor above, the route earlier phases used.
3. The scaffold link check failed on the first guard run because Codex's
   `review.md` named absolute paths. `review_tool.py sanitize` replaced them.

## Review

One reviewer is one reviewer: Codex, read-only, through the review helper.

- Round 1 (`notes/reviews/phase-RP1-r1/`): CHANGES_REQUESTED, three
  findings, all reproduced against the bytes and fixed:
  - F1: rows equal by numeric identity merged into a pass;
  - F2: disconnected vacuity read the claims, not the computed view;
  - F3: the LQP program exited 1 on a refused cell.
  F1 and F3 predate RP1 (inline uniqueness on a Float role; every LQP cell
  refusal), and the repairs cover those cases too. Each has a regression
  test.
- Round 2 (`notes/reviews/phase-RP1-r2/`): CHANGES_REQUESTED, two
  findings, both reproduced:
  - F1, deferred to RP3: integers beyond 2**53 in a Float anchor merge as
    binary floats (program 0, GND 1). This is plan D6, which predates RP1
    and is assigned to RP3. RP3's spec schedules the regression (T11,
    `rp3/anchor-beyond.population.json`).
  - F2, fixed: round 1's identity key raised `OverflowError` on `1e400`.
- Round 3 (`notes/reviews/phase-RP1-r3/`): CHANGES_REQUESTED, two
  findings, both reproduced and fixed:
  - F1: the finite check missed rosters and plan bindings; it now lives in
    the shared `check_cell`.
  - F2: this record and RP3's scheduling of the deferred regression did not
    exist yet.
  Both concern this phase's own repairs, a self-inflicted ratio of 2/2, above
  the convergence rule's 1/2. Review rounds stop here. The round-3 repairs
  are verified by the regression tests and the lanes above, not by a fourth
  reader.

`review.log` (machine paths) is not retained.

## Refactoring review

Executed:
- The not-checked row gained `vacuous_if_empty`, one field that the report
  reads, rather than a second unchecked list.
- The cell type for an external entity is one method (`cell_type`) read by
  `ROLES` and `ROSTERS`.

Not executed: `_external_uniqueness` and `_uniqueness` stay separate. The
inline form's witness is facts and the external form's is referenced tuples
(GND's two message shapes), so a shared body would branch on every line.

## Process note

The implementation was drafted in the working tree before the spec's
delegated gate was written. The gate (spec §12) was then ruled over the
`(p3)` text and committed (`6cfeed33`) before this phase commit. Nothing was
committed before the gate.

## Boundary — what this phase does NOT establish

- No RelationalAI engine ran; the LQP program's enforcement is unverified.
  The LQP program lists a disconnected rule as not checked even when its
  lists are empty (it reads no population before the engine), so its exit
  there is 4 where GND's is 2.
- A repeated fact (now including `1` and `1.0` in one role) is refused, exit
  3, where GND reports it (exit 1); this is the programs' existing stance on
  repeated facts.
- A `NaN` or infinity in any cell, roster or plan binding is now refused
  (exit 3) by `check_cell`, where it was admitted before; GND refuses it too.
- Integers beyond 2**53 in a Float or Number cell are still admitted at
  these bytes: two such anchors can merge into a pass (review r2-F1),
  until RP3 refuses them.
- External frequency stays refused.
- `uv run ruff check` over the whole tree stays red (the known 198 errors).

## Open questions

None new.
