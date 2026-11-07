# Phase RC5: a population source for deterministic tool output

## 1. Status

**r1, 2026-11-06. Draft, awaiting the owner gate (process-phase step 2).**
No implementation file is created or edited before the owner approves this
spec or its corpus (§11). `auto=false`.

## 2. Provenance

- Plan: [rule-check-adoption-plan.md](rule-check-adoption-plan.md) r6,
  sha256 `6f0056b31b8df7eae5c85d6d32eb09395a8240bc137a7300de85bab71639f138`,
  approved with every §10 proposal ([005-plan.md](../005-plan.md)). RC-D8
  is ruled: the value is `tool-output`, with an optional `producer` string
  (1-200 characters, naming tool and revision) allowed only with it.
- Request: issue 97 (GR-D6). RC5 is independent of RC1-RC4 (plan §3).
- Base: main at `14f66ad3` (RC4 merged as PR 108).

## 3. Obligations (step 0 harvest)

| Source | Obligation | Discharged by |
|---|---|---|
| plan §4 RC5-C1 | `tool-output` loads; `producer` (1-200 chars) is a retained `Population` field, passed through both constructors (O27), asserted after loading; empty or 201-character `producer`, or `producer` with another source, refused (exit 3) | corpus cases 1-5; T1 |
| RC5-C2 | the schema is the one normative spelling; a test fails if `population.py` or `extract/projection.py` disagrees | T2 (see D2 for the projection) |
| plan §2.5 / RC-D8 | spelling `tool-output`; avoid `extracted` (collides with `gnd extract`, whose output is `agent-output`) | M1 |
| plan §0 rule 1 | the new field is untrusted header text, bounded by the schema | M1 |
| plan §0 rule 5 | three spellings of the enum today: the schema, `population.py`'s `Literal`, `extract/projection.py`; the schema is normative and the others are pinned to it | M1, T2 |
| plan §5 | the two sync-pinned schemas; the population-format reference; `gnd-extract` keeps writing `agent-output` | M1, M3, D4 |
| plan §7 | `gnd extract` and every skill workflow unchanged | D2 |
| plan §9 RC5 row | RC5 tests + `tests/test_schema_sync.py` + extract projection tests | V2 |
| O27 | `_build_population` and `_combine_validated_populations` both drop header values they do not name | M2 |
| AGENTS.md | guard registries; component index | V4, V6 |

## 4. Standing rules bound to this phase

- **Totality (1).** `producer` is a bounded string in the schema (layer 1),
  checked before any model-relative validation.
- **One home (5).** `population.schema.json` (and its byte-identical skill
  copy, pinned by `tests/test_schema_sync.py`) is the normative enum.
  `Population.source`'s `Literal` is pinned to it by test (T2).
- **Frozen variants (7).** No report changes: `source` and `producer` appear
  in no check payload.

## 5. Goal

A population written by a deterministic program says so:
`source: tool-output`, optionally with `producer: "<tool> <revision>"`. It
loads and checks exactly like any other population.

## 6. Design

**Reuse table** (searched 2026-11-06 at `14f66ad3`: `components_index.py
search population source`, `git grep agent-output`).

| Capability | Found | Decision |
|---|---|---|
| the source enum | schema `population.schema.json:18` (+ skill copy); `Population.source: Literal[...]` (`population.py:131`); `extract/projection.py:278` | **adapt** schema and `Literal`; projection per D2 |
| header → `Population` | `_build_population` (`population.py:453`), `_combine_validated_populations` (`:485`) | **adapt**: pass `producer` |
| content digest | `_content_digest` over the population's content | **reuse**: `producer` is content |
| reference text | `skills/gnd-orm-core/references/population-format.md` lines 22, 45 | **adapt** (D4) |

**M1. Schema (+ sync-pinned copy), ~6 lines.** In `population.properties`:
`"source": { "enum": ["agent-output", "synthetic", "fixture", "tool-output"] }`
and `"producer": { "type": "string", "minLength": 1, "maxLength": 200 }`;
on the `population` object, `"dependentSchemas": { "producer": { "properties":
{ "source": { "const": "tool-output" } } } }`, so `producer` with another
source fails layer 1 (`jsonschema:*`, exit 3).

**M2. `population.py`, ~10 lines.** `source` gains `"tool-output"`;
`producer: str | None = None`; a model validator refuses `producer` without
`source == "tool-output"` for direct construction; both constructors pass
`header.get("producer")`.

**M3. Reference text (D4), ~6 lines.** `population-format.md`: the enum line,
the `source` description, and a `producer` entry.

## 7. Decisions (owner rules at step 2)

| D | Question | Proposal |
|---|---|---|
| D1 | Approval instrument | **corpus-first**, small: a validation predicate is one of the three shapes the convergence reference defaults to a corpus |
| D2 | `extract/projection.py`'s enum | **keep its three values** and pin them by test as a subset of the schema's: it is the structured-output schema handed to an extraction agent, whose output is always `agent-output`, and its bytes are hashed into recorded `projection_sha256` values (fidelity reports and the examples' recordings), which a fourth value would move (F1). The plan's "disagrees" is read as "names a value the schema does not have" |
| D3 | Where the "only with `tool-output`" rule lives | the schema (`dependentSchemas`, so the loader refuses it at layer 1), plus a model validator for direct construction |
| D4 | Reference documentation in this phase | the population-format reference only (it describes the enum the sync-pinned schema copy changes); broader documentation stays RC6's |
| D5 | Review over the spec bytes | none |

## 8. Tests and verification ledger

**Corpus** (`tests/fixtures/rc5-tool-output/`, §11) and `tests/test_rc5_tool_output.py`:

| T | Case | Expected |
|---|---|---|
| T1 | load each accepted corpus case | `source`, `producer` retained on `Population`; a check of it exits as the same facts with `source: fixture` |
| T2 | the schema enum vs `Population.source`'s `Literal` (equal) and vs the projection's enum (a subset) | pinned both ways; a test-local fourth value in either fails |
| T3 | the combined-population route (`_combine_validated_populations`) | `producer` survives |
| T4 | `Population(source="fixture", producer="x")` | refused |

**Verification-selection ledger.**

| # | Obligation | Disposition | Command or evidence | Invalidation |
|---|---|---|---|---|
| V1 | merge-base record | run before any source edit | V2's existing files at `14f66ad3`; full-suite base from RC4's record (main 4713fc8a) unless main moved in tested code | a new base |
| V2 | plan §9 RC5 row | run | `uv run pytest -q tests/test_rc5_tool_output.py tests/test_schema_sync.py tests/test_extract_projection.py tests/test_population_load.py --tb=short -p no:cacheprovider` | any RC5 edit |
| V3 | full suite vs base | run, sharded on beast-3 as before | failure set equal to the base's | any source edit after the run |
| V4 | impact closure | run | every test file that names `population.schema`, `Population(` or `source:` in a population header, plus the guard suites (RF4-RF8, `test_rf6_packages`, `test_public_registry_runtime`) | edits to those surfaces |
| V5 | lint | run | changed Python files clean | any Python edit |
| V6 | component index | run at record time | `components_index.py changed --base 14f66ad3 --strict` | any edit |
| V7 | broad lanes | cadence: not run | milestone close if selected | owner request |

## 9. Out of scope for this phase

Changing `gnd extract`, its projection, or any skill workflow; showing the
source or producer in reports; structured producer metadata (a free string
was ruled, RC-D8); documentation beyond the population-format reference
(RC6).

## 10. Size

Plan estimate: about 30 source and 80 test lines; rule 8 pauses past 45
source or 120 test lines. This design: about 16 source lines plus about 12
schema lines (two copies) and about 6 reference lines; about 90 test lines.

## 11. Approval instrument

Proposed (D1): **corpus-first** at `tests/fixtures/rc5-tool-output/`, landing
red before code. One small model; populations with a README story each and
an expected exit and issue rule id:

1. `tool-output`: `source: tool-output`, no producer → loads; check exits as
   the facts dictate;
2. `tool-output-producer`: with `producer: "components-scan 1.4.0 @ 9f3c2a1"`
   → loads, producer retained;
3. `producer-on-fixture`: `source: fixture` with a producer → exit 3;
4. `producer-empty`: `producer: ""` → exit 3;
5. `producer-too-long`: 201 characters → exit 3;
6. `producer-200`: exactly 200 characters → loads.

## Findings (step 0/1, recorded as found)

- **F1 (refines RC5-C2).** The extraction projection's bytes are hashed
  (`projection_sha256` in `fidelity.schema.json` and in the recorded
  examples' feedback files), so adding a value there moves recorded
  digests; and the projection is only ever handed to an extraction agent,
  whose source is fixed at `agent-output` (`gnd-extract`'s contract). D2
  keeps it a pinned subset.
- **F2.** `_combine_validated_populations` already drops `label` today;
  RC5 passes `producer` through and leaves `label` as it is (out of scope,
  recorded).

## Implementability sweep (step 1, author inspection)

- Every criterion has a case that can fail (§3, §8).
- `dependentSchemas` is Draft 2020-12, the dialect the loader validates
  with.
- No report, payload or CLI change; no new dependency.
