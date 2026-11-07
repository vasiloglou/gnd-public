# Rule-check follow-ups

**Status: draft r1, 2026-11-07, awaiting the owner's plan gate. Not
reviewed** (no review instrument selected yet; RF-D0 below). `auto=false`.

Eight small follow-ups that the rule-check-adoption milestone deferred at its
close ([012-milestone-close.md](../../rule-check-adoption/012-milestone-close.md),
open-questions sweep): issues 111, 112, 113, 114, 115, 116, 117 and 119. The
owner asked for them as one milestone (2026-11-07). Probes at main
`6651e5a4` (§1) show that two of them (111, 112) are not small; the plan
gives each a scope ruling instead of assuming one.

## Completion predicates

The milestone is complete when, on main after merge:

1. A version-7 (and every version sharing `$defs.derivation_verdict`) check
   report whose derivations are unchecked for a `term:*` reason validates
   against `report.schema.json`; no report's bytes change (FU1, issue 113).
2. A combined or reference-bound population keeps its `label`, and no copy
   of a `Population` can carry `producer` without `source: tool-output`
   (FU2, issues 115, 116).
3. Under `--rule-ids`, a failing `acyclic` ring over an exact-term derived
   fact type lists in-group edges that equal the pairs the checker judged,
   pinned by a corpus case (FU3, issue 119).
4. The two timing tests no longer fail under the six-shard full run, without
   loosening what they assert beyond what a ruling allows (FU4, issue 117).
5. The unused cycle helpers are retired or explicitly kept, per RF-D5
   (FU5, issue 114).
6. Issues 111 and 112 are each either delivered (FU6, FU7) or split out to a
   named target by owner ruling (FD1, FD2).
7. Each phase has an approved spec, a record with verbatim focused-gate
   output and one independent reviewer; the close record disposes every open
   question and closes the delivered issues.

## 0. Binding design rules

Inherited from rule-check-adoption §0 where they still bind; restated here:

1. **Frozen variants.** No existing report's bytes change. A schema may
   accept more (FU1) but not less.
2. **Measure, don't assert.** Every claim about a failure, a flake or a
   digest is reproduced before it is planned against, and every fix has a
   regression observed red first.
3. **Shims.** Moved or retired names follow AGENTS.md and RF-D5: retirement
   is a separately approved phase.
4. **One home.** A fix lands where the behaviour lives (`population.py`, the
   binder, the schema), not in a caller.
5. **Stop rule (size).** A phase pauses for the owner past 1.5 times its
   estimate.

## 1. Scope, sources and authority

| Issue | Probe at `6651e5a4` (2026-11-07) | Observed |
|---|---|---|
| 113 | `exact-terms.orm.yaml` with `redact: true` removed, `term-input.pop.yaml`: `gnd check --format json` → version 7, exit 4, `term:mod-zero` derivations, **1** schema error; `term-clean`: 0 errors. `$defs.derivation_verdict.reason_code` admits 3 values plus null; `derivation_verdict_v15` admits 11; `derivation_verdict` is also used by `derivation_verdict_v9`, `legacy_reference_report` and `temporal_admission_report` | reproduced |
| 115 | `Population(model='m', source='tool-output', producer='x', facts={}).model_copy(update={'source': 'fixture'})` → `fixture x`, no error | reproduced |
| 116 | `Population.label` (`population.py:136`) is read by `_build_population` (`:473`); `_combine_validated_populations` (`:495-506`) and `model.bind_population` (`model/__init__.py:697-704`) do not pass it | read |
| 119 | no fixture has an `acyclic` ring over an exact-term derived fact type; `correspondence.acyclic_extents` keeps the version-7 row when no group is found (RC2 record, boundary) | read |
| 117 | `test_scope_walk_scales_linearly`: `large < 5.0` and `large < 6 * small`; `test_driver_kills_the_whole_process_group_on_timeout`: `timeout_seconds=3` with a real grandchild. Both pass alone (3/3 at RC6), each failed once under six shards | observed in records 008, 011 |
| 114 | `_find_cycle`, `_dfs_cycle`, `_ring_component_violations` (`checker/_core.py:1296-1380`) have no production caller; re-exported from `gnd.checker` (`__init__.py:101, 129, 184`); `tests/test_checker_families.py:206` tests `_find_cycle`; RF metrics files name `gnd.checker._find_cycle` | read |
| 112 | `output._print_projected_text` prints a `REDACTION` header and then `render_json(payload)`, by design: "Render only the already-projected tree on declaration-bearing routes" (`output.py:113`), so the text renderer never sees unredacted values. Observed for redaction; temporal routes to be confirmed in the spec | read, deliberate |
| 111 | `values._model_digest` is `sha256(repr(model_dump(...)))`. It crosses a process boundary: `transition.verify_digests` compares a caller-supplied `model_digest` to it (`transition:model-digest-mismatch`), and about 100 files under `tests`, `src` and `docs` record `"model_digest": "sha256:…"`. `operations_digest` beside it already uses canonical JSON for exactly this reason (`transition.py:94-111`) | read |

Authority: the owner's request (2026-11-07); the eight issues; the
rule-check-adoption close record.

## 2. Contract proposal and product behavior

- **FU1:** widen `$defs.derivation_verdict.reason_code` to the same set as
  `derivation_verdict_v15` (FD3). Reports are unchanged; only validation
  accepts them.
- **FU2:** `label` passes through both constructors and the binder. A
  `Population` validates the producer invariant on copy as well as
  construction, either by a validator that `model_copy` cannot skip or by
  refusing `model_copy` updates to `source`/`producer` (spec decides).
- **FU3:** a corpus case; if the extent and the checker disagree, the fix
  makes the extent read the checker's pairs.
- **FU4:** per FD4.
- **FU5:** per FD5.
- **FU6 (111), FU7 (112):** only if FD1 / FD2 keep them here.

## 3. Dependencies and artifact homes

```
FU1   FU2   FU3   FU4   FU5   [FU6]  [FU7]   ──> close
```

The phases are independent; the order is by size and risk. FU3 reuses the
exact-terms fixtures FU1 uses.

| Artifact | Home |
|---|---|
| derivation reason enum | `src/gnd/report.schema.json` `$defs.derivation_verdict` |
| producer invariant, label | `src/gnd/population.py`; `src/gnd/model/__init__.py` `bind_population` |
| acyclic extent | `src/gnd/correspondence.py` `acyclic_extents` |
| timing tests | the two test files; pytest markers in `pyproject.toml` if FD4 chooses a lane |
| cycle helpers | `src/gnd/checker/_core.py`, `src/gnd/checker/__init__.py`, the shim inventory |

## 4. Phases, deliverables, named criteria

### FU1: version-7 derivation reasons (issue 113; about 15 schema, 60 test lines)
- FU1-C1: the probe's report validates; a corpus case per `term:*` reason
  the checker can emit under version 7.
- FU1-C2: no report variant's bytes move (full suite).
- FU1-C3: every schema that references `derivation_verdict` is listed and
  tested (v7, v9, legacy reference, temporal admission).

### FU2: population header integrity (issues 115, 116; about 20 source, 80 test lines)
- FU2-C1: `model_copy` (and any other construction route the spec finds)
  cannot produce a producer without `tool-output`.
- FU2-C2: `label` survives `_combine_validated_populations` and
  `bind_population`.
- FU2-C3: content and model digests of existing populations unchanged where
  `label` is unset; where it is set, the spec lists every recorded digest that
  moves before code (rule 1).

### FU3: derived-ring extent (issue 119; about 0-40 source, 100 test lines)
- FU3-C1: a corpus model with an `acyclic` ring over an exact-term derived
  fact type, failing; `--rule-ids` rows equal the checker's judged pairs in
  strongly connected groups.
- FU3-C2: a disjoint added cycle leaves existing rows unchanged (RC2-C2's
  property for this route).

### FU4: timing tests (issue 117; about 20 test lines)
- FU4-C1: per FD4; each test still fails against a mutant that breaks what
  it guards (a quadratic walk; a leader-only kill).

### FU5: cycle helpers (issue 114; about -90 source, -10 test lines)
- FU5-C1: per FD5; the guard registries and metrics successors updated.

### FU6: canonical model identity (issue 111) — only under FD1 (b)
### FU7: text rendering of projected reports (issue 112) — only under FD2 (b)

### Close
Close record; question sweep; full suite against the merge-base record.

## 5. Documentation, skill and compatibility surfaces

FU1 touches the report reference only if it lists reason codes per version.
FU5 touches the shim inventory. No skill text changes unless FU7 runs.

## 6. Risks and required controls

| Risk | Control |
|---|---|
| A recorded digest moves (FU2 label) | rule 1; listed before code; full suite |
| A flaky test is "fixed" by asserting nothing | FU4-C1 mutants |
| Retiring a shim breaks an importer | FU5 source scan and guard suites |

## 7. Out of scope

GR-D4 (issue 95) and GR-T17 (issue 104); any new report version; changing
the version-7 report's bytes.

## 8. Execution, approval and review protocol

`auto=false`. Each phase: spec, owner gate, implement, focused gate, one
independent reviewer in a different tool (Codex), refactoring review,
record, commit on `claude/rule-check-followups`, PR. Merge is the owner's.
The plan-review bar is the maintained panel (project.md); RF-D0 asks the
owner which instrument reviews this plan.

## 9. Per-phase verification story

| Phase | Focused gate (exact files in each spec) | Affected consumers |
|---|---|---|
| FU1 | new FU1 tests + `tests/test_schema_sync.py tests/test_report_json.py` | report schema consumers |
| FU2 | new FU2 tests + `tests/test_rc5_tool_output.py tests/test_population_load.py` | composition, witness wire, digests |
| FU3 | new FU3 tests + `tests/test_rc2_acyclic_extent.py` | version-15 consumers |
| FU4 | the two tests, alone and under the six-shard run | — |
| FU5 | guard suites + `tests/test_checker_families.py` | shim inventory, RF metrics |
| close | full suite vs the merge-base record (main `6651e5a4`) | — |

The merge-base full suite is run on beast-3 before FU1 changes code.

## 10. Owner decisions and open questions

| ID | Question | Proposal |
|---|---|---|
| RF-D0 | Review this plan before the gate? | one reviewer (Codex), as for this milestone's predecessor's r3-r5; the panel is the project's bar |
| FD1 | Issue 111 (repr model digest) | **(a) split out to its own milestone**: it is a cross-process identity with ~100 recorded values and a supplied-digest check in the transition arm; doing it right means a versioned identity accepted beside the old one, which is not small. (b) keep it here as FU6 |
| FD2 | Issue 112 (projected JSON in text output) | **(a) split out**: the JSON-only text is a deliberate no-leak design; rendering verdict lines from the projected tree needs its own design and a leak review. (b) keep it here as FU7 |
| FD3 | FU1: widen the version-7 enum to version 15's set, or only to the `term:*` values the version-7 route can emit? | version 15's set: one list, and a value the route cannot emit costs nothing |
| FD4 | FU4: widen the bounds, or move both tests to a serial lane? | widen: the scope walk's ratio and ceiling, and the driver test's time margins, to values measured under the six-shard load (fixed in the FU4 spec), each checked against its mutant; a serial lane needs runner support the shard script lacks |
| FD5 | FU5: retire the three helpers (RF-D5's later approved phase, after the first public release), or keep them? | retire `_dfs_cycle` and `_ring_component_violations`; keep `_find_cycle` only if a test outside the checker family needs it, else retire it and its test |
