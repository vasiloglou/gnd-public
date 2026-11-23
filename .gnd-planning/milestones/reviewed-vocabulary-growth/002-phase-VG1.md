---
milestone: reviewed-vocabulary-growth
station: "phase-VG1"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-VG1
date: 2026-11-23
gates:
  - command: "uv run pytest -q tests/test_vg1_object_type_scaling.py tests/test_reference_universe.py tests/test_subtype_universe.py tests/test_public_semantic_adapter.py tests/test_tp1_index_scope.py tests/test_ir1_judgments_includes.py tests/test_rf1_semantic_pins.py --tb=short"
    exit: 0
    output: "413 passed in 179.94s (0:02:59)"
    note: "the plan's section 9 VG1 lane with the new file, on the laptop, at 5427e8fe"
  - command: "uv run pytest -q tests/test_vg1_object_type_scaling.py tests/test_reference_universe.py tests/test_subtype_universe.py tests/test_public_semantic_adapter.py tests/test_tp1_index_scope.py tests/test_ir1_judgments_includes.py tests/test_rf1_semantic_pins.py --tb=short -p no:cacheprovider"
    exit: 0
    output: "413 passed in 103.77s (0:01:43)"
    note: "the same lane on beast-3 at 5427e8fe, the machine that ran the base sweep, where T3-T8 are judged"
  - command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
    output: "679 passed, 2 deselected in 140.11s (0:02:20)"
  - command: "uv run ruff check src tests tools"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base 1f403b07 --strict"
    exit: 0
    output: "changed against 1f403b07 (1f403b0): 123 file(s) differ; 0 to fix, 0 warning(s), 1 to reread"
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "explicit owner request, or the milestone-close default lane"
  reason: "the walks' other consumers (checker families, witness, replay, transition, proof bridge) see answers T1 holds equal to the base bodies over every loadable model; T10 holds the report goldens"
evidence:
  - path: src/gnd/model_index.py
    sha256: e1f62e184cffb8f58ef945cbc927a7af5e71d342db8f131248d6835fb8b6e5b7
  - path: src/gnd/universe.py
    sha256: 0a38d9b37787fde7f31504609770d22f5c114ef2e4c31aa713badd8e19c3da59
  - path: src/gnd/semantic_adapter.py
    sha256: 308dc84557cec6b51e90a36254b5a69d51362dacf7303e6fe3b2577b793399cf
  - path: tests/test_vg1_object_type_scaling.py
    sha256: 712b3a6c5736092153c9812fa08c8c219e0b18ca8967605aeeef6d81c3ccd46b
  - path: tests/test_ir1_judgments_includes.py
    sha256: 2fbea7d5421be9acfdd4110e75ea7d85c42987d3aaa6304ebc5c9a61a98c6793
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/notes/phase-VG1-spec.md
    sha256: 752b9a5660e2875beef7751a5ed4aed3d371d62aefdeffb2b806c8b4c35568d8
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviews/phase-VG1-r1/review.md
    sha256: b90f3bcf1f85f927f3653565855986bb7d04abe2b6901ef6d569b78834edff6d
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviews/phase-VG1-r1/FINDINGS.md
    sha256: 8310797d581fcaa23b06fafd2510c26f147861c44292b3d14a8ddad174732773
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/evidence/VG1-sweep/base-sweep.jsonl
    sha256: ee549ec8f91820bcbaf8d6f6ef0ac1811ac8ee26a366fce978b8b3d3d4353385
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/evidence/VG1-sweep/head-sweep.jsonl
    sha256: d3dd2fc85440c2728cd2ece6c6fafb30698024e3dc4bb508b3058b479c2d29df
---

# Claim

At `5427e8fe`, the VG1 lane exited 0 on the laptop and on beast-3 (413
passed each), the guard block exited 0 (679 passed), `uv run ruff check src
tests tools` exited 0 and the component-index check exited 0. On beast-3,
`gnd check` on the interop checking root with 1,000 extra object types took
at most 1.19 s for each of five shapes, against 2.4 s to over 120 s at the
base, with the same exit and verdicts in every row.

## What shipped

- `src/gnd/model_index.py`: four tables on `ModelIndex`, each built once per
  index and returned as a read-only view or a new set:
  `reference_value_types()`, `denoted_by(ids)`, `subtype_children()`,
  `kind(id)`, and the walk `descendants(id)` over the children table. They
  are built from the canonical JSON form of the document, the bytes the
  cache key is a digest of, decoded by `gnd.input_policy.loads` (review r1,
  F1; RF7). A type whose resolution raises resolves to None (review r1, F2).
- `src/gnd/universe.py`: `_descendant_closure`, `_denoting_types` and
  `_kind_of` read those tables. Names, aliases and `__module__` lines are
  unchanged; `resolve_reference_value_type` is unchanged and stays the
  definition (VG1-D2).
- `src/gnd/semantic_adapter.py`: `adapt_snapshot` runs in an index scope
  (`@scoped`, VG1-D4).
- `tests/test_vg1_object_type_scaling.py`: T1-T13 of the spec and the two
  review regressions. `tests/test_ir1_judgments_includes.py`: IR1's
  withdrawn route-level row restored at 20 s (VG1-C5).
- `dev/components/`: the `model.query_index` and `check.universe` entries.
  `semantics.snapshot_adapter` was re-read beside the diff: still accurate,
  since its one change is the scope.

Measured size: 551 lines added and 28 removed under `src` and `tests`
(`git diff --stat 1f403b07 5427e8fe`); source about 160 of them, against an
estimate of about 100. The difference is the canonical copy, the
descendant walk moved into `ModelIndex` and the docstrings.

## Gate output (verbatim)

    $ uv run pytest -q tests/test_vg1_object_type_scaling.py tests/test_reference_universe.py tests/test_subtype_universe.py tests/test_public_semantic_adapter.py tests/test_tp1_index_scope.py tests/test_ir1_judgments_includes.py tests/test_rf1_semantic_pins.py --tb=short
    413 passed in 179.94s (0:02:59)
    (beast-3, same lane, -p no:cacheprovider) 413 passed in 103.77s (0:01:43)
    $ uv run pytest -q <the project.md guard block> --tb=short
    679 passed, 2 deselected in 140.11s (0:02:20)
    $ uv run ruff check src tests tools
    All checks passed!
    $ python3 scripts/components_index.py changed --base 1f403b07 --strict
    reread: semantics.snapshot_adapter (entry not edited): src/gnd/semantic_adapter.py
    changed against 1f403b07 (1f403b0): 123 file(s) differ; 0 to fix, 0 warning(s), 1 to reread

The 123 files include `main` merged into the topic branch at `28ec43c4`
(planning records and three dev-tools scripts).

## The criteria, measured

| Criterion | Measure | Bound | Result |
|---|---|---|---|
| VG1-C1 | T1 over every model that loads under `src/gnd/examples/` and `tests/fixtures/` (407 at `1f403b07`; asserted at least 200), every object type, all four branches seen | equal | exit 0 |
| VG1-C2 | `values`, 1,000: 0.42 s on beast-3; base over 120 s | under 10 s | met |
| VG1-C3 | `entities` 0.58 s, `shared` 0.74 s, `tree` 0.53 s, `both` 1.19 s (base 116.8 s, 2.41 s, 2.41 s, over 120 s) | under 10 s | met |
| VG1-C4 | 2,000 over 1,000 on beast-3: `values` 2.19, `entities` 2.11, `shared` 2.08, `tree` 2.14 (T11 also ran in both lanes) | at most 3 | met |
| VG1-C5 | `gnd judgments check`, `values`, 1,000: 1.01 s (base over 120 s); IR1's row restored | under 20 s | met |
| VG1-C6 | T10: the existing focused files unchanged, no golden changed | exit 0 | met |
| VG1-C7 | supertype-map builds in one `gnd check`: 48 at 300 and 48 at 600 extra value types (base 184,876 at 300, plan H2); negative control 21,677 at 100 | equal, at most 100 | met |
| VG1-C8 | `gnd verify`, `values`, 1,000: base over 120 s, head 0.40 s | over 10 s at the head changes the oracle | at or under: nothing changes (VG1-D5) |

Liveness of the sweep: at `values`, 250, the base took 3.77 s and the head
0.158 s, 23.8 times; the floor was 5. The sweep's rows are in
[`evidence/VG1-sweep/`](evidence/VG1-sweep/README.md). The deep chain (out of
scope, plan D12) still costs 0.80 s at 200, 5.31 s at 400 and 44.6 s at 800
(base 1.28, 9.00, 74.0).

## Review

One reviewer is one reviewer: Codex (default model, effort high, read-only)
through the review helper, round `notes/reviews/phase-VG1-r1/`, over the
diff from `125b91ca` (the spec gate) to the working tree at `1519ecb8`.
Verdict `CHANGES_REQUESTED`, two findings, both reproduced and fixed with a
regression test that failed first (the ledger, `FINDINGS.md`):

- F1, blocking: a str-enum `kind` in a code-built model and the plain
  string share a cache key, so a loaded model could get the other model's
  answer, and a range check read `vacuous` for `fail`. Fixed at `7e235d4a`.
- F2, hardening: a code-built `reference` that is a string made the table
  build raise. Fixed at `7e235d4a`.

The reviewer checked and found true: T1 parity, the T2 cases, T13, all 25
RF1 checker pairs against their goldens on four routes, and a separate
profile counting 7 supertype-map builds at both 300 and 600 on another
fixture. It could not run the interop scaling, judgments or verify
experiments, because their setup writes files. `review.md` and
`review.log` were sanitized of local paths by the helper, which says so at
the top of each.

Audit against the branch table: the four table branches are each asserted
seen by T1 on the fixtures; the cycle, undeclared-supertype,
no-reference, two-supertype and duplicate-id branches are T2's; the
cached-collision branch is R1-F1's; the raising-resolution branch is
R1-F2's.

## Refactoring review

Refactors executed: the descendant walk moved into `ModelIndex.descendants`
(spec finding 1), because shared model queries live there and the
query-policy guard keeps dynamic lookups out of `universe.py`. Behaviour
preserved: T1 and T2 compare it with the frozen base body.

Deferred: the `ModelIndex` cache-key collision itself (open questions).

## Boundary -- what this phase does NOT establish

- One reviewer is one reviewer. The fix commits `7e235d4a` and `5427e8fe`
  carry no review opinion; the round read `1519ecb8`.
- The absolute bounds were judged on one machine, beast-3, and also held on
  the laptop. No CI runner and no other machine ran them.
- The sweep could not measure a real vocabulary whose types are used by
  facts, population size or memory (the spec's experiment, "Cannot
  measure").
- A subtype chain hundreds of types deep is still slow (44.6 s at 800);
  out of scope (plan D12).
- `_instance_values_of` still walks every fact type once per object type;
  T7 bounds it at 1,000 by 1,000 only.
- For a code-built `Model` whose rows `model_dump()` alters, the tables
  answer for the canonical JSON form, not the live rows (VG1-D1, the limit
  accepted on 2026-11-11). A str-enum `kind` is one such row.
- Past the routed reader's 10 MB or 64-level caps the tables read the
  cached rows, so the F1 collision can still reach a model that large.
- `gnd judgments check` still runs the checker twice (plan D10).

## Open questions

- **The `ModelIndex` cache key admits two models with different values.**
  The key is a digest of canonical JSON, while the cached document keeps
  the first model's Python values; every reader other than the VG1 tables
  still reads those. Found by review r1; predates VG1. Target: a
  maintenance pass, the owner to file it (the fix is to key and build the
  shared document from one form).
- VG1-D5 is closed: `gnd verify` measured 0.40 s at 1,000 at the head.
- Plan D12 (the deep chain) and D10 (two checker runs) stay successor
  questions, with the figures above.

## Refuted premises

- The spec's §6 said the tables read "the index's dump of the model". Review
  r1 showed that the cached dump belongs to whichever model reached the
  cache first, not to the model asked about. The tables now read the
  canonical form instead (spec, implementation finding 5).
