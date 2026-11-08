# Phase FU3: derived-ring extent (issue 119)

## 1. Status

**Approved (2026-11-07); implemented (test-only).** The owner approved the
corpus (commit 11aef429) with "Approve, finish FU3", answering "Do you
approve the FU3 corpus answers?". Prior status: "Owner-decided; approval
pending on the corpus." D1-D3 were
ruled over r1 (sha256 `313122c4…`, commit c29bb33d) with "Approve as
proposed". `auto=false`. Prior status: "Draft r1, awaiting the owner gate."

## 2. Provenance

- Plan r3 §4 FU3 (FU3-C1, FU3-C2), §2, §9 row FU3; completion predicate 3.
- Issue 119; rule-check-adoption close review K1
  ([012-milestone-close.md](../../rule-check-adoption/012-milestone-close.md),
  predicate 2 and the sweep row "Exact-term derived rings under version 15");
  RC2 record boundary
  ([007-phase-RC2.md](../../rule-check-adoption/007-phase-RC2.md)).
- Base: main `1e63aeb5` (FU2 merged).

## 3. Obligations (step 0 harvest)

| Source | Obligation | Discharged by |
|---|---|---|
| FU3-C1 | a corpus model with an `acyclic` ring over an exact-term derived fact type, failing; `--rule-ids` rows equal the checker's judged pairs in strongly connected groups | T1, T2, T3 |
| FU3-C2 | a disjoint added cycle leaves existing rows unchanged on this route | T4 |
| plan §2 FU3 | if the extent and the checker disagree, the extent is fixed to read the checker's pairs | M1, only if T1-T5 find a disagreement |
| RC2 boundary | a ref with no group keeps its version-7 row; a mismatch between the two views has no case | T3 (derived-only cycle), T5 (term unavailable) |
| plan §0 rule 1 | no report's bytes change | T6 (version 7 unchanged), V3 |
| plan §0 rule 2 | measure before planning | §5 probes |
| plan §0 rule 4 | a fix lands in `correspondence.acyclic_extents` | M1 |
| plan §0 rule 5 | pause past 1.5 times the estimate | §10, stated at each gate |
| §9 row | new FU3 tests + `tests/test_rc2_acyclic_extent.py`; consumers: version 15 | V2 |
| §7 | GR-D4, GR-T17, new report versions, version-7 bytes | §9 |
| AGENTS.md | component index | V6 |

## 4. Goal

Under `gnd check --rule-ids`, a failing `acyclic` ring over a fact type
derived through an exact term lists exactly the in-group edges of the pairs
the checker judged, and a ring the checker did not fail gets no extent.

## 5. Probes (2026-11-07, `1e63aeb5`, scratch model)

Model: value type `node` (Integer); asserted `hop(from, a, b)`; derived
`leads(from, to)` with head `to: { fn: mod, args: [$a, $b] }` (so
`model_uses_exact_derivations` is true and `_check_dispatch` post-processes);
`acyclic` ring `no_loops` on `leads`. The hops derive `1->2, 2->1, 3->4,
4->3, 2->3, 5->1`.

| Population (`leads` asserted) | v7 verdict | v15 rows | derivation |
|---|---|---|---|
| none, `leads` not covered | vacuous | none | not covered |
| equal to the derived six | fail, cycle `1->2->1` | `[1,2],[2,1],[3,4],[4,3]`, "2 groups (sizes 2, 2) hold 4 edges" | pass |
| only `3->4, 4->3` | fail, `3->4->3` | `[3,4],[4,3]` | fail, incomplete |
| the six plus `7->8, 8->7` | fail, `1->2->1` | the four plus `[7,8],[8,7]` | fail, unsound |
| `1->2, 2->3` (cycle only in the derived set) | pass | none | fail, incomplete |
| `1->2, 3->4, 2->3, 5->1, 7->8, 8->7` (cycle only in the asserted set) | fail, `7->8->7` | `[7,8],[8,7]` | fail, incomplete and unsound |
| a hop with `b: 0`, `leads` `1->2, 2->1` | unchecked, `term:mod-zero` | none (only failing refs get an extent, `checking_service.py:526-533`) | unchecked, `term:mod-zero` |

**Finding P1.** In every probe the checker and the extent read the same
pairs: the asserted `leads` facts. A mismatch between the asserted and the
derived set is reported separately, as a failing derivation. No
disagreement was found, so M1 is expected to be empty; the corpus pins the
agreement.

**Finding P2 (refuted premise).** Plan §3 says FU3 reuses FU1's
exact-terms fixtures. `fu1-term-reasons/models/terms.orm.yaml` has no
binary fact type over one object type, so it cannot carry a ring. FU3
needs its own model (about 35 lines). Open-questions row FU3-O1 records it
for the close.

## 6. Design

**Reuse table** (searched 2026-11-07 at `1e63aeb5`:
`components_index.py search "acyclic extent strongly connected"`).

| Capability | Found | Decision |
|---|---|---|
| extent rows | `gnd.semantic_spec.acyclic_extent`, `correspondence.acyclic_extents` | **reuse**, unchanged unless T1-T5 disagree |
| an independent oracle | `gnd.graphs.strongly_connected_components` (`infra.graphs`) | **reuse** in T2, as `test_rc2_acyclic_extent.py` does |
| corpus shape | `tests/fixtures/rc2-acyclic` (README, models, populations, expected bytes and `exits.json`) | **reuse** the shape |
| a model with exact terms | `fu1-term-reasons/models/terms.orm.yaml` | **reject** (P2) |

**Corpus** `tests/fixtures/fu3-derived-ring/`: `README.md` (each case's
story), `models/ring.orm.yaml` (the probe model), and one population per
case: `agree`, `add-disjoint`, `asserted-only`, `derived-only`,
`mod-zero`. `expected/` holds each case's version-15 and version-7 JSON
bytes and `exits.json`, recorded at `1e63aeb5` before any source change,
run with the corpus as the working directory as RC2's are.

**M1 (conditional, about 0-40 lines).** Only if a corpus case shows the
extent's rows differ from the checker's pairs: `acyclic_extents` reads the
checker's own pairs for that ref. A disagreement found while authoring the
corpus is recorded in §11 and brought back to the owner before code.

## 7. Decisions (owner rules at step 2)

| D | Question | Proposal |
|---|---|---|
| D1 | Approval instrument | **corpus-first** (a serialized report and its exit codes): the five cases, their README stories, and the expected bytes; it lands green if P1 holds, red cases only where it does not **Ruled (o, 2026-11-07): as proposed** ("Approve as proposed", answering "How do you rule on FU3's D1–D3?"). |
| D2 | What "the checker's judged pairs" means for a derived ring | **the asserted facts of the derived fact type**, as the checker judges them today (P1); a gap between asserted and derived facts stays the derivation's finding, not the ring's. The alternative, judging the ring over the derived set, changes version-7 verdicts (rule 1) and is out of scope **Ruled (o, 2026-11-07): as proposed** ("Approve as proposed", answering "How do you rule on FU3's D1–D3?"). |
| D3 | Review over the spec bytes | none **Ruled (o, 2026-11-07): as proposed** ("Approve as proposed", answering "How do you rule on FU3's D1–D3?"). |

## 8. Tests and verification ledger

| T | Case | Expected |
|---|---|---|
| T1 | each case under `--rule-ids --format json` | exit and bytes equal `expected/<case>.json`; the report validates against `report.schema.json` |
| T2 | `agree`, `asserted-only`, and `add-disjoint` | the rows equal the edges of the asserted `leads` facts that lie in a strongly connected group, computed by `strongly_connected_components`; the version-7 cycle's edges are among them |
| T3 | `derived-only` | the ring passes; no extent; version-15 verdict equals version 7's except the added fields |
| T4 | `add-disjoint` (`agree` plus `20->21, 21->20`, asserted and derived) | `agree`'s rows appear unchanged and in order; the two new edges are added (FU3-C2) |
| T5 | `mod-zero` | unchecked with `term:mod-zero` on both versions; no extent |
| T6 | each case without `--rule-ids` | bytes equal `expected/<case>.v7.json` |

Mutant: T2 and T4 are shown to fail against `acyclic_extents` patched to
read the derived extension instead of the asserted facts (the disagreement
the issue asks about); recorded in the record.

| # | Obligation | Disposition | Command or evidence |
|---|---|---|---|
| V2 | plan §9 FU3 row | run | `uv run pytest -q tests/test_fu3_*.py tests/test_rc2_acyclic_extent.py` |
| V3 | full suite vs base | run, sharded on beast-3, only if M1 changes source | failure set equal to the base's (sha256 `8261732b…`) |
| V5 | Codex review of the diff | run | `notes/phase-FU3-codex-review.md` |
| V6 | component index | run at record time | `components_index.py changed --base 1e63aeb5 --strict` |

## 9. Out of scope

`--baseline` with structured derivations (refused, RC-D11); other ring
variants' extents; GR-D4, GR-T17; any new report version; issue 117 (FU4)
and 114 (FU5).

## 10. Size

Plan estimate: 0-40 source and 100 test lines. Stop lines (rule 5): 60
source, 150 test lines (the test module; the corpus files are counted
separately and reported).

## Implementability sweep (author inspection)

- Every T case was run as a probe (§5) except `add-disjoint`, whose
  behaviour is RC2-C2's on asserted rings.
- T2's oracle uses no code under test.
- If P1 holds, the phase is test-only and V3 is not needed; the RC2 focused
  file still runs (V2).

## 11. Corpus and implementation findings

Recorded while authoring the corpus (2026-11-07, `1e63aeb5`).

- **C1 (P1 confirmed in source).** `extensions.constraint_view_legacy`
  (`extensions.py:2573-2610`) gives a constraint the asserted facts of a
  derived fact type the population covers, the extension only for a
  `semiderived` one, and nothing for an uncovered derived one. The checker
  and `acyclic_extents` both build their view through it, so they read the
  same pairs. M1 is empty; the phase is test-only.
- **C2.** The answers were recorded from the reports at `1e63aeb5`, not
  from an implementation. All 17 FU3 cases and the 26 RC2 cases pass
  (`uv run pytest -q tests/test_fu3_derived_ring.py
  tests/test_rc2_acyclic_extent.py`: 43 passed). The corpus lands green, as
  D1 allows when P1 holds.
- **C3 (mutant; the spec's prediction was partly wrong).** Patching
  `acyclic_extents` to read the derived extension
  (`effective_facts={**view.facts, **_relation_facts(extensions)}`) turns 2
  cases red: T1 and T2 on `asserted-only`. The spec predicted T2 and T4. T4
  cannot catch this mutant, because in `agree` and `add-disjoint` the
  stated and derived edges are equal by construction; `derived-only` cannot
  either, because the checker passes it and no extent is computed. The
  mutant is caught by `asserted-only` alone. No approved answer changed.
- **C4 (size).** The test module is 115 lines (stop line 150); source 0.
  The corpus is 5 populations (73 lines), one model (33), two READMEs and
  the answer key.
