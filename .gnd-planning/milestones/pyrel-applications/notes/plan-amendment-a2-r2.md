# PyRel applications — proposed tutorial amendment A2 (r2)

2026-10-13. **r2, after four amendment readings.** r1 bytes are retained as
`notes/plan-amendment-a2-r1.md` (SHA-256 `555a0e76…c3d1`) with readings
`plan-amendment-a2-review-{one,two,three,four}.md`. A2 becomes effective only
through a delegated auto=true gate record after its readings converge, as A1
did in `003-plan-amendment.md`. Until then the effective plan is r1 + A1.

## Why

The PA5 chapters (`docs/bookrec/07-native.md`, `docs/expense/04-native.md`)
work as acceptance tests but don't teach anyone how to build an app.
Owner direction, 2026-10-13:

- Write for a junior developer, not a GND expert.
- Show that GND gets you from rules to a working, checked app quickly.
- Make GND the obvious choice for PyRel users building agentic apps: whatever
  produces a candidate (a PyRel query, a script, an LLM agent) hands it to GND,
  and nothing is published unless the model's rules pass.
- Speak to teams that model their ontology in PyRel, including on Snowflake,
  without claiming anything this milestone has not measured.

Review findings this amendment repairs:

1. The PyRel code is hidden; no page shows how a rule relates to a query.
2. `native_query.py` uses private runtime internals, so readers learn neither
   ordinary PyRel nor a stable interface.
3. The blocks are test harnesses, not commands a reader would type.
4. The prose uses internal planning vocabulary.
5. Neither chapter says how to create the two Python environments.
6. Expense chapter 4 needs a manual package/rename step, and its policy-change
   exercise edits model JSON by hand.
7. The native chapters never show a bad candidate going through the app and
   being rejected (Ada/`night` appears only in chapters 2 and 5 via `gnd check`),
   and never say which component does what.

## Honesty rules

Measured facts, verified 2026-10-13:

- Applications run on local PyRel 1.30.1 with DuckDB 1.5.5, pinned in the
  runtime (`src/gnd/export/pyrel_runtime.py:1676-1677`).
- The applications runtime refuses anything but in-memory local execution
  (`pyrel_runtime.py:1752-1754`), and the exporter refuses named remote
  connections (`:1770-1775`; `docs/runtimes/pyrel.md:160-161`).

Rules for every page PA5R writes or touches:

- State the measured runtime plainly.
- Snowflake appears only as context ("if your team models its ontology in
  PyRel, including on Snowflake…") or as an explicit boundary ("running
  against Snowflake is outside this tutorial and outside the applications
  runtime, which refuses non-local connections"). No hook-up point is shown,
  because none exists. The D1 seam takes no connection parameter.
- "Governed" appears only in that conditional form, never describing GND output.
- No claims about adoption, performance, governance certification, production
  readiness or ranking quality.
- The existing caption meaning is kept: a passing check means the supplied facts
  satisfy the modeled rules, nothing more.

## Deliverables (phase PA5R)

**D0 — Fix existing Snowflake overclaims.** Rewrite the Snowflake execution
claims at `docs/index.md:241-242`, `docs/tour.md:157-158`,
`docs/agents/export-and-review.md:16` and `docs/agents/index.md:25-26` into the
boundary form above. These pages fall under D7's claim check.

**D1 — Public query seam in the emitted program.** The native query runs in the
isolated PyRel interpreter (`src/gnd/export/applications.py:183`), where `gnd`
cannot be imported. The seam therefore lives in `pyrel_runtime.py`, which is
concatenated into the emitted program (`src/gnd/export/emit.py:31-34`). This is
a delegated adjustment of ruling O3, which first named a `gnd.pyrel_app` module.

One documented entry point, e.g. `open_app(runtime_globals, population_path,
computed=…)`. It returns an object whose public surface covers everything both
queries need today:

- `model` (the PyRel `Model`), `match(fact_type, **roles)`, `ref(value_type)`,
  `relationship(name, **fields)`, bounded `rows(query)`;
- `has_fact_type(name)`;
- the ordered derivations and their computed facts;
- declaring computed coverage before admission (BookRec's current pre-admission
  step moves into the seam);
- `write_candidate(path, candidate, calculation)` and `refuse(path, kind, reason)`,
  which write the envelope with the binding digests the driver requires
  (`applications.py:192-193`).

Admission, profile limits and version pins are enforced inside the seam exactly
as today. Both `native_query.py` files are rewritten to use only this seam and
documented `relationalai` APIs.

Repository rules:

- No new module. `gnd.export.pyrel_runtime` is already mapped
  (`tools/gnd_layers.json:437`).
- A PyRel-lane test loads the emitted program with `runpy` and pins the seam's
  public name set.
- Existing private names and the RF1/RF2 pins on them stay unchanged
  (`tests/test_rf1_helper_pins.py:401,455`).
- The emitted-program digest change is recorded as an intentional new
  expectation, separately from legacy pins (plan §5).

**D2 — Examples run without manual surgery.**

Expense:
- Chapter 4 continues in chapter 2's `expense-project`, keeping its `cli/` layout
  (`docs/expense/02-application.md:25,41-44`).
- Chapter 2's existing install step also places `native_query.py`.
- Chapter 4 has no packaging or rename step.
- `tests/test_public_generated_examples.py` stays green.

Policy change:
- The meal-cap exercise changes a reader-local copy of the model through the
  same `gnd evolve preview/apply` path chapter 3 teaches.
- No sixth shipped model; the frozen corpus and answer key are unchanged.
- The PA5R spec must confirm that path supports this comparison-value change.
  If it does not, the spec records the refuted premise and uses a reader-local
  copy changed by one shown, explained command. Hand-editing JSON paths inside
  the chapter's code is not allowed.

**D3 — Commands with checked output.**

New marker grammar: `<!-- gnd-run expect=N [lane=x] output=stdout|stderr -->`
followed by a `sh` fence holding one command, then a `text` fence holding the
expected output or a marked excerpt.

Normalization covers:
- the run's temp directory;
- the `gnd-native-application-*` and `gnd-native-checker-*` temp prefixes;
- elapsed times.

Output that can't be normalized deterministically is excluded explicitly, and
shown abbreviated with an ellipsis marker.

Reader-visible commands use `gnd` and `"$GND_TUTORIAL_GND_PYTHON"` for GND steps
and pass `--pyrel-python "$GND_TUTORIAL_PYREL_PYTHON"` for the native side. Bare
`python` is never used in pyrel-lane blocks, because the runner shadows it
(`tools/run_tutorials.py:113-115`).

Every refusal and repair step's shown output includes the disposition, the rule
id and the witness, so PA6's installed page run still asserts semantic outcomes
(PA5-C1, PA6-C1). The pytest file extracts its commands from the marked page
blocks, so page and test cannot drift (PA5-C4). The existing marker count
invariant and receipt fields remain.

**D4 — Rewritten learning path.**

The native chapters continue chapters 1–6 (BookRec) and 1–3 (Expense); they are
not standalone. A new overview page, "PyRel + GND: from rules to a checked app",
sits under Tutorials. It routes newcomers to BookRec chapter 1, where the rules
are written, and readers who have done the earlier chapters straight to the
native ones.

Both native chapters follow this order:

1. **What you'll build.** The flow diagram plus a "who does what" table:
   - candidate producer (PyRel query, script or agent) proposes;
   - PyRel computes;
   - Python orders and limits;
   - GND checks and publishes.
2. **Set up** (D5) and run one hello check in each environment.
3. **One rule beside the code that relates to it.**
   - BookRec: `age_appropriate` beside the blocked relation and `not_` that
     exclude those pairs while computing.
   - Expense: `approval_limit_team_lead` from the model beside the native
     count/sum query, stating plainly that no query enforces the limit; GND's
     check does. That is the point: rules live in the model, not the query.
4. **Run the app and read the checked output.**
5. **A faulty agent.**
   - BookRec: the reader submits a shipped bad candidate through the app's
     publish path, standing in for a faulty agent. A new documented CLI option
     (e.g. `--proposal FILE`) checks a supplied candidate and publishes only on
     acceptance. The page says plainly that the reader is injecting it. Shown
     witness: `{"$u":"ada","$b":"night"}`.
   - Expense: the `--chain team-lead` argument is presented as the agent's
     proposal. Shown witness: `[{"$e":102,"$a":800}]`.
   - Both: the existing "checking catches what filtering cannot" demonstration
     (Ada/read through the standalone checker) folds in here.
6. **Fix it and rerun.**
7. **Change a rule without touching the query.**
   - BookRec: advisory → strict → preferred repair.
   - Expense: the meal cap (D2) plus the currency evolution.
   - The complete-mode material moves to an optional "Go further" section.
8. **Recap** of the step 1 table.
9. **Troubleshooting** as a symptom → cause → fix table.
10. **Next steps:**
    - your own rules (`gnd-model-from-text`);
    - driving a real agent through a separate session contract you author with
      `gnd exp run`, against the same model and checker;
    - the Snowflake boundary sentence.

Keep:

- all six figures, placed in steps 1, 3, 5 or 7, with source captions;
- the exact witnesses (Ada/night, Ada/read, `[{"$e":102,"$a":800}]`,
  `[[101],[102]]`);
- the input-unchanged guarantee;
- the "completion is not acceptance" and warning/unknown distinctions, in plain
  words.

**D5 — Setup for both environments.** Concrete commands, run by the reader
outside the tutorial runner (they need `uv`, Python 3.13 and network, as
`docs/runtimes/scenario.md:37-45` already says):

1. A virtual environment where `gnd` is importable (`bookrec.cli` imports
   `gnd.api`), plus a hello check.
2. The pinned PyRel environment, from the already-shipped, byte-gated
   `release_governance/runtime-environment` copy (no third twin), plus a
   version-printing hello check.

**D6 — Agentic framing.** The "candidate producer" is the agent slot.

- In the PyRel lane, the PyRel query is the producer.
- The faulty-agent step uses a shipped candidate or argument and says so.
- `gnd exp run` is linked only as a separate session contract the reader
  authors; it does not drive these CLIs.
- No LLM call, model key or nondeterministic step is added.

**D7 — Readability and claim gate.** A test over the overview, both native
chapters, the D5 setup section and the D0 pages. It fails on any of these:

- **Banned terms:** "covers_fact_types", "nonowned", "bounded profile",
  "operational failure", "exit 70", "receipt", "binding digest", "admission",
  "witness" without a plain gloss on first use, "governed" outside the
  conditional, "certified", "enterprise-ready", "production", "scal*".
  - Exit codes are allowed only inside the troubleshooting table, each with a
    plain meaning.
  - The list may rename terms but never remove the warning/unknown or
    completion-vs-acceptance distinctions; the test checks that their
    plain-language replacements are present.
- **Paragraph length:** any prose paragraph over 90 words.
- **Missing output:** any executed command without a shown output block.
- **Snowflake wording:** any "Snowflake" sentence lacking "outside" or
  "not tested", or containing "runs on" or "deploy".
- **Required sentences missing:** the measured-runtime sentence
  ("PyRel 1.30.1 with DuckDB 1.5.5") or the passing-check caption meaning on
  each new page.

Elapsed times may be shown only as "measured command time, excludes setup".

## Sequence, PA6 and criteria

- §3 sequence becomes PA5 → PA5R → PA6.
- PA5R must re-satisfy PA5-C1 through C6 in full: six graphics placed, rebound
  to the new bytes, and re-reviewed rendered on desktop and mobile in both themes.
- PA6 is partly committed (`1d6c0c6`, `81ae7bb`), and its harness pins the
  current shape:
  - `(7,52,2)`/`(4,34,3)` and page paths (`tools/accept_pyrel_applications_install.py:67,179`);
  - counts (`tests/test_pyrel_applications_install.py:61`);
  - the `native_query.py` resource inventory;
  - its spec's "PA5 c9432b0/009 complete" prerequisite.
- After PA5R, PA6 gets a new delegated spec gate that updates those constants,
  the inventory and the prerequisite, then reruns its gates.
- Earlier PA6 runs, committed and uncommitted, are superseded but retained.
  No committed history is rewritten.

## Reviews and budget

- **This amendment:** one initial round (done) and one repair round, limited to
  the readers whose blocking findings are reproduced (two, three, four). Every
  r1 finding's disposition is recorded in the gate record.
- **PA5R:** uses the selected Claude Code phase reviewer
  (`notes/phase-review-authorization.md`), with one initial review and at most
  one repair for reproduced blockers. The junior-reader pass is an extra
  reading by that same instrument. It must list every page claim with its
  evidence, and it fails on any step where the reader got stuck until repaired.
- Close still uses the four local readers.

## Out of scope

Snowflake execution or credentials, LLM agents, ranking quality, changing any
policy rule's meaning in shipped models, corpus or answer-key changes, GND
checker semantics, A1's agreement contract, merge, release and certification.

## Owner rulings (2026-10-13)

- **O1:** messaging only, tightened by review two to the boundary form above.
- **O2:** the scripted/native producer is framed as the agent slot, linking to
  `gnd exp run` as a separate contract.
- **O3:** add the public seam. It is relocated into the emitted program as a
  delegated adjustment (D1); the original `gnd.pyrel_app` wording is superseded.
- **O4:** proceed under the milestone's existing auto=true delegation with four
  local amendment readers.
