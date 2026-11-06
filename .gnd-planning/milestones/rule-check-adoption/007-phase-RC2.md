---
milestone: rule-check-adoption
station: phase-RC2
skill: "n/a -- repository development via process-phase auto=false, not a gnd-solve station over a domain model"
scope: phase-RC2
date: 2026-11-06
gate:
  command: "uv run pytest -q tests/test_rc2_acyclic_extent.py tests/test_rc1_rule_ids.py tests/test_ring_frozen.py tests/test_v6_phase2_ring.py --tb=short -p no:cacheprovider"
  exit: 0
  output: "120 passed"
  note: >-
    The plan section 9 RC2 row (V2), at eecd85ba. The impact closure (V4,
    2091 passed), lint (V5), the component index check (V6) and the sharded
    full default suite against main c5fe86bb (V1/V3, failure lists
    byte-identical) are in the body.
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "explicit owner selection at milestone close (plan section 9)"
  reason: "RC2 changes no historical artifact; the full default suite and the guard suites cover the changed paths"
evidence:
  - path: src/gnd/graphs.py
    sha256: 6156e442912d9d9f4cad21c27d89390dc15d213ba9fd3a1cb4d164309750ab3d
  - path: src/gnd/correspondence.py
    sha256: 845ce008b44f681ce55e6103bc9722beecdb08b6d5955cbeeee17262608f7bfd
  - path: src/gnd/semantic_spec.py
    sha256: 8689218de1c41674af3460e5991673efe14c56c011e5f147ee989ba9463a2ffa
  - path: src/gnd/verbalize.py
    sha256: af95d805250a478292c8d515592c0fd7ddacc382fcdd7818150e3075a630c5ff
  - path: src/gnd/payloads.py
    sha256: 7cb29c57c88f6d2956a536dd0c6ca7ac488b1589806333baa08bb64b488b6d69
  - path: src/gnd/checking_service.py
    sha256: 1561b95d5db81cccda70643c0b275b444a842056ebe5ed8a305bf01e16223edb
  - path: src/gnd/output.py
    sha256: 855cc9494759d2b7bd8d24fdd90562e61404ed6b57a12538a9fdca7ae9b577cf
  - path: src/gnd/commands/checking.py
    sha256: bfdbac45402e107ea77a6635be430fc9d0d0149fabff268375b3054daa17dfb0
  - path: src/gnd/export/pyrel_rules.py
    sha256: 80ade6a743ff43a455c51365619099c44c4305b96b44df8fffcb1aa610bebcda
  - path: src/gnd/model/_validation.py
    sha256: 5ef729120c7bac8fd3f578b7f07b0a1b98fb863eeffb1c596199e92ed921ba17
  - path: tools/gnd_layers.json
    sha256: 2450b49264516177a5148f385ce4b322e0c0de713bccce0f0f22a54507bc60b3
  - path: tests/test_rc2_acyclic_extent.py
    sha256: d0dd527e27be8f3f7fbeb570d77ae861810575955e31d5aebbc90518627297f4
  - path: tests/test_v6_phase2_ring.py
    sha256: b810e06fe1adda35c9ce608b8226519441c05439e36e69d6ec3eb9ad8e2e6498
  - path: tests/fixtures/rc2-acyclic/README.md
    sha256: 42de34e9b61b5398fd7b4b7bf463736393149a8156e81c08e898570044a553e0
  - path: tests/fixtures/rc2-acyclic/generate.py
    sha256: 2812f60c778cfb84d84dee3307652993b80f66d7fc4214859d04e1f1d3bcc723
  - path: tests/fixtures/rc2-acyclic/expected/two-groups.json
    sha256: e86f53971281c22152b894373ca99ee67c4e79fd09147bcf5ffc58f51de7aac2
  - path: tests/fixtures/rc2-acyclic/expected/add-disjoint.json
    sha256: 0f79023831d251fbc5a9a72f2eb9d65c38edead74e4b28d091a322923453cfd1
  - path: tests/fixtures/rc1-rule-ids/expected/declared-fail.json
    sha256: 6376fd9731fd7b92db69a4544efba284e54ebfff700fff3d242ac8e6f4cdffd2
  - path: tests/fixtures/rc1-rule-ids/expected/declared-fail.txt
    sha256: 4796a805d29197a789aed50d4d4c08c610a817036dbd412629050e5dbd84810c
  - path: .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/source-successors.json
    sha256: 4c7e0e9da837ce45e30c663c102da7537ee36c7dd10c99e115348e37fe2edabb
  - path: .gnd-planning/milestones/rule-check-adoption/evidence/RC2/query-successor.json
    sha256: 279ba81395970e7708dbd714241f565d173e4e384fb6d631316421e8c9113424
  - path: .gnd-planning/milestones/rule-check-adoption/evidence/RC2/dynamic-query-successor.json
    sha256: 8a8e1ae3a856a8ffc43feacf3c4067bfb8743b18e793123f246b26b308e94b83
  - path: .gnd-planning/milestones/rule-check-adoption/evidence/RC2/full-suite-main-c5fe86bb.txt
    sha256: fd5e3efc6be2041935e76470e1e1c2e2ea5ce984423f48500302ff899572948a
  - path: .gnd-planning/milestones/rule-check-adoption/evidence/RC2/full-suite-rc2-eecd85ba.txt
    sha256: 239bb2fb903348154ee4e519285501475c496062d3539fb721c0957514175043
  - path: .gnd-planning/milestones/rule-check-adoption/notes/phase-RC2-spec.md
    sha256: 00e3ca46cefe9538861042161db815f07d832918dbe6b223edc75a21ce20965d
  - path: .gnd-planning/milestones/rule-check-adoption/notes/phase-RC2-codex-review.md
    sha256: de1948ab1bf7acb2bda80bc358fe1b00d627bf8cad347c24a55ed19e3888cf51
  - path: dev/components/COMPONENTS.md
    sha256: 8db81f2b76a2761366709abcdc63a0f0a953d9b5e0bb08e781891b12d8a8ae01
---

# Claim

At eecd85ba, `gnd check MODEL POP --rule-ids` lists every edge inside a
strongly connected group for a failing `acyclic` (and the loop part of
`acyclic-intransitive`) rule, with the group count and sizes in its
message, as the owner-approved corpus specifies. Version 7 is unchanged, and
`src/gnd` keeps one strongly-connected-components implementation. The
focused gate V2 exited 0 (120 passed), the impact closure V4 exited 0 (2091
passed), and the sharded full default suite fails exactly the 2 tests main
fails at c5fe86bb. RC2 adds no failure.

## What shipped

- **M1** `src/gnd/graphs.py` (layer `infrastructure`):
  `strongly_connected_components(nodes, successors)`, one iterative Tarjan,
  completion order, singletons included. Component index entry
  `infra.graphs`.
- **M2** the three former SCC walks call it: `pyrel_rules._strata` (same
  stratum order), `model._validation._derivation_components` (a Kosaraju
  walk the plan did not know of; same groups, node set built once) and the
  unused `_derivation_cycles` (same cycles).
- **M3** `semantic_spec.ring_pairs` (the pair extraction moved unchanged out
  of `ring_result`) and `acyclic_extent(pairs)` (groups keyed by NS-IDENT-1
  identity; rows in canonical pair order; sizes largest first).
- **M4** `verbalize.ring_extent_message`; version-15 verdict rows and message
  replaced in `payloads._rule_ids_verdict` from an `extents` map.
- **M5** `correspondence.acyclic_extents`: at wire version 15 only, for asked
  refs that are acyclic ring rules, rebuilds the snapshot the checker judges
  (same derivation view, `evaluation_snapshot` coverage) and projects rows
  through `project_witness`, the projection `project_finding` now also
  calls. `checking_service._run_check_raw` calls it for failing ring
  verdicts.
- **D6** text under `--rule-ids` prints the version-15 message
  (`output._identified_verdict_lines`, map read back from the payload).
- **D5** RC1's corpus answers `expected/declared-fail.json` (was sha256
  `9b783855…cafcfa`) and `expected/declared-fail.txt` (was
  `774ff14c…7c153`) moved to the RC2 form; new digests in the evidence list.
- Guard bookkeeping: RF4 rows `_run_check_raw`, `build_check_payload` and
  RF5 row `_print_report` extended; RF6b rows for the two derivation bodies;
  RC2 static and dynamic query deltas chained.

## Gate output (verbatim)

V1, focused, at the base c5fe86bb before any source edit:

    uv run pytest -q tests/test_rc1_rule_ids.py tests/test_ring_frozen.py tests/test_v6_phase2_ring.py --tb=short -p no:cacheprovider
    94 passed in 7.33s
    exit=0

V2, focused gate (plan §9 row), at eecd85ba:

    uv run pytest -q tests/test_rc2_acyclic_extent.py tests/test_rc1_rule_ids.py tests/test_ring_frozen.py tests/test_v6_phase2_ring.py --tb=short -p no:cacheprovider
    120 passed in 8.74s
    V2 exit=0

V4, impact closure, at eecd85ba:

    uv run pytest -q tests/test_derivation_rule.py tests/test_public_derivation_parity_corpus.py tests/test_public_semantic_boundaries.py tests/test_v62_phase3_validation.py tests/test_pyrel_rules.py tests/test_pyrel_rules_derivations.py tests/test_pyrel_rules_families.py tests/test_pyrel_rules_plans.py tests/test_gnd_arch.py tests/test_rf1_layering.py tests/test_rf3_core.py tests/test_rf4_peripheral.py tests/test_rf5_commands.py tests/test_rf6_query_policy.py tests/test_rf6_packages.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_checker_families.py tests/test_report_json.py tests/test_public_session_driver.py tests/test_public_registry_runtime.py --tb=line -p no:cacheprovider
    2091 passed, 209 deselected in 75.82s (0:01:15)
    V4 exit=0

V5, lint, at eecd85ba:

    uv run ruff check <the Python files changed since c5fe86bb>
    All checks passed!

V6, component index, at eecd85ba:

    python3 scripts/components_index.py changed --base c5fe86bb --strict
    changed against c5fe86bb (c5fe86b): 52 file(s) differ; 0 to fix, 0 warning(s), 8 to reread

Edited with the code: `infra.graphs` (new), and search verbs on
`infra.verdict_prose`, `semantics.snapshot_spec` and `checker.evaluate`.
The 8 reread entries (`subsystem.check`, `cli.checking_command`,
`check.service`, `infra.report_payloads`, `infra.text_output`,
`export.pyrel_rules`, `model.validation`, `check.snapshot_decision`)
were read beside the diff and still describe their code.

V1 (main c5fe86bb) and V3 (eecd85ba), full default lane, sharded on
beast-3, same layout for both (sorted test files dealt round-robin into 6
shards, each in its own clone, after `uv sync --locked --group dev` and
`uv run gnd install --symlink --project --force`, with `~/.local/bin` on
PATH, then `uv run pytest -q --tb=line -p no:cacheprovider <files>`):

    V1 main c5fe86bb: 17603 passed, 2 errors; shards exit 0,0,0,1,0,0
    V3 rc2 eecd85ba:  17629 passed, 2 errors; shards exit 0,0,0,1,0,0
    sorted failing ids: 2 each; comm -13 (only in V3): empty; comm -23: empty
    sha256 of each sorted failing-id list:
      8261732b98e252d1e17e491a8480080bafd2434fbd17f8a503aad8390ea9c20a (both)

The 26 extra passes are RC2's test file. The 2 errors on both sides are
`tests/test_public_optional.py` setup errors, "P2 verified build profile
requires uv 0.10.10": environmental on that host. Per-shard summaries and
failing-id lists: `evidence/RC2/full-suite-*.txt`. With `~/.local/bin` on
PATH, the 116 `uv`-not-found reds RC1's record carried no longer occur.

Two earlier full runs were superseded by fixes (spec findings I6, I7): at
cbcd0e86 three `test_rf6_packages` guard failures (pinned derivation
bodies; `checker/_core.py` past its 2,400-line ceiling) and a
session-driver timeout that did not recur; at b199b851 one
`test_public_registry_runtime` failure (a second `CorrespondedFinding`
construction site). Both guard suites are now in V4.

## Criteria

| Criterion | Evidence | Result |
|---|---|---|
| RC2-C1 | corpus `two-groups`, `self-loop`, `composite` | byte-equal to the oracle-derived answers; schema-valid |
| RC2-C2 | corpus `add-disjoint`; `test_a_disjoint_loop_leaves_the_existing_rows_in_place` | old rows kept, in order (today's report drops them) |
| RC2-C3 | the five `.v7.json` controls; T9; V3 against V1 | byte-identical; the extent never runs at version 7; no new failure |
| RC2-C4 | T7 on the seed-209 fixture | under 0.5 s; sizes 90, 19, 13, 7, 3, 3, 2, 2; 780 rows |
| RC2-C5 | T6, T7, corpus messages | group count and sizes named |
| RC2-C6 | T8 (oracles of the three retired bodies on 200 seeded graphs; source scan), Q4 | same order and groups; no SCC walk outside `graphs.py` |

## Review

One reviewer is one reviewer: Codex (gpt-6-sol, xhigh, read-only), over
`git diff c5fe86bb cbcd0e86 -- src tests tools`, disposition `block`, 4
findings, all reproduced. Q1 blocking (no coverage assertion: the extent
fell back to the single cycle), Q2 and Q3 hardening, Q4 a test gap; Q1-Q3
regressions observed red before their fixes. Retained verbatim with the
triage in [phase-RC2-codex-review.md](notes/phase-RC2-codex-review.md). The
fixes (c7f884cd) and the later full-suite fixes (b199b851, eecd85ba) were not
re-reviewed.

## Refactoring review

Refactors EXECUTED (each behaviour-preserving, behind V2, V4 and V3):
- Three SCC walks to one home, `gnd.graphs` (RC-D10).
- `ring_pairs` out of `ring_result`; `evaluation_snapshot` out of
  `_evaluate_constraint`; `project_witness` out of `project_finding`: each
  so the version-15 extent reads exactly what the checker reads, without a
  second copy.

Seen, deferred: `checker/_core.py`'s `_find_cycle`, `_dfs_cycle` and
`_ring_component_violations` have no production caller (spec F2); the
component index was stale before RC2 (spec I5).

## Boundary: what this phase does NOT establish

- One reviewer read the diff; none of the fixes after it was re-reviewed.
- The extent is computed by re-evaluating derivations and re-adapting the
  snapshot, not by reading the checker's own snapshot. A model whose ring is
  over an exact-term derived fact type, where `_check_dispatch` replaces the
  report after `check_legacy`, has no case; such a ref keeps its version-7
  row if no group is found, but a mismatch between the two views is not
  tested.
- Version 15 still exists only for the plain snapshot arm and plain
  version-7 models; other ring variants keep their rows.
- The full suite's base is c5fe86bb; the broad lanes did not run
  (`slow_cadence`). Two host-environment errors are present on both sides.
- No live caller ran against this build.

## Open questions

- **Size (plan rule 8).** Measured at eecd85ba: source +310/-193 (net +117)
  against the plan's 120-line estimate (pause at 180 added); tests +326/-2
  against 280 (pause at 420); fixtures 24 files, +262. Added source lines
  pass 1.5 times the estimate. Most of it is moving three SCC walks onto one
  home (-150 removed there) and the three extractions the review and guards
  required. Target: owner, before RC3.
- **Unused cycle helpers** in `checker/_core.py` (F2). Target: its own
  issue or the milestone close.
- **Component index drift** (I5): adopt dev-tools' CI check here; upstream
  search limits filed as vasiloglou/dev-tools#1. Target: maintenance.
- **Exact-term derived rings under version 15** (boundary). Target: RC3's
  spec, since its baseline key reads these rows.

## Refuted premises

- Plan O17 said strongly connected components were computed twice; there
  were three implementations (spec F1, probe of `src/gnd` with `git grep`,
  2026-11-06). RC-D10's "one implementation remains" was applied to all three
  (owner ruling D3).
