---
milestone: composition-and-type-induction
station: "phase-CT2"
skill: "n/a -- repository development under process-milestone auto=true, not a gnd-solve station"
scope: phase-CT2
date: 2026-11-04
gate:
  command: "uv run pytest -q tests/test_composition.py tests/test_anchor_sidecar_v2.py tests/test_public_api.py tests/test_v61_phase2_api.py tests/test_public_runtime.py tests/test_why_not_near_misses_public.py tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py tests/test_conformance_payload.py tests/test_public_built_inventory.py tests/test_v70_phase1_surfaces.py tests/test_v70_phase5_corpus.py tests/test_incremental_sessions.py tests/test_skill_prose_sync.py tests/test_packaged_skills.py"
  exit: 0
  output: "663 passed, 30 deselected in 68.65s"
  note: >-
    The spec's verification selection plus the session signature, skill
    and packaged-skill pins. Run after the review fixes. Docs: strict build
    clean; 13922 links checked; ruff clean on the changed modules. A wider
    sweep before the review (every check, report, public, anchor and API test
    file: 3662 passed) had one failure,
    test_incremental_performance::test_prepared_policy_rechecks_live_hashability,
    which fails identically on main at a2e44f8 and is unrelated.
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "outside CT2's impact closure"
evidence:
  - path: .gnd-planning/milestones/composition-and-type-induction/notes/phase-CT2-spec.md
    sha256: b907ed784078c83f85e1d9ff6b8a4ae546cca65a768f9ef159c03325bd3ca3cd
  - path: .gnd-planning/milestones/composition-and-type-induction/notes/phase-CT2-claude-review.md
    sha256: b52879aa665bf52fa02c8b6d3fe762f57ac7e734b40c24f1fc0e8bd88ed5edb4
  - path: .gnd-planning/milestones/composition-and-type-induction/evidence/CT2/parity-after.json
    sha256: b1ad697616e2d96ac56f14277b419c5fffd4ff5fa7882292a8eaef4e12412a7b
  - path: .gnd-planning/milestones/composition-and-type-induction/evidence/CT2/dynamic-query-successor.json
    sha256: 86f0d766ac1b6a55118a6fb5180da6180140af22bb24a2cf0fd0be59de282296
  - path: src/gnd/composition.py
    sha256: edaa3dc3b803066c79deed4e3d6d7a63de2e6caa3e9edf46a0ee9b41ba931253
  - path: src/gnd/checking_service.py
    sha256: cd824fab543088bd5eab5a83f8789b4d8092320e42c590c62a4683f0344d613f
  - path: src/gnd/checker/_core.py
    sha256: 7b54b96eb45c51c8af7616817130e00747d27ca640bd2eb352dfe53b9aa41ffe
  - path: src/gnd/api.py
    sha256: 7cc84a57f26d4f6fd0bdaf7fc0a6ce6d457475eada51a26e978eb51d69b86477
  - path: src/gnd/commands/checking.py
    sha256: 1317d1caa3e6b8e58e3800c4f9ec57f2fad6bdf5ac7c4f2543049f31c6f742e9
  - path: src/gnd/composition-manifest.schema.json
    sha256: a69af972586c3b4c8c55e48205116a850496477a1eb6bd96a9ecb1a18f0b96cc
  - path: src/gnd/composition.schema.json
    sha256: 13d4525a6439250f5f2d25f8274fee4f299b281de6d464540802cfa43310bdcd
  - path: src/gnd/report.schema.json
    sha256: 980dedef6cd4be94480d551a6a0db9a8a745dd2003debb437cf6f927293a8598
  - path: tests/test_composition.py
    sha256: 97bc0d96d34ce1ec571458fb155214744fa3409c34a0d07f7b5dd209dd472c7e
  - path: docs/reference/composition.md
    sha256: 08fb3681aa863472dad03ea7a2674754cafabd1a2368176bea247cfb6a622e46
  - path: tests/fixtures/rf1-pins/goldens.sha256
    sha256: ac651fe84ca1426f53b79bf4a8f77dd8dae9dd1e80859824bf2cb25d2a61ee60
  - path: tests/fixtures/compiled-snapshot-cli/expected.json
    sha256: d0d52bb57940d10647459bc55e8c59d21afcf8e4a752ccc3eecc2919b0d49ef9
---

# Phase CT2: composition

**Claim.** `gnd compose MODEL DIR --out COMPOSED --record RECORD` and
`gnd.api.compose` build one population from several anchored sources under
a manifest of exact renamings, identical-row deduplication and scope tags,
and write a value-free `gnd-composition/1` record. `gnd check --composition
RECORD --sources DIR` (and `api.check(composition=, sources=)`) checks the
record's digests, composes again and compares every record field and the
composed bytes, then checks exactly the verified bytes, with each anchored
value matched against its own source before renaming; the report's
`composition` block names the source facts of every offending composed
fact. Without the new options, the 33-row CT1 table is identical to
`a2e44f8` except U01, a usage error whose usage line now lists the two new
options (same exit 64 and stdout). The focused gate exits 0.

**Authority.** Plan r3 `(a1)`. Spec r1 under **delegated approval
(auto=true)** `(d1)` 2026-11-04 (digest in the spec); an agent ruling under
the owner's "Yes, run it auto", not the owner's personal reading.

## What changed

- `src/gnd/composition.py` (new, layer `model`): manifest and record
  parsers on the anchor parser's strict JSON reader (`gnd.anchors.strict_json`,
  one helper), `compose`, `verify_composition`, `lineage_index`.
- `src/gnd/checker/_core.py`: `check_with_composed_anchors`, one
  `_anchored_verdicts` run per source (D3).
- `src/gnd/checking_service.py`: the composition view and lineage block.
- `src/gnd/api.py`: `compose`; `composition=` and `sources=` on `check`.
- `src/gnd/commands/checking.py`, `src/gnd/cli.py`: `gnd compose`; the
  two `gnd check` options; lineage lines in text.
- Schemas: `composition-manifest.schema.json`, `composition.schema.json`
  (registered in both inventories); `report.schema.json` gains `composition`.
- Disclosure: `gnd compose` and `api:compose` every-mode rows, table at 49.
- Pins: four `__all__` pins and `run_public_acceptance.py`; the `api.check`
  signature; RF1 goldens for the root help and the three root-usage exit
  probes (py311, py313, py314, by the same text change, checked to reproduce
  the fresh py314 capture), the new `gnd compose` help and exit probe, the
  `gnd check` successor fixture and `tree.json`; `EXPECTED_PARSERS` 58;
  manifest digest; one RF6 dynamic successor (69 added rows).
- Docs: `docs/reference/composition.md` (new, in the nav), `python-api.md`
  (eleven functions), `cli.md`, `disclosure.md`, release note.

## Criteria

| Criterion | Evidence | Result |
|---|---|---|
| CT2-C1 schemas; parsers total | T1, T2 | holds |
| CT2-C2 renamings, dedupe, tags, lineage, determinism, no value in the record | T3, T4, T5, T7, canary test | holds |
| CT2-C3 re-binding, re-derivation, one refusal per step, no value in refusals | T9 (six edits), the per-field verify tests, canary | holds |
| CT2-C4 alethic conflict exit 1 with both sources; deontic exit 0 with a warning | T13 (both modalities) | holds |
| CT2-C5 renamed value passes against its source span; a bad source anchor fails | T15 | holds |
| CT2-C6 50 x 2,000 linear | T6: 100,000 row visits and 100,000 index probes | holds |
| CT2-C7 API, CLI, pins, schemas, disclosure, RF1 | gate | holds |

**Deviations, recorded.** The composed header copies the first source's
`model`, `model_id` and `source` instead of `"source": "composition"`,
because the population schema's `source` enum does not allow it. A record
fact's `renamings` is the union over its source facts (each index names its
source in the manifest); the spec's T4 wording ("on B's entry only") reads
per entry. The `gnd compose` RF1 goldens were captured under py314 only and
committed version-independent, like `gnd check`'s.

## Review

One local reviewer agent, read-only: **approve-with-fixes**, two blocking
findings ([review](notes/phase-CT2-claude-review.md)); 10 of 18 mutants
survived before the fixes.

| Finding | Disposition |
|---|---|
| F1 (blocking) `api.check` verified `population_bytes` but checked the file | fixed: `population_bytes` (and `admission`) refused with `composition`; the checker runs over the verified composed bytes; a row with no lineage fails; `.get` in the block |
| F2 (blocking) renamings skipped instances | fixed: a renaming also rewrites that value among the source's instances of the role's object type; documented; test |
| F3 lineage could name a row of another fact type | fixed: a fact type's own constraint matches its own fact type; value-only offending facts name no lineage, documented |
| F4 a dict record with NaN raised | fixed: exit 3 |
| F5 `--out` equal to `--record`, outputs inside DIR, half-written outputs | fixed: 64 for the first two; both staged before either is renamed |
| F6 a record over its cap could be written | fixed: refused at compose |
| F7 composed `unchecked` drops per-source `fact_refs` | accepted: nit, no consumer |
| F8 `--admission` accepted | fixed: 64 |
| F9 the two deviations | accepted, recorded above |
| F10 row identity spelled in three places; case-insensitive ids on macOS | accepted residual: each spelling matches the checker's own key; ids are documented as path segments |
| F11 surviving mutants | fixed by tests for each record-field comparison, the composed-bytes comparison, a failing second source, deontic warning, vacuous, covers union. Remaining: "unchecked over fail" (no lexical fixture yields unchecked beside a fail) and re-validation of the composed population (redundant with source validation) |

## Refactoring review

`strict_json` is the anchor parser's reader exposed once, not copied. The
composer is one walk; the checker re-derives through the same `compose`.
Per-source anchoring reuses `_anchored_verdicts` unchanged. New module in
the layer map at `model`; no allowance added.

## Questions

| ID | Question | Owner |
|---|---|---|
| CT2-Q1 | `gnd compose` goldens on py311/py313 | the next RF1 recapture (with MG3-Q1) |
| CT2-Q2 | `test_prepared_policy_rechecks_live_hashability` fails on main | maintenance, outside this milestone |

## Boundary

Not merged, released or certified.
