---
milestone: ossie-relational-bundle
station: "phase-OB3"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-OB3
date: 2026-11-24
gates:
  - command: "ruling: owner approved .gnd-planning/milestones/ossie-relational-bundle/notes/phase-OB3-spec.md r1 sha256 fa034f27c81394f4a69a7e230d008a3b7121f7ed72bd1df0d5192d0feb619484, E1-E16 as proposed (009-OB3-spec-gate.md)"
    exit: "n/a -- ruling"
  - command: "ruling: owner approved the corpus and amendment r1.1 (010-OB3-corpus-gate.md); expected files sha256 f4926423d727483e7028c5d5cf1d13b4092fcfaa372547b90af63601ef5477b2"
    exit: "n/a -- ruling"
  - command: "ruling: owner directed the merge of PRs 264, 266 and 270 (Merge all three), which met E1, and then Start OB3"
    exit: "n/a -- ruling"
  - command: "uv run pytest -q tests/test_ossie_export.py tests/test_ossie_relational.py tests/test_rmap.py tests/test_ossie_import.py tests/test_ossie_formulas.py tests/test_rf1_cli_pins.py tests/test_li0_witness_wire.py --tb=line"
    exit: 0
    output: "695 passed in 140.39s (0:02:20)"
    note: "plan §9 OB3 row (the first two files), plus the consumers this phase touched: the Rmap, the import, the formulas, the CLI pins and the fixture-model scan"
  - command: "the project.md structure and inventory guard block (16 files)"
    exit: 1
    output: "1 failed, 865 passed, 2 deselected in 129.60s (0:02:09)"
    note: "the one failure, tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap, is the known red (see Gate)"
  - command: "uv run ruff check"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base origin/main --strict"
    exit: 0
    output: "changed against origin/main (fd73318): 66 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
    note: "cli.export_command, export.ossie, model.relational_mapping and tools.ossie_oracle were edited with the code; export.ossie_relational is new"
  - command: "uv run python -m tests.support.ossie_relational_corpus"
    exit: 0
    output: "01: ok 04: ok 09: ok 14: ok 15: ok 17: ok 18: ok"
slow_cadence:
  command: "uv run pytest -q -m ossie_oracle tests/test_ossie_external_oracle.py"
  trigger: "explicit owner request, with GND_OSSIE_ORACLE_ROOT prepared from the OS0 receipt"
  reason: "T11 is written and not run: the upstream validator is the opt-in oracle lane. The evidence and census lanes are outside this phase's impact closure."
evidence:
  - path: .gnd-planning/milestones/ossie-relational-bundle/notes/phase-OB3-spec.md
    sha256: 297f2354b7148ac117e498fb2e1c5dc1f702fd520affe14877637e7bcd37b66d
  - path: "tests/fixtures/ossie_relational/*/expected.* (21 files; semantic models, mappings, extensions, each sorted by case)"
    sha256: f4926423d727483e7028c5d5cf1d13b4092fcfaa372547b90af63601ef5477b2
    note: "identical to the digest approved at the corpus gate: no approved file changed"
  - path: src/gnd/export/ossie_relational.py
    sha256: 50c7c039f25ee7eb104ef0f9e6d00999ff06f4d2aa62829d2bc79a372743490f
  - path: src/gnd/export/ossie.py
    sha256: 7be80aabd46213e9376c7a8211503899e8fd9806cf43ba965621417f1f8dcef4
  - path: src/gnd/commands/export.py
    sha256: 746f27147042a4cd45d884093e2dcc5700fd8dfa13d8f1bfa427b5a12df26110
  - path: src/gnd/rmap.py
    sha256: c985bb90051c7c774da75c3fcb7e1e55cfd3ed13b4d748fd7700f89f6cd3e2f9
  - path: src/gnd/schema/ossie/mapping.json
    sha256: 936118ca7753676c069d1fa615c8dced7e9a9499ab185cc2ddbe8d1c2d4404f3
    note: "apache/ossie ontology/mapping.json at ee89dbdc2844d8b7d293ed42c8613928bb99505f, byte for byte"
  - path: src/gnd/schema/ossie/PINNED.json
    sha256: e8c51162cb925bd4ada873d71edd0924483a6d3ce1fbe66f8d33eb6739c38f9d
  - path: src/gnd/skills/gnd-orm-core/references/representation-format.md
    sha256: 3fd6e99c0907035b17a41f8d35cf7640bd3a473010f12c78031475a80795a239
  - path: tests/test_ossie_relational.py
    sha256: 75c1ee1e8561087a00a17b684c50d13450af0113ff957d7e323086f4608b5e57
  - path: tests/support/ossie_relational_corpus.py
    sha256: c013b99b72e9e79a3b79010718b22ae9975394e5985903a9657c19a93c83a102
  - path: tests/test_rmap.py
    sha256: 7aab62ed9a7f3c22b8e749d739a89335e9714ec54103fa1582dcddffc7039ce0
  - path: tests/test_ossie_external_oracle.py
    sha256: 6e789feeab73c07d5de52f7ed169eb29494450f29493b63dc12041b4cffc7293
  - path: tools/ossie_oracle.py
    sha256: 7190dd76a08571575054ec7a3cf56fb1d641f6a56b0bc2743a05fbf27e0bc1a8
  - path: .gnd-planning/milestones/ossie-relational-bundle/notes/OB3-rmap-measurement-after-E3.md
    sha256: 42ac0a7dce19ca5763184806e206d9c0d3e3734ac02bf8303af8a40592fc8f38
  - path: .gnd-planning/milestones/ossie-relational-bundle/evidence/OB3/dynamic-query-successor.json
    sha256: d20de719ce33ba4c5d58f53b913c7ef0ab7704c2be698726e43c12599397b4e6
  - path: .gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB3-r1/review.md
    sha256: d90fe2009507c11d4349a61d6527c4e71fa3fd94f384b1d52cfff112587f8dc1
    note: "sanitized; the reviewer's original bytes are 607d402f7212e41e60d7ea9b9de4d22d0477d283b4aeca55d606fbe89ffe4b93, bound by run.json"
  - path: .gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB3-r1/SANITIZATION.md
    sha256: 7e7c1e5ec466b4d7684dade40ef534564a36ea45ba324dc6b3935d7f292639d2
  - path: .gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB3-r1/FINDINGS.md
    sha256: 373845db26b2404a51b3cfc9747bebb182b5564dd62def2a759b357c28bae0ce
---

# Phase OB3: the relational files (semantic model and mapping)

## Claim

- **Five files by default** (D2 a). `gnd export ossie MODEL --out OUT` writes
  the ontology, sidecar and loss report as before, plus
  `OUT.semantic_model.<fmt>` and `OUT.mapping.<fmt>`. `--ontology-only`
  writes the first three.
- **The legacy files do not change.** With `--ontology-only`, all 82 census
  entries equal the OB1 baseline (T6). The default run's three legacy files
  are the same bytes (OB1 T1, and T6 at the command).
- **The approved corpus holds.** All seven cases equal their hand-derived
  files byte for byte in YAML, and in structure in JSON (T1).
- **Valid against the pins** (OB3-C1). The vendored core-spec accepts every
  semantic model and the vendored `mapping.json` every mapping, for every
  scanned model the export maps (844 exports), with cross-document
  references resolved offline (T2).
- **Self-consistent** (T3). Every expression names a declared field; every
  link names a relationship of its concept at the level its arity calls
  for; every referent follows the ontology's `identify_by`.
- **One walk** (OB3-C3). Every fact type and constraint appears exactly once
  in the mapping's `GND` extension. Every carried fact type is named by
  exactly one link tree or listed in `unmapped_links` with a reason (T4).
- **Reproducible** (OB3-C4). The five files do not depend on the run or the
  source path (T5).
- **Collisions and size** (OB3-C5, C6). A file at any of the five paths
  exits 11 and publishes nothing (T7). `--max-output-bytes` bounds the
  semantic model and the mapping, at size minus 1 and at size (T8).
- **Populations** (OB3-C7, D6). A `sample_population` leaves the semantic
  model identical and changes only `model_identity` in the mapping; the loss
  report gains its `population:out-of-scope` rows (T9).
- **Time** (plan §0 rule 2). At 1,400 entities and 4,500 fact types the five
  files render in 3.3 s, against 2.6 s for three; the ratio to one fifth of
  that scale is 5.1 (T10).
- **Rmap** (E3, E4). A composite identifier needs every component functional
  on the entity. `RelationalSchema` publishes role placements and
  identifications (T13, T16).
- **One home.** The rules are in `representation-format.md` § "Ossie
  interchange", "Semantic model and mapping".

## Gate

The front matter gives each command and its exit verbatim.

**Known red.** `tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap`
fails because `.agents/skills/review-pr/SKILL.md` cannot resolve
`../process-phase/references/review-tool.md`, a discovery-link layout this
worktree has not adopted. It failed on the phase base before any OB3 edit:
the tree `95ca5a24`, which is main at `fd733185`, was tested before the
merges of PRs #264, #266 and #270 and gave `1 failed, 1423 passed`, that
test being the failure. OB3 touches no part of that layout.

## Review

There was one reviewer, Codex, run through `review_tool.py` with a read-only
sandbox and effort high, over base `39e3d4c3` to head `5f687385`. **One
reviewer is one reviewer.**

| Item | Value |
|---|---|
| Review | [review.md](notes/reviews/phase-OB3-r1/review.md), sha256 `607d402f…4b93` as written, `d90fe200…8dc1` after path sanitization ([SANITIZATION.md](notes/reviews/phase-OB3-r1/SANITIZATION.md)) |
| Verdict | CHANGES_REQUESTED, with five findings |
| Ledger | [FINDINGS.md](notes/reviews/phase-OB3-r1/FINDINGS.md) |

| Id | Class | Reproduced | Disposition |
|---|---|---|---|
| F1 | blocking | yes | fixed: a composite identifier's object mapping reads the table's own key columns |
| F2 | blocking | yes (crash at 250 roles) | fixed: more than 32 roles is listed as `arity-over-limit`, not nested |
| F3 | blocking | yes | fixed: foreign-key names are unique in the schema |
| F4 | hardening | yes | fixed: each `iri` percent-encodes the file name |
| F5 | completeness | yes (it is IF1) | **open, the owner's** (OB3-Q1) |

Eight regression tests were shown failing on the pre-repair bytes before any
fix. The repairs are commit `110f805a`.

The reviewer also confirmed: 194 tests over the corpus, census and
baselines; validation with sockets blocked and no network attempt; the
bound at size minus 1 and at size for both new files; identical bytes across
runs and paths; the functional-component rule under both variants; and its
matcher probes of the identifier quoting and lexing, with no breaking input.

**The repaired bytes are not reviewed.** No second round ran.

## Refactoring review

**Refactors EXECUTED**, behind the same gates:
- **One encoder.** The YAML and JSON encoding of the ontology was inline in
  `render_ossie`. It is now `_encode`, which all five files use. The
  ontology's bytes are unchanged (the OB1 baseline).
- **One projection.** `_ontology` became `_project`, which also returns the
  `OntologyView` the mapping reads, so concept names, role order and
  `identify_by` are computed once. `_ontology` remains for its two callers.

**Seen and deferred.**
- The ontology export declares no identifier for a unit-based reference,
  nor for a subtype inheriting through several supertypes. The mapping
  cannot cover those (16 fact types in 14 scanned models). Row OB3-Q5.
- `export/ossie.py` still has its own "confirmed alethic" predicate (OB2-Q1),
  kept by E15.
- `tests/test_ossie_relational.py` and `tests/test_rmap.py` each scan the
  fixture models with a small helper of their own. Row OB3-Q6.

## Refuted premises and findings

The spec's §12 (IF1–IF13), §13 (H1–H4), §14 (B1–B14) and §15 (RR1–RR4) list
them all. The ones that change an earlier document:

- **Plan predicate 2 and §5** say the default run always adds the two
  files. A model that maps to no table cannot have a semantic model, because
  the pinned core-spec requires a dataset (IF1).
- **Plan §2.3** says the Rmap takes any preferred external uniqueness as a
  composite key. The ontology export requires functional components, and so
  does Halpin; E3 (a) aligned the Rmap.
- **Spec §6.4** gave value types object mappings. The pinned schema allows
  them only on entity types (B1).
- **Spec §6.2** gave one `render_relational` function. The builders are
  split from the encoder (IF6), and `render_ossie` needs the output file's
  name (B2).
- **Spec §6.5 and §6.6** named two reasons and no list for unmapped links.
  There are three reasons and the list `unmapped_links` (IF2, RR2).
- **OB2 A11** counted foreign-key names per table pair. They are now unique
  in the schema (RR3).

The plan is not edited here; these go to the milestone-close amendment.

## Open questions

| Id | Question | Target |
|---|---|---|
| OB3-Q1 | **A model that maps to no table** writes three files and a note (IF1, review F5). Accept that, or refuse such an export unless `--ontology-only` is given? | owner, before OB4 |
| OB3-Q2 | Accept the three rules implementation and review added: the `unmapped_links` list (IF2), the 32-role limit with reason `arity-over-limit` (RR2), and schema-wide foreign-key names (RR3, amending OB2 A11)? | owner, before OB4 |
| OB3-Q3 | Run the opt-in oracle lane (T11)? Until it runs, upstream acceptance of the quoted identifiers and of `CASE WHEN` is unconfirmed. | owner |
| OB3-Q4 | Should the review repairs (`110f805a`) get a second round, or are OB4's tests the next instrument? | owner, before OB4 |
| OB3-Q5 | Should the ontology export declare identifiers for unit-based references and multi-supertype subtypes, so that the mapping can cover them? | close sweep, or a separate issue |
| OB3-Q6 | Share one fixture-model scan between the Rmap and relational tests? | OB4, which adds a third test file |
| OB1-Q1 | Carried: `guard_yaml`'s captured default. | OB5 or the close sweep |
| OB1-Q2 | Carried: D11, the source cap. At the reporter's scale the generated source is 1.5 MB. | after D10's answer |
| OB2-Q1, OB2-Q2 | Carried: the duplicated predicate; `refscheme`'s selection. | close sweep |

## Boundary

- **Residuals.**
  - **NULL semantics (E8).** "A NULL yields no link" is GND's reading; Ossie
    does not define it. Unary fact types and absorbed subtypes depend on it.
  - **Identifier length (E16).** No name is shortened. None of 3,157 scanned
    fields exceeds 128 characters.
  - **`identification-differs`.** 16 fact types in 14 of 422 scanned models
    have a table and no link mapping.
- **Size** (spec §10 estimated about 350 renderer, 60 wiring, 40 Rmap, 90
  normative and 450 test lines):
  - `ossie_relational.py`: 316 lines.
  - `ossie.py` and `commands/export.py`: 138 lines added and 26 removed,
    about 2.3× the estimate, from the ontology view (E12), the encoder and
    the IRI encoding.
  - `rmap.py`: 89 added and 5 removed, about 2.2×, from the identification
    record (IF5).
  - Normative text: 98 lines.
  - Tests: `test_ossie_relational.py` 586 lines and the corpus checker 336,
    about 2× the estimate, mostly the cross-checks that had to exist before
    the renderer.
- **Not done:** the physical binding (OB4). The explanation, how-to, export
  skill and release-note entry (OB5): **they still describe three files.**
  No import of a semantic model or mapping. No DDL.
- **Not run:** the opt-in oracle lane (T11), and the evidence and census
  lanes.
- **Not pushed.** Branch `claude/ossie-ob3-relational-spec`, cut from main
  at `fd733185`, has no pull request; opening one is the owner's call.
- **Approval:** this record approves nothing beyond OB3. Merge is the
  owner's.
