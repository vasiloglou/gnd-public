---
milestone: composition-and-type-induction
station: "phase-CT3"
skill: "n/a -- repository development under process-milestone auto=true, not a gnd-solve station"
scope: phase-CT3
date: 2026-11-04
gate:
  command: "uv run pytest -q tests/test_composition.py tests/test_schema_sync.py tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py tests/test_v61_phase2_api.py tests/test_public_api.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py tests/test_packaged_skills.py tests/test_skill_prose_sync.py tests/test_public_v71_witness_corpus.py tests/test_public_optional_value_witness.py tests/test_public_replay_admission.py tests/test_public_replay_driver_support.py $(grep -rl 'gnd.witness\\|api.witness\\|api.replay' tests/*.py)"
  exit: 0
  output: "1341 passed, 11 deselected in 297.52s"
  note: >-
    The spec's verification selection plus every test file that imports
    gnd.witness or calls api.witness or api.replay (15 files, among them
    test_witness_composition, test_disclosure_mode and the why-not suites).
    Run after the review fixes. Docs: strict build clean; 13926 links
    checked; ruff clean on gnd.witness and the new tests.
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "outside CT3's impact closure"
evidence:
  - path: .gnd-planning/milestones/composition-and-type-induction/notes/phase-CT3-spec.md
    sha256: d98c632acae4fa39cc886fd3b71dd23c6d4890981244b123876e891f41fbea97
  - path: .gnd-planning/milestones/composition-and-type-induction/notes/phase-CT3-claude-review.md
    sha256: 19fd8daadaebb75e77291946ca44667d2f647ac88e4b53b78499481e8b86d731
  - path: .gnd-planning/milestones/composition-and-type-induction/evidence/CT3/capture_parity.py
    sha256: 907897e7d71d2c2fc008e5390a005709f9221acc9ef7ec1d53937b5e4368464c
  - path: .gnd-planning/milestones/composition-and-type-induction/evidence/CT3/parity-a2e44f8.json
    sha256: 4af54a97bac7e73094c49364b82a52bd3b1ce548a7a284aae85644b27fed9b23
  - path: .gnd-planning/milestones/composition-and-type-induction/evidence/CT3/parity-after.json
    sha256: 4af54a97bac7e73094c49364b82a52bd3b1ce548a7a284aae85644b27fed9b23
  - path: .gnd-planning/milestones/composition-and-type-induction/evidence/CT3/dynamic-query-successor.json
    sha256: b91632850188468ad56997754a1bdd51037e6c0945b27753ef47d58b4a731ab9
  - path: src/gnd/witness/io.py
    sha256: 6e9802812c4e4b8f55c0eb6f1b3e944a0c6460e1159fdf6184e1c7e5232d170e
  - path: src/gnd/witness/kernel.py
    sha256: 85337abf192f2950b07eea8854f72e2f57188d71e4cee5ad48a4db8605d35fdd
  - path: src/gnd/witness/service.py
    sha256: 8026b5dd9f4d79dda3a884f0ad5f3878b501442599f79e3566452eea9d754ce7
  - path: src/gnd/witness/cli.py
    sha256: a9b51df9f64ee629d3bc15bfed3a5d86ce7909160d7bd7d489c4781597b6fe30
  - path: src/gnd/witness/view.py
    sha256: 4e9f25371f225c912d7123dae54ffe65fb51550a579b9dcdd57da79baa7243e1
  - path: src/gnd/schema/witness.schema.json
    sha256: 6d2b955fd50bbb38f990c4e8e67dbcb7f2a1489b8a3b4b90384f1c4e9a64c6bd
  - path: src/gnd/skills/gnd-export/references/witness-contract.md
    sha256: cbf2c85cc15764736ebda9eab3e591803291807cfd1167011656a72317062029
  - path: tests/test_witness_composition.py
    sha256: 13c3ecbed9fd4352a5be2a64944af2408a48780bf91bc6400e2f848d91653ff9
  - path: tests/fixtures/rf1-pins/goldens.sha256
    sha256: 7f5015376669b296939c3289c81f4cba3f51b505609105affac46cd68a976465
---

# Phase CT3: witness lineage

**Claim.** `gnd witness ... --composition RECORD` (and `api.witness(...,
composition=)`) writes a version-2 witness whose binding names the record's
raw-byte SHA-256 and whose base nodes list their source facts from the
record. `gnd replay ... --composition RECORD` (and `api.replay`) refuses a
different record (3 `binding-stale`), any base node whose `sources` differs
(1 `proof-invalid`), a version-2 witness without a record (3
`composition-required`) and a version-1 witness with one (3), then replays
the graph as before. Version-1 production, replay and views over the v71
witness corpus are byte-identical to `a2e44f8` (20 rows). The focused gate
exits 0.

**Authority.** Plan r3 `(a1)`. Spec r1 under **delegated approval
(auto=true)** `(d1)` 2026-11-04 (digest in the spec); an agent ruling under
the owner's "Yes, run it auto", not the owner's personal reading.

## What changed

- `gnd.witness.io.certificate_shape` accepts version 2; `kernel.replay_witness`
  takes `composition=`; `service` adds `composed_witness_result` and
  `composed_replay_result` (the pinned `witness_result` and `replay_result`
  are unchanged, as `test_disclosure_mode.py` requires); `cli` adds
  `--composition` to `witness` and `replay`; `view` lists `sources`.
- Schema and its `gnd-export` twin (now pinned in `tests/test_schema_sync.py`);
  the witness contract's version-2 section; `docs/reference/composition.md`
  "Trace a derived fact back to its sources"; release note.
- Pins: RF1 goldens for `witness` and `replay` and `tree.json`; manifest
  digest; one RF6 successor (4 rows).

## Criteria

| Criterion | Evidence | Result |
|---|---|---|
| CT3-C1 version 2 in the schema and twin; v1 table | T2 tests; `test_schema_sync`; `evidence/CT3/parity-*.json` identical | holds |
| CT3-C2 edited `sources` exits the mismatch code; unedited 0 | replay tests (first and last base node, a float index) | holds, code 1 (D2) |
| CT3-C3 two documents, a rule joining both, base nodes trace to spans in each | end-to-end test | holds |
| CT3-C4 Souffle witness export and why-not | refuted premise: neither reads a certificate (D4); why-not on composed bytes equals the plain run | holds for why-not; `souffle-witness` needs the optional native toolchain and was argued from code only |

**Refuted premise.** The plan's §2.3 says "The Souffle witness export and
`why-not` read witnesses". Neither does: both take a model and a population.

**Deviation.** The spec says `result_view` shows `sources`; that view lists
results only, no nodes, so `sources` appear in `witness-view` (both
redacted and expanded) and in the raw certificate.

## Review

One local reviewer agent, read-only: **approve-with-fixes**, one blocking
finding ([review](notes/phase-CT3-claude-review.md)).

| Finding | Disposition |
|---|---|
| F1 (blocking) `ArtifactError` from unsafe or missing paths escaped as a traceback (exit 1); a record missing a base fact raised `KeyError` | fixed: both composed paths catch it (3); a missing lineage entry is 3; tests |
| F2 the byte ceiling was not re-checked after stamping | fixed: exit 4 `work-limit`; test |
| F3 replay checks the witness against the record, not the record against the sources | documented in the contract and the composition page |
| F4 reference-origin bases | fixed: a model with reference populations is refused (3); stamping requires candidate origins |
| F5 inputs read twice with different rules | accepted residual: both reads are of the same caller paths; the second read is the existing witness intake |
| F6 surviving mutants | fixed by tests for the model digest, the last base node, a float index, expanded views, the producer lookup (the end-to-end test names index 0 of two different facts) and the API signatures; `souffle-witness` stays untested (native lane) |
| F7 the schema is looser than the shape check on a few values | accepted: the shape check is the authority |
| F8 the contract omitted `input-invalid` | fixed |
| F9 the parity table covers success paths only | accepted: the v1 failure paths are covered by the unchanged witness suites in the gate |

## Refactoring review

The composed paths wrap the unchanged producer and replay rather than adding
parameters to the pinned functions. The lineage index is built once per call.
No new module; no layer change.

## Questions

None opened.

## Boundary

Not merged, released or certified.
