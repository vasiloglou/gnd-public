---
name: process-phase
description: Executes one phase of a GND milestone plan under that milestone's own protocol -- harvest obligations, author the spec and stop for its owner gate, implement and verify, review the diff and refactoring, then record and commit. Use for requests to run, process, execute, specify, review, or close a numbered or multi-part phase, and for deciding whether another review round is warranted. It accepts auto=true for explicitly delegated approval, otherwise stops at owner gates, writes no code before recorded spec approval, and treats findings as unproved until reproduced. Certification and recertification are opt-in by explicit owner request; older certificates remain tied to their original bytes. Not for authoring the milestone plan, GND station work over a domain model, or the milestone-close record.
---

# Process Phase

## Summary

**What:** one phase of a GND milestone, executed end to end under the plan's
own section 8 execution protocol. Six numbered steps, an owner gate before any
code, and a record that binds the result to bytes on disk.

**The protocol, in one table.** Each step's detail lives in the reference it
names; this table is the contract.

| # | Step | Produces | Stops? |
|---|---|---|---|
| 0 | **Harvest** the phase's obligations from every source that assigns one | the obligations table that opens the spec note | no |
| 1 | **Spec** | `notes/phase-N-spec.md` | **STOP** |
| 2 | **Owner gate** — approve or amend; optional review panel over the spec bytes | owner decisions, recorded in the spec with a mark | **STOP** |
| 3 | **Implement + verify** | code + tests; the plan's section 9 row and the phase's impact-closure gates run | no |
| 4 | **Adversarial review of the diff** | `notes/phase-N-<reviewer>-review.md` + one regression test per finding | no |
| 5 | **Refactoring review** | the record's `Refactoring review` section | no |
| 6 | **Record + commit** | `milestones/<milestone>/NNN-phase-N.md` + a commit in GND grammar | done |

**When to use:**
- The owner says "phase N", "the next phase", or "process this phase"
- A phase's spec needs writing, or a written spec needs executing
- A finished phase needs its review, its refactoring review, or its record

**When NOT to use:**
- Revising the milestone plan itself — that is a separate artifact with its own
  four-reviewer panel bar, and this skill consumes the plan, never edits it.
  A phase that finds the plan wrong records a **refuted premise** and an
  open-questions row naming the repair; the plan is repaired at milestone close
- The milestone-close record — it cites every phase record and performs the
  open-questions sweep, which is not a phase's work
- GND station work over a domain model — `gnd-solve` and its siblings own that.
  A phase record's `skill:` field says so explicitly

## Invocation and delegated approval

Invoke as `process-phase PHASE MILESTONE [auto=true|auto=false]`; omission means
`auto=false`. Natural-language authorization to auto approve supplies `auto=true`
for the named scope. This is a skill argument, not a new gnd CLI flag.

With `auto=true`, the user's explicit delegation supplies approval at steps 1
and 2. Complete the spec and implementability sweep before recording each
ruling as **delegated approval (auto=true)** with date, authorization, chosen
instrument, exact artifact SHA-256, budget and compatibility decisions. Then
continue without a confirmation pause. Never label these agent decisions a
human reading of the artifact. Apply the same recorded delegation to amendments
and changed corpus answers within the authorized scope; retain the prior answer
and explain the change. The default instrument still follows
references/review-convergence.md. Optional spec panels default to omitted unless
needed to settle a concrete uncertainty or expressly requested.

The STOP rows and owner-gate asks below apply when `auto=false`; with `auto=true`
they are recorded transitions, preserving spec-before-implementation ordering.
Delegation does not waive required reviews, falsifiable cases, reproduction,
compatibility, verification, evidence, convergence or commits. It neither
fabricates passing results nor authorizes unrelated destructive/external work,
broad suites or certification. A technical refusal remains a refusal; continue
independent authorized work and report any genuine unmet prerequisite.

A milestone-wide auto instruction persists across its phases until revoked.
Required plan and close reviews still run under their own protocol. Record their
delegated owner dispositions separately; this skill remains a phase workflow.

## Step 0 — Harvest the obligations

**A phase's obligations are not in one place, and the plan is deliberate about
that.** A spec that reads only the phase's own bullets in section 4 will ship
missing half of what binds it. Collect all of it, by name, before writing prose.

| Source | What it assigns | How it must appear in the spec |
|---|---|---|
| §4, the phase's own section | the deliverables and the **Criteria** list | each criterion becomes a named test with an expected exit |
| §4, the phase's **Residual** paragraph (when present) | an accepted risk, stated in the reviewers' own terms | copied forward verbatim into the spec and then into the record's boundary |
| §9 verification story, this phase's row | the proof obligation | the row is quoted; the spec says which test discharges each clause |
| §0 design rules | rules earlier phases already paid for, binding every remaining phase | each rule bound to this phase's work **by name**, or argued inapplicable |
| §10 open-questions ledger | rows whose owner column names this phase | each becomes a **decision** the owner rules on at step 2 |
| §5 skill-surface table | skill edits and their **pin sites** | pin sites listed; counts measured at execution time, never derived |
| §6 risk register | the failure classes this phase can re-commit | named in the spec's own coverage argument |
| §7 out of scope | what a reviewer must not ask for | a short "out of scope for this phase" section |
| prior phase records | boundaries, open questions and refuted premises still live | anything this phase inherits or discharges, cited by path |

**This is the step to fan out.** Harvesting is mechanical reading across a large
plan and several records, which is exactly what parallel readers are good at and
exactly where a single pass silently skips a row. See
[`references/agent-delegation.md`](references/agent-delegation.md) for what to
delegate, what each agent returns, and the rule that governs every finding one
brings back.

**Output:** an obligations table at the head of the spec note. Never a pointer —
"see the plan" is how an obligation goes unmet without anyone noticing.

## Step 1 — The spec note, then STOP

Expand the phase's plan section into a scannable spec at
`notes/phase-N-spec.md`: exact schema fragments, exact function signatures, the
rule list, and the test list with expected exits. Full contract in
[`references/spec-note-contract.md`](references/spec-note-contract.md).
The test list includes a verification-selection ledger under
[`references/verification-selection.md`](references/verification-selection.md):
plan-mandated gates, direct phase tests, impact closure, and an explicit
disposition for broader historical suites. A full repository replay is not an
implicit per-phase gate.

Before offering the spec at the gate, run the **implementability sweep** — for
every requirement, can *some* implementation satisfy it as written? The rule,
its named failure shapes, and the approval it once cost are in
[`references/review-convergence.md`](references/review-convergence.md);
implementability is a gate precondition, not a review discovery.

**Then stop.** No implementation file is created, edited, or sketched before
step 2 clears. This is the protocol's one hard ordering rule.

## Step 2 — The owner gate

The owner approves or amends. Three things are decided here, and the skill asks
rather than assumes:

1. **The approval instrument.** Either the spec prose, or a committed fixture
   corpus authored first with narrated expected outcomes — the corpus-first
   pattern piloted in the transition phase, where the owner approves by reading
   the fixture stories and the spec stands as the design record. Corpus-first
   costs a station-0 session before implementation; it bought the discovery of a
   defect in the corpus itself and of a declared finding class with no case.
   **The plan states this pattern was a pilot and that later phases adopt it only
   if it earned its cost — so it is asked, never inherited.** The ask is not
   neutral, though: for the three phase shapes named in
   [`references/review-convergence.md`](references/review-convergence.md) —
   serialized formats, exit-code contracts, validation predicates — that
   reference sets corpus-first as the default answer and puts the burden of
   argument on prose. The rule and its evidence live there, not here.
2. **Whether a review panel runs over the spec bytes.** The plan mandates the
   four-reviewer panel for plan review and milestone close, not per phase. A
   panel here is the owner's call. If one runs, note the standing hazard: in one
   measured round, five of eight agreed concerns were defects introduced by the
   *previous* repair pass, so any repair round re-checks the neighbours of every
   edit, and repaired bytes carry no panel opinion until re-reviewed. **Repeated
   rounds over one artifact are bounded, and the bound is declared before round
   two** — fill the convergence ledger each round, and when the stop rule of
   [`references/review-convergence.md`](references/review-convergence.md) fires,
   the next instrument is implementation, not another panel. That reference is
   the rule's one home; do not paraphrase its conditions here or anywhere.
   The panel skill's source-provenance precondition is mandatory when developing
   GND itself: if `src/gnd/review` or either packaged panel skill differs from
   `HEAD`, validate and commit those bytes before creating a disposable worktree
   from `HEAD`. A clean checkout that silently omits pending harness fixes is not
   an admissible panel environment. When the owner requires all six seats to
   work, the same panel contract stops before invocation unless the parent
   environment carries `OPENROUTER_API_KEY` and `ZAI_API_KEY`. In this
   repository, invoke that all-six run through
   `uv run python tools/run_gnd_review_panel.py REQUEST --out DIR ...`. The
   launcher fills only those two names from the owner-only trusted
   `~/.codex/.env` when the parent lacks them, accepting the historical aliases
   `QWEN_API_KEY_2` and `Z_API_KEY`; it parses the file as data rather than
   executing shell, never reads a repository `.env`, and fails before spending
   the panel budget if either target remains absent. It also checks the selected
   OpenRouter credential against the provider before launching reviewers: a
   populated alias alone does not prove authentication. `--check-credentials`
   checks loading only; `--check-auth` performs that provider check without a
   panel. For an explicitly selected light panel, place `--light` before
   `REQUEST`; the same credential handling then launches `panel-light`.
3. **Every ledger row harvested at step 0.** Each gets a ruling, marked in the
   spec with an owner mark and a date, so a later reader can tell a decision
   from a draft.

**Opt-in recertification.** Read
[`references/architect-overrides.md`](references/architect-overrides.md) when
certification or recertification is proposed. A phase end, milestone close,
changed source, or historical plan clause does not itself authorize or require
a new run. The owner must explicitly request one for a named subject and
scope. Focused verification still follows the phase's impact boundary; a
prior certificate never becomes evidence about changed bytes.

**Then stop again.** Implementation begins on explicit go-ahead.

## Step 3 — Implement + verify

- If corpus-first was chosen: the harness lands **red** first — every case
  failing because the lane does not exist — and each subsequent commit names the
  cases it turns green.
- Keep the owner-approved corpus's meanings stable. Add implementation and
  adversarial regression cases as separately identified successors and bind
  their results in the completion record; changing an approved expected answer
  returns that answer to the owner gate.
- Implement lane by lane, not file by file. A lane is a boundary a test can sit
  on (loader → evaluator → CLI → report), so each lane ends green.
- The section 9 row runs as written. Its clauses are the gate, not a summary of
  the gate.
- Run the verification-selection ledger from the approved spec. Select tests by
  changed inputs and downstream contracts, not by age or runtime, and apply the
  inheritance, invalidation, cadence, and isolation rules in
  [`references/verification-selection.md`](references/verification-selection.md).
- Use the reduced v6.3 test selection for ordinary phase work: direct phase
  tests and focused affected-consumer nodes under the default lane filter.
  Preserve the configured exclusions; do not launch the exhaustive historical
  replay merely because CLI, API, model or report inputs changed. The exact
  selection and explicit-request rule live in the verification-selection
  reference. An invalidated old claim becomes unavailable until its selected
  current-byte controls run; it does not authorize a broad replay.
- **The shipment rule applies without exception: a declared branch that has no
  case which can fail it does not ship.** This is the milestone's defining defect
  class — it has been found in a spec draft five times in one pass, and once in
  the very file written to prevent it. Count coverage per **branch**, not per
  class: a finding class whose deontic half is unreachable with the fixture model
  is half-covered, and closing it may mean editing the fixture model rather than
  adding cases.
- Record implementation findings **as they are found**, in the spec's own
  findings section, including the ones that refute the spec. A finding discovered
  and then quietly designed around is the same as one never found.

## Step 4 — Adversarial review of the diff

A single reviewer is admissible for a phase diff **and the record must say
"one reviewer is one reviewer"**; the four-reviewer panel remains the bar for
plan review and milestone close. Invocation, prompt shape, the
reproduce-before-believe rule, the retained-evidence sanitization trap, and what
a review that finds nothing still owes are in
[`references/review-and-record.md`](references/review-and-record.md).

Every finding is reproduced before it is believed, every fix carries a
regression test **proven to fail against the pre-fix code**, and the reviewer's
findings are retained verbatim.

Every finding is then **triaged for MVP relevance before any of it is fixed** —
blocking, hardening, or completeness, with completeness deferred by default. The
classes, the default handling, and why the panel's severity axis cannot do this
job are in
[`references/review-convergence.md`](references/review-convergence.md).

## Step 5 — Refactoring review

After the code and its adversarial review land, ask one question explicitly:
**what did this phase's work reveal about existing structure that should
change?**

The record carries a `Refactoring review` section with one of exactly two honest
answers:

- **Refactors EXECUTED** — each named, behavior-preserving, landed behind the
  same green gates as the phase's own work.
- **"None needed"**, argued from what the phase actually touched. An asserted
  negative fails record review the same way an unfalsifiable gate does.

A refactor **seen but deferred** is an open-questions row with a named target
milestone. Never silent debt.

## Step 6 — Record + commit

The record is the phase's completion. Contract, scope tokens, the phase-specific
extensions to the base record format, and the commit grammar are in
[`references/review-and-record.md`](references/review-and-record.md). In short:
gate commands and exits **verbatim**, evidence bound by path + sha256, a
mandatory boundary section, open questions, refuted premises when a belief died,
and the refactoring-review section from step 5.

The commit uses GND grammar with a phase scope token, an evidence-bearing body,
`--` rather than em-dashes, **no backticks anywhere in the message**, and the
record path on its own closing line. Stage by explicit path — never `git add -A`.

## Phase shapes this protocol has to cover

The six steps do not change. What changes is where the difficulty sits, and a
spec that misreads its own shape discharges the wrong obligations.

| Shape | Example work | Where the difficulty sits |
|---|---|---|
| **Schema / loader** | a format version, a new reader | backward compatibility pinned by identity tests; old readers frozen, and any admitted exception named |
| **Evaluator** | new checking semantics | the branch table and its coverage; the fixture model's reachability; a normative order with exactly one home |
| **Enablement** | a contract kind, a subprocess runner, a hardened parser | trust boundaries -- every refusal exercised, and an accepted **residual** restated in the reviewers' own terms rather than softened |
| **Harness / orchestration** | a station harness, a skill rewritten as a thin wrapper | the order pinned as a **literal**; fake-station tests for the branches; and at least ONE real end-to-end run, since a walk of fakes proves the harness, not the walk |
| **Read-only view** | a coverage or report surface | criteria that are **absences** -- no aggregate number, no file written, no command consuming the output. An absence is pinned field-for-field, because an absence test that cannot fail is this milestone's defining defect wearing its most convincing disguise |
| **Dogfood** | a migration run over this repository | the gate output **is** the artifact. Criteria must be predicates a run can fail -- "the tool shows an honest wall of open work" is not one; "the committed output is cited by digest and its uncovered count is strictly greater than zero" is |

Two structural notes:

- **Multi-part phases** (a skill plus its dogfood, say) get one spec covering
  both parts and one record per part, numbered monotonically. A part that lands
  separately gets its own gate output; neither part's record claims the other's.
- **A criterion may not depend on a phase the plan calls optional.** If this
  phase's criteria need an earlier phase's output, that dependency is **hard**,
  and if the plan's header says otherwise the plan is wrong -- record it as a
  refuted premise with an open-questions row, and say so before implementing
  against a dependency that might not be there.

## The rules that bind every phase

Six design rules the milestone has already paid for with reproduced defects, and
the register classes a phase can re-commit, are in
[`references/standing-rules.md`](references/standing-rules.md). A spec discharges
each **by name** or argues it inapplicable; silence on one is a review finding.

## Limits — what this skill does not establish

- **A completed walk of these six steps is not an acceptance claim.** Each step
  has its own gate and each gate speaks for itself; running them in order adds
  no authority to any of them.
- **The adversarial review is one reviewer's reading**, usually without the
  ability to run the full suite. It is evidence, not a proof of correctness.
- **An independence pass, where one runs, is a disagreement locator.** An
  agreeing reader and an agreeing implementation can be wrong together, and
  nothing in this protocol separates that case.
- **Repeated review rounds are not monotone improvement.** Measured over five
  rounds on one spec: same-seat finding counts did not fall — they ended higher
  than they began — while each repair round opened the next round's findings,
  and across seventeen seat returns no adversarial seat ever came back empty. Only the convergence measures in
  [`references/review-convergence.md`](references/review-convergence.md)
  distinguish progress from churn; a finding count alone never does.
- **This skill never edits the milestone plan**, records owner decisions or explicitly delegated auto rulings, and never
  proceeds past a STOP on inference.

## Public staging boundary

P1 ships this development protocol and its reference closure, not a runnable
GND package. The source-pinned review tool is a temporary conditional dependency
described in `docs/development/bootstrap.md`. No provider access is needed for
ordinary scaffold checks. Installer-owned links are deferred until P2 supplies
the complete package targets and installer. P4 must demonstrate target-only
wheel-based discovery and remove the bootstrap. Never treat imported historical
review results as opinions over target adaptations.
