# Phase RC2: acyclic extent under report version 15

## 1. Status

**Owner-decided (2026-11-06); approval pending on the corpus (§11).** The
owner ruled the step-2 asks over r1 (sha256 `846943be…e8cd`, commit
27258a9e), answering "How do you rule on RC2's decisions D1-D7?" with
"Approve all as proposed" (o, 2026-11-06). D1 is corpus-first, so no
implementation file is created or edited until the owner approves the
corpus. `auto=false`. Prior status (r1): "Draft, awaiting the owner gate
(process-phase step 2)."

## 2. Provenance

- Plan: [rule-check-adoption-plan.md](rule-check-adoption-plan.md) r6,
  sha256 `6f0056b31b8df7eae5c85d6d32eb09395a8240bc137a7300de85bab71639f138`,
  approved at the plan gate ([005-plan.md](../005-plan.md)) with every §10
  proposal, so RC-D3 (one row per in-group edge) and RC-D10 (one shared SCC
  home) are already ruled.
- RC1 record: [006-phase-RC1.md](../006-phase-RC1.md); report version 15
  exists for the plain snapshot arm, and RC1 left the Tarjan copies to RC2.
- Base: main at `c5fe86bb` (RC1 merged as PR 101, then PR 102).

## 3. Obligations (step 0 harvest)

| Source | Obligation | Discharged by |
|---|---|---|
| plan §4 RC2-C1 | two disjoint cycles both appear; a self-loop appears as its own edge; a pair outside every group does not | T1, T2, corpus `two-groups`, `self-loop` |
| plan §4 RC2-C2 | adding a disjoint cycle leaves the existing group's rows byte-identical (today's report fails this) | T3, corpus `add-disjoint` |
| plan §4 RC2-C3 | version 7 output for the same input unchanged; full suite matches the merge-base record | T4, V1/V3 |
| plan §4 RC2-C4 | group computation over the fixture's 2,047 edges under 0.5 s | T7 |
| plan §4 RC2-C5 | the message names group count and sizes (90, 19, 13, 7, 3, 3, 2, 2 on the fixture) | T6, T7 |
| plan §4 RC2-C6 | the existing SCC callers call the shared home and keep no Tarjan of their own (source scan); their tests pass unchanged | T8, V4 |
| plan §2.2 | the checker's verdict is unchanged; the version-15 builder computes the extent through one separate function over the same pairs; no version-7 path reads it | M3-M5, T4, T9 |
| plan §9 RC2 row | RC2 tests + `tests/test_ring_frozen.py tests/test_v6_phase2_ring.py`; full suite; pyrel ring expected.json must not move | V2, V3 |
| plan §9 fixture | 209 components, 2,047 edges, groups 90, 19, 13, 7, 3, 3, 2, 2, rest acyclic; seeded generator (seed 209) committed with RC2's tests | M6 |
| plan §0 rule 2 | group computation linear (Tarjan over the pairs), with a test at the §4 numbers | M1, T7 |
| plan §0 rule 5 | one home for strongly connected groups (RC-D10) | M1, M2, T8 |
| plan §0 rule 6 | row shape measured on the synthetic fixture | T7 (rows and groups on the fixture) |
| plan §0 rule 7 | frozen variants stay frozen | T4, V3 |
| plan §0 rule 8 | stop rule: 1.5 times the estimate | §10 |
| plan §10 RC-D3 | per-edge rows, groups in the message (ruled) | M4 |
| plan §10 RC-D10 | lift one iterative Tarjan into a shared lower-layer home; move every caller (ruled) | M1, M2 |
| plan §6 | "A third SCC copy" risk | M2; finding F1 |
| RC1 record, refactoring review | "the two Tarjan copies (RC2 owns)" | M2 |
| RC1 corpus | `declared-fail` and `text-declared-fail` contain a failing `acyclic` verdict under version 15 | D5 |
| AGENTS.md | new module needs a home in `tools/gnd_layers.json`; moved names stay as identity aliases; guard registries (RF4/RF5 body pins, RF6 read inventory) record changed bodies | M1, M2, V4 |
| project rule (component index) | search `dev/components/` before writing; update it with the code; `components_index.py changed --strict` at record time | §6 reuse table, V6 |

## 4. Standing rules bound to this phase

- **Totality / input cap (rules 1, 2).** The SCC walk is iterative (no
  recursion limit) and linear in nodes plus edges. The pairs it reads are the
  ones `ring_result` already reads, after its existing population caps.
- **Validation order (rule 3).** Unchanged: RC2 adds no flag and no refusal.
- **One walk (rule 4).** The pair extraction is factored out of
  `ring_result` into one function both the checker and the version-15
  builder call (M3), so the two cannot read different pairs.
- **One home (rule 5).** `strongly_connected_components` in a new
  `src/gnd/graphs.py` (M1); every SCC computation in `src/gnd` calls it (M2).
- **Measure (rule 6).** T7 records rows and group sizes on the fixture.
- **Frozen variants (rule 7).** Version 7 messages and rows are produced by
  the unchanged checker; the extent is applied only in the version-15
  projection (M5).

## 5. Goal

Under `gnd check MODEL POP --rule-ids`, a failing `acyclic` verdict lists
every edge that lies inside a strongly connected group, so a fix in one group
cannot move the rows of another, and its message names how many groups there
are and their sizes. Version 7 is unchanged. The repository keeps one
strongly-connected-components implementation.

## 6. Design

**Reuse table** (searched 2026-11-06 at c5fe86bb, `scripts/components_index.py
search` for `strongly connected`, `cycle`, `graph`, and `git grep -n
"Tarjan\|lowlink\|strongly connected"`).

| Capability | Found | Decision |
|---|---|---|
| strongly connected components | three implementations, not the two the plan names (F1): iterative Tarjan `_derivation_cycles` (`src/gnd/model/_validation.py:4497`, no caller, aliased in `gnd.model`); iterative Kosaraju `_derivation_components` (`_validation.py:3633`, used by `derivation_strata` and `_rule_derivation_unstratified`); iterative Tarjan `_strata` (`src/gnd/export/pyrel_rules.py:681`, emission order is the PyRel stratum order). The index has no component for it | **new** shared home, lifted from the `_validation.py` Tarjan (it already uses an on-stack set); all three move onto it |
| the pairs a ring constraint judges | `ring_result` (`src/gnd/semantic_spec.py:1432`) builds them inline from the snapshot relation and `canonical_distinct_rows` | **adapt**: factor out `ring_pairs(constraint, snapshot)`; `ring_result` calls it |
| the acyclic witness | `ring_component_witness` → `ring_cycle_witness` (`semantic_spec.py:1305,1383`), one deterministic cycle | **reuse unchanged** for version 7 |
| snapshot for a model + population | `adapt_snapshot` / `adapt_snapshot_observed` (`src/gnd/semantic_adapter.py:648,800`), `adapt_constraint` (`:379`) | **reuse** |
| ring message | `verbalize.ring_message` (`src/gnd/verbalize.py:440`) | **adapt**: a sibling `ring_extent_message`; `ring_message` unchanged |
| version-15 projection | `build_check_payload(..., declared=...)`, `_rule_ids_verdict` (`src/gnd/payloads.py:374,380`) | **adapt**: an optional `extents` map |
| text under `--rule-ids` | `output._identified_verdict_lines` | **adapt**: prints the version-15 message when an extent exists |
| `_find_cycle`, `_dfs_cycle`, `_ring_component_violations` (`src/gnd/checker/_core.py:1296-1378`) | no production caller; `tests/test_checker_families.py:209` calls `_find_cycle` | **out of scope** (F2, open question) |

**M1. `src/gnd/graphs.py` (new, layer `infrastructure`), ~45 lines.**

```python
def strongly_connected_components(
    nodes: Iterable[N], successors: Mapping[N, Sequence[N]]
) -> list[list[N]]:
    """Every strongly connected component, in Tarjan completion order.

    Iterative. Roots are tried in ``nodes`` order and successors in the
    order given, so the result is deterministic for deterministic inputs.
    Components come out dependencies first (a component is emitted before
    any component that reaches it); members are in stack-pop order.
    Singletons are included; callers filter.
    """
```

Registered in `tools/gnd_layers.json` and in the component index.

**M2. Callers move onto M1, ~15 lines added, ~95 removed.**

- `pyrel_rules._strata`: `[m for c in strongly_connected_components(heads, reads) for m in c]`.
  Its output order must not change (the PyRel stratum order); pinned by the
  pyrel expected files and by T8's equality against the retired body kept as
  a test oracle.
- `_validation._derivation_components`: `tuple(tuple(sorted(c)) for c in ...)`.
  Component order changes from Kosaraju order to Tarjan order. Its two
  callers depend only on membership: `derivation_strata` orders by component
  content, `_rule_derivation_unstratified` maps heads to components. T8
  checks `derivation_strata` and the unstratified issues are unchanged over
  the derivation corpus.
- `_validation._derivation_cycles` (no caller): filtered and sorted on M1;
  the name stays (identity alias in `gnd.model`).

**M3. `src/gnd/semantic_spec.py`, ~25 lines.**

- `ring_pairs(constraint, snapshot) -> list[tuple] | None`: the existing
  pair extraction from `ring_result`, unchanged in behaviour (None where
  `ring_result` returns -1). `ring_result` calls it.
- `acyclic_extent(pairs) -> tuple[list[tuple], list[int]]`: groups by M1
  over the pairs (nodes in first-appearance order of `pairs`, successors in
  pair order); returns the pairs whose two ends share a group, in the
  canonical order `pairs` already has, and the group sizes sorted largest
  first. A group is a component of two or more nodes, or one node with a
  self-loop.

**M4. Version-15 rows and message (RC-D3), ~20 lines in `payloads.py`, ~12
in `verbalize.py`.** For a failing ring verdict whose variant is `acyclic`
or `acyclic-intransitive` (D2):

- `offending_facts`: the acyclic component's single cycle row is replaced by
  one `[a, b]` row per in-group edge, in M3's order; any `intransitive`
  rows of the composite follow unchanged.
- `message`: `ring_extent_message(variant, fact_type, sizes, edges, other)`,
  for example
  `The relation 'uses' is acyclic — violated: 8 strongly connected groups (sizes 90, 19, 13, 7, 3, 3, 2, 2) hold 312 edges.`
  and, with one group,
  `... — violated: 1 strongly connected group (size 2) holds 2 edges.`
  A composite appends the existing `; intransitive broken by (…)` parts.
- Every other key of the verdict, and every other verdict, is as in RC1.

**M5. Wiring, ~20 lines in `checking_service.py`.** Only when the wire
version is 15 and the report has a failing verdict of those variants: adapt
the snapshot and the constraint once (the same adapters the checker uses),
call `ring_pairs` then `acyclic_extent`, and pass
`extents: dict[constraint_ref, (rows, sizes)]` to `build_check_payload`.
At version 7 none of this runs (T9 patches `acyclic_extent` to raise).

**M6. Fixture generator, test side.** `tests/fixtures/rc2-acyclic/generate.py`:
`random.Random(209)`; 209 components; groups of sizes 90, 19, 13, 7, 3, 3,
2, 2 each closed by a ring plus random in-group edges; the remaining 70
components and all cross-group edges follow one topological order, so they
form no cycle; exactly 2,047 distinct edges. The test builds the population
in memory; nothing large is committed.

## 7. Decisions (owner rules at step 2)

| D | Question | Proposal |
|---|---|---|
| D1 | Approval instrument | **corpus-first**: RC2 changes a serialized format (version-15 rows and message), the shape the convergence reference defaults to a corpus **Ruled (o, 2026-11-06): as proposed.** |
| D2 | Does the extent also apply to the `acyclic` part of `acyclic-intransitive`? | **yes**: its acyclic rows would otherwise stay unstable for RC3's baseline. Its intransitive rows are unchanged **Ruled (o, 2026-11-06): as proposed.** |
| D3 | The third SCC implementation (F1) | **move all three** onto M1, so RC2-C6's "keep no Tarjan of their own" holds for every SCC in `src/gnd`, not only the two the plan named **Ruled (o, 2026-11-06): as proposed.** |
| D4 | Home and name | `src/gnd/graphs.py`, `strongly_connected_components`, layer `infrastructure` (it imports nothing from `gnd`) **Ruled (o, 2026-11-06): as proposed.** |
| D5 | RC1's approved goldens `expected/declared-fail.json` and `expected/declared-fail.txt` hold a version-15 acyclic verdict and will change: rows `[[core.base_types, core.identifiers], [core.identifiers, core.base_types]]`, message "1 strongly connected group (size 2) holds 2 edges" | **approve the successor** answers; the old answers stay in git history and the RC2 record cites both digests **Ruled (o, 2026-11-06): as proposed.** |
| D6 | Text output under `--rule-ids` | prints the version-15 message (the extent), so text and JSON agree; without the flag text is unchanged **Ruled (o, 2026-11-06): as proposed.** |
| D7 | Review over the spec bytes | none (as RC1) **Ruled (o, 2026-11-06): as proposed.** |

## 8. Tests and verification ledger

**Direct tests** (`tests/test_rc2_acyclic_extent.py` and the corpus).

| T | Case | Expected |
|---|---|---|
| T1 | two disjoint 2-cycles plus an acyclic edge between them | v15 rows: the four in-group edges, not the bridge; message "2 strongly connected groups (sizes 2, 2) hold 4 edges" |
| T2 | a self-loop `a→a` plus an acyclic chain | one row `[a, a]`; "1 strongly connected group (size 1) holds 1 edge" |
| T3 | T1's population, then the same plus a disjoint 3-cycle | the first group's rows are byte-identical in both reports (a v7 control shows its cycle row can move or not; the v15 assertion is the criterion) |
| T4 | each corpus input without `--rule-ids` | v7 bytes equal the base's (goldens taken at c5fe86bb before any edit) |
| T5 | `acyclic-intransitive` with a cycle and an intransitive triple | in-group edge rows, then the intransitive rows; message has both parts |
| T6 | message grammar: one group, several groups, singular/plural edge | exact strings |
| T7 | the seed-209 fixture | `acyclic_extent` under 0.5 s; sizes `[90, 19, 13, 7, 3, 3, 2, 2]`; 2,047 edges; row count recorded |
| T8 | `strongly_connected_components` against the three retired bodies (kept as oracles in the test) on 200 seeded random graphs and on the derivation corpus | `_strata` order equal; `_derivation_components` equal as sets of sorted tuples; `_derivation_cycles` equal; source scan: no `lowlink`/`low[`/`on_stack` SCC walk left outside `graphs.py` |
| T9 | a v7 check with `acyclic_extent` patched to raise | exit and bytes as without the patch |
| T10 | M1 totality: a 100,000-node chain and a 100,000-node cycle | no recursion error; one component each way as expected |

**Verification-selection ledger.**

| # | Obligation | Disposition | Command or evidence | Invalidation |
|---|---|---|---|---|
| V1 | merge-base record | run before any source edit | focused list below at c5fe86bb; the full suite's base is RC1's main record (`evidence/RC1/full-suite-main-508d6bec.txt`) unless main has moved in tested code | a new base |
| V2 | plan §9 RC2 focused gate | run | `uv run pytest -q tests/test_rc2_acyclic_extent.py tests/test_rc1_rule_ids.py tests/test_ring_frozen.py tests/test_v6_phase2_ring.py --tb=short -p no:cacheprovider` | any edit to M1-M6 or the corpus |
| V3 | plan rule 7 full suite | run, sharded on beast-3 as in RC1, base and final with the same layout | failure set equal to the base's | any source edit after the run |
| V4 | impact closure | run | `uv run pytest -q tests/test_derivation_rule.py tests/test_public_derivation_parity_corpus.py tests/test_public_semantic_boundaries.py tests/test_v62_phase3_validation.py tests/test_pyrel_rules.py tests/test_pyrel_rules_derivations.py tests/test_pyrel_rules_families.py tests/test_pyrel_rules_plans.py tests/test_gnd_arch.py tests/test_rf1_layering.py tests/test_rf3_core.py tests/test_rf4_peripheral.py tests/test_rf5_commands.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_checker_families.py tests/test_report_json.py --tb=short -p no:cacheprovider` | an edit to those surfaces |
| V5 | lint | run | `uv run ruff check <changed Python files>`; whole tree compared with main's 11 | any Python edit |
| V6 | component index | run at record time | `python3 scripts/components_index.py changed --base c5fe86bb --strict` | any edit |
| V7 | broad lanes `-m "evidence or census"` | cadence: not run | milestone close, if the owner selects it | owner request |

## 9. Out of scope for this phase

Baseline (RC3), vacuous acceptance (RC4), population source (RC5), prose
(RC6); version 7 acyclic output; the other ring variants' rows; the unused
`_core` cycle helpers (F2); version 15 for arms RC1 refuses.

## 10. Size

Plan estimate: about 120 source and 280 test lines; rule 8 pauses past 180
source or 420 test lines. This design: about 140 source lines added (M1 45,
M2 15, M3 25, M4 32, M5 20, layer map and index rows) and about 95 removed;
tests about 300 lines plus the corpus. Guard-registry rows (RF4/RF5/RF6
successors) are evidence, as in RC1, and are measured separately.

## 11. Approval instrument

Proposed (D1): **corpus-first**, at `tests/fixtures/rc2-acyclic/`, landing
red before code:

- `README.md`: one story per case, no answers;
- `models/graph.orm.yaml` (one `acyclic` rule with an id and remedy) and
  `models/graph-composite.orm.yaml` (`acyclic-intransitive`);
- `populations/`: `two-groups`, `self-loop`, `add-disjoint` (two-groups plus
  a 3-cycle), `composite`, `clean` (no cycle);
- `expected/`: `<case>.json` (v15) and `<case>.v7.json` (taken from the base
  before any edit, the frozen control), `two-groups.txt` (text under
  `--rule-ids`), `exits.json`;
- `generate.py` (M6), run by the test, not by the corpus.

The owner approves by reading the stories and the goldens, together with
D5's successor answers for RC1's corpus.

## Findings (step 0/1, recorded as found)

- **F1 (refutes plan O17).** There are three SCC implementations, not two:
  the plan's two (one of which, `_derivation_cycles`, has no caller) and a
  Kosaraju `_derivation_components` that `derivation_strata` and the
  unstratified rule use. D3 moves all three.
- **F2.** `checker/_core.py`'s `_find_cycle`, `_dfs_cycle` and
  `_ring_component_violations` are not on the checker's path; the checker
  uses `semantic_spec.ring_result`. They are left alone (out of scope) and
  listed for the record's open questions.
- **F3.** RC1's approved corpus contains a failing acyclic verdict under
  version 15, so RC2 changes approved answers (D5).

## Corpus findings (recorded while authoring the corpus, 2026-11-06)

- **C1 (corrects M4's wording).** Today's composite message does not say
  `intransitive broken by`: the ring message hook passes the variant name
  for every witness, so it reads `acyclic-intransitive broken by (…)` for
  each row. The version-15 composite message keeps that existing wording
  for the non-loop rows and replaces only the cycle part (corpus
  `composite`).
- **C2 (constrains M5).** The version-15 builder cannot tell a composite's
  cycle row from its intransitive rows by shape (a 2-cycle path and a
  triple both have three members). M5 therefore recomputes both parts from
  `ring_pairs` (the loop extent, then the `intransitive` witnesses) rather
  than editing the checker's rows.
- **C3.** With the first disjoint loop tried (`x -> y -> z`), today's
  report kept naming the old loop, so it showed nothing. The corpus uses
  `A -> B -> C`, which sorts first, and today's report then drops the old
  loop entirely; that is the defect RC2-C2 removes.
- **C4.** The generator's graph is checked by the oracle: groups
  `[90, 19, 13, 7, 3, 3, 2, 2]`, 780 of the 2,047 edges inside them. Plain
  `gnd check` over it took 1.24 s wall clock (`/usr/bin/time`), as O21
  measured.
- Red at commit: 9 failing (the four failing `--rule-ids` cases, the text
  case, RC2-C2, RC1's `declared-fail` JSON and text, and RC1's P2, which
  reruns them); the v7 controls and `clean` pass.

## Implementability sweep (step 1, author inspection)

- Every criterion has a case that can fail: C1 (T1, T2), C2 (T3), C3 (T4,
  T9, V3), C4 (T7), C5 (T6, T7), C6 (T8).
- The fixture's numbers are constructible: 209 = 139 in groups + 70 others;
  the minimum in-group edges is 139 (one ring each) and the maximum far
  exceeds 2,047, so the edge count is met with acyclic cross edges filling
  the rest.
- `_strata` order equality is the one risk to an exact move; if any seeded
  graph differs, the move keeps `_strata`'s order by construction (M1 is
  told the same root and successor order), and T8 fails rather than hides it.
- No new dependency, flag, refusal or report version.
