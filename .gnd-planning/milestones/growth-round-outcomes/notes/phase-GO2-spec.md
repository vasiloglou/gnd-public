# Phase GO2 · an outcome for every operation of a proposal · spec r1

## 1. Status

**Draft r1, 2026-11-23, awaiting its gate.** Planning only: no file under
`src/gnd/evolve/` changes until reviewed-vocabulary-growth VG2 and VG4 are
merged on `main` (plan §3) and the coordinating session answers
"READY GO2". Written against VG2's approved change (one branch in
`_enforce_d12`) and VG4's (`_source_document_target` in
`evolve/service.py`, `enforce_ownership` in `evolve/_includes.py`), read on
`claude/reviewed-vocabulary-growth` (PR 240) at `8f15e7c1`.

## 2. Provenance

- Derives from [plan r4](growth-round-outcomes-plan.md) (sha256
  `b107bd36…7431`, `001-plan-gate.md`): Goal (GO2), R0.1–R0.4, §1 H10–H13,
  §2 GO2, §4 GO2-C1 to C7, §5, §6, §9 GO2 lane, §10 D1, D2 and the GO2 open
  questions.
- From [#227](https://github.com/vasiloglou/gnd-public/issues/227), request 1.
- Code read at `92cc161f` (GO1 head). No review has read these bytes.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| plan GO2, H10 | every operation gets an outcome; `policy_issues` keeps its rows and meaning | §6; T1, T4 |
| plan H11 (unread half) | the exit and message of each whole-proposal refusal | §6 "Refusals today", read below |
| plan D1 (a) | tie a refusal to its operation where the gate can locate the element; collect what one pass can; `admitted` means every gate ran and none refused | §6; T2, T3 |
| plan D2 (a) | optional preview field, omitted when unset, no schema version move; a separate outcome report for a refused candidate | §6; T4, T5 |
| plan R0.1 | `apply` stays whole and refuses an outcome report | §6; T5 |
| plan R0.3, GO2-C3 | a preview without outcomes keeps every byte and digest | T4 |
| plan R0.4, GO2-C4 | value-free rows | §6; T6 |
| plan GO2-C6 | `apply` replays the outcomes setting from the reviewed preview | §6; T7 |
| plan GO2-C7 | an operation a later gate never reached is `unassessed`, the gates named | §6; T3 |
| VG2 `(d)` | the `sample` / `common-sense` branch of `_enforce_d12` | §6: the collecting walk keeps its branches, VG2's included |
| VG4 `(d)` | `enforce_ownership` refuses `repin-include` on an unattended root | §6: the include gate stays a whole-proposal refusal |

## 4. The standing rules, bound to this phase

- **Totality (rule 1).** The outcome report is read back by GO3 and GO5:
  its reader is total over arbitrary JSON (closed model, size cap on the
  read, a hostile-input test, T8).
- **A cap bounds the document (rule 2).** Locating a refusal is a lookup
  from a path or a host id to an operation index, built once per proposal:
  linear in operations plus issues. T9 times the locator over 2,000
  operations and 2,000 issues.
- **Validation order (rule 3).** The refusal order of `preview` does not
  move: gate (18), current model, candidate validation, replay equality,
  D-12, then the policy. The outcome pass runs after a refusal is decided
  and never changes which refusal is reported or its exit. T2 pins the
  first message byte for byte against the scope-off path.
- **One walk for N kinds (rule 4).** One locator maps every refusal source
  (validation issue path, D-12 host and constraint, policy issue) to an
  operation; there is no per-gate mapper.
- **One home (rule 5).** The verdict words and the report's fields live in
  the evolution contract's preview section; `unattended-growth.md` cites it.
- **Measurement (rule 6).** Whether one pass can locate a D-12 refusal is
  decided by T3 over the IK2 and VG2 rows, not argued.
- **General solutions (`AGENTS.md`).** A validation issue's path is read by
  the path grammar the validator writes (`$.collection[index]...`), parsed
  by the existing path helpers of `gnd.model._includes` (`remap_issues`
  reads the same grammar); the spec adds no second matcher (§6, reuse).

## 5. Goal

`gnd evolve preview --operation-outcomes` names an outcome for every
operation of the proposal: in the preview when the candidate is admitted
to the policy step, and in an outcome report when an earlier gate refuses
it. Without the flag nothing changes.

## 6. Design

### Refusals today (H11's unread half, read at `92cc161f`)

Every refusal below is an `EvolutionError` (or a subclass), printed as
`EVOLUTION PREVIEW REFUSED (<exit>): <message>`:

| Gate | Where | Exit | Names an element |
|---|---|---|---|
| operations gate | `_enforce_operations_gate` | 18 | the locator, in the message |
| include ownership (VG4 adds repin) | `enforce_ownership` | 3 | the reference |
| current model invalid | `_load_model_document`, label `current model` | 3 | no operation |
| candidate invalid | `_load_model_document`, label `candidate model` | 3 | a `ValidationIssue.path` per issue |
| replay inequality | `preview`, "declared operations do not equal…" | 3 | no |
| D-12 | `_enforce_d12` | 3 | no (the constraint is known to the walk) |
| policy | `additive_policy_issues` | 3 after the preview is written | yes, `PolicyIssue` |

### Verdicts

`admitted`, `refused-by-policy`, `refused-by-validation`, `refused-by-d12`,
`dropped-with` (depends on a refused operation), `unassessed` (a gate that
would read it did not run, or the refusal could not be located). Every row
carries `operation_index`, `operation_id`, `reference` (the locator's
reference string, as `PolicyIssue` has it), `verdict`, `detail` (value-free:
ids, key names, a rule id) and `gates_not_run` (a list, empty unless
`unassessed`).

### Where they live

- **Admitted to the policy step:** `EvolutionPreview.operation_outcomes`,
  `tuple[OperationOutcome, ...] | None = None`, added to
  `_OPTIONAL_PREVIEW_FIELDS`, so a preview without it keeps its bytes and
  `preview_sha256`. No schema version moves.
- **Refused earlier:** an `EvolutionOutcomeReport` (closed, `schema_version:
  1`, `kind: "evolution-outcome-report"`): `proposal_id`, `proposal_sha256`,
  `before_model` (`CommittedText`, as the preview has it), `refusal`
  (`gate`, `exit`, `message` exactly as printed), `operation_outcomes`.
  Written to `--outcome-report PATH`, a workspace path the CLI confines as
  it confines `--out`; never to the preview path. `apply` reads a preview
  through the closed `EvolutionPreview` model, so a report given to `apply`
  is refused as an invalid preview (exit 3) by type (T5).

### The locator (one walk)

Built once per proposal from its operations: element id → index for each
`ElementLocator`, host id (fact type or `model`) plus family → indexes for
each `ConstraintLocator`, fact type id → index for each `RoleLocator`,
document sha256 → index for `source-document`, include id → index for an
`IncludeLocator`.

- A validation issue's path `$.object_types[i]…` or `$.fact_types[i]…`
  names the candidate element at that index; its id finds the operation.
  The candidate is parsed with `parse_model_document` (the GO1 scope makes
  this free) even when it does not validate. A path that names no element
  an operation touched, or a candidate that does not parse, is
  unlocatable.
- A D-12 refusal is located by its host and the canonical JSON of the
  constraint: the operation whose `ConstraintLocator` names that host and
  whose `after` has that canonical JSON.
- A policy issue already carries its `operation_index`.
- `dropped-with`: after the refused set is known, an operation is dropped
  with a refused one when its constraint host, its role's fact type, or
  one of its fact type's role players is an element a refused operation
  adds. One pass in operation order (an operation can only depend on an
  earlier one in the replay), so the closure is linear.

### One pass

- `_enforce_d12` becomes a collecting walk, `_d12_refusals(before,
  candidate) -> list[(host, constraint, message)]`, in the same order;
  `_enforce_d12` raises its first message, so the printed refusal is byte
  identical (T2). VG2's branch is one of its branches.
- Candidate validation already returns every issue of the layer that
  failed (`ModelValidationError.issues`); layer 2 does not run after a
  layer-1 failure, so operations no layer-1 issue names are `unassessed`
  with `gates_not_run: ["semantic-validation", "d12", "policy"]`.
- When validation refuses, D-12 still runs over the parsed candidate
  document in the outcome pass (it reads documents only), so a D-12 fault
  in another operation is reported in the same report. The policy reads
  loaded models and does not run: operations not otherwise refused are
  `unassessed` with `gates_not_run: ["policy"]` when a policy was
  requested, `admitted` when none was.
- Replay inequality, a current-model refusal, the operations gate and the
  include gate are unlocatable: one whole-proposal row in the report's
  `refusal`, every operation `unassessed` with the gates that did not run.

### Apply replays the setting

`_cmd_evolve_apply` rebuilds the fresh preview with
`operation_outcomes=reviewed.operation_outcomes is not None`, as it does for
`shape_report` (`cli_service.py:810`). An edited outcome row changes the
reviewed preview, which then no longer equals the fresh one: stale, exit
11 (T7).

### Pages

The evolution contract's preview section: the field, the report, the six
words and `gates_not_run`; `unattended-growth.md` gains no rule (GO4 and
GO5 cite the contract). `docs/release-notes.md`: one entry.

### Homes

`src/gnd/evolve/service.py`, `models.py`, `cli_service.py` (the two
options and the replay), `src/gnd/commands/evolve.py` (the two arguments),
the evolution contract, `tests/test_go2_operation_outcomes.py` (new),
`docs/release-notes.md`, `dev/components/`.

## 7. Decisions

| ID | Question | Readings | Proposed |
|---|---|---|---|
| GO2-D1 | Instrument | corpus-first is the default for a serialized format; the report and the field are one closed model each, and their cases are six verdict words that T1–T3 enumerate | this prose, with the closed models as the format's one home |
| GO2-D2 | Run D-12 over a candidate that failed validation | (a) yes, over the parsed document: more refusals per round. (b) no: those operations `unassessed` | (a) |
| GO2-D3 | Where the report is written | (a) `--outcome-report PATH`, separate. (b) the `--out` path: a refused round would leave a file at the preview path | (a) |
| GO2-D4 | The flag | (a) `--operation-outcomes` on `preview`; `apply` takes it from the reviewed preview. (b) always on: every preview changes bytes | (a) |
| GO2-D5 | Dependents (plan open question) | (a) from locators and the operations' `after` values. (b) from the candidate's references | (a): the candidate may not parse |

## 8. Tests

New `tests/test_go2_operation_outcomes.py`, built on the proposals of
`tests/test_evolve_additive_policy.py` and the acceptance replay.

| # | Case | Expected |
|---|---|---|
| T1 | four operations, one refused by candidate validation at a locatable element (GO2-C1) | no preview; the report names four rows: one `refused-by-validation`, three `unassessed` with `gates_not_run` naming what did not run, or `admitted` where GO2-D2 ran D-12 and no policy was requested; exit and stderr equal to the run without the flag |
| T2 | one fixture per verdict word (GO2-C2), walked from the verdict table; and two faults in two operations | each word reached; both faults named, or the second `unassessed`; the printed first refusal byte-identical to today |
| T3 | the IK2 and VG2 D-12 rows, each as a one-operation proposal beside an admitted one | `refused-by-d12` on the right row and `admitted` on the other; GO2-C7 |
| T4 | a proposal admitted today, previewed without the flag and with it (GO2-C3) | without: byte-identical preview and `preview_sha256`; with: every row `admitted`, every other field equal |
| T5 | the report given to `apply` as its preview (GO2-C5) | refused as an invalid preview, exit 3 |
| T6 | the disclosure tests over a report and a preview with outcomes (GO2-C4) | no constraint or sample value in any row |
| T7 | `apply` of a preview with outcomes; the same with one row's verdict edited (GO2-C6) | 0; 11 stale |
| T8 | the report reader over hostile JSON (deep nesting, a long integer, NaN, an extra key, 11 MiB) | a named refusal each, never a traceback |
| T9 | the locator over 2,000 operations and 2,000 issues | under one second (time bound over the added layer, rule 2) |
| T10 | the existing lane: `tests/test_evolve_additive_policy.py`, `test_evolve_loading.py`, `test_evolve_source_document.py`, `test_evolve_population_check.py`, `test_evolve_shape_matches.py`, `test_mc3_evolution.py`, `test_unattended_model_growth_acceptance.py`, `test_vg2_evolve_sources.py` | exit 0, unmodified |

Branch table: located, unlocatable, dropped-with, unassessed by an
earlier-layer refusal, unassessed by a policy not run. T1–T3 reach each.

Gate: plan §9 GO2 lane plus `tests/test_vg2_evolve_sources.py`, the guard
block, both lint commands, the component check.

## 9. Out of scope

Partial application in `apply` (R0.1); narrowing the proposal (GO3);
locating a replay-inequality or current-model refusal; any change to a
refusal's text or exit.

## 10. Size

About 200 source lines (locator 60, collecting D-12 40, models 40, CLI 30,
report writing 30) and 400 test lines.

## 11. Approval instrument

This prose (GO2-D1).

## 12. Gate — delegated approval (auto=true)

**Delegated approval (auto=true), 2026-11-23**, of this spec r1, sha256
`59026870edb9fc4823de19ed950453864c849f5b2f8170fa7d10baf1a145ace3` (the bytes above this section). Authorization: the owner's
delegation of `auto` for growth-round-outcomes, recorded in
`001-plan-gate.md`. An agent ruling under that delegation, not the owner's
reading of the spec. No spec review ran (optional, omitted).

- Rulings: GO2-D1 prose; GO2-D2 (a); GO2-D3 (a); GO2-D4 (a); GO2-D5 (a) [delegated].
- Sweep: every gate of the refusal table was read at `92cc161f`; the locator needs only ids the operations carry; VG2's `_enforce_d12` branch and VG4's `enforce_ownership` refusal fit the collecting walk and the whole-proposal row unchanged. Open at implementation: whether layer-2 issues of other operations surface when layer 1 passed for them (measured by T2's two-fault case).
- Budget: one diff review round (D8), a second only if the first blocks.
- **Approval is of the design only. Implementation waits** for the
  start condition of plan §3 on `main` and the coordinating session's
  "GO" to "READY GO2". A spec approved now is re-read against `main` at
  that start; a change on `main` that moves a cited line or a premise
  amends this spec before code, with the prior wording retained.
