# PA0 — Frozen application corpus and checking contract

Status: implementable once the four local plan reviews and delegated plan gate are recorded.

## Provenance

Draft r1 of `pyrel-applications-plan.md`, all sections, especially PA0 and §9.
This spec precedes corpus implementation. Whole-milestone owner authorization:
`@process-milestone pyrel-applications auto=true`, 2026-10-13. The owner selected
four local reviewer subagents for plan and close. No paid review is selected.

## Obligations and discharge

| Source | Obligation | Discharge |
|---|---|---|
| PA0-C1 | Address every rule and derivation in five models; positive/negative/warning controls | Frozen matrix and answer key below |
| PA0-C2 | Native unsupported guarded and supplied-derived baseline; successor genuinely red | Baseline driver and red-successor mode |
| PA0-C3 / PA-D1–D5 | Exact grammar, interfaces, compatibility, ceilings, normalized agreement | Contract and decisions below |
| PA0-C4 / §9 | Public raw-input driver, exact inputs/runtime, legacy controls, local config | Native commands and focused selection |
| §5 | Report clients/export goldens/runtime locks/runner markers | Consumer inventory in matrix manifest |
| §6 | False enforcement, circular agreement, unknown empties, warnings, forged claims, arithmetic, isolation, skipped lanes, compiler scope, budgets | Named corpus controls and separate query assertions in PA3/PA4 |
| §7 | No universal compiler, actor/payment/transition authority, hosted deployment or release | Scope below |
| public-launch/007 | Isolated interpreters, native steps actually executed, matching packaged locks | Use existing maintained lock; record versions; no inherited native pass |
| RF6a/011, RF6b/012 | ModelIndex policy, actual patch homes, no GND import in standalone runtime | Inventory consumers; no runtime edits in PA0 |
| RF7/013 | Strict scalars/total bounded intake; prior evidence is historical | Raw model/population admission and hostile successors |
| RF9/015,016,017; shim inventory | Frozen authority units/goldens, original owners and retirement gates | Preserve historical inputs; new corpus separately identified |
| compiled-snapshot/004 | Compiled operations opt-in is separate from guarded checking | No compiled-operation changes or acceptance claim |

## Standing rules

PA-R1: the native baseline executes generated programs; comparison calls GND
only in the development driver. PA-R2: matrix traversal enumerates every model
constraint and derived head, and asserts counts. PA-R3: original/strict genre
siblings and missing/extra derived claims have narrated expected answers.
PA-R4: legacy completion zero is recorded independently of business outcomes.
PA-R5: publication is later work; PA0 never publishes a candidate. PA-R6: pinned
isolated runtime, explicit local DuckDB and timeout; no credentials needed.
PA-R7: this phase adds development fixtures, not another production evaluator.
PA-R8: baseline evidence is native execution, not completed application checking.

Process standing rules: totality binds the corpus driver's document boundary;
algorithm bounds bind subprocess timeout and fixture count; validation order
is input/version admission before execution and output checks; complete policy
traversal is asserted by matrix counts; one normative home is this contract;
contested runtime representations are settled by native/GND measurements.

## Goal

The PA0 inventory and GND answer-key gate exits 0; native baseline measurement
exits 0 while retaining unsupported guarded verdicts. The successor comparison
exits 1 specifically because native guarded checking is absent. No successor
acceptance implementation is credited to this phase.

## Contract for successor phases

One opt-in profile, `applications-v1`, lives in the standalone translation
runtime. Legacy `report_document`, `evaluate_document`, report schema version 1
and audit completion exits retain their interface. Add `--accept` to exported
programs; without it existing behavior remains the compatibility surface.

Public callable in standalone runtime:

```python
def acceptance_document(model: dict[str, Any], population: dict[str, Any], *,
                        model_sha256: str, population_sha256: str) -> dict[str, Any]: ...
```

The command computes hashes of the exact embedded model UTF-8 text and the exact
bounded population bytes it parses, never rereading to hash. Applications check
those bindings before publishing the same staged bytes. Model hashing is the
emitter's decoded UTF-8 text re-encoded as UTF-8 (including retained newlines);
the installed application's original model must match that representation.

```json
{"schema_version":1,"profile":"applications-v1","backend":"duckdb-local",
 "status":"accepted","exit_code":0,"accepted":true,
 "binding":{"model_sha256":"64 hex","population_sha256":"64 hex"},
 "verdicts":[],"derivations":[]}
```

Each verdict carries `constraint_ref` (existing structural address), `id`
(explicit id or structural address), `constraint_type`, `modality`, `status`,
`witnesses`, and `reason` (null when absent). Status vocabulary:
`satisfied`, `vacuous`, `violated`, `warning`, `incomplete`, `unsupported`, `error`.
Guarded witnesses are sorted dictionaries with the antecedent's variable names
(including `$`) and typed JSON scalar values. Native rows are deduplicated as
logical tuples. Existing uniqueness duplicate-count behavior remains separately
pinned; duplicate approval is also an application refusal. Derivation entries
carry head identity, status, and sorted missing/extra role dictionaries.

Overall precedence: `runtime_failure` (70), `incomplete` (2, including
unsupported or work refusal), `rejected` (1), `accepted_with_warnings` (0),
`accepted` (0). Malformed input is 3; missing input 66; invalid command 64;
occupied audit output 11; operational output failure 70. `accepted` is true
only for the two accepted statuses. No empty verdict inventory bypasses model
traversal. Refusal outputs contain honest coverage/reasons; applications publish
no business output on any nonaccepted status.

Coverage requires each referenced asserted relation in `population.covers`
and an explicit list in `facts` (empty lists are known empty); absent or uncovered
relations are unknown. Computed derived relations acquire coverage only after
all positive/negative dependencies are known and native computation succeeds.
Supplied claims for derived heads require explicit covered lists and are compared
with the computed result. An unknown consequent remains incomplete even if the
antecedent is empty. Known empty antecedents are vacuous. Explicit model IDs,
when present on the population, must match the selected model.

Admitted guarded grammar: 1–8 conjunctive fact atoms with role bindings to
variables or typed scalar literals; partial bindings mean existential wildcards.
Consequent has exactly one `atom`, `absence` or `comparison`; consequent variables
must be positively bound. Repeated/shared variables retain one primitive type;
conflicting primitives and unbound comparison operands refuse. Comparisons admit
`=`, `==`, `!=`, `<>`, `<`, `<=`, `>`, `>=` over compatible primitive values.
Strings and booleans admit equality/inequality only. Numeric comparisons execute
native PyRel operators. The application profile admits String, Boolean and
signed integer scalars within ±(2**53-1); Float/Number are outside this initial
profile and refuse rather than silently round. This covers all five shipped
models. Legacy scalar support remains unchanged.

Derivation fragment: acyclic structured `body`, optional `negate`, and `head`;
1–8 positive atoms, at most 8 negatives, head/negative variables positively
bound, no clauses/recursion/aggregate/temporal constructs. Typed tuple identity
is preserved; no supplied derived claim enters the native definitions. Native
computed facts feed guarded completeness checks.

Profile ceilings: 1 MiB each model/population, 32 fact types, 64 constraints,
8 roles per relation, 1,000 asserted/claimed rows total, 8 atoms per conjunction,
100,000 conservative intermediate combinations and 10,000 result tuples.
Projected join work is conservatively multiplied before building/executing a
query; empty dependencies are still coverage checked. A 60-second isolated
subprocess ceiling and 4 MiB retained-output cap govern native application calls.
Library calls require the same admitted work boundary; the hard wall belongs to
the application subprocess. Budget refusal cannot become acceptance. PA0's
baseline driver uses a 60-second subprocess timeout and caps retained reports.

Normalization compares each structural obligation identity and status, including
warnings, vacuity, unknowns and derived discrepancies, plus canonical sorted
witness dictionaries where GND exposes them. GND batch summaries cannot supply
passing identities: use public `gnd.api.check(..., unredacted=True)` reports.
Format/process exits are compared only for the new acceptance contract; legacy
completion zero is not expected to equal GND's business exit.

## Design and approval instrument

`tests/fixtures/pyrel_applications/README.md`: stories/entry point, no answer key.
`answers.json`: separate frozen expected business outcomes. `matrix.json`: every
model SHA, structural obligation, branch, named controls and consumer inventory.
`cases/*.population.json`: baseline and discriminating mutants with inherited
resource facts; the matrix links exact model resource paths.
`tools/measure_pyrel_applications.py`: public exporter + raw subprocess driver,
baseline and successor modes, versions/hashes/receipts, no hidden GND predicate.
`tests/test_pyrel_application_corpus.py`: matrix/answer-key/current GND controls.

Corpus-first is selected because this work fixes an acceptance format and
validation predicates. Freeze and commit the answer corpus RED before successor
runtime implementation. PA0's own corpus gate is green only for completeness,
GND expectations and reproduced baseline omission.

## Decisions — delegated choices pending plan gate

| ID | Proposed ruling | Cost and boundary |
|---|---|---|
| PA-D1 | Local CLI/library demos | No hosted product |
| PA-D2 | All five existing model paths mandatory | Complete derivations cannot be dropped |
| PA-D3 | Opt-in applications-v1 schema/exit contract above | Legacy reports unaffected |
| PA-D4 | Existing 1.30.1/1.5.5 lock, bounds above | Refuse profiles beyond declared fragment |
| PA-D5 | Full public check reports, finite obligation denominator | No arbitrary equivalence claim |
| PA-D6 | Owner-selected four local plan/close readers | Same model family; no provider consensus |
| PA0 instrument | Corpus-first; no optional spec panel | Exact expected outcomes committed before successor implementation |

## Verification selection

| Obligation | Disposition / exact command (expected exit) | Input boundary and invalidation |
|---|---|---|
| C1,C3 inventory/expectations | run: `.venv/bin/python -m pytest -q tests/test_pyrel_application_corpus.py --tb=short` (0) | Five models, corpus/answers; any changed bytes rerun |
| C2,C4 actual baseline | run: `.venv/bin/python tools/measure_pyrel_applications.py --mode baseline --out .gnd-planning/milestones/pyrel-applications/evidence/PA0/baseline.json` (0) | Exporter/runtime, lock, raw fixtures |
| C2 omission | run: same driver `--mode successor` with distinct output (1 before PA1/PA2) | Guarded and derived omission; recorded red evidence |
| Legacy client/control preservation | run: `.venv/bin/python -m pytest -q tests/test_pyrel_export.py tests/test_pyrel_export_boundaries.py tests/test_public_pyrel_export_runtime_optional.py tests/test_external_runtime_tutorials.py --tb=short` (0) | No production changes; focused seam preservation |
| Broader historical/provider/native/proof/census | cadence: separately selected CI or explicit owner request | Outside PA0 impact; no broad replay |

Independent phase diff review uses process-phase's distinct-harness requirement;
the owner-selected local plan/close readers do not by themselves establish that
phase review. Record the actual instrument before claiming PA0 complete.

## Out of scope and size

No production/runtime changes, application publication, generic compiler, docs
graphics, installed-wheel acceptance or certification in PA0. Estimated driver
200 lines, corpus generation/test 300 lines, fixture data up to 15,000 lines.
Source/query correctness and future native acceptance remain PA1–PA6 obligations.

## Implementability sweep

All five model paths exist and use the admitted primitive fragment. The complete
derivation graph is blocked → eligible; no recursive support is needed. Explicit
coverage and exact report identities exist in input/public comparison surfaces.
The existing native lock installs and constructs a local DuckDB model. A real
preflight export on the BookRec seed reports three guarded unsupported entries
with completion exit 0. These are feasibility observations, not retained PA0
gate evidence. Consumer pins will be measured when the corpus lands.

## Delegated approval (auto=true), 2026-10-13

Approved specification prefix SHA-256: 574221595d4196d884bb4a55504eff46dddc6ccd097131cb1d41b244ea98150a.
Authorization: owner's named whole-milestone auto invocation; plan gate 001.
Instrument: corpus-first, separate entry/answers; optional spec panel omitted.
PA-D1–D6 and PA0 instrument rulings above are adopted after the implementability
sweep. Budget: 200 driver lines, 300 test/generator lines, 15,000 fixture lines;
60 seconds per native process, 4 MiB report retention. No production edits in PA0.
Subsequent measurements must record any refuted premise before amending its answer.

## Implementation findings and exact corpus ruling

PA0-F1: a generated dangling chain control omitted its required chain role.
Public GND admission refused it before verdicts; the corrected control keeps
the chain value and changes only expense identity. No invalid case was frozen
as a negative policy control. PA0-F2: consumer inventory initially misspelled
pyrel-export as pyrel_export; the inventory test failed (1 failed, 125 passed),
then the actual path was corrected. baseline.json retains that earlier matrix
digest; baseline-current.json measures the corrected inventory.

Delegated corpus approval (auto=true), 2026-10-13: adopt the 61 obligations
and 124 hand-narrated controls after checking every target against the public
GND report, including both missing and extra derived claims. Full GND verdict
rows are frozen measurements, not independently authored universal answers.
The target stories and expected dispositions are the executable approval
instrument; runtime agreement remains a separate native obligation.

- tests/fixtures/pyrel_applications/matrix.json: c9c2ef19fa6ec46cf7224b616ea538c7fe70dd860e2cbc4a24f36e93752b3472
- tests/fixtures/pyrel_applications/answers.json: 7bed9d8569ee8aec801dd816adb62d7658500c54b3c73473204db57517c1a9e4
- tests/fixtures/pyrel_applications/README.md: f14999654e11b2caebae1a9bdec48c1898ab7cd343f51fcd57ae1f7ebac7b7b1

124 population files are byte-identified by the native receipts. Fixture data
is 5,735 lines and 317,489 bytes, within the declared 15,000-line ceiling.
The corpus gate is 128 passed; the selected legacy gate is 72 passed,
13 deselected under existing exclusions. Distinct-harness phase review remains
pending owner instrument selection; no PA0 completion record is claimed yet.
