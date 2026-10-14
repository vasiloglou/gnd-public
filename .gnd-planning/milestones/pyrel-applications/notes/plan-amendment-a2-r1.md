# PyRel applications — proposed tutorial amendment A2

2026-10-13. **Proposed; owner rulings below; pending four amendment readings.** Raised by the owner after reviewing the
shipped PA5 chapters (`docs/bookrec/07-native.md`, `docs/expense/04-native.md`).
Effective plan stays r1 + A1 until the owner rules on this note.

## Why

The PA5 chapters work as acceptance tests, but they don't teach anyone how to
build an app. Owner direction:

- Write for a junior developer, not a GND expert.
- Show that GND gets you from rules to a working app quickly.
- Make GND the obvious choice for PyRel users building agentic apps: the agent
  proposes, PyRel computes over the governed ontology, GND checks before
  anything ships.
- Speak to teams that already govern their ontology in PyRel on Snowflake.

Review findings this amendment repairs:

1. The PyRel code is hidden. No page shows how a rule becomes a query.
2. `native_query.py` uses private internals (`runtime['_parse_document']`,
   `_profile_admit`, `oracle._concept_for`, `oracle._rows`,
   `relationalai.semantics.frontend.base.Field`), so readers learn neither
   ordinary PyRel nor a stable GND interface.
3. The blocks are test harnesses (loops, `subprocess.run`, one-line asserts),
   not commands a reader would type.
4. The prose uses internal planning vocabulary ("unknown coverage",
   "nonowned facts", "exit 70", "bounded profile").
5. No page says how to create the PyRel environment.
6. Expense needs a manual `cli/` package and a file rename to run, and the
   meal-cap exercise edits model JSON by hand.
7. BookRec's opening hook (Ada/`night`) is never demonstrated; the split
   between PyRel, Python and the GND check is never stated.

## Honesty rules for the positioning

The message has to survive a skeptical PyRel/Snowflake reader.

- **Measured:** local PyRel 1.30.1 on DuckDB 1.5.5. Say so plainly.
- **Allowed:** the native query is ordinary PyRel; conditional framing such as
  "if your team already models its ontology in PyRel…"; pointing to where
  a Snowflake connection would plug in, labeled **not tested by this tutorial**.
- **Not allowed:** claiming Snowflake execution, adoption by named or unnamed
  corporations, performance, governance certification, or ranking quality.
- The existing caption rule still holds: a passing check means the supplied
  facts satisfy the modeled rules, nothing more.

## Deliverables (proposed phase PA5R, before PA6 closes)

**D1 — Public query seam.** The native query runs in the separate PyRel
interpreter, where `gnd` is not importable (the PyRel and GND Pydantic pins
conflict), so a `gnd.*` module cannot serve it. The seam therefore lives in the
standalone program that `gnd export pyrel` emits (source:
`src/gnd/export/pyrel_runtime.py`), which `native_query.py` already loads.
Add one documented entry point there, e.g. `open_app(population_path)`
returning an object with public `model` (the PyRel `Model`), `relation(fact_type)`,
`match(fact_type, **roles)`, `ref(value_type)`, `relationship(name, **fields)`
and bounded `rows(query)`, enforcing the existing admission and limits.
Rewrite both `native_query.py` files to use only that entry point and
documented `relationalai` APIs. Existing private names and exported checker
behavior stay unchanged; the new names get layer-map and export golden coverage
as the repository's rules require.

**D2 — Examples run as installed.** Expense runs from the copied directory
with no package creation or renaming. The policy-change exercise uses a shipped
`lower-cap` model variant (or the chapter 3 evolve path) instead of editing JSON.

**D3 — Commands with checked output.** The tutorial runner gains a block kind
that shows a shell command followed by its expected output, and verifies the
output after normalizing paths and timings. Assertions move to
`tests/test_pyrel_tutorial_experience.py`, which runs the same commands.
Readers see `gnd …`/`python …` lines and real output, not harness code.

**D4 — Rewritten learning path.** New overview page
"PyRel + GND: from rules to a checked agentic app" (nav under Tutorials), then
BookRec 7 and Expense 4 restructured as:

1. What you'll build, in 3 sentences and one diagram.
2. Set up the PyRel environment (D5) and run one hello check.
3. One rule next to its PyRel query, explained line by line
   (`age_appropriate` → `where(...)` / `not_(...)` for BookRec;
   `approval_limit_team_lead` for Expense).
4. Run the app and read the output.
5. Break it: the agent proposes Ada/`night` (and the 800 EUR team-lead approval);
   see the rejection and its witness.
6. Fix it and rerun.
7. Change a rule without touching the query.
8. "Who does what" table: agent proposes / PyRel computes / GND checks and
   publishes / Python orders and limits.
9. Troubleshooting as a symptom → cause → fix table.
10. Next steps: your own rules (`gnd-model-from-text`), your own data
    (Snowflake hook-up point, labeled untested).

**D5 — Setup instructions.** Concrete commands to create the pinned PyRel
environment from a resource shipped in the wheel. Measured starting point:
`src/gnd/examples/release_governance` already ships an exact copy of the
`tutorials/runtimes` project and lock, and `docs/runtimes/scenario.md` gives
working `uv sync … --only-group tutorial-runtimes --python 3.13` commands.
Ship the same byte-gated copy with the BookRec/Expense examples (or point to
the existing one) so setup works without a repository checkout.

**D6 — Agentic framing.** The existing deterministic proposer is presented as
the "agent" slot: the step where any agent, scripted or LLM, puts forward a
candidate. Each chapter links to `gnd exp run` for driving a real agent against
the same checker. No LLM call, model key or nondeterministic step is added.

**D7 — Readability gate.** A test that fails on a banned-jargon list in the two
chapters and the overview, on paragraphs over a set length, and on any executed
command without shown output. One independent review reads the pages as a
junior developer and reports where they got stuck.

## Effect on PA6

PA6 binds tutorial bytes, installed pages and receipts. PA5R changes those
bytes, so the current PA6 evidence (uncommitted under `evidence/PA6/`) becomes
superseded. PA6 reruns its unchanged gates after PA5R. Nothing already
committed is rewritten.

## Out of scope

Snowflake execution or credentials, ranking quality, changing any policy rule's
meaning, GND checker semantics, A1's agreement contract, merge, release and
certification.

## Owner rulings (2026-10-13)

O1 messaging only; O2 scripted proposer framed as the agent slot, linking to
`gnd exp run`; O3 add the public seam (D1, as relocated above); O4 proceed under
the milestone's existing auto=true delegation with four local amendment readers.

Original options, retained for the record:

- **O1 Snowflake:** messaging-only with the hook-up point labeled untested
  (recommended), or add an optional Snowflake lane that needs an account and
  credentials you supply.
- **O2 Agent depth:** present the existing scripted proposer as the agent slot
  and link to `gnd exp run` (recommended), or add a chapter where a real LLM
  agent proposes and GND rejects/accepts its output.
- **O3 Helper API:** approve adding public `gnd.pyrel_app` (D1), or keep it
  docs-only and explain the current internals instead.
- **O4 Approval mode:** this note is approved by you personally, or under the
  milestone's existing auto=true delegation with the usual reviews.
