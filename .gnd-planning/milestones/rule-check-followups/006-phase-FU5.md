---
milestone: rule-check-followups
station: phase-FU5
skill: "n/a -- repository development via process-phase auto=false, not a gnd-solve station over a domain model"
scope: phase-FU5
date: 2026-11-08
gate:
  command: "ls tests/test_rf*.py tests/test_checker_families.py tests/test_fu5_retired_helpers.py | xargs uv run pytest -q -p no:cacheprovider"
  exit: 0
  output: "2540 passed in 176.22s (0:02:56)"
  note: >-
    The plan section 9 FU5 row (V2) plus the new FU5 test file, at e84cd02d.
    The mutants, the component index check (V6), the Codex review (V5) and
    the sharded full default suite against the base failure list (V3) are
    in the body.
evidence:
  - path: src/gnd/checker/_core.py
    sha256: ff83d4b366dae96058a9f50ebc5e5ab035e5bb965bb202cef52190b544cb8b5b
  - path: src/gnd/checker/__init__.py
    sha256: befe4dfbbba4601f57d14df71bf3d696088744f34592923def5c8bb74da8ba42
  - path: tests/support/rf9_ci_sources.py
    sha256: 5728f57c0e3ab3dc48d65eab77caaa4ae9c258b0ae2f5a56c8e667dfdd67db59
  - path: tests/support/pyrel_application_successors.py
    sha256: 0a3cd848a3b0cd35d63eb807231bc0f59a1b5611d4a13853e7eee929dea3815e
  - path: tests/test_fu5_retired_helpers.py
    sha256: c0e4811804c4e086ef95ad067a89ae112d6593beec10b45311e39d51e9e79923
  - path: tests/test_rf6_packages.py
    sha256: 93b5f2301975ad13efe4f3a540ee396a1ec70355296c4fc1ac6a44f7b3a3c6e0
  - path: tests/test_rf9_ci_repairs.py
    sha256: ba0166d44cfd092cf82fe8aa9b891be9b89ee4725c4af7de44a6425207f27ee6
  - path: tests/test_checker_families.py
    sha256: 773f537d64bade634b649a9156665dd57536ec9aef0e0d893b23915f28f9f6b1
  - path: .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/retired-names.json
    sha256: 23e8cf1d6b1c7724f59b7bc4718a534c6cb68c0dc6fea4279de72fdcf4f64942
  - path: .gnd-planning/milestones/rule-check-followups/evidence/FU5/dynamic-query-successor.json
    sha256: 10f1d0e90dff618c9641007ccfbf26d8e21fe5ad7c7b5e6708859d0d56dbbb5d
  - path: .gnd-planning/milestones/rule-check-followups/evidence/FU5/full-suite-e84cd02d.txt
    sha256: c4f5d62769fc83f40c622e7068f53815de51a6144ae54f174b11ba2a4ef17b7a
  - path: .gnd-planning/milestones/rule-check-followups/evidence/FU5/failures-e84cd02d.txt
    sha256: 8a43e5676c270a3a4828ba0d4cd5967fc0f360f2b786a4a3f4894d95f74dc70b
  - path: .gnd-planning/milestones/rule-check-followups/notes/phase-FU5-spec.md
    sha256: 54536b61a576f19755ff7e37b572ab15f36330fed601a565b76dd9d1dddd2d7b
  - path: .gnd-planning/milestones/rule-check-followups/notes/phase-FU5-codex-review.md
    sha256: e79068c0a3eef3eac9dde8a0eb265ce527fa57444b3f04da98bc75797012d1bf
  - path: .gnd-planning/milestones/rule-check-followups/notes/phase-FU5-codex-review-impl.md
    sha256: 667d65a05102ef435b35c2e8a211bf7fab54b48d20c0c907cd73919e6db42f1b
  - path: .gnd-planning/milestones/code-refactoring/notes/shim-inventory.md
    sha256: 209a4c02b568ef9cf20d9a5331b837e5338316977dbbd0bfcdbba0c4303feddc
---

# Claim

At e84cd02d, the three RF6b compatibility helpers that lost their last
production caller in RC2 -- `_find_cycle`, `_dfs_cycle` and
`_ring_component_violations` -- are retired from `gnd.checker` and
`gnd.checker._core` (issue 114), under the owner's D1 r2 ruling "Retire
them now" once RF-D5's release trigger was shown to have occurred
(v0.1.0 contains RF6). Every guard that bound them is told so through an
explicit record, and a listed name that becomes importable again fails
those guards. No frozen historical evidence changed.

## What shipped

- **M1** `src/gnd/checker/_core.py`, `src/gnd/checker/__init__.py`: the three
  bodies, their `__module__` lines and their re-exports are deleted (91
  lines). The `graphlib` import stays; `gnd.checker` re-exports
  `CycleError` and `TopologicalSorter` from it (spec I3).
- **M2** `compiled-snapshot-obligations/evidence/CI/retired-names.json`
  (D2) and `retired_names()` in `tests/support/rf9_ci_sources.py`. The
  reader refuses a duplicate row, a row without issue, phase or ruling, and
  a listed name still bound in its facade or its home. Its consumers:
  the import baseline (`live_baseline` in `tests/test_rf6_packages.py`:
  230 frozen, 227 live, and every retired name must be in the frozen
  baseline), the definition baseline (a retired row must have no
  definition) and `coupling_sites` (retired aliases leave the inventory,
  so a revived one is an uninventoried edge again). The dynamic-query
  census drops 13 rows (15 occurrences) through a new FU5 link in the
  authenticated successor chain (spec I4). After main was merged in, the
  link follows report-output-fidelity ROF3's (result 7306 rows, 9122
  occurrences); V2 on the merged tree: 2540 passed. The V3 full run is at
  e84cd02d, before that merge; the merge brought no change under
  `src/gnd/checker`.
- **M3** `test_find_cycle_helper_names_members` deleted;
  `tests/test_fu5_retired_helpers.py` added (T2, T3);
  `tests/test_rf9_ci_repairs.py` feeds the live alias list and pins the
  revived-alias case.
- The shim inventory rows 755-757 are annotated "retired in
  rule-check-followups FU5" and kept (review R1).

## Gate output (verbatim)

V2, at e84cd02d:

    ls tests/test_rf*.py tests/test_checker_families.py tests/test_fu5_retired_helpers.py | xargs uv run pytest -q -p no:cacheprovider
    2540 passed in 176.22s (0:02:56)

Mutants (the FU5 test file plus test_rf6_packages, test_rf9_ci_repairs,
test_rf6_query_policy, test_rf3_core, test_rf4_peripheral):

    helpers restored (src at 4ff9b0ca):   252 failed, 1050 passed
    _find_cycle dropped from the record:   13 failed, 1289 passed

The first fails every case that reads the record (the reader refuses a
bound retired name) plus the FU5 tests and the dynamic census; the second
fails the import baseline, the `_find_cycle` definition case, the
coupling accounting and its consumers, and the FU5 record tests.

V6, component index:

    python3 scripts/components_index.py changed --base 6ed86d90 --strict
    reread: subsystem.check (entry not edited): its members changed: checker.evaluate
    reread: checker.evaluate (entry not edited): src/gnd/checker/__init__.py, src/gnd/checker/_core.py
    changed against 6ed86d90 (6ed86d9): 14 file(s) differ; 0 to fix, 0 warning(s), 2 to reread
    exit=0

Both reread entries were read beside the diff and stay accurate: neither
names a retired helper, and "historical exports" still describes the
facade. `dev/components/modules/checker.md` was regenerated (line numbers
only).

V3, full default lane, six round-robin shards on beast-3, at e84cd02d:

    17879 passed, 1 failed, 2 errors; shards exit 0,1,0,0,0,0
    failing list: sha256 8a43e5676c270a3a4828ba0d4cd5967fc0f360f2b786a4a3f4894d95f74dc70b
    ERROR tests/test_public_optional.py::test_base_wheel_refuses_missing_synth_extra_and_still_checks
    ERROR tests/test_public_optional.py::test_declared_synth_extra_is_seeded_and_loader_valid
    FAILED tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap

The two errors are the known uv-version pins. The failure is a known red
on the base (spec I5): main 6ed86d90 fails it in a clean worktree,
because the rule-check-release RR1 record links a nonexistent
`../notes/phase-RR1-codex-review.md`; FU5 does not touch that milestone.

## Criteria

| Criterion | Result |
|---|---|
| FU5-C1, per FD5 | all three retired: no test outside the checker family used `_find_cycle` (P3) |
| FU5-C1, name the live guards | spec §5 P4: 15 cases in 6 files; each now subtracts exactly the listed names (T1) |
| FU5-C1, historical baselines byte-identical | no file under `code-refactoring/evidence` or an earlier phase's evidence changed |
| FU5-C1, explicit successor or exemption | `retired-names.json` and the FU5 dynamic-query link |
| FU5-C1, negative test | `tests/test_fu5_retired_helpers.py` |
| predicate 5 | retired, per RF-D5, in this separately approved phase |
| plan §0 rule 5 | stopped at +75 net test-side lines (stop line +60); owner accepted (spec I6) |

## Review

One reviewer is one reviewer: Codex (gpt-6-sol, xhigh, read-only) over
`git diff 4ff9b0ca e84cd02d`, disposition `revise`, one completeness
finding: [phase-FU5-codex-review-impl.md](notes/phase-FU5-codex-review-impl.md).
R1 (shim inventory rows not annotated) was right and is fixed in
d37ada82; the annotation is planning text, not a guard. The reviewer
otherwise found no remaining caller, exact subtraction in each guard, an
exact and authenticated successor link, and no edited historical
evidence. The r1 spec review is separate:
[phase-FU5-codex-review.md](notes/phase-FU5-codex-review.md).

## Refactoring review

None executed. The phase exposed that three guard families (the RF6b
import and definition baselines and the RF9 compatibility private sites)
had no retirement path, while the dynamic and query censuses already had
successor chains. `retired_names()` is that path, in the module that
already holds the source successors, so the next shim retirement under
RF-D5 adds rows instead of plumbing. Nothing else in the touched code
duplicates it.

## Boundary: what this phase does NOT establish

- Only these three names are retired; every other RF6b shim stays, and
  RF-D5 itself is unchanged.
- The reader checks that a retired name is unbound in its facade and its
  home module only; a copy re-exported from some third module would pass
  it (the import-graph guards would still see a new private edge).
- A v0.1.0 user who imported one of the three underscore-private names
  breaks on upgrade; they were documented nowhere public.
- One reviewer read e84cd02d; the R1 repair after it is planning text and
  was not re-reviewed.

## Open questions

- **FU5-O2.** The base known red in
  `tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap`
  (the rule-check-release RR1 record's broken relative link) belongs to the
  rule-check-release milestone; owner: that milestone's next phase.
