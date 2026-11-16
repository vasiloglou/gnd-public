# LD3 · Replayable reading and coverage

Status: delegated approval recorded in the LD3 spec gate.

## Provenance

[Plan r3](literature-depth-plan.md) assigns LD3 the part 7 workflow and its
stronger absence evidence. [LD1](../004-phase-LD1.md) supplies the rooted
molecular model, immutable source excerpts and saved extraction practice.
[LD2](../006-phase-LD2.md) records the time-anchor selector and exact decimal
worked fixture. The reviewed part 7 plan is bound by the
[plan gate](../002-plan-gate.md). The LD2 numeric workflow is a separate existing
consumer. The reading example uses the existing text predicates needed to
establish the methods recovery.

## Obligations

| Source | Obligation | Control |
|---|---|---|
| #193 part 7 and plan §4 LD3 | Six ordered stages, exact evidence and provider-free replay | T1, T2 |
| #193 part 7 criteria 2, 3, 7 | Recover the methods-only assertion, record absent methods, and preserve a reported violation | T3, T4 |
| §0 and §4 | Evidence binding, bounded rooted parser, digest-checked roster and independent question coverage | T1, T5, T8 |
| §4 | Carry changes to the vocabulary worklist, retain missing, refused and empty observations, and count all attempted inspected bytes | T3, T5, T6 |
| §4 and §9 | Required coverage, exhausted evidence and exhausted budget are distinct terminal states | T6 |
| §2 and §4 | Stronger absence uses typed scope coverage and adequate independent measured fidelity | T7 |
| §4 and predecessor LI1 | Activate its optional coverage view with frozen exact floors | T9 |
| Plan §5–§7 | Document, ship and independently verify the installed host workflow; preserve part 10 deferral | T10 |

## Standing rules

- **Meaning and provenance.** A reported constraint violation remains an
  observed fact population and has failed check status. A coverage row states
  what was inspected or unavailable. It carries no implied scientific support.
- **Totality and input cost.** Read bounded UTF-8 and strict JSON from
  fixed fixture and run roots. Cap declared file/row counts. Index
  source ranges and question IDs once per run. Test duplicate IDs, invalid
  spans, unlisted paths and oversized retained evidence. The time-bound
  workload probes stage artifact validation with a bounded roster.
- **Validation order.** Check trusted manifest and source bytes first.
  Check step ordering and exact roster before reading retained outputs.
  Verify each output and coverage relation before reporting replay success.
  A missing or stale output carries incomplete status.
- **Shared walk.** Derive the applicable review, coverage and revisit outputs
  with the same ordered stage evaluator on fresh and replay paths. A replay
  implementation supplies its retained results through the replay input seam.
- **One normative home.** The packaged README owns the stage evidence layout
  and modes. The existing command contract owns extraction and fidelity.
- **Measure the contested route.** A counting producer receives both broad
  and targeted requests on fresh runs. Replay has zero calls. Tests consult
  both outcomes, a real GND check and a measured positive fidelity denominator.

## Design

| Capability | Catalog searches | Reuse decision |
|---|---|---|
| Saved extraction | `extract verify saved responses fidelity cases`, `rooted extraction include projection` | Use the public extract, verify and check routes with the existing bundle and population shapes. |
| Evidence | `assurance reading coverage passage denominators`, `work passages evidence receipt` | Reuse bounded artifact readers, canonical JSON and exact coverage metric reporting. New workflow record stays in the example. |
| Fidelity | `saved responses held-back source populations`, `extract verify saved responses fidelity cases` | Use public fidelity over separate held-back source and candidate responses. |
| Worklist | `targeted reading scope vocabulary revisit`, `assurance reading coverage passage denominators` | The reading workflow needs source ranges associated with declared dependency keys. LD4 consumes the rule's artifact identities later. |

`gnd.examples.literature.reading` exposes fresh and replay through
`main(argv: list[str] | None = None) -> int`. Modes are
`run --out DIR [--budget-bytes N] [--scenario full|unavailable]` and
`replay RUN`. Exit 0 means the selected run ended with one of the
declared reasons and supplied its report. An invalid or stale stage is
incomplete at exit 3. A valid incomplete evidence scope still has its
declared reason and rows; it cannot issue the stronger absence claim.

The fixture is rooted beside the packaged examples. The input roster
declares source IDs, versions, relative local source paths and SHA-256
hashes. Sections use `{id, source, kind, span, keys}` with sorted
nonoverlapping byte ranges; the available kinds are section, equation
and table. An unavailable section has null span and a reason. Only
present source scopes are read. Compare each source digest before spans
can acquire evidence. Source and section IDs are unique. Questions use
`{id, section, key, required, superseded_by}`; the last field is
nullable and names a different declared question. Validate a
supersession graph for unknown targets, self-loops and cycles before
using a question. Keep not-applicable evidence and explicit denial
distinct from a negative result of scanning.

The six records appear in this order: `inventory`,
`broad-extraction`, `selection`, `targeted-extraction`, `review`,
`recheck`. Each has `{stage, purpose, inputs, predecessor_sha256,
payload_sha256, inspected, questions}`. Hash all emitted records and
outputs using canonical JSON and actual input bytes. The run manifest
pins the exact stage roster plus companion coverage, gold fidelity,
closure and scope artifacts. Replay validates the complete stage roster
and claimed file pins against its supplied case and independently
rederives the states using saved stage payloads. If anything relied on
by a stage changes or is missing, replay reports incomplete. Producer
adapters never run on replay, including a stale replay path.

The broad producer reads the available opening ranges; targeted
selection uses unresolved keys and available ranges. Each recorded
inspection carries source/version, section ID, start/end, bytes and
producer outcome. The adapter's returned extraction evidence is bound
to those exact bytes. A fresh run uses both producer steps and records
actual calls by stage. A report's read cost sums each attempt's inspected
bytes, including repeated ranges and attempted empty or refused extraction.
Uninspected omitted or unavailable ranges count in the roster and contribute
zero bytes. The reading report identifies the supported fact gain and
newly resolved questions alongside the cost and retained denominators.

The required method assertion uses the molecular model's `approximation`
predicate. It is absent from the broad result and appears in targeted
verify/check. The synthetic source control returns both conflicting label
facts; its retained verification and check both fail without changing
the population. The not-found, unavailable, not-applicable and explicit
denial states use different source or applicability evidence. Each
question ends resolved, retained with reason or superseded with a valid
target. Required adjudications control stop reason. The order is
completed required coverage, budget prevented an available read, or
available evidence exhausted. The full, unavailable-method and budget
runs exercise each reason independently.

Coverage rows carry `{source, section, state, inspected}`, where state
distinguishes `supported`, `inspected-not-found`, `unavailable`,
`not-applicable`, `explicitly-denied` and `omitted`. A declared
vocabulary key reopens an earlier matching section by a deterministic
source/section lookup. The run report retains this list and its inputs
for LD4. The assurance report's new opt-in coverage stanza binds a
run-scoped coverage record by digest and compares its exact roster against
independent expected rows from the answer key. Precision and recall floors
are both 1/1 with a positive denominator. If both sides omit this stanza,
the legacy coverage stage stays dormant.

The stronger absence gate needs four authenticated inputs: closure, scope,
coverage and measured fidelity. Scope names the exact relevant source
and section keys. Closure fixes that roster and the question's predicate;
coverage must show that all scoped ranges were examined. The controlled
claim asks whether a named alternate setting is reported in the declared
small source scope. The held-back fidelity denominator is two positive
facts. Score both a 2/2 and a 1/2 response over the same in-scope held-back
material using `gnd fidelity`. The qualifying recall floor is 2/2. An
independent validation of each input must fail on omission or stale bytes.
The issued result describes the finite fixture scope only.

## Decisions

| ID | Delegated disposition |
|---|---|
| D1 | Fresh run consumes local saved responses through an observable producer; replay consumes retained evidence. |
| D2 | Keep the recorded reported conflict and its real public check results. Preserve all states and denominators independently of check admission. |
| D3 | Charge read-byte lengths per attempted producer range; full, unavailable and budget cases freeze stop outcomes. |
| D4 | Require two checked fidelity reference facts and a 2/2 recall floor for the stronger absence control. A 1/2 measurement must refuse that claim. |
| D5 | Activate the assurance coverage stage when both new inputs are present. Require separate roster evidence. Corpus-first gate, no optional spec panel. |

## End-to-end tests

| Test family | Expected observations |
|---|---|
| T1 | Six exact stage records and public route results. Fresh summary names the actual positive producer counts; fresh and replay stage bytes agree. |
| T2 | Replay invokes zero producers. A missing stage, corrupted output or independently re-pinned wrong semantics is incomplete, exit 3. |
| T3 | A methods fact enters targeted extract/verify/check, each exit 0. Broken source bindings fail; unavailable and negative evidence remain distinct. |
| T4 | Reported conflict is retained; public verify and check exit 1 and the row stays visible. |
| T5 | Each question has one disposition. Omitted, duplicate, empty or invalidly superseded roster refuses exit 3. A relevant old source is revisited and unrelated content is excluded. |
| T6 | Each stop reason is reachable. Report exact repeated/empty/refused/omitted attempt counts and read cost, including budget-zero control. |
| T7 | Real 2/2 qualifies. Real 1/2, missing closure, missing scope, missing coverage and missing fidelity each refuse a scoped absence claim. |
| T8 | Invalid or oversized input and malicious relative paths fail closed. Bounded stress verifies the roster pass. |
| T9 | Optional LI1 coverage stage passes exact rows, fails incomplete/mismatching rows and retains the legacy absence behavior. |
| T10 | Installed fresh and replay operate over the same packaged fixture and preserve report identity. |

The focused gate includes direct LD3 tests, LI1 assurance, LD1–LD2,
rooted extraction and fidelity consumers. Run the structural guard list,
whole-tree Ruff and strict component checks when code changes. Record
the separately invoked installed commands. Existing broad cadence applies.

## Boundary and size

The example evaluates a bounded public authored fixture with saved
responses. The release freshness consumer and dependency recipe belong
to LD4. Part 10 remains deferred. Estimate 350–500 implementation lines,
120–220 test lines and the input corpus.

## Approval instrument

Commit the public red corpus under `tests/test_ld3_reading_workflow.py`
and `tests/fixtures/ld3-reading/expected.json`. The expected output file
is distinct from all workflow inputs.
