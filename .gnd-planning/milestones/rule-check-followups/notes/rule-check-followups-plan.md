# Rule-check follow-ups

**Status: r3, approved by the owner at the plan gate on 2026-11-07
("Approve r3"; [plan-gate record](../001-plan.md)).** r3 applies the Codex
review of r2 (P1-P6, [plan-review-r2](../evidence/plan-review-r2/codex-review.md));
r3 itself was not re-reviewed. The owner ruled RF-D0 and FD1-FD5 as
proposed over r1. `auto=false`. Amended at the milestone close (§11).

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
6. Issues 111 and 112 stay open, split out by owner ruling (FD1, FD2) to
   milestones of their own; this milestone does not close them.
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

- **FU1:** widen both reason-code enums of `$defs.derivation_verdict` (the
  property enum and the unchecked branch's conditional enum,
  `report.schema.json:1108-1113`) to the same set as `derivation_verdict_v15`
  (FD3; review P1). Reports are unchanged; only validation
  accepts them.
- **FU2:** `label` passes through both constructors and the binder. A
  `Population` validates the producer invariant on copy as well as
  construction, either by a validator that `model_copy` cannot skip or by
  refusing `model_copy` updates to `source`/`producer` (spec decides).
- **FU3:** a corpus case; if the extent and the checker disagree, the fix
  makes the extent read the checker's pairs.
- **FU4:** per FD4.
- **FU5:** per FD5.
- Issues 111 and 112: split out (FD1, FD2).

## 3. Dependencies and artifact homes

```
FU1   FU2   FU3   FU4   FU5   ──> close
```

The phases are independent; the order is by size and risk. FU3 has its
own ring model and corpus (`tests/fixtures/fu3-derived-ring/`); FU1's
exact-terms fixtures cannot carry a ring (amended at the close, §11).

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
- FU1-C3: every branch whose reason-code enum comes from
  `derivation_verdict` (v7, v9, legacy reference, temporal admission) has a
  direct schema case, whether or not a CLI route emits the reason; a
  version-15 non-regression case, since `derivation_verdict_v15` reuses six of
  its properties (review P2).

### FU2: population header integrity (issues 115, 116; about 20 source, 80 test lines)
- FU2-C1: validated construction and `model_copy` cannot produce a
  producer without `tool-output`. `model_construct` (unvalidated by design,
  review P3) is in or out of scope by an FU2 spec decision, with a case
  either way.
- FU2-C2: `label` survives `_combine_validated_populations` and
  `bind_population`, the candidate's label winning as its `source` and
  `producer` do, with a conflicting-labels case; the combined population's
  content digest change is pinned and the witness candidate binding (which
  hashes the original candidate) is pinned unchanged (review P4).
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
- FU4-C1: the spec first captures which assertion fails under load. The
  driver test's survivor check (`pgrep -f "pathlib.Path"`, machine-wide,
  `tests/test_public_session_driver.py:387-390`) is scoped to the spawned
  process group before any margin is widened (review P5); then FD4's measured
  margins. Each test still fails against a mutant that breaks what it guards
  (a quadratic walk; a leader-only kill).

### FU5: cycle helpers (issue 114; about -90 source, -10 test lines)
- FU5-C1: per FD5. The spec names the live guards that bind the helpers:
  `tests/test_rf6_packages.py` (historical checker bindings and RF6b
  baselines), `tests/support/rf9_ci_sources.py` with
  `compatibility-private-sites.json` (frozen import sites), and
  `tests/test_checker_families.py:206`. Historical baselines and evidence
  stay byte-identical; retirement is an explicit successor or exemption for
  the three names, with a negative test that the retired imports fail
  (review P6).

FU6 (issue 111) and FU7 (issue 112) are withdrawn: split out by FD1 and FD2.

### Close
Close record; question sweep; full suite against the merge-base record.

## 5. Documentation, skill and compatibility surfaces

FU1 touches the report reference only if it lists reason codes per version.
FU5 touches the shim inventory. No skill text changes.

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
| RF-D0 | Review this plan before the gate? | one reviewer (Codex), as for this milestone's predecessor's r3-r5; the panel is the project's bar **Ruled (o, 2026-11-07): as proposed** ("Approve all as proposed", answering "How do you rule on the plan's decisions RF-D0 and FD1–FD5?"). |
| FD1 | Issue 111 (repr model digest) | **(a) split out to its own milestone**: it is a cross-process identity with ~100 recorded values and a supplied-digest check in the transition arm; doing it right means a versioned identity accepted beside the old one, which is not small. (b) keep it here as FU6 **Ruled (o, 2026-11-07): as proposed** ("Approve all as proposed", answering "How do you rule on the plan's decisions RF-D0 and FD1–FD5?"). |
| FD2 | Issue 112 (projected JSON in text output) | **(a) split out**: the JSON-only text is a deliberate no-leak design; rendering verdict lines from the projected tree needs its own design and a leak review. (b) keep it here as FU7 **Ruled (o, 2026-11-07): as proposed** ("Approve all as proposed", answering "How do you rule on the plan's decisions RF-D0 and FD1–FD5?"). |
| FD3 | FU1: widen the version-7 enum to version 15's set, or only to the `term:*` values the version-7 route can emit? | version 15's set: one list, and a value the route cannot emit costs nothing **Ruled (o, 2026-11-07): as proposed** ("Approve all as proposed", answering "How do you rule on the plan's decisions RF-D0 and FD1–FD5?"). |
| FD4 | FU4: widen the bounds, or move both tests to a serial lane? | widen: the scope walk's ratio and ceiling, and the driver test's time margins, to values measured under the six-shard load (fixed in the FU4 spec), each checked against its mutant; a serial lane needs runner support the shard script lacks **Ruled (o, 2026-11-07): as proposed** ("Approve all as proposed", answering "How do you rule on the plan's decisions RF-D0 and FD1–FD5?"). |
| FD5 | FU5: retire the three helpers (RF-D5's later approved phase, after the first public release), or keep them? | retire `_dfs_cycle` and `_ring_component_violations`; keep `_find_cycle` only if a test outside the checker family needs it, else retire it and its test **Ruled (o, 2026-11-07): as proposed** ("Approve all as proposed", answering "How do you rule on the plan's decisions RF-D0 and FD1–FD5?"). |

## 11. Close amendments

Proposed at the milestone close (2026-11-08,
[007-milestone-close.md](../007-milestone-close.md)); they take effect with
the owner's close ruling, the merge of the close PR. The prior wording is
kept here.

| Where | Raised by | Prior wording | Now |
|---|---|---|---|
| §3, the paragraph under the diagram | FU3 spec finding P2, record row FU3-O1 ([004-phase-FU3.md](../004-phase-FU3.md)) | "FU3 reuses the exact-terms fixtures FU1 uses." | FU3 has its own ring model and corpus; FU1's `terms.orm.yaml` has no binary fact type over one object type, so it cannot carry a ring |
| Completion predicate 2 | close review K1 (reproduced at the close) | "no copy of a `Population` can carry `producer` without `source: tool-output`" | no copy of a validated `Population` can; `model_construct` is unvalidated and its copies are not revalidated (FU2 boundary) |
| Completion predicate 6 | close review K2 | "Issues 111 and 112 stay open, split out by owner ruling (FD1, FD2) to milestones of their own; this milestone does not close them." | this milestone closes neither; issue 112 was closed on 2026-11-08 by the report-output-fidelity milestone (PRs 124, 127), which supersedes the open-state clause for it |
