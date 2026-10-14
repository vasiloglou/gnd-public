# Plan amendment A1: documentation for people who build with a coding assistant

Draft, 2026-10-14. Milestone `pyrel-agent-loop`. Supersedes the PL5 page design
(plan r1 §2 "Pages", `notes/phase-PL5-spec.md`). PL1–PL4 code stays.

## Context: the second owner review

After PL5/PL6 the owner rejected the pages again (2026-10-14):

1. Figures render as literal `![...](...svg)` text.
2. The docs should look like GSD (open-gsd/gsd-core), which inspired GND: how to
   build agentic apps easily. "Users will not write python code, coding
   assistants would", so the Python snippets are not useful.
3. The agreed agent replays, in the style of the home page's animated plan
   (`docs/assets/hero.svg`), are missing.
4. Show the GSD-style journey inside Claude Code: a document with the rules in
   free text, a skill builds the ORM model, GND skills set up a bot, the user
   asks for a recommendation, the bot proposes a plan, the validator checks it,
   and the plan is executed or repaired.
5. Every recorded session was accepted first try, so no refusal or repair is
   shown. Owner ruling: **use a smaller model that shows the retry.**

Root cause: PL5 treated the closed milestone's test pins and chapter shape as
fixed and optimized for runnable Python. A1 changes the reader: a person typing
into Claude Code. Python moves to reference pages.

## What GSD does that we copy

gsd-core's README is short and ordered: tagline, "What is", "How it works" as a
numbered loop, "Quickstart" with one install command and slash commands typed
in the assistant, then Documentation grouped as Tutorials, How-to guides,
Reference and Explanation, then "Why it works". Commands the user types are
slash commands; shell appears only for install.

GND adopts the same skeleton and adds what GSD lacks: animated replays of real
sessions and the checker's verdict at each step.

## Target documentation

### README and home page

- **How it works**, a numbered loop with one line each: write the rules in plain
  English → model them (`/gnd:gnd-model-from-text`) → set up the bot
  (`/gnd:gnd-codegen`) → ask the bot → it proposes a plan → GND checks the plan
  → execute it, or repair it from GND's feedback → change a rule
  (`/gnd:gnd-model-evolve`).
- **Quickstart**: install the plugin (`/plugin marketplace add vasiloglou/gnd-public`,
  `/plugin install gnd@gnd-marketplace`), then one prompt that starts the
  tutorial. Shell only for `uv`/PyRel setup, behind a "Run on PyRel" toggle.
- Hero replay stays; it links to the new tutorial.

### Flagship tutorial: "Build a checked book recommender with Claude Code"

One page, in the user's voice, eight steps. Each step has the same four parts:

| Part | What the reader sees |
|---|---|
| You type | the exact prompt or slash command, in a chat bubble |
| Claude Code does | a replay (animated SVG, with a static first frame and a text transcript under a disclosure) of what the assistant read, asked, ran and wrote |
| You get | the artifact, short: a few lines of `rules.md`, the model's verbalization, the plan, the bot's answer |
| GND says | the verdict exactly as the terminal prints it, with the witness explained in one sentence |

Steps:

1. **Write the rules.** `rules.md` in free text: "Never recommend a book a
   reader has already rated. Never recommend an adult-rated book to a minor.
   Prefer the reader's favourite genres." Plus a short catalogue and two readers.
2. **Model them.** `/gnd:gnd-model-from-text` in MVP-fast mode. Replay shows the
   skill reading each rule back, asking one clarifying question ("is genre fit a
   must or a should?"), writing `model.orm.yaml`, and `gnd validate` exit 0.
   Artifact: the verbalized rules, not YAML.
3. **Set up the bot.** `/gnd:gnd-codegen` then `/gnd:gnd-conformance`. Replay
   shows the generated project and the extension the assistant writes: a
   `recommend` command whose answer is a plan of `recommend_book` steps.
4. **Ask the bot.** "What should Ada read next? She loved *Night*'s cover."
5. **It proposes a plan.** Replay of the small model proposing `night` for Ada.
6. **GND checks it.** `gnd check --pre … --steps …` refuses:
   `age_appropriate` with witness Ada/night. One sentence on why the query
   could not be trusted to filter this.
7. **Repair and execute.** Replay of the model reading the feedback (rule and
   offending facts, never the answer), proposing `river`, GND accepting, and the
   plan executed into the reader's recommendations.
8. **Change a rule.** `/gnd:gnd-model-evolve` makes genre fit a must; the same
   question now gets a different, checked answer.

A shorter companion, "Approve expenses with Claude Code", follows the same
eight steps with the team-lead limit.

### What moves where

| Content | New home |
|---|---|
| BookRec ch. 7 and Expense ch. 4 (PyRel app, `rules_in_pyrel.py`, stand-in, `gnd exp` contracts) | Reference: "Run the checker on PyRel" and "Session contracts", linked from step 6 as "Under the hood" |
| Python snippets in tutorials | removed; runnable checks move into tests that read the committed recordings |
| Skills table in `docs/agents/index.md` | How-to guides, one page per skill, each opening with its slash command |
| `pyrel-apps.md` | Explanation: "How a rule becomes a PyRel check" (kept, shortened) |

## The plan as a first-class artifact

The journey in point 4 is "propose a plan, validate, execute or repair". BookRec
today has no operations, so a recommendation is a population, not a plan. A1
adds one operation to the BookRec model, `recommend_book(user, book)`, whose
preconditions carry the three rules, so the bot's answer is a `steps.json` plan,
`gnd check --pre --steps` validates it, and executing it adds the
recommendation facts. This mirrors the approvals example behind the hero replay
and uses ORM+ v2 operations that `gnd-model-from-text` already authors (its
step 6f). Expense gets `approve_expense(expense, chain)` the same way.

Open choice, decided at the PL7 spec: keep populations and call them "the
proposed answer" instead. Operations are recommended because they make the
story literal and the hero animation and tutorial show the same mechanism.

## Recording a retry with a smaller model

### What the earlier evidence says

The 2026-10-04 approvals recordings ran nine hosted models. Small models did
fail: Llama 3.1 8B and Llama 3.2 3B produced rule-level (band 1) rejections,
and Gemma 3 4B produced ill-formed plans. But no model recovered from a
rule-level rejection. Every recovery came after an ill-formed attempt. The
reason is visible in the feedback format: transition feedback names the failed
step and outcome but carries no bindings.

### What changes here

- **Witness in the feedback.** A1's plans are checked with constraint
  preconditions whose feedback names the offending facts (Ada, `night`). Before
  recording, PL7 measures whether `gnd exp run` transition feedback can carry
  the precondition's witness. If it cannot, the session uses
  constraint-satisfaction mode over the resulting state, which already returns
  `offending_facts` (shown in PL3).
- **The gateway shows the feedback in words.** `tools/openrouter_gateway.py`
  today is hard-wired to the approvals plan. Generalize it to read the task,
  model and input named by the contract. On a retry, decode the feedback into a
  plain sentence the small model can use: "Rejected: age_appropriate. Offending
  facts: user ada, book night."
- **A task that invites the mistake.** The user asks for *Night* for Ada, the
  same conflict variant as PL4.

### Models and protocol

| Route | Candidates | Why |
|---|---|---|
| Claude Code, small model | `claude --model haiku` | a real coding-assistant transcript with skills and tool calls; the main replay if it retries |
| OpenRouter via gateway | `meta-llama/llama-3.1-8b-instruct`, `google/gemma-3-4b-it`, `meta-llama/llama-3.2-3b-instruct` | each produced a refusal in earlier recordings |
| Claude Code, default model | account default | the happy-path contrast: reads the rule first and is accepted |

Protocol, declared before any run:

- 5 runs per model, 3 attempts each.
- Every run is listed in `results.json`.
- The tutorial replays the first run, in recording order, that shows a band-1
  refusal followed by acceptance. The page says which run it is and links the
  full table.
- If no model shows refusal-then-repair, the tutorial says so plainly. It then
  replays a refused run, with the stand-in repair labelled as scripted.

### Credentials, needing the owner

- **OpenRouter:** `OPENROUTER_API_KEY` is read from `.env` as data by the
  gateway only, through `tools/agent_with_env_key.py`, under a new gate record.
  The session's permission classifier refused this wrapper once. The owner must
  allow that one command, or export the key in the shell that starts the
  gateway.
- **Claude Code:** the standalone `claude` CLI is not logged in on this machine.
  The owner runs `claude login`, or allows the wrapper with
  `ANTHROPIC_API_KEY`.

## Replays

`tools/render_replay.py` turns a committed transcript into an animated SVG, in
the same visual language as `hero.svg`:

- **Input:** Claude Code `stream-json`, Codex `--json`, or GND session feedback.
- **Content:** chat bubbles, collapsed tool calls, the artifact diff, and GND's
  verdict line.
- **Output:** a static first frame for `prefers-reduced-motion` and an
  accessible text transcript under a disclosure.

Replays are generated from committed, SHA-256-checked recordings. A test
re-renders them and compares the bytes, so a replay cannot drift from what the
model did.

## Figures fix

Markdown images inside `<div markdown="1">` render on the docs site but print
as text on GitHub. Replace them with plain `<img src alt>` inside the
scroll-region `div`, or leave a blank line after the opening tag. Add a test
that fails on a Markdown image line directly after an HTML opening tag. Check
one page through `gh api markdown`.

## Phases

| ID | Deliverable | Gate |
|---|---|---|
| PL7 | `recommend_book` / `approve_expense` operations (via a `gnd evolve` proposal); feedback-witness measurement; generalized gateway; figures fix | spec gate; `gnd validate`; transition checks refuse and accept the pinned cases |
| PL8 | Recordings: Claude Code haiku, three OpenRouter models, Claude Code default; new gate record | owner gate for credentials; `results.json` complete; at least one declared outcome per the protocol |
| PL9 | `tools/render_replay.py`; replays for steps 2, 3, 5–8 | re-render byte-equality test; reduced-motion frame; screen-reader transcript |
| PL10 | README "How it works"/Quickstart; flagship BookRec tutorial; Expense companion; IA move (Tutorials/How-to/Reference/Explanation); old chapters demoted to Reference | prose gate (rewritten for chat-style pages); no Python fences in Tutorials; strict build; GitHub render check |
| PL11 | Tests and pins updated, fresh-install acceptance, close readers, PR #22 updated | acceptance exit 0; four close readers; owner merges |

## Tests that change

- `tests/test_pyrel_learning_path.py`: applies to the new tutorials. It drops
  the step-3 Python-excerpt rule and the per-chapter section numbering. It adds
  "no `python` fence in a Tutorials page" and "every replay has a transcript".
- `tests/test_tutorial_output_blocks.py`, `tools/run_tutorials.py` groups,
  `tools/accept_pyrel_applications_install.py` counts: the old chapters move to
  Reference and keep their runnable blocks. The new tutorials are checked by
  tests over the recordings, not by executing prose.
- New: `tests/test_replays.py`, `tests/test_figures_render.py`, and recording
  tests for the new tasks.

## Out of scope

Snowflake. Changing rule meanings. Benchmarking or ranking models. Rewriting
BookRec chapters 1–6, beyond links into the new tutorial.

## Decisions for the owner

| # | Question | Recommendation |
|---|---|---|
| A1-D1 | Model the bot's answer as an operation plan (`recommend_book`) or keep populations | operation plan |
| A1-D2 | Claude Code login route: `claude login`, or allow the key wrapper | `claude login`, so no key is handled by tooling |
| A1-D3 | OpenRouter key: allow the wrapper once, or export it in the gateway's shell | allow the wrapper under a gate record |
| A1-D4 | Small-model list and run count as declared above | as declared |
| A1-D5 | Keep the old PyRel chapters as Reference pages, or retire them | keep, demoted |

## Appendix: more toy examples, by capability

### What the shipped examples already exercise

Measured from the models on `main`:

| Example | Covers |
|---|---|
| BookRec | guarded rules (absence, atom), deontic versus alethic, derived fact types with negation |
| Expense | value lists, subset, guarded comparisons, mandatory, model evolution |
| Approvals | operations, preconditions, frame |
| Release, dispatch | a subset rule, one derivation, version-4 models |

No shipped example touches these, all of which GND checks today
(`docs/reference/capabilities.md`, `gnd-orm-core/references/constraint-reference.md`):

- **ORM:** frequency, internal and external; external uniqueness; equality;
  exclusion; exclusive-or; inclusive-or mandatory; ring constraints; value
  ranges; object and role cardinality; subtype partition.
- **ORM+:** dynamic rules (old value versus new); calendar-day terms with Date,
  Duration, `date_add` and `date_sub` (version 3); fixed reference populations
  bound by hash (version 4).
- **ORM++:** recursive derivations; exact aggregates (`count`, `sum`); multi-clause rules.
- **Documents:** source anchoring.

### Five candidates, all in the flagship tutorial's shape

Each candidate follows the same eight-step story: a free-text rules file, a
model built by the skill, a bot, a question, a proposed plan, a refusal with a
witness, a repair, and a rule change. Each has one natural request that breaks
exactly one rule with a witness that points at the fix, which makes it a good
small-model retry case.

| # | Example | The question you ask the bot | The plan it proposes | GND refuses because | Repair |
|---|---|---|---|---|---|
| 1 | **Course planner** (registrar) | "Plan Maya's spring semester; she wants Machine Learning." | `enroll` steps | ML needs Linear Algebra through a prerequisite chain that Maya has not completed; the witness is the missing ancestor course | enroll in the prerequisite first, defer ML |
| 2 | **Clinic refills** (pharmacy) | "Refill Sam's prescriptions today." | `dispense` steps | a 30-day refill was last dispensed 12 days ago; or two dispensed drugs interact in the fixed catalogue | set the refill date to `date_add(last, 30 days)`; drop the interacting drug |
| 3 | **Access requests** (org chart) | "Give Bob access to payroll; Carol approves." | `grant`, `approve` steps | Carol is in Bob's own management chain, which counts as self-approval through a recursive rule | route to an approver outside the chain |
| 4 | **Trip planner** (itinerary) | "Plan three days in Lisbon under 900 EUR." | `book_hotel`, `book_activity` steps | the summed cost is 1,040 EUR; or two bookings overlap in time | swap the hotel; move the activity |
| 5 | **Lease reader** (documents) | "Read this lease and set up the rent schedule." | an extracted facts file, then `schedule_payment` steps | an extracted rent amount has no source span in the lease; or a due date falls outside the lease term | re-extract with an anchor; clip the schedule |

### Capability matrix

| Capability | Tier | 1 Course | 2 Clinic | 3 Access | 4 Trip | 5 Lease |
|---|---|---|---|---|---|---|
| Internal and external uniqueness | ORM | room + timeslot unique per section | | | one hotel per night | |
| Frequency | ORM | 3–6 courses per term | | | 1–3 activities per day | |
| Cardinality, object or role | ORM | section capacity | | | | |
| Ring: acyclic, irreflexive | ORM | prerequisite of | | reports to | | |
| Exclusion | ORM | TA and student of the same section | | requester and approver | | |
| Exclusive-or, subtype partition | ORM | | patient is adult xor minor | employee xor contractor | | |
| Inclusive-or mandatory | ORM | | phone or email on file | | | |
| Value range | ORM | credits 1–6 | dose range | | | |
| Equality | ORM | | prescription has a prescriber if and only if a diagnosis | | | |
| Operations, preconditions, frame | ORM+ | enroll, drop | dispense | grant, approve, revoke | book | schedule payment |
| Dynamic rule (new versus old) | ORM+ | grade never changes after it is final | refill count only increases | clearance never rises without approval | | |
| Calendar terms: Date, Duration | ORM+ (v3) | | refill interval | | check-out after check-in | due dates within the term |
| Fixed reference population (hash-bound) | ORM+ (v4) | course catalogue | drug catalogue and interactions | | price list | |
| Recursive derivation | ORM++ | prerequisite closure | | management chain | | |
| Aggregate `count`/`sum` + guarded comparison | ORM++ | total credits ≤ 18 | | | total cost ≤ budget | |
| Negation as failure | ORM++ | "not completed" | "no interaction recorded" | "not in chain" | | |
| Multi-clause rule | ORM++ | | an interaction holds either way round | | | |
| Source anchoring, `gnd-extract`, `gnd verify` | documents | | | | | every extracted fact |
| Textual constraint, reported unchecked | ORM | | "pharmacist uses judgement" | | | |

### Recommendation

1. **Course planner next.** It is the richest single example: ring constraints,
   recursion, aggregates, frequency, cardinality, operations and a dynamic rule.
   Its refusal ("you are missing the prerequisite") is intuitive to any reader
   and easy for a small model to repair from the witness.
2. **Clinic refills.** This is the calendar and reference-catalogue story: a
   hash-bound drug list the agent may read but not change. It shows how GND
   handles "today" without a live clock, through an explicit `as_of` date fact.
3. **Access requests.** This is the governance story, where self-approval is
   caught through a recursive chain. It pairs with the existing release-governance pages.
4. **Trip planner.** The most consumer-friendly example, and the best one for
   the README hero after BookRec. It covers aggregate budgets and time overlap.
5. **Lease reader.** Documents in, plan out. It shows `gnd-extract` and
   `gnd-render-doc` in the same assistant flow.

### Feasibility checks before committing to an example

Each must be measured with `gnd validate` and `gnd check` before its spec is approved:

- **Operation preconditions are positive atoms only.** "Not completed" and
  "amount ≤ budget" must be written as guarded or derived invariants. The walk
  checks them after each step; they cannot be preconditions. The tutorial must
  say "the plan is refused at step 2", not "the operation is not allowed".
- **Subtype partition is checked only when membership is observable.** Model
  adult and minor as fact types, not derived subtypes.
- **There is no live clock.** Every "today" is a dated input fact, and the page
  says so.
- **Each example declares a fixed set of fact types** (the population's `covers`
  list). Fact types it leaves out are reported unknown, not empty, so their
  rules are not checked.
- **PyRel export profile.** The applications profile admits only some
  constraint families. Ring, frequency, aggregates and calendar terms may be
  checked by GND but refused by the PyRel applications runtime. Each example
  states which runtime checks it, and the PyRel page lists any refusals instead
  of hiding them.

Phase placement: PL12 (Course planner) and PL13 (Clinic) after A1's PL11, each
as one tutorial page in the flagship shape. Trip, Access and Lease become How-to
pages afterwards, or a later milestone. Each needs its own small-model retry
recording under the A1 protocol.

## Appendix: how all five examples run on PyRel

Owner ruling, 2026-10-14: implement all five examples.

### What PyRel does today (measured on `main`)

There are two layers in `src/gnd/export/pyrel_runtime.py`:

- **The audit translator** (`PyrelOracle.evaluate`, used by `gnd export pyrel`)
  already evaluates these families in PyRel: uniqueness, mandatory, value,
  frequency, ring, subset, equality, exclusion, exclusive-or, value comparison,
  cardinality and subtype partition. It reports `unsupported` for anchored
  facts, multi-range values and time-relative operands.
- **The applications profile** (`ApplicationOracle`, used by the apps and
  `check_proposal`) is much narrower:
  - model version 1 or 2 only, with no `operations` section;
  - guarded rules, mandatory, subset, value and uniqueness;
  - derivations as positive body plus negation with no cycles, so no
    recursion, no `where`, no aggregates and no clauses;
  - no plan or transition checking at all.

None of the five examples can run on PyRel today without extending the applications profile.

### Probe, 2026-10-14

PyRel 1.30.1 with DuckDB 1.5.5:

- a recursive `define` (prerequisite closure) reached the full fixpoint natively;
- `aggregates.sum(...).per(...)` inside a comparison (total credits > 18)
  returned the right rows.

So recursion and aggregates can be native PyRel, not Python loops.

### Design: one translator, widened by layer

Each layer is a change to the generated PyRel program. Each is admitted into
the applications profile only after an agreement test against GND on that
example's corpus.

| Layer | Needed by | How it becomes PyRel | Where |
|---|---|---|---|
| L1 Snapshot families | all five | admit frequency, ring, equality, exclusion, exclusive-or, cardinality, subtype partition and external uniqueness into `ApplicationOracle` by reusing the audit translator's handlers, which already emit PyRel; add each family's witness shape to the verdict format | `pyrel_runtime.py` (`_profile_guard`, `ApplicationOracle.profile_evaluate`) |
| L2 ORM++ derivations | Course, Access, Trip, Clinic | recursion: lift the no-cycles refusal for monotone cycles and emit self-referencing `define` (probe passed); negation stratified by computed strata, refusing negation through a cycle; `where` as PyRel comparisons; `aggregate` as `aggregates.count/sum(...).per(...)`; `clauses` as several `define`s into one relation | `_profile_derivations`, `ApplicationOracle._derive` |
| L3 Calendar terms (v3) | Clinic, Trip, Lease | Date encoded as an integer day ordinal, Duration as integer days; `date_add`/`date_sub` become integer `+`/`-`. Exact, with no timezone, as GND's spec requires; the encoding is decoded back to dates in witnesses | translator scalar layer plus witness rendering |
| L4 Reference populations (v4) | Course, Clinic, Trip | the parent verifies each reference file's SHA-256 before launch; reference relations are loaded read-only and listed as owned by the reference, so a plan that touches them is refused before the check (existing `_preserve_source`) | `applications.py`, translator loader |
| L5 Plans (ORM+ operations) | all five | new `check_plan` entry point. For each step, preconditions are PyRel queries over state S(i-1); the step's effects build S(i) by the transition equation; every invariant (guarded, derived, snapshot family) is a PyRel query over S(i); dynamic rules join S(i-1) and S(i); the frame is a PyRel symmetric-difference query over fact types the operation does not touch. Applying an effect is data movement, not a policy decision, so it stays in the generated program's Python, and every verdict is a PyRel query, per PA-R1 | new functions in `pyrel_runtime.py` and `applications.py`; app CLIs gain `plan` and `execute` |
| L6 Source anchoring | Lease | stays GND-only: anchors need the bound document and lexical matching. The Lease app checks anchors with `gnd verify`, then the schedule rules in PyRel; the page says which runtime checked what | none; documented boundary |
| L7 Textual constraints | Clinic | reported unchecked by both runtimes, as today | none |

### Rules in PyRel without hand-writing them

The owner wanted to see the rules in PyRel, and also does not want readers
writing Python. One `rules_in_pyrel.py` per example would be five more files
to keep in sync by hand. Instead:

- **`gnd export pyrel MODEL --explain`** prints, for each constraint, the PyRel
  query the translator actually builds: a short `where(...).select(...)` with
  readable relation and variable names. It is produced from the same code path
  that runs the check, so there is one home.
- **A test executes every printed query** against the example corpus and
  compares rows with the real check, so the printed text cannot drift.
- The Explanation page "How a rule becomes a PyRel check" and each tutorial's
  "Under the hood" disclosure show this output. The BookRec and Expense
  hand-written files from PL2 are retired once `--explain` covers them.

### Agreement and limits

- **Agreement corpus.** Each example adds a corpus: seed, the pinned bad plan,
  the repaired plan, and one case per family and layer it exercises, including
  vacuous and unknown-coverage cases. The existing agreement harness
  (`tools/measure_pyrel_applications.py`) runs GND and PyRel on every case and
  compares status, witness and exit. A family is admitted only when its rows
  agree.
- **Work limits.** Recursion and aggregates get explicit bounds: fixpoint row
  limit, aggregate group limit, plan length limit. Exceeding a bound is a named
  refusal, never a pass. This needs a time-bound test per layer (standing rule 2).
- **Version gate.** The applications profile admits model versions 1 to 4,
  feature-detected rather than keyed on the version number, as the format
  requires.

### Phases (replace PL12–PL13 from the examples appendix)

| ID | Deliverable | Gate |
|---|---|---|
| PL12 | L1 snapshot families, plus `--explain` | per-family agreement corpus; `--explain` execution test |
| PL13 | L2 derivations: recursion, aggregates, clauses, `where` | agreement corpus; time-bound tests; refusal for negation through a cycle |
| PL14 | L3 calendar, L4 reference populations | agreement corpus; reference hash tamper control |
| PL15 | L5 plans: `check_plan`, `execute`, app `plan` commands | GND transition versus PyRel plan verdict agreement on every example's walks |
| PL16 | Five example models via `gnd-model-from-text` from free-text rule files, five apps, corpora | each example: `gnd validate` 0, pinned refusal and repair on both runtimes |
| PL17 | Small-model retry recordings for each example; replays | protocol from A1 |
| PL18 | Tutorials: Course and Clinic as full tutorials; Access, Trip and Lease as How-to pages; Explanation page from `--explain` | A1 page gates |

Order: PL12 → PL13 → PL14 → PL15. PL16 starts once PL12 lands and follows the
layers. PL17 and PL18 come last.

## Appendix: rules as PyRel requirements, not row fetches

Owner comment, 2026-10-14: the design uses PyRel as a database, fetching
facts and checking them in Python. PyRel has requirements
(`where(...).require(...)`) for writing logical rules, and GND should use them.

### Measured, 2026-10-14

Probe in the session scratchpad (`pyrel-require/probe.py`), PyRel 1.30.1 with
DuckDB 1.5.5: `m.where(rec(u, b), minor(u)).require(not_(adult(b)))` over data
containing Ada/night.

| Setting | Result on local DuckDB |
|---|---|
| default `require_mode` (`ignore`) | query runs, no error, violation unreported |
| `compiler={'require_mode': 'report'}` | same: no error, violation unreported |

Source confirms why: `require_mode` is read only by the logic-reasoner (LQP)
backends. On the SQL/DuckDB backend, `_extract_require_blocks` lifts
requirements only into the logic reasoner's install payload. The logic reasoner
compiles `where(domain).require(check)` to

    domain ∧ ¬check ⇒ Error(e), message(e, "Requirements not met"), <var>(e, value) per domain variable

(`semantics/backends/lqp/metamodel2flow/require_errors.py`). That is exactly the
breach query GND runs today, and the error carries the witness variables.

### Design change

1. **Every rule is authored as a PyRel requirement.** The translator's
   intermediate form for each constraint becomes one requirement object:
   `domain` (antecedent atoms, or the universe of a type), `check` (the
   consequent), the witness variables and the modality. The readable program
   and `gnd export pyrel --explain` print `m.where(<domain>).require(<check>)`,
   the idiomatic PyRel rule, with deontic rules marked "should".
2. **Two lowerings from that one object.**
   - **RelationalAI logic reasoner:** emitted as `require(...)` with
     `require_mode="report"`. Violations come back as `Error` entities with
     their variables; GND reads them as witnesses. This is real enforcement,
     but it needs a RelationalAI engine, today the Snowflake native app. That
     is outside the local-only boundary from A2 and needs an owner decision
     and credentials.
   - **Local DuckDB:** requirements are not enforced (measured above), so GND
     emits the same denial form the logic reasoner compiles a requirement into:
     `where(<domain>, not_(<check>)).select(<witness vars>)`. Pages say this
     plainly: on your laptop the requirement is checked by asking PyRel for
     the facts that would violate it; on the RelationalAI engine it is
     enforced directly.
   - A test asserts both lowerings come from the same requirement object. When
     a logic-reasoner lane exists, an agreement test compares its `Error`
     witnesses with the local denial rows.
3. **Family mapping, each shape measured before admission:**

   | Family | Domain | Check |
   |---|---|---|
   | Guarded rule | antecedent atoms | consequent atom; `not_(atom)` for absence; the comparison |
   | Mandatory | object-type universe `x` | fact mentioning `x` |
   | Subset | left-hand fact | right-hand fact |
   | Exclusion | one fact | `not_(other)` |
   | Equality | two subsets | both directions |
   | Value | the fact | a membership or range test (spec measures the PyRel form) |
   | Uniqueness | n/a | `unique_fields(...)`, PyRel's own functional dependency, which the logic reasoner records as an FD; locally, a count `> 1` denial |
   | Frequency, cardinality | grouped domain | count bounds via `aggregates.count(...).per(...)` |
   | Ring | binary fact | `not_` of the reversed or self pair; acyclic as `not_(closure(x, x))` over the recursive closure |
   | Plan preconditions | step `i` | a requirement over state S(i-1) |
   | Plan invariants | step `i` | requirements over state S(i) |

   GND's modality survives: alethic rules refuse, deontic rules warn.
4. **Derivations stay `define`.** Derived fact types are PyRel `define` rules,
   including recursion (measured working locally); requirements then refer to
   them. That is the separation PyRel intends: `define` for what follows,
   `require` for what must hold.

### Affected phases

- **PL12:** introduce the requirement object, the denial lowering, `--explain`
  printing requirements, and the single-source test.
- **New PL12b, owner-gated:** a logic-reasoner lane on a RelationalAI engine,
  running `require_mode="report"`, with the agreement test. It needs owner
  approval to cross the local-only boundary, plus credentials.
- **Tutorials:** "Under the hood" and the Explanation page show the rules as
  requirements and state which lowering ran.
