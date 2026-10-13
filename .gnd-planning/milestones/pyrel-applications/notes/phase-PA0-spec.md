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

## Reviewed repair amendment and delegated approval, 2026-10-13

A1/003 supersedes unconditional per-row GND/native agreement only for the two
named completeness source disagreements. Original statements remain historical;
current full native expectations are frozen separately from GND observations.
The corpus revision 2 adds 12 distinct-value uniqueness cases and one joint
claim/recommendation omission, for 137 case entries over the same 61 obligations.
Control count means addressed test scenarios, not distinct input byte hashes.

The verifier now compares complete native dispositions, every guarded witness,
derived missing/extra tuples, modality, profile/status/accepted/process exit and
exact byte bindings. Current successor mode invokes --accept, just as acceptance
mode does. Legacy mode is baseline only. The original successor mode was a
refuted premise: it incorrectly expected new warning/derivation fields from the
unchanged legacy schema. Its old red receipt is retained as omission history.

Native derived rows use derivation_ref plus status, missing and extra arrays of
role dictionaries. Zero/two-join/coverage branches are PA1 direct controls; PA0
never measured them in its original 124 fully covered populations. PA1 will
record exact native/GND normalization for those measured branches before claims.

Consumer inventory now includes RF2 rendered-program SHA pins, RF1 helper
goldens, constraint-oracle/isolation consumers, layer map and runtime/CLI docs.
Historical goldens remain frozen; PA1 must route any actual rendered-source
change through the named authenticated successor policy, never recapture old goldens.

Current baseline command targets evidence/PA0/baseline-r2.json (expected 0);
current successor command targets evidence/PA0/successor-r2-red.json (expected 1
before the new profile exists). Select fresh output names on a rerun; the driver
rejects occupied output before native work. Public CLI export uses relative model
labels, stable UTF-8 encoding, pre-run byte hashes and post-run stability checks.
The raw corpus/receipt caps and explicit version/error checks do not depend on
Python assertions.

Adopt these repaired design/corpus meanings under existing auto=true delegation.
No new production code or phase completion is authorized by preparation alone.
Exact revised corpus hashes:
- tests/fixtures/pyrel_applications/matrix.json: b102ac2dcb19a2b7dc5c6a43b14cb436f8f043e7c503e9607f4ac8806d381c09
- tests/fixtures/pyrel_applications/answers.json: db902a387cbbae4b1c87bf0bafed03e66f27b9741439d980e808a716998a00ba

Review convergence before round two: 11 retained initial items; reproduced
blocking 4/11 (R1 contract impossibility, R2 false driver green, R3 legacy
successor contradiction, R4 missing affected-consumer routing); self-inflicted
0/11 (no prior repair round). R5/R6/R7/R10 are corpus/verifier hardening and
fixed within their owned deliverables. R8 is completeness corrected now because
incorrect finance/positive stories determine corpus approval. R9's original
coverage discharge claim is narrowed to PA0's measured boundary; its actual
unknown/vacuous cases remain PA1. R11 is informational; model labels are source
provenance, exact hashes bind the variant. Round two is one focused Claude repair
review, with no third round; new blocking findings require measured disposition.

## Final owned hardening disposition and corpus approval

Claude round two found no blocker. Its current complete-model recomputation
confirms all native expectations and exactly the two A1 disagreements.
F1: frozen approval.json and tests now enforce native answers/hash/exclusions,
including the joint case's obligation link. F2: 13 added inputs actually run
in native legacy mode: 12 distinct uniqueness violations; the joint derived
claim has no derivation verdict. F3: array placement, identity/type/reason and
witness shape now reject malformed native rows. F4: non-object/malformed/oversized
reports produce recorded mismatches, not a pop-before-validation traceback.
F5: semantic/manifest/primitive-ambiguity/registry consumers are inventoried.
F6: actual uniqueness index is used and the unused driver map is removed.
F7: current navigation and fixture entry point are updated; historical 002 keeps
its old scope. No native acceptance is credited to mocked checker tests.

The row-placement vulnerable logic was reproduced through an exact inversion
of the added F3 checks, retained as reconstructed pre-fix logic rather than an
original-file replay. Original target-only driver and witness-key regressions
have actual pre-fix red streams. New corrupted-report/schema/hash controls are
green. Subsequent hardening has root execution evidence; Claude's opinion is
limited to its reviewed bytes, not falsely extended to these later edits.

Round-two convergence: 7 findings; 0 blocking; self-inflicted 5/7 (F1/F2/F3/F6/F7),
ceiling Medium-Low. F4's pop boundary and F5's incomplete consumer routing
predate the repair. The >1/2 rule and the declared one-repair budget stop further
prose rounds; next instrument is implementation. These are concrete owned
hardening fixes, not a claim of a third independent opinion.

Explicit delegated budget amendment: driver 200 -> 240 lines; tests 300 -> 380.
Actual 207/329 exceeds original estimates by 7/29; the revised ceilings retain
33/51 lines of headroom for required verification, not added product scope.
Original estimate misses remain recorded. Current fixture data remains beneath
the original 15,000-line ceiling; recovered intermediate receipts are evidence,
not new domain fixtures.

Adopt the final approval.json snapshot and native key under the named auto=true
authorization and A1/003. Fresh corpus/driver gate is 151 passed (exit 0); expanded
legacy/isolation gate is 77 passed, 13 deselected (exit 0). Native additions are
13/13 completed audit processes (exit 0); acceptance remains a deliberate red.
Final snapshot identities:
- tests/fixtures/pyrel_applications/matrix.json: 4fbb82a5188d60ff27f10d0cba462744e0cc6cce050eb8a9e5733862ca3ba57c
- tests/fixtures/pyrel_applications/answers.json: db902a387cbbae4b1c87bf0bafed03e66f27b9741439d980e808a716998a00ba
- tests/fixtures/pyrel_applications/approval.json: b380a31b92297a00d66997ad87da790ee51868bb4a33b984d525c15a36f735b7
- tests/fixtures/pyrel_applications/README.md: b307a40da8c9d26b454f5e804d263b60c37849a8514d4dbc7580e1bdbe04b578
