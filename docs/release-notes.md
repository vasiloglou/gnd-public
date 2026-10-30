# Release notes and milestones

The development package version remains 0.1.0. Publishing these unreleased
changes requires a separate release decision.

## Unreleased: why a derived fact is missing (2026-10-30)

`gnd why-not` and `gnd.api.why_not` explain a derivation that produced nothing,
or not the row you expected ([issue #66](https://github.com/vasiloglou/gnd-public/issues/66)).
GND's evaluator decides first whether the row is derived. If it is not, the
answer walks each clause in declared order. It gives the binding count after
each step and the first step that left none, with up to five of the bindings
that reached it, and explains a derived blocker's row in turn.

- New surface: one command, one API function (`why_not`, appended to
  `gnd.api.__all__`), and one output schema, `why-not.schema.json`.
- The CLI redacts population values unless `--raw` is passed; the API returns
  them, like `api.witness`.
- Exit bands: `0` blocked or derived, `2` unsupported (aggregates, prose rules,
  opaque values), `3` invalid input, `4` an unavailable term or a work limit.
- `check`, `witness` and `replay` are unchanged.

See [Why a derived fact is missing](reference/why-not.md).

## Unreleased: ILP import hardening (2026-10-30)

- The rules and Popper imports refuse a threshold their export never offered
  as `off-threshold`: a rules column the export could write but did not, and a
  Popper `ge_` or `le_` threshold name that `bias.pl` does not declare.
- An ILASP `#sum+` aggregate, or one with more than 16 terms and conditions,
  is refused `aggregate` by clause, not by a schema error.
- `tools/ilp_comparison.py` names a refusal that cites no clause, counts every
  clause as not evaluated after a refusal before the first clause, reports
  output the import refused at its reader, and exits 2 on other learner output
  it cannot read.
- `gnd import mined-rules` refuses a population whose bytes are not the run
  record's as `population-mismatch` (exit 3) before loading it, so a broken
  population that is not the bound one no longer exits 5. It counts every rule
  before any admission check, so a later rule's `too-large` is reported before
  an earlier rule's `covers-nothing` or `support-mismatch`; the exit is still 3.
- `gnd import mined-rules` refuses as `own-reference-join`, before any
  count, a mined rule with a variable whose types span two subtype families,
  or whose types' references resolve to more than one kind of value (text,
  number or boolean). The count spells such values apart or alike where the
  checker does not. The first was refused `support-mismatch`, falsely when
  the references share a kind; the second, a type under two references, could
  exit 70. Both now exit 3 by the new name. A rule over such a type whose
  values happen to be of one kind is refused too.

## Unreleased: more rule learners (2026-10-28)

The ILP bridge now has an adapter for each of five learners, and each was run
against a real learner version: once, or once per setting the owner approved. The committed outputs replay in the
documentation, so the comparison is reproducible without installing a learner.

- `gnd export ilp --target ilasp` writes an answer-set-programming task for
  ILASP, and `--target rules` a feature table for a rule-set learner such as
  RIPPER. `gnd import ilp-rules` reads both back, plus a language model's
  answer with `--target llm`.
- `gnd export ilp --target amie --population POPULATION` writes one unlabelled
  population as typed triples for the AMIE rule miner, and
  `gnd import mined-rules` brings its rules back. GND counts each rule on the
  population itself and admits the set only when every rule holds.
- The Popper adapter ran against Popper 5.0.1; its rendering now writes each
  threshold as a predicate of its own.
- Fixes at the milestone's close (2026-10-29):
  - A mined rule that joins a subtype with its supertype now counts as the
    checker does. The AMIE export spells such values by their subtype family,
    and its adapter version is now 2.
  - A mined run record must name the facts the miner read (`facts_sha256`).
    Facts the model renders differently are refused `facts-mismatch`.
  - An infix comparison of two variables, such as `C > D`, is type-checked as a
    join.
  - An ILASP constant that is not one of the export's thresholds is refused
    `off-threshold`.
  - The Popper reader keeps every rule in the solution block, and reads a bare
    `true` or `false` as a boolean.
  - A Popper threshold that the export never rendered is refused
    `off-threshold`, and the Popper export refuses an integer outside clingo's
    32-bit range as `unrepresentable`, as the ILASP export does.
  - The ILASP extractor reads every non-blank line after the timing block, so
    no learned rule after a blank line is dropped.

[Compare the rule learners on real runs](how-to/compare-ilp-learners.md)
replays every run, and the [comparison table](reference/ilp-bridge.md#comparing-the-learners)
summarizes them. Each row is a single run on a small example, not a ranking.

## Unreleased: induced knowledge (2026-10-26)

GND can now propose rules from data, and never adopts one without review.
Object types take an optional `description` that verbalization and generated
docstrings carry. A description is never checked, so it must not restate a
constraint: state the rule as a constraint instead (see the
[representation format](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/representation-format.md)).
A seventh provenance source, `induced`, records a rule found
from data, with its inducer, support and evidence digests; it
enters a model only as `proposed` and advisory, through `gnd evolve`.

- `gnd measure --labels` scores each rule against populations you labelled.
- `gnd discover` suggests constraints that hold in one population.
- `gnd export ilp` writes labelled populations for a rule learner, and
  `gnd import ilp-rules` brings its rules back after re-checking every claimed
  coverage itself; a claim it cannot reproduce is refused.
- `gnd evolve` binds a model's reference populations as `gnd validate` does.

The tutorial [Find the rule your auditors are really using](tutorials/learn-rules.md)
walks the loop on a synthetic refunds example. GND has no rule learner of its
own: the example carries a small stand-in learner script, and no real learner
has been run in its tests.

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
calculation results match. Initial IE5 wall time regressed on the measured small public
fixtures: reporter medians 5.83 s versus 6.79 s in one balanced shared-host run.
IE6 then reduced repeated policy accounting, preserving live hashing, mutation
guards, cloning and limits. In a new balanced comparison, session medians improved
9.59→9.03 s on the reporter, 2.41→1.99 s on course and 0.574→0.541 s on localized
controls against the archived pre-IE6 session. Full evaluation with receipts was
still faster in each comparison (8.50 s, 0.86 s and 0.423 s). Small shared-host
samples establish no general speedup; remaining bookkeeping stays an explicit
performance follow-up. Do not compare elapsed values across these separate runs.

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
