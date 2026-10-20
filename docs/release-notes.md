# Release notes and milestones

The development package version remains 0.1.0. Publishing these unreleased
changes requires a separate release decision.

## Unreleased: opt-in incremental evaluation (2026-10-20)

`api.EvaluationSession` reuses eligible extension components and constraint findings
across loaded snapshots while keeping the normal public report semantics. Host
observations pass through normal population validation; separate bounded version-1
counts feedback supports ordered attempts. Persistent experiment wires and existing
stateless defaults keep their contracts. Receipts now consume a private report copy,
so changing their public report cannot alter a later transition. Failed receipt
minting also avoids a repeated checker invocation.

The frozen public reporter replay executes 4,878 rule bodies with receipts and 179
with sessions plus receipts. Complete reports, branches and ordered logical
calculation results match. Wall time regressed on the measured small public
fixtures: reporter medians 5.83 s versus 6.79 s in one balanced shared-host run.
Counted savings do not establish elapsed-time gains; bookkeeping remains a named
performance follow-up.

The session is in-process and bounded to one generation, 100,000 retained rows and
32 MiB projected cache content by default. Unknown/reference/observer modes and
oversized units compute fresh. Current witness/lineage/unavailable state remains
part of parity checks. Profiling and balanced measurements are recorded with the
incremental-evaluation milestone; timing is workload-specific and is not a claim
about the offered 547-program workload, which has not been supplied. No production
publication or fresh certification is implied.

## Earlier transition-check work

Checks and transitions do less internal work. Each public call now computes the model's index key once, and the checker reads fact types without copying them. Results are unchanged. On a 13-call plan workload, GND time per call fell by about a third.

`api.check_with_receipt` now allows receipt-bound reuse of a transition pre-state check. On the same workload, it cuts checker runs from 25 to 19.

## Documentation for agentic data apps

The documentation is reorganized around agents: GND as skills plus Python, an executable
ORM ontology with ORM 2 diagrams, a "Work with an agent" section covering every skill,
a capabilities tour, a runnable plan-checking example (`approvals`) and an offline,
runnable development-session loop, plus recorded Claude Code, Codex and hosted-model sessions on one task. GND's lineage from GSD is documented, with a guide
for adopting a GSD project.

## Phase 4.1 documentation and applications

A navigable documentation site introduces GND, its supported capabilities and
stable Python API. BookRec teaches application development, hard rules, advisory
warnings and model evolution. Expense approval teaches policy checks and a
currency evolution. Both include synthetic inputs, runnable checkpoints and
instructions tested directly from Markdown. Dispatch remains the short first check.

## Acceptance status

Phase 3 accepted its recorded candidate on macOS/Python 3.13 and Ubuntu/Python
3.11. Phase 4.1 changes documentation and packaged tutorial resources; prior
artifact hashes do not describe these changes. Focused tutorial/build validation
and the final Phase 4 candidate sign-off are distinct. Phase 5 owns publication.

Independent external-user trials and the publishing service rehearsal remain
unmeasured. Optional provider/native profiles have separate prerequisites. No
fresh certification was requested; unavailable assurance is not inferred from
passing application checks.

## Development milestones

GND was built in a series of development milestones before its first public release.
Milestone numbers are not package versions; 0.1.0 is the first public release and
contains the public parts of all of them.

| Milestone | Date | What it added |
|---|---|---|
| v1.0 Core framework | 2026-08-17 | The ORM YAML format and `validate`; the population checker with alethic and deontic modality and verdict bands; `synth` and `measure`; the document round trip; code generation and conformance; data-driven sessions with closed feedback; model evolution and recovery; the review panel; packaging with `gnd install` |
| v1.1 Dogfooding repairs | 2026-08-18 | Acceptance by constraint satisfaction with coverage floors; digest-only expected answers, so no answer key sits on disk |
| v1.2 Milestone records | 2026-08-19 | Append-only planning records written by the skills; `gnd-new-project` |
| v2.0 Operations | 2026-08-25 | Operations with preconditions, effects and frames; transition checks with the frame check; sealed-test sessions; `gnd solve`; `gnd coverage`; `gnd-adopt` for GSD projects |
| v3.0 Guarded rules | 2026-08-28 | Guarded constraints; promoting advice to a hard rule through evolution; the BookRec application |
| v4.0 Architecture contracts | 2026-08-30 | Declared architecture contracts, a static architecture conformance check and smoke runs |
| v5.0 Derived fact types | 2026-09-01 | Structured derivations with stratified negation; incomplete and unsound derived-claim verdicts |
| v5.1 First outside user | 2026-09-04 | Generated projects that run outside the repository; evidence bound to the model's digest; the sixth review seat |
| v5.2 PyRel | 2026-09-05 | `gnd export pyrel`, a standalone program that runs locally on DuckDB |
| v6.0 Verified kernel | 2026-09-17 | A checker kernel verified with Nagini and the `proof-backed` assurance label; the evidence bundle is development-only, so public builds report `unavailable` |
| v6.1 Outside consumers | 2026-09-25 | `gnd.api`; batch checks; plan mode; witness redaction; walk floors; declared command and OpenAI-compatible adapters; `gnd import rai-orm` |
| v6.2 Composed semantics | 2026-09-25 | Operations and derivations in one model; exact integer arithmetic; aggregates; floats with explicit undefined cases |
| v6.3 Test lanes | 2026-09-28 | Faster evidence loading and separated test lanes (maintainer-facing) |
| v7.0 Theory core | 2026-09-29 | Source anchoring; recursion; opaque values and per-fact admission; three-valued derivations; `gnd verbalize population`; `gnd diff` |
| v7.1 Portable evidence | 2026-09-30 | Calendar dates and durations; immutable reference populations; witnesses and replay; patch and ranking sessions; saved-judgment gates; Soufflé and Lean exports |
| v7.2 Reliability | 2026-10-01 | Stricter session and admission consistency; one shared evaluator path |
| Public launch | 2026-10 | The public repository, packaged examples, this documentation site with executable tutorials, and the external-runtimes path |
