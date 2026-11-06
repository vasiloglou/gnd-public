# GND rules for the milestone workflow

`process-phase`, `start-milestone` and `process-milestone` read this file before
anything else. It belongs to this repository. The other files in the three skill
folders are delivered from dev-tools by its sync command (`.devtools.toml` lists
them, `.devtools-receipt.json` records them): do not edit those by hand, write
the repository's own rules here. Keep the copy under `.claude/skills` and the
copy under `.codex/skills` byte-identical, like every other file of these skills.

Each heading names the step or the reference file its rules applied to in the
skill text this repository wrote for itself, before the shared text replaced it.

## What these skills are here (all three skills)

- They are source-owned development skills, present as real copies in both real
  discovery roots. They are not `gnd` commands and not installer-managed
  packaged skills.
- `auto=true` is a skill argument, not a new gnd CLI flag.
- The project's own workflow skills are the packaged GND station skills under
  `src/gnd/skills/`. GND station work over a domain model belongs to
  `gnd-solve` and its siblings, never to `process-phase`.
- The project's scaffold workflow is the packaged `gnd-new-project`. When
  `.gnd-planning` or a plan is missing, offer it (or `start-milestone` for a
  missing plan); do not invoke planning or model skills automatically.
- There is no component index in this repository. Skip every component-index
  step of the shared text.

## Plan-review bar (process-phase steps 2 and 4, start-milestone "Verify and hand off", process-milestone "Resolve readiness")

- The four-reviewer panel is the bar for plan review and milestone close. It is
  not mandated per phase. The repository retains this bar and the bounded
  convergence rules; it stays binding wherever this repository's protocol
  requires it.
- A single reviewer is admissible for a phase diff, and a single reviewer is
  never relabelled as a panel. No project instrument is defined for a phase
  diff: use the shared default in `review-and-record.md` (one reviewer in a
  different tool, prompt on stdin).

## Review instrument: the maintained panel (process-phase step 2; review-and-record.md "Invocation")

- The review instrument for plan review and milestone close, and for a spec
  when the owner calls for one, is the maintained GND review panel (packaged
  skills `gnd-review-panel` and `gnd-review-panel-light`, code in
  `src/gnd/review`).
  Using one of these three skills does not activate the maintained panel, does
  not select a paid review panel and does not authorize reviewer subagents.
- The panel skill's source-provenance precondition is mandatory when developing
  GND itself: if `src/gnd/review` or either packaged panel skill differs from
  `HEAD`, validate and commit those bytes before creating a disposable worktree
  from `HEAD`. A clean checkout that silently omits pending harness fixes is not
  an admissible panel environment.
- When the owner requires all six seats to work, the same panel contract stops
  before invocation unless the parent environment carries `OPENROUTER_API_KEY`
  and `ZAI_API_KEY`.
- In this repository, invoke that all-six run through
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
- Prompt on stdin: routing reviewed-artifact bytes through argv is the transport
  this project already refused once, and it is why a fourth reviewer is absent
  from the panel roster.
- The panel's only severity axis is `low|medium|high|critical`
  (`ConcernSeverity` in `src/gnd/review/request.py`). `ReviewResponse` rejects a
  non-approve verdict that carries no concern ("a {disposition} response must
  contain a concern", same file), so the structural pressure toward producing
  some finding is in the code.
- Provenance tags in a spec: `(p2)` marks a change applied for a first panel
  round, `(o)` an owner decision.

## Opt-in gates: certification and recertification (process-phase step 2; architect-overrides.md; verification-selection.md)

- The opt-in gates of this repository are certification and recertification.
  The owner ruled on 2026-09-28 that they are not automatic phase or milestone
  gates. Run one only when the owner explicitly requests it for a particular
  subject and scope. A changed source, stale installed bundle, completed phase,
  milestone close, or historical plan clause is not such a request.
- An earlier certificate stays bound to its original bytes. If changed bytes
  cause the installed reader to withhold assurance, report that state; do not
  call the older certificate current or bypass the reader.
- This policy supersedes the v6.3 plan gate's D10 one-matrix-per-milestone
  default for future work.
- Merge, publication and certification each keep their separate owner
  authorization; `auto=true` covers none of them.

## Test and gate commands (process-phase step 3; verification-selection.md)

- Focused public selection, owner ruling of 2026-09-29: ordinary phase and
  milestone work uses the reduced v6.3 test selection, the phase's direct tests
  and focused affected-consumer nodes under the default lane filter:

  ```bash
  python -m pytest -q tests/<phase-tests>.py tests/<affected-consumer-tests>.py --tb=short
  ```

  Under uv this is `uv run pytest -q ...`, the form CONTRIBUTING.md and the
  record example use.

- Do not override `addopts` or use `-m` to bring the evidence, census, proof,
  distribution, external-oracle or other excluded lanes into an ordinary gate.
  Missing historical inputs are not green skips. Native skipped lanes are not
  completed gates.
- The broad-lane command is `uv run pytest -q -m "evidence or census"`. Reserve
  `census` for exhaustive tracked-tree assertions and `evidence` for historical
  bytes, fixed-commit replays and retained-output pins.
- The record's verbatim gate output includes the lint gate. The skill text named
  no command for it; ruff is the linter `pyproject.toml` configures.
- Do not introduce `pytest-xdist` as a semantic change merely to make a health
  check faster.
- Frozen v5.1 report-golden replay, explicit request only. The 664-row,
  1,328-command replay is exhaustive historical work outside the reduced phase
  selection. Changes to CLI, API, report renderers, normalizers or population
  classifiers invalidate old evidence; they do not select this replay. It is
  unavailable in this repository: neither its runner nor its answer manifests
  are shipped. If it is later explicitly selected, first restore its exact
  reviewed dependency closure and amend the applicable spec. The original source
  command, historical context only, was
  `uv run python tools/run_v51_historical_replay.py --workers 8`: it accepts
  exact frozen pytest-module and answer-manifest digests, runs all text/JSON
  observations in separate processes with at most eight children, and requires
  the pinned mismatch set; a census or model-binding change also fails the
  selected claim. Do not select the legacy 664-row serial pytest node for
  ordinary phase work.

## Standing design rules: section 0, the paid-for rules (spec section 4; standing-rules.md)

Six design rules this project has already paid for with reproduced defects. They
bind every phase. A spec discharges each by name (the specific loader that must
be total, the specific layer that gets a time-bound test, the specific policy
walk that must not sprout per-kind copies) or argues it inapplicable in one
sentence.

### 1. Totality belongs to the function, not the caller

"This only ever sees validated documents" is a claim about today's callers.
Any new consumer of document shapes is **total over arbitrary JSON**, with a
hostile-input test. The defect that bought this rule: a gate that consumed
proposal-supplied bytes with no validation layer in front of it, in a codebase
where every other consumer had one.

Totality is more than catching one exception class. Check all of:

- The cap is applied to the **read**, not after it. A cap applied after
  `read_bytes()` is a report, not a cap.
- Exception classes that are not the obvious one: a very long integer literal
  raises `ValueError`, not `JSONDecodeError`; deep nesting raises
  `RecursionError`.
- The non-JSON constants. `NaN` and infinities are accepted by default and are
  not JSON.
- The docstring. If it promises totality, a traceback out of that function is a
  contradiction of the shipped contract, not a rough edge.

### 2. An input cap bounds the document, not the algorithm

A rule quadratic in a count the document controls turns a legal input into
minutes of CPU under the cap. Every phase that adds work proportional to
untrusted input ships a **time-bound test over the layer it adds**. This is the
class that was caught once and that nobody searched for twice.

### 3. Validation order is part of the design, stated per boundary

Which check runs first is a design decision with a user-visible consequence: a
gated delta should report "gated", not "your candidate is invalid", or the author
is sent into the other half of the same gate. Where two orderings both reject and
no return value distinguishes them, **pin the order by source-order assertion**.

### 4. A policy governing N element kinds is enforced by one walk over all N

Not N copies of the policy. A shared policy implemented per-kind will be right in
the kinds someone remembered and absent in the rest. The corollary bites on the
fix side too: when **one** function serves both an authoring-time warning and an
evaluation-time verdict, a defect in it is wrong in both places and is fixed
once, which is the point.

### 5. Normative prose has exactly one home

A document written alongside its implementation is a second chance to make the
same mistake, not independent evidence. Keep each normative sentence in one home
so a divergence is a **bug** rather than an ambiguity; everything else cites it.
When a phase's work makes two homes disagree, one of them yields in that phase,
and the spec names which.

**Scope:** the rule governs normative *prose*. It does not forbid byte-identical
sync-pinned copies of an interchange schema: a canonical reference plus a
vendored copy held identical by a mechanical identity test is ONE artifact. This
scope is written down because a reviewer reading the unscoped rule literally
reported such a pair as a violation.

### 6. Resolve contested representation questions by measurement, not argument

Where the codebase can host an experiment, run it. A contested digest question
was settled by making the change and watching eight committed-payload tests go
red: the artifact's own contract decided it, in minutes, with no debate.

## Failure classes this project has committed (standing-rules.md, second list)

These add to the classes the shared `standing-rules.md` lists.

- **A rule made unfalsifiable by how the fixtures were built.** A grading rule
  quantified over "any" versus "every" reads identically on fixtures where the
  subject is only ever touched once. The fixture set has to contain the
  discriminating case, or the rule ships unverified while its coverage row says
  otherwise. Ask of every rule: *what fixture would tell the two readings apart,
  and is it in the set?*
- **An interchange field defined in Python-only terms.** Every digest or
  identifier a **caller** must reproduce is defined over canonical JSON, with a
  stated empty case and a shipped producer. In-process markers may use
  language-specific representations only if they never cross a boundary.
  Related traps, each seen:
  - A digest that **coerces non-string mapping keys** loses content: two distinct
    documents hash identically. That is different in kind from a spelling
    coercion, and it is refused rather than documented.
  - A canonical-form helper **re-implemented** at a second site with the same
    arguments and no guarantee they stay the same arguments.
  - A digest taken over a section that something else then **writes into**: the
    digest moves and every committed artifact stops matching its own source.
- **Fixtures here are fixture models.** A finding class whose deontic half is
  unreachable with the fixture model is half-covered, and closing it may mean
  editing the fixture model rather than adding cases. An independence pass
  bundle carries the normative documents, the model, and enough data to author
  cases.

### Implementation traps worth a checklist

Each of these was a real finding, and each generalizes past the phase that found
it.

- **The schema's spelling and the implementation's spelling differ.** Check the
  enum members literally, and assert the implementation's map covers the enum.
- **"Not implemented" folded into the same branch as "violated."** The failure
  mode is the bad one: input that *satisfies* a rule is reported as failing it.
  Raise a distinct unknown-operator error instead of fabricating a verdict.
- **A property decided about the wrong subject**: about the type rather than
  about the binding, so the answer depends on which fact happens to come first.
- **A guard that goes quiet exactly when it matters**: a fallback to a null
  state makes every later check look clean, losing the strong finding and
  reporting only the weak one.
- **First-match where a multimap was needed**: only the first eligible item
  compiles, or a repeated variable keeps only its last role, so a pattern
  licenses more than it checks.
- **A guard that assumes history.** "This is the only writer" does not entail
  "nothing removes it"; check both directions before compiling an obligation.

## Review convergence: what this project already mechanized (review-convergence.md "The stop rule")

GND already mechanized the stop rule one level down. `gnd exp run` bounds
attempts by contract and terminates a nonaccepted session with a disposition
from a closed vocabulary in which `stagnation`, `oscillation`, and
`budget-exhausted` are first-class terminal outcomes: computed facts, not
judgment calls, decided in code. A repeated review loop is the same loop with
prose in place of populations and deserves the same discipline.

The convergence rules were measured on one phase spec that the panel reviewed
five times in one day (2026-08-23, Phase 4 of the v2.0 milestone). The table of
rounds and the examples drawn from it are in the text this repository wrote
before the shared one replaced it:
`git show e8a21f0e:.claude/skills/process-phase/references/review-convergence.md`.

## Record and commit (process-phase step 6; review-and-record.md; process-milestone "Close the named milestone")

- The base record contract of this repository is the packaged
  `src/gnd/skills/gnd-orm-core/references/milestone-record-format.md`. Phase
  records, material execution records and the milestone close record follow it.
  The `milestone-record-format.md` beside this file is the shared, generalized
  form of the same contract, which the three skills link to. It adds the
  `gates` list, rulings and the plan-gate record, and those additions apply to
  phase, plan-gate and close records. GND's station scope tokens, the `covers:`
  field and the exit bands are in the packaged file only.
- A phase of a milestone plan is **not** a `gnd-solve` station over a domain
  model, and the record says so:
  `skill: "n/a -- repository development, not a gnd-solve station over a domain model"`.
- The focused gate is recorded as `uv run pytest -q tests/<selected-test-file>.py`
  with its verbatim pytest summary line; `slow_cadence` names
  `uv run pytest -q -m "evidence or census"`.
- The commit uses GND grammar with a phase scope token: `feat(v2-p3): ...`, and
  `test(...)`, `fix(...)`, `docs(...)` for the same phase as the work warrants.
- Record names already in use under `.gnd-planning/milestones/`:
  `NNN-plan-gate.md` (scope `plan-gate`) for the plan gate,
  `NNN-phase-<ID>.md` (scope `phase-<ID>`) for a phase and
  `NNN-milestone-close.md` (scope `milestone-close`) for the close. Keep them;
  the shared contract's `NNN-plan.md` and `NNN-close.md` names are not used
  here. This line was taken from the existing records, not from the skill text
  that was replaced, and awaits the owner's confirmation.
- Retained reviewer output: this repository has a guard that will refuse an
  operator's home directory in the milestone's evidence. Sanitize to a
  placeholder and say in the file's own header that it was edited.
- Never treat imported historical review results as opinions over target
  adaptations.

## Planning a milestone (start-milestone "Resolve the milestone and scope")

- For a domain-model successor, read the relevant `gnd coverage MODEL` census
  before selecting goals, following `gnd-new-project`. For a framework
  milestone, explain why an experiment-claim census does not settle runtime
  feature coverage. Do not confuse this planning task with authoring or
  evolving an ORM model.
- Preserve installer links, as well as PROJECT.md, other milestone records and
  unrelated user files.
- Do not run native acceptance lanes merely to fill a plan.
