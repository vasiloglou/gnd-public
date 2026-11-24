---
milestone: ossie-relational-bundle
station: "phase-OB2"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-OB2
date: 2026-11-24
gates:
  - command: "ruling: owner approved .gnd-planning/milestones/ossie-relational-bundle/notes/phase-OB2-spec.md r1 sha256 6bcca4ed157ec84b674fb2b2fb955ad470f5f17c33e3c72e8dac68625c2cb972, S1-S11 as proposed (005-OB2-spec-gate.md)"
    exit: "n/a -- ruling"
  - command: "ruling: owner approved the corpus and amendment r1.1, spec sha256 7b38ddbd67fec77e091b578ba869be27a28cf9ebe249deb49c64fb784990b26b (006-OB2-corpus-gate.md)"
    exit: "n/a -- ruling"
  - command: "ruling: owner ruled D5 = HALPIN and accepted IF5 and RR1 (007-OB2-D5-gate.md)"
    exit: "n/a -- ruling"
  - command: "uv run pytest -q tests/test_rmap.py tests/test_li0_witness_wire.py --tb=short"
    exit: 0
    output: "96 passed in 38.69s"
    note: "plan §9 OB2 row, plus test_li0_witness_wire, which scans fixture models (spec IF10)"
  - command: "the project.md structure and inventory guard block (16 files)"
    exit: 1
    output: "1 failed, 865 passed, 2 deselected in 122.31s (0:02:02)"
    note: "the one failure, tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap, is the known red (see Gate)"
  - command: "uv run ruff check"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base a7847f2b --strict"
    exit: 0
    output: "changed against a7847f2b (a7847f2): 106 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "the broad controls are outside this phase's impact closure; T1 and T5 already map every census model"
evidence:
  - path: .gnd-planning/milestones/ossie-relational-bundle/notes/phase-OB2-spec.md
    sha256: 80ef7b68e6ae0bb9c07590201d8a07c8273e995d2a3018a29eb279e8b8676743
  - path: .gnd-planning/milestones/ossie-relational-bundle/007-OB2-D5-gate.md
    sha256: 769a582738383a1e115b9e41b7becff992afa2669938cc34f63c8f1175e611eb
  - path: src/gnd/rmap.py
    sha256: 414a891733d63d1b5ef4040fc2552e0ab0f04110e89e0f1a79c70d752adbc67e
  - path: src/gnd/skills/gnd-orm-core/references/representation-format.md
    sha256: dd67d53b65fdac6f2b53443f39365621f52768d4a57fe2012e5ccb7a6d0f786f
  - path: tests/test_rmap.py
    sha256: 5c893a4cc219bed7c8dea00daefa3db48f32173c01dec232c3f8972f0de18d89
  - path: tests/support/rmap_large.py
    sha256: 2ad02afe03b94e4e69fffec2f4a60276dfd75591864554b353c23f802adfb36b
  - path: tests/fixtures/rmap/README.md
    sha256: 3922e662d8ce61118a4d33b25090bbf207e065e164076d2257e13c497f3e69b2
  - path: tests/fixtures/rmap/answers/README.md
    sha256: 84ae2427b49911355dfdb0ea472de54cc8f32286b4074897eba2262412edb2a1
  - path: "tests/fixtures/rmap/answers/*.json (28 files, sorted concatenation)"
    sha256: 7a4e6ee6116f0e327252abfc8a7d5d9fcb387d187d849154d50ae7acf7fb78e0
    note: "identical to the digest approved at the corpus gate: no approved answer changed"
  - path: tools/rmap_variant_measurement.py
    sha256: c8cc82db8f552c884160adc51e798b1225b1dbd877c258d16c9f497bf88b358e
  - path: .gnd-planning/milestones/ossie-relational-bundle/notes/OB2-variant-measurement.md
    sha256: 90d7d0d39feb384c427b59911245d16fadb2a6d2d7109f39e909179a270ab36d
  - path: .gnd-planning/milestones/ossie-relational-bundle/evidence/OB2/dynamic-query-successor.json
    sha256: deaa829cc2a4442849fca747d8cbff2fa4a5936a88364981c344a086506aedb4
  - path: .gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB2-r1/review.md
    sha256: 8ecc9256423dc0158b32c834b64a0157f3ec9641ab0dbeeff46d9c9469824c93
    note: "sanitized; the reviewer's original bytes are 50e188ef9302c5992a6de9ed1dc047bcaf5717aa1554cdb7b9bfc4f00de0af8b, bound by run.json"
  - path: .gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB2-r1/SANITIZATION.md
    sha256: 26941c7f96caefc9e67fce2c3f803d55d25111e2d3b7adf2993e99f6e802bbd9
  - path: .gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB2-r1/FINDINGS.md
    sha256: 7d0f36b01140df8ea85d12876b5e4e84aeb6f87cf099825a991e0f1e0a7c534e
---

# Phase OB2: the Halpin relational mapping (`gnd.rmap`)

## Claim

- **Library.** `gnd.rmap.map_model(model, *, variant=RmapVariant.HALPIN)`
  maps a loaded model to a `RelationalSchema`: tables, ordered columns,
  primary keys, unique keys, ordered composite foreign keys, and an unmapped
  list with a closed set of reasons. `dispositions(model, schema)` is the one
  walk: exactly one row for every fact type and every constraint (plan §0
  rule 4). No CLI, no Ossie file and no DDL change (§9).
- **Corpus.** All 25 owner-approved corpus cases equal their hand-derived
  answers under HALPIN, and cases 07, 08 and 15 also under ALTERNATE (T6).
  No approved answer changed.
- **Totality** (OB2-C1). Every standalone census and fixture model the loader
  admits maps under both variants without raising, including adversarial
  identification cycles (T1, T1b).
- **One walk.** Every fact type and constraint address appears exactly once
  in `dispositions` over census and corpus (T2). A missing row raises rather
  than defaulting (IF1).
- **Determinism** (OB2-C3). Reversed declaration order and another source
  path give an equal schema and equal dispositions (T3, T3b, R3).
- **Time** (OB2-C4). The 1,400-entity, 4,500-fact-type model maps within
  the recorded bound; the 5× model's time ratio is under 12 (T4, T4b), and
  composite identification does not grow superlinearly (R9).
- **D5** (OB2-C5). Both variants are measured over 66 models
  ([measurement](notes/OB2-variant-measurement.md)); the owner ruled HALPIN
  ([D5 gate](007-OB2-D5-gate.md)). ALTERNATE stays behind the internal switch.
- **Normative home** (plan §0 rule 5). The rules are in
  `representation-format.md` § "Relational mapping (Rmap)", before
  "Ossie interchange".
- **Homes.** `gnd.rmap` is assigned layer `model` in `tools/gnd_layers.json`
  and indexed as `model.relational_mapping`. Its model reads go through
  `ModelIndex`; its dynamic-subscript census is a counted successor delta
  (IF6), and no query exception is widened.

## Gate

The front matter gives each command and its exit verbatim.

**Known red.** `tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap`
fails because `.agents/skills/review-pr/SKILL.md` cannot resolve
`../process-phase/references/review-tool.md`. That is a discovery-link
layout this worktree has not adopted (AGENTS.md:
`uv run gnd install --symlink --project --force`). OB2 is cut from the same
base, `a7847f2b`, on which the OB1 record proved this test fails with no
phase diff applied (`1 failed in 0.47s`), and OB2 touches no part of that
layout.

## Review

There was one reviewer, Codex, run through `review_tool.py` with a read-only
sandbox and effort high, over base `e7af6f50` to head `af34a54e`. **One
reviewer is one reviewer.**

| Item | Value |
|---|---|
| Review | [review.md](notes/reviews/phase-OB2-r1/review.md), sha256 `50e188ef…af8b` as written, `8ecc9256…9c93` after path sanitization ([SANITIZATION.md](notes/reviews/phase-OB2-r1/SANITIZATION.md)) |
| Verdict | CHANGES_REQUESTED, with nine findings |
| Ledger | [FINDINGS.md](notes/reviews/phase-OB2-r1/FINDINGS.md) |

| Id | Class | Reproduced | Disposition |
|---|---|---|---|
| F1 | blocking | yes (R1) | fixed: the Rmap selects the confirmed, alethic, preferred external uniqueness (RR1) |
| F2 | blocking | yes (R2) | fixed: duplicate uniqueness constraints form one key, preferred if any is |
| F3 | blocking | yes (R3) | fixed: unique keys sort by column position |
| F4 | blocking | yes (R4) | fixed: an external uniqueness within one table is a unique key |
| F5 | blocking | yes (R5) | fixed: a narrower objectified uniqueness is a unique key |
| F6 | blocking | yes (R6) | fixed: under ALTERNATE, an inheriting subtype's supertype gets a table |
| F7 | hardening | yes (R7) | fixed: a role played by a tabled value type is a foreign key |
| F8 | blocking | yes (R8) | fixed: an absorbed unary column is nullable |
| F9 | blocking | yes (R9) | fixed: identifiers are indexed once per model |

All 15 regression tests were shown failing on the pre-repair bytes before
any fix. The repairs are commit `4b50f740`.

**The repaired bytes are not reviewed.** No second round ran.

## Refactoring review

**Refactor EXECUTED.**
- **What (RR9):** the role-to-column map was held as text keys and split
  apart again. It is now a dictionary from fact type to role to columns, and
  the constraint index is passed in rather than parsed out of its address
  (AGENTS.md, "General solutions").
- **Behaviour:** preserved; the corpus and every census row are unchanged.
- **Gate:** the same focused gate and guard block above.

**Seen and deferred.**
- `export/ossie.py` and `gnd.rmap` each decide "confirmed alethic"
  uniqueness. OB3 edits `export/ossie.py` and should make it consume the
  Rmap's dispositions (spec §9). Row OB2-Q1.
- `refscheme.reference_identity` takes the first external uniqueness
  anchored on an entity, whatever its `preferred` flag and status, and
  rebuilds a map per call. The Rmap no longer uses it (RR1), but its other
  callers keep that behaviour. Row OB2-Q2.

## Refuted premises and findings

The spec's §13 (IF1–IF10) and §14 (RR1–RR9) list them all. The ones that
change an earlier document:

- **Plan §2.3 rule 2** groups n−1 uniqueness of n-aries into an entity
  table. That is not Halpin and has no table to group into. Corrected by S5
  at the spec gate.
- **Plan §2.3 on "no uniqueness".** The plan did not cover the majority
  case: 119 of 226 census fact types declare no uniqueness. S1 covers it.
- **Plan OB2-C4's 10× scale** cannot load under `MAX_MODEL_BYTES` (IF4).
  T4b runs at 5×.
- **Spec §6 reuse table** said composite identification reuses `refscheme`.
  It cannot: wrong selection (F1) and quadratic cost (F9). Replaced by RR1,
  accepted at the D5 gate.
- **Spec S7 and A4** omitted rule 1 from the rules that give an entity a
  table (IF5), accepted at the D5 gate.

The plan is not edited here; these go to the milestone-close amendment.

## Open questions

| Id | Question | Target |
|---|---|---|
| OB1-Q1 | Carried: should `guard_yaml`'s default `max_bytes` resolve `MAX_BYTES` at call time? OB2 reads no YAML itself. | OB5 or the close sweep |
| OB2-Q1 | Should `export/ossie.py` take its "confirmed alethic" decisions from `gnd.rmap.dispositions` instead of its own predicate? | OB3 |
| OB2-Q2 | Should `refscheme.reference_identity` honour `preferred` and confirmation, and cache its value-type map, for its other callers? | milestone close sweep, or a separate issue |
| OB2-Q3 | Should the repaired Rmap bytes (`4b50f740`) get a second review round before OB3 builds on them? | owner, before OB3 |

## Boundary

- **Size** (spec §10 estimated about 450 source, 120 normative and 350 test
  lines):
  - `rmap.py`: 741 lines, about 1.6× the estimate, from the composite
    identifier index (RR1), external and objectified unique keys (RR4, RR5)
    and the ALTERNATE supertype tables (RR6).
  - Normative section: 126 lines.
  - Tests: `test_rmap.py` 518 lines, plus a 42-line generator; the
    measurement tool is 94 lines.
  - Corpus: 25 cases with stories and 28 answer files.
- **Not done:** no Ossie semantic model or mapping files (OB3), no physical
  binding (OB4), no docs or skill (OB5), no DDL, no CLI.
- **Not run:** the opt-in oracle lane, and the evidence and census lanes.
- **Not pushed.** This branch has no pull request; opening one is the
  owner's call. It is cut from the planning branch, not from OB1.
- **Approval:** this record approves nothing beyond OB2. Merge is the
  owner's.
