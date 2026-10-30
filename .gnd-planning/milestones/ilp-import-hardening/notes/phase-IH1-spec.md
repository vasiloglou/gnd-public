# IH1: one counting entry for the mined import

**Status:** r1 draft, awaiting this phase's owner gate. `auto=false`. Nothing
below is approved. The plan (r2) is approved ([plan gate](../001-plan-gate.md));
its IH1 rows IH1-D1 (a) and IH1-D2 (a) are ruled (o).

## Provenance

- Plan: `ilp-import-hardening-plan.md` r2, the IH1 predicate, §0 (IH-R2,
  IH-R4), §2 "The counting entry", §4 "IH1", §5, §6, §9 IH1 row, §10.
- IH0's record, `../002-phase-IH0.md`, and its triage: findings E, F and J
  are assigned to IH1 (IH0-D3 (o)); three suspicions name IH1.

## Obligations

| Obligation | Source | Discharged in |
|---|---|---|
| Public `count_mined_rules`, called by the import and `hold()`; raises only mapping refusals and `too-large` | plan §4 IH1, §2 | Design 1, 3, 4; T1, T3 |
| No module outside `ilp_service` imports `_mined_inputs` (finding E) | plan §4 IH1; IH0 triage E | Design 4; T1 |
| One import builds `relation_table` and `pairs` once each (IL-close-Q1) | plan §4 IH1 | Design 2; T2 |
| `ilp_amie.provenance`, from the counted pairs; no `ilp_amie` → `gnd.discover` edge (IL4-Q3 remainder) | plan §2, §4 IH1 | Design 5; T6 |
| `facts-mismatch` precedes every mapping refusal; pin red against a mutant | plan §2; IH1-D1 (o) | Design 3; T4 |
| Refusal order pinned against the docs, red against a swapped tuple | IH-R4 | T5 |
| IH-R2: goldens, replays, comparison golden byte-identical; AMIE `adapter_version` 2 | IH-R2; plan §4 IH1 | T8 |
| `hold()`'s error order through the entry | IH1-D2 (o) | Design 4; T7 |
| `population-mismatch` before the population loads (finding F) | IH0 triage F | IH1-D5; T9 |
| `ilp_amie.EXPORT_REFUSALS` names `opaque` and `too-large` (finding J) | IH0 triage J | Design 6; T10 |
| `_mined_inputs` kept as an identity alias; every importer listed | plan §2 "Names" | Design 1 |
| RF6 census successor regenerated; RF6, layer and arch tests exit 0 | plan §4 IH1 | T11 |
| Suspicions IH0 named for IH1: "invalid model" without a rule index; the mined learner check ignores the tuple form | IH0 triage | Out of scope, carried |

## Standing rules, bound to this phase

- **IK-R1 to IK-R12, IL-R1 to IL-R11:** bind unchanged. IL-R7: any change
  that moves a wire, a golden or an adapter version returns to the gate.
- **IH-R1:** no learner, solver or model runs; the retained AMIE outputs are
  the evidence.
- **IH-R2:** binds every design item. The two exceptions are named error-path
  changes put to the owner: IH1-D4 and IH1-D5.
- **IH-R4:** T5 is the pin. IH1 adds no refusal name.
- **RF and AGENTS.md:**
  - `tools/gnd_layers.json` needs no new home;
  - the allowance count stays 0;
  - the RF6 dynamic census gets an IH1 successor, chained after IH0's;
  - `_mined_inputs` stays as an identity alias.

## Goal

`gnd import mined-rules` and `tools/ilp_comparison.hold()` count mined rules
through one public entry. An admitting import builds the relation table and
the spelled pairs once. Every committed golden, replay and the comparison
golden stay byte-identical.

## Design

1. **Public names in `gnd.export.ilp_service`**, added to `__all__`:
   ```python
   @dataclass(frozen=True)
   class MinedInputs: ...            # today's _Mined, fields unchanged
   _Mined = MinedInputs              # identity alias

   @dataclass(frozen=True)
   class MinedTables:
       relations: dict[str, Relation]
       uncovered: dict[str, Relation]
       skipped: list[dict[str, str]]
       facts: dict[str, list[tuple[str, str]]]   # the one spelled-pairs table

   @dataclass(frozen=True)
   class MinedCount:
       tables: MinedTables
       rules: tuple[MinedRule, ...]
       counts: tuple[Counts, ...]

   def load_mined_inputs(model_path, population_path, *,
                         population_sha256: str | None = None) -> MinedInputs: ...
   _mined_inputs = load_mined_inputs  # identity alias
   def mined_tables(inputs: MinedInputs) -> MinedTables: ...
   def count_mined_rules(inputs: MinedInputs, parsed: list[dict[str, Any]], *,
                         tables: MinedTables | None = None) -> MinedCount: ...
   ```
   **Importers today:** `_mined_inputs` is used only by `ilp_service` itself
   (the export and the import) and by `tools/ilp_comparison.hold()`. No test
   or retained evidence script imports it. That was measured with `grep -rn`
   over `src`, `tools`, `tests` and `.gnd-planning`.
2. **Build once (IH1-D3).** The plan's signature
   `count_mined_rules(inputs, parsed)` builds the tables itself. The import
   must also render the facts digest before mapping (IH1-D1 (o)), and today's
   `ilp_amie.render` builds the same tables again. So with that signature the
   import would still build them twice: the plan's §2 and its build-once
   criterion cannot both hold. Proposed:
   - `ilp_amie.render` is split, so the import renders `amie/facts.tsv` from
     tables it already holds: `render_tables(relations, skipped, facts,
     population_sha256)`. `render` stays as `render_tables` over
     `relation_table` and `pairs`, with the same bytes and refusals.
   - The import builds `mined_tables(inputs)` once, renders and compares the
     digest, then passes the tables to `count_mined_rules`.
   - `hold()` passes no tables, so the entry builds them.
3. **The import's order,** with IH1-D1 (a) (o):
   - reader;
   - learner, then rules;
   - the model loads;
   - `population-mismatch` (IH1-D5);
   - the population loads;
   - the tables are built, then `facts-mismatch`;
   - `count_mined_rules`: every rule's mapping in `MAPPING_REFUSALS` order,
     then every rule's count, refusing `too-large`;
   - the admission checks over the counts: `covers-nothing`, then
     `support-mismatch` per rule, then `does-not-hold` over all;
   - then provenance, validation, the checker and the proposal, as today.
   A failure to build the tables, before the digest, is reported as
   `facts-mismatch` with the same text as today.
4. **`hold()`:**
   - it calls `load_mined_inputs` and `count_mined_rules`;
   - it counts `numerator == denominator > 0`;
   - it names a refusal with `ilp.refusal_name`, not `_REFUSAL`;
   - `tools/` no longer names `_mined_inputs`.
   Under IH1-D2 (a) (o), every mapping refusal now precedes any `too-large`.
5. **`ilp_amie.provenance(head_pairs, satisfied, fact_id, fact_type)`:**
   - it returns each satisfied pair's first row's fact id, in satisfied order;
   - `head_pairs` is `tables.facts[head relation]`, the counted pairs in
     population row order, so there is no second `spell` pass;
   - `fact_id` is the import's `PopulationView.fact_id`, passed in, so
     `ilp_amie` imports nothing from `gnd.discover`.
6. **`EXPORT_REFUSALS`** becomes `("no-relations", "unrepresentable",
   "opaque", "too-large")`. The AMIE section of `docs/reference/ilp-bridge.md`
   names the two added refusals, so IL's `test_c8c` pin covers them.

## Decisions

| ID | Question | Readings and cost | Proposed |
|---|---|---|---|
| IH1-D3 | The plan's signature cannot meet its build-once criterion (Design 2) | **(a)** split `render`, with an optional `tables` argument on the entry, as Design 2. **(b)** the entry renders and returns the digest; that is IH1-D1 (b), already ruled out. **(c)** drop the build-once criterion; IL-close-Q1 stays open | (a) |
| IH1-D4 | Through the entry, a later rule's `too-large` now precedes an earlier rule's `covers-nothing` or `support-mismatch`. Today the checks interleave rule by rule | **(a)** accept. Only the message changes: the exit stays 3, admission is all-or-nothing, and the docs' counting prose already lists `too-large` first. **(b)** the entry stops at the first rule that refuses and returns partial counts; that keeps today's order, but `hold()` needs every count | (a) |
| IH1-D5 | Finding F: check `population-mismatch` before loading the population | **(a)** fix in IH1. `load_mined_inputs` takes the bound digest and compares the bytes before parsing. One error path changes: an unloadable population that is not the bound one exits 3, not 5. No golden moves. **(b)** carry it, so IH1 stays strictly byte- and exit-preserving | (a) |

## Tests

New file `tests/test_ih1_counting.py`. "Red first" means red at IH0's head, recorded in `evidence/IH1/red.txt`.

| Test | Expected |
|---|---|
| T1 the public names exist; `_mined_inputs is load_mined_inputs`; no file under `tools/` names `_mined_inputs` | red first, then exit 0 |
| T2 an admitting import of the committed `amie-2` run calls `relation_table` once and `pairs` once, counted by wrapping both | red first (2 and 2), then exit 0 |
| T3 `count_mined_rules` over AMIE invocation 1's 8 rules returns 8 counts, 6 of them not holding, and raises nothing | red first, then exit 0 |
| T4 a run record with a wrong `facts_sha256` and an unmappable rule is refused `facts-mismatch` | exit 0 at IH0's head and after; red against a mutant copy with the digest moved after the entry (`evidence/IH1/mutant.txt`) |
| T5 `MAPPING_REFUSALS` equals the order of the mapping table's rows, and `COUNT_REFUSALS` the counting prose's order, in the AMIE section of `docs/reference/ilp-bridge.md` | exit 0; red with either tuple swapped by monkeypatch (recorded) |
| T6 `ilp_amie.provenance` exists; an AST scan finds no `gnd.discover` import in `ilp_amie` | red first, then exit 0 |
| T7 `hold()` over rule 0 `too-large` and rule 1 unmappable names rule 1's mapping refusal (IH1-D2 (o)). Staffing's relations are too small to reach the bound, so the test lowers `ilp_amie.MAX_JOIN_ROWS`; the entry reads it at call time | red first, then exit 0 |
| T8 IH-R2: `tests/test_ilp_amie.py` (including `test_t9_the_recorded_run_replays`), `tests/test_il_close.py`, `tests/test_il6_walk.py`; `tools/ilp_comparison.py`; `ilp_amie.ADAPTER_VERSION == "2"` | exit 0, unchanged files |
| T9 (if IH1-D5 (a)) an unloadable population whose digest differs from the record's is refused `population-mismatch`, exit 3 | red first (exit 5), then exit 0 |
| T10 `EXPORT_REFUSALS` holds `opaque` and `too-large`; `test_c8c` passes | red first, then exit 0 |
| T11 `tests/test_rf6_*.py`, `tests/test_gnd_arch.py`, `tests/test_development_scaffold.py` | exit 0 with the IH1 successor |

**Verification selection:**
- the plan §9 IH1 row;
- T1 to T11;
- `tests/test_ih0_review.py`;
- the six `tests/test_ilp_*.py` suites;
- `tests/test_release_docs.py`;
- `tools/ilp_comparison.py`;
- ruff on the changed files.

**The full default suite runs once before the phase commit.** IH0's
narrower gate missed the RF6 census (IH0's record, "Gate repair"). It is not
the close's CI run (IH-R3).

## Out of scope for this phase

- IH2's own-reference joins, and any refusal name or spelling change.
- **Two suspicions, carried, not reproduced:** the mined import's "invalid
  model" message without a rule index, and the learner tuple form. No mined
  entry uses the tuple, and no reader built the invalid-model case.
- Any wire, golden, or adapter-version change (IH-R2).
- Any learner, solver or model run (IH-R1).

## Size

About 120 changed lines in `ilp_service`, `ilp_amie` and `tools/ilp_comparison.py`,
plus the tests. The record measures it.

## Approval instrument

This prose. The phase is a refactor whose cases are the existing goldens and
replays (IH-R2), plus T1 to T11.
