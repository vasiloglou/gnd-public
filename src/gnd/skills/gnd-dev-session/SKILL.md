---
name: gnd-dev-session
description: Drives GND's data-driven development session — `gnd exp init` to declare the questions, a versioned session contract binding inputs and a verifier plus exact outputs, constraint floors, sealed tests, or a transition walk, `gnd exp run` to invoke a bounded legacy or locally declared adapter, and `gnd exp close` as the separate completeness gate. Use when asked to "run a data-driven session", "run gnd exp run", "author a session contract", "drive the agent against the verifier", "interpret a session outcome", or "close an experiment". Exit 0 means every required case met its declared acceptance mode; 15 is every well-formed nonaccepted session, whose terminal disposition is one of agent-failure, verifier-failure, stagnation, oscillation, or budget-exhausted (`retry` is non-terminal and never appears in a final result); 3 rejects malformed or digest-mismatched input before an agent starts; 14 is the separate close gate refusing an experiment that has not discharged what it declared. Every attempt is retained as immutable evidence; transition sessions use closed answer-free feedback that exposes operation outcomes but never private bindings, schema-version-5 contracts can add walk floors, and schema-version-6 contracts select a caller-supplied command or OpenAI-compatible policy by id. Not for checking whether generated code still matches its model (gnd-conformance), generating or regenerating the project (gnd-codegen), independent review of an outcome bundle (gnd-review-panel), or checking a population directly against a model (`gnd verify`).
---

# GND Dev Session

## Separate in-process host loops

The Python api.EvaluationSession is a separate opt-in host loop. Its validated
whole-relation observations and bounded counts-only evaluation-session-feedback
version1 do not modify this skill's persistent contracts, feedback versions or
retained attempt evidence. Cache handles are process-local and never serialized.
Use this skill for the persistent experiment workflow described below.

## Summary

**What:** one bounded loop over one experiment directory. A `kind: data-driven`
experiment binds an agent to a versioned contract — input blobs, a verifier,
and either byte-exact outputs or checker coverage floors. Every committed blob
is bound by `sha256` and `size_bytes`. `gnd exp run` drives the
input→agent→output→verify cycle until every required case meets its declared
acceptance relation or a bound is hit. Every attempt is retained as immutable
evidence, and closing the experiment is a separate gate with its own command.

| You do | A validator discharges it |
|---|---|
| declare the questions and author `session.contract.json` | `gnd exp init` refuses a spec declaring zero questions; `gnd exp validate` refuses a malformed SPEC.md at **3** |
| run the session and read the exit band | `gnd exp run` — each required case is judged by its explicit exact-bytes or constraint-satisfaction branch |
| interpret the disposition and the retained evidence | nothing — reading the evidence is the part only you can do |
| record the answers in `CONCLUSIONS.md` and close | `gnd exp close`, which refuses at **14** while any declared question is unresolved |

Skill prose explains; validators discharge. If you find yourself reasoning
about whether a session "basically passed", read `result.json` and the exit
code instead — the disposition is a recorded fact, not a judgment call.

**When to use:**
- The model is validated, the verifier is trusted, and an agent must now be
  driven against that verifier under a bounded, digest-pinned contract
- A development question ("does the agent converge within N attempts?") needs
  an answer a reviewer can recompute from a committed tree
- A previous session was not accepted and you are authoring the next run

**When NOT to use:**
- Asking whether generated code still matches its model — [`../gnd-conformance/SKILL.md`](../gnd-conformance/SKILL.md)
- Generating or regenerating the agent project — [`../gnd-codegen/SKILL.md`](../gnd-codegen/SKILL.md)
- Independent readers over a closed outcome bundle — [`../gnd-review-panel/SKILL.md`](../gnd-review-panel/SKILL.md)
- Changing the model the session exposed as wrong — [`../gnd-model-evolve/SKILL.md`](../gnd-model-evolve/SKILL.md)
- Checking one population against the model, no agent involved — that is
  `gnd verify` (or `gnd check`), and its band contract lives in
  [`../gnd-orm-core/references/population-format.md`](../gnd-orm-core/references/population-format.md)
- Looking up the ORM YAML spec or the population format — [`../gnd-orm-core/SKILL.md`](../gnd-orm-core/SKILL.md)

## Workflow

### 1. Declare the experiment

```
uv run gnd exp init EXP-001-contact-roster --out . --kind data-driven \
  --question "Q1=Does the agent converge to a model-conforming roster within two attempts?"
```

The id must match `^EXP-\d{3}-[a-z0-9][a-z0-9-]*$` because the id IS the
directory name. `--question ID=TEXT` is repeatable, and every declared id must
be answered to close. A SPEC declaring **zero** questions is refused at
declaration time — both of the close gate's set differences would be empty, so
it would close having established nothing. An existing experiment directory is
refused at **11**, never overwritten, and there is deliberately no `--force`.

### 2. Author the contract

Write `session.contract.json` beside `SPEC.md`. Each case binds every input by
`sha256` and `size_bytes`, and its verify block binds the model the same way
(the model format is specified in
[`../gnd-orm-core/references/representation-format.md`](../gnd-orm-core/references/representation-format.md)).
Schema version 2 makes the acceptance choice explicit at the case level:

- **`exact-bytes`** — choose this only when byte identity is the question.
  Declare at least one `expected_output`; verifier success AND byte identity at
  every `candidate_path` are acceptance-binding. `comparison` remains the
  closed literal `"exact-bytes"`. Derive expected bytes from a trustworthy
  source such as `gnd synth`, not from an improvised hand-written answer. Do
  not copy its digest into the contract or leave its bytes under the experiment
  root by hand. Put the produced file under the experiment root temporarily
  and run:

  ```bash
  gnd exp author-expectation EXP-001-contact-roster \
    --case contact-roster-exact --output-id population \
    --candidate-path population.json --from authoring/population.json
  ```

  The command safely reads and hashes the source, inserts or replaces the
  selected pathless expectation, removes the source, scans every regular file
  under the experiment root for equal bytes, atomically replaces the contract,
  and reloads it through the production reader before exit **0**. The entry has
  no `path` and no `size_bytes`. An exact-mode draft may temporarily have an
  empty `expected_outputs` array solely so this command can insert its first
  output; such a draft does not load and cannot be run until authoring exits 0.
- **`constraint-satisfaction`** — choose this when any population satisfying
  the bound model is an acceptable answer. Use verifier command `check` and
  declare task-specific `coverage` floors. Every floor names a model fact type
  and has `min_facts >= 1`. Floors are mandatory and explicit: omitting them
  permits no constraint-mode case, while automatically flooring every model
  fact type would wrongly forbid legitimate partial-population tasks.

Constraint mode authors **no answer key**: no `expected_outputs`, no
`expected/` directory, no expected digest or byte target in prose. A checker
band 0 is necessary but not sufficient there. The session compares each
floor against the checker's reported `coverage[FACT_TYPE].facts`; candidate
declarations do not count and a missing row observes zero. A deficient floor
is a session-level rejection at parent exit **15**, while the retained checker
payload remains band **0**. Normative checker bands, including globally empty
band 2, live only in the population-format reference linked below in step 4.

### Sealing a committed test suite — schema version 3

Schema version 3 adds a third acceptance mode for the case where a **committed
test suite** is the question rather than a population.

- **`tests`** — the case carries **no `inputs` and no `verify`**; the reader
  refuses both, because in this mode the suite is the verifier. Declare
  `results_format`, `results_path`, and:
  - **`protected[]`** — every file the agent must not weaken, bound by `path`
    and `sha256`. The digests are verified **three times**, and the three
    boundaries report differently, so know which one you are seeing: a
    mismatch present **before the run** refuses the contract outright at exit
    **3**, with no run directory written; one appearing **before the child is
    spawned** ends the session with `tests:verifier-io`; one made **by the
    running suite** ends it with `tests:protected-mutated` at exit **15**.
  - **`required_tests`** — the exact test node ids the run must report passed,
    **relative to the candidate root**, which is what the child's working
    directory is. A node id that no collected test matches is a failure, not a
    skip.

Seal the thing that decides, not just the thing that is decided: if a test
reads a fixture, the fixture belongs in `protected[]` beside the test, or the
agent can pass a sealed assertion by rewriting what it asserts over.

**When the sealed suite is the emitted `test_architecture_smoke_<package>.py`,
its node ids are `test_smoke[<id>]` with `<id>` taken verbatim from the
architecture contract's `smoke[].id`** — the loader refuses an id containing a
bracket or whitespace precisely so this bridge holds. Seal the contract itself
alongside the module: the module has no behaviour of its own, and every row it
runs is declared in the contract.

### Asking for a transition walk — schema version 4

Use **`acceptance.mode: transition`** when the candidate is an operation walk
rather than a population. The case binds one digest-bound pre population in
`inputs[]`; its transition verifier names that same path in `pre`. The agent
owns the candidate steps and optional candidate post, so `steps` and a non-null
`post` must be normalized candidate-relative paths and must not also appear in
`inputs[]`. A null post asks the verifier to compute it; a path asks for the
ordinary declared-post audit. Acceptance is exactly verifier band 0.

Transition feedback is schema version 5. Each transition case row names only
its case id, role, band, and the ordered step index, operation id, and outcome --
never bindings or witnesses, offending facts, messages, expected values, or
paths. Mixed version-4 contracts may combine transition with the older modes;
each case retains its validator while the attempt uses one version-5 envelope.

### Requiring and forbidding walk operations -- schema version 5

A schema-version-5 contract may add `acceptance.walk` to transition cases.
`required_ops` rows name an operation and a `bindings_subset`; one submitted
step must match that whole subset, while an empty subset means any step using
the operation. `forbidden_ops` names operations that must not appear. Both
arrays are present and at least one is nonempty. Every name and subset value is
validated against the digest-bound model before a run starts.

The transition verdict always comes first. A refused walk or a nonzero band is
never rescued by a floor. Only exact band 0 is checked for required and
forbidden operations. A missing requirement or present forbidden operation
keeps the verifier's band-0 payload unchanged but makes the session
nonaccepted at parent exit 15.

These sessions use feedback and attempt schema version 7. Their
`unmet_walk_floors` rows expose only `required-op-missing` or
`forbidden-op-present` plus the operation id -- never expected binding keys or
values, observed values, witnesses, messages, or paths. Result schema version
5 binds the exact contract digest and records per-case declaration counts and
whether each floor set was discharged. Contract versions 1-4, feedback and
attempt versions 1-6, and result versions 1-4 retain their closed meanings.

### Selecting a local adapter policy -- schema version 6

A schema-version-6 contract replaces the closed legacy adapter name with
`adapter.policy_id` and the single optional parameter `model`. It never stores
an executable, argv, endpoint, credential name, header, environment allowlist,
or policy path. The caller supplies those trusted local choices separately:

```bash
uv run gnd exp run EXP-001-contact-roster \
  --adapter-policy /trusted/local/adapter.policy.json
```

The policy is strict JSON and exactly one of two kinds. `command` declares an
exact executable/argv template, a version probe, `argv` or canonical-JSON
`stdin` prompt transport, and a non-credential environment allowlist; it never
uses a shell. `openai-compatible` declares an HTTPS base URL (or IP-literal
loopback HTTP for a local probe) and the name of a required credential variable.
It sends one non-streaming request, follows no redirect, retries nothing, rejects
tool calls, and accepts only one closed base64 file bundle. The contract model
must agree with policy use exactly.

The policy is caller-trusted configuration, not committed experiment input.
GND retains its raw digest and sanitized policy identity, never the path,
endpoint text, credential name or credential value. That redaction is not a
sandbox: a command can affect anything its operating-system process can reach,
and a remote service receives the prompt. Resume requires the same policy bytes.
Contract versions 1-5 still require exactly one `--adapter claude|codex` and
forbid `--adapter-policy`; version 6 does the inverse.

#### Grounding the expectations — when synth and measure earn their keep

This is the decision guide Station 2 of the solve walk points at. Synthetic
grounding is justified when a case's evidence must be independent of both the
agent under test and your own improvisation:

- **Exact-bytes cases** need expected bytes from a trustworthy source.
  `uv run gnd synth MODEL --out corpus --class all` emits labelled
  populations — conforming, violating, and edge — each with a provenance
  sidecar. Pick the corpus artifact whose label matches the case's question
  and route it through `gnd exp author-expectation` exactly as above; the
  command, not you, hashes and inserts it.
- **Constraint-coverage floors** are guesses until measured. When floors need
  grounding, `uv run gnd measure MODEL --populations corpus` reports observed
  per-constraint rates; set `min_facts` from what the corpus actually
  exercises, not from intuition.
- **Corpus to contract:** a selected corpus artifact enters a case either as
  a digest-bound input blob or, through `author-expectation`, as an expected
  output. The contract binds bytes, so a regenerated corpus is a new contract
  version, never an in-place swap.

For small reversible MVP work, a focused **hand-authored input fixture** plus
constraint-satisfaction floors is enough — skip the corpus. The one thing a
hand-authored fixture never supplies is an exact-byte *expectation*: those
come through `author-expectation` from a source such as `gnd synth`, or the
case belongs in constraint mode.

Schema-version-1 contracts remain strict exact-byte contracts. They normalize
to exact mode only in memory; their bytes and digests do not change. Readers
dispatch version 1 and version 2 before parsing and reject cross-version fields.
A resumed version-1 contract may append schema-version-2 attempt, feedback, and
result leaves; replay reads every immutable leaf by its own version and never
migrates or rewrites earlier evidence.

Then check the declaration:

```
uv run gnd exp validate EXP-001-contact-roster
```

This reads `SPEC.md` only — it confirms the experiment's declared structure
(id, kind, question ids), exiting 0 when well-formed, **3** when the spec is
unparseable or disagrees with its own directory name, **66** when `SPEC.md` is
missing entirely. It does not read the contract; the contract is checked by
`gnd exp run` itself, which refuses malformed or digest-mismatched committed
input at **3** before any agent starts.

### 3. Run the session

```
uv run gnd exp run EXP-001-contact-roster --adapter codex
```

For contract versions 1-5 the adapter vocabulary remains **closed**:
`--adapter claude` or `--adapter codex`. Version 6 instead requires the local
`--adapter-policy` route above. Supplying both selectors, neither required
selector, or the selector for the other contract generation is usage exit
**64**. `--wall-seconds` may only **tighten** the contract's positive finite
wall bound; a loosening is also 64.

### 4. Read the band and the disposition, do not translate them

| Exit | What it means | What to do |
|---|---|---|
| **0** | every required case met its declared acceptance relation — disposition `accepted` | record the evidence pointer and acceptance mode, then go to step 5 |
| **15** | a well-formed session that did not accept | read `result.json` for the disposition; see below |
| **3** | malformed or digest-mismatched committed input | fix the contract or the artifact; no agent ran on stale bytes |
| **64** | usage error, including a wall-bound loosening | fix the invocation |
| **66** | a required artifact or the selected adapter is missing | nothing ran; this is **not** a failing session |
| **70** | an internal defect in gnd itself | report it; the session claim is void |
| **74** | a path or I/O operation was refused | says nothing about the agent or the data |

The disposition in `result.json` is one of exactly six terminal values:
`accepted`, `agent-failure`, `verifier-failure`, `stagnation`, `oscillation`,
or `budget-exhausted`. The per-attempt feedback envelope has the seventh,
non-terminal `retry` value. A **run's** terminal disposition at 15 names why
it stopped — the agent process failed, the verifier harness failed (exit 70
from the child is terminal harness failure), the exact candidate/signature
pair recurred (`stagnation`/`oscillation`, with the attempt it was first seen),
or a budget ran out (`budget-exhausted` covers both the wall bound and the
attempt bound, and its reason says which). Child verifier exits 1 through 4
are retained as case evidence and never become the parent exit — the band
contract for those verdicts is
[`../gnd-orm-core/references/population-format.md`](../gnd-orm-core/references/population-format.md).

The retained evidence under `runs/` has a fixed shape:

```
runs/run-0001/attempts/0001/agent.stdout
runs/run-0001/attempts/0001/agent.stderr
runs/run-0001/attempts/0001/attempt.json
runs/run-0001/attempts/0001/candidate.inventory.json
runs/run-0001/attempts/0001/candidate/...
runs/run-0001/attempts/0001/feedback.json
runs/run-0001/attempts/0001/verifier/<case_id>.json
runs/run-0001/best.json
runs/run-0001/launches/0001.json
runs/run-0001/result.json
```

`attempt.json` is the manifest-last **immutable commit point** for its
attempt; `best.json` and `result.json` are **separate claims** and are never
folded into it. `feedback.json` is what the agent got back after a rejected
attempt: a closed current-attempt machine record — the disposition, per-case
verdict counts, and the contract and candidate digests — with controller prose,
filesystem paths, timing, streams, best-so-far and cumulative history
**forbidden fields**. Snapshot feedback schema version 2 selects one acceptance
branch; transition sessions select the closed version-5 row described above,
or version 7 when `acceptance.walk` is declared:

| Current condition | Answer-free retry record |
|---|---|
| exact mismatch | output id plus `absent`, `differs`, or `matched`; never expected bytes, path, digest, or size |
| checker band 1 | failing constraint reference/type/modality/reason, checker message, and offending candidate facts |
| checker band 3 | normalized population issue rule/severity/path/message |
| checker band 2 | vacuity findings, plus any applicable coverage gaps |
| checker band 4 | unchecked alethic constraint references and reason codes |
| checker band 0 with a deficient floor | fact type, required count, observed checker count, and checker declaration state |
| transition band 1/2/3/4 | case band plus each step's operation id and accepted/violated/inadequate/indeterminate outcome; no bindings or witnesses |
| transition band 0 with an unmet walk floor | operation id plus `required-op-missing` or `forbidden-op-present`; no expected or observed bindings |

These records are derived only from the validated verifier payload and bound
contract. Their canonical bytes are retained as `feedback.json` and supplied
byte-for-byte on the next launch's stdin; only their SHA-256 is mentioned in
the controller prompt. A re-run after a nonaccepted session is a **new run with
its own evidence**, never a mutation of this one.

### 5. Close the experiment

Write `CONCLUSIONS.md` resolving every declared question id with an outcome
and an evidence pointer that names a file inside the experiment directory,
then:

```
uv run gnd exp close EXP-001-contact-roster
```

The verdict is **completeness-only**: a two-way set difference between the
declared question ids and the resolved ids, plus pointer resolvability. The
outcome **values** never affect it — an experiment whose every question
honestly resolves to `unanswered` with a reason and a citation closes at 0. It
refuses at **14** while any obligation is undischarged, including a missing
`CONCLUSIONS.md`. A `kind: codegen` experiment carries one obligation more: a
`conformance.json` beside its SPEC, without which close refuses at 14 — that
evidence is produced by [`../gnd-conformance/SKILL.md`](../gnd-conformance/SKILL.md).

A `kind: work` experiment carries two more, because its declared session **is**
the work it committed to do: at least one `runs/run-NNNN/result.json` must
exist, and the **highest-numbered** run — the last thing that happened — must
report `accepted`. Neither reads an outcome value, so the completeness-only
rule above is intact: a work experiment whose questions all resolve
`unanswered` with reasons still closes at 0 once its session accepted. An
earlier acceptance does not speak for a later refusal; re-run until the work
lands, or record the refusal honestly as a `docs` record instead of closing.
For a schema-version-5 contract, that accepted result must also bind the exact
current contract digest and account for every declared walk floor with the
same case roster and counts; a stale digest, missing or extra row, changed
count, or undischarged required row keeps close at 14. Other experiment kinds
retain the completeness-only close rule.

## Where an outcome routes — and where it does not

| What the session told you | Where it routes | The boundary the handoff keeps |
|---|---|---|
| accepted, and the experiment is `kind: codegen` | [`../gnd-conformance/SKILL.md`](../gnd-conformance/SKILL.md) — produce the close gate's evidence | the conformance result stays its own claim; it is never merged into `result.json` (D-24) |
| the outcome shows the MODEL must change | [`../gnd-model-evolve/SKILL.md`](../gnd-model-evolve/SKILL.md) — one owner-authorized evolution | session evidence is information, not permission; evolution never regenerates code as a side effect |
| not accepted: a **derived-file or generated-interface** defect | do **not** edit the derived file — evolve the model ([`../gnd-model-evolve/SKILL.md`](../gnd-model-evolve/SKILL.md)), regenerate through [`../gnd-codegen/SKILL.md`](../gnd-codegen/SKILL.md), then rerun focused verification | codegen refuses a hand-edited derived file at exit 11; the durable home for the change is the model, never the emitted bytes |
| not accepted: an **extension-code** defect | direct edit in extension-owned files, then focused tests and a smoke run | `gnd verify` claims only the population contract it actually checks — it is not a substitute for those tests |
| not accepted: a **contract or expectation** defect | revise the session contract, then a new bounded `gnd exp run` | a re-run is a new run with its own evidence; the previous attempt is retained, never edited or replaced |
| the outcome bundle needs independent readers | [`../gnd-review-panel/SKILL.md`](../gnd-review-panel/SKILL.md) — advisory panel | the panel never edits the reviewed artifact and never applies a fix (D-22); its synthesis is its own claim |

## What this session will not do

- **It never edits the model.** A session that exposes a wrong constraint is
  evidence for an evolution proposal, not a license to change `model.orm.yaml`.
- **It never regenerates the project.** Drift and regeneration belong to
  conformance and codegen, each a deliberate act with its own evidence.
- **It never overrides or substitutes for the close gate.** `gnd exp run`
  does not close the experiment; a disposition of `accepted` is not a closed
  experiment, and 14 from `gnd exp close` is the gate's own verdict.
- **It never merges claim families.** The session's `result.json`, each
  per-case verifier payload under `verifier/`, and any conformance result stay
  separate claims, even when one cites another by digest (D-24).
- **It surfaces no process policy.** Executable, argv, and environment
  selection stay Python-owned in the session service; evidence records
  environment names and provenance only.
- **It never substitutes for your software tests.** The `gnd verify` verdicts
  a session retains check population behavior against the model. They do not
  replace dependency and build checks, focused unit or integration tests, or
  a smoke run over your extension code — keep those, proportionate to the
  extension surface that changed.

## Report

State, in your reply: the command you ran and its exit code verbatim; the
disposition from `result.json` and its recorded reason; the attempt count;
and where the evidence lives (`runs/run-NNNN/`). Also name the acceptance mode
for each required case and, in constraint mode, report floor gaps from checker
fact counts without translating them into a checker band. When the band was 15, name
the disposition — do not translate an exit band into an adjective, and do not
describe a nonaccepted session as "almost passing" or an accepted one as "the
agent is correct": acceptance establishes only the declared relation. A
constraint result does not establish model completeness or unique correctness,
and an accepted result does not close the experiment; `gnd exp close` remains a
separate completeness-only claim.

## Record and commit

Routine fast-lane grounding fixtures need no station record. When grounding is evidence-lane work, after `gnd synth` exits 0 (and `gnd measure` exits 0 when it ran), append `NNN-synth.md` and commit `feat(synth): ...`, staging by explicit path the corpus, the rates file when measure ran, and the record, only on the user's explicit go-ahead.

An experiment material event is evidence-lane work. At `gnd exp close` exit 0, append `NNN-<lowercase experiment id>.md` and commit `feat(<lowercase experiment id>): ...`; for `EXP-001-contact-roster`, the worked forms are `004-exp-001-contact-roster.md` and `feat(exp-001-contact-roster): ...`. A retained terminal `gnd exp run` exit 15 disposition worth recording uses `docs(<lowercase experiment id>): ...`, with the disposition verbatim. A `gnd exp close` exit 14 is a refusal, not a terminal session outcome; record it only as a `docs` refusal that taught something, with the close exit verbatim. Stage by explicit path the experiment directory (`SPEC.md`, `session.contract.json`, `runs/`, `CONCLUSIONS.md`, `conformance.json` when present) and the record, only on the user's explicit go-ahead. The lane rule, record shape, staging discipline, and commit grammar have one home: [`../gnd-orm-core/references/milestone-record-format.md`](../gnd-orm-core/references/milestone-record-format.md). If `.gnd-planning/` is absent, offer [`../gnd-new-project/SKILL.md`](../gnd-new-project/SKILL.md) first. The record and the commit are the driving agent's acts; `gnd` itself never reads or writes `.gnd-planning/` and never touches git.

For schema-version-7 patch sessions, ranking, repair ownership and retained wire
versions, read [the v7 contract](references/session-v7-contract.md).

For explicitly selected saved external opinions or confidence evidence, read the [version-8 judgment contract](references/judgment-contract.md).
