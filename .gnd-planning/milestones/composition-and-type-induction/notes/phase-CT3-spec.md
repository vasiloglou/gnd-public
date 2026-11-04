# Phase CT3: witness lineage

**Status: r1, delegated approval (auto=true) 2026-11-04 `(d1)`.**
Implementation follows this approval and the CT2 record.

`(d1)` **Delegated approval (auto=true)**, 2026-11-04. Authorization: the
owner's "Yes, run it auto" in this session, invoking `process-milestone
composition-and-type-induction auto`. An agent ruling under that delegation,
not the owner's personal reading. Approved bytes: SHA-256
`b544f5ea65af89e243b90a9711a70a16cefa5bdfc98c69e2b6e50b7b963aad3c` (before this tag), after the implementability sweep at `2c25ba4`
(CT2 committed): `certificate_shape`, `identity` and `replay_witness` are the
only certificate readers besides `witness-view` (`view.py`); `gnd export
souffle-witness` and `gnd why-not` take a model and population and read no
certificate (D4: the plan's assumption that they read witnesses is a refuted
premise); the schema twins are byte-identical today. Rulings: D1 to D4 (a).
Budget: about 140 source, 40 schema and 350 test lines; no paid calls.
Compatibility: version-1 witnesses unchanged (CT-R1, T1). Diff review
instrument: one local reviewer agent.

## Provenance

- Plan: [composition-and-type-induction-plan.md](composition-and-type-induction-plan.md)
  r3, approved `(a1)` 2026-11-03: §2.3, §3 (homes), §4 CT3, §9 CT3 row, §10
  CT-D6, CT-Q2, CT-Q3.
- Source: [issue #73](https://github.com/vasiloglou/gnd-public/issues/73)
  request 2 (GR-T10).
- Inspection baseline: `a2e44f8` plus CT1 and CT2 on the same branch; CT2
  supplies the composition record and its lineage.
- Authority: the owner's "Yes, run it auto" (2026-11-04). **This spec's
  bytes carry no review opinion.**

## Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| #73.2, plan O3 | A witness over a composed population names, for each base fact, its source facts, and through them their spans | witness version 2; T3, T5 |
| Plan CT-R1 | Version-1 witnesses replay byte-identically | T1 table |
| Plan CT-D6 (a) | `origin.kind` stays `candidate`; `sources` is added | schema; T2 |
| Plan CT-Q2 | Witness digest form against raw-byte sidecar digests | D3 |
| Plan CT-Q3 | Replay's mismatch exit code; Souffle and why-not handling | D2, D4 |
| Plan CT-R7 | Witness views stay value-free under `customer`; `sources` carries ids and indexes only | T6 |
| Plan CT-R8 | Layering, RF6, anonymity | T8 |

## Standing rules bound to this phase

1. **Totality:** `certificate_shape` stays total over both versions; every
   new branch raises `WitnessInputError`, reported as exit 3 `input-invalid`.
2. **Input cap bounds the algorithm:** the record is read under CT2's 16 MiB
   cap; the lineage lookup is one dictionary built once, so stamping and
   checking `sources` is linear in base nodes.
3. **Validation order:** certificate shape, then the record (parse, then its
   model and population digests against the replay inputs), then the binding
   (including `composition_sha256`), then the graph.
4. **One walk:** the producer stamps `sources` on the base nodes it already
   emits; replay compares `sources` while it already visits each base node.
5. **One home:** `witness-contract.md` is the normative prose for version 2;
   the schema and its twin describe it and `tests/test_schema_sync.py` holds
   them byte-identical.
6. **Measurement over argument:** CT-R1 is a recorded before/after table over
   every committed witness case (T1).

**Plan rules:** CT-R1 (T1), CT-R2 (contract wording: lineage locates spans,
it proves nothing), CT-R3 (the record is read, never re-derived here: re-
derivation is `gnd check --composition`, D1), CT-R4 (D3), CT-R5 and CT-R6 not
applicable, CT-R7 (T6), CT-R8 (T8).

## Goal

`gnd witness MODEL COMPOSED --targets T --composition RECORD` writes a version-2
witness: `binding.composition_sha256` is the SHA-256 of the record's bytes and
every base node carries `sources`, the record's lineage for its composed fact.
`gnd replay MODEL COMPOSED CERT --composition RECORD` exits as replay does
today when every node's `sources` equals the record's lineage, and 1
(`proof-invalid`) when one differs. Version-1 witnesses produce and replay
byte-identically to `a2e44f8` (T1). The CT3 gate exits 0.

## Design

### Witness version 2 (schema, twin, contract)

- `version`: `1` or `2`.
- Version 2 `binding`: `model_digest`, `candidate_digest`, `references` as
  today, plus `composition_sha256` (64 lowercase hex, no prefix: it is a
  raw-byte digest of a file the caller holds, CT-R4).
- Version 2 base node: as today plus `sources: [{source, fact_type,
  fact_index}]`, one or more entries, equal to the record's `facts[].sources`
  for (`fact_type`, `origin.fact_index`). `origin.kind` stays `candidate`
  (CT-D6 (a)).
- Version 1 is unchanged: no `composition_sha256`, no `sources`.

`src/gnd/schema/witness.schema.json` and
`src/gnd/skills/gnd-export/references/witness.schema.json` change together and
`witness.schema.json` joins `tests/test_schema_sync.py`'s pairs, comparing the
`gnd-export` references copy with `src/gnd/schema/` (a second canonical
directory beside `gnd-orm-core`). `witness-contract.md` gains a "Version 2:
composed populations" section.

### Producer (`src/gnd/witness/service.py`, `producer.py`, about +50 lines)

`witness_result(..., composition=None)`: with a record path, read and parse it
(CT2's `parse_record`), require `model_sha256` and `population_sha256` to equal
the raw-byte SHA-256 of the model and population files (3 otherwise, D1), and
produce as today; then set `version: 2`, add `binding.composition_sha256`, and
stamp `sources` on every base node from the lineage index. A model with
reference populations cannot be composed (CT-D11), so every base node has
`origin.kind: candidate`.

### Replay (`src/gnd/witness/kernel.py`, `service.py`, about +40 lines)

`replay_result(..., composition=None)`:

| Certificate | `--composition` | Result |
|---|---|---|
| version 1 | absent | unchanged (T1) |
| version 1 | present | 3, `binding-stale`: the certificate binds no composition |
| version 2 | absent | 3, `composition-required` |
| version 2 | present, record digests differ from the inputs | 3, `input-invalid` |
| version 2 | present, `composition_sha256` differs from the record's bytes | 3, `binding-stale` |
| version 2 | present, a node's `sources` differs from the record's lineage | 1, `proof-invalid` (D2) |
| version 2 | present, all equal | the existing replay of the graph |

The binding comparison compares the version-1 identity fields exactly as
today and `composition_sha256` separately.

### Viewer

`gnd witness-view` and `result_view` accept version 2 and show `sources` as
ids and indexes in every view; they carry no value.

### CLI and API

- `gnd witness ... --composition RECORD`, `gnd replay ... --composition RECORD`.
- `gnd.api.witness(..., composition=)` and `gnd.api.replay(...,
  composition=)` take a record path.
- `--composition` with `--reference-root` is a usage error (64) on both.

### Souffle witness export and why-not (CT-Q3)

Neither reads a witness certificate: `gnd export souffle-witness` and
`gnd why-not` take a model and a population and build their own evidence. So
version 2 needs no handling there (D4). T7 runs each over a composed
population and records that the output equals its output over the same
population bytes without composition (there is no composition option to
pass).

## Decisions

| ID | Question | Readings and cost | Proposal |
|---|---|---|---|
| D1 | Does `gnd witness --composition` re-derive the composition? | (a) no: it checks the record's model and population digests; re-derivation belongs to `gnd check --composition`; (b) yes: needs `--sources` and repeats CT2's whole check | (a) |
| D2 | Exit for edited `sources` | (a) 1 `proof-invalid`: the certificate's content is wrong, as for an edited premise; (b) 3 `binding-stale`: reads as stale inputs, which they are not | (a) |
| D3 | Digest form (CT-Q2) | (a) `composition_sha256` is the raw-byte SHA-256 of the record file, bare hex, like reference `raw_sha256`; the existing `model_digest`/`candidate_digest` keep their canonical form; (b) a canonical digest of the parsed record: equal here because the record is written canonically, but a second form to explain | (a) |
| D4 | Souffle and why-not (CT-Q3) | (a) no change: neither reads a witness; (b) teach them `sources`: no input to read it from | (a) |

## Tests

New file `tests/test_witness_composition.py` unless noted.

| # | Case | Expected |
|---|---|---|
| T1 | Before/after: every committed witness case (`tests/fixtures/public-v71-witness`, the why-not and replay fixtures the existing suites use) produced and replayed at `a2e44f8` and after, digests in `evidence/CT3/parity-*.json` | identical |
| T2 | Schema: a version-2 witness validates; version 2 without `composition_sha256` or a base node without `sources` fails; version 1 with either fails; schema and twin byte-identical (`tests/test_schema_sync.py`) | as stated |
| T3 | End to end: two documents, a rule joining a fact from each (`party_is_based_in_city` from B, `contract_has_party` from A, deriving a contract's city), `gnd witness --composition` | exit 0; the root's base nodes name `contract-a` and `contract-b` source facts; following each to its source sidecar gives a span in that source's document |
| T4 | Replay: unedited (0); `sources` of one base node edited (1); record edited (3 `binding-stale` or `input-invalid`); v2 without `--composition` (3); v1 with `--composition` (3) | as stated |
| T5 | A deduplicated fact (lineage of two sources) as a premise | its base node lists both source facts |
| T6 | `GND_DISCLOSURE=customer`: `gnd witness --composition` and `witness-view` | `sources` present, no value |
| T7 | `gnd export souffle-witness` and `gnd why-not` over the composed population | identical to the same command on the same bytes outside a composition directory |
| T8 | `tests/test_rf1_layering.py`, `tests/test_rf6_query_policy.py`, `tests/test_gnd_arch.py`; anonymity scan | exit 0 |
| T9 | Pins: RF1 help goldens for `witness` and `replay`; signature pins for `api.witness`, `api.replay` | updated and passing |

### Verification selection

```
uv run pytest -q tests/test_witness_composition.py tests/test_composition.py \
  tests/test_schema_sync.py tests/test_public_v71_witness_corpus.py \
  tests/test_public_optional_value_witness.py tests/test_public_replay_admission.py \
  tests/test_public_replay_driver_support.py tests/test_why_not_near_misses_public.py \
  tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py tests/test_disclosure_mode.py \
  tests/test_public_api.py tests/test_v61_phase2_api.py tests/test_rf1_layering.py \
  tests/test_rf6_query_policy.py tests/test_gnd_arch.py tests/test_packaged_skills.py \
  tests/test_skill_prose_sync.py
```

plus every other test file that imports `gnd.witness`, named at
implementation, and T1's table.

## Out of scope for this phase

- Re-deriving a composition inside witness or replay (D1).
- Type proposals (CT4).

## Size

About 140 source lines, 40 schema lines, 350 test lines.
