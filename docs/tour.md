# Capabilities tour

Each capability below starts from a problem, shows what GND does about it, and links
to a page where you can run it. For prerequisites and limits, see
[supported capabilities](reference/capabilities.md).

## Check what the agent produced

**Pass, fail, warn, or cannot decide.** An agent answered; was the answer acceptable?
`gnd check` evaluates every constraint and returns one of five bands. Failures name the
constraint and the offending facts. Unknowns are reported, never guessed.
`--format json` gives a stable report with `acceptance_ready`.
*Example:* a shipping request whose route exceeds its deadline fails
`constraints[1]` (`dispatch_deadline`), and the repaired request passes.
→ [Run a check in 60 seconds](quickstart.md)

**Hard rules and advice.** Not every rule should block. Alethic constraints decide
acceptance; deontic ones produce warnings and the output can still be used.
*Example:* recommending a book Ada already rated fails `unread_only`; recommending
outside her preferred genre only warns. → [BookRec, chapter 2](bookrec/02-facts.md)

**Thirteen constraint families.** Uniqueness, mandatory, value, frequency, subset and
equality, exclusion and exclusive-or, ring constraints (thirteen variants), comparison,
cardinality, subtype partitions, guarded rules, source anchoring and textual
requirements. → [Constraint coverage](reference/capabilities.md#constraint-coverage)

**Batch and in-process.** Check a directory of populations into one matrix with
`gnd check MODEL --populations DIR`, or call the same checker from your application
through the seven-function `gnd.api`. → [Python API](reference/python-api.md)

## Check plans, not only states

**Plan mode.** An agent proposes `reimburse_expense(41)` for an expense that is still a
draft. `gnd check --pre STATE --steps PLAN` walks the plan, computes the result, and
fails the step whose precondition does not hold (`pre_submitted`). The revised plan
(approve, submit, reimburse) passes. → [Check an agent's plan](agents/plans.md)

**The frame check.** An approval also flipped a bystander expense to `rejected`. Every
fact is individually legal, so no snapshot check can see it. Supplying the claimed
`--post` makes GND compare declared and actual changes and fail the undeclared one.
→ [A side effect nobody declared](agents/plans.md#a-side-effect-nobody-declared)

**Walk requirements.** A session contract can require operations (a specific approval
must happen) and forbid others (no payment without approval). The feedback reports
`required-op-missing` or `forbidden-op-present`, without revealing private bindings.
→ [Experiment sessions](guides/experiments.md)

## Derive facts instead of trusting the agent's

**Derived fact types.** An agent should not guess which books are eligible; the model
can compute it. Structured derivations support joins, stratified negation, recursion
(warehouse A reaches C through B), exact integer arithmetic and aggregates (`count`,
`sum`, `min`, `max`, `avg`). → [Data and transitions](guides/data-and-transitions.md)

**Claims checked against the derivation.** If the application also *claims* derived
facts, GND compares claims with the computed extension. A missing claim is reported as
`derived-extension-incomplete` and a wrong one as `derived-extension-unsound`, each
naming the tuple. → [BookRec, chapter 6](bookrec/06-evolution.md#distinguish-an-omitted-recommendation-from-an-incorrect-derivation)

**Three-valued results.** Opaque values and unknown inputs propagate as *unknown*,
which is reported as band 4 (indeterminate). Unknown never becomes yes or no.
→ [ORM: the executable ontology](concepts.md#validate-check-and-walk)

**Fixed reference data and calendar dates.** Catalogs the agent must not rewrite are
bound by path and SHA-256 as reference populations. Removing the catalog is an input
refusal (exit 3), not an empty catalog. Calendar-day dates and durations support
deadlines. → [Data and transitions](guides/data-and-transitions.md#separate-the-candidate-from-fixed-reference-data)

## Run agents in a bounded loop

**Sessions.** A contract fixes the inputs, the verifier, the acceptance mode (exact
bytes, constraint satisfaction with coverage floors, sealed tests, or a transition walk)
and the budget. `gnd exp run` loops attempt, check and closed feedback until one of six
recorded dispositions. *Example:* attempt 1 is rejected at `reimburse_expense`, and
attempt 2 is accepted at band 0. → [Drive an agent against the verifier](agents/dev-session.md)

**Small models, any agent.** Claude Code, Codex, any declared command or any
OpenAI-compatible endpoint can be the agent. A deterministic checker with exact
feedback lets a cheaper model converge by repairing what failed.
→ [Use a small model](agents/dev-session.md#use-a-small-model)

**Answer keys never touch the disk.** `gnd exp author-expectation` hashes an exact
expected answer and removes the source, so an agent cannot read the answer from the
workspace. Saved external judgments can gate acceptance with confidence floors
(`gnd judgments check`). → [Experiment sessions](guides/experiments.md)

## Author and evolve the ontology

**Model by dialogue.** `gnd-model-from-text` runs Halpin's design procedure with you:
examples first, then facts, then constraints. Every constraint records its source and
your words. → [Model a domain by dialogue](agents/model-from-text.md)

**Recover, adopt, import.** Recover a model from an existing codebase with recorded
evidence (`gnd recovery`), migrate a GSD project's requirements (`gnd-adopt`), or import
an ORM model written in the RelationalAI ORM-skill dialect (`gnd import rai-orm`).
→ [Evolution and recovery](guides/evolution-and-recovery.md)

**Change rules with a blast radius.** `gnd evolve preview` lists everything a change
touches before it is published; `apply` publishes with compare-and-swap and rechecks
linked projects. *Example:* the same frozen recommendations pass before and fail after
an advisory rule becomes a hard one. → [Change the rules safely](agents/evolve.md)

**Compare versions.** `gnd diff` reports bounded entailment between two models and how
each judges given populations. → [Python API: diff](reference/python-api.md#diff-compare-rules-over-the-same-vocabulary)

**Read it back.** `gnd verbalize population` turns any population into sentences for a
reviewer or the next agent turn. → [Python API: verbalize](reference/python-api.md#verbalize-display-the-supplied-facts)

## Build the application around the model

**Code generation with clear ownership.** `gnd codegen` writes the model-derived half
of a Python project; your extension code is never overwritten (exit 11 refuses instead).
→ [Generate a project](agents/codegen-conformance.md)

**Conformance and architecture contracts.** `gnd conformance` detects drift between
project and model (exit 13), including declared architecture: the layout, entry points
and smoke cases your extension promises. → [BookRec, chapter 5](bookrec/05-repair.md)

**Publish only checked output.** The generated application calls `gnd.api.check`
before publishing, so the application checks itself at run time.
→ [BookRec, chapter 4](bookrec/04-application.md)

## Test the tester

**Synthetic populations.** `gnd synth` generates conforming, boundary and violating
populations from the model, using 26 mutation operators, with recorded seeds.
→ [Synthetic data](guides/synthetic-data.md)

**Measured verifier.** `gnd measure` reports false-pass, false-fail and undecided rates
per constraint, each with its own denominator. It never blends them into one accuracy
score. → [Read measurement per constraint](guides/synthetic-data.md#read-measurement-per-constraint)

## Documents

**Extract facts, quote-not-obey.** `gnd-extract` reads a document into a population
with a digest-bound sidecar; instructions inside the document are treated as data.
`gnd verify` checks the handoff, then the facts. → [Documents in, documents out](agents/documents.md)

**Render test documents with distractors.** `gnd-render-doc` writes a document from
known facts and plants three kinds of distractors; `gnd doccheck` verifies the
rendering, and `gnd fidelity` measures the round trip.
→ [Documents in, documents out](agents/documents.md#write-a-document-from-facts)

**Source anchoring.** Bind values to spans in the source document and check that each
has a witness. → [Documents guide](guides/documents.md#bind-important-values-to-source-spans)

## Other engines and independent evidence

**Soufflé.** Export recursive derivations as standalone Datalog; trace which services a
vulnerable dependency reaches. → [Soufflé: dependency impact](runtimes/souffle.md)

**Lean.** Export finite definitions with explicitly unproved obligations. Prove that an
approval policy step is redundant, and find a counterexample to a tempting converse.
→ [Lean: policy proofs](runtimes/lean.md)

**PyRel.** Export a standalone relational program that runs locally on DuckDB, or on
Snowflake when the data lives there. → [PyRel: approval audits](runtimes/pyrel.md)

**Witnesses.** `gnd witness` produces a finite derivation certificate and `gnd replay`
re-checks it with a separate kernel. → [Exports and witnesses](guides/exports.md)

**Review panel.** Six reviewer seats across five CLIs with a quorum of three. The panel
keeps every dissent and never applies a fix.
→ [Exports and a second opinion](agents/export-and-review.md#get-a-second-opinion-from-six-models)

## Assurance, honestly labelled

GND's checker kernel was machine-verified with the Nagini verifier in the development
repository, and a result can carry a `proof-backed` assurance label when every
applicable obligation is covered by current evidence. That evidence bundle is **not**
shipped in this release, so public builds report assurance as `unavailable`. GND never
upgrades an assurance label silently. Exports and replays are separate evidence and
grant no assurance. → [Formats and errors](reference/formats.md)

See the [release notes](release-notes.md#development-milestones) for the milestones in
which these capabilities were built.
